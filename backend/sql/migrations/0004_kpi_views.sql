-- 0004: canonical KPI views (business/08_kpi_dictionary.md). One definition per KPI; Python, API, report and
-- Power BI read these views. Values are unrounded; rounding happens only at presentation (RULE-08).
-- Months come from dim_date, so months with no orders (e.g. 2016-11) appear explicitly with zero counts.
-- coverage_flag implements RULE-25 (D-018 default window 2017-01..2018-08; edges flagged, never hidden).

-- Grain: one row per calendar month 2016-09..2018-10.
-- K01 Delivered Merchandise Value (Revenue Proxy) = sum of item price of DELIVERED orders by purchase month (D-016).
-- K02 freight, K03 delivered orders, K04 AOV, K05 items/order, K06 orders placed, K12 cancellation rate
-- (canceled only, RULE-26), K26 unavailable rate, K21 active customers (customer_unique_id), K23 active sellers.
CREATE VIEW vw_kpi_monthly AS
SELECT m.month_start,
       m.coverage_flag,
       COALESCE(a.orders_placed, 0) AS orders_placed,
       COALESCE(a.delivered_orders, 0) AS delivered_orders,
       COALESCE(a.delivered_merchandise_value, 0) AS delivered_merchandise_value,
       COALESCE(a.freight_billed, 0) AS freight_billed,
       COALESCE(a.delivered_items, 0) AS delivered_items,
       COALESCE(a.canceled_orders, 0) AS canceled_orders,
       COALESCE(a.unavailable_orders, 0) AS unavailable_orders,
       COALESCE(a.active_customers, 0) AS active_customers,
       COALESCE(s.active_sellers, 0) AS active_sellers,
       a.delivered_merchandise_value / NULLIF(a.delivered_orders, 0) AS average_order_value,
       a.delivered_items / NULLIF(a.delivered_orders, 0) AS items_per_delivered_order,
       a.canceled_orders / NULLIF(a.orders_placed, 0) AS cancellation_rate,
       a.unavailable_orders / NULLIF(a.orders_placed, 0) AS unavailable_rate
FROM (
    SELECT DISTINCT month_start, coverage_flag FROM dim_date WHERE coverage_flag <> 'outside_source'
) m
LEFT JOIN (
    SELECT d.month_start,
           COUNT(*) AS orders_placed,
           SUM(o.order_status = 'delivered') AS delivered_orders,
           SUM(CASE WHEN o.order_status = 'delivered' THEN o.items_price_total ELSE 0 END) AS delivered_merchandise_value,
           SUM(CASE WHEN o.order_status = 'delivered' THEN o.items_freight_total ELSE 0 END) AS freight_billed,
           SUM(CASE WHEN o.order_status = 'delivered' THEN o.item_count ELSE 0 END) AS delivered_items,
           SUM(o.order_status = 'canceled') AS canceled_orders,
           SUM(o.order_status = 'unavailable') AS unavailable_orders,
           COUNT(DISTINCT CASE WHEN o.order_status = 'delivered' THEN c.customer_unique_id END) AS active_customers
    FROM fact_orders o
    JOIN dim_customer c ON c.customer_id = o.customer_id
    JOIN dim_date d ON d.date_key = o.purchase_date
    GROUP BY d.month_start
) a ON a.month_start = m.month_start
LEFT JOIN (
    SELECT d.month_start, COUNT(DISTINCT i.seller_id) AS active_sellers
    FROM fact_order_items i
    JOIN fact_orders o ON o.order_id = i.order_id AND o.order_status = 'delivered'
    JOIN dim_date d ON d.date_key = i.purchase_date
    GROUP BY d.month_start
) s ON s.month_start = m.month_start;

-- Grain: month x category (English name; 'unknown' for missing, Portuguese if untranslated - RULE-13).
-- K11 basis. delivered_orders counts an order in every category it contains, so it must NOT be summed across
-- categories (use vw_kpi_monthly for order counts).
CREATE VIEW vw_kpi_category_monthly AS
SELECT d.month_start,
       d.coverage_flag,
       p.category_name_en,
       p.is_category_missing,
       p.is_untranslated,
       SUM(i.price) AS delivered_merchandise_value,
       COUNT(*) AS delivered_items,
       COUNT(DISTINCT i.order_id) AS delivered_orders
FROM fact_order_items i
JOIN fact_orders o ON o.order_id = i.order_id AND o.order_status = 'delivered'
JOIN dim_product p ON p.product_id = i.product_id
JOIN dim_date d ON d.date_key = i.purchase_date
GROUP BY d.month_start, d.coverage_flag, p.category_name_en, p.is_category_missing, p.is_untranslated;

-- Grain: purchase month, delivered orders only (RULE-11). K14 lead time uses UTC (D-017 T3/T8): orders whose
-- purchase or delivery UTC is NULL (ambiguous DST time) are excluded and counted. K15/K16 compare local
-- calendar dates (RULE-12).
CREATE VIEW vw_kpi_delivery_monthly AS
SELECT d.month_start,
       d.coverage_flag,
       COUNT(*) AS delivered_orders,
       SUM(o.delivered_customer_local IS NULL) AS excluded_missing_delivery_date,
       SUM(o.delivered_customer_local IS NOT NULL
           AND (o.purchase_utc IS NULL OR o.delivered_customer_utc IS NULL)) AS excluded_ambiguous_time,
       SUM(o.purchase_utc IS NOT NULL AND o.delivered_customer_utc IS NOT NULL) AS lead_time_orders,
       AVG(CASE WHEN o.purchase_utc IS NOT NULL AND o.delivered_customer_utc IS NOT NULL
                THEN TIMESTAMPDIFF(SECOND, o.purchase_utc, o.delivered_customer_utc) END) AS avg_lead_time_seconds,
       SUM(o.delivered_customer_local IS NOT NULL) AS on_time_eligible_orders,
       SUM(DATE(o.delivered_customer_local) <= o.estimated_delivery_date) AS on_time_orders,
       SUM(DATE(o.delivered_customer_local) > o.estimated_delivery_date) AS late_orders,
       SUM(DATE(o.delivered_customer_local) <= o.estimated_delivery_date)
           / NULLIF(SUM(o.delivered_customer_local IS NOT NULL), 0) AS on_time_rate,
       AVG(CASE WHEN DATE(o.delivered_customer_local) > o.estimated_delivery_date
                THEN DATEDIFF(DATE(o.delivered_customer_local), o.estimated_delivery_date) END) AS avg_days_late
FROM fact_orders o
JOIN dim_date d ON d.date_key = o.purchase_date
WHERE o.order_status = 'delivered'
GROUP BY d.month_start, d.coverage_flag;

-- Grain: purchase month. K13 = mean over orders of each order's mean review score (D-019b, RULE-15).
-- orders_with_shared_review counts orders whose review_id is shared with another order (non-independent).
CREATE VIEW vw_kpi_reviews_monthly AS
SELECT d.month_start,
       d.coverage_flag,
       COUNT(*) AS orders_with_review,
       SUM(r.order_score) AS sum_order_scores,
       AVG(r.order_score) AS avg_review_score,
       SUM(r.has_shared_review) AS orders_with_shared_review
FROM (
    SELECT order_id, AVG(review_score) AS order_score, MAX(is_shared_review) AS has_shared_review
    FROM fact_reviews
    GROUP BY order_id
) r
JOIN fact_orders o ON o.order_id = r.order_id
JOIN dim_date d ON d.date_key = o.purchase_date
GROUP BY d.month_start, d.coverage_flag;

-- Grain: purchase month x payment type (all order statuses). K19 mix; K20 instalments exclude invalid
-- credit-card records with 0 instalments and report their count (RULE-28).
CREATE VIEW vw_kpi_payments_monthly AS
SELECT d.month_start,
       d.coverage_flag,
       p.payment_type,
       COUNT(*) AS payment_records,
       SUM(p.payment_value) AS payment_value,
       SUM(NOT p.is_invalid_installments) AS valid_installment_records,
       SUM(CASE WHEN NOT p.is_invalid_installments THEN p.payment_installments ELSE 0 END) AS sum_valid_installments,
       SUM(p.is_invalid_installments) AS invalid_installment_records
FROM fact_payments p
JOIN fact_orders o ON o.order_id = p.order_id
JOIN dim_date d ON d.date_key = o.purchase_date
GROUP BY d.month_start, d.coverage_flag, p.payment_type;

-- Grain: order status. K18 payment vs (item price + freight), compared at order level (RULE-06).
CREATE VIEW vw_payment_reconciliation AS
SELECT order_status,
       COUNT(*) AS orders,
       SUM(item_count > 0 AND payment_count > 0) AS orders_with_both,
       SUM(item_count > 0 AND payment_count > 0
           AND ABS(payments_total - (items_price_total + items_freight_total)) <= 0.01) AS matched_orders,
       SUM(item_count > 0 AND payment_count > 0
           AND payments_total - (items_price_total + items_freight_total) > 0.01) AS payments_higher_orders,
       SUM(item_count > 0 AND payment_count > 0
           AND payments_total - (items_price_total + items_freight_total) < -0.01) AS payments_lower_orders,
       SUM(item_count > 0 AND payment_count = 0) AS items_only_orders,
       SUM(item_count = 0 AND payment_count > 0) AS payments_only_orders,
       SUM(CASE WHEN item_count > 0 AND payment_count > 0
                THEN payments_total - (items_price_total + items_freight_total) ELSE 0 END) AS net_difference
FROM fact_orders
GROUP BY order_status;

-- Grain: cohort month x months since first purchase. K08. Cohort = month of a person's first DELIVERED order
-- over the FULL history (RULE-25: history is never truncated by the display window). Cells beyond the data
-- end have no row (unobservable, not zero).
CREATE VIEW vw_cohort_retention AS
WITH activity AS (
    SELECT DISTINCT c.customer_unique_id AS uid, d.month_start
    FROM fact_orders o
    JOIN dim_customer c ON c.customer_id = o.customer_id
    JOIN dim_date d ON d.date_key = o.purchase_date
    WHERE o.order_status = 'delivered'
),
first_month AS (
    SELECT uid, MIN(month_start) AS cohort_month FROM activity GROUP BY uid
),
sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size FROM first_month GROUP BY cohort_month
)
SELECT f.cohort_month,
       TIMESTAMPDIFF(MONTH, f.cohort_month, a.month_start) AS months_since_first,
       COUNT(*) AS active_customers,
       s.cohort_size
FROM first_month f
JOIN activity a ON a.uid = f.uid
JOIN sizes s ON s.cohort_month = f.cohort_month
GROUP BY f.cohort_month, months_since_first, s.cohort_size;
