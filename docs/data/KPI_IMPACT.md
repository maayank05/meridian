# Impact of Phase 2 Profiling on KPI Definitions

Generated 2026-10-31 from [profile_results.json](profile_results.json). **No KPI values are calculated.** This document records whether each definition in [08_kpi_dictionary.md](../../business/08_kpi_dictionary.md) still holds against the observed data.

| KPI | Result | Evidence and consequence |
|---|---|---|
| K01 | Confirmed | `delivered` exists (96,478 orders, spelling verified). Delivered orders all have items. 8 delivered orders lack a delivery date but remain in K01 (status-based, D-016). Months 2018-09/10 contain 0 delivered orders and 2016-09/11/12 are sparse, so trend displays need D-018 |
| K02 | Confirmed | Freight never negative; 383 item rows have freight 0 (valid value) |
| K03 | Confirmed | order_id unique; use COUNT(DISTINCT order_id) when items are joined (measured fan-out) |
| K04 | Confirmed | Item-level numerator and order-level denominator from the same delivered population; no zero prices |
| K05 | Confirmed | No quantity column; order_item_id is contiguous 1..n; 6,968 orders repeat a product across rows, consistent with row = unit (A-09) |
| K06 | Confirmed | 99,441 orders, no missing purchase timestamps |
| K07 | Confirmed (risk) | customer_unique_id validated as person key; 93,099 of 96,096 people map to a single customer_id (one order of any status). Repeat behaviour will be sparse (R-08) |
| K08 | Confirmed (risk) | As K07; cohort cells will be sparse; censoring at the data end (D-018) |
| K09 | Confirmed (risk) | Frequency will be 1 for most customers; RFM scoring method must handle ties (Phase 5) |
| K10 | Confirmed | No change |
| K11 | Confirmed | 610 products → 'unknown'; 2 untranslated categories (13 products) keep Portuguese names |
| K12 | Resolved (D-019a): `canceled` only | `canceled` spelling verified (625 orders). `unavailable` (609) is a separate status; 603 of these orders have no items |
| K13 | Resolved (D-019b): mean per order; 1,412 orders non-independent | Score range 1–5 verified, no missing scores. `review_id` is not unique (789 review_ids shared across orders, identical content); 547 orders have more than one review; 5,127 reviews were created before delivery |
| K14 | Confirmed | Eligible population (RULE-11) = 96,470 delivered orders with a delivery date; 0 delivered-before-purchase violations |
| K15 | Confirmed | order_estimated_delivery_date is date-only (100% midnight), so RULE-12's calendar-date comparison is appropriate |
| K16 | Confirmed | As K15 |
| K17 | Resolved (D-019c): retained, low-confidence label, RULE-27 exclusions | Carrier date is order-level and 1,278 orders have several sellers; 1,359 carrier-before-approval and 166 carrier-before-purchase violations; 4 shipping-limit dates after 2018 |
| K18 | Confirmed | payment_value ≈ price + freight for 98,362 of 98,665 orders with both sides (A-06 validated); 775 orders have payments but no items; 1 delivered order has items but no payments |
| K19 | Confirmed | 5 payment types verified incl. `not_defined` (3 records, all zero value) |
| K20 | Resolved (D-019d): 2 invalid records excluded and reported | 2 credit-card records have 0 instalments (invalid); instalments > 1 only for credit_card |
| K21 | Confirmed | As K07 |
| K22 | Confirmed | Every seller has at least one item (0 sellers never selling) |
| K23 | Confirmed | As K22 |
| K24 | Confirmed | The 23 issues in the DQ register define the first set of checks for Phase 3 |
| K25 | Constrained; window fixed (D-018) | Only 20 months (2017-01 to 2018-08) have substantial volume, so annual seasonality cannot be estimated reliably (less than two full cycles). A seasonal-naive baseline is still possible |

| K26 | New (CR-004) | Unavailable Order Rate, reported separately from K12: 609 `unavailable` orders in the profiled data |

Y-series (synthetic/scenario) definitions are unaffected, except that their observed baselines inherit the D-018 window. U-series (unsupported) are unchanged: profiling found no cost, marketing, inventory, refund or session data.

## Decisions (approved 2026-10-31)
- **D-018** Default analysis window 2017-01-01 to 2018-08-31 (RULE-25).
- **D-019** (a) K12 `canceled` only + K26; (b) K13 mean per order, non-independence documented (RULE-15); (c) K17 low confidence + RULE-27 exclusions; (d) K20 RULE-28 exclusion with count.
