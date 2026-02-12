"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from src.config import get_settings
from src.server.api import router
from src.utils.logging import configure_logging
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""

    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Analyze LLM outputs and reconstruct likely source prompts.",
    )

# --- ADD THIS BLOCK ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# ----------------------

    app.include_router(router)
    return app


app = create_app()
