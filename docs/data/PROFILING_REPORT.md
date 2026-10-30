# Olist Dataset Profiling Report (Phase 2)

> Generated 2026-10-31 from the Phase 2 profiler output ([profile_results.json](profile_results.json)). Every number below is copied programmatically from that file.
> Source: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0), files in `data/raw/olist/` (not committed). Raw files were read only; SHA-256 hashes were identical before and after profiling.
> Aggregates only. No customer-, seller- or order-level rows are reproduced. **No KPI values are calculated here** (KPIs are implemented in Phase 4).

## 1. Files

| Alias | File | Rows | Columns | Physical lines | Duplicate full rows | BOM | Line endings |
|---|---|---:|---:|---:|---:|---|---|
| customers | `olist_customers_dataset.csv` | 99,441 | 5 | 99,442 | 0 | no | LF |
| geolocation | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | 1,000,164 | 261,831 | no | LF |
| order_items | `olist_order_items_dataset.csv` | 112,650 | 7 | 112,651 | 0 | no | LF |
| order_payments | `olist_order_payments_dataset.csv` | 103,886 | 5 | 103,887 | 0 | no | LF |
| order_reviews | `olist_order_reviews_dataset.csv` | 99,224 | 7 | 104,720 | 0 | no | CRLF |
| orders | `olist_orders_dataset.csv` | 99,441 | 8 | 99,442 | 0 | no | LF |
| products | `olist_products_dataset.csv` | 32,951 | 9 | 32,952 | 0 | no | LF |
| sellers | `olist_sellers_dataset.csv` | 3,095 | 4 | 3,096 | 0 | no | LF |
| category_translation | `product_category_name_translation.csv` | 71 | 2 | 71 | 0 | yes | CRLF |

`order_reviews` has 5,495 more physical lines than records because review text fields contain embedded line breaks inside quoted fields (3,852 messages contain at least one). A naive line-based loader would corrupt this file.

## 2. Column types and missing values
Inferred from the actual values (all columns read as text first). Full per-column detail is in the [data dictionary](DATA_DICTIONARY.md).

Columns with missing (empty) values:

| Column | Missing | % of rows |
|---|---:|---:|
| order_reviews.review_comment_title | 87,656 | 88.34% |
| order_reviews.review_comment_message | 58,247 | 58.70% |
| orders.order_approved_at | 160 | 0.16% |
| orders.order_delivered_carrier_date | 1,783 | 1.79% |
| orders.order_delivered_customer_date | 2,965 | 2.98% |
| products.product_category_name | 610 | 1.85% |
| products.product_name_lenght | 610 | 1.85% |
| products.product_description_lenght | 610 | 1.85% |
| products.product_photos_qty | 610 | 1.85% |
| products.product_weight_g | 2 | 0.01% |
| products.product_length_cm | 2 | 0.01% |
| products.product_height_cm | 2 | 0.01% |
| products.product_width_cm | 2 | 0.01% |

All other columns have no empty values. All 32-character identifiers are lowercase hex. All zip-code prefixes are 5-character strings that keep leading zeros. No timestamp failed to parse with format `YYYY-MM-DD HH:MM:SS`.

## 3. Candidate keys

| Key | Rows | Distinct | Rows sharing a key | Result |
|---|---:|---:|---:|---|
| customers.customer_id | 99,441 | 99,441 | 0 | **unique** |
| orders.order_id | 99,441 | 99,441 | 0 | **unique** |
| orders.customer_id | 99,441 | 99,441 | 0 | **unique** |
| order_items.(order_id,order_item_id) | 112,650 | 112,650 | 0 | **unique** |
| order_payments.(order_id,payment_sequential) | 103,886 | 103,886 | 0 | **unique** |
| order_reviews.review_id | 99,224 | 98,410 | 1,603 | **not unique** |
| order_reviews.(review_id,order_id) | 99,224 | 99,224 | 0 | **unique** |
| order_reviews.order_id | 99,224 | 98,673 | 1,098 | **not unique** |
| products.product_id | 32,951 | 32,951 | 0 | **unique** |
| sellers.seller_id | 3,095 | 3,095 | 0 | **unique** |
| category_translation.product_category_name | 71 | 71 | 0 | **unique** |
| geolocation.(all columns) | 1,000,163 | 738,332 | 390,005 | **not unique** |
| geolocation.geolocation_zip_code_prefix | 1,000,163 | 19,015 | 999,120 | **not unique** |

- `orders.customer_id` is unique: **each customer_id belongs to exactly one order**. People are identified by `customer_unique_id`: 96,096 distinct values across 99,441 customer_id rows. 2,997 people have more than one customer_id (distribution: {'1': 93099, '2': 2745, '3': 203, '4': 30, '5': 19}, where bucket 5 means 5 or more).
- `order_item_id` runs contiguously from 1 to n in all 98,666 orders that have items.
- `payment_sequential` is not contiguous from 1 in 80 orders. In all 80 of them the sequence does not start at 1, and none involve vouchers.
- `review_id` is **not unique**: 789 review_ids are attached to more than one order (at most 3). For all 789 of them, score, message and creation date are identical across the orders. `(review_id, order_id)` is unique.

## 4. Order status

| Status | Orders | Share | Missing approved_at | Missing carrier date | Missing customer delivery date | Without items | Without payments | Without review |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delivered | 96,478 | 97.02% | 14 | 2 | 8 | 0 | 1 | 646 |
| shipped | 1,107 | 1.11% | 0 | 0 | 1,107 | 1 | 0 | 75 |
| canceled | 625 | 0.63% | 141 | 550 | 619 | 164 | 0 | 20 |
| unavailable | 609 | 0.61% | 0 | 609 | 609 | 603 | 0 | 14 |
| invoiced | 314 | 0.32% | 0 | 314 | 314 | 2 | 0 | 5 |
| processing | 301 | 0.30% | 0 | 301 | 301 | 0 | 0 | 6 |
| created | 5 | 0.01% | 5 | 5 | 5 | 5 | 0 | 2 |
| approved | 2 | 0.00% | 0 | 2 | 2 | 0 | 0 | 0 |

The 8 status values match assumption A-05 exactly (spelling `canceled`). The **`delivered` status exists** (96,478 orders), which D-016 depends on.

## 5. Delivered-order completeness

| Check | Count |
|---|---:|
| Delivered orders | 96,478 |
| Delivered, missing customer delivery date | 8 |
| Delivered, missing carrier date | 2 |
| Delivered, missing approved_at | 14 |
| Delivered, without items | 0 |
| Delivered, without payments | 1 |
| Non-delivered orders that do have a customer delivery date | {'canceled': 6} |

Delivery duration plausibility (purchase → customer delivery, delivered orders with both dates, n = 96,470): minimum 0.53 days, maximum 209.63 days, 0 negative durations. Averages are deliberately not reported here; they are KPI K14 (Phase 4).

## 6. Timestamps and date coverage

| Column | Non-empty | Parse failures | Min | Max |
|---|---:|---:|---|---|
| orders.order_purchase_timestamp | 99,441 | 0 | 2016-09-04 21:15:19 | 2018-10-17 17:30:18 |
| orders.order_approved_at | 99,281 | 0 | 2016-09-15 12:16:38 | 2018-09-03 17:40:06 |
| orders.order_delivered_carrier_date | 97,658 | 0 | 2016-10-08 10:34:01 | 2018-09-11 19:48:28 |
| orders.order_delivered_customer_date | 96,476 | 0 | 2016-10-11 13:46:32 | 2018-10-17 13:22:46 |
| orders.order_estimated_delivery_date | 99,441 | 0 | 2016-09-30 00:00:00 | 2018-11-12 00:00:00 |
| order_items.shipping_limit_date | 112,650 | 0 | 2016-09-19 00:15:34 | 2020-04-09 22:35:08 |
| order_reviews.review_creation_date | 99,224 | 0 | 2016-10-02 00:00:00 | 2018-08-31 00:00:00 |
| order_reviews.review_answer_timestamp | 99,224 | 0 | 2016-10-07 18:32:28 | 2018-10-29 12:27:35 |

- `order_estimated_delivery_date` is 100% at midnight, so it is a **date, not a timestamp**. `review_creation_date` is 99.9143% at midnight.
- `shipping_limit_date` contains far-future values: 4 rows after 2018-12-31 (max 2020-04-09 22:35:08); 12 rows are more than 60 days after purchase.
- Last purchase: 2018-10-17 17:30:18; last customer delivery: 2018-10-17 13:22:46.

### Date-ordering checks (rows where both dates are present)

| Check (first date earlier than second) | Compared | Violations |
|---|---:|---:|
| approved before purchase | 99,281 | 0 |
| carrier before purchase | 97,658 | 166 |
| carrier before approved | 97,644 | 1,359 |
| delivered before purchase | 96,476 | 0 |
| delivered before carrier | 96,475 | 23 |
| estimated before purchase | 99,441 | 0 |
| review answer before creation | 99,224 | 0 |

Additionally, 5,127 of 96,359 reviews on delivered-dated orders were created before the delivery date, and 64 were created before the purchase date.

### Monthly coverage (orders by purchase month; delivered = current status)

| Month | Orders | Delivered status |
|---|---:|---:|
| 2016-09 | 4 | 1 |
| 2016-10 | 324 | 265 |
| 2016-12 | 1 | 1 |
| 2017-01 | 800 | 750 |
| 2017-02 | 1,780 | 1,653 |
| 2017-03 | 2,682 | 2,546 |
| 2017-04 | 2,404 | 2,303 |
| 2017-05 | 3,700 | 3,546 |
| 2017-06 | 3,245 | 3,135 |
| 2017-07 | 4,026 | 3,872 |
| 2017-08 | 4,331 | 4,193 |
| 2017-09 | 4,285 | 4,150 |
| 2017-10 | 4,631 | 4,478 |
| 2017-11 | 7,544 | 7,289 |
| 2017-12 | 5,673 | 5,513 |
| 2018-01 | 7,269 | 7,069 |
| 2018-02 | 6,728 | 6,555 |
| 2018-03 | 7,211 | 7,003 |
| 2018-04 | 6,939 | 6,798 |
| 2018-05 | 6,873 | 6,749 |
| 2018-06 | 6,167 | 6,099 |
| 2018-07 | 6,292 | 6,159 |
| 2018-08 | 6,512 | 6,351 |
| 2018-09 | 16 | 0 |
| 2018-10 | 4 | 0 |

- **No orders in 2016-11**; 2016-09 and 2016-12 are near-empty.
- 2018-09 and 2018-10 contain only 20 orders, none delivered. The extract ends during these months: right-censoring (RULE-23).
- Months with substantial volume run from 2017-01 to 2018-08 (20 months).

### Timezone evidence (A-02)
Purchases by hour of day: 1,176 orders between 02:00 and 05:59 vs 75,277 between 10:00 and 21:59. This daily rhythm is consistent with Brazilian local time, but it **cannot prove** the timezone or DST handling. A-02 stays an assumption (D-017).

## 7. Monetary fields

| Field | n | Min | P1 | P99 | Max | Zero | Negative |
|---|---:|---:|---:|---:|---:|---:|---:|
| order_items.price | 112,650 | 0.85 | 9.99 | 890.0 | 6735.0 | 0 | 0 |
| order_items.freight_value | 112,650 | 0.0 | 4.4198 | 84.52 | 409.68 | 383 | 0 |
| order_payments.payment_value | 103,886 | 0.0 | 6.69 | 1039.9165 | 13664.08 | 9 | 0 |
| order_payments.payment_installments | 103,886 | 0 | 1.0 | 10.0 | 24 | 2 | 0 |

Maximum decimal places: {'price': 2, 'freight_value': 2, 'payment_value': 2}. No negative amounts; no zero prices. Currency is not stated anywhere (A-01: BRL).

### Payment types

| Type | Records | Zero value | Zero instalments | Instalments > 1 |
|---|---:|---:|---:|---:|
| boleto | 19,784 | 0 | 0 | 0 |
| credit_card | 76,795 | 0 | 2 | 51,338 |
| debit_card | 1,529 | 0 | 0 | 0 |
| not_defined | 3 | 3 | 0 | 0 |
| voucher | 5,775 | 6 | 0 | 0 |

`not_defined` occurs 3 times, all with zero value. Instalments greater than 1 occur only for `credit_card`.

## 8. Reviews
Score distribution (records): {'1': 11424, '2': 3151, '3': 8179, '4': 19142, '5': 57328}. Score range 1–5, no missing scores. Free text: 87,656 titles and 58,247 messages are empty. Free text may contain personal information and is excluded from logs and screenshots (SECURITY.md).

## 9. Products, geography
- Products: 610 without category; the same 610 also lack name length, description length and photo count. 2 products lack weight and dimensions; 4 have weight 0. 73 distinct categories vs 71 translations; untranslated: {'pc_gamer': 3, 'portateis_cozinha_e_preparadores_de_alimentos': 10}.
- Geolocation: 1,000,163 rows, 261,831 exact duplicate rows, 19,015 distinct zip prefixes (up to 1146 rows per prefix). 8,556 prefixes have more than one city spelling. 42 rows fall outside a Brazil bounding box (lat −33.75 to 5.27, lng −73.99 to −34.79).
- States: customers 27 distinct, sellers 23, geolocation 27.

## 10. Verification
- An independent standard-library implementation (csv + Decimal, no pandas) recomputed 33 key figures (row counts, key uniqueness, orphan counts, status/payment/score distributions, Decimal reconciliation, fan-out row count, monthly coverage): **33 matched, 0 differed**.
- Raw-file SHA-256 hashes were identical before and after profiling (9/9).
