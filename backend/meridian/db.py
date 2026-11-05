"""MySQL engines (SQLAlchemy Core + PyMySQL).

Connections use TLS (MySQL 8 enables it by default) so `caching_sha2_password` authentication works
without the optional `cryptography` package. Certificates are not verified because the server is local
and uses MySQL's self-signed certificate; see docs/DECISIONS.md D-020.
Every session uses UTC (`time_zone = '+00:00'`, D-017 rule T7).
"""

import ssl
from enum import StrEnum

from sqlalchemy import URL, Engine, create_engine, event

from meridian.config import Settings, get_settings


class Role(StrEnum):
    OWNER = "owner"
    READER = "reader"
    TEST = "test"


class UnsafeDatabaseError(RuntimeError):
    """Raised when an operation would touch a database it must not touch."""


def _tls_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def make_engine(role: Role = Role.OWNER, settings: Settings | None = None) -> Engine:
    s = settings or get_settings()
    user, password, database = {
        Role.OWNER: (s.db_owner_user, s.db_owner_password, s.db_name),
        Role.READER: (s.db_reader_user, s.db_reader_password, s.db_name),
        Role.TEST: (s.test_db_user, s.test_db_password, s.test_db_name),
    }[role]
    if role is Role.TEST and not (database.endswith("_test") and user == "meridian_test"):
        raise UnsafeDatabaseError("Test engine requires a database ending in '_test' and user 'meridian_test'")
    if not password.get_secret_value():
        raise RuntimeError(f"Password for role '{role.value}' is not set in .env")
    url = URL.create(
        "mysql+pymysql",
        username=user,
        password=password.get_secret_value(),
        host=s.db_host,
        port=s.db_port,
        database=database,
        query={"charset": "utf8mb4"},
    )
    engine = create_engine(
        url,
        pool_size=s.db_pool_size,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"ssl": _tls_context(), "connect_timeout": s.db_connect_timeout_seconds},
    )

    @event.listens_for(engine, "connect")
    def _session_setup(dbapi_conn, _record):  # noqa: ANN001
        with dbapi_conn.cursor() as cur:
            cur.execute("SET time_zone = '+00:00'")

    return engine
