# Fee Layer — CIP Evaluation Synthesis

This folder evaluates the CIPs that act on the **fee layer** of the Cardano reward pipeline — the operator/member split that runs *after* the SL-D1 reward formula has already produced a per-pool allocation. The reward envelope itself is left untouched by these candidates; what changes is how the resulting pool reward is divided between the operator's take and the delegators' share.

<div class="cps-lifecycle" aria-label="CPS lifecycle">
<a class="cps-stage cps-stage-done" href="intended-game.html" title="The Intended Game — plain-prose design baseline">
<span class="cps-stage-num">Stage 01</span>
<span class="cps-stage-label">The Intended Game</span>
<span class="cps-stage-meta">Design intent &middot; baseline</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="diagnostic.html" title="The Mainnet Diagnostic — observations &amp; findings">
<span class="cps-stage-num">Stage 02</span>
<span class="cps-stage-label">Mainnet evidence</span>
<span class="cps-stage-meta">Observations &amp; Findings</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="problem-statements.html" title="Induced Problems — proto-CPS scoped against the diagnostic">
<span class="cps-stage-num">Stage 03</span>
<span class="cps-stage-label">Induced problem</span>
<span class="cps-stage-meta">proto-CPS</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="solution-design.html" title="Solution Design — prioritising the nine problems into directions and milestones">
<span class="cps-stage-num">Stage 04</span>
<span class="cps-stage-label">Solution Design</span>
<span class="cps-stage-meta">Directions &amp; milestones</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<div class="cps-stage cps-stage-current" title="You are here — CIPs Evaluation, fee layer">
<span class="cps-stage-num">Stage 05</span>
<span class="cps-stage-label">CIPs (Evaluation)</span>
<span class="cps-stage-meta">IntersectMBO governance &middot; this section</span>
</div>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-future" href="build-scoping.html" title="Build Estimation / Scoping — sizing the build for the V2 stage-1 reform">
<span class="cps-stage-num">Stage 06</span>
<span class="cps-stage-label">Build Estimation / Scoping</span>
<span class="cps-stage-meta">Build sizing</span>
</a>
</div>

<nav class="cps-sublocation" aria-label="Position within the CIPs evaluation">
<a href="solution-evaluation.html">Existing CIPs</a> <span class="cps-sublocation-sep" aria-hidden="true">&rarr;</span> <span class="cps-sublocation-current">Fee layer</span> <span class="cps-sublocation-sep" aria-hidden="true">&middot;</span> CIP-0023 &amp; CIP-0082
</nav>

The two CIPs in scope ([CIP-0023](cip-0023.md), [CIP-0082](cip-0082.md)) target the priority-1 problem the [mainnet diagnostic](../../diagnostic/README.md) identifies for any V2 reform: **small-operator viability**. Today, **73 % of productive pools sit below the ~3 M ADA viability line**, and **no single-pool retail operator earns a competitive wage** — the median 12 410 ADA/yr covers infrastructure but not 5–15 hours/month of skilled labour. Both CIPs correctly identify this population as the target. They differ on the instrument used (margin floor vs rate floor) and whether `minPoolCost` survives the reform.

CIP-0082's stages 3–4 raise the protocol parameter `k` (target pool count). `k` is not itself a CIP — it is a transversal protocol parameter, raised here as part of the four-stage package. The standalone k-lever analysis that supports the verdict on those stages lives in [cip-0082.md §B.3](cip-0082.md#b3-standalone-k-lever-deep-dive). The same analysis applies to any future k-recalibration proposal — not only to CIP-0082.

**Assessment on both CIPs — problem validated · root-level solution researched · recommendation: place viability at the source first, then assess whether a fee-layer margin floor is still needed as a secondary step.**

**The constructive answer leads — abstract viability from pricing.** `minPoolCost` (flat fee / fixed cost) and `minPoolRate` / `poolRate` (rate / commission) are **pricing tools**: operators should remain free to set them to compete on an open market, because the pricing signal is what delegators read to distinguish between operators. The **viability floor** — the minimum income a productive operator needs to cover operational cost — is a different function and belongs on the **reward-distribution layer (pre-split)**, delivered through a conditional `λ_viability` sub-budget funded from the `λ_size` reduction, **without raising the total pool pot** (full design in the [stake-cap layer synthesis](../pools-distribution/README.md)). A V2 design therefore keeps pricing tools (flat fee + rate) **fully flexible** as competitive levers and engineers viability where it structurally belongs, rather than forcing every operator into the same pricing regime whether they need the floor or not.

**Where the two CIPs sit relative to that source.** CIP-0023 and CIP-0082 correctly identify the target — small-operator viability — but mechanically they address ROS *attractiveness*, not profitability *structure*. Both act on fee-layer pricing (flat-fee reduction, margin / rate floors) to make small pools more ROS-attractive to delegators, without revising the reward-distribution formula itself. For a hollow pool below saturation, pool reward still scales linearly with pool stake ($\hat f' = R \lambda_{\text{size}} \sigma_{\text{rel}}$), so small-operator **absolute profitability** changes only if delegation actually migrates from large pools to small ones — and the diagnostic does not observe that migration: the flow tracks brand, wallet integration, and visibility, not yield.

**Why sequencing matters.** Absent the migration, a flat-rate margin floor can run against its own intent: sub-reliable operator revenue is cut **−9×** under the Margin swap (12 410 → 1 365 ADA/yr, still below the ~28 600 ADA/yr cost floor), and the transfer compounds with fleet size — **+200 K ADA/yr per 11+ pool entity vs −11 K ADA/yr per sub-reliable single-pool operator**. Placing viability at the source first removes that dependency on an unobserved migration; a margin floor, if still wanted, can then be assessed as a complementary pricing choice rather than the viability backstop itself.

## Table of Contents

- [1. Fee-layer parameters](#1-fee-layer-parameters)
- [2. The two candidates](#2-the-two-candidates)
- [3. Reading order](#3-reading-order)
- [4. References](#4-references)

## 1. Fee-layer parameters

The fee-split formula has three parameters with distinct roles:

| Parameter | Type | Current role |
| --- | --- | --- |
| `minPoolCost` | Absolute ADA fixed-fee floor | Deducted from per-pool allocation before the margin split — produces the $1/\sigma$ regressivity hyperbola |
| `minPoolMargin` (CIP-0023) | Relative % margin floor | Applied after `minPoolCost`; targets a floor on operator take |
| `minPoolRate` (CIP-0082 stage 2) | Proportional rate floor | **Replaces** `minPoolCost` under the 4-stage reform; flat 3 % rate everywhere |

*Table 1.1 — Fee-layer parameters. `minPoolCost` is a pricing tool used today as a viability backstop; `minPoolMargin` and `minPoolRate` are the same primitive (a margin floor) at two different calibrations.*

> **Reading aid — what the n-MPO axis means.** *n* = how many pools an operator runs as a single entity. n = 1 means a single-pool operator; n ≥ 11 means an entity controlling 11 or more pools. Findings labelled "n-MPO" measure the per-entity effect across that axis — i.e. how a reform's revenue impact compounds with fleet size. The nine-tier pool-size taxonomy (Dormant → Saturated → Oversaturated) and the n-MPO bracketing are the two reference axes used throughout the per-CIP files.

## 2. The two candidates

| Candidate | Instrument | Assessment | Per-CIP file | Source |
| --- | --- | --- | --- | --- |
| **CIP-0023** — Fair Min Fees | `minPoolMargin` floor (no hard fork) | **Problem validated → folds into CIP-0082 stage 2** — same instrument at a smaller calibration; viability best placed pre-split | [`cip-0023.md`](cip-0023.md) | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| **CIP-0082** — Improved Rewards Scheme Parameters | 4-stage: `minPoolCost` halving (done) → `minPoolRate = 3 %` (HFC) → `k`-raises | **Problem validated → root-level fix first** — viability sits more cleanly pre-split; stages 3–4 sequence after a stake-cap precondition | [`cip-0082.md`](cip-0082.md) | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |

*Table 2.1 — The two fee-layer CIPs and the assessment carried in their per-CIP files.*

**Mechanical relation between the two CIPs.** CIP-0082 stage 2 is mechanically equivalent to a *paired* variant of CIP-0023 (reduction of `minPoolCost` + introduction of a margin floor) — at the extreme calibration: cost taken to zero, rate set to 3 % (vs CIP-0023's illustrative 50 ADA + 1.5 %). The CIP-0082 author credits CIP-0023 explicitly. As live governance items, **CIP-0023 standalone is subsumed by CIP-0082 stage 2** unless governance explicitly declines the hard fork that stage 2 requires.

**On the `k`-raise embedded in CIP-0082 stages 3–4.** The standalone analysis of the `k` lever — its mechanical effect on the split, its delegator-market assumptions, and its structural limits — lives in [cip-0082.md §B.3](cip-0082.md#b3-standalone-k-lever-deep-dive). It is independently citable from any future k-recalibration proposal because the analysis does not depend on stage 2 being in scope.

## 3. Reading order

1. [`cip-0023.md`](cip-0023.md) — narrower instrument, single parameter, clearer historical lineage. Start here: every structural finding on the margin-floor mechanism carries into CIP-0082 stage 2.
2. [`cip-0082.md`](cip-0082.md) — broader 4-stage reform that subsumes and extends the CIP-0023 intent. Stage 2 is CIP-0023's paired variant at harsher calibration; stages 3–4 are pool-count expansions.

The standalone k-lever deep dive in [cip-0082.md §B.3](cip-0082.md#b3-standalone-k-lever-deep-dive) supports the §3 verdict on stages 3–4 and does not need to be read separately.

## 4. References

- **Folder parent:** [`../README.md`](../README.md) — solution-evaluation landing + cross-CIP conclusion.
- **Cross-layer subfolder:** [`../pools-distribution/README.md`](../pools-distribution/README.md) — stake-cap-layer evaluations (the principled home for a viability backstop).
- **Standalone k-lever deep dive:** [cip-0082.md §B.3](cip-0082.md#b3-standalone-k-lever-deep-dive) — supports CIP-0082's §3 verdict on stages 3–4 and remains independently citable for future k-recalibration proposals.
- **Diagnostic anchors:**
  - [Operator-delegator distribution](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md) — fee-rate hyperbola, no-competitive-wage finding, n-MPO brackets.
  - [Pools distribution](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md) — nine-tier pool-size taxonomy, viability and production thresholds.

> **Status:** Active 2026/04/23. Subfolder of [`../README.md`](../README.md). Candidates that act on the fee layer of the Cardano reward pipeline.
