-- 11a_pool_size_variability.sql
-- Per-pool stake variability over the last year (~73 epochs: 551–623).
-- Lightweight version: avoids large sort spills.
WITH yearly_stake AS (
  SELECT
    pool_id AS pool_hash_id,
    epoch_no,
    SUM(amount) AS total_stake
  FROM epoch_stake
  WHERE epoch_no BETWEEN 551 AND 623
  GROUP BY pool_id, epoch_no
),

pool_stats AS (
  SELECT
    pool_hash_id,
    COUNT(*) AS epoch_count,
    AVG(total_stake) AS mean_stake,
    STDDEV_SAMP(total_stake) AS stddev_stake,
    MIN(total_stake) AS min_stake,
    MAX(total_stake) AS max_stake
  FROM yearly_stake
  GROUP BY pool_hash_id
  HAVING COUNT(*) >= 10
)

SELECT
  ph.view AS pool_id,
  ps.epoch_count,
  ROUND(ps.mean_stake / 1000000) AS mean_stake_ada,
  ROUND(COALESCE(ps.stddev_stake, 0) / 1000000) AS stddev_ada,
  ROUND(100.0 * COALESCE(ps.stddev_stake, 0) / NULLIF(ps.mean_stake, 0), 2) AS cv_pct,
  ROUND(ps.min_stake / 1000000) AS min_ada,
  ROUND(ps.max_stake / 1000000) AS max_ada,
  ROUND(100.0 * (ps.max_stake - ps.min_stake) / NULLIF(ps.max_stake, 0), 2) AS range_pct
FROM pool_stats ps
JOIN pool_hash ph ON ph.id = ps.pool_hash_id
ORDER BY cv_pct DESC;
