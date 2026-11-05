"""API tests on the MySQL fixture (meridian_test): contracts, values, validation, errors, CORS (FR-002/003, NFR-007)."""

import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine

from meridian.api.main import create_app
from tests import expected as E

pytestmark = pytest.mark.mysql


@pytest.fixture(scope="module")
def client(engine, loaded):
    with TestClient(create_app(lambda: engine)) as c:
        yield c


def test_health_and_ready(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/api/v1/ready").json() == {"status": "ready", "schema_migrations": 6}


def test_overview_values_match_canonical_kpis(client):
    r = client.get("/api/v1/overview")
    assert r.status_code == 200 and r.headers["X-Request-ID"]
    body = r.json()
    k = {x["id"]: x for x in body["kpis"]}
    assert k["K01"]["value"] == float(E.K01_TOTAL) and k["K01"]["provenance"] == "derived"
    assert k["K01"]["name"] == "Delivered Merchandise Value (Revenue Proxy)"
    assert k["K03"]["value"] == 3 and k["K21"]["value"] == 2
    assert k["K04"]["value"] == round(float(E.K01_TOTAL) / 3, 2)
    assert (body["prior_period"]["start"], body["prior_period"]["end"]) == ("2015-05-01", "2016-12-31")  # 20 months
    assert body["prior_period"]["comparable"] is False  # mostly outside the data: never compared
    assert all(x["change"] is None for x in body["kpis"])
    assert len(body["monthly"]) == 20 and body["months_flagged"] == []


def test_period_including_flagged_months(client):
    body = client.get("/api/v1/overview", params={"start_month": "2016-09", "end_month": "2018-10"}).json()
    assert "2016-11-01" in body["months_flagged"] and "2018-10-01" in body["months_flagged"]
    flags = {m["month"]: m["coverage_flag"] for m in body["monthly"]}
    assert flags["2016-11-01"] == "low_coverage" and flags["2018-09-01"] == "incomplete_cutoff"


@pytest.mark.parametrize(
    ("params", "fragment"),
    [
        ({"start_month": "2018-05", "end_month": "2017-01"}, "start must not be after end"),
        ({"start_month": "2015-01", "end_month": "2017-01"}, "within the data coverage"),
        ({"start_month": "2017-13", "end_month": "2018-01"}, "YYYY-MM"),
        ({"start_month": "2017-01'; DROP TABLE x;--", "end_month": "2018-01"}, "YYYY-MM"),
    ],
)
def test_invalid_periods_return_envelope(client, params, fragment):
    r = client.get("/api/v1/overview", params=params)
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "invalid_input" and fragment in err["message"] and err["request_id"]


def test_customers_products_operations(client):
    c = client.get("/api/v1/customers").json()
    assert c["repeat_rate"] == E.REPEAT_DEFAULT_WINDOW
    assert {x["cohort_month"] for x in c["cohorts"]} == {"2017-03-01", "2017-10-01"}
    mar = next(x for x in c["cohorts"] if x["cohort_month"] == "2017-03-01")
    assert mar["observable_months"] == 17  # 2017-03 -> 2018-08
    rates = {r["months_since_first"]: r["active_customers"] for r in mar["retention"]}
    assert rates[11] == 1 and rates[1] == 0 and 18 not in rates  # observed zero vs unobservable
    p = client.get("/api/v1/products").json()
    assert {x["category"]: x["delivered_merchandise_value"] for x in p["categories"]} == {
        k: float(v) for k, v in E.CATEGORY_VALUE.items()
    }
    assert all(x["small_sample"] for x in p["categories"])  # fewer than 30 orders each
    o = client.get("/api/v1/operations").json()
    assert o["delivery"]["excluded_ambiguous_time"] == 1
    assert o["delivery"]["avg_lead_time_days"] == pytest.approx(E.DELIVERY["avg_lead_time_seconds"] / 86400, abs=1e-6)
    assert o["delivery"]["on_time_rate"] == 1.0
    assert o["reviews"]["avg_review_score"] == E.REVIEWS["avg_review_score"]


def test_quality_and_metadata(client):
    q = client.get("/api/v1/quality").json()
    assert q["latest_run"]["run_id"] and len(q["files"]) == 9
    assert {c["check_id"]: c["affected_rows"] for c in q["checks"]} == E.QUALITY
    m = client.get("/api/v1/metadata").json()
    assert m["default_period"] == {"start": "2017-01-01", "end": "2018-08-31"} and m["currency"] == "BRL"
    assert "scenario_output" in m["provenance_classes"]


def test_forecast_on_fixture_is_valid_json_with_undefined_mape(client):
    r = client.get("/api/v1/forecast")  # fixture months are mostly zero -> MAPE undefined
    assert r.status_code == 200
    assert "Infinity" not in r.text and "NaN" not in r.text
    body = r.json()
    assert body["provenance"] == "forecast" and all(e["mape"] is None for e in body["evaluations"])


def test_simulator_compare(client):
    body = {
        "intervention_cost": "100.00",
        "contribution_margin": "0.5",
        "horizon_months": 12,
        "downside_uplift": "0",
        "base_uplift": "0.1",
        "upside_uplift": "0.2",
    }
    r = client.post("/api/v1/simulator/compare", json=body).json()
    baseline = float(E.K01_TOTAL) / 20  # mean over the 20 default-window months
    assert r["baseline"]["monthly_delivered_merchandise_value"] == pytest.approx(baseline, abs=0.01)
    base = next(c for c in r["cases"] if c["case"] == "base")
    assert base["incremental_revenue_proxy"] == pytest.approx(baseline * 0.1 * 12, abs=0.01)
    assert base["net_benefit"] == pytest.approx(baseline * 0.1 * 12 * 0.5 - 100, abs=0.01)
    assert r["provenance"] == "scenario_output" and r["assumptions"]["provenance"] == "synthetic_assumption"
    assert r["break_even_uplift"] == pytest.approx(100 / (baseline * 12 * 0.5), rel=1e-9)


@pytest.mark.parametrize(
    "patch",
    [
        {"intervention_cost": "-1"},
        {"contribution_margin": "0"},
        {"contribution_margin": "1.5"},
        {"base_uplift": "-1"},
        {"horizon_months": 0},
        {"downside_uplift": "0.5"},
    ],
)
def test_simulator_rejects_invalid_input(client, patch):
    body = {
        "intervention_cost": "100",
        "contribution_margin": "0.5",
        "horizon_months": 12,
        "downside_uplift": "0",
        "base_uplift": "0.1",
        "upside_uplift": "0.2",
    } | patch
    r = client.post("/api/v1/simulator/compare", json=body)
    assert r.status_code == 422 and r.json()["error"]["code"] in {"validation_error", "invalid_input"}


def test_campaign_scenario(client):
    body = {
        "synthetic_spend": "2000",
        "baseline_new_customers": 400,
        "baseline_revenue_proxy": "50000",
        "attributed_share": "0.2",
        "incremental_lift": "0.05",
        "contribution_margin": "0.3",
    }
    r = client.post("/api/v1/simulator/campaign", json=body).json()
    assert (r["scenario_cac"], r["attributed_roas"], r["incremental_roas"]) == (25.0, 5.0, 1.25)
    assert r["provenance"] == "scenario_output" and "No observed marketing data" in r["disclaimer"]


def test_cors_allows_only_configured_origin(client):
    ok = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
    bad = client.get("/api/v1/health", headers={"Origin": "https://evil.example"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in bad.headers


def test_database_down_returns_503_without_details(caplog):
    dead = create_engine(
        URL.create("mysql+pymysql", username="unreachable", host="127.0.0.1", port=1),
        connect_args={"connect_timeout": 2},
    )
    with (
        TestClient(create_app(lambda: dead), raise_server_exceptions=False) as c,
        caplog.at_level(logging.INFO, logger="meridian.api"),
    ):
        assert c.get("/api/v1/health").status_code == 200  # liveness does not need the database
        r = c.get("/api/v1/ready")
    assert r.status_code == 503 and r.json()["error"]["code"] == "database_unavailable"
    text_body = r.text.lower()
    assert "unreachable" not in text_body and "traceback" not in text_body and "127.0.0.1" not in text_body
    assert "unreachable" not in caplog.text  # connection details never logged
    dead.dispose()


def test_executive_report_matches_api(client, engine):
    from datetime import date  # noqa: PLC0415

    from meridian.reporting.executive import build_report  # noqa: PLC0415

    with engine.connect() as conn:
        doc, payloads = build_report(conn, date(2017, 1, 1), date(2018, 8, 31))
    assert payloads["overview"]["kpis"] == client.get("/api/v1/overview").json()["kpis"]
    assert payloads["products"] == client.get("/api/v1/products").json()
    assert "R$ 376.25" in doc and "not accounting revenue, not profit" in doc and "Generated " in doc
    assert "Limitations" in doc and "data:image/png;base64," in doc
    r = client.get("/api/v1/reports/executive")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html") and "R$ 376.25" in r.text


def test_change_computed_only_for_comparable_prior_period(client):
    body = client.get("/api/v1/overview", params={"start_month": "2018-02", "end_month": "2018-02"}).json()
    assert body["prior_period"] == {"start": "2018-01-01", "end": "2018-01-31", "comparable": True, "note": None}
    k01 = next(x for x in body["kpis"] if x["id"] == "K01")
    assert (k01["value"], k01["prior_value"], k01["change"]) == (75.25, 0.0, None)  # change vs zero is undefined
    body = client.get("/api/v1/overview", params={"start_month": "2017-11", "end_month": "2017-11"}).json()
    assert body["prior_period"]["comparable"] is True
    k01 = next(x for x in body["kpis"] if x["id"] == "K01")
    assert (k01["value"], k01["prior_value"], k01["change"]) == (0.0, 50.5, -1.0)  # order-5 delivered in 2017-10
