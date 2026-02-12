"""API tests for prompt reverse engineer service."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app


@pytest.mark.asyncio
async def test_health() -> None:
    """Health endpoint should return service metadata."""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "app" in payload


@pytest.mark.asyncio
async def test_reverse_success() -> None:
    """Reverse endpoint should produce required keys."""

    sample = """1. First, define a Python function.
2. Then explain edge cases.
3. Output JSON with fields and confidence."""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/reverse", json={"output_text": sample})

    assert response.status_code == 200
    payload = response.json()
    assert payload["inferred_prompt"]
    assert payload["prompt_style"]
    assert payload["task_type"] in {"code", "reasoning", "explanation", "essay", "general"}
    assert 0 <= payload["confidence_score"] <= 1


@pytest.mark.asyncio
async def test_reverse_batch_success() -> None:
    """Batch endpoint should process multiple items."""

    req = {
        "items": [
            {"output_text": "Explain photosynthesis in three bullet points and be concise."},
            {"output_text": "You are a senior engineer. Provide code with tests and comments."},
        ]
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/reverse/batch", json=req)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) == 2


@pytest.mark.asyncio
async def test_validation_guard_for_input_length() -> None:
    """Input guard should reject too-short payloads based on schema constraints."""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/reverse", json={"output_text": "too short"})

    assert response.status_code == 422
