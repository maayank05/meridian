# Phase Checkpoint — Milestone C (Phases 8, 9, 11: API, React app, executive report)
Date: 2026-11-06
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## Delivered
- **FastAPI** (`backend/meridian/api/`): `/api/v1` health, ready, metadata, overview, customers, products, operations, quality, forecast, simulator (compare, campaign), reports/executive. Thin routes over `analytics/dashboard.py`. Read-only DB account, error envelope (no stack traces or SQL), request IDs, JSON access logs, narrow CORS, Pydantic-validated inputs, OpenAPI at `/docs`.
- **React app** (`frontend/`, Vite + TypeScript + Recharts): Overview (KPIs, honest comparison, trend with flagged months, forecast verdict), Customers (repeat rate, concentration, cohort retention), Products & Operations, Decision Simulator (scenario + synthetic campaign), Data Quality & Methods. Loading, error-with-retry and empty states; provenance badges on everything; URL-based period filter with validation and reset; dark mode; responsive.
- **Executive report** (`meridian/reporting/executive.py`): HTML with a Matplotlib chart, built from the same payloads as the API; descriptive observations only; limitations section.
- **Performance layer:** migrations 0005/0006, `agg_*` tables refreshed from the canonical views each load.
- **Screenshots** (real data): `docs/screenshots/*.png`.

## Evidence (commands actually run)
| Check | Result |
|---|---|
| `ruff check .` / `ruff format --check .` | Pass |
| `pytest` | **112 passed, 0 failed, 0 skipped** |
| Frontend `lint` / `typecheck` / `test` / `build` | Pass / pass / **8 passed** / built (no mock data in bundle) |
| Playwright E2E (real API, full dataset) | **7 passed** |
| Full data after aggregates | verify_dev_load 28/28, reconcile_kpis 8/8, agg = view for all 7 aggregates |
| Report vs API | `test_executive_report_matches_api`: identical payloads |

## Defects found and fixed
1. **Misleading growth figure:** +32,469% against a prior period mostly outside the data. Changes now require a fully covered prior period (RULE-22/25).
2. **MAPE = infinity** when an actual is 0, which produced invalid JSON. It is now null.
3. **Cohort table conflated a real 0% with unobservable months.** The API now returns an observable horizon.
4. **Endpoints took 11–13 s** on full data. Aggregates and indexes bring them to 0.01–0.26 s; customers is 1.82 s.
5. **Periods were not month-aligned** (prior period started mid-month). Now whole months.
6. Smaller issues: numbers mixed locale formats; `useApi` set state synchronously inside an effect; test-helper and locator issues.

## Limitations
L-C01 to L-C07 in [KNOWN_LIMITATIONS](../KNOWN_LIMITATIONS.md): customers endpoint 1.8 s (target 1.5 s), load time about 9 minutes, period-only filters, HTML-only report and no authentication, 680 kB bundle, dev-only npm advisory, no automated accessibility audit.

## Next
Milestone D: GitHub Actions CI (backend + frontend), README with these screenshots, short learning guide, Power BI spec + DAX, clean-clone reproducibility check.
