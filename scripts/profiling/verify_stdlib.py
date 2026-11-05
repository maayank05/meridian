"""Independent re-computation of key Phase 2 profile figures using only the standard library
(csv + Decimal, no pandas), compared against the pandas profile JSON.
Usage: py -3.13 -I verify_stdlib.py <raw_dir> <profile_json>"""

import csv
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAW, prof = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))


def load(name):
    with open(RAW / name, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


T = {a: load(f["file"]) for a, f in prof["files"].items()}
o, it, pay, rev, cus = T["orders"], T["order_items"], T["order_payments"], T["order_reviews"], T["customers"]
checks = []


def cmp(name, ours, theirs):
    checks.append((name, ours == theirs, ours, theirs))


for a, rows in T.items():
    cmp(f"rows {a}", len(rows), prof["files"][a]["rows"])
cmp("distinct orders.order_id", len({r["order_id"] for r in o}), prof["keys"]["orders.order_id"]["distinct_keys"])
cmp(
    "distinct customer_unique_id",
    len({r["customer_unique_id"] for r in cus}),
    prof["customer_identity"]["distinct_customer_unique_id"],
)
cmp(
    "distinct item key",
    len({(r["order_id"], r["order_item_id"]) for r in it}),
    prof["keys"]["order_items.(order_id,order_item_id)"]["distinct_keys"],
)
cmp(
    "distinct payment key",
    len({(r["order_id"], r["payment_sequential"]) for r in pay}),
    prof["keys"]["order_payments.(order_id,payment_sequential)"]["distinct_keys"],
)
cmp("distinct review_id", len({r["review_id"] for r in rev}), prof["keys"]["order_reviews.review_id"]["distinct_keys"])
cmp(
    "distinct (review_id,order_id)",
    len({(r["review_id"], r["order_id"]) for r in rev}),
    prof["keys"]["order_reviews.(review_id,order_id)"]["distinct_keys"],
)
geo_rows = [tuple(r.values()) for r in T["geolocation"]]
cmp(
    "geolocation duplicate full rows",
    len(geo_rows) - len(set(geo_rows)),
    prof["files"]["geolocation"]["duplicate_full_rows"],
)

order_ids = {r["order_id"] for r in o}
rel = {r["relationship"]: r["orphan_rows"] for r in prof["relationships"]}
cmp(
    "orphan items->orders",
    sum(r["order_id"] not in order_ids for r in it),
    rel["order_items.order_id -> orders.order_id"],
)
cmp(
    "orphan payments->orders",
    sum(r["order_id"] not in order_ids for r in pay),
    rel["order_payments.order_id -> orders.order_id"],
)
cmp(
    "orphan reviews->orders",
    sum(r["order_id"] not in order_ids for r in rev),
    rel["order_reviews.order_id -> orders.order_id"],
)
pids, sids, cids = (
    {r["product_id"] for r in T["products"]},
    {r["seller_id"] for r in T["sellers"]},
    {r["customer_id"] for r in cus},
)
cmp(
    "orphan items->products",
    sum(r["product_id"] not in pids for r in it),
    rel["order_items.product_id -> products.product_id"],
)
cmp(
    "orphan items->sellers",
    sum(r["seller_id"] not in sids for r in it),
    rel["order_items.seller_id -> sellers.seller_id"],
)
cmp(
    "orphan orders->customers",
    sum(r["customer_id"] not in cids for r in o),
    rel["orders.customer_id -> customers.customer_id"],
)
gz = {r["geolocation_zip_code_prefix"] for r in T["geolocation"]}
cmp(
    "orphan customer zips",
    sum(r["customer_zip_code_prefix"] not in gz for r in cus),
    rel["customers.zip_prefix -> geolocation.zip_prefix"],
)

status = Counter(r["order_status"] for r in o)
cmp("order_status counts", dict(status), {k: v["orders"] for k, v in prof["order_status"].items()})
cmp(
    "payment_type counts",
    dict(Counter(r["payment_type"] for r in pay)),
    {k: v["records"] for k, v in prof["payment_type"].items()},
)
cmp("review_score counts", dict(Counter(r["review_score"] for r in rev)), prof["review_score"])
deliv = {r["order_id"] for r in o if r["order_status"] == "delivered"}
cmp(
    "delivered missing customer date",
    sum(1 for r in o if r["order_status"] == "delivered" and r["order_delivered_customer_date"] == ""),
    prof["delivered_completeness"]["delivered_missing_customer_date"],
)
item_orders = {r["order_id"] for r in it}
cmp(
    "orders without items",
    sum(1 for r in o if r["order_id"] not in item_orders),
    prof["reconciliation"]["orders_payments_only"] + prof["reconciliation"]["orders_neither"],
)

# Exact decimal reconciliation (independent of pandas float arithmetic)
iv, pv = defaultdict(Decimal), defaultdict(Decimal)
for r in it:
    iv[r["order_id"]] += Decimal(r["price"]) + Decimal(r["freight_value"])
for r in pay:
    pv[r["order_id"]] += Decimal(r["payment_value"])
both = set(iv) & set(pv)
within = sum(1 for k in both if abs(pv[k] - iv[k]) <= Decimal("0.01"))
cmp("orders with items and payments", len(both), prof["reconciliation"]["all_with_both"]["orders"])
cmp("reconciled within 0.01 (Decimal)", within, prof["reconciliation"]["all_with_both"]["abs_diff_le_0.01"])
cmp(
    "payments higher > 0.01 (Decimal)",
    sum(1 for k in both if pv[k] - iv[k] > Decimal("0.01")),
    prof["reconciliation"]["all_with_both"]["payments_higher"],
)

# Fan-out: rows produced by an items x payments join on order_id
pay_n = Counter(r["order_id"] for r in pay)
cmp(
    "items x payments joined rows",
    sum(pay_n[r["order_id"]] for r in it),
    prof["fan_out"]["items_x_payments"]["joined_rows"],
)

months = Counter(r["order_purchase_timestamp"][:7] for r in o)
cmp("monthly purchase coverage", dict(months), {m: v["orders"] for m, v in prof["monthly_purchase_coverage"].items()})

for name, ok, ours, theirs in checks:
    show = "" if ok else f"  stdlib={ours} pandas={theirs}"
    print(f"{'MATCH' if ok else 'DIFF '}  {name}{show}")
bad = sum(1 for c in checks if not c[1])
print(f"\n{len(checks) - bad} matched, {bad} differed")
sys.exit(1 if bad else 0)
