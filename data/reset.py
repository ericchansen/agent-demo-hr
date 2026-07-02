"""Drop and rebuild the local SQLite database cleanly.

python data/reset.py
"""

from __future__ import annotations

from seed_local import db_path, seed


def reset() -> None:
    target = db_path()
    if target.exists():
        target.unlink()
        print(f"removed {target}")
    seed(target)


if __name__ == "__main__":
    reset()
