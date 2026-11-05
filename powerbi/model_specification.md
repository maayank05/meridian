# Power BI semantic model specification

Source: MySQL `meridian_dev` (read-only `meridian_reader` account), Import mode. Grain and definitions follow `backend/sql/migrations/0003_marts.sql` and the KPI dictionary (`business/08_kpi_dictionary.md`).

## Tables
| Table | Grain | Key | Provenance | Notes |
|---|---|---|---|---|
| `dim_date` | calendar day 2016-01-01..2020-12-31 | `date_key` | derived | `coverage_flag`: default_window / low_coverage / incomplete_cutoff / outside_source (D-018). Mark as date table |
| `dim_customer` | one row per `customer_id` (= one order) | `customer_id` | source_observed | Person = `customer_unique_id` (RULE-02) |
| `dim_product` | product | `product_id` | source_observed + derived | `category_name_en`: 'unknown' if missing, Portuguese if untranslated (RULE-13) |
| `dim_seller` | seller | `seller_id` | source_observed | |
| `fact_orders` | order | `order_id` | source_observed + derived | Order-level totals pre-aggregated (no fan-out); timestamps local and UTC (D-017) |
| `fact_order_items` | order item (one unit) | `order_id`, `order_item_id` | source_observed | `price`, `freight_value` (BRL) |
| `fact_payments` | payment record | `order_id`, `payment_sequential` | source_observed | `is_invalid_installments` (RULE-28) |
| `fact_reviews` | (`review_id`, `order_id`) | both | source_observed | `is_shared_review` (RULE-15) |
| `agg_kpi_monthly` (optional) | month | `month_start` | derived | Pre-computed copy of the canonical monthly view, for validation |

## Relationships (all single direction, many-to-one)
| From (many) | To (one) |
|---|---|
| `fact_orders[purchase_date]` | `dim_date[date_key]` |
| `fact_orders[customer_id]` | `dim_customer[customer_id]` |
| `fact_order_items[order_id]` | `fact_orders[order_id]` |
| `fact_order_items[product_id]` | `dim_product[product_id]` |
| `fact_order_items[seller_id]` | `dim_seller[seller_id]` |
| `fact_payments[order_id]` | `fact_orders[order_id]` |
| `fact_reviews[order_id]` | `fact_orders[order_id]` |

Date filters flow dim_date → fact_orders → items/payments/reviews. Product and seller filters apply to item-level measures only. Order counts are not filtered by product, because an order can contain several categories (the same rule as the SQL views).

## Provenance in the report
| Class | In Power BI | Label on visuals |
|---|---|---|
| Observed | fact/dim columns | "Observed" |
| Derived | all DAX measures below | "Derived" |
| Synthetic | none imported | n/a (simulator assumptions live in the app only) |
| Forecast | not reproduced | if imported from the app: "Forecast (not observed)" |
| Scenario | not reproduced | if imported: "Scenario (hypothetical)" |

Unsupported metrics (profit, COGS, CAC, ROAS, conversion, churn) must **not** be created: the source has no data for them (KPI dictionary Part D).
