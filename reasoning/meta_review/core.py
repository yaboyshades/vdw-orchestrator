"""Core Meta-Review Framework Implementation.

This module contains the foundational classes for conducting comprehensive
meta-reviews of reasoning processes using the Mental Game Analysis approach.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime


class ReviewDepth(Enum):
    """Defines the depth levels for meta-review analysis."""
    SURFACE = "surface"  # Basic review criteria
    STANDARD = "standard"  # Standard analytical framework 
    DEEP = "deep"  # Mental games analysis
    META_META = "meta_meta"  # Recursive meta-analysis


class ReviewPerspective(Enum):
    """Defines the analytical perspectives for mental games."""
    SKEPTICAL = "skeptical"  # Critical, doubt-focused analysis
    NOVICE = "novice"  # Beginner's perspective
    CROSS_DOMAIN = "cross_domain"  # Expert from different field
    COLLABORATIVE = "collaborative"  # Multi-reviewer consensus


@dataclass
class ReasoningArtifact:
    """Represents a reasoning document or process to be reviewed."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    phase: Optional[str] = None  # VDW phase if applicable
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "phase": self.phase,
            "version": self.version
        }


@dataclass
class ReviewInsight:
    """Represents a single insight from a meta-review analysis."""
    perspective: ReviewPerspective
    category: str  # e.g., "strengths", "weaknesses", "blind_spots"
    insight: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0
    actionable: bool = False
    

@dataclass
class MetaReviewResult:
    """Complete results from a meta-review analysis."""
    artifact_id: str
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    depth_level: ReviewDepth = ReviewDepth.STANDARD
    perspectives_used: List[ReviewPerspective] = field(default_factory=list)
    insights: List[ReviewInsight] = field(default_factory=list)
    overall_score: float = 0.0  # 0.0 to 10.0
    recommendations: List[str] = field(default_factory=list)
    meta_insights: List[str] = field(default_factory=list)  # About the review process itself
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_insights_by_perspective(self, perspective: ReviewPerspective) -> List[ReviewInsight]:
        """Filter insights by perspective."""
        return [insight for insight in self.insights if insight.perspective == perspective]
    
    def get_insights_by_category(self, category: str) -> List[ReviewInsight]:
        """Filter insights by category."""
        return [insight for insight in self.insights if insight.category == category]


class MetaReviewFramework:
    """Core framework for conducting meta-reviews of reasoning processes."""
    
    def __init__(self):
        self.review_history: List[MetaReviewResult] = []
        self.quality_thresholds = {
            "minimum_acceptable": 6.0,
            "good_quality": 7.5,
            "excellent_quality": 9.0
        }
    
    def conduct_review(self, 
                      artifact: ReasoningArtifact,
                      depth: ReviewDepth = ReviewDepth.STANDARD,
                      perspectives: Optional[List[ReviewPerspective]] = None) -> MetaReviewResult:
        """Conduct a comprehensive meta-review of a reasoning artifact."""
        
        if perspectives is None:
            perspectives = [ReviewPerspective.SKEPTICAL, ReviewPerspective.NOVICE, ReviewPerspective.CROSS_DOMAIN]
        
        result = MetaReviewResult(
            artifact_id=artifact.id,
            depth_level=depth,
            perspectives_used=perspectives
        )
        
        # Conduct analysis from each perspective
        for perspective in perspectives:
            insights = self._analyze_from_perspective(artifact, perspective, depth)
            result.insights.extend(insights)
        
        # Calculate overall score
        result.overall_score = self._calculate_overall_score(result)
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        # Add meta-insights if deep analysis
        if depth in [ReviewDepth.DEEP, ReviewDepth.META_META]:
            result.meta_insights = self._generate_meta_insights(result)
        
        self.review_history.append(result)
        return result
    
    def _analyze_from_perspective(self, 
                                 artifact: ReasoningArtifact, 
                                 perspective: ReviewPerspective,
                                 depth: ReviewDepth) -> List[ReviewInsight]:
        """Analyze artifact from a specific perspective."""
        insights = []
        
        if perspective == ReviewPerspective.SKEPTICAL:
            insights.extend(self._skeptical_analysis(artifact, depth))
        elif perspective == ReviewPerspective.NOVICE:
            insights.extend(self._novice_analysis(artifact, depth))
        elif perspective == ReviewPerspective.CROSS_DOMAIN:
            insights.extend(self._cross_domain_analysis(artifact, depth))
        
        return insights
    
    def _skeptical_analysis(self, artifact: ReasoningArtifact, depth: ReviewDepth) -> List[ReviewInsight]:
        """Conduct skeptical analysis looking for flaws and gaps."""
        insights = []
        
        # Check for missing evidence
        if "evidence" not in artifact.content.lower():
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.SKEPTICAL,
                category="missing_evidence",
                insight="Limited evidence provided to support claims",
                confidence=0.7,
                actionable=True
            ))
        
        # Check for cherry-picking
        if "however" not in artifact.content.lower() and "but" not in artifact.content.lower():
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.SKEPTICAL,
                category="potential_bias",
                insight="No counterarguments or limitations mentioned - potential cherry-picking",
                confidence=0.6,
                actionable=True
            ))
        
        # Check reasoning chain completeness
        if depth == ReviewDepth.DEEP:
            reasoning_gaps = self._identify_reasoning_gaps(artifact.content)
            for gap in reasoning_gaps:
                insights.append(ReviewInsight(
                    perspective=ReviewPerspective.SKEPTICAL,
                    category="reasoning_gaps",
                    insight=f"Potential reasoning gap: {gap}",
                    confidence=0.8,
                    actionable=True
                ))
        
        return insights
    
    def _novice_analysis(self, artifact: ReasoningArtifact, depth: ReviewDepth) -> List[ReviewInsight]:
        """Analyze from a beginner's perspective focusing on clarity and accessibility."""
        insights = []
        
        # Check for jargon
        technical_terms = self._identify_technical_terms(artifact.content)
        if len(technical_terms) > 5:
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.NOVICE,
                category="accessibility",
                insight=f"High technical jargon density may impede understanding for novices",
                evidence=technical_terms[:3],  # Show first 3 examples
                confidence=0.8,
                actionable=True
            ))
        
        # Check for examples
        if "example" not in artifact.content.lower() and "for instance" not in artifact.content.lower():
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.NOVICE,
                category="learning_support",
                insight="Lacks concrete examples to aid understanding",
                confidence=0.7,
                actionable=True
            ))
        
        return insights
    
    def _cross_domain_analysis(self, artifact: ReasoningArtifact, depth: ReviewDepth) -> List[ReviewInsight]:
        """Analyze transferability to other domains."""
        insights = []
        
        # Check for domain-specific assumptions
        if artifact.phase:
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.CROSS_DOMAIN,
                category="transferability",
                insight=f"Methods may need adaptation for domains outside {artifact.phase}",
                confidence=0.6,
                actionable=True
            ))
        
        # Check for universal principles
        universal_terms = ["principle", "pattern", "framework", "methodology"]
        universal_count = sum(1 for term in universal_terms if term in artifact.content.lower())
        
        if universal_count >= 2:
            insights.append(ReviewInsight(
                perspective=ReviewPerspective.CROSS_DOMAIN,
                category="strengths",
                insight="Contains transferable principles applicable across domains",
                confidence=0.8,
                actionable=False
            ))
        
        return insights
    
    def _identify_reasoning_gaps(self, content: str) -> List[str]:
        """Identify potential gaps in reasoning chain."""
        gaps = []
        
        # Simple heuristics for common reasoning gaps
        if "therefore" in content.lower() and "because" not in content.lower():
            gaps.append("Conclusion drawn without explicit causal reasoning")
        
        if "should" in content.lower() and "evidence" not in content.lower():
            gaps.append("Normative claims made without supporting evidence")
        
        return gaps
    
    def _identify_technical_terms(self, content: str) -> List[str]:
        """Identify technical terms that might confuse novices."""
        # This is a simplified implementation - in practice, you'd use NLP
        technical_indicators = ["algorithm", "framework", "methodology", "paradigm", "heuristic", "optimization"]
        found_terms = []
        
        for term in technical_indicators:
            if term in content.lower():
                found_terms.append(term)
        
        return found_terms
    
    def _calculate_overall_score(self, result: MetaReviewResult) -> float:
        """Calculate overall quality score based on insights."""
        if not result.insights:
            return 5.0  # Neutral score
        
        # Weight insights by confidence and actionability
        positive_weight = 0
        negative_weight = 0
        
        for insight in result.insights:
            weight = insight.confidence
            if insight.actionable:
                weight *= 1.2  # Boost actionable insights
            
            if insight.category in ["strengths", "good_practices"]:
                positive_weight += weight
            else:
                negative_weight += weight
        
        # Calculate score (0-10 scale)
        total_weight = positive_weight + negative_weight
        if total_weight == 0:
            return 5.0
        
        score = 5.0 + (positive_weight - negative_weight) / total_weight * 5.0
        return max(0.0, min(10.0, score))
    
    def _generate_recommendations(self, result: MetaReviewResult) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []
        
        # Group actionable insights by category
        actionable_insights = [i for i in result.insights if i.actionable]
        categories = set(i.category for i in actionable_insights)
        
        for category in categories:
            category_insights = [i for i in actionable_insights if i.category == category]
            if len(category_insights) >= 2:
                recommendations.append(f"Address multiple {category.replace('_', ' ')} issues identified")
        
        # Add specific high-confidence recommendations
        for insight in actionable_insights:
            if insight.confidence >= 0.8:
                recommendations.append(f"High priority: {insight.insight}")
        
        return recommendations
    
    def _generate_meta_insights(self, result: MetaReviewResult) -> List[str]:
        """Generate insights about the review process itself."""
        meta_insights = []
        
        # Analyze perspective convergence
        perspective_agreement = self._calculate_perspective_agreement(result)
        if perspective_agreement > 0.8:
            meta_insights.append("High agreement across perspectives suggests robust analysis")
        elif perspective_agreement < 0.3:
            meta_insights.append("Low agreement across perspectives - may need deeper investigation")
        
        # Analyze insight distribution
        category_distribution = {}
        for insight in result.insights:
            category_distribution[insight.category] = category_distribution.get(insight.category, 0) + 1
        
        if len(category_distribution) < 3:
            meta_insights.append("Limited analytical breadth - consider additional review dimensions")
        
        return meta_insights
    
    def _calculate_perspective_agreement(self, result: MetaReviewResult) -> float:
        """Calculate agreement level between different perspectives."""
        if len(result.perspectives_used) < 2:
            return 1.0
        
        # Simple heuristic: check for similar categories across perspectives
        perspective_categories = {}
        for perspective in result.perspectives_used:
            categories = set(i.category for i in result.get_insights_by_perspective(perspective))
            perspective_categories[perspective] = categories
        
        # Calculate Jaccard similarity between perspective categories
        perspectives = list(perspective_categories.keys())
        if len(perspectives) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(perspectives)):
            for j in range(i + 1, len(perspectives)):
                set1 = perspective_categories[perspectives[i]]
                set2 = perspective_categories[perspectives[j]]
                if len(set1) == 0 and len(set2) == 0:
                    similarity = 1.0
                elif len(set1) == 0 or len(set2) == 0:
                    similarity = 0.0
                else:
                    similarity = len(set1.intersection(set2)) / len(set1.union(set2))
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 1.0


class MentalGameAnalyzer:
    """Specialized analyzer for conducting "mental games" - systematic perspective-taking exercises."""
    
    def __init__(self, framework: MetaReviewFramework):
        self.framework = framework
    
    def play_skeptics_game(self, artifact: ReasoningArtifact) -> List[ReviewInsight]:
        """Play the skeptic's mental game to identify potential flaws."""
        return self.framework._skeptical_analysis(artifact, ReviewDepth.DEEP)
    
    def play_novice_game(self, artifact: ReasoningArtifact) -> List[ReviewInsight]:
        """Play the novice's mental game to assess accessibility."""
        return self.framework._novice_analysis(artifact, ReviewDepth.DEEP)
    
    def play_cross_domain_game(self, artifact: ReasoningArtifact, target_domain: str = "general") -> List[ReviewInsight]:
        """Play the cross-domain expert's mental game."""
        insights = self.framework._cross_domain_analysis(artifact, ReviewDepth.DEEP)
        
        # Add domain-specific analysis
        domain_insight = ReviewInsight(
            perspective=ReviewPerspective.CROSS_DOMAIN,
            category="domain_adaptation",
            insight=f"Consider adaptation requirements for {target_domain} domain",
            confidence=0.7,
            actionable=True
        )
        insights.append(domain_insight)
        
        return insights
    
    def conduct_mental_game_session(self, 
                                   artifact: ReasoningArtifact,
                                   games: Optional[List[str]] = None) -> MetaReviewResult:
        """Conduct a full mental game analysis session."""
        if games is None:
            games = ["skeptic", "novice", "cross_domain"]
        
        perspectives = []
        if "skeptic" in games:
            perspectives.append(ReviewPerspective.SKEPTICAL)
        if "novice" in games:
            perspectives.append(ReviewPerspective.NOVICE)
        if "cross_domain" in games:
            perspectives.append(ReviewPerspective.CROSS_DOMAIN)
        
        return self.framework.conduct_review(
            artifact=artifact,
            depth=ReviewDepth.DEEP,
            perspectives=perspectives
        )
