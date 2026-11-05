-- raw_* -> stg_*: typing, renaming (H-01 `*_lenght` -> `*_length`), NULL for empty source fields.
-- STRICT sql_mode makes any unparseable value fail the run instead of being silently coerced.

INSERT INTO stg_customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
SELECT customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state
FROM raw_customers;

INSERT INTO stg_geolocation_zip (zip_code_prefix, lat, lng, n_points, n_points_outside_bbox)
SELECT zip,
       AVG(CASE WHEN in_bbox THEN lat END),
       AVG(CASE WHEN in_bbox THEN lng END),
       COUNT(*),
       SUM(CASE WHEN in_bbox THEN 0 ELSE 1 END)
FROM (
    SELECT geolocation_zip_code_prefix AS zip,
           CAST(geolocation_lat AS DOUBLE) AS lat,
           CAST(geolocation_lng AS DOUBLE) AS lng,
           (CAST(geolocation_lat AS DOUBLE) BETWEEN -33.75 AND 5.27
            AND CAST(geolocation_lng AS DOUBLE) BETWEEN -73.99 AND -34.79) AS in_bbox
    FROM raw_geolocation
) g
GROUP BY zip;

INSERT INTO stg_orders (order_id, customer_id, order_status, purchase_local, approved_local,
                        delivered_carrier_local, delivered_customer_local, estimated_delivery_date)
SELECT order_id,
       customer_id,
       order_status,
       STR_TO_DATE(order_purchase_timestamp, '%Y-%m-%d %H:%i:%s'),
       STR_TO_DATE(NULLIF(order_approved_at, ''), '%Y-%m-%d %H:%i:%s'),
       STR_TO_DATE(NULLIF(order_delivered_carrier_date, ''), '%Y-%m-%d %H:%i:%s'),
       STR_TO_DATE(NULLIF(order_delivered_customer_date, ''), '%Y-%m-%d %H:%i:%s'),
       DATE(STR_TO_DATE(order_estimated_delivery_date, '%Y-%m-%d %H:%i:%s'))
FROM raw_orders;

INSERT INTO stg_order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_local, price, freight_value)
SELECT order_id,
       CAST(order_item_id AS UNSIGNED),
       product_id,
       seller_id,
       STR_TO_DATE(shipping_limit_date, '%Y-%m-%d %H:%i:%s'),
       CAST(price AS DECIMAL(10, 2)),
       CAST(freight_value AS DECIMAL(10, 2))
FROM raw_order_items;

INSERT INTO stg_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
SELECT order_id,
       CAST(payment_sequential AS UNSIGNED),
       payment_type,
       CAST(payment_installments AS UNSIGNED),
       CAST(payment_value AS DECIMAL(10, 2))
FROM raw_order_payments;

INSERT INTO stg_order_reviews (review_id, order_id, review_score, has_comment_title, has_comment_message,
                               review_creation_date, review_creation_had_time, answer_local)
SELECT review_id,
       order_id,
       CAST(review_score AS UNSIGNED),
       TRIM(review_comment_title) <> '',
       TRIM(review_comment_message) <> '',
       DATE(STR_TO_DATE(review_creation_date, '%Y-%m-%d %H:%i:%s')),
       TIME(STR_TO_DATE(review_creation_date, '%Y-%m-%d %H:%i:%s')) <> '00:00:00',
       STR_TO_DATE(review_answer_timestamp, '%Y-%m-%d %H:%i:%s')
FROM raw_order_reviews;

INSERT INTO stg_products (product_id, product_category_name, product_name_length, product_description_length,
                          product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
SELECT product_id,
       NULLIF(product_category_name, ''),
       CAST(NULLIF(product_name_lenght, '') AS UNSIGNED),
       CAST(NULLIF(product_description_lenght, '') AS UNSIGNED),
       CAST(NULLIF(product_photos_qty, '') AS UNSIGNED),
       CAST(NULLIF(product_weight_g, '') AS UNSIGNED),
       CAST(NULLIF(product_length_cm, '') AS UNSIGNED),
       CAST(NULLIF(product_height_cm, '') AS UNSIGNED),
       CAST(NULLIF(product_width_cm, '') AS UNSIGNED)
FROM raw_products;

INSERT INTO stg_sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
SELECT seller_id, seller_zip_code_prefix, seller_city, seller_state
FROM raw_sellers;

INSERT INTO stg_category_translation (product_category_name, product_category_name_english)
SELECT product_category_name, product_category_name_english
FROM raw_category_translation;
