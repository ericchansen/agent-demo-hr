"""Roster MCP server entrypoint (stdio transport).

python -m roster_mcp.server        # run the server
python -m roster_mcp.server --smoke  # local smoke check, no MCP client needed
"""

from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from data.seed_local import ensure_seeded

from .registry import register


def build_server() -> FastMCP:
    ensure_seeded()
    mcp = FastMCP("roster-mcp")
    register(mcp)
    return mcp


def _smoke() -> None:
    """Exercise the tools directly against the local DB (no MCP round-trip)."""
    from .auth_obo import resolve_scope
    from .tools import count, export_roster, schema
    from .tools import list as list_tool
    from .tools import org as org_tool

    ensure_seeded()
    scope = resolve_scope()
    print(f"scope: {scope.user_upn} region={scope.allowed_region} team={scope.allowed_team}")
    print("schema:", schema.get_roster_schema())
    active = count.count_roster({"active_status": "Active"}, scope)
    print("active count:", active["count"])
    listed = list_tool.list_roster({"active_status": "Active", "team": "Azure Data"}, 5, scope)
    print(f"list Azure Data active: total={listed['total_matching']} shown={listed['row_count']}")
    exported = export_roster.export_roster({"active_status": "Active"}, "xlsx", scope)
    print(f"export: {exported['path']} rows={exported['row_count']}")
    top = list_tool.list_roster({}, 1, scope)
    if top["rows"]:
        mgr = top["rows"][0]["employee_id"]
        print(f"org under {mgr}:", org_tool.list_org_under(mgr, 2, scope)["row_count"], "reports")


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        _smoke()
    else:
        build_server().run()
