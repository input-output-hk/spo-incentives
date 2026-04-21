-- 09b_retail_flow_matrix.sql
-- Top 500 retail pool-to-pool flows.

WITH latest_margin AS (
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),
retail_pools AS (
  SELECT pool_hash_id
  FROM latest_margin
  WHERE margin < 0.999
),
ordered_certs AS (
  SELECT
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no,
    d.tx_id,
    LAG(d.pool_hash_id) OVER (PARTITION BY d.addr_id ORDER BY d.active_epoch_no, d.tx_id) AS prev_pool
  FROM delegation d
  WHERE d.pool_hash_id IN (SELECT pool_hash_id FROM retail_pools)
),
switches AS (
  SELECT prev_pool AS from_pool, pool_hash_id AS to_pool
  FROM ordered_certs
  WHERE prev_pool IS NOT NULL
    AND pool_hash_id <> prev_pool
    -- Also require the origin pool to be retail
    AND prev_pool IN (SELECT pool_hash_id FROM retail_pools)
)
SELECT
  ph_from.view AS from_pool_id,
  ph_to.view   AS to_pool_id,
  COUNT(*)      AS flow_count
FROM switches s
JOIN pool_hash ph_from ON ph_from.id = s.from_pool
JOIN pool_hash ph_to   ON ph_to.id   = s.to_pool
GROUP BY ph_from.view, ph_to.view
ORDER BY flow_count DESC
LIMIT 500;
