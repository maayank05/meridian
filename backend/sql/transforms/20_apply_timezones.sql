-- Apply stg_tz_map (filled by Python, D-017) to every converted timestamp column.
-- Ambiguous / non-existent local times keep *_utc = NULL; their status is recorded in *_tz.

UPDATE stg_orders o JOIN stg_tz_map m ON m.local_ts = o.purchase_local
SET o.purchase_utc = m.utc_ts, o.purchase_tz = m.tz_status;

UPDATE stg_orders o JOIN stg_tz_map m ON m.local_ts = o.approved_local
SET o.approved_utc = m.utc_ts, o.approved_tz = m.tz_status;

UPDATE stg_orders o JOIN stg_tz_map m ON m.local_ts = o.delivered_carrier_local
SET o.delivered_carrier_utc = m.utc_ts, o.delivered_carrier_tz = m.tz_status;

UPDATE stg_orders o JOIN stg_tz_map m ON m.local_ts = o.delivered_customer_local
SET o.delivered_customer_utc = m.utc_ts, o.delivered_customer_tz = m.tz_status;

UPDATE stg_order_items i JOIN stg_tz_map m ON m.local_ts = i.shipping_limit_local
SET i.shipping_limit_utc = m.utc_ts, i.shipping_limit_tz = m.tz_status;

UPDATE stg_order_reviews r JOIN stg_tz_map m ON m.local_ts = r.answer_local
SET r.answer_utc = m.utc_ts, r.answer_tz = m.tz_status;
