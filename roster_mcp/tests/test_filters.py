"""Filter correctness + the SQL-injection boundary."""

from __future__ import annotations

import pytest

from roster_mcp.db import connect
from roster_mcp.tools.count import count_roster
from roster_mcp.tools.list import list_roster
from roster_mcp.tools.schema import get_roster_schema


def _direct_count(sql: str, params: list) -> int:
    with connect() as conn:
        return int(conn.execute(sql, params).fetchone()[0])


def test_count_matches_direct_sql(emea_scope):
    got = count_roster({"team": "Azure Data", "active_status": "Active"}, emea_scope)["count"]
    expected = _direct_count(
        "SELECT COUNT(*) FROM fact_employee "
        "WHERE region='EMEA' AND team='Azure Data' AND active_status='Active'",
        [],
    )
    assert got == expected > 0


def test_list_rows_all_match_filter_and_scope(emea_scope):
    res = list_roster({"team": "Azure Data"}, limit=200, scope=emea_scope)
    assert res["rows"], "expected some rows"
    assert all(r["region"] == "EMEA" and r["team"] == "Azure Data" for r in res["rows"])


def test_list_respects_row_cap(emea_scope):
    res = list_roster({}, limit=10_000, scope=emea_scope)
    assert res["row_count"] <= 200  # config.LIST_ROW_CAP
    assert res["truncated"] is True


def test_schema_exposes_every_supported_discovery_column(emea_scope):
    result = get_roster_schema(emea_scope)

    assert set(result) == {"region", "team", "org", "office_location", "department"}
    assert result["department"]


def test_unknown_filter_column_rejected(emea_scope):
    with pytest.raises(ValueError, match="unknown filter column"):
        count_roster({"totally_not_a_column": "x"}, emea_scope)


def test_injection_input_is_a_literal(emea_scope):
    # A classic injection payload must be treated as an ordinary string value.
    payload = "Azure Data'; DROP TABLE fact_employee; --"
    res = count_roster({"team": payload}, emea_scope)
    assert res["count"] == 0  # no team literally named that
    # Table must still be intact and queryable afterwards.
    assert count_roster({"active_status": "Active"}, emea_scope)["count"] > 0
