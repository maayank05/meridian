# Known Limitations

Last updated: 2026-10-31 (Phase 0). Items marked *(expected)* come from public dataset documentation and the instruction pack; they will be confirmed or corrected against the real files in Phase 2.

## Source-data limitations
- L-S01 *(verified by headers and profiling)* Olist has no COGS, operating expenses, marketing spend, campaign attribution, inventory snapshots or experiment assignments. Profit, CAC, ROAS, lift and stock metrics cannot be observed.
- L-S02 *(verified)* `customer_id` is one-per-order; customer-level and repeat analysis must use `customer_unique_id`.
- L-S03 *(verified)* Purchases span 2016-09 to 2018-10, but 2016-11 is empty, 2016-09/12 are near-empty and 2018-09/10 have no delivered orders. Only 20 months (2017-01 to 2018-08) carry substantial volume, which limits seasonal forecasting (D-018).
- L-S04 *(verified)* No refund or return fields exist; cancellation is only an order status.
- L-S08 23 data-quality issues are logged in [DATA_QUALITY_ISSUES.md](data/DATA_QUALITY_ISSUES.md), the most material being non-unique `review_id` (DQ-01), geolocation duplicates (DQ-03) and coverage edges (DQ-15).
- L-S05 Dataset was downloaded manually by the user to `data/raw/olist/` (9 CSVs present 2026-10-31). Not yet profiled (Phase 2).
- L-S07 Header-level source facts (2026-10-31): misspelled columns `product_name_lenght`/`product_description_lenght`; UTF-8 BOM in the category translation file; mixed CRLF/LF line endings; no currency, timezone, quantity, cost, marketing, inventory or refund columns ([SOURCE_HEADERS](data/SOURCE_HEADERS.md)).
- L-S06 Olist licence is CC BY-NC-SA 4.0 (verified by project owner 2026-10-31): attribution required, non-commercial use only, share-alike. Raw data is never committed. MIT applies only to MERIDIAN's own code/docs.

## Metric limitations
- L-M01 25 observed/derived KPIs, 8 synthetic/scenario metrics and 10 unsupported metrics are defined in [08_kpi_dictionary.md](../business/08_kpi_dictionary.md). None is calculated yet. Value domains (status values etc.) are unverified until Phase 2.
- L-M04 Default analysis window 2017-01 to 2018-08 (D-018): 20 months, limiting seasonal modelling. Out-of-window months are visible but flagged.
- L-M05 K13 review score: 1,412 orders share review records with other orders (non-independent). K17 is low confidence (order-level carrier date; RULE-27 exclusions). K20 excludes 2 invalid records.
- L-M03 Canonical revenue is a **proxy** (D-016): "Delivered Merchandise Value (Revenue Proxy)" = item price of delivered orders by purchase date. It is not audited accounting revenue or profit. Refunds, returns, chargebacks, voucher/discount and other accounting adjustments are unavailable. Freight is excluded (reported as K02). Recent periods are understated by right-censoring and must carry a warning.
- L-M02 Payments vs order-item totals are expected to differ (instalments/vouchers/freight); differences will be shown, not hidden.

## Statistical / model limitations
- L-A01 No defensible churn label exists by default; any inactivity model requires an explicit observation window and cutoff (M02/M08).

## Synthetic assumptions
- L-Y01 None created yet. M03 will use a synthetic campaign scenario model (D-015); it never represents actual marketing performance. Any future cost/budget/marketing tables will live in `scenario_*` tables with seed, distributions and rationale documented.

## Technical / deployment limitations
- L-T01 Docker and WSL are not installed; local MySQL runs as the native Windows service `MySQL80` (8.0.38). Production parity with Linux is achieved via GitHub Actions instead of local containers.
- L-T02 `mysql` client is not on PATH (`C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` exists); scripts will reference it explicitly or use Python.
- L-T03 Default `python` on PATH is 3.11 without pip; project must use `py -3.13` (D-002).
- L-T04 `gh` CLI not installed. Remote is https://github.com/maayank05/meridian (public); pushes use plain `git` over HTTPS with the user's own Git credential manager. GitHub Actions runs are checked in the GitHub web UI.
- L-T05 Render has no native managed MySQL; production DB provider and cost undecided (D-011, Q-6).
- L-T07 Source timezone is inferred as America/Sao_Paulo (D-017). 39 ambiguous DST fall-back timestamps have no UTC value and are excluded from duration KPIs.
- L-T06 Machine has 7.7 GB RAM; large files (geolocation) must be ingested in chunks.

## Power BI connectivity limitations
- L-P01 The Power BI Desktop GUI cannot be automated in this setup; PBIX authoring and screenshots need the owner (D-012).
- L-P02 Power BI Service refresh from a private cloud MySQL is not automatic (gateway/networking) — to be researched in Phase 10/12.

## Deferred features
- None deferred yet.

## Milestone A limitations
- L-A02 Full refresh only (no incremental loads); a full run takes about 4.5 minutes on this machine.
- L-A03 Local MySQL TLS certificates are not verified (D-020); acceptable only for a local server.
- L-A04 Geolocation is reduced to one mean coordinate per zip prefix inside the Brazil bounding box (duplicates included in the mean).
- L-A05 85 `review_creation_date` values carry a non-midnight time but are stored as DATE (D-017 T6); counted in the DQ results.
- L-A06 Repeat-load idempotency and rebuild determinism are proven on the fixture; the full dataset was loaded once.

## Milestone B limitations
- L-B01 The forecast model does not beat the naive baseline; forecasts use the naive method and cover months outside the data (unverifiable).
- L-B02 K09 RFM and K17 seller-handover KPIs are not implemented (D-021).
- L-B03 MySQL `SUM()` over boolean expressions returns DECIMAL; consumers must convert counts to integers (handled in services; API in Milestone C).
- L-B04 Simulator and campaign outputs depend entirely on user-entered synthetic assumptions (margin, uplift, lift, attribution) and are never results.

## Milestone C limitations
- L-C01 Customers endpoint takes about 1.8 s on the full data (NFR-003 target 1.5 s); other endpoints are under 0.3 s.
- L-C02 A full reload takes about 7.5 minutes (first load into empty tables about 4.5 minutes). Profiling (D-023): deleting the previous load is the largest step; kept for rollback safety.
- L-C03 Filters are period-only (whole months); no category or state filters.
- L-C04 Executive report is HTML only (no PDF); no authentication (local, read-only data).
- L-C05 Frontend bundle 680 kB (charts library); no code splitting.
- L-C06 Resolved: minimatch advisory fixed with an npm override (D-023); `npm audit` reports 0 vulnerabilities.
- L-C07 No automated accessibility audit has been run.

## Milestone D limitations
- L-D01 No Power BI `.pbix` is included; it must be built in Power BI Desktop from the specification.
- L-D02 No hosted deployment (Render and managed MySQL deferred: no paid services). Local execution only.
- L-D03 Playwright E2E runs locally only (needs the licensed dataset); CI covers everything else.

## Phase 2 tooling notes
- Profiling ran in a throwaway scratch environment (Python 3.13.2, pandas 3.1.0, numpy 2.5.4). These versions installed and ran correctly; this is early evidence for D-002/D-003 compatibility, not the locked project environment (Phase 3).
- The profiler scripts are committed under `scripts/profiling/` (Milestone A) with fixture tests and a reproduction guide.

## Known defects
- None (no code exists).
