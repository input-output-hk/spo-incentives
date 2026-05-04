-- 15_tx_epoch_summary.sql
-- Per-epoch transaction count and total fees (Shelley onward)
-- Source: db-sync Instance B (full, epoch 627)
-- Output: one row per epoch with tx count, total/avg/median fee
-- Figures: figures/tx_epoch_summary.png

SELECT
    b.epoch_no,
    COUNT(*)            AS tx_count,
    SUM(t.fee) / 1e6    AS total_fee_ada,
    AVG(t.fee) / 1e6    AS avg_fee_ada,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.fee) / 1e6 AS median_fee_ada
FROM tx t
JOIN block b ON b.id = t.block_id
WHERE b.epoch_no >= 208
GROUP BY b.epoch_no
ORDER BY b.epoch_no;
