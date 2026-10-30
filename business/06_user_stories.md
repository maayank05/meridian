# 06 — User Stories and Acceptance Criteria

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Format: *As a [stakeholder], I want [capability], so that [business outcome].* Priority is MoSCoW. **Test IDs are reservations for planned tests; no test exists until it appears in QUALITY_REPORT with an executed result.** API/UI references are planned names from `instructions/06`–`07`, refined in Phases 8–9. KPI and rule IDs refer to [08_kpi_dictionary.md](08_kpi_dictionary.md) and [07_business_rules.md](07_business_rules.md).

---

### US-001 — Navigate all analytical sections
- **Requirement:** FR-001 · **Priority:** Must · **Stakeholder:** SH-01
- **Story:** As a CEO, I want a clear navigation to every analytical section, so that I can move from overview to detail without hunting.
- **Business value:** Shorter time from question to evidence.
- **Dependencies:** US-002
- **Acceptance criteria:**
  - Given the app is loaded, When I use only the keyboard, Then I can reach all 10 sections listed in `07` and the active section is announced.
  - Given a 360 px wide viewport, When I open the navigation, Then every section link is visible without horizontal scrolling.
- **Data required:** None (shell)
- **API/UI:** React app shell (planned `src/app/`)
- **Test ID:** TST-US-001 (planned) · **Status:** Not started

### US-002 — Consume analytics through a documented API
- **Requirement:** FR-002 · **Priority:** Must · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want versioned, documented REST endpoints, so that every client uses the same calculations.
- **Business value:** One source of truth for app, report and checks.
- **Dependencies:** Phase 3–5 data and services
- **Acceptance criteria:**
  - Given a valid request, When I call an `/api/v1` endpoint, Then I receive 200 and a body matching the published schema, including currency and provenance metadata.
  - Given an invalid query parameter, When I call the endpoint, Then I receive 422 with the standard error envelope and no stack trace.
  - Given the database is unreachable, When I call the readiness endpoint, Then it returns 503 without exposing connection details.
- **Data required:** Analytical tables
- **API/UI:** `/api/v1/health`, `/api/v1/metadata/*`, OpenAPI docs (planned)
- **Test ID:** TST-US-002 (planned) · **Status:** Not started

### US-003 — See honest loading, empty and error states
- **Requirement:** FR-003 · **Priority:** Must · **Stakeholder:** SH-01
- **Story:** As an executive, I want the app to tell me clearly when data is loading, missing or failed, so that I never mistake a placeholder for a result.
- **Business value:** Prevents decisions based on fake or partial visuals.
- **Dependencies:** US-002
- **Acceptance criteria:**
  - Given a filter combination with no matching orders, When the page loads, Then an empty state explains why and no chart axes or zero-valued bars are drawn.
  - Given the API returns an error, When the page loads, Then an error message with a retry action is shown.
  - Given the production build, When I inspect it, Then it contains no mock datasets.
- **Data required:** None beyond API responses
- **API/UI:** Shared state components (planned `src/components/`)
- **Test ID:** TST-US-003 (planned) · **Status:** Not started

### US-004 — Filter by date range and dimensions
- **Requirement:** FR-004 · **Priority:** Must · **Stakeholder:** SH-04
- **Story:** As a category manager, I want to filter by purchase date range, category, customer state and seller state, so that I can isolate where performance changed.
- **Business value:** Faster diagnosis.
- **Dependencies:** US-002, RULE-10
- **Acceptance criteria:**
  - Given a start and end date, When I apply the filter, Then orders with purchase timestamps on both boundary dates are included.
  - Given a start date after the end date, When I apply the filter, Then it is rejected with a validation message and no request is sent.
  - Given a range entirely outside the data coverage, When I apply it, Then an empty state is shown.
  - Given active filters, When I press reset, Then all filters return to documented defaults.
- **Data required:** `orders.order_purchase_timestamp`, `products.product_category_name`, `customers.customer_state`, `sellers.seller_state`
- **API/UI:** `/api/v1/filters` (planned); filter bar component
- **Test ID:** TST-US-004 (planned) · **Status:** Not started

### US-005 — Know where every number comes from
- **Requirement:** FR-005 · **Priority:** Must · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want each KPI to show its provenance class, definition and data freshness, so that I can judge how much to trust it.
- **Business value:** Prevents synthetic or forecast values being read as actuals.
- **Dependencies:** KPI dictionary, audit tables
- **Acceptance criteria:**
  - Given any KPI card or chart, When it renders, Then it displays exactly one of: Observed, Derived, Synthetic, Forecast, Scenario.
  - Given a KPI card, When I open its definition, Then the formula, denominator, exclusions and time basis match the KPI dictionary entry.
  - Given a completed ingestion, When I view any page, Then freshness shows the last successful run timestamp (UTC).
- **Data required:** KPI metadata; `audit_*` run records
- **API/UI:** `/api/v1/metadata/metrics`, `/api/v1/metadata/sources` (planned); provenance badge, definition drawer
- **Test ID:** TST-US-005 (planned) · **Status:** Not started

### US-006 — Ingest the Olist files repeatably
- **Requirement:** FR-010 · **Priority:** Must · **Stakeholder:** SH-08
- **Story:** As a data engineer, I want to load the local Olist CSVs with one documented command, so that anyone can rebuild the database.
- **Business value:** Reproducibility.
- **Dependencies:** MySQL dev/test databases (Q-5)
- **Acceptance criteria:**
  - Given all 9 files in the configured folder, When I run ingestion, Then every file loads and the run is recorded as successful.
  - Given one file is missing, When I run ingestion, Then it fails before writing any rows and names the missing file.
  - Given no Kaggle credentials exist, When files are present locally, Then ingestion succeeds.
- **Data required:** All 9 source files ([SOURCE_HEADERS](../docs/data/SOURCE_HEADERS.md))
- **API/UI:** CLI ingestion command (planned `backend/ingestion/`)
- **Test ID:** TST-US-006 (planned) · **Status:** Not started

### US-007 — Detect schema and relationship problems at load time
- **Requirement:** FR-011 · **Priority:** Must · **Stakeholder:** SH-08
- **Story:** As a data engineer, I want ingestion to validate columns, types, keys and relationships, so that bad data is caught before it reaches reports.
- **Business value:** Earlier, cheaper detection of data issues.
- **Dependencies:** US-006
- **Acceptance criteria:**
  - Given a file with a missing or renamed column, When validated, Then the run fails and names the column.
  - Given duplicate values in a candidate key, When validated, Then the duplicates are counted and reported.
  - Given order items whose `order_id` is absent from orders, When validated, Then orphans are counted and reported by relationship.
- **Data required:** All source headers and keys
- **API/UI:** Validation module (planned)
- **Test ID:** TST-US-007 (planned) · **Status:** Not started

### US-008 — Preserve raw data with run metadata
- **Requirement:** FR-012 · **Priority:** Must · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want raw source rows kept unchanged alongside run metadata, so that any figure can be traced back to its input.
- **Business value:** Auditability.
- **Dependencies:** US-006
- **Acceptance criteria:**
  - Given a successful run, When I compare row counts, Then each `raw_*` table equals its source file's data-row count.
  - Given a run, When I query the audit table, Then it shows run id, file name, file checksum, row count, start/end UTC and status.
- **Data required:** Source files; `audit_*`
- **API/UI:** `/api/v1/metadata/sources` (planned)
- **Test ID:** TST-US-008 (planned) · **Status:** Not started

### US-009 — Transform through ordered SQL scripts
- **Requirement:** FR-013 · **Priority:** Must · **Stakeholder:** SH-08
- **Story:** As a data engineer, I want transformations in numbered, version-controlled SQL scripts, so that the model is reviewable and rebuildable.
- **Business value:** Transparent, reviewable logic.
- **Dependencies:** US-008
- **Acceptance criteria:**
  - Given a clean database, When the scripts run in order, Then all `stg_*`, `dim_*` and `fact_*` tables are created.
  - Given each fact table, When the grain test runs, Then the documented grain key is unique.
- **Data required:** `raw_*` tables
- **API/UI:** `backend/sql/` (planned)
- **Test ID:** TST-US-009 (planned) · **Status:** Not started

### US-010 — Rebuild safely
- **Requirement:** FR-014 · **Priority:** Must · **Stakeholder:** SH-08
- **Story:** As a data engineer, I want reloads to be idempotent and failures to roll back, so that a rerun never corrupts the database.
- **Business value:** Reliability.
- **Dependencies:** US-006, US-009
- **Acceptance criteria:**
  - Given a loaded database, When ingestion runs again with the same files, Then row counts and table checksums are unchanged.
  - Given a failure injected mid-load, When the run ends, Then no partially written rows remain for that run.
  - Given the production environment flag, When a destructive reset is requested, Then it is refused.
- **Data required:** Fixtures
- **API/UI:** CLI flags (planned)
- **Test ID:** TST-US-010 (planned) · **Status:** Not started

### US-011 — Read an ingestion and data-quality report
- **Requirement:** FR-015 · **Priority:** Must · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want a per-run quality report, so that I know which checks passed and how many rows were affected.
- **Business value:** Trust.
- **Dependencies:** US-007
- **Acceptance criteria:**
  - Given a completed run, When I open the report, Then every check is listed with status and affected row count.
  - Given a check that failed, When I read the report, Then the failing rule and table are named.
- **Data required:** `audit_*` quality results
- **API/UI:** `/api/v1/quality/summary` (planned)
- **Test ID:** TST-US-011 (planned) · **Status:** Not started

### US-012 — See headline commercial KPIs with period comparison
- **Requirement:** FR-020 · **Priority:** Must · **Stakeholder:** SH-01
- **Story:** As a CEO, I want Delivered Merchandise Value (revenue proxy), orders, AOV and items per order for a period compared with the prior period, so that I can see what changed.
- **Business value:** Single trusted performance view.
- **Dependencies:** D-016 (revenue definition), US-004
- **Acceptance criteria:**
  - Given a selected period, When the overview loads, Then K01–K05 equal the SQL reference values for the same filters.
  - Given a selected period, When the comparison shows, Then the prior period has the same length and partial months are flagged (RULE-22).
  - Given months near the end of the data, When shown, Then the right-censoring warning is visible (RULE-23).
  - Given the K01 card, When it renders, Then it is titled "Delivered Merchandise Value (Revenue Proxy)", shows freight separately, and its definition states it is not accounting revenue or profit.
- **Data required:** `order_items.price`, `order_items.freight_value`, `orders.order_status`, `orders.order_purchase_timestamp`
- **API/UI:** `/api/v1/executive/summary`, `/api/v1/executive/trends` (planned); Overview page
- **Test ID:** TST-US-012 (planned) · **Status:** Not started

### US-013 — Decompose KPI movement
- **Requirement:** FR-020 · **Priority:** Should · **Stakeholder:** SH-01
- **Story:** As a CEO, I want revenue change broken down by category and customer state, so that I know where the change occurred.
- **Business value:** Faster diagnosis.
- **Dependencies:** US-012
- **Acceptance criteria:**
  - Given two periods, When decomposition runs, Then the segment contributions sum exactly to the total change.
  - Given orders with unknown category, When decomposed, Then they appear as an "unknown" segment rather than being dropped.
- **Data required:** As US-012 plus `products.product_category_name`, `customers.customer_state`
- **API/UI:** `/api/v1/executive/trends` (planned)
- **Test ID:** TST-US-013 (planned) · **Status:** Not started

### US-014 — Analyse cohort retention
- **Requirement:** FR-021 · **Priority:** Must · **Stakeholder:** SH-03
- **Story:** As the head of marketing, I want monthly acquisition cohorts with retention, so that I can see whether customers come back.
- **Business value:** Visibility of retention risk.
- **Dependencies:** RULE-02, D-016
- **Acceptance criteria:**
  - Given a customer whose first qualifying purchase is on the last day of a month, When cohorts are assigned, Then the customer belongs to that month's cohort.
  - Given a cohort, When retention is calculated, Then month 0 equals 100% and later months use the cohort size as denominator.
  - Given cohorts with fewer months of observable history, When displayed, Then unobservable cells are blank, not zero.
- **Data required:** `customers.customer_unique_id`, `orders.customer_id`, `orders.order_purchase_timestamp`, `orders.order_status`
- **API/UI:** `/api/v1/customers/cohorts` (planned); Customers page
- **Test ID:** TST-US-014 (planned) · **Status:** Not started

### US-015 — Segment customers with RFM
- **Requirement:** FR-021 · **Priority:** Should · **Stakeholder:** SH-04
- **Story:** As a commercial manager, I want customers scored by recency, frequency and monetary value against a stated reference date, so that I can understand concentration.
- **Business value:** Targeting and concentration-risk insight.
- **Dependencies:** US-014
- **Acceptance criteria:**
  - Given a reference date, When RFM runs, Then no purchase after the reference date affects any score (no leakage).
  - Given all scored customers, When totals are summed, Then monetary value reconciles to K01 for the same population and period.
- **Data required:** As US-014 plus `order_items.price`
- **API/UI:** `/api/v1/customers/segments` (planned)
- **Test ID:** TST-US-015 (planned) · **Status:** Not started

### US-016 — Compare product categories
- **Requirement:** FR-022 · **Priority:** Must · **Stakeholder:** SH-04
- **Story:** As a category manager, I want category revenue, volume, share and review scores, so that I can find categories that over- or under-perform.
- **Business value:** Focus commercial effort.
- **Dependencies:** D-016
- **Acceptance criteria:**
  - Given categories, When ranked, Then the ranking grain (category, English name where translated) is stated.
  - Given products without a category, When ranked, Then they appear as "unknown" and are counted.
  - Given a category with fewer orders than the small-sample threshold, When shown, Then it is flagged.
- **Data required:** `products.product_category_name`, `category_translation.product_category_name_english`, `order_items.price`, `order_reviews.review_score`
- **API/UI:** `/api/v1/products/performance` (planned); Products page
- **Test ID:** TST-US-016 (planned) · **Status:** Not started

### US-017 — Measure delivery performance
- **Requirement:** FR-023 · **Priority:** Must · **Stakeholder:** SH-05
- **Story:** As the head of operations, I want delivery lead time and on-time rate against the estimated date, so that I can see where fulfilment fails.
- **Business value:** Operational improvement targeting.
- **Dependencies:** RULE-11, RULE-12
- **Acceptance criteria:**
  - Given a delivered order with a delivery date equal to its estimated date, When on-time is evaluated, Then it counts as on time.
  - Given a delivered order with a missing delivery date, When metrics run, Then it is excluded from the denominator and counted in the exclusion report.
  - Given a delivery date earlier than the purchase timestamp, When validated, Then it is flagged as invalid.
- **Data required:** `orders.order_purchase_timestamp`, `orders.order_delivered_customer_date`, `orders.order_estimated_delivery_date`, `orders.order_status`
- **API/UI:** `/api/v1/operations/delivery` (planned); Operations page
- **Test ID:** TST-US-017 (planned) · **Status:** Not started

### US-018 — Compare sellers
- **Requirement:** FR-023 · **Priority:** Should · **Stakeholder:** SH-05
- **Story:** As the head of operations, I want seller-level revenue, handover timeliness, delivery and review metrics, so that I can prioritise seller conversations.
- **Business value:** Seller performance management.
- **Dependencies:** US-017
- **Acceptance criteria:**
  - Given a multi-seller order, When seller revenue is computed, Then each item is attributed to its own seller and the order total is not double-counted.
  - Given seller review relationships, When displayed, Then wording describes association, not cause.
- **Data required:** `order_items.seller_id`, `order_items.shipping_limit_date`, `orders.order_delivered_carrier_date`, `sellers.seller_state`, `order_reviews.review_score`
- **API/UI:** `/api/v1/operations/sellers` (planned)
- **Test ID:** TST-US-018 (planned) · **Status:** Not started

### US-019 — Reconcile payments with order values
- **Requirement:** FR-024 · **Priority:** Must · **Stakeholder:** SH-02
- **Story:** As the CFO, I want payments reconciled with item and freight values per order, so that I know how far the revenue figures can be trusted.
- **Business value:** Financial control.
- **Dependencies:** RULE-05, RULE-06
- **Acceptance criteria:**
  - Given orders with multiple payments and multiple items, When reconciled, Then payments and items are each aggregated to order level before comparison (no fan-out).
  - Given differences, When shown, Then counts and totals of orders with positive, negative and zero difference are visible.
  - Given orders with items but no payments (or the reverse), When reconciled, Then they are listed as a separate category.
- **Data required:** `order_payments.payment_value`, `order_payments.payment_sequential`, `order_items.price`, `order_items.freight_value`
- **API/UI:** `/api/v1/finance/reconciliation` (planned); Financial Intelligence page
- **Test ID:** TST-US-019 (planned) · **Status:** Not started

### US-020 — See which costs are unavailable
- **Requirement:** FR-024 · **Priority:** Must · **Stakeholder:** SH-02
- **Story:** As the CFO, I want the unavailable cost data listed explicitly and any synthetic cost assumptions labelled, so that nobody mistakes revenue for profit.
- **Business value:** Prevents misleading financial claims.
- **Dependencies:** U01, U02; synthetic tables
- **Acceptance criteria:**
  - Given the financial page, When it loads, Then COGS, opex and marketing spend are listed as "not available in source data".
  - Given a synthetic cost scenario, When shown, Then every value carries the Synthetic or Scenario label, and missing costs are never shown as zero.
- **Data required:** KPI dictionary (unsupported section); `scenario_*`
- **API/UI:** Financial Intelligence page (planned)
- **Test ID:** TST-US-020 (planned) · **Status:** Not started

### US-021 — Understand the impact of data-quality issues
- **Requirement:** FR-025 · **Priority:** Should · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want each failed quality check to name the KPIs it affects, so that I can warn stakeholders accurately.
- **Business value:** Informed use of imperfect data.
- **Dependencies:** US-011
- **Acceptance criteria:**
  - Given a failed check on missing delivery dates, When I view impact, Then K14–K16 are listed with the share of eligible orders affected.
- **Data required:** `audit_*`, KPI-to-field mapping
- **API/UI:** `/api/v1/quality/summary` (planned); Data Quality page
- **Test ID:** TST-US-021 (planned) · **Status:** Not started

### US-022 — Compare decision scenarios
- **Requirement:** FR-026 · **Priority:** Must · **Stakeholder:** SH-01
- **Story:** As a CEO, I want to compare a baseline against an intervention under base, upside and downside assumptions, so that I can see the range of plausible outcomes before deciding.
- **Business value:** Better-structured decisions.
- **Dependencies:** RULE-20; observed baseline KPIs
- **Acceptance criteria:**
  - Given intervention cost 1,000 and incremental benefit 1,500, When ROI is calculated, Then ROI = 0.50 (50%) and net benefit = 500.
  - Given intervention cost 0, When ROI is calculated, Then ROI is reported as undefined with an explanation.
  - Given a negative cost or a response rate above 100%, When submitted, Then the input is rejected with a validation message.
  - Given any output, When displayed, Then it is labelled Scenario and lists its assumptions.
- **Data required:** Baseline KPIs; user-entered assumptions
- **API/UI:** `/api/v1/scenarios/compare` (planned); Decision Simulator page
- **Test ID:** TST-US-022 (planned) · **Status:** Not started

### US-023 — See a forecast only when it beats or is honestly compared to a baseline
- **Requirement:** FR-027 · **Priority:** Should · **Stakeholder:** SH-02
- **Story:** As an FP&A lead, I want forecasts evaluated against a naive baseline on held-out months with intervals, so that I know whether to rely on them.
- **Business value:** Prevents over-confidence.
- **Dependencies:** D-016; Phase 6 analysis
- **Acceptance criteria:**
  - Given a chronological split, When evaluated, Then no training observation is later than any test observation.
  - Given model and baseline errors, When reported, Then both are shown; if the model does not beat the baseline, the report says so.
  - Given a forecast, When shown, Then it carries the Forecast label and an interval.
- **Data required:** Monthly K01/K03 series
- **API/UI:** `/api/v1/forecasting/summary` (planned); Forecasting & Risk page
- **Test ID:** TST-US-023 (planned) · **Status:** Not started

### US-024 — Get statistically valid comparisons and anomaly flags
- **Requirement:** FR-027 · **Priority:** Could · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want hypothesis tests run only when their assumptions are checked, and anomaly flags based on stated thresholds, so that statistical claims are defensible.
- **Business value:** Credible analysis.
- **Dependencies:** Phase 6
- **Acceptance criteria:**
  - Given a test, When reported, Then the method, assumptions checked, effect size, p-value and confidence interval are shown.
  - Given an anomaly flag, When shown, Then the baseline and threshold rule are stated.
- **Data required:** Derived KPI series
- **API/UI:** `/api/v1/forecasting/summary` (planned)
- **Test ID:** TST-US-024 (planned) · **Status:** Not started

### US-025 — Generate the executive report
- **Requirement:** FR-028 · **Priority:** Must · **Stakeholder:** SH-01
- **Story:** As a CEO, I want a timestamped HTML executive report generated from the same analytical outputs as the app, so that the report and app always agree.
- **Business value:** Consistent communication.
- **Dependencies:** API services
- **Acceptance criteria:**
  - Given identical filters, When the report is generated, Then every KPI value equals the API value.
  - Given the report, When opened, Then it shows generation timestamp, period, data freshness, quality warnings and limitations.
- **Data required:** Analytical outputs
- **API/UI:** `/api/v1/reports/executive` (planned); Executive Reports page
- **Test ID:** TST-US-025 (planned) · **Status:** Not started

### US-026 — Reconcile Power BI with the platform
- **Requirement:** FR-029 · **Priority:** Should · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want Power BI measures that reconcile to the API for identical filters, so that both tools report the same numbers.
- **Business value:** Cross-tool trust.
- **Dependencies:** D-012; Phase 10
- **Acceptance criteria:**
  - Given the same period and filters, When totals are compared, Then K01, K03 and K04 match the API to the cent / unit.
- **Data required:** Mart tables
- **API/UI:** `powerbi/` specification (planned)
- **Test ID:** TST-US-026 (planned) · **Status:** Not started

### US-027 — Explore a synthetic marketing scenario
- **Requirement:** FR-030 · **Priority:** Should · **Stakeholder:** SH-03
- **Story:** As the head of marketing, I want a clearly synthetic campaign scenario model, so that I can reason about spend, attributed outcomes and incrementality without pretending we have real campaign data.
- **Business value:** Structured thinking about marketing investment.
- **Dependencies:** D-015; [14_M03_marketing_methodology.md](14_M03_marketing_methodology.md)
- **Acceptance criteria:**
  - Given the scenario generator and a fixed seed, When it runs twice, Then the outputs are identical.
  - Given any M03 value, When shown in API or UI, Then it is labelled Synthetic or Scenario, never Observed.
  - Given the M03 page, When it loads, Then a banner states that no observed marketing data exists.
- **Data required:** `scenario_*` synthetic campaign tables; observed baseline K01/K03
- **API/UI:** `/api/v1/marketing/scenario` (planned)
- **Test ID:** TST-US-027 (planned) · **Status:** Not started

### US-028 — Understand marketing measurement limits
- **Requirement:** FR-030 · **Priority:** Must · **Stakeholder:** SH-03
- **Story:** As the head of marketing, I want a methodology page explaining why CAC, ROAS and lift cannot be observed here and what data would be needed, so that I do not over-claim.
- **Business value:** Credibility.
- **Dependencies:** None
- **Acceptance criteria:**
  - Given the methodology page, When read, Then it defines attributed vs incremental outcomes and lists the data required for each metric.
- **Data required:** None
- **API/UI:** Methodology & Definitions page (planned)
- **Test ID:** TST-US-028 (planned) · **Status:** Not started

### US-029 — Trace requirements end to end
- **Requirement:** FR-040 · **Priority:** Must · **Stakeholder:** SH-07
- **Story:** As a business analyst, I want every requirement linked to stories, implementation, tests and evidence, so that completion claims can be audited.
- **Business value:** Governance.
- **Dependencies:** None
- **Acceptance criteria:**
  - Given the traceability matrix, When checked automatically, Then every FR has at least one story and no requirement is marked Complete without executed-test evidence.
- **Data required:** Documentation
- **API/UI:** `docs/REQUIREMENTS_TRACEABILITY.md`
- **Test ID:** TST-US-029 (planned) · **Status:** In progress

### US-030 — Follow data lineage
- **Requirement:** FR-041 · **Priority:** Must · **Stakeholder:** SH-06
- **Story:** As a BI analyst, I want lineage from source column to KPI, so that I can explain any number.
- **Business value:** Explainability.
- **Dependencies:** Phases 3–4
- **Acceptance criteria:**
  - Given any canonical KPI, When I follow its lineage, Then I reach the source columns listed in the KPI dictionary.
- **Data required:** Model metadata
- **API/UI:** `docs/architecture/`, `docs/data/` (planned)
- **Test ID:** TST-US-030 (planned) · **Status:** Not started

### US-031 — Learn the implementation
- **Requirement:** FR-042 · **Priority:** Must · **Stakeholder:** SH-09
- **Story:** As the project owner, I want lessons tied to the real code, so that I can learn and explain the platform from first principles.
- **Business value:** Knowledge transfer.
- **Dependencies:** Implementation phases
- **Acceptance criteria:**
  - Given any lesson, When reviewed, Then it covers the 12 elements in `instructions/13` and every file reference exists.
- **Data required:** None
- **API/UI:** `learning/` (planned)
- **Test ID:** TST-US-031 (planned) · **Status:** Not started

### US-032 — Set up from a clean clone
- **Requirement:** FR-043 · **Priority:** Must · **Stakeholder:** SH-10
- **Story:** As a reviewer, I want to set up, test and run the project from the README alone, so that I can verify it independently.
- **Business value:** Credibility and portability.
- **Dependencies:** All phases
- **Acceptance criteria:**
  - Given a clean clone and the dataset in place, When I follow the README, Then tests pass and the app runs locally.
- **Data required:** Olist files (user-supplied)
- **API/UI:** `README.md`, `docs/DEPLOYMENT_RUNBOOK.md`
- **Test ID:** TST-US-032 (planned) · **Status:** Not started
