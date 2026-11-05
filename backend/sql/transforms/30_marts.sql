-- stg_* -> dim_* / fact_*. Runs only after blocking data-quality checks pass.

SET SESSION cte_max_recursion_depth = 5000;

-- RULE-25 / D-018: default analysis window 2017-01-01..2018-08-31; edges flagged, never hidden.
INSERT INTO dim_date (date_key, year_num, month_num, month_start, coverage_flag)
WITH RECURSIVE d AS (
    SELECT DATE('2016-01-01') AS dt
    UNION ALL
    SELECT dt + INTERVAL 1 DAY FROM d WHERE dt < DATE('2020-12-31')
)
SELECT dt, YEAR(dt), MONTH(dt), DATE_FORMAT(dt, '%Y-%m-01'),
       CASE
           WHEN dt BETWEEN '2017-01-01' AND '2018-08-31' THEN 'default_window'
           WHEN dt BETWEEN '2016-09-01' AND '2016-12-31' THEN 'low_coverage'
           WHEN dt BETWEEN '2018-09-01' AND '2018-10-31' THEN 'incomplete_cutoff'
           ELSE 'outside_source'
       END
FROM d;

INSERT INTO dim_customer (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state,
                          zip_in_geolocation)
SELECT c.customer_id, c.customer_unique_id, c.customer_zip_code_prefix, c.customer_city, c.customer_state,
       g.zip_code_prefix IS NOT NULL
FROM stg_customers c
LEFT JOIN stg_geolocation_zip g ON g.zip_code_prefix = c.customer_zip_code_prefix;

INSERT INTO dim_product (product_id, category_name_pt, category_name_en, is_category_missing, is_untranslated,
                         product_weight_g, product_photos_qty)
SELECT p.product_id,
       COALESCE(p.product_category_name, 'unknown'),
       COALESCE(t.product_category_name_english, p.product_category_name, 'unknown'),
       p.product_category_name IS NULL,
       p.product_category_name IS NOT NULL AND t.product_category_name IS NULL,
       p.product_weight_g,
       p.product_photos_qty
FROM stg_products p
LEFT JOIN stg_category_translation t ON t.product_category_name = p.product_category_name;

INSERT INTO dim_seller (seller_id, seller_zip_code_prefix, seller_city, seller_state, zip_in_geolocation)
SELECT s.seller_id, s.seller_zip_code_prefix, s.seller_city, s.seller_state, g.zip_code_prefix IS NOT NULL
FROM stg_sellers s
LEFT JOIN stg_geolocation_zip g ON g.zip_code_prefix = s.seller_zip_code_prefix;

-- Items and payments are aggregated to order grain in subqueries first (no fan-out, RULE-06).
INSERT INTO fact_orders (order_id, customer_id, order_status, purchase_date, purchase_local, purchase_utc, approved_utc,
                         delivered_carrier_local, delivered_carrier_utc, delivered_customer_local,
                         delivered_customer_utc, estimated_delivery_date, item_count, items_price_total,
                         items_freight_total, payment_count, payments_total)
SELECT o.order_id, o.customer_id, o.order_status, DATE(o.purchase_local), o.purchase_local, o.purchase_utc,
       o.approved_utc, o.delivered_carrier_local, o.delivered_carrier_utc, o.delivered_customer_local,
       o.delivered_customer_utc, o.estimated_delivery_date,
       COALESCE(i.item_count, 0), COALESCE(i.price_total, 0), COALESCE(i.freight_total, 0),
       COALESCE(p.payment_count, 0), COALESCE(p.payments_total, 0)
FROM stg_orders o
LEFT JOIN (
    SELECT order_id, COUNT(*) AS item_count, SUM(price) AS price_total, SUM(freight_value) AS freight_total
    FROM stg_order_items GROUP BY order_id
) i ON i.order_id = o.order_id
LEFT JOIN (
    SELECT order_id, COUNT(*) AS payment_count, SUM(payment_value) AS payments_total
    FROM stg_order_payments GROUP BY order_id
) p ON p.order_id = o.order_id;

INSERT INTO fact_order_items (order_id, order_item_id, product_id, seller_id, purchase_date, shipping_limit_local,
                              shipping_limit_utc, price, freight_value)
SELECT i.order_id, i.order_item_id, i.product_id, i.seller_id, DATE(o.purchase_local), i.shipping_limit_local,
       i.shipping_limit_utc, i.price, i.freight_value
FROM stg_order_items i
JOIN stg_orders o ON o.order_id = i.order_id;

-- RULE-28: credit-card records with 0 instalments are flagged invalid (K20 excludes and counts them).
INSERT INTO fact_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value,
                           is_invalid_installments)
SELECT order_id, payment_sequential, payment_type, payment_installments, payment_value,
       payment_type = 'credit_card' AND payment_installments = 0
FROM stg_order_payments;

-- RULE-15: review_ids attached to more than one order are flagged (non-independent observations).
INSERT INTO fact_reviews (review_id, order_id, review_score, has_comment_message, review_creation_date, answer_utc,
                          is_shared_review)
SELECT r.review_id, r.order_id, r.review_score, r.has_comment_message, r.review_creation_date, r.answer_utc,
       s.review_id IS NOT NULL
FROM stg_order_reviews r
LEFT JOIN (
    SELECT review_id FROM stg_order_reviews GROUP BY review_id HAVING COUNT(*) > 1
) s ON s.review_id = r.review_id;
