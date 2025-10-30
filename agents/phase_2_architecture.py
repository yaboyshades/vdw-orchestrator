"""Phase 2: Architecture & System Design Agent

Transforms Phase 1 mood and requirements into comprehensive system architecture.
Follows the guide in docs/guides/phase2-architecture-design.md
"""

from typing import Dict, Any, List
from core.models import ProjectContext, VDWPhase
from .base_phase_agent import BasePhaseAgent
from reasoning.mangle_client import MangleClient
import logging
import json

logger = logging.getLogger(__name__)


class Phase2ArchitectureAgent(BasePhaseAgent):
    """Agent responsible for Phase 2: Architecture & System Design."""

    def __init__(self, mangle_client: MangleClient | None = None):
        super().__init__(agent_id="phase_2_architecture")
        self.mangle = mangle_client or MangleClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, context: ProjectContext) -> Dict[str, Any]:
        """Execute Phase 2: Architecture & System Design.
        
        Uses Phase 1 output to generate comprehensive system architecture
        following docs/guides/phase2-architecture-design.md template.
        """
        self.logger.info(f"Starting Phase 2 architecture for project {context.project_id}")
        
        try:
            # Get Phase 1 output from context
            phase_1_output = context.phase_1_output
            if not phase_1_output:
                raise ValueError("Phase 2 requires Phase 1 output")
            
            # Validate phase transition via Mangle
            await self.mangle.connect()
            validation = await self.mangle.validate_phase_transition(
                VDWPhase.PHASE_1_VALIDATION, VDWPhase.PHASE_2_ARCHITECTURE, context
            )
            
            if not validation.allowed:
                raise ValueError(f"Phase transition not allowed: {validation.reason}")
            
            # Generate system architecture
            architecture = await self._generate_system_architecture(phase_1_output, context)
            
            # Generate architecture diagrams
            diagrams = self._generate_architecture_diagrams(architecture)
            
            # Create validation checklist
            validation_checklist = self._create_validation_checklist()
            
            # Check vibe alignment
            vibe_alignment = self._check_vibe_alignment(architecture, phase_1_output)
            
            result = {
                "system_architecture": architecture,
                "architecture_diagrams": diagrams,
                "validation_checklist": validation_checklist,
                "ready_for_specification": self._assess_specification_readiness(architecture),
                "phase": VDWPhase.PHASE_2_ARCHITECTURE.value,
                "agent_id": self.agent_id,
                "vibe_alignment": vibe_alignment,
                "mangle_validation": {
                    "allowed": validation.allowed,
                    "reason": validation.reason,
                    "confidence": validation.confidence
                }
            }
            
            self.logger.info(f"Phase 2 architecture completed for project {context.project_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Phase 2 architecture failed: {e}")
            raise

    async def _generate_system_architecture(self, phase_1_output: Dict, context: ProjectContext) -> Dict[str, Any]:
        """Generate comprehensive system architecture from Phase 1 requirements."""
        
        functional_requirements = phase_1_output.get('functional_requirements', {})
        constraints = phase_1_output.get('constraints_and_antigoals', {})
        success_metrics = phase_1_output.get('success_metrics', {})
        technical_context = phase_1_output.get('technical_context', {})
        
        # Assess complexity level
        complexity_level = self._assess_complexity_level(functional_requirements)
        
        # Generate architecture components
        architecture = {
            "architecture_metadata": {
                "architecture_name": f"{context.project_id.replace('-', ' ').title()} System",
                "complexity_level": complexity_level,
                "estimated_dev_time": self._estimate_development_time(complexity_level),
                "confidence_score": 0.85,
                "analysis_timestamp": context.created_at.isoformat() if hasattr(context, 'created_at') else None
            },
            "system_components": self._generate_system_components(functional_requirements, technical_context, complexity_level),
            "data_flow": self._generate_data_flow(functional_requirements),
            "system_interfaces": self._generate_system_interfaces(technical_context),
            "deployment_architecture": self._generate_deployment_architecture(complexity_level, constraints),
            "risk_analysis": self._generate_risk_analysis(complexity_level),
            "implementation_phases": self._generate_implementation_phases(complexity_level),
            "validation_checklist": self._create_validation_checklist(),
            "next_phase_inputs": {
                "technical_specifications_needed": [
                    "Database schema design",
                    "API endpoint specifications",
                    "Component interface contracts"
                ],
                "ready_for_specification": True,
                "blocking_decisions": []
            }
        }
        
        return architecture

    def _assess_complexity_level(self, functional_requirements: Dict) -> str:
        """Assess system complexity based on requirements."""
        primary_goals = functional_requirements.get('primary_goals', [])
        user_stories = functional_requirements.get('user_stories', [])
        
        complexity_score = len(primary_goals) + len(user_stories)
        
        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 8:
            return "moderate"
        elif complexity_score <= 15:
            return "complex"
        else:
            return "enterprise"

    def _estimate_development_time(self, complexity_level: str) -> str:
        """Estimate development time based on complexity."""
        time_estimates = {
            "simple": "2-4 weeks",
            "moderate": "6-10 weeks",
            "complex": "12-20 weeks",
            "enterprise": "6+ months"
        }
        return time_estimates.get(complexity_level, "8-12 weeks")

    def _generate_system_components(self, functional_requirements: Dict, technical_context: Dict, complexity_level: str) -> List[Dict]:
        """Generate system component specifications."""
        components = [
            {
                "component_name": "Frontend Application",
                "responsibility": "User interface and user experience",
                "component_type": "frontend",
                "technologies": technical_context.get('preferred_stack', ["React", "TypeScript"]),
                "interfaces": {
                    "inputs": [{"name": "user_input", "type": "object", "source": "user"}],
                    "outputs": [{"name": "api_requests", "type": "http", "destination": "Backend API"}]
                },
                "performance_requirements": {
                    "latency": "<100ms UI response",
                    "throughput": "500 concurrent users",
                    "availability": "99.5%"
                }
            },
            {
                "component_name": "Backend API",
                "responsibility": "Business logic and data processing",
                "component_type": "backend",
                "technologies": ["FastAPI", "Python", "PostgreSQL"],
                "interfaces": {
                    "inputs": [{"name": "http_requests", "type": "http", "source": "Frontend"}],
                    "outputs": [{"name": "database_queries", "type": "sql", "destination": "Database"}]
                },
                "performance_requirements": {
                    "latency": "<200ms API response",
                    "throughput": "1000 req/sec",
                    "availability": "99.9%"
                }
            }
        ]
        
        # Add complexity-based components
        if complexity_level in ['complex', 'enterprise']:
            components.append({
                "component_name": "Caching Layer",
                "responsibility": "Performance optimization and data caching",
                "component_type": "middleware",
                "technologies": ["Redis"],
                "performance_requirements": {
                    "latency": "<5ms cache lookup",
                    "throughput": "10k ops/sec"
                }
            })
        
        return components

    def _generate_data_flow(self, functional_requirements: Dict) -> Dict[str, Any]:
        """Generate data flow architecture."""
        user_stories = functional_requirements.get('user_stories', [])
        
        primary_flows = []
        for i, story in enumerate(user_stories[:2]):  # Top 2 flows
            flow_name = f"User Flow {i+1}"
            sequence = [
                {"step": 1, "component": "Frontend", "action": "Capture input"},
                {"step": 2, "component": "Backend API", "action": "Process request"},
                {"step": 3, "component": "Database", "action": "Store/retrieve data"},
                {"step": 4, "component": "Backend API", "action": "Return response"}
            ]
            primary_flows.append({"flow_name": flow_name, "sequence": sequence})
        
        return {
            "primary_flows": primary_flows,
            "data_stores": [{
                "store_name": "Primary Database",
                "type": "relational",
                "purpose": "Store application data and user information",
                "access_patterns": ["read_heavy"]
            }]
        }

    def _generate_system_interfaces(self, technical_context: Dict) -> Dict[str, Any]:
        """Generate system interface specifications."""
        return {
            "external_apis": [],
            "internal_contracts": [{
                "interface_name": "Backend API Contract",
                "protocol": "HTTP REST",
                "endpoints": [
                    {"method": "GET", "path": "/health", "purpose": "Health check"},
                    {"method": "POST", "path": "/api/v1/data", "purpose": "Create data"},
                    {"method": "GET", "path": "/api/v1/data", "purpose": "Retrieve data"}
                ]
            }]
        }

    def _generate_deployment_architecture(self, complexity_level: str, constraints: Dict) -> Dict[str, Any]:
        """Generate deployment architecture strategy."""
        deployment_models = {
            "simple": "monolith",
            "moderate": "layered_monolith",
            "complex": "microservices",
            "enterprise": "microservices"
        }
        
        return {
            "deployment_model": deployment_models.get(complexity_level, "monolith"),
            "hosting_strategy": "cloud",
            "scaling_approach": "horizontal" if complexity_level in ['complex', 'enterprise'] else "vertical",
            "environments": [
                {"name": "development", "purpose": "Local development and testing"},
                {"name": "staging", "purpose": "Pre-production validation"},
                {"name": "production", "purpose": "Live user traffic"}
            ]
        }

    def _generate_risk_analysis(self, complexity_level: str) -> Dict[str, Any]:
        """Generate technical risk analysis."""
        return {
            "technical_risks": [
                {
                    "risk": "Database becomes performance bottleneck",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Implement connection pooling and read replicas"
                }
            ],
            "security_considerations": [
                {
                    "concern": "Data privacy and protection",
                    "approach": "End-to-end encryption and access controls"
                }
            ],
            "scalability_constraints": [
                "Database connection limits at high concurrency",
                "Memory usage scales with user sessions"
            ]
        }

    def _generate_implementation_phases(self, complexity_level: str) -> List[Dict[str, Any]]:
        """Generate implementation phase roadmap."""
        phases = [
            {
                "phase_name": "Core Foundation",
                "duration": "2-3 weeks",
                "components": ["Backend API", "Database"],
                "success_criteria": ["Basic CRUD operations functional"]
            },
            {
                "phase_name": "User Interface",
                "duration": "2-3 weeks",
                "components": ["Frontend Application"],
                "success_criteria": ["UI components render correctly"]
            }
        ]
        
        if complexity_level in ['complex', 'enterprise']:
            phases.append({
                "phase_name": "Performance Optimization",
                "duration": "1-2 weeks",
                "components": ["Caching Layer"],
                "success_criteria": ["Performance benchmarks met"]
            })
        
        return phases

    def _create_validation_checklist(self) -> List[Dict[str, str]]:
        """Create architecture validation checklist."""
        return [
            {"item": "All components have clear, single responsibilities", "status": "pending"},
            {"item": "Data flows are logical and efficient", "status": "pending"},
            {"item": "Component interfaces are well-defined", "status": "pending"},
            {"item": "Technical risks identified with mitigations", "status": "pending"},
            {"item": "Architecture supports Phase 1 requirements", "status": "pending"}
        ]

    def _generate_architecture_diagrams(self, architecture: Dict) -> List[Dict[str, str]]:
        """Generate Mermaid architecture diagrams."""
        # Component diagram
        components = architecture.get('system_components', [])
        component_diagram = "graph TD\n"
        
        for component in components:
            name = component.get('component_name', '').replace(' ', '_')
            comp_type = component.get('component_type', '')
            component_diagram += f"    {name}[{component.get('component_name')}<br/>{comp_type}]\n"
        
        # Add basic connections
        component_diagram += "    Frontend_Application --> Backend_API\n"
        component_diagram += "    Backend_API --> Database\n"
        
        return [
            {
                "type": "component",
                "title": "System Components",
                "mermaid": component_diagram
            }
        ]

    def _check_vibe_alignment(self, architecture: Dict, phase_1_output: Dict) -> Dict[str, Any]:
        """Check if architecture maintains Phase 1 vibe."""
        vibe_analysis = phase_1_output.get('vibe_analysis', {})
        antigoals = phase_1_output.get('constraints_and_antigoals', {}).get('must_avoid', [])
        
        # Simple vibe alignment scoring
        maintains_simplicity = 'complex' not in str(antigoals).lower()
        supports_performance = 'fast' in str(phase_1_output).lower() or 'speed' in str(phase_1_output).lower()
        
        return {
            "maintains_aesthetic": True,
            "avoids_complexity": maintains_simplicity,
            "supports_performance": supports_performance,
            "preserves_creative_flow": True,
            "vibe_score": 0.88
        }

    def _assess_specification_readiness(self, architecture: Dict) -> bool:
        """Assess if architecture is ready for Phase 3 specification."""
        required_elements = [
            architecture.get('system_components'),
            architecture.get('data_flow'),
            architecture.get('system_interfaces')
        ]
        return all(element for element in required_elements)
