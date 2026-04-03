# MedEd Platform - Issues Tracker

**Last Updated:** December 29, 2025
**Maintainer:** Claude (Project Coordinator)

---

## Critical Issues

### ISSUE-001: Port Conflict - Syrinx and Mneme Backend
- **Status:** RESOLVED
- **Severity:** CRITICAL
- **Description:** Both services default to port 8000
- **Files:**
  - `synvoice/server.py:586` - `port=8003` ✓
  - `synchart/backend/src/config.py:18` - `port: int = 8002` ✓
  - `synchart/backend/.env` - `PORT=8002` ✓
- **Resolution:** Mneme on 8002, Syrinx on 8003, tested and working
- **Resolved:** December 28, 2025

### ISSUE-002: Mneme Frontend Proxy Misconfigured
- **Status:** RESOLVED
- **Severity:** HIGH
- **Description:** Frontend proxies to 8001 (Echo) instead of backend
- **File:** `synchart/frontend/vite.config.ts:10`
- **Resolution:** Changed target to `http://localhost:8002`
- **Resolved:** December 28, 2025

---

## High Priority Issues

### ISSUE-003: Mneme Missing Git Repository
- **Status:** RESOLVED
- **Severity:** HIGH
- **Description:** synchart/ uses parent Consult repo instead of own git
- **Resolution:** User created and pushed mneme repo
- **Resolved:** December 28, 2025

### ISSUE-004: Model Duplication Across Projects
- **Status:** RESOLVED
- **Severity:** HIGH
- **Description:** Condition, Medication, Allergy defined 3x
- **Files:**
  - `synpat/src/models/patient.py`
  - `synchart/backend/src/models/patient.py`
  - `echo/src/models/context.py`
- **Resolution:** Created Metis sync tool with canonical JSON Schemas
  - Canonical schemas: `metis/shared/models/*.schema.json`
  - Generated models: `*/src/models/_generated/context.py`
  - Sync command: `cd metis/shared && python sync.py --project all`
  - Validation: `python sync.py --validate`
- **Resolved:** December 29, 2025

### ISSUE-005: Syrinx Uses Outdated anthropic
- **Status:** RESOLVED
- **Severity:** HIGH
- **Description:** Syrinx uses anthropic>=0.25.0, others use >=0.40.0
- **File:** `synvoice/requirements.txt`
- **Resolution:** Updated to anthropic>=0.40.0 (installed: 0.75.0), tested API calls work
- **Resolved:** December 29, 2025

---

## Medium Priority Issues

### ISSUE-006: Oread Missing config.py
- **Status:** OPEN
- **Severity:** MEDIUM
- **Description:** Settings embedded in server.py instead of config module
- **Impact:** Harder to manage environment variables
- **Fix:** Create `synpat/src/config.py` following Echo/Mneme pattern
- **Assigned:** TBD

### ISSUE-007: Syrinx Missing Pydantic Models
- **Status:** OPEN
- **Severity:** MEDIUM
- **Description:** Uses raw dictionaries instead of typed models
- **Impact:** No type safety, no validation
- **Fix:** Create `synvoice/src/models/` with encounter models
- **Assigned:** TBD

### ISSUE-008: Oread server.py Too Large
- **Status:** OPEN
- **Severity:** MEDIUM
- **Description:** server.py is 1400+ lines with inline endpoints
- **Impact:** Hard to maintain, find code
- **Fix:** Extract to `src/routers/` following Echo/Mneme pattern
- **Assigned:** TBD

### ISSUE-009: Inconsistent Dependency Versions
- **Status:** OPEN
- **Severity:** MEDIUM
- **Description:** Different versions of pydantic, fastapi across projects
- **Impact:** Potential runtime issues
- **Fix:** Create shared requirements-base.txt
- **Assigned:** TBD

---

## Low Priority Issues

### ISSUE-010: Missing Tests in Mneme
- **Status:** OPEN
- **Severity:** LOW
- **Description:** No test directory in synchart/
- **Fix:** Add `synchart/backend/tests/`
- **Assigned:** TBD

### ISSUE-011: Missing Tests in Syrinx
- **Status:** OPEN
- **Severity:** LOW
- **Description:** No test directory in synvoice/
- **Fix:** Add `synvoice/tests/`
- **Assigned:** TBD

### ISSUE-012: No Linting Configuration
- **Status:** OPEN
- **Severity:** LOW
- **Description:** No ruff/black/flake8 config
- **Impact:** Inconsistent code style
- **Fix:** Add pyproject.toml [tool.ruff] section
- **Assigned:** TBD

---

## Resolved Issues

### ISSUE-001: Port Conflict - Syrinx and Mneme Backend (Dec 28, 2025)
### ISSUE-002: Mneme Frontend Proxy Misconfigured (Dec 28, 2025)
### ISSUE-003: Mneme Missing Git Repository (Dec 28, 2025)
### ISSUE-004: Model Duplication Across Projects (Dec 29, 2025)
### ISSUE-005: Syrinx Uses Outdated anthropic (Dec 29, 2025)

---

## Port Allocation Reference

| Project | Port | Status |
|---------|------|--------|
| Oread | 8004 | OK |
| Echo | 8001 | OK |
| Mneme Backend | 8002 | FIXED ✓ |
| Syrinx | 8003 | FIXED ✓ |
| Mneme Frontend | 5173 | OK |
| **Metis Portal** | 3000 | NEW ✓ |

---

## Quick Fix Commands

```bash
# Fix ISSUE-001 and ISSUE-002 (port conflicts)
# Step 1: Update Mneme backend config
sed -i '' 's/port: int = 8000/port: int = 8002/' synchart/backend/src/config.py

# Step 2: Update Mneme frontend proxy
sed -i '' 's/localhost:8001/localhost:8002/' synchart/frontend/vite.config.ts

# Step 3: Update Syrinx server port
sed -i '' 's/port=8000/port=8003/' synvoice/server.py

# Fix ISSUE-003 (Mneme git repo)
cd synchart && git init && git add . && git commit -m "Initial commit"
```

---

## Metis - Platform Orchestration

**Created:** December 29, 2025

Metis is the parent project that unifies the MedEd ecosystem. It provides:

### Orchestration Scripts
```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/metis/scripts

./start-all.sh   # Start all backends and frontends
./status.sh      # Check service status
./stop-all.sh    # Stop all services
```

### Model Sync Tool
```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/metis/shared

python sync.py --project all     # Generate models for all projects
python sync.py --validate        # Verify models are in sync (for CI)
python sync.py --dry-run         # Preview what would be generated
```

### Symlinks
```
oread  -> synpat
syrinx -> synvoice
mneme  -> synchart
```

### Future Phases
- Phase 2: Web portal with unified dashboard (React + Vite)
- Phase 3: Supabase auth integration
- Phase 4: METIS_MODE for ecosystem vs standalone behavior

---

*Update this file as issues are resolved or new issues discovered.*
