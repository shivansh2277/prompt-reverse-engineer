# Model Card — Prompt Reverse Engineer Agent

## Overview
Prompt Reverse Engineer is an analysis agent that infers likely prompt structure from AI-generated output text.

## Intended Users
- AI product teams
- Prompt engineers
- QA / evaluation teams
- Marketplace integrators

## Intended Uses
- Prompt diagnostics
- Output auditability and explainability
- Prompt-style classification and constraints discovery

## Out-of-Scope Uses
- Exact attribution of proprietary prompts
- Security bypass or model jailbreak generation
- Legal proof of prompt origin

## Inputs / Outputs
- Input: raw LLM output text (+ optional deterministic/seed controls)
- Output: inferred prompt, style/task labels, constraints, temperature estimate, reasoning trace, analyzer scores, explainability, confidence score

## Safety Features
- Prompt injection pattern detection
- Rate limits and quota hooks
- Structured logging and request IDs

## Risks
- False confidence in inferred prompts
- Misinterpretation of heuristic scores
- Domain-shift performance degradation

## Evaluation Notes
Use `scripts/generate_dataset.py`, `scripts/evaluate.py`, and `scripts/benchmark.py` to reproduce baseline operational checks.
