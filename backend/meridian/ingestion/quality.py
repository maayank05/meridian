"""Data-quality checks on the staging layer (docs/data/DATA_QUALITY_ISSUES.md).

Each check is a SQL query returning the number of affected rows.
- 'blocking': must be 0, otherwise the whole pipeline run fails and rolls back.
- 'warning' / 'info': counted and recorded in audit_dq_result; downstream KPIs handle them by rule.
"""

from dataclasses import dataclass

from sqlalchemy import Connection, text


@dataclass(frozen=True)
class Check:
    check_id: str
    description: str
    severity: str
    sql: str


_TZ_COLUMNS = (
    ("stg_orders", "purchase_tz"),
    ("stg_orders", "approved_tz"),
    ("stg_orders", "delivered_carrier_tz"),
    ("stg_orders", "delivered_customer_tz"),
    ("stg_order_items", "shipping_limit_tz"),
    ("stg_order_reviews", "answer_tz"),
)


def _tz_count(status: str) -> str:
    parts = [f"(SELECT COUNT(*) FROM {t} WHERE {c} = '{status}')" for t, c in _TZ_COLUMNS]
    return "SELECT " + " + ".join(parts)


CHECKS: tuple[Check, ...] = (
    Check(
        "orphan_items_orders",
        "Order items whose order_id is not in orders",
        "blocking",
        "SELECT COUNT(*) FROM stg_order_items i LEFT JOIN stg_orders o ON o.order_id = i.order_id "
        "WHERE o.order_id IS NULL",
    ),
    Check(
        "orphan_items_products",
        "Order items whose product_id is not in products",
        "blocking",
        "SELECT COUNT(*) FROM stg_order_items i LEFT JOIN stg_products p ON p.product_id = i.product_id "
        "WHERE p.product_id IS NULL",
    ),
    Check(
        "orphan_items_sellers",
        "Order items whose seller_id is not in sellers",
        "blocking",
        "SELECT COUNT(*) FROM stg_order_items i LEFT JOIN stg_sellers s ON s.seller_id = i.seller_id "
        "WHERE s.seller_id IS NULL",
    ),
    Check(
        "orphan_payments_orders",
        "Payments whose order_id is not in orders",
        "blocking",
        "SELECT COUNT(*) FROM stg_order_payments p LEFT JOIN stg_orders o ON o.order_id = p.order_id "
        "WHERE o.order_id IS NULL",
    ),
    Check(
        "orphan_reviews_orders",
        "Reviews whose order_id is not in orders",
        "blocking",
        "SELECT COUNT(*) FROM stg_order_reviews r LEFT JOIN stg_orders o ON o.order_id = r.order_id "
        "WHERE o.order_id IS NULL",
    ),
    Check(
        "orphan_orders_customers",
        "Orders whose customer_id is not in customers",
        "blocking",
        "SELECT COUNT(*) FROM stg_orders o LEFT JOIN stg_customers c ON c.customer_id = o.customer_id "
        "WHERE c.customer_id IS NULL",
    ),
    Check(
        "orders_without_items",
        "Orders with no item rows (DQ-08)",
        "info",
        "SELECT COUNT(*) FROM stg_orders o WHERE NOT EXISTS "
        "(SELECT 1 FROM stg_order_items i WHERE i.order_id = o.order_id)",
    ),
    Check(
        "orders_without_payments",
        "Orders with no payment rows (DQ-09)",
        "warning",
        "SELECT COUNT(*) FROM stg_orders o WHERE NOT EXISTS "
        "(SELECT 1 FROM stg_order_payments p WHERE p.order_id = o.order_id)",
    ),
    Check(
        "delivered_missing_customer_date",
        "Delivered orders without customer delivery date (DQ-10)",
        "warning",
        "SELECT COUNT(*) FROM stg_orders WHERE order_status = 'delivered' AND delivered_customer_local IS NULL",
    ),
    Check(
        "carrier_before_approved",
        "Carrier date earlier than approval (DQ-12, RULE-27)",
        "warning",
        "SELECT COUNT(*) FROM stg_orders WHERE delivered_carrier_local < approved_local",
    ),
    Check(
        "carrier_before_purchase",
        "Carrier date earlier than purchase (DQ-12, RULE-27)",
        "warning",
        "SELECT COUNT(*) FROM stg_orders WHERE delivered_carrier_local < purchase_local",
    ),
    Check(
        "delivered_before_purchase",
        "Customer delivery earlier than purchase",
        "warning",
        "SELECT COUNT(*) FROM stg_orders WHERE delivered_customer_local < purchase_local",
    ),
    Check(
        "shipping_limit_over_60_days",
        "Item shipping limit > 60 days after purchase (DQ-13, RULE-27)",
        "warning",
        "SELECT COUNT(*) FROM stg_order_items i JOIN stg_orders o ON o.order_id = i.order_id "
        "WHERE i.shipping_limit_local > o.purchase_local + INTERVAL 60 DAY",
    ),
    Check(
        "products_missing_category",
        "Products without category (DQ-06)",
        "info",
        "SELECT COUNT(*) FROM stg_products WHERE product_category_name IS NULL",
    ),
    Check(
        "products_untranslated_category",
        "Products whose category has no English translation (DQ-07)",
        "info",
        "SELECT COUNT(*) FROM stg_products p LEFT JOIN stg_category_translation t "
        "ON t.product_category_name = p.product_category_name "
        "WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL",
    ),
    Check(
        "customers_zip_not_in_geolocation",
        "Customers whose zip prefix is absent from geolocation (DQ-05)",
        "info",
        "SELECT COUNT(*) FROM stg_customers c LEFT JOIN stg_geolocation_zip g "
        "ON g.zip_code_prefix = c.customer_zip_code_prefix WHERE g.zip_code_prefix IS NULL",
    ),
    Check(
        "sellers_zip_not_in_geolocation",
        "Sellers whose zip prefix is absent from geolocation (DQ-05)",
        "info",
        "SELECT COUNT(*) FROM stg_sellers s LEFT JOIN stg_geolocation_zip g "
        "ON g.zip_code_prefix = s.seller_zip_code_prefix WHERE g.zip_code_prefix IS NULL",
    ),
    Check(
        "geolocation_points_outside_bbox",
        "Geolocation rows outside Brazil bounding box (DQ-04)",
        "info",
        "SELECT COALESCE(SUM(n_points_outside_bbox), 0) FROM stg_geolocation_zip",
    ),
    Check(
        "payment_item_mismatch_orders",
        "Orders where payments differ from items+freight by > 0.01 (DQ-16)",
        "warning",
        "SELECT COUNT(*) FROM (SELECT order_id, SUM(price + freight_value) v FROM stg_order_items GROUP BY order_id) i "
        "JOIN (SELECT order_id, SUM(payment_value) v FROM stg_order_payments GROUP BY order_id) p "
        "ON p.order_id = i.order_id WHERE ABS(p.v - i.v) > 0.01",
    ),
    Check(
        "zero_value_payments",
        "Payment records with value 0 (DQ-17)",
        "info",
        "SELECT COUNT(*) FROM stg_order_payments WHERE payment_value = 0",
    ),
    Check(
        "credit_card_zero_installments",
        "Credit-card records with 0 instalments (DQ-17, RULE-28)",
        "warning",
        "SELECT COUNT(*) FROM stg_order_payments WHERE payment_type = 'credit_card' AND payment_installments = 0",
    ),
    Check(
        "shared_review_ids",
        "review_ids attached to more than one order (DQ-01, RULE-15)",
        "info",
        "SELECT COUNT(*) FROM (SELECT review_id FROM stg_order_reviews GROUP BY review_id HAVING COUNT(*) > 1) s",
    ),
    Check(
        "orders_multiple_reviews",
        "Orders with more than one review (DQ-02)",
        "info",
        "SELECT COUNT(*) FROM (SELECT order_id FROM stg_order_reviews GROUP BY order_id HAVING COUNT(*) > 1) s",
    ),
    Check(
        "review_before_delivery",
        "Reviews created before the delivery date (DQ-14)",
        "info",
        "SELECT COUNT(*) FROM stg_order_reviews r JOIN stg_orders o ON o.order_id = r.order_id "
        "WHERE o.delivered_customer_local IS NOT NULL AND r.review_creation_date < DATE(o.delivered_customer_local)",
    ),
    Check(
        "review_creation_had_time",
        "review_creation_date values with a non-midnight time (stored as DATE)",
        "info",
        "SELECT COUNT(*) FROM stg_order_reviews WHERE review_creation_had_time",
    ),
    Check(
        "tz_ambiguous_timestamps",
        "Local timestamps in a DST fall-back hour; UTC left NULL (D-017)",
        "info",
        _tz_count("ambiguous"),
    ),
    Check(
        "tz_nonexistent_timestamps",
        "Local timestamps in a DST gap; UTC left NULL (D-017)",
        "warning",
        _tz_count("nonexistent"),
    ),
)


def run_checks(conn: Connection) -> dict[str, int]:
    return {c.check_id: int(conn.execute(text(c.sql)).scalar_one()) for c in CHECKS}


def blocking_failures(results: dict[str, int]) -> list[str]:
    return [c.check_id for c in CHECKS if c.severity == "blocking" and results[c.check_id] > 0]
