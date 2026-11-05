"""Hand-calculated expected values for the synthetic fixture (see fixtures/make_olist_fixture.py).

Written from the fixture definition by hand, NOT copied from pipeline output.
"""

from decimal import Decimal

RAW_ROWS = {
    "raw_customers": 6,
    "raw_geolocation": 5,
    "raw_order_items": 6,
    "raw_order_payments": 7,
    "raw_order_reviews": 4,
    "raw_orders": 6,
    "raw_products": 4,
    "raw_sellers": 2,
    "raw_category_translation": 2,
}
MART_ROWS = {
    "dim_customer": 6,
    "dim_product": 4,
    "dim_seller": 2,
    "fact_orders": 6,
    "fact_order_items": 6,
    "fact_payments": 7,
    "fact_reviews": 4,
    "dim_date": 1827,  # 2016-01-01..2020-12-31 = 366 + 365 + 365 + 365 + 366
}
DEFAULT_WINDOW_DAYS = 608  # 2017-01-01..2018-08-31 = 365 + 243

# Items: 100.00 + 100.00 + 50.50 + 75.25 + 20.00 + 50.50 ; freight: 10 + 10 + 0 + 12.75 + 5 + 8
ITEMS_PRICE_TOTAL = Decimal("396.25")
ITEMS_FREIGHT_TOTAL = Decimal("45.75")
# Payments: 190.00 + 80.50 + 88.00 + 30.00 + 25.00 + 60.00 + 10.00
PAYMENTS_TOTAL = Decimal("483.50")

QUALITY = {
    "orphan_items_orders": 0,
    "orphan_items_products": 0,
    "orphan_items_sellers": 0,
    "orphan_payments_orders": 0,
    "orphan_reviews_orders": 0,
    "orphan_orders_customers": 0,
    "orders_without_items": 2,  # order-3 (canceled), order-6 (unavailable)
    "orders_without_payments": 0,
    "delivered_missing_customer_date": 0,
    "carrier_before_approved": 1,  # order-5
    "carrier_before_purchase": 1,  # order-5
    "delivered_before_purchase": 0,
    "shipping_limit_over_60_days": 1,  # order-5 item (2020-04-09)
    "products_missing_category": 1,  # product-3
    "products_untranslated_category": 1,  # product-2 (pc_gamer)
    "customers_zip_not_in_geolocation": 1,  # customer-5 (99999)
    "sellers_zip_not_in_geolocation": 1,  # seller-2 (88888)
    "geolocation_points_outside_bbox": 1,
    "payment_item_mismatch_orders": 1,  # order-5: 60.00 vs 58.50
    "zero_value_payments": 0,
    "credit_card_zero_installments": 1,  # order-4
    "shared_review_ids": 1,  # review-2 on order-2 and order-5
    "orders_multiple_reviews": 0,
    "review_before_delivery": 0,
    "review_creation_had_time": 0,
    "tz_ambiguous_timestamps": 1,  # order-2 purchase 2018-02-17 23:30 (DST fall-back hour)
    "tz_nonexistent_timestamps": 0,
}
