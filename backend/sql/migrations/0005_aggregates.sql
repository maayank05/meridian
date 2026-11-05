-- 0005: pre-computed aggregates for fast reads (NFR-003). The KPI VIEWS in 0004 remain the single canonical
-- definition; each agg_kpi_* table is filled by `INSERT ... SELECT * FROM` its view at the end of every
-- pipeline run (transforms/40_aggregates.sql), inside the same transaction. Tests assert agg = view.
-- Column types are copied from the views (CREATE ... SELECT ... WHERE 1 = 0 creates an empty table).

CREATE TABLE agg_kpi_monthly ENGINE=InnoDB AS SELECT * FROM vw_kpi_monthly WHERE 1 = 0;
ALTER TABLE agg_kpi_monthly ADD PRIMARY KEY (month_start);

CREATE TABLE agg_kpi_category_monthly ENGINE=InnoDB AS SELECT * FROM vw_kpi_category_monthly WHERE 1 = 0;
ALTER TABLE agg_kpi_category_monthly ADD PRIMARY KEY (month_start, category_name_en);

CREATE TABLE agg_kpi_delivery_monthly ENGINE=InnoDB AS SELECT * FROM vw_kpi_delivery_monthly WHERE 1 = 0;
ALTER TABLE agg_kpi_delivery_monthly ADD PRIMARY KEY (month_start);

CREATE TABLE agg_kpi_reviews_monthly ENGINE=InnoDB AS SELECT * FROM vw_kpi_reviews_monthly WHERE 1 = 0;
ALTER TABLE agg_kpi_reviews_monthly ADD PRIMARY KEY (month_start);

CREATE TABLE agg_kpi_payments_monthly ENGINE=InnoDB AS SELECT * FROM vw_kpi_payments_monthly WHERE 1 = 0;
ALTER TABLE agg_kpi_payments_monthly ADD PRIMARY KEY (month_start, payment_type);

CREATE TABLE agg_payment_reconciliation ENGINE=InnoDB AS SELECT * FROM vw_payment_reconciliation WHERE 1 = 0;
ALTER TABLE agg_payment_reconciliation ADD PRIMARY KEY (order_status);

CREATE TABLE agg_cohort_retention ENGINE=InnoDB AS SELECT * FROM vw_cohort_retention WHERE 1 = 0;
ALTER TABLE agg_cohort_retention ADD PRIMARY KEY (cohort_month, months_since_first);

-- Grain: person (customer_unique_id) x purchase month, delivered orders only. Basis for period measures
-- (K21 active customers, K07 repeat rate, K10 concentration) over month-aligned periods.
CREATE TABLE agg_customer_month (
    customer_unique_id          CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    month_start                 DATE NOT NULL,
    delivered_orders            INT UNSIGNED NOT NULL,
    delivered_merchandise_value DECIMAL(14, 2) NOT NULL,
    PRIMARY KEY (month_start, customer_unique_id)
) ENGINE=InnoDB;

-- Grain: seller x purchase month, delivered orders only (K22 seller concentration).
CREATE TABLE agg_seller_month (
    seller_id                   CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    month_start                 DATE NOT NULL,
    delivered_merchandise_value DECIMAL(14, 2) NOT NULL,
    PRIMARY KEY (month_start, seller_id)
) ENGINE=InnoDB;
