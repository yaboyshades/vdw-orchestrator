"""VDW Orchestrator Core Package

This package contains the core components of the Vibe-Driven Waterfall Orchestrator:
- Models: Pydantic data models for project context and tool metadata
- Orchestrator: Main orchestration logic
- State Machine: FSM for phase transitions
- Event Bus: Redis-backed event communication
- Memory Store: Atoms and Bonds memory system
- Tool Registry: MCP Box for dynamic tool management
"""

from .models import (
    VDWPhase,
    ProjectContext,
    ToolMetadata,
    ReasoningQuery,
)

# Import core components when they're implemented
# from .orchestrator import VDWOrchestrator
# from .state_machine import VDWStateMachine

__version__ = "0.1.0"
__all__ = [
    "VDWPhase",
    "ProjectContext", 
    "ToolMetadata",
    "ReasoningQuery",
    # "VDWOrchestrator",
    # "VDWStateMachine",
]