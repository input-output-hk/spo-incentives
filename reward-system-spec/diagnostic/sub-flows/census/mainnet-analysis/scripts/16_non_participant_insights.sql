-- §5 Non-Participants — deeper insights queries (Instance B, full UTxO).
--
-- IMPORTANT: This Instance B has consumed_by_tx_id always NULL (the
-- --consumed-tx-out flag is not enabled). We must use anti-join with
-- tx_in to detect unspent outputs.
--
-- Generates six CSVs at /tmp inside the container using server-side COPY.

SET statement_timeout = 0;
SET work_mem = '256MB';
SET max_parallel_workers_per_gather = 2;

\echo === [1/8] Materialise unspent UTxO snapshot (heavy)

CREATE TEMP TABLE t_unspent AS
SELECT txo.tx_id,
       txo.index,
       txo.address,
       txo.payment_cred,
       txo.stake_address_id,
       txo.address_has_script,
       txo.value
FROM tx_out txo
WHERE NOT EXISTS (
  SELECT 1 FROM tx_in txi
  WHERE txi.tx_out_id = txo.tx_id
    AND txi.tx_out_index = txo.index
);

CREATE INDEX ON t_unspent (stake_address_id) WHERE stake_address_id IS NOT NULL;
CREATE INDEX ON t_unspent (address) WHERE stake_address_id IS NULL;
ANALYZE t_unspent;

\echo === [2/8] Build no-stake-credential per-address aggregate

CREATE TEMP TABLE t_no_cred_addr AS
  SELECT address,
         CASE
           WHEN address LIKE 'addr1v%' THEN 'enterprise_key'
           WHEN address LIKE 'addr1w%' THEN 'enterprise_script'
           WHEN address LIKE 'Ae2%' OR address LIKE 'DdzFF%' THEN 'byron'
           ELSE 'other'
         END                                AS address_type,
         payment_cred,
         SUM(value)::bigint                 AS lovelace,
         COUNT(*)                           AS utxo_count
  FROM t_unspent
  WHERE stake_address_id IS NULL
  GROUP BY address, payment_cred;

ANALYZE t_no_cred_addr;

\echo === [3/8] (A) Address-level concentration of the no-stake-credential UTxO set

COPY (
  WITH ranked AS (
    SELECT address,
           address_type,
           lovelace,
           utxo_count,
           ROW_NUMBER() OVER (ORDER BY lovelace DESC) AS rank,
           SUM(lovelace) OVER ()                       AS total_lovelace
    FROM t_no_cred_addr
  )
  SELECT rank,
         LEFT(address, 12) || '…' || RIGHT(address, 8) AS address_short,
         address,
         address_type,
         utxo_count,
         lovelace,
         (lovelace / 1000000.0)::bigint AS ada,
         100.0 * lovelace / total_lovelace AS pct_of_no_cred
  FROM ranked
  WHERE rank <= 200
  ORDER BY rank
) TO '/tmp/no_cred_top200.csv' WITH CSV HEADER;

\echo === [4/8] (B) Bucketed size distribution of no-cred address holdings

COPY (
  WITH bucketed AS (
    SELECT
      CASE
        WHEN lovelace < 1000000             THEN '00_under_1_ada'
        WHEN lovelace < 10000000            THEN '01_1_to_10_ada'
        WHEN lovelace < 100000000           THEN '02_10_to_100_ada'
        WHEN lovelace < 1000000000          THEN '03_100_to_1k_ada'
        WHEN lovelace < 10000000000         THEN '04_1k_to_10k_ada'
        WHEN lovelace < 100000000000        THEN '05_10k_to_100k_ada'
        WHEN lovelace < 1000000000000       THEN '06_100k_to_1m_ada'
        WHEN lovelace < 10000000000000      THEN '07_1m_to_10m_ada'
        WHEN lovelace < 100000000000000     THEN '08_10m_to_100m_ada'
        ELSE                                     '09_above_100m_ada'
      END AS size_bucket,
      address_type,
      lovelace,
      utxo_count,
      address
    FROM t_no_cred_addr
  )
  SELECT
    size_bucket,
    address_type,
    COUNT(*)        AS address_count,
    SUM(utxo_count) AS utxo_count,
    SUM(lovelace)   AS total_lovelace,
    (SUM(lovelace) / 1000000.0)::bigint AS total_ada
  FROM bucketed
  GROUP BY size_bucket, address_type
  ORDER BY address_type, size_bucket
) TO '/tmp/no_cred_size_distribution.csv' WITH CSV HEADER;

\echo === [5/8] Stake-address status table

CREATE TEMP TABLE t_stake_status AS
  SELECT
    sa.id           AS stake_address_id,
    sa.script_hash IS NOT NULL AS is_script,
    CASE WHEN d.tx_id IS NOT NULL AND (sd.tx_id IS NULL OR d.tx_id > sd.tx_id) THEN true ELSE false END AS is_delegated,
    CASE WHEN sd.tx_id IS NOT NULL AND (d.tx_id IS NULL OR sd.tx_id > d.tx_id) THEN true ELSE false END AS is_deregistered,
    r.tx_id         AS reg_tx_id,
    d.tx_id         AS last_deleg_tx_id
  FROM stake_address sa
  LEFT JOIN LATERAL (SELECT tx_id FROM delegation         WHERE addr_id = sa.id ORDER BY tx_id DESC LIMIT 1) d  ON true
  LEFT JOIN LATERAL (SELECT tx_id FROM stake_deregistration WHERE addr_id = sa.id ORDER BY tx_id DESC LIMIT 1) sd ON true
  LEFT JOIN LATERAL (SELECT tx_id FROM stake_registration   WHERE addr_id = sa.id ORDER BY tx_id DESC LIMIT 1) r  ON true;

CREATE INDEX ON t_stake_status (stake_address_id);

\echo === [6/8] (C) Addressable-pool balance distribution

CREATE TEMP TABLE t_addressable AS
  SELECT stake_address_id, is_script, reg_tx_id, last_deleg_tx_id IS NOT NULL AS ever_delegated
  FROM t_stake_status
  WHERE NOT is_delegated AND NOT is_deregistered AND reg_tx_id IS NOT NULL;

CREATE INDEX ON t_addressable (stake_address_id);

CREATE TEMP TABLE t_addr_balance AS
  SELECT
    a.stake_address_id,
    a.is_script,
    a.ever_delegated,
    COALESCE(SUM(u.value), 0)::bigint AS lovelace
  FROM t_addressable a
  LEFT JOIN t_unspent u ON u.stake_address_id = a.stake_address_id
  GROUP BY a.stake_address_id, a.is_script, a.ever_delegated;

COPY (
  SELECT
    CASE
      WHEN lovelace = 0                     THEN '00_zero'
      WHEN lovelace < 10000000              THEN '01_under_10_ada'
      WHEN lovelace < 100000000             THEN '02_10_to_100_ada'
      WHEN lovelace < 1000000000            THEN '03_100_to_1k_ada'
      WHEN lovelace < 10000000000           THEN '04_1k_to_10k_ada'
      WHEN lovelace < 100000000000          THEN '05_10k_to_100k_ada'
      WHEN lovelace < 1000000000000         THEN '06_100k_to_1m_ada'
      WHEN lovelace < 10000000000000        THEN '07_1m_to_10m_ada'
      ELSE                                       '08_above_10m_ada'
    END                                          AS size_bucket,
    CASE WHEN is_script THEN 'script' ELSE 'key' END AS credential_type,
    COUNT(*)                                     AS account_count,
    SUM(lovelace)                                AS total_lovelace,
    (SUM(lovelace) / 1000000.0)::bigint          AS total_ada
  FROM t_addr_balance
  GROUP BY size_bucket, credential_type
  ORDER BY credential_type, size_bucket
) TO '/tmp/addressable_pool_size.csv' WITH CSV HEADER;

\echo === [7/8] (D) Addressable-pool registration vintage

COPY (
  WITH with_epoch AS (
    SELECT a.is_script, b.epoch_no AS reg_epoch
    FROM t_addressable a
    JOIN tx t  ON t.id = a.reg_tx_id
    JOIN block b ON b.id = t.block_id
  )
  SELECT
    CASE
      WHEN reg_epoch < 250 THEN '01_shelley_allegra_208_249'
      WHEN reg_epoch < 290 THEN '02_mary_250_289'
      WHEN reg_epoch < 350 THEN '03_alonzo_290_349'
      WHEN reg_epoch < 450 THEN '04_babbage_350_449'
      WHEN reg_epoch < 550 THEN '05_early_conway_450_549'
      ELSE                       '06_late_conway_550_plus'
    END                                          AS reg_vintage,
    CASE WHEN is_script THEN 'script' ELSE 'key' END AS credential_type,
    COUNT(*) AS account_count,
    MIN(reg_epoch) AS min_epoch,
    MAX(reg_epoch) AS max_epoch
  FROM with_epoch
  GROUP BY reg_vintage, credential_type
  ORDER BY credential_type, reg_vintage
) TO '/tmp/addressable_pool_vintage.csv' WITH CSV HEADER;

\echo === [8/8] (E) Addressable-pool lifecycle + (F) Top scripthashes

COPY (
  SELECT
    CASE WHEN is_script THEN 'script' ELSE 'key' END AS credential_type,
    CASE WHEN ever_delegated THEN 'ex_delegator_undelegated' ELSE 'never_delegated' END AS lifecycle,
    COUNT(*)                                         AS account_count,
    SUM(lovelace)                                    AS total_lovelace,
    (SUM(lovelace) / 1000000.0)::bigint              AS total_ada
  FROM t_addr_balance
  GROUP BY credential_type, lifecycle
  ORDER BY credential_type, lifecycle
) TO '/tmp/addressable_pool_lifecycle.csv' WITH CSV HEADER;

COPY (
  WITH per_cred AS (
    SELECT payment_cred,
           MIN(address)        AS sample_address,
           SUM(utxo_count)     AS utxo_count,
           SUM(lovelace)::bigint AS lovelace
    FROM t_no_cred_addr
    WHERE address_type = 'enterprise_script'
    GROUP BY payment_cred
  ),
  total AS (SELECT SUM(lovelace) AS t FROM per_cred)
  SELECT ROW_NUMBER() OVER (ORDER BY p.lovelace DESC) AS rank,
         encode(p.payment_cred, 'hex')                AS scripthash_hex,
         p.sample_address,
         p.utxo_count,
         p.lovelace,
         (p.lovelace / 1000000.0)::bigint             AS ada,
         100.0 * p.lovelace / t.t                     AS pct_of_script_no_cred
  FROM per_cred p, total t
  ORDER BY p.lovelace DESC
  LIMIT 100
) TO '/tmp/script_no_cred_top100.csv' WITH CSV HEADER;

-- Sanity check: total no-cred + total with-cred should ≈ circulation - reward - deposits
COPY (
  SELECT
    'no_stake_credential'                         AS category,
    COUNT(*)                                       AS utxo_count,
    SUM(value)::bigint                             AS total_lovelace,
    (SUM(value) / 1000000.0)::bigint               AS total_ada
  FROM t_unspent
  WHERE stake_address_id IS NULL
  UNION ALL
  SELECT 'has_stake_credential', COUNT(*), SUM(value)::bigint, (SUM(value)/1000000.0)::bigint
  FROM t_unspent
  WHERE stake_address_id IS NOT NULL
) TO '/tmp/utxo_sanity_check.csv' WITH CSV HEADER;

\echo === Done.
