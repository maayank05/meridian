# Data Dictionary — Olist Source Layer (Phase 2)

> Generated 2026-10-31 from the Phase 2 profiler output ([profile_results.json](profile_results.json)). Every number below is copied programmatically from that file.
> Source: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0), files in `data/raw/olist/` (not committed). Raw files were read only; SHA-256 hashes were identical before and after profiling.
> Aggregates only. No customer-, seller- or order-level rows are reproduced. **No KPI values are calculated here** (KPIs are implemented in Phase 4).

- **Descriptions** of business meaning (e.g. what `shipping_limit_date` represents) come from the public dataset documentation and are not provable from the data. **Observed type, missing, distinct and range** columns come from profiling.
- **Observed type** is inferred from the values: `hex32_id` = 32-char lowercase hex; `integer_text` = digits only, stored as text in the source (leading zeros preserved where relevant).
- **Proposed MySQL types are proposals for Phase 3** and will be confirmed with the DDL and migration tests. Raw layer (`raw_*`) keeps source column names, including the misspelled `*_lenght`. Staging (`stg_*`) renames them to `*_length` (documented transformation, H-01).
- All fields are `source_observed`. Derived fields and KPIs are defined in [08_kpi_dictionary.md](../../business/08_kpi_dictionary.md).
- Timestamps carry no timezone; see A-02 / D-017.

### customers — `olist_customers_dataset.csv` (99,441 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| customer_id | Order-scoped customer key; exactly one order per value (FK target of orders.customer_id) | hex32_id | CHAR(32) | PK | 0 | 99,441 | len 32–32 | source_observed |
| customer_unique_id | Person-level customer identifier; use for repeat/cohort analysis (RULE-02) | hex32_id | CHAR(32) | Person key | 0 | 96,096 | len 32–32 | source_observed |
| customer_zip_code_prefix | First 5 digits of customer postcode, text with leading zeros | integer_text | CHAR(5) |  | 0 | 14,994 | len 5–5 (text) | source_observed |
| customer_city | Customer city name as supplied | text | VARCHAR(32) |  | 0 | 4,119 | len 3–32 | source_observed |
| customer_state | Customer state (UF) code | text | CHAR(2) |  | 0 | 27 | len 2–2 | source_observed |

### geolocation — `olist_geolocation_dataset.csv` (1,000,163 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| geolocation_zip_code_prefix | Postcode prefix; repeats (many coordinates per prefix) | integer_text | CHAR(5) |  | 0 | 19,015 | len 5–5 (text) | source_observed |
| geolocation_lat | Latitude (decimal degrees) | decimal | DOUBLE |  | 0 | 717,372 | -36.605374 → 45.065933 | source_observed |
| geolocation_lng | Longitude (decimal degrees) | decimal | DOUBLE |  | 0 | 717,615 | -101.466766 → 121.105394 | source_observed |
| geolocation_city | City name; spellings vary within a prefix | text | VARCHAR(40) |  | 0 | 8,011 | len 2–38 | source_observed |
| geolocation_state | State (UF) code | text | CHAR(2) |  | 0 | 27 | len 2–2 | source_observed |

### order_items — `olist_order_items_dataset.csv` (112,650 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| order_id | Order key (FK → orders) | hex32_id | CHAR(32) | PK part, FK | 0 | 98,666 | len 32–32 | source_observed |
| order_item_id | Item sequence within order, 1..n contiguous; one row per unit (A-09) | integer_text | TINYINT UNSIGNED | PK part | 0 | 21 | 1 → 21 | source_observed |
| product_id | Product key (FK → products) | hex32_id | CHAR(32) | FK | 0 | 32,951 | len 32–32 | source_observed |
| seller_id | Seller key (FK → sellers) | hex32_id | CHAR(32) | FK | 0 | 3,095 | len 32–32 | source_observed |
| shipping_limit_date | Seller deadline to hand item to carrier; contains far-future outliers | datetime | DATETIME |  | 0 | 93,318 | 2016-09-19 00:15:34 → 2020-04-09 22:35:08 | source_observed |
| price | Item price (BRL, A-01) | decimal | DECIMAL(10,2) |  | 0 | 5,968 | 0.85 → 6735.0 | source_observed |
| freight_value | Freight charged for the item (BRL); may be 0 | decimal | DECIMAL(10,2) |  | 0 | 6,999 | 0.0 → 409.68 | source_observed |

### order_payments — `olist_order_payments_dataset.csv` (103,886 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| order_id | Order key (FK → orders) | hex32_id | CHAR(32) | PK part, FK | 0 | 99,440 | len 32–32 | source_observed |
| payment_sequential | Payment sequence within order; gaps in some orders | integer_text | TINYINT UNSIGNED | PK part | 0 | 29 | 1 → 29 | source_observed |
| payment_type | credit_card, boleto, voucher, debit_card, not_defined | text | VARCHAR(16) |  | 0 | 5 | len 6–11 | source_observed |
| payment_installments | Number of instalments; >1 only for credit_card | integer_text | TINYINT UNSIGNED |  | 0 | 24 | 0 → 24 | source_observed |
| payment_value | Amount of this payment record (BRL); includes freight share | decimal | DECIMAL(10,2) |  | 0 | 29,077 | 0.0 → 13664.08 | source_observed |

### order_reviews — `olist_order_reviews_dataset.csv` (99,224 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| review_id | Review identifier; NOT unique (shared across orders) | hex32_id | CHAR(32) | PK part (not unique alone) | 0 | 98,410 | len 32–32 | source_observed |
| order_id | Order key (FK → orders) | hex32_id | CHAR(32) | PK part, FK | 0 | 98,673 | len 32–32 | source_observed |
| review_score | Customer satisfaction score 1–5 | integer_text | TINYINT UNSIGNED |  | 0 | 5 | 1 → 5 | source_observed |
| review_comment_title | Optional free-text title (personal-data risk) | text | VARCHAR(26) |  | 87,656 | 4,527 | len 1–26 | source_observed |
| review_comment_message | Optional free text, may contain line breaks (personal-data risk) | text | VARCHAR(208) |  | 58,247 | 36,159 | len 1–208 | source_observed |
| review_creation_date | Date the review survey was created (date semantics) | datetime | DATETIME |  | 0 | 636 | 2016-10-02 00:00:00 → 2018-08-31 00:00:00 | source_observed |
| review_answer_timestamp | Timestamp the review was answered | datetime | DATETIME |  | 0 | 98,248 | 2016-10-07 18:32:28 → 2018-10-29 12:27:35 | source_observed |

### orders — `olist_orders_dataset.csv` (99,441 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| order_id | Order key (PK) | hex32_id | CHAR(32) | PK | 0 | 99,441 | len 32–32 | source_observed |
| customer_id | Order-scoped customer key (FK → customers, 1:1) | hex32_id | CHAR(32) | FK, unique | 0 | 99,441 | len 32–32 | source_observed |
| order_status | Lifecycle status, 8 values | text | VARCHAR(16) |  | 0 | 8 | len 7–11 | source_observed |
| order_purchase_timestamp | Purchase time; default time basis (RULE-10) | datetime | DATETIME |  | 0 | 98,875 | 2016-09-04 21:15:19 → 2018-10-17 17:30:18 | source_observed |
| order_approved_at | Payment approval time | datetime | DATETIME |  | 160 | 90,733 | 2016-09-15 12:16:38 → 2018-09-03 17:40:06 | source_observed |
| order_delivered_carrier_date | Handover to carrier (order level) | datetime | DATETIME |  | 1,783 | 81,018 | 2016-10-08 10:34:01 → 2018-09-11 19:48:28 | source_observed |
| order_delivered_customer_date | Delivery to customer | datetime | DATETIME |  | 2,965 | 95,664 | 2016-10-11 13:46:32 → 2018-10-17 13:22:46 | source_observed |
| order_estimated_delivery_date | Promised delivery date (date only) | datetime | DATE (source time always 00:00:00) |  | 0 | 459 | 2016-09-30 00:00:00 → 2018-11-12 00:00:00 | source_observed |

### products — `olist_products_dataset.csv` (32,951 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| product_id | Product key (PK) | hex32_id | CHAR(32) | PK | 0 | 32,951 | len 32–32 | source_observed |
| product_category_name | Category (Portuguese); missing for some products | text | VARCHAR(48) | FK (soft; 2 untranslated) | 610 | 73 | len 3–46 | source_observed |
| product_name_lenght | Characters in product name (source misspelling 'lenght') | integer_text | TINYINT UNSIGNED |  | 610 | 66 | 5 → 76 | source_observed |
| product_description_lenght | Characters in description (source misspelling 'lenght') | integer_text | SMALLINT UNSIGNED |  | 610 | 2,960 | 4 → 3992 | source_observed |
| product_photos_qty | Number of published photos | integer_text | TINYINT UNSIGNED |  | 610 | 19 | 1 → 20 | source_observed |
| product_weight_g | Weight in grams | integer_text | SMALLINT UNSIGNED |  | 2 | 2,204 | 0 → 40425 | source_observed |
| product_length_cm | Length in cm | integer_text | TINYINT UNSIGNED |  | 2 | 99 | 7 → 105 | source_observed |
| product_height_cm | Height in cm | integer_text | TINYINT UNSIGNED |  | 2 | 102 | 2 → 105 | source_observed |
| product_width_cm | Width in cm | integer_text | TINYINT UNSIGNED |  | 2 | 95 | 6 → 118 | source_observed |

### sellers — `olist_sellers_dataset.csv` (3,095 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| seller_id | Seller key (PK) | hex32_id | CHAR(32) | PK | 0 | 3,095 | len 32–32 | source_observed |
| seller_zip_code_prefix | Seller postcode prefix (text, leading zeros) | integer_text | CHAR(5) |  | 0 | 2,246 | len 5–5 (text) | source_observed |
| seller_city | Seller city | text | VARCHAR(40) |  | 0 | 611 | len 2–40 | source_observed |
| seller_state | Seller state (UF) | text | CHAR(2) |  | 0 | 23 | len 2–2 | source_observed |

### category_translation — `product_category_name_translation.csv` (71 rows)

| Column | Description | Observed type | Proposed MySQL type (Phase 3) | Key role | Missing | Distinct | Range / length | Provenance |
|---|---|---|---|---|---:|---:|---|---|
| product_category_name | Portuguese category (PK) | text | VARCHAR(48) | PK | 0 | 71 | len 3–46 | source_observed |
| product_category_name_english | English category name | text | VARCHAR(40) |  | 0 | 71 | len 3–39 | source_observed |
