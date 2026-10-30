# Test Strategy

Last updated: 2026-10-31 (Phase 0 — strategy only; no tests exist yet)

## Principles
1. **Testing is never skipped because the app appears to work.** Every phase gate requires executed test runs with pass/fail/skip counts recorded in [QUALITY_REPORT.md](QUALITY_REPORT.md).
2. A test is reported as passing only after it has actually run and passed. Skips must be explained.
3. Expected values for financial and metric tests are hand-calculated from small fixtures and written in the test, not copied from the code's own output.
4. Requirements are not weakened to make a check pass.
5. Destructive tests run only against `meridian_test` (guarded by a check on the database name), never production.

## Test layers

| # | Layer | Tooling | Scope | Location | Runs in CI |
|---|---|---|---|---|---|
| 1 | Python unit | Pytest | Metric functions, transforms, statistics, scenario maths | `backend/tests/unit/` | Yes |
| 2 | Data tests | Pytest + Pandas | Schema, keys, nulls, ranges, relationships, reconciliation | `backend/tests/data/` | Yes (fixtures) |
| 3 | MySQL integration | Pytest (`-m mysql`) | Migrations, SQL transforms, repositories, transactions, idempotent reload | `backend/tests/integration/` | Yes (MySQL 8.0 service container) |
| 4 | API | Pytest + FastAPI TestClient | Routes, validation, error envelope, contracts, DB-down | `backend/tests/api/` | Yes |
| 5 | Frontend | Vitest + React Testing Library | Components, filters, loading/empty/error states | `frontend/` | Yes |
| 6 | E2E smoke | Playwright | Critical journeys against local API + fixture DB | `frontend/e2e/` | Yes |
| 7 | Deployment smoke | Python script | Live health, frontend load, API connectivity, DB persistence | `scripts/` | Manual/post-deploy |

## Fixtures
- Small, deterministic, hand-built CSVs mirroring the **observed** Olist schema (built in Phase 2 after profiling). Labelled synthetic test fixtures.
- Fixtures deliberately include: duplicate keys, orphan foreign keys, missing delivery dates, cancelled orders, multi-item orders, multi-payment orders, boundary dates (month/cohort edges), zero/negative amounts.
- A schema-conformance test asserts that fixture headers match the real dataset's headers (recorded in Phase 2).

## Mandatory specific tests
- Join fan-out / double-counting (order vs item vs payment grain).
- Payment vs item reconciliation differences surfaced.
- Cohort boundary assignment.
- Chronological split and no-future-leakage for any model.
- Model vs naive baseline on held-out data.
- Scenario/ROI maths incl. zero cost and undefined ROI.
- SQL vs Python vs API vs report value reconciliation for identical filters.
- Idempotent re-ingestion and rollback on partial failure.
- No mock data present in production frontend build.

## Quality gates
See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md#standard-gate-commands-become-active-as-tooling-is-installed). Ruff (`check` + `format --check`) must pass; rule exceptions must be narrow and documented inline and in this file.

## Rule exceptions register
| Rule | Scope | Reason | Approved |
|---|---|---|---|
| — | — | — | — |
