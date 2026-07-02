"""Row-level-security negative tests — out-of-scope rows must NEVER be returned.

These must pass 100%. They are the security money-shot of the whole demo.
"""

from __future__ import annotations

from roster_mcp.auth_obo import resolve_scope
from roster_mcp.tools.count import count_roster
from roster_mcp.tools.list import list_roster


def test_scope_confines_rows_to_region(emea_scope, apac_scope):
    emea = list_roster({}, limit=200, scope=emea_scope)["rows"]
    apac = list_roster({}, limit=200, scope=apac_scope)["rows"]
    assert emea and apac
    assert all(r["region"] == "EMEA" for r in emea)
    assert all(r["region"] == "APAC" for r in apac)


def test_explicit_cross_region_request_returns_nothing(emea_scope):
    # EMEA persona explicitly asks for APAC → scope wins, zero rows leak.
    assert count_roster({"region": "APAC"}, emea_scope)["count"] == 0
    assert list_roster({"region": "APAC"}, limit=200, scope=emea_scope)["rows"] == []


def test_personas_see_disjoint_rowsets(emea_scope, apac_scope):
    emea_ids = {r["employee_id"] for r in list_roster({}, 200, emea_scope)["rows"]}
    apac_ids = {r["employee_id"] for r in list_roster({}, 200, apac_scope)["rows"]}
    assert emea_ids and apac_ids
    assert emea_ids.isdisjoint(apac_ids)


def test_unknown_user_fails_closed():
    scope = resolve_scope("intruder@example.com")
    assert count_roster({}, scope)["count"] == 0
    assert list_roster({}, 200, scope)["rows"] == []
