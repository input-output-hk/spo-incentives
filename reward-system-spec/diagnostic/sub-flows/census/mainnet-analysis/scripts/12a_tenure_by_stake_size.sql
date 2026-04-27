-- 12a_tenure_by_stake_size.sql
-- Cross-tabulation: delegation tenure bucket × delegator stake size bucket.
-- Tenure from delegation table (LEAD-based), stake from epoch_stake at epoch 623.

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LEAD(active_epoch_no) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS next_epoch
  FROM delegation
),

-- Latest delegation per address (the one active at epoch 623)
latest_deleg AS (
  SELECT DISTINCT ON (addr_id)
    addr_id,
    pool_hash_id,
    active_epoch_no,
    COALESCE(next_epoch, 624) - active_epoch_no AS tenure_epochs
  FROM ordered_certs
  ORDER BY addr_id, active_epoch_no DESC, tx_id DESC
),

-- Stake size at epoch 623
stake_size AS (
  SELECT
    addr_id,
    SUM(amount) AS stake_lovelace
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY addr_id
),

classified AS (
  SELECT
    ld.addr_id,
    ld.tenure_epochs,
    COALESCE(ss.stake_lovelace, 0) AS stake,
    CASE
      WHEN ld.tenure_epochs <= 5   THEN '0-5 ep (volatile)'
      WHEN ld.tenure_epochs <= 25  THEN '6-25 ep'
      WHEN ld.tenure_epochs <= 100 THEN '26-100 ep'
      WHEN ld.tenure_epochs <= 200 THEN '101-200 ep'
      ELSE '201+ ep (loyal)'
    END AS tenure_bucket,
    CASE
      WHEN COALESCE(ss.stake_lovelace, 0) < 1000000000 THEN '<1K'
      WHEN ss.stake_lovelace < 10000000000 THEN '1K-10K'
      WHEN ss.stake_lovelace < 100000000000 THEN '10K-100K'
      WHEN ss.stake_lovelace < 1000000000000 THEN '100K-1M'
      ELSE '1M+'
    END AS size_bucket
  FROM latest_deleg ld
  LEFT JOIN stake_size ss ON ss.addr_id = ld.addr_id
)

SELECT
  tenure_bucket,
  size_bucket,
  COUNT(*) AS delegation_count,
  ROUND(SUM(stake) / 1000000) AS total_stake_ada,
  ROUND(AVG(stake) / 1000000) AS avg_stake_ada
FROM classified
GROUP BY tenure_bucket, size_bucket
ORDER BY
  CASE tenure_bucket
    WHEN '0-5 ep (volatile)' THEN 1
    WHEN '6-25 ep' THEN 2
    WHEN '26-100 ep' THEN 3
    WHEN '101-200 ep' THEN 4
    ELSE 5
  END,
  CASE size_bucket
    WHEN '<1K' THEN 1
    WHEN '1K-10K' THEN 2
    WHEN '10K-100K' THEN 3
    WHEN '100K-1M' THEN 4
    ELSE 5
  END;
