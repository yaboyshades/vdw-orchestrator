# AGENTS TODO Log

This file tracks a living, detailed task list for agent-related work across the VDW Orchestrator. Use atomic, checkable tasks. Reference PRs, commits, or issues inline.

Conventions:
- Status: [ ] open, [~] in progress, [x] done, [!] blocked, [?] needs input
- Scope tags: [core], [agents], [reasoning], [mcp-box], [infra], [docs], [tests]
- Link to nested TODOs: see per-directory TODO.md files

## Phase 2: Reasoning Layer Integration (current)

- [~][reasoning][agents] Implement ConversationDistiller into Phase 1 agent pipeline (context injection, YAML export)
- [ ][reasoning] Add unit tests for ConversationDistiller segmentation and dependency graph generation
- [ ][reasoning] Wire MangleClient into VDWStateMachine.can_transition_to with real gRPC call (replace simulator)
- [ ][mcp-box] Expose MCPBoxRegistry via dependency injection and add CRUD API endpoints
- [ ][agents] Scaffold Phase 1 and Phase 2 agents (execute(), validation emit, prompt loading)
- [ ][infra] Add docker-compose.dev.yml with hot-reload and bind mounts
- [ ][infra] Create monitoring dashboards (Grafana) for reasoning latency and tool success rate

## Backlog

- [ ][core] Implement EventBus (Redis pub/sub) and event types handlers
- [ ][core] Implement MemoryStore (Atoms/Bonds) with persistence
- [ ][core] Finish VDWOrchestrator orchestration loop and event handlers
- [ ][agents] Implement Phases 3–5 skeletal agents with contracts
- [ ][tests] CI pipeline (lint, unit, integration) and pre-commit hooks
- [ ][docs] Author AGENTS.md and directory-level AGENTS.md with contracts & prompts

## Done

- [x][docs] Add advanced enhancements documentation
- [x][infra] Add Dockerfile and docker-compose with mangle, redis, monitoring stack
- [x][mcp-box] Implement SQLite schema and MCPBoxRegistry
