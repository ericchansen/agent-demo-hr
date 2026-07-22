---
title: Runbook
nav_order: 9
---

# Runbook

## Local dev loop

```bash
pip install -e ".[dev]"
hr-demo                              # auto-seed + run the user-facing demo
python -m roster_mcp.server --smoke   # smoke the tools
python -m roster_mcp.server           # run the MCP server (stdio)
python orchestrator/eval/run_eval.py  # eval + RLS
pytest -q                             # tests
ruff check . && ruff format --check . # lint + format
```

## Common tasks

- **Switch persona / demo RLS:** set `ROSTER_DEV_UPN` to `emea.hrbp@contoso.com`
  or `apac.hrbp@contoso.com` and re-run.
- **Regenerate the synthetic CSVs:** install `pip install -e ".[data]"`, then run
  `python data/generate_hr.py`. The committed seed normally requires no setup.
- **Regenerate golden numbers:** if you change the generator, recompute
  `orchestrator/eval/golden.jsonl` from the new seed, then re-run the eval.
- **Where do exports go?** `exports/` by default (`ROSTER_EXPORT_DIR`),
  git-ignored.

## Troubleshooting

- Missing `fact_employee.csv` / `hr_access.csv` → restore the committed files or
  regenerate them with the data extra.
- Eval/tests see stale data → rerun `hr-demo` or `python data/seed_local.py`; both
  replace the local SQLite database from the committed CSVs.
- Wrong rowset in a demo → check `ROSTER_DEV_UPN`; the scope follows the user.

## Cloud operations — TODO
Deploy, monitoring, on-call, token rotation, and incident response are authored
with the cloud phases (`infra/`, `docs/production-mapping.md`).
