# MERIDIAN — Claude Implementation Pack

This pack instructs Claude Code to build MERIDIAN from an empty repository into a tested, documented, deployable analytics product.

## Before starting

1. Create/open a dedicated Git repository named `meridian`.
2. Put this entire pack in the repository root, preserving the `instructions/` folder.
3. Open the repository in Claude Code.
4. Give Claude the full contents of `MASTER_BUILD_PROMPT.md` (or tell it to read that file first).
5. Ensure Claude has permission to inspect and edit the repository. Do not provide production credentials in chat.
6. Work phase-by-phase. Do not ask Claude to generate the entire application in one unreviewed pass.

## Files in this pack

- `MASTER_BUILD_PROMPT.md` — the initial instruction to Claude.
- `CLAUDE.md` — persistent repository rules.
- `instructions/01_PROJECT_CHARTER.md` — business case and scope.
- `instructions/02_REQUIREMENTS_AND_ACCEPTANCE.md` — functional and non-functional requirements.
- `instructions/03_ARCHITECTURE.md` — approved technical architecture.
- `instructions/04_DATA_AND_MYSQL.md` — Olist data strategy, modelling, ingestion and persistence.
- `instructions/05_ANALYTICS_MODULES.md` — ten business/analytics modules.
- `instructions/06_API_CONTRACTS.md` — FastAPI requirements and API contract guidance.
- `instructions/07_REACT_FRONTEND.md` — frontend pages, UX and integration requirements.
- `instructions/08_POWER_BI.md` — Power BI model, measures and reconciliation.
- `instructions/09_TESTING_AND_QUALITY_GATES.md` — testing, Ruff, CI and mandatory checkpoints.
- `instructions/10_SECURITY_DEPLOYMENT.md` — Render deployment, persistent MySQL, secrets and operations.
- `instructions/11_BUSINESS_ANALYSIS_ARTIFACTS.md` — BRD, user stories, process maps, RAID and traceability.
- `instructions/12_GITHUB_AND_DELIVERY.md` — repository structure, issues, commits, README and release standards.
- `instructions/13_LEARNING_GUIDE_REQUIREMENTS.md` — make the finished project teachable from scratch.
- `instructions/14_PHASE_PLAN_AND_CHECKPOINTS.md` — execution order and review gates.
- `instructions/15_STATUS_TEMPLATES.md` — living project status, quality and decision logs.

## Important stack decision

The approved stack is exactly:

Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI and Render.

Do not silently substitute PostgreSQL, DuckDB, dbt, Streamlit, or another database/application stack. If a genuine technical blocker requires a change, stop and present evidence plus alternatives for approval.

## Human review rule

Claude must pause after each phase and provide a concise checkpoint report. Do not allow it to mark a phase complete based on generated files alone. It must run the available checks and show evidence.
