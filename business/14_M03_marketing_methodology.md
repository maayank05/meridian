# 14 — M03 Marketing Performance: Methodology and Limitations

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31 · Decision: D-015 (option A + B) · Requirement: FR-030

> **No observed marketing data exists in this project.** The Olist files contain no marketing spend, campaigns, channels, impressions, clicks, sessions, attribution touchpoints or experiment assignments (header evidence H-05). Every marketing number MERIDIAN shows is **synthetic** or a **scenario output**.

## 1. What can and cannot be measured

| Question | Measurable from Olist? | Why | What MERIDIAN shows instead |
|---|---|---|---|
| How many new customers per month? | **Yes** (derived) | First delivered order per `customer_unique_id` | Observed new-customer counts (K21/K08 basis) |
| Retention of acquired customers? | **Yes** (derived) | Cohorts | K08 |
| Customer acquisition cost (CAC)? | **No** (U03) | No spend | Scenario CAC (Y02) from synthetic spend |
| Return on ad spend (ROAS)? | **No** (U04) | No spend, no attribution | Scenario ROAS (Y03) |
| Incremental lift of a campaign? | **No** (U05) | No randomised or quasi-experimental assignment | Assumed-lift scenarios (Y04) with ranges |
| Which channel drove an order? | **No** | No touchpoints | Not shown |

## 2. Attributed vs incremental outcomes
- **Attributed outcome:** revenue or customers *credited* to a campaign by a rule (last-click, first-touch, data-driven). Attribution distributes credit. It does **not** prove the campaign caused the outcome, because many customers would have bought anyway.
- **Incremental outcome:** the difference between what happened *with* the campaign and what would have happened *without* it (the counterfactual). Measuring it requires a credible comparison group, such as a randomised holdout, geo experiment, or a quasi-experimental design with stated assumptions.
- **Why it matters:** ROAS on attributed revenue usually overstates value. A campaign can show high attributed ROAS and near-zero incremental lift.

## 3. Synthetic campaign scenario model (built in Milestone B: `CampaignScenario` in `backend/meridian/analytics/simulator.py`)

> **Implementation note (CR-005):** spend, attribution share, incremental lift and margin are entered explicitly as assumptions instead of drawn by a seeded random generator. The outputs are scenario CAC, attributed ROAS vs incremental ROAS, incremental revenue proxy and net benefit, all labelled `scenario_output`.

Purpose: let stakeholders explore how spend, attribution assumptions and lift assumptions change CAC, ROAS and net benefit. It is **not** a claim about real performance.

| Element | Design |
|---|---|
| Storage | `scenario_marketing_*` tables only (RULE-17) |
| Channels | Illustrative set (e.g. search, social, email, affiliates), each labelled synthetic |
| Spend generator (Y01) | Seeded random generator; monthly spend per channel drawn around a user-set budget with documented distribution and variance; seed stored with every run |
| Attribution assumption | User-set share of observed new customers/revenue credited to each channel (sums ≤ 100%) |
| Lift assumption | User-set incremental % with low/base/high range; default base case is conservative |
| Observed inputs | Monthly observed K01 and new-customer counts (baseline only) |
| Outputs | Y02 Scenario CAC, Y03 Scenario ROAS, Y04 Scenario incremental revenue, Y06 ROI/net benefit, for base/upside/downside |
| Validation | Same seed → identical output; attribution shares ≤ 100%; negative spend rejected; zero spend → CAC/ROAS undefined |
| Labelling | Every value: Synthetic or Scenario badge; page banner per the notice at the top of this document; exports carry the label |

Exact distributions, defaults and parameter ranges are documented with rationale when the generator is built, and recorded as a decision before implementation.

## 4. Data required to replace the synthetic model with real measurement
1. Marketing spend by channel, campaign and date.
2. Campaign identifiers linked to orders or sessions (UTM or click IDs).
3. Touchpoint or session data for attribution.
4. Experimental design for incrementality: randomised holdouts or geo-split tests with pre-registered metrics; alternatively a documented quasi-experimental design (difference-in-differences, synthetic control) with its assumptions tested.
5. Cost data for contribution-based ROI (COGS, fulfilment, fees).

## 5. Prohibited claims
- Calling any M03 value "actual", "observed" or "Northstar's CAC/ROAS".
- Causal language ("the campaign increased sales") from attributed or synthetic numbers.
- Combining synthetic spend with observed revenue into a single unlabelled metric.

## 6. Uncertainty presentation
Always show the base, upside and downside cases side by side, the full assumption list, and a sensitivity view showing how outputs change as the lift assumption varies across its range.
