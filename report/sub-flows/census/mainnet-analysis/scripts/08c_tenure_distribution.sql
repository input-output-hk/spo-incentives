-- 08c_tenure_distribution.sql
-- How long delegators stay with the same pool before switching or leaving.
--
-- Tenure = (next_active_epoch - current_active_epoch) for switches,
--          (max_epoch - current_active_epoch) for the last delegation (still active).
-- We use 624 as the current epoch ceiling for still-active delegations.

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LEAD(active_epoch_no) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS next_epoch
  FROM delegation
),
tenures AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    COALESCE(next_epoch, 624) - active_epoch_no AS tenure_epochs
  FROM ordered_certs
)
SELECT
  CASE
    WHEN tenure_epochs <= 5   THEN '0-5'
    WHEN tenure_epochs <= 10  THEN '6-10'
    WHEN tenure_epochs <= 25  THEN '11-25'
    WHEN tenure_epochs <= 50  THEN '26-50'
    WHEN tenure_epochs <= 100 THEN '51-100'
    WHEN tenure_epochs <= 200 THEN '101-200'
    ELSE '201+'
  END AS tenure_bucket,
  COUNT(*) AS delegation_count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM tenures
GROUP BY
  CASE
    WHEN tenure_epochs <= 5   THEN '0-5'
    WHEN tenure_epochs <= 10  THEN '6-10'
    WHEN tenure_epochs <= 25  THEN '11-25'
    WHEN tenure_epochs <= 50  THEN '26-50'
    WHEN tenure_epochs <= 100 THEN '51-100'
    WHEN tenure_epochs <= 200 THEN '101-200'
    ELSE '201+'
  END
ORDER BY MIN(tenure_epochs);
