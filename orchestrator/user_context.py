"""Signed-in user context for the orchestrator.

Maps the signed-in UPN to its RLS scope so the orchestrator can resolve
phrases like "my region" before calling a Roster MCP tool. Thin wrapper over
the same auth_obo shim the MCP server uses — one source of truth for scope.
"""

from __future__ import annotations

from roster_mcp.auth_obo import resolve_scope


def caller_context(upn: str | None = None) -> dict:
    scope = resolve_scope(upn)
    return {
        "upn": scope.user_upn,
        "my_region": scope.allowed_region,
        "my_team": scope.allowed_team,
    }


def my_region_filters(upn: str | None = None, active_only: bool = True) -> dict:
    """Filters for a 'my region' request.

    Region is enforced server-side by the caller's scope regardless, so we only
    add the active-status filter here; region is left to RLS.
    """
    return {"active_status": "Active"} if active_only else {}


if __name__ == "__main__":
    print(caller_context("emea.hrbp@contoso.com"))
    print(caller_context("apac.hrbp@contoso.com"))
