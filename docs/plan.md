# Plan & phases

This repo is built in phases. This session delivered the **local scaffold**
(Phases 0, 2, 5, and the eval harness). Cloud phases are authored later by a
human against a demo Azure tenant.

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Repo scaffold, tooling, CI, local dev loop | ✅ this session |
| 1 | Fabric lakehouse + semantic model | ⛔ cloud — TODO |
| 2 | Synthetic data generator (deterministic) | ✅ this session |
| 3 | Fabric data agent (NL2SQL, aggregate path) | ⛔ cloud — TODO |
| 4 | Foundry orchestrator wiring to live services | ⛔ cloud — TODO |
| 5 | Roster MCP server + tools (local SQLite + mock identity) | ✅ this session |
| 6 | Teams SSO + publish | ⛔ cloud — TODO |
| 7 | azd / Bicep deploy | ⛔ cloud — TODO |
| — | Local eval harness (routing/golden/RLS) | ✅ this session |

## What "done" means for the local scaffold

Clone → `pip install -e ".[dev]"` → `generate → seed → eval` → a working local
roster demo: MCP tools return correct scoped data, export produces a real
xlsx/csv with a verified row count, the RLS negative test passes 100%, and
ruff + pytest + CI are green.

See `docs/production-mapping.md` for how each local piece maps to its cloud
counterpart.
