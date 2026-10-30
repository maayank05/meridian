# 05 — Non-Functional Requirements

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

NFR IDs come from `instructions/02`. Each NFR has measurable acceptance criteria and a planned verification method. Thresholds marked *(proposed)* are starting targets and get confirmed when the relevant phase measures real behaviour.

| NFR ID | Category | Requirement | Measurable acceptance criteria | Verification (planned) | Phase |
|---|---|---|---|---|---|
| NFR-001 | Security | Secrets in env vars / secret manager; none in Git | 0 secret-pattern hits in tracked files and history; `.env` ignored; DB user is not root; frontend bundle contains no DB credentials | Secret scan in CI; `git check-ignore`; bundle grep | 3, 12 |
| NFR-002 | Reliability | Clear failure modes, transaction boundaries, retries where appropriate | Multi-step writes are atomic (partial-failure test leaves no partial rows); readiness returns 503 when DB unreachable | MySQL integration and API tests | 3, 8 |
| NFR-003 | Performance | Paginate large responses; aggregate in MySQL; no full-table loads into API memory | List endpoints enforce max page size *(proposed 500)*; p95 latency for summary endpoints on full dataset *(proposed < 1.5 s locally)* measured, not assumed | API tests; timing script against local full load | 8 |
| NFR-004 | Maintainability | Layered backend, reusable services, readable SQL, modular React | Route handlers contain no SQL (static check); React components contain no metric formulas (review + lint rule where feasible) | Code review checklist; grep-based test | 8, 9 |
| NFR-005 | Testability | Unit, integration, API, SQL, frontend, E2E smoke tests | Each of the 7 layers in TEST_STRATEGY has ≥1 executed suite before release | QUALITY_REPORT counts | 3–12 |
| NFR-006 | Accessibility | Semantic markup, keyboard navigation, contrast, labels | All interactive controls keyboard reachable; text contrast ≥ 4.5:1; status never by colour alone | Component tests + automated a11y check *(tool to be proposed in Phase 9)* | 9 |
| NFR-007 | Observability | Structured logs without secrets or unnecessary customer data | JSON logs with request id; test asserts no customer/seller identifiers or credentials in log output | API log-capture test | 8 |
| NFR-008 | Reproducibility | Pinned dependencies; deterministic fixtures | Hashed lockfiles; fixtures checked in; same input → same output checksum across two runs | Lockfile presence; rebuild determinism test | 3 |
| NFR-009 | Portability | Documented local setup and Render deployment | Clean-clone setup on a second directory succeeds using docs only; Render deploy follows runbook | Phase 13 clean-clone log; Phase 12 runbook execution | 12, 13 |
| NFR-010 | Data integrity | MySQL constraints, referential integrity, reconciliation | PK/FK/unique constraints on all modelled tables (or documented exceptions for source orphans); row-count and amount reconciliation raw → stg → fact | MySQL integration and reconciliation tests | 3, 4 |
