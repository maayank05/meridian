"""Decision simulator (FR-026, M07, RULE-20). All outputs are scenario estimates, never observed results.

Definitions (Decimal arithmetic, no intermediate rounding):
    incremental revenue proxy   = baseline monthly revenue proxy x uplift x horizon months
    incremental contribution    = incremental revenue proxy x contribution margin   (margin is a SYNTHETIC assumption)
    net benefit                 = incremental contribution - intervention cost
    ROI                         = net benefit / intervention cost        (undefined when cost = 0)
    payback months              = cost / monthly incremental contribution (undefined when that is <= 0)
    break-even uplift           = cost / (baseline monthly x horizon x margin) (undefined when denominator = 0)
Revenue proxy is not profit (RULE-18): ROI is computed on assumed contribution, never on revenue.
"""

from dataclasses import dataclass
from decimal import Decimal

PROVENANCE = "scenario_output"


@dataclass(frozen=True)
class Assumptions:
    baseline_monthly_value: Decimal  # observed K01 per month (source of the baseline must be stated by the caller)
    horizon_months: int
    intervention_cost: Decimal
    contribution_margin: Decimal  # synthetic assumption, 0 < m <= 1

    def validate(self) -> None:
        if self.baseline_monthly_value < 0:
            raise ValueError("baseline_monthly_value must be >= 0")
        if not 1 <= self.horizon_months <= 60:
            raise ValueError("horizon_months must be between 1 and 60")
        if self.intervention_cost < 0:
            raise ValueError("intervention_cost must be >= 0")
        if not Decimal(0) < self.contribution_margin <= Decimal(1):
            raise ValueError("contribution_margin must be in (0, 1]")


@dataclass(frozen=True)
class CaseResult:
    case: str
    uplift: Decimal
    incremental_revenue_proxy: Decimal
    incremental_contribution: Decimal
    net_benefit: Decimal
    roi: Decimal | None
    payback_months: Decimal | None
    provenance: str = PROVENANCE


def _check_uplift(uplift: Decimal) -> None:
    if uplift <= Decimal(-1) or uplift > Decimal(5):
        raise ValueError("uplift must be greater than -100% and at most +500%")


def evaluate_case(a: Assumptions, case: str, uplift: Decimal) -> CaseResult:
    a.validate()
    _check_uplift(uplift)
    revenue = a.baseline_monthly_value * uplift * a.horizon_months
    contribution = revenue * a.contribution_margin
    net = contribution - a.intervention_cost
    roi = net / a.intervention_cost if a.intervention_cost > 0 else None
    monthly = a.baseline_monthly_value * uplift * a.contribution_margin
    payback = a.intervention_cost / monthly if monthly > 0 else None
    return CaseResult(case, uplift, revenue, contribution, net, roi, payback)


def break_even_uplift(a: Assumptions) -> Decimal | None:
    a.validate()
    denominator = a.baseline_monthly_value * a.horizon_months * a.contribution_margin
    return a.intervention_cost / denominator if denominator > 0 else None


def compare_scenarios(a: Assumptions, downside: Decimal, base: Decimal, upside: Decimal) -> list[CaseResult]:
    if not downside <= base <= upside:
        raise ValueError("expected downside <= base <= upside uplift")
    return [evaluate_case(a, "downside", downside), evaluate_case(a, "base", base), evaluate_case(a, "upside", upside)]


def sensitivity(a: Assumptions, uplifts: list[Decimal]) -> list[CaseResult]:
    return [evaluate_case(a, f"uplift {u}", u) for u in uplifts]


@dataclass(frozen=True)
class CampaignScenario:
    """M03 synthetic campaign scenario (D-015, FR-030). Spend, attribution share and lift are ASSUMPTIONS."""

    synthetic_spend: Decimal
    baseline_new_customers: int  # observed, per scenario period
    baseline_revenue_proxy: Decimal  # observed K01, per scenario period
    attributed_share: Decimal  # share of baseline credited to the campaign by an attribution rule
    incremental_lift: Decimal  # share of baseline that would NOT have happened without the campaign
    contribution_margin: Decimal

    def evaluate(self) -> dict:
        if self.synthetic_spend <= 0:
            raise ValueError("synthetic_spend must be > 0")
        if not (0 <= self.incremental_lift <= self.attributed_share <= 1):
            raise ValueError("expected 0 <= incremental_lift <= attributed_share <= 1")
        if not Decimal(0) < self.contribution_margin <= Decimal(1):
            raise ValueError("contribution_margin must be in (0, 1]")
        attributed_customers = Decimal(self.baseline_new_customers) * self.attributed_share
        attributed_revenue = self.baseline_revenue_proxy * self.attributed_share
        incremental_revenue = self.baseline_revenue_proxy * self.incremental_lift
        net = incremental_revenue * self.contribution_margin - self.synthetic_spend
        return {
            "provenance": PROVENANCE,
            "scenario_cac": self.synthetic_spend / attributed_customers if attributed_customers > 0 else None,
            "attributed_roas": attributed_revenue / self.synthetic_spend,
            "incremental_roas": incremental_revenue / self.synthetic_spend,
            "incremental_revenue_proxy": incremental_revenue,
            "net_benefit": net,
            "roi": net / self.synthetic_spend,
        }
