"""Streaming file export for roster results (CSV / XLSX).

Rows are consumed from a live cursor and written out incrementally — we never
materialize the whole result set in memory.
"""

from __future__ import annotations

import csv
import secrets
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from openpyxl import Workbook


def export_rows(
    rows: Iterable[Sequence],
    columns: Sequence[str],
    fmt: str,
    out_dir: Path,
    name_hint: str = "roster",
) -> tuple[Path, int]:
    """Write ``rows`` to a uniquely named file. Returns (path, row_count)."""
    if fmt not in ("csv", "xlsx"):
        raise ValueError(f"unsupported format: {fmt!r} (use csv or xlsx)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{name_hint}_{ts}_{secrets.token_hex(8)}.{fmt}"

    n = 0
    if fmt == "csv":
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(columns)
            for row in rows:
                writer.writerow([row[c] for c in columns])
                n += 1
    else:  # xlsx — write_only keeps memory flat for large exports
        wb = Workbook(write_only=True)
        ws = wb.create_sheet("roster")
        ws.append(list(columns))
        for row in rows:
            ws.append([row[c] for c in columns])
            n += 1
        wb.save(path)
    return path, n
