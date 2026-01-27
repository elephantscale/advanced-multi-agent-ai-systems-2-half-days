from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import json
import pandas as pd
from datetime import datetime


class IncidentSearchInput(BaseModel):
    query: str = Field(..., description="Search query for incidents")
    limit: int = Field(default=5, description="Maximum number of results")


class IncidentSearchTool(BaseTool):
    name: str = "search_incidents"
    description: str = "Search for similar incidents in the knowledge base. Use this to find duplicates or related incidents."
    args_schema: type[BaseModel] = IncidentSearchInput
    incident_db: List[Dict[str, Any]] = Field(default_factory=list)
    
    def _run(self, query: str, limit: int = 5) -> str:
        """Search incidents (read-only operation)."""
        if not self.incident_db:
            return json.dumps({"results": [], "message": "No incidents in database"})
        
        results = []
        query_lower = query.lower()
        
        for incident in self.incident_db[:limit]:
            title = incident.get('title', '').lower()
            description = incident.get('description', '').lower()
            
            if query_lower in title or query_lower in description:
                results.append({
                    'incident_id': incident.get('id', 'unknown'),
                    'title': incident.get('title', ''),
                    'severity': incident.get('severity', ''),
                    'similarity_score': 0.85
                })
        
        return json.dumps({"results": results, "count": len(results)})


class PolicyLookupInput(BaseModel):
    policy_type: str = Field(..., description="Type of policy to lookup (sla, escalation, routing)")
    severity: Optional[str] = Field(None, description="Severity level for policy lookup")


class PolicyLookupTool(BaseTool):
    name: str = "lookup_policy"
    description: str = "Look up organizational policies for SLA, escalation, and routing. Read-only operation."
    args_schema: type[BaseModel] = PolicyLookupInput
    policies: Dict[str, Any] = Field(default_factory=dict)
    
    def _run(self, policy_type: str, severity: Optional[str] = None) -> str:
        """Lookup policy (read-only operation)."""
        if not self.policies:
            return json.dumps({
                "policy_type": policy_type,
                "data": {"sla_hours": 4, "escalation_required": False},
                "source": "default"
            })
        
        policy_data = self.policies.get(policy_type, {})
        
        if severity and isinstance(policy_data, dict):
            policy_data = policy_data.get(severity, policy_data)
        
        return json.dumps({
            "policy_type": policy_type,
            "severity": severity,
            "data": policy_data,
            "source": "knowledge_base"
        })


class LogQueryInput(BaseModel):
    service: str = Field(..., description="Service name to query logs for")
    time_range_minutes: int = Field(default=60, description="Time range in minutes")
    error_level: Optional[str] = Field(None, description="Filter by error level (ERROR, WARN, INFO)")


class LogQueryTool(BaseTool):
    name: str = "query_logs"
    description: str = "Query logs for a specific service and time range. Read-only operation."
    args_schema: type[BaseModel] = LogQueryInput
    log_data: str = Field(default="")
    
    def _run(self, service: str, time_range_minutes: int = 60, error_level: Optional[str] = None) -> str:
        """Query logs (read-only operation)."""
        if not self.log_data:
            return json.dumps({
                "service": service,
                "time_range_minutes": time_range_minutes,
                "entries": [],
                "message": "No log data available"
            })
        
        lines = self.log_data.split('\n')
        filtered_lines = []
        
        for line in lines:
            if service.lower() in line.lower():
                if error_level is None or error_level.upper() in line.upper():
                    filtered_lines.append(line)
        
        return json.dumps({
            "service": service,
            "time_range_minutes": time_range_minutes,
            "error_level": error_level,
            "entries": filtered_lines[:20],
            "total_count": len(filtered_lines)
        })


class MetricQueryInput(BaseModel):
    service: str = Field(..., description="Service name to query metrics for")
    metric_name: str = Field(..., description="Metric name (cpu, memory, latency)")
    time_range_minutes: int = Field(default=60, description="Time range in minutes")


class MetricQueryTool(BaseTool):
    name: str = "query_metrics"
    description: str = "Query metrics for a specific service. Read-only operation."
    args_schema: type[BaseModel] = MetricQueryInput
    metrics_data: Optional[pd.DataFrame] = None
    
    def _run(self, service: str, metric_name: str, time_range_minutes: int = 60) -> str:
        """Query metrics (read-only operation)."""
        if self.metrics_data is None or self.metrics_data.empty:
            return json.dumps({
                "service": service,
                "metric_name": metric_name,
                "data_points": [],
                "statistics": {"avg": 0, "max": 0, "min": 0},
                "message": "No metrics data available"
            })
        
        try:
            filtered = self.metrics_data[
                (self.metrics_data['service'] == service) &
                (self.metrics_data['metric'] == metric_name)
            ]
            
            if filtered.empty:
                return json.dumps({
                    "service": service,
                    "metric_name": metric_name,
                    "data_points": [],
                    "statistics": {"avg": 0, "max": 0, "min": 0}
                })
            
            values = filtered['value'].tolist()
            
            return json.dumps({
                "service": service,
                "metric_name": metric_name,
                "data_points": values[:50],
                "statistics": {
                    "avg": float(filtered['value'].mean()),
                    "max": float(filtered['value'].max()),
                    "min": float(filtered['value'].min()),
                    "count": len(values)
                }
            })
        except Exception as e:
            return json.dumps({"error": str(e)})


class EscalateIncidentInput(BaseModel):
    incident_id: str = Field(..., description="Incident ID to escalate")
    reason: str = Field(..., description="Reason for escalation")
    target_team: str = Field(..., description="Team to escalate to")


class EscalateIncidentTool(BaseTool):
    name: str = "escalate_incident"
    description: str = "Escalate an incident to a higher-level team. REQUIRES APPROVAL - use only when necessary."
    args_schema: type[BaseModel] = EscalateIncidentInput
    require_approval: bool = Field(default=True)
    escalation_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    def _run(self, incident_id: str, reason: str, target_team: str) -> str:
        """Escalate incident (controlled write operation)."""
        if self.require_approval:
            return json.dumps({
                "status": "pending_approval",
                "incident_id": incident_id,
                "reason": reason,
                "target_team": target_team,
                "message": "Escalation requires human approval. Request submitted.",
                "approval_required": True
            })
        
        escalation_record = {
            "incident_id": incident_id,
            "reason": reason,
            "target_team": target_team,
            "timestamp": datetime.now().isoformat(),
            "status": "escalated"
        }
        
        self.escalation_log.append(escalation_record)
        
        return json.dumps({
            "status": "escalated",
            "incident_id": incident_id,
            "target_team": target_team,
            "timestamp": escalation_record["timestamp"]
        })


class UpdateIncidentInput(BaseModel):
    incident_id: str = Field(..., description="Incident ID to update")
    field: str = Field(..., description="Field to update (status, priority, notes)")
    value: str = Field(..., description="New value for the field")


class UpdateIncidentTool(BaseTool):
    name: str = "update_incident"
    description: str = "Update incident fields. REQUIRES APPROVAL for critical changes."
    args_schema: type[BaseModel] = UpdateIncidentInput
    require_approval: bool = Field(default=True)
    update_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    def _run(self, incident_id: str, field: str, value: str) -> str:
        """Update incident (controlled write operation)."""
        critical_fields = ['status', 'severity', 'assigned_team']
        
        if field in critical_fields and self.require_approval:
            return json.dumps({
                "status": "pending_approval",
                "incident_id": incident_id,
                "field": field,
                "value": value,
                "message": f"Update to {field} requires human approval.",
                "approval_required": True
            })
        
        update_record = {
            "incident_id": incident_id,
            "field": field,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "status": "updated"
        }
        
        self.update_log.append(update_record)
        
        return json.dumps({
            "status": "updated",
            "incident_id": incident_id,
            "field": field,
            "value": value,
            "timestamp": update_record["timestamp"]
        })


def create_tool_allowlist(tools: List[BaseTool], allowed_tool_names: List[str]) -> List[BaseTool]:
    """Filter tools to only allowed ones (guardrail)."""
    return [tool for tool in tools if tool.name in allowed_tool_names]


def get_default_tools(
    incident_db: Optional[List[Dict[str, Any]]] = None,
    policies: Optional[Dict[str, Any]] = None,
    log_data: Optional[str] = None,
    metrics_data: Optional[pd.DataFrame] = None,
    allow_writes: bool = False
) -> List[BaseTool]:
    """
    Get default tool set with data injected.
    
    Args:
        incident_db: Incident database for search
        policies: Policy knowledge base
        log_data: Log data for queries
        metrics_data: Metrics data for queries
        allow_writes: Whether to include write tools
    
    Returns:
        List of configured tools
    """
    tools = [
        IncidentSearchTool(incident_db=incident_db or []),
        PolicyLookupTool(policies=policies or {}),
        LogQueryTool(log_data=log_data or ""),
        MetricQueryTool(metrics_data=metrics_data)
    ]
    
    if allow_writes:
        tools.extend([
            EscalateIncidentTool(require_approval=True),
            UpdateIncidentTool(require_approval=True)
        ])
    
    return tools


def get_read_only_tools(
    incident_db: Optional[List[Dict[str, Any]]] = None,
    policies: Optional[Dict[str, Any]] = None,
    log_data: Optional[str] = None,
    metrics_data: Optional[pd.DataFrame] = None
) -> List[BaseTool]:
    """Get only read-only tools (safest for automation)."""
    return [
        IncidentSearchTool(incident_db=incident_db or []),
        PolicyLookupTool(policies=policies or {}),
        LogQueryTool(log_data=log_data or ""),
        MetricQueryTool(metrics_data=metrics_data)
    ]
