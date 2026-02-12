"""Thin marketplace-facing wrapper exposing sync + async invoke interfaces."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Any

from src.config import get_settings
from src.services.reverse_engineering_service import ReverseEngineeringService


@dataclass
class UsageMeter:
    """Basic call + token estimation meter."""

    call_counter: int = 0
    token_estimate_total: int = 0

    def record(self, text: str) -> dict[str, int]:
        self.call_counter += 1
        estimated_tokens = max(1, len(text) // 4)
        self.token_estimate_total += estimated_tokens
        return {
            "call_counter": self.call_counter,
            "estimated_tokens": estimated_tokens,
            "estimated_tokens_total": self.token_estimate_total,
        }


class PromptReverseEngineerAgent:
    """Single-callable agent wrapper for marketplace integrations."""

    def __init__(self) -> None:
        self.service = ReverseEngineeringService()
        self.settings = get_settings()
        self.usage_meter = UsageMeter()

    async def invoke_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Async invoke entrypoint with structured error responses."""

        try:
            output_text = str(payload.get("output_text", "")).strip()
            if not output_text:
                return {"ok": False, "error": {"code": "validation_error", "message": "output_text is required"}}

            deterministic = bool(payload.get("deterministic", self.settings.deterministic_default))
            seed = payload.get("seed")
            request_id = str(payload.get("request_id", uuid.uuid4()))

            result = await self.service.reverse(
                output_text=output_text,
                request_id=request_id,
                deterministic=deterministic,
                seed=seed if isinstance(seed, int) else None,
            )

            usage = self.usage_meter.record(output_text)
            return {"ok": True, "data": result.model_dump(), "usage": usage}
        except Exception as exc:  # defensive wrapper boundary
            return {
                "ok": False,
                "error": {"code": "invoke_failed", "message": str(exc)},
            }

    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Synchronous invoke entrypoint."""

        return asyncio.run(self.invoke_async(payload))
