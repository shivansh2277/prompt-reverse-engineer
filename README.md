# Prompt Reverse Engineer

Production-grade AI agent that infers likely prompt structures from model-generated output text.

## What it does

Given raw LLM output, the service predicts:

- `inferred_prompt`
- `prompt_style` (`instruction`, `role-based`, `chain-of-thought`, `template`)
- `task_type` (`code`, `essay`, `explanation`, `reasoning`, `general`)
- `constraints_detected`
- `temperature_estimate` (`low`, `medium`, `high`)
- `reasoning_trace`
- `confidence_score` (0 to 1)

## Architecture

The service uses a modular, multi-step analysis pipeline:

1. linguistic pattern detection (`StructureAnalyzer`)
2. constraint extraction (`ConstraintDetector`)
3. tone detection (`ToneClassifier`)
4. instruction/format fingerprinting (`FormatDetector`)
5. reasoning depth estimation (`ReasoningDepthEstimator`)
6. ensemble scoring merge (`ScoringEnsemble`)

See `docs/architecture.md` for details.

## Tech stack

- Python 3.11
- FastAPI
- Pydantic v2 models
- Async endpoints/services
- OpenAI-compatible async client layer
- dotenv-based config
- pytest
- Docker

## Project structure

```text
src/
  analyzers/
  client/
  models/
  server/
  services/
  utils/
  app.py
  main.py
tests/
Dockerfile
requirements.txt
```

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API

### `GET /health`
Health check.

### `POST /reverse`
Request:

```json
{
  "output_text": "1. First define assumptions. 2. Then provide code in JSON format."
}
```

Response (strict JSON):

```json
{
  "inferred_prompt": "Think step-by-step. Then answer. Task: Generate production-ready code with comments and edge-case handling.",
  "prompt_style": "chain-of-thought",
  "task_type": "code",
  "constraints_detected": ["json_format", "stepwise"],
  "temperature_estimate": "medium",
  "reasoning_trace": [
    "style=chain-of-thought, task_type=code, template_markers=false",
    "constraint_hits=json_format,stepwise"
  ],
  "confidence_score": 0.73
}
```

### `POST /reverse/batch`
Request:

```json
{
  "items": [
    {"output_text": "Explain this topic in 3 bullet points."},
    {"output_text": "You are a senior reviewer. Provide concise feedback."}
  ]
}
```

Returns:

```json
{
  "results": [
    {
      "inferred_prompt": "...",
      "prompt_style": "instruction",
      "task_type": "explanation",
      "constraints_detected": ["bullet_points"],
      "temperature_estimate": "low",
      "reasoning_trace": ["..."],
      "confidence_score": 0.69
    }
  ]
}
```

## Testing

```bash
pytest -q
```

## Docker

```bash
docker build -t prompt-reverse-engineer .
docker run --rm -p 8000:8000 --env-file .env prompt-reverse-engineer
```

## Notes

- Input guards protect token/character overload via `max_input_chars` and batch limits.
- Failures return graceful HTTP errors and log context.
