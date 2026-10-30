# Phase Checkpoint
Phase: 1 — Business analysis and specification
Date: 2026-10-31
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## Objective
Produce the business-analysis package so that every proposed metric is tied to header-verified Olist fields or explicitly marked unsupported or synthetic, with full requirement → story traceability. No application code and no data profiling.

## Work completed
- Read **only the header line** of the 9 Olist CSVs; recorded in [SOURCE_HEADERS.md](../data/SOURCE_HEADERS.md) with 7 header-level observations (H-01 to H-07).
- Created the 14 business documents in [business/](../../business/).
- Added FR-030 (M03 synthetic scenario model + methodology) through approved change CR-001 / D-015.
- Raised D-016 (canonical revenue, **Proposed — awaiting user**) and D-017 (timestamp handling, Open — Phase 3).
- Updated traceability, status, spec open questions, limitations and the quality report.
- Built an extended consistency checker (44 checks), then mutation-tested it and fixed the weaknesses found.

## Files created / modified (unstaged; not part of the Phase 0 commit)
- Created: `business/01_business_case.md` … `business/14_M03_marketing_methodology.md` (14 files), `docs/data/SOURCE_HEADERS.md`, `docs/checkpoints/PHASE_01_CHECKPOINT.md`
- Modified: `docs/DECISIONS.md` (D-016, D-017), `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/PROJECT_STATUS.md`, `docs/PROJECT_SPEC.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/QUALITY_REPORT.md`

## Commands actually executed
- `py -3.13 -I -` script reading the first line of each CSV (`readline()` once per file)
- `py -3.13 -I phase1_check.py <repo_root>` (scratchpad): three full runs, plus two mutation-test runs on a scratch copy
- Control-character scan of all docs and staged blobs; `git diff --cached --name-only`

## Header validation evidence
9/9 expected files present, no extra files; 57 columns; no duplicate column names. Check P02 re-reads the header lines and asserts exact equality with SOURCE_HEADERS.md → PASS. Header issues: misspelled `*_lenght` columns, BOM in the translation file, CRLF in 2 files, no currency/timezone/quantity/cost/marketing/inventory/refund columns.

## KPI → source-field mapping (generated from the KPI dictionary)
| KPI | Name | Provenance | Source fields (header-verified) |
|---|---|---|---|
| K01 | Delivered Merchandise Revenue | derived | `order_items.price`, `order_items.order_id`, `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K02 | Freight Billed | derived | `order_items.freight_value`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K03 | Delivered Orders | derived | `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K04 | Average Order Value | derived | `order_items.price`, `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K05 | Items per Delivered Order | derived | `order_items.order_id`, `order_items.order_item_id`, `orders.order_status` |
| K06 | Orders Placed | derived | `orders.order_id`, `orders.order_purchase_timestamp` |
| K07 | Repeat Purchase Rate | derived | `customers.customer_unique_id`, `customers.customer_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K08 | Cohort Retention Rate | derived | `customers.customer_unique_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K09 | RFM Score | derived | `customers.customer_unique_id`, `orders.customer_id`, `orders.order_purchase_timestamp`, `orders.order_status`, `order_items.price` |
| K10 | Customer Revenue Concentration | derived | `customers.customer_unique_id`, `orders.customer_id`, `order_items.price`, `orders.order_status` |
| K11 | Category Revenue Share | derived | `products.product_category_name`, `category_translation.product_category_name_english`, `order_items.product_id`, `order_items.price`, `orders.order_status` |
| K12 | Cancellation Rate | derived | `orders.order_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K13 | Average Review Score | derived | `order_reviews.review_id`, `order_reviews.order_id`, `order_reviews.review_score`, `order_reviews.review_creation_date` |
| K14 | Delivery Lead Time | derived | `orders.order_purchase_timestamp`, `orders.order_delivered_customer_date`, `orders.order_status` |
| K15 | On-Time Delivery Rate | derived | `orders.order_delivered_customer_date`, `orders.order_estimated_delivery_date`, `orders.order_status` |
| K16 | Average Delay of Late Deliveries | derived | `orders.order_delivered_customer_date`, `orders.order_estimated_delivery_date`, `orders.order_status` |
| K17 | Seller Handover On-Time Rate | derived | `order_items.shipping_limit_date`, `order_items.seller_id`, `orders.order_delivered_carrier_date` |
| K18 | Payment vs Order Value Difference | derived | `order_payments.order_id`, `order_payments.payment_value`, `order_items.order_id`, `order_items.price`, `order_items.freight_value` |
| K19 | Payment Type Mix | derived | `order_payments.payment_type`, `order_payments.payment_value`, `order_payments.order_id` |
| K20 | Average Instalments | derived | `order_payments.payment_installments`, `order_payments.payment_type` |
| K21 | Active Customers | derived | `customers.customer_unique_id`, `customers.customer_id`, `orders.customer_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K22 | Seller Revenue Concentration | derived | `order_items.seller_id`, `order_items.price`, `orders.order_status` |
| K23 | Active Sellers | derived | `order_items.seller_id`, `sellers.seller_id`, `orders.order_status`, `orders.order_purchase_timestamp` |
| K24 | Data-Quality Check Pass Rate | derived | pipeline: audit quality results (generated by MERIDIAN, not an Olist field) |
| K25 | Revenue Forecast | forecast | `order_items.price`, `orders.order_status`, `orders.order_purchase_timestamp` (via K01 monthly series) |
| Y01 | Synthetic Campaign Spend | synthetic_assumption | synthetic: generator parameters (no Olist field) |
| Y02 | Scenario CAC | scenario_output | synthetic: Y01 and attribution assumptions; observed new-customer counts from `customers.customer_unique_id`, `orders.order_purchase_timestamp` |
| Y03 | Scenario ROAS | scenario_output | synthetic: Y01 and attribution share; observed revenue baseline K01 |
| Y04 | Scenario Incremental Revenue | scenario_output | synthetic: lift assumption; observed baseline K01 |
| Y05 | Synthetic COGS Rate | synthetic_assumption | synthetic: assumption table (no Olist field) |
| Y06 | Scenario ROI and Net Benefit | scenario_output | synthetic: user-entered assumptions; observed baseline from K01/K03 |
| Y07 | Scenario Estimated Contribution | scenario_output | synthetic: Y05; observed K01 from `order_items.price` |
| Y08 | Synthetic Budget and Variance | synthetic_assumption | synthetic: budget table; observed K01 |

| ID | Unsupported metric | Class |
|---|---|---|
| U01 | Gross profit / gross margin | unsupported |
| U02 | Net profit / operating profit | unsupported |
| U03 | Observed CAC | unsupported |
| U04 | Observed ROAS | unsupported |
| U05 | Observed incremental lift | unsupported |
| U06 | Return / refund rate | unsupported |
| U07 | Inventory turnover / stock-outs | unsupported |
| U08 | Conversion rate / traffic | unsupported |
| U09 | Observed churn (true label) | unsupported |
| U10 | Price elasticity | conditional |

All 27 distinct `table.column` references across the KPI dictionary, rules and stories exist in the headers (check P05). **No KPI has been calculated; the documents contain no metric values** (check P21).

## Requirement → story traceability results
- 12 business requirements → 26 functional requirements (25 from `instructions/02` + FR-030) → 32 user stories.
- Every FR has ≥1 story; every story cites a valid FR; BRD and FRD BR mappings agree (P09, P10, P15, P17).
- Every story has all 11 fields, the "As a/an/the … I want … so that …" form, ≥1 Given/When/Then criterion, a MoSCoW priority, and a test ID marked **(planned)** (P11–P14).
- NFR-001 to NFR-010 have measurable criteria in `05_NFR.md`.
- Nothing is marked Complete (P18). In progress: FR-030, FR-040, FR-041, FR-043, NFR-001, AC-M09.

## Checks and actual results
| Run | Result | Notes |
|---|---|---|
| Phase 1 checker run 1 | Aborted: 35 passed, 1 failed before crash | Checker bug (cp1252 console encoding); P12 failed on 8 stories |
| Fixes | — | 2 stories missing an article corrected; checker accepts "As the …"; UTF-8 output |
| Run 2 | 43 passed, 1 failed | P20 false positive on a correctly negated sentence |
| Mutation test 1 (8 injected violations) | 8/9 caught | **P20 missed a real "profit trend" claim**; rule was too loose |
| P20 rule unit cases | 6/6 | Windowed negation rule |
| Mutation test 2 | Missed, then caught | A heredoc had written `\b` as literal backspace bytes; fixed with chr() and the mutant was then caught |
| Control-character scan | Clean | All docs and the 31 staged blobs |
| **Final run** | **44 passed, 0 failed, 0 skipped** | Real repository |

Ruff/Pytest/frontend: not applicable (no code). The checker is still a scratchpad script; it becomes a committed Pytest suite in Phase 3.

## Acceptance criteria evidence
| Criterion | Evidence |
|---|---|
| Every proposed metric has a valid source or is unsupported/simulated | P03–P07: 25 K-KPIs with header-valid fields (K24 = pipeline audit), 8 Y-metrics declared synthetic, 10 U-metrics with reason and data required |
| Header-only reading; no profiling | One `readline()` per file; no row counts, types or values recorded |
| No unsupported business claims | P20 (profit wording), P21 (no monetary figures); AS-IS process and stakeholders labelled illustrative |
| Revenue alternatives presented, not decided | KPI dictionary Part A; D-016 Proposed (P23) |
| Phase 0 staged snapshot untouched | P24: 31 staged, none from business/ or data/ |

## Defects and unresolved issues
- None open in the deliverables. Three checker defects were found and fixed during the phase (encoding crash, over-strict story regex, P20 loose negation plus backspace corruption).

## Known limitations
- Value domains (order statuses, payment types, review range), nulls, grain uniqueness and date coverage are **unverified until Phase 2**; the KPI dictionary marks them.
- Thresholds such as the small-sample cut-off of 30 (A-07) and NFR performance targets are proposed, not derived.
- The checker is heuristic for wording (P20) and cannot prove the absence of every unsupported claim; human review remains part of each gate.

## Outstanding assumptions, risks and decisions
- **Decision needed: D-016 / Q-7 canonical revenue** (recommend option A).
- Open assumptions: A-02, A-03, A-05, A-06, A-07, A-08, A-09, A-13 (all validated in Phase 2).
- Top risks: R-02 right-censoring, R-03 synthetic data mistaken for real, R-01 pre-profiling definitions.
- D-017 timestamp handling (Phase 3); Q-5 MySQL setup; Q-6 hosting budget.

## Next phase recommendation
Phase 2 — dataset discovery and profiling: validate grain, keys, status and payment domains, nulls and date coverage. Build the data dictionary and synthetic fixtures. Then confirm or revise D-016 and assumptions A-02 to A-13.

## User approval requested
1. Final approval to commit and push the staged Phase 0 snapshot.
2. Decision on D-016.
3. Approval of this Phase 1 checkpoint (Phase 1 files would go in a second commit, with the same pre-commit verification).

---
## Post-review addendum (2026-10-31)
The body above is a point-in-time record. Outcome of the user's review:
- **Accepted with documented limitations** as the Phase 1 *documentation milestone*. This is **not** validation of the future application or analytics.
- **D-016 accepted: Option A**, with a naming clarification. K01 is renamed **"Delivered Merchandise Value (Revenue Proxy)"** (the mapping table above shows its pre-approval name). Conditions: freight separate; not audited revenue or profit; refunds and accounting adjustments documented as unavailable; right-censoring warning; one definition across SQL/Python/API/Power BI.
- Phase 0 committed and pushed as `7270770`.
