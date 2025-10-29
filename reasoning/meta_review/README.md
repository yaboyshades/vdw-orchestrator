# Meta-Review and Mental Game Analysis

This directory contains the implementation of a comprehensive meta-cognitive analysis system for evaluating and improving reasoning processes across the VDW lifecycle.

## Components

- `core.py` — Core framework with `MetaReviewFramework`, `MentalGameAnalyzer`, data models, scoring, and insight generation.
- `perspectives.py` — Modular analyzers for Skeptical, Novice, and Cross-Domain perspectives.
- `validators.py` — Quantitative metrics and validation gates for phase transitions.
- `integration.py` — High-level helper to run meta-review at VDW phase gates and return structured results.

## Quick Start

```python
from reasoning.meta_review.core import MetaReviewFramework, ReasoningArtifact, ReviewDepth
from reasoning.meta_review.validators import QualityMetrics, ValidationGates
from reasoning.meta_review.integration import VDWIntegration

framework = MetaReviewFramework()
integration = VDWIntegration(
    framework=framework,
    gates=ValidationGates(min_score=7.5, min_breadth=3, require_meta_insights=True),
    metrics=QualityMetrics(),
)

artifact = ReasoningArtifact(
    title="Phase 2 Architecture Review",
    content="""Summarize the artifact content here. Include evidence, counterpoints, and examples.
This improves skeptical and novice analyses and avoids penalties for missing evidence.
""",
    author="reviewer",
    phase="phase2",
)

result_payload = integration.review_phase_output(
    title=artifact.title,
    content=artifact.content,
    phase=artifact.phase,
    author=artifact.author,
)

if integration.should_advance_phase(result_payload):
    print("Phase can advance ✅")
else:
    print("Hold phase ❌:", result_payload["validation_errors"])
```

## CLI Hook (optional)

You can wire this into `main.py` or a new CLI command to run meta-review on files in `reasoning/`.

```bash
python -m reasoning.meta_review.cli --file reasoning/file4.md --phase phase2
```

## Roadmap

- Add collaborative reviewer consensus and inter-rater reliability
- Persist reviews to database and expose via MCP tools
- Add domain-specific analyzers and uncertainty quantification
- Integrate with monitoring dashboards for longitudinal tracking
