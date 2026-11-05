"""Generate the small SYNTHETIC Olist-shaped fixture used by tests (not real data).

Run: python backend/tests/fixtures/make_olist_fixture.py
Every value is invented. Identifiers are md5 hashes of readable labels (e.g. "order-1") so tests can refer to them.
Edge cases are planted deliberately; expected results are hand-calculated in backend/tests/expected.py.
"""

import csv
import hashlib
from pathlib import Path

OUT = Path(__file__).resolve().parent / "olist"


def hid(label: str) -> str:
    return hashlib.md5(label.encode(), usedforsecurity=False).hexdigest()


def write(name: str, header: list[str], rows: list[list[str]], *, crlf: bool = False, bom: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", newline="", encoding="utf-8-sig" if bom else "utf-8") as f:
        w = csv.writer(f, lineterminator="\r\n" if crlf else "\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(rows)


def main() -> None:
    c, o, p, s, r = (lambda n, k=k: hid(f"{k}-{n}") for k in ("customer", "order", "product", "seller", "review"))
    u = lambda n: hid(f"person-{n}")  # noqa: E731
    write(
        "olist_customers_dataset.csv",
        ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
        [
            [c(1), u(1), "01310", "sao paulo", "SP"],
            [c(2), u(1), "01310", "sao paulo", "SP"],  # same person, second order
            [c(3), u(2), "20040", "rio de janeiro", "RJ"],
            [c(4), u(3), "20040", "rio de janeiro", "RJ"],
            [c(5), u(4), "99999", "nowhere", "MG"],  # zip not in geolocation
            [c(6), u(5), "01310", "sao paulo", "SP"],
        ],
    )
    write(
        "olist_geolocation_dataset.csv",
        ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"],
        [
            ["01310", "-23.56", "-46.65", "sao paulo", "SP"],
            ["01310", "-23.56", "-46.65", "sao paulo", "SP"],  # exact duplicate
            ["01310", "-23.57", "-46.66", "são paulo", "SP"],
            ["01310", "45.0", "10.0", "sao paulo", "SP"],  # outside Brazil bounding box
            ["20040", "-22.90", "-43.17", "rio de janeiro", "RJ"],
        ],
    )
    write(
        "olist_orders_dataset.csv",
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        [
            [
                o(1),
                c(1),
                "delivered",
                "2017-03-10 10:00:00",
                "2017-03-10 10:15:00",
                "2017-03-12 09:00:00",
                "2017-03-20 15:00:00",
                "2017-03-25 00:00:00",
            ],
            # purchase falls in the repeated hour at DST fall-back (2018-02-17 23:00-23:59) -> ambiguous
            [
                o(2),
                c(2),
                "delivered",
                "2018-02-17 23:30:00",
                "2018-02-18 01:00:00",
                "2018-02-19 10:00:00",
                "2018-02-25 12:00:00",
                "2018-03-05 00:00:00",
            ],
            [o(3), c(3), "canceled", "2017-10-14 12:00:00", "", "", "", "2017-11-01 00:00:00"],
            [
                o(4),
                c(4),
                "shipped",
                "2018-08-30 08:00:00",
                "2018-08-30 09:00:00",
                "2018-08-31 10:00:00",
                "",
                "2018-09-15 00:00:00",
            ],
            # DST start day (gap was 00:00-00:59; 09:00 is valid); carrier before approval
            [
                o(5),
                c(5),
                "delivered",
                "2017-10-15 09:00:00",
                "2017-10-15 09:10:00",
                "2017-10-15 08:00:00",
                "2017-10-20 18:00:00",
                "2017-10-30 00:00:00",
            ],
            [o(6), c(6), "unavailable", "2016-10-05 10:00:00", "2016-10-05 11:00:00", "", "", "2016-10-25 00:00:00"],
        ],
    )
    write(
        "olist_order_items_dataset.csv",
        ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"],
        [
            [o(1), "1", p(1), s(1), "2017-03-14 10:00:00", "100.00", "10.00"],
            [o(1), "2", p(1), s(1), "2017-03-14 10:00:00", "100.00", "10.00"],  # same product twice
            [o(1), "3", p(2), s(2), "2017-03-14 10:00:00", "50.50", "0.00"],  # free freight
            [o(2), "1", p(3), s(1), "2018-02-22 10:00:00", "75.25", "12.75"],
            [o(4), "1", p(4), s(2), "2018-09-03 08:00:00", "20.00", "5.00"],
            [o(5), "1", p(2), s(2), "2020-04-09 22:35:08", "50.50", "8.00"],
        ],
    )  # far-future shipping limit
    write(
        "olist_order_payments_dataset.csv",
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
        [
            [o(1), "1", "credit_card", "4", "190.00"],
            [o(1), "2", "voucher", "1", "80.50"],  # o1 total 270.50 = items 250.50 + freight 20.00
            [o(2), "1", "boleto", "1", "88.00"],  # = 75.25 + 12.75
            [o(3), "1", "credit_card", "1", "30.00"],  # payments but no items
            [o(4), "1", "credit_card", "0", "25.00"],  # invalid 0 instalments; = 20.00 + 5.00
            [o(5), "1", "debit_card", "1", "60.00"],  # 1.50 above 50.50 + 8.00
            [o(6), "2", "voucher", "1", "10.00"],
        ],
    )  # sequence does not start at 1
    write(
        "olist_order_reviews_dataset.csv",
        [
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ],
        [
            [r(1), o(1), "5", "", "Ótimo produto,\nchegou rápido", "2017-03-21 00:00:00", "2017-03-22 10:00:00"],
            [r(2), o(2), "4", "", "", "2018-02-26 00:00:00", "2018-02-27 08:00:00"],  # shared review_id
            [r(2), o(5), "4", "", "", "2018-02-26 00:00:00", "2018-02-27 08:00:00"],
            [r(3), o(4), "1", "Atraso", "Não recebi", "2018-09-16 00:00:00", "2018-09-17 11:00:00"],
        ],
        crlf=True,
    )
    write(
        "olist_products_dataset.csv",
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
        [
            [p(1), "beleza_saude", "40", "300", "2", "500", "20", "10", "15"],
            [p(2), "pc_gamer", "35", "250", "1", "2000", "40", "20", "30"],  # untranslated category
            [p(3), "", "", "", "", "300", "16", "10", "11"],  # missing category/text attrs
            [p(4), "utilidades_domesticas", "30", "120", "3", "0", "10", "5", "8"],
        ],
    )  # weight 0
    write(
        "olist_sellers_dataset.csv",
        ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
        [[s(1), "01310", "sao paulo", "SP"], [s(2), "88888", "nowhere", "SC"]],
    )  # zip not in geolocation
    write(
        "product_category_name_translation.csv",
        ["product_category_name", "product_category_name_english"],
        [["beleza_saude", "health_beauty"], ["utilidades_domesticas", "housewares"]],
        crlf=True,
        bom=True,
    )


if __name__ == "__main__":
    main()
