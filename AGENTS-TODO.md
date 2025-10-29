# AGENTS TODO Log

This file tracks a living, detailed task list for agent-related work across the VDW Orchestrator. Use atomic, checkable tasks. Reference PRs, commits, or issues inline.

Conventions:
- Status: [ ] open, [~] in progress, [x] done, [!] blocked, [?] needs input
- Scope tags: [core], [agents], [reasoning], [mcp-box], [infra], [docs], [tests]
- Link to nested TODOs: see per-directory TODO.md files

## Phase 2: Reasoning Layer Integration (current)

- [x][agents][reasoning] Implement ConversationDistiller into Phase 1 agent pipeline (context injection, YAML export) — commit 3585b3d
- [~][reasoning] Wire MangleClient into VDWStateMachine.can_transition_to with real gRPC call (replace simulator)
  - [x] Generate Python stubs from proto (scripts/build_grpc_stubs.sh) — script added
  - [x] Import generated stubs in reasoning/mangle_client.py and call stub.Query — commit a127a5d
  - [ ] Map full ReasoningQuery facts/rules/goals into protobuf fields
- [x][agents] Scaffold Phase 1 and Phase 2 agents (execute(), validation emit, prompt loading) — commits 3585b3d, 8bcdc15d
- [x][infra] Add docker-compose.dev.yml with hot-reload and bind mounts — commit 3585b3d
- [x][core] Wire orchestrator + API endpoints for Phase 1→2 flow — commit 8bcdc15d
- [x][infra] Monitoring: add Prometheus scrape config — commit 3585b3d
- [x][core] Expand API with GET project/artifacts and rejection loop — commit e4c162e
- [~][mcp-box] Expose MCPBoxRegistry via dependency injection and add CRUD API endpoints — commits f1ae8e2, c9c0b18
  - [ ] Add capability gap analysis endpoint (/tools/gaps)
  - [ ] Add record usage endpoint (/tools/{id}/usage)
- [ ][tests] Add unit tests for ConversationDistiller segmentation and dependency graph generation
- [ ][infra] Create Grafana dashboards (reasoning latency, tool success rate)

## Backlog

- [ ][core] Implement MemoryStore bonds queries and search API
- [ ][agents] Implement Phases 3–5 skeletal agents with contracts
- [ ][tests] CI pipeline (lint, unit, integration) and pre-commit hooks
- [ ][docs] Expand AGENTS.md with JSON schemas for IO contracts
