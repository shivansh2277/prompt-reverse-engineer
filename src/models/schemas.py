"""Pydantic models for API contracts and internal analyzer output."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

from src.config import get_settings


class PromptStyle(str, Enum):
    instruction = "instruction"
    role_based = "role-based"
    chain_of_thought = "chain-of-thought"
    template = "template"


class TemperatureEstimate(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ReverseRequest(BaseModel):
    """Single reverse engineering request."""

    output_text: str = Field(..., min_length=20, description="Raw text produced by an LLM.")
    deterministic: bool | None = Field(default=None)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)

    @field_validator("output_text")
    @classmethod
    def validate_text_length(cls, value: str) -> str:
        max_chars = get_settings().max_input_chars
        if len(value) > max_chars:
            raise ValueError(f"output_text exceeds max length of {max_chars} characters")
        return value.strip()


class BatchReverseRequest(BaseModel):
    items: List[ReverseRequest] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def validate_batch_size(cls, value: List[ReverseRequest]) -> List[ReverseRequest]:
        max_batch = get_settings().max_batch_items
        if len(value) > max_batch:
            raise ValueError(f"batch size exceeds limit of {max_batch}")
        return value


class Explainability(BaseModel):
    """Human-readable explanations for marketplace trust and auditability."""

    summary: str
    key_signals: List[str]
    risk_flags: List[str]


class AnalyzerSignals(BaseModel):
    inferred_prompt: str
    prompt_style: PromptStyle
    task_type: str
    constraints_detected: List[str]
    temperature_estimate: TemperatureEstimate
    reasoning_trace: List[str]
    analyzer_scores: Dict[str, float]
    explainability: Explainability
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ReverseResponse(AnalyzerSignals):
    request_id: str
    cached: bool = False


class BatchReverseResponse(BaseModel):
    results: List[ReverseResponse]


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
