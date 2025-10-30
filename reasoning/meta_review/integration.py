"""Integration points to wire Meta-Review into the VDW phases and MCP server."""

from dataclasses import dataclass
from typing import Optional

from .core import MetaReviewFramework, MentalGameAnalyzer, ReasoningArtifact, ReviewDepth
from .validators import ValidationGates, QualityMetrics


@dataclass
class VDWIntegration:
    """Provides high-level APIs to run meta-review at phase gates and emit results."""
    framework: MetaReviewFramework
    gates: ValidationGates
    metrics: QualityMetrics

    def review_phase_output(self, *, title: str, content: str, phase: str, author: str = "system"):
        artifact = ReasoningArtifact(title=title, content=content, author=author, phase=phase)
        result = self.framework.conduct_review(artifact, depth=ReviewDepth.DEEP)
        errors = self.gates.check(result)
        summary = self.metrics.compute(result)
        return {
            "artifact": artifact.to_dict(),
            "result": {
                "review_id": result.review_id,
                "overall_score": result.overall_score,
                "recommendations": result.recommendations,
                "meta_insights": result.meta_insights,
                "insights": [
                    {
                        "perspective": i.perspective.value,
                        "category": i.category,
                        "insight": i.insight,
                        "confidence": i.confidence,
                        "actionable": i.actionable,
                        "evidence": i.evidence,
                    } for i in result.insights
                ],
            },
            "validation_errors": errors,
            "metrics": summary,
        }

    def should_advance_phase(self, review_payload: dict) -> bool:
        return len(review_payload.get("validation_errors", [])) == 0
