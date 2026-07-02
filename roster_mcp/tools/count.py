"""count_roster — headcount for a filter, within the caller's RLS scope."""

from __future__ import annotations

from typing import Any

from ..auth_obo import Scope, resolve_scope
from ..db import build_where, connect, get_query


def count_roster(filters: dict[str, Any] | None = None, scope: Scope | None = None) -> dict:
    scope = scope or resolve_scope()
    where, params = build_where(filters, scope)
    sql = get_query("count_roster").format(where=where)
    with connect() as conn:
        n = conn.execute(sql, params).fetchone()["n"]
    return {"count": int(n), "filters": filters or {}, "scope_upn": scope.user_upn}
