# Data-Quality Issue Register (Phase 2)

> Generated 2026-10-31 from the Phase 2 profiler output ([profile_results.json](profile_results.json)). Every number below is copied programmatically from that file.
> Source: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0), files in `data/raw/olist/` (not committed). Raw files were read only; SHA-256 hashes were identical before and after profiling.
> Aggregates only. No customer-, seller- or order-level rows are reproduced. **No KPI values are calculated here** (KPIs are implemented in Phase 4).

Severity: **High** = can materially distort a headline KPI if unhandled; **Medium** = distorts a specific KPI or segment; **Low** = limited or reference-data impact; **Info** = structural fact requiring a modelling rule. "Treatment" entries are proposals implemented in Phase 3 ingestion/staging (raw data is never altered).

| ID | Severity | Table(s) | Issue (evidence) | Affected KPIs | Proposed treatment | Status |
|---|---|---|---|---|---|---|
| DQ-01 | High | order_reviews | `review_id` not unique: 789 review_ids shared by up to 3 orders (814 extra rows); duplicates carry identical score/text/date | K13 | Key on (review_id, order_id). Decide review-count semantics (D-019) | Open |
| DQ-02 | Medium | order_reviews | 547 orders have more than one review | K13 | RULE-15 order-level mean; D-019 | Open |
| DQ-03 | Medium | geolocation | 261,831 exact duplicate rows; zip prefix not unique (19,015 prefixes, up to 1146 rows each); 8,556 prefixes with multiple city spellings | Geo views only | Keep raw; stg aggregates to one row per prefix (e.g. median lat/lng) — Phase 3 decision | Open |
| DQ-04 | Low | geolocation | 42 rows outside the Brazil bounding box | Geo views only | Flag and exclude from coordinate aggregation | Open |
| DQ-05 | Low | customers, sellers | 278 customers and 7 sellers have zip prefixes absent from geolocation | Geo views only | Soft relationship; report unmatched; state fields remain usable | Open |
| DQ-06 | Medium | products | 610 products lack category, name length, description length and photo count; 2 lack weight/dimensions; 4 weigh 0 g | K11, M04 | Category 'unknown' (RULE-13); attributes NULL, never 0 | Open |
| DQ-07 | Low | products | Untranslated categories: {'pc_gamer': 3, 'portateis_cozinha_e_preparadores_de_alimentos': 10} | K11 | Keep Portuguese name, flag (RULE-13) | Open |
| DQ-08 | Medium | orders/order_items | 775 orders have no items: {'unavailable': 603, 'canceled': 164, 'created': 5, 'invoiced': 2, 'shipped': 1} | K03, K06, K12, K18 | Expected for unavailable/canceled; excluded from item metrics; counted in K06/K12 | Open |
| DQ-09 | Low | orders/order_payments | 1 delivered order has no payment records | K18, K19 | Reconciliation category 'items only' | Open |
| DQ-10 | Medium | orders | Delivered orders missing timestamps: customer delivery 8, carrier 2, approved 14 | K14–K17 | Excluded from delivery metrics and counted (RULE-11); still included in K01 (status-based) | Open |
| DQ-11 | Low | orders | Non-delivered orders with a customer delivery date: {'canceled': 6} | K14–K16 | Status governs eligibility; report | Open |
| DQ-12 | Medium | orders | Date-order violations: carrier before purchase 166, carrier before approval 1,359, delivered before carrier 23 | K17 | Flag rows; K17 confidence reduced. No purchase→delivery violations | Open |
| DQ-13 | Low | order_items | `shipping_limit_date` outliers: 4 rows after 2018-12-31 (max 2020-04-09 22:35:08); 12 rows > 60 days after purchase | K17 | Flag as implausible; exclude from K17 | Open |
| DQ-14 | Medium | order_reviews | 5,127 reviews created before delivery; 64 before purchase date | K13 | Report; reviews before delivery may reflect delay, an association only (RULE-19) | Open |
| DQ-15 | High | orders | Coverage gaps: 2016-11 has 0 orders; 2016-09 (4) and 2016-12 (1) near-empty; 2018-09/10 have 20 orders and 0 delivered (extract cutoff) | K01–K08, K25, all trends | Default analysis window decision (D-018); censoring flag (RULE-23) | Open |
| DQ-16 | Medium | payments vs items | 303 orders differ by > 0.01 (264 higher, 39 lower); range -51.62 to 182.81 | K18 | Show differences; possible explanations labelled unconfirmed | Open |
| DQ-17 | Low | order_payments | Zero-value payments: 9 (not_defined 3, voucher 6); credit-card records with 0 instalments: 2 | K19, K20 | Keep; exclude 0-instalment rows from K20; not_defined shown as own category | Open |
| DQ-18 | Low | order_payments | `payment_sequential` does not start at 1 in 80 orders | K18 | Possibly missing payment records; reconciliation will surface any value gap | Open |
| DQ-19 | Low | order_items | 383 item rows with freight 0 | K02 | Valid value (free shipping plausible); not treated as missing | Open |
| DQ-20 | Medium | order_reviews | Free text: 3,852 messages with line breaks; leading/trailing whitespace in 1,998 titles and 9,451 messages | None (no text KPI) | Quote-aware loader; keep raw text; never log; trim only in staging | Open |
| DQ-21 | Low | products, translation, reviews | Source format quirks: misspelled `*_lenght` columns, UTF-8 BOM in translation file, CRLF in 2 files (H-01–H-03) | Ingestion | BOM-aware decoding; rename in staging; tests with fixtures | Open |
| DQ-22 | Info | customers | 2,997 people have more than one customer_id | K07–K10, K21 | Use customer_unique_id (RULE-02 validated) | Open |
| DQ-23 | Info | order_items | 6,968 orders repeat the same product on several item rows; no quantity column | K05 | Row = unit (A-09 consistent with data) | Open |

Issues previously logged in the RAID log (I-01–I-04) are covered by DQ-21 and A-01/A-02.
