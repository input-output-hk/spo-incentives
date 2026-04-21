-- 11b_variability_distribution.sql
-- CV distribution among productive pools over 1 year.
WITH yearly_stake AS (
  SELECT
    pool_id AS pool_hash_id,
    epoch_no,
    SUM(amount) AS total_stake
  FROM epoch_stake
  WHERE epoch_no BETWEEN 551 AND 623
  GROUP BY pool_id, epoch_no
),

prod_threshold AS (
  SELECT SUM(amount) / 21600 AS threshold
  FROM epoch_stake
  WHERE epoch_no = 623
),

pool_stats AS (
  SELECT
    pool_hash_id,
    COUNT(*) AS epoch_count,
    AVG(total_stake) AS mean_stake,
    STDDEV_SAMP(total_stake) AS stddev_stake
  FROM yearly_stake
  GROUP BY pool_hash_id
  HAVING COUNT(*) >= 10
),

productive_cv AS (
  SELECT
    ps.pool_hash_id,
    100.0 * COALESCE(ps.stddev_stake, 0) / NULLIF(ps.mean_stake, 0) AS cv_pct
  FROM pool_stats ps
  CROSS JOIN prod_threshold pt
  WHERE ps.mean_stake >= pt.threshold
),

bucketed AS (
  SELECT
    CASE
      WHEN cv_pct <= 5  THEN '0-5%'
      WHEN cv_pct <= 10 THEN '5-10%'
      WHEN cv_pct <= 20 THEN '10-20%'
      WHEN cv_pct <= 50 THEN '20-50%'
      WHEN cv_pct <= 100 THEN '50-100%'
      ELSE '100%+'
    END AS cv_bucket,
    cv_pct
  FROM productive_cv
)

SELECT
  cv_bucket,
  COUNT(*) AS pool_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
  ROUND(AVG(cv_pct), 2) AS avg_cv_in_bucket
FROM bucketed
GROUP BY cv_bucket
ORDER BY
  CASE cv_bucket
    WHEN '0-5%' THEN 1 WHEN '5-10%' THEN 2 WHEN '10-20%' THEN 3
    WHEN '20-50%' THEN 4 WHEN '50-100%' THEN 5 ELSE 6
  END;
