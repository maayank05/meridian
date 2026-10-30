# Security

Last updated: 2026-10-31 (Phase 0 — policy; controls implemented in later phases)

## Secrets
- Local secrets live only in `.env` (gitignored; rule verified present in [.gitignore](../.gitignore)). `.env.example` with placeholders will be added in Phase 3.
- Production secrets live in Render / DB-provider secret configuration only.
- Credentials are never pasted into chat, logged, echoed in errors, or placed in frontend (`VITE_*`) variables.
- Any credential accidentally committed is rotated immediately; history rewriting needs explicit user approval.

## Database
- Separate credentials per environment (dev, test, prod) and per role: admin/migration user vs least-privilege app user vs read-only reporting user (Power BI).
- Root MySQL account is not used by the application.
- All SQL uses bound parameters; no string concatenation of user input. Identifiers (e.g. sort columns) come from allow-lists.
- TLS required for any non-local MySQL connection.
- Production DB is never exposed publicly to make Power BI refresh work.

## API
- Pydantic validation on all inputs; bounded pagination.
- Consistent error envelope; no stack traces or DB errors returned to clients.
- CORS restricted to exact frontend origins.
- Request IDs and structured logs with no secrets and no customer-level identifiers.
- Rate limiting on public endpoints (mechanism to be chosen in Phase 8 — will be a documented decision).
- Authentication required if any administrative function (e.g. ingestion trigger) is exposed; otherwise such functions are CLI-only.

## Data
- Raw Olist files are never committed (licence + size). Olist identifiers are already anonymised hashes, but customer-level rows are still kept out of logs and screenshots.
- Synthetic data is labelled and kept in `scenario_*` tables.

## Dependencies
- Pinned via lockfiles; periodic `pip-audit`/`npm audit` review is proposed for Phase 12 (would be a new dev tool — requires approval).

## Verification status
| Control | Status | Evidence |
|---|---|---|
| `.env` gitignored | Implemented | `.gitignore` lines 2–4 |
| Secret scan of repository | Not started | — |
| Parameterized SQL | Not started | — |
| CORS restriction | Not started | — |
| Error envelope | Not started | — |
