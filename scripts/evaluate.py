"""Offline evaluation for Prompt Reverse Engineer quality controls."""

from __future__ import annotations

import json
from pathlib import Path

from src.services.reverse_engineering_service import ReverseEngineeringService


def main() -> int:
    dataset = Path("scripts/data/synthetic_outputs.jsonl")
    if not dataset.exists():
        print("dataset missing; run scripts/generate_synthetic_dataset.py first")
        return 1

    service = ReverseEngineeringService()
    total = 0
    confidence_sum = 0.0

    for line in dataset.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        response = __import__("asyncio").run(
            service.reverse(
                output_text=record["output_text"],
                request_id=f"eval-{record['id']}",
                deterministic=True,
                seed=1337,
            )
        )
        total += 1
        confidence_sum += response.confidence_score

    avg_conf = confidence_sum / total if total else 0.0
    print(json.dumps({"samples": total, "avg_confidence": round(avg_conf, 4)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
