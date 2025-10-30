"""Synthesis and Integration of Meta-Insights.

Phase 6: Cross-pattern analysis, adaptive review protocols, context-sensitive 
checklists, and escalation triggers for comprehensive meta-review integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
import json

from .core import MetaReviewResult, ReviewInsight, ReviewPerspective, ReasoningArtifact, ReviewDepth
from .collaborative import CollaborativeReview, Reviewer
from .temporal import ReasoningVersionControl
from .recursive import MetaMetaInsight, RecursiveAnalyzer


class InsightPattern(Enum):
    """Types of cross-cutting insight patterns."""
    RECURRING_WEAKNESS = "recurring_weakness"
    STRENGTH_AMPLIFIER = "strength_amplifier" 
    PERSPECTIVE_BIAS = "perspective_bias"
    CONTEXTUAL_DEPENDENCY = "contextual_dependency"
    EVOLUTION_TREND = "evolution_trend"


class ContextType(Enum):
    """Different contexts that affect review approach."""
    DOMAIN = "domain"  # Technical domain (AI, web dev, etc.)
    COMPLEXITY = "complexity"  # Simple, moderate, complex
    STAKEHOLDER = "stakeholder"  # Team size, expertise level
    TIMELINE = "timeline"  # Urgent, standard, research
    RISK_LEVEL = "risk_level"  # Low, medium, high impact


@dataclass
class CrossPatternInsight:
    """Insights that emerge from analyzing patterns across multiple reviews."""
    pattern_type: InsightPattern
    affected_perspectives: List[ReviewPerspective]
    evidence_sources: List[str]  # Review IDs or artifact IDs
    pattern_strength: float  # 0.0 to 1.0
    context_dependencies: Dict[ContextType, List[str]]
    synthesis_insight: str
    recommended_adaptations: List[str]
    confidence: float = 0.0


@dataclass
class AdaptiveReviewProtocol:
    """Context-sensitive review protocol with adaptive parameters."""
    protocol_id: str
    name: str
    context_triggers: Dict[ContextType, List[str]]
    adapted_parameters: Dict[str, Any]  # min_score, required_perspectives, etc.
    escalation_rules: List[str]
    success_metrics: Dict[str, float]
    usage_count: int = 0
    effectiveness_score: float = 0.0


class CrossPatternAnalyzer:
    """Analyzes patterns across multiple reviews to generate synthesis insights."""
    
    def __init__(self):
        self.pattern_history: List[CrossPatternInsight] = []
        self.context_cache: Dict[str, Dict[ContextType, str]] = {}
    
    def analyze_cross_patterns(self, review_results: List[MetaReviewResult]) -> List[CrossPatternInsight]:
        """Identify patterns that emerge across multiple reviews."""
        
        if len(review_results) < 5:
            return []
        
        patterns = []
        patterns.extend(self._analyze_recurring_weaknesses(review_results))
        patterns.extend(self._analyze_strength_amplifiers(review_results))
        patterns.extend(self._analyze_perspective_biases(review_results))
        
        return patterns
    
    def _analyze_recurring_weaknesses(self, reviews: List[MetaReviewResult]) -> List[CrossPatternInsight]:
        """Find weaknesses that appear across multiple reviews."""
        patterns = []
        category_insights = defaultdict(list)
        
        for review in reviews:
            for insight in review.insights:
                if insight.category not in ["strengths", "good_practices"]:
                    category_insights[insight.category].append((review.review_id, insight))
        
        for category, insights_list in category_insights.items():
            if len(insights_list) >= 3:
                review_ids = [review_id for review_id, _ in insights_list]
                unique_reviews = len(set(review_ids))
                
                if unique_reviews >= 3:
                    pattern = CrossPatternInsight(
                        pattern_type=InsightPattern.RECURRING_WEAKNESS,
                        affected_perspectives=[insight.perspective for _, insight in insights_list],
                        evidence_sources=list(set(review_ids)),
                        pattern_strength=min(1.0, unique_reviews / len(reviews)),
                        context_dependencies={},
                        synthesis_insight=f"Recurring weakness in {category}",
                        recommended_adaptations=[f"Develop specialized checklist for {category} issues"],
                        confidence=0.8
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_strength_amplifiers(self, reviews: List[MetaReviewResult]) -> List[CrossPatternInsight]:
        """Find strengths that consistently lead to higher scores."""
        patterns = []
        high_scoring_reviews = [r for r in reviews if r.overall_score >= 8.5]
        
        if len(high_scoring_reviews) < 3:
            return patterns
        
        strength_categories = defaultdict(int)
        for review in high_scoring_reviews:
            strength_insights = [i for i in review.insights if i.category in ["strengths", "good_practices"]]
            for insight in strength_insights:
                strength_categories[insight.category] += 1
        
        min_appearances = max(2, len(high_scoring_reviews) * 0.6)
        
        for category, count in strength_categories.items():
            if count >= min_appearances:
                pattern = CrossPatternInsight(
                    pattern_type=InsightPattern.STRENGTH_AMPLIFIER,
                    affected_perspectives=[ReviewPerspective.SKEPTICAL],
                    evidence_sources=[r.review_id for r in high_scoring_reviews],
                    pattern_strength=count / len(high_scoring_reviews),
                    context_dependencies={},
                    synthesis_insight=f"Strength amplifier: {category} correlates with high scores",
                    recommended_adaptations=[f"Prioritize {category} in review guidance"],
                    confidence=0.9
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_perspective_biases(self, reviews: List[MetaReviewResult]) -> List[CrossPatternInsight]:
        """Identify systematic biases in different perspectives."""
        patterns = []
        perspective_scores = defaultdict(list)
        
        for review in reviews:
            for perspective in review.perspectives_used:
                perspective_insights = [i for i in review.insights if i.perspective == perspective]
                if perspective_insights:
                    avg_confidence = statistics.mean([i.confidence for i in perspective_insights])
                    perspective_scores[perspective].append(review.overall_score * avg_confidence)
        
        for perspective, scores in perspective_scores.items():
            if len(scores) >= 3:
                avg_score = statistics.mean(scores)
                overall_avg = statistics.mean([r.overall_score for r in reviews])
                bias_magnitude = abs(avg_score - overall_avg)
                
                if bias_magnitude > 0.5:
                    bias_direction = "positive" if avg_score > overall_avg else "negative"
                    pattern = CrossPatternInsight(
                        pattern_type=InsightPattern.PERSPECTIVE_BIAS,
                        affected_perspectives=[perspective],
                        evidence_sources=[r.review_id for r in reviews if perspective in r.perspectives_used],
                        pattern_strength=min(1.0, bias_magnitude / 2.0),
                        context_dependencies={},
                        synthesis_insight=f"{perspective.value} shows {bias_direction} bias",
                        recommended_adaptations=[f"Calibrate {perspective.value} perspective scoring"],
                        confidence=0.7
                    )
                    patterns.append(pattern)
        
        return patterns


class SynthesisEngine:
    """Main orchestrator for synthesis and integration of meta-insights."""
    
    def __init__(self):
        self.cross_pattern_analyzer = CrossPatternAnalyzer()
        self.synthesis_history: List[Dict] = []
    
    def synthesize_meta_insights(self, review_results: List[MetaReviewResult]) -> Dict[str, Any]:
        """Perform comprehensive synthesis of meta-insights."""
        
        if len(review_results) < 3:
            return {"status": "insufficient_data", "review_count": len(review_results)}
        
        cross_patterns = self.cross_pattern_analyzer.analyze_cross_patterns(review_results)
        
        synthesis_result = {
            "synthesis_timestamp": datetime.now().isoformat(),
            "input_data_summary": {"review_count": len(review_results)},
            "cross_pattern_insights": [{
                "pattern_type": p.pattern_type.value,
                "affected_perspectives": [per.value for per in p.affected_perspectives],
                "evidence_sources": p.evidence_sources,
                "pattern_strength": p.pattern_strength,
                "synthesis_insight": p.synthesis_insight,
                "recommended_adaptations": p.recommended_adaptations,
                "confidence": p.confidence
            } for p in cross_patterns],
            "integration_recommendations": self._generate_integration_recommendations(cross_patterns)
        }
        
        self.synthesis_history.append(synthesis_result)
        return synthesis_result
    
    def _generate_integration_recommendations(self, patterns: List[CrossPatternInsight]) -> List[str]:
        """Generate actionable recommendations for integrating insights."""
        
        recommendations = []
        
        recurring_weaknesses = [p for p in patterns if p.pattern_type == InsightPattern.RECURRING_WEAKNESS]
        if recurring_weaknesses:
            recommendations.append(f"Address {len(recurring_weaknesses)} recurring weakness patterns")
        
        strength_amplifiers = [p for p in patterns if p.pattern_type == InsightPattern.STRENGTH_AMPLIFIER]
        if strength_amplifiers:
            recommendations.append(f"Leverage {len(strength_amplifiers)} strength amplifiers")
        
        return recommendations