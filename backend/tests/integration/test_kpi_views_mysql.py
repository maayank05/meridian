"""SQL KPI views and services on MySQL (fixture) vs hand-calculated values AND vs the independent Python KPIs."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import text

from meridian.analytics import kpis, services
from meridian.analytics.source_frames import load_source_frames
from meridian.db import Role, make_engine
from tests import expected as E
from tests.integration.conftest import FIXTURE

pytestmark = pytest.mark.mysql


@pytest.fixture(scope="module")
def frames():
    return load_source_frames(FIXTURE)


def rows(engine, sql):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(sql)).mappings()]


def test_monthly_view_matches_hand_calculation_and_python(engine, loaded, frames):
    view = {r["month_start"].strftime("%Y-%m"): r for r in rows(engine, "SELECT * FROM vw_kpi_monthly")}
    assert len(view) == 26  # 2016-09..2018-10 inclusive, months without orders included
    assert view["2016-11"]["orders_placed"] == 0 and view["2016-11"]["coverage_flag"] == "low_coverage"
    assert view["2018-09"]["coverage_flag"] == "incomplete_cutoff"
    py = kpis.monthly_commercial(frames)
    for month, exp in E.MONTHLY.items():
        assert {k: view[month][k] for k in exp} == exp, month
        py_row = py.loc[next(m for m in py.index if str(m) == month)]
        assert {k: view[month][k] for k in exp} == {
            k: getattr(py_row[k], "item", lambda v=py_row[k]: v)() for k in exp
        }, month
    assert view["2017-03"]["average_order_value"] == Decimal("250.50")
    assert view["2017-10"]["cancellation_rate"] == Decimal("0.5")
    assert sum(r["delivered_merchandise_value"] for r in view.values()) == E.K01_TOTAL


def test_category_view(engine, loaded, frames):
    got = {}
    for r in rows(engine, "SELECT category_name_en, delivered_merchandise_value FROM vw_kpi_category_monthly"):
        got[r["category_name_en"]] = got.get(r["category_name_en"], Decimal(0)) + r["delivered_merchandise_value"]
    assert got == E.CATEGORY_VALUE == kpis.category_value(frames)


def test_delivery_view(engine, loaded, frames):
    r = rows(
        engine,
        "SELECT SUM(delivered_orders) d, SUM(excluded_missing_delivery_date) m, "
        "SUM(excluded_ambiguous_time) a, SUM(lead_time_orders) n, "
        "SUM(avg_lead_time_seconds * lead_time_orders) / SUM(lead_time_orders) s, "
        "SUM(on_time_orders) ot, SUM(late_orders) l FROM vw_kpi_delivery_monthly",
    )[0]
    py = kpis.delivery_summary(frames)
    got = (r["d"], r["m"], r["a"], r["n"], float(r["s"]), r["ot"], r["l"])
    keys = (
        "delivered_orders",
        "excluded_missing_delivery_date",
        "excluded_ambiguous_time",
        "lead_time_orders",
        "avg_lead_time_seconds",
        "on_time_orders",
        "late_orders",
    )
    assert got == tuple(E.DELIVERY[k] for k in keys) == tuple(py[k] for k in keys)


def test_reviews_view(engine, loaded, frames):
    r = rows(
        engine,
        "SELECT SUM(orders_with_review) n, SUM(sum_order_scores) / SUM(orders_with_review) avg_score, "
        "SUM(orders_with_shared_review) shared FROM vw_kpi_reviews_monthly",
    )[0]
    got = {
        "orders_with_review": r["n"],
        "avg_review_score": float(r["avg_score"]),
        "orders_with_shared_review": r["shared"],
    }
    assert got == E.REVIEWS == kpis.review_summary(frames)


def test_payments_view(engine, loaded, frames):
    by_type, valid_n, valid_sum, invalid = {}, 0, 0, 0
    for r in rows(engine, "SELECT * FROM vw_kpi_payments_monthly"):
        n, v = by_type.get(r["payment_type"], (0, Decimal(0)))
        by_type[r["payment_type"]] = (n + r["payment_records"], v + r["payment_value"])
        valid_n += r["valid_installment_records"]
        valid_sum += r["sum_valid_installments"]
        invalid += r["invalid_installment_records"]
    py = kpis.payment_summary(frames)
    assert by_type == E.PAYMENTS["by_type"] == {t: (v["records"], v["value"]) for t, v in py["by_type"].items()}
    assert float(valid_sum / valid_n) == E.PAYMENTS["avg_valid_installments"] == py["avg_valid_installments"]
    assert invalid == E.PAYMENTS["invalid_records"] == py["invalid_records"]


def test_reconciliation_view(engine, loaded, frames):
    keys = list(E.RECONCILIATION)
    total = {k: sum(r[k] for r in rows(engine, "SELECT * FROM vw_payment_reconciliation")) for k in keys}
    assert total == E.RECONCILIATION == kpis.payment_reconciliation(frames)


def test_cohort_view(engine, loaded, frames):
    got = {
        (r["cohort_month"].strftime("%Y-%m"), r["months_since_first"]): r["active_customers"]
        for r in rows(engine, "SELECT * FROM vw_cohort_retention")
    }
    assert got == E.COHORTS == kpis.cohort_retention(frames)


def test_services_on_fixture(engine, loaded):
    with engine.connect() as conn:
        summary = services.period_summary(conn)
        assert summary.current["delivered_merchandise_value"] == E.K01_TOTAL
        assert summary.current["delivered_orders"] == 3
        assert summary.current["average_order_value"] == pytest.approx(float(E.K01_TOTAL) / 3)
        assert summary.current["active_customers"] == 2
        assert summary.current["months_flagged"] == []
        assert summary.prior_end == date(2016, 12, 31)
        assert summary.prior["unavailable_orders"] == 1 and summary.prior["delivered_orders"] == 0
        assert "2016-11-01" in summary.prior["months_flagged"]
        assert services.repeat_rate(conn) == E.REPEAT_DEFAULT_WINDOW
        c = services.concentration(conn)
        assert c["customer_top10_share"] == pytest.approx(E.CUSTOMER_TOP10_SHARE)
        assert c["seller_top10_share"] == pytest.approx(E.SELLER_TOP10_SHARE)
        with pytest.raises(ValueError, match="start must not be after end"):
            services.period_summary(conn, date(2018, 1, 1), date(2017, 1, 1))


def test_reader_can_query_views():
    reader = make_engine(Role.READER)
    try:
        with reader.connect() as conn:
            assert conn.execute(text("SELECT COUNT(*) FROM vw_kpi_monthly")).scalar_one() >= 0
    finally:
        reader.dispose()
