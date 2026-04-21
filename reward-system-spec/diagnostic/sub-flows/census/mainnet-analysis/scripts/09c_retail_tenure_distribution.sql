-- 09c_retail_tenure_distribution.sql
-- Tenure distribution for retail pool delegations only.

WITH latest_margin AS (
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),
retail_pools AS (
  SELECT pool_hash_id
  FROM latest_margin
  WHERE margin < 0.999
),
ordered_certs AS (
  SELECT
    d.addr_id,
    d.pool_hash_id,
    d.active_epoch_no,
    d.tx_id,
    LEAD(d.active_epoch_no) OVER (PARTITION BY d.addr_id ORDER BY d.active_epoch_no, d.tx_id) AS next_epoch
  FROM delegation d
  WHERE d.pool_hash_id IN (SELECT pool_hash_id FROM retail_pools)
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
