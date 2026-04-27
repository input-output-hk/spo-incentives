# Solution Evaluation — Do the Existing CIPs Solve What V2 Names?

> **Status:** Active 2026/04/22. Working folder evaluating the live CIPs and parameter-level proposals against the V2 specification.

## 1. The situation

The Cardano network has been observed in detail through a multi-stage [mainnet diagnostic](../diagnostic/README.md) — covering the Treasury & Pool-Pots layer, the Pools-Distribution layer, the Operator-Delegator split, and the Staking Census. The diagnostic surfaced a small set of **structural problems** in the current reward system, each grounded in mainnet evidence rather than theory:

- A large share of productive operators sit below the viability line — running pools that do not cover their operational cost, irrespective of how reliably they produce blocks.
- Pledge no longer functions as a binding signal of operator commitment — the formula prices it as a small smooth nudge that the operator population has rationally chosen to ignore.
- Delegator yield is barely differentiated by pool quality — the dispersion delegators see across pools is dominated by fee structure, not by performance.
- Stake concentration bypasses the anti-Sybil mechanics at the entity level — multi-pool operators capture a majority of participating stake, the very pattern the formula's pledge term was meant to discourage.

The [V2 specification](../README.md) turns each of those problems into a **named milestone** — a concrete outcome the next generation of the reward system must deliver. Four are foreground microeconomics — [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [Pledge](../README.md#32-restore-the-notion-of-pledge-among-operators), [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield), [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) — and four are macroeconomics or transversal — [Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), [Price Robustness](../README.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios), and the [Recalibration Pipeline](../README.md#44-the-mechanism-must-be-governable). The dependency chain is strict: Operator Viability → Pledge → Delegator Yield → Deconcentration → Pot Survival → Fee Policy.

**But the CIP backlog already contained proposals before this diagnostic was performed.** [CIP-0023](operator-delegator/cip-0023.md) (2021), [CIP-0037](pools-distribution/cip-0037.md) (2021), [CIP-0050](pools-distribution/cip-0050.md) (2021), and [CIP-0082](operator-delegator/cip-0082.md) (2024) were each drafted with their own framing, their own evidence, and their own design choices. Most are still on the table for governance ratification today. None of them were written with the V2 specification in hand, because V2 did not exist yet.

*The question this folder asks: do those pre-existing proposals — written before the diagnostic — actually deliver the milestones V2 names? Partially? Not at all? Or do some of them, by side-effect, regress on a milestone they don't claim to address?*

## Table of Contents

- [1. The situation](#1-the-situation)
- [2. How this evaluation works](#2-how-this-evaluation-works)
- [3. The candidates and how to read them](#3-the-candidates-and-how-to-read-them)
  - [3.1 Stake-cap layer](#31-stake-cap-layer)
  - [3.2 Fee layer](#32-fee-layer)
  - [3.3 Suggested reading order](#33-suggested-reading-order)
- [4. Cross-CIP analysis](#4-cross-cip-analysis)
  - [4.1 The bundle reduces to two effective candidates](#41-the-bundle-reduces-to-two-effective-candidates)
  - [4.2 Coverage — Microeconomics](#42-coverage-microeconomics)
    - [4.2.1 Operator Viability](#421-operator-viability)
    - [4.2.2 Pledge](#422-pledge)
    - [4.2.3 Delegator Yield](#423-delegator-yield)
    - [4.2.4 Deconcentration](#424-deconcentration)
  - [4.3 The Microeconomics headline](#43-the-microeconomics-headline)
  - [4.4 Cross-CIP findings](#44-cross-cip-findings)
- [5. Verdict — no-go on the existing bundle](#5-verdict-no-go-on-the-existing-bundle)
  - [5.1 Stake-cap CIPs (CIP-0050 / CIP-0037)](#51-stake-cap-cips-cip-0050-cip-0037)
  - [5.2 CIP-0082](#52-cip-0082)
  - [5.3 CIP-0023](#53-cip-0023)
  - [5.4 Sub-aspects untouched by the bundle](#54-sub-aspects-untouched-by-the-bundle)
  - [5.5 Cumulative read](#55-cumulative-read)
- [6. Toward a new proposal](#6-toward-a-new-proposal)
- [7. References](#7-references)

## 2. How this evaluation works

Each candidate is taken on its own terms. The method is the same for every CIP:

- **Read what the proposal itself says it does.** Its rationale, its parameters, its claimed effects — straight from the canonical CIP source.
- **Map it against the V2 milestones.** Which milestone is the primary intent? Which is touched as a side-effect? Which is left untouched?
- **Quantify the mechanical effect on mainnet.** Using the same nine-tier pool-size taxonomy and n-MPO operator-fleet brackets the diagnostic uses, every per-CIP file produces a row-by-row readout of who gains, who loses, and by how much, at current mainnet parameters.
- **Surface verdicts as Delivers / Regresses / Blind spot.** Every quantified finding gets one of three tags, tied to a specific formula property or a specific mainnet measurement. *Delivers* — the proposal achieves what it claims. *Regresses* — the proposal worsens an unrelated milestone by side-effect. *Blind spot* — the proposal depends on a behavioural response the diagnostic does not strongly support.

What this evaluation does **not** do: it does not invent new CIPs (a new proposal is in preparation — see [§6 Toward a new proposal](#6-toward-a-new-proposal)); it does not recommend a package or a sequencing across multiple CIPs; it does not advocate for or against any candidate beyond what the structural analysis shows; it does not assume operator behavioural responses where mainnet provides no signal — those claims are flagged as Blind spot rather than treated as predictions.

## 3. The candidates and how to read them

The reward pipeline has **two independent layers**. The four pre-existing CIPs distribute across them:

### 3.1 Stake-cap layer

Modifies the reward-eligible pool stake $\sigma'$ used inside the SL-D1 reward formula — *upstream* of the operator/member split. The two candidates here propose competing primitives for the same intent: make pledge a binding cap on σ′. → [`pools-distribution/`](pools-distribution/README.md)

| Candidate | Instrument | What it does to a non-compliant pool | Source |
|---|---|---|---|
| [**CIP-0050**](pools-distribution/cip-0050.md) — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` (single scalar) | At L=100, the median retail pool (π = 0.07 %) is clipped to **~7 % of V1 reward** | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| [**CIP-0037**](pools-distribution/cip-0037.md) — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve, with 20 % floor + slope + ceiling (three anchors) | At reference parameters, Healthy-tier pools at the median pledge ratio lose **10–64 %** of reward; Large-healthy / Saturated lose **73–82 %** | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

### 3.2 Fee layer

Modifies the operator/member split *after* the per-pool reward has been computed. The reward envelope itself is untouched. → [`operator-delegator/`](operator-delegator/README.md)

| Candidate | Instrument | What it does | Source |
|---|---|---|---|
| [**CIP-0023**](operator-delegator/cip-0023.md) — Fair Min Fees | `minPoolMargin` floor | Compresses delegator fee-rate dispersion **38× → 13×** in the productive range. Dominated by CIP-0082 stage 2 which reproduces the same intent | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| [**CIP-0082**](operator-delegator/cip-0082.md) — Improved Rewards Scheme Parameters | 4-stage package: stage 1 floor halving (done), stage 2 margin swap (`minPoolCost` → `minPoolRate = 3 %`, hard fork), stages 3–4 `k`-raises (500 → 750 → 1000) | The Margin swap inverts operator revenue across the viability line: Sub-viable **−9×** (12 410 → 1 365 ₳/yr), Saturated **+4×**. On n-MPO axis: 11+-pool MPO **+200 k ₳/yr** vs sub-viable single-pool **+431 ₳/yr** | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |

CIP-0082 stages 3–4 are pool-count expansions — i.e. `k` raises. The mechanical analysis of *what raising `k` actually does to the operator/delegator split, while holding the reward formula fixed* is a sub-document of the CIP-0082 evaluation: → [`operator-delegator/k-parameter.md`](operator-delegator/k-parameter.md). It backs the verdict on CIP-0082's stages 3–4.

### 3.3 Suggested reading order

1. The two layer indexes — [`pools-distribution/README.md`](pools-distribution/README.md), [`operator-delegator/README.md`](operator-delegator/README.md) — for the layer-level framing.
2. The individual per-CIP pages, in any order. CIP-0082 readers should also read [`k-parameter.md`](operator-delegator/k-parameter.md) for stages 3–4.
3. Come back to [§4 Cross-CIP analysis](#4-cross-cip-analysis) for the cross-CIP readout, then [§5 Verdict](#5-verdict-no-go-on-the-existing-bundle) for the overall judgement.

## 4. Cross-CIP analysis

### 4.1 The bundle reduces to two effective candidates

The four pre-existing CIPs are not four independent design decisions. Once each candidate's primitive is read against the others, two structural relations collapse the bundle:

- **CIP-0023 is a subset of CIP-0082 stage 2.** Both rewrite the same per-pool fee split with the same primitive shape — a floor on operator extraction. Stage 2 is the strictly more aggressive version (delete `minPoolCost`, introduce `minPoolRate = 3 %` as a hard fork). Enacting CIP-0023 alongside CIP-0082 doubles the governance surface without adding mechanism.
- **CIP-0050 and CIP-0037 are functionally near-identical.** Both implement the stake-cap intent — make pledge a binding cap on the reward-eligible stake σ′. They differ only in shape: CIP-0050 is a single scalar `L` (hard cap, no floor); CIP-0037 is a three-anchor curve (20 % floor + slope + ceiling). Same primitive, two parameterisations.

Net, **governance is choosing between two effective candidates**:

| Effective candidate | Intent | What is in this slot |
|---|---|---|
| **A stake-cap CIP** | Make pledge a binding signal on σ′ — the [Pledge milestone](../README.md#32-restore-the-notion-of-pledge-among-operators) | CIP-0050 (single hard cap `L`) · CIP-0037 (three-anchor curve with 20 % floor) — pick a shape |
| **CIP-0082** | Multi-stage fee-layer + pool-count package — touches [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield), [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) | Stage 1 floor halving (done) · Stage 2 margin swap (supersedes CIP-0023) · Stages 3–4 `k`: 500 → 750 → 1000 |

The Coverage matrix below preserves all four CIPs as distinct columns — the granularity is still useful when reading specific milestones, especially because CIP-0082's stages behave very differently from each other — but the headline is that the design space is two-dimensional, not four.

### 4.2 Coverage — Microeconomics

V2's Microeconomics chapter ([§3](../README.md#3-microeconomics--participant-incentives-and-market-structure)) names four milestones — **Operator Viability**, **Pledge**, **Delegator Yield**, **Deconcentration** — each broken into sub-aspects that the specification treats as separately addressable. Below, each milestone is mapped onto its sub-aspects, and each cell records what a candidate does at that level of granularity. Symbols: **●** delivers · **○** partial / indirect · **·** neutral · **▼** regresses on this sub-aspect.

CIP-0082's two distinct phases are kept separate: **stage 2** is the Margin swap (delete `minPoolCost`, introduce `minPoolRate`); **stages 3–4** are the `k`-raises (`500 → 750 → 1000`). They behave very differently against each milestone, and lumping them into a single column hides the structural difference between a fee-layer reform and a pool-count expansion.

The Macroeconomics milestones ([V2 §4](../README.md#4-macroeconomics--a-self-sustaining-and-governable-mechanism) — [Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), [Price Robustness](../README.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios), [Recalibration Pipeline](../README.md#44-the-mechanism-must-be-governable)) are deliberately omitted from this coverage view: none of the four pre-existing CIPs targets the pre-depletion-vs-post-depletion pot composition, the fee-generating population, or the recalibration cycle, and the price-robustness implications appear in each per-CIP page rather than as a cross-CIP comparison.

#### 4.2.1 [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)

V2 splits this milestone into a **structural** sub-milestone (the production-threshold rule the protocol must enforce) and an **economic** sub-milestone (every pool above the production threshold must cover its operational cost).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Structural — enforce the production threshold](../README.md#312-structural-enforce-the-production-threshold) | · | · | · | · | · |
| [Economic — every productive pool must be profitable](../README.md#313-economic-every-productive-pool-must-be-profitable) | ○ regressive transfers up the distribution | ▼ Sub-viable revenue **−9×** (12 410 → 1 365 ₳/yr); Saturated **+4×** | ▼ top-tail $P_{\max} = R/k$ compresses; bottom invariant | ▼ retail low-pledge pools clipped to ~7 % of V1 baseline | ○ 20 % floor protects Sub-viable; Healthy & above clipped 10–82 % |

*None of the candidates touches the structural sub-milestone — the production threshold is set by Praos slot mechanics and active stake; no fee-layer parameter or `k`-raise moves it. The economic sub-milestone is where the candidates engage, but every engagement carries a regressive caveat documented in the per-CIP files.*

#### 4.2.2 [Pledge](../README.md#32-restore-the-notion-of-pledge-among-operators)

V2 specifies a single sub-aspect: make pledge a **binding signal** in the reward calculation rather than a small smooth nudge.

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Make pledge a binding signal](../README.md#322-specification) | · | · | · | ● single hard cap | ● cap with 20 % floor |

*Only the stake-cap CIPs target this milestone. Both make pledge binding on the reward-eligible stake σ′; both share a capital-capability bias toward populations that can self-pledge — Custodial-by-extraction stake (~21 % of productive stake) cannot respond. CIP-0037 softens the bottom; CIP-0050 is sharper.*

#### 4.2.3 [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield)

V2 splits this milestone into three sub-aspects: **base yield competitiveness** (the floor of the delegator return), **rewarding operators who play the game** (yield differentiated by operator effort), and **diversifying the offer** (a delegator should be able to read distinct propositions across pools).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Make base yield competitive](../README.md#331-make-the-base-yield-competitive) | · | · | ▼ saturated-pool ceiling shrinks → ROS drops at the top | · | · |
| [Reward operators who play the game](../README.md#332-make-the-yield-reward-operators-who-play-the-game) | ● compresses fee-rate dispersion **38× → 13×** in the productive range | · uniform 3 % rate removes the operator-quality signal | · | ○ pledge-ratio binding price-discriminates pools | ○ pledge-curve binding price-discriminates pools |
| [Diversify the delegation offer](../README.md#333-diversify-the-delegation-offer) | · | ▼ flat 3 % floor eliminates fee-based differentiation | · | · | · |

*CIP-0023 narrows the dispersion delegators see and gives them a cleaner signal across pool sizes. CIP-0082 stage 2 collapses dispersion entirely (same rate everywhere) — which **removes** the fee-based differentiation rather than diversifying it. The stake-cap CIPs introduce a different price-discrimination axis (pledge ratio), which is partial coverage of the "reward those who play the game" sub-aspect.*

#### 4.2.4 [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations)

V2 splits this milestone into the **operator side** (multi-pool entity concentration), **entity-level awareness in reward distribution** (rewards that account for which entity controls a pool, not just the pool itself), and **differentiated delegation incentives** (titan delegators vs the micro-delegation tail).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Operator side — multi-pool entity concentration](../README.md#3411-the-operator-side--multi-pool-entity-concentration) | · | · | ▼ 2020 `k:150→500` precedent: MPO fleet absorption (85 entities, 75.4 % stake, 901 pools today) | ● revenue-neutral pool-splitting at the pool level | ○ slope penalises split; 20 % floor undoes it for sub-floor splits |
| [Entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) | · | · | · | · | · |
| [Differentiated delegation incentives — titans vs micro-delegators](../README.md#343-differentiated-delegation-incentives--titans-versus-micro-delegators) | · | · | · | · | · |

*CIP-0050's revenue-neutral pool-splitting is the sharpest tool for pool-level Deconcentration in the bundle. **None of the candidates addresses entity-level Deconcentration** — the 10 entities holding 1.59 B ₳ via custodial-by-pledge sit above any pool-level cap or floor regardless of the rule. **None addresses the titans-vs-micro-delegators sub-aspect** either — it is a delegator-side incentive question, and no candidate touches the delegator side except through pool-side fee changes.*

### 4.3 The Microeconomics headline

The four pre-existing CIPs cover **Pledge** well (stake-cap CIPs deliver the binding-signal sub-aspect), partially **Operator Viability** and **Delegator Yield** (fee CIPs engage the economic and price-discrimination sub-aspects, with regressive caveats), and only the **operator side** of **Deconcentration** (CIP-0050 in particular).

Three Microeconomics sub-aspects are **entirely untouched** by every candidate:

- the structural sub-milestone of [Operator Viability](../README.md#312-structural-enforce-the-production-threshold) — production-threshold enforcement;
- [entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) inside [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations);
- [differentiated delegation incentives between titans and micro-delegators](../README.md#343-differentiated-delegation-incentives--titans-versus-micro-delegators).

None of the four CIPs was written to target these, because they were drafted before V2 surfaced them as separable problems.

### 4.4 Cross-CIP findings

Five mechanical observations stitch the per-CIP analyses into a single cross-CIP readout. Each is grounded in a specific formula property or a specific mainnet measurement; no behavioural prediction is made unless flagged as such.

**F1 — CIP-0082 stage 2 inverts operator viability for the population it claims to help.** A Sub-viable single-pool operator, who today earns ~12 410 ₳/yr from `minPoolCost = 170`, would earn ~**1 365 ₳/yr** under `minPoolRate = 3 %` — a **9× revenue cut**. A Saturated pool gains **4×**. On the n-MPO fleet axis, the transfer compounds: a sub-viable single-pool operator gains **+431 ₳/yr**; an 11+-pool MPO entity gains **+200 000 ₳/yr**. The reform claims §3.1 viability but the mechanical effect is a regressive transfer up the operator-fleet distribution.

**F2 — Both stake-cap CIPs share a capital-capability bias.** Custodial-by-extraction stake (57 entities, 2.04 B ₳ — about **21 %** of productive stake) holds custodied retail funds the operator legally cannot self-pledge. For this segment, every stake-cap reform produces a reward cut with no recourse — under CIP-0050 the σ′ collapses to zero; under CIP-0037 it's clipped to the 20 % floor. Custodial-by-pledge entities (10 entities, 1.59 B ₳) sit *above* the cap regardless and are unaffected. The reform pressures pools that are not the actual concentration concern.

**F3 — CIP-0023 is structurally dominated by CIP-0082 stage 2.** Both rewrite the same per-pool fee split with the same primitive shape — a floor on operator extraction. Stage 2 is the strictly more aggressive version. Enacting both doubles the governance surface without adding mechanism, which is the structural relation that lets the bundle collapse to two effective candidates in [§4.1](#41-the-bundle-reduces-to-two-effective-candidates).

**F4 — A `k`-raise under the current weak-pledge regime regenerates the 2020 outcome.** The only previous `k` change in Cardano's history (`k: 150 → 500` in August 2020) produced today's MPO landscape: 85 entities operating 901 pools that hold 75.4 % of participating stake. Stages 3–4 of CIP-0082 propose `k: 500 → 750 → 1000` on a 3-epoch cadence, which leaves no window to activate a stake-cap layer in between — meaning the new pool slots fire in exactly the regressive regime [`k-parameter.md`](operator-delegator/k-parameter.md) identifies.

**F5 — The bonus function `A(ν, π)` is untouched by every candidate.** The cubic suppression of the pledge bonus for sub-half-saturated pools, and the quadratic outer size penalty `ν²` that holds at every pledge ratio, survive intact. The four reforms patch *around* the function rather than *into* it — which is why [§4.3 The Microeconomics headline](#43-the-microeconomics-headline) identifies sub-aspects no candidate engages.

## 5. Verdict — no-go on the existing bundle

Read across the four candidates, and through the simplification into two effective candidates ([§4.1](#41-the-bundle-reduces-to-two-effective-candidates)), the verdict is **no-go on the existing bundle as a path to V2**. None of the candidates closes the V2 milestone gap, and each carries a structural caveat that the per-CIP analyses surface as a hard objection rather than a tunable parameter. The table below is the synoptic; the sub-sections argue, each pointing to the per-CIP file that backs the claim.

| Candidate | Verdict | Primary objection | Backed by |
|---|:---:|---|---|
| **CIP-0050** | ▼ no-go | Capital-capability bias — Custodial-by-extraction segment cannot self-pledge; σ′ collapses to zero | [`cip-0050.md`](pools-distribution/cip-0050.md) · [F2](#44-cross-cip-findings) |
| **CIP-0037** | ▼ no-go | Same capital-capability bias; softened by 20 % floor but not removed | [`cip-0037.md`](pools-distribution/cip-0037.md) · [F2](#44-cross-cip-findings) |
| **CIP-0023** | ⊂ moot | Subsumed by CIP-0082 stage 2 — strictly less mechanism, same regression | [`cip-0023.md`](operator-delegator/cip-0023.md) · [F3](#44-cross-cip-findings) |
| **CIP-0082 stage 2** | ▼ no-go | Inverts Operator Viability — Sub-viable **−9×** revenue, **+200 k ₳/yr** to 11+-pool MPO entity | [`cip-0082.md`](operator-delegator/cip-0082.md) · [F1](#44-cross-cip-findings) |
| **CIP-0082 stages 3–4** | ▼ no-go | `k`-raise on a 3-epoch cadence regenerates the 2020 MPO-fleet absorption pattern | [`k-parameter.md`](operator-delegator/k-parameter.md) · [F4](#44-cross-cip-findings) |

### 5.1 Stake-cap CIPs (CIP-0050 / CIP-0037)

Both implement the right intent — binding pledge on σ′ to deliver the [Pledge milestone](../README.md#32-restore-the-notion-of-pledge-among-operators) — but on a population that **cannot respond**. The capital-capability bias documented in [§4.4 / F2](#44-cross-cip-findings) draws the line: Custodial-by-extraction stake (57 entities, 2.04 B ₳, ~21 % of productive stake) holds custodied retail funds the operator legally cannot self-pledge, while Custodial-by-pledge entities (10 entities, 1.59 B ₳) sit *above* any cap regardless. Both shapes — single hard cap (CIP-0050) and three-anchor curve with 20 % floor (CIP-0037) — therefore turn the reform into a regressive transfer to the segments that already concentrate stake.

The verdict is no-go, but the underlying intent is sound. The [new proposal](#6-toward-a-new-proposal) needs a stake-cap mechanic that accommodates Custodial-by-extraction without rewarding Custodial-by-pledge — a constraint neither CIP-0050 nor CIP-0037 can satisfy on its own primitive. The structural argument is in [`cip-0050.md`](pools-distribution/cip-0050.md) and [`cip-0037.md`](pools-distribution/cip-0037.md).

### 5.2 CIP-0082

The four-stage package fails on two of its stages.

**Stage 2 (Margin swap, hard fork).** Inverts operator viability for the population it claims to help. A Sub-viable single-pool operator loses **9× revenue** under `minPoolRate = 3 %` versus today's `minPoolCost = 170` (12 410 → 1 365 ₳/yr); on the n-MPO axis, the same reform transfers **+200 000 ₳/yr** to an 11+-pool MPO entity ([§4.4 / F1](#44-cross-cip-findings)). The stated milestone is Operator Viability; the mechanical effect is a regressive transfer up the operator-fleet distribution. See [`cip-0082.md`](operator-delegator/cip-0082.md).

**Stages 3–4 (`k`: 500 → 750 → 1000 on a 3-epoch cadence).** Reproduce the August 2020 outcome under the current weak-pledge regime. The only previous `k` change in Cardano's history (`k: 150 → 500`) produced today's MPO landscape: 85 entities operating 901 pools that hold 75.4 % of participating stake. The proposed cadence leaves no window to activate a stake-cap layer in between, so the new pool slots fire in exactly the regressive regime ([§4.4 / F4](#44-cross-cip-findings)). The mechanics are in [`k-parameter.md`](operator-delegator/k-parameter.md).

Stage 1 (floor halving, already shipped) is the only stage that survives this evaluation — and it is also the only stage whose mechanical effect is bounded.

### 5.3 CIP-0023

Subsumed by CIP-0082 stage 2 ([§4.4 / F3](#44-cross-cip-findings)) — same intent, less aggressive primitive. Inherits the same regressive transfer up the operator-fleet distribution, with strictly less mechanism. No independent verdict is needed: if Stage 2 is a no-go, CIP-0023 is too. See [`cip-0023.md`](operator-delegator/cip-0023.md).

### 5.4 Sub-aspects untouched by the bundle

Even setting the regressions aside, the bundle is **structurally incomplete against V2** ([§4.3](#43-the-microeconomics-headline)). Three Microeconomics sub-aspects are entirely uncovered:

- the [structural sub-milestone of Operator Viability](../README.md#312-structural-enforce-the-production-threshold) — production-threshold enforcement;
- [entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) — the multi-pool entity lens the diagnostic surfaced is not present in any candidate;
- [differentiated delegation incentives between titans and micro-delegators](../README.md#343-differentiated-delegation-incentives--titans-versus-micro-delegators) — the delegator side is untouched except as a side-effect of pool-side fee changes.

The four pre-existing CIPs were drafted before V2 surfaced these as separable problems, so this gap is not a failure of the candidates — it is a constraint on what the bundle can deliver at all.

### 5.5 Cumulative read

The four pre-existing CIPs each respond to a partial framing of the problem. Treated as a package, **they do not close the V2 milestone set**, and the pieces that do engage individual milestones do so through mechanisms that regress on milestones they do not target. The bundle is not a viable path to V2 as it stands.

This is not a rejection of the underlying intents. CIP-0050 and CIP-0037 capture a real Pledge milestone goal; CIP-0023 and CIP-0082 stage 2 react to a real fee-layer dispersion problem. What the evaluation rejects is the **mechanical realisation** each picks — and the structural caveats are not parameter tunings but objections that the chosen primitives cannot accommodate. The design space needs a fresh proposal that addresses the caveats together rather than in isolation, see [§6 Toward a new proposal](#6-toward-a-new-proposal).

## 6. Toward a new proposal

The structural caveats surfaced by [§5 Verdict](#5-verdict-no-go-on-the-existing-bundle) — combined with the V2 milestones the existing bundle does not close ([V2 §4.1 Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [V2 §4.2 Fee Policy](../README.md#42-the-fee-generating-population-must-expand), the entity-level gap inside [V2 §3.4 Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations), and the untouched bonus function `A(ν, π)`) — motivate a new proposal currently in preparation.

> *Document en préparation. This section will be expanded with a summary and linked to the dedicated proposal page once the draft is ready for review.*

## 7. References

- **V2 specification:** [`../README.md`](../README.md) — §3 milestones, §5 evaluation framework.
- **Mainnet diagnostic:** [`../diagnostic/README.md`](../diagnostic/README.md).
- **Mechanism-intent narrative:** [`../the-intended-game/README.md`](../the-intended-game/README.md).
- **Per-layer indexes:** [`pools-distribution/README.md`](pools-distribution/README.md), [`operator-delegator/README.md`](operator-delegator/README.md).
- **Per-CIP evaluations:** [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md), [`operator-delegator/k-parameter.md`](operator-delegator/k-parameter.md).
- **Canonical CIP sources:** [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs) on GitHub; per-CIP page at [cips.cardano.org](https://cips.cardano.org/).
