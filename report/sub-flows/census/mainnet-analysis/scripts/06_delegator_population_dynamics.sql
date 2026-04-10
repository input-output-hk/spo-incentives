-- §3.5 population dynamics: delegator entries and exits per epoch
--   (restricted to delegators of productive pools)
--
-- For each epoch (from 212 onward), count:
--   - entries:   addr_id delegating to a productive pool at epoch e
--                but NOT delegating to any productive pool at epoch e-1
--   - exits:     addr_id delegating to a productive pool at epoch e-1
--                but NOT delegating to any productive pool at epoch e
--   - survivors: addr_id delegating to a productive pool at both e-1 and e
--   - net_change: entries - exits
--
-- "Productive pool" = pool_stake >= production_threshold (total_staked / 21600).
--
-- Very heavy query — full scan of epoch_stake (~560 M rows) with self-join
-- on addr_id across consecutive epochs.  Budget several hours.

\copy (
  WITH per_pool AS (
    SELECT
      epoch_no,
      pool_id,
      SUM(amount) AS pool_stake
    FROM epoch_stake
    GROUP BY epoch_no, pool_id
  ),
  epoch_totals AS (
    SELECT
      epoch_no,
      SUM(pool_stake) AS total_staked
    FROM per_pool
    GROUP BY epoch_no
  ),
  productive_pools AS (
    SELECT pp.epoch_no, pp.pool_id
    FROM per_pool pp
    JOIN epoch_totals et USING (epoch_no)
    WHERE pp.pool_stake >= (et.total_staked::numeric / 21600)
  ),
  -- Distinct delegators in productive pools per epoch
  productive_delegators AS (
    SELECT DISTINCT es.epoch_no, es.addr_id
    FROM epoch_stake es
    JOIN productive_pools pr
      ON es.epoch_no = pr.epoch_no
      AND es.pool_id = pr.pool_id
  ),
  -- Entries: delegating to a productive pool at e, absent at e-1
  entries_per_epoch AS (
    SELECT
      curr.epoch_no,
      COUNT(*) AS entries
    FROM productive_delegators curr
    LEFT JOIN productive_delegators prev
      ON curr.addr_id = prev.addr_id
      AND prev.epoch_no = curr.epoch_no - 1
    WHERE prev.addr_id IS NULL
    GROUP BY curr.epoch_no
  ),
  -- Exits: delegating to a productive pool at e-1, absent at e
  -- Attributed to epoch e (the epoch where the delegator is gone)
  exits_per_epoch AS (
    SELECT
      prev.epoch_no + 1 AS epoch_no,
      COUNT(*) AS exits
    FROM productive_delegators prev
    LEFT JOIN productive_delegators curr
      ON prev.addr_id = curr.addr_id
      AND curr.epoch_no = prev.epoch_no + 1
    WHERE curr.addr_id IS NULL
    GROUP BY prev.epoch_no
  ),
  -- Survivors: present in productive pools at both e-1 and e
  survivors_per_epoch AS (
    SELECT
      curr.epoch_no,
      COUNT(*) AS survivors
    FROM productive_delegators curr
    INNER JOIN productive_delegators prev
      ON curr.addr_id = prev.addr_id
      AND prev.epoch_no = curr.epoch_no - 1
    GROUP BY curr.epoch_no
  )
  SELECT
    d.epoch_no,
    COALESCE(en.entries, 0)   AS entries,
    COALESCE(ex.exits, 0)    AS exits,
    COALESCE(s.survivors, 0)  AS survivors,
    COALESCE(en.entries, 0) - COALESCE(ex.exits, 0) AS net_change
  FROM (SELECT DISTINCT epoch_no FROM productive_delegators WHERE epoch_no >= 212) d
  LEFT JOIN entries_per_epoch   en USING (epoch_no)
  LEFT JOIN exits_per_epoch     ex USING (epoch_no)
  LEFT JOIN survivors_per_epoch s  USING (epoch_no)
  ORDER BY d.epoch_no
) TO '/tmp/delegator_population_dynamics.csv' WITH CSV HEADER;
