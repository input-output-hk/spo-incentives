-- 14c_concentration_metrics.sql
-- Concentration metrics: Gini, top-N shares, median, percentiles.

WITH deleg_stake AS (
  SELECT
    addr_id,
    SUM(amount) AS stake
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY addr_id
),
stats AS (
  SELECT
    COUNT(*) AS n,
    SUM(stake) AS total,
    AVG(stake) AS mean_stake,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY stake) AS median_stake,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY stake) AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY stake) AS p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY stake) AS p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY stake) AS p99
  FROM deleg_stake
),
-- Top-N concentration
top_shares AS (
  SELECT
    SUM(CASE WHEN rn <= 100 THEN stake ELSE 0 END) AS top100_stake,
    SUM(CASE WHEN rn <= 1000 THEN stake ELSE 0 END) AS top1000_stake,
    SUM(CASE WHEN rn <= 10000 THEN stake ELSE 0 END) AS top10000_stake,
    SUM(stake) AS total
  FROM (
    SELECT stake, ROW_NUMBER() OVER (ORDER BY stake DESC) AS rn
    FROM deleg_stake
  ) r
)
SELECT
  s.n AS delegator_count,
  ROUND(s.total / 1000000) AS total_stake_ada,
  ROUND(s.mean_stake / 1000000) AS mean_ada,
  ROUND(s.median_stake / 1000000) AS median_ada,
  ROUND(s.p75 / 1000000) AS p75_ada,
  ROUND(s.p90 / 1000000) AS p90_ada,
  ROUND(s.p95 / 1000000) AS p95_ada,
  ROUND(s.p99 / 1000000) AS p99_ada,
  ROUND(100.0 * t.top100_stake / t.total, 2) AS top100_pct,
  ROUND(100.0 * t.top1000_stake / t.total, 2) AS top1000_pct,
  ROUND(100.0 * t.top10000_stake / t.total, 2) AS top10000_pct
FROM stats s, top_shares t;
