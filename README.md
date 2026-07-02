# agent-demo-hr

An open-source parallel of a real customer engagement: a **Fabric-first HR
chatbot** on Azure AI Foundry, surfaced in Microsoft Teams, demonstrating a
**two-path agent pattern** with **row-level security** keyed to the signed-in
user.

> ## ⚠️ Synthetic data only
> Every employee, name, email, salary, and metric in this repo is **100%
> fictional** — generated for the imaginary company "Contoso" by
> `data/generate_hr.py`. **No real people or PII.** Design reference only (not
> downloaded): IBM HR Analytics Employee Attrition
> ([CC0, Kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset)).

## The two-path pattern

| Question style | Path | Example |
|----------------|------|---------|
| Aggregate / fuzzy (a number, rate, ranking) | **Fabric data agent** (NL2SQL) | "What's EMEA's attrition rate this year?" |
| Deterministic list / count / export | **Roster MCP server** (parameterized SQL, writes a file) | "Export the active EMEA roster to Excel." |

The **security money-shot**: an EMEA HR-BP and an APAC HR-BP ask the *identical*
question and get *different rows*, because every Roster MCP tool enforces the
caller's RLS scope server-side. See `docs/demo-script.md` for the full script.

## What's in this repo (local scaffold)

This session builds the **locally-runnable foundation only** — no cloud:

- `data/` — deterministic synthetic HR data generator + local SQLite seed.
- `roster_mcp/` — the Roster MCP server (MCP Python SDK), one module per tool,
  running against local SQLite with a **mock identity** shim.
- `orchestrator/` — draft instructions, user-context resolver, and a
  **local eval harness** (roster correctness + RLS non-leakage).
- `docs/`, `teams/`, `infra/`, `e2e/` — docs and **clearly-marked TODO stubs**
  for the cloud phases.

**Cloud deploy is a later phase** (Fabric lakehouse/semantic model/data agent,
Foundry live wiring, Teams SSO/publish, azd/Bicep, real OBO token exchange) —
see `docs/production-mapping.md`. Those are intentionally **not** built here.

## Quickstart

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Unix: source .venv/bin/activate
pip install -e ".[dev]"

python data/generate_hr.py            # (re)generate deterministic data — already committed
python data/seed_local.py             # build the local SQLite DB
python -m roster_mcp.server --smoke   # exercise the tools directly
python orchestrator/eval/run_eval.py  # roster correctness + RLS non-leakage
pytest -q                             # unit tests
```

### Run the MCP server

```bash
python -m roster_mcp.server           # stdio transport; point an MCP client at it
```

### Switch persona (see RLS in action)

The signed-in user is a dev shim driven by an env var. Swap it and re-run any
tool to get a different rowset:

```bash
# Windows PowerShell
$env:ROSTER_DEV_UPN = "apac.hrbp@contoso.com"
python -m roster_mcp.server --smoke
```

Personas live in `teams/personas.md`; the RLS scope map is `hr_access` in
`data/`.

## Tools (`roster_mcp/tools/`)

| Tool | Purpose |
|------|---------|
| `get_roster_schema` | distinct teams/orgs/regions/offices you may filter on (scoped) |
| `count_roster` | headcount for a filter (scoped) |
| `list_roster` | capped list of matching employees (scoped) |
| `list_org_under` | recursive org-tree walk under a manager (scoped) |
| `export_roster` | stream full in-scope result to CSV/XLSX; excludes sensitive columns |

All tools apply the caller's RLS scope server-side and use **parameterized SQL
only** (`roster_mcp/queries.sql`) — the SQL-injection boundary.

## License

MIT — see [LICENSE](LICENSE).
