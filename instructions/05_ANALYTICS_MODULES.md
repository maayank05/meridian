# 05 — Ten Analytics and Decision Modules

Every module requires: business question, data requirements, metric definitions, analysis method, API contract, UI, tests, limitations and evidence.

## M01 Executive Intelligence Centre
- Orders, documented revenue, order volume, average order value where valid.
- Monthly trends and period comparisons.
- Category, seller and geography breakdowns where data supports them.
- Contribution/decomposition of observed KPI movement.
- Filters, drill-down and metric definitions.
- Acceptance: every metric traceable to canonical calculation; filters work; no fabricated values.

## M02 Customer Intelligence
- Customer purchase summaries.
- RFM with documented reference date and scoring.
- Repeat purchase, cohort acquisition and retention.
- Segment trends and revenue concentration.
- Optional inactivity model only with defensible label, cutoff and evaluation.
- Acceptance: no future leakage; cohort boundaries tested; customer-level results reconcile to aggregate totals.

## M03 Marketing Performance and Incrementality
- Olist does not provide complete campaign spend/attribution by default.
- Do not claim CAC, ROAS or incremental lift from Olist alone.
- Provide a clearly separated synthetic campaign scenario model only if approved.
- Explain attributed vs incremental outcomes.
- Use experiments/credible causal design before causal claims.
- Acceptance: observed and synthetic measures are separated; assumptions and uncertainty are visible.

## M04 Product and Pricing Intelligence
- Product/category sales, ranking, contribution, review patterns.
- Returns/cancellations only with valid source semantics.
- Pricing elasticity only if suitable price variation and identification assumptions exist.
- Break-even discount and volume sensitivity scenarios can be simulated with labelled assumptions.
- Acceptance: ranking grain and missing categories documented; small samples flagged.

## M05 Operations and Seller Intelligence
- Seller performance, delivery durations, estimated vs actual delivery, delays, geography, review relationships.
- Define eligible order population and denominator for each metric.
- Missing delivery dates and cancelled orders handled explicitly.
- Association is not causation.
- Acceptance: time calculations validated; invalid/missing records reported.

## M06 Financial Intelligence / FP&A
- Documented revenue and payment/order reconciliation.
- Revenue is not profit.
- List unavailable costs explicitly.
- Build optional synthetic budget/COGS/operating cost assumptions in separate scenario tables.
- Actual vs budget only for labelled synthetic budget scenario unless a genuine source exists.
- Acceptance: currency, rounding, refunds and cancellation treatment documented; missing costs never silently set to zero.

## M07 Business Decision Simulator
- Compare baseline and intervention scenarios.
- Inputs: budget, intervention cost, assumed response, expected benefit, downside and upside.
- Outputs: incremental revenue (if defined), incremental contribution, net estimated benefit, ROI and payback where mathematically valid.
- Define ROI formula and denominator explicitly.
- Reject invalid inputs; handle zero cost/undefined cases.
- Scenario outputs are estimates, not realized results.
- Acceptance: calculations live in Python service, not UI; known input/output tests; assumptions visible.

## M08 Forecasting, Statistics and Risk
- Trend summaries, confidence intervals, hypothesis tests where assumptions hold.
- Forecasting using chronological splits and naive/seasonal baseline.
- Appropriate metrics and forecast intervals where supported.
- Anomaly detection with interpretable thresholds/baselines.
- Scikit-learn models only where a valid target exists.
- Acceptance: no leakage; held-out evaluation; model report; uncertainty and limitations shown.

## M09 Business Requirements and Governance
- Business case, stakeholders, BRD/FRD, user stories, acceptance criteria, business rules.
- KPI dictionary, data dictionary, process diagrams, assumptions, RAID, traceability, change and decision logs.
- Acceptance: every major requirement maps to implementation, tests and evidence.

## M10 Automated Executive Reporting
- Reporting period, overview, KPI movements, segment differences, customer/operations findings, quality warnings, forecast/scenario results, follow-up actions and limitations.
- Generate HTML at minimum; PDF only if verified.
- Acceptance: report comes from actual analytical outputs, timestamped, reconciled with app and includes limitations.
