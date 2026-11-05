"""Expected Olist source files and exact headers (verified in Phase 2: docs/data/SOURCE_HEADERS.md)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFile:
    alias: str
    file_name: str
    columns: tuple[str, ...]

    @property
    def raw_table(self) -> str:
        return f"raw_{self.alias}"


SOURCES: tuple[SourceFile, ...] = (
    SourceFile(
        "customers",
        "olist_customers_dataset.csv",
        ("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"),
    ),
    SourceFile(
        "geolocation",
        "olist_geolocation_dataset.csv",
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"),
    ),
    SourceFile(
        "order_items",
        "olist_order_items_dataset.csv",
        ("order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"),
    ),
    SourceFile(
        "order_payments",
        "olist_order_payments_dataset.csv",
        ("order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"),
    ),
    SourceFile(
        "order_reviews",
        "olist_order_reviews_dataset.csv",
        (
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
    ),
    SourceFile(
        "orders",
        "olist_orders_dataset.csv",
        (
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    SourceFile(
        "products",
        "olist_products_dataset.csv",
        (
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    SourceFile(
        "sellers", "olist_sellers_dataset.csv", ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state")
    ),
    SourceFile(
        "category_translation",
        "product_category_name_translation.csv",
        ("product_category_name", "product_category_name_english"),
    ),
)
