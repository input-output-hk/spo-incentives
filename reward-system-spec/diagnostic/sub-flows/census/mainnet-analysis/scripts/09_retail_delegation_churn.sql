-- 09_retail_delegation_churn.sql
-- Same as 08_delegation_churn.sql but restricted to "retail" pools:
-- non-private, non-custodial-by-extraction pools.
--
-- Retail filter: the pool's latest registered margin must be < 99.9%.
-- This excludes private pools (100% margin) and custodial-by-extraction pools.
--
-- Three result sets (run as three separate queries):
--   1. Per-epoch churn  → data/retail_delegation_churn_per_epoch.csv
--   2. Flow matrix      → data/retail_delegation_flow_matrix.csv
--   3. Tenure           → data/retail_delegation_tenure_distribution.csv

--------------------------------------------------------------------
-- Part 1: per-epoch retail redelegation count
--------------------------------------------------------------------

WITH latest_margin AS (
  -- For each pool, get the most recent registered margin
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
    LAG(d.pool_hash_id) OVER (PARTITION BY d.addr_id ORDER BY d.active_epoch_no, d.tx_id) AS prev_pool
  FROM delegation d
  -- Current delegation must be to a retail pool
  WHERE d.pool_hash_id IN (SELECT pool_hash_id FROM retail_pools)
),
classified AS (
  SELECT
    active_epoch_no,
    CASE
      WHEN prev_pool IS NULL THEN 'initial'
      WHEN pool_hash_id <> prev_pool THEN 'switch'
      ELSE 'renewal'
    END AS cert_type
  FROM ordered_certs
)
SELECT
  active_epoch_no AS epoch_no,
  COUNT(*) FILTER (WHERE cert_type = 'switch')  AS redelegations,
  COUNT(*) FILTER (WHERE cert_type = 'initial') AS initial_delegations,
  COUNT(*) FILTER (WHERE cert_type = 'renewal') AS renewals,
  COUNT(*) AS total_certs
FROM classified
GROUP BY active_epoch_no
ORDER BY active_epoch_no;
