# MedEd Platform — Worklist

## Completed (This Session)
- [x] Plan 1: Athena service built (62 tests, 12 endpoints)
- [x] Plan 2: Knowledge migration (46 peds conditions, 170 frameworks)
- [x] Plan 3: Service wiring (all ports 9100-9105)
- [x] Plan 4: IM content (167 conditions + 167 frameworks)
- [x] Plan 5: MVP polish (specialty selector, Echo→Athena, E2E tested)
- [x] IM disease arcs (8 arcs)
- [x] Adult wellness frameworks (5 age-based)
- [x] ACIP immunization schedule
- [x] Adult patient generation wired into Oread
- [x] Dashboard redesign (IBM Plex Mono command center)
- [x] 146 tests (unit + integrity + resolver + smoke)

## High Priority
- [ ] Wire Oread engine to query Athena at runtime (currently uses local conditions.yaml)
- [ ] Add specialty_variants to shared conditions (peds vs IM presentation differences)
- [ ] Mneme learning sessions pass specialty context through
- [ ] Echo case start uses Athena specialty parameter

## Medium Priority
- [ ] IM disease arcs integrated with Oread Time Travel
- [ ] Adult growth/BMI data for Athena (wellness visits need this)
- [ ] Oread validation fixes (R69 fallback, age-impossible conditions)
- [ ] Dashboard: add learner level selector
- [ ] Dashboard: show Athena knowledge stats dynamically (not hardcoded)

## Low Priority
- [ ] Docker/compose deployment
- [ ] Persist Syrinx/Echo patient imports to DB (currently in-memory)
- [ ] Standardize Echo routes to use /api/ prefix
- [ ] Additional IM conditions (ophthalmology, allergy/immunology)
- [ ] Vaccine catch-up calculator
- [ ] Documentation practice (note writing + AI feedback)
- [ ] Billing/coding practice modules

## Technical Debt
- [ ] Oread server.py is 1400+ lines — should be split
- [ ] Inconsistent system names across peds conditions (respiratory vs pulmonary, neurological vs neurology)
- [ ] Some Echo framework IDs don't match Athena condition IDs (naming mismatches)
- [ ] No linting configuration across projects
- [ ] Test coverage in Oread, Echo, Syrinx, Mneme is minimal
