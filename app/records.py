"""
Fort Records Data Accessor for GadKille.

Loads the master fort dataset from data/records.json (203 forts with coordinates
and trekking details) with a safe fallback to data.sample_records.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from data.sample_records import forts as fallback_forts

RECORDS_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"
_CACHED_RECORDS: Optional[List[Dict[str, Any]]] = None


def load_records() -> List[Dict[str, Any]]:
    """Return all fort records from master records.json or fallback."""
    global _CACHED_RECORDS
    if _CACHED_RECORDS is not None:
        return _CACHED_RECORDS

    if RECORDS_FILE.exists():
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                if isinstance(records, list) and len(records) > 0:
                    _CACHED_RECORDS = records
                    return _CACHED_RECORDS
        except Exception:
            pass

    _CACHED_RECORDS = fallback_forts
    return _CACHED_RECORDS


def search(keyword: str) -> List[Dict[str, Any]]:
    """Search forts by name or district."""
    kw = (keyword or "").lower()
    if not kw:
        return []

    records = load_records()
    results = []
    for fort in records:
        name = str(fort.get("fort_name", "")).lower()
        district = str(fort.get("district", "")).lower()
        if kw in name or kw in district:
            results.append(fort)

    return results


def count_by(category: str) -> Dict[str, int]:
    """Count records by a selected category."""
    records = load_records()
    counts: Dict[str, int] = {}

    for fort in records:
        value = fort.get(category)
        if value is not None:
            counts[value] = counts.get(value, 0) + 1

    return counts


def get_by_id(fort_id: int) -> Optional[Dict[str, Any]]:
    """Get a fort using its position (1-based ID)."""
    records = load_records()
    if 1 <= fort_id <= len(records):
        return records[fort_id - 1]

    return None
