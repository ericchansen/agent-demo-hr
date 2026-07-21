---
title: Local → cloud mapping
nav_order: 8
---

# Production mapping

How each local scaffold piece maps to its cloud counterpart. **TODO items are
not built in this repo yet.**

| Local (this repo) | Production (cloud — TODO) |
|-------------------|---------------------------|
| `data/generate_hr.py` → parquet/CSV | Load into a **Fabric lakehouse**; build a semantic model / star schema |
| `data/hr_local.db` (SQLite) | **Fabric SQL** endpoint |
| `demo/data_agent.py` computes aggregate answers from SQLite | **Fabric data agent** (NL2SQL) for the aggregate path |
| `roster_mcp` against SQLite | Same MCP server against **Fabric SQL**, hosted (Container Apps / Functions) |
| `auth_obo.py` dev shim (env UPN) | **Confidential-client OBO** token exchange; Fabric enforces RLS |
| `hr_access` filter emulation | **Fabric row-level security** keyed to user identity |
| `export_roster` → local file path | Write to **Blob storage**, return a short-lived **SAS URL** |
| `orchestrator/instructions.md` | **Foundry** orchestrator agent config + tool wiring |
| `orchestrator/eval/run_eval.py` | Same eval, plus live routing/answer assertions against the deployed agent |
| Local persona dropdown / env-var identity | **Teams SSO** identity |
| — | **azd / Bicep** infra (`infra/`) |
| — | **Playwright/Edge** E2E (`e2e/`) |

The design intent: the MCP tool contracts and the RLS *behavior* stay identical
from local to cloud — only the data source and the identity mechanism change.
