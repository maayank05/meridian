"""Dashboard/report composition: builds JSON-ready payloads from the canonical views and services.

Routes and the executive report call these functions, so the app and the report always show the same numbers.
Money is returned as float rounded to 2 dp for display (exact values stay in the SQL views). Every KPI carries
its provenance class (RULE-16).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Connection, text

from meridian.analytics import services
from meridian.analytics.simulator import (
    Assumptions,
    CampaignScenario,
    break_even_uplift,
    compare_scenarios,
    sensitivity,
)

DATA_START, DATA_END = date(2016, 9, 1), date(2018, 10, 31)
SMALL_SAMPLE_ORDERS = 30  # RULE-14 / A-07

KPI_DEFINITIONS = {
    "K01": (
        "Delivered Merchandise Value (Revenue Proxy)",
        "BRL",
        "derived",
        "Sum of item price of delivered orders by purchase date. Not accounting revenue or profit; freight "
        "excluded; refunds and accounting adjustments unavailable (D-016).",
    ),
    "K02": ("Freight billed", "BRL", "derived", "Freight charged on items of delivered orders."),
    "K03": ("Delivered orders", "orders", "derived", "Distinct orders with status delivered."),
    "K04": ("Average order value", "BRL", "derived", "K01 / K03 for the same period."),
    "K06": ("Orders placed", "orders", "derived", "All orders created in the period, any status."),
    "K12": ("Cancellation rate", "%", "derived", "Orders with status canceled / orders placed (RULE-26)."),
    "K26": ("Unavailable order rate", "%", "derived", "Orders with status unavailable / orders placed (RULE-26)."),
    "K21": ("Active customers", "people", "derived", "Distinct customer_unique_id with a delivered order."),
}


def _money(v) -> float | None:
    return None if v is None else round(float(v), 2)


def _num(v) -> float | None:
    return None if v is None else float(v)


def _change(cur, prior) -> float | None:
    return (float(cur) - float(prior)) / float(prior) if prior not in (None, 0) and cur is not None else None


def validate_period(start: date, end: date) -> None:
    if start > end:
        raise ValueError("start must not be after end")
    if start.day != 1 or end != services.month_end(end):
        raise ValueError("periods must start on the first and end on the last day of a month")
    if start < DATA_START or end > DATA_END:
        raise ValueError(f"period must lie within the data coverage {DATA_START} to {DATA_END}")


def metadata(conn: Connection) -> dict:
    run = conn.execute(
        text(
            "SELECT run_id, finished_at_utc FROM audit_ingestion_run WHERE status = 'succeeded' "
            "ORDER BY run_id DESC LIMIT 1"
        )
    ).first()
    months = conn.execute(text("SELECT month_start, coverage_flag FROM agg_kpi_monthly ORDER BY month_start")).all()
    return {
        "data_freshness_utc": run.finished_at_utc.isoformat() if run else None,
        "latest_run_id": run.run_id if run else None,
        "default_period": {"start": services.DEFAULT_START.isoformat(), "end": services.DEFAULT_END.isoformat()},
        "data_coverage": {"start": DATA_START.isoformat(), "end": DATA_END.isoformat()},
        "month_coverage": [{"month": m.month_start.isoformat(), "coverage_flag": m.coverage_flag} for m in months],
        "provenance_classes": ["source_observed", "derived", "synthetic_assumption", "forecast", "scenario_output"],
        "currency": "BRL",
        "kpis": [
            {"id": k, "name": n, "unit": u, "provenance": p, "definition": d}
            for k, (n, u, p, d) in KPI_DEFINITIONS.items()
        ],
    }


def overview(conn: Connection, start: date, end: date) -> dict:
    validate_period(start, end)
    s = services.period_summary(conn, start, end)
    cur, pri = s.current, s.prior
    # RULE-22/25: a change is only meaningful if every prior month is a full-coverage (default-window) month.
    n_prior = (s.prior_end.year - s.prior_start.year) * 12 + s.prior_end.month - s.prior_start.month + 1
    prior_ok = (
        conn.execute(
            text(
                "SELECT COUNT(*) FROM agg_kpi_monthly WHERE month_start BETWEEN :s AND :e "
                "AND coverage_flag = 'default_window'"
            ),
            {"s": s.prior_start, "e": s.prior_end},
        ).scalar_one()
        == n_prior
    )
    values = {
        "K01": (cur["delivered_merchandise_value"], pri["delivered_merchandise_value"]),
        "K02": (cur["freight_billed"], pri["freight_billed"]),
        "K03": (cur["delivered_orders"], pri["delivered_orders"]),
        "K04": (cur["average_order_value"], pri["average_order_value"]),
        "K06": (cur["orders_placed"], pri["orders_placed"]),
        "K12": (cur["cancellation_rate"], pri["cancellation_rate"]),
        "K26": (cur["unavailable_rate"], pri["unavailable_rate"]),
        "K21": (cur["active_customers"], pri["active_customers"]),
    }
    kpis = []
    for k, (c, p) in values.items():
        name, unit, prov, definition = KPI_DEFINITIONS[k]
        fmt = _money if unit == "BRL" else _num
        kpis.append(
            {
                "id": k,
                "name": name,
                "unit": unit,
                "provenance": prov,
                "definition": definition,
                "value": fmt(c),
                "prior_value": fmt(p),
                "change": _change(c, p) if prior_ok else None,
            }
        )
    monthly = services.monthly_kpis(conn, start, end)
    series = [
        {
            "month": r["month_start"].isoformat(),
            "coverage_flag": r["coverage_flag"],
            "delivered_merchandise_value": _money(r["delivered_merchandise_value"]),
            "orders_placed": int(r["orders_placed"]),
            "delivered_orders": int(r["delivered_orders"]),
            "average_order_value": _money(r["average_order_value"]),
        }
        for _, r in monthly.iterrows()
    ]
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "prior_period": {
            "start": s.prior_start.isoformat(),
            "end": s.prior_end.isoformat(),
            "comparable": prior_ok,
            "note": None
            if prior_ok
            else "Prior period is not fully inside the 2017-01..2018-08 "
            "full-coverage window, so no change is computed (RULE-22/25).",
        },
        "months_flagged": cur["months_flagged"],
        "kpis": kpis,
        "monthly": series,
    }


def customers(conn: Connection, start: date, end: date) -> dict:
    validate_period(start, end)
    rr, conc = services.customer_measures(conn, start, end)
    rows = conn.execute(
        text(
            "SELECT * FROM agg_cohort_retention WHERE cohort_month BETWEEN :s AND :e "
            "ORDER BY cohort_month, months_since_first"
        ),
        {"s": start.replace(day=1), "e": end},
    ).all()
    last_full = services.DEFAULT_END.replace(day=1)  # last full-coverage month (RULE-25): later cells unobservable
    cohorts: dict[str, dict] = {}
    for r in rows:
        cm = r.cohort_month
        c = cohorts.setdefault(
            cm.isoformat(),
            {
                "cohort_month": cm.isoformat(),
                "cohort_size": int(r.cohort_size),
                "observable_months": (last_full.year - cm.year) * 12 + last_full.month - cm.month,
                "retention": [],
            },
        )
        c["retention"].append(
            {
                "months_since_first": int(r.months_since_first),
                "active_customers": int(r.active_customers),
                "rate": int(r.active_customers) / int(r.cohort_size),
            }
        )
    for c in cohorts.values():  # within the observable horizon, a missing cell is a real zero
        seen = {x["months_since_first"] for x in c["retention"]}
        c["retention"] += [
            {"months_since_first": n, "active_customers": 0, "rate": 0.0}
            for n in range(1, c["observable_months"] + 1)
            if n not in seen
        ]
        c["retention"].sort(key=lambda x: x["months_since_first"])
    return {
        "provenance": "derived",
        "repeat_rate": rr,
        "concentration": conc,
        "cohorts": list(cohorts.values()),
        "note": "Cohort = month of first delivered order over the full history. Months after 2018-08 (last "
        "full-coverage month) are unobservable and omitted; within that horizon a 0 is a real zero.",
    }


def products(conn: Connection, start: date, end: date) -> dict:
    validate_period(start, end)
    rows = conn.execute(
        text(
            "SELECT category_name_en, MAX(is_category_missing) missing, MAX(is_untranslated) untranslated, "
            "SUM(delivered_merchandise_value) v, SUM(delivered_items) items, SUM(delivered_orders) orders "
            "FROM agg_kpi_category_monthly WHERE month_start BETWEEN :s AND :e "
            "GROUP BY category_name_en ORDER BY v DESC"
        ),
        {"s": start.replace(day=1), "e": end},
    ).all()
    total = sum((r.v for r in rows), Decimal(0))
    cats = [
        {
            "category": r.category_name_en,
            "delivered_merchandise_value": _money(r.v),
            "share": float(r.v / total) if total else None,
            "delivered_items": int(r.items),
            "delivered_orders": int(r.orders),
            "small_sample": int(r.orders) < SMALL_SAMPLE_ORDERS,
            "is_category_missing": bool(r.missing),
            "is_untranslated": bool(r.untranslated),
        }
        for r in rows
    ]
    return {"provenance": "derived", "total_delivered_merchandise_value": _money(total), "categories": cats}


def operations(conn: Connection, start: date, end: date) -> dict:
    validate_period(start, end)
    p = {"s": start.replace(day=1), "e": end}
    d = conn.execute(
        text(
            "SELECT SUM(delivered_orders) delivered, SUM(excluded_missing_delivery_date) missing, "
            "SUM(excluded_ambiguous_time) ambiguous, SUM(lead_time_orders) lt_n, "
            "SUM(avg_lead_time_seconds * lead_time_orders) / NULLIF(SUM(lead_time_orders), 0) lt_s, "
            "SUM(on_time_orders) on_time, SUM(on_time_eligible_orders) eligible, SUM(late_orders) late, "
            "SUM(avg_days_late * late_orders) / NULLIF(SUM(late_orders), 0) days_late "
            "FROM agg_kpi_delivery_monthly WHERE month_start BETWEEN :s AND :e"
        ),
        p,
    ).one()
    monthly = conn.execute(
        text(
            "SELECT month_start, coverage_flag, on_time_rate, avg_lead_time_seconds "
            "FROM agg_kpi_delivery_monthly WHERE month_start BETWEEN :s AND :e "
            "ORDER BY month_start"
        ),
        p,
    ).all()
    rv = conn.execute(
        text(
            "SELECT SUM(orders_with_review) n, SUM(sum_order_scores) / NULLIF(SUM(orders_with_review), 0) "
            "s, SUM(orders_with_shared_review) shared FROM agg_kpi_reviews_monthly "
            "WHERE month_start BETWEEN :s AND :e"
        ),
        p,
    ).one()
    pay = conn.execute(
        text(
            "SELECT payment_type, SUM(payment_records) n, SUM(payment_value) v, "
            "SUM(valid_installment_records) vn, SUM(sum_valid_installments) vs, "
            "SUM(invalid_installment_records) inv FROM agg_kpi_payments_monthly "
            "WHERE month_start BETWEEN :s AND :e GROUP BY payment_type ORDER BY v DESC"
        ),
        p,
    ).all()
    pay_total = sum((r.v for r in pay), Decimal(0))
    valid_n = sum(int(r.vn) for r in pay)
    recon = conn.execute(text("SELECT * FROM agg_payment_reconciliation ORDER BY orders DESC")).mappings().all()
    return {
        "provenance": "derived",
        "delivery": {
            "delivered_orders": int(d.delivered or 0),
            "excluded_missing_delivery_date": int(d.missing or 0),
            "excluded_ambiguous_time": int(d.ambiguous or 0),
            "lead_time_orders": int(d.lt_n or 0),
            "avg_lead_time_days": None if d.lt_s is None else float(d.lt_s) / 86400,
            "on_time_rate": None if not d.eligible else int(d.on_time) / int(d.eligible),
            "late_orders": int(d.late or 0),
            "avg_days_late": _num(d.days_late),
            "monthly": [
                {
                    "month": r.month_start.isoformat(),
                    "coverage_flag": r.coverage_flag,
                    "on_time_rate": _num(r.on_time_rate),
                    "avg_lead_time_days": None
                    if r.avg_lead_time_seconds is None
                    else float(r.avg_lead_time_seconds) / 86400,
                }
                for r in monthly
            ],
        },
        "reviews": {
            "orders_with_review": int(rv.n or 0),
            "avg_review_score": _num(rv.s),
            "orders_with_shared_review": int(rv.shared or 0),
            "note": "Mean of per-order mean scores; orders sharing a review_id are not independent (RULE-15).",
        },
        "payments": {
            "by_type": [
                {
                    "payment_type": r.payment_type,
                    "records": int(r.n),
                    "value": _money(r.v),
                    "share_of_value": float(r.v / pay_total) if pay_total else None,
                }
                for r in pay
            ],
            "avg_installments_valid": (sum(int(r.vs) for r in pay) / valid_n) if valid_n else None,
            "invalid_installment_records_excluded": sum(int(r.inv) for r in pay),
        },
        "payment_reconciliation_all_time": [
            {k: (_money(v) if k == "net_difference" else (v if k == "order_status" else int(v))) for k, v in r.items()}
            for r in recon
        ],
    }


def quality(conn: Connection) -> dict:
    run = (
        conn.execute(text("SELECT * FROM audit_ingestion_run WHERE status = 'succeeded' ORDER BY run_id DESC LIMIT 1"))
        .mappings()
        .first()
    )
    if run is None:
        return {"latest_run": None, "files": [], "checks": [], "failed_runs": 0}
    files = (
        conn.execute(
            text("SELECT file_name, row_count, sha256 FROM audit_source_file WHERE run_id = :r ORDER BY file_name"),
            {"r": run["run_id"]},
        )
        .mappings()
        .all()
    )
    checks = (
        conn.execute(
            text(
                "SELECT check_id, description, severity, affected_rows, status FROM audit_dq_result "
                "WHERE run_id = :r ORDER BY FIELD(severity, 'blocking', 'warning', 'info'), check_id"
            ),
            {"r": run["run_id"]},
        )
        .mappings()
        .all()
    )
    failed = conn.execute(text("SELECT COUNT(*) FROM audit_ingestion_run WHERE status = 'failed'")).scalar_one()
    return {
        "latest_run": {
            "run_id": run["run_id"],
            "started_at_utc": run["started_at_utc"].isoformat(),
            "finished_at_utc": run["finished_at_utc"].isoformat(),
        },
        "files": [{**f, "row_count": int(f["row_count"])} for f in files],
        "checks": [{**c, "affected_rows": int(c["affected_rows"])} for c in checks],
        "failed_runs": int(failed),
    }


def forecast(conn: Connection) -> dict:
    r = services.revenue_forecast(conn)
    return {
        "provenance": "forecast",
        "series": "K01 monthly, D-018 window",
        "test_months": r.test_months,
        "evaluations": [
            {"method": e.method, "mae": round(e.mae, 2), "rmse": round(e.rmse, 2), "mape": e.mape}
            for e in r.evaluations.values()
        ],
        "best_baseline": r.best_baseline,
        "model_justified": r.model_justified,
        "chosen_method": r.chosen_method,
        "forecast": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in f.items()} for f in r.forecast],
    }


def baseline_monthly_value(conn: Connection, start: date, end: date) -> Decimal:
    validate_period(start, end)
    df = services.monthly_kpis(conn, start, end)
    df = df[df["coverage_flag"] == "default_window"]
    return Decimal(str(df["delivered_merchandise_value"].sum())) / len(df) if len(df) else Decimal(0)


def _case(c) -> dict:
    return {
        "case": c.case,
        "uplift": float(c.uplift),
        "incremental_revenue_proxy": _money(c.incremental_revenue_proxy),
        "incremental_contribution": _money(c.incremental_contribution),
        "net_benefit": _money(c.net_benefit),
        "roi": _num(c.roi),
        "payback_months": _num(c.payback_months),
        "provenance": c.provenance,
    }


def simulate(
    conn: Connection,
    *,
    start: date,
    end: date,
    horizon_months: int,
    intervention_cost: Decimal,
    contribution_margin: Decimal,
    downside: Decimal,
    base: Decimal,
    upside: Decimal,
) -> dict:
    baseline = baseline_monthly_value(conn, start, end)
    a = Assumptions(baseline, horizon_months, intervention_cost, contribution_margin)
    cases = compare_scenarios(a, downside, base, upside)
    grid = [Decimal(x) / 100 for x in range(-10, 31, 5)]
    be = break_even_uplift(a)
    return {
        "provenance": "scenario_output",
        "baseline": {
            "monthly_delivered_merchandise_value": _money(baseline),
            "provenance": "derived",
            "basis": f"mean monthly K01 over default-window months in {start} to {end}",
        },
        "assumptions": {
            "horizon_months": horizon_months,
            "intervention_cost": _money(intervention_cost),
            "contribution_margin": float(contribution_margin),
            "provenance": "synthetic_assumption",
        },
        "cases": [_case(c) for c in cases],
        "break_even_uplift": _num(be),
        "sensitivity": [_case(c) for c in sensitivity(a, grid)],
        "disclaimer": "Hypothetical estimate based on your assumptions. Not an observed or realised result.",
    }


def campaign(s: CampaignScenario) -> dict:
    r = s.evaluate()
    return {
        k: (
            _money(v)
            if isinstance(v, Decimal) and k in ("incremental_revenue_proxy", "net_benefit")
            else _num(v)
            if isinstance(v, Decimal)
            else v
        )
        for k, v in r.items()
    } | {"disclaimer": "Synthetic campaign scenario (D-015). No observed marketing data exists in this project."}
