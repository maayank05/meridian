"""Typed pandas frames built directly from the Olist CSV files (no database).

Used by the independent Python KPI implementation so that SQL views can be reconciled against a separate
code path that starts from the source files. Money is kept as `Decimal` for exact sums.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import cache
from pathlib import Path

import pandas as pd

from meridian.ingestion.pipeline import validate_sources
from meridian.ingestion.timezones import to_utc

FMT = "%Y-%m-%d %H:%M:%S"


@dataclass
class SourceFrames:
    orders: pd.DataFrame
    items: pd.DataFrame
    payments: pd.DataFrame
    reviews: pd.DataFrame
    customers: pd.DataFrame
    products: pd.DataFrame
    translation: pd.DataFrame


@cache
def _utc(local: datetime) -> datetime | None:
    return to_utc(local)[0]


def _ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series.replace("", None), format=FMT)


def load_source_frames(raw_dir: Path) -> SourceFrames:
    f = {lf.source.alias: lf.frame for lf in validate_sources(raw_dir)}
    o = f["orders"].copy()
    for col in ("order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"):
        o[col] = _ts(o[col])
    o["purchase_utc"] = [_utc(t.to_pydatetime()) for t in o["order_purchase_timestamp"]]
    o["delivered_utc"] = [None if pd.isna(t) else _utc(t.to_pydatetime()) for t in o["order_delivered_customer_date"]]
    o["month"] = o["order_purchase_timestamp"].dt.to_period("M")
    items = f["order_items"].copy()
    items["price"] = items["price"].map(Decimal)
    items["freight_value"] = items["freight_value"].map(Decimal)
    pay = f["order_payments"].copy()
    pay["payment_value"] = pay["payment_value"].map(Decimal)
    pay["payment_installments"] = pay["payment_installments"].astype(int)
    rev = f["order_reviews"][["review_id", "order_id", "review_score"]].copy()
    rev["review_score"] = rev["review_score"].astype(int)
    return SourceFrames(o, items, pay, rev, f["customers"], f["products"], f["category_translation"])
