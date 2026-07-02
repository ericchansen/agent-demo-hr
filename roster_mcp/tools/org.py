"""list_org_under — everyone who rolls up to a manager (recursive org tree).

Uses a recursive CTE on manager_id. RLS scope is still applied, so a caller
only sees in-scope reports even when walking someone else's org.
"""

from __future__ import annotations

from ..auth_obo import Scope, resolve_scope
from ..db import ROSTER_COLUMNS, build_where, columns_sql, connect, get_query


def list_org_under(
    manager_id: int,
    depth: int | None = None,
    scope: Scope | None = None,
) -> dict:
    scope = scope or resolve_scope()
    # depth counts levels below the manager: 1 = direct reports only.
    max_depth = 50 if depth is None else max(1, int(depth))
    where, params = build_where(None, scope)
    sql = get_query("org_under").format(where=where, columns=columns_sql())
    with connect() as conn:
        rows = [
            dict(r) for r in conn.execute(sql, [int(manager_id), max_depth, *params]).fetchall()
        ]
    return {
        "manager_id": int(manager_id),
        "depth": max_depth,
        "rows": rows,
        "row_count": len(rows),
        "columns": ROSTER_COLUMNS,
        "scope_upn": scope.user_upn,
    }
