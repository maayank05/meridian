"""Phase 2 follow-up checks (read-only, aggregates only). Usage: python -I followups.py <raw_dir> <out_json>"""

import json
import sys
from pathlib import Path

import pandas as pd

R, OUT = Path(sys.argv[1]), Path(sys.argv[2])
F = "%Y-%m-%d %H:%M:%S"
rd = lambda n: pd.read_csv(R / n, dtype=str, keep_default_na=False, encoding="utf-8-sig")  # noqa: E731
o, it, pay, rev = (
    rd(n)
    for n in [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
    ]
)
ts = lambda s: pd.to_datetime(s.replace("", None), format=F)  # noqa: E731
res = {}
# Orders with at least one voucher payment (set logic is safe for empty selections).
VOUCHER_ORDERS = set(pay.loc[pay["payment_type"] == "voucher", "order_id"])

# 1. Fan-out: orders with items AND >=2 payment records (each item row is duplicated per payment)
pn = pay.groupby("order_id").size()
item_orders = set(it["order_id"])
res["fanout_orders_items_and_multi_payment"] = int(sum(1 for k, n in pn.items() if n >= 2 and k in item_orders))
rn = rev.groupby("order_id").size()
res["fanout_orders_items_and_multi_review"] = int(sum(1 for k, n in rn.items() if n >= 2 and k in item_orders))

# 2. shipping_limit_date far beyond purchase
sl = ts(it["shipping_limit_date"])
res["shipping_limit_after_2018_12_31_rows"] = int((sl > "2018-12-31").sum())
po = o.set_index("order_id")["order_purchase_timestamp"]
gap = (sl - ts(it["order_id"].map(po))).dt.days
res["shipping_limit_minus_purchase_days"] = {
    "min": int(gap.min()),
    "max": int(gap.max()),
    "gt_60_days_rows": int((gap > 60).sum()),
}

# 3. review dates vs purchase / delivery
rv = rev.merge(o[["order_id", "order_purchase_timestamp", "order_delivered_customer_date"]], on="order_id")
rc = ts(rv["review_creation_date"])
res["review_created_before_purchase_date"] = int((rc < ts(rv["order_purchase_timestamp"]).dt.normalize()).sum())
dd = ts(rv["order_delivered_customer_date"])
m = dd.notna()
res["review_created_before_delivery_date"] = {
    "compared": int(m.sum()),
    "violations": int((rc[m] < dd[m].dt.normalize()).sum()),
}

# 4. duplicate review_id structure
g = rev.groupby("review_id")["order_id"].nunique()
res["review_ids_shared_by_multiple_orders"] = int((g > 1).sum())
res["max_orders_per_review_id"] = int(g.max())
sub = rev[rev["review_id"].isin(g[g > 1].index)]
res["shared_review_ids_with_identical_score_and_text"] = int(
    (
        sub.groupby("review_id")[["review_score", "review_comment_message", "review_creation_date"]]
        .nunique()
        .max(axis=1)
        == 1
    ).sum()
)

# 5. Purchase hour distribution (timezone plausibility evidence, A-02)
h = ts(o["order_purchase_timestamp"]).dt.hour
res["purchase_hour_counts"] = {str(k): int(v) for k, v in h.value_counts().sort_index().items()}

# 6. payment_sequential gaps
pseq = pay.assign(n=pd.to_numeric(pay["payment_sequential"])).groupby("order_id")["n"].agg(["min", "max", "count"])
bad = pseq[~((pseq["min"] == 1) & (pseq["max"] == pseq["count"]))]
res["payment_seq_gap_orders"] = {
    "orders": int(len(bad)),
    "min_seq_not_1": int((bad["min"] != 1).sum()),
    "voucher_involved": len(VOUCHER_ORDERS & set(bad.index)),
}

# 7. Reconciliation: payment types among orders where payments exceed items by > 0.01
iv = it.assign(v=pd.to_numeric(it["price"]) + pd.to_numeric(it["freight_value"])).groupby("order_id")["v"].sum()
pv = pay.assign(v=pd.to_numeric(pay["payment_value"])).groupby("order_id")["v"].sum()
d = (pv - iv).dropna().round(2)
hi, lo = set(d[d > 0.01].index), set(d[d < -0.01].index)
p_ = pay.assign(inst=pd.to_numeric(pay["payment_installments"]))
res["recon_payments_higher_profile"] = {
    "orders": len(hi),
    "any_credit_card_installments_gt1": len(set(p_.loc[p_["inst"] > 1, "order_id"]) & hi),
    "any_voucher": len(VOUCHER_ORDERS & hi),
}
res["recon_payments_lower_profile"] = {
    "orders": len(lo),
    "any_voucher": len(VOUCHER_ORDERS & lo),
}

# 8. Orders without items by status (cross-check) and the single delivered order without payment
noi = o[~o["order_id"].isin(item_orders)]
res["orders_without_items_by_status"] = {k: int(v) for k, v in noi["order_status"].value_counts().items()}
res["orders_without_payments_by_status"] = {
    k: int(v) for k, v in o[~o["order_id"].isin(set(pay["order_id"]))]["order_status"].value_counts().items()
}

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
