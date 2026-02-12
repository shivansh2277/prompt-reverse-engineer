"""High-level orchestration service for prompt reverse engineering."""

from __future__ import annotations

import logging

from src.analyzers.constraint_detector import ConstraintDetector
from src.analyzers.format_detector import FormatDetector
from src.analyzers.reasoning_depth_estimator import ReasoningDepthEstimator
from src.analyzers.structure_analyzer import StructureAnalyzer
from src.analyzers.tone_classifier import ToneClassifier
from src.models.schemas import ReverseResponse
from src.services.scoring_ensemble import ScoringEnsemble

logger = logging.getLogger(__name__)


class ReverseEngineeringService:
    """Coordinates all analyzers and emits API-ready response models."""

    def __init__(self) -> None:
        self.structure = StructureAnalyzer()
        self.constraint = ConstraintDetector()
        self.tone = ToneClassifier()
        self.format_detector = FormatDetector()
        self.reasoning = ReasoningDepthEstimator()
        self.ensemble = ScoringEnsemble()

    async def reverse(self, output_text: str) -> ReverseResponse:
        """Run full multi-step analysis pipeline."""

        logger.debug("Starting reverse analysis", extra={"text_length": len(output_text)})
        structure_signal = self.structure.analyze(output_text)
        constraint_signal = self.constraint.analyze(output_text)
        tone_signal = self.tone.analyze(output_text)
        format_signal = self.format_detector.analyze(output_text)
        reasoning_signal = self.reasoning.analyze(output_text)

        merged = self.ensemble.merge(
            structure=structure_signal,
            constraints=constraint_signal,
            tone=tone_signal,
            fmt=format_signal,
            reasoning=reasoning_signal,
        )

        return ReverseResponse(**merged.model_dump())
