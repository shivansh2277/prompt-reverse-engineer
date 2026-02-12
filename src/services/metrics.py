"""In-memory request timing and endpoint counters."""

from __future__ import annotations

import time
from collections import defaultdict


class MetricsRegistry:
    """Simple metrics registry for observability."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = defaultdict(int)
        self._durations_ms: dict[str, list[float]] = defaultdict(list)

    def track(self, endpoint: str, started_at: float) -> float:
        elapsed = (time.perf_counter() - started_at) * 1000
        self._counts[endpoint] += 1
        self._durations_ms[endpoint].append(elapsed)
        return elapsed

    def snapshot(self) -> dict[str, dict[str, float]]:
        return {
            endpoint: {
                "count": float(count),
                "avg_ms": (sum(self._durations_ms[endpoint]) / len(self._durations_ms[endpoint]))
                if self._durations_ms[endpoint]
                else 0.0,
            }
            for endpoint, count in self._counts.items()
        }
