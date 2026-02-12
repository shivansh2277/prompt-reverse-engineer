"""Generate synthetic outputs for evaluation and benchmarking."""

from __future__ import annotations

import json
import random
from pathlib import Path

SAMPLES = [
    "You are a senior Python engineer. Provide concise code with tests.",
    "Explain quantum computing in 3 bullet points for beginners.",
    "Step 1: analyze constraints. Step 2: provide JSON output with confidence.",
    "{{ROLE}} {{TASK}} {{CONSTRAINTS}} Produce production-grade answer.",
]


def main() -> int:
    random.seed(1337)
    rows = []
    for i in range(200):
        text = random.choice(SAMPLES)
        rows.append({"id": i, "output_text": text})
    out = Path("scripts/data/synthetic_outputs.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
