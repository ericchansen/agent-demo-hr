"""list_roster — capped list of matching employees, within the caller's scope."""

from __future__ import annotations

from typing import Any

from ..auth_obo import Scope, resolve_scope
from ..config import LIST_ROW_CAP
from ..db import ROSTER_COLUMNS, build_where, columns_sql, connect, get_query


def list_roster(
    filters: dict[str, Any] | None = None,
    limit: int = 100,
    scope: Scope | None = None,
) -> dict:
    scope = scope or resolve_scope()
    limit = max(1, min(int(limit), LIST_ROW_CAP))
    where, params = build_where(filters, scope)
    list_sql = get_query("list_roster").format(where=where, columns=columns_sql())
    count_sql = get_query("count_roster").format(where=where)
    with connect() as conn:
        rows = [dict(r) for r in conn.execute(list_sql, [*params, limit]).fetchall()]
        total = int(conn.execute(count_sql, params).fetchone()["n"])
    return {
        "rows": rows,
        "row_count": len(rows),
        "total_matching": total,
        "truncated": total > len(rows),
        "columns": ROSTER_COLUMNS,
        "scope_upn": scope.user_upn,
    }
