# 12 — GitHub, Repository and Portfolio Delivery

## Suggested repository layout
```text
meridian/
├── CONTRIBUTING.md
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml              # optional local MySQL only if useful
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── analytics/
│   ├── sql/
│   │   ├── migrations/
│   │   ├── staging/
│   │   ├── marts/
│   │   └── reports/
│   ├── ingestion/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/
│   │   ├── types/
│   │   └── styles/
│   └── tests/
├── powerbi/
│   ├── README.md
│   ├── model_specification.md
│   ├── dax_measures.md
│   ├── report_design.md
│   └── reconciliation.md
├── business/
├── docs/
│   ├── architecture/
│   ├── data/
│   ├── testing/
│   ├── deployment/
│   ├── PROJECT_SPEC.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROJECT_STATUS.md
│   ├── REQUIREMENTS_TRACEABILITY.md
│   ├── DECISIONS.md
│   ├── KNOWN_LIMITATIONS.md
│   └── QUALITY_REPORT.md
├── learning/
├── reports/
├── scripts/
├── tests/
└── .github/workflows/
```
Adapt only with a documented reason. Do not create empty folders just to match the diagram.

## Git practices
- Initialize repository if not already initialized.
- Use descriptive branch names and small commits.
- Suggested commit format: `feat(customer): add cohort retention endpoint`.
- Do not commit full Olist data unless license and redistribution rights explicitly permit.
- Include data acquisition instructions and small permitted fixtures.
- Never commit secrets, local virtual environments, caches or build output.
- Do not force push or rewrite history without permission.

## README
Include:
- Product overview and business problem.
- Architecture diagram.
- Actual screenshots.
- Modules and implementation status.
- Stack.
- Data sources and licensing.
- Setup and data acquisition.
- Database setup and migrations.
- Pipeline run instructions.
- API and frontend run instructions.
- Tests and CI.
- Deployment and persistence notes.
- Actual findings only after validated analysis.
- Scenario examples clearly labelled hypothetical.
- Known limitations and future work.

## GitHub Actions
Run tests and Ruff on backend; frontend lint/test/build; SQL validation/integration checks feasible without secrets. Use fixtures. Do not download full datasets on every CI run. Use MySQL service container only if supported/reliable in workflow; otherwise separate integration job with documented service.

## Portfolio evidence
Capture genuine screenshots after the feature works. Include architecture, ERD, data lineage, API docs screenshot, Power BI screenshots and test/CI status. Never fake GitHub badges or success indicators.
