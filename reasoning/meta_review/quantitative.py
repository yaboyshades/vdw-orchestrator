"""Quantitative Validation and Metrics System.

Phase 11: Statistical validation models, A/B testing frameworks, benchmarking
standards, and performance baselines for meta-review system validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
import statistics
import math
import uuid
from collections import defaultdict

from .core import MetaReviewResult, ReviewInsight, ReasoningArtifact


class MetricType(Enum):
    """Types of quantitative metrics."""
    ACCURACY = "accuracy"
    RELIABILITY = "reliability"
    SENSITIVITY = "sensitivity"
    SPECIFICITY = "specificity"
    EFFICIENCY = "efficiency"
    CALIBRATION = "calibration"


@dataclass
class QuantitativeMetric:
    """Represents a quantitative measurement."""
    metric_id: str
    metric_type: MetricType
    value: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    measurement_timestamp: datetime
    method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestConfig:
    """Configuration for A/B testing experiments."""
    test_id: str
    name: str
    hypothesis: str
    control_condition: Dict[str, Any]
    treatment_condition: Dict[str, Any]
    success_metrics: List[str]
    minimum_sample_size: int
    minimum_effect_size: float
    significance_level: float = 0.05
    power: float = 0.8
    max_duration_days: int = 30


class StatisticalValidator:
    """Performs statistical validation of meta-review performance."""
    
    def __init__(self):
        self.validation_history: List[Dict] = []
        self.baseline_metrics: Dict[MetricType, float] = {}
    
    def calculate_accuracy(self, predictions: List[float], actual_outcomes: List[float], threshold: float = 7.0) -> QuantitativeMetric:
        """Calculate accuracy of review predictions against actual outcomes."""
        
        if len(predictions) != len(actual_outcomes) or len(predictions) == 0:
            raise ValueError("Predictions and outcomes must have same non-zero length")
        
        pred_binary = [1 if p >= threshold else 0 for p in predictions]
        actual_binary = [1 if a >= threshold else 0 for a in actual_outcomes]
        
        correct = sum(1 for p, a in zip(pred_binary, actual_binary) if p == a)
        accuracy = correct / len(predictions)
        
        n = len(predictions)
        z = 1.96  # 95% confidence
        
        if n == 0:
            ci_lower = ci_upper = accuracy
        else:
            p = accuracy
            ci_lower = max(0, (p + z*z/(2*n) - z * math.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n))
            ci_upper = min(1, (p + z*z/(2*n) + z * math.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n))
        
        return QuantitativeMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.ACCURACY,
            value=accuracy,
            confidence_interval=(ci_lower, ci_upper),
            sample_size=n,
            measurement_timestamp=datetime.now(),
            method="wilson_score_interval",
            metadata={"threshold": threshold, "correct_predictions": correct}
        )
    
    def calculate_reliability(self, review_pairs: List[Tuple[MetaReviewResult, MetaReviewResult]]) -> QuantitativeMetric:
        """Calculate inter-rater reliability using correlation."""
        
        if len(review_pairs) < 3:
            raise ValueError("Need at least 3 review pairs for reliability calculation")
        
        scores1 = [pair[0].overall_score for pair in review_pairs]
        scores2 = [pair[1].overall_score for pair in review_pairs]
        
        correlation = self._calculate_correlation(scores1, scores2)
        
        n = len(review_pairs)
        if correlation in [1.0, -1.0] or n < 4:
            ci_lower = ci_upper = correlation
        else:
            z_r = 0.5 * math.log((1 + correlation) / (1 - correlation))
            se = 1 / math.sqrt(n - 3)
            z = 1.96
            
            ci_z_lower = z_r - z * se
            ci_z_upper = z_r + z * se
            
            ci_lower = (math.exp(2 * ci_z_lower) - 1) / (math.exp(2 * ci_z_lower) + 1)
            ci_upper = (math.exp(2 * ci_z_upper) - 1) / (math.exp(2 * ci_z_upper) + 1)
        
        return QuantitativeMetric(
            metric_id=str(uuid.uuid4()),
            metric_type=MetricType.RELIABILITY,
            value=correlation,
            confidence_interval=(ci_lower, ci_upper),
            sample_size=n,
            measurement_timestamp=datetime.now(),
            method="pearson_correlation",
            metadata={"mean_diff": statistics.mean([abs(s1 - s2) for s1, s2 in zip(scores1, scores2)])}
        )
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        
        if len(x) != len(y) or len(x) == 0:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        return numerator / denominator if denominator != 0 else 0.0


class ABTestFramework:
    """Framework for conducting A/B tests on meta-review system improvements."""
    
    def __init__(self):
        self.active_tests: Dict[str, ABTestConfig] = {}
        self.test_data: Dict[str, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
        self.statistical_validator = StatisticalValidator()
    
    def create_test(self, config: ABTestConfig) -> str:
        """Create a new A/B test experiment."""
        self.active_tests[config.test_id] = config
        return config.test_id
    
    def add_test_observation(self, test_id: str, condition: str, metrics: Dict[str, float]):
        """Add an observation to an active test."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        for metric_name, value in metrics.items():
            self.test_data[test_id][f"{condition}_{metric_name}"].append(value)
    
    def analyze_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Analyze A/B test results and determine statistical significance."""
        if test_id not in self.active_tests:
            return None
        
        config = self.active_tests[test_id]
        data = self.test_data[test_id]
        
        control_samples = len(data.get(f"control_{config.success_metrics[0]}", []))
        treatment_samples = len(data.get(f"treatment_{config.success_metrics[0]}", []))
        
        if control_samples < config.minimum_sample_size or treatment_samples < config.minimum_sample_size:
            return None
        
        results = {"test_id": test_id, "analysis_complete": True, "metrics": {}}
        
        for metric_name in config.success_metrics:
            control_values = data[f"control_{metric_name}"]
            treatment_values = data[f"treatment_{metric_name}"]
            
            control_mean = statistics.mean(control_values)
            treatment_mean = statistics.mean(treatment_values)
            
            t_stat, p_value = self._welch_t_test(control_values, treatment_values)
            
            results["metrics"][metric_name] = {
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "p_value": p_value,
                "significant": p_value < config.significance_level,
                "effect_size": treatment_mean - control_mean
            }
        
        return results
    
    def _welch_t_test(self, group1: List[float], group2: List[float]) -> Tuple[float, float]:
        """Perform Welch's t-test for unequal variances."""
        if len(group1) < 2 or len(group2) < 2:
            return (0.0, 1.0)
        
        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)
        var1 = statistics.variance(group1) if len(group1) > 1 else 0.0
        var2 = statistics.variance(group2) if len(group2) > 1 else 0.0
        n1, n2 = len(group1), len(group2)
        
        if var1 == 0 and var2 == 0:
            return (0.0, 1.0 if mean1 == mean2 else 0.0)
        
        t_stat = (mean1 - mean2) / math.sqrt(var1/n1 + var2/n2) if (var1/n1 + var2/n2) > 0 else 0.0
        
        # Simplified p-value approximation
        abs_t = abs(t_stat)
        if abs_t > 2.58:
            p_value = 0.01
        elif abs_t > 1.96:
            p_value = 0.05
        elif abs_t > 1.64:
            p_value = 0.1
        else:
            p_value = 0.2
        
        return (t_stat, p_value)


class BenchmarkingSystem:
    """System for establishing and tracking performance benchmarks."""
    
    def __init__(self):
        self.benchmarks: Dict[str, Dict[MetricType, float]] = {}
        self.industry_standards: Dict[MetricType, Dict[str, float]] = {
            MetricType.ACCURACY: {"minimum": 0.7, "good": 0.8, "excellent": 0.9},
            MetricType.RELIABILITY: {"minimum": 0.6, "good": 0.75, "excellent": 0.85},
            MetricType.SENSITIVITY: {"minimum": 0.8, "good": 0.85, "excellent": 0.9},
            MetricType.SPECIFICITY: {"minimum": 0.7, "good": 0.8, "excellent": 0.9},
            MetricType.CALIBRATION: {"maximum": 0.1, "good": 0.05, "excellent": 0.02}
        }
    
    def establish_baseline(self, name: str, metrics: Dict[MetricType, QuantitativeMetric]) -> Dict[str, Any]:
        """Establish a performance baseline."""
        baseline = {metric_type: metric.value for metric_type, metric in metrics.items()}
        self.benchmarks[name] = baseline
        
        comparisons = {}
        for metric_type, value in baseline.items():
            standards = self.industry_standards.get(metric_type, {})
            
            if metric_type == MetricType.CALIBRATION:  # Lower is better
                if value <= standards.get("excellent", float('inf')):
                    performance = "excellent"
                elif value <= standards.get("good", float('inf')):
                    performance = "good"
                else:
                    performance = "needs_improvement"
            else:  # Higher is better
                if value >= standards.get("excellent", 0):
                    performance = "excellent"
                elif value >= standards.get("good", 0):
                    performance = "good"
                else:
                    performance = "needs_improvement"
            
            comparisons[metric_type.value] = {"value": value, "performance_level": performance}
        
        return {
            "baseline_name": name,
            "timestamp": datetime.now().isoformat(),
            "industry_comparison": comparisons
        }
    
    def generate_performance_report(self, metrics: Dict[MetricType, QuantitativeMetric]) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_performance": {mt.value: {"value": m.value, "sample_size": m.sample_size} 
                                   for mt, m in metrics.items()},
            "recommendations": ["Continue monitoring performance metrics"]
        }


class QuantitativeValidationEngine:
    """Main engine for quantitative validation activities."""
    
    def __init__(self):
        self.statistical_validator = StatisticalValidator()
        self.ab_test_framework = ABTestFramework()
        self.benchmarking_system = BenchmarkingSystem()
        self.validation_history: List[Dict] = []
    
    def run_comprehensive_validation(self, review_data: List[MetaReviewResult]) -> Dict[str, Any]:
        """Run comprehensive quantitative validation."""
        
        if len(review_data) < 10:
            return {
                "status": "insufficient_data",
                "review_count": len(review_data),
                "recommendations": ["Need at least 10 reviews for validation"]
            }
        
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "data_summary": {"review_count": len(review_data)},
            "metrics": {},
            "recommendations": []
        }
        
        # Calculate reliability if possible
        reliability_pairs = self._create_reliability_pairs(review_data)
        if len(reliability_pairs) >= 3:
            reliability_metric = self.statistical_validator.calculate_reliability(reliability_pairs)
            validation_result["metrics"]["reliability"] = {
                "value": reliability_metric.value,
                "confidence_interval": reliability_metric.confidence_interval,
                "sample_size": reliability_metric.sample_size
            }
        
        self.validation_history.append(validation_result)
        return validation_result
    
    def _create_reliability_pairs(self, reviews: List[MetaReviewResult]) -> List[Tuple[MetaReviewResult, MetaReviewResult]]:
        """Create pairs of reviews for reliability calculation."""
        artifact_groups = defaultdict(list)
        for review in reviews:
            artifact_groups[review.artifact_id].append(review)
        
        pairs = []
        for artifact_reviews in artifact_groups.values():
            if len(artifact_reviews) >= 2:
                for i in range(len(artifact_reviews)):
                    for j in range(i + 1, len(artifact_reviews)):
                        pairs.append((artifact_reviews[i], artifact_reviews[j]))
        
        return pairs[:50]  # Limit pairs
    
    def get_validation_dashboard(self) -> Dict[str, Any]:
        """Generate validation dashboard."""
        if not self.validation_history:
            return {"status": "no_validation_history"}
        
        latest = self.validation_history[-1]
        return {
            "last_validation": latest["validation_timestamp"],
            "current_metrics": latest.get("metrics", {}),
            "validation_count": len(self.validation_history)
        }