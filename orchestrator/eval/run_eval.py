"""Local eval harness for the HR chatbot.

Runs the **roster path** (Roster MCP tools) for real against the seeded SQLite
DB and asserts correctness + RLS non-leakage across the two demo personas.
The **routing** and **data-agent (NL2SQL)** layers need the live orchestrator/
Fabric services, so they are printed and marked SKIP here.

    python orchestrator/eval/run_eval.py
"""

from __future__ import annotations

import json
from pathlib import Path

from data.seed_local import seed

HERE = Path(__file__).resolve().parent


def _seed() -> None:
    seed()


def _load(name: str) -> list[dict]:
    lines = (HERE / name).read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines if x.strip()]


class Runner:
    def __init__(self) -> None:
        self.passed = self.failed = self.skipped = 0

    def check(self, name: str, cond: bool) -> None:
        if cond:
            self.passed += 1
            print(f"  PASS  {name}")
        else:
            self.failed += 1
            print(f"  FAIL  {name}")

    def skip(self, name: str, why: str) -> None:
        self.skipped += 1
        print(f"  SKIP  {name} ({why})")


def main() -> int:
    _seed()
    from roster_mcp.auth_obo import resolve_scope
    from roster_mcp.db import connect
    from roster_mcp.tools.count import count_roster
    from roster_mcp.tools.export_roster import export_roster
    from roster_mcp.tools.list import list_roster

    golden = _load("golden.jsonl")
    prompts = _load("prompts.jsonl")
    r = Runner()

    print("== Roster path - Roster MCP tools (live) ==")
    for g in golden:
        if g["kind"] == "roster_rowset":
            scope = resolve_scope(g["scope_upn"])
            rows = list_roster(g["filters"], limit=10_000, scope=scope)["rows"]
            ids = sorted(row["employee_id"] for row in rows)
            r.check("roster_rowset ids exactly match golden", ids == g["employee_ids"])
            r.check(
                "roster_rowset count matches golden",
                count_roster(g["filters"], scope)["count"] == g["count"],
            )
        elif g["kind"] == "export_rowcount":
            scope = resolve_scope(g["scope_upn"])
            res = export_roster(g["filters"], "csv", scope)
            r.check("export row_count matches golden", res["row_count"] == g["row_count"])
            r.check(
                "export row_count reconciles with count tool",
                res["row_count"] == count_roster(g["filters"], scope)["count"],
            )
            print(f"        wrote {res['path']} ({res['row_count']} rows)")

    print("== RLS non-leakage across personas (must be 100%) ==")
    emea = resolve_scope("emea.hrbp@contoso.com")
    apac = resolve_scope("apac.hrbp@contoso.com")
    emea_ids = {row["employee_id"] for row in list_roster({}, 10_000, emea)["rows"]}
    apac_ids = {row["employee_id"] for row in list_roster({}, 10_000, apac)["rows"]}
    r.check("EMEA and APAC rowsets are disjoint", bool(emea_ids) and emea_ids.isdisjoint(apac_ids))
    r.check(
        "EMEA persona cannot pull APAC rows",
        count_roster({"region": "APAC"}, emea)["count"] == 0,
    )
    r.check(
        "APAC persona cannot pull EMEA rows",
        count_roster({"region": "EMEA"}, apac)["count"] == 0,
    )
    r.check(
        "unknown user fails closed (0 rows)",
        count_roster({}, resolve_scope("intruder@example.com"))["count"] == 0,
    )

    print("== Aggregate / data-agent path (NL2SQL) ==")
    for g in golden:
        if g["kind"] == "region_metrics":
            with connect() as conn:
                tot = conn.execute(
                    "SELECT COUNT(*) FROM fact_employee WHERE region=?", (g["region"],)
                ).fetchone()[0]
                attr = conn.execute(
                    "SELECT COUNT(*) FROM fact_employee WHERE region=? AND attrition_flag=1",
                    (g["region"],),
                ).fetchone()[0]
            r.check(
                f"golden region_metrics reconciles with seed: {g['region']}",
                tot == g["total"] and attr == g["attrition_count"],
            )
            r.skip(f"data-agent attrition answer: {g['region']}", "requires live orchestrator")
        elif g["kind"] == "top_attrition_team":
            with connect() as conn:
                team = conn.execute(
                    "SELECT team FROM fact_employee GROUP BY team "
                    "ORDER BY AVG(attrition_flag) DESC LIMIT 1"
                ).fetchone()[0]
            r.check("golden top_attrition_team reconciles with seed", team == g["team"])
            r.skip("data-agent ranking answer", "requires live orchestrator")

    print("== Routing (prompt -> path) ==")
    known = {"list_roster", "count_roster", "export_roster", "list_org_under"}
    for p in prompts:
        if not all(t in known for t in p["expected_tools"]):
            r.check(f"routing spec references real tools: {p['prompt'][:40]}", False)
        r.skip(f"route: {p['prompt'][:55]}", "requires live orchestrator")

    print(f"\n{r.passed} passed, {r.failed} failed, {r.skipped} skipped")
    return 1 if r.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
