"""Reconcile the SQL KPI views (meridian_dev) with the independent Python KPIs computed from the raw CSV files.

Usage: python scripts/reconcile_kpis.py
Read-only. Prints aggregate MATCH/DIFF lines only (no KPI values); exits non-zero on any difference.
Exact equality for counts and Decimal money; float averages compared to 1e-6 relative tolerance.
"""

import math
import sys
from decimal import Decimal

from sqlalchemy import text

from meridian.analytics import kpis
from meridian.analytics.source_frames import load_source_frames
from meridian.config import get_settings
from meridian.db import Role, make_engine

MONTHLY_KEYS = (
    "orders_placed",
    "delivered_orders",
    "delivered_merchandise_value",
    "freight_billed",
    "delivered_items",
    "canceled_orders",
    "unavailable_orders",
    "active_customers",
    "active_sellers",
)


def same(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and math.isclose(float(a), float(b), rel_tol=1e-6)
    return a == b


def main() -> int:
    frames = load_source_frames(get_settings().raw_dir)
    engine = make_engine(Role.READER)
    checks: list[tuple[str, bool]] = []
    with engine.connect() as conn:

        def rows(sql):
            return [dict(r) for r in conn.execute(text(sql)).mappings()]

        view = {r["month_start"].strftime("%Y-%m"): r for r in rows("SELECT * FROM vw_kpi_monthly")}
        py = kpis.monthly_commercial(frames)
        py_months = {str(m): row for m, row in py.iterrows()}
        bad = [
            m
            for m, r in py_months.items()
            if any(not same(view[m][k], getattr(r[k], "item", lambda v=r[k]: v)()) for k in MONTHLY_KEYS)
        ]
        empty_ok = all(view[m]["orders_placed"] == 0 for m in set(view) - set(py_months))
        checks.append((f"monthly K01-K06/K12/K21/K23/K26: {len(py_months)} months with orders", not bad and empty_ok))

        cat = {}
        for r in rows("SELECT category_name_en, delivered_merchandise_value FROM vw_kpi_category_monthly"):
            cat[r["category_name_en"]] = cat.get(r["category_name_en"], Decimal(0)) + r["delivered_merchandise_value"]
        checks.append((f"category value K11: {len(cat)} categories", cat == kpis.category_value(frames)))

        d = rows(
            "SELECT SUM(delivered_orders) delivered_orders, SUM(excluded_missing_delivery_date) "
            "excluded_missing_delivery_date, SUM(excluded_ambiguous_time) excluded_ambiguous_time, "
            "SUM(lead_time_orders) lead_time_orders, SUM(avg_lead_time_seconds * lead_time_orders) / "
            "SUM(lead_time_orders) avg_lead_time_seconds, SUM(on_time_orders) on_time_orders, "
            "SUM(late_orders) late_orders, SUM(avg_days_late * late_orders) / SUM(late_orders) avg_days_late "
            "FROM vw_kpi_delivery_monthly"
        )[0]
        pd_ = kpis.delivery_summary(frames)
        checks.append(
            ("delivery K14-K16", all(same(float(d[k]) if k.startswith("avg") else d[k], pd_[k]) for k in pd_))
        )

        r = rows(
            "SELECT SUM(orders_with_review) n, SUM(sum_order_scores) / SUM(orders_with_review) s, "
            "SUM(orders_with_shared_review) sh FROM vw_kpi_reviews_monthly"
        )[0]
        pr = kpis.review_summary(frames)
        checks.append(
            (
                "reviews K13",
                r["n"] == pr["orders_with_review"]
                and same(float(r["s"]), pr["avg_review_score"])
                and r["sh"] == pr["orders_with_shared_review"],
            )
        )

        by_type, vn, vs, inv = {}, 0, 0, 0
        for p in rows("SELECT * FROM vw_kpi_payments_monthly"):
            n, v = by_type.get(p["payment_type"], (0, Decimal(0)))
            by_type[p["payment_type"]] = (n + p["payment_records"], v + p["payment_value"])
            vn, vs, inv = (
                vn + p["valid_installment_records"],
                vs + p["sum_valid_installments"],
                inv + p["invalid_installment_records"],
            )
        pp = kpis.payment_summary(frames)
        checks.append(
            (
                "payments K19/K20",
                by_type == {t: (x["records"], x["value"]) for t, x in pp["by_type"].items()}
                and same(float(vs / vn), pp["avg_valid_installments"])
                and inv == pp["invalid_records"],
            )
        )

        recon = kpis.payment_reconciliation(frames)
        total = {k: sum(x[k] for x in rows("SELECT * FROM vw_payment_reconciliation")) for k in recon}
        checks.append(("payment reconciliation K18", total == recon))

        coh = {
            (x["cohort_month"].strftime("%Y-%m"), x["months_since_first"]): x["active_customers"]
            for x in rows("SELECT * FROM vw_cohort_retention")
        }
        checks.append((f"cohort retention K08: {len(coh)} cells", coh == kpis.cohort_retention(frames)))

        k07 = conn.execute(
            text(
                "SELECT COUNT(*), SUM(n >= 2) FROM (SELECT c.customer_unique_id, COUNT(*) n FROM fact_orders o "
                "JOIN dim_customer c USING (customer_id) WHERE o.order_status = 'delivered' "
                "AND o.purchase_date BETWEEN '2017-01-01' AND '2018-08-31' GROUP BY c.customer_unique_id) x"
            )
        ).one()
        pk = kpis.repeat_rate(frames, "2017-01-01", "2018-08-31")
        checks.append(("repeat rate K07 (D-018 window)", (k07[0], k07[1]) == (pk["customers"], pk["repeat_customers"])))
    engine.dispose()
    for name, ok in checks:
        print(f"{'MATCH' if ok else 'DIFF '}  {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"\n{len(checks) - failed} matched, {failed} differed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
