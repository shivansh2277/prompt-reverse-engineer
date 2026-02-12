"""Ensemble logic to merge analyzer signals into one response."""

from __future__ import annotations

from src.analyzers.constraint_detector import ConstraintSignal
from src.analyzers.format_detector import FormatSignal
from src.analyzers.prompt_injection_detector import InjectionSignal
from src.analyzers.reasoning_depth_estimator import ReasoningSignal
from src.analyzers.structure_analyzer import StructureSignal
from src.analyzers.tone_classifier import ToneSignal
from src.models.schemas import AnalyzerSignals, Explainability


class ScoringEnsemble:
    """Combine independent analyzer outputs into a cohesive prediction."""

    def merge(
        self,
        structure: StructureSignal,
        constraints: ConstraintSignal,
        tone: ToneSignal,
        fmt: FormatSignal,
        reasoning: ReasoningSignal,
        injection: InjectionSignal,
    ) -> AnalyzerSignals:
        confidence = self._confidence(constraints, fmt, reasoning, injection)
        analyzer_scores = {
            "structure": 0.8 if structure.task_type != "general" else 0.55,
            "constraint": min(0.3 + len(constraints.constraints) * 0.15, 0.95),
            "tone": 0.75 if tone.tone != "neutral" else 0.6,
            "format": 0.8 if "plain_text" not in fmt.format_markers else 0.55,
            "reasoning_depth": round(reasoning.depth_score, 2),
            "injection_safety": 0.25 if injection.suspected_injection else 0.9,
        }
        trace = [
            structure.trace,
            constraints.trace,
            tone.trace,
            fmt.trace,
            reasoning.trace,
            injection.trace,
            f"confidence={confidence:.2f}",
        ]

        explainability = Explainability(
            summary=(
                f"Detected {structure.prompt_style.value} style and {structure.task_type} task with "
                f"{len(constraints.constraints)} constraint signals."
            ),
            key_signals=[structure.trace, constraints.trace, fmt.trace],
            risk_flags=injection.matched_patterns or ["none"],
        )

        return AnalyzerSignals(
            inferred_prompt=structure.inferred_prompt,
            prompt_style=structure.prompt_style,
            task_type=structure.task_type,
            constraints_detected=constraints.constraints,
            temperature_estimate=tone.temperature,
            reasoning_trace=trace,
            analyzer_scores=analyzer_scores,
            explainability=explainability,
            confidence_score=confidence,
        )

    @staticmethod
    def _confidence(
        constraints: ConstraintSignal,
        fmt: FormatSignal,
        reasoning: ReasoningSignal,
        injection: InjectionSignal,
    ) -> float:
        base = 0.48
        base += 0.12 if constraints.constraints and constraints.constraints[0] != "none-explicit" else -0.04
        base += 0.1 if "plain_text" not in fmt.format_markers else 0.03
        base += min(reasoning.depth_score * 0.35, 0.23)
        if injection.suspected_injection:
            base -= 0.35
        calibrated = 1 / (1 + pow(2.71828, -4 * (base - 0.5)))
        return round(max(0.03, min(calibrated, 0.99)), 2)
