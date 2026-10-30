# MERIDIAN — Project Specification

Status: **Draft v0.1 (Phase 0)**. This document is the authoritative implementation spec once approved. It consolidates `MASTER_BUILD_PROMPT.md`, `CLAUDE.md` and `instructions/01`–`15`. Where those sources conflict, the resolution is recorded in [DECISIONS.md](DECISIONS.md).

Last updated: 2026-10-31

---

## 1. Product

MERIDIAN is a Business Intelligence & Decision Intelligence Platform for **Northstar Commerce**, a **simulated** online retailer. Observed data comes from the public **Olist Brazilian E-Commerce** dataset. Anything Olist does not contain (costs, marketing spend, budgets, inventory) is either declared unsupported or modelled in clearly labelled synthetic scenario tables.

Questions the product must answer, with evidence:

1. What happened to commercial and operational performance?
2. Where did the change occur?
3. What evidence supports the interpretation?
4. What may happen next, where prediction is justified?
5. What decisions could be considered, and what might they be worth under stated assumptions?
6. How reliable is the underlying data?

## 2. Approved technology stack (locked — D-001)

| Concern | Approved technology |
|---|---|
| Language | Python |
| Database (system of record) | MySQL (InnoDB) |
| Data analysis | Pandas |
| Transformations | Version-controlled, ordered SQL scripts |
| Backend API | FastAPI |
| Frontend | React (TypeScript permitted) |
| Statistical plots / reports | Matplotlib, Seaborn |
| Statistics | SciPy, Statsmodels |
| Machine learning | Scikit-learn |
| Testing | Pytest |
| Code quality | Ruff |
| Version control | Git + GitHub |
| CI/CD | GitHub Actions |
| BI dashboards | Power BI |
| Hosting | Render |

Prohibited substitutions: PostgreSQL / DuckDB / SQLite as the application DB, Streamlit instead of React, dbt. Any change requires evidence + alternatives + written user approval.

### 2.1 Supporting libraries — PROPOSED, awaiting approval

These are not core-stack substitutions; they are the minimum libraries needed to implement the approved stack. None will be installed until approved (see D-003 … D-008, D-014).

| Library | Purpose | Why needed | Decision |
|---|---|---|---|
| pip-tools | Lock Python dependencies (`requirements*.txt` with hashes) | Master prompt requires locked deps | D-003 |
| SQLAlchemy 2.x **Core** (no ORM) | Connection pooling, bound parameters, transactions | Safe parameterized SQL + pool limits (06) | D-006 |
| PyMySQL | Pure-Python MySQL driver | No compiler needed on Windows/Render | D-006 |
| Uvicorn | ASGI server for FastAPI | FastAPI cannot serve itself | D-006 |
| pydantic-settings | Environment/config validation | `config/` layer (03) | D-006 |
| httpx | FastAPI TestClient dependency | API tests (09) | D-006 |
| pytest-cov | Coverage reporting | Quality evidence | D-006 |
| Vite | React build tool | 03 asks for a maintained React build tool | D-004 |
| TypeScript | Typed frontend | Recommended in 03/07 | D-004 |
| React Router | Page navigation | 10 module pages | D-004 |
| Vitest + React Testing Library | Frontend unit/component tests | 07/09 | D-004 |
| ESLint | Frontend lint | 09 gate | D-004 |
| Recharts (MIT) | Interactive charts in React | 07 requires a documented React chart library | D-005 |
| Playwright | End-to-end smoke tests | 09 layer 6 | D-014 |

## 3. Architecture

```
Olist CSV files (manual download, gitignored)      Synthetic scenario assumptions (seeded, labelled)
            │                                                   │
            ▼                                                   ▼
   Python ingestion + validation  ──────────►  MySQL 8.0 (InnoDB), one database per environment
                                                 raw_*  → stg_*  → dim_* / fact_*   (ordered SQL scripts)
                                                 audit_* (runs, quality results)   scenario_* (synthetic)
                                                                   │
                                     ┌─────────────────────────────┼──────────────────────────┐
                                     ▼                             ▼                          ▼
                       Python analytics services          Power BI (Desktop, specs +   Matplotlib/Seaborn
                       (Pandas/SciPy/Statsmodels/          reconciliation)              HTML executive report
                        Scikit-learn)
                                     │
                       FastAPI /api/v1 (routers → services → repositories → MySQL)
                                     │
                       React + TypeScript SPA (Render Static Site)
```

### 3.1 Backend layering (03)
`api/` (routers, schemas, middleware) → `services/` (use cases) → `repositories/` (parameterized SQL) → MySQL. Calculations live in `analytics/`. Settings in `core/`/`config/`. Route handlers contain no SQL and no business rules.

### 3.2 Frontend layering (03, 07)
`src/app`, `src/pages`, `src/components`, `src/features`, `src/services` (single typed API client), `src/types`, `src/styles`. Components render; they do not calculate business metrics.

### 3.3 Repository layout
Adopts `instructions/12` layout with documented deviations (D-010):
- Python tests live in `backend/tests/` (unit, data, integration, api). No duplicate top-level `tests/`.
- Frontend tests in `frontend/tests/` (or co-located, decided in Phase 9); Playwright E2E in `frontend/e2e/`.
- Control documents `DEPLOYMENT_RUNBOOK.md`, `SECURITY.md`, `TEST_STRATEGY.md` live in `docs/` (required by master prompt, missing from 12's tree).
- Folders are created only when they receive real content.

## 4. Data

### 4.1 Source
Olist Brazilian E-Commerce Public Dataset — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

**Expected** (from public documentation; **unverified until Phase 2**): 9 CSV files — customers, orders, order_items, order_payments, order_reviews, products, sellers, geolocation, product_category_name_translation; roughly 100k orders, 2016–2018, BRL currency. No schema, row count or date range will be relied on until profiled from the actual files. Licence CC BY-NC-SA 4.0, verified by the project owner (D-013).

### 4.2 Acquisition
Manual download by the user (no Kaggle credentials on this machine) into `data/raw/olist/` (gitignored). Ingestion reads a configurable path; Kaggle credentials are never required when files exist locally.

### 4.3 Provenance classes (04)
Every table, field, metric, API value and UI badge carries one of: `source_observed`, `derived`, `synthetic_assumption`, `forecast`, `scenario_output`.

### 4.4 MySQL layering
Single database per environment (`meridian_dev`, `meridian_test`, production DB on managed host) with table prefixes `raw_`, `stg_`, `dim_`, `fact_`, `audit_`, `scenario_` (D-009). Schema changes via ordered SQL migration scripts tracked in a `schema_version` table (D-007). DECIMAL for money; timestamps stored as UTC with source timezone documented in Phase 2.

### 4.5 Fixtures
CI and unit tests use small, deterministic, hand-built fixtures that mimic the observed schema and are labelled **synthetic test fixtures**. They are never presented as Olist results.

## 5. Modules

| ID | Module | Scope constraint known at Phase 0 | Status |
|---|---|---|---|
| M01 | Executive Intelligence Centre | Canonical revenue proxy fixed by D-016 ("Delivered Merchandise Value (Revenue Proxy)") | Not started |
| M02 | Customer Intelligence | Olist `customer_id` is per-order; repeat analysis must use `customer_unique_id` (to verify Phase 2) | Not started |
| M03 | Marketing Performance & Incrementality | **No marketing spend/attribution in Olist.** CAC/ROAS/lift cannot be observed. Synthetic scenario model + methodology approved (D-015, FR-030) | Not started |
| M04 | Product & Pricing Intelligence | Elasticity only if identification assumptions hold; otherwise descriptive + labelled sensitivity scenarios | Not started |
| M05 | Operations & Seller Intelligence | Eligible population and denominators per metric | Not started |
| M06 | Financial Intelligence / FP&A | No COGS/opex in Olist → no profit claims; synthetic budget only if labelled | Not started |
| M07 | Business Decision Simulator | Python-service calculations, hand-calculated tests | Not started |
| M08 | Forecasting, Statistics & Risk | Chronological splits, naive/seasonal baseline; ~2 years of history limits seasonal models | Not started |
| M09 | Data Quality & Governance Centre (+ BA governance artefacts) | — | Not started |
| M10 | Automated Executive Reporting | HTML from real analytical outputs; PDF only if verified | Not started |

## 6. Metric governance
- One canonical definition per KPI, recorded in the KPI dictionary (Phase 1) with SQL/Python/DAX references and a reconciliation test.
- Revenue is not profit. Association is not causation. No future leakage.
- Missingness and reconciliation differences (e.g. payments vs order items) are shown, never hidden.

## 7. Integrity rules enforced throughout (user-mandated, 2026-10-31)
1. **Testing is never skipped** because the application appears to work. Every phase gate requires executed tests with counts.
2. **No dummy charts or fabricated findings.** Empty or unavailable data renders an explicit empty state; findings appear only after validated analysis on real data.
3. **No silent stack changes.** Any deviation is raised with evidence and alternatives and waits for approval.

## 8. Open questions for the user

| ID | Question | Needed by |
|---|---|---|
| Q-1 | Approve the supporting-library list in §2.1? | **Resolved 2026-10-31:** approved, subject to compatibility verification |
| Q-2 | Please download the Olist dataset from Kaggle and place the CSVs in `data/raw/olist/`. | **Resolved 2026-10-31:** 9 CSVs present; headers verified |
| Q-3 | M03 Marketing: build a clearly-labelled synthetic campaign scenario model, or limit M03 to an explicit "not supported by source data" statement plus methodology? | **Resolved 2026-10-31:** both (D-015) |
| Q-4 | Create a GitHub repository (name `meridian`?) and confirm whether it should be public. `gh` CLI is not installed. | **Resolved 2026-10-31:** public, https://github.com/maayank05/meridian |
| Q-5 | Local MySQL: you will need to create `meridian_dev` / `meridian_test` databases and a non-root app user, and put credentials in a local `.env` (never in chat). Instructions will be provided in Phase 3. | Phase 3 |
| Q-7 | Approve the canonical revenue definition (D-016) | **Resolved 2026-10-31:** Option A, "Delivered Merchandise Value (Revenue Proxy)" |
| Q-6 | Production budget for hosted MySQL + Render (free tiers may lack persistence/backups). | Phase 12 |
