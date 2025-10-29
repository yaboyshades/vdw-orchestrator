# Vibe-Driven Waterfall (VDW) Orchestrator

*A revolutionary MCP-based agentic system implementing the Vibe-Driven Waterfall methodology for structured software development*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://spec.modelcontextprotocol.io/)

## 🌟 Overview

The VDW Orchestrator bridges the gap between creative "vibe-driven" ideation and disciplined, structured execution. Built on the Model Context Protocol (MCP), it implements a sequential orchestration pattern featuring five specialized agents, each handling a distinct phase of the software development lifecycle with advanced reasoning capabilities.

### Revolutionary Features

🧠 **Advanced Reasoning**: Integrates Google's Mangle deductive reasoning engine for recursive self-reflection and dependency analysis

🔄 **Self-Evolving Toolbox**: Dynamic tool synthesis and the "MCP Box" for autonomous capability expansion

💬 **Conversation Distillation**: Transforms unstructured user input into structured, actionable implementation plans

🤖 **Human-in-the-Loop**: Mandatory validation gates using MCP elicitation/request primitives

📊 **Unified Memory**: Atoms and Bonds architecture for comprehensive project artifact tracking

## 🏗️ Architecture

The system implements a **Sequential Orchestration** pattern enhanced with advanced cognitive capabilities:

### Core Phases

1. **Phase 1: Mood & Requirements** - Captures initial "vibe" using conversation distillation
2. **Phase 2: Architecture & Design** - Creates system architecture with reasoning validation
3. **Phase 3: Technical Specification** - Develops detailed technical specifications
4. **Phase 4: Implementation** - Generates production-ready code with dependency analysis
5. **Phase 5: Validation & Testing** - Performs comprehensive testing and validation

### Enhanced Architecture Components

```mermaid
graph TD
    subgraph User Interaction
        A[User provides "vibe"]
        I[User validates phase]
    end
    
    subgraph VDW Orchestrator Core
        B(Orchestrator)
        C(State Machine)
        D(Event Bus)
        E(Memory Store)
        F(Tool Registry / MCP Box)
    end
    
    subgraph Reasoning Layer
        G(Mangle Sidecar)
        H(Conversation Distiller)
    end
    
    subgraph VDW Phase Agents
        P1(Phase 1: Mood)
        P2(Phase 2: Architecture)
        P3(Phase 3: Specification)
        P4(Phase 4: Implementation)
        P5(Phase 5: Validation)
    end
    
    A -->|raw input| H
    H -->|distilled structure| P1
    P1 -->|mood JSON| B
    B <-->|gRPC| G
    G -->|validates dependencies| B
    G -->|queries| E
    B --> C --> D --> F
    F -->|provides tools| P1
    F -->|provides tools| P2
    F -->|provides tools| P3
    F -->|provides tools| P4
    F -->|provides tools| P5
    B -->|elicitation| I
    I -->|feedback| B
```

## 📁 Project Structure

```
vdw-orchestrator/
├── core/
│   ├── __init__.py
│   ├── orchestrator.py           # VDWOrchestrator class
│   ├── state_machine.py          # VDWStateMachine class
│   ├── models.py                 # Pydantic models
│   ├── event_bus.py              # Redis-backed event bus
│   ├── memory_store.py           # Atoms and Bonds memory
│   └── tool_registry.py          # MCP Box implementation
├── reasoning/
│   ├── __init__.py
│   ├── mangle_client.py          # gRPC client for Mangle
│   ├── conversation_distiller.py # Input distillation
│   └── self_reflection.py        # Recursive learning
├── agents/
│   ├── __init__.py
│   ├── base_phase_agent.py       # Base class for all phases
│   ├── phase_1_mood.py           # Enhanced with distillation
│   ├── phase_2_architecture.py   # Reasoning-enhanced design
│   ├── phase_3_specification.py  # Specification generation
│   ├── phase_4_implementation.py # Dependency-aware coding
│   └── phase_5_validation.py     # Comprehensive testing
├── prompts/
│   ├── phase_1_mood.md
│   ├── phase_2_architecture.md
│   ├── phase_3_specification.md
│   ├── phase_4_implementation.md
│   └── phase_5_validation.md
├── mangle/
│   ├── Dockerfile                # Mangle reasoning sidecar
│   ├── reasoning_rules.dl        # Datalog reasoning rules
│   └── grpc_server.go           # gRPC reasoning service
├── docs/
│   ├── architecture.md
│   ├── implementation-blueprint.md
│   ├── research-findings.md
│   └── advanced-enhancements.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── docker-compose.yml        # Full stack deployment
│   └── Dockerfile.orchestrator   # Main orchestrator
├── database/
│   ├── schema.sql               # SQLite schema for tool metadata
│   └── migrations/
├── main.py                      # MCP server entry point
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

## 🚀 Implementation Roadmap

### Phase 1: Enhanced Core Infrastructure (2-3 weeks)
- ✅ Repository setup and enhanced project structure
- 🔄 Core Pydantic models with reasoning integration
- 🔄 Redis-backed EventBus with gRPC support
- 🔄 Enhanced State Machine with Mangle validation
- 🔄 MCP Box tool registry implementation

### Phase 2: Reasoning Layer Integration (3-4 weeks)
- 🔄 Mangle sidecar deployment and gRPC integration
- 🔄 Conversation distillation for Phase 1
- 🔄 Basic dependency validation rules
- 🔄 Two-phase proof of concept with reasoning

### Phase 3: Full Five-Phase with Advanced Features (4-5 weeks)
- 🔄 All phase agents with reasoning capabilities
- 🔄 Self-reflection and cross-project learning
- 🔄 Dynamic tool synthesis and registration
- 🔄 Complete memory store with Atoms and Bonds

### Phase 4: Production Hardening (3-4 weeks)
- 🔄 Comprehensive security implementation
- 🔄 Full containerization with orchestration
- 🔄 Performance optimization and monitoring
- 🔄 Complete testing suite and CI/CD

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Redis (for event bus)
- Go 1.19+ (for Mangle sidecar)

### Installation

```bash
# Clone the repository
git clone https://github.com/yaboyshades/vdw-orchestrator.git
cd vdw-orchestrator

# Install Python dependencies
pip install -r requirements.txt

# Start the full stack with Docker Compose
docker-compose up -d

# Run the MCP server
python main.py
```

### Basic Usage

```python
from vdw_orchestrator import VDWOrchestrator

# Initialize the orchestrator
orchestrator = VDWOrchestrator()

# Submit a new project with your "vibe"
project_id = await orchestrator.submit_project(
    vibe="I want to build a social media app for developers to share code snippets"
)

# The orchestrator will guide you through all five phases
# with Human-in-the-Loop validation at each step
```

## 📚 Documentation

- [**Architecture Overview**](docs/architecture.md) - Detailed system architecture and design principles
- [**Implementation Blueprint**](docs/implementation-blueprint.md) - Developer-focused implementation guide
- [**Research Findings**](docs/research-findings.md) - Comprehensive research backing the VDW methodology
- [**Advanced Enhancements**](docs/advanced-enhancements.md) - Mangle integration and conversation distillation

## 🧪 Advanced Features

### Mangle Reasoning Integration

The system uses Google's Mangle deductive reasoning engine for:
- **Recursive Self-Reflection**: Analyzes past project outcomes to improve future executions
- **Dependency Analysis**: Validates phase prerequisites and artifact completeness
- **Goal Decomposition**: Breaks complex tasks into actionable sub-goals

### Dynamic Tool Synthesis

The "MCP Box" enables:
- **Autonomous Tool Creation**: Generates specialized tools for specific project needs
- **Cross-Project Learning**: Reuses successful tools from previous projects
- **Performance Optimization**: Tracks tool usage and optimizes for better performance

### Conversation Distillation

Transforms unstructured user input into:
- **Logical Segments**: Groups related concepts and requirements
- **Dependency Graphs**: Maps causal relationships and prerequisites
- **Structured Output**: Generates hierarchical requirements with explicit links

## 🤝 Contributing

This project implements a novel software development methodology combining cutting-edge research in:
- Deductive reasoning systems
- Autonomous agent architectures  
- Conversation understanding
- Model Context Protocol integration

Contributions are welcome! Please ensure all changes align with the VDW methodology principles and advanced cognitive architecture.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black . && flake8 .

# Start development stack
docker-compose -f docker-compose.dev.yml up
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 References

- [Microsoft AI Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [MCP Production Best Practices](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Google Mangle: Datalog-based Deductive Reasoning](https://research.google/)
- [Conversation Distillation for Implementation Planning](https://arxiv.org/)

---

*Built with ❤️ using the revolutionary Vibe-Driven Waterfall methodology*

**"Where creative intuition meets disciplined execution"**