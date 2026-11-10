"""Static demo snapshot helpers and presets (D-024)."""

from decimal import Decimal

from meridian.analytics.presets import CAMPAIGN_PRESETS, PRESET_ORDER, SCENARIO_PRESETS
from meridian.api.routes import CampaignRequest, SimulationRequest
from meridian.snapshot import has_identifier, month_pairs, snapshot_name


def test_month_pairs_cover_every_ordered_period():
    months = ["2017-01", "2017-02", "2017-03"]
    pairs = month_pairs(months)
    assert len(pairs) == 6
    assert ("2017-01", "2017-03") in pairs
    assert all(s <= e for s, e in pairs)
    assert len(month_pairs([f"m{i:02d}" for i in range(26)])) == 351


def test_snapshot_name_matches_frontend_static_path():
    assert snapshot_name("2017-01", "2018-08") == "2017-01_2018-08"


def test_identifier_scan():
    assert has_identifier(b'{"order": "e481f51cbdc54678b7cc49136f2d6af7"}')
    assert has_identifier(b'{"contact": "someone@example.com"}')
    assert not has_identifier(b'{"sha256": "' + b"a" * 64 + b'", "month": "2017-01"}')
    assert not has_identifier(b'{"value": 13181027.13}')


def test_presets_are_valid_requests_and_base_matches_dashboard_defaults():
    assert set(SCENARIO_PRESETS) == set(CAMPAIGN_PRESETS) == set(PRESET_ORDER)
    for preset in PRESET_ORDER:
        SimulationRequest(start_month="2017-01", end_month="2018-08", **SCENARIO_PRESETS[preset])
        CampaignRequest(**CAMPAIGN_PRESETS[preset])
    base = SCENARIO_PRESETS["base"]
    assert (base["intervention_cost"], base["contribution_margin"], base["horizon_months"]) == (
        Decimal("50000"),
        Decimal("0.25"),
        12,
    )
    assert (base["downside_uplift"], base["base_uplift"], base["upside_uplift"]) == (
        Decimal("0"),
        Decimal("0.02"),
        Decimal("0.05"),
    )
    assert CAMPAIGN_PRESETS["base"]["attributed_share"] == Decimal("0.20")


def test_presets_only_differ_in_assumptions():
    for key in ("intervention_cost", "horizon_months"):
        assert len({SCENARIO_PRESETS[p][key] for p in PRESET_ORDER}) == 1
    for key in ("synthetic_spend", "baseline_new_customers", "baseline_revenue_proxy"):
        assert len({CAMPAIGN_PRESETS[p][key] for p in PRESET_ORDER}) == 1
