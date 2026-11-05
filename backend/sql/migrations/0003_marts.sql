-- 0003: analytical marts (dimensions and facts). Grain is stated per table.
-- All facts are source_observed / derived; nothing synthetic is stored here (RULE-17).

-- Grain: one row per calendar date 2016-01-01..2020-12-31. coverage_flag implements RULE-25 / D-018.
CREATE TABLE dim_date (
    date_key       DATE NOT NULL PRIMARY KEY,
    year_num       SMALLINT NOT NULL,
    month_num      TINYINT NOT NULL,
    month_start    DATE NOT NULL,
    coverage_flag  VARCHAR(20) NOT NULL,
    CONSTRAINT chk_coverage_flag CHECK (coverage_flag IN ('default_window', 'low_coverage', 'incomplete_cutoff', 'outside_source'))
) ENGINE=InnoDB;

-- Grain: one row per customer_id (= one per order). Person = customer_unique_id (RULE-02).
CREATE TABLE dim_customer (
    customer_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    customer_unique_id        CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    customer_zip_code_prefix  CHAR(5) NOT NULL,
    customer_city             VARCHAR(64) NOT NULL,
    customer_state            CHAR(2) NOT NULL,
    zip_in_geolocation        BOOLEAN NOT NULL,
    KEY ix_dim_customer_unique (customer_unique_id),
    KEY ix_dim_customer_state (customer_state)
) ENGINE=InnoDB;

-- Grain: one row per product. Missing category -> 'unknown'; untranslated keeps Portuguese name (RULE-13).
CREATE TABLE dim_product (
    product_id             CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    category_name_pt       VARCHAR(64) NOT NULL,
    category_name_en       VARCHAR(64) NOT NULL,
    is_category_missing    BOOLEAN NOT NULL,
    is_untranslated        BOOLEAN NOT NULL,
    product_weight_g       INT UNSIGNED NULL,
    product_photos_qty     SMALLINT UNSIGNED NULL,
    KEY ix_dim_product_category (category_name_en)
) ENGINE=InnoDB;

-- Grain: one row per seller.
CREATE TABLE dim_seller (
    seller_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    seller_zip_code_prefix  CHAR(5) NOT NULL,
    seller_city             VARCHAR(64) NOT NULL,
    seller_state            CHAR(2) NOT NULL,
    zip_in_geolocation      BOOLEAN NOT NULL,
    KEY ix_dim_seller_state (seller_state)
) ENGINE=InnoDB;

-- Grain: one row per order. Item and payment totals are aggregated per order BEFORE joining (RULE-06),
-- so this table can never fan out.
CREATE TABLE fact_orders (
    order_id                  CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    customer_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_status              VARCHAR(16) NOT NULL,
    purchase_date             DATE NOT NULL,
    purchase_local            DATETIME NOT NULL,
    purchase_utc              DATETIME NULL,
    approved_utc              DATETIME NULL,
    delivered_carrier_local   DATETIME NULL,
    delivered_carrier_utc     DATETIME NULL,
    delivered_customer_local  DATETIME NULL,
    delivered_customer_utc    DATETIME NULL,
    estimated_delivery_date   DATE NOT NULL,
    item_count                SMALLINT UNSIGNED NOT NULL,
    items_price_total         DECIMAL(12, 2) NOT NULL,
    items_freight_total       DECIMAL(12, 2) NOT NULL,
    payment_count             SMALLINT UNSIGNED NOT NULL,
    payments_total            DECIMAL(12, 2) NOT NULL,
    KEY ix_fact_orders_status_date (order_status, purchase_date),
    CONSTRAINT fk_fact_orders_customer FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    CONSTRAINT fk_fact_orders_date FOREIGN KEY (purchase_date) REFERENCES dim_date (date_key)
) ENGINE=InnoDB;

-- Grain: one row per order item (one unit, A-09).
CREATE TABLE fact_order_items (
    order_id              CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_item_id         SMALLINT UNSIGNED NOT NULL,
    product_id            CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    seller_id             CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    purchase_date         DATE NOT NULL,
    shipping_limit_local  DATETIME NOT NULL,
    shipping_limit_utc    DATETIME NULL,
    price                 DECIMAL(10, 2) NOT NULL,
    freight_value         DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    KEY ix_items_product (product_id),
    KEY ix_items_seller (seller_id),
    KEY ix_items_date (purchase_date),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES fact_orders (order_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    CONSTRAINT fk_items_seller FOREIGN KEY (seller_id) REFERENCES dim_seller (seller_id)
) ENGINE=InnoDB;

-- Grain: one row per payment record.
CREATE TABLE fact_payments (
    order_id                   CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    payment_sequential         SMALLINT UNSIGNED NOT NULL,
    payment_type               VARCHAR(16) NOT NULL,
    payment_installments       SMALLINT UNSIGNED NOT NULL,
    payment_value              DECIMAL(10, 2) NOT NULL,
    is_invalid_installments    BOOLEAN NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES fact_orders (order_id)
) ENGINE=InnoDB;

-- Grain: one row per (review_id, order_id). is_shared_review flags review_ids linked to >1 order (RULE-15).
CREATE TABLE fact_reviews (
    review_id              CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    review_score           TINYINT UNSIGNED NOT NULL,
    has_comment_message    BOOLEAN NOT NULL,
    review_creation_date   DATE NOT NULL,
    answer_utc             DATETIME NULL,
    is_shared_review       BOOLEAN NOT NULL,
    PRIMARY KEY (review_id, order_id),
    KEY ix_reviews_order (order_id),
    CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) REFERENCES fact_orders (order_id)
) ENGINE=InnoDB;
