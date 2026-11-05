"""Generate docs/analytics/FORECAST_REPORT.md from a live forecast evaluation on meridian_dev (reader account).

Usage: python scripts/forecast_report.py
"""

from datetime import UTC, datetime

from meridian.analytics.services import revenue_forecast
from meridian.config import REPO_ROOT
from meridian.db import Role, make_engine

OUT = REPO_ROOT / "docs" / "analytics" / "FORECAST_REPORT.md"


def main() -> None:
    engine = make_engine(Role.READER)
    with engine.connect() as conn:
        r = revenue_forecast(conn, n_test=6, horizon=3)
    engine.dispose()
    rows = "\n".join(
        f"| {ev.method} | {ev.mae:,.0f} | {ev.rmse:,.0f} | {'n/a' if ev.mape is None else format(ev.mape, '.1%')} |"
        for ev in sorted(r.evaluations.values(), key=lambda e: e.mae)
    )
    fc = "\n".join(
        f"| {f['month']} | {f['point']:,.0f} | {f['lower_80']:,.0f} to {f['upper_80']:,.0f} |" for f in r.forecast
    )
    verdict = (
        "**The damped Holt model beat the best baseline** and is used for the forecast."
        if r.model_justified
        else f"**The damped Holt model did NOT beat the best baseline ({r.best_baseline}).** A statistical model is "
        f"therefore not justified on this history; the forecast below uses the {r.chosen_method} baseline."
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        f"""# Forecast Report: K25 (Delivered Merchandise Value, monthly)

Generated {datetime.now(UTC):%Y-%m-%d %H:%M} UTC by `scripts/forecast_report.py` from `meridian_dev` (provenance: **forecast**).
Forecasts are estimates, not observations. Values are BRL; revenue proxy only, not accounting revenue or profit (D-016).

## Design
- **Series:** monthly K01 over the D-018 window 2017-01 to 2018-08 (20 months). Censored months (2018-09/10) and low-coverage 2016 months are never used (RULE-25).
- **Evaluation:** rolling origin, one-step-ahead, over the last 6 months ({r.test_months[0]} to {r.test_months[-1]}). Each forecast is fitted only on earlier months; an assertion enforces this (unit-tested).
- **Candidates:** naive (last month), seasonal naive (same month last year), damped additive Holt (Statsmodels). The model is "justified" only if its MAE beats the best baseline.

## Results (one-step errors, test months)
| Method | MAE | RMSE | MAPE |
|---|---:|---:|---:|
{rows}

{verdict}

## Forecast (next 3 months after the window)
| Month | Point | Approx. 80% interval |
|---|---:|---|
{fc}

## Limitations
- Only 20 usable months and 6 test points; error estimates are themselves uncertain.
- Seasonal naive performs poorly because 2017 was a high-growth year; one year of history cannot separate seasonality from growth.
- Intervals come from empirical quantiles of 6 one-step errors, widened by sqrt(h). This is an approximation, not a calibrated predictive distribution.
- The forecast months fall after the dataset's coverage, so they can never be validated against observed data.
- No machine-learning model is used: with this history nothing more complex is defensible against the baseline.
""",
        encoding="utf-8",
    )
    print(f"written {OUT.relative_to(REPO_ROOT)} | justified={r.model_justified} | chosen={r.chosen_method}")


if __name__ == "__main__":
    main()
