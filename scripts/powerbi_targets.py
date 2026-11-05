"""Write Power BI reconciliation targets (from the live API payload) into powerbi/dax_measures.md.

Usage: python scripts/powerbi_targets.py      (reads meridian_dev with the read-only account)
"""

import re
from datetime import UTC, date, datetime

from meridian.analytics import dashboard
from meridian.config import REPO_ROOT
from meridian.db import Role, make_engine

DOC = REPO_ROOT / "powerbi" / "dax_measures.md"


def main() -> None:
    engine = make_engine(Role.READER)
    with engine.connect() as conn:
        ov = dashboard.overview(conn, date(2017, 1, 1), date(2018, 8, 31))
        ops = dashboard.operations(conn, date(2017, 1, 1), date(2018, 8, 31))
    engine.dispose()
    fmt = {"BRL": lambda v: f"R$ {v:,.2f}", "%": lambda v: f"{v:.4%}"}
    rows = [f"| {k['name']} | {fmt.get(k['unit'], lambda v: f'{v:,.0f}')(k['value'])} |" for k in ov["kpis"]]
    rows.append(f"| On-Time Delivery Rate | {ops['delivery']['on_time_rate']:.4%} |")
    rows.append(f"| Average Review Score | {ops['reviews']['avg_review_score']:.4f} |")
    block = f"Generated {datetime.now(UTC):%Y-%m-%d %H:%M} UTC.\n\n| Measure | Target |\n|---|---:|\n" + "\n".join(rows)
    text = DOC.read_text(encoding="utf-8")
    text = re.sub(
        r"<!-- TARGETS:START -->.*<!-- TARGETS:END -->",
        f"<!-- TARGETS:START -->\n{block}\n<!-- TARGETS:END -->",
        text,
        flags=re.S,
    )
    DOC.write_text(text, encoding="utf-8")
    print(block)


if __name__ == "__main__":
    main()
