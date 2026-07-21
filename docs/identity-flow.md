---
title: Identity & RLS
nav_order: 6
---

# Identity & RLS flow

## Local (this scaffold)

```
ROSTER_DEV_UPN ──► auth_obo.resolve_scope() ──► hr_access lookup ──► Scope
                                                                       │
                          every tool ANDs Scope into the WHERE clause ─┘
```

- `auth_obo.current_upn()` returns the default mock identity
  (`ROSTER_DEV_UPN`); the local web demo can explicitly select a synthetic
  persona instead.
- `resolve_scope()` reads `hr_access(user_upn, allowed_region, allowed_team)`.
- Unknown UPN → **fail closed** (impossible region, zero rows).
- RLS is emulated by filtering on `allowed_region` / `allowed_team`.
- The persona selector is a demo control, not an authentication boundary.

## Cloud (TODO — later phase)

```
Teams SSO ──► user token ──► Foundry orchestrator ──► Roster MCP
                                                          │
                              confidential-client OBO exchange (auth_obo TODO)
                                                          │
                                                    Fabric SQL token
                                                          │
                                          Fabric enforces RLS by user identity
```

Real flow, keyed to the signed-in user:
1. Teams SSO issues a user token (audience = the app).
2. The MCP server validates the token (issuer + audience).
3. Confidential-client **On-Behalf-Of** exchange for a Fabric SQL scope
   (`msal.ConfidentialClientApplication.acquire_token_on_behalf_of`) — see the
   fully-worked TODO block in `roster_mcp/auth_obo.py`.
4. Query Fabric **as the user**, so Fabric's own RLS applies. The local
   `hr_access` map becomes unnecessary once Fabric RLS is authoritative.

> **TODO (cloud):** implement steps 1–4, token caching/refresh, and audit
> logging. None of this is built locally.
