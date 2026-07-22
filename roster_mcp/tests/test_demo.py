"""User-facing demo routing over the local stand-ins."""

from __future__ import annotations

from demo.router import route
from roster_mcp.tools.count import count_roster


def test_headline_questions_use_the_expected_paths(emea_scope):
    cases = [
        ("What's Contoso's attrition rate in EMEA this year?", "aggregate", "region_attrition"),
        ("Which team has the highest attrition?", "aggregate", "top_attrition_team"),
        ("List active employees on the Azure Data team in EMEA.", "deterministic", "list_roster"),
        (
            "Export the full active roster for my region to Excel.",
            "deterministic",
            "export_roster",
        ),
        ("Who rolls up to employee 100001?", "deterministic", "list_org_under"),
        (
            "Show EMEA attrition and list employees who left.",
            "mixed",
            "region_attrition + list_roster",
        ),
    ]

    for question, path, tool in cases:
        result = route(question, emea_scope)
        assert (result["path"], result["tool"]) == (path, tool)


def test_demo_export_applies_filters_and_scope(emea_scope):
    result = route("Export active Azure Data employees in EMEA to CSV.", emea_scope)
    expected = count_roster(
        {"active_status": "Active", "team": "Azure Data", "region": "EMEA"},
        emea_scope,
    )["count"]

    assert result["path"] == "deterministic"
    assert result["row_count"] == expected


def test_demo_inactive_list_uses_terminated_status(emea_scope):
    result = route("List inactive employees in EMEA.", emea_scope)

    assert result["total_matching"] == 322
