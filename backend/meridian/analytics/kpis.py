"""Independent Python implementation of the canonical KPIs (business/08_kpi_dictionary.md).

These functions start from source-shaped frames (see source_frames.py) and deliberately do NOT reuse the SQL
views, so the two implementations can be reconciled (scripts/reconcile_kpis.py, integration tests).
Every function aggregates each grain separately before combining, so nothing fans out (RULE-06).
"""

import math
from decimal import Decimal

import pandas as pd

from meridian.analytics.source_frames import SourceFrames

DELIVERED = "delivered"


def _dsum(values) -> Decimal:
    return sum(values, Decimal(0))


def monthly_commercial(s: SourceFrames) -> pd.DataFrame:
    """K01-K06, K12, K21, K23, K26 per purchase month (months with orders only)."""
    o = s.orders.merge(s.customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
    item_tot = s.items.groupby("order_id").agg(
        price=("price", _dsum), freight=("freight_value", _dsum), n_items=("order_item_id", "size")
    )
    o = o.merge(item_tot, left_on="order_id", right_index=True, how="left")
    rows = []
    for month, g in o.groupby("month"):
        d = g[g["order_status"] == DELIVERED]
        d_items = s.items[s.items["order_id"].isin(set(d["order_id"]))]
        rows.append(
            {
                "month": month,
                "orders_placed": len(g),
                "delivered_orders": len(d),
                "delivered_merchandise_value": _dsum(d["price"].dropna()),
                "freight_billed": _dsum(d["freight"].dropna()),
                "delivered_items": int(d["n_items"].fillna(0).sum()),
                "canceled_orders": int((g["order_status"] == "canceled").sum()),
                "unavailable_orders": int((g["order_status"] == "unavailable").sum()),
                "active_customers": d["customer_unique_id"].nunique(),
                "active_sellers": d_items["seller_id"].nunique(),
            }
        )
    return pd.DataFrame(rows).set_index("month")


def category_value(s: SourceFrames) -> dict[str, Decimal]:
    """Delivered merchandise value per English category ('unknown' for missing; Portuguese if untranslated)."""
    delivered = set(s.orders.loc[s.orders["order_status"] == DELIVERED, "order_id"])
    tr = dict(zip(s.translation["product_category_name"], s.translation["product_category_name_english"], strict=True))
    cat = {
        pid: (tr.get(c, c) if c else "unknown")
        for pid, c in zip(s.products["product_id"], s.products["product_category_name"], strict=True)
    }
    out: dict[str, Decimal] = {}
    for pid, price in s.items.loc[s.items["order_id"].isin(delivered), ["product_id", "price"]].itertuples(index=False):
        out[cat[pid]] = out.get(cat[pid], Decimal(0)) + price
    return out


def delivery_summary(s: SourceFrames) -> dict[str, float | int | None]:
    """K14-K16 over all delivered orders (RULE-11, RULE-12, D-017 T8)."""
    d = s.orders[s.orders["order_status"] == DELIVERED]
    has_date = d["order_delivered_customer_date"].notna()
    utc_ok = d["purchase_utc"].notna() & d["delivered_utc"].notna()
    secs = [
        (b - a).total_seconds()
        for a, b in zip(d.loc[utc_ok, "purchase_utc"], d.loc[utc_ok, "delivered_utc"], strict=True)
    ]
    dd = d[has_date]
    delivered_date = dd["order_delivered_customer_date"].dt.normalize()
    late_days = (delivered_date - dd["order_estimated_delivery_date"]).dt.days
    late = late_days[late_days > 0]
    return {
        "delivered_orders": len(d),
        "excluded_missing_delivery_date": int((~has_date).sum()),
        "excluded_ambiguous_time": int((has_date & ~utc_ok).sum()),
        "lead_time_orders": len(secs),
        "avg_lead_time_seconds": sum(secs) / len(secs) if secs else None,
        "on_time_orders": int((late_days <= 0).sum()),
        "late_orders": len(late),
        "avg_days_late": float(late.mean()) if len(late) else None,
    }


def review_summary(s: SourceFrames) -> dict[str, float | int]:
    """K13: mean over orders of each order's mean score; shared review_ids flagged (D-019b)."""
    r = s.reviews
    per_order = r.groupby("order_id")["review_score"].mean()
    orders_per_review = r.groupby("review_id")["order_id"].nunique()
    shared_ids = set(orders_per_review[orders_per_review > 1].index)
    shared_orders = r.loc[r["review_id"].isin(shared_ids), "order_id"].nunique()
    return {
        "orders_with_review": len(per_order),
        "avg_review_score": float(per_order.mean()),
        "orders_with_shared_review": int(shared_orders),
    }


def payment_summary(s: SourceFrames) -> dict[str, dict]:
    """K19 records/value per type; K20 valid instalments excluding credit-card 0 instalments (RULE-28)."""
    p = s.payments
    invalid = (p["payment_type"] == "credit_card") & (p["payment_installments"] == 0)
    by_type = {t: {"records": len(g), "value": _dsum(g["payment_value"])} for t, g in p.groupby("payment_type")}
    valid = p.loc[~invalid, "payment_installments"]
    return {"by_type": by_type, "avg_valid_installments": float(valid.mean()), "invalid_records": int(invalid.sum())}


def payment_reconciliation(s: SourceFrames) -> dict[str, int]:
    """K18 at order level: items (price + freight) vs payments, each aggregated per order first."""
    iv = s.items.assign(v=s.items["price"] + s.items["freight_value"]).groupby("order_id")["v"].agg(_dsum)
    pv = s.payments.groupby("order_id")["payment_value"].agg(_dsum)
    both = iv.index.intersection(pv.index)
    diff = pv[both] - iv[both]
    tol = Decimal("0.01")
    return {
        "orders_with_both": len(both),
        "matched_orders": int(sum(abs(x) <= tol for x in diff)),
        "payments_higher_orders": int(sum(x > tol for x in diff)),
        "payments_lower_orders": int(sum(x < -tol for x in diff)),
        "items_only_orders": len(iv.index.difference(pv.index)),
        "payments_only_orders": len(pv.index.difference(iv.index)),
    }


def cohort_retention(s: SourceFrames) -> dict[tuple[str, int], int]:
    """K08: {(cohort_month 'YYYY-MM', months_since_first): active customers}, full history."""
    o = s.orders[s.orders["order_status"] == DELIVERED].merge(s.customers, on="customer_id")
    act = o[["customer_unique_id", "month"]].drop_duplicates()
    first = act.groupby("customer_unique_id")["month"].min().rename("cohort")
    act = act.join(first, on="customer_unique_id")
    act["k"] = [(m - c).n for m, c in zip(act["month"], act["cohort"], strict=True)]
    return {(str(c), int(k)): int(n) for (c, k), n in act.groupby(["cohort", "k"]).size().items()}


def repeat_rate(s: SourceFrames, start: str, end: str) -> dict[str, float | int | None]:
    """K07 within [start, end] (inclusive dates): people with >=2 delivered orders / people with >=1."""
    o = s.orders[(s.orders["order_status"] == DELIVERED)].merge(s.customers, on="customer_id")
    day = o["order_purchase_timestamp"].dt.normalize()
    o = o[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))]
    n = o.groupby("customer_unique_id").size()
    return {
        "customers": len(n),
        "repeat_customers": int((n >= 2).sum()),
        "repeat_rate": float((n >= 2).mean()) if len(n) else None,
    }


def top_share(values: list[Decimal], top_fraction: float = 0.1) -> float | None:
    """K10/K22: share of the total held by the top ceil(n * fraction) contributors."""
    vals = sorted(values, reverse=True)
    total = _dsum(vals)
    if not vals or total == 0:
        return None
    k = math.ceil(len(vals) * top_fraction)
    return float(_dsum(vals[:k]) / total)
