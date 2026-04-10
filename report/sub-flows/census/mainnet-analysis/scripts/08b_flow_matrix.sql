-- 08b_flow_matrix.sql
-- Top 500 pool-to-pool delegation flows (by number of addresses switching).
-- Joins to pool_hash to get the bech32 pool IDs.

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LAG(pool_hash_id) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS prev_pool
  FROM delegation
),
switches AS (
  SELECT prev_pool AS from_pool, pool_hash_id AS to_pool
  FROM ordered_certs
  WHERE prev_pool IS NOT NULL
    AND pool_hash_id <> prev_pool
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
