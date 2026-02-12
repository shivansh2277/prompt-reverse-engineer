"""Estimate how deep the hidden reasoning process likely was."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReasoningSignal:
    """Signal emitted by reasoning depth estimator."""

    depth_score: float
    trace: str


class ReasoningDepthEstimator:
    """Approximate reasoning depth using linguistic proxies."""

    CONNECTORS = ("because", "therefore", "however", "if", "then", "thus", "so that")

    def analyze(self, text: str) -> ReasoningSignal:
        """Return a normalized reasoning depth score from 0 to 1."""

        words = max(len(text.split()), 1)
        connectors = sum(text.lower().count(c) for c in self.CONNECTORS)
        multiline_steps = sum(1 for line in text.splitlines() if line.strip().startswith(tuple("123456789")))
        raw = connectors * 0.08 + multiline_steps * 0.1 + min(words / 1500, 0.25)
        depth = max(0.0, min(raw, 1.0))
        return ReasoningSignal(depth_score=depth, trace=f"connectors={connectors}, steps={multiline_steps}")
