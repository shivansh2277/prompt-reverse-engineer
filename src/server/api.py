"""API routes for prompt reverse engineering."""

from __future__ import annotations

import hashlib
import logging
import time

from fastapi import APIRouter, HTTPException, Request

from src.config import get_settings
from src.models.schemas import (
    BatchReverseRequest,
    BatchReverseResponse,
    HealthResponse,
    ReverseRequest,
    ReverseResponse,
)
from src.services.cache import TTLCache
from src.services.metrics import MetricsRegistry
from src.services.rate_limiter import RateLimiter
from src.services.reverse_engineering_service import ReverseEngineeringService

logger = logging.getLogger(__name__)
router = APIRouter()
service = ReverseEngineeringService()
settings = get_settings()
rate_limiter = RateLimiter(settings.max_requests_per_minute, settings.max_unique_texts_per_minute)
cache = TTLCache[ReverseResponse](settings.cache_ttl_seconds, settings.cache_max_entries)
metrics = MetricsRegistry()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


@router.post("/reverse", response_model=ReverseResponse)
async def reverse(request: ReverseRequest, http_request: Request) -> ReverseResponse:
    started = time.perf_counter()
    request_id = getattr(http_request.state, "request_id", "unknown")
    client_key = (http_request.client.host if http_request.client else "unknown")
    content_hash = _hash(request.output_text)

    if not rate_limiter.allow(client_key, content_hash):
        raise HTTPException(status_code=429, detail="rate_limit_exceeded")

    cached_item = cache.get(content_hash)
    if cached_item is not None:
        elapsed = metrics.track("/reverse", started)
        logger.info(
            "reverse_processed",
            extra={"request_id": request_id, "path": "/reverse", "duration_ms": round(elapsed, 2), "cache_hit": True},
        )
        return cached_item.model_copy(update={"request_id": request_id, "cached": True})

    deterministic = settings.deterministic_default if request.deterministic is None else request.deterministic
    try:
        response = await service.reverse(
            output_text=request.output_text,
            request_id=request_id,
            deterministic=deterministic,
            seed=request.seed,
            cached=False,
        )
        cache.set(content_hash, response)
        elapsed = metrics.track("/reverse", started)
        logger.info(
            "reverse_processed",
            extra={"request_id": request_id, "path": "/reverse", "duration_ms": round(elapsed, 2), "cache_hit": False},
        )
        return response
    except Exception as exc:
        logger.exception("reverse_failed", extra={"request_id": request_id, "path": "/reverse"})
        raise HTTPException(status_code=500, detail="reverse_engineering_failed") from exc


@router.post("/reverse/batch", response_model=BatchReverseResponse)
async def reverse_batch(request: BatchReverseRequest, http_request: Request) -> BatchReverseResponse:
    started = time.perf_counter()
    request_id = getattr(http_request.state, "request_id", "unknown")
    try:
        results: list[ReverseResponse] = []
        for item in request.items:
            deterministic = settings.deterministic_default if item.deterministic is None else item.deterministic
            content_hash = _hash(item.output_text)
            cached_item = cache.get(content_hash)
            if cached_item is not None:
                results.append(cached_item.model_copy(update={"request_id": request_id, "cached": True}))
                continue
            response = await service.reverse(
                output_text=item.output_text,
                request_id=request_id,
                deterministic=deterministic,
                seed=item.seed,
                cached=False,
            )
            cache.set(content_hash, response)
            results.append(response)

        elapsed = metrics.track("/reverse/batch", started)
        logger.info(
            "reverse_batch_processed",
            extra={"request_id": request_id, "path": "/reverse/batch", "duration_ms": round(elapsed, 2)},
        )
        return BatchReverseResponse(results=results)
    except Exception as exc:
        logger.exception("reverse_batch_failed", extra={"request_id": request_id, "path": "/reverse/batch"})
        raise HTTPException(status_code=500, detail="batch_reverse_engineering_failed") from exc
