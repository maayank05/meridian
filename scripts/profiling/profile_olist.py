"""MERIDIAN Phase 2 — Olist dataset profiler (read-only).

Usage: python -I profile_olist.py <raw_dir> <out_json>

* Reads every column as string (dtype=str, keep_default_na=False) so nothing is silently coerced;
  an empty string is the only representation of "missing".
* Never writes to <raw_dir>.
* Emits aggregate statistics only (no customer/seller/order-level rows).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(sys.argv[1])
OUT = Path(sys.argv[2])
TS_FMT = "%Y-%m-%d %H:%M:%S"
FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
TS_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}


def py(v):
    """Convert numpy/pandas scalars to JSON-safe Python values."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return None if np.isnan(v) else round(float(v), 6)
    if isinstance(v, pd.Timestamp):
        return v.strftime(TS_FMT)
    return v


def dist(series: pd.Series) -> dict:
    return {str(k): int(v) for k, v in series.value_counts().sort_index().items()}


def num_summary(x: pd.Series) -> dict:
    x = x.dropna()
    if x.empty:
        return {}
    q = x.quantile([0.01, 0.25, 0.5, 0.75, 0.99])
    return {
        "n": int(x.size),
        "min": py(x.min()),
        "p01": py(q[0.01]),
        "p25": py(q[0.25]),
        "median": py(q[0.5]),
        "p75": py(q[0.75]),
        "p99": py(q[0.99]),
        "max": py(x.max()),
        "mean": py(x.mean()),
        "zero": int((x == 0).sum()),
        "negative": int((x < 0).sum()),
    }


def infer_type(nonempty: pd.Series) -> str:
    if nonempty.empty:
        return "empty"
    if nonempty.str.fullmatch(r"[0-9a-f]{32}").all():
        return "hex32_id"
    if nonempty.str.fullmatch(r"-?\d+").all():
        return "integer_text"  # may carry leading zeros (e.g. zip prefixes)
    if pd.to_numeric(nonempty, errors="coerce").notna().all():
        return "decimal"
    if pd.to_datetime(nonempty, format=TS_FMT, errors="coerce").notna().all():
        return "datetime"
    return "text"


# ---------------------------------------------------------------- load
df, out = {}, {"files": {}}
for alias, fname in FILES.items():
    path = RAW / fname
    raw_bytes = path.read_bytes()
    d = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df[alias] = d
    cols = {}
    for c in d.columns:
        s = d[c]
        nonempty = s[s != ""]
        t = infer_type(nonempty)
        info = {
            "inferred_type": t,
            "missing": int((s == "").sum()),
            "missing_pct": round(100 * (s == "").mean(), 4),
            "distinct": int(nonempty.nunique()),
            "max_len": int(s.str.len().max()) if len(s) else 0,
            "min_len_nonempty": int(nonempty.str.len().min()) if len(nonempty) else 0,
            "leading_trailing_ws": int((s != s.str.strip()).sum()),
        }
        if t in ("integer_text", "decimal"):
            info["numeric"] = num_summary(pd.to_numeric(nonempty, errors="coerce"))
        if t == "datetime":
            dt = pd.to_datetime(nonempty, format=TS_FMT)
            info["min"], info["max"] = py(dt.min()), py(dt.max())
            info["midnight_time_share_pct"] = round(
                100 * ((dt.dt.hour == 0) & (dt.dt.minute == 0) & (dt.dt.second == 0)).mean(), 4
            )
        cols[c] = info
    out["files"][alias] = {
        "file": fname,
        "bytes": len(raw_bytes),
        "physical_lines": raw_bytes.count(b"\n"),
        "bom": raw_bytes.startswith(b"\xef\xbb\xbf"),
        "crlf": b"\r\n" in raw_bytes[:10000],
        "rows": int(len(d)),
        "columns": list(d.columns),
        "column_profile": cols,
        "duplicate_full_rows": int(d.duplicated().sum()),
    }

o, it, pay, rev, cus, prod, sel, geo, tr = (
    df[k]
    for k in [
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "customers",
        "products",
        "sellers",
        "geolocation",
        "category_translation",
    ]
)


# ---------------------------------------------------------------- keys
def key_check(d, cols):
    dup_rows = int(d.duplicated(subset=cols, keep=False).sum())
    return {
        "key": cols,
        "rows": int(len(d)),
        "distinct_keys": int(d.drop_duplicates(subset=cols).shape[0]),
        "rows_in_duplicate_keys": dup_rows,
        "unique": dup_rows == 0,
        "empty_key_rows": int((d[cols] == "").any(axis=1).sum()),
    }


out["keys"] = {
    "customers.customer_id": key_check(cus, ["customer_id"]),
    "orders.order_id": key_check(o, ["order_id"]),
    "orders.customer_id": key_check(o, ["customer_id"]),
    "order_items.(order_id,order_item_id)": key_check(it, ["order_id", "order_item_id"]),
    "order_payments.(order_id,payment_sequential)": key_check(pay, ["order_id", "payment_sequential"]),
    "order_reviews.review_id": key_check(rev, ["review_id"]),
    "order_reviews.(review_id,order_id)": key_check(rev, ["review_id", "order_id"]),
    "order_reviews.order_id": key_check(rev, ["order_id"]),
    "products.product_id": key_check(prod, ["product_id"]),
    "sellers.seller_id": key_check(sel, ["seller_id"]),
    "category_translation.product_category_name": key_check(tr, ["product_category_name"]),
    "geolocation.(all columns)": key_check(geo, list(geo.columns)),
    "geolocation.geolocation_zip_code_prefix": key_check(geo, ["geolocation_zip_code_prefix"]),
}
cid_per_uid = cus.groupby("customer_unique_id")["customer_id"].nunique()
out["customer_identity"] = {
    "customer_id_rows": int(len(cus)),
    "distinct_customer_unique_id": int(cus["customer_unique_id"].nunique()),
    "customer_ids_per_unique_id": dist(cid_per_uid.clip(upper=5).astype(int)),
    "note": "bucket 5 = 5 or more",
}
seq = it.assign(n=pd.to_numeric(it["order_item_id"])).groupby("order_id")["n"].agg(["min", "max", "count"])
pseq = pay.assign(n=pd.to_numeric(pay["payment_sequential"])).groupby("order_id")["n"].agg(["min", "max", "count"])
out["sequences"] = {
    "order_item_id_contiguous_1_to_n_orders": int(((seq["min"] == 1) & (seq["max"] == seq["count"])).sum()),
    "order_item_id_noncontiguous_orders": int((~((seq["min"] == 1) & (seq["max"] == seq["count"]))).sum()),
    "payment_sequential_contiguous_orders": int(((pseq["min"] == 1) & (pseq["max"] == pseq["count"])).sum()),
    "payment_sequential_noncontiguous_orders": int((~((pseq["min"] == 1) & (pseq["max"] == pseq["count"]))).sum()),
}


# ---------------------------------------------------------------- relationships
def fk(child, ccol, parent, pcol, label):
    c = child[child[ccol] != ""][ccol]
    pset = set(parent[pcol])
    orphan_mask = ~c.isin(pset)
    return {
        "relationship": label,
        "child_rows_checked": int(c.size),
        "child_empty_fk": int((child[ccol] == "").sum()),
        "orphan_rows": int(orphan_mask.sum()),
        "orphan_distinct_keys": int(c[orphan_mask].nunique()),
    }


out["relationships"] = [
    fk(o, "customer_id", cus, "customer_id", "orders.customer_id -> customers.customer_id"),
    fk(cus, "customer_id", o, "customer_id", "customers.customer_id -> orders.customer_id (customers without orders)"),
    fk(it, "order_id", o, "order_id", "order_items.order_id -> orders.order_id"),
    fk(it, "product_id", prod, "product_id", "order_items.product_id -> products.product_id"),
    fk(it, "seller_id", sel, "seller_id", "order_items.seller_id -> sellers.seller_id"),
    fk(pay, "order_id", o, "order_id", "order_payments.order_id -> orders.order_id"),
    fk(rev, "order_id", o, "order_id", "order_reviews.order_id -> orders.order_id"),
    fk(
        prod,
        "product_category_name",
        tr,
        "product_category_name",
        "products.product_category_name -> category_translation",
    ),
    fk(
        cus,
        "customer_zip_code_prefix",
        geo,
        "geolocation_zip_code_prefix",
        "customers.zip_prefix -> geolocation.zip_prefix",
    ),
    fk(
        sel,
        "seller_zip_code_prefix",
        geo,
        "geolocation_zip_code_prefix",
        "sellers.zip_prefix -> geolocation.zip_prefix",
    ),
    fk(prod, "product_id", it, "product_id", "products.product_id -> order_items.product_id (products never sold)"),
    fk(sel, "seller_id", it, "seller_id", "sellers.seller_id -> order_items.seller_id (sellers never selling)"),
]
untranslated = sorted(
    set(
        prod.loc[
            (prod["product_category_name"] != "")
            & ~prod["product_category_name"].isin(set(tr["product_category_name"])),
            "product_category_name",
        ]
    )
)
out["untranslated_categories"] = {name: int((prod["product_category_name"] == name).sum()) for name in untranslated}

# ---------------------------------------------------------------- orders / statuses
items_per_order = it.groupby("order_id").size()
pays_per_order = pay.groupby("order_id").size()
revs_per_order = rev.groupby("order_id").size()
o2 = o.assign(
    has_items=o["order_id"].isin(items_per_order.index),
    has_payments=o["order_id"].isin(pays_per_order.index),
    has_review=o["order_id"].isin(revs_per_order.index),
)
status_tbl = {}
for st, g in o2.groupby("order_status"):
    status_tbl[st] = {
        "orders": int(len(g)),
        **{f"missing_{c}": int((g[c] == "").sum()) for c in TS_COLS["orders"]},
        "without_items": int((~g["has_items"]).sum()),
        "without_payments": int((~g["has_payments"]).sum()),
        "without_review": int((~g["has_review"]).sum()),
    }
out["order_status"] = status_tbl
out["per_order_counts"] = {
    "items_per_order": dist(items_per_order.clip(upper=6)),
    "payments_per_order": dist(pays_per_order.clip(upper=6)),
    "reviews_per_order": dist(revs_per_order.clip(upper=4)),
    "note": "top bucket = that value or more",
}
dup_prod = it.groupby(["order_id", "product_id"]).size()
out["quantity_proxy"] = {
    "order_product_pairs": int(dup_prod.size),
    "pairs_repeated_in_same_order": int((dup_prod > 1).sum()),
    "orders_with_repeated_product": int(dup_prod[dup_prod > 1].reset_index()["order_id"].nunique()),
    "orders_with_multiple_sellers": int((it.groupby("order_id")["seller_id"].nunique() > 1).sum()),
}

# ---------------------------------------------------------------- timestamps
ts = {}
for alias, cols in TS_COLS.items():
    for c in cols:
        s = df[alias][c]
        ne = s[s != ""]
        parsed = pd.to_datetime(ne, format=TS_FMT, errors="coerce")
        ts[f"{alias}.{c}"] = {
            "nonempty": int(ne.size),
            "parse_failures": int(parsed.isna().sum()),
            "min": py(parsed.min()),
            "max": py(parsed.max()),
        }
out["timestamps"] = ts
P = {c: pd.to_datetime(o[c].replace("", None), format=TS_FMT) for c in TS_COLS["orders"]}


def before(a, b):  # count rows where a < b with both present
    m = P[a].notna() & P[b].notna()
    return {"compared": int(m.sum()), "violations": int((P[a][m] < P[b][m]).sum())}


out["date_ordering"] = {
    "approved_before_purchase": before("order_approved_at", "order_purchase_timestamp"),
    "carrier_before_purchase": before("order_delivered_carrier_date", "order_purchase_timestamp"),
    "carrier_before_approved": before("order_delivered_carrier_date", "order_approved_at"),
    "delivered_before_purchase": before("order_delivered_customer_date", "order_purchase_timestamp"),
    "delivered_before_carrier": before("order_delivered_customer_date", "order_delivered_carrier_date"),
    "estimated_before_purchase": before("order_estimated_delivery_date", "order_purchase_timestamp"),
}
rc = pd.to_datetime(rev["review_creation_date"], format=TS_FMT)
ra = pd.to_datetime(rev["review_answer_timestamp"], format=TS_FMT)
out["date_ordering"]["review_answer_before_creation"] = {
    "compared": int((rc.notna() & ra.notna()).sum()),
    "violations": int((ra < rc).sum()),
}
month = P["order_purchase_timestamp"].dt.to_period("M").astype(str)
monthly = (
    o.assign(month=month)
    .groupby("month")
    .agg(orders=("order_id", "size"), delivered=("order_status", lambda s: int((s == "delivered").sum())))
)
out["monthly_purchase_coverage"] = {
    m: {"orders": int(r.orders), "delivered": int(r.delivered)} for m, r in monthly.iterrows()
}
deliv = o["order_status"] == "delivered"
lead = (P["order_delivered_customer_date"] - P["order_purchase_timestamp"]).dt.total_seconds() / 86400
out["delivered_completeness"] = {
    "delivered_orders": int(deliv.sum()),
    "delivered_missing_customer_date": int((deliv & P["order_delivered_customer_date"].isna()).sum()),
    "delivered_missing_carrier_date": int((deliv & P["order_delivered_carrier_date"].isna()).sum()),
    "delivered_missing_approved_at": int((deliv & P["order_approved_at"].isna()).sum()),
    "delivered_without_items": int((deliv & ~o2["has_items"]).sum()),
    "delivered_without_payments": int((deliv & ~o2["has_payments"]).sum()),
    "non_delivered_with_customer_date": dist(
        o.loc[~deliv & P["order_delivered_customer_date"].notna(), "order_status"]
    ),
    "lead_time_days_delivered": num_summary(lead[deliv]),
    "last_purchase_timestamp": py(P["order_purchase_timestamp"].max()),
    "last_delivered_customer_date": py(P["order_delivered_customer_date"].max()),
}

# ---------------------------------------------------------------- money
price, freight, pval = (
    pd.to_numeric(it["price"]),
    pd.to_numeric(it["freight_value"]),
    pd.to_numeric(pay["payment_value"]),
)
inst = pd.to_numeric(pay["payment_installments"])
out["money"] = {
    "order_items.price": num_summary(price),
    "order_items.freight_value": num_summary(freight),
    "order_payments.payment_value": num_summary(pval),
    "order_payments.payment_installments": num_summary(inst),
    "decimal_places_max": {
        c: int(s.str.split(".").str[1].fillna("").str.len().max())
        for c, s in [
            ("price", it["price"]),
            ("freight_value", it["freight_value"]),
            ("payment_value", pay["payment_value"]),
        ]
    },
}
out["payment_type"] = {
    t: {
        "records": int(len(g)),
        "value_zero": int((pd.to_numeric(g["payment_value"]) == 0).sum()),
        "installments_zero": int((pd.to_numeric(g["payment_installments"]) == 0).sum()),
        "installments_gt1": int((pd.to_numeric(g["payment_installments"]) > 1).sum()),
    }
    for t, g in pay.groupby("payment_type")
}
out["review_score"] = dist(rev["review_score"])
out["review_text"] = {
    "title_missing": int((rev["review_comment_title"] == "").sum()),
    "message_missing": int((rev["review_comment_message"] == "").sum()),
    "message_with_newline": int(rev["review_comment_message"].str.contains("\n|\r", regex=True).sum()),
}

# ---------------------------------------------------------------- reconciliation & fan-out
item_tot = (
    it.assign(v=price + freight, p=price).groupby("order_id").agg(items_value=("v", "sum"), price_sum=("p", "sum"))
)
pay_tot = pay.assign(v=pval).groupby("order_id")["v"].sum().rename("pay_value")
rec = o[["order_id", "order_status"]].set_index("order_id").join(item_tot, how="left").join(pay_tot, how="left")
both = rec.dropna(subset=["items_value", "pay_value"])
diff = (both["pay_value"] - both["items_value"]).round(2)


def rec_bucket(sub_diff):
    return {
        "orders": int(sub_diff.size),
        "abs_diff_le_0.01": int((sub_diff.abs() <= 0.01).sum()),
        "payments_higher": int((sub_diff > 0.01).sum()),
        "payments_lower": int((sub_diff < -0.01).sum()),
        "diff_summary": num_summary(sub_diff),
    }


out["reconciliation"] = {
    "orders_total": int(len(rec)),
    "orders_items_only": int((rec["items_value"].notna() & rec["pay_value"].isna()).sum()),
    "orders_payments_only": int((rec["items_value"].isna() & rec["pay_value"].notna()).sum()),
    "orders_neither": int((rec["items_value"].isna() & rec["pay_value"].isna()).sum()),
    "all_with_both": rec_bucket(diff),
    "delivered_with_both": rec_bucket(diff[both["order_status"] == "delivered"]),
}
naive = it.merge(pay, on="order_id", how="inner")
correct_rows = it[it["order_id"].isin(set(pay["order_id"]))]
naive_price = pd.to_numeric(naive["price"]).sum()
correct_price = pd.to_numeric(correct_rows["price"]).sum()
naive_r = it.merge(rev, on="order_id", how="inner")
correct_r = it[it["order_id"].isin(set(rev["order_id"]))]
out["fan_out"] = {
    "items_x_payments": {
        "item_rows": int(len(correct_rows)),
        "joined_rows": int(len(naive)),
        "orders_affected": int(
            naive.groupby("order_id").size().gt(items_per_order.reindex(naive["order_id"].unique()).values).sum()
        ),
        "price_inflation_pct": round(100 * (naive_price / correct_price - 1), 4),
    },
    "items_x_reviews": {
        "item_rows": int(len(correct_r)),
        "joined_rows": int(len(naive_r)),
        "price_inflation_pct": round(
            100 * (pd.to_numeric(naive_r["price"]).sum() / pd.to_numeric(correct_r["price"]).sum() - 1), 4
        ),
    },
    "orders_x_items_rows": {"orders": int(len(o)), "joined_rows": int(len(o.merge(it, on="order_id", how="inner")))},
}

# ---------------------------------------------------------------- products / geo / customers
prod_num = {
    c: num_summary(pd.to_numeric(prod[c].replace("", None)))
    for c in [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
}
out["products"] = {
    "missing_category": int((prod["product_category_name"] == "").sum()),
    "distinct_categories": int(prod.loc[prod["product_category_name"] != "", "product_category_name"].nunique()),
    "numeric": prod_num,
    "rows_missing_all_text_attrs": int(
        ((prod["product_category_name"] == "") & (prod["product_name_lenght"] == "")).sum()
    ),
}
lat, lng = pd.to_numeric(geo["geolocation_lat"]), pd.to_numeric(geo["geolocation_lng"])
in_br = lat.between(-33.75, 5.27) & lng.between(-73.99, -34.79)
out["geolocation"] = {
    "rows": int(len(geo)),
    "distinct_zip_prefixes": int(geo["geolocation_zip_code_prefix"].nunique()),
    "rows_outside_brazil_bbox": int((~in_br).sum()),
    "lat": num_summary(lat),
    "lng": num_summary(lng),
    "rows_per_zip": num_summary(geo.groupby("geolocation_zip_code_prefix").size().astype(float)),
    "zips_with_multiple_city_spellings": int(
        geo.groupby("geolocation_zip_code_prefix")["geolocation_city"].nunique().gt(1).sum()
    ),
}
out["states"] = {
    "customer_state": dist(cus["customer_state"]),
    "seller_state": dist(sel["seller_state"]),
    "geolocation_state_distinct": int(geo["geolocation_state"].nunique()),
}
out["zip_prefix_lengths"] = {
    "customers": dist(cus["customer_zip_code_prefix"].str.len()),
    "sellers": dist(sel["seller_zip_code_prefix"].str.len()),
    "geolocation": dist(geo["geolocation_zip_code_prefix"].str.len()),
}

OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"profile written: {OUT} ({OUT.stat().st_size} bytes)")
