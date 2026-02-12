"""Detect response formatting patterns used by the model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FormatSignal:
    """Signal emitted by format detector."""

    format_markers: list[str]
    trace: str


class FormatDetector:
    """Inspect output for canonical LLM formatting signatures."""

    def analyze(self, text: str) -> FormatSignal:
        """Return detected formatting signatures."""

        markers: list[str] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if "```" in text:
            markers.append("markdown_code_block")
        if any(line.startswith(("- ", "* ")) for line in lines):
            markers.append("bullet_list")
        if any(line[:2].isdigit() and line[2:3] in (".", ")") for line in lines if len(line) >= 3):
            markers.append("numbered_steps")
        if "{" in text and "}" in text and '"' in text:
            markers.append("json_like")
        if not markers:
            markers.append("plain_text")

        return FormatSignal(markers, trace=f"format_markers={','.join(markers)}")
