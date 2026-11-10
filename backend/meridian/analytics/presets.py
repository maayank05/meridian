"""Named SYNTHETIC assumption sets for the static demo (D-024).

The hosted demo cannot run the simulator on free-form input, so it ships pre-computed results for these three
presets. Every value is a synthetic assumption, never an observed figure. "base" equals the dashboard's defaults.
Cost, horizon and the campaign baseline are held constant so the presets differ only in their assumptions.
"""

from decimal import Decimal

PRESET_ORDER: tuple[str, ...] = ("cautious", "base", "optimistic")

PRESET_LABELS: dict[str, str] = {"cautious": "Cautious", "base": "Base", "optimistic": "Optimistic"}

SCENARIO_PRESETS: dict[str, dict] = {
    "cautious": {
        "horizon_months": 12,
        "intervention_cost": Decimal("50000"),
        "contribution_margin": Decimal("0.20"),
        "downside_uplift": Decimal("-0.01"),
        "base_uplift": Decimal("0.01"),
        "upside_uplift": Decimal("0.02"),
    },
    "base": {
        "horizon_months": 12,
        "intervention_cost": Decimal("50000"),
        "contribution_margin": Decimal("0.25"),
        "downside_uplift": Decimal("0"),
        "base_uplift": Decimal("0.02"),
        "upside_uplift": Decimal("0.05"),
    },
    "optimistic": {
        "horizon_months": 12,
        "intervention_cost": Decimal("50000"),
        "contribution_margin": Decimal("0.30"),
        "downside_uplift": Decimal("0.01"),
        "base_uplift": Decimal("0.04"),
        "upside_uplift": Decimal("0.08"),
    },
}

CAMPAIGN_PRESETS: dict[str, dict] = {
    "cautious": {
        "synthetic_spend": Decimal("20000"),
        "baseline_new_customers": 4000,
        "baseline_revenue_proxy": Decimal("800000"),
        "attributed_share": Decimal("0.15"),
        "incremental_lift": Decimal("0.01"),
        "contribution_margin": Decimal("0.20"),
    },
    "base": {
        "synthetic_spend": Decimal("20000"),
        "baseline_new_customers": 4000,
        "baseline_revenue_proxy": Decimal("800000"),
        "attributed_share": Decimal("0.20"),
        "incremental_lift": Decimal("0.03"),
        "contribution_margin": Decimal("0.25"),
    },
    "optimistic": {
        "synthetic_spend": Decimal("20000"),
        "baseline_new_customers": 4000,
        "baseline_revenue_proxy": Decimal("800000"),
        "attributed_share": Decimal("0.30"),
        "incremental_lift": Decimal("0.06"),
        "contribution_margin": Decimal("0.30"),
    },
}
