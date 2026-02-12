# Architecture

## System

```text
Client -> FastAPI Router -> ReverseEngineeringService -> Analyzer Pipeline -> ScoringEnsemble
                     |-> RateLimiter
                     |-> TTL Cache
                     |-> Request-ID + Timing Middleware
```

## Security controls
- Input length and batch-size validation in Pydantic models.
- Payload size guard in HTTP middleware.
- Per-client rate limiting + unique-content abuse guard.
- Prompt injection detector analyzer with risk flags.
- Safe structured logs (no raw secrets).

## Observability
- JSON structured logs.
- `x-request-id` propagation.
- Timing metrics registry by endpoint.
- Analyzer-level scoring and trace outputs.

## Scalability and reliability
- Stateless API endpoints.
- Async handlers.
- Batch endpoint for throughput.
- Bounded TTL cache for repeat workloads.

## Quality controls
- Confidence calibration in ensemble scorer.
- Explainability object in output.
- Deterministic mode + optional seed for reproducibility.
- `.env` driven model selection and temperature override knobs.
