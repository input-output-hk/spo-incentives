-- 10_switch_motivation.sql
-- For each redelegation, compare origin pool vs destination pool characteristics
-- at the epoch of the switch. Aggregates into a motivation profile.
--
-- Characteristics compared:
--   - margin (lower = better for delegator)
--   - pool size / saturation (proxy for ROS stability)
--   - entity type (SPO vs MPO, via pool count per entity)
--
-- Output: one row per switch with directional flags, then aggregated.
-- Expected runtime: 2-5 minutes (window function + joins).

WITH pool_params AS (
  -- Latest pool parameters at or before each epoch.
  -- Using registered_tx_id ordering as proxy for time.
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin,
    fixed_cost
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),

-- Pool size at epoch 623 (latest complete)
pool_size AS (
  SELECT
    pool_id AS pool_hash_id,
    SUM(amount) AS total_stake,
    COUNT(DISTINCT addr_id) AS delegator_count
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY pool_id
),

-- Identify multi-pool operators: pools sharing an owner key
pool_owner_count AS (
  SELECT
    po.pool_update_id,
    pu.hash_id AS pool_hash_id
  FROM pool_owner po
  JOIN pool_update pu ON pu.id = po.pool_update_id
),

-- Ordered delegation certificates with previous pool
ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LAG(pool_hash_id) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS prev_pool
  FROM delegation
),

-- Only switches (different pool)
switches AS (
  SELECT
    addr_id,
    prev_pool AS from_pool,
    pool_hash_id AS to_pool,
    active_epoch_no
  FROM ordered_certs
  WHERE prev_pool IS NOT NULL
    AND pool_hash_id <> prev_pool
    AND active_epoch_no BETWEEN 210 AND 623
),

-- Enrich with pool characteristics
enriched AS (
  SELECT
    s.active_epoch_no,
    -- Margin direction
    CASE
      WHEN pp_to.margin < pp_from.margin THEN 'lower_margin'
      WHEN pp_to.margin > pp_from.margin THEN 'higher_margin'
      ELSE 'same_margin'
    END AS margin_direction,
    -- Size direction
    CASE
      WHEN ps_to.total_stake > ps_from.total_stake * 1.1 THEN 'to_larger'
      WHEN ps_to.total_stake < ps_from.total_stake * 0.9 THEN 'to_smaller'
      ELSE 'similar_size'
    END AS size_direction,
    -- Margin buckets
    CASE
      WHEN pp_from.margin <= 0.02 THEN 'competitive'
      WHEN pp_from.margin <= 0.05 THEN 'moderate'
      WHEN pp_from.margin < 0.999 THEN 'high'
      ELSE 'private'
    END AS from_margin_bucket,
    CASE
      WHEN pp_to.margin <= 0.02 THEN 'competitive'
      WHEN pp_to.margin <= 0.05 THEN 'moderate'
      WHEN pp_to.margin < 0.999 THEN 'high'
      ELSE 'private'
    END AS to_margin_bucket
  FROM switches s
  LEFT JOIN pool_params pp_from ON pp_from.pool_hash_id = s.from_pool
  LEFT JOIN pool_params pp_to   ON pp_to.pool_hash_id   = s.to_pool
  LEFT JOIN pool_size ps_from   ON ps_from.pool_hash_id  = s.from_pool
  LEFT JOIN pool_size ps_to     ON ps_to.pool_hash_id    = s.to_pool
)

SELECT
  margin_direction,
  size_direction,
  COUNT(*) AS switch_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM enriched
GROUP BY margin_direction, size_direction
ORDER BY switch_count DESC;
