from __future__ import annotations

import csv
import os
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence

# NOTE: This module is intentionally simplistic.
# - Reads do full-file scans
# - Updates rewrite the whole file
# - No locking by default (race conditions are part of the lesson)


def ensure_parent_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def read_csv_dicts(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)


def write_csv_dicts(path: str, fieldnames: Sequence[str], rows: Iterable[Dict[str, Any]]) -> None:
    ensure_parent_dir(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            # Everything becomes a string in CSV.
            w.writerow({k: "" if row.get(k) is None else str(row.get(k)) for k in fieldnames})


def next_id_naive(rows: List[Dict[str, str]]) -> int:
    """Naïve ID generation: max(id)+1.

    This is vulnerable to race conditions if two processes compute next_id simultaneously.
    (That's part of the point of the exercise.)
    """
    if not rows:
        return 1
    try:
        return max(int(r["id"]) for r in rows) + 1
    except Exception:
        # If the file is corrupted/malformed, this may crash elsewhere—also part of the lesson.
        return 1


def find_by_id(rows: List[Dict[str, str]], id_value: int) -> Optional[Dict[str, str]]:
    sid = str(id_value)
    for r in rows:
        if r.get("id") == sid:
            return r
    return None


def update_row_by_id(rows: List[Dict[str, str]], id_value: int, updates: Dict[str, Any]) -> bool:
    """Update a row in-memory. Caller is responsible for writing back."""
    sid = str(id_value)
    for r in rows:
        if r.get("id") == sid:
            for k, v in updates.items():
                r[k] = "" if v is None else str(v)
            return True
    return False
