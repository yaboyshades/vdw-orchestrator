# Vibe-Driven Waterfall (VDW) Orchestrator Architecture

**Author**: Manus AI  
**Date**: October 29, 2025

## 1. Overview

This document outlines the comprehensive architecture for the **Vibe-Driven Waterfall (VDW) Orchestrator**, an MCP-based agentic system designed to implement the VDW methodology. This architecture synthesizes the robust, event-driven patterns from the provided `agentic-orchestrator` framework with the specific, phase-based requirements of the VDW cognitive model.

The VDW Orchestrator is designed as a **Sequential Orchestration** pattern, as defined by Microsoft Azure's AI Agent Orchestration Patterns [1], where each of the five VDW phases is a distinct, specialized agent in a predefined, linear sequence. The system leverages the stateful, real-time capabilities of the Model Context Protocol (MCP) to manage the lifecycle of a software project from initial "vibe" to final validation.

## 2. Core Architectural Principles

The architecture is founded on best practices identified during the research phase, combining the provided framework's design with MCP production guidelines [2].

- **Bounded Context**: The entire orchestrator acts as a single bounded context for the "software development lifecycle." Each of the five VDW phases is implemented as a distinct, specialized agent (or "tool" in MCP terms) within this context.
- **Event-Driven Communication**: All interactions between the orchestrator, the phase-agents, and the user are handled via a central `EventBus`, ensuring decoupled and asynchronous communication.
- **Stateful, Sequential Orchestration**: The core orchestrator implements a state machine that manages the project's progression through the five VDW phases. A project cannot advance to the next phase until the current one is completed and validated.
- **Human-in-the-Loop (HITL) Validation**: Phase transitions are gated by mandatory human validation, implemented using the MCP `elicitation/request` primitive. This is the core mechanism for ensuring quality and alignment with the user's intent.
- **Unified Memory (Atom/Bond Model)**: All artifacts generated during the VDW process (mood analysis, architecture diagrams, specifications, code) are stored as `Atoms` in a central `MemoryStore`. The relationships between these artifacts (e.g., "Phase 2 architecture is based on Phase 1 mood") are stored as `Bonds`.
- **Contract-Based Capabilities**: Each VDW phase is exposed as an MCP tool with a clearly defined `input_schema` and `output_schema`, ensuring predictable, type-safe interactions.

## 3. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph User Interaction (MCP Client)
        A[User provides initial "vibe"]
        I[User validates phase output]
    end

    subgraph VDW Orchestrator (MCP Server)
        B(Orchestrator Core)
        C(State Machine)
        D(Event Bus)
        E(Memory Store)
        F(Agent Registry)

        subgraph VDW Phase Agents
            P1(Phase 1: Mood)
            P2(Phase 2: Architecture)
            P3(Phase 3: Specification)
            P4(Phase 4: Implementation)
            P5(Phase 5: Validation)
        end
    end

    A -->|submit_task| B
    B --triggers--> C
    C --updates_state--> E
    C --dispatches_event--> D
    D --notifies--> B

    B --finds_agent--> F
    F --returns_agent_info--> B

    B --assigns_task--> D
    D --sends_to_agent--> P1
    P1 --returns_result--> D
    D --notifies_completion--> B

    B --requests_validation--> D
    D --sends_elicitation--> I
    I --provides_feedback--> D
    D --notifies_validation--> B

    B --triggers_next_phase--> P2
    P2 --> D --> B
    B --> P3
    P3 --> D --> B
    B --> P4
    P4 --> D --> B
    B --> P5
    P5 --> D --> B
```

## 4. Core Components

This architecture adapts the components from the provided `agentic-orchestrator` framework for the VDW use case.

| Component | Description |
|---|---|
| **Orchestrator Core** | The central brain. It receives the initial user request, initializes the state machine, and manages the overall lifecycle of the VDW process. It listens for events and dispatches new tasks based on the current state. |
| **State Machine** | Manages the current phase of the project (`PHASE_1_MOOD`, `PHASE_2_ARCHITECTURE`, etc.). It contains the logic for transitioning between states, triggered by successful phase completion and user validation. |
| **Event Bus** | A Redis-backed message bus for all asynchronous communication. It handles `TaskCreated`, `TaskCompleted`, `HumanValidationRequired`, and `PhaseTransition` events. |
| **Memory Store** | A persistent store (e.g., using JSON files or a simple DB) for all project artifacts, modeled as Atoms and Bonds. It maintains the "Project Context." |
| **Agent Registry** | A simple registry that holds the definitions of the five VDW phase-agents. Since the agents are fixed, this is less dynamic than in a general-purpose orchestrator. |
| **VDW Phase Agents** | Five specialized agents, each corresponding to one phase of the VDW methodology. Each agent is essentially a wrapper around the detailed prompts you created. |

## 5. VDW State Machine & Data Flow

The core of the orchestrator is a Finite State Machine (FSM) where each state represents a phase of the waterfall.

### States
1.  `IDLE`
2.  `PHASE_1_MOOD`
3.  `PHASE_1_VALIDATION`
4.  `PHASE_2_ARCHITECTURE`
5.  `PHASE_2_VALIDATION`
6.  `PHASE_3_SPECIFICATION`
7.  `PHASE_3_VALIDATION`
8.  `PHASE_4_IMPLEMENTATION`
9.  `PHASE_4_VALIDATION`
10. `PHASE_5_VALIDATION_TESTING`
11. `PHASE_5_VALIDATION`
12. `COMPLETED`
13. `FAILED`

### Data Flow: The Project Context

A `ProjectContext` object is created for each project. It is passed between phases and accumulates the artifacts (Atoms) from each completed phase. This object serves as the "common state" in the sequential orchestration pattern.

```python
class ProjectContext(BaseModel):
    project_id: str
    initial_vibe: str
    phase_1_output: Optional[Dict] = None # The JSON from the mood phase
    phase_2_output: Optional[Dict] = None # The JSON from the architecture phase
    phase_3_output: Optional[Dict] = None # The generated spec files
    phase_4_output: Optional[Dict] = None # The implemented code files
    phase_5_output: Optional[Dict] = None # The validation results
```

### Transitions

A transition from `PHASE_N` to `PHASE_N+1` occurs only if the `PHASE_N_VALIDATION` state is successfully passed. The validation state is entered after the `PHASE_N` agent completes its task. The orchestrator sends an `elicitation/request` to the user and waits for a positive confirmation.

## 6. Human-in-the-Loop (HITL) Protocol

The validation gates between phases are the most critical part of the VDW process. This is implemented using the MCP `elicitation/request` primitive.

**Orchestrator -> Client (Elicitation Request):**

```json
{
  "jsonrpc": "2.0",
  "method": "elicitation/request",
  "params": {
    "request_id": "validation-p1-abcde",
    "type": "confirmation",
    "schema": {
      "type": "object",
      "properties": {
        "approved": {"type": "boolean"},
        "feedback": {"type": "string"}
      },
      "required": ["approved"]
    },
    "content": {
      "title": "Phase 1: Mood & Requirements Validation",
      "checklist": [
        {"item": "Vibe Captured Accurately", "value": "✅"},
        {"item": "Key Features Identified", "value": "✅"},
        {"item": "Technical Stack Aligned", "value": "⚠️ (User clarification needed)"}
      ],
      "summary": "The initial analysis is complete. Please review the generated artifacts and confirm if we can proceed to the Architecture phase."
    }
  }
}
```

**Client -> Orchestrator (Elicitation Response):**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "request_id": "validation-p1-abcde",
    "response": {
      "approved": true,
      "feedback": "Looks good, but for the tech stack, let's use PostgreSQL instead of MySQL."
    }
  },
  "id": 123
}
```

The orchestrator parses this response. If `approved` is `true`, it transitions to the next phase, passing the `feedback` into the `ProjectContext`. If `false`, it re-runs the current phase with the feedback as additional input.

## 7. Mapping VDW to MCP Primitives

| VDW Concept | MCP Primitive | Implementation Detail |
|---|---|---|
| **VDW Phase** | `tool` | Each of the 5 phases is an MCP tool (e.g., `vdw/phase1_mood`). The orchestrator calls these tools sequentially. |
| **Phase Artifact** | `resource` | The JSON output of each phase is stored as a versioned, addressable resource. The resource URI is added to the `ProjectContext`. |
| **Phase Prompt** | `prompt` | The detailed prompt for each phase is stored as an MCP prompt and is called by the corresponding phase-tool. |
| **Validation Gate** | `elicitation/request` | Used to present the `validation_checklist` to the user and get explicit approval before transitioning to the next phase. |
| **Phase Transition** | `notification` | The orchestrator can emit `vdw/phase_changed` notifications to inform the client of progress. |

## 8. References

[1] Microsoft. (2025, July 18). *AI Agent Orchestration Patterns*. Azure Architecture Center. Retrieved from https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns

[2] MSV, J. (2025, September 15). *15 Best Practices for Building MCP Servers in Production*. The New Stack. Retrieved from https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/