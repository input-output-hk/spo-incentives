-- 18_tx_type_composition.sql
-- Script vs key transactions per epoch, with fee breakdown
-- Uses t.script_size as proxy: >0 means the tx includes Plutus scripts
-- Source: db-sync Instance B (full, epoch 627)
-- Output: one row per epoch with script/key tx counts and fee totals
-- Figures: figures/tx_type_composition.png (stacked area)

SELECT
    b.epoch_no,
    COUNT(*) FILTER (WHERE t.script_size > 0)  AS script_tx_count,
    COUNT(*) FILTER (WHERE t.script_size = 0)   AS key_tx_count,
    SUM(t.fee) FILTER (WHERE t.script_size > 0) / 1e6 AS script_fee_ada,
    SUM(t.fee) FILTER (WHERE t.script_size = 0) / 1e6  AS key_fee_ada
FROM tx t
JOIN block b ON b.id = t.block_id
WHERE b.epoch_no >= 208
GROUP BY b.epoch_no
ORDER BY b.epoch_no;
