"""API tests for prompt reverse engineer service."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import app


@pytest.mark.asyncio
async def test_health() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


@pytest.mark.asyncio
async def test_reverse_success_has_explainability_and_scores() -> None:
    sample = """1. First, define a Python function.
2. Then explain edge cases.
3. Output JSON with fields and confidence."""

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/reverse", json={"output_text": sample})

    assert response.status_code == 200
    payload = response.json()
    assert payload["inferred_prompt"]
    assert isinstance(payload["analyzer_scores"], dict)
    assert isinstance(payload["explainability"]["key_signals"], list)
    assert 0 <= payload["confidence_score"] <= 1


@pytest.mark.asyncio
async def test_reverse_batch_success() -> None:
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/reverse", json={"output_text": "too short"})

    assert response.status_code == 422
