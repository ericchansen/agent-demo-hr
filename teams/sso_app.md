# Teams SSO app — notes / TODO (cloud phase)

> **Not built in this scaffold.** This file records what the Teams surface will
> need so the structure exists.

## TODO
- [ ] Register an Entra ID app (single-tenant demo tenant).
- [ ] Expose an API scope (`access_as_user`) for the Roster MCP / orchestrator.
- [ ] Configure a Teams app manifest with SSO (`webApplicationInfo`: app id +
      resource URI).
- [ ] Consent flow for the OBO downstream scope (Fabric SQL).
- [ ] Wire the acquired user token into the Foundry orchestrator → Roster MCP,
      where the confidential-client OBO exchange happens (see
      `roster_mcp/auth_obo.py` TODO).
- [ ] Publish to the demo tenant's Teams app catalog.

## Identity contract
The signed-in Teams user's token replaces the local `ROSTER_DEV_UPN` shim. RLS
is then enforced by Fabric keyed to that identity. See `docs/identity-flow.md`.
