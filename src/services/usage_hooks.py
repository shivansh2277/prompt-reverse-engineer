"""Marketplace usage metering, quota, and billing hook points."""

from __future__ import annotations

import time
from collections import defaultdict


class UsageHookManager:
    """In-memory hook manager for quota checks and usage metering.

    This implementation is intentionally thin and swappable for external
    marketplace billing providers.
    """

    def __init__(
        self,
        per_user_quota_per_minute: int,
        per_key_quota_per_minute: int,
        billing_unit_chars: int,
    ) -> None:
        self.per_user_quota_per_minute = per_user_quota_per_minute
        self.per_key_quota_per_minute = per_key_quota_per_minute
        self.billing_unit_chars = max(1, billing_unit_chars)
        self._user_hits: dict[str, list[float]] = defaultdict(list)
        self._key_hits: dict[str, list[float]] = defaultdict(list)
        self._usage_log: list[dict[str, str | int | float]] = []

    def check_and_record(self, user_id: str, api_key_id: str, chars: int, request_id: str) -> tuple[bool, int]:
        """Check quotas and return allowed flag plus billing units for this request."""

        now = time.time()
        self._trim(self._user_hits[user_id], now)
        self._trim(self._key_hits[api_key_id], now)

        if len(self._user_hits[user_id]) >= self.per_user_quota_per_minute:
            return False, 0
        if len(self._key_hits[api_key_id]) >= self.per_key_quota_per_minute:
            return False, 0

        self._user_hits[user_id].append(now)
        self._key_hits[api_key_id].append(now)

        units = max(1, (chars + self.billing_unit_chars - 1) // self.billing_unit_chars)
        self._usage_log.append(
            {
                "request_id": request_id,
                "user_id": user_id,
                "api_key_id": api_key_id,
                "billing_units": units,
                "chars": chars,
                "timestamp": now,
            }
        )
        return True, units

    @property
    def call_count(self) -> int:
        """Return total metered calls."""

        return len(self._usage_log)

    @staticmethod
    def _trim(items: list[float], now: float) -> None:
        valid = [t for t in items if now - t < 60]
        items[:] = valid
