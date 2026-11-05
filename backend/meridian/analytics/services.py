"""KPI services on top of the canonical SQL views (used by the API, report and scripts).

All queries are parameterized. Ratios over a period are recomputed from summed numerators and denominators,
never averaged across months. Default period = D-018 window (RULE-25).
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import Connection, text

from meridian.analytics.forecast import ForecastResult, evaluate_and_forecast
from meridian.analytics.kpis import top_share

DEFAULT_START = date(2017, 1, 1)
DEFAULT_END = date(2018, 8, 31)
SUM_COLUMNS = (
    "orders_placed",
    "delivered_orders",
    "delivered_merchandise_value",
    "freight_billed",
    "delivered_items",
    "canceled_orders",
    "unavailable_orders",
)


def _ratio(num, den) -> float | None:
    return float(num) / float(den) if den else None


def monthly_kpis(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> pd.DataFrame:
    rows = (
        conn.execute(
            text("SELECT * FROM vw_kpi_monthly WHERE month_start BETWEEN :s AND :e ORDER BY month_start"),
            {"s": start.replace(day=1), "e": end},
        )
        .mappings()
        .all()
    )
    return pd.DataFrame(rows)


def _totals(conn: Connection, start: date, end: date) -> dict:
    df = monthly_kpis(conn, start, end)
    t = {c: (df[c].sum() if len(df) else 0) for c in SUM_COLUMNS}
    people = conn.execute(
        text(
            "SELECT COUNT(DISTINCT c.customer_unique_id) FROM fact_orders o JOIN dim_customer c USING (customer_id) "
            "WHERE o.order_status = 'delivered' AND o.purchase_date BETWEEN :s AND :e"
        ),
        {"s": start, "e": end},
    ).scalar_one()
    t |= {
        "active_customers": int(people),
        "average_order_value": _ratio(t["delivered_merchandise_value"], t["delivered_orders"]),
        "items_per_delivered_order": _ratio(t["delivered_items"], t["delivered_orders"]),
        "cancellation_rate": _ratio(t["canceled_orders"], t["orders_placed"]),
        "unavailable_rate": _ratio(t["unavailable_orders"], t["orders_placed"]),
        "months_flagged": sorted({str(r) for r in df.loc[df["coverage_flag"] != "default_window", "month_start"]})
        if len(df)
        else [],
    }
    return t


@dataclass
class PeriodSummary:
    start: date
    end: date
    current: dict
    prior_start: date
    prior_end: date
    prior: dict


def period_summary(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> PeriodSummary:
    """Current period vs the immediately preceding period of equal length (RULE-22)."""
    if start > end:
        raise ValueError("start must not be after end")
    length = (end - start).days + 1
    prior_end = start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=length - 1)
    return PeriodSummary(
        start, end, _totals(conn, start, end), prior_start, prior_end, _totals(conn, prior_start, prior_end)
    )


def repeat_rate(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> dict:
    """K07: people with >= 2 delivered orders / people with >= 1, within the period."""
    customers, repeat = conn.execute(
        text(
            "SELECT COUNT(*), COALESCE(SUM(n >= 2), 0) FROM (SELECT c.customer_unique_id, COUNT(*) AS n "
            "FROM fact_orders o JOIN dim_customer c USING (customer_id) "
            "WHERE o.order_status = 'delivered' AND o.purchase_date BETWEEN :s AND :e GROUP BY c.customer_unique_id) x"
        ),
        {"s": start, "e": end},
    ).one()
    return {"customers": int(customers), "repeat_customers": int(repeat), "repeat_rate": _ratio(repeat, customers)}


def concentration(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> dict:
    """K10 (top 10% of people) and K22 (top 10% of sellers) share of K01 in the period."""
    params = {"s": start, "e": end}
    by_person = [
        Decimal(v)
        for (v,) in conn.execute(
            text(
                "SELECT SUM(o.items_price_total) FROM fact_orders o JOIN dim_customer c USING (customer_id) "
                "WHERE o.order_status = 'delivered' AND o.purchase_date BETWEEN :s AND :e "
                "GROUP BY c.customer_unique_id"
            ),
            params,
        )
    ]
    by_seller = [
        Decimal(v)
        for (v,) in conn.execute(
            text(
                "SELECT SUM(i.price) FROM fact_order_items i JOIN fact_orders o USING (order_id) "
                "WHERE o.order_status = 'delivered' AND o.purchase_date BETWEEN :s AND :e GROUP BY i.seller_id"
            ),
            params,
        )
    ]
    return {
        "customer_top10_share": top_share(by_person),
        "seller_top10_share": top_share(by_seller),
        "customers": len(by_person),
        "sellers": len(by_seller),
    }


def revenue_forecast(conn: Connection, n_test: int = 6, horizon: int = 3) -> ForecastResult:
    """K25 on the D-018 window only (censored months are never used)."""
    df = monthly_kpis(conn, DEFAULT_START, DEFAULT_END)
    series = pd.Series(
        df["delivered_merchandise_value"].astype(float).to_numpy(),
        index=pd.PeriodIndex(pd.to_datetime(df["month_start"]), freq="M"),
    )
    return evaluate_and_forecast(series, n_test=n_test, horizon=horizon)
