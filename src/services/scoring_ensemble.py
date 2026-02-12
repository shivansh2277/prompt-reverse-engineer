"""Ensemble logic to merge analyzer signals into one response."""

from __future__ import annotations

from src.analyzers.constraint_detector import ConstraintSignal
from src.analyzers.format_detector import FormatSignal
from src.analyzers.reasoning_depth_estimator import ReasoningSignal
from src.analyzers.structure_analyzer import StructureSignal
from src.analyzers.tone_classifier import ToneSignal
from src.models.schemas import AnalyzerSignals


class ScoringEnsemble:
    """Combine independent analyzer outputs into a cohesive prediction."""

    def merge(
        self,
        structure: StructureSignal,
        constraints: ConstraintSignal,
        tone: ToneSignal,
        fmt: FormatSignal,
        reasoning: ReasoningSignal,
    ) -> AnalyzerSignals:
        """Merge analyzer outputs and compute confidence score."""

        confidence = self._confidence(constraints, fmt, reasoning)
        trace = [
            structure.trace,
            constraints.trace,
            tone.trace,
            fmt.trace,
            reasoning.trace,
            f"confidence={confidence:.2f}",
        ]

        return AnalyzerSignals(
            inferred_prompt=structure.inferred_prompt,
            prompt_style=structure.prompt_style,
            task_type=structure.task_type,
            constraints_detected=constraints.constraints,
            temperature_estimate=tone.temperature,
            reasoning_trace=trace,
            confidence_score=confidence,
        )

    @staticmethod
    def _confidence(
        constraints: ConstraintSignal,
        fmt: FormatSignal,
        reasoning: ReasoningSignal,
    ) -> float:
        base = 0.45
        base += 0.12 if constraints.constraints and constraints.constraints[0] != "none-explicit" else -0.05
        base += 0.1 if "plain_text" not in fmt.format_markers else 0.02
        base += min(reasoning.depth_score * 0.35, 0.25)
        return round(max(0.05, min(base, 0.99)), 2)
