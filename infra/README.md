# Infra — notes / TODO (cloud phase)

> **Not built in this scaffold.** azd / Bicep is authored later against a demo
> Azure tenant. This directory exists so the structure is in place.

## Planned (TODO)
- [ ] `azure.yaml` (azd) describing the services.
- [ ] Bicep modules for:
  - [ ] Azure AI Foundry project + orchestrator agent.
  - [ ] Fabric capacity / lakehouse / SQL endpoint (or reference existing).
  - [ ] Roster MCP host (Container Apps or Functions).
  - [ ] Storage account + container for roster exports (Blob + SAS).
  - [ ] Key Vault for the confidential-client secret (OBO).
  - [ ] Entra ID app registration wiring (see `teams/sso_app.md`).
- [ ] `azd up` provisions + deploys end to end.

## Mapping
See `docs/production-mapping.md` for how local pieces map to these resources.
