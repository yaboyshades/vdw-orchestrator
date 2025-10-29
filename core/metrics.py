from prometheus_client import Counter, Histogram

# Distillation metrics
distillation_latency_ms = Histogram(
    'vdw_distillation_latency_ms', 'Time spent distilling conversation',
    buckets=(10, 25, 50, 100, 250, 500, 1000, 2500, 5000)
)

# Mangle metrics
mangle_query_latency_ms = Histogram(
    'vdw_mangle_query_latency_ms', 'Latency of Mangle reasoning queries (ms)',
    buckets=(5, 10, 20, 50, 100, 200, 500, 1000, 2000)
)

# Phase durations
phase_duration_ms = Histogram(
    'vdw_phase_duration_ms', 'Duration of VDW phases (ms)',
    ['phase'], buckets=(50, 100, 250, 500, 1000, 5000, 10000, 30000)
)

# Tool outcomes
tool_success_total = Counter(
    'vdw_tool_success_total', 'Total successful tool executions', ['tool_id']
)

tool_failure_total = Counter(
    'vdw_tool_failure_total', 'Total failed tool executions', ['tool_id']
)
