"""FastAPI application factory."""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.server.api import router
from src.utils.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""

    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="Analyze LLM outputs and reconstruct likely source prompts.",
    )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request.state.request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.started_at = time.perf_counter()

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_input_chars * 2:
            return JSONResponse(status_code=413, content={"detail": "payload_too_large"})

        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        return response

    app.include_router(router)
    return app


app = create_app()
