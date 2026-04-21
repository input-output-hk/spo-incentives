-- 10d_loyal_pool_aggregate.sql
-- Aggregate profile: what margin bands and size bands do loyal delegators
-- (tenure >= 201 epochs) concentrate in, vs the overall population?

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LEAD(active_epoch_no) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS next_epoch
  FROM delegation
),

tenures AS (
  SELECT
    addr_id,
    pool_hash_id,
    COALESCE(next_epoch, 624) - active_epoch_no AS tenure_epochs
  FROM ordered_certs
),

pool_params AS (
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),

classified AS (
  SELECT
    t.addr_id,
    t.pool_hash_id,
    t.tenure_epochs,
    CASE
      WHEN t.tenure_epochs >= 201 THEN 'loyal'
      WHEN t.tenure_epochs <= 5   THEN 'volatile'
      ELSE 'moderate'
    END AS delegator_type,
    CASE
      WHEN pp.margin IS NULL THEN 'unknown'
      WHEN pp.margin <= 0.02 THEN '0-2%'
      WHEN pp.margin <= 0.05 THEN '2-5%'
      WHEN pp.margin <= 0.10 THEN '5-10%'
      WHEN pp.margin < 0.999 THEN '10-99%'
      ELSE '100%'
    END AS margin_band
  FROM tenures t
  LEFT JOIN pool_params pp ON pp.pool_hash_id = t.pool_hash_id
)

SELECT
  delegator_type,
  margin_band,
  COUNT(*) AS delegation_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY delegator_type), 2) AS pct_within_type
FROM classified
GROUP BY delegator_type, margin_band
ORDER BY delegator_type, delegation_count DESC;
