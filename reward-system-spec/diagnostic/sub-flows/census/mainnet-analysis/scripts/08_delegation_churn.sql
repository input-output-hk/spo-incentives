-- 08_delegation_churn.sql
-- Delegation churn: track pool switches from the delegation certificate table.
--
-- For each addr_id, reconstruct the ordered sequence of delegation certificates.
-- A "redelegation" event = consecutive certificates pointing to different pools.
-- The first certificate per address is an "initial delegation", not a switch.
--
-- Outputs three result sets (run as three separate queries or split manually):
--   1. Redelegation events per epoch  (active_epoch_no, redelegations, initial_delegations, total_certs)
--   2. Top flow matrix               (from_pool_hash_id, to_pool_hash_id, flow_count)  top 500
--   3. Tenure distribution            (tenure_epochs, address_count)
--
-- Performance: ~3.5M rows in delegation, window function per addr_id.
-- Expected runtime: 1-3 minutes.

--------------------------------------------------------------------
-- Part 1: per-epoch redelegation count
--------------------------------------------------------------------

WITH ordered_certs AS (
  SELECT
    addr_id,
    pool_hash_id,
    active_epoch_no,
    tx_id,
    LAG(pool_hash_id) OVER (PARTITION BY addr_id ORDER BY active_epoch_no, tx_id) AS prev_pool
  FROM delegation
),
classified AS (
  SELECT
    active_epoch_no,
    CASE
      WHEN prev_pool IS NULL THEN 'initial'
      WHEN pool_hash_id <> prev_pool THEN 'switch'
      ELSE 'renewal'  -- same pool re-delegation (e.g. after deregistration)
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
