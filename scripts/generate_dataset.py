"""Generate a synthetic dataset for Prompt Reverse Engineer evaluation/benchmarking."""

from __future__ import annotations

import json
import random
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "synthetic_outputs.jsonl"
SAMPLES = [
    "You are a senior Python engineer. Provide concise code with tests and comments.",
    "Explain quantum computing in three bullet points for beginners.",
    "Step 1: analyze constraints. Step 2: provide JSON output with confidence.",
    "{{ROLE}} {{TASK}} {{CONSTRAINTS}} Produce a production-grade answer.",
    "As an architect, provide a short design proposal with risks and mitigations.",
]


def main() -> int:
    """Generate deterministic JSONL synthetic outputs."""

    random.seed(1337)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for idx in range(250):
        rows.append({"id": idx, "output_text": random.choice(SAMPLES)})

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Generated {len(rows)} rows at {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
