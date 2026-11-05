# MERIDIAN learning guide

A short tour of how the project works, with the files to read for each part. Read it with the code open.

## 1. The data pipeline (`backend/meridian/ingestion/`, `backend/sql/`)
1. **Validate before writing** (`pipeline.validate_sources`): all 9 CSVs must exist with *exactly* the expected headers (`sources.py`). Every column is read as text, so nothing is silently converted, and a SHA-256 is computed per file.
2. **One transaction** (`run_pipeline`): `00_clear.sql` → raw load → `10_staging.sql` → timezones → quality checks → `30_marts.sql` → `40_aggregates.sql`. It uses `DELETE`, not `TRUNCATE`, so any failure rolls back to the previous consistent state. The run is audited separately (`audit_ingestion_run`), so failures are recorded too.
3. **Layers.** `raw_*` keeps the source text unchanged. `stg_*` adds types and renames (and fixes the source typo `lenght`). `dim_*`/`fact_*` are the analytical model with a stated grain and foreign keys.
4. **Timezones (D-017).** Source times are São Paulo local time. `timezones.to_utc` returns `None` for the DST-ambiguous hour (fall-back) and for the non-existent hour (spring-forward), so UTC is never invented. Durations use UTC; business dates use local time.
5. **Quality gate** (`quality.py`): 27 checks. Blocking ones (orphan keys) abort the run; the others are counted in `audit_dq_result`.
6. **Migrations** (`migrations.py`): ordered `NNNN_*.sql` files recorded in `schema_version` with a checksum, so editing an applied migration is detected.

*Try it:* add a stray order-item line referencing an unknown order to a copy of the fixture and run the pipeline. It fails on `orphan_items_orders` and the database is unchanged (`test_failed_run_rolls_back_and_is_audited`).

## 2. How SQL and Python analytics are reconciled
- The **canonical definitions** are SQL views (`0004_kpi_views.sql`), e.g. K01 = item price of delivered orders by purchase month.
- `analytics/kpis.py` re-implements the same KPIs **independently** in pandas, starting from the raw CSV files (`source_frames.py`), not from the database.
- `scripts/reconcile_kpis.py` compares both on the full dataset (8 KPI families). Integration tests compare SQL, Python and **hand-calculated** values on a small synthetic fixture (`backend/tests/expected.py`).
- **Fan-out rule (RULE-06):** items and payments are each aggregated per order *before* being joined. `verify_dev_load.py` proves item-grain and order-grain totals are equal.
- `agg_*` tables are pre-computed copies of the views, for speed. A test asserts they are identical.

*Try it:* change the K01 status filter in a copy of the view and watch the fixture tests fail against `expected.py`.

## 3. How the API connects to the dashboard
- `api/routes.py` holds thin routes: parse `YYYY-MM` periods, open a **read-only** connection, call `analytics/dashboard.py`.
- `dashboard.py` assembles JSON from the aggregates and services. Every KPI carries `provenance`. The prior-period change is `null` unless every prior month is a full-coverage month.
- `api/main.py` provides the error envelope (`{"error": {code, message, request_id}}`), request IDs, JSON logs and CORS.
- Frontend: `src/services/api.ts` (single typed client) → `src/features/useApi.ts` (loading/error/success) → pages. **Components only format; they never calculate.** In development, Vite proxies `/api` to port 8000.

*Try it:* `GET http://127.0.0.1:8000/api/v1/overview?start_month=2018-03&end_month=2018-03` and compare with the Overview page.

## 4. How the forecast is evaluated (`analytics/forecast.py`)
- Series: monthly K01 over the default window only (2017-01 to 2018-08). Censored months are excluded.
- **Rolling origin:** for each of the last 6 months, fit on earlier months only, forecast one step, record the error. A guard raises if training data reaches the target month.
- Candidates: naive (last month), seasonal naive (same month last year), damped Holt (Statsmodels). The model is used **only if its MAE beats the best baseline**. On this data it does not (naive MAE 52k vs Holt 110k), so the naive forecast is shown, with an approximate interval. See `docs/analytics/FORECAST_REPORT.md`.

*Try it:* run `pytest backend/tests/unit/test_forecast.py`. On a purely seasonal synthetic series, seasonal naive wins and the model is reported as "not justified".

## 5. How the simulator works (`analytics/simulator.py`)
```
incremental revenue proxy = baseline monthly K01 × uplift × horizon months
incremental contribution  = incremental revenue proxy × contribution margin   (margin = YOUR assumption)
net benefit               = incremental contribution − intervention cost
ROI                       = net benefit / cost        (undefined if cost = 0)
break-even uplift         = cost / (baseline × horizon × margin)
```
The baseline is the observed mean monthly K01. Everything else is an assumption, so outputs are labelled **Scenario**. The campaign scenario contrasts *attributed* ROAS (credit by rule) with *incremental* ROAS (would not have happened otherwise). All arithmetic uses `Decimal`; the hand-checked cases are in `test_simulator.py`.

## 6. Reproduce the project
Follow the README: venv + hashed install → `npm ci` → create the databases ([setup guide](setup/PHASE3_PREPARATION.md)) → `.env` → `python -m meridian.ingestion` → `verify_dev_load.py` and `reconcile_kpis.py` (all must match) → `pytest` → run the API and `npm run dev`. To reproduce the Phase 2 profiling reports byte-for-byte, see `scripts/profiling/README.md`.

## Glossary
**Grain:** what one row represents. **Fan-out:** row multiplication from joining one-to-many tables, which double-counts sums. **Provenance:** whether a value is observed, derived, synthetic, forecast or scenario. **Right-censoring:** recent orders not yet delivered when the data was extracted, which makes the last months look artificially low. **Baseline:** the simple method a model must beat to be worth using.
