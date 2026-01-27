from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import json


class PerformanceMetrics:
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.metrics: Dict[str, Any] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.timings: Dict[str, List[float]] = defaultdict(list)
    
    def record_metric(self, key: str, value: Any):
        self.metrics[key] = value
    
    def increment_counter(self, key: str, amount: int = 1):
        self.counters[key] += amount
    
    def record_timing(self, key: str, duration_ms: float):
        self.timings[key].append(duration_ms)
    
    def finish(self):
        self.end_time = datetime.now()
    
    def get_duration(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        summary = {
            'name': self.name,
            'duration_seconds': self.get_duration(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'metrics': self.metrics,
            'counters': dict(self.counters)
        }
        
        if self.timings:
            timing_stats = {}
            for key, values in self.timings.items():
                timing_stats[key] = {
                    'count': len(values),
                    'total_ms': sum(values),
                    'avg_ms': sum(values) / len(values),
                    'min_ms': min(values),
                    'max_ms': max(values)
                }
            summary['timing_stats'] = timing_stats
        
        return summary


class MetricsCollector:
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.current_metric: Optional[PerformanceMetrics] = None
    
    def start_tracking(self, name: str) -> PerformanceMetrics:
        metric = PerformanceMetrics(name)
        self.current_metric = metric
        self.metrics.append(metric)
        return metric
    
    def stop_tracking(self):
        if self.current_metric:
            self.current_metric.finish()
            self.current_metric = None
    
    def get_current(self) -> Optional[PerformanceMetrics]:
        return self.current_metric
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        return [m.get_summary() for m in self.metrics]
    
    def get_aggregate_stats(self) -> Dict[str, Any]:
        if not self.metrics:
            return {'error': 'No metrics collected'}
        
        total_duration = sum(m.get_duration() for m in self.metrics)
        
        all_counters = defaultdict(int)
        for metric in self.metrics:
            for key, value in metric.counters.items():
                all_counters[key] += value
        
        return {
            'total_metrics': len(self.metrics),
            'total_duration_seconds': total_duration,
            'avg_duration_seconds': total_duration / len(self.metrics),
            'aggregate_counters': dict(all_counters)
        }
    
    def export_to_json(self, filepath: str):
        data = {
            'metrics': self.get_all_metrics(),
            'aggregate': self.get_aggregate_stats(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear(self):
        self.metrics = []
        self.current_metric = None
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 Performance Metrics Summary")
        print("="*60)
        
        for i, metric in enumerate(self.metrics, 1):
            summary = metric.get_summary()
            print(f"\n{i}. {summary['name']}")
            print(f"   Duration: {summary['duration_seconds']:.2f}s")
            
            if summary['counters']:
                print(f"   Counters: {summary['counters']}")
            
            if 'timing_stats' in summary:
                print(f"   Timing Stats:")
                for key, stats in summary['timing_stats'].items():
                    print(f"     - {key}: {stats['count']} calls, avg {stats['avg_ms']:.2f}ms")
        
        agg = self.get_aggregate_stats()
        print(f"\n{'='*60}")
        print(f"Total Duration: {agg['total_duration_seconds']:.2f}s")
        print(f"Average Duration: {agg['avg_duration_seconds']:.2f}s")
        print("="*60 + "\n")
