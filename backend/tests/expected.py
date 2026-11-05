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

# ---------------------------------------------------------------- Milestone B KPIs (hand-calculated)
# Orders by purchase month: 2016-10 o6 unavailable | 2017-03 o1 delivered | 2017-10 o3 canceled, o5 delivered |
# 2018-02 o2 delivered | 2018-08 o4 shipped.  Delivered item prices: o1 100+100+50.50, o2 75.25, o5 50.50.
MONTHLY = {
    "2016-10": {
        "orders_placed": 1,
        "delivered_orders": 0,
        "delivered_merchandise_value": Decimal("0"),
        "freight_billed": Decimal("0"),
        "delivered_items": 0,
        "canceled_orders": 0,
        "unavailable_orders": 1,
        "active_customers": 0,
        "active_sellers": 0,
    },
    "2017-03": {
        "orders_placed": 1,
        "delivered_orders": 1,
        "delivered_merchandise_value": Decimal("250.50"),
        "freight_billed": Decimal("20.00"),
        "delivered_items": 3,
        "canceled_orders": 0,
        "unavailable_orders": 0,
        "active_customers": 1,
        "active_sellers": 2,
    },
    "2017-10": {
        "orders_placed": 2,
        "delivered_orders": 1,
        "delivered_merchandise_value": Decimal("50.50"),
        "freight_billed": Decimal("8.00"),
        "delivered_items": 1,
        "canceled_orders": 1,
        "unavailable_orders": 0,
        "active_customers": 1,
        "active_sellers": 1,
    },
    "2018-02": {
        "orders_placed": 1,
        "delivered_orders": 1,
        "delivered_merchandise_value": Decimal("75.25"),
        "freight_billed": Decimal("12.75"),
        "delivered_items": 1,
        "canceled_orders": 0,
        "unavailable_orders": 0,
        "active_customers": 1,
        "active_sellers": 1,
    },
    "2018-08": {
        "orders_placed": 1,
        "delivered_orders": 0,
        "delivered_merchandise_value": Decimal("0"),
        "freight_billed": Decimal("0"),
        "delivered_items": 0,
        "canceled_orders": 0,
        "unavailable_orders": 0,
        "active_customers": 0,
        "active_sellers": 0,
    },
}
K01_TOTAL = Decimal("376.25")  # 250.50 + 50.50 + 75.25
CATEGORY_VALUE = {"health_beauty": Decimal("200.00"), "pc_gamer": Decimal("101.00"), "unknown": Decimal("75.25")}
# Lead time (UTC): o1 2017-03-10 13:00 -> 2017-03-20 18:00 = 882,000 s; o5 2017-10-15 11:00 -> 2017-10-20 20:00
# = 464,400 s; o2 excluded (ambiguous purchase time). All 3 delivered on/before the estimate.
DELIVERY = {
    "delivered_orders": 3,
    "excluded_missing_delivery_date": 0,
    "excluded_ambiguous_time": 1,
    "lead_time_orders": 2,
    "avg_lead_time_seconds": 673200.0,
    "on_time_orders": 3,
    "late_orders": 0,
    "avg_days_late": None,
}
# Order scores: o1 5, o2 4, o5 4 (shared review-2), o4 1 -> mean 3.5; shared orders o2, o5.
REVIEWS = {"orders_with_review": 4, "avg_review_score": 3.5, "orders_with_shared_review": 2}
# Valid instalments: 4, 1, 1, 1, 1, 1 (credit-card 0 excluded) -> 9 / 6 = 1.5
PAYMENTS = {
    "by_type": {
        "boleto": (1, Decimal("88.00")),
        "credit_card": (3, Decimal("245.00")),
        "debit_card": (1, Decimal("60.00")),
        "voucher": (2, Decimal("90.50")),
    },
    "avg_valid_installments": 1.5,
    "invalid_records": 1,
}
RECONCILIATION = {
    "orders_with_both": 4,
    "matched_orders": 3,
    "payments_higher_orders": 1,
    "payments_lower_orders": 0,
    "items_only_orders": 0,
    "payments_only_orders": 2,
}
# People: person-1 (o1 2017-03, o2 2018-02), person-4 (o5 2017-10).
COHORTS = {("2017-03", 0): 1, ("2017-03", 11): 1, ("2017-10", 0): 1}
REPEAT_DEFAULT_WINDOW = {"customers": 2, "repeat_customers": 1, "repeat_rate": 0.5}
# Top 10% = ceil(0.1 * n) = 1 contributor. People: 325.75, 50.50. Sellers: seller-1 275.25, seller-2 101.00.
CUSTOMER_TOP10_SHARE = float(Decimal("325.75") / Decimal("376.25"))
SELLER_TOP10_SHARE = float(Decimal("275.25") / Decimal("376.25"))
