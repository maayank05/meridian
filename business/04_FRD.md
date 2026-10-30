# 04 — Functional Requirements Document (FRD)

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

FR IDs come from `instructions/02`. **FR-030 is an addition** approved through D-015 and recorded as change CR-001 in [11_change_log.md](11_change_log.md). Detailed Given/When/Then criteria live in the user stories ([06_user_stories.md](06_user_stories.md)). Filter semantics, endpoints and UI details are refined in Phases 8–9.

| FR ID | Functional requirement | BR | Module | Key testable conditions (valid / invalid / missing / boundary) | Stories |
|---|---|---|---|---|---|
| FR-001 | Responsive React app with clear navigation to the 10 sections in `07` | BR-01 | Platform | All 10 sections reachable by keyboard; usable layout at 360 px and 1440 px widths | US-001 |
| FR-002 | FastAPI REST endpoints under `/api/v1` for health, metadata, filters and analytics | BR-01 | Platform | Valid request → 200 + schema; invalid parameter → 422 error envelope; DB down → 503 readiness; OpenAPI published | US-002 |
| FR-003 | Consistent loading, empty, validation and error states | BR-01 | Platform | No data → empty state (never a fake chart); API error → message + retry; invalid filter → inline validation | US-003 |
| FR-004 | Documented date and dimension filters | BR-01 | Platform | Date range inclusive of both ends; start > end rejected; range outside data coverage returns empty state; reset restores defaults | US-004 |
| FR-005 | Display data freshness, source, metric definition and provenance class | BR-01 | Platform | Every KPI/chart shows one of 5 provenance classes; definition opens from KPI dictionary; freshness = last successful ingestion time | US-005 |
| FR-010 | Repeatable Python ingestion of locally supplied Olist files | BR-08 | Data | Configurable path; all 9 files present → load; missing file → fail before any write; no Kaggle credentials needed | US-006 |
| FR-011 | Validate required files, columns, types, candidate keys and relationships | BR-08 | Data / M09 | Missing/extra column detected; duplicate candidate key reported; orphan FK reported with counts | US-007 |
| FR-012 | Preserve raw source data and record ingestion metadata | BR-08 | Data | `raw_*` equals the source row count; audit row with run id, file checksum, row counts, start/end UTC, status | US-008 |
| FR-013 | Transform source data through ordered SQL scripts into analytical tables | BR-08 | Data | Scripts run in numbered order; each fact table has a documented grain and a grain-uniqueness test | US-009 |
| FR-014 | Make rebuild/reload behaviour explicit and safe | BR-08 | Data | Re-run gives identical results (idempotent); partial failure rolls back; destructive reset requires explicit flag and refuses production | US-010 |
| FR-015 | Produce ingestion and data-quality reports | BR-08 | Data / M09 | Report lists every check with pass/fail and affected row counts; generated per run | US-011 |
| FR-020 | Executive commercial KPIs | BR-01 | M01 | KPIs K01–K05 per KPI dictionary; period comparison; decomposition by category/state; values reconcile to SQL reference | US-012, US-013 |
| FR-021 | Customer purchase, cohort and segmentation analysis | BR-02 | M02 | Customer = `customer_unique_id` (RULE-02); cohort boundaries tested; RFM reference date explicit; customer totals reconcile to aggregate | US-014, US-015 |
| FR-022 | Product/category performance analysis | BR-03 | M04 | Ranking grain stated; missing category shown as "unknown"; n < threshold flagged (RULE-14) | US-016 |
| FR-023 | Seller and fulfilment analysis | BR-04 | M05 | Eligible population per metric (RULE-11); missing delivery dates counted, not dropped silently; association language only | US-017, US-018 |
| FR-024 | Financial reconciliation and scenario estimates without unsupported profit claims | BR-05 | M06 | Payment vs item+freight differences shown per order and in total; unavailable costs listed; synthetic costs only in `scenario_*` | US-019, US-020 |
| FR-025 | Data-quality monitoring with downstream impact explanations | BR-08 | M09 | Each failed check names the KPIs affected and the share of rows involved | US-021 |
| FR-026 | Scenario comparison with documented assumptions | BR-06 | M07 | Baseline vs intervention; base/upside/downside; ROI per RULE-20; zero cost → ROI undefined, not infinite; invalid inputs rejected | US-022 |
| FR-027 | Statistical analysis and forecasts only when justified | BR-07 | M08 | Chronological split; beats or is compared against naive/seasonal baseline; intervals shown; assumptions checked before tests | US-023, US-024 |
| FR-028 | Reproducible executive report | BR-09 | M10 | HTML report timestamped; numbers equal API values for same filters; includes limitations and quality warnings | US-025 |
| FR-029 | Power BI model and DAX documentation with reconciliation tests | BR-10 | Power BI | Explicit measures; totals equal API for identical filters/periods; connectivity limits documented | US-026 |
| FR-030 | Synthetic marketing campaign scenario model with methodology and limitations (D-015) | BR-11 | M03 | Synthetic inputs in `scenario_*` with seed; outputs labelled `scenario_output`; no observed CAC/ROAS/lift shown; methodology page present | US-027, US-028 |
| FR-040 | BRD, FRD, user stories, acceptance criteria, process flows, KPI/data dictionaries, RAID and traceability | BR-12 | M09 / BA | Every FR → story → test ID; every KPI → source fields or unsupported/synthetic | US-029 |
| FR-041 | Architecture, data lineage, decisions and limitations | BR-12 | Docs | Lineage from source column to KPI for every canonical KPI | US-030 |
| FR-042 | Learning materials explaining core implementation concepts | BR-12 | Learning | Each topic covers the 12 elements in `instructions/13` and links to real files | US-031 |
| FR-043 | Reproducible setup, test, pipeline and deployment instructions | BR-12 | Docs | Clean-clone run succeeds following README only | US-032 |
