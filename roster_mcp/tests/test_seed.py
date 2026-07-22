"""Local database seed behavior."""

from __future__ import annotations

import sqlite3

from data.seed_local import ensure_seeded, seed
from roster_mcp.server import build_server


def test_seed_loads_committed_csv(tmp_path):
    path = seed(tmp_path / "hr.db")

    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM fact_employee").fetchone()[0] == 5000
        assert conn.execute("SELECT COUNT(*) FROM hr_access").fetchone()[0] == 2


def test_ensure_seeded_reuses_current_seed(tmp_path):
    path = tmp_path / "hr.db"
    first = ensure_seeded(path)
    modified = path.stat().st_mtime_ns
    second = ensure_seeded(path)

    assert first == second == path
    assert path.stat().st_mtime_ns == modified


def test_mcp_server_bootstraps_a_fresh_database(capsys, monkeypatch, tmp_path):
    path = tmp_path / "fresh" / "hr.db"
    monkeypatch.setenv("ROSTER_DB_PATH", str(path))

    build_server()

    assert capsys.readouterr().out == ""
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM fact_employee").fetchone()[0] == 5000
