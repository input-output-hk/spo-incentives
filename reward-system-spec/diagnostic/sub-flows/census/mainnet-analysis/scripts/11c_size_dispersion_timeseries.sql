-- 11c_size_dispersion_timeseries.sql
-- Per-epoch pool size dispersion (mean, stddev, CV) among productive pools.
-- Avoids PERCENTILE_CONT to keep memory usage low.
WITH epoch_pool_stake AS (
  SELECT
    epoch_no,
    pool_id AS pool_hash_id,
    SUM(amount) AS total_stake
  FROM epoch_stake
  WHERE epoch_no BETWEEN 210 AND 623
  GROUP BY epoch_no, pool_id
),

epoch_threshold AS (
  SELECT
    epoch_no,
    SUM(total_stake) / 21600 AS threshold
  FROM epoch_pool_stake
  GROUP BY epoch_no
),

productive AS (
  SELECT e.epoch_no, e.total_stake
  FROM epoch_pool_stake e
  JOIN epoch_threshold t ON t.epoch_no = e.epoch_no
  WHERE e.total_stake >= t.threshold
)

SELECT
  epoch_no,
  COUNT(*) AS pool_count,
  ROUND(AVG(total_stake) / 1000000) AS mean_ada,
  ROUND(STDDEV_SAMP(total_stake) / 1000000) AS stddev_ada,
  ROUND(100.0 * STDDEV_SAMP(total_stake) / NULLIF(AVG(total_stake), 0), 2) AS cv_pct,
  ROUND(MIN(total_stake) / 1000000) AS min_ada,
  ROUND(MAX(total_stake) / 1000000) AS max_ada
FROM productive
GROUP BY epoch_no
ORDER BY epoch_no;
