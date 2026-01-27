from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import json


class AgentRole(Enum):
    CLASSIFIER = "classifier"
    DEDUPLICATOR = "deduplicator"
    ROUTER = "router"
    LOG_PARSER = "log_parser"
    PATTERN_DETECTOR = "pattern_detector"
    CORRELATOR = "correlator"
    HYPOTHESIS_GENERATOR = "hypothesis_generator"
    VALIDATOR = "validator"
    SUMMARIZER = "summarizer"
    COORDINATOR = "coordinator"


class Agent:
    
    def __init__(self, name: str, role: AgentRole, llm, system_prompt: Optional[str] = None):
        self.name = name
        self.role = role
        self.llm = llm
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.execution_history: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}
    
    def _default_system_prompt(self) -> str:
        prompts = {
            AgentRole.CLASSIFIER: "You are an expert incident classifier. Analyze incidents and assign severity (P0-P4) and category.",
            AgentRole.DEDUPLICATOR: "You are an expert at finding duplicate incidents. Compare incidents and identify similarities.",
            AgentRole.ROUTER: "You are an expert incident router. Assign incidents to the appropriate team based on expertise.",
            AgentRole.LOG_PARSER: "You are an expert log parser. Extract structured information from unstructured logs.",
            AgentRole.PATTERN_DETECTOR: "You are an expert pattern detector. Identify anomalies and patterns in data.",
            AgentRole.CORRELATOR: "You are an expert at correlating events. Find relationships between different events.",
            AgentRole.HYPOTHESIS_GENERATOR: "You are an expert at generating root cause hypotheses based on evidence.",
            AgentRole.VALIDATOR: "You are an expert at validating hypotheses against evidence.",
            AgentRole.SUMMARIZER: "You are an expert at summarizing complex information concisely.",
            AgentRole.COORDINATOR: "You are an expert coordinator. Manage and orchestrate multiple agents."
        }
        return prompts.get(self.role, "You are a helpful AI assistant.")
    
    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = datetime.now()
        
        prompt = self._build_prompt(input_data, context)
        
        llm_response = self.llm.generate(prompt, temperature=0.3, max_tokens=800)
        
        result = self._parse_response(llm_response['response'], input_data)
        
        execution_record = {
            'timestamp': start_time.isoformat(),
            'input': input_data,
            'context': context,
            'prompt': prompt,
            'llm_response': llm_response,
            'result': result,
            'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
        }
        self.execution_history.append(execution_record)
        
        return result
    
    def _build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        prompt_parts = [self.system_prompt, "\n\n"]
        
        if context:
            prompt_parts.append("Context:\n")
            prompt_parts.append(json.dumps(context, indent=2))
            prompt_parts.append("\n\n")
        
        prompt_parts.append("Input:\n")
        prompt_parts.append(json.dumps(input_data, indent=2))
        prompt_parts.append("\n\n")
        
        prompt_parts.append(self._get_task_instruction())
        
        return "".join(prompt_parts)
    
    def _get_task_instruction(self) -> str:
        instructions = {
            AgentRole.CLASSIFIER: "Classify this incident and provide: severity (P0-P4), category, confidence score, and reasoning.",
            AgentRole.DEDUPLICATOR: "Analyze for duplicates and provide: similarity score, duplicate status, related incident IDs.",
            AgentRole.ROUTER: "Route this incident and provide: assigned team, confidence, escalation flag, SLA, and reasoning.",
            AgentRole.LOG_PARSER: "Parse the logs and provide: error types, occurrences, timestamps, affected services, and key patterns.",
            AgentRole.PATTERN_DETECTOR: "Detect patterns and provide: primary pattern, anomaly score, frequency, affected metrics.",
            AgentRole.CORRELATOR: "Correlate events and provide: correlated events, time window, correlation strength, causal chain.",
            AgentRole.HYPOTHESIS_GENERATOR: "Generate root cause hypothesis and provide: hypothesis, confidence, supporting evidence, recommended action.",
            AgentRole.VALIDATOR: "Validate the hypothesis and provide: validation result, evidence strength, contradictions, recommendation.",
            AgentRole.SUMMARIZER: "Summarize the incident and provide: duration, impact, root cause, resolution, prevention measures.",
            AgentRole.COORDINATOR: "Coordinate the workflow and provide: next steps, agent assignments, priorities."
        }
        return instructions.get(self.role, "Analyze the input and provide insights.")
    
    def _parse_response(self, response_text: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'agent': self.name,
            'role': self.role.value,
            'response': response_text,
            'timestamp': datetime.now().isoformat(),
            'input_summary': self._summarize_input(input_data)
        }
    
    def _summarize_input(self, input_data: Dict[str, Any]) -> str:
        if 'title' in input_data:
            return input_data['title']
        elif 'description' in input_data:
            return input_data['description'][:100] + "..."
        else:
            return str(input_data)[:100] + "..."
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
    
    def clear_history(self):
        self.execution_history = []
    
    def update_state(self, key: str, value: Any):
        self.state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', role={self.role.value}, executions={len(self.execution_history)})"
