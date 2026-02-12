"""Detect high-level structure and reconstruct probable prompt skeleton."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.models.schemas import PromptStyle


@dataclass
class StructureSignal:
    """Signal emitted by structure analyzer."""

    inferred_prompt: str
    prompt_style: PromptStyle
    task_type: str
    trace: str


class StructureAnalyzer:
    """Infer prompt structure and primary task from output text."""

    CODE_HINTS = ("```", "def ", "class ", "import ", "function", "algorithm")
    ESSAY_HINTS = ("introduction", "conclusion", "thesis", "paragraph")
    REASONING_HINTS = ("step", "therefore", "because", "let's", "first,")

    def analyze(self, text: str) -> StructureSignal:
        """Analyze generated text and infer likely upstream prompt frame."""

        lower = text.lower()
        is_template = bool(re.search(r"\{\{.*?\}\}|\[[A-Z_]+\]", text))
        role_based = "as an" in lower or "you are" in lower
        cot = any(h in lower for h in self.REASONING_HINTS) and len(text.splitlines()) > 4

        if is_template:
            prompt_style = PromptStyle.template
        elif role_based:
            prompt_style = PromptStyle.role_based
        elif cot:
            prompt_style = PromptStyle.chain_of_thought
        else:
            prompt_style = PromptStyle.instruction

        task_type = self._infer_task_type(lower)
        inferred_prompt = self._reconstruct_prompt(task_type, prompt_style)
        trace = f"style={prompt_style.value}, task_type={task_type}, template_markers={is_template}"
        return StructureSignal(
            inferred_prompt=inferred_prompt,
            prompt_style=prompt_style,
            task_type=task_type,
            trace=trace,
        )

    def _infer_task_type(self, lower_text: str) -> str:
        if any(h in lower_text for h in self.CODE_HINTS):
            return "code"
        if any(h in lower_text for h in self.ESSAY_HINTS):
            return "essay"
        if "explain" in lower_text or "overview" in lower_text:
            return "explanation"
        if any(h in lower_text for h in self.REASONING_HINTS):
            return "reasoning"
        return "general"

    @staticmethod
    def _reconstruct_prompt(task_type: str, style: PromptStyle) -> str:
        base = {
            "code": "Generate production-ready code with comments and edge-case handling.",
            "essay": "Write a structured essay with intro, body, and conclusion.",
            "explanation": "Explain the concept clearly for an intermediate audience.",
            "reasoning": "Solve the problem step-by-step and justify each conclusion.",
            "general": "Respond clearly and helpfully to the user request.",
        }[task_type]

        prefixes = {
            PromptStyle.instruction: "Instruction: ",
            PromptStyle.role_based: "Role: You are a domain expert. Task: ",
            PromptStyle.chain_of_thought: "Think step-by-step. Then answer. Task: ",
            PromptStyle.template: "Template: [ROLE] [TASK] [CONSTRAINTS]. Task: ",
        }

        return f"{prefixes[style]}{base}"
