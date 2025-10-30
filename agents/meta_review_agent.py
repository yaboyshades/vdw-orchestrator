"""Meta-Review Agent for VDW Phase Validation.

This agent automatically runs meta-review analysis on phase outputs
and determines if phases should advance or be held for improvement.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import asdict

from .base_phase_agent import BasePhaseAgent
from core.models import ProjectContext
from reasoning.meta_review.core import MetaReviewFramework, ReasoningArtifact, ReviewDepth
from reasoning.meta_review.validators import ValidationGates, QualityMetrics  
from reasoning.meta_review.integration import VDWIntegration


class MetaReviewAgent(BasePhaseAgent):
    """Agent that performs meta-review analysis on VDW phase outputs."""
    
    def __init__(self, agent_id: str = "meta_review_agent"):
        super().__init__(agent_id)
        self.framework = MetaReviewFramework()
        self.gates = ValidationGates(
            min_score=7.5,
            min_breadth=3,
            require_meta_insights=True
        )
        self.metrics = QualityMetrics()
        self.integration = VDWIntegration(
            framework=self.framework,
            gates=self.gates, 
            metrics=self.metrics
        )
        
    async def execute(self, context: ProjectContext) -> Dict:
        """Execute meta-review on the current phase output."""
        
        # Extract phase information from context
        current_phase = context.current_phase
        phase_output = getattr(context, f"{current_phase}_output", "")
        
        if not phase_output:
            self.logger.warning(f"No output found for {current_phase}")
            return {
                "success": False,
                "error": f"No output available for {current_phase}",
                "can_advance": False
            }
        
        # Run meta-review analysis
        try:
            review_result = self.integration.review_phase_output(
                title=f"{current_phase.title()} Output Review",
                content=str(phase_output),
                phase=current_phase,
                author="vdw_orchestrator"
            )
            
            can_advance = self.integration.should_advance_phase(review_result)
            
            # Log review summary
            self.logger.info(f"Meta-review completed for {current_phase}")
            self.logger.info(f"Overall score: {review_result['result']['overall_score']:.2f}")
            self.logger.info(f"Can advance: {can_advance}")
            
            if not can_advance:
                self.logger.warning(f"Phase {current_phase} held due to validation errors:")
                for error in review_result["validation_errors"]:
                    self.logger.warning(f"  - {error}")
            
            return {
                "success": True,
                "review_result": review_result,
                "can_advance": can_advance,
                "overall_score": review_result["result"]["overall_score"],
                "recommendations": review_result["result"]["recommendations"],
                "validation_errors": review_result["validation_errors"],
                "metrics": review_result["metrics"]
            }
            
        except Exception as e:
            self.logger.error(f"Meta-review failed for {current_phase}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "can_advance": True  # Fail open to avoid blocking
            }
    
    def set_validation_thresholds(self, min_score: float = 7.5, min_breadth: int = 3):
        """Update validation gate thresholds."""
        self.gates.min_score = min_score
        self.gates.min_breadth = min_breadth
        self.logger.info(f"Updated thresholds: min_score={min_score}, min_breadth={min_breadth}")
        
    def get_review_history(self) -> List[Dict]:
        """Get history of all meta-reviews conducted."""
        return [
            {
                "review_id": result.review_id,
                "artifact_id": result.artifact_id,
                "overall_score": result.overall_score,
                "depth_level": result.depth_level.value,
                "perspectives_used": [p.value for p in result.perspectives_used],
                "created_at": result.created_at.isoformat(),
                "insight_count": len(result.insights),
                "recommendation_count": len(result.recommendations)
            }
            for result in self.framework.review_history
        ]
