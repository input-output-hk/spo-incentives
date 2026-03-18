# Zero-Pledge Large Pool History Summary (Mainnet)

_Built on `2026-03-12 09:53 UTC` from local history through epoch `615` plus live Koios epoch `618`._

## Why this chart is the right comparison

- The report's pool-size discussion uses the `>70M ADA` threshold, so the history chart keeps that threshold to stay comparable.
- Declared pledge is reconstructed from `koios_pool_updates_mainnet.csv`, not from owner snapshots, because owner-history alone misses many large pools.
- A second exact-zero line uses `>=80%` of saturation to show the stricter near-saturation bucket.

## Key points

- Report checkpoint reproduced: epoch `583` has **77** pools above `70M ADA`.
- At that same epoch, **34** of those pools had declared pledge below **10k ADA**, holding **2.509B ADA**.
- At that same epoch, **24** of those pools were already exact zero-pledge, holding **1.702B ADA**.
- Latest local epoch `615`: **81** pools above `70M ADA`; **37** below `10k ADA` pledge; **24** exact zero-pledge.
- Live Koios epoch `618`: **82** pools above `70M ADA`; **37** below `10k ADA` pledge holding **2.823B ADA**; **25** exact zero-pledge holding **1.805B ADA**.
- Peak exact-zero `>70M` count in local history: epoch `483` with **28** pools.
- Peak exact-zero `>70M` stake in local history: epoch `232` with **2.107B ADA**.

## Interpretation

- The report's large-pool count matches the local recomputation exactly.
- The broader low-pledge large-pool phenomenon is stronger than the exact-zero subset. At the report endpoint, nearly half of the `>70M ADA` pools were already below `10k ADA` pledge.
- The exact-zero large-pool phenomenon is not a new live artifact; it is already visible at the report endpoint once pledge is reconstructed from registration updates rather than sparse owner snapshots.
- The live point remains in the same broad range rather than showing a sudden recent explosion.
