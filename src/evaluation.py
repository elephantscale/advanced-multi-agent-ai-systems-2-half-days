from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
from src.schemas import ClassificationResult, SeverityLevel


class EvaluationCase(BaseModel):
    """Single evaluation test case."""
    incident_id: str
    ground_truth_severity: SeverityLevel
    ground_truth_category: str
    ground_truth_team: str
    description: str


class ClassificationEvaluation(BaseModel):
    """Evaluation results for classification."""
    correct_severity: int = 0
    correct_category: int = 0
    total_cases: int = 0
    accuracy_severity: float = 0.0
    accuracy_category: float = 0.0
    confusion_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    def calculate_accuracy(self):
        """Calculate accuracy scores."""
        if self.total_cases > 0:
            self.accuracy_severity = self.correct_severity / self.total_cases
            self.accuracy_category = self.correct_category / self.total_cases


class RoutingEvaluation(BaseModel):
    """Evaluation results for routing."""
    correct_team: int = 0
    total_cases: int = 0
    accuracy: float = 0.0
    avg_sla_hours: float = 0.0
    
    def calculate_accuracy(self):
        """Calculate accuracy score."""
        if self.total_cases > 0:
            self.accuracy = self.correct_team / self.total_cases


class PerformanceEvaluation(BaseModel):
    """Performance evaluation metrics."""
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    success_rate: float = 0.0


class Evaluator:
    """Evaluate multi-agent system performance."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.latencies: List[float] = []
    
    def add_result(
        self,
        incident_id: str,
        predicted_severity: Optional[str],
        predicted_category: Optional[str],
        predicted_team: Optional[str],
        ground_truth: EvaluationCase,
        latency_ms: float,
        success: bool
    ):
        """Add evaluation result."""
        result = {
            "incident_id": incident_id,
            "predicted_severity": predicted_severity,
            "predicted_category": predicted_category,
            "predicted_team": predicted_team,
            "ground_truth_severity": ground_truth.ground_truth_severity.value,
            "ground_truth_category": ground_truth.ground_truth_category,
            "ground_truth_team": ground_truth.ground_truth_team,
            "latency_ms": latency_ms,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        self.latencies.append(latency_ms)
    
    def evaluate_classification(self) -> ClassificationEvaluation:
        """Evaluate classification performance."""
        eval_result = ClassificationEvaluation()
        
        for result in self.results:
            if not result['success']:
                continue
            
            eval_result.total_cases += 1
            
            if result['predicted_severity'] == result['ground_truth_severity']:
                eval_result.correct_severity += 1
            
            if result['predicted_category'] == result['ground_truth_category']:
                eval_result.correct_category += 1
            
            gt_sev = result['ground_truth_severity']
            pred_sev = result['predicted_severity'] or 'unknown'
            
            if gt_sev not in eval_result.confusion_matrix:
                eval_result.confusion_matrix[gt_sev] = {}
            
            eval_result.confusion_matrix[gt_sev][pred_sev] = \
                eval_result.confusion_matrix[gt_sev].get(pred_sev, 0) + 1
        
        eval_result.calculate_accuracy()
        return eval_result
    
    def evaluate_routing(self) -> RoutingEvaluation:
        """Evaluate routing performance."""
        eval_result = RoutingEvaluation()
        
        for result in self.results:
            if not result['success']:
                continue
            
            eval_result.total_cases += 1
            
            if result['predicted_team'] == result['ground_truth_team']:
                eval_result.correct_team += 1
        
        eval_result.calculate_accuracy()
        return eval_result
    
    def evaluate_performance(self) -> PerformanceEvaluation:
        """Evaluate performance metrics."""
        eval_result = PerformanceEvaluation()
        
        if not self.latencies:
            return eval_result
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        eval_result.avg_latency_ms = sum(sorted_latencies) / n
        eval_result.p50_latency_ms = sorted_latencies[int(n * 0.5)]
        eval_result.p95_latency_ms = sorted_latencies[int(n * 0.95)]
        eval_result.p99_latency_ms = sorted_latencies[int(n * 0.99)]
        
        success_count = sum(1 for r in self.results if r['success'])
        eval_result.success_rate = success_count / len(self.results) if self.results else 0.0
        
        return eval_result
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """Get results as pandas DataFrame."""
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.results)
    
    def generate_report(self) -> str:
        """Generate evaluation report."""
        classification_eval = self.evaluate_classification()
        routing_eval = self.evaluate_routing()
        performance_eval = self.evaluate_performance()
        
        lines = [
            "=" * 70,
            "EVALUATION REPORT",
            "=" * 70,
            "",
            "CLASSIFICATION METRICS",
            "-" * 70,
            f"Total Cases: {classification_eval.total_cases}",
            f"Severity Accuracy: {classification_eval.accuracy_severity:.2%}",
            f"Category Accuracy: {classification_eval.accuracy_category:.2%}",
            "",
            "ROUTING METRICS",
            "-" * 70,
            f"Total Cases: {routing_eval.total_cases}",
            f"Team Assignment Accuracy: {routing_eval.accuracy:.2%}",
            "",
            "PERFORMANCE METRICS",
            "-" * 70,
            f"Average Latency: {performance_eval.avg_latency_ms:.2f}ms",
            f"P50 Latency: {performance_eval.p50_latency_ms:.2f}ms",
            f"P95 Latency: {performance_eval.p95_latency_ms:.2f}ms",
            f"P99 Latency: {performance_eval.p99_latency_ms:.2f}ms",
            f"Success Rate: {performance_eval.success_rate:.2%}",
            "",
            "=" * 70
        ]
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all results."""
        self.results = []
        self.latencies = []


def create_evaluation_cases() -> List[EvaluationCase]:
    """Create sample evaluation cases with ground truth."""
    return [
        EvaluationCase(
            incident_id="EVAL-001",
            ground_truth_severity=SeverityLevel.P0,
            ground_truth_category="Database",
            ground_truth_team="Database Team",
            description="Production database connection pool exhausted. All users affected."
        ),
        EvaluationCase(
            incident_id="EVAL-002",
            ground_truth_severity=SeverityLevel.P1,
            ground_truth_category="Network",
            ground_truth_team="Network Operations",
            description="API Gateway returning 503 errors. Multiple services impacted."
        ),
        EvaluationCase(
            incident_id="EVAL-003",
            ground_truth_severity=SeverityLevel.P2,
            ground_truth_category="Application",
            ground_truth_team="Application Support",
            description="Memory leak in payment service. Gradual performance degradation."
        ),
        EvaluationCase(
            incident_id="EVAL-004",
            ground_truth_severity=SeverityLevel.P3,
            ground_truth_category="Infrastructure",
            ground_truth_team="Infrastructure",
            description="Disk space warning on log server. 85% capacity."
        ),
        EvaluationCase(
            incident_id="EVAL-005",
            ground_truth_severity=SeverityLevel.P1,
            ground_truth_category="Security",
            ground_truth_team="Security Team",
            description="Suspicious login attempts detected. Potential security breach."
        )
    ]


def calculate_precision_recall_f1(
    true_positives: int,
    false_positives: int,
    false_negatives: int
) -> Dict[str, float]:
    """Calculate precision, recall, and F1 score."""
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


def compare_runs(evaluator1: Evaluator, evaluator2: Evaluator, run1_name: str = "Run 1", run2_name: str = "Run 2") -> str:
    """Compare two evaluation runs."""
    eval1_class = evaluator1.evaluate_classification()
    eval2_class = evaluator2.evaluate_classification()
    
    eval1_perf = evaluator1.evaluate_performance()
    eval2_perf = evaluator2.evaluate_performance()
    
    lines = [
        "=" * 70,
        f"COMPARISON: {run1_name} vs {run2_name}",
        "=" * 70,
        "",
        "CLASSIFICATION ACCURACY",
        "-" * 70,
        f"{run1_name} Severity: {eval1_class.accuracy_severity:.2%}",
        f"{run2_name} Severity: {eval2_class.accuracy_severity:.2%}",
        f"Difference: {(eval2_class.accuracy_severity - eval1_class.accuracy_severity):.2%}",
        "",
        "PERFORMANCE",
        "-" * 70,
        f"{run1_name} Avg Latency: {eval1_perf.avg_latency_ms:.2f}ms",
        f"{run2_name} Avg Latency: {eval2_perf.avg_latency_ms:.2f}ms",
        f"Difference: {(eval2_perf.avg_latency_ms - eval1_perf.avg_latency_ms):.2f}ms",
        "",
        f"{run1_name} Success Rate: {eval1_perf.success_rate:.2%}",
        f"{run2_name} Success Rate: {eval2_perf.success_rate:.2%}",
        f"Difference: {(eval2_perf.success_rate - eval1_perf.success_rate):.2%}",
        "",
        "=" * 70
    ]
    
    return "\n".join(lines)
