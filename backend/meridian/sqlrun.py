"""Run version-controlled SQL files statement by statement on an open connection.

Statements are separated by a `;` at the end of a line; `--` comment lines are dropped. The SQL files in this
repository contain no procedures or string literals with `;`, so this simple splitter is sufficient.
Statements are executed through the DBAPI cursor without parameters, so `%` in date formats is literal.
"""

from pathlib import Path

from sqlalchemy import Connection

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def split_sql(text: str) -> list[str]:
    statements, current = [], []
    for line in text.splitlines():
        if line.strip().startswith("--"):
            continue
        current.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(current).strip().rstrip(";").strip()
            if stmt:
                statements.append(stmt)
            current = []
    if "\n".join(current).strip():
        raise ValueError("SQL text ends without a terminating ';'")
    return statements


def execute_statements(conn: Connection, statements: list[str]) -> None:
    cursor = conn.connection.driver_connection.cursor()
    try:
        for stmt in statements:
            cursor.execute(stmt)
    finally:
        cursor.close()


def run_sql_file(conn: Connection, path: Path) -> None:
    execute_statements(conn, split_sql(path.read_text(encoding="utf-8")))
