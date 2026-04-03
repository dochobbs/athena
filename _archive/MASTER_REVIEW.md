# MedEd Platform Master Review

**Prepared by:** Claude (Project Coordinator)
**Date:** December 29, 2025
**Last Updated:** December 29, 2025

This document provides a comprehensive analysis of the MedEd platform, including all five sub-projects: **Metis** (orchestration), Oread, Syrinx, Mneme, and Echo.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Status Overview](#2-project-status-overview)
3. [Git Repository Analysis](#3-git-repository-analysis)
4. [Port Configuration Issues](#4-port-configuration-issues)
5. [Design Consistency Analysis](#5-design-consistency-analysis)
6. [Code Consistency Analysis](#6-code-consistency-analysis)
7. [Shared Code Opportunities](#7-shared-code-opportunities)
8. [Recommendations](#8-recommendations)
9. [Action Items](#9-action-items)

---

## 1. Executive Summary

### Platform Health: 8.5/10 (Up from 7.1)

The MedEd platform now consists of five well-integrated microservices with **Metis** providing orchestration and model sync:

| Finding | Status | Resolution |
|---------|--------|------------|
| Port conflicts between projects | **RESOLVED** | Standardized: Oread=8004, Syrinx=8003, Mneme=8002, Echo=8001 |
| Mneme frontend misconfigured proxy | **RESOLVED** | Updated to target localhost:8002 |
| No shared models package | **RESOLVED** | Metis sync.py generates models from JSON Schemas |
| Syrinx uses outdated anthropic | **RESOLVED** | Updated to >=0.40.0 |
| Missing git repo for Mneme | **RESOLVED** | User created dedicated repo |
| Syrinx lacks Pydantic models | **MEDIUM** | Still uses raw dictionaries |
| Inconsistent dependency versions | **MEDIUM** | Potential runtime incompatibilities |
| Oread server.py is 500+ lines | **MEDIUM** | Maintainability concern |

### What's New: Metis (December 29, 2025)

Metis is now the parent project for the MedEd ecosystem:

```bash
# Start all services
cd metis/scripts && ./start-all.sh

# Sync shared models
cd metis/shared && python sync.py --project all

# Check model sync status
python sync.py --validate
```

### Symlinks Created

```
oread  -> synpat
syrinx -> synvoice
mneme  -> synchart
```

---

## 2. Project Status Overview

| Project | Directory | Port | Maturity | Key Features |
|---------|-----------|------|----------|--------------|
| **Metis** | metis/ | 3000 | New | Orchestration, model sync, shell scripts |
| **Oread** | synpat/ | 8004 | Production | Time Travel, Panels, Messiness, FHIR/C-CDA |
| **Syrinx** | synvoice/ | 8003 | Production | Script gen, Error injection, Audio |
| **Mneme** | synchart/ | 8002 | Early Dev | Import, Patient list/detail |
| **Echo** | echo/ | 8001 | Early Dev | Socratic tutor structure |

### Lines of Code (Approximate)

| Project | Python LOC | Key Files |
|---------|------------|-----------|
| **Oread** | ~8,000 | server.py (1400), engine.py (4000), patient.py (1500) |
| **Syrinx** | ~2,500 | script_generator.py (300), syrinx.py (400) |
| **Mneme** | ~1,200 | main.py (92), routers (~300), models (~400) |
| **Echo** | ~600 | tutor.py (200), models (~150) |

---

## 3. Git Repository Analysis

### Repository Structure

| Project | Has .git | Commit Count | Last Commit |
|---------|----------|--------------|-------------|
| **Oread** (synpat) | Yes | 20+ | Dec 27, 2025 |
| **Syrinx** (synvoice) | Yes | 3 | Dec 28, 2025 |
| **Mneme** (synchart) | **No** | Uses parent | N/A |
| **Echo** (echo) | Yes | 3 | Dec 28, 2025 |

### Oread Commits (Most Active)

```
d724c8c CHORE: Update paths after directory rename to synpat
b308831 FIX: Resolve 13 patient generation bugs
01cc0b3 FIX: Code review cleanup and bug fixes
573ce53 FEATURE: Enhanced messiness system with timeline-aware error injection
4caf947 FIX: Medication attribute names in timeline endpoint
a537a86 FIX: Auto-create user profile on first authenticated request
20ea6f5 FIX: Database repository error handling
53c59b5 FIX: Panel patient viewing and new encounter flow
bb224f6 FIX: Header text visibility in dark mode
40e24c3 FEATURE: Dark mode + Time Travel UI improvements
09152ca DOCS: Mark Phase 1 complete in roadmap
8f235a4 FEATURE: Complete Phase 1 - Panels, Mass Generate, Single Case UI
10a755a FEATURE: Time Travel - Disease Arc Visualization
e2d3052 FEATURE: Login/Signup UI for Web Interface
8952ed9 FEATURE: Single Case Generation for Learning Platform
d934bf1 FEATURE: Database + Auth infrastructure (Supabase)
```

**Observations:**
- Oread has the most mature commit history
- Good commit message conventions (FEATURE:, FIX:, CHORE:, DOCS:)
- Active development with regular bug fixes

### Syrinx Commits

```
9881e2e FEATURE: Add Syrinx Web Application
1c11b21 FEATURE: Add error validation, target inference, and ground truth extraction
17f0f95 FEATURE: Initial Syrinx implementation
```

**Observations:**
- Newer project with fewer commits
- Follows same commit conventions

### Echo Commits

```
6dbcdb1 FEATURE: Add React widget package for embedding Echo
7d3d9f2 FEATURE: Add Eleven Labs TTS integration
8c560b2 Initial Echo scaffold
```

**Observations:**
- Newest project, scaffold phase
- Already has TTS integration

### Issue: Mneme Has No Git Repo

Mneme (synchart/) does not have its own `.git` directory. It appears to use the parent `Consult/` repository, which contains unrelated projects (Clara Provider App, VHS evals, etc.).

**Recommendation:** Initialize a dedicated git repo for synchart/.

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/synchart
git init
git add .
git commit -m "FEATURE: Initial Mneme EMR scaffold"
```

---

## 4. Port Configuration (RESOLVED)

### Final Port Allocation

All port conflicts have been resolved. The platform now uses:

| Project | Component | Port | Status |
|---------|-----------|------|--------|
| **Oread** | FastAPI | 8004 | OK |
| **Syrinx** | FastAPI | 8003 | FIXED (was 8000) |
| **Mneme Backend** | FastAPI | 8002 | FIXED (was 8000) |
| **Mneme Frontend** | Vite | 5173 | OK |
| **Mneme Proxy** | API | 8002 | FIXED (was 8001) |
| **Echo** | FastAPI | 8001 | OK |
| **Metis Portal** | Vite | 3000 | NEW |

### Files Updated (December 28-29, 2025)

1. `synchart/backend/src/config.py` - Changed port to 8002
2. `synchart/backend/.env` - Changed PORT to 8002
3. `synchart/frontend/vite.config.ts` - Changed proxy target to 8002
4. `synvoice/server.py` - Changed port to 8003, fixed reload string

All services can now run simultaneously.

---

## 5. Design Consistency Analysis

### API Design Patterns

| Pattern | Oread | Syrinx | Mneme | Echo |
|---------|-------|--------|-------|------|
| **FastAPI** | Yes | Yes | Yes | Yes |
| **Routers** | No (inline) | No (inline) | Yes | Yes |
| **Pydantic Models** | Yes | No | Yes | Yes |
| **Config Module** | No | No | Yes | Yes |
| **Dependency Injection** | Partial | No | Yes | Yes |
| **Async Endpoints** | Mixed | Mixed | Yes | Yes |

### Directory Structure Patterns

| Pattern | Oread | Syrinx | Mneme | Echo |
|---------|-------|--------|-------|------|
| **src/ package** | Yes | No | Yes | Yes |
| **models/ dir** | Yes | No | Yes | Yes |
| **routers/ dir** | No | No | Yes | Yes |
| **core/ dir** | No | Yes | No | Yes |
| **config.py** | No | No | Yes | Yes |
| **tests/ dir** | Yes | No | No | Yes |

### Recommendations

1. **Add routers to Oread**: Move endpoints from server.py to `src/routers/`
2. **Add Pydantic models to Syrinx**: Create `src/models/` with typed encounter models
3. **Add config.py to Oread and Syrinx**: Centralize settings
4. **Add tests to Mneme and Syrinx**: Match Oread/Echo pattern

---

## 6. Code Consistency Analysis

### Pydantic Model Duplication

The following models are defined independently in multiple projects:

| Model | Oread | Mneme | Echo |
|-------|-------|-------|------|
| **Condition** | 20+ fields | 12 fields | 8 fields |
| **Medication** | 25+ fields | 15 fields | 10 fields |
| **Allergy** | 12 fields | 8 fields | 6 fields |
| **Patient** | 50+ fields | 30 fields | Context only |

**Impact:**
- No single source of truth
- Risk of field name mismatches
- Duplicate maintenance effort

### LLM Client Duplication

Three different patterns for calling Claude:

```python
# Oread: Wrapper with caching
class LLMClient:
  def __init__(self, api_key, model):
    self.client = Anthropic(api_key=api_key)

# Syrinx: Direct calls
client = anthropic.Anthropic()
response = client.messages.create(...)

# Echo: Simple wrapper
class Tutor:
  def __init__(self, api_key, model):
    self.client = anthropic.Anthropic(api_key=api_key)
```

### Dependency Version Mismatches

| Package | Oread | Syrinx | Mneme | Echo |
|---------|-------|--------|-------|------|
| anthropic | >=0.40.0 | >=0.25.0 | — | >=0.40.0 |
| fastapi | >=0.110.0 | >=0.110.0 | >=0.109.0 | >=0.109.0 |
| pydantic | >=2.0.0 | >=2.0.0 | >=2.5.0 | >=2.5.0 |

**Issue:** Syrinx uses anthropic 0.25.0 which has different API than 0.40.0+

### Import Style Consistency

All projects follow good import patterns:
```python
# Standard library
import json
from datetime import date

# Third-party
import anthropic
from fastapi import FastAPI

# Local
from ..models import Patient
from .config import Settings
```

---

## 7. Shared Code (IMPLEMENTED via Metis)

### Metis Model Sync System

Instead of a shared pip package, Metis provides JSON Schema definitions and code generation:

```
metis/shared/
├── models/
│   ├── clinical.schema.json   # Condition, Medication, Allergy
│   └── context.schema.json    # PatientContext, EncounterContext
└── sync.py                    # Generates Pydantic models for each project
```

### Usage

```bash
# Generate models for all projects
cd metis/shared
python sync.py --project all

# Validate sync status (for CI)
python sync.py --validate

# Generate for specific project
python sync.py --project oread
```

### Generated Output

Each project receives `src/models/_generated/context.py`:
```python
"""
GENERATED BY METIS - DO NOT EDIT DIRECTLY
Generated at: 2025-12-29T07:39:17
Project: oread
"""
from pydantic import BaseModel
from typing import Literal

class Condition(BaseModel):
    id: str
    display_name: str
    code: str | None = None
    status: Literal["active", "resolved", "inactive"] = "active"
```

### Why Not a Pip Package?

- Projects must function independently when cloned
- No build step required for standalone use
- Generated code checked into each repo
- Clear source of truth in JSON Schemas

### Shared Model Examples

```python
# meded_shared/models/clinical.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class Condition(BaseModel):
  """Unified condition model for all MedEd projects."""
  id: str
  code: str
  code_system: str  # snomed, icd10
  display_name: str
  status: str  # active, resolved, inactive
  severity: Optional[str] = None
  onset_date: Optional[date] = None
  abatement_date: Optional[date] = None
  notes: Optional[str] = None

class Medication(BaseModel):
  """Unified medication model."""
  id: str
  code: str
  code_system: str  # rxnorm
  display_name: str
  status: str  # active, stopped, completed
  dose: Optional[str] = None
  frequency: Optional[str] = None
  route: Optional[str] = None
  start_date: Optional[date] = None
  end_date: Optional[date] = None

class Allergy(BaseModel):
  """Unified allergy model."""
  id: str
  display_name: str
  category: str  # food, medication, environment
  criticality: str  # low, high, unable-to-assess
  reactions: list[str] = []
  notes: Optional[str] = None
```

### Shared LLM Client

```python
# meded_shared/llm.py
from functools import lru_cache
import anthropic

class AnthropicClient:
  """Unified Claude client with caching and retry logic."""

  def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
    self.client = anthropic.Anthropic(api_key=api_key)
    self.model = model

  def complete(self, system: str, user: str, **kwargs) -> str:
    response = self.client.messages.create(
      model=self.model,
      system=system,
      messages=[{"role": "user", "content": user}],
      **kwargs
    )
    return response.content[0].text

@lru_cache
def get_client() -> AnthropicClient:
  from .config import get_settings
  settings = get_settings()
  return AnthropicClient(settings.anthropic_api_key)
```

---

## 8. Recommendations

### Completed (December 28-29, 2025)

| # | Task | Status |
|---|------|--------|
| 1 | Fix Mneme frontend proxy (8001 → 8002) | **DONE** |
| 2 | Change Mneme backend port (8000 → 8002) | **DONE** |
| 3 | Change Syrinx port (8000 → 8003) | **DONE** |
| 4 | Initialize git repo for Mneme | **DONE** |
| 5 | Create shared model system | **DONE** (Metis sync.py) |
| 6 | Update Syrinx to anthropic 0.40.0+ | **DONE** |

### Priority 1: High (Next Sprint)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 7 | Build Metis web portal | 6-8 hours | Unified entry point |
| 8 | Add config.py to Oread | 1 hour | Better maintainability |
| 9 | Add Pydantic models to Syrinx | 3 hours | Type safety |

### Priority 2: Medium (Following Sprint)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 10 | Refactor Oread server.py into routers | 4 hours | Maintainability |
| 11 | Add tests to Mneme and Syrinx | 4 hours | Quality assurance |
| 12 | Standardize dependency versions | 2 hours | Consistency |
| 13 | Add linting config (ruff/black) | 1 hour | Code quality |

### Priority 3: Low (Backlog)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 14 | Create custom exception hierarchy | 2 hours | Better error handling |
| 15 | Add mypy configuration | 2 hours | Type checking |
| 16 | Add METIS_MODE to all projects | 3 hours | Ecosystem mode |
| 17 | Create integration tests | 6 hours | End-to-end testing |

---

## 9. Action Items

### Completed (December 28-29, 2025)

- [x] Fixed Mneme frontend proxy (8001 → 8002)
- [x] Changed Mneme backend port (8000 → 8002)
- [x] Changed Syrinx port (8000 → 8003)
- [x] User created Mneme git repo
- [x] Updated Syrinx anthropic to 0.40.0+
- [x] Created Metis orchestration layer
- [x] Created model sync system (sync.py)
- [x] Created shell scripts (start-all, stop-all, status)
- [x] Created symlinks (oread, syrinx, mneme)
- [x] Generated shared models for all projects

### How to Start Everything

```bash
# Option 1: Via Metis scripts
cd /Users/dochobbs/Downloads/Consult/MedEd/metis/scripts
./start-all.sh

# Option 2: Manual (individual terminals)
cd synpat && source .venv/bin/activate && python server.py          # Port 8004
cd synvoice && source venv/bin/activate && python server.py         # Port 8003
cd synchart/backend && source .venv/bin/activate && python -m src.main  # Port 8002
cd echo && source .venv/bin/activate && uvicorn src.main:app --port 8001
cd synchart/frontend && npm run dev                                 # Port 5173

# Check status
./status.sh
```

### Next Sprint

1. Build Metis web portal (React + Vite)
2. Add config.py to Oread
3. Add Pydantic models to Syrinx

### Future

1. Refactor Oread server.py into routers
2. Add tests to Mneme and Syrinx
3. Add METIS_MODE detection to all projects
4. Implement Supabase auth in portal

---

## Appendix: File References

### Configuration Files

| File | Lines | Status |
|------|-------|--------|
| synpat/pyproject.toml | 133 | Good |
| echo/pyproject.toml | 35 | Good |
| synvoice/requirements.txt | 19 | Needs update |
| synchart/backend/requirements.txt | 10 | Good |
| echo/src/config.py | 48 | Good pattern |
| synchart/backend/src/config.py | 33 | Good pattern |

### Model Files

| File | Lines | Status |
|------|-------|--------|
| synpat/src/models/patient.py | 1500+ | Comprehensive |
| echo/src/models/context.py | 95 | Minimal, good |
| echo/src/models/feedback.py | 72 | Good |
| synchart/backend/src/models/patient.py | 240 | Good |

### Main Application Files

| File | Lines | Status |
|------|-------|--------|
| synpat/server.py | 1400+ | Needs refactoring |
| synchart/backend/src/main.py | 92 | Good pattern |
| echo/src/main.py | 56 | Excellent pattern |
| synvoice/server.py | 600 | Acceptable |

---

*This document should be updated as issues are resolved and new findings emerge.*
