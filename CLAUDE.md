# CLAUDE.md - Athena (Curriculum & Knowledge Service)

**Last Updated:** April 2026

## Overview

Athena is the curriculum and knowledge orchestrator for the MedEd platform. It centralizes all medical condition definitions, teaching frameworks, specialty metadata, and learner track definitions, serving them via REST API to other MedEd services (Oread, Echo, Syrinx, Mneme).

Named after the Greek goddess of wisdom — Athena knows *what to teach* while other services know *how to teach it*.

## Quick Start

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/athena
source .venv/bin/activate
cd /Users/dochobbs/Downloads/Consult/MedEd
PYTHONPATH=. uvicorn athena.src.main:app --host 0.0.0.0 --port 9105 --reload
```

## Tech Stack

- Python 3.11+, FastAPI, Pydantic v2, PyYAML
- Port: 9105
- All routes prefixed with `/api/`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check with loaded knowledge counts |
| GET | `/api/conditions` | List conditions (filters: specialty, age_months, level, system) |
| GET | `/api/conditions/{id}` | Get single condition |
| GET | `/api/frameworks` | List frameworks (filters: specialty, category) |
| GET | `/api/frameworks/{id}` | Get single framework |
| GET | `/api/frameworks/for-condition/{id}?specialty=` | Framework for a specific condition in specialty context |
| GET | `/api/specialties` | List all specialties |
| GET | `/api/specialties/{id}` | Get specialty detail |
| GET | `/api/learner-tracks` | List learner tracks (filters: specialty, level) |
| GET | `/api/disease-arcs` | List disease arcs (filter: specialty) |
| GET | `/api/disease-arcs/{id}` | Get single disease arc |
| GET | `/api/immunizations` | List immunizations (filter: age_months) |

## Knowledge Structure

```
knowledge/
├── specialties/          # pediatrics.yaml, internal_medicine.yaml, family_practice.yaml
├── conditions/
│   ├── shared/           # Conditions spanning peds + IM (asthma, UTI, etc.)
│   ├── peds/             # Peds-only conditions (croup, bronchiolitis, etc.)
│   └── im/               # IM-only conditions (COPD, CHF, etc.)
├── frameworks/
│   ├── shared/
│   ├── peds/
│   └── im/
├── disease_arcs/
│   ├── peds/
│   └── im/
├── immunizations/
├── growth/
└── learner_tracks/       # medical_student.yaml, resident.yaml, np_student.yaml
```

## Specialty Model

- **Pediatrics**: knowledge pools = [peds, shared], age 0-18
- **Internal Medicine**: knowledge pools = [im, shared], age 18+
- **Family Practice**: knowledge pools = [peds, im, shared], all ages

FP is not a separate knowledge base — it's a resolver mode that queries both pools.

## Key Architecture

| Module | File | Purpose |
|--------|------|---------|
| Config | `src/config.py` | Pydantic BaseSettings with env vars |
| Models | `src/models.py` | All Pydantic schemas |
| Loader | `src/loader.py` | YAML → Pydantic, directory scanning |
| Resolver | `src/resolver.py` | Specialty + age + level filtering |
| Deps | `src/deps.py` | Shared store/resolver singletons |
| Client | `client/athena_client.py` | HTTP client for other services |

## AthenaClient (For Other Services)

```python
from athena.client.athena_client import AthenaClient

client = AthenaClient(base_url="http://localhost:9105")
conditions = await client.get_conditions(specialty="pediatrics", age_months=36)
framework = await client.get_framework_for_condition("asthma", specialty="pediatrics")
```

Falls back gracefully if Athena is unreachable — returns empty lists or None.

## Testing

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd
source athena/.venv/bin/activate
PYTHONPATH=. pytest athena/tests/ -v
```

## Code Conventions

- 2 spaces indentation (project standard)
- Type hints on all functions
- Pydantic v2 models with `model_dump(exclude_none=True)`
- Google-style docstrings
- YAML files use snake_case keys
