"""Validation gates and quality metrics for the Meta-Review system."""

from dataclasses import dataclass
from typing import Dict, List

from .core import MetaReviewResult, ReviewDepth


@dataclass
class QualityMetrics:
    """Compute quantitative metrics from review results."""
    def compute(self, result: MetaReviewResult) -> Dict[str, float]:
        total_insights = len(result.insights)
        actionable = len([i for i in result.insights if i.actionable])
        avg_confidence = sum(i.confidence for i in result.insights) / total_insights if total_insights else 0.0
        breadth = len(set(i.category for i in result.insights))
        return {
            "overall_score": result.overall_score,
            "insight_count": float(total_insights),
            "actionable_ratio": (actionable / total_insights) if total_insights else 0.0,
            "avg_confidence": avg_confidence,
            "analytical_breadth": float(breadth),
        }


@dataclass
class ValidationGates:
    """Gate checks for VDW phase transitions leveraging meta-review outputs."""
    min_score: float = 7.5
    min_breadth: int = 3
    require_meta_insights: bool = True

    def check(self, result: MetaReviewResult) -> List[str]:
        errors: List[str] = []
        if result.overall_score < self.min_score:
            errors.append(f"Score {result.overall_score:.2f} below threshold {self.min_score}")
        breadth = len(set(i.category for i in result.insights))
        if breadth < self.min_breadth:
            errors.append(f"Analytical breadth {breadth} below minimum {self.min_breadth}")
        if self.require_meta_insights and result.depth_level == ReviewDepth.DEEP and not result.meta_insights:
            errors.append("Missing meta-insights for deep analysis")
        return errors
