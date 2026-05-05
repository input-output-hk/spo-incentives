# Fee Layer — CIP Evaluation Synthesis

This folder evaluates the CIPs that act on the **fee layer** of the Cardano reward pipeline — the operator/member split that runs *after* the SL-D1 reward formula has already produced a per-pool allocation. The reward envelope itself is left untouched by these candidates; what changes is how the resulting pool reward is divided between the operator's take and the delegators' share.

The two CIPs in scope ([CIP-0023](cip-0023.md), [CIP-0082](cip-0082.md)) target the priority-1 problem the [mainnet diagnostic](../../diagnostic/README.md) identifies for any V2 reform: **small-operator viability**. Today, **73 % of productive pools sit below the ~3 M ADA viability line**, and **no single-pool retail operator earns a competitive wage** — the median 12 410 ADA/yr covers infrastructure but not 5–15 hours/month of skilled labour. Both CIPs correctly identify this population as the target. They differ on the instrument used (margin floor vs rate floor) and whether `minPoolCost` survives the reform.

A third candidate filed here — the [`k`-parameter standalone lever](k-parameter.md) — is a transversal protocol parameter rather than a fee-layer primitive, but its standalone analysis holds the pool-distribution formula fixed, so it interacts with operator revenue through the per-pool ceiling $P_{\max} = R/k$ rather than through the reward envelope.

**Verdict on both CIPs: no-go, for one structural reason.**

**The two CIPs correctly identify the target — small-operator viability — but mechanically they address ROS attractiveness, not profitability structure.** Both act on fee-layer pricing (flat-fee reduction, margin / rate floors) to make small pools more *ROS-attractive* to delegators. But neither revises the reward-distribution formula itself. For a hollow pool below saturation, pool reward still scales linearly with pool stake ($\hat f' = R \lambda_{\text{size}} \sigma_{\text{rel}}$). Small-operator **absolute profitability** therefore changes only if delegation actually migrates from large pools to small ones — the fee reform by itself does not raise what a small-pool operator earns at constant size.

**The redistribution bet is unevidenced.** Both CIPs implicitly depend on that migration. The diagnostic does not support it: delegation is not sticky, but not clearly yield-following either — the observed flow tracks brand, wallet integration, and visibility. There is no mainnet signal that the migration will occur at the scale the CIPs need.

**If the migration does not happen, the reforms invert their intent.** Without the redistribution, fee-layer tightening produces the opposite outcome of what the CIPs target: it **fragilises the small-operator population** (sub-reliable operator revenue cut −9× under the Margin swap, while remaining below the ~28 600 ADA/yr cost floor); it **amplifies multi-pool operator concentration** (the transfer compounds with fleet size — +200 K ADA/yr per 11+ pool entity vs −11 K ADA/yr per sub-reliable single-pool operator); and it **amplifies profit disparity** because proportional margin rules scale operator take linearly with pool reward.

**A principled separation — abstract viability from pricing.** `minPoolCost` (flat fee / fixed cost) and `minPoolRate` / `poolRate` (rate / commission) are **pricing tools**. Operators should remain free to set them to compete on an open market; the pricing signal is what delegators read to distinguish between operators. The **viability floor** (the minimum income a productive operator needs to cover operational cost) is a different function and belongs on a different layer. Conflating them — as CIP-0023 and CIP-0082 do by using pricing floors to bolt viability into the fee structure — forces every operator into the same pricing regime whether they need the floor or not, and weakens the pricing signal. A V2 design should:

- Keep pricing tools (flat fee + rate) **fully flexible** as competitive levers.
- Engineer the viability floor elsewhere — on the reward-distribution layer (pre-split), not on the fee-split layer (post-split). Stake-cap instruments ([`../pools-distribution/`](../pools-distribution/README.md)) reshape the reward-eligible stake before the formula applies; a dedicated viability primitive is an open design question.

## Table of Contents

- [1. Fee-layer parameters](#1-fee-layer-parameters)
- [2. The two candidates](#2-the-two-candidates)
- [3. Composition with other layers and `k`](#3-composition-with-other-layers-and-k)
- [4. Reading order](#4-reading-order)
- [5. References](#5-references)

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

| Candidate | Instrument | Verdict | Per-CIP file | Source |
| --- | --- | --- | --- | --- |
| **CIP-0023** — Fair Min Fees | `minPoolMargin` floor (no hard fork) | **No-go as standalone** — same instrument as CIP-0082 stage 2 with smaller calibration | [`cip-0023.md`](cip-0023.md) | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| **CIP-0082** — Improved Rewards Scheme Parameters | 4-stage: `minPoolCost` halving (done) → `minPoolRate = 3 %` (HFC) → `k`-raises | **No-go as standalone** — stage 2 inverts operator revenue, stages 3–4 fire in the wrong regime | [`cip-0082.md`](cip-0082.md) | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |
| **`k` lever** — target-pool count (standalone) | `stakePoolTargetNum` | **No-go as standalone** — under weak pledge, MPO fleets absorb new slots | [`k-parameter.md`](k-parameter.md) | Protocol parameter — no dedicated CIP; filed here as the standalone analysis holds the pool-distribution formula fixed and affects the operator/member split via $P_{\max} = R/k$ |

*Table 2.1 — Fee-layer-cluster candidates and the verdict carried in their per-CIP files.*

**Mechanical relation between the two CIPs.** CIP-0082 stage 2 is mechanically equivalent to a *paired* variant of CIP-0023 (reduction of `minPoolCost` + introduction of a margin floor) — at the extreme calibration: cost taken to zero, rate set to 3 % (vs CIP-0023's illustrative 50 ADA + 1.5 %). The CIP-0082 author credits CIP-0023 explicitly. As live governance items, **CIP-0023 standalone is subsumed by CIP-0082 stage 2** unless governance explicitly declines the hard fork that stage 2 requires.

## 3. Composition with other layers and `k`

| Composition | Status |
| --- | --- |
| CIP-0023 ⊕ CIP-0082 (same-layer) | **Not canonical** — both rewrite the per-pool fee split. Pick one primitive (margin floor or rate floor); union is incoherent |
| Fee layer ⊕ stake-cap layer (cross-layer) | **Clean** — layers act on different stages of the reward pipeline. No precedence rule required |

*Table 3.1 — Composition of the fee-layer candidates with the rest of the bundle.*

**Design decision.** Is the right primitive a *margin* floor (CIP-0023) or a *rate* floor (CIP-0082 stage 2)? Does the absolute floor (`minPoolCost`) survive the reform? These are analysed in both per-CIP files.

**`k` interaction.** The standalone `k`-lever analysis at [`k-parameter.md`](k-parameter.md) deliberately holds the reward formula fixed. CIP-0082 stages 3–4 raise `k` from 500 → 750 → 1000, just **6 epochs** after the Margin swap (stage 2) — leaving no window to negotiate, vote, and activate a stake-cap layer in between. Stages 3–4 therefore fire in exactly the regime [`k-parameter.md`](k-parameter.md) identifies as regressive: weak pledge, MPO-dominated fleet, empirically non-yield-following delegator base. The package either needs to acquire a stake-cap layer between stage 2 and stage 3, or to remove stages 3–4.

**V2 sequencing — fee layer first, stake-cap second, `k` third.** A coherent V2 deployment sequences the levers so that each step's preconditions are satisfied by the prior step. Fee-layer reform alone — without a viability primitive on the reward-distribution layer — produces the regressive transfer documented in the per-CIP files; that is why a future proposal must move the viability function to the right layer before any pricing reform is enacted.

## 4. Reading order

1. [`cip-0023.md`](cip-0023.md) — narrower instrument, single parameter, clearer historical lineage. Start here: every structural finding on the margin-floor mechanism carries into CIP-0082 stage 2.
2. [`cip-0082.md`](cip-0082.md) — broader 4-stage reform that subsumes and extends the CIP-0023 intent. Stage 2 is CIP-0023's paired variant at harsher calibration; stages 3–4 are pool-count expansions.
3. [`k-parameter.md`](k-parameter.md) — the standalone `k`-lever analysis; companion to CIP-0082 stages 3–4.

## 5. References

- **Folder parent:** [`../README.md`](../README.md) — solution-evaluation landing + cross-CIP conclusion.
- **Cross-layer subfolder:** [`../pools-distribution/README.md`](../pools-distribution/README.md) — stake-cap-layer evaluations (the principled home for a viability backstop).
- **Transversal lever in this folder:** [`k-parameter.md`](k-parameter.md) — standalone `k`-raise analysis; companion to CIP-0082 stages 3–4.
- **Diagnostic anchors:**
  - [Operator-delegator distribution](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md) — fee-rate hyperbola, no-competitive-wage finding, n-MPO brackets.
  - [Pools distribution](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md) — nine-tier pool-size taxonomy, viability and production thresholds.

> **Status:** Active 2026/04/23. Subfolder of [`../README.md`](../README.md). Candidates that act on the fee layer of the Cardano reward pipeline.
