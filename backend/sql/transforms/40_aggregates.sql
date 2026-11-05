-- Refresh pre-computed aggregates from the canonical views (0004) and marts. Runs last, inside the pipeline
-- transaction, so readers always see aggregates consistent with the facts.
DELETE FROM agg_kpi_monthly;
DELETE FROM agg_kpi_category_monthly;
DELETE FROM agg_kpi_delivery_monthly;
DELETE FROM agg_kpi_reviews_monthly;
DELETE FROM agg_kpi_payments_monthly;
DELETE FROM agg_payment_reconciliation;
DELETE FROM agg_cohort_retention;
DELETE FROM agg_customer_month;
DELETE FROM agg_seller_month;

INSERT INTO agg_kpi_monthly SELECT * FROM vw_kpi_monthly;
INSERT INTO agg_kpi_category_monthly SELECT * FROM vw_kpi_category_monthly;
INSERT INTO agg_kpi_delivery_monthly SELECT * FROM vw_kpi_delivery_monthly;
INSERT INTO agg_kpi_reviews_monthly SELECT * FROM vw_kpi_reviews_monthly;
INSERT INTO agg_kpi_payments_monthly SELECT * FROM vw_kpi_payments_monthly;
INSERT INTO agg_payment_reconciliation SELECT * FROM vw_payment_reconciliation;
INSERT INTO agg_cohort_retention SELECT * FROM vw_cohort_retention;

INSERT INTO agg_customer_month (customer_unique_id, month_start, delivered_orders, delivered_merchandise_value)
SELECT c.customer_unique_id, d.month_start, COUNT(*), SUM(o.items_price_total)
FROM fact_orders o
JOIN dim_customer c ON c.customer_id = o.customer_id
JOIN dim_date d ON d.date_key = o.purchase_date
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, d.month_start;

INSERT INTO agg_seller_month (seller_id, month_start, delivered_merchandise_value)
SELECT i.seller_id, d.month_start, SUM(i.price)
FROM fact_order_items i
JOIN fact_orders o ON o.order_id = i.order_id AND o.order_status = 'delivered'
JOIN dim_date d ON d.date_key = i.purchase_date
GROUP BY i.seller_id, d.month_start;
