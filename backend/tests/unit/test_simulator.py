"""Decision simulator: hand-calculated expectations (RULE-20, US-022)."""

from decimal import Decimal as D

import pytest

from meridian.analytics.simulator import (
    Assumptions,
    CampaignScenario,
    break_even_uplift,
    compare_scenarios,
    evaluate_case,
    sensitivity,
)

# baseline 10,000/month, 1 month, cost 1,000, margin 100% -> uplift 15% gives benefit 1,500
A = Assumptions(
    baseline_monthly_value=D("10000"), horizon_months=1, intervention_cost=D("1000"), contribution_margin=D("1")
)


def test_us022_example_roi_and_net_benefit():
    r = evaluate_case(A, "base", D("0.15"))
    assert r.incremental_revenue_proxy == D("1500")
    assert r.net_benefit == D("500")
    assert r.roi == D("0.5")
    assert r.payback_months == D("1000") / D("1500")
    assert r.provenance == "scenario_output"


def test_contribution_margin_applied_before_roi():
    a = Assumptions(D("10000"), 3, D("1000"), D("0.25"))  # 3 months, 25% assumed margin
    r = evaluate_case(a, "base", D("0.10"))
    assert r.incremental_revenue_proxy == D("3000")  # 10,000 x 10% x 3
    assert r.incremental_contribution == D("750")  # x 25%
    assert r.net_benefit == D("-250")
    assert r.roi == D("-0.25")
    assert break_even_uplift(a) == D("1000") / D("7500")  # 0.1333...


def test_zero_cost_makes_roi_undefined_not_infinite():
    a = Assumptions(D("10000"), 1, D("0"), D("1"))
    r = evaluate_case(a, "base", D("0.05"))
    assert r.roi is None and r.net_benefit == D("500")
    assert break_even_uplift(a) == D("0")


def test_negative_uplift_has_no_payback():
    r = evaluate_case(A, "downside", D("-0.05"))
    assert r.net_benefit == D("-1500") and r.payback_months is None


def test_zero_baseline_break_even_undefined():
    assert break_even_uplift(Assumptions(D("0"), 1, D("100"), D("1"))) is None


def test_scenarios_ordered_and_sensitivity_monotonic():
    cases = compare_scenarios(A, D("0.05"), D("0.10"), D("0.20"))
    assert [c.case for c in cases] == ["downside", "base", "upside"]
    nets = [r.net_benefit for r in sensitivity(A, [D("0"), D("0.05"), D("0.10"), D("0.20")])]
    assert nets == sorted(nets) and nets[0] == D("-1000")
    with pytest.raises(ValueError, match="downside <= base <= upside"):
        compare_scenarios(A, D("0.2"), D("0.1"), D("0.3"))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"intervention_cost": D("-1")}, "intervention_cost"),
        ({"contribution_margin": D("0")}, "contribution_margin"),
        ({"contribution_margin": D("1.5")}, "contribution_margin"),
        ({"horizon_months": 0}, "horizon_months"),
        ({"baseline_monthly_value": D("-5")}, "baseline_monthly_value"),
    ],
)
def test_invalid_assumptions_rejected(kwargs, message):
    a = Assumptions(**{**A.__dict__, **kwargs})
    with pytest.raises(ValueError, match=message):
        evaluate_case(a, "base", D("0.1"))


@pytest.mark.parametrize("uplift", [D("-1"), D("-2"), D("6")])
def test_invalid_uplift_rejected(uplift):
    with pytest.raises(ValueError, match="uplift"):
        evaluate_case(A, "base", uplift)


def test_campaign_scenario_attributed_vs_incremental():
    s = CampaignScenario(
        synthetic_spend=D("2000"),
        baseline_new_customers=400,
        baseline_revenue_proxy=D("50000"),
        attributed_share=D("0.20"),
        incremental_lift=D("0.05"),
        contribution_margin=D("0.30"),
    )
    r = s.evaluate()
    assert r["scenario_cac"] == D("25")  # 2000 / (400 x 20%)
    assert r["attributed_roas"] == D("5")  # 50,000 x 20% / 2000
    assert r["incremental_roas"] == D("1.25")  # 50,000 x 5% / 2000
    assert r["net_benefit"] == D("-1250")  # 2,500 x 30% - 2,000
    assert r["provenance"] == "scenario_output"


def test_campaign_lift_cannot_exceed_attribution():
    with pytest.raises(ValueError, match="incremental_lift <= attributed_share"):
        CampaignScenario(D("100"), 10, D("1000"), D("0.1"), D("0.2"), D("0.3")).evaluate()
