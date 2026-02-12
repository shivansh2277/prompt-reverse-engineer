"""FastAPI application factory."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.server.api import router
from src.services.usage_hooks import UsageHookManager
from src.utils.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""

    settings = get_settings()
    configure_logging(settings.log_level)
    usage_hooks = UsageHookManager(
        per_user_quota_per_minute=settings.per_user_quota_per_minute,
        per_key_quota_per_minute=settings.per_key_quota_per_minute,
        billing_unit_chars=settings.billing_unit_chars,
    )

    app = FastAPI(
        title=settings.app_name,
        version="2.1.0",
        description="Analyze LLM outputs and reconstruct likely source prompts.",
    )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request.state.request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.started_at = time.perf_counter()

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_input_chars * 2:
            return JSONResponse(status_code=413, content={"detail": "payload_too_large"})

        user_id = request.headers.get("x-user-id", "anonymous")
        api_key_id = request.headers.get("x-api-key-id", "public")
        chars = int(content_length or 0)
        allowed, billing_units = usage_hooks.check_and_record(
            user_id=user_id,
            api_key_id=api_key_id,
            chars=chars,
            request_id=request.state.request_id,
        )
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "quota_exceeded"})

        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        response.headers["x-billing-units"] = str(billing_units)
        response.headers["x-usage-calls"] = str(usage_hooks.call_count)
        return response

    app.include_router(router)
    return app


app = create_app()
