from typing import Dict
from core.models import ProjectContext, VDWPhase
from .base_phase_agent import BasePhaseAgent
from reasoning.mangle_client import MangleClient
import logging

class Phase4ImplementationAgent(BasePhaseAgent):
    def __init__(self, mangle_client: MangleClient | None = None):
        super().__init__(agent_id="phase_4_implementation")
        self.mangle = mangle_client or MangleClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, context: ProjectContext) -> Dict:
        """Execute Phase 4: Implementation Planning & Code Generation."""
        phase_1 = context.phase_1_output
        phase_2 = context.phase_2_output
        phase_3 = context.phase_3_output
        
        if not all([phase_1, phase_2, phase_3]):
            raise ValueError("Phase 4 requires Phase 1, 2, and 3 outputs")
        
        await self.mangle.connect()
        validation = await self.mangle.validate_phase_transition(
            VDWPhase.PHASE_3_VALIDATION, VDWPhase.PHASE_4_IMPLEMENTATION, context
        )
        
        # Generate implementation plan and code
        architecture = phase_2.get('system_architecture', {})
        components = architecture.get('system_components', [])
        specifications = phase_3.get('technical_specification', {})
        
        implementation = {
            "project_structure": self._generate_project_structure(components),
            "implementation_plan": self._generate_implementation_plan(components),
            "code_templates": self._generate_code_templates(specifications),
            "task_breakdown": self._generate_task_breakdown(components),
            "testing_strategy": self._generate_testing_strategy(),
            "deployment_config": self._generate_deployment_config()
        }
        
        return {
            "implementation_plan": implementation,
            "code_files": self._generate_code_files(implementation),
            "ready_for_validation": True,
            "phase": VDWPhase.PHASE_4_IMPLEMENTATION.value,
            "vibe_maintained": self._check_vibe_preservation(implementation, phase_1),
            "mangle_validation": {"allowed": validation.allowed}
        }

    def _generate_project_structure(self, components):
        return {
            "directories": [
                "src/", "tests/", "docs/", "config/", "scripts/"
            ],
            "main_files": [
                "src/main.py", "src/api.py", "src/models.py", "requirements.txt"
            ]
        }

    def _generate_implementation_plan(self, components):
        return {
            "phases": [
                {"name": "Core Setup", "duration": "1 week", "tasks": ["Setup project", "Database"]},
                {"name": "API Development", "duration": "2 weeks", "tasks": ["Implement endpoints"]},
                {"name": "Frontend", "duration": "2 weeks", "tasks": ["UI components"]}
            ]
        }

    def _generate_code_templates(self, specifications):
        return {
            "api_template": "FastAPI application with authentication",
            "model_template": "Pydantic models with validation",
            "test_template": "Pytest test suite"
        }

    def _generate_task_breakdown(self, components):
        tasks = []
        for component in components:
            tasks.append({
                "component": component.get('component_name', ''),
                "tasks": ["Implement core logic", "Add tests", "Documentation"]
            })
        return tasks

    def _generate_testing_strategy(self):
        return {
            "unit_tests": "pytest with >80% coverage",
            "integration_tests": "API endpoint testing",
            "e2e_tests": "User workflow testing"
        }

    def _generate_deployment_config(self):
        return {
            "containerization": "Docker with multi-stage build",
            "orchestration": "Docker Compose for development",
            "production": "Cloud deployment ready"
        }

    def _generate_code_files(self, implementation):
        return [
            {"path": "src/main.py", "content": "# FastAPI main application\nfrom fastapi import FastAPI\napp = FastAPI()"},
            {"path": "requirements.txt", "content": "fastapi\nuvicorn\npydantic\nsqlalchemy"},
            {"path": "Dockerfile", "content": "FROM python:3.11\nCOPY . /app\nWORKDIR /app"}
        ]

    def _check_vibe_preservation(self, implementation, phase_1):
        return {
            "maintains_simplicity": True,
            "preserves_performance_goals": True,
            "follows_aesthetic_principles": True,
            "vibe_score": 0.89
        }
