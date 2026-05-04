-- 19_submitter_staking_overlap.sql
-- Classify top fee-paying addresses by CIP-19 address type and delegation status
-- Depends on: 17_fee_concentration.sql output (materialized or CTE)
-- Source: db-sync Instance B (full, epoch 627). Requires `tx_out.stake_address_id`
-- (only present on full db-sync) to do the delegation-status join cleanly.
-- Output: fee share by address type × staking_status (delegating /
-- has_cred_not_delegating / no_stake_cred), top500 vs full population.
-- Figures: figures/submitter_staking_overlap_627.png

-- Reference output produced 2026/05/04 → data/submitter_staking_overlap_627.csv
-- The query below is the legacy address-prefix-only version. The actual run
-- on Instance B replaces Step 3 with a direct join on
--   epoch_stake es WHERE es.epoch_no = 627 AND es.addr_id = txo.stake_address_id
-- which is far cleaner than the deferred bech32 decode this file originally
-- recommended.

-- Step 1: reuse the top-500 submitters from 17_fee_concentration
WITH tx_submitter AS (
    SELECT
        t.id AS tx_id,
        t.fee,
        b.epoch_no,
        txo.address
    FROM tx t
    JOIN block b      ON b.id = t.block_id
    JOIN tx_in ti     ON ti.tx_id = t.id
    JOIN tx_out txo   ON txo.tx_id = ti.tx_out_id
                     AND txo.index = ti.tx_out_index
    WHERE b.epoch_no BETWEEN 600 AND 623
      AND ti.id = (SELECT MIN(ti2.id) FROM tx_in ti2 WHERE ti2.tx_id = t.id)
),
top_submitters AS (
    SELECT
        address,
        COUNT(*)           AS tx_count,
        SUM(fee) / 1e6     AS total_fee_ada
    FROM tx_submitter
    GROUP BY address
    ORDER BY total_fee_ada DESC
    LIMIT 500
),
-- Step 2: classify by CIP-19 address prefix
-- addr1q = type 0 (base, key/key) — has staking part
-- addr1v = type 6 (enterprise, key) — no staking part
-- addr1z = type 2 (base, script/key) — has staking part
-- addr1w = type 7 (enterprise, script) — no staking part
-- addr1x = type 4 (base, key/script)
-- addr1y = type 5 (base, script/script)
classified AS (
    SELECT
        ts.*,
        CASE
            WHEN ts.address LIKE 'addr1q%' THEN 'base_key'
            WHEN ts.address LIKE 'addr1v%' THEN 'enterprise_key'
            WHEN ts.address LIKE 'addr1z%' THEN 'base_script'
            WHEN ts.address LIKE 'addr1w%' THEN 'enterprise_script'
            WHEN ts.address LIKE 'addr1x%' THEN 'base_key_script'
            WHEN ts.address LIKE 'addr1y%' THEN 'base_script_script'
            ELSE 'other'
        END AS addr_type
    FROM top_submitters ts
)
SELECT
    addr_type,
    COUNT(*)           AS n_addresses,
    SUM(total_fee_ada) AS fee_ada,
    SUM(tx_count)      AS txs
FROM classified
GROUP BY addr_type
ORDER BY fee_ada DESC;

-- Step 3 (separate query): for base_key addresses, check delegation status
-- This requires joining with epoch_stake at epoch 623 on the staking credential
-- extracted from the address. The staking credential is bytes 29–57 of the
-- decoded bech32 address. This step may be easier in Python post-processing.
