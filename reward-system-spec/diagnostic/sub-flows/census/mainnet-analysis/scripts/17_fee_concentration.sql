-- 17_fee_concentration.sql
-- Top fee-paying addresses over epochs 622–627 (recent window)
-- Heuristic: first input of each transaction = fee payer
-- Source: db-sync Instance B (full, epoch 627)
-- Output: top 500 addresses by cumulative fee expenditure
-- Figures: figures/fee_concentration_627.png (Lorenz curve)
-- NOTE: in newer db-sync schemas, the consuming-tx column on tx_in is
-- `tx_in_id` (formerly `tx_id`). Update the JOIN below if needed.

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
)
SELECT
    address,
    COUNT(*)           AS tx_count,
    SUM(fee) / 1e6     AS total_fee_ada,
    AVG(fee) / 1e6     AS avg_fee_ada
FROM tx_submitter
GROUP BY address
ORDER BY total_fee_ada DESC
LIMIT 500;
