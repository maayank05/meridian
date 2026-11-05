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
            text("SELECT * FROM agg_kpi_monthly WHERE month_start BETWEEN :s AND :e ORDER BY month_start"),
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
        text("SELECT COUNT(DISTINCT customer_unique_id) FROM agg_customer_month WHERE month_start BETWEEN :s AND :e"),
        {"s": start.replace(day=1), "e": end},
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


def month_end(d: date) -> date:
    nxt = date(d.year + d.month // 12, d.month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def add_months(d: date, n: int) -> date:
    m = d.year * 12 + d.month - 1 + n
    return date(m // 12, m % 12 + 1, 1)


def period_summary(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> PeriodSummary:
    """Current whole-month period vs the immediately preceding period with the same number of months (RULE-22)."""
    if start > end:
        raise ValueError("start must not be after end")
    if start.day != 1 or end != month_end(end):
        raise ValueError("periods must start on the first and end on the last day of a month")
    n_months = (end.year - start.year) * 12 + end.month - start.month + 1
    prior_start = add_months(start, -n_months)
    prior_end = start - timedelta(days=1)
    return PeriodSummary(
        start, end, _totals(conn, start, end), prior_start, prior_end, _totals(conn, prior_start, prior_end)
    )


def _person_totals(conn: Connection, start: date, end: date) -> list[tuple[int, Decimal]]:
    """(delivered orders, delivered value) per person over whole months, read once for K07 and K10."""
    return [
        (int(n), Decimal(v))
        for n, v in conn.execute(
            text(
                "SELECT SUM(delivered_orders), SUM(delivered_merchandise_value) FROM agg_customer_month "
                "WHERE month_start BETWEEN :s AND :e GROUP BY customer_unique_id"
            ),
            {"s": start.replace(day=1), "e": end},
        )
    ]


def repeat_rate(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END, people=None) -> dict:
    """K07 over whole months: people with >= 2 delivered orders / people with >= 1."""
    people = _person_totals(conn, start, end) if people is None else people
    repeat = sum(1 for n, _ in people if n >= 2)
    return {"customers": len(people), "repeat_customers": repeat, "repeat_rate": _ratio(repeat, len(people))}


def concentration(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END, people=None) -> dict:
    """K10 (top 10% of people) and K22 (top 10% of sellers) share of K01 over whole months."""
    people = _person_totals(conn, start, end) if people is None else people
    by_seller = [
        Decimal(v)
        for (v,) in conn.execute(
            text(
                "SELECT SUM(delivered_merchandise_value) FROM agg_seller_month WHERE month_start BETWEEN :s AND :e "
                "GROUP BY seller_id"
            ),
            {"s": start.replace(day=1), "e": end},
        )
    ]
    return {
        "customer_top10_share": top_share([v for _, v in people]),
        "seller_top10_share": top_share(by_seller),
        "customers": len(people),
        "sellers": len(by_seller),
    }


def customer_measures(conn: Connection, start: date = DEFAULT_START, end: date = DEFAULT_END) -> tuple[dict, dict]:
    """K07 and K10/K22 from a single read of per-person totals."""
    people = _person_totals(conn, start, end)
    return repeat_rate(conn, start, end, people), concentration(conn, start, end, people)


def revenue_forecast(conn: Connection, n_test: int = 6, horizon: int = 3) -> ForecastResult:
    """K25 on the D-018 window only (censored months are never used)."""
    df = monthly_kpis(conn, DEFAULT_START, DEFAULT_END)
    series = pd.Series(
        df["delivered_merchandise_value"].astype(float).to_numpy(),
        index=pd.PeriodIndex(pd.to_datetime(df["month_start"]), freq="M"),
    )
    return evaluate_and_forecast(series, n_test=n_test, horizon=horizon)
