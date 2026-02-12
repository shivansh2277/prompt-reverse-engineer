"""API routes for prompt reverse engineering."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from src.config import get_settings
from src.models.schemas import (
    BatchReverseRequest,
    BatchReverseResponse,
    HealthResponse,
    ReverseRequest,
    ReverseResponse,
)
from src.services.reverse_engineering_service import ReverseEngineeringService

logger = logging.getLogger(__name__)
router = APIRouter()
service = ReverseEngineeringService()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health metadata."""

    settings = get_settings()
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


@router.post("/reverse", response_model=ReverseResponse)
async def reverse(request: ReverseRequest) -> ReverseResponse:
    """Reverse engineer a likely prompt from one model output."""

    try:
        return await service.reverse(request.output_text)
    except Exception as exc:  # defensive catch for graceful failure
        logger.exception("Failed to reverse engineer prompt")
        raise HTTPException(status_code=500, detail="reverse_engineering_failed") from exc


@router.post("/reverse/batch", response_model=BatchReverseResponse)
async def reverse_batch(request: BatchReverseRequest) -> BatchReverseResponse:
    """Reverse engineer prompts for a batch of outputs."""

    try:
        results = [await service.reverse(item.output_text) for item in request.items]
        return BatchReverseResponse(results=results)
    except Exception as exc:  # defensive catch for graceful failure
        logger.exception("Batch reverse engineering failed")
        raise HTTPException(status_code=500, detail="batch_reverse_engineering_failed") from exc
