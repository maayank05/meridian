# Olist Source Headers (header-line evidence only)

Captured 2026-10-31 in Phase 1 by reading **only the first line** of each file in `data/raw/olist/`. No data rows were read. Types, keys, nulls, row counts, value domains and date ranges are **not known** until Phase 2 profiling.

Licence: CC BY-NC-SA 4.0 (verified by project owner, D-013). Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Files and columns

The alias is the short table name used in the KPI dictionary and business rules (`alias.column`).

| Alias | File | Columns |
|---|---|---|
| customers | olist_customers_dataset.csv | customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state |
| geolocation | olist_geolocation_dataset.csv | geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state |
| order_items | olist_order_items_dataset.csv | order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value |
| order_payments | olist_order_payments_dataset.csv | order_id, payment_sequential, payment_type, payment_installments, payment_value |
| order_reviews | olist_order_reviews_dataset.csv | review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp |
| orders | olist_orders_dataset.csv | order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date |
| products | olist_products_dataset.csv | product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm |
| sellers | olist_sellers_dataset.csv | seller_id, seller_zip_code_prefix, seller_city, seller_state |
| category_translation | product_category_name_translation.csv | product_category_name, product_category_name_english |

Total: 9 files, 57 columns, no duplicate column names within any file.

## Header-level observations

| ID | Observation | Consequence |
|---|---|---|
| H-01 | `product_name_lenght`, `product_description_lenght` are misspelled in the source | Keep source names in `raw_*`; rename to `*_length` in `stg_*`, documented in the data dictionary |
| H-02 | `product_category_name_translation.csv` begins with a UTF-8 BOM | Ingestion must decode with BOM handling (`utf-8-sig`) |
| H-03 | Line endings: CRLF in `order_reviews` and `category_translation`, LF in the other 7 | Parser must accept both; review comments may contain embedded newlines (verify in Phase 2) |
| H-04 | No currency column in any file | BRL is a documented assumption (A-01), not an observed field |
| H-05 | No cost, COGS, marketing spend, campaign, session, inventory, refund or return columns | Confirms unsupported KPIs U01–U09 at header level |
| H-06 | Both `customer_id` and `customer_unique_id` exist | Supports RULE-02. Semantics (order-scoped vs person-level) to verify in Phase 2 |
| H-07 | No timezone information in any timestamp column name | Timezone is an assumption (A-02) |
