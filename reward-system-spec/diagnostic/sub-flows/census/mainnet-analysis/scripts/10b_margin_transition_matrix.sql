-- 10b_margin_transition_matrix.sql
-- Margin bucket transition matrix: when delegators switch, which margin band
-- do they leave and which do they enter?

WITH pool_params AS (
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),

ordered_certs AS (
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
    AND active_epoch_no BETWEEN 210 AND 623
),

classified AS (
  SELECT
    CASE
      WHEN pp_from.margin IS NULL THEN 'unknown'
      WHEN pp_from.margin <= 0.02 THEN '0-2%'
      WHEN pp_from.margin <= 0.05 THEN '2-5%'
      WHEN pp_from.margin <= 0.10 THEN '5-10%'
      WHEN pp_from.margin < 0.999 THEN '10-99%'
      ELSE '100%'
    END AS from_band,
    CASE
      WHEN pp_to.margin IS NULL THEN 'unknown'
      WHEN pp_to.margin <= 0.02 THEN '0-2%'
      WHEN pp_to.margin <= 0.05 THEN '2-5%'
      WHEN pp_to.margin <= 0.10 THEN '5-10%'
      WHEN pp_to.margin < 0.999 THEN '10-99%'
      ELSE '100%'
    END AS to_band
  FROM switches s
  LEFT JOIN pool_params pp_from ON pp_from.pool_hash_id = s.from_pool
  LEFT JOIN pool_params pp_to   ON pp_to.pool_hash_id   = s.to_pool
)

SELECT
  from_band,
  to_band,
  COUNT(*) AS flow_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM classified
GROUP BY from_band, to_band
ORDER BY flow_count DESC;
