"""Build the local SQLite database from the committed synthetic CSV data."""

from __future__ import annotations

import csv
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from roster_mcp.config import DATA_DIR, db_path

SOURCES = {
    "fact_employee": DATA_DIR / "fact_employee.csv",
    "hr_access": DATA_DIR / "hr_access.csv",
}
INDEXES = (
    "CREATE INDEX ix_emp_region ON fact_employee(region)",
    "CREATE INDEX ix_emp_team ON fact_employee(team)",
    "CREATE INDEX ix_emp_mgr ON fact_employee(manager_id)",
    "CREATE INDEX ix_access_upn ON hr_access(user_upn)",
)


def _coerce(value: str):
    if not value:
        return None
    for convert in (int, float):
        try:
            return convert(value)
        except ValueError:
            pass
    return value


def _load(conn: sqlite3.Connection, table: str, source: Path) -> int:
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        columns = next(reader)
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(f"CREATE TABLE {table} ({', '.join(columns)})")
        placeholders = ", ".join("?" for _ in columns)
        rows = ([_coerce(value) for value in row] for row in reader)
        conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def seed(path: Path | None = None) -> Path:
    target = path or db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(target)) as conn, conn:
        employee_rows = _load(conn, "fact_employee", SOURCES["fact_employee"])
        access_rows = _load(conn, "hr_access", SOURCES["hr_access"])
        for statement in INDEXES:
            conn.execute(statement)
    print(
        f"seeded {employee_rows} employees + {access_rows} access rows -> {target}",
        file=sys.stderr,
    )
    return target


def ensure_seeded(path: Path | None = None) -> Path:
    target = path or db_path()
    if not target.exists() or any(
        source.stat().st_mtime_ns > target.stat().st_mtime_ns for source in SOURCES.values()
    ):
        seed(target)
    return target


if __name__ == "__main__":
    seed()
