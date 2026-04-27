-- §2.5 population dynamics: productive pool births and deaths per epoch
--
-- For each epoch (from 212 onward — epoch 211 is the baseline), count:
--   - entries: pools productive at epoch e but NOT at epoch e-1
--   - exits:   pools productive at epoch e-1 but NOT at epoch e
--   - survivors: pools productive at both e-1 and e
--   - net_change: entries - exits
--
-- "Productive" = pool_stake >= production_threshold (total_staked / 21600).
--
-- Heavy query — same scan of epoch_stake as 03_operator_landscape_history.sql.
-- Budget ~30–60 min.

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
  productive AS (
    SELECT pp.epoch_no, pp.pool_id
    FROM per_pool pp
    JOIN epoch_totals et USING (epoch_no)
    WHERE pp.pool_stake >= (et.total_staked::numeric / 21600)
  ),
  -- Entries: productive at e but absent at e-1
  entries_per_epoch AS (
    SELECT
      curr.epoch_no,
      COUNT(*) AS entries
    FROM productive curr
    LEFT JOIN productive prev
      ON curr.pool_id = prev.pool_id
      AND prev.epoch_no = curr.epoch_no - 1
    WHERE prev.pool_id IS NULL
    GROUP BY curr.epoch_no
  ),
  -- Exits: productive at e-1 but absent at e
  -- Attributed to epoch e (the epoch where the pool is no longer present)
  exits_per_epoch AS (
    SELECT
      prev.epoch_no + 1 AS epoch_no,
      COUNT(*) AS exits
    FROM productive prev
    LEFT JOIN productive curr
      ON prev.pool_id = curr.pool_id
      AND curr.epoch_no = prev.epoch_no + 1
    WHERE curr.pool_id IS NULL
    GROUP BY prev.epoch_no
  ),
  -- Survivors: productive at both e-1 and e
  survivors_per_epoch AS (
    SELECT
      curr.epoch_no,
      COUNT(*) AS survivors
    FROM productive curr
    INNER JOIN productive prev
      ON curr.pool_id = prev.pool_id
      AND prev.epoch_no = curr.epoch_no - 1
    GROUP BY curr.epoch_no
  )
  SELECT
    p.epoch_no,
    COALESCE(en.entries, 0)   AS entries,
    COALESCE(ex.exits, 0)    AS exits,
    COALESCE(s.survivors, 0)  AS survivors,
    COALESCE(en.entries, 0) - COALESCE(ex.exits, 0) AS net_change
  FROM (SELECT DISTINCT epoch_no FROM productive WHERE epoch_no >= 212) p
  LEFT JOIN entries_per_epoch   en USING (epoch_no)
  LEFT JOIN exits_per_epoch     ex USING (epoch_no)
  LEFT JOIN survivors_per_epoch s  USING (epoch_no)
  ORDER BY p.epoch_no
) TO '/tmp/pool_population_dynamics.csv' WITH CSV HEADER;
