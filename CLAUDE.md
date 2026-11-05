# MERIDIAN — Claude Code Persistent Instructions

## Mission
Build and maintain MERIDIAN, an enterprise-style Business Intelligence & Decision Intelligence Platform for the simulated Northstar Commerce business.

## Read before work
Read `MASTER_BUILD_PROMPT.md` and all files under `instructions/`. `docs/PROJECT_SPEC.md` is the authoritative implementation specification once created.

## Approved stack
Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI, Render.

Do not replace core stack components without written approval.

## Engineering rules
- Python backend and analytics code must be modular, typed where practical, documented and testable.
- React components must not contain business calculations.
- FastAPI routers should delegate to services.
- SQL scripts must be version-controlled, ordered, repeatable where possible, and safe to re-run or explicitly documented as one-time migrations.
- Use parameterized SQL; never concatenate untrusted input into SQL.
- Use MySQL InnoDB, explicit constraints, foreign keys and indexes.
- Use UTC for stored timestamps where applicable; document source timezone conversions.
- Use `Decimal` or database DECIMAL for monetary values where precision matters.
- Centralize metric definitions and reconcile SQL, Python and Power BI.
- Use `.env.example`; never commit `.env`.
- Do not log credentials or sensitive customer-level data.
- Avoid unnecessary abstractions and dependencies.

## Analytics integrity
- Distinguish actual source observations, derived metrics, synthetic assumptions, forecasts and scenarios.
- Explicitly define denominators, time windows, eligibility rules, currency and rounding.
- Revenue is not profit.
- Correlation is not causation.
- No future leakage in historical prediction.
- Compare predictive models with a simple baseline and held-out evaluation.
- Show missingness and reconciliation differences instead of silently hiding them.

## Mandatory check loop
After every meaningful unit of work:
1. Inspect the diff.
2. Run relevant Pytest tests.
3. Run Ruff.
4. Run frontend lint/tests/build for frontend changes.
5. Run SQL/MySQL integration tests for database changes when the environment is available.
6. Fix failures and re-run.
7. Update traceability, status and quality reports.

At each phase boundary, stop and provide a checkpoint report. Never claim completion without evidence.

## Documentation maintenance
Update `docs/PROJECT_STATUS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/DECISIONS.md`, `docs/KNOWN_LIMITATIONS.md` and `docs/QUALITY_REPORT.md` whenever relevant.

## Git discipline
Use small, descriptive commits. Do not rewrite history or force-push without explicit approval. Do not commit datasets, secrets, build artifacts or generated files unless explicitly intended and permitted.

## User preference
The user wants a complete project built first and intends to learn it from the ground up afterward. Include clear learning material and walkthroughs, but do not block sound implementation on the user's current skill level.

## User-mandated enforcement rules (2026-10-31) — non-negotiable
1. Never skip testing because the application appears to work. Every phase gate needs executed tests with counts recorded in `docs/QUALITY_REPORT.md`.
2. Never create dummy charts, placeholder data or fabricated business findings to make the application look complete. No data → explicit empty state.
3. Never silently change the approved technology stack. Supporting libraries also need an entry in `docs/DECISIONS.md` and user approval before installation.

## Workflow
- Work one phase at a time per `docs/IMPLEMENTATION_PLAN.md`; stop after each phase checkpoint (`docs/checkpoints/PHASE_NN_CHECKPOINT.md`) and wait for approval.
- Decisions marked *Proposed* in `docs/DECISIONS.md` are not acted on until approved.

## Local environment notes (verified 2026-10-31)
- Use `py -3.13` — the `python` on PATH is 3.11 without pip.
- MySQL 8.0.38 runs as Windows service `MySQL80` on 3306; client binary is `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` (not on PATH).
- No Docker/WSL. Node 24 + npm 11 available.
- Olist CSVs go in `data/raw/olist/` (gitignored). Never ask for or handle DB credentials in chat; they live in local `.env`.

## Commands (Milestone A)
- Setup: `py -3.13 -m venv .venv`; `.venv\Scripts\python -m pip install --require-hashes -r requirements/requirements.txt -r requirements/requirements-dev.txt`; `.venv\Scripts\python -m pip install --no-deps --no-build-isolation -e .`
- Lint: `.venv\Scripts\ruff check .` and `.venv\Scripts\ruff format --check .`
- Tests: `.venv\Scripts\python -m pytest` (MySQL tests use meridian_test only)
- Load: `.venv\Scripts\python -m meridian.ingestion`; reconcile: `.venv\Scripts\python scripts/verify_dev_load.py`
- KPIs: `.venv\Scripts\python scripts/reconcile_kpis.py`; forecast report: `.venv\Scripts\python scripts/forecast_report.py`
- Before every push: verify the staged list and scan staged content (no .env, secrets, raw data, review text, record IDs, personal paths); LICENSE untouched.
