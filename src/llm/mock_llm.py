import hashlib
import random
from typing import Dict, List, Optional, Any
from datetime import datetime


class MockLLM:
    
    def __init__(self, deterministic: bool = True, seed: int = 42):
        self.deterministic = deterministic
        self.seed = seed
        self.call_count = 0
        self.total_tokens = 0
        
        if not deterministic:
            random.seed(seed)
        
        self.response_templates = {
            'classify': self._classify_response,
            'deduplicate': self._deduplicate_response,
            'route': self._route_response,
            'parse_logs': self._parse_logs_response,
            'detect_patterns': self._detect_patterns_response,
            'correlate': self._correlate_response,
            'hypothesize': self._hypothesize_response,
            'validate': self._validate_response,
            'summarize': self._summarize_response,
            'analyze': self._analyze_response,
        }
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        self.call_count += 1
        
        task_type = self._detect_task_type(prompt)
        
        if self.deterministic:
            response_text = self._deterministic_response(prompt, task_type)
        else:
            response_text = self._probabilistic_response(prompt, task_type)
        
        tokens_used = len(prompt.split()) + len(response_text.split())
        self.total_tokens += tokens_used
        
        return {
            'response': response_text,
            'model': 'MockLLM',
            'tokens': tokens_used,
            'cost': 0.0,
            'timestamp': datetime.now().isoformat(),
            'call_number': self.call_count
        }
    
    def _detect_task_type(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if 'classify' in prompt_lower or 'severity' in prompt_lower or 'priority' in prompt_lower:
            return 'classify'
        elif 'duplicate' in prompt_lower or 'similar' in prompt_lower:
            return 'deduplicate'
        elif 'route' in prompt_lower or 'assign' in prompt_lower or 'team' in prompt_lower:
            return 'route'
        elif 'parse' in prompt_lower or 'extract' in prompt_lower:
            return 'parse_logs'
        elif 'pattern' in prompt_lower or 'anomaly' in prompt_lower:
            return 'detect_patterns'
        elif 'correlate' in prompt_lower or 'relationship' in prompt_lower:
            return 'correlate'
        elif 'hypothesis' in prompt_lower or 'root cause' in prompt_lower:
            return 'hypothesize'
        elif 'validate' in prompt_lower or 'verify' in prompt_lower:
            return 'validate'
        elif 'summarize' in prompt_lower or 'summary' in prompt_lower:
            return 'summarize'
        else:
            return 'analyze'
    
    def _deterministic_response(self, prompt: str, task_type: str) -> str:
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        hash_int = int(prompt_hash[:8], 16)
        
        if task_type in self.response_templates:
            return self.response_templates[task_type](prompt, hash_int)
        else:
            return self._generic_response(prompt, hash_int)
    
    def _probabilistic_response(self, prompt: str, task_type: str) -> str:
        if task_type in self.response_templates:
            return self.response_templates[task_type](prompt, random.randint(0, 1000000))
        else:
            return self._generic_response(prompt, random.randint(0, 1000000))
    
    def _classify_response(self, prompt: str, seed: int) -> str:
        severities = ['P0', 'P1', 'P2', 'P3', 'P4']
        categories = ['Database', 'Network', 'Application', 'Infrastructure', 'Security']
        
        severity_idx = seed % len(severities)
        category_idx = (seed // 10) % len(categories)
        
        if 'database' in prompt.lower() or 'query' in prompt.lower():
            category_idx = 0
        elif 'network' in prompt.lower() or 'connection' in prompt.lower():
            category_idx = 1
        elif 'crash' in prompt.lower() or 'error' in prompt.lower():
            category_idx = 2
        
        if 'critical' in prompt.lower() or 'outage' in prompt.lower():
            severity_idx = 0
        elif 'high' in prompt.lower() or 'urgent' in prompt.lower():
            severity_idx = 1
        
        return f"""Classification Result:
- Severity: {severities[severity_idx]}
- Category: {categories[category_idx]}
- Confidence: {85 + (seed % 15)}%
- Reasoning: Based on incident description, this appears to be a {severities[severity_idx]} {categories[category_idx]} issue requiring immediate attention."""
    
    def _deduplicate_response(self, prompt: str, seed: int) -> str:
        similarity_score = 60 + (seed % 40)
        
        if 'similar' in prompt.lower():
            return f"""Deduplication Analysis:
- Similar incidents found: {1 + (seed % 3)}
- Highest similarity: {similarity_score}%
- Recommendation: {'DUPLICATE - Link to existing incident' if similarity_score > 80 else 'UNIQUE - Create new incident'}
- Related incident IDs: INC-{10000 + (seed % 1000)}, INC-{10000 + ((seed + 100) % 1000)}"""
        else:
            return f"""Deduplication Analysis:
- Similar incidents found: 0
- Recommendation: UNIQUE - Create new incident
- No closely related incidents detected"""
    
    def _route_response(self, prompt: str, seed: int) -> str:
        teams = ['Database Team', 'Network Operations', 'Application Support', 'Infrastructure', 'Security Team']
        team_idx = seed % len(teams)
        
        if 'database' in prompt.lower():
            team_idx = 0
        elif 'network' in prompt.lower():
            team_idx = 1
        elif 'security' in prompt.lower():
            team_idx = 4
        
        return f"""Routing Decision:
- Assigned Team: {teams[team_idx]}
- Confidence: {80 + (seed % 20)}%
- Escalation Required: {seed % 2 == 0}
- SLA: {2 + (seed % 6)} hours
- Reasoning: Based on incident characteristics, {teams[team_idx]} has the expertise to resolve this issue."""
    
    def _parse_logs_response(self, prompt: str, seed: int) -> str:
        error_types = ['NullPointerException', 'ConnectionTimeout', 'OutOfMemoryError', 'PermissionDenied', 'ResourceExhausted']
        error_idx = seed % len(error_types)
        
        return f"""Log Parsing Results:
- Error Type: {error_types[error_idx]}
- Occurrences: {10 + (seed % 100)}
- First Seen: 2024-01-27 10:{seed % 60:02d}:00
- Last Seen: 2024-01-27 14:{seed % 60:02d}:00
- Affected Services: service-{seed % 5}, service-{(seed + 1) % 5}
- Key Patterns: Spike detected at 12:00, correlates with deployment event"""
    
    def _detect_patterns_response(self, prompt: str, seed: int) -> str:
        patterns = [
            'Periodic spikes every 5 minutes',
            'Gradual degradation over time',
            'Sudden spike followed by recovery',
            'Cascading failures across services',
            'Resource exhaustion pattern'
        ]
        pattern_idx = seed % len(patterns)
        
        return f"""Pattern Detection:
- Primary Pattern: {patterns[pattern_idx]}
- Anomaly Score: {70 + (seed % 30)}%
- Frequency: {1 + (seed % 10)} occurrences per hour
- Affected Metrics: CPU usage, memory consumption, response time
- Correlation: Strong correlation with external API calls"""
    
    def _correlate_response(self, prompt: str, seed: int) -> str:
        return f"""Correlation Analysis:
- Events Correlated: {3 + (seed % 5)}
- Time Window: {5 + (seed % 15)} minutes
- Correlation Strength: {75 + (seed % 25)}%
- Causal Chain Detected: Deployment → Config Change → Service Restart → Error Spike
- Key Finding: All events trace back to deployment at 12:00 UTC"""
    
    def _hypothesize_response(self, prompt: str, seed: int) -> str:
        hypotheses = [
            'Database connection pool exhaustion due to increased load',
            'Memory leak in recently deployed code causing OOM errors',
            'Network configuration change blocking service communication',
            'Cache invalidation issue causing excessive database queries',
            'Rate limiting triggered by unexpected traffic spike'
        ]
        hypothesis_idx = seed % len(hypotheses)
        
        return f"""Root Cause Hypothesis:
- Primary Hypothesis: {hypotheses[hypothesis_idx]}
- Confidence: {70 + (seed % 30)}%
- Supporting Evidence:
  1. Log patterns consistent with hypothesis
  2. Timeline matches deployment window
  3. Similar incidents resolved with same fix
- Recommended Action: Rollback deployment and investigate code changes
- Estimated Resolution Time: {1 + (seed % 4)} hours"""
    
    def _validate_response(self, prompt: str, seed: int) -> str:
        validation_result = seed % 2 == 0
        
        return f"""Validation Results:
- Hypothesis Valid: {validation_result}
- Evidence Strength: {60 + (seed % 40)}%
- Contradictions Found: {0 if validation_result else 1 + (seed % 3)}
- Recommendation: {'PROCEED with proposed fix' if validation_result else 'INVESTIGATE further before applying fix'}
- Risk Assessment: {'Low' if validation_result else 'Medium'} risk of incorrect diagnosis"""
    
    def _summarize_response(self, prompt: str, seed: int) -> str:
        return f"""Incident Summary:
- Duration: {1 + (seed % 8)} hours
- Impact: {100 + (seed % 1000)} users affected
- Root Cause: Configuration issue in deployment
- Resolution: Rollback to previous version
- Prevention: Add pre-deployment validation checks
- Lessons Learned: Improve staging environment testing"""
    
    def _analyze_response(self, prompt: str, seed: int) -> str:
        return f"""Analysis Results:
- Key Findings: {2 + (seed % 5)} critical issues identified
- Severity Assessment: Medium to High
- Recommended Actions:
  1. Immediate: Investigate error logs
  2. Short-term: Apply configuration fix
  3. Long-term: Implement monitoring improvements
- Confidence Level: {70 + (seed % 30)}%"""
    
    def _generic_response(self, prompt: str, seed: int) -> str:
        return f"""MockLLM Response (Generic):
Based on the provided input, I've analyzed the situation and identified key patterns.

Key Observations:
- Pattern ID: {seed % 1000}
- Confidence: {60 + (seed % 40)}%
- Recommendation: Further investigation required

This is a deterministic mock response for testing purposes. In production, this would be replaced with actual LLM analysis.
"""
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_calls': self.call_count,
            'total_tokens': self.total_tokens,
            'total_cost': 0.0,
            'model': 'MockLLM',
            'mode': 'deterministic' if self.deterministic else 'probabilistic'
        }
