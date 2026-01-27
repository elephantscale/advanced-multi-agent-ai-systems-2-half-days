import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd


class TraceLogger:
    """JSONL-based trace logger for observability."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "traces.jsonl"
        self.traces: List[Dict[str, Any]] = []
        self.current_trace_id: Optional[str] = None
        
    def start_trace(self, workflow_name: str, input_data: Dict[str, Any]) -> str:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())
        self.current_trace_id = trace_id
        
        trace_entry = {
            "trace_id": trace_id,
            "event_type": "trace_start",
            "workflow_name": workflow_name,
            "input_data": input_data,
            "timestamp": datetime.now().isoformat(),
            "start_time": datetime.now().timestamp()
        }
        
        self.traces.append(trace_entry)
        self._write_to_file(trace_entry)
        
        return trace_id
    
    def log_node_start(self, node_name: str, state: Dict[str, Any]):
        """Log node execution start."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "node_start",
            "node_name": node_name,
            "state_snapshot": self._sanitize_state(state),
            "timestamp": datetime.now().isoformat(),
            "start_time": datetime.now().timestamp()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def log_node_end(self, node_name: str, state: Dict[str, Any], duration_ms: float):
        """Log node execution end."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "node_end",
            "node_name": node_name,
            "state_snapshot": self._sanitize_state(state),
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], result: Any, duration_ms: float):
        """Log tool execution."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "tool_call",
            "tool_name": tool_name,
            "inputs": inputs,
            "result": str(result)[:500],  # Truncate long results
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def log_state_transition(self, from_node: str, to_node: str, decision: Optional[str] = None):
        """Log state transition."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "state_transition",
            "from_node": from_node,
            "to_node": to_node,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def log_error(self, node_name: str, error: str, state: Dict[str, Any]):
        """Log error."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "error",
            "node_name": node_name,
            "error": error,
            "state_snapshot": self._sanitize_state(state),
            "timestamp": datetime.now().isoformat()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def log_guardrail_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log guardrail violation."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "guardrail_violation",
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
    
    def end_trace(self, status: str, output_data: Optional[Dict[str, Any]] = None):
        """End the current trace."""
        if not self.current_trace_id:
            return
        
        entry = {
            "trace_id": self.current_trace_id,
            "event_type": "trace_end",
            "status": status,
            "output_data": output_data,
            "timestamp": datetime.now().isoformat(),
            "end_time": datetime.now().timestamp()
        }
        
        self.traces.append(entry)
        self._write_to_file(entry)
        
        self.current_trace_id = None
    
    def _sanitize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize state for logging (remove large objects)."""
        sanitized = {}
        for key, value in state.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = {k: str(v)[:100] for k, v in list(value.items())[:5]}
            elif isinstance(value, list):
                sanitized[key] = f"<list of {len(value)} items>"
            else:
                sanitized[key] = str(type(value))
        return sanitized
    
    def _write_to_file(self, entry: Dict[str, Any]):
        """Write entry to JSONL file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write to log file: {e}")
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get summary for a specific trace."""
        trace_entries = [t for t in self.traces if t.get('trace_id') == trace_id]
        
        if not trace_entries:
            return {"error": "Trace not found"}
        
        start_entry = next((t for t in trace_entries if t['event_type'] == 'trace_start'), None)
        end_entry = next((t for t in trace_entries if t['event_type'] == 'trace_end'), None)
        
        node_timings = {}
        for entry in trace_entries:
            if entry['event_type'] == 'node_end':
                node_name = entry['node_name']
                duration = entry['duration_ms']
                node_timings[node_name] = node_timings.get(node_name, 0) + duration
        
        tool_calls = [t for t in trace_entries if t['event_type'] == 'tool_call']
        errors = [t for t in trace_entries if t['event_type'] == 'error']
        violations = [t for t in trace_entries if t['event_type'] == 'guardrail_violation']
        
        total_duration = 0
        if start_entry and end_entry:
            total_duration = (end_entry['end_time'] - start_entry['start_time']) * 1000
        
        return {
            "trace_id": trace_id,
            "workflow_name": start_entry.get('workflow_name') if start_entry else None,
            "status": end_entry.get('status') if end_entry else 'incomplete',
            "total_duration_ms": total_duration,
            "node_timings": node_timings,
            "tool_calls_count": len(tool_calls),
            "errors_count": len(errors),
            "violations_count": len(violations),
            "total_events": len(trace_entries)
        }
    
    def get_all_traces_summary(self) -> pd.DataFrame:
        """Get summary of all traces as DataFrame."""
        trace_ids = list(set(t['trace_id'] for t in self.traces if 'trace_id' in t))
        summaries = [self.get_trace_summary(tid) for tid in trace_ids]
        
        if not summaries:
            return pd.DataFrame()
        
        return pd.DataFrame(summaries)
    
    def load_from_file(self, log_file: Optional[str] = None):
        """Load traces from JSONL file."""
        file_path = log_file or self.log_file
        
        if not Path(file_path).exists():
            return
        
        self.traces = []
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    self.traces.append(entry)
                except json.JSONDecodeError:
                    continue
    
    def clear(self):
        """Clear all traces."""
        self.traces = []
        self.current_trace_id = None
        
        if Path(self.log_file).exists():
            Path(self.log_file).unlink()


class PerformanceMonitor:
    """Monitor performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
    
    def record_metric(self, metric_name: str, value: float):
        """Record a metric value."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        values = self.metrics[metric_name]
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "total": sum(values)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics."""
        return {name: self.get_stats(name) for name in self.metrics.keys()}
    
    def clear(self):
        """Clear all metrics."""
        self.metrics = {}


class GuardrailMonitor:
    """Monitor guardrail violations."""
    
    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
    
    def record_violation(self, violation_type: str, severity: str, message: str, context: Dict[str, Any]):
        """Record a guardrail violation."""
        violation = {
            "violation_type": violation_type,
            "severity": severity,
            "message": message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.violations.append(violation)
    
    def get_violations(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get violations, optionally filtered by severity."""
        if severity:
            return [v for v in self.violations if v['severity'] == severity]
        return self.violations
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of violations."""
        by_type = {}
        by_severity = {}
        
        for v in self.violations:
            vtype = v['violation_type']
            severity = v['severity']
            
            by_type[vtype] = by_type.get(vtype, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_violations": len(self.violations),
            "by_type": by_type,
            "by_severity": by_severity
        }
    
    def clear(self):
        """Clear all violations."""
        self.violations = []


def create_trace_viewer(logger: TraceLogger) -> pd.DataFrame:
    """Create a pandas DataFrame for trace viewing."""
    df = logger.get_all_traces_summary()
    
    if df.empty:
        return pd.DataFrame(columns=[
            'trace_id', 'workflow_name', 'status', 'total_duration_ms',
            'tool_calls_count', 'errors_count', 'violations_count'
        ])
    
    return df


def format_trace_for_display(logger: TraceLogger, trace_id: str) -> str:
    """Format a trace for human-readable display."""
    trace_entries = [t for t in logger.traces if t.get('trace_id') == trace_id]
    
    if not trace_entries:
        return "Trace not found"
    
    lines = [f"Trace ID: {trace_id}", "=" * 60]
    
    for entry in trace_entries:
        event_type = entry.get('event_type', 'unknown')
        timestamp = entry.get('timestamp', '')
        
        if event_type == 'trace_start':
            lines.append(f"\n🚀 Workflow Started: {entry.get('workflow_name')}")
            lines.append(f"   Time: {timestamp}")
        
        elif event_type == 'node_start':
            lines.append(f"\n▶️  Node: {entry.get('node_name')}")
        
        elif event_type == 'node_end':
            duration = entry.get('duration_ms', 0)
            lines.append(f"   ✓ Completed in {duration:.2f}ms")
        
        elif event_type == 'tool_call':
            tool_name = entry.get('tool_name', 'unknown')
            duration = entry.get('duration_ms', 0)
            lines.append(f"   🔧 Tool: {tool_name} ({duration:.2f}ms)")
        
        elif event_type == 'state_transition':
            from_node = entry.get('from_node', '')
            to_node = entry.get('to_node', '')
            lines.append(f"   → Transition: {from_node} → {to_node}")
        
        elif event_type == 'error':
            error = entry.get('error', '')
            lines.append(f"   ❌ Error: {error}")
        
        elif event_type == 'guardrail_violation':
            vtype = entry.get('violation_type', '')
            lines.append(f"   ⚠️  Guardrail Violation: {vtype}")
        
        elif event_type == 'trace_end':
            status = entry.get('status', 'unknown')
            lines.append(f"\n✅ Workflow Ended: {status}")
            lines.append(f"   Time: {timestamp}")
    
    lines.append("=" * 60)
    return "\n".join(lines)
