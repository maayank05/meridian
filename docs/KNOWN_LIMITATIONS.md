# Known Limitations

Last updated: 2026-10-31 (Phase 0). Items marked *(expected)* come from public dataset documentation and the instruction pack; they will be confirmed or corrected against the real files in Phase 2.

## Source-data limitations
- L-S01 *(expected)* Olist has no COGS, operating expenses, marketing spend, campaign attribution, inventory snapshots or experiment assignments. Profit, CAC, ROAS, lift and stock metrics cannot be observed.
- L-S02 *(expected)* `customer_id` is generated per order; customer-level/repeat analysis must use `customer_unique_id`. To verify.
- L-S03 *(expected)* Limited time coverage (~2016–2018) with sparse early and late months — constrains seasonal forecasting and period comparisons.
- L-S04 *(expected)* Refund/return semantics are not explicitly provided; cancellation is only an order status.
- L-S05 Dataset was downloaded manually by the user to `data/raw/olist/` (9 CSVs present 2026-10-31). Not yet profiled (Phase 2).
- L-S06 Olist licence is CC BY-NC-SA 4.0 (verified by project owner 2026-10-31): attribution required, non-commercial use only, share-alike. Raw data is never committed. MIT applies only to MERIDIAN's own code/docs.

## Metric limitations
- L-M01 No KPI is defined yet. Canonical revenue definition (statuses and fields included) is a Phase 1 deliverable.
- L-M02 Payments vs order-item totals are expected to differ (instalments/vouchers/freight); differences will be shown, not hidden.

## Statistical / model limitations
- L-A01 No defensible churn label exists by default; any inactivity model requires an explicit observation window and cutoff (M02/M08).

## Synthetic assumptions
- L-Y01 None created yet. M03 will use a synthetic campaign scenario model (D-015); it never represents actual marketing performance. Any future cost/budget/marketing tables will live in `scenario_*` tables with seed, distributions and rationale documented.

## Technical / deployment limitations
- L-T01 Docker and WSL are not installed; local MySQL runs as the native Windows service `MySQL80` (8.0.38). Production parity with Linux is achieved via GitHub Actions instead of local containers.
- L-T02 `mysql` client is not on PATH (`C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` exists); scripts will reference it explicitly or use Python.
- L-T03 Default `python` on PATH is 3.11 without pip; project must use `py -3.13` (D-002).
- L-T04 `gh` CLI not installed. Remote is https://github.com/maayank05/meridian (public); pushes use plain `git` over HTTPS with the user's own Git credential manager. Claude cannot verify GitHub Actions runs without `gh` or the web UI.
- L-T05 Render has no native managed MySQL; production DB provider and cost undecided (D-011, Q-6).
- L-T06 Machine has 7.7 GB RAM; large files (geolocation) must be ingested in chunks.

## Power BI connectivity limitations
- L-P01 Claude cannot operate the Power BI Desktop GUI; PBIX authoring and screenshots need the user (D-012).
- L-P02 Power BI Service refresh from a private cloud MySQL is not automatic (gateway/networking) — to be researched in Phase 10/12.

## Deferred features
- None deferred yet.

## Known defects
- None (no code exists).
