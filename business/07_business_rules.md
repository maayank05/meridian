# 07 — Business Rules Catalogue

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Column references are `alias.column` from [SOURCE_HEADERS](../docs/data/SOURCE_HEADERS.md). Column **names** are header-verified. The verification column records the Phase 2 profiling result ([PROFILING_REPORT](../docs/data/PROFILING_REPORT.md)).

| Rule ID | Rule | Applies to | Basis | Verify in |
|---|---|---|---|---|
| RULE-01 | Canonical revenue proxy = **"Delivered Merchandise Value (Revenue Proxy)"**: Σ item price of delivered orders by purchase date (D-016, approved). Freight separate; not accounting revenue or profit; refunds/adjustments unavailable; right-censoring flag on recent periods; one definition across SQL/Python/API/DAX | K01, K04, K09–K11, K22, K25 | D-016 | **Verified Phase 2**: `delivered` exists (96,478 orders) |
| RULE-02 | A customer is identified by `customers.customer_unique_id`. `orders.customer_id` links an order to a customers row but is treated as order-scoped | M02, K07–K10, K21 | H-06, public dataset documentation | **Verified Phase 2**: customer_id 1:1 with orders; 2,997 people have >1 customer_id |
| RULE-03 | Order grain: one row per `orders.order_id` | fact_orders | Expected | **Verified Phase 2**: order_id unique |
| RULE-04 | Order-item grain: one row per (`order_items.order_id`, `order_items.order_item_id`) | fact_order_items | Expected | **Verified Phase 2**: key unique; order_item_id contiguous 1..n |
| RULE-05 | Payment grain: one row per (`order_payments.order_id`, `order_payments.payment_sequential`) | fact_payments | Expected | **Verified Phase 2**: key unique; 80 orders have sequence gaps (DQ-18) |
| RULE-06 | Items and payments are **never** joined row-to-row for summed metrics. Each is aggregated to order level first | K18, all revenue joins | Fan-out prevention (`04`) | Phase 4 tests |
| RULE-07 | All monetary values are BRL; no FX conversion is performed | All money KPIs | A-01 (no currency column, H-04) | — (assumption) |
| RULE-08 | Money is stored as DECIMAL and rounded only for display (2 dp, half-up) | All money KPIs | `CLAUDE.md` | Phase 3 |
| RULE-09 | Source timestamps carry no timezone. They are stored as recorded (source-local) and labelled as such; pipeline metadata timestamps are UTC | All time KPIs | A-02, H-07 | Decision in Phase 3 (D-017 to be raised) |
| RULE-10 | Default time basis for commercial KPIs is `orders.order_purchase_timestamp`. Other bases (approval, carrier, delivery) are used only where named | K01–K13 | Demand-timing convention | — |
| RULE-11 | Delivery-metric eligible population: `order_status` = delivered **and** `order_delivered_customer_date` present. Excluded orders are counted in an exclusion report, never silently dropped | K14–K16 | `05` M05 | **Verified Phase 2**: eligible = 96,470; 8 delivered orders excluded (no date) |
| RULE-12 | On time = delivered **calendar date** ≤ estimated delivery **calendar date** | K15, K16 | Date-level comparison avoids time-of-day artefacts | **Verified Phase 2**: estimated date is date-only (100% midnight) |
| RULE-13 | Products with missing category are reported as category "unknown", not dropped. Categories without English translation keep the Portuguese name and are flagged | M04, K11 | `05` M04 | **Verified Phase 2**: 610 missing, 2 untranslated |
| RULE-14 | Segments with fewer than **30** orders are flagged "small sample"; no ranking claim is made about them | M04, M05 | A-07 | Revisit after profiling |
| RULE-15 | Review score (K13): grain `(review_id, order_id)`. Each order's score = mean of its review scores; K13 = mean of order scores. **Non-independence:** 789 review_ids are shared by 2–3 orders (1,412 orders affected) with identical content, so those order-level observations are not independent. Any statistical test on K13 must account for this (e.g. cluster by review_id or a sensitivity run with one order per shared review) | K13 | D-019(b) | **Verified Phase 2** |
| RULE-16 | Every table, field, KPI, API value and UI element carries a provenance class: `source_observed`, `derived`, `synthetic_assumption`, `forecast`, `scenario_output` | All | `04` | Phase 8–9 tests |
| RULE-17 | Synthetic data lives only in `scenario_*` tables and is never summed into observed totals | M03, M06, M07 | `04` | Phase 3 tests |
| RULE-18 | No metric is called profit, margin or net income unless built on a cost source. Revenue minus incomplete costs is never labelled profit | M06, M07 | Master prompt rule 4 | Terminology review each phase |
| RULE-19 | Relationships between variables are described as associations unless an experimental or quasi-experimental design supports a causal claim | All analysis | Master prompt rule 5 | Report review |
| RULE-20 | Scenario ROI = (incremental benefit − intervention cost) ÷ intervention cost. Net benefit = incremental benefit − intervention cost. ROI is **undefined** when cost = 0. Payback is reported only when benefit accrues over a defined period | Y06, M07 | `05` M07 | Phase 7 hand-calculated tests |
| RULE-21 | Cancellation (an order status) is not treated as a return or refund. No return/refund metric is produced | M04, M06 | H-05 | — |
| RULE-25 | Default analysis window (D-018): **2017-01-01 to 2018-08-31** for trends, period comparisons and forecasting. The full source range (2016-09 to 2018-10) stays selectable. Months outside the window are flagged: 2016-09 to 2016-12 "low coverage", 2018-09 to 2018-10 "incomplete — extract cutoff". Customer history (first purchase, repeat status) uses the full range regardless of the display window | All trend KPIs, K08, K25 | D-018 | **Verified Phase 2** (DQ-15) |
| RULE-26 | Cancellation (K12) counts `order_status` = `canceled` only. `unavailable` is reported separately (K26). The two are never summed under the name "cancellation" | K12, K26 | D-019(a) | **Verified Phase 2**: canceled 625, unavailable 609 |
| RULE-27 | K17 exclusion rules (low-confidence KPI). An item row is excluded, and counted by reason, if: (1) `order_delivered_carrier_date` is missing; (2) carrier date < `order_approved_at`; (3) carrier date < `order_purchase_timestamp`; (4) `shipping_limit_date` > purchase + 60 days. Profiling counts at order level: (2) 1,359, (3) 166; item rows for (4): 12 | K17 | D-019(c) | **Verified Phase 2** (DQ-12, DQ-13) |
| RULE-28 | K20 excludes `credit_card` payment records with `payment_installments` = 0 as invalid and reports the excluded record count with the KPI (2 in profiled data) | K20 | D-019(d) | **Verified Phase 2** (DQ-17) |
| RULE-22 | Period comparison uses a prior period of equal length; partially covered months at the data edges are flagged | M01 | `05` M01 | Phase 4 |
| RULE-23 | Months near the end of the dataset are flagged for right-censoring when the KPI depends on later events (delivery, review, repeat purchase) | K01 (if delivered-only), K07, K08, K14–K16 | Data cutoff effect | **Verified Phase 2**: 2018-09/10 contain 0 delivered orders; default window D-018 |
| RULE-24 | Forecast and model evaluation use chronological splits only; features may use only information available at the cutoff | M08, M02 | `05` M08 | Phase 6 leakage tests |
