"""Independent Python KPIs on the synthetic fixture vs hand-calculated values (no database)."""

from decimal import Decimal as D
from pathlib import Path

import pytest

from meridian.analytics import kpis
from meridian.analytics.source_frames import load_source_frames
from tests import expected as E

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "olist"


@pytest.fixture(scope="module")
def frames():
    return load_source_frames(FIXTURE)


def test_monthly_commercial(frames):
    df = kpis.monthly_commercial(frames)
    assert {str(m) for m in df.index} == set(E.MONTHLY)
    for month, exp in E.MONTHLY.items():
        row = df.loc[next(m for m in df.index if str(m) == month)]
        assert {k: row[k] for k in exp} == exp, month
    assert sum(df["delivered_merchandise_value"]) == E.K01_TOTAL


def test_category_value(frames):
    assert kpis.category_value(frames) == E.CATEGORY_VALUE


def test_delivery_summary(frames):
    assert kpis.delivery_summary(frames) == E.DELIVERY


def test_review_summary(frames):
    assert kpis.review_summary(frames) == E.REVIEWS


def test_payment_summary(frames):
    p = kpis.payment_summary(frames)
    assert {t: (v["records"], v["value"]) for t, v in p["by_type"].items()} == E.PAYMENTS["by_type"]
    assert p["avg_valid_installments"] == E.PAYMENTS["avg_valid_installments"]
    assert p["invalid_records"] == E.PAYMENTS["invalid_records"]


def test_payment_reconciliation(frames):
    assert kpis.payment_reconciliation(frames) == E.RECONCILIATION


def test_cohorts_and_repeat_rate(frames):
    assert kpis.cohort_retention(frames) == E.COHORTS
    assert kpis.repeat_rate(frames, "2017-01-01", "2018-08-31") == E.REPEAT_DEFAULT_WINDOW


def test_top_share():
    assert kpis.top_share([D("325.75"), D("50.50")]) == E.CUSTOMER_TOP10_SHARE
    assert kpis.top_share([]) is None
    assert kpis.top_share([D("1")] * 20) == pytest.approx(0.1)  # ceil(2) of 20 equal values
