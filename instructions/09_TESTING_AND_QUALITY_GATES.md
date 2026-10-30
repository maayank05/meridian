# 09 — Testing, Quality and Review Gates

## Required test layers
1. Python unit tests: metric functions, transformations, statistics, scenarios.
2. Data tests: schema, keys, relationships, nulls, ranges, reconciliation.
3. MySQL integration tests: migrations, queries, transactions and repository methods.
4. API tests: FastAPI routes, validation, error handling and response contracts.
5. Frontend tests: components, filters, empty/error states and page behaviour.
6. End-to-end smoke tests: critical user journeys.
7. Deployment smoke tests: live health, frontend loading, API connectivity and DB persistence.

## Pytest
- Use fixtures with small deterministic datasets.
- Test expected values and edge cases.
- Include invalid and missing data.
- Test duplicate joins and double-counting.
- Test financial formulas with hand-calculated expected outputs.
- Use separate test database/schema. Never run destructive tests against production.

## Ruff
Configure Ruff for linting and formatting. Run it in CI. Do not silence rules broadly. If an exception is needed, make it narrow and documented.

## Mandatory gate commands
Document exact commands after selecting package manager. Typical examples:
- `pytest`
- `ruff check .`
- `ruff format --check .`
- frontend test command
- frontend production build command
- SQL migration/integration test command

Do not assume commands exist before configuring them.

## Phase gate
A phase passes only if:
- Acceptance criteria are met.
- Relevant tests were executed.
- No critical test is skipped without explanation.
- Lint/build checks pass or deviations are explicitly approved.
- Traceability and status documents are updated.
- Known limitations are recorded.
- A human-readable evidence report exists.

## Checkpoint report template
### Phase:
### Scope:
### Files changed:
### Commands run:
### Test results:
### Acceptance criteria evidence:
### Defects:
### Limitations:
### Traceability updated:
### Status: PASS / PASS WITH DOCUMENTED LIMITATIONS / BLOCKED
### Approval requested:
