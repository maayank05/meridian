"""Monthly forecast of K01 with honest baseline comparison (FR-027, M08, K25).

Method:
- Series: monthly Delivered Merchandise Value (Revenue Proxy) over the D-018 window only (RULE-25).
- Rolling-origin, one-step-ahead evaluation over the last `n_test` months: each forecast for month t is fitted
  on months strictly before t (no leakage; enforced by an assertion).
- Candidates: naive (last value), seasonal naive (same month last year, when 12+ months of history exist),
  and damped additive Holt (statsmodels). The model is only "justified" if it beats the best baseline on MAE.
- The final forecast uses the best method; the interval comes from the empirical quantiles of its rolling
  one-step errors, widened by sqrt(h) for horizon h (an approximation, documented as such).
Outputs are labelled provenance 'forecast' and are estimates, not observations.
"""

import math
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

Method = Callable[[pd.Series], float]


def naive(history: pd.Series) -> float:
    return float(history.iloc[-1])


def seasonal_naive(history: pd.Series) -> float:
    if len(history) < 12:
        raise ValueError("seasonal naive needs at least 12 months of history")
    return float(history.iloc[-12])


def damped_holt(history: pd.Series) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # statsmodels convergence/frequency warnings on short series
        fit = ExponentialSmoothing(history.to_numpy(dtype=float), trend="add", damped_trend=True).fit()
    return float(fit.forecast(1)[0])


METHODS: dict[str, Method] = {"naive": naive, "seasonal_naive": seasonal_naive, "damped_holt": damped_holt}
BASELINES = ("naive", "seasonal_naive")


@dataclass
class Evaluation:
    method: str
    errors: list[float]
    mae: float
    mape: float | None
    rmse: float


@dataclass
class ForecastResult:
    test_months: list[str]
    evaluations: dict[str, Evaluation]
    best_baseline: str
    model_justified: bool
    chosen_method: str
    forecast: list[dict] = field(default_factory=list)
    provenance: str = "forecast"


def rolling_origin(series: pd.Series, method: Method, n_test: int) -> list[float]:
    """Return one-step errors (actual - forecast) for the last n_test points, fitting only on earlier data."""
    errors = []
    for t in range(len(series) - n_test, len(series)):
        history = series.iloc[:t]
        if history.index.max() >= series.index[t]:
            raise RuntimeError("leakage: history reaches the target month")
        errors.append(float(series.iloc[t]) - method(history))
    return errors


def _evaluate(name: str, errors: list[float], actuals: np.ndarray) -> Evaluation:
    e = np.array(errors)
    # MAPE is undefined when any actual is 0 -> None (never inf/NaN in outputs)
    mape = None if np.any(actuals == 0) else float(np.mean(np.abs(e) / np.abs(actuals)))
    return Evaluation(name, errors, float(np.abs(e).mean()), mape, float(math.sqrt(np.mean(e**2))))


def evaluate_and_forecast(series: pd.Series, n_test: int = 6, horizon: int = 3) -> ForecastResult:
    if len(series) < n_test + 6:
        raise ValueError("series too short for the requested evaluation")
    actuals = series.iloc[-n_test:].to_numpy(dtype=float)
    evals = {}
    for name, method in METHODS.items():
        if name == "seasonal_naive" and len(series) - n_test < 12:
            continue
        evals[name] = _evaluate(name, rolling_origin(series, method, n_test), actuals)
    best_baseline = min((b for b in BASELINES if b in evals), key=lambda b: evals[b].mae)
    justified = evals["damped_holt"].mae < evals[best_baseline].mae
    chosen = "damped_holt" if justified else best_baseline
    errs = np.array(evals[chosen].errors)
    lo_q, hi_q = np.quantile(errs, [0.1, 0.9])
    history = series.copy()
    out = []
    for h in range(1, horizon + 1):
        point = METHODS[chosen](history)
        month = history.index[-1] + 1
        out.append(
            {
                "month": str(month),
                "point": point,
                "lower_80": point + lo_q * math.sqrt(h),
                "upper_80": point + hi_q * math.sqrt(h),
            }
        )
        history = pd.concat([history, pd.Series([point], index=[month])])
    return ForecastResult([str(m) for m in series.index[-n_test:]], evals, best_baseline, justified, chosen, out)
