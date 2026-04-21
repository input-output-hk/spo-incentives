-- §1 + §2: ADA supply decomposition + staking rate per epoch

COPY (
  SELECT
    a.epoch_no,
    a.reserves                                                               AS reserve,
    a.treasury                                                               AS treasury,
    a.utxo + a.rewards + a.deposits_stake + a.deposits_drep
      + a.deposits_proposal + a.fees                                         AS circulating,
    a.utxo                                                                   AS utxo,
    a.rewards                                                                AS unclaimed_rewards,
    a.deposits_stake + a.deposits_drep + a.deposits_proposal                 AS deposits,
    a.fees                                                                   AS fees_pot
  FROM ada_pots a
  ORDER BY a.epoch_no
) TO '/tmp/supply_decomposition.csv' WITH CSV HEADER;

COPY (
  SELECT
    epoch_no,
    SUM(amount)          AS total_staked,
    COUNT(*)             AS delegation_count,
    COUNT(DISTINCT pool_id) AS pool_count
  FROM epoch_stake
  GROUP BY epoch_no
  ORDER BY epoch_no
) TO '/tmp/staking_per_epoch.csv' WITH CSV HEADER;
