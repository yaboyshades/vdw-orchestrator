from typing import Dict
from core.models import ProjectContext, VDWPhase
from .base_phase_agent import BasePhaseAgent
from reasoning.conversation_distiller import ConversationDistiller
import logging

class Phase1MoodAgent(BasePhaseAgent):
    def __init__(self):
        super().__init__(agent_id="phase_1_mood")
        self.distiller = ConversationDistiller()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, context: ProjectContext) -> Dict:
        # Distill vibe into structured requirements
        result = await self.distiller.distill(context.initial_vibe)
        yaml_output = self.distiller.to_yaml_output(result)

        output = {
            "mood_json": {
                "distillation_id": result.distillation_id,
                "confidence": result.confidence_score,
                "segments": [s.__dict__ for s in result.segments],
            },
            "requirements_yaml": yaml_output,
            "dependency_graph": result.dependency_graph,
            "validation_checklist": result.validation_checklist,
        }
        return output
