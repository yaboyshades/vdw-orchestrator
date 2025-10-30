import asyncio
import logging
import uuid
from typing import Dict

from core.models import ProjectContext, VDWPhase
from core.state_machine import VDWStateMachine
from core.event_bus import EventBus
from core.memory_store import MemoryStore
from reasoning.mangle_client import MangleClient
from agents.phase_1_mood import Phase1MoodAgent
from agents.phase_2_architecture import Phase2ArchitectureAgent
from agents.phase_3_specification import Phase3SpecificationAgent
from agents.phase_4_implementation import Phase4ImplementationAgent
from agents.phase_5_validation import Phase5ValidationAgent

class VDWOrchestrator:
    """VDW Orchestrator managing the complete 5-phase development lifecycle."""
    
    def __init__(self, event_bus: EventBus, memory_store: MemoryStore, mangle_client: MangleClient):
        self.event_bus = event_bus
        self.memory_store = memory_store
        self.mangle = mangle_client
        self.projects: Dict[str, ProjectContext] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize phase agents
        self._init_phase_agents()

    def _init_phase_agents(self):
        """Initialize all phase agents."""
        self.agents = {
            VDWPhase.PHASE_1_MOOD: Phase1MoodAgent(),
            VDWPhase.PHASE_2_ARCHITECTURE: Phase2ArchitectureAgent(self.mangle),
            VDWPhase.PHASE_3_SPECIFICATION: Phase3SpecificationAgent(self.mangle),
            VDWPhase.PHASE_4_IMPLEMENTATION: Phase4ImplementationAgent(self.mangle),
            VDWPhase.PHASE_5_VALIDATION_TESTING: Phase5ValidationAgent(self.mangle)
        }

    async def submit_new_project(self, vibe: str) -> str:
        """Submit a new project with initial vibe and start Phase 1."""
        project_id = str(uuid.uuid4())
        ctx = ProjectContext(project_id=project_id, initial_vibe=vibe)
        self.projects[project_id] = ctx
        
        # Store initial project context
        await self.memory_store.store_atom(f"project:{project_id}", ctx.model_dump())
        
        # Transition to Phase 1 and execute
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        await fsm.transition_to(VDWPhase.PHASE_1_MOOD, reason="project_created")
        await self._execute_phase(project_id, VDWPhase.PHASE_1_MOOD)
        
        return project_id

    async def _execute_phase(self, project_id: str, phase: VDWPhase):
        """Execute a specific phase using the appropriate agent."""
        ctx = self.projects[project_id]
        agent = self.agents.get(phase)
        
        if not agent:
            raise ValueError(f"No agent available for phase {phase}")
        
        self.logger.info(f"Executing {phase.value} for project {project_id}")
        
        try:
            # Execute the phase
            output = await agent.execute(ctx)
            
            # Store phase output in context
            ctx.set_phase_output(phase, output)
            
            # Store output in memory store
            phase_key = phase.value.lower().replace('_', '')
            await self.memory_store.store_atom(f"project:{project_id}:{phase_key}", output)
            
            # Transition to validation state
            validation_phase = self._get_validation_phase(phase)
            if validation_phase:
                fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
                await fsm.transition_to(validation_phase, reason=f"{phase.value}_completed")
                
                self.logger.info(f"Phase {phase.value} completed, awaiting validation for project {project_id}")
            
        except Exception as e:
            self.logger.error(f"Phase {phase.value} execution failed for project {project_id}: {e}")
            # Transition to failed state
            fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
            await fsm.transition_to(VDWPhase.FAILED, reason=f"{phase.value}_failed: {e}")
            raise

    def _get_validation_phase(self, phase: VDWPhase) -> VDWPhase | None:
        """Get the corresponding validation phase for a given execution phase."""
        validation_mapping = {
            VDWPhase.PHASE_1_MOOD: VDWPhase.PHASE_1_VALIDATION,
            VDWPhase.PHASE_2_ARCHITECTURE: VDWPhase.PHASE_2_VALIDATION,
            VDWPhase.PHASE_3_SPECIFICATION: VDWPhase.PHASE_3_VALIDATION,
            VDWPhase.PHASE_4_IMPLEMENTATION: VDWPhase.PHASE_4_VALIDATION,
            VDWPhase.PHASE_5_VALIDATION_TESTING: VDWPhase.PHASE_5_VALIDATION
        }
        return validation_mapping.get(phase)

    def _get_next_execution_phase(self, validation_phase: VDWPhase) -> VDWPhase | None:
        """Get the next execution phase after validation approval."""
        next_phase_mapping = {
            VDWPhase.PHASE_1_VALIDATION: VDWPhase.PHASE_2_ARCHITECTURE,
            VDWPhase.PHASE_2_VALIDATION: VDWPhase.PHASE_3_SPECIFICATION,
            VDWPhase.PHASE_3_VALIDATION: VDWPhase.PHASE_4_IMPLEMENTATION,
            VDWPhase.PHASE_4_VALIDATION: VDWPhase.PHASE_5_VALIDATION_TESTING,
            VDWPhase.PHASE_5_VALIDATION: VDWPhase.COMPLETED
        }
        return next_phase_mapping.get(validation_phase)

    async def approve_phase(self, project_id: str, current_validation_phase: VDWPhase, feedback: str | None = None, approved: bool = True):
        """Approve or reject a phase validation and proceed accordingly."""
        ctx = self.projects[project_id]
        
        if feedback:
            # Map validation phase to execution phase for feedback storage
            execution_phase = self._validation_to_execution_phase(current_validation_phase)
            if execution_phase:
                ctx.user_feedback[execution_phase] = feedback
        
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        
        if approved:
            # Move to next phase
            next_phase = self._get_next_execution_phase(current_validation_phase)
            if next_phase == VDWPhase.COMPLETED:
                # Project is complete
                await fsm.transition_to(VDWPhase.COMPLETED, reason="all_phases_approved")
                self.logger.info(f"Project {project_id} completed successfully!")
            elif next_phase:
                # Execute next phase
                await fsm.transition_to(next_phase, reason=f"{current_validation_phase.value}_approved")
                await self._execute_phase(project_id, next_phase)
        else:
            # Rejected - go back to execution phase for revision
            execution_phase = self._validation_to_execution_phase(current_validation_phase)
            if execution_phase:
                await fsm.transition_to(execution_phase, reason=f"{current_validation_phase.value}_rejected")
                await self._execute_phase(project_id, execution_phase)

    def _validation_to_execution_phase(self, validation_phase: VDWPhase) -> VDWPhase | None:
        """Map validation phase back to execution phase."""
        execution_mapping = {
            VDWPhase.PHASE_1_VALIDATION: VDWPhase.PHASE_1_MOOD,
            VDWPhase.PHASE_2_VALIDATION: VDWPhase.PHASE_2_ARCHITECTURE,
            VDWPhase.PHASE_3_VALIDATION: VDWPhase.PHASE_3_SPECIFICATION,
            VDWPhase.PHASE_4_VALIDATION: VDWPhase.PHASE_4_IMPLEMENTATION,
            VDWPhase.PHASE_5_VALIDATION: VDWPhase.PHASE_5_VALIDATION_TESTING
        }
        return execution_mapping.get(validation_phase)

    # Legacy method support for backward compatibility
    async def approve_phase_1(self, project_id: str, feedback: str | None = None):
        """Legacy method - approve Phase 1."""
        await self.approve_phase(project_id, VDWPhase.PHASE_1_VALIDATION, feedback, True)

    async def approve_phase_2(self, project_id: str, feedback: str | None = None):
        """Approve Phase 2 and proceed to Phase 3."""
        await self.approve_phase(project_id, VDWPhase.PHASE_2_VALIDATION, feedback, True)

    async def approve_phase_3(self, project_id: str, feedback: str | None = None):
        """Approve Phase 3 and proceed to Phase 4."""
        await self.approve_phase(project_id, VDWPhase.PHASE_3_VALIDATION, feedback, True)

    async def approve_phase_4(self, project_id: str, feedback: str | None = None):
        """Approve Phase 4 and proceed to Phase 5."""
        await self.approve_phase(project_id, VDWPhase.PHASE_4_VALIDATION, feedback, True)

    async def approve_phase_5(self, project_id: str, feedback: str | None = None):
        """Approve Phase 5 and complete the project."""
        await self.approve_phase(project_id, VDWPhase.PHASE_5_VALIDATION, feedback, True)

    def get_project_context(self, project_id: str) -> ProjectContext | None:
        """Get project context by ID."""
        return self.projects.get(project_id)

    def get_project_phase(self, project_id: str) -> VDWPhase | None:
        """Get current phase for a project."""
        ctx = self.projects.get(project_id)
        return ctx.current_phase if ctx else None

    def get_project_artifacts(self, project_id: str) -> Dict:
        """Get all artifacts for a project."""
        ctx = self.projects.get(project_id)
        if not ctx:
            return {}
        
        return {
            "project_id": project_id,
            "current_phase": ctx.current_phase.value,
            "initial_vibe": ctx.initial_vibe,
            "phase_1_output": ctx.phase_1_output,
            "phase_2_output": ctx.phase_2_output,
            "phase_3_output": ctx.phase_3_output,
            "phase_4_output": ctx.phase_4_output,
            "phase_5_output": ctx.phase_5_output,
            "user_feedback": {k.value: v for k, v in ctx.user_feedback.items()}
        }

    async def advance_project(self, project_id: str) -> Dict:
        """Advance project to next phase (for API endpoint)."""
        ctx = self.projects.get(project_id)
        if not ctx:
            raise ValueError(f"Project {project_id} not found")
        
        current_phase = ctx.current_phase
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        next_phases = fsm.get_next_phases()
        
        if not next_phases:
            return {"message": "Project is in final state", "current_phase": current_phase.value}
        
        # If in validation phase, we need human approval
        if "VALIDATION" in current_phase.value:
            return {
                "message": "Project awaiting human validation",
                "current_phase": current_phase.value,
                "awaiting_validation": True,
                "next_phases": [p.value for p in next_phases]
            }
        
        # If in execution phase, check if we can auto-advance to validation
        validation_phase = self._get_validation_phase(current_phase)
        if validation_phase and validation_phase in next_phases:
            # Already transitioned to validation in _execute_phase
            return {
                "message": f"Phase {current_phase.value} completed, moved to validation",
                "current_phase": ctx.current_phase.value,
                "awaiting_validation": True
            }
        
        return {"message": "No automatic advancement possible", "current_phase": current_phase.value}
