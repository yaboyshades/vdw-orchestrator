# MCP Production Best Practices

## Key Findings from Production Deployments

### 1. Bounded Context Design
Model each MCP server around a single microservice domain. Expose only capabilities belonging to that domain with cohesive, uniquely named tools. Use clear JSON schemas for inputs/outputs to enable LLM disambiguation.

### 2. Stateless & Idempotent Tools
Tools should be idempotent to handle agent retries and parallelization. Accept client-generated request IDs and return deterministic results. Use pagination tokens for list operations to maintain predictable response sizes.

### 3. Transport Selection
- **STDIO**: Baseline transport for maximum compatibility, preferred for development/testing
- **Streamable HTTP**: First-class transport for production, remote deployments, and horizontal scaling
- **SSE**: Deprecated as of 2025-06-18 specification
- Implement request cancellation and timeouts to prevent resource starvation

### 4. Elicitation for Human-in-the-Loop
Use elicitation to fill missing parameters or confirm risky actions. Keep prompts concise, validate responses against schemas, implement graceful fallbacks. **Note**: Feature introduced June 2025, not universally supported yet—gate with capability checks.

### 5. Security-First Design (OAuth 2.1)
- OAuth 2.1 is **mandatory** for HTTP-based transports (March 2025 spec update)
- Generate non-predictable session identifiers
- Verify all authorized requests
- Minimize data exposure
- Implement authorization server metadata discovery
- Support dynamic client registration
- Never echo secrets in tool results or elicitation messages

### 6. Dual UX: Agent + Human
Responses must be both LLM-parsable and human-readable. Use:
- `outputSchema` for precise, typed outputs (June 2025 spec)
- `structuredContent` fields for structured data
- Traditional content blocks for human users
- Machine-readable error codes with brief explanations

### 7. Production Instrumentation
Emit structured logs with:
- Correlation IDs
- Tool name and invocation ID
- Latency metrics
- Success/failure rates
- Token-cost hints
- Soft limits and rate limits for agent budgeting

### 8. Versioning & Capability Advertisement
- Use semantic versioning for servers and individual tools
- Publish tool lists, resource types, and optional features at handshake
- Enable capability-driven client adaptation
- Support graceful degradation for missing features

### 9. Separation of Concerns
- **Prompts**: Store server-side, expose via MCP prompts interface
- **Tools**: Keep decoupled from prompts
- **Resources**: Treat as read-only or minimally mutable with explicit URIs, access rules, and pagination

### 10. Streaming & Large Outputs
- Emit incremental chunks for long operations on Streamable HTTP
- Advertise total counts where feasible
- Return handles/URIs for large payloads instead of inlining data
- Optimize for both simple queries and complex streaming operations

### 11. Comprehensive Testing
- Validate against multiple MCP clients/hosts (including STDIO-only)
- Inject faults: slow downstreams, partial failures, malformed inputs
- Use official quickstart and inspector tools
- Test both traditional content blocks and structured content outputs

### 12. Microservice Packaging
- Containerize servers
- Declare transport and invocation commands clearly
- Publish minimal runtime images
- Provide comprehensive README with tool catalog, schemas, examples, security notes

### 13. Platform Awareness
- MCP adoption growing across Windows, IDEs, vendor ecosystems
- Capabilities differ by host
- OAuth 2.1 and structured content not universally available
- Implement feature flags and graceful degradation

### 14. API Design Fundamentals
Behind MCP layer, maintain:
- Least-privilege operations
- Clear resource lifecycles
- Eventual consistency where appropriate
- Idempotent mutations
- Predictable request/response semantics

### 15. Risk Documentation & Consent
For state-changing or financial operations:
- Require confirmation via elicitation or dry-run mode
- Return diff of intended changes before execution
- Use structured content for machine-readable change summaries
- Provide human-readable descriptions

## Critical Specification Updates

### March 2025
- OAuth 2.1 mandatory for HTTP transports

### June 2025
- SSE transport deprecated
- Streamable HTTP introduced as first-class transport
- `outputSchema` and `structuredContent` fields added
- Elicitation feature introduced

## Implications for Vibe-Driven Waterfall

### Architecture Decisions
1. **Phase as Tools**: Each waterfall phase can be exposed as an MCP tool
2. **Artifacts as Resources**: Phase outputs (JSON) can be MCP resources
3. **State Management**: Use stateful protocol features for phase tracking
4. **Human Validation**: Leverage elicitation for phase gate approvals
5. **Structured Outputs**: Use `outputSchema` for phase transition data

### Implementation Strategy
- Build as bounded context around "software development lifecycle"
- Implement STDIO for development, Streamable HTTP for production
- Use elicitation for validation checklists between phases
- Store phase prompts as MCP prompts
- Emit phase artifacts as MCP resources
- Version phase tools independently
- Instrument phase transitions with structured logging