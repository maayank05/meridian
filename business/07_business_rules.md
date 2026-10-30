# 07 — Business Rules Catalogue

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Column references are `alias.column` from [SOURCE_HEADERS](../docs/data/SOURCE_HEADERS.md). Column **names** are header-verified. Column **semantics, value domains and grain uniqueness** are assumptions until Phase 2 profiling (verification column).

| Rule ID | Rule | Applies to | Basis | Verify in |
|---|---|---|---|---|
| RULE-01 | Canonical revenue proxy = **"Delivered Merchandise Value (Revenue Proxy)"**: Σ item price of delivered orders by purchase date (D-016, approved). Freight separate; not accounting revenue or profit; refunds/adjustments unavailable; right-censoring flag on recent periods; one definition across SQL/Python/API/DAX | K01, K04, K09–K11, K22, K25 | D-016 | Phase 2 (status value `delivered` exists) |
| RULE-02 | A customer is identified by `customers.customer_unique_id`. `orders.customer_id` links an order to a customers row but is treated as order-scoped | M02, K07–K10, K21 | H-06, public dataset documentation | Phase 2 (cardinality check) |
| RULE-03 | Order grain: one row per `orders.order_id` | fact_orders | Expected | Phase 2 (uniqueness) |
| RULE-04 | Order-item grain: one row per (`order_items.order_id`, `order_items.order_item_id`) | fact_order_items | Expected | Phase 2 |
| RULE-05 | Payment grain: one row per (`order_payments.order_id`, `order_payments.payment_sequential`) | fact_payments | Expected | Phase 2 |
| RULE-06 | Items and payments are **never** joined row-to-row for summed metrics. Each is aggregated to order level first | K18, all revenue joins | Fan-out prevention (`04`) | Phase 4 tests |
| RULE-07 | All monetary values are BRL; no FX conversion is performed | All money KPIs | A-01 (no currency column, H-04) | — (assumption) |
| RULE-08 | Money is stored as DECIMAL and rounded only for display (2 dp, half-up) | All money KPIs | `CLAUDE.md` | Phase 3 |
| RULE-09 | Source timestamps carry no timezone. They are stored as recorded (source-local) and labelled as such; pipeline metadata timestamps are UTC | All time KPIs | A-02, H-07 | Decision in Phase 3 (D-017 to be raised) |
| RULE-10 | Default time basis for commercial KPIs is `orders.order_purchase_timestamp`. Other bases (approval, carrier, delivery) are used only where named | K01–K13 | Demand-timing convention | — |
| RULE-11 | Delivery-metric eligible population: `order_status` = delivered **and** `order_delivered_customer_date` present. Excluded orders are counted in an exclusion report, never silently dropped | K14–K16 | `05` M05 | Phase 2 (status values) |
| RULE-12 | On time = delivered **calendar date** ≤ estimated delivery **calendar date** | K15, K16 | Date-level comparison avoids time-of-day artefacts | Phase 2 (time components) |
| RULE-13 | Products with missing category are reported as category "unknown", not dropped. Categories without English translation keep the Portuguese name and are flagged | M04, K11 | `05` M04 | Phase 2 |
| RULE-14 | Segments with fewer than **30** orders are flagged "small sample"; no ranking claim is made about them | M04, M05 | A-07 | Revisit after profiling |
| RULE-15 | Review metrics use one score per review. Order-level review aggregation (if an order has several reviews) uses the mean and is documented | K13 | Expected | Phase 2 (reviews per order) |
| RULE-16 | Every table, field, KPI, API value and UI element carries a provenance class: `source_observed`, `derived`, `synthetic_assumption`, `forecast`, `scenario_output` | All | `04` | Phase 8–9 tests |
| RULE-17 | Synthetic data lives only in `scenario_*` tables and is never summed into observed totals | M03, M06, M07 | `04` | Phase 3 tests |
| RULE-18 | No metric is called profit, margin or net income unless built on a cost source. Revenue minus incomplete costs is never labelled profit | M06, M07 | Master prompt rule 4 | Terminology review each phase |
| RULE-19 | Relationships between variables are described as associations unless an experimental or quasi-experimental design supports a causal claim | All analysis | Master prompt rule 5 | Report review |
| RULE-20 | Scenario ROI = (incremental benefit − intervention cost) ÷ intervention cost. Net benefit = incremental benefit − intervention cost. ROI is **undefined** when cost = 0. Payback is reported only when benefit accrues over a defined period | Y06, M07 | `05` M07 | Phase 7 hand-calculated tests |
| RULE-21 | Cancellation (an order status) is not treated as a return or refund. No return/refund metric is produced | M04, M06 | H-05 | — |
| RULE-22 | Period comparison uses a prior period of equal length; partially covered months at the data edges are flagged | M01 | `05` M01 | Phase 4 |
| RULE-23 | Months near the end of the dataset are flagged for right-censoring when the KPI depends on later events (delivery, review, repeat purchase) | K01 (if delivered-only), K07, K08, K14–K16 | Data cutoff effect | Phase 2 (date coverage) |
| RULE-24 | Forecast and model evaluation use chronological splits only; features may use only information available at the cutoff | M08, M02 | `05` M08 | Phase 6 leakage tests |
