-- 10c_loyal_delegator_pools.sql
-- Profile of pools where loyal delegators (tenure >= 201 epochs) stay.
-- What margin, size, and saturation characteristics do these pools share?

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
),

loyal AS (
  SELECT addr_id, pool_hash_id, tenure_epochs
  FROM tenures
  WHERE tenure_epochs >= 201
),

pool_params AS (
  SELECT DISTINCT ON (hash_id)
    hash_id AS pool_hash_id,
    margin,
    fixed_cost
  FROM pool_update
  ORDER BY hash_id, registered_tx_id DESC
),

pool_size AS (
  SELECT
    pool_id AS pool_hash_id,
    SUM(amount) AS total_stake,
    COUNT(DISTINCT addr_id) AS delegator_count
  FROM epoch_stake
  WHERE epoch_no = 623
  GROUP BY pool_id
),

-- Saturation reference: k=500, total supply ~35.4B
-- saturation_point ~ 35.4B / 500 = 70.8M ADA = 70,800,000,000,000 lovelace
pool_profile AS (
  SELECT
    l.pool_hash_id,
    pp.margin,
    pp.fixed_cost,
    ps.total_stake,
    ps.delegator_count,
    ROUND(100.0 * ps.total_stake / 70800000000000000, 2) AS saturation_pct,
    COUNT(*) AS loyal_delegation_count,
    ROUND(AVG(l.tenure_epochs), 1) AS avg_tenure
  FROM loyal l
  LEFT JOIN pool_params pp ON pp.pool_hash_id = l.pool_hash_id
  LEFT JOIN pool_size ps   ON ps.pool_hash_id = l.pool_hash_id
  GROUP BY l.pool_hash_id, pp.margin, pp.fixed_cost, ps.total_stake, ps.delegator_count
)

SELECT
  ph.view AS pool_id,
  p.margin,
  p.fixed_cost,
  p.total_stake,
  p.delegator_count,
  p.saturation_pct,
  p.loyal_delegation_count,
  p.avg_tenure
FROM pool_profile p
JOIN pool_hash ph ON ph.id = p.pool_hash_id
ORDER BY p.loyal_delegation_count DESC
LIMIT 200;
