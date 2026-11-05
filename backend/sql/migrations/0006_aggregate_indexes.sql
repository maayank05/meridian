-- 0006: covering indexes so period measures can group by person / seller without a temporary table (NFR-003).
CREATE INDEX ix_agg_customer_month_person ON agg_customer_month (customer_unique_id, month_start, delivered_orders, delivered_merchandise_value);
CREATE INDEX ix_agg_seller_month_seller ON agg_seller_month (seller_id, month_start, delivered_merchandise_value);
