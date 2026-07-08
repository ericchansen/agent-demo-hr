"""Aggregate answers (the data-agent path) computed from the local seed.

# ponytail: stands in for the Fabric data agent (NL2SQL). It computes the
# aggregate answers directly from the SQLite seed so the demo runs with zero
# cloud. Phase 3 swaps in the real Foundry-wired agent; the numbers this must
# reproduce are pinned by orchestrator/eval/golden.jsonl (see _selfcheck).
#
# Aggregate stats are workforce-level (a rate, a ranking) — not row-level PII —
# so, like the eval, they are computed over the whole workforce, not RLS-scoped.
"""

from __future__ import annotations

from roster_mcp.db import connect


def region_attrition(region: str | None) -> dict:
    """Attrition rate for one region, or overall when region is None."""
    where = "WHERE region = ?" if region else ""
    where_attr = f"{where} AND attrition_flag = 1" if region else "WHERE attrition_flag = 1"
    params = (region,) if region else ()
    with connect() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM fact_employee {where}", params).fetchone()[0]
        attr = conn.execute(
            f"SELECT COUNT(*) FROM fact_employee {where_attr}", params
        ).fetchone()[0]
    rate = attr / total if total else 0.0
    return {
        "region": region or "overall",
        "total": total,
        "attrition_count": attr,
        "attrition_rate": rate,
    }


def top_attrition_team() -> dict:
    """The single team with the highest attrition rate."""
    with connect() as conn:
        team, rate = conn.execute(
            "SELECT team, AVG(attrition_flag) AS r FROM fact_employee "
            "GROUP BY team ORDER BY r DESC LIMIT 1"
        ).fetchone()
    return {"team": team, "attrition_rate": rate}


def _selfcheck() -> None:
    """Assert the aggregate numbers match the committed golden seed."""
    import json
    from pathlib import Path

    golden = Path(__file__).resolve().parents[1] / "orchestrator" / "eval" / "golden.jsonl"
    rows = [json.loads(x) for x in golden.read_text(encoding="utf-8").splitlines() if x.strip()]
    for g in rows:
        if g["kind"] == "region_metrics":
            m = region_attrition(g["region"])
            assert m["total"] == g["total"], (g["region"], m, g)
            assert m["attrition_count"] == g["attrition_count"], (g["region"], m, g)
            assert round(m["attrition_rate"], 4) == g["attrition_rate"], (g["region"], m, g)
        elif g["kind"] == "top_attrition_team":
            assert top_attrition_team()["team"] == g["team"], top_attrition_team()
    print("data_agent OK: region metrics + top team match golden.jsonl")


if __name__ == "__main__":
    _selfcheck()
