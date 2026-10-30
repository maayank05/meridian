# Relationship and Join Validation Report (Phase 2)

> Generated 2026-10-31 from the Phase 2 profiler output ([profile_results.json](profile_results.json)). Every number below is copied programmatically from that file.
> Source: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0), files in `data/raw/olist/` (not committed). Raw files were read only; SHA-256 hashes were identical before and after profiling.
> Aggregates only. No customer-, seller- or order-level rows are reproduced. **No KPI values are calculated here** (KPIs are implemented in Phase 4).

## 1. Foreign-key / orphan checks

| Relationship (child → parent) | Child rows checked | Empty FK | Orphan rows | Orphan distinct keys |
|---|---:|---:|---:|---:|
| orders.customer_id -> customers.customer_id | 99,441 | 0 | 0 | 0 |
| customers.customer_id -> orders.customer_id (customers without orders) | 99,441 | 0 | 0 | 0 |
| order_items.order_id -> orders.order_id | 112,650 | 0 | 0 | 0 |
| order_items.product_id -> products.product_id | 112,650 | 0 | 0 | 0 |
| order_items.seller_id -> sellers.seller_id | 112,650 | 0 | 0 | 0 |
| order_payments.order_id -> orders.order_id | 103,886 | 0 | 0 | 0 |
| order_reviews.order_id -> orders.order_id | 99,224 | 0 | 0 | 0 |
| products.product_category_name -> category_translation | 32,341 | 610 | 13 | 2 |
| customers.zip_prefix -> geolocation.zip_prefix | 99,441 | 0 | 278 | 157 |
| sellers.zip_prefix -> geolocation.zip_prefix | 3,095 | 0 | 7 | 7 |
| products.product_id -> order_items.product_id (products never sold) | 32,951 | 0 | 0 | 0 |
| sellers.seller_id -> order_items.seller_id (sellers never selling) | 3,095 | 0 | 0 | 0 |

- **Referential integrity holds for every transactional relationship** (orders, items, payments, reviews, customers, products, sellers): 0 orphans.
- Every product and every seller appears in at least one order item.
- Gaps exist only in reference data: 13 products use 2 untranslated categories; 278 customers (157 prefixes) and 7 sellers have zip prefixes absent from geolocation.
- `geolocation` has no usable key: `zip_code_prefix` repeats (see profiling §9). It cannot be a FK parent without first aggregating it to one row per prefix.

## 2. Cardinalities (observed)

| Relationship | Observed cardinality | Evidence |
|---|---|---|
| customers.customer_id : orders | 1 : 1 | both keys unique, 0 orphans either way |
| customer_unique_id : customer_id | 1 : many | 2,997 people with >1 customer_id |
| orders : order_items | 1 : 0..many | items per order {'1': 88863, '2': 7516, '3': 1322, '4': 505, '5': 204, '6': 256} (top bucket = 6+); 775 orders have none |
| orders : order_payments | 1 : 0..many | payments per order {'1': 96479, '2': 2382, '3': 301, '4': 108, '5': 52, '6': 118} (top bucket = 6+); 1 order has none |
| orders : order_reviews | 1 : 0..many | reviews per order {'1': 98126, '2': 543, '3': 4}; 547 orders have more than one |
| review_id : orders | 1 : 1..3 | 789 review_ids shared |
| orders : sellers (via items) | many : many | 1,278 orders have more than one seller |

## 3. Fan-out and double-counting risks (measured)

| Join | Base rows | Joined rows | Orders affected | Effect on Σ price if summed after join |
|---|---:|---:|---:|---:|
| order_items × order_payments (on order_id) | 112,647 | 117,601 | 2,936 | +4.5441% (overstated) |
| order_items × order_reviews (on order_id) | 111,708 | 112,372 | 544 | +0.4476% (overstated) |
| orders × order_items | 99,441 orders | 112,650 | all multi-item orders | order-level fields (status, dates) repeat per item: counting rows ≠ counting orders |

**Rules confirmed by measurement** (RULE-06):
1. Never sum item values after joining payments or reviews. Aggregate each side to `order_id` first.
2. Count orders with `COUNT(DISTINCT order_id)` whenever items are joined.
3. Review metrics use the `(review_id, order_id)` grain. Shared review_ids must not be double-counted when reviews are counted as unique reviews.
4. Seller-level metrics stay at item grain. Order-level dates (carrier date) are shared by every seller in a multi-seller order.

## 4. Payment ↔ item reconciliation (order level, both sides aggregated first)

| Population | Orders with both | |diff| ≤ 0.01 | Payments higher | Payments lower |
|---|---:|---:|---:|---:|
| All statuses | 98,665 | 98,362 (99.69%) | 264 | 39 |
| Delivered | 96,477 | 96,178 (99.69%) | 260 | 39 |

Orders with items only: 1; payments only: 775; neither: 0. Largest differences: -51.62 to 182.81 (BRL, per order).

- `payment_value` matches `price + freight_value` for nearly all orders. This validates A-06: payments include freight.
- Of the 264 orders where payments exceed items, 249 have a credit-card instalment count above 1 and 7 include a voucher. This is an **association** consistent with instalment charges, not a confirmed cause.
- 39 orders have payments lower than items; 0 of these involve vouchers. The cause is unknown.
- Reconciliation used exact Decimal arithmetic in the independent check (counts matched pandas).
