"""MCP Server Tools for Meta-Review System.

Phase 10: Complete VDW Integration with MCP-compatible server components.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .core import MetaReviewFramework, ReasoningArtifact, ReviewDepth
from .validators import ValidationGates, QualityMetrics
from .integration import VDWIntegration
from .temporal import ReasoningVersionControl
from .collaborative import CollaborativeMetaReview, Reviewer, ReviewerExpertise
from .recursive import SelfImprovingReviewSystem


class MetaReviewMCPServer:
    """MCP Server that exposes meta-review capabilities as tools."""
    
    def __init__(self):
        self.framework = MetaReviewFramework()
        self.integration = VDWIntegration(
            framework=self.framework,
            gates=ValidationGates(),
            metrics=QualityMetrics()
        )
        self.version_control = ReasoningVersionControl()
        self.collaborative_system = CollaborativeMetaReview()
        self.recursive_system = SelfImprovingReviewSystem()
        
        # Initialize with some default reviewers
        self._initialize_default_reviewers()
    
    def _initialize_default_reviewers(self):
        """Initialize some default AI reviewers."""
        reviewers = [
            Reviewer(
                reviewer_id="skeptic_ai",
                name="Skeptical AI Reviewer",
                expertise_level=ReviewerExpertise.EXPERT,
                domain_specializations=["critical_analysis", "evidence_evaluation"]
            ),
            Reviewer(
                reviewer_id="novice_ai",
                name="Novice-Perspective AI",
                expertise_level=ReviewerExpertise.NOVICE,
                domain_specializations=["accessibility", "clarity"]
            ),
            Reviewer(
                reviewer_id="domain_expert_ai",
                name="Cross-Domain Expert AI",
                expertise_level=ReviewerExpertise.DOMAIN_EXPERT,
                domain_specializations=["transferability", "generalization"]
            )
        ]
        
        for reviewer in reviewers:
            self.collaborative_system.calibration_system.add_reviewer(reviewer)
    
    # MCP Tool Implementations
    
    def tool_conduct_meta_review(self, 
                                title: str,
                                content: str,
                                phase: str = "unknown",
                                author: str = "user",
                                depth: str = "standard") -> Dict[str, Any]:
        """MCP Tool: Conduct a comprehensive meta-review of reasoning content.
        
        Args:
            title: Title of the reasoning artifact
            content: The reasoning content to review
            phase: VDW phase (phase1, phase2, etc.)
            author: Author of the content
            depth: Review depth (surface, standard, deep, meta_meta)
        
        Returns:
            Complete meta-review analysis with scores, insights, and recommendations
        """
        try:
            depth_enum = ReviewDepth(depth)
        except ValueError:
            depth_enum = ReviewDepth.STANDARD
        
        result = self.integration.review_phase_output(
            title=title,
            content=content,
            phase=phase,
            author=author
        )
        
        # Add version tracking
        artifact = ReasoningArtifact(
            title=title,
            content=content,
            author=author,
            phase=phase
        )
        version = self.version_control.commit_version(artifact)
        result["version_id"] = version.version_id
        
        return result
    
    def tool_validate_phase_gate(self,
                                title: str,
                                content: str,
                                phase: str,
                                min_score: float = 7.5,
                                min_breadth: int = 3) -> Dict[str, Any]:
        """MCP Tool: Validate if content passes phase gate requirements.
        
        Args:
            title: Title of the reasoning artifact
            content: The reasoning content to validate
            phase: VDW phase being validated
            min_score: Minimum score required to pass
            min_breadth: Minimum analytical breadth required
        
        Returns:
            Validation result with pass/fail status and detailed feedback
        """
        # Temporarily update thresholds
        original_score = self.integration.gates.min_score
        original_breadth = self.integration.gates.min_breadth
        
        self.integration.gates.min_score = min_score
        self.integration.gates.min_breadth = min_breadth
        
        try:
            result = self.integration.review_phase_output(
                title=title,
                content=content,
                phase=phase
            )
            
            validation_result = {
                "phase": phase,
                "can_advance": self.integration.should_advance_phase(result),
                "overall_score": result["result"]["overall_score"],
                "required_score": min_score,
                "analytical_breadth": len(set(i["category"] for i in result["result"]["insights"])),
                "required_breadth": min_breadth,
                "validation_errors": result["validation_errors"],
                "recommendations": result["result"]["recommendations"],
                "gate_decision": "PASS" if len(result["validation_errors"]) == 0 else "FAIL"
            }
            
            return validation_result
        
        finally:
            # Restore original thresholds
            self.integration.gates.min_score = original_score
            self.integration.gates.min_breadth = original_breadth
    
    def tool_start_collaborative_review(self,
                                       title: str,
                                       content: str,
                                       phase: str = "unknown",
                                       required_reviewers: int = 3) -> Dict[str, Any]:
        """MCP Tool: Start a collaborative review process.
        
        Args:
            title: Title of the reasoning artifact
            content: The reasoning content to review
            phase: VDW phase
            required_reviewers: Number of reviewers needed
        
        Returns:
            Collaborative review session ID and initial status
        """
        artifact = ReasoningArtifact(
            title=title,
            content=content,
            phase=phase
        )
        
        review_id = self.collaborative_system.initiate_collaborative_review(
            artifact=artifact,
            required_reviewers=required_reviewers
        )
        
        return {
            "review_id": review_id,
            "artifact_id": artifact.id,
            "status": "initiated",
            "required_reviewers": required_reviewers,
            "instructions": "Review session started. Individual reviews will be collected and consensus calculated."
        }
    
    def tool_get_collaborative_result(self, review_id: str) -> Dict[str, Any]:
        """MCP Tool: Get results from a collaborative review.
        
        Args:
            review_id: ID of the collaborative review session
        
        Returns:
            Collaborative review results with consensus and disagreement analysis
        """
        return self.collaborative_system.get_collaborative_result(review_id)
    
    def tool_analyze_reasoning_evolution(self, artifact_id: str) -> Dict[str, Any]:
        """MCP Tool: Analyze how reasoning has evolved over time.
        
        Args:
            artifact_id: ID of the reasoning artifact to analyze
        
        Returns:
            Evolution analysis with trends, gaps, and recovered insights
        """
        evolution = self.version_control.analyze_evolution(artifact_id)
        learning_curve = self.version_control.get_learning_curve(artifact_id)
        
        return {
            "artifact_id": artifact_id,
            "evolution_analysis": evolution,
            "learning_curve": learning_curve,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def tool_conduct_post_mortem(self, 
                               artifact_id: str,
                               failure_threshold: float = 6.0) -> Dict[str, Any]:
        """MCP Tool: Conduct post-mortem analysis of failed reasoning attempts.
        
        Args:
            artifact_id: ID of the reasoning artifact
            failure_threshold: Score threshold below which attempts are considered failures
        
        Returns:
            Post-mortem analysis with failure patterns and recovery strategies
        """
        return self.version_control.conduct_post_mortem(artifact_id, failure_threshold)
    
    def tool_recursive_system_analysis(self) -> Dict[str, Any]:
        """MCP Tool: Conduct recursive analysis of the meta-review system itself.
        
        Returns:
            Meta-meta analysis with system improvements and evolution tracking
        """
        review_history = self.framework.review_history
        
        if len(review_history) < 3:
            return {
                "status": "insufficient_data",
                "message": "Need at least 3 reviews for meaningful recursive analysis",
                "current_review_count": len(review_history)
            }
        
        analysis = self.recursive_system.conduct_recursive_analysis(review_history)
        evolution_report = self.recursive_system.get_system_evolution_report()
        
        return {
            "recursive_analysis": analysis,
            "system_evolution": evolution_report,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def tool_get_reviewer_calibration(self) -> Dict[str, Any]:
        """MCP Tool: Get calibration status of all reviewers.
        
        Returns:
            Calibration metrics and recommendations for reviewer improvement
        """
        calibration_system = self.collaborative_system.calibration_system
        
        reviewers_data = []
        for reviewer in calibration_system.reviewers.values():
            reviewers_data.append(reviewer.to_dict())
        
        miscalibrated = calibration_system.identify_miscalibrated_reviewers()
        
        return {
            "total_reviewers": len(calibration_system.reviewers),
            "reviewers": reviewers_data,
            "miscalibrated_reviewers": [r.reviewer_id for r in miscalibrated],
            "calibration_recommendations": [
                f"Reviewer {r.reviewer_id} needs recalibration (score: {r.calibration_score:.2f})"
                for r in miscalibrated
            ]
        }
    
    def tool_update_validation_gates(self,
                                   min_score: Optional[float] = None,
                                   min_breadth: Optional[int] = None,
                                   require_meta_insights: Optional[bool] = None) -> Dict[str, Any]:
        """MCP Tool: Update validation gate thresholds.
        
        Args:
            min_score: New minimum score threshold
            min_breadth: New minimum breadth threshold
            require_meta_insights: Whether to require meta-insights for deep reviews
        
        Returns:
            Updated gate configuration
        """
        gates = self.integration.gates
        
        if min_score is not None:
            gates.min_score = min_score
        if min_breadth is not None:
            gates.min_breadth = min_breadth
        if require_meta_insights is not None:
            gates.require_meta_insights = require_meta_insights
        
        return {
            "updated": True,
            "current_config": {
                "min_score": gates.min_score,
                "min_breadth": gates.min_breadth,
                "require_meta_insights": gates.require_meta_insights
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def tool_get_review_history(self, 
                              limit: int = 10,
                              phase: Optional[str] = None) -> Dict[str, Any]:
        """MCP Tool: Get history of meta-reviews conducted.
        
        Args:
            limit: Maximum number of reviews to return
            phase: Filter by VDW phase (optional)
        
        Returns:
            Historical review data with trends and statistics
        """
        history = self.framework.review_history[-limit:]
        
        if phase:
            # Filter by phase if specified - would need phase info in results
            pass
        
        review_data = []
        for review in history:
            review_data.append({
                "review_id": review.review_id,
                "artifact_id": review.artifact_id,
                "overall_score": review.overall_score,
                "depth_level": review.depth_level.value,
                "perspectives_used": [p.value for p in review.perspectives_used],
                "insight_count": len(review.insights),
                "recommendation_count": len(review.recommendations),
                "created_at": review.created_at.isoformat()
            })
        
        # Calculate trends
        scores = [r["overall_score"] for r in review_data]
        trends = {
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "score_trend": "improving" if len(scores) >= 2 and scores[-1] > scores[0] else "stable",
            "total_reviews": len(self.framework.review_history),
            "recent_reviews": len(review_data)
        }
        
        return {
            "reviews": review_data,
            "trends": trends,
            "retrieved_at": datetime.now().isoformat()
        }
    
    # MCP Server Interface Methods
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools."""
        return [
            {
                "name": "conduct_meta_review",
                "description": "Conduct comprehensive meta-review of reasoning content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the reasoning artifact"},
                        "content": {"type": "string", "description": "The reasoning content to review"},
                        "phase": {"type": "string", "description": "VDW phase (phase1, phase2, etc.)", "default": "unknown"},
                        "author": {"type": "string", "description": "Author of the content", "default": "user"},
                        "depth": {"type": "string", "enum": ["surface", "standard", "deep", "meta_meta"], "default": "standard"}
                    },
                    "required": ["title", "content"]
                }
            },
            {
                "name": "validate_phase_gate",
                "description": "Validate if content passes VDW phase gate requirements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the reasoning artifact"},
                        "content": {"type": "string", "description": "The reasoning content to validate"},
                        "phase": {"type": "string", "description": "VDW phase being validated"},
                        "min_score": {"type": "number", "description": "Minimum score required", "default": 7.5},
                        "min_breadth": {"type": "integer", "description": "Minimum analytical breadth", "default": 3}
                    },
                    "required": ["title", "content", "phase"]
                }
            },
            {
                "name": "start_collaborative_review",
                "description": "Start a collaborative review process with multiple reviewers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the reasoning artifact"},
                        "content": {"type": "string", "description": "The reasoning content to review"},
                        "phase": {"type": "string", "description": "VDW phase", "default": "unknown"},
                        "required_reviewers": {"type": "integer", "description": "Number of reviewers needed", "default": 3}
                    },
                    "required": ["title", "content"]
                }
            },
            {
                "name": "get_collaborative_result",
                "description": "Get results from a collaborative review session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "review_id": {"type": "string", "description": "ID of the collaborative review session"}
                    },
                    "required": ["review_id"]
                }
            },
            {
                "name": "analyze_reasoning_evolution",
                "description": "Analyze how reasoning has evolved over time",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string", "description": "ID of the reasoning artifact to analyze"}
                    },
                    "required": ["artifact_id"]
                }
            },
            {
                "name": "conduct_post_mortem",
                "description": "Conduct post-mortem analysis of failed reasoning attempts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string", "description": "ID of the reasoning artifact"},
                        "failure_threshold": {"type": "number", "description": "Score threshold for failures", "default": 6.0}
                    },
                    "required": ["artifact_id"]
                }
            },
            {
                "name": "recursive_system_analysis",
                "description": "Conduct recursive analysis of the meta-review system itself",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_reviewer_calibration",
                "description": "Get calibration status of all reviewers",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_validation_gates",
                "description": "Update validation gate thresholds",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "min_score": {"type": "number", "description": "New minimum score threshold"},
                        "min_breadth": {"type": "integer", "description": "New minimum breadth threshold"},
                        "require_meta_insights": {"type": "boolean", "description": "Require meta-insights for deep reviews"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_review_history",
                "description": "Get history of meta-reviews conducted",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum reviews to return", "default": 10},
                        "phase": {"type": "string", "description": "Filter by VDW phase"}
                    },
                    "required": []
                }
            }
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        tool_methods = {
            "conduct_meta_review": self.tool_conduct_meta_review,
            "validate_phase_gate": self.tool_validate_phase_gate,
            "start_collaborative_review": self.tool_start_collaborative_review,
            "get_collaborative_result": self.tool_get_collaborative_result,
            "analyze_reasoning_evolution": self.tool_analyze_reasoning_evolution,
            "conduct_post_mortem": self.tool_conduct_post_mortem,
            "recursive_system_analysis": self.tool_recursive_system_analysis,
            "get_reviewer_calibration": self.tool_get_reviewer_calibration,
            "update_validation_gates": self.tool_update_validation_gates,
            "get_review_history": self.tool_get_review_history
        }
        
        if name not in tool_methods:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            return tool_methods[name](**arguments)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
