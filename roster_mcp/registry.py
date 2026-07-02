"""Tool registry — wires the plain tool functions into a FastMCP server.

The MCP surface deliberately does NOT expose a `scope` parameter: identity is
resolved server-side (auth_obo) so a caller can never widen their own RLS scope.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import count, schema
from .tools import export_roster as export_tool
from .tools import list as list_tool
from .tools import org as org_tool


def _filters(
    region: str | None,
    team: str | None,
    org: str | None,
    department: str | None,
    office_location: str | None,
    active_status: str | None,
    employment_type: str | None,
) -> dict:
    raw = {
        "region": region,
        "team": team,
        "org": org,
        "department": department,
        "office_location": office_location,
        "active_status": active_status,
        "employment_type": employment_type,
    }
    return {k: v for k, v in raw.items() if v is not None}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def get_roster_schema() -> dict:
        """Distinct teams/orgs/regions/offices you're allowed to filter on."""
        return schema.get_roster_schema()

    @mcp.tool()
    def count_roster(
        region: str | None = None,
        team: str | None = None,
        org: str | None = None,
        department: str | None = None,
        office_location: str | None = None,
        active_status: str | None = None,
        employment_type: str | None = None,
    ) -> dict:
        """Headcount of employees matching the filters, within your access scope."""
        return count.count_roster(
            _filters(region, team, org, department, office_location, active_status, employment_type)
        )

    @mcp.tool()
    def list_roster(
        region: str | None = None,
        team: str | None = None,
        org: str | None = None,
        department: str | None = None,
        office_location: str | None = None,
        active_status: str | None = None,
        employment_type: str | None = None,
        limit: int = 100,
    ) -> dict:
        """List matching employees (capped) within your access scope."""
        return list_tool.list_roster(
            _filters(
                region, team, org, department, office_location, active_status, employment_type
            ),
            limit=limit,
        )

    @mcp.tool()
    def list_org_under(manager_id: int, depth: int | None = None) -> dict:
        """Everyone who rolls up to a manager (recursive), within your access scope."""
        return org_tool.list_org_under(manager_id, depth)

    @mcp.tool()
    def export_roster(
        region: str | None = None,
        team: str | None = None,
        org: str | None = None,
        department: str | None = None,
        office_location: str | None = None,
        active_status: str | None = None,
        employment_type: str | None = None,
        format: str = "csv",
    ) -> dict:
        """Export the full in-scope roster to a CSV/XLSX file. Excludes sensitive columns."""
        return export_tool.export_roster(
            _filters(
                region, team, org, department, office_location, active_status, employment_type
            ),
            format=format,
        )
