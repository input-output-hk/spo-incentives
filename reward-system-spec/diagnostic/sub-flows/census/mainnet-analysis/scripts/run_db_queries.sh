#!/bin/bash
set -e
DC="/Users/nhenin/dev/ARC/stream-SPO/spo-incentives/mainnet-indexer/docker-compose.yml"
OUT="/Users/nhenin/dev/ARC/stream-SPO/spo-incentives/report/sub-flows/population-analysis/mainnet-analysis/data"
PSQL="docker compose -f $DC exec -T postgres psql -U postgres -d cexplorer"

echo "=== Q3a: Pool SPO/MPO classification ==="
$PSQL <<'SQL'
COPY (
  WITH latest_reg AS (
    SELECT DISTINCT ON (hash_id)
      hash_id AS pool_hash_id, id AS update_id
    FROM pool_update
    ORDER BY hash_id, registered_tx_id DESC
  ),
  pool_owners_flat AS (
    SELECT lr.pool_hash_id,
      array_agg(DISTINCT po.addr_id ORDER BY po.addr_id) AS owner_key
    FROM latest_reg lr
    JOIN pool_owner po ON po.pool_update_id = lr.update_id
    GROUP BY lr.pool_hash_id
  ),
  entity AS (
    SELECT owner_key, COUNT(*) AS pools_in_entity
    FROM pool_owners_flat GROUP BY owner_key
  )
  SELECT ph.view AS pool_id,
    pof.pool_hash_id,
    e.pools_in_entity,
    CASE WHEN e.pools_in_entity = 1 THEN 'SPO' ELSE 'MPO' END AS op_type
  FROM pool_owners_flat pof
  JOIN entity e ON e.owner_key = pof.owner_key
  JOIN pool_hash ph ON ph.id = pof.pool_hash_id
  ORDER BY e.pools_in_entity DESC, ph.view
) TO '/tmp/pool_operator_type.csv' WITH CSV HEADER;
SQL
docker cp dbsync-postgres-1:/tmp/pool_operator_type.csv "$OUT/pool_operator_type.csv"
echo "[OK] pool_operator_type.csv"

echo "=== Q3b: Delegation count per epoch (from delegation table) ==="
$PSQL <<'SQL'
COPY (
  WITH last_deleg AS (
    -- For each address, each time they redelegate, pick the latest cert in that epoch
    SELECT DISTINCT ON (addr_id, active_epoch_no)
      addr_id, pool_hash_id, active_epoch_no, tx_id
    FROM delegation
    ORDER BY addr_id, active_epoch_no, tx_id DESC, cert_index DESC
  ),
  timeline AS (
    SELECT addr_id, pool_hash_id, active_epoch_no AS epoch_start,
      LEAD(active_epoch_no) OVER (PARTITION BY addr_id ORDER BY active_epoch_no) AS epoch_end
    FROM last_deleg
  )
  SELECT g.epoch_no,
    COUNT(DISTINCT t.addr_id)       AS active_delegators,
    COUNT(DISTINCT t.pool_hash_id)  AS active_pools
  FROM generate_series(211, 623) AS g(epoch_no)
  JOIN timeline t
    ON t.epoch_start <= g.epoch_no
    AND (t.epoch_end IS NULL OR t.epoch_end > g.epoch_no)
  GROUP BY g.epoch_no
  ORDER BY g.epoch_no
) TO '/tmp/delegator_pool_count_per_epoch.csv' WITH CSV HEADER;
SQL
docker cp dbsync-postgres-1:/tmp/delegator_pool_count_per_epoch.csv "$OUT/delegator_pool_count_per_epoch.csv"
echo "[OK] delegator_pool_count_per_epoch.csv"

echo "=== Q4: Stake deregistrations per epoch ==="
$PSQL <<'SQL'
COPY (
  SELECT e.epoch_no, COUNT(*) AS deregistrations
  FROM stake_deregistration sd
  JOIN tx t ON t.id = sd.tx_id
  JOIN block b ON b.id = t.block_id
  JOIN epoch e ON e.no = b.epoch_no
  GROUP BY e.epoch_no
  ORDER BY e.epoch_no
) TO '/tmp/stake_dereg_per_epoch.csv' WITH CSV HEADER;
SQL
docker cp dbsync-postgres-1:/tmp/stake_dereg_per_epoch.csv "$OUT/stake_dereg_per_epoch.csv" 2>/dev/null && echo "[OK] stake_dereg_per_epoch.csv" || echo "[SKIP] stake_dereg_per_epoch"

echo "=== Check epoch_stake query status ==="
$PSQL -t -c "SELECT pid, now()-query_start AS duration FROM pg_stat_activity WHERE state='active' AND pid != pg_backend_pid();"

echo "=== Done: $(date) ==="
