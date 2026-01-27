from typing import Dict, Any, TypedDict, Annotated, Sequence
from datetime import datetime
import json
import uuid

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import BaseMessage, HumanMessage
    from langchain_core.language_models import BaseLanguageModel
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = "END"

from src.schemas import LogAnalysisResult, CorrelationResult, RCAHypothesis, ValidationResult
from src.observability import TraceLogger
from src.rca import LogAnalyzer, EvidenceCollector, HypothesisGenerator, HypothesisValidator


class RCAState(TypedDict):
    """State for RCA workflow."""
    incident_id: str
    trace_id: str
    incident_data: Dict[str, Any]
    log_data: str
    log_analysis: Dict[str, Any]
    patterns: list
    correlation: Dict[str, Any]
    hypothesis: Dict[str, Any]
    validation: Dict[str, Any]
    evidence_collected: list
    errors: list
    step_count: int
    max_steps: int
    loop_detection: Dict[str, int]
    messages: Sequence[BaseMessage]


class RCAWorkflow:
    """LangGraph-based Root Cause Analysis workflow."""
    
    def __init__(
        self,
        llm: BaseLanguageModel,
        logger: TraceLogger,
        max_steps: int = 15,
        log_data: str = ""
    ):
        self.llm = llm
        self.logger = logger
        self.max_steps = max_steps
        self.log_data = log_data
        
        self.log_analyzer = LogAnalyzer()
        self.evidence_collector = EvidenceCollector()
        self.hypothesis_generator = HypothesisGenerator()
        self.hypothesis_validator = HypothesisValidator()
        
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not available. Install with: pip install langgraph")
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph for RCA."""
        workflow = StateGraph(RCAState)
        
        workflow.add_node("parse_logs", self.parse_logs_node)
        workflow.add_node("detect_patterns", self.detect_patterns_node)
        workflow.add_node("correlate_events", self.correlate_events_node)
        workflow.add_node("generate_hypothesis", self.generate_hypothesis_node)
        workflow.add_node("validate_hypothesis", self.validate_hypothesis_node)
        workflow.add_node("check_guardrails", self.check_guardrails_node)
        
        workflow.set_entry_point("parse_logs")
        
        workflow.add_edge("parse_logs", "detect_patterns")
        workflow.add_edge("detect_patterns", "correlate_events")
        workflow.add_edge("correlate_events", "check_guardrails")
        
        workflow.add_conditional_edges(
            "check_guardrails",
            self.should_continue_to_hypothesis,
            {
                "generate_hypothesis": "generate_hypothesis",
                "end": END
            }
        )
        
        workflow.add_edge("generate_hypothesis", "validate_hypothesis")
        workflow.add_edge("validate_hypothesis", END)
        
        return workflow.compile()
    
    def parse_logs_node(self, state: RCAState) -> RCAState:
        """Parse logs node."""
        start_time = datetime.now()
        self.logger.log_node_start("parse_logs", state)
        
        try:
            log_analysis = self.log_analyzer.parse_logs(state["log_data"])
            
            self.evidence_collector.add_log_evidence(log_analysis)
            
            state["log_analysis"] = log_analysis
            state["step_count"] += 1
            state["loop_detection"]["parse_logs"] = state["loop_detection"].get("parse_logs", 0) + 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("parse_logs", state, duration_ms)
            
        except Exception as e:
            error_msg = f"Log parsing error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("parse_logs", error_msg, state)
        
        return state
    
    def detect_patterns_node(self, state: RCAState) -> RCAState:
        """Detect patterns node."""
        start_time = datetime.now()
        self.logger.log_node_start("detect_patterns", state)
        
        log_analysis = state.get("log_analysis", {})
        
        prompt = f"""You are an expert at detecting patterns in log data. Analyze this log summary:

Log Analysis:
- Total Errors: {log_analysis.get('error_count', 0)}
- Error Types: {json.dumps(log_analysis.get('error_types', {}))}
- Affected Services: {log_analysis.get('affected_services', [])}
- Time Range: {log_analysis.get('time_range', {})}

Detect patterns and provide analysis. Return ONLY valid JSON:
{{
  "patterns": [
    {{
      "pattern_type": "error_spike",
      "occurrences": 50,
      "first_seen": "2024-01-27T10:00:00Z",
      "last_seen": "2024-01-27T14:00:00Z",
      "affected_services": ["service-1"],
      "severity": "high"
    }}
  ],
  "key_findings": ["Finding 1", "Finding 2"]
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            pattern_data = json.loads(response_text)
            
            patterns = pattern_data.get('patterns', [])
            
            for pattern in patterns:
                self.evidence_collector.add_pattern_evidence(pattern)
            
            state["patterns"] = patterns
            state["step_count"] += 1
            state["loop_detection"]["detect_patterns"] = state["loop_detection"].get("detect_patterns", 0) + 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("detect_patterns", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from pattern detection: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("detect_patterns", error_msg, state)
        except Exception as e:
            error_msg = f"Pattern detection error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("detect_patterns", error_msg, state)
        
        return state
    
    def correlate_events_node(self, state: RCAState) -> RCAState:
        """Correlate events node."""
        start_time = datetime.now()
        self.logger.log_node_start("correlate_events", state)
        
        log_analysis = state.get("log_analysis", {})
        patterns = state.get("patterns", [])
        
        prompt = f"""You are an expert at correlating events. Analyze the relationship between these events:

Log Analysis: {json.dumps(log_analysis, indent=2)[:500]}
Patterns: {json.dumps(patterns, indent=2)[:500]}

Correlate events and identify causal chains. Return ONLY valid JSON:
{{
  "correlated_events": ["event1", "event2"],
  "correlation_strength": 0.85,
  "time_window_minutes": 15,
  "causal_chain": ["Deployment", "Config Change", "Error Spike"],
  "confidence": 0.80
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            correlation_data = json.loads(response_text)
            
            correlation = CorrelationResult(**correlation_data)
            
            state["correlation"] = correlation.dict()
            state["step_count"] += 1
            state["loop_detection"]["correlate_events"] = state["loop_detection"].get("correlate_events", 0) + 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("correlate_events", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from correlation: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("correlate_events", error_msg, state)
        except Exception as e:
            error_msg = f"Correlation error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("correlate_events", error_msg, state)
        
        return state
    
    def generate_hypothesis_node(self, state: RCAState) -> RCAState:
        """Generate hypothesis node."""
        start_time = datetime.now()
        self.logger.log_node_start("generate_hypothesis", state)
        
        log_analysis = state.get("log_analysis", {})
        patterns = state.get("patterns", [])
        correlation = state.get("correlation", {})
        
        evidence_summary = self.evidence_collector.get_evidence_summary()
        
        prompt = f"""You are an expert at root cause analysis. Generate a hypothesis based on this evidence:

Log Analysis: {json.dumps(log_analysis, indent=2)[:300]}
Patterns: {json.dumps(patterns, indent=2)[:300]}
Correlation: {json.dumps(correlation, indent=2)[:300]}
Evidence Count: {evidence_summary.get('total_evidence', 0)}

Generate root cause hypothesis. Return ONLY valid JSON:
{{
  "hypothesis": "Database connection pool exhaustion due to increased load",
  "confidence": 0.85,
  "supporting_evidence": [],
  "contradicting_evidence": [],
  "recommended_actions": ["Action 1", "Action 2"],
  "estimated_resolution_time_hours": 2
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            hypothesis_data = json.loads(response_text)
            
            hypothesis_data['supporting_evidence'] = [ev.dict() for ev in self.evidence_collector.evidence[:3]]
            hypothesis_data['contradicting_evidence'] = []
            
            hypothesis = RCAHypothesis(**hypothesis_data)
            
            state["hypothesis"] = hypothesis.dict()
            state["step_count"] += 1
            state["loop_detection"]["generate_hypothesis"] = state["loop_detection"].get("generate_hypothesis", 0) + 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("generate_hypothesis", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from hypothesis generation: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("generate_hypothesis", error_msg, state)
        except Exception as e:
            error_msg = f"Hypothesis generation error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("generate_hypothesis", error_msg, state)
        
        return state
    
    def validate_hypothesis_node(self, state: RCAState) -> RCAState:
        """Validate hypothesis node."""
        start_time = datetime.now()
        self.logger.log_node_start("validate_hypothesis", state)
        
        hypothesis_dict = state.get("hypothesis", {})
        
        if not hypothesis_dict:
            state["errors"].append("No hypothesis to validate")
            return state
        
        try:
            hypothesis = RCAHypothesis(**hypothesis_dict)
            
            validation = self.hypothesis_validator.validate(hypothesis)
            
            state["validation"] = validation
            state["step_count"] += 1
            state["loop_detection"]["validate_hypothesis"] = state["loop_detection"].get("validate_hypothesis", 0) + 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("validate_hypothesis", state, duration_ms)
            
        except Exception as e:
            error_msg = f"Validation error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("validate_hypothesis", error_msg, state)
        
        return state
    
    def check_guardrails_node(self, state: RCAState) -> RCAState:
        """Check guardrails."""
        if state["step_count"] >= state["max_steps"]:
            violation = {
                "violation_type": "max_steps_exceeded",
                "severity": "error",
                "message": f"Maximum steps ({state['max_steps']}) exceeded",
                "action_taken": "workflow_terminated"
            }
            state["errors"].append(f"Guardrail violation: {violation['message']}")
            self.logger.log_guardrail_violation("max_steps_exceeded", violation)
        
        for node_name, count in state["loop_detection"].items():
            if count > 3:
                violation = {
                    "violation_type": "loop_detected",
                    "severity": "warning",
                    "message": f"Node {node_name} executed {count} times",
                    "action_taken": "workflow_may_terminate"
                }
                self.logger.log_guardrail_violation("loop_detected", violation)
        
        if len(state["errors"]) > 5:
            violation = {
                "violation_type": "too_many_errors",
                "severity": "critical",
                "message": f"Too many errors: {len(state['errors'])}",
                "action_taken": "workflow_terminated"
            }
            self.logger.log_guardrail_violation("too_many_errors", violation)
        
        return state
    
    def should_continue_to_hypothesis(self, state: RCAState) -> str:
        """Decide whether to continue to hypothesis generation."""
        if state["step_count"] >= state["max_steps"]:
            return "end"
        
        if len(state["errors"]) > 5:
            return "end"
        
        if not state.get("log_analysis") or not state.get("patterns"):
            return "end"
        
        return "generate_hypothesis"
    
    def run(self, incident_data: Dict[str, Any], log_data: str) -> Dict[str, Any]:
        """Run the RCA workflow."""
        trace_id = self.logger.start_trace("RCAWorkflow", incident_data)
        
        initial_state: RCAState = {
            "incident_id": incident_data.get("id", str(uuid.uuid4())),
            "trace_id": trace_id,
            "incident_data": incident_data,
            "log_data": log_data,
            "log_analysis": {},
            "patterns": [],
            "correlation": {},
            "hypothesis": {},
            "validation": {},
            "evidence_collected": [],
            "errors": [],
            "step_count": 0,
            "max_steps": self.max_steps,
            "loop_detection": {},
            "messages": []
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            self.logger.end_trace("completed", {
                "hypothesis": final_state.get("hypothesis"),
                "validation": final_state.get("validation"),
                "errors": final_state.get("errors")
            })
            
            return {
                "status": "completed" if not final_state.get("errors") else "completed_with_errors",
                "trace_id": trace_id,
                "log_analysis": final_state.get("log_analysis"),
                "patterns": final_state.get("patterns"),
                "correlation": final_state.get("correlation"),
                "hypothesis": final_state.get("hypothesis"),
                "validation": final_state.get("validation"),
                "errors": final_state.get("errors"),
                "step_count": final_state.get("step_count")
            }
        
        except Exception as e:
            error_msg = f"Workflow execution error: {e}"
            self.logger.log_error("workflow", error_msg, initial_state)
            self.logger.end_trace("failed", {"error": error_msg})
            
            return {
                "status": "failed",
                "trace_id": trace_id,
                "error": error_msg,
                "errors": [error_msg]
            }


def create_rca_workflow(
    llm: BaseLanguageModel,
    logger: TraceLogger,
    max_steps: int = 15,
    log_data: str = ""
) -> RCAWorkflow:
    """Factory function to create RCA workflow."""
    return RCAWorkflow(
        llm=llm,
        logger=logger,
        max_steps=max_steps,
        log_data=log_data
    )
