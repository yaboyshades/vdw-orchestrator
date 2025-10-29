"""Perspective-specific analyzers used by the Meta-Review system."""

from dataclasses import dataclass
from typing import List
from .core import ReviewInsight, ReviewPerspective, ReasoningArtifact, ReviewDepth


@dataclass
class SkepticalAnalyzer:
    """Encapsulates skeptic-style checks for modular use."""
    def analyze(self, artifact: ReasoningArtifact, depth: ReviewDepth = ReviewDepth.DEEP) -> List[ReviewInsight]:
        from .core import MetaReviewFramework
        return MetaReviewFramework()._skeptical_analysis(artifact, depth)


@dataclass
class NoviceAnalyzer:
    """Encapsulates novice-style checks for modular use."""
    def analyze(self, artifact: ReasoningArtifact, depth: ReviewDepth = ReviewDepth.DEEP) -> List[ReviewInsight]:
        from .core import MetaReviewFramework
        return MetaReviewFramework()._novice_analysis(artifact, depth)


@dataclass
class CrossDomainAnalyzer:
    """Encapsulates cross-domain expert checks for modular use."""
    def analyze(self, artifact: ReasoningArtifact, depth: ReviewDepth = ReviewDepth.DEEP) -> List[ReviewInsight]:
        from .core import MetaReviewFramework
        return MetaReviewFramework()._cross_domain_analysis(artifact, depth)
