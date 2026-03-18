# Eta History (Mainnet)

- Definition: `eta_epoch = Blocks_produced_epoch / Blocks_expected_epoch`.
- Mainnet constants from Koios genesis: `active slot coeff = 0.05`, `epoch length = 432000`, so `Blocks_expected_epoch = 21600`.
- Coverage in the refreshed dataset: epochs **208..618**.
- Graph treats epoch **618** as the current partial epoch and keeps **208..617** as the complete-history window.
- Complete-epoch average eta: **0.976972**.
- Complete-epoch minimum eta: **0.895602** at epoch **347** (2022-06-24).
- Complete-epoch maximum eta: **1.005972** at epoch **606** (2026-01-09).
- Complete epochs with `eta > 1`: **7**. These are clipped by `min(eta, 1)` in the reward-pot formula.

## Lowest complete epochs
- Epoch **347** (2022-06-24): `eta = 0.895602` from `19345` blocks out of `21600` expected.
- Epoch **596** (2025-11-20): `eta = 0.901389` from `19470` blocks out of `21600` expected.
- Epoch **348** (2022-06-29): `eta = 0.924907` from `19978` blocks out of `21600` expected.

## Highest complete epochs
- Epoch **606** (2026-01-09): `eta = 1.005972` from `21729` blocks out of `21600` expected.
- Epoch **267** (2021-05-20): `eta = 1.004722` from `21702` blocks out of `21600` expected.
- Epoch **572** (2025-07-23): `eta = 1.001574` from `21634` blocks out of `21600` expected.

## Current partial epoch
- Epoch **618** (2026-03-10): `eta_so_far = 0.511250` from `11043` blocks so far out of `21600` expected.
