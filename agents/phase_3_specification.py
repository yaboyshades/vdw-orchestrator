from typing import Dict
from core.models import ProjectContext, VDWPhase
from .base_phase_agent import BasePhaseAgent
from reasoning.mangle_client import MangleClient
import logging

class Phase3SpecificationAgent(BasePhaseAgent):
    def __init__(self, mangle_client: MangleClient | None = None):
        super().__init__(agent_id="phase_3_specification")
        self.mangle = mangle_client or MangleClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, context: ProjectContext) -> Dict:
        """Execute Phase 3: Technical Specification."""
        phase_1 = context.phase_1_output
        phase_2 = context.phase_2_output
        
        if not phase_1 or not phase_2:
            raise ValueError("Phase 3 requires Phase 1 and 2 outputs")
        
        await self.mangle.connect()
        validation = await self.mangle.validate_phase_transition(
            VDWPhase.PHASE_2_VALIDATION, VDWPhase.PHASE_3_SPECIFICATION, context
        )
        
        # Generate technical specifications
        spec = {
            "constitution": {"vision": phase_1.get('vibe_analysis', {}).get('core_aesthetic', '')},
            "data_models": {"User": {"id": "uuid", "email": "string"}},
            "api_contracts": {"endpoints": [{"path": "/health", "method": "GET"}]},
            "algorithms": {"core_algorithm": {"complexity": "O(n)"}},
            "security": {"auth": "JWT"},
            "performance": {"latency": "<200ms"}
        }
        
        return {
            "technical_specification": spec,
            "spec_files": [{"path": ".specify/constitution.md", "content": "# Constitution"}],
            "ready_for_implementation": True,
            "phase": VDWPhase.PHASE_3_SPECIFICATION.value,
            "mangle_validation": {"allowed": validation.allowed}
        }
