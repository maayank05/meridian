"""Forecast evaluation on deterministic SYNTHETIC series (test data only): leakage, baselines, honesty."""

import pandas as pd
import pytest

from meridian.analytics.forecast import evaluate_and_forecast, naive, rolling_origin, seasonal_naive

IDX = pd.period_range("2017-01", periods=20, freq="M")


def test_rolling_origin_uses_only_earlier_months():
    seen = []

    def spy(history: pd.Series) -> float:
        seen.append(history.index.max())
        return 0.0

    s = pd.Series(range(20), index=IDX, dtype=float)
    rolling_origin(s, spy, n_test=6)
    assert seen == list(IDX[13:19])  # each forecast for IDX[t] saw data up to IDX[t-1] only


def test_naive_and_seasonal_naive_values():
    s = pd.Series(range(20), index=IDX, dtype=float)
    assert naive(s) == 19.0
    assert seasonal_naive(s) == 8.0  # 12 months before the next point
    with pytest.raises(ValueError):
        seasonal_naive(s.iloc[:5])


def test_naive_errors_on_linear_series():
    s = pd.Series([10.0 * i for i in range(20)], index=IDX)
    assert rolling_origin(s, naive, n_test=6) == [10.0] * 6


def test_model_not_justified_when_baseline_is_perfect():
    pattern = [100, 120, 90, 110, 130, 95, 105, 125, 85, 115, 140, 100]
    s = pd.Series([float(pattern[i % 12]) for i in range(20)], index=IDX)  # pure seasonality, no trend
    r = evaluate_and_forecast(s, n_test=6, horizon=3)
    assert r.evaluations["seasonal_naive"].mae == 0.0
    assert r.best_baseline == "seasonal_naive"
    assert r.model_justified is False and r.chosen_method == "seasonal_naive"
    assert [f["month"] for f in r.forecast] == ["2018-09", "2018-10", "2018-11"]
    assert r.forecast[0]["point"] == 85.0  # 2017-09 = index 8 = pattern[8], 12 months before 2018-09
    assert r.provenance == "forecast"


def test_interval_contains_point_and_widens():
    s = pd.Series([1000.0 + 50 * i + (30 if i % 2 else -30) for i in range(20)], index=IDX)
    r = evaluate_and_forecast(s, n_test=6, horizon=3)
    widths = [f["upper_80"] - f["lower_80"] for f in r.forecast]
    assert all(f["lower_80"] <= f["point"] <= f["upper_80"] for f in r.forecast)
    assert widths == sorted(widths)


def test_short_series_rejected():
    with pytest.raises(ValueError, match="too short"):
        evaluate_and_forecast(pd.Series([1.0] * 8, index=IDX[:8]), n_test=6)
