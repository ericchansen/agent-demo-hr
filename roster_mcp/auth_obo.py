"""Identity + row-level-security scope resolution.

LOCAL DEV SHIM. This module fakes the signed-in user and resolves their data
scope from the local ``hr_access`` table. In production this is replaced by a
real On-Behalf-Of (OBO) token exchange — see the TODO block below.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config, db


@dataclass(frozen=True)
class Scope:
    """The rows a caller is allowed to see. ``None`` means unrestricted on that axis."""

    user_upn: str
    allowed_region: str | None
    allowed_team: str | None


def current_upn() -> str:
    """Dev shim: the 'signed-in' user is whoever ROSTER_DEV_UPN points at.

    Swap the env var (or pass an explicit upn to resolve_scope) to demo RLS
    from a different persona.
    """
    return config.dev_upn()


def resolve_scope(upn: str | None = None) -> Scope:
    """Resolve a UPN to its RLS scope via the local hr_access map."""
    upn = upn or current_upn()
    with db.connect() as conn:
        row = conn.execute(
            "SELECT allowed_region, allowed_team FROM hr_access WHERE user_upn = ?",
            (upn,),
        ).fetchone()
    if row is None:
        # Unknown user → deny everything. An impossible region guarantees no
        # rows can ever match, so we fail closed rather than open.
        # ponytail: sentinel region beats a special-case branch in every tool.
        return Scope(upn, "__no_access__", None)
    return Scope(upn, row["allowed_region"], row["allowed_team"])


# ---------------------------------------------------------------------------
# TODO (cloud phase): replace the dev shim above with a real OBO exchange.
# ---------------------------------------------------------------------------
# In production the MCP server receives the end user's access token (audience =
# this API) from the Foundry orchestrator / Teams. To call Fabric SQL *as that
# user* (so Fabric's own RLS applies), perform a confidential-client
# On-Behalf-Of exchange:
#
#   from msal import ConfidentialClientApplication
#   app = ConfidentialClientApplication(
#       client_id=CLIENT_ID,
#       client_credential=CLIENT_SECRET,        # from Key Vault — never in git
#       authority=f"https://login.microsoftonline.com/{TENANT_ID}",
#   )
#   result = app.acquire_token_on_behalf_of(
#       user_assertion=incoming_user_token,
#       scopes=["https://analysis.windows.net/powerbi/api/.default"],  # Fabric SQL scope
#   )
#   fabric_token = result["access_token"]
#
# Then open the Fabric SQL connection with `fabric_token` and let Fabric enforce
# row-level security keyed to the user's identity. The `resolve_scope` mapping
# here becomes unnecessary once Fabric RLS is authoritative; until then we
# emulate it locally by filtering on allowed_region / allowed_team.
#
# Security notes for that phase:
#   * Validate the incoming token audience + issuer before exchange.
#   * Cache OBO results per (user, scope) with expiry; handle refresh.
#   * Log user_upn + tool + resolved scope for audit (see docs/threat-model.md).
# ---------------------------------------------------------------------------
