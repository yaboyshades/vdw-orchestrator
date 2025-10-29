from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import BaseModel
from core.models import ProjectContext
import logging

class BasePhaseAgent(ABC):
    """Base class for all VDW phase agents.
    Provides common utilities for prompt loading, context injection, and logging.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, context: ProjectContext) -> Dict:
        """Execute the agent for the given project context and return outputs."""
        raise NotImplementedError

    async def _load_prompt(self, prompt_path: str) -> str:
        with open(prompt_path, "r") as f:
            return f.read()

    def _inject(self, template: str, values: Dict[str, str]) -> str:
        try:
            return template.format(**values)
        except Exception:
            return template
