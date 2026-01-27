from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from collections import Counter, defaultdict
from src.schemas import Evidence, RCAHypothesis


class LogAnalyzer:
    """Analyze logs for RCA."""
    
    def __init__(self):
        self.error_patterns = {
            'connection_timeout': r'(connection|connect).*(timeout|timed out)',
            'out_of_memory': r'(out of memory|oom|memory exhausted)',
            'null_pointer': r'(nullpointer|null pointer|npe)',
            'permission_denied': r'(permission denied|access denied|forbidden)',
            'resource_exhausted': r'(resource exhausted|too many|limit exceeded)',
            'deadlock': r'(deadlock|lock timeout)',
            'disk_full': r'(disk full|no space left)',
            'network_error': r'(network error|connection refused|unreachable)'
        }
    
    def parse_logs(self, log_text: str) -> Dict[str, Any]:
        """Parse logs and extract key information."""
        lines = log_text.strip().split('\n')
        
        error_lines = []
        warn_lines = []
        timestamps = []
        services = set()
        error_types = Counter()
        
        for line in lines:
            if not line.strip():
                continue
            
            if 'ERROR' in line.upper() or 'CRITICAL' in line.upper():
                error_lines.append(line)
            elif 'WARN' in line.upper():
                warn_lines.append(line)
            
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', line)
            if timestamp_match:
                timestamps.append(timestamp_match.group(0))
            
            service_match = re.search(r'service[_-]?\w+', line, re.IGNORECASE)
            if service_match:
                services.add(service_match.group(0))
            
            for error_type, pattern in self.error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    error_types[error_type] += 1
        
        return {
            'total_lines': len(lines),
            'error_count': len(error_lines),
            'warning_count': len(warn_lines),
            'error_types': dict(error_types),
            'affected_services': list(services),
            'time_range': {
                'start': timestamps[0] if timestamps else None,
                'end': timestamps[-1] if timestamps else None
            },
            'sample_errors': error_lines[:5]
        }
    
    def detect_patterns(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect patterns in log analysis."""
        patterns = []
        
        error_types = log_analysis.get('error_types', {})
        if error_types:
            most_common = max(error_types.items(), key=lambda x: x[1])
            patterns.append({
                'pattern_type': 'dominant_error',
                'error_type': most_common[0],
                'occurrences': most_common[1],
                'severity': 'high' if most_common[1] > 10 else 'medium'
            })
        
        error_count = log_analysis.get('error_count', 0)
        if error_count > 50:
            patterns.append({
                'pattern_type': 'error_spike',
                'occurrences': error_count,
                'severity': 'critical'
            })
        
        services = log_analysis.get('affected_services', [])
        if len(services) > 3:
            patterns.append({
                'pattern_type': 'cascading_failure',
                'affected_services': services,
                'severity': 'high'
            })
        
        return patterns


class EvidenceCollector:
    """Collect and organize evidence for RCA."""
    
    def __init__(self):
        self.evidence: List[Evidence] = []
    
    def add_log_evidence(self, log_analysis: Dict[str, Any], confidence: float = 0.85):
        """Add evidence from log analysis."""
        error_types = log_analysis.get('error_types', {})
        if error_types:
            most_common = max(error_types.items(), key=lambda x: x[1])
            
            evidence = Evidence(
                evidence_type='log',
                source='application_logs',
                content=f"Detected {most_common[1]} occurrences of {most_common[0]}",
                timestamp=datetime.now().isoformat(),
                confidence=confidence,
                relevance_score=0.90
            )
            self.evidence.append(evidence)
    
    def add_metric_evidence(self, metric_data: Dict[str, Any], confidence: float = 0.80):
        """Add evidence from metrics."""
        evidence = Evidence(
            evidence_type='metric',
            source='monitoring_system',
            content=f"Metric anomaly detected: {metric_data.get('metric_name', 'unknown')}",
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            relevance_score=0.85
        )
        self.evidence.append(evidence)
    
    def add_event_evidence(self, event_data: Dict[str, Any], confidence: float = 0.90):
        """Add evidence from events."""
        evidence = Evidence(
            evidence_type='event',
            source='event_log',
            content=f"Event detected: {event_data.get('event_type', 'unknown')}",
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            relevance_score=0.95
        )
        self.evidence.append(evidence)
    
    def add_pattern_evidence(self, pattern_data: Dict[str, Any], confidence: float = 0.75):
        """Add evidence from pattern detection."""
        evidence = Evidence(
            evidence_type='pattern',
            source='pattern_detector',
            content=f"Pattern detected: {pattern_data.get('pattern_type', 'unknown')}",
            timestamp=datetime.now().isoformat(),
            confidence=confidence,
            relevance_score=0.80
        )
        self.evidence.append(evidence)
    
    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary of collected evidence."""
        by_type = defaultdict(int)
        for ev in self.evidence:
            by_type[ev.evidence_type] += 1
        
        avg_confidence = sum(ev.confidence for ev in self.evidence) / len(self.evidence) if self.evidence else 0.0
        avg_relevance = sum(ev.relevance_score for ev in self.evidence) / len(self.evidence) if self.evidence else 0.0
        
        return {
            'total_evidence': len(self.evidence),
            'by_type': dict(by_type),
            'avg_confidence': avg_confidence,
            'avg_relevance': avg_relevance,
            'evidence_list': [ev.dict() for ev in self.evidence]
        }


class HypothesisGenerator:
    """Generate RCA hypotheses based on evidence."""
    
    def __init__(self):
        self.hypothesis_templates = {
            'connection_timeout': {
                'hypothesis': 'Database connection pool exhaustion due to increased load',
                'recommended_actions': [
                    'Increase connection pool size',
                    'Review recent traffic patterns',
                    'Check for connection leaks'
                ]
            },
            'out_of_memory': {
                'hypothesis': 'Memory leak in recently deployed code',
                'recommended_actions': [
                    'Rollback recent deployment',
                    'Analyze heap dumps',
                    'Review code changes for memory issues'
                ]
            },
            'resource_exhausted': {
                'hypothesis': 'Resource limits exceeded due to traffic spike',
                'recommended_actions': [
                    'Scale up resources',
                    'Implement rate limiting',
                    'Review resource allocation'
                ]
            },
            'cascading_failure': {
                'hypothesis': 'Cascading failure across multiple services',
                'recommended_actions': [
                    'Implement circuit breakers',
                    'Review service dependencies',
                    'Add fallback mechanisms'
                ]
            }
        }
    
    def generate_hypothesis(
        self,
        log_analysis: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        evidence: List[Evidence]
    ) -> RCAHypothesis:
        """Generate hypothesis based on analysis."""
        error_types = log_analysis.get('error_types', {})
        
        if error_types:
            most_common_error = max(error_types.items(), key=lambda x: x[1])[0]
            
            if most_common_error in self.hypothesis_templates:
                template = self.hypothesis_templates[most_common_error]
                hypothesis_text = template['hypothesis']
                actions = template['recommended_actions']
            else:
                hypothesis_text = f"Issue related to {most_common_error} errors"
                actions = ['Investigate error logs', 'Review recent changes']
        else:
            hypothesis_text = "Unable to determine specific root cause from available evidence"
            actions = ['Collect more evidence', 'Expand log analysis']
        
        supporting_evidence = [ev for ev in evidence if ev.confidence > 0.70]
        contradicting_evidence = [ev for ev in evidence if ev.confidence < 0.50]
        
        confidence = sum(ev.confidence for ev in supporting_evidence) / len(supporting_evidence) if supporting_evidence else 0.50
        
        return RCAHypothesis(
            hypothesis=hypothesis_text,
            confidence=min(confidence, 0.95),
            supporting_evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            recommended_actions=actions,
            estimated_resolution_time_hours=2 if confidence > 0.80 else 4
        )


class HypothesisValidator:
    """Validate RCA hypotheses against evidence."""
    
    def validate(self, hypothesis: RCAHypothesis, additional_checks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate hypothesis."""
        supporting_count = len(hypothesis.supporting_evidence)
        contradicting_count = len(hypothesis.contradicting_evidence)
        
        evidence_strength = supporting_count / (supporting_count + contradicting_count) if (supporting_count + contradicting_count) > 0 else 0.5
        
        is_valid = (
            hypothesis.confidence > 0.70 and
            evidence_strength > 0.70 and
            contradicting_count < 2
        )
        
        risk_level = 'low' if is_valid and hypothesis.confidence > 0.85 else 'medium' if is_valid else 'high'
        
        recommendation = 'Proceed with proposed fix' if is_valid else 'Investigate further before applying fix'
        
        return {
            'is_valid': is_valid,
            'confidence': hypothesis.confidence,
            'evidence_strength': evidence_strength,
            'contradictions_found': contradicting_count,
            'recommendation': recommendation,
            'risk_level': risk_level
        }


def perform_rca(
    log_text: str,
    metric_data: Optional[Dict[str, Any]] = None,
    event_data: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Perform complete RCA analysis."""
    analyzer = LogAnalyzer()
    collector = EvidenceCollector()
    generator = HypothesisGenerator()
    validator = HypothesisValidator()
    
    log_analysis = analyzer.parse_logs(log_text)
    
    patterns = analyzer.detect_patterns(log_analysis)
    
    collector.add_log_evidence(log_analysis)
    
    for pattern in patterns:
        collector.add_pattern_evidence(pattern)
    
    if metric_data:
        collector.add_metric_evidence(metric_data)
    
    if event_data:
        for event in event_data:
            collector.add_event_evidence(event)
    
    evidence_summary = collector.get_evidence_summary()
    
    hypothesis = generator.generate_hypothesis(
        log_analysis,
        patterns,
        collector.evidence
    )
    
    validation = validator.validate(hypothesis)
    
    return {
        'log_analysis': log_analysis,
        'patterns': patterns,
        'evidence_summary': evidence_summary,
        'hypothesis': hypothesis.dict(),
        'validation': validation,
        'rca_complete': True,
        'timestamp': datetime.now().isoformat()
    }
