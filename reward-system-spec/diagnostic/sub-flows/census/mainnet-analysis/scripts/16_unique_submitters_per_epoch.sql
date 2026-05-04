-- 16_unique_submitters_per_epoch.sql
-- Distinct fee-paying addresses per epoch
-- Heuristic: first input of each transaction = fee payer
-- Source: db-sync Instance B (full, epoch 627)
-- NOTE: in newer db-sync schemas, the consuming-tx column on tx_in is
-- `tx_in_id` (formerly `tx_id`). Update the JOIN below if you see a
-- "column ti.tx_id does not exist" error.
-- Output: one row per epoch with unique submitter count
-- Figures: figures/unique_submitters_per_epoch.png

WITH tx_submitter AS (
    SELECT
        b.epoch_no,
        txo.address
    FROM tx t
    JOIN block b      ON b.id = t.block_id
    JOIN tx_in ti     ON ti.tx_id = t.id
    JOIN tx_out txo   ON txo.tx_id = ti.tx_out_id
                     AND txo.index = ti.tx_out_index
    WHERE b.epoch_no >= 208
      AND ti.id = (SELECT MIN(ti2.id) FROM tx_in ti2 WHERE ti2.tx_id = t.id)
)
SELECT
    epoch_no,
    COUNT(DISTINCT address) AS unique_submitters
FROM tx_submitter
GROUP BY epoch_no
ORDER BY epoch_no;
