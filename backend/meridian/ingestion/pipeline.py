"""Full-refresh ingestion pipeline (FR-010 to FR-015).

1. Validate: all 9 files present with exact headers (fails before any database write).
2. One transaction: clear -> raw load -> staging -> timezone map -> blocking quality gate -> marts -> audit rows.
   Any error rolls the whole transaction back, so the database keeps its previous consistent state.
3. The run itself is recorded in audit_ingestion_run in a separate transaction (status running/succeeded/failed).
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from sqlalchemy import Connection, Engine, text

from meridian.ingestion.quality import CHECKS, blocking_failures, run_checks
from meridian.ingestion.sources import SOURCES, SourceFile
from meridian.ingestion.timezones import to_utc
from meridian.sqlrun import SQL_DIR, run_sql_file

log = logging.getLogger(__name__)
TRANSFORMS = SQL_DIR / "transforms"
BATCH = 10_000
_TS_SOURCES = (
    ("stg_orders", "purchase_local"),
    ("stg_orders", "approved_local"),
    ("stg_orders", "delivered_carrier_local"),
    ("stg_orders", "delivered_customer_local"),
    ("stg_order_items", "shipping_limit_local"),
    ("stg_order_reviews", "answer_local"),
)


class SourceValidationError(ValueError):
    pass


class QualityGateError(RuntimeError):
    pass


@dataclass
class LoadedFile:
    source: SourceFile
    frame: pd.DataFrame
    sha256: str


@dataclass
class RunResult:
    run_id: int
    row_counts: dict[str, int]
    quality: dict[str, int]
    tz_status_counts: dict[str, int] = field(default_factory=dict)
    step_seconds: dict[str, float] = field(default_factory=dict)


def read_source(raw_dir: Path, source: SourceFile) -> LoadedFile:
    path = raw_dir / source.file_name
    if not path.is_file():
        raise SourceValidationError(f"Missing source file: {source.file_name}")
    data = path.read_bytes()
    # All columns as text; empty string is the only 'missing' marker; quote-aware (embedded line breaks).
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8-sig")
    if tuple(frame.columns) != source.columns:
        raise SourceValidationError(
            f"Unexpected header in {source.file_name}: expected {list(source.columns)}, got {list(frame.columns)}"
        )
    return LoadedFile(source, frame, hashlib.sha256(data).hexdigest())


def validate_sources(raw_dir: Path) -> list[LoadedFile]:
    return [read_source(raw_dir, s) for s in SOURCES]


def _load_raw(conn: Connection, loaded: LoadedFile) -> None:
    cols = ("source_row_number", *loaded.source.columns)
    sql = f"INSERT INTO {loaded.source.raw_table} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})"
    rows = list(loaded.frame.itertuples(index=False, name=None))
    cursor = conn.connection.driver_connection.cursor()
    try:
        for start in range(0, len(rows), BATCH):
            chunk = rows[start : start + BATCH]
            cursor.executemany(sql, [(start + i + 1, *r) for i, r in enumerate(chunk)])
    finally:
        cursor.close()
    loaded_count = conn.execute(text(f"SELECT COUNT(*) FROM {loaded.source.raw_table}")).scalar_one()
    if loaded_count != len(rows):
        raise QualityGateError(f"{loaded.source.raw_table}: loaded {loaded_count} rows, file has {len(rows)}")


def _build_tz_map(conn: Connection, tz_name: str) -> dict[str, int]:
    union = " UNION ".join(f"SELECT {c} AS ts FROM {t} WHERE {c} IS NOT NULL" for t, c in _TS_SOURCES)
    distinct = [row[0] for row in conn.execute(text(union))]
    rows, counts = [], {"ok": 0, "ambiguous": 0, "nonexistent": 0}
    for local in distinct:
        utc, status = to_utc(local, tz_name)
        rows.append((local, utc, status))
        counts[status] += 1
    cursor = conn.connection.driver_connection.cursor()
    try:
        for start in range(0, len(rows), BATCH):
            cursor.executemany(
                "INSERT INTO stg_tz_map (local_ts, utc_ts, tz_status) VALUES (%s, %s, %s)", rows[start : start + BATCH]
            )
    finally:
        cursor.close()
    return counts  # counts of DISTINCT local values by status


def run_pipeline(engine: Engine, raw_dir: Path, tz_name: str = "America/Sao_Paulo") -> RunResult:
    loaded = validate_sources(raw_dir)
    steps: dict[str, float] = {}
    with engine.begin() as conn:
        run_id = conn.execute(
            text(
                "INSERT INTO audit_ingestion_run (started_at_utc, status, source_dir_name) "
                "VALUES (UTC_TIMESTAMP(3), 'running', :d)"
            ),
            {"d": raw_dir.name},
        ).lastrowid
    try:
        with engine.begin() as conn:
            clock = time.perf_counter()

            def lap(step: str) -> None:
                nonlocal clock
                steps[step] = round(time.perf_counter() - clock, 1)
                clock = time.perf_counter()

            run_sql_file(conn, TRANSFORMS / "00_clear.sql")
            lap("clear")
            for item in loaded:
                _load_raw(conn, item)
            lap("raw_load")
            run_sql_file(conn, TRANSFORMS / "10_staging.sql")
            lap("staging")
            tz_counts = _build_tz_map(conn, tz_name)
            run_sql_file(conn, TRANSFORMS / "20_apply_timezones.sql")
            lap("timezones")
            quality = run_checks(conn)
            lap("quality_checks")
            failed = blocking_failures(quality)
            if failed:
                raise QualityGateError(
                    "Blocking data-quality checks failed: " + ", ".join(f"{c}={quality[c]}" for c in failed)
                )
            run_sql_file(conn, TRANSFORMS / "30_marts.sql")
            lap("marts")
            run_sql_file(conn, TRANSFORMS / "40_aggregates.sql")
            lap("aggregates")
            for item in loaded:
                conn.execute(
                    text(
                        "INSERT INTO audit_source_file (run_id, file_name, sha256, row_count) VALUES (:r, :f, :s, :n)"
                    ),
                    {"r": run_id, "f": item.source.file_name, "s": item.sha256, "n": len(item.frame)},
                )
            for check in CHECKS:
                status = "pass" if check.severity == "blocking" else "reported"
                conn.execute(
                    text(
                        "INSERT INTO audit_dq_result (run_id, check_id, description, severity, "
                        "affected_rows, status) VALUES (:r, :c, :d, :s, :n, :st)"
                    ),
                    {
                        "r": run_id,
                        "c": check.check_id,
                        "d": check.description,
                        "s": check.severity,
                        "n": quality[check.check_id],
                        "st": status,
                    },
                )
            conn.execute(
                text(
                    "UPDATE audit_ingestion_run SET status = 'succeeded', "
                    "finished_at_utc = UTC_TIMESTAMP(3) WHERE run_id = :r"
                ),
                {"r": run_id},
            )
    except Exception as exc:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE audit_ingestion_run SET status = 'failed', finished_at_utc = UTC_TIMESTAMP(3), "
                    "message = :m WHERE run_id = :r"
                ),
                {"m": f"{type(exc).__name__}: {exc}"[:1000], "r": run_id},
            )
        log.error("Pipeline run %s failed: %s", run_id, type(exc).__name__)
        raise
    return RunResult(run_id, {i.source.raw_table: len(i.frame) for i in loaded}, quality, tz_counts, steps)
