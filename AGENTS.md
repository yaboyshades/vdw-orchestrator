# AGENTS Overview

This document describes agent responsibilities, IO contracts, prompts, and validation protocols for each VDW phase. Each directory with agents or reasoning components should include its own AGENTS.md with local details and links back to this root.

Structure:
- Role and responsibilities
- Input schema (contract)
- Output schema (contract)
- Prompts and prompt variables
- Events emitted / consumed
- Validation checklist (HITL)

## Phase 1: Mood & Requirements Agent
- Role: Transform raw "vibe" into structured requirements using Conversation Distillation
- Input: { project_id, vibe, distilled_requirements? }
- Output: { mood_json, requirements_yaml, dependency_graph }
- Emits: validation_required(phase=PHASE_1_VALIDATION)
- Consumes: prompts/phase_1_mood.md

## Phase 2: Architecture & Design Agent
- Role: Produce system architecture and validate via Mangle
- Input: { project_context.phase_1_output }
- Output: { architecture_json, diagrams, decisions }
- Emits: validation_required(phase=PHASE_2_VALIDATION)
- Consumes: prompts/phase_2_architecture.md

## Validation Protocol (HITL)
- Send MCP elicitation/request with checklist derived from phase outputs
- On approval -> transition to next phase; on reject -> re-run with feedback

See nested AGENTS.md files in:
- /agents
- /reasoning
- /core
