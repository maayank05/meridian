# Implementation Plan

Source: `instructions/14_PHASE_PLAN_AND_CHECKPOINTS.md`, refined with Phase 0 environment findings.
Last updated: 2026-10-31

Every phase: (1) state scope/risks/files/acceptance criteria before starting, (2) implement in small units with targeted tests after each, (3) run the full gate, (4) update status/traceability/quality/limitations, (5) write `docs/checkpoints/PHASE_NN_CHECKPOINT.md`, (6) **stop for user approval**.

A phase cannot pass if any critical test is skipped without explanation, or if lint/build fails without an approved deviation.

## Standard gate commands (become active as tooling is installed)

| Layer | Command | Active from |
|---|---|---|
| Python lint | `ruff check .` | Phase 3 |
| Python format | `ruff format --check .` | Phase 3 |
| Python tests (unit/data) | `pytest backend/tests -m "not mysql"` | Phase 3 |
| MySQL integration | `pytest backend/tests -m mysql` (needs local `meridian_test`) | Phase 3 |
| Frontend lint | `npm --prefix frontend run lint` | Phase 9 |
| Frontend typecheck | `npm --prefix frontend run typecheck` | Phase 9 |
| Frontend tests | `npm --prefix frontend run test` | Phase 9 |
| Frontend build | `npm --prefix frontend run build` | Phase 9 |
| E2E smoke | `npm --prefix frontend run e2e` | Phase 9 |
| Deployment smoke | `python scripts/smoke_deploy.py <url>` | Phase 12 |

Exact commands are confirmed when each tool is configured; this table is updated, not assumed.

---

## Phase 0 — Repository and environment audit
- **Objective:** understand requirements, environment, constraints; create control documents only.
- **Deliverables:** `docs/*` control docs, `.gitignore`, updated `CLAUDE.md`, `docs/checkpoints/PHASE_00_CHECKPOINT.md`.
- **Acceptance:** all 11 mandated control docs exist; every FR/NFR from `02` appears in traceability; environment facts recorded from executed commands; contradictions and decisions logged; no application code.

## Phase 1 — Business analysis and specification
- **Deliverables (`business/`):** business case, scope, stakeholder register/map, BRD, FRD, NFRs, user stories (Given/When/Then), business rules catalogue, KPI dictionary (draft, every KPI tagged with source fields or `unsupported`/`synthetic`), assumptions register, RAID log, change log, UAT template skeleton.
- **Risk:** KPI dictionary written before data is profiled → mark source-field references "to verify in Phase 2".
- **Gate:** every proposed metric has a valid expected source or is explicitly unsupported/simulated; traceability links stories → requirements.

## Phase 2 — Dataset discovery and profiling
- **Prerequisite:** user places Olist CSVs in `data/raw/olist/` (Q-2).
- **Deliverables:** profiling script (Python/Pandas), profiling report (headers, dtypes, row counts, nulls, duplicate candidate keys, orphans, date ranges, amount distributions, categories), licence review record, data dictionary, deterministic synthetic test fixtures, update KPI dictionary with verified fields.
- **Gate:** data model is designed from observed schema; licence terms recorded; fixture schema matches real schema (tested).

## Phase 3 — MySQL design and ingestion
- **Prerequisites:** approval of D-003/D-006/D-007/D-009; user creates `meridian_dev`/`meridian_test` + app user and local `.env` (Q-5).
- **Deliverables:** `pyproject.toml` (Ruff/Pytest config), locked requirements, `.env.example`, config module, migration runner + `schema_version`, `raw_*`/`stg_*`/`audit_*` DDL, ingestion with validation and run metadata, SQL transformations to `dim_*`/`fact_*`.
- **Tests:** clean load, repeat load (idempotent), partial-failure rollback, rebuild determinism, FK/orphan checks, row-count reconciliation.
- **Gate:** fixture ingestion passes on real MySQL; full Olist load recorded in audit tables.

## Phase 4 — Core SQL analytics
- Revenue/order trends, category/product, customer purchase, repeat, cohort, seller, delivery, reviews, period comparison as versioned SQL (`backend/sql/marts`, `backend/sql/reports`).
- **Gate:** each query matches independently hand-computed expected values on fixtures; explicit fan-out/double-counting tests.

## Phase 5 — Python analytics services
- Pandas metric functions, quality checks, report data assembly.
- **Gate:** unit tests incl. edge cases; SQL vs Python reconciliation tests on identical fixtures.

## Phase 6 — Statistics and ML
- Document valid questions first; baselines before models; chronological validation; intervals.
- **Gate:** leakage tests, held-out evaluation vs baseline, model report with limitations. A model that does not beat baseline is reported as such.

## Phase 7 — Decision simulator
- Scenario engine (baseline vs intervention, base/upside/downside, break-even, sensitivity, ROI/payback with explicit denominators).
- **Gate:** hand-calculated tests incl. zero-cost/undefined cases; terminology review (no "profit" without costs).

## Phase 8 — FastAPI
- `/api/v1` routers, Pydantic schemas, error envelope, request IDs, structured logs, CORS, health/readiness, pagination.
- **Gate:** API tests (success/invalid/missing/empty/boundary/DB-down/unexpected) on MySQL; OpenAPI reviewed.

## Phase 9 — React application
- Shell, 10 pages, filters, KPI cards, charts, tables, provenance badges, loading/empty/error states, accessibility.
- **Gate:** lint, typecheck, unit/component tests, production build, Playwright smoke against local API. No mock data in production build.

## Phase 10 — Power BI
- Semantic model spec, DAX measures, report page spec, connection/refresh notes, reconciliation checklist.
- PBIX authored by the user in Power BI Desktop (installed, v2.159.883.0) following the spec — Claude cannot operate the GUI (D-012).
- **Gate:** reconciliation of PBIX totals vs API for identical filters, or explicitly documented as "requires Desktop authoring".

## Phase 11 — Reporting and governance
- HTML executive report (Matplotlib/Seaborn figures from real outputs), UAT pack, final BA artefacts, recommendations with evidence/alternatives/uncertainty.
- **Gate:** report numbers match API values (automated test).

## Phase 12 — CI/CD and deployment
- GitHub Actions (Ruff, Pytest with MySQL service container, frontend checks), Render static site + web service, managed MySQL provider chosen after current pricing/feature verification (D-011), secrets, backups, restore test.
- **Gate:** live smoke test; data persists across redeploy; restore proven.

## Phase 13 — Portfolio and learning package
- README with real screenshots, diagrams, demo script, `learning/` curriculum (17 sections per `13`), interview guide.
- **Gate:** clean-clone reproducibility run; honest completion audit of all requirements.

## Lean completion (approved 2026-11-06, D-020)
Remaining phases are delivered as four milestones with one checkpoint each:
- **A** Phase 3: data pipeline. **Done**, see [PHASE_03_CHECKPOINT](checkpoints/PHASE_03_CHECKPOINT.md).
- **B** Phases 4–7: core SQL analytics, Python services, one forecast vs baseline, compact decision simulator. **Done**, see [PHASE_07_CHECKPOINT](checkpoints/PHASE_07_CHECKPOINT.md).
- **C** Phases 8, 9, 11: FastAPI, React (about 5 pages), concise executive report. **Done**, see [PHASE_11_CHECKPOINT](checkpoints/PHASE_11_CHECKPOINT.md).
- **D** Phases 12–13: CI, README, short learning guide, clean-clone check. Power BI = spec + DAX (owner builds PBIX); paid hosting deferred.
