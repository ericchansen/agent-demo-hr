"""list_org_under: recursive depth semantics on the manager_id tree."""

from __future__ import annotations

from roster_mcp.db import connect
from roster_mcp.tools.org import list_org_under


def _busiest_emea_manager():
    with connect() as conn:
        row = conn.execute(
            "SELECT manager_id, COUNT(*) c FROM fact_employee "
            "WHERE region='EMEA' AND manager_id IS NOT NULL "
            "GROUP BY manager_id ORDER BY c DESC, manager_id LIMIT 1"
        ).fetchone()
    return int(row["manager_id"]), int(row["c"])


def test_depth_one_is_direct_reports_only(emea_scope):
    mgr, direct = _busiest_emea_manager()
    res = list_org_under(mgr, depth=1, scope=emea_scope)
    assert res["row_count"] == direct
    assert all(r["manager_id"] == mgr for r in res["rows"])


def test_deeper_depth_includes_more(emea_scope):
    mgr, _ = _busiest_emea_manager()
    d1 = list_org_under(mgr, depth=1, scope=emea_scope)["row_count"]
    d_all = list_org_under(mgr, depth=None, scope=emea_scope)["row_count"]
    assert d_all >= d1


def test_org_walk_respects_scope(apac_scope, emea_scope):
    # An EMEA manager has zero in-scope reports when queried by an APAC caller.
    mgr, direct = _busiest_emea_manager()
    assert direct > 0
    assert list_org_under(mgr, depth=None, scope=apac_scope)["row_count"] == 0
    assert list_org_under(mgr, depth=None, scope=emea_scope)["row_count"] >= direct
