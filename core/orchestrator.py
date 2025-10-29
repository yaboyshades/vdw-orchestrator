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

class VDWOrchestrator:
    def __init__(self, event_bus: EventBus, memory_store: MemoryStore, mangle_client: MangleClient):
        self.event_bus = event_bus
        self.memory_store = memory_store
        self.mangle = mangle_client
        self.projects: Dict[str, ProjectContext] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def submit_new_project(self, vibe: str) -> str:
        project_id = str(uuid.uuid4())
        ctx = ProjectContext(project_id=project_id, initial_vibe=vibe)
        self.projects[project_id] = ctx
        await self.memory_store.store_atom(f"project:{project_id}", ctx.model_dump())
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        await fsm.transition_to(VDWPhase.PHASE_1_MOOD, reason="project_created")
        await self._run_phase_1(project_id)
        return project_id

    async def _run_phase_1(self, project_id: str):
        agent = Phase1MoodAgent()
        ctx = self.projects[project_id]
        output = await agent.execute(ctx)
        ctx.set_phase_output(VDWPhase.PHASE_1_MOOD, output)
        await self.memory_store.store_atom(f"project:{project_id}:p1", output)
        # Move to validation state
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        await fsm.transition_to(VDWPhase.PHASE_1_VALIDATION, reason="phase_1_completed")

    async def approve_phase_1(self, project_id: str, feedback: str | None = None):
        ctx = self.projects[project_id]
        if feedback:
            ctx.user_feedback[VDWPhase.PHASE_1_MOOD] = feedback
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        await fsm.transition_to(VDWPhase.PHASE_2_ARCHITECTURE, reason="phase_1_approved")
        await self._run_phase_2(project_id)

    async def _run_phase_2(self, project_id: str):
        agent = Phase2ArchitectureAgent(self.mangle)
        ctx = self.projects[project_id]
        output = await agent.execute(ctx)
        ctx.set_phase_output(VDWPhase.PHASE_2_ARCHITECTURE, output)
        await self.memory_store.store_atom(f"project:{project_id}:p2", output)
        fsm = VDWStateMachine(ctx, mangle_client=self.mangle)
        await fsm.transition_to(VDWPhase.PHASE_2_VALIDATION, reason="phase_2_completed")
