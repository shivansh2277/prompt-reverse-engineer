"""Optional OpenAI-compatible client layer for future model-assisted analysis."""

from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from src.config import Settings


class OpenAICompatibleClient:
    """Thin wrapper around OpenAI-compatible async chat completions."""

    def __init__(self, settings: Settings) -> None:
        self._enabled = bool(settings.openai_api_key)
        self._model = settings.openai_model
        self._client = (
            AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
            if self._enabled
            else None
        )

    @property
    def enabled(self) -> bool:
        """Whether external model calls are configured and available."""

        return self._enabled

    async def summarize(self, text: str) -> str:
        """Optionally summarize text; graceful fallback when not configured."""

        if not self._enabled or self._client is None:
            return "external_model_unavailable"

        response: Any = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "Summarize this output in one line for analysis metadata."},
                {"role": "user", "content": text[:4000]},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""
