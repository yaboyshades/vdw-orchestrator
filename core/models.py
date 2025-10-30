"""Pydantic models for VDW Orchestrator"""
from enum import Enum
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

class VDWPhase(str, Enum):
    IDLE = "IDLE"
    PHASE_1_MOOD = "PHASE_1_MOOD"
    PHASE_1_VALIDATION = "PHASE_1_VALIDATION"
    PHASE_2_ARCHITECTURE = "PHASE_2_ARCHITECTURE"
    PHASE_2_VALIDATION = "PHASE_2_VALIDATION"
    PHASE_3_SPECIFICATION = "PHASE_3_SPECIFICATION"
    PHASE_3_VALIDATION = "PHASE_3_VALIDATION"
    PHASE_4_IMPLEMENTATION = "PHASE_4_IMPLEMENTATION"
    PHASE_4_VALIDATION = "PHASE_4_VALIDATION"
    PHASE_5_VALIDATION_TESTING = "PHASE_5_VALIDATION_TESTING"
    PHASE_5_VALIDATION = "PHASE_5_VALIDATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ProjectContext(BaseModel):
    project_id: str = Field(..., description="Unique ID for the project")
    current_phase: VDWPhase = Field(default=VDWPhase.IDLE)
    initial_vibe: str
    distilled_requirements: Optional[Dict[str, Any]] = None  # From conversation distillation
    phase_1_output: Optional[Dict[str, Any]] = None
    phase_2_output: Optional[Dict[str, Any]] = None
    phase_3_output: Optional[Dict[str, Any]] = None
    phase_4_output: Optional[Dict[str, Any]] = None
    phase_5_output: Optional[Dict[str, Any]] = None
    user_feedback: Dict[VDWPhase, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tools_created: List[str] = Field(default_factory=list)  # Tools created for this project
    
    def set_phase_output(self, phase: VDWPhase, output: Dict[str, Any]):
        """Set the output for a specific phase"""
        if phase == VDWPhase.PHASE_1_MOOD:
            self.phase_1_output = output
        elif phase == VDWPhase.PHASE_2_ARCHITECTURE:
            self.phase_2_output = output
        elif phase == VDWPhase.PHASE_3_SPECIFICATION:
            self.phase_3_output = output
        elif phase == VDWPhase.PHASE_4_IMPLEMENTATION:
            self.phase_4_output = output
        elif phase == VDWPhase.PHASE_5_VALIDATION_TESTING:
            self.phase_5_output = output
        self.updated_at = datetime.now()

class ToolMetadata(BaseModel):
    tool_id: str
    name: str
    description: str
    capabilities: List[str]
    created_by: str  # project_id that created this tool
    created_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = 0
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    deprecated: bool = False

class ReasoningQuery(BaseModel):
    query_type: str  # "dependency_check", "gap_analysis", "optimization"
    context: Dict[str, Any]
    project_id: Optional[str] = None
    
class ReasoningResponse(BaseModel):
    query_id: str
    result: Dict[str, Any]
    confidence: float = 1.0
    reasoning_trace: Optional[List[str]] = None

class ToolCapability(BaseModel):
    """Capability provided by a tool"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
