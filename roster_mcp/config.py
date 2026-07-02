"""Local configuration for the Roster MCP server.

All values have safe local-dev defaults and can be overridden by environment
variables (see ``.env.example``). No secrets live here.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def db_path() -> Path:
    return Path(os.environ.get("ROSTER_DB_PATH", str(DATA_DIR / "hr_local.db")))


def export_dir() -> Path:
    return Path(os.environ.get("ROSTER_EXPORT_DIR", str(REPO_ROOT / "exports")))


def dev_upn() -> str:
    """Mock signed-in user for the dev identity shim (see auth_obo.py)."""
    return os.environ.get("ROSTER_DEV_UPN", "emea.hrbp@contoso.com")


# Hard cap on rows returned inline by list_roster, for context safety.
LIST_ROW_CAP = 200
