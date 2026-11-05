"""Thin /api/v1 routes: validate input, open a read-only connection, delegate to analytics.dashboard."""

import re
from collections.abc import Iterator
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import Connection, text

from meridian.analytics import dashboard, services
from meridian.analytics.simulator import CampaignScenario
from meridian.reporting.executive import build_report

router = APIRouter()
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def get_conn(request: Request) -> Iterator[Connection]:
    with request.app.state.engine_factory().connect() as conn:
        yield conn


def _period(start_month: str, end_month: str) -> tuple[date, date]:
    for m in (start_month, end_month):
        if not MONTH.match(m):
            raise ValueError("months must use the format YYYY-MM")
    s = date(int(start_month[:4]), int(start_month[5:]), 1)
    e = services.month_end(date(int(end_month[:4]), int(end_month[5:]), 1))
    return s, e


StartQ = Query("2017-01", description="First month (YYYY-MM), inclusive. Default = D-018 window start.")
EndQ = Query("2018-08", description="Last month (YYYY-MM), inclusive. Default = D-018 window end.")


@router.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready", tags=["system"])
def ready(conn: Connection = Depends(get_conn)) -> dict:
    migrations = conn.execute(text("SELECT COUNT(*) FROM schema_version")).scalar_one()
    return {"status": "ready", "schema_migrations": int(migrations)}


@router.get("/metadata", tags=["metadata"])
def metadata(conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.metadata(conn)


@router.get("/overview", tags=["analytics"])
def overview(start_month: str = StartQ, end_month: str = EndQ, conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.overview(conn, *_period(start_month, end_month))


@router.get("/customers", tags=["analytics"])
def customers(start_month: str = StartQ, end_month: str = EndQ, conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.customers(conn, *_period(start_month, end_month))


@router.get("/products", tags=["analytics"])
def products(start_month: str = StartQ, end_month: str = EndQ, conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.products(conn, *_period(start_month, end_month))


@router.get("/operations", tags=["analytics"])
def operations(start_month: str = StartQ, end_month: str = EndQ, conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.operations(conn, *_period(start_month, end_month))


@router.get("/quality", tags=["data quality"])
def quality(conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.quality(conn)


@router.get("/forecast", tags=["forecast"])
def forecast(conn: Connection = Depends(get_conn)) -> dict:
    return dashboard.forecast(conn)


class SimulationRequest(BaseModel):
    start_month: str = Field("2017-01", description="Baseline period start (YYYY-MM)")
    end_month: str = Field("2018-08", description="Baseline period end (YYYY-MM)")
    horizon_months: int = Field(12, ge=1, le=60)
    intervention_cost: Decimal = Field(..., ge=0, max_digits=14, decimal_places=2)
    contribution_margin: Decimal = Field(..., gt=0, le=1, description="SYNTHETIC assumption (share of revenue proxy)")
    downside_uplift: Decimal = Field(..., gt=-1, le=5)
    base_uplift: Decimal = Field(..., gt=-1, le=5)
    upside_uplift: Decimal = Field(..., gt=-1, le=5)


@router.post("/simulator/compare", tags=["decision simulator"])
def simulate(req: SimulationRequest, conn: Connection = Depends(get_conn)) -> dict:
    s, e = _period(req.start_month, req.end_month)
    return dashboard.simulate(
        conn,
        start=s,
        end=e,
        horizon_months=req.horizon_months,
        intervention_cost=req.intervention_cost,
        contribution_margin=req.contribution_margin,
        downside=req.downside_uplift,
        base=req.base_uplift,
        upside=req.upside_uplift,
    )


class CampaignRequest(BaseModel):
    synthetic_spend: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)
    baseline_new_customers: int = Field(..., ge=0)
    baseline_revenue_proxy: Decimal = Field(..., ge=0, max_digits=14, decimal_places=2)
    attributed_share: Decimal = Field(..., ge=0, le=1)
    incremental_lift: Decimal = Field(..., ge=0, le=1)
    contribution_margin: Decimal = Field(..., gt=0, le=1)


@router.post("/simulator/campaign", tags=["decision simulator"])
def campaign(req: CampaignRequest) -> dict:
    return dashboard.campaign(CampaignScenario(**req.model_dump()))


@router.get("/reports/executive", tags=["reports"], response_class=HTMLResponse)
def executive_report(start_month: str = StartQ, end_month: str = EndQ, conn: Connection = Depends(get_conn)) -> str:
    return build_report(conn, *_period(start_month, end_month))[0]
