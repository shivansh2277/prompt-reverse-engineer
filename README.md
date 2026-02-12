# Prompt Reverse Engineer

Production-grade AI agent/API that infers likely prompt structures from model-generated outputs.

## Core output fields

- inferred_prompt
- prompt_style
- task_type
- constraints_detected
- temperature_estimate
- reasoning_trace
- analyzer_scores
- explainability
- confidence_score

## Production upgrades

### Security
- Request rate limiting and abuse guardrails.
- Payload size guards and strict schema validation.
- Prompt injection detection heuristics.
- Safe structured logging without raw secret leakage.

### Observability
- Structured JSON logs.
- Request IDs (`x-request-id`).
- Endpoint timing metrics.
- Analyzer scoring breakdown for traceability.

### Scalability
- Stateless API design.
- Async endpoints and service pipeline.
- Batch processing endpoint.
- TTL cache for repeated outputs.

### Quality controls
- Confidence calibration in ensemble scoring.
- Explainability section per response.
- Deterministic mode toggle and reproducibility seed.
- Model/temperature config knobs via `.env`.

## Endpoints
- `GET /health`
- `POST /reverse`
- `POST /reverse/batch`

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Example request
```bash
curl -X POST http://localhost:8000/reverse \
  -H "Content-Type: application/json" \
  -d '{
    "output_text": "Step 1: Think through constraints. Step 2: return JSON.",
    "deterministic": true,
    "seed": 1337
  }'
```

## Example response (strict JSON)
```json
{
  "request_id": "f6c9...",
  "cached": false,
  "inferred_prompt": "Think step-by-step. Then answer. Task: ...",
  "prompt_style": "chain-of-thought",
  "task_type": "reasoning",
  "constraints_detected": ["json_format", "stepwise"],
  "temperature_estimate": "medium",
  "reasoning_trace": ["..."],
  "analyzer_scores": {
    "structure": 0.8,
    "constraint": 0.6,
    "tone": 0.6,
    "format": 0.8,
    "reasoning_depth": 0.3,
    "injection_safety": 0.9
  },
  "explainability": {
    "summary": "Detected chain-of-thought style...",
    "key_signals": ["..."],
    "risk_flags": ["none"]
  },
  "confidence_score": 0.77
}
```

## Tooling scripts
```bash
python scripts/generate_synthetic_dataset.py
python scripts/evaluate.py
python scripts/benchmark.py
python scripts/build.py
```

## Docker
```bash
docker build -t prompt-reverse-engineer .
docker run --rm -p 8000:8000 --env-file .env prompt-reverse-engineer
```

## Marketplace Packaging (MuleRun-style)

### Who this is for
- AI builders shipping prompt-heavy workflows.
- Teams needing explainable post-hoc prompt diagnostics.
- Marketplace operators requiring usage hooks and quota control.

### When to use
- You need quick probabilistic prompt reconstruction from generated outputs.
- You need operational metadata (request IDs, confidence, analyzer scoring).
- You need wrapper-level invoke interfaces for embedding in agent platforms.

### When not to use
- You require exact or legally authoritative prompt recovery.
- You need forensic-grade attribution across unknown multi-model pipelines.
- You need guarantees against all adversarial outputs.

### Competitive positioning
- Lightweight, deployment-friendly FastAPI core.
- Explainability-rich outputs with analyzer score breakdown.
- Built-in marketplace extension points: quotas, billing units, usage metering, and manifest metadata.

### Benchmarks summary
- Use `scripts/benchmark.py` for p50/p95 latency and request throughput checks in your target runtime.
- Use `scripts/evaluate.py` for confidence/risk aggregate metrics on synthetic and curated datasets.

### Example workflows
1. Route LLM outputs to `/reverse` for prompt diagnostics in CI.
2. Meter usage through headers (`x-user-id`, `x-api-key-id`) and middleware quota hooks.
3. Surface `explainability` + `confidence_score` in trust dashboards.
4. Package for marketplace ingestion using `agent_manifest.json`, `demo_requests.json`, and `demo_outputs.json`.
