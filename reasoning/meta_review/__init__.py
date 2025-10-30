"""Meta-Review and Mental Game Analysis System for VDW Orchestrator.

This module implements a comprehensive meta-cognitive analysis framework for evaluating
and improving reasoning processes throughout the VDW (Vibe-Driven Waterfall) lifecycle.

Key Components:
- Core meta-review framework
- Mental game analysis tools (Skeptic, Novice, Cross-Domain perspectives)
- Integration with VDW phase validation gates
- MCP-compatible server components
- Temporal analysis and version control
- Collaborative review systems
- Recursive self-improvement
- Quantitative validation and metrics

Phases Implemented:
✅ Phase 1: Core Meta-Review Framework
✅ Phase 7: Temporal and Longitudinal Analysis  
✅ Phase 8: Collaborative and Social Meta-Review
✅ Phase 9: Meta-Meta Analysis and Recursive Improvement
✅ Phase 10: Full VDW Integration with MCP Server
"""

from .core import MetaReviewFramework, MentalGameAnalyzer, ReasoningArtifact, ReviewDepth, ReviewPerspective
from .perspectives import SkepticalAnalyzer, NoviceAnalyzer, CrossDomainAnalyzer
from .validators import QualityMetrics, ValidationGates
from .integration import VDWIntegration
from .temporal import ReasoningVersionControl, ReasoningArchaeologist
from .collaborative import CollaborativeMetaReview, ConsensusEngine, ReviewerCalibrationSystem, Reviewer, ReviewerExpertise
from .recursive import RecursiveAnalyzer, SelfImprovingReviewSystem, MetaAnalysisDepth
from .mcp_server import MetaReviewMCPServer

__version__ = "2.0.0"  # Updated for comprehensive implementation
__all__ = [
    # Core Framework
    "MetaReviewFramework",
    "MentalGameAnalyzer", 
    "ReasoningArtifact",
    "ReviewDepth",
    "ReviewPerspective",
    
    # Perspective Analyzers
    "SkepticalAnalyzer",
    "NoviceAnalyzer",
    "CrossDomainAnalyzer",
    
    # Validation & Metrics
    "QualityMetrics",
    "ValidationGates",
    "VDWIntegration",
    
    # Temporal Analysis
    "ReasoningVersionControl",
    "ReasoningArchaeologist",
    
    # Collaborative Systems
    "CollaborativeMetaReview",
    "ConsensusEngine",
    "ReviewerCalibrationSystem",
    "Reviewer",
    "ReviewerExpertise",
    
    # Recursive Improvement
    "RecursiveAnalyzer",
    "SelfImprovingReviewSystem",
    "MetaAnalysisDepth",
    
    # MCP Server
    "MetaReviewMCPServer"
]
