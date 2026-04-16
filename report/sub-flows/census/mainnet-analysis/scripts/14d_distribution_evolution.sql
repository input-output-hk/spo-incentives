-- 14d_distribution_evolution.sql
-- How has the stake distribution evolved over time?
-- Per-epoch: mean, median, Gini proxy (top-1% share), delegator count.
-- Sampled every 10 epochs to keep runtime manageable.

WITH epochs AS (
  SELECT generate_series(210, 623, 10) AS epoch_no
),
deleg_stake AS (
  SELECT
    e.epoch_no,
    es.addr_id,
    SUM(es.amount) AS stake
  FROM epochs e
  JOIN epoch_stake es ON es.epoch_no = e.epoch_no
  GROUP BY e.epoch_no, es.addr_id
),
ranked AS (
  SELECT
    epoch_no,
    stake,
    ROW_NUMBER() OVER (PARTITION BY epoch_no ORDER BY stake DESC) AS rn,
    COUNT(*) OVER (PARTITION BY epoch_no) AS n,
    SUM(stake) OVER (PARTITION BY epoch_no) AS total
  FROM deleg_stake
),
epoch_stats AS (
  SELECT
    epoch_no,
    MAX(n) AS delegator_count,
    ROUND(MAX(total) / 1000000) AS total_ada,
    ROUND(AVG(stake) / 1000000) AS mean_ada,
    -- Top 1% share
    ROUND(100.0 * SUM(CASE WHEN rn <= GREATEST(n * 0.01, 1) THEN stake ELSE 0 END) / MAX(total), 2) AS top1pct_share,
    -- Top 0.1% share
    ROUND(100.0 * SUM(CASE WHEN rn <= GREATEST(n * 0.001, 1) THEN stake ELSE 0 END) / MAX(total), 2) AS top01pct_share
  FROM ranked
  GROUP BY epoch_no
)
SELECT * FROM epoch_stats ORDER BY epoch_no;
