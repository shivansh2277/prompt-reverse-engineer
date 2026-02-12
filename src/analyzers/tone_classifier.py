"""Classify tone and infer likely temperature from output variance."""

from __future__ import annotations

from dataclasses import dataclass

from src.models.schemas import TemperatureEstimate


@dataclass
class ToneSignal:
    """Signal emitted by tone classifier."""

    tone: str
    temperature: TemperatureEstimate
    trace: str


class ToneClassifier:
    """Estimate output tone and likely sampling temperature."""

    def analyze(self, text: str) -> ToneSignal:
        """Analyze output tone and estimate temperature."""

        lower = text.lower()
        exclamations = text.count("!")
        hedging = sum(lower.count(w) for w in ("maybe", "might", "possibly", "could"))
        formal = sum(lower.count(w) for w in ("therefore", "moreover", "hence", "in summary"))

        if exclamations >= 3 or hedging >= 4:
            temperature = TemperatureEstimate.high
            tone = "creative"
        elif formal >= 3:
            temperature = TemperatureEstimate.low
            tone = "formal"
        else:
            temperature = TemperatureEstimate.medium
            tone = "neutral"

        trace = f"tone={tone}, exclamations={exclamations}, hedging={hedging}, formal={formal}"
        return ToneSignal(tone=tone, temperature=temperature, trace=trace)
