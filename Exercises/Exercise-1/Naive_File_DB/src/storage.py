from __future__ import annotations

import csv
import os
from typing import Dict, List, Optional, Sequence, Tuple

# Storage notes:
# - This is intentionally naive for the exercise.
# - Updates rewrite the entire file.
# - No locking (race conditions possible).
# - No schema validation beyond headers.


def ensure_file(path: str, headers: Sequence[str]) -> None:
    """Create a CSV file with headers if it doesn't exist."""
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(list(headers))


def read_all(path: str) -> List[Dict[str, str]]:
    """Read entire CSV into a list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)


def write_all(path: str, headers: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    """Rewrite entire CSV file."""
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(headers))
        w.writeheader()
        for row in rows:
            w.writerow(row)
    # NOTE: os.replace is atomic on most platforms for same filesystem.
    os.replace(tmp, path)


def next_id(path: str) -> int:
    """Return next integer id by scanning all rows (slow, race-prone)."""
    rows = read_all(path)
    max_id = 0
    for row in rows:
        try:
            max_id = max(max_id, int(row.get("id", "0") or "0"))
        except ValueError:
            # Corrupt row -> ignore for max id (also a form of pain)
            pass
    return max_id + 1


def append_row(path: str, headers: Sequence[str], row: Dict[str, str]) -> None:
    """Append a row. Assumes file exists with matching headers."""
    ensure_file(path, headers)
    # NOTE: Append is not atomic across processes and can interleave writes.
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(headers))
        w.writerow(row)


def find_by_id(path: str, id_value: int) -> Optional[Dict[str, str]]:
    """Linear scan to find first row with id == id_value."""
    target = str(id_value)
    for row in read_all(path):
        if row.get("id") == target:
            return row
    return None


def update_by_id(path: str, headers: Sequence[str], id_value: int, changes: Dict[str, str]) -> bool:
    """Update a row by id by rewriting the entire file. Returns True if updated."""
    target = str(id_value)
    rows = read_all(path)
    updated = False
    new_rows: List[Dict[str, str]] = []
    for row in rows:
        if row.get("id") == target and not updated:
            row = dict(row)
            row.update(changes)
            updated = True
        new_rows.append(row)
    if updated:
        write_all(path, headers, new_rows)
    return updated
