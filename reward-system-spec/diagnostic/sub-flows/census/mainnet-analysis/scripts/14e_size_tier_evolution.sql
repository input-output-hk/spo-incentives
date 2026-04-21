-- 14e_size_tier_evolution.sql
-- Size tier composition over time (sampled every 20 epochs for speed).
-- Shows how the delegator population's size structure has evolved.

WITH epochs AS (
  SELECT generate_series(210, 623, 20) AS epoch_no
  UNION SELECT 623
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
classified AS (
  SELECT
    epoch_no,
    CASE
      WHEN stake < 1000000000 THEN 'micro_under_1k'
      WHEN stake < 100000000000 THEN 'small_1k_100k'
      WHEN stake < 1000000000000 THEN 'medium_100k_1m'
      ELSE 'large_1m_plus'
    END AS tier,
    stake
  FROM deleg_stake
)
SELECT
  epoch_no,
  tier,
  COUNT(*) AS delegator_count,
  ROUND(SUM(stake) / 1000000) AS total_stake_ada
FROM classified
GROUP BY epoch_no, tier
ORDER BY epoch_no, tier;
