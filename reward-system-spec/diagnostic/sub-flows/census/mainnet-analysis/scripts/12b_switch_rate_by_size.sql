-- 12b_switch_rate_by_size.sql
-- Average number of pool switches per delegator, bucketed by stake size.
-- Also: share of delegators who have NEVER switched.

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LAG(pool_hash_id) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS prev_pool
  FROM delegation
),

switch_count AS (
  SELECT
    addr_id,
    COUNT(*) FILTER (WHERE prev_pool IS NOT NULL AND pool_hash_id <> prev_pool) AS switches,
    COUNT(*) AS total_certs
  FROM ordered_certs
  GROUP BY addr_id
),

stake_size AS (
  SELECT addr_id, SUM(amount) AS stake_lovelace
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY addr_id
),

classified AS (
  SELECT
    sc.addr_id,
    sc.switches,
    sc.total_certs,
    COALESCE(ss.stake_lovelace, 0) AS stake,
    CASE
      WHEN COALESCE(ss.stake_lovelace, 0) < 1000000000 THEN '<1K'
      WHEN ss.stake_lovelace < 10000000000 THEN '1K-10K'
      WHEN ss.stake_lovelace < 100000000000 THEN '10K-100K'
      WHEN ss.stake_lovelace < 1000000000000 THEN '100K-1M'
      ELSE '1M+'
    END AS size_bucket
  FROM switch_count sc
  LEFT JOIN stake_size ss ON ss.addr_id = sc.addr_id
)

SELECT
  size_bucket,
  COUNT(*) AS delegator_count,
  ROUND(SUM(stake) / 1000000) AS total_stake_ada,
  ROUND(AVG(switches), 2) AS avg_switches,
  ROUND(100.0 * COUNT(*) FILTER (WHERE switches = 0) / COUNT(*), 1) AS pct_never_switched,
  ROUND(100.0 * COUNT(*) FILTER (WHERE switches >= 3) / COUNT(*), 1) AS pct_frequent_switcher
FROM classified
GROUP BY size_bucket
ORDER BY
  CASE size_bucket
    WHEN '<1K' THEN 1
    WHEN '1K-10K' THEN 2
    WHEN '10K-100K' THEN 3
    WHEN '100K-1M' THEN 4
    ELSE 5
  END;
