# 09 — Assumptions Register

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Every assumption has an owner, a validation method and a consequence if wrong. Status: **Open** (unvalidated), **Validated**, **Invalidated**, **Accepted** (cannot be validated; consciously accepted).

| ID | Assumption | Basis | Impact if wrong | Validation | Owner | Status |
|---|---|---|---|---|---|---|
| A-01 | All monetary values are Brazilian reais (BRL) | Public dataset documentation; Brazilian marketplace. No currency column exists (H-04) | All money labels wrong | Cannot be validated from data. Phase 2: max 2 decimals, plausible ranges (price 0.85–6735.0) | SH-02 | Accepted |
| A-02 | Timestamps are Brazilian local time with no timezone stored; Brazil spans several zones and had DST in 2016–2018 | No timezone in headers (H-07) | Sub-day durations could be off by hours; day-level metrics minimally affected | Phase 2: purchase-hour pattern consistent with local time (low 02:00–05:59, high 10:00–21:59) but not proof; decision D-017 in Phase 3 | SH-08 | Open (evidence supports) |
| A-03 | `customer_unique_id` identifies a person; `customer_id` is generated per order | Public dataset documentation; H-06 | Repeat and retention metrics wrong | Phase 2: customer_id 1:1 with orders; 96,096 unique_ids over 99,441 customer_ids | SH-06 | Validated |
| A-04 | Northstar's revenue = merchandise value of Olist orders (marketplace GMV). Olist's own commission income is not modelled | Simulation design | Misinterpretation as Olist's income | Labelled in UI and docs | SH-09 | Accepted |
| A-05 | Order status values include delivered, shipped, canceled, unavailable, invoiced, processing, created, approved | Public dataset documentation | Revenue/cancellation filters wrong | Phase 2: exactly these 8 values observed | SH-08 | Validated |
| A-06 | `payment_value` is the amount paid per payment record and may include freight, instalment effects and vouchers | Public documentation; column names | Reconciliation explanations wrong | Phase 2: payments = price + freight within 0.01 for 98,362 of 98,665 orders | SH-02 | Validated (with exceptions, DQ-16) |
| A-07 | Small-sample threshold is 30 orders | Common rule of thumb, not statistically derived | Over- or under-flagging of segments | Revisit after Phase 2 distributions | SH-06 | Open |
| A-08 | Identifiers in Olist are anonymised hashes; no direct personal data | Public dataset documentation | Privacy handling insufficient | Phase 2: all identifiers are 32-char hex; review free text exists (DQ-20) and is excluded from logs/screenshots | SH-08 | Validated (free-text caveat) |
| A-09 | Each `order_items` row represents one unit (no quantity column) | Header shows no quantity field | K05 and unit metrics wrong | Phase 2: no quantity column; 6,968 orders repeat a product across contiguous item rows | SH-04 | Validated (consistent) |
| A-10 | The dataset is a static historical extract; "refresh" means re-ingestion, not live updates | Kaggle distribution | Freshness messaging wrong | Accepted by design | SH-09 | Accepted |
| A-11 | Northstar organisation, stakeholders, AS-IS process and pains are illustrative | Simulation (`11`: do not invent a real company's process) | None if labelled | Labels checked in docs and UI | SH-09 | Accepted |
| A-12 | Synthetic generator parameters (M03, M06, M07) are illustrative and carry no claim about real markets | D-015 | Users may over-trust outputs | Labels, banners, methodology page | SH-03 | Accepted |
| A-13 | Dates near the start and end of the dataset may be sparsely populated (handled by D-018 / RULE-25) | Public documentation | Misleading trends at the edges | Phase 2: 2016-11 empty; 2016-09/12 near-empty; 2018-09/10 0 delivered (DQ-15) | SH-06 | Validated |
