import os
import hashlib
import random
from typing import Any, Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

try:
    from langchain_core.language_models.base import BaseLanguageModel
    from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
    from langchain_core.outputs import ChatGeneration, ChatResult, LLMResult
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = object


class MockLLM(BaseLanguageModel):
    """
    LangChain-compatible MockLLM that runs without API keys.
    Provides deterministic or probabilistic responses for testing.
    """
    
    def __init__(self, deterministic: bool = True, seed: int = 42, **kwargs):
        super().__init__(**kwargs)
        self.deterministic = deterministic
        self.seed = seed
        self.call_count = 0
        self.total_tokens = 0
        
        if not deterministic:
            random.seed(seed)
        
        self.response_patterns = {
            'classify': self._classify_response,
            'deduplicate': self._deduplicate_response,
            'route': self._route_response,
            'parse_logs': self._parse_logs_response,
            'detect_patterns': self._detect_patterns_response,
            'correlate': self._correlate_response,
            'hypothesize': self._hypothesize_response,
            'validate': self._validate_response,
        }
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """Generate response for LangChain compatibility."""
        self.call_count += 1
        
        prompt = self._messages_to_prompt(messages)
        task_type = self._detect_task_type(prompt)
        
        if self.deterministic:
            response_text = self._deterministic_response(prompt, task_type)
        else:
            response_text = self._probabilistic_response(prompt, task_type)
        
        tokens_used = len(prompt.split()) + len(response_text.split())
        self.total_tokens += tokens_used
        
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to prompt string."""
        parts = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                parts.append(f"System: {msg.content}")
            elif isinstance(msg, HumanMessage):
                parts.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                parts.append(f"AI: {msg.content}")
            else:
                parts.append(str(msg.content))
        return "\n".join(parts)
    
    def _detect_task_type(self, prompt: str) -> str:
        """Detect task type from prompt."""
        prompt_lower = prompt.lower()
        
        if 'classify' in prompt_lower or 'severity' in prompt_lower:
            return 'classify'
        elif 'duplicate' in prompt_lower or 'similar' in prompt_lower:
            return 'deduplicate'
        elif 'route' in prompt_lower or 'assign' in prompt_lower:
            return 'route'
        elif 'parse' in prompt_lower or 'extract' in prompt_lower:
            return 'parse_logs'
        elif 'pattern' in prompt_lower or 'anomaly' in prompt_lower:
            return 'detect_patterns'
        elif 'correlate' in prompt_lower:
            return 'correlate'
        elif 'hypothesis' in prompt_lower or 'root cause' in prompt_lower:
            return 'hypothesize'
        elif 'validate' in prompt_lower:
            return 'validate'
        else:
            return 'generic'
    
    def _deterministic_response(self, prompt: str, task_type: str) -> str:
        """Generate deterministic response based on prompt hash."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        hash_int = int(prompt_hash[:8], 16)
        
        if task_type in self.response_patterns:
            return self.response_patterns[task_type](prompt, hash_int)
        else:
            return self._generic_response(prompt, hash_int)
    
    def _probabilistic_response(self, prompt: str, task_type: str) -> str:
        """Generate probabilistic response with controlled randomness."""
        rand_seed = random.randint(0, 1000000)
        
        if task_type in self.response_patterns:
            return self.response_patterns[task_type](prompt, rand_seed)
        else:
            return self._generic_response(prompt, rand_seed)
    
    def _classify_response(self, prompt: str, seed: int) -> str:
        """Generate classification response in JSON format."""
        severities = ['P0', 'P1', 'P2', 'P3', 'P4']
        categories = ['Database', 'Network', 'Application', 'Infrastructure', 'Security']
        
        severity_idx = seed % len(severities)
        category_idx = (seed // 10) % len(categories)
        
        if 'database' in prompt.lower() or 'connection' in prompt.lower():
            category_idx = 0
        if 'critical' in prompt.lower() or 'outage' in prompt.lower():
            severity_idx = 0
        
        return f'''{{
  "severity": "{severities[severity_idx]}",
  "category": "{categories[category_idx]}",
  "confidence": {0.75 + (seed % 25) / 100},
  "reasoning": "Based on incident description, classified as {severities[severity_idx]} {categories[category_idx]} issue requiring immediate attention.",
  "requires_escalation": {str(severity_idx < 2).lower()}
}}'''
    
    def _deduplicate_response(self, prompt: str, seed: int) -> str:
        """Generate deduplication response in JSON format."""
        similarity = 60 + (seed % 40)
        is_dup = similarity > 80
        
        return f'''{{
  "is_duplicate": {str(is_dup).lower()},
  "duplicate_of": {"\"INC-" + str(10000 + (seed % 1000)) + "\"" if is_dup else "null"},
  "similar_incidents": [{{"incident_id": "INC-{10000 + (seed % 1000)}", "similarity_score": {similarity / 100}, "reason": "Similar error patterns and affected services"}}],
  "confidence": {0.70 + (seed % 30) / 100},
  "recommendation": "{'Link to existing incident' if is_dup else 'Create new incident'}"
}}'''
    
    def _route_response(self, prompt: str, seed: int) -> str:
        """Generate routing response in JSON format."""
        teams = ['Database Team', 'Network Operations', 'Application Support', 'Infrastructure', 'Security Team']
        team_idx = seed % len(teams)
        
        if 'database' in prompt.lower():
            team_idx = 0
        elif 'network' in prompt.lower():
            team_idx = 1
        
        return f'''{{
  "assigned_team": "{teams[team_idx]}",
  "sla_hours": {2 + (seed % 6)},
  "priority": {1 + (seed % 3)},
  "escalation_required": {str(seed % 2 == 0).lower()},
  "reasoning": "Based on incident characteristics, {teams[team_idx]} has the expertise to resolve this issue.",
  "confidence": {0.80 + (seed % 20) / 100}
}}'''
    
    def _parse_logs_response(self, prompt: str, seed: int) -> str:
        """Generate log analysis response in JSON format."""
        error_types = ['ConnectionTimeout', 'NullPointerException', 'OutOfMemoryError', 'PermissionDenied']
        error_idx = seed % len(error_types)
        
        return f'''{{
  "total_errors": {10 + (seed % 100)},
  "error_types": {{"{error_types[error_idx]}": {5 + (seed % 50)}}},
  "patterns": [{{
    "pattern_type": "Spike detected",
    "occurrences": {10 + (seed % 50)},
    "first_seen": "2024-01-27T10:00:00Z",
    "last_seen": "2024-01-27T14:00:00Z",
    "affected_services": ["service-1", "service-2"],
    "severity": "high"
  }}],
  "time_range": {{"start": "2024-01-27T10:00:00Z", "end": "2024-01-27T14:00:00Z"}},
  "key_findings": ["Error spike correlates with deployment", "Multiple services affected"]
}}'''
    
    def _detect_patterns_response(self, prompt: str, seed: int) -> str:
        """Generate pattern detection response."""
        patterns = ['Periodic spikes', 'Gradual degradation', 'Sudden spike', 'Cascading failures']
        pattern_idx = seed % len(patterns)
        
        return f'''{{
  "patterns": [{{
    "pattern_type": "{patterns[pattern_idx]}",
    "occurrences": {5 + (seed % 20)},
    "first_seen": "2024-01-27T10:00:00Z",
    "last_seen": "2024-01-27T14:00:00Z",
    "affected_services": ["service-1"],
    "severity": "high"
  }}],
  "anomaly_score": {0.70 + (seed % 30) / 100},
  "confidence": {0.75 + (seed % 25) / 100}
}}'''
    
    def _correlate_response(self, prompt: str, seed: int) -> str:
        """Generate correlation response in JSON format."""
        return f'''{{
  "correlated_events": ["event-1", "event-2", "event-3"],
  "correlation_strength": {0.70 + (seed % 30) / 100},
  "time_window_minutes": {5 + (seed % 15)},
  "causal_chain": ["Deployment", "Config Change", "Service Restart", "Error Spike"],
  "confidence": {0.75 + (seed % 25) / 100}
}}'''
    
    def _hypothesize_response(self, prompt: str, seed: int) -> str:
        """Generate RCA hypothesis in JSON format."""
        hypotheses = [
            'Database connection pool exhaustion',
            'Memory leak in recent deployment',
            'Network configuration issue',
            'Cache invalidation problem'
        ]
        hyp_idx = seed % len(hypotheses)
        
        return f'''{{
  "hypothesis": "{hypotheses[hyp_idx]}",
  "confidence": {0.70 + (seed % 30) / 100},
  "supporting_evidence": [{{
    "evidence_type": "log",
    "source": "application-logs",
    "content": "Connection timeout errors",
    "timestamp": "2024-01-27T12:00:00Z",
    "confidence": 0.85,
    "relevance_score": 0.90
  }}],
  "contradicting_evidence": [],
  "recommended_actions": ["Rollback deployment", "Increase connection pool size"],
  "estimated_resolution_time_hours": {1 + (seed % 4)}
}}'''
    
    def _validate_response(self, prompt: str, seed: int) -> str:
        """Generate validation response in JSON format."""
        is_valid = seed % 2 == 0
        
        return f'''{{
  "is_valid": {str(is_valid).lower()},
  "confidence": {0.70 + (seed % 30) / 100},
  "evidence_strength": {0.65 + (seed % 35) / 100},
  "contradictions_found": {0 if is_valid else 1 + (seed % 3)},
  "recommendation": "{'Proceed with proposed fix' if is_valid else 'Investigate further'}",
  "risk_level": "{'low' if is_valid else 'medium'}"
}}'''
    
    def _generic_response(self, prompt: str, seed: int) -> str:
        """Generic response for unknown task types."""
        return f'''{{
  "status": "completed",
  "confidence": {0.60 + (seed % 40) / 100},
  "result": "Analysis completed based on provided input.",
  "recommendation": "Review results and proceed with next steps."
}}'''
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type for LangChain."""
        return "mock"
    
    def get_num_tokens(self, text: str) -> int:
        """Estimate token count."""
        return len(text.split())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_calls': self.call_count,
            'total_tokens': self.total_tokens,
            'total_cost': 0.0,
            'model': 'MockLLM',
            'mode': 'deterministic' if self.deterministic else 'probabilistic'
        }


def get_llm(force_mock: bool = False, deterministic: bool = True, verbose: bool = True) -> BaseLanguageModel:
    """
    Get LLM instance - MockLLM or ChatOpenAI based on environment.
    
    Args:
        force_mock: Force use of MockLLM even if API key present
        deterministic: Use deterministic mode for MockLLM
        verbose: Print initialization info
    
    Returns:
        LangChain-compatible LLM instance
    """
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if force_mock or not api_key:
        if verbose:
            if force_mock:
                print("🤖 Running with MockLLM (forced)")
            else:
                print("🤖 Running with MockLLM (no API key found)")
            print(f"   Mode: {'Deterministic' if deterministic else 'Probabilistic'}")
        return MockLLM(deterministic=deterministic)
    
    else:
        if not LANGCHAIN_AVAILABLE:
            if verbose:
                print("⚠️  LangChain not available, falling back to MockLLM")
            return MockLLM(deterministic=deterministic)
        
        try:
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            base_url = os.getenv('OPENAI_BASE_URL')
            
            kwargs = {
                'model': model,
                'temperature': 0.3,
                'api_key': api_key
            }
            
            if base_url:
                kwargs['base_url'] = base_url
            
            if verbose:
                print(f"🚀 Running with ChatOpenAI")
                print(f"   Model: {model}")
                if base_url:
                    print(f"   Base URL: {base_url}")
            
            return ChatOpenAI(**kwargs)
        
        except Exception as e:
            if verbose:
                print(f"⚠️  Failed to initialize ChatOpenAI: {e}")
                print("🤖 Falling back to MockLLM")
            return MockLLM(deterministic=deterministic)


def print_llm_stats(llm: BaseLanguageModel) -> None:
    """Print LLM usage statistics."""
    if isinstance(llm, MockLLM):
        stats = llm.get_stats()
        print("\n" + "="*50)
        print("📊 LLM Usage Statistics")
        print("="*50)
        print(f"Model: {stats['model']}")
        print(f"Total Calls: {stats['total_calls']}")
        print(f"Total Tokens: {stats['total_tokens']}")
        print(f"Total Cost: ${stats['total_cost']:.4f}")
        print(f"Mode: {stats['mode']}")
        print("="*50 + "\n")
    else:
        print("\n" + "="*50)
        print("📊 LLM Usage Statistics")
        print("="*50)
        print(f"Model: ChatOpenAI")
        print("Note: Use LangSmith or callbacks for detailed tracking")
        print("="*50 + "\n")
