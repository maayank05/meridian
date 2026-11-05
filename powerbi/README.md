# MERIDIAN — Power BI

**Status:** specification, DAX measures and build instructions are complete. **No `.pbix` file is included.** Power BI Desktop is a GUI tool and the report must be built by hand (D-012). Nothing in this folder claims a report exists.

- [model_specification.md](model_specification.md): tables, grain, relationships, provenance
- [dax_measures.md](dax_measures.md): DAX for the canonical KPIs plus reconciliation targets

## Build the report (about 30 minutes)
1. **Prerequisites:** Power BI Desktop and the **MySQL Connector/NET** driver (required by Power BI's MySQL connector). A loaded `meridian_dev` database (`python -m meridian.ingestion`).
2. **Get data → MySQL database**: server `localhost`, database `meridian_dev`. Sign in with the **read-only** `meridian_reader` account (Database credentials). Use **Import** mode.
3. Select the tables listed in the model specification (`dim_*`, `fact_*`, optionally `agg_kpi_monthly`). Do not import `raw_*` tables: they contain review free text.
4. **Model view:** create the relationships exactly as specified (single direction, one-to-many). Mark `dim_date` as the date table (`date_key`).
5. **New measures:** paste each measure from `dax_measures.md` into a measure table named `_Measures`.
6. **Pages** (suggested): Executive Overview (K01–K06 cards, monthly line), Commercial (category bar, AOV), Customers (K21, repeat rate), Operations (on-time rate, review score), Data Quality (import `audit_dq_result` as a table visual).
7. Add a **page-level filter** `dim_date[coverage_flag] = "default_window"` (D-018), and a text box on every page: *"Revenue proxy: item value of delivered orders. Not accounting revenue or profit."*
8. **Reconcile** (below) before using the report.

## Reconciliation
With the page filter set to the default window (2017-01 to 2018-08), each card must equal the API (`GET /api/v1/overview`) and the app's Overview page. Targets measured on 2026-11-06 are listed in `dax_measures.md`. If a value differs, the DAX or a relationship direction is wrong. The SQL views are the reference.

## Limitations
- Power BI Service refresh from a local MySQL needs an on-premises data gateway. It is not configured (no hosting in this project).
- Forecast (K25) and simulator outputs are computed in Python and are **not** reproduced in Power BI. If you show them, import them labelled *Forecast* / *Scenario*.
