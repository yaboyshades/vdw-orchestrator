"""Collaborative and Social Meta-Review System.

Phase 8: Multi-reviewer consensus, expert-novice calibration, and social validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime
import statistics
import uuid

from .core import MetaReviewResult, ReviewInsight, ReviewPerspective, ReasoningArtifact


class ReviewerExpertise(Enum):
    """Levels of reviewer expertise."""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    DOMAIN_EXPERT = "domain_expert"


@dataclass
class Reviewer:
    """Represents a human or AI reviewer."""
    reviewer_id: str
    name: str
    expertise_level: ReviewerExpertise
    domain_specializations: List[str] = field(default_factory=list)
    review_count: int = 0
    average_agreement: float = 0.0  # Agreement with consensus
    calibration_score: float = 0.0  # How well-calibrated their confidence is
    active: bool = True
    
    def to_dict(self):
        return {
            "reviewer_id": self.reviewer_id,
            "name": self.name,
            "expertise_level": self.expertise_level.value,
            "domain_specializations": self.domain_specializations,
            "review_count": self.review_count,
            "average_agreement": self.average_agreement,
            "calibration_score": self.calibration_score,
            "active": self.active
        }


@dataclass
class CollaborativeReview:
    """Represents a multi-reviewer analysis of an artifact."""
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_id: str = ""
    individual_reviews: List[Tuple[Reviewer, MetaReviewResult]] = field(default_factory=list)
    consensus_review: Optional[MetaReviewResult] = None
    disagreement_analysis: Dict = field(default_factory=dict)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "in_progress"  # "in_progress", "consensus_reached", "irreconcilable_differences"


class ConsensusEngine:
    """Manages consensus building between multiple reviewers."""
    
    def __init__(self, agreement_threshold: float = 0.7):
        self.agreement_threshold = agreement_threshold
        
    def calculate_consensus(self, reviews: List[Tuple[Reviewer, MetaReviewResult]]) -> Dict:
        """Calculate consensus from multiple individual reviews."""
        if len(reviews) < 2:
            return {"error": "Need at least 2 reviews for consensus"}
        
        # Extract scores and insights
        scores = [review.overall_score for _, review in reviews]
        all_insights = []
        
        for reviewer, review in reviews:
            for insight in review.insights:
                all_insights.append((reviewer, insight))
        
        # Calculate consensus metrics
        consensus = {
            "overall_score": {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                "range": (min(scores), max(scores)),
                "agreement_level": self._calculate_score_agreement(scores)
            },
            "insight_consensus": self._analyze_insight_consensus(all_insights),
            "perspective_alignment": self._analyze_perspective_alignment(reviews),
            "confidence_weighted_score": self._calculate_confidence_weighted_score(reviews)
        }
        
        # Determine if consensus is reached
        consensus["consensus_reached"] = (
            consensus["overall_score"]["agreement_level"] >= self.agreement_threshold and
            consensus["insight_consensus"]["agreement_ratio"] >= self.agreement_threshold
        )
        
        return consensus
    
    def identify_disagreements(self, reviews: List[Tuple[Reviewer, MetaReviewResult]]) -> Dict:
        """Identify and categorize disagreements between reviewers."""
        disagreements = {
            "score_outliers": [],
            "conflicting_insights": [],
            "perspective_conflicts": [],
            "expertise_bias": {},
            "resolution_strategies": []
        }
        
        scores = [(reviewer.reviewer_id, review.overall_score) for reviewer, review in reviews]
        mean_score = statistics.mean([score for _, score in scores])
        std_dev = statistics.stdev([score for _, score in scores]) if len(scores) > 1 else 0.0
        
        # Identify score outliers (> 1.5 standard deviations from mean)
        threshold = 1.5 * std_dev
        for reviewer_id, score in scores:
            if abs(score - mean_score) > threshold:
                disagreements["score_outliers"].append({
                    "reviewer_id": reviewer_id,
                    "score": score,
                    "deviation": abs(score - mean_score)
                })
        
        # Analyze conflicting insights (same category, opposite sentiment)
        insights_by_category = {}
        for reviewer, review in reviews:
            for insight in review.insights:
                category = insight.category
                if category not in insights_by_category:
                    insights_by_category[category] = []
                insights_by_category[category].append((reviewer, insight))
        
        for category, category_insights in insights_by_category.items():
            if len(category_insights) >= 2:
                sentiments = self._analyze_insight_sentiments(category_insights)
                if len(set(sentiments)) > 1:  # Conflicting sentiments
                    disagreements["conflicting_insights"].append({
                        "category": category,
                        "conflict_count": len(set(sentiments)),
                        "insights": [(r.reviewer_id, i.insight) for r, i in category_insights]
                    })
        
        # Analyze expertise bias
        expert_scores = [review.overall_score for reviewer, review in reviews 
                        if reviewer.expertise_level == ReviewerExpertise.EXPERT]
        novice_scores = [review.overall_score for reviewer, review in reviews 
                        if reviewer.expertise_level == ReviewerExpertise.NOVICE]
        
        if expert_scores and novice_scores:
            expert_mean = statistics.mean(expert_scores)
            novice_mean = statistics.mean(novice_scores)
            bias_magnitude = abs(expert_mean - novice_mean)
            
            disagreements["expertise_bias"] = {
                "expert_mean": expert_mean,
                "novice_mean": novice_mean,
                "bias_magnitude": bias_magnitude,
                "significant": bias_magnitude > 1.0
            }
        
        # Generate resolution strategies
        disagreements["resolution_strategies"] = self._generate_resolution_strategies(disagreements)
        
        return disagreements
    
    def _calculate_score_agreement(self, scores: List[float]) -> float:
        """Calculate agreement level for scores (0.0 to 1.0)."""
        if len(scores) < 2:
            return 1.0
        
        std_dev = statistics.stdev(scores)
        # Normalize by range (0-10 scale) - lower std_dev = higher agreement
        return max(0.0, 1.0 - (std_dev / 5.0))  # 5.0 is half of score range
    
    def _analyze_insight_consensus(self, insights: List[Tuple[Reviewer, ReviewInsight]]) -> Dict:
        """Analyze consensus among insights."""
        category_counts = {}
        total_insights = len(insights)
        
        for reviewer, insight in insights:
            category = insight.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate agreement ratio (how many insights fall into agreed-upon categories)
        if not category_counts:
            return {"agreement_ratio": 1.0, "categories": {}}
        
        max_category_count = max(category_counts.values())
        agreement_ratio = max_category_count / total_insights if total_insights > 0 else 1.0
        
        return {
            "agreement_ratio": agreement_ratio,
            "categories": category_counts,
            "most_agreed_category": max(category_counts.keys(), key=category_counts.get)
        }
    
    def _analyze_perspective_alignment(self, reviews: List[Tuple[Reviewer, MetaReviewResult]]) -> Dict:
        """Analyze how well different perspectives align."""
        perspective_usage = {}
        
        for reviewer, review in reviews:
            for perspective in review.perspectives_used:
                if perspective not in perspective_usage:
                    perspective_usage[perspective] = []
                perspective_usage[perspective].append((reviewer, review))
        
        alignment = {
            "perspective_overlap": len(perspective_usage),
            "common_perspectives": [],
            "perspective_agreement": {}
        }
        
        # Find perspectives used by multiple reviewers
        for perspective, perspective_reviews in perspective_usage.items():
            if len(perspective_reviews) >= 2:
                alignment["common_perspectives"].append(perspective.value)
                
                # Calculate agreement within this perspective
                scores = [review.overall_score for _, review in perspective_reviews]
                perspective_agreement = self._calculate_score_agreement(scores)
                alignment["perspective_agreement"][perspective.value] = perspective_agreement
        
        return alignment
    
    def _calculate_confidence_weighted_score(self, reviews: List[Tuple[Reviewer, MetaReviewResult]]) -> float:
        """Calculate score weighted by reviewer confidence."""
        total_weighted = 0.0
        total_weight = 0.0
        
        for reviewer, review in reviews:
            # Use average confidence of insights as reviewer confidence
            if review.insights:
                avg_confidence = statistics.mean([insight.confidence for insight in review.insights])
            else:
                avg_confidence = 0.5  # Default neutral confidence
            
            weight = avg_confidence * self._get_expertise_weight(reviewer.expertise_level)
            total_weighted += review.overall_score * weight
            total_weight += weight
        
        return total_weighted / total_weight if total_weight > 0 else 0.0
    
    def _get_expertise_weight(self, expertise: ReviewerExpertise) -> float:
        """Get weight multiplier based on expertise level."""
        weights = {
            ReviewerExpertise.NOVICE: 0.7,
            ReviewerExpertise.INTERMEDIATE: 1.0,
            ReviewerExpertise.EXPERT: 1.3,
            ReviewerExpertise.DOMAIN_EXPERT: 1.5
        }
        return weights.get(expertise, 1.0)
    
    def _analyze_insight_sentiments(self, insights: List[Tuple[Reviewer, ReviewInsight]]) -> List[str]:
        """Simple sentiment analysis of insights."""
        sentiments = []
        
        for reviewer, insight in insights:
            # Simple heuristic - could be enhanced with NLP
            text = insight.insight.lower()
            
            if any(word in text for word in ['good', 'excellent', 'strong', 'clear', 'effective']):
                sentiments.append('positive')
            elif any(word in text for word in ['poor', 'weak', 'unclear', 'missing', 'lacking']):
                sentiments.append('negative')
            else:
                sentiments.append('neutral')
        
        return sentiments
    
    def _generate_resolution_strategies(self, disagreements: Dict) -> List[str]:
        """Generate strategies to resolve disagreements."""
        strategies = []
        
        if disagreements["score_outliers"]:
            strategies.append("Conduct focused discussion with outlier reviewers to understand divergent perspectives")
        
        if disagreements["conflicting_insights"]:
            strategies.append("Use structured debate format to examine conflicting insights with evidence")
        
        if disagreements.get("expertise_bias", {}).get("significant", False):
            strategies.append("Calibrate expert and novice perspectives through guided mentoring session")
        
        if not strategies:
            strategies.append("Continue with consensus - disagreement levels are within acceptable range")
        
        return strategies


class ReviewerCalibrationSystem:
    """Manages calibration of reviewers to maintain consistent standards."""
    
    def __init__(self):
        self.reviewers: Dict[str, Reviewer] = {}
        self.calibration_artifacts: List[ReasoningArtifact] = []
        self.consensus_engine = ConsensusEngine()
    
    def add_reviewer(self, reviewer: Reviewer):
        """Add a reviewer to the system."""
        self.reviewers[reviewer.reviewer_id] = reviewer
    
    def conduct_calibration_session(self, 
                                  artifact: ReasoningArtifact, 
                                  expert_baseline: MetaReviewResult) -> Dict:
        """Conduct calibration session where reviewers are compared against expert baseline."""
        calibration_results = {
            "artifact_id": artifact.id,
            "expert_baseline_score": expert_baseline.overall_score,
            "reviewer_results": {},
            "calibration_metrics": {},
            "improvement_recommendations": {}
        }
        
        # This would typically involve reviewers submitting their reviews
        # For now, we'll simulate the process structure
        
        for reviewer_id, reviewer in self.reviewers.items():
            if not reviewer.active:
                continue
                
            # In a real system, reviewer would submit their MetaReviewResult
            # calibration_results["reviewer_results"][reviewer_id] = {
            #     "submitted_score": reviewer_result.overall_score,
            #     "deviation_from_expert": abs(reviewer_result.overall_score - expert_baseline.overall_score),
            #     "insight_overlap": self._calculate_insight_overlap(reviewer_result, expert_baseline)
            # }
            
            pass
        
        return calibration_results
    
    def update_reviewer_calibration(self, reviewer_id: str, calibration_result: Dict):
        """Update reviewer's calibration metrics based on session results."""
        if reviewer_id not in self.reviewers:
            return
        
        reviewer = self.reviewers[reviewer_id]
        
        # Update calibration score based on alignment with expert baseline
        if "deviation_from_expert" in calibration_result:
            deviation = calibration_result["deviation_from_expert"]
            # Lower deviation = better calibration
            new_calibration = max(0.0, 1.0 - (deviation / 10.0))  # Normalize to 0-1 scale
            
            # Moving average with previous calibration score
            reviewer.calibration_score = (reviewer.calibration_score * 0.7 + new_calibration * 0.3)
        
        reviewer.review_count += 1
    
    def identify_miscalibrated_reviewers(self, threshold: float = 0.6) -> List[Reviewer]:
        """Identify reviewers who need additional calibration."""
        return [
            reviewer for reviewer in self.reviewers.values() 
            if reviewer.calibration_score < threshold and reviewer.review_count >= 3
        ]
    
    def recommend_reviewer_assignments(self, 
                                     artifact: ReasoningArtifact, 
                                     required_perspectives: List[ReviewPerspective]) -> List[Reviewer]:
        """Recommend optimal reviewer assignments for an artifact."""
        recommendations = []
        
        # Sort reviewers by calibration score and expertise relevance
        sorted_reviewers = sorted(
            [r for r in self.reviewers.values() if r.active],
            key=lambda r: (r.calibration_score, r.review_count),
            reverse=True
        )
        
        # Ensure we have representation across expertise levels
        expertise_coverage = {level: 0 for level in ReviewerExpertise}
        
        for reviewer in sorted_reviewers[:len(required_perspectives)]:
            recommendations.append(reviewer)
            expertise_coverage[reviewer.expertise_level] += 1
        
        return recommendations


class CollaborativeMetaReview:
    """Main orchestrator for collaborative meta-review processes."""
    
    def __init__(self):
        self.consensus_engine = ConsensusEngine()
        self.calibration_system = ReviewerCalibrationSystem()
        self.active_reviews: Dict[str, CollaborativeReview] = {}
    
    def initiate_collaborative_review(self, 
                                    artifact: ReasoningArtifact,
                                    required_reviewers: int = 3) -> str:
        """Start a collaborative review process."""
        
        review = CollaborativeReview(
            artifact_id=artifact.id
        )
        
        # Get reviewer recommendations
        required_perspectives = [ReviewPerspective.SKEPTICAL, ReviewPerspective.NOVICE, ReviewPerspective.CROSS_DOMAIN]
        recommended_reviewers = self.calibration_system.recommend_reviewer_assignments(
            artifact, required_perspectives
        )
        
        self.active_reviews[review.review_id] = review
        
        return review.review_id
    
    def submit_individual_review(self, 
                               review_id: str, 
                               reviewer: Reviewer, 
                               meta_review_result: MetaReviewResult):
        """Submit an individual reviewer's analysis."""
        if review_id not in self.active_reviews:
            raise ValueError(f"Review {review_id} not found")
        
        review = self.active_reviews[review_id]
        review.individual_reviews.append((reviewer, meta_review_result))
        
        # Check if we have enough reviews to calculate consensus
        if len(review.individual_reviews) >= 2:
            self._update_consensus(review_id)
    
    def _update_consensus(self, review_id: str):
        """Update consensus calculation for a collaborative review."""
        review = self.active_reviews[review_id]
        
        # Calculate consensus
        consensus_data = self.consensus_engine.calculate_consensus(review.individual_reviews)
        review.disagreement_analysis = self.consensus_engine.identify_disagreements(review.individual_reviews)
        
        # Update status based on consensus
        if consensus_data.get("consensus_reached", False):
            review.status = "consensus_reached"
        elif len(review.individual_reviews) >= 5:  # Max reviewers reached
            if consensus_data["overall_score"]["agreement_level"] < 0.3:
                review.status = "irreconcilable_differences"
            else:
                review.status = "consensus_reached"  # Accept weak consensus
    
    def get_collaborative_result(self, review_id: str) -> Dict:
        """Get the final collaborative review result."""
        if review_id not in self.active_reviews:
            return {"error": "Review not found"}
        
        review = self.active_reviews[review_id]
        
        if review.status == "in_progress":
            return {"status": "in_progress", "reviews_submitted": len(review.individual_reviews)}
        
        consensus_data = self.consensus_engine.calculate_consensus(review.individual_reviews)
        
        return {
            "review_id": review_id,
            "status": review.status,
            "artifact_id": review.artifact_id,
            "reviewer_count": len(review.individual_reviews),
            "consensus_score": consensus_data["overall_score"]["mean"],
            "confidence_weighted_score": consensus_data["confidence_weighted_score"],
            "agreement_level": consensus_data["overall_score"]["agreement_level"],
            "disagreement_analysis": review.disagreement_analysis,
            "individual_scores": [result.overall_score for _, result in review.individual_reviews],
            "resolution_strategies": review.disagreement_analysis.get("resolution_strategies", [])
        }
