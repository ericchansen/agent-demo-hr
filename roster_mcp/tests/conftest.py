"""Shared pytest fixtures: a freshly seeded temp SQLite DB + persona scopes."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "data"))


@pytest.fixture(scope="session", autouse=True)
def _local_db(tmp_path_factory):
    import seed_local  # from data/ (added to path above)

    db = tmp_path_factory.mktemp("db") / "test_hr.db"
    exports = tmp_path_factory.mktemp("exports")
    os.environ["ROSTER_DB_PATH"] = str(db)
    os.environ["ROSTER_EXPORT_DIR"] = str(exports)
    seed_local.seed(db)
    yield


@pytest.fixture
def emea_scope():
    from roster_mcp.auth_obo import resolve_scope

    return resolve_scope("emea.hrbp@contoso.com")


@pytest.fixture
def apac_scope():
    from roster_mcp.auth_obo import resolve_scope

    return resolve_scope("apac.hrbp@contoso.com")
