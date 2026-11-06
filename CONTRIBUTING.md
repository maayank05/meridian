# Contributing to MERIDIAN

Engineering and analytics rules for anyone changing this project. Setup and run commands are in the [README](README.md).

## Approved stack
Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI, Render.

Core components are not replaced without a recorded decision. A new supporting library needs an entry in [docs/DECISIONS.md](docs/DECISIONS.md) before it is installed.

## Engineering rules
- Python backend and analytics code is modular, typed where practical, documented and testable.
- React components contain no business calculations.
- FastAPI routes validate input and delegate to services.
- SQL scripts are version-controlled and ordered; migrations run once (`schema_version`), transforms are safe to re-run.
- SQL is parameterised; untrusted input is never concatenated into SQL.
- MySQL tables use InnoDB, explicit constraints, foreign keys and indexes.
- Stored timestamps are UTC; source timezone conversions are documented (D-017).
- Money uses Python `Decimal` or MySQL `DECIMAL`, rounded only for display (RULE-08).
- Each metric has one definition (the `vw_*` views), reconciled across SQL, Python and Power BI.
- `.env.example` documents settings; `.env` is never committed.
- Credentials and customer-level data are never logged.
- No unnecessary abstractions or dependencies.

## Analytics integrity
- Every number is labelled as observed, derived, synthetic assumption, forecast or scenario.
- Denominators, time windows, eligibility rules, currency and rounding are stated explicitly.
- Revenue is not profit. Correlation is not causation.
- No future leakage in historical prediction; models are compared with a simple baseline on held-out data.
- Missing data and reconciliation differences are shown, never silently hidden.
- No dummy charts, placeholder data or fabricated findings: no data means an explicit empty state.

## Check loop
After every meaningful change:
1. Inspect the diff.
2. Run the relevant tests: `.venv\Scripts\python -m pytest` (MySQL tests use `meridian_test` only).
3. Run Ruff: `.venv\Scripts\ruff check .` and `.venv\Scripts\ruff format --check .`
4. For frontend changes, from `frontend/`: `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build`, and `npm run e2e` where the dataset is available.
5. For database changes, run the MySQL integration tests and `scripts/verify_dev_load.py` / `scripts/reconcile_kpis.py`.
6. Fix failures and re-run. Never weaken a test to make it pass.
7. Update [PROJECT_STATUS](docs/PROJECT_STATUS.md), [REQUIREMENTS_TRACEABILITY](docs/REQUIREMENTS_TRACEABILITY.md), [DECISIONS](docs/DECISIONS.md), [KNOWN_LIMITATIONS](docs/KNOWN_LIMITATIONS.md) and [QUALITY_REPORT](docs/QUALITY_REPORT.md) where relevant.

## Git discipline
- Small, descriptive commits. No history rewrites or force-pushes.
- Before every push, check the staged file list and content: no `.env`, secrets, raw data, review text, record IDs or personal paths. `LICENSE` stays unchanged.

## Local environment notes (Windows)
- Use `py -3.13` to create the virtual environment.
- MySQL 8.0 runs as the Windows service `MySQL80` on port 3306; the client is `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`.
- Olist CSVs go in `data/raw/olist/` (gitignored). Database credentials live only in the local `.env`.
- Ports: 8000 (API), 5173 (dashboard dev server), 5180 (E2E tests).
