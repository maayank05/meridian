-- 0002: staging layer (typed, renamed, keys enforced). Free review text is NOT carried beyond raw.
-- Timestamps (D-017): *_local = source value as recorded (America/Sao_Paulo civil time, inferred);
-- *_utc = derived UTC, NULL when the local time is ambiguous or non-existent; *_tz = 'ok' | 'ambiguous' | 'nonexistent'.

CREATE TABLE stg_customers (
    customer_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    customer_unique_id        CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    customer_zip_code_prefix  CHAR(5) NOT NULL,
    customer_city             VARCHAR(64) NOT NULL,
    customer_state            CHAR(2) NOT NULL,
    KEY ix_stg_customers_unique (customer_unique_id)
) ENGINE=InnoDB;

-- One row per zip prefix: mean of coordinates inside Brazil's bounding box (DQ-03, DQ-04).
CREATE TABLE stg_geolocation_zip (
    zip_code_prefix   CHAR(5) NOT NULL PRIMARY KEY,
    lat               DOUBLE NULL,
    lng               DOUBLE NULL,
    n_points          INT UNSIGNED NOT NULL,
    n_points_outside_bbox INT UNSIGNED NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_orders (
    order_id                       CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    customer_id                    CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_status                   VARCHAR(16) NOT NULL,
    purchase_local                 DATETIME NOT NULL,
    purchase_utc                   DATETIME NULL,
    purchase_tz                    VARCHAR(11) NULL,
    approved_local                 DATETIME NULL,
    approved_utc                   DATETIME NULL,
    approved_tz                    VARCHAR(11) NULL,
    delivered_carrier_local        DATETIME NULL,
    delivered_carrier_utc          DATETIME NULL,
    delivered_carrier_tz           VARCHAR(11) NULL,
    delivered_customer_local       DATETIME NULL,
    delivered_customer_utc         DATETIME NULL,
    delivered_customer_tz          VARCHAR(11) NULL,
    estimated_delivery_date        DATE NOT NULL,
    UNIQUE KEY uq_stg_orders_customer (customer_id)
) ENGINE=InnoDB;

CREATE TABLE stg_order_items (
    order_id              CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_item_id         SMALLINT UNSIGNED NOT NULL,
    product_id            CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    seller_id             CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    shipping_limit_local  DATETIME NOT NULL,
    shipping_limit_utc    DATETIME NULL,
    shipping_limit_tz     VARCHAR(11) NULL,
    price                 DECIMAL(10, 2) NOT NULL,
    freight_value         DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
) ENGINE=InnoDB;

CREATE TABLE stg_order_payments (
    order_id              CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    payment_sequential    SMALLINT UNSIGNED NOT NULL,
    payment_type          VARCHAR(16) NOT NULL,
    payment_installments  SMALLINT UNSIGNED NOT NULL,
    payment_value         DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
) ENGINE=InnoDB;

CREATE TABLE stg_order_reviews (
    review_id                CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    order_id                 CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    review_score             TINYINT UNSIGNED NOT NULL,
    has_comment_title        BOOLEAN NOT NULL,
    has_comment_message      BOOLEAN NOT NULL,
    review_creation_date     DATE NOT NULL,
    review_creation_had_time BOOLEAN NOT NULL,
    answer_local             DATETIME NOT NULL,
    answer_utc               DATETIME NULL,
    answer_tz                VARCHAR(11) NULL,
    PRIMARY KEY (review_id, order_id),
    CONSTRAINT chk_stg_review_score CHECK (review_score BETWEEN 1 AND 5)
) ENGINE=InnoDB;

CREATE TABLE stg_products (
    product_id                  CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    product_category_name       VARCHAR(64) NULL,
    product_name_length         SMALLINT UNSIGNED NULL,
    product_description_length  SMALLINT UNSIGNED NULL,
    product_photos_qty          SMALLINT UNSIGNED NULL,
    product_weight_g            INT UNSIGNED NULL,
    product_length_cm           SMALLINT UNSIGNED NULL,
    product_height_cm           SMALLINT UNSIGNED NULL,
    product_width_cm            SMALLINT UNSIGNED NULL
) ENGINE=InnoDB;

CREATE TABLE stg_sellers (
    seller_id               CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
    seller_zip_code_prefix  CHAR(5) NOT NULL,
    seller_city             VARCHAR(64) NOT NULL,
    seller_state            CHAR(2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE stg_category_translation (
    product_category_name          VARCHAR(64) NOT NULL PRIMARY KEY,
    product_category_name_english  VARCHAR(64) NOT NULL
) ENGINE=InnoDB;

-- Distinct local timestamps -> UTC, computed in Python with zoneinfo (D-017).
CREATE TABLE stg_tz_map (
    local_ts   DATETIME NOT NULL PRIMARY KEY,
    utc_ts     DATETIME NULL,
    tz_status  VARCHAR(11) NOT NULL,
    CONSTRAINT chk_tz_status CHECK (tz_status IN ('ok', 'ambiguous', 'nonexistent'))
) ENGINE=InnoDB;
