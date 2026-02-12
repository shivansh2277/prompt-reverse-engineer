"""Simple benchmark runner against running local API."""

from __future__ import annotations

import asyncio
import statistics
import time

import httpx


async def hit(client: httpx.AsyncClient, payload: dict[str, str]) -> float:
    start = time.perf_counter()
    response = await client.post("/reverse", json=payload)
    response.raise_for_status()
    return (time.perf_counter() - start) * 1000


async def main() -> int:
    durations: list[float] = []
    payload = {"output_text": "Step 1: analyze. Step 2: return JSON with confidence and constraints."}
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=15) as client:
        tasks = [hit(client, payload) for _ in range(100)]
        durations.extend(await asyncio.gather(*tasks))

    print(
        {
            "requests": len(durations),
            "p50_ms": round(statistics.median(durations), 2),
            "p95_ms": round(sorted(durations)[int(len(durations) * 0.95) - 1], 2),
            "avg_ms": round(sum(durations) / len(durations), 2),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
