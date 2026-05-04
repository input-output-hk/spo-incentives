-- 20_submitter_growth.sql
-- Per-epoch: new submitters (first-ever tx) vs returning submitters
-- WARNING: this query is expensive — it requires a full scan of tx + tx_in + tx_out
-- to find each address's first epoch. Consider materializing first_tx as a table.
-- Source: db-sync Instance B (full, epoch 627)
-- Output: one row per epoch with active/new/returning submitter counts
-- Figures: figures/submitter_growth.png (stacked area)

WITH first_tx AS (
    SELECT
        txo.address,
        MIN(b.epoch_no) AS first_epoch
    FROM tx t
    JOIN block b      ON b.id = t.block_id
    JOIN tx_in ti     ON ti.tx_id = t.id
    JOIN tx_out txo   ON txo.tx_id = ti.tx_out_id
                     AND txo.index = ti.tx_out_index
    WHERE b.epoch_no >= 208
      AND ti.id = (SELECT MIN(ti2.id) FROM tx_in ti2 WHERE ti2.tx_id = t.id)
    GROUP BY txo.address
),
per_epoch AS (
    SELECT DISTINCT
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
    pe.epoch_no,
    COUNT(DISTINCT pe.address)                                              AS active_submitters,
    COUNT(DISTINCT pe.address) FILTER (WHERE ft.first_epoch = pe.epoch_no)  AS new_submitters,
    COUNT(DISTINCT pe.address) FILTER (WHERE ft.first_epoch < pe.epoch_no)  AS returning_submitters
FROM per_epoch pe
JOIN first_tx ft ON ft.address = pe.address
GROUP BY pe.epoch_no
ORDER BY pe.epoch_no;
