# 10 — RAID Log (Risks, Assumptions, Issues, Dependencies)

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Likelihood and impact use H / M / L and are qualitative judgements. Assumptions are tracked in detail in [09_assumptions_register.md](09_assumptions_register.md).

## Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R-01 | KPI definitions written before profiling turn out to be wrong (status values, grain, nulls) | M | M | Field names header-verified; value domains flagged "verify in Phase 2"; Phase 2 gate updates the dictionary | SH-09 | Open |
| R-02 | Right-censoring makes recent months look like a decline | H | H | RULE-23 flag; exclude censored months from forecast training | SH-02 | Open |
| R-03 | Synthetic marketing or cost figures are mistaken for real performance | M | H | RULE-16/17; banners; separate tables; tests for labels | SH-03 | Open |
| R-04 | Public repository accidentally exposes data, secrets or personal details | L | H | `.gitignore`; staged-content scans before every commit; noreply author email | SH-09 | Open |
| R-05 | Dependency incompatibility with Python 3.13 | L | M | Compatibility verification before locking (D-002 condition) | SH-09 | Open |
| R-06 | Hosted MySQL costs or free-tier limits block persistent deployment | M | M | Provider comparison in Phase 12; budget question Q-6 | SH-09 | Open |
| R-07 | Power BI Service cannot refresh from a private cloud database | H | M | Document limits; Desktop against local or approved endpoint; never expose production DB | SH-06 | Open |
| R-08 | Low repeat purchase rates make cohort/RFM analysis uninformative | M | M | Report honestly; adjust segmentation after Phase 2 | SH-03 | Open |
| R-09 | Large files exceed memory on a 7.7 GB machine | L | M | Chunked ingestion | SH-08 | Open |
| R-10 | Scope creep from ten modules delays a working core | M | H | Phase gates; core data and KPI reliability before ML/UI polish | SH-09 | Open |

## Issues (current, observed)

| ID | Issue | Evidence | Resolution plan | Status |
|---|---|---|---|---|
| I-01 | Misspelled source columns `product_name_lenght`, `product_description_lenght` | H-01 | Rename in `stg_*`; keep raw names in `raw_*` | Open |
| I-02 | UTF-8 BOM at start of `product_category_name_translation.csv` | H-02 | Decode with BOM handling; test with a BOM fixture | Open |
| I-03 | Mixed CRLF/LF line endings across files | H-03 | Parser accepts both; fixture coverage | Open |
| I-04 | No currency or timezone metadata in source | H-04, H-07 | A-01 accepted; A-02 → D-017 in Phase 3 | Open |
| I-05 | Canonical revenue definition not yet approved | D-016 | Approved: Option A, "Delivered Merchandise Value (Revenue Proxy)" | Resolved 2026-10-31 |

## Dependencies

| ID | Dependency | Needed by | Owner | Status |
|---|---|---|---|---|
| DEP-01 | User approval of D-016 (revenue definition) | Phase 4 metric implementation | SH-09 | Closed 2026-10-31 (Option A approved) |
| DEP-02 | Local MySQL `meridian_dev` / `meridian_test` databases, app user and `.env` (Q-5) | Phase 3 | SH-09 | Open |
| DEP-03 | Power BI Desktop authoring by the project owner (D-012) | Phase 10 | SH-09 | Open |
| DEP-04 | GitHub repository and Actions (public, https://github.com/maayank05/meridian) | Phase 12 CI | SH-09 | Repository exists |
| DEP-05 | Managed MySQL provider and budget (D-011, Q-6) | Phase 12 | SH-09 | Open |
| DEP-06 | Olist dataset in `data/raw/olist/` | Phase 2 | SH-09 | Present (headers verified 2026-10-31) |
