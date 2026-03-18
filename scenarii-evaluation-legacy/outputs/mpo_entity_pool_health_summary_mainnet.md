# MPO Entity Pool Health Summary (Mainnet)

_Snapshot built from live Koios data at epoch `617` on `2026-03-10 15:31 UTC`._

## What the health tags mean

- `Healthy core`: live registered pool with at least **3M ADA** active stake. This reuses the report's core viability threshold for consistent block production.
- `Subscale active`: live registered pool with **100k to <3M ADA** active stake.
- `Dormant`: live registered pool with **>0 and <100k ADA** active stake.
- `Zero-stake registered`: still registered, but no live active stake right now.

These are **current-size tags**, not a full 36-epoch profitability verdict.
All counts below refer to **currently registered pools only**.

## Two different questions

- `Operational health` asks whether the current live fleet is materially staked or mostly thin / dormant.
- `Decentralization pressure` asks whether one cluster still controls enough live stake and enough healthy pools to matter for network concentration.
- A cluster can be operationally strong and still be bad news for decentralization. Coinbase is the clearest example.

## Context

- Koios supply: **38.484B ADA**
- Protocol `k`: **500**
- Approximate saturation point: **76.97M ADA per pool**

## Entity summaries

### Coinbase / bison.run

- Claim type: **Same operational cluster**
- Confidence: **Medium-High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **Very high**
- Attribution basis: metadata domains `92a8429c.cardano-metadata.herd.run` (1), `26e894b1.cardano-metadata.herd.run` (1), `7ddb9c28.cardano-metadata.bison.run` (1); Koios `pool_group` `COINBASE` (46); AdaStat n/a; BalanceAnalytics `COINBASE` (44); relay hints `92a8429c.cardano-relay.herd.run` (1), `26e894b1.cardano-relay.herd.run` (1), `7ddb9c28.cardano-relay.bison.run` (1)
- Current fleet: **48 currently registered pools**, **47 with positive live stake**
- Live stake under this entity / cluster: **2.451B ADA** (**6.37%** of supply)
- Current live health mix: **41 Healthy core**, **1 Subscale active**, **5 Dormant**, **1 Zero-stake registered**
- Saturation mix: **23 Near saturation** pools; median live stake = **60.94M ADA**; largest live pool = **119.94M ADA**
- Current live parameters: median pledge = **0 ADA**, average live pledge = **21 ADA**, average margin = **4.64%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **47 Zero pledge** pools and **1 Minimal pledge** pools
- Largest pools:
  - `N/A` 119.94M ADA, pledge 0 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `N/A` 70.98M ADA, pledge 0 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `KOH` 70.54M ADA, pledge 0 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `WGM` 70.34M ADA, pledge 0 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `UBE` 70.33M ADA, pledge 0 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation

### CHUCK BUX

- Claim type: **Unresolved cluster label**
- Confidence: **Low**
- Operational health: **Dense live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `git.io` (1); Koios `pool_group` `CHUCK BUX` (17); AdaStat `stake1u8ww9v63kydymm7hslk4mxyte36str9ehdz06lzsu5r4jlq0e2shk` (2); BalanceAnalytics `CHUCK BUX` (17); relay hints `26.cardano.staked.cloud` (1), `27.cardano.staked.cloud` (1), `28.cardano.staked.cloud` (1)
- Current fleet: **17 currently registered pools**, **15 with positive live stake**
- Live stake under this entity / cluster: **0.834B ADA** (**2.17%** of supply)
- Current live health mix: **13 Healthy core**, **0 Subscale active**, **2 Dormant**, **2 Zero-stake registered**
- Saturation mix: **10 Near saturation** pools; median live stake = **74.03M ADA**; largest live pool = **76.33M ADA**
- Current live parameters: median pledge = **73,000,000 ADA**, average live pledge = **49,466,667 ADA**, average margin = **94.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **5 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `pool1vhz8753...8kp83z` 76.33M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1r99a6pu...4yevz5` 76.32M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1yafxktv...a7aknf` 76.27M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1ntlyr9h...d7p5sh` 74.04M ADA, pledge 73,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1hv59awq...hd7wqr` 74.03M ADA, pledge 73,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation

### Figment

- Claim type: **Same provider cluster**
- Confidence: **Medium-High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `pcpm.s3.amazonaws.com` (37); Koios `pool_group` `FIGMENT` (37); AdaStat `ledger.com` (37); BalanceAnalytics `FIGMENT` (9); relay hints n/a
- Current fleet: **37 currently registered pools**, **36 with positive live stake**
- Live stake under this entity / cluster: **0.788B ADA** (**2.05%** of supply)
- Current live health mix: **19 Healthy core**, **7 Subscale active**, **10 Dormant**, **1 Zero-stake registered**
- Saturation mix: **4 Near saturation** pools; median live stake = **9.52M ADA**; largest live pool = **92.76M ADA**
- Current live parameters: median pledge = **0 ADA**, average live pledge = **1 ADA**, average margin = **8.36%**, average fixed cost = **170 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **37 Minimal pledge** pools
- Largest pools:
  - `pool1f2wfjqk...xjqfze` 92.76M ADA, pledge 2 ADA, margin 6.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `gjp7a` 91.51M ADA, pledge 2 ADA, margin 10.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `LBF4` 84.69M ADA, pledge 2 ADA, margin 6.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `FGMTI` 69.47M ADA, pledge 0 ADA, margin 10.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `pool1cunvnkj...2p24x4` 55.48M ADA, pledge 2 ADA, margin 6.00%, fixed cost 170 ADA, Healthy core, Mid-scale

### Binance

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `s3.amazonaws.com` (32), `binance-ada.s3.us-east-2.amazonaws.com` (13), `s3-us-west-2.amazonaws.com` (5); Koios `pool_group` `BINANCE` (53); AdaStat `binance.com` (50), `infstones.com` (2); BalanceAnalytics `BINANCE` (52); relay hints `54.84.119.195` (13), `52.6.109.221` (2), `3.234.66.234` (2)
- Current fleet: **53 currently registered pools**, **50 with positive live stake**
- Live stake under this entity / cluster: **0.691B ADA** (**1.80%** of supply)
- Current live health mix: **20 Healthy core**, **8 Subscale active**, **22 Dormant**, **3 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **0.13M ADA**; largest live pool = **61.62M ADA**
- Current live parameters: median pledge = **2 ADA**, average live pledge = **1 ADA**, average margin = **6.10%**, average fixed cost = **345 ADA**
- Pledge posture across matched set: **16 Zero pledge** pools and **37 Minimal pledge** pools
- Largest pools:
  - `IFS1` 61.62M ADA, pledge 0 ADA, margin 10.00%, fixed cost 345 ADA, Healthy core, Near saturation
  - `pool1fd0q9h8...wq540p` 59.69M ADA, pledge 0 ADA, margin 10.00%, fixed cost 345 ADA, Healthy core, Mid-scale
  - `KKS` 34.52M ADA, pledge 0 ADA, margin 3.00%, fixed cost 345 ADA, Healthy core, Mid-scale
  - `BNP` 33.34M ADA, pledge 2 ADA, margin 6.00%, fixed cost 345 ADA, Healthy core, Mid-scale
  - `BNP` 33.29M ADA, pledge 2 ADA, margin 6.00%, fixed cost 345 ADA, Healthy core, Mid-scale

### Kiln

- Claim type: **Same provider cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `tinyurl.com` (11); Koios `pool_group` `ADALITE` (10); AdaStat `kiln.fi` (9); BalanceAnalytics `ADALITE` (9); relay hints `relay-trustwallet-5-0.cardano.mainnet.kiln.fi` (1), `relay-trustwallet-5-1.cardano.mainnet.kiln.fi` (1), `relay-trustwallet-5-2.cardano.mainnet.kiln.fi` (1)
- Current fleet: **11 currently registered pools**, **11 with positive live stake**
- Live stake under this entity / cluster: **0.687B ADA** (**1.78%** of supply)
- Current live health mix: **9 Healthy core**, **1 Subscale active**, **1 Dormant**, **0 Zero-stake registered**
- Saturation mix: **6 Near saturation** pools; median live stake = **69.58M ADA**; largest live pool = **116.02M ADA**
- Current live parameters: median pledge = **100 ADA**, average live pledge = **100 ADA**, average margin = **5.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **11 Minimal pledge** pools
- Largest pools:
  - `TW001` 116.02M ADA, pledge 100 ADA, margin 10.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `KILN9` 95.40M ADA, pledge 100 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `KILN4` 76.01M ADA, pledge 100 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `KILN3` 75.94M ADA, pledge 100 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `KILN2` 75.75M ADA, pledge 100 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Near saturation

### Wave / Wavepool

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `meta.wavepool.digital` (14), `raw.githubusercontent.com` (2), `git.io` (1); Koios `pool_group` `WAVE` (16); AdaStat `wavepool.digital` (14), `wavemkr.github.io` (2); BalanceAnalytics `WAVE` (15); relay hints `relays.wavepool.digital` (14), `relay1.cardanowave.com` (1), `relay2.cardanowave.com` (1)
- Current fleet: **17 currently registered pools**, **17 with positive live stake**
- Live stake under this entity / cluster: **0.611B ADA** (**1.59%** of supply)
- Current live health mix: **14 Healthy core**, **0 Subscale active**, **3 Dormant**, **0 Zero-stake registered**
- Saturation mix: **5 Near saturation** pools; median live stake = **34.79M ADA**; largest live pool = **76.12M ADA**
- Current live parameters: median pledge = **1,000,000 ADA**, average live pledge = **13,353,149 ADA**, average margin = **14.83%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **8 Minimal pledge** pools
- Largest pools:
  - `pool1l0m820v...qvg0je` 76.12M ADA, pledge 50,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1ljqjqsk...f9c70f` 75.04M ADA, pledge 30,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1w4cetqs...8xuj9g` 74.94M ADA, pledge 30,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool155p7g23...zyrk44` 73.85M ADA, pledge 50,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1457cnl7...uln20q` 70.32M ADA, pledge 35,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation

### Blockdaemon

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `cardano.blockdaemon.com` (6), `pcpm.s3.amazonaws.com` (1); Koios `pool_group` `BD` (14), `FIGMENT` (1); AdaStat `blockdaemon.com` (8), `ledger.com` (1); BalanceAnalytics `BD` (15); relay hints `bd-cardano-main-relay-12-a.bdnodes.net` (1), `bd-cardano-main-relay-12-b.bdnodes.net` (1), `olive-geonosis-edffc.cardano.bdnodes.net` (1)
- Current fleet: **15 currently registered pools**, **15 with positive live stake**
- Live stake under this entity / cluster: **0.577B ADA** (**1.50%** of supply)
- Current live health mix: **12 Healthy core**, **1 Subscale active**, **2 Dormant**, **0 Zero-stake registered**
- Saturation mix: **4 Near saturation** pools; median live stake = **48.52M ADA**; largest live pool = **75.57M ADA**
- Current live parameters: median pledge = **200 ADA**, average live pledge = **153 ADA**, average margin = **5.73%**, average fixed cost = **272 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **15 Minimal pledge** pools
- Largest pools:
  - `pool1mfyzxyg...krlps5` 75.57M ADA, pledge 200 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1xsj9s3m...sqxrsv` 73.96M ADA, pledge 100 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1zgjk3dz...2d7ekf` 72.82M ADA, pledge 100 ADA, margin 3.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `BD3` 64.79M ADA, pledge 200 ADA, margin 8.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1f9934hk...nl07zj` 57.72M ADA, pledge 200 ADA, margin 3.00%, fixed cost 170 ADA, Healthy core, Mid-scale

### Everstake

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `everstake.one` (15); Koios `pool_group` `EVE` (15); AdaStat `everstake.one` (15); BalanceAnalytics `EVE` (11); relay hints `cardano-main.everstake.one` (15), `cardano-main2.everstake.one` (15), `cardano-relay1.everstake.one` (15)
- Current fleet: **15 currently registered pools**, **15 with positive live stake**
- Live stake under this entity / cluster: **0.567B ADA** (**1.47%** of supply)
- Current live health mix: **12 Healthy core**, **2 Subscale active**, **1 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **41.27M ADA**; largest live pool = **62.14M ADA**
- Current live parameters: median pledge = **1,000 ADA**, average live pledge = **736 ADA**, average margin = **2.93%**, average fixed cost = **339 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **15 Minimal pledge** pools
- Largest pools:
  - `EVE7` 62.14M ADA, pledge 10 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `RSTK` 58.65M ADA, pledge 1,000 ADA, margin 4.00%, fixed cost 400 ADA, Healthy core, Mid-scale
  - `EVE6` 58.64M ADA, pledge 10 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Mid-scale
  - `EVE1` 55.83M ADA, pledge 1,000 ADA, margin 4.00%, fixed cost 400 ADA, Healthy core, Mid-scale
  - `EVRST` 52.07M ADA, pledge 1,000 ADA, margin 4.00%, fixed cost 400 ADA, Healthy core, Mid-scale

### Upbit

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `staking-static.upbit.com` (20); Koios `pool_group` `UPBIT` (20); AdaStat `upbit.com` (20); BalanceAnalytics `UPBIT` (15); relay hints `cardano-relay-1.upbit.com` (20), `cardano-relay-2.upbit.com` (20), `cardano-relay-3.upbit.com` (20)
- Current fleet: **20 currently registered pools**, **20 with positive live stake**
- Live stake under this entity / cluster: **0.551B ADA** (**1.43%** of supply)
- Current live health mix: **20 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **35.01M ADA**; largest live pool = **35.72M ADA**
- Current live parameters: median pledge = **200,000 ADA**, average live pledge = **200,000 ADA**, average margin = **100.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `UPBIT` 35.72M ADA, pledge 200,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `UPBIT` 35.67M ADA, pledge 200,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `UPBIT` 35.65M ADA, pledge 200,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `UPBIT` 35.61M ADA, pledge 200,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `UPBIT` 35.60M ADA, pledge 200,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### eToro

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `etoro-spo.github.io` (14), `bit.ly` (7); Koios `pool_group` `ETORO` (24); AdaStat `etoro.com` (24); BalanceAnalytics `ETORO` (16); relay hints `108.142.42.161` (14), `108.142.42.221` (14), `20.61.228.218` (14)
- Current fleet: **24 currently registered pools**, **12 with positive live stake**
- Live stake under this entity / cluster: **0.472B ADA** (**1.23%** of supply)
- Current live health mix: **11 Healthy core**, **0 Subscale active**, **1 Dormant**, **12 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **50.00M ADA**; largest live pool = **57.00M ADA**
- Current live parameters: median pledge = **0 ADA**, average live pledge = **0 ADA**, average margin = **100.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **24 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `ETO3` 57.00M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ETO9` 54.63M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ETO10` 50.01M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ETO6` 50.00M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ETO11` 50.00M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### YUTA

- Claim type: **Same managed cluster**
- Confidence: **Medium**
- Operational health: **Dense live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `tokyostaker.com` (5), `coinzzz.jp` (5), `popool.net` (4); Koios `pool_group` `YUTA` (25); AdaStat `tokyostaker.com` (5), `coinzzz.jp` (5), `stake1ux2g76f0l7cv8g6ugzc3q54shlh57sqzad0tydysw7srqpq377vgr` (4); BalanceAnalytics `YUTA` (25); relay hints `asia.jazzstakepool.net` (4), `3.111.14.60` (2), `asia-pacific-japan.popsp.net` (2)
- Current fleet: **25 currently registered pools**, **25 with positive live stake**
- Live stake under this entity / cluster: **0.465B ADA** (**1.21%** of supply)
- Current live health mix: **25 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **20.17M ADA**; largest live pool = **37.71M ADA**
- Current live parameters: median pledge = **50,000 ADA**, average live pledge = **46,000 ADA**, average margin = **12.59%**, average fixed cost = **41713 ADA**
- Pledge posture across matched set: **2 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `KTN3` 37.71M ADA, pledge 50,000 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `JP2` 36.88M ADA, pledge 50,000 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ZZZ2` 35.48M ADA, pledge 50,000 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `ZZZ` 31.13M ADA, pledge 50,000 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `JAZZ` 25.59M ADA, pledge 50,000 ADA, margin 5.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### Cardano Foundation

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `mainnet.pool.cardanofoundation.org` (6); Koios `pool_group` `cardanofoundation.org` (6); AdaStat `cardanofoundation.org` (6); BalanceAnalytics n/a; relay hints `cf1r1.mainnet.pool.cardanofoundation.org` (1), `cf1r2.mainnet.pool.cardanofoundation.org` (1), `cf4r1.mainnet.pool.cardanofoundation.org` (1)
- Current fleet: **6 currently registered pools**, **6 with positive live stake**
- Live stake under this entity / cluster: **0.456B ADA** (**1.19%** of supply)
- Current live health mix: **6 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **6 Near saturation** pools; median live stake = **76.30M ADA**; largest live pool = **76.32M ADA**
- Current live parameters: median pledge = **76,000,000 ADA**, average live pledge = **65,291,667 ADA**, average margin = **100.00%**, average fixed cost = **170 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `CF1` 76.32M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `CF4` 76.30M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `CF2` 76.30M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `CF3` 76.30M ADA, pledge 76,000,000 ADA, margin 100.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `CF5` 75.50M ADA, pledge 73,000,000 ADA, margin 100.00%, fixed cost 170 ADA, Healthy core, Near saturation

### NuFi

- Claim type: **Same provider cluster**
- Confidence: **High**
- Operational health: **Dense live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `pools-meta.nu.fi` (17), `adalite.io` (1); Koios `pool_group` `ADALITE` (18); AdaStat `nu.fi` (18); BalanceAnalytics `ADALITE` (18); relay hints `cardano-relays-1.nu.fi` (17), `cardano-relays-2.nu.fi` (17), `34.249.11.89` (1)
- Current fleet: **18 currently registered pools**, **18 with positive live stake**
- Live stake under this entity / cluster: **0.313B ADA** (**0.81%** of supply)
- Current live health mix: **17 Healthy core**, **0 Subscale active**, **1 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **13.06M ADA**; largest live pool = **41.49M ADA**
- Current live parameters: median pledge = **1,000 ADA**, average live pledge = **1,000 ADA**, average margin = **3.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **18 Minimal pledge** pools
- Largest pools:
  - `NUFID` 41.49M ADA, pledge 1,000 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `NUFIE` 36.27M ADA, pledge 1,000 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `NUFI` 30.06M ADA, pledge 1,000 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `NUFI7` 26.64M ADA, pledge 1,000 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `NUFIB` 25.43M ADA, pledge 1,000 ADA, margin 3.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### Emurgo

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `emurgo.github.io` (9), `kficz.github.io` (2), `d5935b72a1770a1a34f5.github.io` (2); Koios `pool_group` `EMURGO` (13); AdaStat `emurgo.io` (9), `theswim.net` (2), `d5935b72a1770a1a34f5.github.io` (2); BalanceAnalytics `EMURGO` (12); relay hints `49.12.123.178` (2), `51.161.35.246` (2), `51.195.91.118` (2)
- Current fleet: **14 currently registered pools**, **11 with positive live stake**
- Live stake under this entity / cluster: **0.271B ADA** (**0.70%** of supply)
- Current live health mix: **8 Healthy core**, **2 Subscale active**, **1 Dormant**, **3 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **14.76M ADA**; largest live pool = **62.45M ADA**
- Current live parameters: median pledge = **500 ADA**, average live pledge = **1,273 ADA**, average margin = **1.55%**, average fixed cost = **201 ADA**
- Pledge posture across matched set: **2 Zero pledge** pools and **9 Minimal pledge** pools
- Largest pools:
  - `EMUR1` 62.45M ADA, pledge 500 ADA, margin 1.50%, fixed cost 170 ADA, Healthy core, Near saturation
  - `EMUR5` 60.46M ADA, pledge 500 ADA, margin 1.50%, fixed cost 170 ADA, Healthy core, Mid-scale
  - `EMUR4` 48.03M ADA, pledge 500 ADA, margin 1.50%, fixed cost 170 ADA, Healthy core, Mid-scale
  - `EMUR3` 42.44M ADA, pledge 500 ADA, margin 1.50%, fixed cost 170 ADA, Healthy core, Mid-scale
  - `EMUR2` 19.09M ADA, pledge 500 ADA, margin 1.50%, fixed cost 170 ADA, Healthy core, Mid-scale

### 1PCT

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **High**
- Attribution basis: metadata domains `www.1percentpool.eu` (28), `www.epicpool.eu` (1), `1pct.net` (1); Koios `pool_group` `1PCT` (29); AdaStat `1percentpool.eu` (28); BalanceAnalytics `1PCT` (29); relay hints `r1.1percentpool.eu` (28), `r2.1percentpool.eu` (28), `relay1.epicpool.eu` (1)
- Current fleet: **30 currently registered pools**, **30 with positive live stake**
- Live stake under this entity / cluster: **0.270B ADA** (**0.70%** of supply)
- Current live health mix: **16 Healthy core**, **12 Subscale active**, **2 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **4.61M ADA**; largest live pool = **68.31M ADA**
- Current live parameters: median pledge = **50,000 ADA**, average live pledge = **51,667 ADA**, average margin = **0.97%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `1PCT0` 68.31M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `1PCT2` 52.55M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `1PCT7` 27.91M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `1PCT9` 16.35M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `1PCT3` 15.65M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### Bloom

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `bloompool.io` (6), `t.co` (1); Koios `pool_group` `BLOOM` (7); AdaStat `bloompool.io` (6); BalanceAnalytics `BLOOM` (7); relay hints `157.245.228.134` (6), `159.89.120.164` (6), `209.97.186.44` (6)
- Current fleet: **7 currently registered pools**, **7 with positive live stake**
- Live stake under this entity / cluster: **0.220B ADA** (**0.57%** of supply)
- Current live health mix: **7 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **30.08M ADA**; largest live pool = **71.03M ADA**
- Current live parameters: median pledge = **1,000,000 ADA**, average live pledge = **10,571,429 ADA**, average margin = **17.71%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `DARK` 71.03M ADA, pledge 68,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `BLOOM` 39.35M ADA, pledge 1,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `BLOOM` 35.17M ADA, pledge 1,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `BLOOM` 30.08M ADA, pledge 1,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `BLOOM` 15.75M ADA, pledge 1,000,000 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Mid-scale

### AdaOcean

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `adaocean.com` (8), `cybercyclone.github.io` (1), `jolly-ocean-0bab2f303.azurestaticapps.net` (1); Koios `pool_group` `OCEAN` (8), `SAFEBLOCK` (1); AdaStat `adaocean.com` (8); BalanceAnalytics `OCEAN` (8); relay hints `relay1.adaocean.com` (8), `relay2.adaocean.com` (8), `relay3.adaocean.com` (8)
- Current fleet: **10 currently registered pools**, **10 with positive live stake**
- Live stake under this entity / cluster: **0.189B ADA** (**0.49%** of supply)
- Current live health mix: **6 Healthy core**, **4 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **12.10M ADA**; largest live pool = **46.52M ADA**
- Current live parameters: median pledge = **10,000 ADA**, average live pledge = **32,000 ADA**, average margin = **3.77%**, average fixed cost = **468 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `OCEA4` 46.52M ADA, pledge 10,000 ADA, margin 3.90%, fixed cost 500 ADA, Healthy core, Mid-scale
  - `OCEA2` 40.20M ADA, pledge 10,000 ADA, margin 3.90%, fixed cost 500 ADA, Healthy core, Mid-scale
  - `OCEA3` 38.75M ADA, pledge 10,000 ADA, margin 3.90%, fixed cost 500 ADA, Healthy core, Mid-scale
  - `OCEAN` 35.73M ADA, pledge 10,000 ADA, margin 3.90%, fixed cost 500 ADA, Healthy core, Mid-scale
  - `OCEA5` 18.72M ADA, pledge 10,000 ADA, margin 3.90%, fixed cost 500 ADA, Healthy core, Mid-scale

### Adalite platform cluster

- Claim type: **Not asserted as same legal entity**
- Confidence: **Low-Medium**
- Operational health: **Thin live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains n/a; Koios `pool_group` `ADALITE` (3); AdaStat n/a; BalanceAnalytics `ADALITE` (3); relay hints `13.236.12.204` (1), `13.211.73.179` (1)
- Current fleet: **3 currently registered pools**, **3 with positive live stake**
- Live stake under this entity / cluster: **0.158B ADA** (**0.41%** of supply)
- Current live health mix: **3 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **2 Near saturation** pools; median live stake = **76.22M ADA**; largest live pool = **76.27M ADA**
- Current live parameters: median pledge = **71,000,000 ADA**, average live pledge = **49,070,000 ADA**, average margin = **100.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `pool1r9fpxs4...740nj9` 76.27M ADA, pledge 71,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1kmmahq4...549yqe` 76.22M ADA, pledge 71,000,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1yraracv...0zueuv` 5.51M ADA, pledge 5,210,000 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Underfilled

### StakeBowl

- Claim type: **Same operator cluster**
- Confidence: **Medium**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `stake-bowl.s3.us-west-2.amazonaws.com` (5), `d2x5gxgj1srogu.cloudfront.net` (3), `neoply.io` (2); Koios `pool_group` `STBL` (10); AdaStat `neoply.io` (10); BalanceAnalytics `STBL` (5), `STAKEBOWL` (2); relay hints `35.164.48.223` (5), `3.35.204.131` (3), `35.75.32.253` (2)
- Current fleet: **10 currently registered pools**, **9 with positive live stake**
- Live stake under this entity / cluster: **0.140B ADA** (**0.36%** of supply)
- Current live health mix: **2 Healthy core**, **0 Subscale active**, **7 Dormant**, **1 Zero-stake registered**
- Saturation mix: **2 Near saturation** pools; median live stake = **0.00M ADA**; largest live pool = **70.05M ADA**
- Current live parameters: median pledge = **0 ADA**, average live pledge = **0 ADA**, average margin = **80.67%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **10 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `SBP1` 70.05M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `SBP2` 70.00M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1m7eljcr...fd4m0h` 0.00M ADA, pledge 0 ADA, margin 13.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `pool1gjmerqh...k2tpdt` 0.00M ADA, pledge 0 ADA, margin 13.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `STBL5` 0.00M ADA, pledge 0 ADA, margin 100.00%, fixed cost 340 ADA, Dormant, Underfilled

### BigLazyCat

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Thin live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `www.biglazycat.com` (2), `api.biglazycat.com` (1); Koios `pool_group` `BLC` (2); AdaStat `biglazycat.com` (2); BalanceAnalytics `BLC` (2); relay hints `ada-relay01.biglazycat.com` (1), `ada-relay02.biglazycat.com` (1), `ada-relay03.biglazycat.com` (1)
- Current fleet: **3 currently registered pools**, **3 with positive live stake**
- Live stake under this entity / cluster: **0.130B ADA** (**0.34%** of supply)
- Current live health mix: **3 Healthy core**, **0 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **49.32M ADA**; largest live pool = **68.83M ADA**
- Current live parameters: median pledge = **1,000 ADA**, average live pledge = **1,000 ADA**, average margin = **0.67%**, average fixed cost = **283 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **3 Minimal pledge** pools
- Largest pools:
  - `BLC` 68.83M ADA, pledge 1,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `pool1a0kp4vl...0zwt7t` 49.32M ADA, pledge 1,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Mid-scale
  - `BLC3` 12.06M ADA, pledge 1,000 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Underfilled

### P2P

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Moderate**
- Attribution basis: metadata domains `cardano.p2p.org` (5), `static.cardano.p2p.world` (1), `k8s-pool.subnet.dev` (1); Koios `pool_group` `P2P` (6); AdaStat `p2p.org` (6); BalanceAnalytics `P2P` (3); relay hints `170.23.181.50` (2), `relay1.ppcx1.mainnet.cardano.p2p.org` (1), `relay2.ppcx1.mainnet.cardano.p2p.org` (1)
- Current fleet: **7 currently registered pools**, **6 with positive live stake**
- Live stake under this entity / cluster: **0.098B ADA** (**0.25%** of supply)
- Current live health mix: **5 Healthy core**, **1 Subscale active**, **0 Dormant**, **1 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **9.57M ADA**; largest live pool = **61.66M ADA**
- Current live parameters: median pledge = **1,000 ADA**, average live pledge = **35,417 ADA**, average margin = **2.17%**, average fixed cost = **312 ADA**
- Pledge posture across matched set: **2 Zero pledge** pools and **3 Minimal pledge** pools
- Largest pools:
  - `PPTG1` 61.66M ADA, pledge 500 ADA, margin 4.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `P2P` 11.39M ADA, pledge 10,000 ADA, margin 2.00%, fixed cost 340 ADA, Healthy core, Underfilled
  - `PPCX1` 11.36M ADA, pledge 1,000 ADA, margin 3.50%, fixed cost 340 ADA, Healthy core, Underfilled
  - `P2P2` 7.78M ADA, pledge 0 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Underfilled
  - `PPCX2` 4.72M ADA, pledge 1,000 ADA, margin 3.50%, fixed cost 340 ADA, Healthy core, Underfilled

### Spire

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mostly healthy live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `data.spireblockchain.com` (3), `data.spirestaking.com` (2); Koios `pool_group` `SPIRE` (5); AdaStat `anetabtc.io` (3), `spirestaking.com` (2); BalanceAnalytics `SPIRE` (4); relay hints `r1.spireblockchain.com` (3), `r1.spirestaking.com` (2)
- Current fleet: **5 currently registered pools**, **5 with positive live stake**
- Live stake under this entity / cluster: **0.096B ADA** (**0.25%** of supply)
- Current live health mix: **3 Healthy core**, **2 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **8.23M ADA**; largest live pool = **75.10M ADA**
- Current live parameters: median pledge = **880 ADA**, average live pledge = **250,432 ADA**, average margin = **22.20%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **3 Minimal pledge** pools
- Largest pools:
  - `SPIRE` 75.10M ADA, pledge 1,000,000 ADA, margin 1.00%, fixed cost 340 ADA, Healthy core, Near saturation
  - `SPIR2` 12.10M ADA, pledge 250,000 ADA, margin 0.00%, fixed cost 340 ADA, Healthy core, Underfilled
  - `lSPF0` 8.23M ADA, pledge 400 ADA, margin 100.00%, fixed cost 340 ADA, Healthy core, Underfilled
  - `NETA1` 0.74M ADA, pledge 880 ADA, margin 5.00%, fixed cost 340 ADA, Subscale active, Underfilled
  - `NETA2` 0.28M ADA, pledge 880 ADA, margin 5.00%, fixed cost 340 ADA, Subscale active, Underfilled

### AutoStake

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Thin live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `autostake.com` (4); Koios `pool_group` `NGINE` (4); AdaStat `autostake.com` (4); BalanceAnalytics `NGINE` (4); relay hints `cardano-relays.autostake.com` (4)
- Current fleet: **4 currently registered pools**, **4 with positive live stake**
- Live stake under this entity / cluster: **0.084B ADA** (**0.22%** of supply)
- Current live health mix: **2 Healthy core**, **2 Subscale active**, **0 Dormant**, **0 Zero-stake registered**
- Saturation mix: **1 Near saturation** pools; median live stake = **10.52M ADA**; largest live pool = **62.58M ADA**
- Current live parameters: median pledge = **100 ADA**, average live pledge = **100 ADA**, average margin = **0.00%**, average fixed cost = **170 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **4 Minimal pledge** pools
- Largest pools:
  - `AUTO` 62.58M ADA, pledge 100 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Near saturation
  - `AUTO` 20.67M ADA, pledge 100 ADA, margin 0.00%, fixed cost 170 ADA, Healthy core, Mid-scale
  - `AUTO` 0.38M ADA, pledge 100 ADA, margin 0.00%, fixed cost 170 ADA, Subscale active, Underfilled
  - `AUTO` 0.20M ADA, pledge 100 ADA, margin 0.00%, fixed cost 170 ADA, Subscale active, Underfilled

### IOG

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `pools.iohk.io` (30), `iog1.cardano.iog.io` (1), `mainnet.assets.midnightpool.network` (1); Koios `pool_group` `IOG` (32); AdaStat `iohk.io` (31); BalanceAnalytics `IOG` (32); relay hints `relays-new.cardano-mainnet.iohk.io` (33), `iog1-relays.cardano.iog.io` (1), `backbone.cardano.iog.io` (1)
- Current fleet: **35 currently registered pools**, **9 with positive live stake**
- Live stake under this entity / cluster: **0.013B ADA** (**0.03%** of supply)
- Current live health mix: **1 Healthy core**, **1 Subscale active**, **7 Dormant**, **26 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **0.00M ADA**; largest live pool = **11.37M ADA**
- Current live parameters: median pledge = **64,000,000 ADA**, average live pledge = **36,111,900 ADA**, average margin = **59.11%**, average fixed cost = **429 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **3 Minimal pledge** pools
- Largest pools:
  - `IOG1` 11.37M ADA, pledge 5,000,000 ADA, margin 7.00%, fixed cost 340 ADA, Healthy core, Underfilled
  - `NIGHT` 1.62M ADA, pledge 1,000 ADA, margin 0.00%, fixed cost 340 ADA, Subscale active, Underfilled
  - `REIT` 0.02M ADA, pledge 5,000 ADA, margin 25.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `CANW0` 0.00M ADA, pledge 1,097 ADA, margin 0.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `IOGP` 0.00M ADA, pledge 64,000,000 ADA, margin 100.00%, fixed cost 500 ADA, Dormant, Underfilled

### RAID

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `git.io` (7); Koios `pool_group` `RAID` (7); AdaStat `raidpools.com` (7); BalanceAnalytics `RAID` (7); relay hints `34.107.5.15` (7)
- Current fleet: **7 currently registered pools**, **7 with positive live stake**
- Live stake under this entity / cluster: **0.000B ADA** (**0.00%** of supply)
- Current live health mix: **0 Healthy core**, **2 Subscale active**, **5 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **0.04M ADA**; largest live pool = **0.13M ADA**
- Current live parameters: median pledge = **30,000 ADA**, average live pledge = **32,857 ADA**, average margin = **1.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **0 Minimal pledge** pools
- Largest pools:
  - `RAID6` 0.13M ADA, pledge 30,000 ADA, margin 1.00%, fixed cost 340 ADA, Subscale active, Underfilled
  - `RAID3` 0.10M ADA, pledge 50,000 ADA, margin 1.00%, fixed cost 340 ADA, Subscale active, Underfilled
  - `RAID5` 0.04M ADA, pledge 30,000 ADA, margin 1.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `RAID1` 0.04M ADA, pledge 30,000 ADA, margin 1.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `RAID2` 0.04M ADA, pledge 30,000 ADA, margin 1.00%, fixed cost 340 ADA, Dormant, Underfilled

### RockX

- Claim type: **Same operator cluster**
- Confidence: **High**
- Operational health: **Mixed live fleet**
- Decentralization pressure: **Limited**
- Attribution basis: metadata domains `static.rockx.com` (10); Koios `pool_group` `ROCKX` (10); AdaStat `rockx.com` (10); BalanceAnalytics `ROCKX` (10); relay hints `ruby-cardano.rockx.com` (1), `garnet-cardano.rockx.com` (1), `diamond-cardano.rockx.com` (1)
- Current fleet: **10 currently registered pools**, **10 with positive live stake**
- Live stake under this entity / cluster: **0.000B ADA** (**0.00%** of supply)
- Current live health mix: **0 Healthy core**, **1 Subscale active**, **9 Dormant**, **0 Zero-stake registered**
- Saturation mix: **0 Near saturation** pools; median live stake = **0.00M ADA**; largest live pool = **0.19M ADA**
- Current live parameters: median pledge = **100 ADA**, average live pledge = **101 ADA**, average margin = **2.00%**, average fixed cost = **340 ADA**
- Pledge posture across matched set: **0 Zero pledge** pools and **10 Minimal pledge** pools
- Largest pools:
  - `RXR` 0.19M ADA, pledge 100 ADA, margin 2.00%, fixed cost 340 ADA, Subscale active, Underfilled
  - `RXG` 0.00M ADA, pledge 100 ADA, margin 2.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `RXD` 0.00M ADA, pledge 110 ADA, margin 2.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `RXP` 0.00M ADA, pledge 100 ADA, margin 2.00%, fixed cost 340 ADA, Dormant, Underfilled
  - `RXE` 0.00M ADA, pledge 100 ADA, margin 2.00%, fixed cost 340 ADA, Dormant, Underfilled

## Interpretation

- A large pool count is not automatically the same thing as 47 equally large pools. The summary above uses currently registered pools only, then separates those with positive live stake from zero-stake registrations.
- For custodial or provider clusters, the more important question is not just count, but how many pools are actually carrying material live stake and how thin the pledge is relative to that stake.
- Coinbase / bison.run is still the biggest concentration issue in this cut: **47 live positive-stake pools**, **41 healthy-core pools**, and **6.37% of supply**, with near-zero pledge on almost the entire fleet.
- The detailed pool sheet is in `mpo_entity_pool_health_mainnet.csv`; the one-row-per-entity overview is in `mpo_entity_health_overview_mainnet.csv`.
- If you need the historical / retired attribution set later, use `mpo_entity_pool_mapping_mainnet.csv` instead of the current-only health outputs.
