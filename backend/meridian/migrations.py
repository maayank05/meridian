"""Ordered SQL migration runner with a `schema_version` table (D-007).

Each file `NNNN_name.sql` in backend/sql/migrations is applied once, in order. Its SHA-256 is recorded;
an already-applied file whose content changed is an error (never edit an applied migration — add a new one).
Note: MySQL DDL commits implicitly, so a migration that fails part-way must be repaired manually.
"""

import hashlib
import re
from pathlib import Path

from sqlalchemy import Engine, text

from meridian.sqlrun import SQL_DIR, run_sql_file

MIGRATIONS_DIR = SQL_DIR / "migrations"
_NAME = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


class MigrationError(RuntimeError):
    pass


def discover(directory: Path = MIGRATIONS_DIR) -> list[tuple[int, Path]]:
    found = []
    for path in sorted(directory.glob("*.sql")):
        m = _NAME.match(path.name)
        if not m:
            raise MigrationError(f"Invalid migration file name: {path.name}")
        found.append((int(m.group(1)), path))
    versions = [v for v, _ in found]
    if versions != list(range(1, len(versions) + 1)):
        raise MigrationError(f"Migration versions must be contiguous from 0001, got {versions}")
    return found


def migrate(engine: Engine, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Apply pending migrations; return the file names applied in this call."""
    applied_now = []
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_version ("
                " version INT UNSIGNED NOT NULL PRIMARY KEY, file_name VARCHAR(128) NOT NULL,"
                " sha256 CHAR(64) NOT NULL, applied_at_utc DATETIME(3) NOT NULL) ENGINE=InnoDB"
            )
        )
        done = {row.version: row.sha256 for row in conn.execute(text("SELECT version, sha256 FROM schema_version"))}
    for version, path in discover(directory):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if version in done:
            if done[version] != digest:
                raise MigrationError(f"Applied migration {path.name} was modified (checksum mismatch)")
            continue
        with engine.begin() as conn:
            run_sql_file(conn, path)
            conn.execute(
                text(
                    "INSERT INTO schema_version (version, file_name, sha256, applied_at_utc) "
                    "VALUES (:v, :f, :s, UTC_TIMESTAMP(3))"
                ),
                {"v": version, "f": path.name, "s": digest},
            )
        applied_now.append(path.name)
    return applied_now
