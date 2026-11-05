# Phase Checkpoint — Milestone B (Phases 4–7: analytics, services, forecast, simulator)
Date: 2026-11-06
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## Delivered
- **Canonical KPI views** (migration `0004`): `vw_kpi_monthly` (K01–K06, K12, K21, K23, K26), `vw_kpi_category_monthly` (K11), `vw_kpi_delivery_monthly` (K14–K16), `vw_kpi_reviews_monthly` (K13), `vw_kpi_payments_monthly` (K19/K20), `vw_payment_reconciliation` (K18), `vw_cohort_retention` (K08). All use D-016 to D-019 definitions, RULE-25 coverage flags, and no fan-out.
- **Independent Python KPIs** from raw CSVs (`analytics/source_frames.py`, `analytics/kpis.py`).
- **Services** (`analytics/services.py`): period summary with equal-length prior period (RULE-22), K07 repeat rate, K10/K22 concentration, K25 forecast.
- **Forecast** (`analytics/forecast.py`): rolling-origin evaluation vs naive and seasonal-naive baselines; [FORECAST_REPORT](../analytics/FORECAST_REPORT.md).
- **Decision simulator** (`analytics/simulator.py`): base/upside/downside, sensitivity, break-even, payback, ROI on an assumed contribution margin; M03 synthetic campaign scenario (attributed vs incremental ROAS).
- **Scripts:** `scripts/reconcile_kpis.py`, `scripts/forecast_report.py`.

## Evidence (commands actually run)
| Check | Result |
|---|---|
| `ruff check .` / `ruff format --check .` | Pass |
| `pytest` | **81 passed, 0 failed, 0 skipped** (unit, MySQL integration, profiling) |
| Fixture: SQL views = hand-calculated = Python KPIs | All 7 view families (test_kpi_views_mysql.py) |
| Full data: `scripts/reconcile_kpis.py` | **8 KPI families matched, 0 differed** (25 months, 74 categories, 219 cohort cells) |
| Forecast on D-018 window | Naive MAE 52,304; damped Holt 110,180; seasonal naive 469,935 → **model not justified**, naive used |
| Simulator | 15 hand-calculated tests incl. US-022 (cost 1,000, benefit 1,500 → ROI 0.50, net 500), zero-cost ROI undefined |

## Acceptance (lean Milestone B)
| Criterion | Evidence |
|---|---|
| Core SQL analytics for approved KPIs | Migration 0004; fixture and full-data reconciliation |
| Python analytics services | services.py; test_services_on_fixture |
| SQL/Python reconciliation | reconcile_kpis.py 8/8; integration tests compare all three (SQL, Python, hand) |
| One forecast with baseline and chronological validation | test_forecast.py (leakage guard, baselines); report |
| Compact simulator: baseline, scenarios, sensitivity, break-even | test_simulator.py |
| No complex ML without defensible improvement | None used; Holt itself did not beat naive (D-021) |

## Defects found and fixed
Test helper used `DROP TABLE` on views; a real `date - pd.Timedelta` bug in `period_summary`; my own wrong expected value in a forecast test (85, not 115); the leakage guard used `assert` (stripped under `-O`), now an explicit error. Details in [QUALITY_REPORT](../QUALITY_REPORT.md).

## Limitations
L-B01 to L-B04 in [KNOWN_LIMITATIONS](../KNOWN_LIMITATIONS.md): the forecast is not better than naive; K09 RFM and K17 deferred; MySQL `SUM()` counts are DECIMAL; simulator outputs depend on synthetic assumptions. No KPI values are presented as business findings yet; the executive report comes in Milestone C.

## Next
Milestone C: FastAPI endpoints over these views and services, React dashboard (about 5 pages), concise executive report.
