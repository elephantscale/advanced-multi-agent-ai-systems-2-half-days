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

from src.schemas import (
    ClassificationResult, DeduplicationResult, RoutingDecision,
    WorkflowState, GuardrailViolation
)
from src.observability import TraceLogger
from src.tools import get_read_only_tools


class TriageState(TypedDict):
    """State for incident triage workflow."""
    incident_id: str
    trace_id: str
    incident_data: Dict[str, Any]
    classification: Dict[str, Any]
    deduplication: Dict[str, Any]
    routing: Dict[str, Any]
    errors: list
    step_count: int
    max_steps: int
    messages: Sequence[BaseMessage]


class TriageWorkflow:
    """LangGraph-based incident triage workflow."""
    
    def __init__(
        self,
        llm: BaseLanguageModel,
        logger: TraceLogger,
        max_steps: int = 10,
        incident_db: list = None,
        policies: dict = None
    ):
        self.llm = llm
        self.logger = logger
        self.max_steps = max_steps
        self.incident_db = incident_db or []
        self.policies = policies or {}
        self.tools = get_read_only_tools(
            incident_db=self.incident_db,
            policies=self.policies
        )
        
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not available. Install with: pip install langgraph")
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph."""
        workflow = StateGraph(TriageState)
        
        workflow.add_node("classify", self.classify_node)
        workflow.add_node("deduplicate", self.deduplicate_node)
        workflow.add_node("route", self.route_node)
        workflow.add_node("check_guardrails", self.check_guardrails_node)
        
        workflow.set_entry_point("classify")
        
        workflow.add_edge("classify", "check_guardrails")
        workflow.add_conditional_edges(
            "check_guardrails",
            self.should_continue_after_classify,
            {
                "deduplicate": "deduplicate",
                "end": END
            }
        )
        workflow.add_edge("deduplicate", "route")
        workflow.add_edge("route", END)
        
        return workflow.compile()
    
    def classify_node(self, state: TriageState) -> TriageState:
        """Classification node."""
        start_time = datetime.now()
        self.logger.log_node_start("classify", state)
        
        incident_data = state["incident_data"]
        
        prompt = f"""You are an expert incident classifier. Analyze this incident and provide classification.

Incident Details:
- Title: {incident_data.get('title', 'N/A')}
- Description: {incident_data.get('description', 'N/A')}
- Affected Users: {incident_data.get('affected_users', 0)}

Classify this incident with:
- severity (P0, P1, P2, P3, P4)
- category (Database, Network, Application, Infrastructure, Security)
- confidence (0.0 to 1.0)
- reasoning (brief explanation)
- requires_escalation (true/false)

Return ONLY valid JSON matching this structure:
{{
  "severity": "P0",
  "category": "Database",
  "confidence": 0.85,
  "reasoning": "explanation here",
  "requires_escalation": false
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            classification_data = json.loads(response_text)
            
            classification = ClassificationResult(**classification_data)
            
            state["classification"] = classification.dict()
            state["step_count"] += 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("classify", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from classification: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("classify", error_msg, state)
        except Exception as e:
            error_msg = f"Classification error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("classify", error_msg, state)
        
        return state
    
    def deduplicate_node(self, state: TriageState) -> TriageState:
        """Deduplication node."""
        start_time = datetime.now()
        self.logger.log_node_start("deduplicate", state)
        
        incident_data = state["incident_data"]
        classification = state.get("classification", {})
        
        prompt = f"""You are an expert at finding duplicate incidents. Analyze this incident for duplicates.

Incident Details:
- Title: {incident_data.get('title', 'N/A')}
- Description: {incident_data.get('description', 'N/A')}
- Classification: {classification.get('severity', 'N/A')} - {classification.get('category', 'N/A')}

Determine if this is a duplicate and provide:
- is_duplicate (true/false)
- duplicate_of (incident ID if duplicate, else null)
- similar_incidents (list of similar incident matches)
- confidence (0.0 to 1.0)
- recommendation (action to take)

Return ONLY valid JSON matching this structure:
{{
  "is_duplicate": false,
  "duplicate_of": null,
  "similar_incidents": [],
  "confidence": 0.80,
  "recommendation": "Create new incident"
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            dedup_data = json.loads(response_text)
            
            deduplication = DeduplicationResult(**dedup_data)
            
            state["deduplication"] = deduplication.dict()
            state["step_count"] += 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("deduplicate", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from deduplication: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("deduplicate", error_msg, state)
        except Exception as e:
            error_msg = f"Deduplication error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("deduplicate", error_msg, state)
        
        return state
    
    def route_node(self, state: TriageState) -> TriageState:
        """Routing node."""
        start_time = datetime.now()
        self.logger.log_node_start("route", state)
        
        incident_data = state["incident_data"]
        classification = state.get("classification", {})
        
        prompt = f"""You are an expert incident router. Determine the best team to handle this incident.

Incident Details:
- Title: {incident_data.get('title', 'N/A')}
- Severity: {classification.get('severity', 'N/A')}
- Category: {classification.get('category', 'N/A')}

Provide routing decision with:
- assigned_team (team name)
- sla_hours (SLA in hours, must be > 0)
- priority (1-5, where 1 is highest)
- escalation_required (true/false)
- reasoning (brief explanation)
- confidence (0.0 to 1.0)

Return ONLY valid JSON matching this structure:
{{
  "assigned_team": "Database Team",
  "sla_hours": 4,
  "priority": 1,
  "escalation_required": false,
  "reasoning": "explanation here",
  "confidence": 0.85
}}"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            routing_data = json.loads(response_text)
            
            routing = RoutingDecision(**routing_data)
            
            state["routing"] = routing.dict()
            state["step_count"] += 1
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_node_end("route", state, duration_ms)
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON from routing: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("route", error_msg, state)
        except Exception as e:
            error_msg = f"Routing error: {e}"
            state["errors"].append(error_msg)
            self.logger.log_error("route", error_msg, state)
        
        return state
    
    def check_guardrails_node(self, state: TriageState) -> TriageState:
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
        
        if len(state["errors"]) > 3:
            violation = {
                "violation_type": "too_many_errors",
                "severity": "critical",
                "message": f"Too many errors: {len(state['errors'])}",
                "action_taken": "workflow_terminated"
            }
            self.logger.log_guardrail_violation("too_many_errors", violation)
        
        return state
    
    def should_continue_after_classify(self, state: TriageState) -> str:
        """Decide whether to continue after classification."""
        if state["step_count"] >= state["max_steps"]:
            return "end"
        
        if len(state["errors"]) > 3:
            return "end"
        
        if not state.get("classification"):
            return "end"
        
        return "deduplicate"
    
    def run(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the triage workflow."""
        trace_id = self.logger.start_trace("TriageWorkflow", incident_data)
        
        initial_state: TriageState = {
            "incident_id": incident_data.get("id", str(uuid.uuid4())),
            "trace_id": trace_id,
            "incident_data": incident_data,
            "classification": {},
            "deduplication": {},
            "routing": {},
            "errors": [],
            "step_count": 0,
            "max_steps": self.max_steps,
            "messages": []
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            self.logger.end_trace("completed", {
                "classification": final_state.get("classification"),
                "deduplication": final_state.get("deduplication"),
                "routing": final_state.get("routing"),
                "errors": final_state.get("errors")
            })
            
            return {
                "status": "completed" if not final_state.get("errors") else "completed_with_errors",
                "trace_id": trace_id,
                "classification": final_state.get("classification"),
                "deduplication": final_state.get("deduplication"),
                "routing": final_state.get("routing"),
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


def create_triage_workflow(
    llm: BaseLanguageModel,
    logger: TraceLogger,
    max_steps: int = 10,
    incident_db: list = None,
    policies: dict = None
) -> TriageWorkflow:
    """Factory function to create triage workflow."""
    return TriageWorkflow(
        llm=llm,
        logger=logger,
        max_steps=max_steps,
        incident_db=incident_db,
        policies=policies
    )
