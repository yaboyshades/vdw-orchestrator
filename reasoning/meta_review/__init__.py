"""Meta-Review and Mental Game Analysis System for VDW Orchestrator.

This module implements a comprehensive meta-cognitive analysis framework for evaluating
and improving reasoning processes throughout the VDW (Vibe-Driven Waterfall) lifecycle.

Key Components:
- Core meta-review framework
- Mental game analysis tools (Skeptic, Novice, Cross-Domain perspectives)
- Integration with VDW phase validation gates
- MCP-compatible server components
- Quantitative validation and metrics
"""

from .core import MetaReviewFramework, MentalGameAnalyzer
from .perspectives import SkepticalAnalyzer, NoviceAnalyzer, CrossDomainAnalyzer
from .validators import QualityMetrics, ValidationGates
from .integration import VDWIntegration

__version__ = "1.0.0"
__all__ = [
    "MetaReviewFramework",
    "MentalGameAnalyzer", 
    "SkepticalAnalyzer",
    "NoviceAnalyzer",
    "CrossDomainAnalyzer",
    "QualityMetrics",
    "ValidationGates",
    "VDWIntegration"
]
