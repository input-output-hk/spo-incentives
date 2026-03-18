# Pool Stake Size and Pledge History Summary (Mainnet)

_Built on `2026-03-09 15:27 UTC` from local pool history through epoch `615` plus live Koios epoch `617`._

## What was built

- `pool_active_stake_by_size_history_mainnet.png`: stacked area chart of total active stake split by **current pool size bucket** in each epoch, plus the total active stake line.
- `pool_active_stake_by_pledge_band_history_mainnet.png`: stacked area chart of total active stake split by the pool's **declared pledge band** in each epoch, plus the total active stake line.

## Live checkpoint read

- Live epoch `617` total active stake in registered positive-stake pools: **21.788B ADA**
- Live epoch `617` active stake in the `>70M ADA` size band: **5.864B ADA**
- Live epoch `617` active stake in pledge bands below `10k ADA`: **9.813B ADA**

## Interpretation

- The size chart shows how the head of very large pools expanded and contracted over time relative to the full active stake base.
- The pledge-band chart answers a different question: not how big the pools are, but how much active stake sits behind pools with different declared pledge levels.
- These two lenses are complementary: one is about **pool scale**, the other about **capital commitment posture**.
