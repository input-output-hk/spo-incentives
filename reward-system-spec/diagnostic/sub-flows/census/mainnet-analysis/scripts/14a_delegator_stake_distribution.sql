-- 14a_delegator_stake_distribution.sql
-- Full delegator stake distribution at epoch 623.
-- Size buckets + Lorenz curve data + concentration metrics.

-- Part 1: Size bucket distribution
WITH deleg_stake AS (
  SELECT
    addr_id,
    SUM(amount) AS stake_lovelace
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY addr_id
),
classified AS (
  SELECT
    addr_id,
    stake_lovelace,
    CASE
      WHEN stake_lovelace < 100000000 THEN '<100'
      WHEN stake_lovelace < 1000000000 THEN '100-1K'
      WHEN stake_lovelace < 10000000000 THEN '1K-10K'
      WHEN stake_lovelace < 100000000000 THEN '10K-100K'
      WHEN stake_lovelace < 1000000000000 THEN '100K-1M'
      WHEN stake_lovelace < 10000000000000 THEN '1M-10M'
      ELSE '10M+'
    END AS size_bucket
  FROM deleg_stake
)
SELECT
  size_bucket,
  COUNT(*) AS delegator_count,
  ROUND(SUM(stake_lovelace) / 1000000) AS total_stake_ada,
  ROUND(AVG(stake_lovelace) / 1000000) AS avg_stake_ada,
  ROUND(MIN(stake_lovelace) / 1000000) AS min_ada,
  ROUND(MAX(stake_lovelace) / 1000000) AS max_ada
FROM classified
GROUP BY size_bucket
ORDER BY
  CASE size_bucket
    WHEN '<100' THEN 1 WHEN '100-1K' THEN 2 WHEN '1K-10K' THEN 3
    WHEN '10K-100K' THEN 4 WHEN '100K-1M' THEN 5 WHEN '1M-10M' THEN 6
    ELSE 7
  END;
