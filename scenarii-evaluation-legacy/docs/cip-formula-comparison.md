# CIP Formula Comparison vs Status Quo

## Table of Contents
- [Scope](#scope)
- [Shared Assumptions](#shared-assumptions)
- [What Was Implemented](#what-was-implemented)
- [Simulation Runs Included](#simulation-runs-included)
- [Formula Comparison vs Status Quo](#formula-comparison-vs-status-quo)
- [Reward-Production Layer Comparison](#reward-production-layer-comparison)
- [Fee-Split Layer Comparison](#fee-split-layer-comparison)
- [Direct K=1000 Implication](#direct-k1000-implication)
- [Simulation Smoke Results](#simulation-smoke-results)
- [Comparison Summary](#comparison-summary)
- [Next Simulation Step](#next-simulation-step)

## Scope

This document compares the formula deltas of `CIP-0023`, `CIP-0037`, `CIP-0050`, and `CIP-0082`
against the Shelley-aligned status quo at the deterministic formula layer.

It covers two layers separately:
- reward production: what changes the pool reward curve itself
- fee split: what changes how operator and delegators split an already-computed pool reward

It does **not** attempt to model the full equilibrium dynamics here. That remains the next step.

## Shared Assumptions

- `K` baseline: `500`
- `a0`: `0.3`
- Saturation at `K=500`: `76,000,000` ADA
- Implied active stake anchor: `38,000,000,000` ADA
- Epoch pool reward pot anchor: `11,500,000` ADA
- Current `minPoolCost` anchor: `170` ADA
- `CIP-0023` illustrative `minPoolMargin`: `5%`
- `CIP-0082` Stage 2 `minPoolRate`: `3%`
- `CIP-0050` illustrative leverage `L`: `100`
- `CIP-0037` pledge reference: `500,000` ADA
- `CIP-0037` saturation floor: `10%` of `K` saturation

## What Was Implemented

- `Status Quo`: baseline Shelley reward function and baseline operator/member split.
- `CIP-0023`: fee-layer clamp only. Pool reward production stays identical to the status quo.
- `CIP-0082`: Stage 2 fee-layer reform (`minPoolCost = 0`, `minPoolRate = 3%`). Stages 3 and 4 are treated separately as `K` changes.
- `CIP-0050`: reward-eligible stake cap becomes `min(stake, z0, L * pledge)`.
- `CIP-0037`: pool saturation becomes pledge-dependent with a lower-limit floor.

## Simulation Runs Included

This document now includes a small comparable smoke batch from the strategic simulator as a visibility aid.
Those runs use the same compact parameters across variants:
- `n = 50`
- `k = 10`
- `a0 = 0.3`
- `seed = 42`
- `max_iterations = 20`

These are **not** the final policy-evaluation runs. They only confirm that the five variants execute cleanly in the engine
and give a first same-parameter comparison point against the status quo.

## Formula Comparison vs Status Quo

The comparison splits cleanly into two buckets:
- `CIP-0023` and `CIP-0082` are primarily fee-layer changes.
- `CIP-0050` and `CIP-0037` are primarily reward-production / stake-cap changes.

That distinction matters because `CIP-0023` and `CIP-0082` do not change the raw pool reward curve at fixed `K`,
while `CIP-0050` and `CIP-0037` can materially reduce or reshape the reward earned by high-stake / low-pledge pools.

## Reward-Production Layer Comparison

Table below compares pool reward production for four representative pool states. `CIP-0023` and `CIP-0082`
match the status quo here because they do not alter the pool reward function itself at fixed `K`.

| Case | Stake (ADA) | Pledge (ADA) | Status Quo reward | CIP-0023 reward | CIP-0082 reward | CIP-0050 reward | CIP-0050 delta % | CIP-0037 reward | CIP-0037 delta % | CIP-0037 dyn sat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Small growth pool | 3,000,000 | 1,000 | 698.38 | 698.38 | 698.38 | 23.28 | -96.67 | 698.38 | 0.00 | 7,600,000 |
| Mid-sized pool | 10,000,000 | 10,000 | 2,328.03 | 2,328.03 | 2,328.03 | 232.80 | -90.00 | 1,769.30 | -24.00 | 7,600,000 |
| Large pool | 40,000,000 | 25,000 | 9,312.66 | 9,312.66 | 9,312.66 | 582.04 | -93.75 | 1,769.40 | -81.00 | 7,600,000 |
| Saturated pool | 76,000,000 | 500,000 | 17,727.23 | 17,727.23 | 17,727.23 | 11,662.57 | -34.21 | 17,727.23 | 0.00 | 76,000,000 |

Reading:
- `CIP-0050` only diverges materially once `L * pledge` is below the pool stake or below the normal saturation cap.
- `CIP-0037` can diverge much earlier because it rewrites the saturation threshold itself.
- For small or moderately growing pools, `CIP-0037` still allows headroom thanks to the floor, but large low-pledge pools lose reward-eligible capacity quickly.

## Fee-Split Layer Comparison

This table fixes the pool reward formula to the status quo and then compares how the same reward gets split.
Each example uses a registered margin of `0%`, so the fee-floor effects are visible immediately.

| Case | Pool reward (ADA) | Status Quo operator | Status Quo delegator 10k | CIP-0023 operator | CIP-0023 delegator 10k | CIP-0082 operator | CIP-0082 delegator 10k |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3M stake / 1k pledge / 0% margin | 698.38 | 170.18 | 1.76 | 196.59 | 1.67 | 21.18 | 2.26 |
| 10M stake / 10k pledge / 0% margin | 2,328.03 | 172.16 | 2.16 | 279.95 | 2.05 | 72.10 | 2.26 |
| 76M stake / 500k pledge / 0% margin | 17,727.23 | 285.51 | 2.31 | 1,157.59 | 2.19 | 644.94 | 2.26 |

Reading:
- `CIP-0023` raises operator take by clamping low margins upward while keeping the fixed-fee floor in place.
- `CIP-0082` Stage 2 removes the fixed-fee floor, so the operator loses the guaranteed fixed component but still receives the 3% rate floor.
- For smaller pools, that means `CIP-0082` can materially improve delegator fairness while worsening operator protection.

## Direct K=1000 Implication

Even before any strategic simulation, the raw formula already shows what `K=1000` means: saturation halves.

| Scenario | Target K | Saturation (ADA) | Reward at saturation |
| --- | --- | --- | --- |
| Status Quo / K=500 | 500 | 76,000,000 | 17,727.23 |
| CIP-0082 Stage 4 style / K=1000 | 1000 | 38,000,000 | 8,881.07 |

This is why `K=1000` must stay a separate policy axis.
It is not a cosmetic tweak. It changes the economic scale of a 'full' pool.

## Simulation Smoke Results

Smoke-run outputs live under the engine output root:
- `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output`

| Variant | Engine scheme | Equilibrium | Pool count | Operator count | Nakamoto | Pledge fraction | Output folder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Status Quo | CardanoRSS | Yes | 10 | 10 | 6 | 0.3375 | 11-doc-status-quo-smoke |
| CIP-0023 | CIP23RSS | Yes | 10 | 10 | 6 | 0.3375 | 13-doc-cip23-smoke |
| CIP-0037 | CIP37RSS | Yes | 10 | 10 | 6 | 0.3375 | 12-doc-cip37-smoke |
| CIP-0050 | CIP50RSS | Yes | 10 | 10 | 6 | 0.3375 | 11-doc-cip50-smoke |
| CIP-0082 | CIP82RSS | Yes | 10 | 10 | 6 | 0.3375 | 14-doc-cip82-smoke |

Reading:
- All five smoke runs converge and expose their results in concrete output folders.
- On this tiny validation setup, the final descriptors are identical across variants, so this section is only a run check, not yet a discriminating policy result.
- The real comparison signal should come from larger equilibrium batches at realistic `k` and stake-distribution settings.

## Comparison Summary

- `Status Quo`: common global saturation, existing pledge term, fixed-cost floor intact.
- `CIP-0023`: no reward-curve change; pure fee-floor intervention via minimum margin.
- `CIP-0082`: no reward-curve change at Stage 2; strong fee-layer redesign. Stages 3/4 are really `K` policy changes.
- `CIP-0050`: keeps the existing saturation rule but adds a leverage ceiling based on pledge.
- `CIP-0037`: changes the saturation rule itself, so the pool reward curve becomes pool-specific.

From a modeling perspective, the cleanest interpretation is:
- `0023` and `0082` answer operator/delegator split fairness.
- `0050` and `0037` answer pledge discipline and MPO leverage.

## Next Simulation Step

The next implementation step is to push these formula deltas into the strategic simulator in two layers:

1. stake-cap layer: `Status Quo`, `CIP-0050`, `CIP-0037`
2. fee layer: `Status Quo`, `CIP-0023`, `CIP-0082`

Then the scenario matrix can combine exactly one rule from each layer and compare equilibrium outcomes against the status quo.
