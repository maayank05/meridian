# 14 — Phase Plan and Mandatory Checkpoints

Claude must complete phases in order. Each phase ends with a report and a pause for approval unless the user explicitly authorizes autonomous continuation.

## Phase 0 — Repository and environment audit
- Inspect repository, Git status and existing code.
- Check Python, package manager, Node, npm/pnpm, MySQL client/server, Power BI availability and Render constraints.
- Check compatibility and versions; do not assume.
- Confirm data acquisition path and licensing review plan.
- Create control documents only.
- Gate: architecture and feasibility understood.

## Phase 1 — Business analysis and specification
- Business case, stakeholders, BRD/FRD, user stories, acceptance criteria, business rules, KPI dictionary, assumptions, RAID and traceability.
- Gate: every proposed metric has a valid source or is explicitly marked unsupported/simulated.

## Phase 2 — Dataset discovery and profiling
- Acquire Olist manually or through approved method.
- Profile all files, types, keys, dates, missingness, duplicates, relationships and licensing.
- Create data dictionary, profiling report and test fixtures.
- Gate: data model based on observed schema, not guessed schema.

## Phase 3 — MySQL design and ingestion
- Create schema, migrations, ingestion scripts, raw/staging layers, audit tables and SQL transformations.
- Test clean load, repeat load, partial failure and rebuild.
- Gate: valid fixture ingestion, relationship checks, reconciliation and deterministic rebuild.

## Phase 4 — Core SQL analytics
- Revenue/order trends, product/category, customer purchase, repeat purchase, cohort, seller, delivery, reviews and period comparisons.
- Compare SQL results to independent expected values on controlled fixtures.
- Gate: key metrics reconcile and no join fan-out/double counting.

## Phase 5 — Python analytics services
- Reusable Pandas and Python metrics, customer/product/operations/financial functions, quality checks and report generation.
- Gate: unit tests, edge cases and SQL/Python reconciliation.

## Phase 6 — Statistics and ML
- Identify valid analytical questions.
- Establish baselines.
- Use SciPy/Statsmodels/Scikit-learn where justified.
- Chronological validation for time series.
- Document uncertainty and limits.
- Gate: no leakage, held-out evaluation and meaningful comparison.

## Phase 7 — Decision simulator
- Scenario models, break-even, sensitivity, base/upside/downside.
- Separate assumptions from observed data.
- Gate: hand-calculated tests and financial terminology review.

## Phase 8 — FastAPI
- Database integration, service/repository layers, API schemas, endpoints, error handling and tests.
- Gate: API integration tests and OpenAPI review.

## Phase 9 — React application
- Shell, navigation, module pages, filters, charts, tables, error/empty/loading states and accessibility.
- Gate: frontend test/lint/build and end-to-end smoke tests.

## Phase 10 — Power BI
- Semantic model, DAX, report layout, data connection, refresh constraints and reconciliation.
- Gate: real report artifact verified or clearly documented as requiring Power BI Desktop authoring.

## Phase 11 — Reporting and governance
- HTML executive report, UAT pack, final BA artifacts, decision/quality/limitations logs.
- Gate: report calculations match app/API.

## Phase 12 — CI/CD and deployment
- GitHub Actions, Render frontend/backend, persistent managed MySQL, secrets, backups, health checks and restore test.
- Gate: live deployment smoke-tested; data persists after redeploy; restore procedure proven.

## Phase 13 — Portfolio and learning package
- README, screenshots, diagrams, demo script, architecture, learning curriculum and interview guide.
- Gate: clean-clone reproducibility and honest completion audit.

## Required checkpoint cadence
- Before phase: scope, risks, files, tests and acceptance criteria.
- Mid-phase: after each substantial subsystem, inspect diff and run targeted checks.
- End phase: checkpoint report and approval pause.
- If a critical test fails: stop feature expansion, diagnose, fix and rerun.
- If a requirement cannot be completed: mark BLOCKED/DEFERRED with reason, impact, workaround and next action.
