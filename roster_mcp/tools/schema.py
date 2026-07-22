"""get_roster_schema — distinct filterable values, scoped to the caller.

Lets the agent resolve/validate filters (e.g. which teams exist in EMEA)
without ever seeing values outside its RLS scope.
"""

from __future__ import annotations

from ..auth_obo import Scope, resolve_scope
from ..db import SCHEMA_COLUMNS, build_where, connect, get_query


def get_roster_schema(scope: Scope | None = None) -> dict:
    """Return the in-scope values accepted by roster filters."""
    scope = scope or resolve_scope()
    where, params = build_where(None, scope)
    out: dict[str, list] = {}
    with connect() as conn:
        for col in SCHEMA_COLUMNS:
            sql = get_query("schema_distinct").format(col=col, where=where)
            out[col] = [r["v"] for r in conn.execute(sql, params).fetchall()]
    return out
