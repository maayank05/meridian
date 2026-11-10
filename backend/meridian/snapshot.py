"""Pure helpers for the static demo snapshot (D-024), shared by scripts/export_static_snapshot.py and its tests."""

import re

# Olist record IDs are 32 hex characters; emails never exist in the source but are checked anyway.
FORBIDDEN = (re.compile(rb"\b[0-9a-f]{32}\b"), re.compile(rb"[\w.+-]+@[\w-]+\.[\w.]+"))


def month_pairs(months: list[str]) -> list[tuple[str, str]]:
    """Every (start, end) pair with start <= end, in coverage order."""
    return [(s, e) for i, s in enumerate(months) for e in months[i:]]


def snapshot_name(start: str, end: str) -> str:
    """File stem shared with frontend/src/services/api.ts (staticPath)."""
    return f"{start}_{end}"


def has_identifier(body: bytes) -> bool:
    """True when a response body contains something that looks like a record ID or an email address."""
    return any(p.search(body) for p in FORBIDDEN)
