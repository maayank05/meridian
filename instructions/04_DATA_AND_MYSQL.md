# 04 — Data Acquisition, Governance and MySQL

## Primary source
Olist Brazilian E-Commerce Public Dataset:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Before designing tables:
1. Confirm exact downloaded files.
2. Inspect every header and actual data type.
3. Count rows and missing values.
4. Inspect duplicate candidate keys.
5. Validate relationships and orphan records.
6. Profile dates, amounts, quantities and categories.
7. Review license/terms and redistribution permissions.
8. Record limitations.

Do not assume the dataset contains advertising spend, full COGS, operating expenses, inventory snapshots, campaign attribution or experimental treatment assignments.

## Data provenance classes
Label every dataset/field/measure as one of:
- `source_observed`: directly from Olist.
- `derived`: calculated from source observations.
- `synthetic_assumption`: deliberately generated for Northstar scenario modelling.
- `forecast`: model output.
- `scenario_output`: hypothetical calculation.
These classes must be visible in metadata and, where relevant, UI labels.

## Acquisition
Support local file upload/path configuration. Provide clear instructions for manual Kaggle download if automated download requires credentials. Do not require Kaggle credentials when source files are already present locally.

## MySQL layers
Use schemas or table prefixes to separate:
- `raw_*`: minimally altered imported records.
- `stg_*`: standardized columns, types and cleaned values.
- `dim_*` / `fact_*` or documented equivalent analytical model.
- `audit_*`: ingestion runs, source metadata, quality results and pipeline status.
- `scenario_*`: explicitly synthetic assumptions and scenario inputs.

Do not over-normalize reporting marts. Document grain for every fact table.

## Candidate source entities
Verify actual files before creating:
- customers
- orders
- order_items
- payments
- reviews
- products
- sellers
- geolocation
- product_category_translation

Potential analytical facts:
- `fact_orders` at one row per order (only after validating the grain).
- `fact_order_items` at one row per order item.
- `fact_payments` at one row per payment record.
- `fact_reviews` at the source-defined review grain.
Potential dimensions:
- customer, product, seller, date, geography, order status.
Do not join order-level and item-level tables without understanding fan-out and double-counting risk.

## Monetary and time rules
- Confirm currency and source semantics before aggregating.
- Use DECIMAL in MySQL for exact financial values.
- Do not round intermediate calculations unnecessarily.
- Document timezone conversion and date selection (purchase, approval, shipment, delivery).
- Distinguish order total, item value, freight, payment value and any refund/cancellation treatment.
- Revenue definition must explicitly state included order statuses and fields.
- Reconcile payments and order items; differences must be visible and explained.

## Data quality controls
- Required file and column checks.
- Type and parse validation.
- Duplicate key detection.
- Foreign-key/orphan checks.
- Date ordering checks.
- Invalid monetary/quantity checks.
- Missingness report.
- Row-count and aggregate reconciliation.
- Unexpected category/status checks.
- Idempotency/reload checks.

## Persistence and backups
Production MySQL must be persistent managed storage. Do not use container filesystem as the database. Configure automated backups and document restore procedure. Test restore before production release. Use separate development/test/production credentials and databases.

## Synthetic assumptions
Any extra tables for costs, marketing, budget, inventory or supplier contracts must be clearly marked synthetic. Keep them separate from observed Olist data. Document generator seed, distributions, rationale and limitations. Never use synthetic values to claim actual company performance.
