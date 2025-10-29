"""Simple CLI for running meta-review on a reasoning file."""

import argparse
from pathlib import Path

from .core import MetaReviewFramework, ReasoningArtifact, ReviewDepth
from .validators import QualityMetrics, ValidationGates
from .integration import VDWIntegration


def main():
    parser = argparse.ArgumentParser(description="Run Meta-Review on a reasoning file")
    parser.add_argument("--file", required=True, help="Path to the reasoning file (markdown or text)")
    parser.add_argument("--phase", required=True, help="VDW phase label (e.g., phase2)")
    parser.add_argument("--author", default="cli", help="Author of the artifact")
    args = parser.parse_args()

    content = Path(args.file).read_text(encoding="utf-8")
    title = Path(args.file).stem

    framework = MetaReviewFramework()
    integration = VDWIntegration(
        framework=framework,
        gates=ValidationGates(),
        metrics=QualityMetrics(),
    )

    payload = integration.review_phase_output(
        title=title,
        content=content,
        phase=args.phase,
        author=args.author,
    )

    print("Meta-Review Summary:")
    print(payload["metrics"]) 
    if integration.should_advance_phase(payload):
        print("Proceed: ✅")
    else:
        print("Hold: ❌")
        for err in payload["validation_errors"]:
            print(" -", err)


if __name__ == "__main__":
    main()
