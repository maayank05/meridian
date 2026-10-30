# 03 — Approved Architecture

## Technology
Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI, Render.

## Logical flow
Olist CSV files / labelled scenario assumptions
→ Python ingestion and validation
→ MySQL raw/staging/analytical schemas or clearly separated table prefixes
→ version-controlled SQL transformations
→ Python analytics services
→ FastAPI endpoints
→ React interface

Power BI connects to approved analytical views/tables using a documented supported connection mode. Do not assume Render's private networking is automatically accessible from Power BI Desktop or Power BI Service; verify connectivity and refresh constraints.

## Backend layering
- `api/`: FastAPI app, routers, dependencies, middleware and schemas.
- `services/`: orchestration and use-case logic.
- `repositories/`: parameterized database access.
- `analytics/`: reusable Pandas/statistics/ML calculations.
- `db/`: connection/session handling and migrations.
- `config/`: settings and environment validation.

Routes should be thin. Do not embed complex SQL, statistical calculations or business rules inside route handlers.

## Frontend layering
- `src/app/`: router and application shell.
- `src/pages/`: business module pages.
- `src/components/`: reusable cards, tables, filters, charts and states.
- `src/features/`: module-specific UI and API hooks.
- `src/services/`: typed API client.
- `src/types/`: shared API contracts.
- `src/styles/`: design tokens and global styles.

Choose a maintained React build tool after checking current compatibility. TypeScript is recommended for frontend reliability. Do not add a state-management library unless actual complexity warrants it.

## Database principles
- MySQL InnoDB.
- Use DECIMAL for financial values where exact decimal representation matters.
- Explicit PK/FK, uniqueness and check constraints where supported by selected MySQL version.
- Index join keys, filter columns and common time dimensions based on measured query plans.
- Use parameterized queries.
- Separate raw, staging and mart objects logically.
- Version SQL scripts and document execution order.
- Prefer safe, repeatable migrations; destructive reset scripts must be clearly labelled and never run automatically in production.
- Store timestamps consistently and document source timezone assumptions.

## Analytics principles
- One canonical definition per KPI.
- Use Pandas for data preparation/analysis where appropriate.
- Use SciPy and Statsmodels only for methods with justified assumptions.
- Use Scikit-learn only with baseline comparison and proper validation.
- Matplotlib/Seaborn are for analytical plots/reports; React visualizations must use a compatible charting approach only if selected and documented. Do not force Matplotlib into the browser.

## Deployment topology
- React frontend deployed as a Render Static Site or suitable web service.
- FastAPI deployed as a Render Web Service.
- MySQL hosted on a persistent managed MySQL provider that is reachable securely from Render.
- Do not assume Render itself offers a native managed MySQL product. Compare current supported providers, pricing, backups, regions, networking and free-tier limitations before selection.
- Keep database private where possible; allow only required application connectivity.
- Configure CORS narrowly.
- Use health/readiness endpoints.
