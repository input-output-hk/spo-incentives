-- §3: Pool operators — SPO vs MPO, stake controlled
-- Uses pool_update (registration transactions) + pool_owner + epoch_stake

-- 2a. Per epoch: pool count, unique owner count, pools per owner distribution
--     A "pool owner" in db-sync is the stake_address in pool_owner table.
--     An entity operating multiple pools will have the same owner across pool_update records.
\copy (
  WITH active_pools AS (
    -- For each epoch, find pools that had stake delegated to them
    SELECT DISTINCT epoch_no, pool_id
    FROM epoch_stake
  ),
  pool_owners AS (
    -- Latest pool_update for each pool (before or at each epoch)
    -- pool_owner links pool_update_id -> stake_address
    SELECT DISTINCT ON (pu.hash_id)
      pu.hash_id        AS pool_hash_id,
      pu.id             AS update_id,
      pu.registered_tx_id
    FROM pool_update pu
    ORDER BY pu.hash_id, pu.registered_tx_id DESC
  ),
  owner_counts AS (
    SELECT
      po.pool_hash_id,
      COUNT(DISTINCT own.addr_id) AS owner_count
    FROM pool_owners po
    JOIN pool_owner own ON own.pool_update_id = po.update_id
    GROUP BY po.pool_hash_id
  )
  SELECT
    ap.epoch_no,
    COUNT(DISTINCT ap.pool_id)                                          AS total_pools,
    SUM(es_agg.total_stake)                                             AS total_staked,
    SUM(es_agg.delegator_count)                                         AS total_delegations
  FROM active_pools ap
  JOIN (
    SELECT epoch_no, pool_id, SUM(amount) AS total_stake, COUNT(*) AS delegator_count
    FROM epoch_stake
    GROUP BY epoch_no, pool_id
  ) es_agg ON es_agg.epoch_no = ap.epoch_no AND es_agg.pool_id = ap.pool_id
  GROUP BY ap.epoch_no
  ORDER BY ap.epoch_no
) TO '/tmp/pool_epoch_summary.csv' WITH CSV HEADER;

-- 2b. For each pool: how many pools does its owner set control?
--     This lets us classify SPO (1 pool) vs MPO (>1 pool)
\copy (
  WITH latest_update AS (
    SELECT DISTINCT ON (hash_id)
      hash_id AS pool_hash_id,
      id      AS update_id
    FROM pool_update
    ORDER BY hash_id, registered_tx_id DESC
  ),
  pool_to_owners AS (
    SELECT
      lu.pool_hash_id,
      array_agg(DISTINCT own.addr_id ORDER BY own.addr_id) AS owner_set
    FROM latest_update lu
    JOIN pool_owner own ON own.pool_update_id = lu.update_id
    GROUP BY lu.pool_hash_id
  ),
  owner_set_pools AS (
    SELECT
      owner_set,
      array_agg(pool_hash_id) AS pools,
      COUNT(*)                AS pool_count
    FROM pool_to_owners
    GROUP BY owner_set
  )
  SELECT
    ph.view             AS pool_id_bech32,
    pto.pool_hash_id,
    osp.pool_count      AS entity_pool_count,
    CASE WHEN osp.pool_count = 1 THEN 'SPO' ELSE 'MPO' END AS operator_type
  FROM pool_to_owners pto
  JOIN owner_set_pools osp ON osp.owner_set = pto.owner_set
  JOIN pool_hash ph ON ph.id = pto.pool_hash_id
  ORDER BY osp.pool_count DESC, ph.view
) TO '/tmp/pool_operator_type.csv' WITH CSV HEADER;
