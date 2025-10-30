"""Meta-Meta Analysis and Recursive Improvement System.

Phase 9: Recursive analysis of the review process itself, self-improving systems,
and detection of diminishing returns in meta-cognitive analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import statistics
from enum import Enum

from .core import MetaReviewResult, MetaReviewFramework
from .collaborative import CollaborativeMetaReview


class MetaAnalysisDepth(Enum):
    """Levels of meta-analysis depth."""
    META = "meta"  # Review of reviews
    META_META = "meta_meta"  # Review of review processes
    META_META_META = "meta_meta_meta"  # Review of meta-review methodology


@dataclass
class MetaMetaInsight:
    """Insights about the review process itself."""
    depth_level: MetaAnalysisDepth
    category: str
    insight: str
    evidence: List[str] = field(default_factory=list)
    impact_assessment: str = ""  # How this affects review quality
    actionable_improvement: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ProcessImprovement:
    """Represents an improvement to the meta-review process."""
    improvement_id: str
    description: str
    rationale: str
    implementation_complexity: str  # "low", "medium", "high"
    expected_impact: float  # 0.0 to 1.0
    implementation_date: Optional[datetime] = None
    effectiveness_measured: Optional[float] = None  # Post-implementation measurement


class RecursiveAnalyzer:
    """Analyzes the meta-review process recursively to identify improvements."""
    
    def __init__(self):
        self.process_history: List[Dict] = []
        self.improvement_history: List[ProcessImprovement] = []
        self.diminishing_returns_threshold = 0.1  # Minimum improvement to be worthwhile
    
    def analyze_review_process(self, review_results: List[MetaReviewResult]) -> List[MetaMetaInsight]:
        """Conduct meta-meta analysis of the review process itself."""
        if len(review_results) < 3:
            return [MetaMetaInsight(
                depth_level=MetaAnalysisDepth.META,
                category="insufficient_data",
                insight="Need at least 3 reviews for meaningful process analysis",
                confidence=1.0
            )]
        
        meta_insights = []
        
        # Analyze review consistency
        consistency_insights = self._analyze_review_consistency(review_results)
        meta_insights.extend(consistency_insights)
        
        # Analyze perspective effectiveness
        perspective_insights = self._analyze_perspective_effectiveness(review_results)
        meta_insights.extend(perspective_insights)
        
        # Analyze insight quality over time
        quality_insights = self._analyze_insight_quality_trends(review_results)
        meta_insights.extend(quality_insights)
        
        # Analyze reviewer behavior patterns
        behavior_insights = self._analyze_reviewer_behavior_patterns(review_results)
        meta_insights.extend(behavior_insights)
        
        return meta_insights
    
    def detect_diminishing_returns(self, improvement_history: List[ProcessImprovement]) -> Dict:
        """Detect when additional meta-analysis provides diminishing returns."""
        if len(improvement_history) < 5:
            return {"status": "insufficient_data", "recommendation": "continue_analysis"}
        
        # Look at recent improvements
        recent_improvements = improvement_history[-5:]
        recent_effectiveness = [imp.effectiveness_measured for imp in recent_improvements 
                              if imp.effectiveness_measured is not None]
        
        if len(recent_effectiveness) < 3:
            return {"status": "pending_measurements", "recommendation": "measure_recent_improvements"}
        
        # Calculate trend
        avg_recent = statistics.mean(recent_effectiveness)
        
        # Compare with earlier improvements
        if len(improvement_history) >= 10:
            earlier_improvements = improvement_history[-10:-5]
            earlier_effectiveness = [imp.effectiveness_measured for imp in earlier_improvements 
                                   if imp.effectiveness_measured is not None]
            
            if earlier_effectiveness:
                avg_earlier = statistics.mean(earlier_effectiveness)
                improvement_rate = avg_recent - avg_earlier
                
                diminishing_returns = {
                    "status": "analyzed",
                    "recent_avg_effectiveness": avg_recent,
                    "earlier_avg_effectiveness": avg_earlier,
                    "improvement_rate": improvement_rate,
                    "diminishing_returns_detected": improvement_rate < self.diminishing_returns_threshold
                }
                
                if improvement_rate < self.diminishing_returns_threshold:
                    diminishing_returns["recommendation"] = "reduce_analysis_depth"
                    diminishing_returns["suggested_actions"] = [
                        "Focus on high-impact improvements only",
                        "Reduce frequency of meta-meta analysis",
                        "Switch to maintenance mode for review process"
                    ]
                else:
                    diminishing_returns["recommendation"] = "continue_analysis"
                
                return diminishing_returns
        
        return {"status": "continue_monitoring", "recommendation": "need_more_data"}
    
    def generate_process_improvements(self, meta_insights: List[MetaMetaInsight]) -> List[ProcessImprovement]:
        """Generate actionable improvements based on meta-insights."""
        improvements = []
        
        for insight in meta_insights:
            if insight.actionable_improvement and insight.confidence >= 0.7:
                improvement = ProcessImprovement(
                    improvement_id=f"imp_{len(self.improvement_history) + len(improvements) + 1}",
                    description=insight.actionable_improvement,
                    rationale=insight.insight,
                    implementation_complexity=self._assess_implementation_complexity(insight),
                    expected_impact=insight.confidence * self._assess_potential_impact(insight)
                )
                improvements.append(improvement)
        
        return improvements
    
    def _analyze_review_consistency(self, reviews: List[MetaReviewResult]) -> List[MetaMetaInsight]:
        """Analyze consistency of review processes."""
        insights = []
        
        # Check score consistency
        scores = [review.overall_score for review in reviews]
        if len(scores) >= 3:
            score_std = statistics.stdev(scores)
            
            if score_std > 2.0:  # High variance
                insights.append(MetaMetaInsight(
                    depth_level=MetaAnalysisDepth.META,
                    category="consistency_issue",
                    insight=f"High score variance ({score_std:.2f}) suggests inconsistent review standards",
                    evidence=[f"Score range: {min(scores):.1f} - {max(scores):.1f}"],
                    impact_assessment="Reduces reliability of review outcomes",
                    actionable_improvement="Implement reviewer calibration sessions",
                    confidence=0.8
                ))
        
        # Check perspective usage consistency
        perspective_usage = {}
        for review in reviews:
            for perspective in review.perspectives_used:
                perspective_usage[perspective] = perspective_usage.get(perspective, 0) + 1
        
        total_reviews = len(reviews)
        inconsistent_perspectives = [
            perspective for perspective, count in perspective_usage.items()
            if count < total_reviews * 0.7  # Used in less than 70% of reviews
        ]
        
        if inconsistent_perspectives:
            insights.append(MetaMetaInsight(
                depth_level=MetaAnalysisDepth.META,
                category="perspective_inconsistency",
                insight=f"Inconsistent perspective usage: {[p.value for p in inconsistent_perspectives]}",
                evidence=[f"{p.value}: {perspective_usage[p]}/{total_reviews} reviews" for p in inconsistent_perspectives],
                impact_assessment="Reduces comprehensiveness of analysis",
                actionable_improvement="Standardize required perspectives for all reviews",
                confidence=0.9
            ))
        
        return insights
    
    def _analyze_perspective_effectiveness(self, reviews: List[MetaReviewResult]) -> List[MetaMetaInsight]:
        """Analyze which perspectives provide the most valuable insights."""
        insights = []
        
        perspective_insight_quality = {}
        
        for review in reviews:
            for perspective in review.perspectives_used:
                if perspective not in perspective_insight_quality:
                    perspective_insight_quality[perspective] = []
                
                # Get insights from this perspective
                perspective_insights = [i for i in review.insights if i.perspective == perspective]
                
                if perspective_insights:
                    avg_confidence = statistics.mean([i.confidence for i in perspective_insights])
                    actionable_ratio = sum(1 for i in perspective_insights if i.actionable) / len(perspective_insights)
                    
                    quality_score = (avg_confidence + actionable_ratio) / 2
                    perspective_insight_quality[perspective].append(quality_score)
        
        # Analyze effectiveness
        for perspective, quality_scores in perspective_insight_quality.items():
            if len(quality_scores) >= 2:
                avg_quality = statistics.mean(quality_scores)
                
                if avg_quality < 0.5:
                    insights.append(MetaMetaInsight(
                        depth_level=MetaAnalysisDepth.META,
                        category="perspective_effectiveness",
                        insight=f"{perspective.value} perspective shows low effectiveness (avg: {avg_quality:.2f})",
                        evidence=[f"Quality scores: {quality_scores}"],
                        impact_assessment="May be providing limited value relative to effort",
                        actionable_improvement=f"Review and refine {perspective.value} analysis methods",
                        confidence=0.7
                    ))
                elif avg_quality > 0.8:
                    insights.append(MetaMetaInsight(
                        depth_level=MetaAnalysisDepth.META,
                        category="perspective_effectiveness",
                        insight=f"{perspective.value} perspective shows high effectiveness (avg: {avg_quality:.2f})",
                        evidence=[f"Quality scores: {quality_scores}"],
                        impact_assessment="Provides high-value insights consistently",
                        actionable_improvement=f"Consider expanding {perspective.value} analysis depth",
                        confidence=0.8
                    ))
        
        return insights
    
    def _analyze_insight_quality_trends(self, reviews: List[MetaReviewResult]) -> List[MetaMetaInsight]:
        """Analyze trends in insight quality over time."""
        insights = []
        
        if len(reviews) < 5:
            return insights
        
        # Sort by creation date
        sorted_reviews = sorted(reviews, key=lambda r: r.created_at)
        
        # Calculate quality metrics over time
        quality_over_time = []
        
        for review in sorted_reviews:
            if review.insights:
                avg_confidence = statistics.mean([i.confidence for i in review.insights])
                actionable_ratio = sum(1 for i in review.insights if i.actionable) / len(review.insights)
                overall_quality = (avg_confidence + actionable_ratio) / 2
                quality_over_time.append(overall_quality)
            else:
                quality_over_time.append(0.0)
        
        # Analyze trend
        if len(quality_over_time) >= 5:
            # Simple linear trend analysis
            n = len(quality_over_time)
            x_values = list(range(n))
            y_values = quality_over_time
            
            # Calculate correlation coefficient
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(y_values)
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
            denominator_x = sum((x - mean_x) ** 2 for x in x_values)
            denominator_y = sum((y - mean_y) ** 2 for y in y_values)
            
            if denominator_x > 0 and denominator_y > 0:
                correlation = numerator / (denominator_x * denominator_y) ** 0.5
                
                if correlation > 0.6:
                    insights.append(MetaMetaInsight(
                        depth_level=MetaAnalysisDepth.META,
                        category="quality_trend",
                        insight=f"Insight quality improving over time (correlation: {correlation:.2f})",
                        evidence=[f"Quality progression: {[f'{q:.2f}' for q in quality_over_time]}"],
                        impact_assessment="Review process is learning and improving",
                        actionable_improvement="Continue current approach and document successful patterns",
                        confidence=0.8
                    ))
                elif correlation < -0.6:
                    insights.append(MetaMetaInsight(
                        depth_level=MetaAnalysisDepth.META,
                        category="quality_trend",
                        insight=f"Insight quality declining over time (correlation: {correlation:.2f})",
                        evidence=[f"Quality progression: {[f'{q:.2f}' for q in quality_over_time]}"],
                        impact_assessment="Review process may be degrading or experiencing fatigue",
                        actionable_improvement="Investigate causes of quality decline and implement corrective measures",
                        confidence=0.8
                    ))
        
        return insights
    
    def _analyze_reviewer_behavior_patterns(self, reviews: List[MetaReviewResult]) -> List[MetaMetaInsight]:
        """Analyze patterns in reviewer behavior that might affect quality."""
        insights = []
        
        # Analyze insight distribution patterns
        insight_counts = [len(review.insights) for review in reviews]
        
        if insight_counts:
            avg_insights = statistics.mean(insight_counts)
            std_insights = statistics.stdev(insight_counts) if len(insight_counts) > 1 else 0
            
            # Check for extreme variability
            if std_insights > avg_insights * 0.5:  # High coefficient of variation
                insights.append(MetaMetaInsight(
                    depth_level=MetaAnalysisDepth.META,
                    category="reviewer_behavior",
                    insight=f"High variability in insight generation (avg: {avg_insights:.1f}, std: {std_insights:.1f})",
                    evidence=[f"Insight counts per review: {insight_counts}"],
                    impact_assessment="Suggests inconsistent reviewer engagement or capability",
                    actionable_improvement="Provide guidelines for minimum insight requirements per review",
                    confidence=0.7
                ))
        
        # Analyze recommendation patterns
        recommendation_counts = [len(review.recommendations) for review in reviews]
        
        if recommendation_counts:
            zero_recommendation_count = sum(1 for count in recommendation_counts if count == 0)
            
            if zero_recommendation_count > len(reviews) * 0.3:  # More than 30% have no recommendations
                insights.append(MetaMetaInsight(
                    depth_level=MetaAnalysisDepth.META,
                    category="reviewer_behavior",
                    insight=f"{zero_recommendation_count}/{len(reviews)} reviews provided no recommendations",
                    evidence=[f"Recommendation counts: {recommendation_counts}"],
                    impact_assessment="Reduces actionability of review outcomes",
                    actionable_improvement="Train reviewers on generating actionable recommendations",
                    confidence=0.8
                ))
        
        return insights
    
    def _assess_implementation_complexity(self, insight: MetaMetaInsight) -> str:
        """Assess implementation complexity of an improvement."""
        improvement = insight.actionable_improvement or ""
        
        if any(keyword in improvement.lower() for keyword in ['train', 'calibrat', 'session']):
            return "medium"  # Requires human coordination
        elif any(keyword in improvement.lower() for keyword in ['implement', 'standard', 'require']):
            return "low"  # Code/process changes
        elif any(keyword in improvement.lower() for keyword in ['investigate', 'research', 'develop']):
            return "high"  # Requires research and development
        else:
            return "medium"  # Default
    
    def _assess_potential_impact(self, insight: MetaMetaInsight) -> float:
        """Assess potential impact of implementing an improvement."""
        impact_assessment = insight.impact_assessment.lower()
        
        if any(keyword in impact_assessment for keyword in ['reliability', 'comprehensiveness', 'quality']):
            return 0.8  # High impact on core review quality
        elif any(keyword in impact_assessment for keyword in ['efficiency', 'consistency']):
            return 0.6  # Medium impact on process
        elif any(keyword in impact_assessment for keyword in ['limited', 'minor']):
            return 0.3  # Low impact
        else:
            return 0.5  # Default moderate impact


class SelfImprovingReviewSystem:
    """A meta-review system that automatically improves itself based on recursive analysis."""
    
    def __init__(self):
        self.recursive_analyzer = RecursiveAnalyzer()
        self.base_framework = MetaReviewFramework()
        self.improvement_log: List[ProcessImprovement] = []
        self.system_version = "1.0.0"
        self.auto_improvement_enabled = True
        
    def conduct_recursive_analysis(self, review_history: List[MetaReviewResult]) -> Dict:
        """Conduct recursive analysis and generate improvement recommendations."""
        
        # Perform meta-meta analysis
        meta_insights = self.recursive_analyzer.analyze_review_process(review_history)
        
        # Generate improvements
        potential_improvements = self.recursive_analyzer.generate_process_improvements(meta_insights)
        
        # Check for diminishing returns
        diminishing_returns = self.recursive_analyzer.detect_diminishing_returns(self.improvement_log)
        
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "meta_insights": [
                {
                    "depth_level": insight.depth_level.value,
                    "category": insight.category,
                    "insight": insight.insight,
                    "evidence": insight.evidence,
                    "impact_assessment": insight.impact_assessment,
                    "actionable_improvement": insight.actionable_improvement,
                    "confidence": insight.confidence
                }
                for insight in meta_insights
            ],
            "potential_improvements": [
                {
                    "improvement_id": imp.improvement_id,
                    "description": imp.description,
                    "rationale": imp.rationale,
                    "complexity": imp.implementation_complexity,
                    "expected_impact": imp.expected_impact
                }
                for imp in potential_improvements
            ],
            "diminishing_returns": diminishing_returns,
            "system_version": self.system_version
        }
        
        # Auto-implement low-complexity, high-impact improvements
        if self.auto_improvement_enabled:
            auto_implemented = self._auto_implement_improvements(potential_improvements)
            analysis_result["auto_implemented"] = auto_implemented
        
        return analysis_result
    
    def _auto_implement_improvements(self, improvements: List[ProcessImprovement]) -> List[str]:
        """Automatically implement suitable improvements."""
        implemented = []
        
        for improvement in improvements:
            if (improvement.implementation_complexity == "low" and 
                improvement.expected_impact >= 0.6):
                
                # This is where actual implementation would occur
                # For now, we'll just simulate the process
                success = self._simulate_implementation(improvement)
                
                if success:
                    improvement.implementation_date = datetime.now()
                    self.improvement_log.append(improvement)
                    implemented.append(improvement.improvement_id)
        
        return implemented
    
    def _simulate_implementation(self, improvement: ProcessImprovement) -> bool:
        """Simulate implementation of an improvement."""
        # In a real system, this would contain actual implementation logic
        # For example, updating validation thresholds, modifying analysis algorithms, etc.
        
        if "standard" in improvement.description.lower():
            # Simulate updating standards
            return True
        elif "require" in improvement.description.lower():
            # Simulate updating requirements
            return True
        elif "threshold" in improvement.description.lower():
            # Simulate updating thresholds
            return True
        
        return False  # Default: manual implementation required
    
    def measure_improvement_effectiveness(self, 
                                       improvement_id: str, 
                                       before_metrics: Dict, 
                                       after_metrics: Dict) -> float:
        """Measure the effectiveness of an implemented improvement."""
        
        improvement = next((imp for imp in self.improvement_log if imp.improvement_id == improvement_id), None)
        if not improvement:
            return 0.0
        
        # Simple effectiveness calculation based on score improvement
        before_avg = before_metrics.get("average_score", 0.0)
        after_avg = after_metrics.get("average_score", 0.0)
        
        effectiveness = (after_avg - before_avg) / 10.0  # Normalize to 0-1 scale
        improvement.effectiveness_measured = max(0.0, effectiveness)
        
        return effectiveness
    
    def get_system_evolution_report(self) -> Dict:
        """Generate a report on how the system has evolved over time."""
        
        implemented_improvements = [imp for imp in self.improvement_log if imp.implementation_date]
        
        report = {
            "system_version": self.system_version,
            "total_improvements": len(self.improvement_log),
            "implemented_improvements": len(implemented_improvements),
            "average_improvement_impact": 0.0,
            "improvement_timeline": [],
            "current_capabilities": [],
            "next_evolution_targets": []
        }
        
        if implemented_improvements:
            measured_improvements = [imp for imp in implemented_improvements if imp.effectiveness_measured is not None]
            
            if measured_improvements:
                report["average_improvement_impact"] = statistics.mean(
                    [imp.effectiveness_measured for imp in measured_improvements]
                )
            
            # Timeline of improvements
            for improvement in sorted(implemented_improvements, key=lambda x: x.implementation_date):
                report["improvement_timeline"].append({
                    "date": improvement.implementation_date.isoformat(),
                    "description": improvement.description,
                    "impact": improvement.effectiveness_measured
                })
        
        return report
