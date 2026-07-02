"""export_roster — stream the full in-scope result to a CSV/XLSX file.

Sensitive columns are excluded (see db.ROSTER_COLUMNS). In dev the file lands
on local disk; the cloud target is Blob storage + a short-lived SAS URL.
"""

from __future__ import annotations

from typing import Any

from ..auth_obo import Scope, resolve_scope
from ..config import export_dir
from ..db import ROSTER_COLUMNS, build_where, columns_sql, connect, get_query
from ..export import export_rows


def export_roster(
    filters: dict[str, Any] | None = None,
    format: str = "csv",
    scope: Scope | None = None,
) -> dict:
    scope = scope or resolve_scope()
    where, params = build_where(filters, scope)
    sql = get_query("export_roster").format(where=where, columns=columns_sql())
    conn = connect()
    try:
        cursor = conn.execute(sql, params)  # streamed, not materialized
        path, n = export_rows(cursor, ROSTER_COLUMNS, format, export_dir())
    finally:
        conn.close()
    # ponytail: local path in dev; cloud phase returns a Blob SAS URL instead.
    return {
        "path": str(path),
        "row_count": n,
        "columns": ROSTER_COLUMNS,
        "format": format,
        "scope_upn": scope.user_upn,
    }
