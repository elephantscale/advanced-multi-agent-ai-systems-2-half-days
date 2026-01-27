import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import Counter


@dataclass
class LogEntry:
    timestamp: str
    level: str
    service: str
    message: str
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'level': self.level,
            'service': self.service,
            'message': self.message,
            'error_type': self.error_type,
            'stack_trace': self.stack_trace,
            'metadata': self.metadata or {}
        }


class LogParser:
    
    def __init__(self):
        self.log_patterns = {
            'timestamp': r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            'level': r'(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)',
            'service': r'service[_-]?\w+',
            'error': r'(Exception|Error|Failure)',
            'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            'status_code': r'\b[1-5]\d{2}\b'
        }
    
    def parse_log_line(self, line: str) -> Optional[LogEntry]:
        timestamp_match = re.search(self.log_patterns['timestamp'], line)
        level_match = re.search(self.log_patterns['level'], line, re.IGNORECASE)
        service_match = re.search(self.log_patterns['service'], line, re.IGNORECASE)
        error_match = re.search(self.log_patterns['error'], line)
        
        if not timestamp_match:
            return None
        
        timestamp = timestamp_match.group(0)
        level = level_match.group(0).upper() if level_match else 'INFO'
        service = service_match.group(0) if service_match else 'unknown'
        error_type = error_match.group(0) if error_match else None
        
        message = line
        
        metadata = {
            'line_length': len(line),
            'has_error': error_type is not None
        }
        
        ip_match = re.search(self.log_patterns['ip'], line)
        if ip_match:
            metadata['ip'] = ip_match.group(0)
        
        status_match = re.search(self.log_patterns['status_code'], line)
        if status_match:
            metadata['status_code'] = int(status_match.group(0))
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            service=service,
            message=message,
            error_type=error_type,
            metadata=metadata
        )
    
    def parse_logs(self, log_text: str) -> List[LogEntry]:
        lines = log_text.strip().split('\n')
        entries = []
        
        for line in lines:
            if not line.strip():
                continue
            
            entry = self.parse_log_line(line)
            if entry:
                entries.append(entry)
        
        return entries
    
    def analyze_logs(self, entries: List[LogEntry]) -> Dict[str, Any]:
        if not entries:
            return {'error': 'No log entries to analyze'}
        
        level_counts = Counter(entry.level for entry in entries)
        service_counts = Counter(entry.service for entry in entries)
        error_counts = Counter(entry.error_type for entry in entries if entry.error_type)
        
        error_entries = [e for e in entries if e.level in ['ERROR', 'CRITICAL', 'FATAL']]
        
        timestamps = [e.timestamp for e in entries]
        
        return {
            'total_entries': len(entries),
            'level_distribution': dict(level_counts),
            'service_distribution': dict(service_counts),
            'error_types': dict(error_counts),
            'error_count': len(error_entries),
            'error_rate': len(error_entries) / len(entries) if entries else 0,
            'time_range': {
                'first': timestamps[0] if timestamps else None,
                'last': timestamps[-1] if timestamps else None
            },
            'services_affected': len(service_counts),
            'unique_errors': len(error_counts)
        }
    
    def filter_by_level(self, entries: List[LogEntry], level: str) -> List[LogEntry]:
        return [e for e in entries if e.level == level.upper()]
    
    def filter_by_service(self, entries: List[LogEntry], service: str) -> List[LogEntry]:
        return [e for e in entries if service.lower() in e.service.lower()]
    
    def filter_by_time_range(self, entries: List[LogEntry], start: str, end: str) -> List[LogEntry]:
        return [e for e in entries if start <= e.timestamp <= end]
    
    def get_error_summary(self, entries: List[LogEntry]) -> str:
        error_entries = [e for e in entries if e.level in ['ERROR', 'CRITICAL', 'FATAL']]
        
        if not error_entries:
            return "No errors found in logs."
        
        error_types = Counter(e.error_type for e in error_entries if e.error_type)
        
        summary_lines = [
            f"Found {len(error_entries)} error entries:",
            ""
        ]
        
        for error_type, count in error_types.most_common(5):
            summary_lines.append(f"  - {error_type}: {count} occurrences")
        
        return "\n".join(summary_lines)
