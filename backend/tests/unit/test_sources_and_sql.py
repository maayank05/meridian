"""Source validation, SQL splitting, migration discovery and database-safety guards (no database needed)."""

import shutil
from pathlib import Path

import pytest
from pydantic import SecretStr

from meridian.config import Settings
from meridian.db import Role, UnsafeDatabaseError, make_engine
from meridian.ingestion.pipeline import SourceValidationError, read_source, validate_sources
from meridian.ingestion.sources import SOURCES
from meridian.migrations import MigrationError, discover
from meridian.sqlrun import SQL_DIR, split_sql

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "olist"
BY_ALIAS = {s.alias: s for s in SOURCES}


def test_all_fixture_files_validate():
    loaded = validate_sources(FIXTURE)
    assert [f.source.alias for f in loaded] == [s.alias for s in SOURCES]
    assert all(len(f.sha256) == 64 for f in loaded)


def test_bom_file_header_is_clean():
    loaded = read_source(FIXTURE, BY_ALIAS["category_translation"])
    assert list(loaded.frame.columns)[0] == "product_category_name"


def test_embedded_line_break_and_empty_strings_preserved():
    frame = read_source(FIXTURE, BY_ALIAS["order_reviews"]).frame
    assert len(frame) == 4
    assert "Ótimo produto,\nchegou rápido" in set(frame["review_comment_message"])
    assert (frame["review_comment_title"] == "").sum() == 3  # empty stays '' (never NaN)


def test_missing_file_fails(tmp_path):
    for s in SOURCES[1:]:
        shutil.copy(FIXTURE / s.file_name, tmp_path / s.file_name)
    with pytest.raises(SourceValidationError, match="Missing source file: olist_customers_dataset.csv"):
        validate_sources(tmp_path)


def test_renamed_column_fails(tmp_path):
    src = BY_ALIAS["sellers"]
    text = (FIXTURE / src.file_name).read_text(encoding="utf-8").replace("seller_city", "city", 1)
    (tmp_path / src.file_name).write_text(text, encoding="utf-8")
    with pytest.raises(SourceValidationError, match="Unexpected header"):
        read_source(tmp_path, src)


def test_split_sql_drops_comments_and_requires_terminator():
    assert split_sql("-- c\nSELECT 1;\nSELECT\n  2;\n") == ["SELECT 1", "SELECT\n  2"]
    with pytest.raises(ValueError, match="terminating"):
        split_sql("SELECT 1")


def test_every_sql_file_parses():
    for path in sorted(SQL_DIR.rglob("*.sql")):
        assert split_sql(path.read_text(encoding="utf-8")), path.name


def test_migrations_are_contiguous():
    assert [v for v, _ in discover()] == [1, 2, 3, 4]


def test_bad_migration_name_rejected(tmp_path):
    (tmp_path / "1_bad.sql").write_text("SELECT 1;", encoding="utf-8")
    with pytest.raises(MigrationError, match="Invalid migration file name"):
        discover(tmp_path)


def test_test_engine_refuses_non_test_database():
    s = Settings(test_db_name="meridian_dev", test_db_password=SecretStr("x"), _env_file=None)
    with pytest.raises(UnsafeDatabaseError):
        make_engine(Role.TEST, s)


def test_missing_password_is_reported_without_value():
    s = Settings(db_owner_password=SecretStr(""), _env_file=None)
    with pytest.raises(RuntimeError, match="Password for role 'owner' is not set"):
        make_engine(Role.OWNER, s)


def test_settings_repr_never_shows_passwords():
    s = Settings(db_owner_password=SecretStr("very-secret-value"), _env_file=None)
    assert "very-secret-value" not in repr(s)
