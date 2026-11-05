"""End-to-end pipeline tests on MySQL (meridian_test) against hand-calculated fixture values."""

import shutil
from datetime import datetime
from decimal import Decimal

import pytest
from pymysql.err import DataError
from sqlalchemy import text

from meridian.db import Role, make_engine
from meridian.ingestion.pipeline import QualityGateError, SourceValidationError, run_pipeline
from meridian.migrations import MIGRATIONS_DIR, MigrationError, migrate
from tests.expected import (
    DEFAULT_WINDOW_DAYS,
    ITEMS_FREIGHT_TOTAL,
    ITEMS_PRICE_TOTAL,
    MART_ROWS,
    PAYMENTS_TOTAL,
    QUALITY,
    RAW_ROWS,
)
from tests.fixtures.make_olist_fixture import hid
from tests.integration.conftest import FIXTURE, checksums, reset_database

pytestmark = pytest.mark.mysql


def scalar(engine, sql, **params):
    with engine.connect() as conn:
        return conn.execute(text(sql), params).scalar_one()


def test_clean_load_row_counts(engine, loaded):
    assert loaded.row_counts == RAW_ROWS
    for table, n in {**RAW_ROWS, **MART_ROWS}.items():
        assert scalar(engine, f"SELECT COUNT(*) FROM {table}") == n, table


def test_quality_results_match_hand_calculation(engine, loaded):
    assert loaded.quality == QUALITY
    stored = scalar(engine, "SELECT COUNT(*) FROM audit_dq_result WHERE run_id = :r", r=loaded.run_id)
    assert stored == len(QUALITY)
    assert scalar(engine, "SELECT status FROM audit_ingestion_run WHERE run_id = :r", r=loaded.run_id) == "succeeded"
    assert scalar(engine, "SELECT COUNT(*) FROM audit_source_file WHERE run_id = :r", r=loaded.run_id) == 9


def test_raw_text_preserved_exactly(engine, loaded):
    msg = scalar(
        engine,
        "SELECT review_comment_message FROM raw_order_reviews WHERE review_id = :r AND order_id = :o",
        r=hid("review-1"),
        o=hid("order-1"),
    )
    assert msg == "Ótimo produto,\nchegou rápido"
    assert scalar(engine, "SELECT order_approved_at FROM raw_orders WHERE order_id = :o", o=hid("order-3")) == ""


def test_reconciliation_raw_to_marts(engine, loaded):
    raw_price = scalar(engine, "SELECT SUM(CAST(price AS DECIMAL(12,2))) FROM raw_order_items")
    assert raw_price == ITEMS_PRICE_TOTAL
    assert scalar(engine, "SELECT SUM(price) FROM fact_order_items") == ITEMS_PRICE_TOTAL
    assert scalar(engine, "SELECT SUM(freight_value) FROM fact_order_items") == ITEMS_FREIGHT_TOTAL
    assert scalar(engine, "SELECT SUM(payment_value) FROM fact_payments") == PAYMENTS_TOTAL
    # order-grain totals equal item/payment-grain totals (no fan-out in fact_orders)
    assert scalar(engine, "SELECT SUM(items_price_total) FROM fact_orders") == ITEMS_PRICE_TOTAL
    assert scalar(engine, "SELECT SUM(payments_total) FROM fact_orders") == PAYMENTS_TOTAL
    with engine.connect() as conn:
        o1 = conn.execute(
            text(
                "SELECT item_count, items_price_total, items_freight_total, payment_count, "
                "payments_total FROM fact_orders WHERE order_id = :o"
            ),
            {"o": hid("order-1")},
        ).one()
    assert tuple(o1) == (3, Decimal("250.50"), Decimal("20.00"), 2, Decimal("270.50"))


def test_relationships_and_flags(engine, loaded):
    for sql in (
        "SELECT COUNT(*) FROM fact_order_items i LEFT JOIN fact_orders o USING (order_id) WHERE o.order_id IS NULL",
        "SELECT COUNT(*) FROM fact_payments p LEFT JOIN fact_orders o USING (order_id) WHERE o.order_id IS NULL",
        "SELECT COUNT(*) FROM fact_reviews r LEFT JOIN fact_orders o USING (order_id) WHERE o.order_id IS NULL",
        "SELECT COUNT(*) FROM fact_orders o LEFT JOIN dim_customer c USING (customer_id) WHERE c.customer_id IS NULL",
    ):
        assert scalar(engine, sql) == 0
    assert scalar(engine, "SELECT COUNT(*) FROM fact_reviews WHERE is_shared_review") == 2
    assert scalar(engine, "SELECT COUNT(*) FROM fact_payments WHERE is_invalid_installments") == 1
    assert (
        scalar(engine, "SELECT category_name_en FROM dim_product WHERE product_id = :p", p=hid("product-3"))
        == "unknown"
    )
    assert (
        scalar(engine, "SELECT category_name_en FROM dim_product WHERE product_id = :p", p=hid("product-2"))
        == "pc_gamer"
    )
    assert scalar(engine, "SELECT is_untranslated FROM dim_product WHERE product_id = :p", p=hid("product-2")) == 1
    assert scalar(engine, "SELECT COUNT(*) FROM dim_date WHERE coverage_flag = 'default_window'") == DEFAULT_WINDOW_DAYS
    assert scalar(engine, "SELECT coverage_flag FROM dim_date WHERE date_key = '2018-09-15'") == "incomplete_cutoff"
    assert (
        scalar(engine, "SELECT zip_in_geolocation FROM dim_customer WHERE customer_id = :c", c=hid("customer-5")) == 0
    )


def test_timezone_columns(engine, loaded):
    with engine.connect() as conn:
        rows = {
            r.order_id: r
            for r in conn.execute(text("SELECT order_id, purchase_local, purchase_utc, purchase_tz FROM stg_orders"))
        }
    o1, o2, o5 = rows[hid("order-1")], rows[hid("order-2")], rows[hid("order-5")]
    assert (o1.purchase_utc, o1.purchase_tz) == (datetime(2017, 3, 10, 13, 0), "ok")  # UTC-3
    assert (o5.purchase_utc, o5.purchase_tz) == (datetime(2017, 10, 15, 11, 0), "ok")  # UTC-2 (DST)
    assert (o2.purchase_local, o2.purchase_utc, o2.purchase_tz) == (datetime(2018, 2, 17, 23, 30), None, "ambiguous")
    assert scalar(engine, "SELECT purchase_utc FROM fact_orders WHERE order_id = :o", o=hid("order-2")) is None
    assert (
        scalar(engine, "SELECT approved_tz FROM stg_orders WHERE order_id = :o", o=hid("order-3")) is None
    )  # no value


def test_repeat_load_is_idempotent(engine, loaded):
    before = checksums(engine)
    run_pipeline(engine, FIXTURE)
    assert checksums(engine) == before


def test_rebuild_from_scratch_is_deterministic(engine, loaded):
    before = checksums(engine)
    reset_database(engine)
    migrate(engine)
    run_pipeline(engine, FIXTURE)
    assert checksums(engine) == before


def test_failed_run_rolls_back_and_is_audited(engine, loaded, tmp_path):
    before = checksums(engine)
    shutil.copytree(FIXTURE, tmp_path, dirs_exist_ok=True)
    items = tmp_path / "olist_order_items_dataset.csv"
    items.write_text(
        items.read_text(encoding="utf-8")
        + f"{hid('order-missing')},1,{hid('product-1')},{hid('seller-1')},2017-03-14 10:00:00,1.00,1.00\n",
        encoding="utf-8",
    )
    with pytest.raises(QualityGateError, match="orphan_items_orders=1"):
        run_pipeline(engine, tmp_path)
    assert checksums(engine) == before  # previous state fully preserved
    with engine.connect() as conn:
        status, message = conn.execute(
            text("SELECT status, message FROM audit_ingestion_run ORDER BY run_id DESC LIMIT 1")
        ).one()
    assert status == "failed" and "orphan_items_orders=1" in message


def test_invalid_value_fails_under_strict_mode_and_rolls_back(engine, loaded, tmp_path):
    before = checksums(engine)
    shutil.copytree(FIXTURE, tmp_path, dirs_exist_ok=True)
    items = tmp_path / "olist_order_items_dataset.csv"
    items.write_text(items.read_text(encoding="utf-8").replace(",100.00,10.00", ",abc,10.00", 1), encoding="utf-8")
    with pytest.raises(DataError, match="1366"):  # strict sql_mode: incorrect DECIMAL value
        run_pipeline(engine, tmp_path)
    assert checksums(engine) == before


def test_missing_file_fails_before_any_write(engine, loaded, tmp_path):
    shutil.copytree(FIXTURE, tmp_path, dirs_exist_ok=True)
    (tmp_path / "olist_orders_dataset.csv").unlink()
    runs_before = scalar(engine, "SELECT COUNT(*) FROM audit_ingestion_run")
    with pytest.raises(SourceValidationError):
        run_pipeline(engine, tmp_path)
    assert scalar(engine, "SELECT COUNT(*) FROM audit_ingestion_run") == runs_before


def test_migrations_are_recorded_and_edits_detected(engine, loaded, tmp_path):
    assert scalar(engine, "SELECT COUNT(*) FROM schema_version") == 6
    assert migrate(engine) == []  # nothing pending
    for f in MIGRATIONS_DIR.glob("*.sql"):
        shutil.copy(f, tmp_path / f.name)
    edited = tmp_path / "0001_audit_and_raw.sql"
    edited.write_text(edited.read_text(encoding="utf-8") + "\n-- edited after being applied\n", encoding="utf-8")
    with pytest.raises(MigrationError, match="checksum mismatch"):
        migrate(engine, tmp_path)


def test_reader_account_cannot_write():
    reader = make_engine(Role.READER)
    try:
        with pytest.raises(Exception, match="(?i)denied"), reader.begin() as conn:  # noqa: B017
            conn.execute(text("CREATE TABLE should_fail (id INT)"))
    finally:
        reader.dispose()
