"""Evaluate Prompt Reverse Engineer output quality on a local synthetic dataset."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.reverse_engineering_service import ReverseEngineeringService

DATASET_PATH = Path(__file__).resolve().parent / "data" / "synthetic_outputs.jsonl"


async def run_evaluation() -> dict[str, float]:
    """Run deterministic evaluation and return aggregate metrics."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_PATH}. Run scripts/generate_dataset.py first."
        )

    service = ReverseEngineeringService()
    total = 0
    confidence_sum = 0.0
    injection_flags = 0

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            result = await service.reverse(
                output_text=item["output_text"],
                request_id=f"eval-{item['id']}",
                deterministic=True,
                seed=1337,
            )
            total += 1
            confidence_sum += result.confidence_score
            if result.explainability.risk_flags and result.explainability.risk_flags[0] != "none":
                injection_flags += 1

    return {
        "samples": float(total),
        "avg_confidence": round(confidence_sum / total, 4) if total else 0.0,
        "risk_flag_rate": round(injection_flags / total, 4) if total else 0.0,
    }


def main() -> int:
    """Script entrypoint."""

    metrics = asyncio.run(run_evaluation())
    print(json.dumps(metrics))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
