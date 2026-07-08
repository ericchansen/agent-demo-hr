---
title: Run the demo
nav_order: 5
---

# Run the demo

A **fully local, Teams-style chat** over the pieces this repo already ships — no
Fabric, Foundry, Entra, or Teams tenant required. It exists so you can see the
product from a user's seat: ask a question, watch it route down the right path,
and prove row-level security by switching who's signed in.

![Contoso HR Assistant — the local chat demo]({{ "/assets/demo.png" | relative_url }})

## Start it

```bash
python data/seed_local.py     # once — builds data/hr_local.db from the synthetic seed
python -m demo.app            # serves http://127.0.0.1:8000
```

Open <http://127.0.0.1:8000> and click a suggested question (or type your own).

## What you're looking at

- **Signed in as** (top right) — the persona dropdown. It sets the signed-in
  user for every request; *nothing in the message* can widen what they see.
- **A path/tool badge** on each answer — <span style="color:#4a9eda">**aggregate**</span>
  (the data-agent path) or <span style="color:#b17ad6">**deterministic**</span>
  (a Roster tool). This mirrors the two paths on the
  [Architecture]({{ "/architecture.html" | relative_url }}) page.
- **Real results** — list/org answers render a table; exports produce a genuine
  `.xlsx` download with sensitive columns stripped out.

## The two paths

| You ask… | Path | Tool |
|----------|------|------|
| "attrition rate in EMEA?", "which team has the highest attrition?" | aggregate | `region_attrition`, `top_attrition_team` |
| "list active Azure Data employees", "who rolls up to 100001?", "export my region" | deterministic | `list_roster`, `list_org_under`, `export_roster` |

The exact numbers are the acceptance test on the
[Demo script]({{ "/demo-script.html" | relative_url }}) page.

## The RLS money-shot

Run **"Export the full active roster for my region"** as **EMEA** → **1088 rows**.
Switch the persona to **APAC** and run the *same question* → **822 rows**. Same
prompt, different rows, enforced **server-side** from the signed-in user — never
from the message. The two rowsets are provably disjoint (see
[Identity & RLS]({{ "/identity-flow.html" | relative_url }})).

## What's real vs. stand-in

The Roster tools, the parameterized SQL, the RLS filtering, and the export are
the **same code** that runs in the cloud. Two pieces are local stand-ins:

- the **aggregate answers** are computed straight from the SQLite seed
  (`demo/data_agent.py`) instead of the Fabric data agent, and
- the **router** (`demo/router.py`) is a keyword heuristic instead of the Foundry
  LLM orchestrator.

Both reproduce the numbers pinned in `orchestrator/eval/golden.jsonl`, and both
get swapped for their cloud counterparts without touching the tool contracts —
see [Local → cloud mapping]({{ "/production-mapping.html" | relative_url }}) and
[Current limitations]({{ "/preview-limitations.html" | relative_url }}).
