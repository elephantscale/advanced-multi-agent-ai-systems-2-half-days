from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentCategory(str, Enum):
    DATABASE = "Database"
    NETWORK = "Network"
    APPLICATION = "Application"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    UNKNOWN = "Unknown"


class ClassificationResult(BaseModel):
    severity: SeverityLevel = Field(..., description="Incident severity level")
    category: IncidentCategory = Field(..., description="Incident category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Explanation for classification")
    requires_escalation: bool = Field(default=False, description="Whether immediate escalation is needed")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v


class DuplicateMatch(BaseModel):
    incident_id: str = Field(..., description="ID of potentially duplicate incident")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    reason: str = Field(..., description="Why this is considered similar")


class DeduplicationResult(BaseModel):
    is_duplicate: bool = Field(..., description="Whether this is a duplicate")
    duplicate_of: Optional[str] = Field(None, description="ID of original incident if duplicate")
    similar_incidents: List[DuplicateMatch] = Field(default_factory=list, description="List of similar incidents")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in deduplication decision")
    recommendation: str = Field(..., description="Recommended action")


class RoutingDecision(BaseModel):
    assigned_team: str = Field(..., description="Team to handle the incident")
    sla_hours: int = Field(..., gt=0, description="SLA in hours")
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest)")
    escalation_required: bool = Field(default=False, description="Whether escalation is needed")
    reasoning: str = Field(..., description="Explanation for routing decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in routing")


class LogPattern(BaseModel):
    pattern_type: str = Field(..., description="Type of pattern detected")
    occurrences: int = Field(..., ge=0, description="Number of occurrences")
    first_seen: str = Field(..., description="Timestamp of first occurrence")
    last_seen: str = Field(..., description="Timestamp of last occurrence")
    affected_services: List[str] = Field(default_factory=list, description="Services affected")
    severity: str = Field(..., description="Pattern severity")


class LogAnalysisResult(BaseModel):
    total_errors: int = Field(..., ge=0, description="Total error count")
    error_types: Dict[str, int] = Field(default_factory=dict, description="Error types and counts")
    patterns: List[LogPattern] = Field(default_factory=list, description="Detected patterns")
    time_range: Dict[str, str] = Field(default_factory=dict, description="Time range of logs")
    key_findings: List[str] = Field(default_factory=list, description="Key findings from analysis")


class CorrelationResult(BaseModel):
    correlated_events: List[str] = Field(default_factory=list, description="List of correlated event IDs")
    correlation_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of correlation")
    time_window_minutes: int = Field(..., gt=0, description="Time window for correlation")
    causal_chain: List[str] = Field(default_factory=list, description="Suspected causal chain")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in correlation")


class Evidence(BaseModel):
    evidence_type: Literal["log", "metric", "event", "pattern"] = Field(..., description="Type of evidence")
    source: str = Field(..., description="Source of evidence")
    content: str = Field(..., description="Evidence content")
    timestamp: str = Field(..., description="When evidence was collected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in evidence")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to incident")


class RCAHypothesis(BaseModel):
    hypothesis: str = Field(..., description="Root cause hypothesis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in hypothesis")
    supporting_evidence: List[Evidence] = Field(default_factory=list, description="Supporting evidence")
    contradicting_evidence: List[Evidence] = Field(default_factory=list, description="Contradicting evidence")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    estimated_resolution_time_hours: Optional[int] = Field(None, description="Estimated time to resolve")


class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether hypothesis is valid")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in validation")
    evidence_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of supporting evidence")
    contradictions_found: int = Field(..., ge=0, description="Number of contradictions")
    recommendation: str = Field(..., description="Validation recommendation")
    risk_level: Literal["low", "medium", "high"] = Field(..., description="Risk level of proceeding")


class WorkflowState(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    trace_id: str = Field(..., description="Trace ID for observability")
    current_step: str = Field(..., description="Current workflow step")
    classification: Optional[ClassificationResult] = None
    deduplication: Optional[DeduplicationResult] = None
    routing: Optional[RoutingDecision] = None
    log_analysis: Optional[LogAnalysisResult] = None
    correlation: Optional[CorrelationResult] = None
    hypothesis: Optional[RCAHypothesis] = None
    validation: Optional[ValidationResult] = None
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    step_count: int = Field(default=0, description="Number of steps executed")
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        arbitrary_types_allowed = True


class ToolExecutionResult(BaseModel):
    tool_name: str = Field(..., description="Name of tool executed")
    success: bool = Field(..., description="Whether execution succeeded")
    result: Any = Field(None, description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class GuardrailViolation(BaseModel):
    violation_type: str = Field(..., description="Type of guardrail violation")
    severity: Literal["warning", "error", "critical"] = Field(..., description="Violation severity")
    message: str = Field(..., description="Violation message")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    action_taken: str = Field(..., description="Action taken in response")


class EvaluationMetrics(BaseModel):
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Classification accuracy")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    avg_processing_time_seconds: float = Field(..., gt=0, description="Average processing time")
    total_incidents_processed: int = Field(..., ge=0, description="Total incidents processed")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    guardrail_violations: int = Field(default=0, ge=0, description="Number of guardrail violations")
