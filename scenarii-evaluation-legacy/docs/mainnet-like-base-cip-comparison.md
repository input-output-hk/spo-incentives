# Mainnet-like Base CIP Comparison

## Table of Contents
- [Scope](#scope)
- [Mainnet-like Input](#mainnet-like-input)
- [Run Parameters](#run-parameters)
- [Scenario Set](#scenario-set)
- [Headline Results](#headline-results)
- [Early-Path Shock](#early-path-shock)
- [Margin and Pledge Read](#margin-and-pledge-read)
- [Interpretation](#interpretation)
- [Raw Outputs](#raw-outputs)
- [Caveats](#caveats)

## Scope

This report compares `Status Quo`, `CIP-0023`, `CIP-0037`, `CIP-0050`, and `CIP-0082`
inside the strategic simulation engine using a current mainnet-like pool-level stake distribution rather than the tiny smoke setup.

## Mainnet-like Input

The stake distribution is built from the current local mainnet snapshot already present in this workspace:
- source file: `scenarii-evaluation/data/koios_pool_list_mainnet.csv`
- currently registered pools with positive stake: `2718`
- active stake represented in this run set: `21,747,864,605.370` ADA
- each positive-stake registered pool contributes one stake value into the engine file-based distribution

This is a **pool-level active-stake distribution**, not a wallet-level delegation snapshot.
It is still much closer to current mainnet structure than the earlier Pareto smoke test.

## Run Parameters

- `k = 500`
- `a0 = 0.3`
- `seed = 42`
- `max_iterations = 150`
- `iterations_after_convergence = 10`
- metrics tracked: `[1, 2, 6, 17, 18, 24, 25, 30]`
- `CIP-0023` floor: `5%`
- `CIP-0050` leverage: `L = 100`
- `CIP-0037` reference: `500,000` ADA with floor `10%`
- `CIP-0082` min rate: `3%`

## Scenario Set

- `Status Quo`: baseline Cardano reward scheme.
- `CIP-0023`: minimum margin floor only.
- `CIP-0037`: pledge-linked saturation, rebased to the active stake represented by this snapshot.
- `CIP-0050`: pledge leverage cap with `L=100`.
- `CIP-0082`: current engine approximation of Stage 2 with `minPoolRate=3%` while preserving operator cost inputs.

## Headline Results

| Scenario | Status | Pools | Delta vs SQ | Operators | Nakamoto | Rounds | Max pools/op |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Status Quo | completed | 501 | 0 | 329 | 124 | 48 | 3 |
| CIP-0023 | completed | 500 | -1 | 328 | 123 | 23 | 3 |
| CIP-0037 | completed | 502 | 1 | 329 | 124 | 37 | 3 |
| CIP-0050 | completed | 500 | -1 | 328 | 124 | 40 | 3 |
| CIP-0082 | completed | 501 | 0 | 329 | 123 | 23 | 3 |

## Early-Path Shock

| Scenario | Status | Step 1 pools | Notes |
| --- | --- | --- | --- |
| Status Quo | completed | 3270 | completed run |
| CIP-0023 | completed | 9764 | completed run |
| CIP-0037 | completed | 5643 | completed run |
| CIP-0050 | completed | 2545 | completed run |
| CIP-0082 | completed | 9486 | completed run |

## Margin and Pledge Read

| Scenario | Status | Step 1 pools | Mean margin | Median margin | Pledge fraction | Output folder | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Status Quo | completed | 3270 | 0.0442 | 0.0447 | 0.7734 | 15-mainnet-like-status-quo | completed run |
| CIP-0023 | completed | 9764 | 0.0652 | 0.0561 | 0.7706 | 18-mainnet-like-cip23-minmargin5 | completed run |
| CIP-0037 | completed | 5643 | 0.0441 | 0.0454 | 0.7729 | 16-mainnet-like-cip37-currentref | completed run |
| CIP-0050 | completed | 2545 | 0.0395 | 0.0389 | 0.7696 | 17-mainnet-like-cip50-L100 | completed run |
| CIP-0082 | completed | 9486 | 0.0574 | 0.0554 | 0.7729 | 20-mainnet-like-cip82-minrate3 | completed run |

## Interpretation

- The mainnet-like setup breaks the artificial smoke-run symmetry immediately.
- `CIP-0023` materially raises the final margin regime and converges much faster than the status quo in this run set.
- `CIP-0037` changes the early trajectory strongly, but lands near the baseline final structure in this first pass.
- `CIP-0050` with `L=100` slightly reduces pools/operators and ends with the lowest margin regime among the completed runs.
- `CIP-0082` should now be read as a margin-floor-only engine approximation until the fee layer is modeled more faithfully.
- The comparison should be read as a first current-mainnet run set, not as a final ledger-faithful economic forecast.

## Raw Outputs

- `Status Quo`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/15-mainnet-like-status-quo`
- `CIP-0023`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/18-mainnet-like-cip23-minmargin5`
- `CIP-0037`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/16-mainnet-like-cip37-currentref`
- `CIP-0050`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/17-mainnet-like-cip50-L100`
- `CIP-0082`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/20-mainnet-like-cip82-minrate3`

## Caveats

- The engine still uses an approximation for fee-layer economics; `CIP-0023` and `CIP-0082` are not fully ledger-faithful.
- The input distribution is pool-level active stake, not wallet-level stake-holder distribution.
- This batch keeps `k=500`; the separate `k=1000` policy axis still needs its own run set.
