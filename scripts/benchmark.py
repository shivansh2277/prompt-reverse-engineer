"""Benchmark local Prompt Reverse Engineer API latency and throughput."""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx


async def hit(client: httpx.AsyncClient, payload: dict[str, str]) -> float:
    """Call reverse endpoint and return latency in ms."""

    start = time.perf_counter()
    response = await client.post("/reverse", json=payload)
    response.raise_for_status()
    return (time.perf_counter() - start) * 1000


async def run_benchmark(base_url: str, requests: int, concurrency: int) -> dict[str, float]:
    """Run asynchronous benchmark for /reverse endpoint."""

    payload = {"output_text": "Step 1: analyze constraints. Step 2: return JSON with confidence."}
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(base_url=base_url, timeout=20) as client:

        async def guarded() -> float:
            async with sem:
                return await hit(client, payload)

        started = time.perf_counter()
        durations = await asyncio.gather(*(guarded() for _ in range(requests)))
        total_elapsed = time.perf_counter() - started

    sorted_lat = sorted(durations)
    p50 = statistics.median(sorted_lat)
    p95 = sorted_lat[max(0, int(len(sorted_lat) * 0.95) - 1)]

    return {
        "requests": float(requests),
        "concurrency": float(concurrency),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "avg_ms": round(sum(sorted_lat) / len(sorted_lat), 2),
        "rps": round(requests / total_elapsed, 2) if total_elapsed > 0 else 0.0,
    }


def main() -> int:
    """Script entrypoint."""

    parser = argparse.ArgumentParser(description="Benchmark Prompt Reverse Engineer API")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of running API")
    parser.add_argument("--requests", type=int, default=100, help="Total requests to send")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent in-flight requests")
    args = parser.parse_args()

    results = asyncio.run(run_benchmark(args.base_url, args.requests, args.concurrency))
    print(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
