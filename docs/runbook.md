---
title: Runbook
nav_order: 9
---

# Runbook

## Local dev loop

```bash
pip install -e ".[dev]"
python data/generate_hr.py            # regenerate data (deterministic; already committed)
python data/seed_local.py             # build data/hr_local.db
python data/reset.py                  # drop + rebuild the DB cleanly
python -m roster_mcp.server --smoke   # smoke the tools
python -m roster_mcp.server           # run the MCP server (stdio)
python orchestrator/eval/run_eval.py  # eval + RLS
pytest -q                             # tests
ruff check . && ruff format --check . # lint + format
```

## Common tasks

- **Switch persona / demo RLS:** set `ROSTER_DEV_UPN` to `emea.hrbp@contoso.com`
  or `apac.hrbp@contoso.com` and re-run.
- **Regenerate golden numbers:** if you change the generator, recompute
  `orchestrator/eval/golden.jsonl` from the new seed, then re-run the eval.
- **Where do exports go?** `exports/` by default (`ROSTER_EXPORT_DIR`),
  git-ignored.

## Troubleshooting

- `FileNotFoundError: fact_employee.parquet` → run `python data/generate_hr.py`.
- Eval/tests see stale data → `python data/reset.py`.
- Wrong rowset in a demo → check `ROSTER_DEV_UPN`; the scope follows the user.

## Cloud operations — TODO
Deploy, monitoring, on-call, token rotation, and incident response are authored
with the cloud phases (`infra/`, `docs/production-mapping.md`).
