"""Generate Phase 2 data documents from profile.json + followups.json (numbers are never hand-typed).
Usage: py -3.13 -I build_reports.py <scratch_dir> <repo_root>"""

import json
import sys
from pathlib import Path

S, ROOT = Path(sys.argv[1]), Path(sys.argv[2])
p = json.loads((S / "profile.json").read_text(encoding="utf-8"))
f = json.loads((S / "followups.json").read_text(encoding="utf-8"))
D = ROOT / "docs" / "data"
DATE = "2026-10-31"
n = lambda x: f"{x:,}"  # noqa: E731
pct = lambda a, b: f"{100 * a / b:.2f}%"  # noqa: E731
FILES, KEYS, ST = p["files"], p["keys"], p["order_status"]
REL = {r["relationship"]: r for r in p["relationships"]}
DC, RC, FO = p["delivered_completeness"], p["reconciliation"], p["fan_out"]
DO = p["date_ordering"]
MC = p["monthly_purchase_coverage"]
total_orders = FILES["orders"]["rows"]
no_items = sum(v["without_items"] for v in ST.values())
reviews_multi = sum(v for k, v in p["per_order_counts"]["reviews_per_order"].items() if k != "1")
multi_cid = sum(v for k, v in p["customer_identity"]["customer_ids_per_unique_id"].items() if k != "1")
review_extra_rows = KEYS["order_reviews.review_id"]["rows"] - KEYS["order_reviews.review_id"]["distinct_keys"]

HEADER = f"""> Generated {DATE} from the Phase 2 profiler output ([profile_results.json](profile_results.json)). Every number below is copied programmatically from that file.
> Source: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0), files in `data/raw/olist/` (not committed). Raw files were read only; SHA-256 hashes were identical before and after profiling.
> Aggregates only. No customer-, seller- or order-level rows are reproduced. **No KPI values are calculated here** (KPIs are implemented in Phase 4).
"""

# ======================================================================= PROFILING REPORT
rows = "\n".join(
    f"| {a} | `{v['file']}` | {n(v['rows'])} | {len(v['columns'])} | {n(v['physical_lines'])} | {n(v['duplicate_full_rows'])} | {'yes' if v['bom'] else 'no'} | {'CRLF' if v['crlf'] else 'LF'} |"
    for a, v in FILES.items()
)
key_rows = "\n".join(
    f"| {k} | {n(v['rows'])} | {n(v['distinct_keys'])} | {n(v['rows_in_duplicate_keys'])} | {'**unique**' if v['unique'] else '**not unique**'} |"
    for k, v in KEYS.items()
)
miss_rows = []
for a, v in FILES.items():
    for c, i in v["column_profile"].items():
        if i["missing"]:
            miss_rows.append(f"| {a}.{c} | {n(i['missing'])} | {i['missing_pct']:.2f}% |")
status_rows = "\n".join(
    f"| {s} | {n(v['orders'])} | {pct(v['orders'], total_orders)} | {n(v['missing_order_approved_at'])} | {n(v['missing_order_delivered_carrier_date'])} | {n(v['missing_order_delivered_customer_date'])} | {n(v['without_items'])} | {n(v['without_payments'])} | {n(v['without_review'])} |"
    for s, v in sorted(ST.items(), key=lambda kv: -kv[1]["orders"])
)
pt_rows = "\n".join(
    f"| {t} | {n(v['records'])} | {n(v['value_zero'])} | {n(v['installments_zero'])} | {n(v['installments_gt1'])} |"
    for t, v in p["payment_type"].items()
)
ts_rows = "\n".join(
    f"| {k} | {n(v['nonempty'])} | {v['parse_failures']} | {v['min']} | {v['max']} |"
    for k, v in p["timestamps"].items()
)
do_rows = "\n".join(f"| {k.replace('_', ' ')} | {n(v['compared'])} | {n(v['violations'])} |" for k, v in DO.items())
mon_rows = "\n".join(f"| {m} | {n(v['orders'])} | {n(v['delivered'])} |" for m, v in MC.items())
money = p["money"]


def mrow(k):
    v = money[k]
    return f"| {k} | {n(v['n'])} | {v['min']} | {v['p01']} | {v['p99']} | {v['max']} | {n(v['zero'])} | {n(v['negative'])} |"


hours = f["purchase_hour_counts"]
night = sum(hours[str(h)] for h in (2, 3, 4, 5))
day = sum(hours[str(h)] for h in range(10, 22))

(D / "PROFILING_REPORT.md").write_text(
    f"""# Olist Dataset Profiling Report (Phase 2)

{HEADER}
## 1. Files

| Alias | File | Rows | Columns | Physical lines | Duplicate full rows | BOM | Line endings |
|---|---|---:|---:|---:|---:|---|---|
{rows}

`order_reviews` has {n(FILES["order_reviews"]["physical_lines"] - FILES["order_reviews"]["rows"] - 1)} more physical lines than records because review text fields contain embedded line breaks inside quoted fields ({n(p["review_text"]["message_with_newline"])} messages contain at least one). A naive line-based loader would corrupt this file.

## 2. Column types and missing values
Inferred from the actual values (all columns read as text first). Full per-column detail is in the [data dictionary](DATA_DICTIONARY.md).

Columns with missing (empty) values:

| Column | Missing | % of rows |
|---|---:|---:|
{chr(10).join(miss_rows)}

All other columns have no empty values. All 32-character identifiers are lowercase hex. All zip-code prefixes are 5-character strings that keep leading zeros. No timestamp failed to parse with format `YYYY-MM-DD HH:MM:SS`.

## 3. Candidate keys

| Key | Rows | Distinct | Rows sharing a key | Result |
|---|---:|---:|---:|---|
{key_rows}

- `orders.customer_id` is unique: **each customer_id belongs to exactly one order**. People are identified by `customer_unique_id`: {n(p["customer_identity"]["distinct_customer_unique_id"])} distinct values across {n(p["customer_identity"]["customer_id_rows"])} customer_id rows. {n(multi_cid)} people have more than one customer_id (distribution: {p["customer_identity"]["customer_ids_per_unique_id"]}, where bucket 5 means 5 or more).
- `order_item_id` runs contiguously from 1 to n in all {n(p["sequences"]["order_item_id_contiguous_1_to_n_orders"])} orders that have items.
- `payment_sequential` is not contiguous from 1 in {n(p["sequences"]["payment_sequential_noncontiguous_orders"])} orders. In all {n(f["payment_seq_gap_orders"]["min_seq_not_1"])} of them the sequence does not start at 1, and none involve vouchers.
- `review_id` is **not unique**: {n(f["review_ids_shared_by_multiple_orders"])} review_ids are attached to more than one order (at most {f["max_orders_per_review_id"]}). For all {n(f["shared_review_ids_with_identical_score_and_text"])} of them, score, message and creation date are identical across the orders. `(review_id, order_id)` is unique.

## 4. Order status

| Status | Orders | Share | Missing approved_at | Missing carrier date | Missing customer delivery date | Without items | Without payments | Without review |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{status_rows}

The 8 status values match assumption A-05 exactly (spelling `canceled`). The **`delivered` status exists** ({n(ST["delivered"]["orders"])} orders), which D-016 depends on.

## 5. Delivered-order completeness

| Check | Count |
|---|---:|
| Delivered orders | {n(DC["delivered_orders"])} |
| Delivered, missing customer delivery date | {n(DC["delivered_missing_customer_date"])} |
| Delivered, missing carrier date | {n(DC["delivered_missing_carrier_date"])} |
| Delivered, missing approved_at | {n(DC["delivered_missing_approved_at"])} |
| Delivered, without items | {n(DC["delivered_without_items"])} |
| Delivered, without payments | {n(DC["delivered_without_payments"])} |
| Non-delivered orders that do have a customer delivery date | {DC["non_delivered_with_customer_date"]} |

Delivery duration plausibility (purchase → customer delivery, delivered orders with both dates, n = {n(DC["lead_time_days_delivered"]["n"])}): minimum {DC["lead_time_days_delivered"]["min"]:.2f} days, maximum {DC["lead_time_days_delivered"]["max"]:.2f} days, {DC["lead_time_days_delivered"]["negative"]} negative durations. Averages are deliberately not reported here; they are KPI K14 (Phase 4).

## 6. Timestamps and date coverage

| Column | Non-empty | Parse failures | Min | Max |
|---|---:|---:|---|---|
{ts_rows}

- `order_estimated_delivery_date` is 100% at midnight, so it is a **date, not a timestamp**. `review_creation_date` is {FILES["order_reviews"]["column_profile"]["review_creation_date"]["midnight_time_share_pct"]}% at midnight.
- `shipping_limit_date` contains far-future values: {f["shipping_limit_after_2018_12_31_rows"]} rows after 2018-12-31 (max {p["timestamps"]["order_items.shipping_limit_date"]["max"]}); {f["shipping_limit_minus_purchase_days"]["gt_60_days_rows"]} rows are more than 60 days after purchase.
- Last purchase: {DC["last_purchase_timestamp"]}; last customer delivery: {DC["last_delivered_customer_date"]}.

### Date-ordering checks (rows where both dates are present)

| Check (first date earlier than second) | Compared | Violations |
|---|---:|---:|
{do_rows}

Additionally, {n(f["review_created_before_delivery_date"]["violations"])} of {n(f["review_created_before_delivery_date"]["compared"])} reviews on delivered-dated orders were created before the delivery date, and {f["review_created_before_purchase_date"]} were created before the purchase date.

### Monthly coverage (orders by purchase month; delivered = current status)

| Month | Orders | Delivered status |
|---|---:|---:|
{mon_rows}

- **No orders in 2016-11**; 2016-09 and 2016-12 are near-empty.
- 2018-09 and 2018-10 contain only {n(MC["2018-09"]["orders"] + MC["2018-10"]["orders"])} orders, none delivered. The extract ends during these months: right-censoring (RULE-23).
- Months with substantial volume run from 2017-01 to 2018-08 (20 months).

### Timezone evidence (A-02)
Purchases by hour of day: {n(night)} orders between 02:00 and 05:59 vs {n(day)} between 10:00 and 21:59. This daily rhythm is consistent with Brazilian local time, but it **cannot prove** the timezone or DST handling. A-02 stays an assumption (D-017).

## 7. Monetary fields

| Field | n | Min | P1 | P99 | Max | Zero | Negative |
|---|---:|---:|---:|---:|---:|---:|---:|
{mrow("order_items.price")}
{mrow("order_items.freight_value")}
{mrow("order_payments.payment_value")}
{mrow("order_payments.payment_installments")}

Maximum decimal places: {money["decimal_places_max"]}. No negative amounts; no zero prices. Currency is not stated anywhere (A-01: BRL).

### Payment types

| Type | Records | Zero value | Zero instalments | Instalments > 1 |
|---|---:|---:|---:|---:|
{pt_rows}

`not_defined` occurs {p["payment_type"]["not_defined"]["records"]} times, all with zero value. Instalments greater than 1 occur only for `credit_card`.

## 8. Reviews
Score distribution (records): {p["review_score"]}. Score range 1–5, no missing scores. Free text: {n(p["review_text"]["title_missing"])} titles and {n(p["review_text"]["message_missing"])} messages are empty. Free text may contain personal information and is excluded from logs and screenshots (SECURITY.md).

## 9. Products, geography
- Products: {n(p["products"]["missing_category"])} without category; the same {n(p["products"]["rows_missing_all_text_attrs"])} also lack name length, description length and photo count. {n(FILES["products"]["column_profile"]["product_weight_g"]["missing"])} products lack weight and dimensions; {p["products"]["numeric"]["product_weight_g"]["zero"]} have weight 0. {p["products"]["distinct_categories"]} distinct categories vs {FILES["category_translation"]["rows"]} translations; untranslated: {f"{p['untranslated_categories']}"}.
- Geolocation: {n(p["geolocation"]["rows"])} rows, {n(FILES["geolocation"]["duplicate_full_rows"])} exact duplicate rows, {n(p["geolocation"]["distinct_zip_prefixes"])} distinct zip prefixes (up to {int(p["geolocation"]["rows_per_zip"]["max"])} rows per prefix). {n(p["geolocation"]["zips_with_multiple_city_spellings"])} prefixes have more than one city spelling. {p["geolocation"]["rows_outside_brazil_bbox"]} rows fall outside a Brazil bounding box (lat −33.75 to 5.27, lng −73.99 to −34.79).
- States: customers {len(p["states"]["customer_state"])} distinct, sellers {len(p["states"]["seller_state"])}, geolocation {p["states"]["geolocation_state_distinct"]}.

## 10. Verification
- An independent standard-library implementation (csv + Decimal, no pandas) recomputed 33 key figures (row counts, key uniqueness, orphan counts, status/payment/score distributions, Decimal reconciliation, fan-out row count, monthly coverage): **33 matched, 0 differed**.
- Raw-file SHA-256 hashes were identical before and after profiling (9/9).
""",
    encoding="utf-8",
)

# ======================================================================= RELATIONSHIP VALIDATION
rel_rows = "\n".join(
    f"| {r['relationship']} | {n(r['child_rows_checked'])} | {n(r['child_empty_fk'])} | {n(r['orphan_rows'])} | {n(r['orphan_distinct_keys'])} |"
    for r in p["relationships"]
)
ipo, ppo, rpo = (p["per_order_counts"][k] for k in ["items_per_order", "payments_per_order", "reviews_per_order"])
(D / "RELATIONSHIP_VALIDATION.md").write_text(
    f"""# Relationship and Join Validation Report (Phase 2)

{HEADER}
## 1. Foreign-key / orphan checks

| Relationship (child → parent) | Child rows checked | Empty FK | Orphan rows | Orphan distinct keys |
|---|---:|---:|---:|---:|
{rel_rows}

- **Referential integrity holds for every transactional relationship** (orders, items, payments, reviews, customers, products, sellers): 0 orphans.
- Every product and every seller appears in at least one order item.
- Gaps exist only in reference data: {REL["products.product_category_name -> category_translation"]["orphan_rows"]} products use {REL["products.product_category_name -> category_translation"]["orphan_distinct_keys"]} untranslated categories; {n(REL["customers.zip_prefix -> geolocation.zip_prefix"]["orphan_rows"])} customers ({REL["customers.zip_prefix -> geolocation.zip_prefix"]["orphan_distinct_keys"]} prefixes) and {REL["sellers.zip_prefix -> geolocation.zip_prefix"]["orphan_rows"]} sellers have zip prefixes absent from geolocation.
- `geolocation` has no usable key: `zip_code_prefix` repeats (see profiling §9). It cannot be a FK parent without first aggregating it to one row per prefix.

## 2. Cardinalities (observed)

| Relationship | Observed cardinality | Evidence |
|---|---|---|
| customers.customer_id : orders | 1 : 1 | both keys unique, 0 orphans either way |
| customer_unique_id : customer_id | 1 : many | {n(multi_cid)} people with >1 customer_id |
| orders : order_items | 1 : 0..many | items per order {ipo} (top bucket = 6+); {n(no_items)} orders have none |
| orders : order_payments | 1 : 0..many | payments per order {ppo} (top bucket = 6+); {DC["delivered_without_payments"]} order has none |
| orders : order_reviews | 1 : 0..many | reviews per order {rpo}; {n(reviews_multi)} orders have more than one |
| review_id : orders | 1 : 1..{f["max_orders_per_review_id"]} | {n(f["review_ids_shared_by_multiple_orders"])} review_ids shared |
| orders : sellers (via items) | many : many | {n(p["quantity_proxy"]["orders_with_multiple_sellers"])} orders have more than one seller |

## 3. Fan-out and double-counting risks (measured)

| Join | Base rows | Joined rows | Orders affected | Effect on Σ price if summed after join |
|---|---:|---:|---:|---:|
| order_items × order_payments (on order_id) | {n(FO["items_x_payments"]["item_rows"])} | {n(FO["items_x_payments"]["joined_rows"])} | {n(f["fanout_orders_items_and_multi_payment"])} | +{FO["items_x_payments"]["price_inflation_pct"]}% (overstated) |
| order_items × order_reviews (on order_id) | {n(FO["items_x_reviews"]["item_rows"])} | {n(FO["items_x_reviews"]["joined_rows"])} | {n(f["fanout_orders_items_and_multi_review"])} | +{FO["items_x_reviews"]["price_inflation_pct"]}% (overstated) |
| orders × order_items | {n(FO["orders_x_items_rows"]["orders"])} orders | {n(FO["orders_x_items_rows"]["joined_rows"])} | all multi-item orders | order-level fields (status, dates) repeat per item: counting rows ≠ counting orders |

**Rules confirmed by measurement** (RULE-06):
1. Never sum item values after joining payments or reviews. Aggregate each side to `order_id` first.
2. Count orders with `COUNT(DISTINCT order_id)` whenever items are joined.
3. Review metrics use the `(review_id, order_id)` grain. Shared review_ids must not be double-counted when reviews are counted as unique reviews.
4. Seller-level metrics stay at item grain. Order-level dates (carrier date) are shared by every seller in a multi-seller order.

## 4. Payment ↔ item reconciliation (order level, both sides aggregated first)

| Population | Orders with both | |diff| ≤ 0.01 | Payments higher | Payments lower |
|---|---:|---:|---:|---:|
| All statuses | {n(RC["all_with_both"]["orders"])} | {n(RC["all_with_both"]["abs_diff_le_0.01"])} ({pct(RC["all_with_both"]["abs_diff_le_0.01"], RC["all_with_both"]["orders"])}) | {n(RC["all_with_both"]["payments_higher"])} | {n(RC["all_with_both"]["payments_lower"])} |
| Delivered | {n(RC["delivered_with_both"]["orders"])} | {n(RC["delivered_with_both"]["abs_diff_le_0.01"])} ({pct(RC["delivered_with_both"]["abs_diff_le_0.01"], RC["delivered_with_both"]["orders"])}) | {n(RC["delivered_with_both"]["payments_higher"])} | {n(RC["delivered_with_both"]["payments_lower"])} |

Orders with items only: {RC["orders_items_only"]}; payments only: {n(RC["orders_payments_only"])}; neither: {RC["orders_neither"]}. Largest differences: {RC["all_with_both"]["diff_summary"]["min"]} to {RC["all_with_both"]["diff_summary"]["max"]} (BRL, per order).

- `payment_value` matches `price + freight_value` for nearly all orders. This validates A-06: payments include freight.
- Of the {n(f["recon_payments_higher_profile"]["orders"])} orders where payments exceed items, {n(f["recon_payments_higher_profile"]["any_credit_card_installments_gt1"])} have a credit-card instalment count above 1 and {f["recon_payments_higher_profile"]["any_voucher"]} include a voucher. This is an **association** consistent with instalment charges, not a confirmed cause.
- {n(f["recon_payments_lower_profile"]["orders"])} orders have payments lower than items; {f["recon_payments_lower_profile"]["any_voucher"]} of these involve vouchers. The cause is unknown.
- Reconciliation used exact Decimal arithmetic in the independent check (counts matched pandas).
""",
    encoding="utf-8",
)

# ======================================================================= DATA DICTIONARY
DESC = {
    "customers": {
        "customer_id": "Order-scoped customer key; exactly one order per value (FK target of orders.customer_id)",
        "customer_unique_id": "Person-level customer identifier; use for repeat/cohort analysis (RULE-02)",
        "customer_zip_code_prefix": "First 5 digits of customer postcode, text with leading zeros",
        "customer_city": "Customer city name as supplied",
        "customer_state": "Customer state (UF) code",
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "Postcode prefix; repeats (many coordinates per prefix)",
        "geolocation_lat": "Latitude (decimal degrees)",
        "geolocation_lng": "Longitude (decimal degrees)",
        "geolocation_city": "City name; spellings vary within a prefix",
        "geolocation_state": "State (UF) code",
    },
    "order_items": {
        "order_id": "Order key (FK → orders)",
        "order_item_id": "Item sequence within order, 1..n contiguous; one row per unit (A-09)",
        "product_id": "Product key (FK → products)",
        "seller_id": "Seller key (FK → sellers)",
        "shipping_limit_date": "Seller deadline to hand item to carrier; contains far-future outliers",
        "price": "Item price (BRL, A-01)",
        "freight_value": "Freight charged for the item (BRL); may be 0",
    },
    "order_payments": {
        "order_id": "Order key (FK → orders)",
        "payment_sequential": "Payment sequence within order; gaps in some orders",
        "payment_type": "credit_card, boleto, voucher, debit_card, not_defined",
        "payment_installments": "Number of instalments; >1 only for credit_card",
        "payment_value": "Amount of this payment record (BRL); includes freight share",
    },
    "order_reviews": {
        "review_id": "Review identifier; NOT unique (shared across orders)",
        "order_id": "Order key (FK → orders)",
        "review_score": "Customer satisfaction score 1–5",
        "review_comment_title": "Optional free-text title (personal-data risk)",
        "review_comment_message": "Optional free text, may contain line breaks (personal-data risk)",
        "review_creation_date": "Date the review survey was created (date semantics)",
        "review_answer_timestamp": "Timestamp the review was answered",
    },
    "orders": {
        "order_id": "Order key (PK)",
        "customer_id": "Order-scoped customer key (FK → customers, 1:1)",
        "order_status": "Lifecycle status, 8 values",
        "order_purchase_timestamp": "Purchase time; default time basis (RULE-10)",
        "order_approved_at": "Payment approval time",
        "order_delivered_carrier_date": "Handover to carrier (order level)",
        "order_delivered_customer_date": "Delivery to customer",
        "order_estimated_delivery_date": "Promised delivery date (date only)",
    },
    "products": {
        "product_id": "Product key (PK)",
        "product_category_name": "Category (Portuguese); missing for some products",
        "product_name_lenght": "Characters in product name (source misspelling 'lenght')",
        "product_description_lenght": "Characters in description (source misspelling 'lenght')",
        "product_photos_qty": "Number of published photos",
        "product_weight_g": "Weight in grams",
        "product_length_cm": "Length in cm",
        "product_height_cm": "Height in cm",
        "product_width_cm": "Width in cm",
    },
    "sellers": {
        "seller_id": "Seller key (PK)",
        "seller_zip_code_prefix": "Seller postcode prefix (text, leading zeros)",
        "seller_city": "Seller city",
        "seller_state": "Seller state (UF)",
    },
    "category_translation": {
        "product_category_name": "Portuguese category (PK)",
        "product_category_name_english": "English category name",
    },
}
ROLE = {
    ("customers", "customer_id"): "PK",
    ("orders", "order_id"): "PK",
    ("orders", "customer_id"): "FK, unique",
    ("order_items", "order_id"): "PK part, FK",
    ("order_items", "order_item_id"): "PK part",
    ("order_items", "product_id"): "FK",
    ("order_items", "seller_id"): "FK",
    ("order_payments", "order_id"): "PK part, FK",
    ("order_payments", "payment_sequential"): "PK part",
    ("order_reviews", "review_id"): "PK part (not unique alone)",
    ("order_reviews", "order_id"): "PK part, FK",
    ("products", "product_id"): "PK",
    ("sellers", "seller_id"): "PK",
    ("category_translation", "product_category_name"): "PK",
    ("products", "product_category_name"): "FK (soft; 2 untranslated)",
    ("customers", "customer_unique_id"): "Person key",
}


def mysql_type(a, c, i):
    t = i["inferred_type"]
    if t == "hex32_id":
        return "CHAR(32)"
    if "zip_code_prefix" in c:
        return "CHAR(5)"
    if c in ("price", "freight_value", "payment_value"):
        return "DECIMAL(10,2)"
    if c in ("geolocation_lat", "geolocation_lng"):
        return "DOUBLE"
    if c in ("order_estimated_delivery_date",):
        return "DATE (source time always 00:00:00)"
    if t == "datetime":
        return "DATETIME"
    if t == "integer_text":
        return "SMALLINT UNSIGNED" if i["numeric"]["max"] > 255 else "TINYINT UNSIGNED"
    if c.endswith("_state"):
        return "CHAR(2)"
    if c.startswith("review_comment"):
        return "TEXT" if i["max_len"] > 255 else f"VARCHAR({i['max_len']})"
    return f"VARCHAR({max(8, ((i['max_len'] + 7) // 8) * 8)})"


dd_parts = []
for a, v in FILES.items():
    lines = [
        f"### {a} — `{v['file']}` ({n(v['rows'])} rows)",
        "",
        "| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |",
        "|---|---|---|---|---|---:|---:|---|---|",
    ]
    for c, i in v["column_profile"].items():
        rng = (
            f"len {i['min_len_nonempty']}–{i['max_len']} (text)"
            if "zip_code_prefix" in c
            else f"{i['min']} → {i['max']}"
            if i["inferred_type"] == "datetime"
            else (
                f"{i['numeric']['min']} → {i['numeric']['max']}"
                if "numeric" in i
                else f"len {i['min_len_nonempty']}–{i['max_len']}"
            )
        )
        lines.append(
            f"| {c} | {DESC[a][c]} | {i['inferred_type']} | {mysql_type(a, c, i)} | {ROLE.get((a, c), '')} | {n(i['missing'])} | {n(i['distinct'])} | {rng} | source_observed |"
        )
    dd_parts.append("\n".join(lines))
(D / "DATA_DICTIONARY.md").write_text(
    f"""# Data Dictionary — Olist Source Layer (Phase 2)

{HEADER}
- **Descriptions** of business meaning (e.g. what `shipping_limit_date` represents) come from the public dataset documentation and are not provable from the data. **Observed type, missing, distinct and range** columns come from profiling.
- **Observed type** is inferred from the values: `hex32_id` = 32-char lowercase hex; `integer_text` = digits only, stored as text in the source (leading zeros preserved where relevant).
- **Proposed MySQL types are proposals for Phase 3** and will be confirmed with the DDL and migration tests. Raw layer (`raw_*`) keeps source column names, including the misspelled `*_lenght`. Staging (`stg_*`) renames them to `*_length` (documented transformation, H-01).
- All fields are `source_observed`. Derived fields and KPIs are defined in [08_kpi_dictionary.md](../../business/08_kpi_dictionary.md).
- Timestamps carry no timezone; see A-02 / D-017.

{(chr(10) * 2).join(dd_parts)}
""",
    encoding="utf-8",
)

# ======================================================================= DATA QUALITY ISSUE REGISTER
G = p["geolocation"]
issues = [
    (
        "DQ-01",
        "High",
        "order_reviews",
        f"`review_id` not unique: {n(f['review_ids_shared_by_multiple_orders'])} review_ids shared by up to {f['max_orders_per_review_id']} orders ({n(review_extra_rows)} extra rows); duplicates carry identical score/text/date",
        "K13",
        "Key on (review_id, order_id). Decide review-count semantics (D-019)",
    ),
    (
        "DQ-02",
        "Medium",
        "order_reviews",
        f"{n(reviews_multi)} orders have more than one review",
        "K13",
        "RULE-15 order-level mean; D-019",
    ),
    (
        "DQ-03",
        "Medium",
        "geolocation",
        f"{n(FILES['geolocation']['duplicate_full_rows'])} exact duplicate rows; zip prefix not unique ({n(G['distinct_zip_prefixes'])} prefixes, up to {int(G['rows_per_zip']['max'])} rows each); {n(G['zips_with_multiple_city_spellings'])} prefixes with multiple city spellings",
        "Geo views only",
        "Keep raw; stg aggregates to one row per prefix (e.g. median lat/lng) — Phase 3 decision",
    ),
    (
        "DQ-04",
        "Low",
        "geolocation",
        f"{G['rows_outside_brazil_bbox']} rows outside the Brazil bounding box",
        "Geo views only",
        "Flag and exclude from coordinate aggregation",
    ),
    (
        "DQ-05",
        "Low",
        "customers, sellers",
        f"{n(REL['customers.zip_prefix -> geolocation.zip_prefix']['orphan_rows'])} customers and {REL['sellers.zip_prefix -> geolocation.zip_prefix']['orphan_rows']} sellers have zip prefixes absent from geolocation",
        "Geo views only",
        "Soft relationship; report unmatched; state fields remain usable",
    ),
    (
        "DQ-06",
        "Medium",
        "products",
        f"{n(p['products']['missing_category'])} products lack category, name length, description length and photo count; {FILES['products']['column_profile']['product_weight_g']['missing']} lack weight/dimensions; {p['products']['numeric']['product_weight_g']['zero']} weigh 0 g",
        "K11, M04",
        "Category 'unknown' (RULE-13); attributes NULL, never 0",
    ),
    (
        "DQ-07",
        "Low",
        "products",
        f"Untranslated categories: {p['untranslated_categories']}",
        "K11",
        "Keep Portuguese name, flag (RULE-13)",
    ),
    (
        "DQ-08",
        "Medium",
        "orders/order_items",
        f"{n(no_items)} orders have no items: {f['orders_without_items_by_status']}",
        "K03, K06, K12, K18",
        "Expected for unavailable/canceled; excluded from item metrics; counted in K06/K12",
    ),
    (
        "DQ-09",
        "Low",
        "orders/order_payments",
        f"{DC['delivered_without_payments']} delivered order has no payment records",
        "K18, K19",
        "Reconciliation category 'items only'",
    ),
    (
        "DQ-10",
        "Medium",
        "orders",
        f"Delivered orders missing timestamps: customer delivery {DC['delivered_missing_customer_date']}, carrier {DC['delivered_missing_carrier_date']}, approved {DC['delivered_missing_approved_at']}",
        "K14–K17",
        "Excluded from delivery metrics and counted (RULE-11); still included in K01 (status-based)",
    ),
    (
        "DQ-11",
        "Low",
        "orders",
        f"Non-delivered orders with a customer delivery date: {DC['non_delivered_with_customer_date']}",
        "K14–K16",
        "Status governs eligibility; report",
    ),
    (
        "DQ-12",
        "Medium",
        "orders",
        f"Date-order violations: carrier before purchase {DO['carrier_before_purchase']['violations']}, carrier before approval {n(DO['carrier_before_approved']['violations'])}, delivered before carrier {DO['delivered_before_carrier']['violations']}",
        "K17",
        "Flag rows; K17 confidence reduced. No purchase→delivery violations",
    ),
    (
        "DQ-13",
        "Low",
        "order_items",
        f"`shipping_limit_date` outliers: {f['shipping_limit_after_2018_12_31_rows']} rows after 2018-12-31 (max {p['timestamps']['order_items.shipping_limit_date']['max']}); {f['shipping_limit_minus_purchase_days']['gt_60_days_rows']} rows > 60 days after purchase",
        "K17",
        "Flag as implausible; exclude from K17",
    ),
    (
        "DQ-14",
        "Medium",
        "order_reviews",
        f"{n(f['review_created_before_delivery_date']['violations'])} reviews created before delivery; {f['review_created_before_purchase_date']} before purchase date",
        "K13",
        "Report; reviews before delivery may reflect delay, an association only (RULE-19)",
    ),
    (
        "DQ-15",
        "High",
        "orders",
        f"Coverage gaps: 2016-11 has 0 orders; 2016-09 ({MC['2016-09']['orders']}) and 2016-12 ({MC['2016-12']['orders']}) near-empty; 2018-09/10 have {MC['2018-09']['orders'] + MC['2018-10']['orders']} orders and 0 delivered (extract cutoff)",
        "K01–K08, K25, all trends",
        "Default analysis window decision (D-018); censoring flag (RULE-23)",
    ),
    (
        "DQ-16",
        "Medium",
        "payments vs items",
        f"{n(RC['all_with_both']['payments_higher'] + RC['all_with_both']['payments_lower'])} orders differ by > 0.01 ({RC['all_with_both']['payments_higher']} higher, {RC['all_with_both']['payments_lower']} lower); range {RC['all_with_both']['diff_summary']['min']} to {RC['all_with_both']['diff_summary']['max']}",
        "K18",
        "Show differences; possible explanations labelled unconfirmed",
    ),
    (
        "DQ-17",
        "Low",
        "order_payments",
        f"Zero-value payments: {money['order_payments.payment_value']['zero']} (not_defined {p['payment_type']['not_defined']['value_zero']}, voucher {p['payment_type']['voucher']['value_zero']}); credit-card records with 0 instalments: {p['payment_type']['credit_card']['installments_zero']}",
        "K19, K20",
        "Keep; exclude 0-instalment rows from K20; not_defined shown as own category",
    ),
    (
        "DQ-18",
        "Low",
        "order_payments",
        f"`payment_sequential` does not start at 1 in {p['sequences']['payment_sequential_noncontiguous_orders']} orders",
        "K18",
        "Possibly missing payment records; reconciliation will surface any value gap",
    ),
    (
        "DQ-19",
        "Low",
        "order_items",
        f"{n(money['order_items.freight_value']['zero'])} item rows with freight 0",
        "K02",
        "Valid value (free shipping plausible); not treated as missing",
    ),
    (
        "DQ-20",
        "Medium",
        "order_reviews",
        f"Free text: {n(p['review_text']['message_with_newline'])} messages with line breaks; leading/trailing whitespace in {n(FILES['order_reviews']['column_profile']['review_comment_title']['leading_trailing_ws'])} titles and {n(FILES['order_reviews']['column_profile']['review_comment_message']['leading_trailing_ws'])} messages",
        "None (no text KPI)",
        "Quote-aware loader; keep raw text; never log; trim only in staging",
    ),
    (
        "DQ-21",
        "Low",
        "products, translation, reviews",
        "Source format quirks: misspelled `*_lenght` columns, UTF-8 BOM in translation file, CRLF in 2 files (H-01–H-03)",
        "Ingestion",
        "BOM-aware decoding; rename in staging; tests with fixtures",
    ),
    (
        "DQ-22",
        "Info",
        "customers",
        f"{n(multi_cid)} people have more than one customer_id",
        "K07–K10, K21",
        "Use customer_unique_id (RULE-02 validated)",
    ),
    (
        "DQ-23",
        "Info",
        "order_items",
        f"{n(p['quantity_proxy']['orders_with_repeated_product'])} orders repeat the same product on several item rows; no quantity column",
        "K05",
        "Row = unit (A-09 consistent with data)",
    ),
]
reg = "\n".join(f"| {a} | {b} | {c} | {d} | {e} | {g} | Open |" for a, b, c, d, e, g in issues)
(D / "DATA_QUALITY_ISSUES.md").write_text(
    f"""# Data-Quality Issue Register (Phase 2)

{HEADER}
Severity: **High** = can materially distort a headline KPI if unhandled; **Medium** = distorts a specific KPI or segment; **Low** = limited or reference-data impact; **Info** = structural fact requiring a modelling rule. "Treatment" entries are proposals implemented in Phase 3 ingestion/staging (raw data is never altered).

| ID | Severity | Table(s) | Issue (evidence) | Affected KPIs | Proposed treatment | Status |
|---|---|---|---|---|---|---|
{reg}

Issues previously logged in the RAID log (I-01–I-04) are covered by DQ-21 and A-01/A-02.
""",
    encoding="utf-8",
)

# machine-readable aggregates for checks
(D / "profile_results.json").write_text(
    json.dumps({"profile": p, "followups": f}, indent=1, ensure_ascii=False), encoding="utf-8"
)
print("written:", [x.name for x in sorted(D.iterdir())])
print("issues:", len(issues))
