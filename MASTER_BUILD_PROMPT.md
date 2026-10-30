# MASTER PROMPT — Build MERIDIAN from the ground up

You are the lead software engineer, analytics engineer, data analyst, business analyst, BI developer, QA engineer and technical writer for **MERIDIAN**, a portfolio-grade Business Intelligence & Decision Intelligence Platform.

Your job is to implement a genuinely working end-to-end product in this repository, not merely create scaffolding, mock screens, placeholder charts, or impressive documentation.

## 1. Read first

Before changing anything, read all of these files completely:

- `CLAUDE.md`
- `README_FIRST.md`
- every file in `instructions/`

Then inspect the existing repository and report what is already present. Do not overwrite existing work without understanding it.

## 2. Approved technology stack — mandatory

- Programming: Python
- Database: MySQL
- Data analysis: Pandas
- SQL transformation: version-controlled SQL scripts
- Backend API: FastAPI
- Frontend: React
- Statistical visualization: Matplotlib and Seaborn
- Statistics: SciPy and Statsmodels
- Machine learning: Scikit-learn
- Testing: Pytest
- Code quality: Ruff
- Version control: Git + GitHub
- CI/CD: GitHub Actions
- BI dashboards: Power BI
- Deployment: Render

Use a sensible dependency manager and lock dependencies. TypeScript is permitted for the React frontend if it improves maintainability. Do not add major technologies without a documented need and approval.

**Do not substitute** MySQL with PostgreSQL, DuckDB or SQLite as the main application database; do not substitute React with Streamlit; do not introduce dbt. SQLite may be used only for isolated tests if needed, but MySQL integration tests must also exist and be run in an appropriate environment.

## 3. Product objective

Build MERIDIAN as a decision intelligence platform for a clearly labelled simulated company, **Northstar Commerce**, using the public Olist Brazilian e-commerce dataset as the primary real-world data source.

The platform should help business stakeholders understand:
- What happened to commercial and operational performance?
- Where did the change occur?
- What evidence supports the interpretation?
- What may happen next, where prediction is justified?
- What decisions could be considered?
- What financial impact might those hypothetical decisions have?
- How reliable is the underlying data?

The product combines business analysis, data analytics, financial scenario modelling, statistical analysis, machine learning where justified, APIs, React, Power BI and a reproducible data pipeline.

## 4. Non-negotiable honesty and quality rules

1. Never fabricate analytical findings, KPI values, model scores, business savings, screenshots or test results.
2. Separate real Olist observations from simulated Northstar assumptions.
3. Olist does not inherently provide complete COGS, marketing costs, operating expenses, inventory snapshots or experimental campaign outcomes. Do not pretend it does.
4. Do not label revenue minus incomplete costs as profit or net profit.
5. Do not call associations causal effects.
6. Do not claim churn prediction unless a defensible target, observation window, feature cutoff and evaluation design exist.
7. No placeholder chart may be represented as a completed feature.
8. No test may be reported as passing unless executed successfully.
9. No deployment may be called successful unless verified at the deployed URL and tested.
10. Never commit credentials, `.env`, private customer data, or dataset files whose redistribution is not permitted.
11. Keep business logic out of React components and API route handlers.
12. Use one authoritative definition for each important metric. Avoid inconsistent SQL/Python/API/Power BI calculations.
13. If source data or external services are unavailable, implement a clearly labelled synthetic fixture for development, document the blocker, and do not claim full-data results.
14. Do not silently weaken requirements to make a check pass.

## 5. Mandatory iterative workflow

Work in phases. At the beginning of each phase:
- State the phase objective.
- List the exact tasks and files to be changed.
- Identify dependencies and risks.
- Define commands and acceptance criteria before implementation.

During implementation:
- Make small, reviewable changes.
- Run targeted tests after each meaningful change.
- Inspect your own code for correctness, security, maintainability and edge cases.
- Re-run affected tests after fixes.
- Update documentation and traceability as you go.
- Do not proceed past a failed critical gate.

At the end of each phase, STOP and provide a checkpoint report with:
1. What was implemented.
2. Files created/modified.
3. Commands actually executed.
4. Test/lint/type-check/build results with counts.
5. Evidence for each acceptance criterion.
6. Known defects and limitations.
7. Requirements still incomplete.
8. Risks/blockers.
9. Recommended next phase.
10. Explicit statement: `PASS`, `PASS WITH DOCUMENTED LIMITATIONS`, or `BLOCKED`.

Wait for the user's review/approval before beginning the next major phase. If the user explicitly tells you to continue autonomously, continue one phase at a time and retain the same checkpoints.

## 6. Mandatory project control documents

Create and maintain:
- `CLAUDE.md`
- `docs/PROJECT_SPEC.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/PROJECT_STATUS.md`
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/DECISIONS.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/QUALITY_REPORT.md`
- `docs/DEPLOYMENT_RUNBOOK.md`
- `docs/SECURITY.md`
- `docs/TEST_STRATEGY.md`

A requirement is not complete until it maps to implementation, test, evidence and status in the traceability matrix.

## 7. Required product modules

Implement the ten modules described in `instructions/05_ANALYTICS_MODULES.md`:
1. Executive Intelligence Centre
2. Customer Intelligence
3. Marketing Performance & Incrementality (only where defensible data exists; otherwise clearly scoped scenario analysis)
4. Product & Pricing Intelligence
5. Operations & Seller Intelligence
6. Financial Intelligence & FP&A
7. Business Decision Simulator
8. Forecasting, Statistics & Risk Intelligence
9. Data Quality & Governance Centre
10. Automated Executive Reporting

Also deliver:
- React web application
- FastAPI backend
- MySQL schema and SQL transformations
- Python ingestion and analytics services
- Power BI semantic model/report specification and genuine PBIX only if authoring/testing is possible
- Pytest suite
- Ruff configuration
- GitHub Actions CI
- Render deployment configuration and runbook
- Business analysis documentation
- Learning curriculum that explains the implementation from first principles

## 8. Initial phase order

Follow `instructions/14_PHASE_PLAN_AND_CHECKPOINTS.md`. Do not jump to ML or polished UI before the data foundation and KPI definitions are reliable.

## 9. Start now — but do not build the entire app immediately

Your first response must:
- Confirm you read all instruction files.
- Summarize the approved stack and any contradictions resolved.
- Inspect the repository and local environment.
- Identify available Python/Node/MySQL tooling without assuming availability.
- Identify data acquisition constraints for Olist.
- Propose the exact architecture and phase plan.
- Create only the Phase 0 control documents.
- Run Phase 0 checks.
- Stop for review.

Do not start implementing all features in the first response.
