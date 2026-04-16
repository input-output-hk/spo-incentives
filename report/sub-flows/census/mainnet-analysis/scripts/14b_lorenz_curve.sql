-- 14b_lorenz_curve.sql
-- Lorenz curve data: cumulative % of delegators vs cumulative % of stake.
-- Output 100 percentile points for smooth plotting.

WITH deleg_stake AS (
  SELECT
    addr_id,
    SUM(amount) AS stake
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY addr_id
),
ranked AS (
  SELECT
    stake,
    ROW_NUMBER() OVER (ORDER BY stake ASC) AS rn,
    COUNT(*) OVER () AS total_n,
    SUM(stake) OVER () AS total_stake
  FROM deleg_stake
),
percentiles AS (
  SELECT
    rn,
    stake,
    total_n,
    total_stake,
    ROUND(100.0 * rn / total_n, 2) AS pct_delegators,
    ROUND(100.0 * SUM(stake) OVER (ORDER BY rn) / total_stake, 4) AS cum_pct_stake
  FROM ranked
),
-- Sample at every 0.1% of delegators (1000 points)
sampled AS (
  SELECT DISTINCT ON (bucket)
    (rn * 1000 / total_n) AS bucket,
    pct_delegators,
    cum_pct_stake
  FROM percentiles
  ORDER BY bucket, rn
)
SELECT pct_delegators, cum_pct_stake FROM sampled ORDER BY pct_delegators;
