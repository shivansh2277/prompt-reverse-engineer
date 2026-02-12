"""In-memory async-safe rate limiter and abuse guardrails."""

from __future__ import annotations

import time
from collections import defaultdict, deque


class RateLimiter:
    """Sliding-window limiter keyed by client identity."""

    def __init__(self, limit_per_minute: int, unique_limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self.unique_limit_per_minute = unique_limit_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._unique_texts: dict[str, dict[str, float]] = defaultdict(dict)

    def allow(self, key: str, content_hash: str) -> bool:
        """Return True when request is allowed under abuse constraints."""

        now = time.time()
        self._trim(self._hits[key], now)
        if len(self._hits[key]) >= self.limit_per_minute:
            return False

        unique = self._unique_texts[key]
        unique = {k: ts for k, ts in unique.items() if now - ts < 60}
        self._unique_texts[key] = unique
        if content_hash not in unique and len(unique) >= self.unique_limit_per_minute:
            return False

        self._hits[key].append(now)
        unique[content_hash] = now
        return True

    @staticmethod
    def _trim(queue: deque[float], now: float) -> None:
        while queue and now - queue[0] >= 60:
            queue.popleft()
