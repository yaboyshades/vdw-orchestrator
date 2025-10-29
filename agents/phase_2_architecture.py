from typing import Dict
from core.models import ProjectContext, VDWPhase
from .base_phase_agent import BasePhaseAgent
from reasoning.mangle_client import MangleClient
import logging

class Phase2ArchitectureAgent(BasePhaseAgent):
    def __init__(self, mangle_client: MangleClient | None = None):
        super().__init__(agent_id="phase_2_architecture")
        self.mangle = mangle_client or MangleClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, context: ProjectContext) -> Dict:
        # Placeholder architecture output
        architecture = {
            "components": ["api", "db", "worker"],
            "decisions": ["event-driven", "redis-pubsub"],
        }
        # Validate dependencies via Mangle
        await self.mangle.connect()
        validation = await self.mangle.validate_phase_transition(
            VDWPhase.PHASE_1_VALIDATION, VDWPhase.PHASE_2_ARCHITECTURE, context
        )
        return {
            "architecture_json": architecture,
            "mangle_validation": {
                "allowed": validation.allowed,
                "reason": validation.reason,
                "confidence": validation.confidence,
            },
        }
