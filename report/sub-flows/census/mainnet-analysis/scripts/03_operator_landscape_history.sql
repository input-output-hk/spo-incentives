-- §2.4 historical: operator landscape per epoch
--
-- For each epoch, compute:
--   - total pools and total staked
--   - production threshold (total_staked / 21 600 blocks per epoch)
--   - productive pools (stake >= threshold) and their aggregate stake/delegations
--   - sub-threshold pools and their aggregate stake/delegations
--
-- Output: one row per epoch with the full decomposition.
-- Heavy query — scans epoch_stake (~560 M rows). Budget ~30–60 min.

\copy (
  WITH per_pool AS (
    SELECT
      epoch_no,
      pool_id,
      SUM(amount)  AS pool_stake,
      COUNT(*)     AS pool_delegations
    FROM epoch_stake
    GROUP BY epoch_no, pool_id
  ),
  epoch_totals AS (
    SELECT
      epoch_no,
      SUM(pool_stake)       AS total_staked,
      SUM(pool_delegations) AS total_delegations,
      COUNT(*)              AS total_pools
    FROM per_pool
    GROUP BY epoch_no
  ),
  thresholded AS (
    SELECT
      pp.epoch_no,
      pp.pool_id,
      pp.pool_stake,
      pp.pool_delegations,
      et.total_staked,
      -- production threshold: enough stake to expect >= 1 block / epoch
      -- 21 600 blocks/epoch  =>  threshold = total_staked / 21600
      (et.total_staked::numeric / 21600) AS threshold
    FROM per_pool pp
    JOIN epoch_totals et USING (epoch_no)
  )
  SELECT
    epoch_no,
    -- raw totals
    MAX(total_staked)                                           AS total_staked,
    COUNT(*)                                                    AS total_pools,
    SUM(pool_delegations)                                       AS total_delegations,
    -- production threshold used
    MAX(threshold)::bigint                                      AS production_threshold,
    -- productive segment (above threshold)
    COUNT(*) FILTER (WHERE pool_stake >= threshold)              AS productive_pools,
    COALESCE(SUM(pool_stake)       FILTER (WHERE pool_stake >= threshold), 0) AS productive_stake,
    COALESCE(SUM(pool_delegations) FILTER (WHERE pool_stake >= threshold), 0) AS productive_delegations,
    -- sub-threshold segment
    COUNT(*) FILTER (WHERE pool_stake < threshold)              AS subthreshold_pools,
    COALESCE(SUM(pool_stake)       FILTER (WHERE pool_stake < threshold), 0) AS subthreshold_stake,
    COALESCE(SUM(pool_delegations) FILTER (WHERE pool_stake < threshold), 0) AS subthreshold_delegations
  FROM thresholded
  GROUP BY epoch_no
  ORDER BY epoch_no
) TO '/tmp/operator_landscape_history.csv' WITH CSV HEADER;
