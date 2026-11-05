"""Local source time -> UTC (D-017).

A local wall-clock time is:
- 'ok'          : exactly one UTC instant;
- 'ambiguous'   : two UTC instants (repeated hour at DST fall-back) -> UTC is NOT invented, returns None;
- 'nonexistent' : no UTC instant (skipped hour at DST spring-forward) -> returns None.
"""

from datetime import UTC, datetime
from typing import Literal
from zoneinfo import ZoneInfo

TzStatus = Literal["ok", "ambiguous", "nonexistent"]


def to_utc(local: datetime, tz_name: str = "America/Sao_Paulo") -> tuple[datetime | None, TzStatus]:
    if local.tzinfo is not None:
        raise ValueError("expected a naive local datetime")
    tz = ZoneInfo(tz_name)
    first = local.replace(tzinfo=tz, fold=0).astimezone(UTC)
    second = local.replace(tzinfo=tz, fold=1).astimezone(UTC)
    if first == second:
        return first.replace(tzinfo=None), "ok"
    roundtrips = [u.astimezone(tz).replace(tzinfo=None) == local for u in (first, second)]
    if all(roundtrips):
        return None, "ambiguous"
    return None, "nonexistent"
