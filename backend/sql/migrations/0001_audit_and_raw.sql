-- 0001: audit tables and raw layer.
-- Raw tables store the source CSV text unchanged (empty string = empty source field).
-- source_row_number = 1-based data-row position in the file; with it every raw row is traceable.

CREATE TABLE audit_ingestion_run (
    run_id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    started_at_utc    DATETIME(3) NOT NULL,
    finished_at_utc   DATETIME(3) NULL,
    status            VARCHAR(16) NOT NULL,
    source_dir_name   VARCHAR(255) NOT NULL,
    message           VARCHAR(1000) NULL,
    CONSTRAINT chk_run_status CHECK (status IN ('running', 'succeeded', 'failed'))
) ENGINE=InnoDB;

CREATE TABLE audit_source_file (
    run_id      BIGINT UNSIGNED NOT NULL,
    file_name   VARCHAR(128) NOT NULL,
    sha256      CHAR(64) NOT NULL,
    row_count   INT UNSIGNED NOT NULL,
    PRIMARY KEY (run_id, file_name),
    CONSTRAINT fk_source_file_run FOREIGN KEY (run_id) REFERENCES audit_ingestion_run (run_id)
) ENGINE=InnoDB;

CREATE TABLE audit_dq_result (
    run_id         BIGINT UNSIGNED NOT NULL,
    check_id       VARCHAR(64) NOT NULL,
    description    VARCHAR(255) NOT NULL,
    severity       VARCHAR(8) NOT NULL,
    affected_rows  BIGINT UNSIGNED NOT NULL,
    status         VARCHAR(8) NOT NULL,
    PRIMARY KEY (run_id, check_id),
    CONSTRAINT fk_dq_run FOREIGN KEY (run_id) REFERENCES audit_ingestion_run (run_id),
    CONSTRAINT chk_dq_severity CHECK (severity IN ('blocking', 'warning', 'info')),
    CONSTRAINT chk_dq_status CHECK (status IN ('pass', 'fail', 'reported'))
) ENGINE=InnoDB;

CREATE TABLE raw_customers (
    source_row_number         INT UNSIGNED NOT NULL PRIMARY KEY,
    customer_id               VARCHAR(64) NOT NULL,
    customer_unique_id        VARCHAR(64) NOT NULL,
    customer_zip_code_prefix  VARCHAR(16) NOT NULL,
    customer_city             VARCHAR(255) NOT NULL,
    customer_state            VARCHAR(16) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_geolocation (
    source_row_number            INT UNSIGNED NOT NULL PRIMARY KEY,
    geolocation_zip_code_prefix  VARCHAR(16) NOT NULL,
    geolocation_lat              VARCHAR(32) NOT NULL,
    geolocation_lng              VARCHAR(32) NOT NULL,
    geolocation_city             VARCHAR(255) NOT NULL,
    geolocation_state            VARCHAR(16) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_order_items (
    source_row_number    INT UNSIGNED NOT NULL PRIMARY KEY,
    order_id             VARCHAR(64) NOT NULL,
    order_item_id        VARCHAR(16) NOT NULL,
    product_id           VARCHAR(64) NOT NULL,
    seller_id            VARCHAR(64) NOT NULL,
    shipping_limit_date  VARCHAR(32) NOT NULL,
    price                VARCHAR(32) NOT NULL,
    freight_value        VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_order_payments (
    source_row_number     INT UNSIGNED NOT NULL PRIMARY KEY,
    order_id              VARCHAR(64) NOT NULL,
    payment_sequential    VARCHAR(16) NOT NULL,
    payment_type          VARCHAR(32) NOT NULL,
    payment_installments  VARCHAR(16) NOT NULL,
    payment_value         VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_order_reviews (
    source_row_number        INT UNSIGNED NOT NULL PRIMARY KEY,
    review_id                VARCHAR(64) NOT NULL,
    order_id                 VARCHAR(64) NOT NULL,
    review_score             VARCHAR(16) NOT NULL,
    review_comment_title     TEXT NOT NULL,
    review_comment_message   TEXT NOT NULL,
    review_creation_date     VARCHAR(32) NOT NULL,
    review_answer_timestamp  VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_orders (
    source_row_number              INT UNSIGNED NOT NULL PRIMARY KEY,
    order_id                       VARCHAR(64) NOT NULL,
    customer_id                    VARCHAR(64) NOT NULL,
    order_status                   VARCHAR(32) NOT NULL,
    order_purchase_timestamp       VARCHAR(32) NOT NULL,
    order_approved_at              VARCHAR(32) NOT NULL,
    order_delivered_carrier_date   VARCHAR(32) NOT NULL,
    order_delivered_customer_date  VARCHAR(32) NOT NULL,
    order_estimated_delivery_date  VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_products (
    source_row_number           INT UNSIGNED NOT NULL PRIMARY KEY,
    product_id                  VARCHAR(64) NOT NULL,
    product_category_name       VARCHAR(255) NOT NULL,
    product_name_lenght         VARCHAR(16) NOT NULL,
    product_description_lenght  VARCHAR(16) NOT NULL,
    product_photos_qty          VARCHAR(16) NOT NULL,
    product_weight_g            VARCHAR(16) NOT NULL,
    product_length_cm           VARCHAR(16) NOT NULL,
    product_height_cm           VARCHAR(16) NOT NULL,
    product_width_cm            VARCHAR(16) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_sellers (
    source_row_number       INT UNSIGNED NOT NULL PRIMARY KEY,
    seller_id               VARCHAR(64) NOT NULL,
    seller_zip_code_prefix  VARCHAR(16) NOT NULL,
    seller_city             VARCHAR(255) NOT NULL,
    seller_state            VARCHAR(16) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE raw_category_translation (
    source_row_number              INT UNSIGNED NOT NULL PRIMARY KEY,
    product_category_name          VARCHAR(255) NOT NULL,
    product_category_name_english  VARCHAR(255) NOT NULL
) ENGINE=InnoDB;
