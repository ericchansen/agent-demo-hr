"""Build a local SQLite database from the committed generated data.

Loads ``fact_employee`` and ``hr_access`` (parquet) into SQLite with indexes
that the Roster MCP tools rely on. Idempotent: tables are replaced each run.

    python data/seed_local.py
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
DEFAULT_DB = DATA_DIR / "hr_local.db"


def db_path() -> Path:
    return Path(os.environ.get("ROSTER_DB_PATH", str(DEFAULT_DB)))


def _load_parquet(name: str) -> pd.DataFrame:
    p = DATA_DIR / f"{name}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing — run `python data/generate_hr.py` first")
    return pd.read_parquet(p)


def seed(path: Path | None = None) -> Path:
    target = path or db_path()
    fact = _load_parquet("fact_employee")
    access = _load_parquet("hr_access")

    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(target) as conn:
        fact.to_sql("fact_employee", conn, if_exists="replace", index=False)
        access.to_sql("hr_access", conn, if_exists="replace", index=False)
        cur = conn.cursor()
        cur.execute("CREATE INDEX IF NOT EXISTS ix_emp_region ON fact_employee(region)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_emp_team ON fact_employee(team)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_emp_mgr ON fact_employee(manager_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_access_upn ON hr_access(user_upn)")
        conn.commit()
    print(f"seeded {len(fact)} employees + {len(access)} access rows -> {target}")
    return target


if __name__ == "__main__":
    seed()
