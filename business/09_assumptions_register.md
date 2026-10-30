# 09 — Assumptions Register

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Every assumption has an owner, a validation method and a consequence if wrong. Status: **Open** (unvalidated), **Validated**, **Invalidated**, **Accepted** (cannot be validated; consciously accepted).

| ID | Assumption | Basis | Impact if wrong | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| A-01 | All monetary values are Brazilian reais (BRL) | Public dataset documentation; Brazilian marketplace. No currency column exists (H-04) | All money labels wrong | Cannot be validated from data; consistency of value ranges checked in Phase 2 | SH-02 | Accepted |
| A-02 | Timestamps are Brazilian local time with no timezone stored; Brazil spans several zones and had DST in 2016–2018 | No timezone in headers (H-07) | Sub-day durations could be off by hours; day-level metrics minimally affected | Phase 2: inspect time components; decision D-017 in Phase 3 | SH-08 | Open |
| A-03 | `customer_unique_id` identifies a person; `customer_id` is generated per order | Public dataset documentation; H-06 | Repeat and retention metrics wrong | Phase 2: cardinality of customer_id per order and unique_id per customer_id | SH-06 | Open |
| A-04 | Northstar's revenue = merchandise value of Olist orders (marketplace GMV). Olist's own commission income is not modelled | Simulation design | Misinterpretation as Olist's income | Labelled in UI and docs | SH-09 | Accepted |
| A-05 | Order status values include delivered, shipped, canceled, unavailable, invoiced, processing, created, approved | Public dataset documentation | Revenue/cancellation filters wrong | Phase 2: distinct value profiling | SH-08 | Open |
| A-06 | `payment_value` is the amount paid per payment record and may include freight, instalment effects and vouchers | Public documentation; column names | Reconciliation explanations wrong | Phase 2: compare totals per order (K18) | SH-02 | Open |
| A-07 | Small-sample threshold is 30 orders | Common rule of thumb, not statistically derived | Over- or under-flagging of segments | Revisit after Phase 2 distributions | SH-06 | Open |
| A-08 | Identifiers in Olist are anonymised hashes; no direct personal data | Public dataset documentation | Privacy handling insufficient | Phase 2: inspect identifier formats; review comments may contain free text and are excluded from logs/screenshots | SH-08 | Open |
| A-09 | Each `order_items` row represents one unit (no quantity column) | Header shows no quantity field | K05 and unit metrics wrong | Phase 2: check repeated product rows within orders | SH-04 | Open |
| A-10 | The dataset is a static historical extract; "refresh" means re-ingestion, not live updates | Kaggle distribution | Freshness messaging wrong | Accepted by design | SH-09 | Accepted |
| A-11 | Northstar organisation, stakeholders, AS-IS process and pains are illustrative | Simulation (`11`: do not invent a real company's process) | None if labelled | Labels checked in docs and UI | SH-09 | Accepted |
| A-12 | Synthetic generator parameters (M03, M06, M07) are illustrative and carry no claim about real markets | D-015 | Users may over-trust outputs | Labels, banners, methodology page | SH-03 | Accepted |
| A-13 | Dates near the start and end of the dataset may be sparsely populated | Public documentation | Misleading trends at the edges | Phase 2 date-coverage profiling; RULE-22/23 | SH-06 | Open |
