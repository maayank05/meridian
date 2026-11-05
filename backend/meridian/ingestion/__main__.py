"""CLI: apply migrations, then run the full-refresh pipeline into the development database.

python -m meridian.ingestion [--raw-dir data/raw/olist]
"""

import argparse
import logging
import time
from pathlib import Path

from meridian.config import get_settings
from meridian.db import Role, make_engine
from meridian.ingestion.pipeline import run_pipeline
from meridian.migrations import migrate


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Load the Olist CSV files into MySQL (full refresh).")
    parser.add_argument("--raw-dir", type=Path, default=settings.raw_dir)
    args = parser.parse_args()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if settings.meridian_env == "production":
        raise SystemExit("Refusing to run the destructive full refresh with MERIDIAN_ENV=production")

    engine = make_engine(Role.OWNER)
    applied = migrate(engine)
    print(f"migrations applied: {applied or 'none (up to date)'}")
    started = time.perf_counter()
    result = run_pipeline(engine, args.raw_dir, settings.source_timezone)
    print(f"run {result.run_id} succeeded in {time.perf_counter() - started:.1f}s")
    for table, n in result.row_counts.items():
        print(f"  {table:28} {n:>10,}")
    print(f"  distinct local timestamps by tz status: {result.tz_status_counts}")
    print(f"  step seconds: {result.step_seconds}")
    print("  data-quality checks:")
    for check_id, n in result.quality.items():
        print(f"    {check_id:36} {n:>8,}")


if __name__ == "__main__":
    main()
