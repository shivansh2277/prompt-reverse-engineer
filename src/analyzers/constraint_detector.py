"""Extract explicit and implicit constraints from generated text."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ConstraintSignal:
    """Signal emitted by constraint detector."""

    constraints: list[str]
    trace: str


class ConstraintDetector:
    """Detect constraints such as formatting, length, and style requirements."""

    PATTERNS = {
        "json_format": re.compile(r"json|\{\s*\".*\"\s*:\s*", re.IGNORECASE),
        "bullet_points": re.compile(r"^-\s|^\*\s", re.MULTILINE),
        "length_limit": re.compile(r"\b\d+\s*(words|sentences|characters)\b", re.IGNORECASE),
        "stepwise": re.compile(r"step\s*\d+|first[,\s]|second[,\s]", re.IGNORECASE),
        "no_fluff": re.compile(r"concise|brief|without fluff|only", re.IGNORECASE),
    }

    def analyze(self, text: str) -> ConstraintSignal:
        """Analyze text and return detected constraints."""

        hits = [name for name, pattern in self.PATTERNS.items() if pattern.search(text)]
        constraints = hits or ["none-explicit"]
        return ConstraintSignal(
            constraints=constraints,
            trace=f"constraint_hits={','.join(constraints)}",
        )
