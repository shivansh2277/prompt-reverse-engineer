import asyncio
import json
from pathlib import Path

from src.services.reverse_engineering_service import ReverseEngineeringService


async def main():
    service = ReverseEngineeringService()
    dataset = Path("scripts/data/synthetic_outputs.jsonl")

    total = 0
    confidence_sum = 0.0

    for line in dataset.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)

        response = await service.reverse(
            output_text=record["output_text"]
        )

        total += 1
        confidence_sum += response.confidence_score

    avg_conf = confidence_sum / total if total else 0

    print({
        "samples": total,
        "avg_confidence": avg_conf
    })


if __name__ == "__main__":
    asyncio.run(main())
