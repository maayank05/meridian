"""Reconcile the loaded meridian_dev database against the source files and the Phase 2 profile.

Usage: python scripts/verify_dev_load.py
Read-only (reader account). Prints only aggregate comparisons; exits non-zero on any mismatch.
"""

import csv
import hashlib
import json
import sys
from decimal import Decimal

from sqlalchemy import text

from meridian.config import REPO_ROOT, get_settings
from meridian.db import Role, make_engine
from meridian.ingestion.sources import SOURCES

PROFILE = REPO_ROOT / "docs" / "data" / "profile_results.json"


def main() -> int:
    raw_dir = get_settings().raw_dir
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))["profile"]
    engine = make_engine(Role.READER)
    results: list[tuple[str, object, object]] = []

    def q(sql: str):
        with engine.connect() as conn:
            return conn.execute(text(sql)).scalar_one()

    run_id = q("SELECT MAX(run_id) FROM audit_ingestion_run WHERE status = 'succeeded'")
    for s in SOURCES:
        results.append(
            (
                f"rows {s.raw_table} vs profile",
                q(f"SELECT COUNT(*) FROM {s.raw_table}"),  # noqa: S608
                profile["files"][s.alias]["rows"],
            )
        )
        path = raw_dir / s.file_name
        stored = q(
            f"SELECT sha256 FROM audit_source_file WHERE run_id = {int(run_id)} "  # noqa: S608
            f"AND file_name = '{s.file_name}'"
        )
        results.append((f"sha256 {s.file_name} (file vs audit)", hashlib.sha256(path.read_bytes()).hexdigest(), stored))

    with open(raw_dir / "olist_orders_dataset.csv", newline="", encoding="utf-8") as f:
        delivered = {r["order_id"] for r in csv.DictReader(f) if r["order_status"] == "delivered"}
    price = freight = delivered_price = Decimal(0)
    with open(raw_dir / "olist_order_items_dataset.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            price += Decimal(r["price"])
            freight += Decimal(r["freight_value"])
            if r["order_id"] in delivered:
                delivered_price += Decimal(r["price"])
    with open(raw_dir / "olist_order_payments_dataset.csv", newline="", encoding="utf-8") as f:
        payments = sum((Decimal(r["payment_value"]) for r in csv.DictReader(f)), Decimal(0))

    results += [
        ("sum price: CSV (Decimal) vs fact_order_items", price, q("SELECT SUM(price) FROM fact_order_items")),
        ("sum freight: CSV vs fact_order_items", freight, q("SELECT SUM(freight_value) FROM fact_order_items")),
        ("sum payments: CSV vs fact_payments", payments, q("SELECT SUM(payment_value) FROM fact_payments")),
        (
            "sum price: item grain vs order grain (no fan-out)",
            q("SELECT SUM(price) FROM fact_order_items"),
            q("SELECT SUM(items_price_total) FROM fact_orders"),
        ),
        (
            "delivered-order price: CSV vs marts (K01 basis, not reported)",
            delivered_price,
            q(
                "SELECT SUM(i.price) FROM fact_order_items i JOIN fact_orders o USING (order_id) "
                "WHERE o.order_status = 'delivered'"
            ),
        ),
        ("fact_orders vs profile orders", q("SELECT COUNT(*) FROM fact_orders"), profile["files"]["orders"]["rows"]),
        (
            "delivered orders vs profile",
            q("SELECT COUNT(*) FROM fact_orders WHERE order_status = 'delivered'"),
            profile["order_status"]["delivered"]["orders"],
        ),
        (
            "distinct customer_unique_id vs profile",
            q("SELECT COUNT(DISTINCT customer_unique_id) FROM dim_customer"),
            profile["customer_identity"]["distinct_customer_unique_id"],
        ),
        (
            "shared-review rows vs profile",
            q("SELECT COUNT(*) FROM fact_reviews WHERE is_shared_review"),
            profile["keys"]["order_reviews.review_id"]["rows_in_duplicate_keys"],
        ),
        (
            "payment mismatch orders vs profile",
            q(
                f"SELECT affected_rows FROM audit_dq_result WHERE run_id = {int(run_id)} "  # noqa: S608
                "AND check_id = 'payment_item_mismatch_orders'"
            ),
            profile["reconciliation"]["all_with_both"]["payments_higher"]
            + profile["reconciliation"]["all_with_both"]["payments_lower"],
        ),
    ]
    engine.dispose()
    failed = 0
    for name, ours, expected in results:
        ok = ours == expected
        failed += not ok
        shown = "" if ok or name.startswith("sha256") else f"  got={ours} expected={expected}"
        print(f"{'MATCH' if ok else 'DIFF '}  {name}{shown}")
    print(f"\n{len(results) - failed} matched, {failed} differed (run {run_id})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
