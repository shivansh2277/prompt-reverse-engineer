# Architecture

## Overview

`Prompt Reverse Engineer` is a layered FastAPI application with deterministic analyzers and ensemble scoring.

```text
API Router -> ReverseEngineeringService -> Analyzer Modules -> ScoringEnsemble -> Response Model
```

## Modules

- `src/server/api.py`: REST endpoints and HTTP error mapping.
- `src/services/reverse_engineering_service.py`: orchestration and pipeline execution.
- `src/analyzers/*.py`: focused analysis components.
- `src/services/scoring_ensemble.py`: confidence synthesis and final merge.
- `src/models/schemas.py`: strict request/response contracts.
- `src/client/openai_compatible.py`: optional OpenAI-compatible integration layer.
- `src/config.py`: dotenv/env driven settings.

## Defensive Design

- Schema validation with min lengths and bounded list sizes.
- Character and batch guards to prevent oversized payloads.
- Graceful exception handling with logged stack traces.
- Pure analyzer classes for easy unit testing.

## Extensibility

You can add model-assisted analysis by injecting `OpenAICompatibleClient` into the service layer and using `summarize()` or custom methods to enrich ensemble features.
