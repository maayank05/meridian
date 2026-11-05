"""Write the executive report to reports/generated/executive_report.html (gitignored).

Usage: python scripts/executive_report.py [--start 2017-01] [--end 2018-08]
"""

import argparse
from datetime import date

from meridian.analytics.services import month_end
from meridian.config import REPO_ROOT
from meridian.db import Role, make_engine
from meridian.reporting.executive import build_report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2017-01")
    ap.add_argument("--end", default="2018-08")
    a = ap.parse_args()
    start = date(int(a.start[:4]), int(a.start[5:]), 1)
    end = month_end(date(int(a.end[:4]), int(a.end[5:]), 1))
    engine = make_engine(Role.READER)
    with engine.connect() as conn:
        doc, _ = build_report(conn, start, end)
    engine.dispose()
    out = REPO_ROOT / "reports" / "generated" / "executive_report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"written {out.relative_to(REPO_ROOT)} ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
