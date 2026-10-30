# 06 — FastAPI Backend Requirements

## API standards
- Version routes under `/api/v1`.
- Use Pydantic request/response schemas.
- Validate all query parameters and payloads.
- Parameterize SQL.
- Return consistent error envelopes and appropriate HTTP status codes.
- Paginate potentially large lists.
- Use explicit date formats/timezones and currency metadata.
- Add OpenAPI documentation.
- Add `/health` and readiness endpoint that verifies critical dependencies safely.
- Add request IDs and structured logging.
- Configure CORS to exact frontend origins.
- Do not expose stack traces or database credentials.

## Suggested endpoint groups
- `/api/v1/health`
- `/api/v1/metadata/sources`
- `/api/v1/metadata/metrics`
- `/api/v1/filters`
- `/api/v1/executive/summary`
- `/api/v1/executive/trends`
- `/api/v1/customers/segments`
- `/api/v1/customers/cohorts`
- `/api/v1/products/performance`
- `/api/v1/operations/delivery`
- `/api/v1/finance/reconciliation`
- `/api/v1/scenarios/compare`
- `/api/v1/forecasting/summary`
- `/api/v1/quality/summary`
- `/api/v1/reports/executive`

These are proposed endpoints; refine based on actual UI needs. Document request/response examples and filter semantics.

## Backend architecture
Use routers → services → repositories → MySQL. Keep analytics calculations in reusable Python modules. Do not make the frontend construct SQL.

## Database access
- Use a maintained MySQL driver and connection pool.
- Read credentials from environment variables.
- Apply connection timeout and pool limits.
- Use transactions for multi-step writes.
- Use read-only database credentials for read/reporting paths where practical.
- Use migrations or ordered SQL migration scripts with a schema version table.

## API tests
Test successful, invalid, missing, empty, boundary, unauthorized (if auth enabled), database unavailable and unexpected error cases. Use deterministic fixtures and MySQL integration tests.
