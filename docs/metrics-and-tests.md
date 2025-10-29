# Metrics and Tests

- [x] Add Prometheus metrics definitions (core/metrics.py)
- [x] Add distillation instrumentation (reasoning/_distiller_metrics_patch.py)
- [x] Add basic pytest for ConversationDistiller (tests/test_conversation_distiller.py)
- [ ] Wire Prometheus ASGI /metrics mount (already present via previous docs config; verify and adjust)
- [ ] Add Mangle query latency instrumentation in MangleClient
