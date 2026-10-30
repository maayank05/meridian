# 08 — KPI Dictionary

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

- **Source field names are header-verified** against [SOURCE_HEADERS](../docs/data/SOURCE_HEADERS.md) (automated check). **Value domains** (e.g. the exact `order_status` values such as `delivered`, `canceled`, `unavailable`), nulls, types and grain uniqueness are **unverified until Phase 2**.
- No KPI here has been calculated. **No values appear in this document.**
- Implementation references are *planned* locations; test names are *planned* reconciliation tests.
- Provenance classes follow RULE-16.

---

## Part A — Canonical revenue definition (D-016, APPROVED 2026-10-31: Option A)

**Context.** Olist is a marketplace. Its own income (commissions/fees) is **not** in the data. Under the simulation, Northstar's "revenue" is the merchandise value of customer orders (assumption A-04). Three value bases, three status scopes and two time bases are possible.

### Alternatives

| Option | Value basis | Status scope | Time basis | Consequences |
|---|---|---|---|---|
| **A (recommended)** | Item price only: Σ `order_items.price` | Delivered orders only | `order_purchase_timestamp` | Conservative "realised sales" closest to revenue recognition on delivery. Excludes freight (a pass-through shipping charge, reported separately as K02). Avoids payment-side effects (instalments, vouchers). **Downside:** the final months are understated because orders placed but not yet delivered at the data cutoff are excluded (right-censoring, RULE-23). Needs a visible warning |
| B | Item price only | All orders except canceled/unavailable | `order_purchase_timestamp` | "Net booked" demand view. Less censoring at the data edge, but includes orders that may never be delivered (shipped/processing at cutoff). Better as a demand indicator than as revenue |
| C | Item price + freight | Delivered only | `order_purchase_timestamp` | Equals what the customer was charged for goods and shipping. Mixes merchandise with logistics charges, which inflates "revenue" and AOV and confuses category comparisons (freight depends on distance and weight) |
| D | Payment value: Σ `order_payments.payment_value` | Delivered or non-canceled | `order_purchase_timestamp` | Cash-collected view. Includes freight and possibly instalment effects and voucher payments (`payment_type` values unverified). Cannot be split by product, category or seller without allocation rules, because payments are order-level. Breaks category/seller drill-down |
| E | Item price only | Delivered only | `order_delivered_customer_date` | Recognition-at-delivery timing. Shifts revenue into later months, mixes purchase cohorts, and is still censored at the cutoff. Harder to reconcile with demand-side metrics (orders, cohorts) that use purchase date |

### Decision: Option A — approved by the project owner 2026-10-31
**K01 Delivered Merchandise Value (Revenue Proxy)** = Σ `order_items.price` over items whose order has `order_status` = delivered, bucketed by `order_purchase_timestamp`, in BRL.

Reasons:
1. Item-level, so it supports category, product and seller drill-down without allocation.
2. Delivered-only avoids counting orders that may still be cancelled.
3. Freight and payments stay available as separate, reconciled KPIs (K02, K18), so nothing is hidden.

Mitigations: the right-censoring flag (RULE-23) is shown on the latest months. A secondary "Booked Merchandise Value" (option B) can be added later as a **demand indicator, not revenue**, if you want it.

**Mandatory presentation rules for K01 (D-016):**
1. Displayed name everywhere (UI, API metadata, report, Power BI): **"Delivered Merchandise Value (Revenue Proxy)"**. Short label "Delivered Merchandise Value"; "revenue" may appear only as "revenue proxy".
2. It is **not audited accounting revenue and not profit**. Refunds, returns, chargebacks, discounts/voucher adjustments, taxes and other accounting adjustments are **not available** in the source and are not applied.
3. Freight is excluded and always reported separately (K02).
4. Recent periods carry a **right-censoring warning** (RULE-23): orders placed but not yet delivered at the data cutoff are excluded, so the latest months are understated.
5. One canonical definition is implemented once in SQL and reused by Python, the API and Power BI (DAX). Any divergence fails reconciliation tests.

---

## Part B — Supported KPIs (observed source → derived)

### K01 — Delivered Merchandise Value (Revenue Proxy)
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Merchandise (item price) value of delivered orders, grouped by purchase date. Canonical **revenue proxy** for simulated Northstar (D-016); not audited accounting revenue, not profit |
| Formula | Σ price over eligible order items |
| Numerator / denominator | Sum; no denominator |
| Grain | Order item, aggregated to the requested period/segment |
| Source fields | `order_items.price`, `order_items.order_id`, `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | `order_status` = delivered (value to verify in Phase 2); global filters (date, category, customer state, seller state) |
| Time basis | `order_purchase_timestamp` (RULE-10) |
| Currency / unit | BRL (A-01), DECIMAL, display 2 dp |
| Null handling | Items with null price are excluded **and counted** in the quality report; never treated as 0 |
| Owner | SH-02 CFO / FP&A |
| Refresh cadence | Per ingestion run (static historical dataset) |
| Limitations | Revenue proxy only. Not audited accounting revenue; not profit (RULE-18). Refunds, returns, chargebacks, voucher/discount and other accounting adjustments are unavailable and not applied. Excludes freight (see K02). Right-censoring warning required on recent periods (RULE-23). Olist marketplace value, not Olist's own income (A-04) |
| Implementation refs | Single canonical definition: SQL planned `backend/sql/marts` (Phase 4), reused by Python `analytics` (Phase 5), API metadata `/api/v1/metadata/metrics` (Phase 8) and the DAX measure (Phase 10) |
| Reconciliation test | Planned: SQL = Python = API = Power BI on a hand-calculated fixture; raw Σ price for delivered orders = mart total; displayed name and censoring flag asserted in API/UI tests |

### K02 — Freight Billed
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Freight charged on items in delivered orders |
| Formula | Σ freight_value over eligible order items |
| Numerator / denominator | Sum; no denominator |
| Grain | Order item |
| Source fields | `order_items.freight_value`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Same population as K01 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | BRL, DECIMAL |
| Null handling | Null freight excluded and counted; not set to 0 |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Freight is charged to the customer; the carrier's cost is not available |
| Implementation refs | SQL Phase 4 · Python Phase 5 · DAX Phase 10 (planned) |
| Reconciliation test | Planned: raw Σ freight_value for delivered orders = mart total |

### K03 — Delivered Orders
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Number of distinct orders with delivered status |
| Formula | COUNT DISTINCT order_id where status = delivered |
| Numerator / denominator | Count |
| Grain | Order |
| Source fields | `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Delivered only; global filters (category/seller filters count an order if any item matches, documented) |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Orders (count) |
| Null handling | Orders with null status reported as a quality failure |
| Owner | SH-01 CEO |
| Refresh cadence | Per ingestion run |
| Limitations | Category/seller filtering of a multi-item order needs a documented inclusion rule (Phase 4) |
| Implementation refs | SQL Phase 4 · Python Phase 5 · DAX Phase 10 (planned) |
| Reconciliation test | Planned: count matches raw distinct delivered order_id; no fan-out from item join |

### K04 — Average Order Value (AOV)
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Average merchandise value per delivered order |
| Formula | K01 ÷ K03 |
| Numerator / denominator | K01 / K03, same population and filters |
| Grain | Period/segment |
| Source fields | `order_items.price`, `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | As K01 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | BRL per order |
| Null handling | Undefined (not 0) when K03 = 0 |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Under a category filter, AOV covers only the matching items; documented in UI |
| Implementation refs | SQL Phase 4 · Python Phase 5 · DAX Phase 10 (planned) |
| Reconciliation test | Planned: hand-calculated fixture; division-by-zero case |

### K05 — Items per Delivered Order
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Average number of item rows per delivered order |
| Formula | COUNT(order items) ÷ K03 |
| Numerator / denominator | Item rows / delivered orders |
| Grain | Period/segment |
| Source fields | `order_items.order_id`, `order_items.order_item_id`, `orders.order_status` |
| Filters / exclusions | Delivered only |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Items per order |
| Null handling | Undefined when K03 = 0 |
| Owner | SH-04 |
| Refresh cadence | Per ingestion run |
| Limitations | Assumes one row = one unit (no quantity column exists — to verify in Phase 2) |
| Implementation refs | SQL Phase 4 · Python Phase 5 (planned) |
| Reconciliation test | Planned: fixture with multi-item orders |

### K06 — Orders Placed (all statuses)
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | All orders created in the period, regardless of outcome |
| Formula | COUNT DISTINCT order_id |
| Numerator / denominator | Count |
| Grain | Order |
| Source fields | `orders.order_id`, `orders.order_purchase_timestamp` |
| Filters / exclusions | None by status |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Orders |
| Null handling | Null purchase timestamp → quality failure, excluded from time-bucketed counts and counted |
| Owner | SH-01 |
| Refresh cadence | Per ingestion run |
| Limitations | Includes cancelled and not-yet-delivered orders |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: equals raw orders row count when unfiltered |

### K07 — Repeat Purchase Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of customers with at least two delivered orders within the observation window |
| Formula | customers with ≥2 delivered orders ÷ customers with ≥1 delivered order |
| Numerator / denominator | Repeat customers / purchasing customers (by `customer_unique_id`) |
| Grain | Customer, aggregated |
| Source fields | `customers.customer_unique_id`, `customers.customer_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Delivered orders only; window stated with the value |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Undefined when denominator = 0 |
| Owner | SH-03 |
| Refresh cadence | Per ingestion run |
| Limitations | Depends on RULE-02; customers acquired near the data end have less time to repeat (RULE-23) |
| Implementation refs | SQL Phase 4 · Python Phase 5 (planned) |
| Reconciliation test | Planned: fixture where one person has two customer_ids under the same customer_unique_id |

### K08 — Cohort Retention Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of a monthly acquisition cohort that places a delivered order in month *n* after their first |
| Formula | customers in cohort c purchasing in month c+n ÷ cohort size of c |
| Numerator / denominator | Active cohort customers in month n / cohort size |
| Grain | Cohort month × months since acquisition |
| Source fields | `customers.customer_unique_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Delivered orders; cohort = month of first delivered-order purchase |
| Time basis | `order_purchase_timestamp`, calendar months |
| Currency / unit | % |
| Null handling | Unobservable cells (beyond data end) are blank, not 0 |
| Owner | SH-03 |
| Refresh cadence | Per ingestion run |
| Limitations | Right-censoring; low repeat rates may make cells sparse |
| Implementation refs | SQL Phase 4 · Python Phase 5 (planned) |
| Reconciliation test | Planned: month-boundary fixture; month 0 = 100% |

### K09 — RFM Score
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Customer scores for Recency (days since last order), Frequency (delivered orders) and Monetary (K01 value) at a stated reference date |
| Formula | Quantile scores 1–5 per dimension (method finalised in Phase 5; ties documented) |
| Numerator / denominator | Not a ratio |
| Grain | Customer (`customer_unique_id`) at reference date |
| Source fields | `customers.customer_unique_id`, `orders.customer_id`, `orders.order_purchase_timestamp`, `orders.order_status`, `order_items.price` |
| Filters / exclusions | Orders up to the reference date only |
| Time basis | Reference date (explicit input) |
| Currency / unit | Scores 1–5; monetary in BRL |
| Null handling | Customers with no delivered orders are not scored |
| Owner | SH-04 |
| Refresh cadence | Per run / per reference date |
| Limitations | Frequency is mostly 1 if repeat rates are low, which weakens quantile scoring; to assess in Phase 5 |
| Implementation refs | Python Phase 5 (planned) |
| Reconciliation test | Planned: Σ monetary = K01 for the same population; leakage test |

### K10 — Customer Revenue Concentration
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of K01 generated by the top 10% of customers by spend |
| Formula | K01 of top-decile customers ÷ total K01 |
| Numerator / denominator | Top-decile revenue / total revenue |
| Grain | Period |
| Source fields | `customers.customer_unique_id`, `orders.customer_id`, `order_items.price`, `orders.order_status` |
| Filters / exclusions | As K01 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Undefined when total = 0 |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Decile cut-off ties documented |
| Implementation refs | Python Phase 5 (planned) |
| Reconciliation test | Planned: fixture with known distribution |

### K11 — Category Revenue Share
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Category's share of K01 |
| Formula | K01 for category ÷ total K01 |
| Numerator / denominator | Category revenue / total revenue |
| Grain | Product category |
| Source fields | `products.product_category_name`, `category_translation.product_category_name_english`, `order_items.product_id`, `order_items.price`, `orders.order_status` |
| Filters / exclusions | As K01; "unknown" category kept (RULE-13) |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Missing category → "unknown" |
| Owner | SH-04 |
| Refresh cadence | Per ingestion run |
| Limitations | Small categories flagged (RULE-14) |
| Implementation refs | SQL Phase 4 · DAX Phase 10 (planned) |
| Reconciliation test | Planned: shares sum to 100% (within rounding) |

### K12 — Cancellation Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of placed orders with cancelled status |
| Formula | orders with status = canceled ÷ K06 |
| Numerator / denominator | Cancelled orders / orders placed |
| Grain | Period/segment |
| Source fields | `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Status value spelling to verify in Phase 2; whether `unavailable` counts is decided after profiling |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Undefined when K06 = 0 |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | Not a return/refund rate (RULE-21); cancellation reason not available |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: fixture with mixed statuses |

### K13 — Average Review Score
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Mean customer review score |
| Formula | AVG(review_score) |
| Numerator / denominator | Σ scores / number of reviews |
| Grain | Review; order-level per RULE-15 when joined to orders |
| Source fields | `order_reviews.review_id`, `order_reviews.order_id`, `order_reviews.review_score`, `order_reviews.review_creation_date` |
| Filters / exclusions | Global filters via order |
| Time basis | `orders.order_purchase_timestamp` (via order) for consistency; review date available |
| Currency / unit | Score 1–5 (range to verify in Phase 2) |
| Null handling | Missing scores excluded and counted |
| Owner | SH-04 |
| Refresh cadence | Per ingestion run |
| Limitations | Not every order may have a review (response bias); associations only (RULE-19) |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: multi-review order fixture |

### K14 — Delivery Lead Time
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Days from purchase to customer delivery |
| Formula | delivered_customer_date − purchase_timestamp, in days (mean and median reported) |
| Numerator / denominator | Σ days / eligible orders (mean) |
| Grain | Order |
| Source fields | `orders.order_purchase_timestamp`, `orders.order_delivered_customer_date`, `orders.order_status` |
| Filters / exclusions | RULE-11 eligible population; negative durations flagged invalid and excluded and counted |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Days (decimal) |
| Null handling | Missing delivery date → excluded, counted in exclusion report |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | Timezone unknown (A-02); right-censoring for recent months |
| Implementation refs | SQL Phase 4 · Python Phase 5 (planned) |
| Reconciliation test | Planned: hand-calculated durations incl. month boundary |

### K15 — On-Time Delivery Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of eligible delivered orders delivered on or before the estimated date |
| Formula | orders with DATE(delivered) ≤ DATE(estimated) ÷ eligible orders |
| Numerator / denominator | On-time orders / eligible delivered orders |
| Grain | Order |
| Source fields | `orders.order_delivered_customer_date`, `orders.order_estimated_delivery_date`, `orders.order_status` |
| Filters / exclusions | RULE-11, RULE-12 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Missing estimated date → excluded and counted |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | Estimated date is a promise set by the platform; its logic is unknown |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: equal-date boundary fixture counts as on time |

### K16 — Average Delay of Late Deliveries
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Mean days late among late orders |
| Formula | AVG(DATE(delivered) − DATE(estimated)) where > 0 |
| Numerator / denominator | Σ late days / late orders |
| Grain | Order |
| Source fields | `orders.order_delivered_customer_date`, `orders.order_estimated_delivery_date`, `orders.order_status` |
| Filters / exclusions | Late eligible orders only |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Days |
| Null handling | Undefined when no late orders |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | As K15 |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: fixture |

### K17 — Seller Handover On-Time Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of order items handed to the carrier by the seller shipping limit |
| Formula | items where order_delivered_carrier_date ≤ shipping_limit_date ÷ eligible items |
| Numerator / denominator | On-time handover items / items with both dates |
| Grain | Order item (seller) |
| Source fields | `order_items.shipping_limit_date`, `order_items.seller_id`, `orders.order_delivered_carrier_date` |
| Filters / exclusions | Items with both dates present |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Missing carrier date → excluded, counted |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | Carrier date is order-level; in multi-seller orders it may not reflect each seller's handover — to assess in Phase 2 |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: multi-seller fixture |

### K18 — Payment vs Order Value Difference
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Difference between payments recorded and item+freight value per order |
| Formula | Σ payment_value (per order) − Σ (price + freight_value) (per order), aggregated after order-level computation |
| Numerator / denominator | Difference; plus counts of orders with +/−/0 difference |
| Grain | Order |
| Source fields | `order_payments.order_id`, `order_payments.payment_value`, `order_items.order_id`, `order_items.price`, `order_items.freight_value` |
| Filters / exclusions | All statuses shown, split by status |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | BRL |
| Null handling | Orders missing on either side reported as a separate category |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Causes of differences (instalment interest, vouchers, rounding) cannot be confirmed from the data; described as possible explanations only |
| Implementation refs | SQL Phase 4 · Python Phase 5 (planned) |
| Reconciliation test | Planned: RULE-06 fan-out fixture (2 items × 2 payments) |

### K19 — Payment Type Mix
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of payment value by payment type |
| Formula | Σ payment_value by type ÷ Σ payment_value |
| Numerator / denominator | Type value / total value |
| Grain | Payment record |
| Source fields | `order_payments.payment_type`, `order_payments.payment_value`, `order_payments.order_id` |
| Filters / exclusions | Status scope as K01 when combined with revenue views |
| Time basis | `order_purchase_timestamp` (via order) |
| Currency / unit | % |
| Null handling | Unknown/undefined types shown as their own category |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Type values unverified until Phase 2 |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: shares sum to 100% |

### K20 — Average Instalments
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Mean number of instalments per payment record |
| Formula | AVG(payment_installments) |
| Numerator / denominator | Σ instalments / payment records |
| Grain | Payment record |
| Source fields | `order_payments.payment_installments`, `order_payments.payment_type` |
| Filters / exclusions | Value-domain checks in Phase 2 (e.g. zero instalments) |
| Time basis | `order_purchase_timestamp` (via order) |
| Currency / unit | Count |
| Null handling | Invalid values excluded and counted |
| Owner | SH-02 |
| Refresh cadence | Per ingestion run |
| Limitations | Instalment interest not observable |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: fixture |

### K21 — Active Customers
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Distinct people with at least one delivered order in the period |
| Formula | COUNT DISTINCT customer_unique_id |
| Numerator / denominator | Count |
| Grain | Customer |
| Source fields | `customers.customer_unique_id`, `customers.customer_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Delivered only |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Customers |
| Null handling | Orders whose customer_id has no customers row → orphan, counted |
| Owner | SH-03 |
| Refresh cadence | Per ingestion run |
| Limitations | RULE-02 dependency |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: two customer_ids → one person fixture |

### K22 — Seller Revenue Concentration
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of K01 from the top 10% of sellers |
| Formula | K01 of top-decile sellers ÷ total K01 |
| Numerator / denominator | Top-decile seller revenue / total revenue |
| Grain | Seller |
| Source fields | `order_items.seller_id`, `order_items.price`, `orders.order_status` |
| Filters / exclusions | As K01 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | % |
| Null handling | Undefined when total = 0 |
| Owner | SH-04 |
| Refresh cadence | Per ingestion run |
| Limitations | Ties at the cut-off documented |
| Implementation refs | Python Phase 5 (planned) |
| Reconciliation test | Planned: fixture |

### K23 — Active Sellers
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Distinct sellers with at least one item in a delivered order in the period |
| Formula | COUNT DISTINCT seller_id |
| Numerator / denominator | Count |
| Grain | Seller |
| Source fields | `order_items.seller_id`, `sellers.seller_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| Filters / exclusions | Delivered only |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | Sellers |
| Null handling | Item sellers missing from sellers table → orphan, counted |
| Owner | SH-05 |
| Refresh cadence | Per ingestion run |
| Limitations | Activity, not registration |
| Implementation refs | SQL Phase 4 (planned) |
| Reconciliation test | Planned: fixture |

### K24 — Data-Quality Check Pass Rate
| Field | Value |
|---|---|
| Provenance | derived |
| Business definition | Share of executed data-quality checks that passed in the latest run |
| Formula | passed checks ÷ executed checks |
| Numerator / denominator | Passed / executed (skipped checks reported separately) |
| Grain | Ingestion run |
| Source fields | pipeline: audit quality results (generated by MERIDIAN, not an Olist field) |
| Filters / exclusions | Latest successful run by default |
| Time basis | Run timestamp (UTC) |
| Currency / unit | % |
| Null handling | Undefined when no checks executed |
| Owner | SH-06 |
| Refresh cadence | Per ingestion run |
| Limitations | A pass rate hides severity; always shown with the failing-check list |
| Implementation refs | Python Phase 3/5 (planned) |
| Reconciliation test | Planned: fixture run with a known failing check |

### K25 — Revenue Forecast
| Field | Value |
|---|---|
| Provenance | forecast |
| Business definition | Projected monthly K01 with prediction interval, only if the model is evaluated against a naive baseline |
| Formula | Model selected in Phase 6; baseline = seasonal-naive or naive |
| Numerator / denominator | Not a ratio |
| Grain | Month |
| Source fields | `order_items.price`, `orders.order_status`, `orders.order_purchase_timestamp` (via K01 monthly series) |
| Filters / exclusions | Censored final months excluded from training (RULE-23) |
| Time basis | Month of `order_purchase_timestamp` |
| Currency / unit | BRL |
| Null handling | Not produced if history is insufficient |
| Owner | SH-02 |
| Refresh cadence | Per model run |
| Limitations | Short history (~2 years expected) limits seasonality; may be reported as "not justified" |
| Implementation refs | Python Phase 6 (planned) |
| Reconciliation test | Planned: chronological-split leakage test; baseline comparison |

---

## Part C — Synthetic and scenario metrics (never observed)

All Y-series values live in `scenario_*` tables (RULE-17) and carry the Synthetic or Scenario label. Generators are seeded, and their distributions are documented when built (Phase 7; M03 per D-015).

### Y01 — Synthetic Campaign Spend
| Field | Value |
|---|---|
| Provenance | synthetic_assumption |
| Business definition | Hypothetical marketing spend by channel and month for scenario exploration |
| Formula | Seeded generator (design in [14_M03_marketing_methodology.md](14_M03_marketing_methodology.md)) |
| Numerator / denominator | n/a |
| Grain | Channel × month |
| Source fields | synthetic: generator parameters (no Olist field) |
| Filters / exclusions | n/a |
| Time basis | Month (aligned to observed K01 months) |
| Currency / unit | BRL |
| Null handling | n/a |
| Owner | SH-03 |
| Refresh cadence | On scenario regeneration |
| Limitations | Not real spend; for illustration only |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: same seed → identical output |

### Y02 — Scenario CAC
| Field | Value |
|---|---|
| Provenance | scenario_output |
| Business definition | Hypothetical cost per new customer under synthetic spend and assumed attribution |
| Formula | Y01 ÷ scenario-attributed new customers |
| Numerator / denominator | Synthetic spend / scenario-attributed new customers |
| Grain | Channel × month |
| Source fields | synthetic: Y01 and attribution assumptions; observed new-customer counts from `customers.customer_unique_id`, `orders.order_purchase_timestamp` |
| Filters / exclusions | n/a |
| Time basis | Month |
| Currency / unit | BRL per customer |
| Null handling | Undefined when attributed customers = 0 |
| Owner | SH-03 |
| Refresh cadence | On scenario run |
| Limitations | Not an observed CAC |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: hand-calculated fixture |

### Y03 — Scenario ROAS
| Field | Value |
|---|---|
| Provenance | scenario_output |
| Business definition | Hypothetical attributed revenue per unit of synthetic spend |
| Formula | scenario-attributed revenue ÷ Y01 |
| Numerator / denominator | Attributed revenue / synthetic spend |
| Grain | Channel × month |
| Source fields | synthetic: Y01 and attribution share; observed revenue baseline K01 |
| Filters / exclusions | n/a |
| Time basis | Month |
| Currency / unit | Ratio |
| Null handling | Undefined when spend = 0 |
| Owner | SH-03 |
| Refresh cadence | On scenario run |
| Limitations | Attributed ≠ incremental (see methodology) |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: hand-calculated fixture |

### Y04 — Scenario Incremental Revenue
| Field | Value |
|---|---|
| Provenance | scenario_output |
| Business definition | Revenue assumed to occur only because of the campaign, under a stated lift assumption |
| Formula | baseline revenue × assumed lift % |
| Numerator / denominator | n/a |
| Grain | Scenario |
| Source fields | synthetic: lift assumption; observed baseline K01 |
| Filters / exclusions | n/a |
| Time basis | Scenario period |
| Currency / unit | BRL |
| Null handling | n/a |
| Owner | SH-03 |
| Refresh cadence | On scenario run |
| Limitations | The lift is assumed, not measured |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: hand-calculated fixture |

### Y05 — Synthetic COGS Rate
| Field | Value |
|---|---|
| Provenance | synthetic_assumption |
| Business definition | Assumed cost of goods as a % of merchandise value, by category, for contribution scenarios |
| Formula | User-set or documented default assumption with range |
| Numerator / denominator | n/a |
| Grain | Category |
| Source fields | synthetic: assumption table (no Olist field) |
| Filters / exclusions | n/a |
| Time basis | n/a |
| Currency / unit | % |
| Null handling | Missing assumption → contribution not computed (never COGS = 0) |
| Owner | SH-02 |
| Refresh cadence | On assumption change |
| Limitations | Not actual costs |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: missing-assumption test |

### Y06 — Scenario ROI and Net Benefit
| Field | Value |
|---|---|
| Provenance | scenario_output |
| Business definition | Return of a hypothetical intervention relative to its cost (RULE-20) |
| Formula | ROI = (incremental benefit − cost) ÷ cost; Net benefit = incremental benefit − cost |
| Numerator / denominator | Net benefit / intervention cost |
| Grain | Scenario × case (base/upside/downside) |
| Source fields | synthetic: user-entered assumptions; observed baseline from K01/K03 |
| Filters / exclusions | Invalid inputs rejected |
| Time basis | Scenario horizon |
| Currency / unit | Ratio (%), BRL |
| Null handling | ROI undefined when cost = 0 |
| Owner | SH-02 |
| Refresh cadence | On scenario run |
| Limitations | Estimate, not a realised result |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: cost 1,000 / benefit 1,500 → ROI 0.50, net 500; zero-cost case |

### Y07 — Scenario Estimated Contribution
| Field | Value |
|---|---|
| Provenance | scenario_output |
| Business definition | Merchandise value minus **assumed** COGS (and other stated assumed costs); explicitly not profit |
| Formula | K01 × (1 − Y05) − other assumed costs |
| Numerator / denominator | n/a |
| Grain | Category × period × scenario |
| Source fields | synthetic: Y05; observed K01 from `order_items.price` |
| Filters / exclusions | As K01 |
| Time basis | `order_purchase_timestamp` |
| Currency / unit | BRL |
| Null handling | Not computed if any required assumption is missing |
| Owner | SH-02 |
| Refresh cadence | On scenario run |
| Limitations | Never labelled profit (RULE-18) |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: hand-calculated fixture |

### Y08 — Synthetic Budget and Variance
| Field | Value |
|---|---|
| Provenance | synthetic_assumption |
| Business definition | Hypothetical monthly revenue budget for actual-vs-budget practice; variance = K01 − budget |
| Formula | Budget from documented generator; variance = actual − budget |
| Numerator / denominator | n/a |
| Grain | Month |
| Source fields | synthetic: budget table; observed K01 |
| Filters / exclusions | n/a |
| Time basis | Month |
| Currency / unit | BRL |
| Null handling | No variance where no budget exists |
| Owner | SH-02 |
| Refresh cadence | On regeneration |
| Limitations | Budget is not a real plan (`05` M06) |
| Implementation refs | Python Phase 7 (planned) |
| Reconciliation test | Planned: fixture |

---

## Part D — Unsupported metrics (not observable in the source)

| ID | Metric | Class | Reason (header evidence) | Data that would be required |
|---|---|---|---|---|
| U01 | Gross profit / gross margin | unsupported | No COGS columns (H-05) | Product or order-level cost of goods |
| U02 | Net profit / operating profit | unsupported | No opex, fees, tax, logistics cost (H-05) | Full P&L cost lines |
| U03 | Observed CAC | unsupported | No marketing spend (H-05) | Spend by channel/date + new-customer attribution |
| U04 | Observed ROAS | unsupported | No spend or attribution | Spend + attributed revenue |
| U05 | Observed incremental lift | unsupported | No experiments or treatment assignment | Randomised holdouts or quasi-experimental design |
| U06 | Return / refund rate | unsupported | No return or refund fields; cancellation ≠ return (RULE-21) | Returns ledger with reasons and amounts |
| U07 | Inventory turnover / stock-outs | unsupported | No inventory snapshots | Stock levels by product and date |
| U08 | Conversion rate / traffic | unsupported | No sessions or visits | Web analytics sessions and funnel events |
| U09 | Observed churn (true label) | unsupported | No subscription or contract end; inactivity is only a proxy | Defined relationship end; otherwise an inactivity proxy with explicit window (Phase 6 decision) |
| U10 | Price elasticity | conditional | Price variation exists per item row, but identification assumptions are unverified | Assessed in Phase 6; reported as unsupported if identification fails |
