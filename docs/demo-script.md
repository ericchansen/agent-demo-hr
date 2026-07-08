---
title: Demo script
nav_order: 4
---

# Demo script — the acceptance test

Six questions. Steps 1–2 exercise the **data-agent** (aggregate) path; steps
3–6 exercise the **Roster MCP** (deterministic) path. Step 6 is the RLS
money-shot. All data is synthetic Contoso.

Golden numbers below come from the committed seed (`orchestrator/eval/golden.jsonl`).

1. **"What's Contoso's attrition rate in EMEA this year?"**
   → data agent. Golden: EMEA attrition ≈ **22.8%** (322 / 1410).

2. **"Which team has the highest attrition?"**
   → data agent. Golden: **Azure Data** (~36%, a deliberately "hot" team).

3. **"List active employees on the Azure Data team in EMEA."**
   → `list_roster(team="Azure Data", active_status="Active")` as an EMEA persona.
   Golden: **62** rows.

4. **"Export the full active roster for my region to Excel."**
   → `export_roster(active_status="Active", format="xlsx")`. "My region" comes
   from the signed-in user's scope, not the message. EMEA persona → **1088** rows.

5. **"Who rolls up to employee 100001?"**
   → `list_org_under(manager_id=100001)` — recursive org-tree walk.

6. **RLS money-shot — run #4 as two different people.**
   - `ROSTER_DEV_UPN=emea.hrbp@contoso.com` → EMEA rows (1088).
   - `ROSTER_DEV_UPN=apac.hrbp@contoso.com` → APAC rows (822).
   Same question, **different rows**, enforced server-side. The two rowsets are
   provably disjoint (`orchestrator/eval/run_eval.py`).

## Reproduce locally

```bash
python data/seed_local.py
python orchestrator/eval/run_eval.py   # asserts 1–6's roster + RLS behavior
```
