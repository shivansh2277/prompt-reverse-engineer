"""TTL cache for repeated reverse engineering requests."""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Simple bounded TTL cache."""

    def __init__(self, ttl_seconds: int, max_entries: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._store: OrderedDict[str, tuple[float, T]] = OrderedDict()

    def get(self, key: str) -> T | None:
        now = time.time()
        entry = self._store.get(key)
        if entry is None:
            return None
        expiry, value = entry
        if now > expiry:
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: T) -> None:
        expiry = time.time() + self.ttl_seconds
        self._store[key] = (expiry, value)
        self._store.move_to_end(key)
        while len(self._store) > self.max_entries:
            self._store.popitem(last=False)
