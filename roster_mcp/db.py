"""SQLite access + the parameterized query builder (the injection boundary).

Everything that touches user input routes through ``build_where``, which only
ever interpolates whitelisted *column names* and binds *values* as parameters.
"""

from __future__ import annotations

import re
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import config

if TYPE_CHECKING:
    from .auth_obo import Scope

_SQL_FILE = Path(__file__).resolve().parent / "queries.sql"

# Columns a caller may filter on. Anything else is rejected at the boundary.
FILTER_COLUMNS = frozenset(
    {
        "region",
        "team",
        "org",
        "department",
        "office_location",
        "active_status",
        "employment_type",
    }
)

# Columns exposed in roster/list/export output. Sensitive attributes
# (gender, age, income, salary_band, performance, satisfaction) are excluded.
ROSTER_COLUMNS = [
    "employee_id",
    "full_name",
    "work_email",
    "manager_id",
    "job_title",
    "department",
    "team",
    "org",
    "region",
    "office_location",
    "hire_date",
    "employment_type",
    "active_status",
]

# Columns exposed for filter discovery.
SCHEMA_COLUMNS = ("region", "team", "org", "office_location", "department")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.db_path())
    conn.row_factory = sqlite3.Row
    return conn


@lru_cache(maxsize=1)
def _queries() -> dict[str, str]:
    text = _SQL_FILE.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for block in re.split(r"^-- name:\s*", text, flags=re.MULTILINE)[1:]:
        name, _, body = block.partition("\n")
        out[name.strip()] = body.strip().rstrip(";")
    return out


def get_query(name: str) -> str:
    return _queries()[name]


def columns_sql() -> str:
    return ", ".join(ROSTER_COLUMNS)


def build_where(filters: dict[str, Any] | None, scope: Scope) -> tuple[str, list[Any]]:
    """Compose a WHERE clause from user filters + the caller's RLS scope.

    # ponytail: keep — injection boundary. Column names come from FILTER_COLUMNS
    # (a code-owned whitelist); values are bound as parameters, never concatenated.
    """
    clauses: list[str] = []
    params: list[Any] = []
    for key, value in (filters or {}).items():
        if key not in FILTER_COLUMNS:
            raise ValueError(f"unknown filter column: {key!r}")
        clauses.append(f"{key} = ?")
        params.append(value)

    # RLS scope is non-negotiable and always ANDed in.
    if scope.allowed_region is not None:
        clauses.append("region = ?")
        params.append(scope.allowed_region)
    if scope.allowed_team is not None:
        clauses.append("team = ?")
        params.append(scope.allowed_team)

    where = " AND ".join(clauses) if clauses else "1=1"
    return where, params
