"""MySQL integration fixtures. Uses ONLY meridian_test via the meridian_test account (guarded in make_engine)."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from meridian.db import Role, make_engine
from meridian.ingestion.pipeline import run_pipeline
from meridian.migrations import migrate

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "olist"
DATA_PREFIXES = ("raw_", "stg_", "dim_", "fact_")


def reset_database(engine: Engine) -> None:
    with engine.begin() as conn:
        db = conn.execute(text("SELECT DATABASE()")).scalar_one()
        if not db.endswith("_test"):
            raise RuntimeError(f"refusing to reset non-test database {db!r}")
        objects = conn.execute(
            text("SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = DATABASE()")
        ).all()
        for name, kind in objects:  # views first: they depend on tables
            if kind == "VIEW":
                conn.execute(text(f"DROP VIEW `{name}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for name, kind in objects:
            if kind != "VIEW":
                conn.execute(text(f"DROP TABLE `{name}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


def data_tables(engine: Engine) -> list[str]:
    with engine.connect() as conn:
        names = [
            r[0]
            for r in conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() ORDER BY table_name"
                )
            )
        ]
    return [n for n in names if n.startswith(DATA_PREFIXES)]


def checksums(engine: Engine) -> dict[str, int]:
    with engine.connect() as conn:
        return {t: conn.execute(text(f"CHECKSUM TABLE `{t}`")).one()[1] for t in data_tables(engine)}


@pytest.fixture(scope="session")
def engine() -> Engine:
    try:
        eng = make_engine(Role.TEST)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"meridian_test database not reachable ({type(exc).__name__}); see docs/setup")
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def loaded(engine):
    """Fresh schema + one successful fixture load, shared by read-only tests."""
    reset_database(engine)
    migrate(engine)
    return run_pipeline(engine, FIXTURE)
