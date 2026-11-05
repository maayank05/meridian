"""Profiling scripts on the SYNTHETIC fixture: they run, agree with each other, and emit aggregates only."""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "backend" / "tests" / "fixtures" / "olist"
SCRIPTS = ROOT / "scripts" / "profiling"


def run(script: str, *args: Path) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603 - fixed interpreter and repository script paths
        [sys.executable, "-I", str(SCRIPTS / script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_profile_and_independent_verification_agree(tmp_path):
    out = tmp_path / "profile.json"
    assert run("profile_olist.py", FIXTURE, out).returncode == 0
    profile = json.loads(out.read_text(encoding="utf-8"))
    assert profile["files"]["orders"]["rows"] == 6
    assert profile["files"]["geolocation"]["duplicate_full_rows"] == 1
    assert profile["order_status"]["delivered"]["orders"] == 3
    assert profile["keys"]["order_reviews.review_id"]["unique"] is False
    assert profile["files"]["category_translation"]["bom"] is True
    verify = run("verify_stdlib.py", FIXTURE, out)
    assert verify.returncode == 0, verify.stdout[-500:]
    assert re.search(r"\b(\d+) matched, 0 differed", verify.stdout)


def test_profile_output_contains_no_record_identifiers_or_review_text(tmp_path):
    out = tmp_path / "profile.json"
    run("profile_olist.py", FIXTURE, out)
    text = out.read_text(encoding="utf-8")
    assert not re.search(r"\b[0-9a-f]{32}\b", text)
    assert "chegou" not in text and "recebi" not in text


def test_followups_run_on_fixture(tmp_path):
    out = tmp_path / "followups.json"
    result = run("followups.py", FIXTURE, out)
    assert result.returncode == 0, result.stderr[-500:]
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["review_ids_shared_by_multiple_orders"] == 1
    assert data["shipping_limit_after_2018_12_31_rows"] == 1
