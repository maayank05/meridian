# Forecast Report: K25 (Delivered Merchandise Value, monthly)

Generated 2026-11-05 21:51 UTC by `scripts/forecast_report.py` from `meridian_dev` (provenance: **forecast**).
Forecasts are estimates, not observations. Values are BRL; revenue proxy only, not accounting revenue or profit (D-016).

## Design
- **Series:** monthly K01 over the D-018 window 2017-01 to 2018-08 (20 months). Censored months (2018-09/10) and low-coverage 2016 months are never used (RULE-25).
- **Evaluation:** rolling origin, one-step-ahead, over the last 6 months (2018-03 to 2018-08). Each forecast is fitted only on earlier months; an assertion enforces this (unit-tested).
- **Candidates:** naive (last month), seasonal naive (same month last year), damped additive Holt (Statsmodels). The model is "justified" only if its MAE beats the best baseline.

## Results (one-step errors, test months)
| Method | MAE | RMSE | MAPE |
|---|---:|---:|---:|
| naive | 52,304 | 73,360 | 5.8% |
| damped_holt | 110,180 | 132,725 | 12.6% |
| seasonal_naive | 469,935 | 484,807 | 51.1% |

**The damped Holt model did NOT beat the best baseline (naive).** A statistical model is therefore not justified on this history; the forecast below uses the naive baseline.

## Forecast (next 3 months after the window)
| Month | Point | Approx. 80% interval |
|---|---:|---|
| 2018-09 | 838,577 | 763,155 to 912,125 |
| 2018-10 | 838,577 | 731,914 to 942,590 |
| 2018-11 | 838,577 | 707,942 to 965,966 |

## Limitations
- Only 20 usable months and 6 test points; error estimates are themselves uncertain.
- Seasonal naive performs poorly because 2017 was a high-growth year; one year of history cannot separate seasonality from growth.
- Intervals come from empirical quantiles of 6 one-step errors, widened by sqrt(h). This is an approximation, not a calibrated predictive distribution.
- The forecast months fall after the dataset's coverage, so they can never be validated against observed data.
- No machine-learning model is used: with this history nothing more complex is defensible against the baseline.
