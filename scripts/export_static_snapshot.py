"""Export a static snapshot of the API for the hosted demo (D-024).

Usage: python scripts/export_static_snapshot.py [--out frontend/public/snapshot]

Calls the real FastAPI app in-process with the READ-ONLY account against meridian_dev and writes each response
byte for byte, so the demo shows exactly what the local API returns. Covers every month pair in the metadata
coverage list, the three simulator presets (meridian.analytics.presets) and the executive report.
Writes into a temporary folder, scans it for identifiers, then replaces the target. Exits non-zero on failure.
"""

import argparse
import json
import shutil
import sys
import time
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from meridian.analytics.presets import CAMPAIGN_PRESETS, PRESET_LABELS, PRESET_ORDER, SCENARIO_PRESETS
from meridian.api.main import create_app
from meridian.snapshot import has_identifier, month_pairs, snapshot_name

ANALYTICS = ("overview", "customers", "products", "operations")


def _plain(values: dict) -> dict:
    """Decimals as strings for JSON request bodies and the manifest."""
    return {k: (str(v) if isinstance(v, Decimal) else v) for k, v in values.items()}


def _write(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def _commit() -> str:
    """Short commit of the working tree, read from .git without running a subprocess."""
    head = Path(".git/HEAD")
    if not head.exists():
        return "unknown"
    ref = head.read_text().strip()
    if ref.startswith("ref: "):
        ref_file = Path(".git") / ref[5:]
        ref = ref_file.read_text().strip() if ref_file.exists() else "unknown"
    return ref[:7]


def export(out: Path) -> int:
    client = TestClient(create_app())
    tmp = out.with_name(out.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    failures: dict[str, int] = {}

    def save(rel: str, response) -> None:
        if response.status_code != 200:
            failures[rel] = response.status_code
        _write(tmp / rel, response.content)

    started = time.perf_counter()
    meta = client.get("/api/v1/metadata")
    if meta.status_code != 200:
        print(f"metadata failed: HTTP {meta.status_code}", file=sys.stderr)
        return 1
    _write(tmp / "metadata.json", meta.content)
    months = [m["month"][:7] for m in meta.json()["month_coverage"]]
    for name in ("quality", "forecast"):
        save(f"{name}.json", client.get(f"/api/v1/{name}"))
    for preset in PRESET_ORDER:
        body = _plain(CAMPAIGN_PRESETS[preset])
        save(f"campaign/{preset}.json", client.post("/api/v1/simulator/campaign", json=body))

    pairs = month_pairs(months)
    for n, (start, end) in enumerate(pairs, 1):
        stem = snapshot_name(start, end)
        query = f"?start_month={start}&end_month={end}"
        for ep in ANALYTICS:
            save(f"{ep}/{stem}.json", client.get(f"/api/v1/{ep}{query}"))
        for preset in PRESET_ORDER:
            body = {"start_month": start, "end_month": end, **_plain(SCENARIO_PRESETS[preset])}
            save(f"simulator/{preset}/{stem}.json", client.post("/api/v1/simulator/compare", json=body))
        save(f"reports/{stem}.html", client.get(f"/api/v1/reports/executive{query}"))
        if n % 25 == 0 or n == len(pairs):
            print(f"{n}/{len(pairs)} periods ({time.perf_counter() - started:.0f} s)", flush=True)

    manifest = {
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_commit": _commit(),
        "months": months,
        "periods": len(pairs),
        "presets": [
            {
                "id": p,
                "label": PRESET_LABELS[p],
                "scenario": _plain(SCENARIO_PRESETS[p]),
                "campaign": _plain(CAMPAIGN_PRESETS[p]),
            }
            for p in PRESET_ORDER
        ],
        "non_200": failures,
    }
    _write(tmp / "manifest.json", json.dumps(manifest, indent=2).encode())

    files = [f for f in tmp.rglob("*") if f.is_file()]
    leaks = [str(f.relative_to(tmp)) for f in files if has_identifier(f.read_bytes())]
    if leaks:
        print(f"identifier-like strings in {len(leaks)} files, snapshot not written: {leaks[:5]}", file=sys.stderr)
        shutil.rmtree(tmp)
        return 1

    shutil.rmtree(out, ignore_errors=True)
    tmp.rename(out)
    files = sum(1 for f in out.rglob("*") if f.is_file())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"wrote {files} files, {size / 1e6:.1f} MB, {len(pairs)} periods, {len(failures)} non-200 responses")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("frontend/public/snapshot"))
    return export(parser.parse_args().out)


if __name__ == "__main__":
    sys.exit(main())
