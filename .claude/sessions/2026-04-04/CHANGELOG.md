# Changelog — 2026-04-03 / 2026-04-04

## Features (14 commits)
- `4d561bc` (athena): Athena curriculum & knowledge service — complete foundation
- `b6a909f` (athena): Plan 2 — Migrate all peds knowledge from Oread and Echo into Athena
- `2478ec4` (athena): Plan 4 — Internal Medicine content (167 conditions + 167 frameworks)
- `2a04148` (athena): IM disease arcs, adult wellness frameworks, ACIP immunization schedule
- `f840bd6` (athena): Comprehensive test suite — 112 tests validating full knowledge base
- `7f6ce90` (metis): Plan 5 — Specialty selector in Dashboard, Athena in service status bar
- `6dc00ed` (metis): Redesigned Metis Dashboard — dense command center with clinical typography
- `ad9c13a` (echo): Plan 5 — Framework loader queries Athena first, falls back to local
- `62ed602` (oread): Adult patient generation — wire AdultEngine into /api/generate

## Chores (5 commits)
- `e5c0116` (athena): Plan 3 — Port migration to 9100-9105 and AthenaClient distribution
- `f5bb36e` (oread): Port migration 8004→9104, add AthenaClient
- `0f7f834` (echo): Port migration 8001→9101, add AthenaClient
- `cbd4e59` (syrinx): Port migration 8003→9103, update Echo URL to 9101
- `2c34295` (mneme): Port migration — backend 8002→9102, echo_url→9101, syrinx→9103

## Docs (6 commits)
- `eb18355` (oread): Update CLAUDE.md with v2 ports and Athena
- `8df0061` (echo): Update CLAUDE.md with v2 ports and Athena
- `c640e6b` (syrinx): Update CLAUDE.md with v2 ports and Athena
- `e062a1b` (mneme): Update CLAUDE.md with v2 ports and Athena
- `98e634d` (metis): Update CLAUDE.md with v2 ports and Athena
- Root CLAUDE.md, INTEGRATION.md, plan overview updated (untracked — root has no git)
