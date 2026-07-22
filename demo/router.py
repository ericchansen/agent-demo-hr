"""Local router: send a question down the aggregate path or the roster path.

# ponytail: a keyword heuristic standing in for the Foundry LLM router described
# in orchestrator/instructions.md. It executes the chosen path and returns a
# rendered result. Upgrade path (Phase 3): replace `route` with the live
# orchestrator's tool choice — the two paths and their tool contracts are
# unchanged, so only this classifier is thrown away.

Precedence mirrors the instructions: an explicit row-level verb (list / count /
export / "rolls up to") means the *deterministic* Roster path; otherwise a
fuzzy/aggregate question (a rate, a ranking) means the *data-agent* path.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from roster_mcp.auth_obo import Scope, resolve_scope
from roster_mcp.db import connect
from roster_mcp.tools.count import count_roster
from roster_mcp.tools.export_roster import export_roster
from roster_mcp.tools.list import list_roster
from roster_mcp.tools.org import list_org_under

from . import data_agent


@lru_cache(maxsize=1)
def _known_teams() -> list[str]:
    """Distinct team names, longest first, for substring matching in a question.

    Team names are not sensitive (they are a filter/output column); RLS still
    applies when rows are actually listed.
    """
    with connect() as conn:
        teams = [r[0] for r in conn.execute("SELECT DISTINCT team FROM fact_employee") if r[0]]
    return sorted(teams, key=len, reverse=True)


def _find_region(q: str) -> str | None:
    up = q.upper()
    for r in ("EMEA", "APAC", "LATAM"):
        if r in up:
            return r
    if "NORTH AMERICA" in up or re.search(r"\bNA\b", up):
        return "NA"
    return None


def _find_team(q: str) -> str | None:
    ql = q.lower()
    for team in _known_teams():
        if team.lower() in ql:
            return team
    return None


def _find_manager_id(q: str) -> int | None:
    m = re.search(r"\b(\d{5,6})\b", q)
    return int(m.group(1)) if m else None


def _roster_filters(q: str) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    ql = q.lower()
    team = _find_team(q)
    if team:
        filters["team"] = team
    region = _find_region(q)
    if region:  # can only narrow within the caller's scope; RLS still ANDs its own
        filters["region"] = region
    if re.search(r"\b(inactive|terminated|former)\b", ql) or "who left" in ql:
        filters["active_status"] = "Terminated"
    elif re.search(r"\bactive\b", ql):
        filters["active_status"] = "Active"
    return filters


def _aggregate_kind(ql: str) -> str | None:
    if "highest" in ql or "which team" in ql or "top team" in ql:
        return "top_team"
    if any(k in ql for k in ("attrition", "turnover", " rate", "average", "trend")):
        return "region_rate"
    return None


def _has_explicit_list_intent(ql: str) -> bool:
    return any(
        k in ql for k in ("list", "who are", "who is on", "who left", "roster of", "employees")
    )


def route(question: str, scope: Scope | None = None) -> dict:
    """Classify, execute the chosen path, and return a rendered result dict."""
    scope = scope or resolve_scope()
    ql = question.lower()
    aggregate_kind = _aggregate_kind(ql)
    explicit_list = _has_explicit_list_intent(ql)

    # --- deterministic (row-level) path: explicit verbs win ---
    if "export" in ql or "download" in ql:
        return _do_export(question, scope)
    if any(k in ql for k in ("roll up", "rolls up", "report to", "reports to", "org under")):
        return _do_org(question, scope)
    if "how many" in ql or "count" in ql:
        return _do_count(question, scope)
    if aggregate_kind and explicit_list:
        return _do_mixed(question, scope, aggregate_kind)
    if explicit_list or ("show" in ql and aggregate_kind is None):
        return _do_list(question, scope)

    # --- aggregate (fuzzy) path ---
    if aggregate_kind == "top_team":
        return _do_top_team()
    return _do_region_rate(question)


# --- deterministic handlers -------------------------------------------------


def _do_list(q: str, scope: Scope) -> dict:
    res = list_roster(_roster_filters(q), limit=200, scope=scope)
    return {
        "path": "deterministic",
        "tool": "list_roster",
        "answer": f"{res['total_matching']} employees match (showing {res['row_count']}).",
        "rows": res["rows"],
        "columns": res["columns"],
        "total_matching": res["total_matching"],
    }


def _do_count(q: str, scope: Scope) -> dict:
    res = count_roster(_roster_filters(q), scope)
    return {
        "path": "deterministic",
        "tool": "count_roster",
        "answer": f"{res['count']} employees match.",
    }


def _do_org(q: str, scope: Scope) -> dict:
    mid = _find_manager_id(q)
    if mid is None:
        return {
            "path": "deterministic",
            "tool": "list_org_under",
            "answer": "Which employee? Try e.g. \u201cWho rolls up to 100001?\u201d",
        }
    res = list_org_under(mid, depth=None, scope=scope)
    return {
        "path": "deterministic",
        "tool": "list_org_under",
        "answer": f"{res['row_count']} people roll up under employee {mid}.",
        "rows": res["rows"],
        "columns": res["columns"],
        "total_matching": res["row_count"],
    }


def _do_export(q: str, scope: Scope) -> dict:
    ql = q.lower()
    fmt = "csv" if ("csv" in ql and "excel" not in ql and "xlsx" not in ql) else "xlsx"
    res = export_roster(_roster_filters(q), fmt, scope)
    name = Path(res["path"]).name
    return {
        "path": "deterministic",
        "tool": "export_roster",
        "answer": f"Exported {res['row_count']} rows (sensitive columns excluded).",
        "download": name,
        "row_count": res["row_count"],
    }


def _do_mixed(q: str, scope: Scope, aggregate_kind: str) -> dict:
    aggregate = _do_top_team() if aggregate_kind == "top_team" else _do_region_rate(q)
    roster = _do_list(q, scope)
    return {
        "path": "mixed",
        "tool": f"{aggregate['tool']} + {roster['tool']}",
        "answer": f"{aggregate['answer']} {roster['answer']}",
        "rows": roster["rows"],
        "columns": roster["columns"],
        "total_matching": roster["total_matching"],
    }


# --- aggregate handlers -----------------------------------------------------


def _do_region_rate(q: str) -> dict:
    region = _find_region(q)
    m = data_agent.region_attrition(region)
    label = m["region"]
    return {
        "path": "aggregate",
        "tool": "region_attrition",
        "answer": (
            f"{label} attrition is {m['attrition_rate']:.1%} "
            f"({m['attrition_count']} of {m['total']} employees) over the trailing year."
        ),
    }


def _do_top_team() -> dict:
    t = data_agent.top_attrition_team()
    return {
        "path": "aggregate",
        "tool": "top_attrition_team",
        "answer": f"Highest attrition: {t['team']} (~{t['attrition_rate']:.0%}).",
    }
