-- §4 non-participants: decompose the unstaked UTxO set by address type
--   and delegation status.
--
-- Produces two result sets exported to separate CSVs.
--
-- (A) utxo_address_type_decomposition.csv
--     Full UTxO set grouped by address type (script / enterprise / base)
--     and whether the stake credential is actively delegated.
--
-- (B) non_participant_dormancy.csv
--     Among non-delegated UTxOs, classify by last activity date
--     to identify dormant wallets.
--
-- Relies on:
--   tx_out, tx_in          — UTxO set
--   stake_address           — stake key registry
--   delegation              — delegation certificates
--   stake_deregistration    — deregistration certificates
--   tx, block               — timestamps for dormancy analysis
--
-- Moderate-to-heavy query.  The UTxO scan is cheaper than epoch_stake
-- since it only touches the current tip state.


-- ═══════════════════════════════════════════════════════════════
-- (A) UTxO decomposition by address type × delegation status
-- ═══════════════════════════════════════════════════════════════
\copy (
  WITH unspent AS (
    SELECT
      txo.value,
      txo.stake_address_id,
      txo.address_has_script
    FROM tx_out txo
    WHERE NOT EXISTS (
      SELECT 1 FROM tx_in txi
      WHERE txi.tx_out_id = txo.tx_id
        AND txi.tx_out_index = txo.index
    )
  ),
  -- For each stake_address, determine current delegation status.
  -- A stake key is "delegated" if its most recent delegation tx_id
  -- is strictly greater than its most recent deregistration tx_id
  -- (or if it was never deregistered).
  stake_status AS (
    SELECT
      sa.id AS stake_address_id,
      CASE
        WHEN d.tx_id IS NOT NULL
          AND (sd.tx_id IS NULL OR d.tx_id > sd.tx_id)
        THEN true
        ELSE false
      END AS is_delegated
    FROM stake_address sa
    LEFT JOIN LATERAL (
      SELECT tx_id FROM delegation
      WHERE addr_id = sa.id
      ORDER BY tx_id DESC LIMIT 1
    ) d ON true
    LEFT JOIN LATERAL (
      SELECT tx_id FROM stake_deregistration
      WHERE addr_id = sa.id
      ORDER BY tx_id DESC LIMIT 1
    ) sd ON true
  ),
  classified AS (
    SELECT
      u.value,
      CASE
        -- Script addresses without staking credential
        WHEN u.address_has_script AND u.stake_address_id IS NULL
          THEN 'script_no_staking_cred'
        -- Script addresses with staking credential
        WHEN u.address_has_script AND u.stake_address_id IS NOT NULL
          THEN CASE WHEN ss.is_delegated THEN 'script_delegated'
                    ELSE 'script_not_delegated'
               END
        -- Enterprise addresses (no staking credential by design)
        WHEN NOT u.address_has_script AND u.stake_address_id IS NULL
          THEN 'enterprise'
        -- Base addresses with staking credential
        ELSE CASE WHEN ss.is_delegated THEN 'base_delegated'
                  ELSE 'base_not_delegated'
             END
      END AS classification
    FROM unspent u
    LEFT JOIN stake_status ss ON u.stake_address_id = ss.stake_address_id
  )
  SELECT
    classification,
    COUNT(*)    AS utxo_count,
    SUM(value)  AS total_lovelace
  FROM classified
  GROUP BY classification
  ORDER BY total_lovelace DESC
) TO '/tmp/utxo_address_type_decomposition.csv' WITH CSV HEADER;


-- ═══════════════════════════════════════════════════════════════
-- (B) Dormancy analysis — non-delegated UTxOs by last tx date
-- ═══════════════════════════════════════════════════════════════
\copy (
  WITH unspent AS (
    SELECT
      txo.tx_id,
      txo.value,
      txo.stake_address_id,
      txo.address_has_script
    FROM tx_out txo
    WHERE NOT EXISTS (
      SELECT 1 FROM tx_in txi
      WHERE txi.tx_out_id = txo.tx_id
        AND txi.tx_out_index = txo.index
    )
  ),
  stake_status AS (
    SELECT
      sa.id AS stake_address_id,
      CASE
        WHEN d.tx_id IS NOT NULL
          AND (sd.tx_id IS NULL OR d.tx_id > sd.tx_id)
        THEN true
        ELSE false
      END AS is_delegated
    FROM stake_address sa
    LEFT JOIN LATERAL (
      SELECT tx_id FROM delegation
      WHERE addr_id = sa.id
      ORDER BY tx_id DESC LIMIT 1
    ) d ON true
    LEFT JOIN LATERAL (
      SELECT tx_id FROM stake_deregistration
      WHERE addr_id = sa.id
      ORDER BY tx_id DESC LIMIT 1
    ) sd ON true
  ),
  non_delegated AS (
    SELECT u.tx_id, u.value
    FROM unspent u
    LEFT JOIN stake_status ss ON u.stake_address_id = ss.stake_address_id
    WHERE ss.is_delegated IS DISTINCT FROM true
  ),
  with_time AS (
    SELECT
      nd.value,
      b.epoch_no AS creation_epoch,
      b.time     AS creation_time
    FROM non_delegated nd
    JOIN tx t ON t.id = nd.tx_id
    JOIN block b ON b.id = t.block_id
  )
  SELECT
    CASE
      WHEN creation_epoch < 208  THEN 'pre_shelley'
      WHEN creation_epoch < 300  THEN 'early_shelley_208_299'
      WHEN creation_epoch < 400  THEN 'epoch_300_399'
      WHEN creation_epoch < 500  THEN 'epoch_400_499'
      WHEN creation_epoch < 600  THEN 'epoch_500_599'
      ELSE                            'epoch_600_plus'
    END AS vintage,
    COUNT(*)    AS utxo_count,
    SUM(value)  AS total_lovelace
  FROM with_time
  GROUP BY 1
  ORDER BY MIN(creation_epoch)
) TO '/tmp/non_participant_dormancy.csv' WITH CSV HEADER;
