# Pool Pledge Ratio by Size History Summary (Mainnet)

_Built on `2026-03-09 15:38 UTC` from local pool history through epoch `615` plus live Koios epoch `617`._

## What this chart shows

- Each panel is a **pool size category**.
- The stacked colors show how much **active stake** sits in pools with different **declared pledge / active stake ratios**.
- The dashed black line is the **total active stake** in that size category.

## Live read

- In the `>70M ADA` size bucket at live epoch `617`, active stake totals **5.864B ADA**.
- Within that same `>70M ADA` bucket, active stake in the tiny-but-nonzero pledge-ratio band `>0-0.001%` is **0.930B ADA**.
- Within that same `>70M ADA` bucket, active stake in the very high pledge-ratio band `>50%` is **1.652B ADA**.

## Interpretation

- This is a better lens than a pure pledge-amount chart when you want to compare small and large pools on the same economic footing.
- A pool with `100 ADA` pledge means something very different at `1M ADA` stake than at `70M ADA` stake.
- The chart therefore normalizes pledge against pool scale instead of looking at absolute pledge only.
