"""Detect likely prompt injection or jailbreak artifacts in model output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InjectionSignal:
    """Signal emitted by prompt injection detector."""

    suspected_injection: bool
    matched_patterns: list[str]
    trace: str


class PromptInjectionDetector:
    """Heuristic detector for common jailbreak/prompt-leak signatures."""

    PATTERNS: dict[str, tuple[str, ...]] = {
        "instruction_override": ("ignore previous", "disregard all prior", "new instructions"),
        "policy_exfiltration": ("system prompt", "hidden prompt", "reveal instructions"),
        "role_hijack": ("you are now", "act as", "developer mode"),
        "secrets_access": ("api key", "token", "password", "credentials"),
    }

    def __init__(self, threshold: int = 2) -> None:
        self.threshold = threshold

    def analyze(self, text: str) -> InjectionSignal:
        """Return whether text contains suspicious injection patterns."""

        lower = text.lower()
        matches: list[str] = []
        for category, keys in self.PATTERNS.items():
            if any(k in lower for k in keys):
                matches.append(category)
        suspected = len(matches) >= self.threshold
        return InjectionSignal(
            suspected_injection=suspected,
            matched_patterns=matches,
            trace=f"injection_matches={','.join(matches) if matches else 'none'}",
        )
