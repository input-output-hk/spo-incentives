# Solution Evaluation — Do the Existing CIPs Solve What V2 Names?

The Cardano network has been observed in detail through a multi-stage [mainnet diagnostic](../diagnostic/README.md) — covering the Treasury & Pool-Pots layer, the Pools-Distribution layer, the Operator-Delegator split, and the Staking Census. The diagnostic surfaced a small set of **structural problems** in the current reward system, each grounded in mainnet evidence rather than theory:

- **A large share of productive operators sit below the viability line** — 73 % of productive pools sit below the ~3 M ADA viability line (OPE.O6.F4); no single-pool retail operator earns a competitive wage at current ADA prices, irrespective of how reliably they produce blocks.
- **Pledge no longer functions as a binding signal of operator commitment** — POL.O2.F1 reports 78 % of staked ADA sits in pools with pledge ratio < 1 %, and POL.O5.F3 finds 42 of 48 saturation-scale MPOs forfeit the pledge bonus. The formula prices pledge as a small smooth nudge (POL.O2.F2: pledge yield 0.68 %/yr vs ~2.3 %/yr passive delegation) that the operator population has rationally chosen to ignore.
- **Delegator yield is barely differentiated by pool quality** — today's delegator fee-rate dispersion across the productive range is **38×** (27.3 % at Sub-reliable pools vs 0.71 % at saturation); the dispersion delegators see is dominated by fee structure, not by performance, and delegation flow does not track yield (OPE.O7.F1).
- **Stake concentration bypasses the anti-Sybil mechanics at the entity level** — 83 attributed entities operating 449 productive pools today control 76.7 % of productive stake; multi-pool operators capture a majority, the very pattern the formula's pledge term was meant to discourage.

The [V2 specification](../README.md) turns each of those problems into a **named milestone** — a concrete outcome the next generation of the reward system must deliver. Four are foreground microeconomics — [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [Pledge](../README.md#32-restore-the-notion-of-pledge-among-operators), [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield), [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) — and four are macroeconomics or transversal — [Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), [Price Robustness](../README.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios), and the [Recalibration Pipeline](../README.md#44-the-mechanism-must-be-governable). The dependency chain is strict: Operator Viability → Pledge → Delegator Yield → Deconcentration → Pot Survival → Fee Policy.

**But the CIP backlog already contained proposals before this diagnostic was performed.** [CIP-0023](operator-delegator/cip-0023.md) (2021), [CIP-0037](pools-distribution/cip-0037.md) (2021), [CIP-0050](pools-distribution/cip-0050.md) (2021), and [CIP-0082](operator-delegator/cip-0082.md) (2024) were each drafted with their own framing, their own evidence, and their own design choices. Most are still on the table for governance ratification today. None of them were written with the V2 specification in hand, because V2 did not exist yet.

*The question this folder asks: do those pre-existing proposals — written before the diagnostic — actually deliver the milestones V2 names? Partially? Not at all? Or do some of them, by side-effect, regress on a milestone they don't claim to address?*

## Table of Contents

- [1. How this evaluation works](#1-how-this-evaluation-works)
- [2. The candidates and how to read them](#2-the-candidates-and-how-to-read-them)
  - [2.1. Stake-cap layer](#21-stake-cap-layer)
  - [2.2. Fee layer](#22-fee-layer)
- [3. Cross-CIP analysis](#3-cross-cip-analysis)
  - [3.1. The bundle reduces to two effective candidates](#31-the-bundle-reduces-to-two-effective-candidates)
  - [3.2. Coverage — Microeconomics](#32-coverage-microeconomics)
    - [3.2.1. Operator Viability](#321-operator-viability)
    - [3.2.2. Pledge](#322-pledge)
    - [3.2.3. Delegator Yield](#323-delegator-yield)
    - [3.2.4. Deconcentration](#324-deconcentration)
  - [3.3. The Microeconomics headline](#33-the-microeconomics-headline)
  - [3.4. Cross-CIP findings](#34-cross-cip-findings)
- [4. Verdict — no-go on the existing bundle](#4-verdict-no-go-on-the-existing-bundle)
  - [4.1. Stake-cap CIPs (CIP-0050 / CIP-0037)](#41-stake-cap-cips-cip-0050-cip-0037)
  - [4.2. CIP-0082](#42-cip-0082)
  - [4.3. CIP-0023](#43-cip-0023)
  - [4.4. Sub-aspects untouched by the bundle](#44-sub-aspects-untouched-by-the-bundle)
  - [4.5. Cumulative read](#45-cumulative-read)
- [5. Toward a new proposal](#5-toward-a-new-proposal)
- [6. References](#6-references)

## 1. How this evaluation works

Each candidate is taken on its own terms. The method is the same for every CIP:

- **Read what the proposal itself says it does.** Its rationale, its parameters, its claimed effects — straight from the canonical CIP source.
- **Map it against the V2 milestones.** Which milestone is the primary intent? Which is touched as a side-effect? Which is left untouched?
- **Quantify the mechanical effect on mainnet.** Using the same nine-tier pool-size taxonomy and n-MPO operator-fleet brackets the diagnostic uses, every per-CIP file produces a row-by-row readout of who gains, who loses, and by how much, at current mainnet parameters.
- **Surface verdicts as Delivers / Regresses / Blind spot.** Every quantified finding gets one of three tags, tied to a specific formula property or a specific mainnet measurement. *Delivers* — the proposal achieves what it claims. *Regresses* — the proposal worsens an unrelated milestone by side-effect. *Blind spot* — the proposal depends on a behavioural response the diagnostic does not strongly support.

What this evaluation does **not** do: it does not invent new CIPs (a new proposal is in preparation — see [Toward a new proposal](#5-toward-a-new-proposal)); it does not recommend a package or a sequencing across multiple CIPs; it does not advocate for or against any candidate beyond what the structural analysis shows; it does not assume operator behavioural responses where mainnet provides no signal — those claims are flagged as Blind spot rather than treated as predictions.

## 2. The candidates and how to read them

The reward pipeline has **two independent layers**. The four pre-existing CIPs distribute across them:

### 2.1. Stake-cap layer

Modifies the reward-eligible pool stake $\sigma'$ used inside the SL-D1 reward formula — *upstream* of the operator/member split. The two candidates here propose competing primitives for the same intent: make pledge a binding cap on σ′. → [`pools-distribution/`](pools-distribution/README.md)

| Candidate | Instrument | What it does to a zero-pledge pool | Source |
|---|---|---|---|
| [**CIP-0050**](pools-distribution/cip-0050.md) — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` (single scalar) | At L=100, the median retail pool (π = 0.07 %) is clipped to **~7 % of V1 reward** | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| [**CIP-0037**](pools-distribution/cip-0037.md) — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve, with 20 % floor + slope + ceiling (three anchors) | At reference parameters, Healthy-tier pools at the median pledge ratio lose **10–64 %** of reward; Large-healthy / Saturated lose **73–82 %** | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

### 2.2. Fee layer

Modifies the operator/member split *after* the per-pool reward has been computed. The reward envelope itself is untouched. → [`operator-delegator/`](operator-delegator/README.md)

| Candidate | Instrument | What it does | Source |
|---|---|---|---|
| [**CIP-0023**](operator-delegator/cip-0023.md) — Fair Min Fees | `minPoolMargin` floor | Compresses delegator fee-rate dispersion **38× → 13×** in the productive range. Dominated by CIP-0082 stage 2 which reproduces the same intent | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| [**CIP-0082**](operator-delegator/cip-0082.md) — Improved Rewards Scheme Parameters | 4-stage package: stage 1 floor halving (done), stage 2 margin swap (`minPoolCost` → `minPoolRate = 3 %`, hard fork), stages 3–4 `k`-raises (500 → 750 → 1000) | The Margin swap inverts operator revenue across the viability line: Sub-reliable **−9×** (12 410 → 1 365 ₳/yr), Saturated **+4×**. On n-MPO axis: 11+-pool MPO **+200 k ₳/yr** vs sub-reliable single-pool **+431 ₳/yr** | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |

CIP-0082 stages 3–4 are pool-count expansions — i.e. `k` raises. The mechanical analysis of *what raising `k` actually does to the operator/delegator split, while holding the reward formula fixed* is a sub-document of the CIP-0082 evaluation: → [`operator-delegator/k-parameter.md`](operator-delegator/k-parameter.md). It backs the verdict on CIP-0082's stages 3–4.

## 3. Cross-CIP analysis

### 3.1. The bundle reduces to two effective candidates

The four pre-existing CIPs are not four independent design decisions. Once each candidate's primitive is read against the others, two structural relations collapse the bundle:

- **CIP-0023 is a subset of CIP-0082 stage 2.** Both rewrite the same per-pool fee split with the same primitive shape — a floor on operator extraction. Stage 2 is the strictly more aggressive version (delete `minPoolCost`, introduce `minPoolRate = 3 %` as a hard fork). Enacting CIP-0023 alongside CIP-0082 doubles the governance surface without adding mechanism.
- **CIP-0050 and CIP-0037 are functionally near-identical.** Both implement the stake-cap intent — make pledge a binding cap on the reward-eligible stake σ′. They differ only in shape: CIP-0050 is a single scalar `L` (hard cap, no floor); CIP-0037 is a three-anchor curve (20 % floor + slope + ceiling). Same primitive, two parameterisations.

Net, **governance is choosing between two effective candidates**:

| Effective candidate | Intent | What is in this slot |
|---|---|---|
| **A stake-cap CIP** | Make pledge a binding signal on σ′ — the [Pledge milestone](../README.md#32-restore-the-notion-of-pledge-among-operators) | CIP-0050 (single hard cap `L`) · CIP-0037 (three-anchor curve with 20 % floor) — pick a shape |
| **CIP-0082** | Multi-stage fee-layer + pool-count package — touches [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield), [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) | Stage 1 floor halving (done) · Stage 2 margin swap (supersedes CIP-0023) · Stages 3–4 `k`: 500 → 750 → 1000 |

The Coverage matrix below preserves all four CIPs as distinct columns — the granularity is still useful when reading specific milestones, especially because CIP-0082's stages behave very differently from each other — but the headline is that the design space is two-dimensional, not four.

### 3.2. Coverage — Microeconomics

V2's [Microeconomics chapter](../README.md#3-microeconomics-participant-incentives-and-market-structure) names four milestones — **Operator Viability**, **Pledge**, **Delegator Yield**, **Deconcentration** — each broken into sub-aspects that the specification treats as separately addressable. Below, each milestone is mapped onto its sub-aspects, and each cell records what a candidate does at that level of granularity. Symbols: **●** delivers · **○** partial / indirect · **·** neutral · **▼** regresses on this sub-aspect.

CIP-0082's two distinct phases are kept separate: **stage 2** is the Margin swap (delete `minPoolCost`, introduce `minPoolRate`); **stages 3–4** are the `k`-raises (`500 → 750 → 1000`). They behave very differently against each milestone, and lumping them into a single column hides the structural difference between a fee-layer reform and a pool-count expansion.

V2's [Macroeconomics milestones](../README.md#4-macroeconomics-a-self-sustaining-and-governable-mechanism) — [Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), [Price Robustness](../README.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios), [Recalibration Pipeline](../README.md#44-the-mechanism-must-be-governable) — are deliberately omitted from this coverage view: none of the four pre-existing CIPs targets the pre-depletion-vs-post-depletion pot composition, the fee-generating population, or the recalibration cycle, and the price-robustness implications appear in each per-CIP page rather than as a cross-CIP comparison.

#### 3.2.1. Operator Viability

V2's [Operator Viability milestone](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population) splits into a **structural** sub-milestone (the production-threshold rule the protocol must enforce) and an **economic** sub-milestone (every pool above the production threshold must cover its operational cost).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Structural — enforce the production threshold](../README.md#312-structural-enforce-the-production-threshold) | · | · | · | · | · |
| [Economic — every productive pool must be profitable](../README.md#313-economic-every-productive-pool-must-be-profitable) | ○ regressive transfers up the distribution | ▼ Sub-reliable revenue **−9×** (12 410 → 1 365 ₳/yr); Saturated **+4×** | ▼ top-tail $P_{\max} = R/k$ compresses; bottom invariant | ▼ retail low-pledge pools clipped to ~7 % of V1 baseline | ○ 20 % floor protects Sub-reliable; Healthy & above clipped 10–82 % |

*None of the candidates touches the structural sub-milestone — the production threshold is set by Praos slot mechanics and active stake; no fee-layer parameter or `k`-raise moves it. The economic sub-milestone is where the candidates engage, but every engagement carries a regressive caveat documented in the per-CIP files.*

#### 3.2.2. Pledge

V2's [Pledge milestone](../README.md#32-restore-the-notion-of-pledge-among-operators) specifies a single sub-aspect: make pledge a **binding signal** in the reward calculation rather than a small smooth nudge.

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Make pledge a binding signal](../README.md#322-specification) | · | · | · | ● single hard cap | ● cap with 20 % floor |

*Only the stake-cap CIPs target this milestone. Both make pledge binding on the reward-eligible stake σ′; both share a capital-capability bias toward populations that can self-pledge — Custodial-by-extraction stake (~21 % of productive stake) cannot respond. CIP-0037 softens the bottom; CIP-0050 is sharper.*

#### 3.2.3. Delegator Yield

V2's [Delegator Yield milestone](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield) splits into three sub-aspects: **base yield competitiveness** (the floor of the delegator return), **rewarding operators who play the game** (yield differentiated by operator effort), and **diversifying the offer** (a delegator should be able to read distinct propositions across pools).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Make base yield competitive](../README.md#331-make-the-base-yield-competitive) | · | · | ▼ saturated-pool ceiling shrinks → ROS drops at the top | · | · |
| [Reward operators who play the game](../README.md#332-make-the-yield-reward-operators-who-play-the-game) | ● compresses fee-rate dispersion **38× → 13×** in the productive range | · uniform 3 % rate removes the operator-quality signal | · | ○ pledge-ratio binding price-discriminates pools | ○ pledge-curve binding price-discriminates pools |
| [Diversify the delegation offer](../README.md#333-diversify-the-delegation-offer) | · | ▼ flat 3 % floor eliminates fee-based differentiation | · | · | · |

*CIP-0023 narrows the dispersion delegators see and gives them a cleaner signal across pool sizes. CIP-0082 stage 2 collapses dispersion entirely (same rate everywhere) — which **removes** the fee-based differentiation rather than diversifying it. The stake-cap CIPs introduce a different price-discrimination axis (pledge ratio), which is partial coverage of the "reward those who play the game" sub-aspect.*

#### 3.2.4. Deconcentration

V2's [Deconcentration milestone](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) splits into the **operator side** (multi-pool entity concentration), **entity-level awareness in reward distribution** (rewards that account for which entity controls a pool, not just the pool itself), and **differentiated delegation incentives** (titan delegators vs the micro-delegation tail).

| Sub-aspect | CIP-0023 | CIP-0082 stage 2 | CIP-0082 stages 3–4 | CIP-0050 | CIP-0037 |
|---|:---:|:---:|:---:|:---:|:---:|
| [Operator side — multi-pool entity concentration](../README.md#3411-the-operator-side-multi-pool-entity-concentration) | · | · | ▼ 2020 `k:150→500` precedent: MPO fleet absorption (83 entities, 75.5 % productive stake, 449 productive pools today) | ● revenue-neutral pool-splitting at the pool level | ○ slope penalises split; 20 % floor undoes it for sub-floor splits |
| [Entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) | · | · | · | · | · |
| [Differentiated delegation incentives — titans vs micro-delegators](../README.md#343-differentiated-delegation-incentives-titans-versus-micro-delegators) | · | · | · | · | · |

*CIP-0050's revenue-neutral pool-splitting is the sharpest tool for pool-level Deconcentration in the bundle. **None of the candidates addresses entity-level Deconcentration** — the 10 entities holding 1.59 B ₳ via custodial-by-pledge sit above any pool-level cap or floor regardless of the rule. **None addresses the titans-vs-micro-delegators sub-aspect** either — it is a delegator-side incentive question, and no candidate touches the delegator side except through pool-side fee changes.*

### 3.3. The Microeconomics headline

The four pre-existing CIPs cover **Pledge** well (stake-cap CIPs deliver the binding-signal sub-aspect), partially **Operator Viability** and **Delegator Yield** (fee CIPs engage the economic and price-discrimination sub-aspects, with regressive caveats), and only the **operator side** of **Deconcentration** (CIP-0050 in particular).

Three Microeconomics sub-aspects are **entirely untouched** by every candidate:

- the structural sub-milestone of [Operator Viability](../README.md#312-structural-enforce-the-production-threshold) — production-threshold enforcement;
- [entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) inside [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations);
- [differentiated delegation incentives between titans and micro-delegators](../README.md#343-differentiated-delegation-incentives-titans-versus-micro-delegators).

None of the four CIPs was written to target these, because they were drafted before V2 surfaced them as separable problems.

### 3.4. Cross-CIP findings

Five mechanical observations stitch the per-CIP analyses into a single cross-CIP readout. Each is grounded in a specific formula property or a specific mainnet measurement; no behavioural prediction is made unless flagged as such.

**F1 — CIP-0082 stage 2 inverts operator viability for the population it claims to help.** A Sub-reliable single-pool operator, who today earns ~12 410 ₳/yr from `minPoolCost = 170`, would earn ~**1 365 ₳/yr** under `minPoolRate = 3 %` — a **9× revenue cut**. A Saturated pool gains **4×**. On the n-MPO fleet axis, the transfer compounds: a sub-reliable single-pool operator gains **+431 ₳/yr**; an 11+-pool MPO entity gains **+200 000 ₳/yr**. The reform claims to deliver Operator Viability but the mechanical effect is a regressive transfer up the operator-fleet distribution. This is the consequence of using a pricing parameter (`minPoolRate`) as a viability instrument — the conceptual critique is laid out in [the verdict on CIP-0082](#42-cip-0082).

**F2 — Both stake-cap CIPs share a capital-capability bias.** Custodial-by-extraction stake (57 entities, 2.04 B ₳ — about **21 %** of productive stake) holds custodied retail funds the operator legally cannot self-pledge. For this segment, every stake-cap reform produces a reward cut with no recourse — under CIP-0050 the σ′ collapses to zero; under CIP-0037 it's clipped to the 20 % floor. Custodial-by-pledge entities (10 entities, 1.59 B ₳) sit *above* the cap regardless and are unaffected. The reform pressures pools that are not the actual concentration concern.

**F3 — CIP-0023 is structurally dominated by CIP-0082 stage 2.** Both rewrite the same per-pool fee split with the same primitive shape — a floor on operator extraction. Stage 2 is the strictly more aggressive version. Enacting both doubles the governance surface without adding mechanism, which is the structural relation that lets [the bundle collapse to two effective candidates](#31-the-bundle-reduces-to-two-effective-candidates).

**F4 — A `k`-raise under the current weak-pledge regime regenerates the 2020 outcome.** The only previous `k` change in Cardano's history (`k: 150 → 500` in August 2020) produced today's MPO landscape: 83 attributed entities operating 449 productive pools that hold 76.7 % of productive stake. Stages 3–4 of CIP-0082 propose `k: 500 → 750 → 1000` on a 3-epoch cadence, which leaves no window to activate a stake-cap layer in between — meaning the new pool slots fire in exactly the regressive regime [`k-parameter.md`](operator-delegator/k-parameter.md) identifies.

**F5 — The bonus function `A(ν, π)` is untouched by every candidate.** The cubic suppression of the pledge bonus for sub-half-saturated pools, and the quadratic outer size penalty `ν²` that holds at every pledge ratio, survive intact. The four reforms patch *around* the function rather than *into* it — which is why [the Microeconomics headline](#33-the-microeconomics-headline) identifies sub-aspects no candidate engages.

## 4. Verdict — no-go on the existing bundle

**Bundle no-go on V2.** None of the candidates closes the V2 milestone gap, and the objections are structural — not parameters to tune. Three patterns recur across the five rows below:

- **The bonus function `A(ν, π)` is the load-bearing piece, and no CIP touches it.** The stake-cap CIPs (CIP-0050 / CIP-0037) add a third layer of σ′ clipping on top of the existing `a₀` and `k` levers, but `A` carries the pledge pathology: a permanent quadratic `ν²` size penalty, a non-monotonicity in π for sub-half-saturated pools (small operators are explicitly incentivised to *under-pledge* — at ν ≈ 0.03 a 2 M operator earns **8.7×** more bonus by pledging 51 % than 100 %), and a cubic `ν³` collapse at full self-pledge (a saturated operator earns **37 595×** more bonus than a 2 M operator at maximum commitment). Today's mainnet equilibrium — **POL.O2.F1: 78 % of staked ADA in pools with π < 1 %**; **POL.O5.F3: 42 of 48 saturation-scale MPOs forfeit the bonus** — is exactly the equilibrium a formula with near-zero pledge gradient in the operating region predicts. The σ′ clip changes *who can earn the V1 reward*; it does not repair what `A` does to the pledge signal. A genuine V2 reform must redesign `A` — smoother operator onset at low ν, no design preference for fully-private pools (π = 1), explicit reward for the balanced-commitment regime (π ≈ 0.5).
- **Pricing-as-viability conflation** rules out the fee-layer reform (CIP-0082 stage 2, with CIP-0023 inheriting). A margin/rate floor is a commission constraint, not a viability backstop — pricing belongs on the operator's competitive lever, viability on the reward-distribution layer (pre-split).
- **`k`-raise on a 3-epoch cadence** (CIP-0082 stages 3–4) leaves no window for a stake-cap layer to activate first, so new pool slots fire in the same regressive regime that produced today's MPO concentration in August 2020.

Five rows below because CIP-0082's stage 2 and stages 3–4 are evaluated separately — they carry different objections. The synoptic table maps each candidate to its primary objection; the sub-sections that follow argue each verdict in turn, each pointing to the per-CIP file with the full quantitative argument.

| Candidate | Verdict | Why |
|---|:---:|---|
| [**CIP-0050**](pools-distribution/cip-0050.md) | ▼ No-go | Patches around `A(ν, π)` — pledge pathology unfixed; capital-capability bias compounds |
| [**CIP-0037**](pools-distribution/cip-0037.md) | ▼ No-go | Same as CIP-0050 — `A` still unmodified; 20 % floor softens the σ′ clip but not the bottleneck |
| [**CIP-0023**](operator-delegator/cip-0023.md) | ⊂ Moot | Subsumed by CIP-0082 stage 2 — same pricing/viability conflation, less mechanism |
| [**CIP-0082 stage 2**](operator-delegator/cip-0082.md) | ▼ No-go | Conflates **pricing** with **viability** — `minPoolRate` bolts viability onto commission (Sub-reliable **−9×**, **+200 k ₳/yr** to MPO entities) |
| [**CIP-0082 stages 3–4**](operator-delegator/k-parameter.md) | ▼ No-go | `k`-raise on a 3-epoch cadence regenerates the 2020 MPO-fleet absorption pattern |

*Each row's Why links to the per-CIP file that backs the claim. The cross-CIP findings these verdicts cite are listed in [Cross-CIP findings](#34-cross-cip-findings) above.*

### 4.1. Stake-cap CIPs (CIP-0050 / CIP-0037)

Both CIPs target the right intent — binding pledge on σ′ to deliver the [Pledge milestone](../README.md#32-restore-the-notion-of-pledge-among-operators) — but they patch *around* the load-bearing piece of the pledge incentive, not into it.

**The protocol already has a pledge lever; the deeper bottleneck is the bonus function `A(ν, π)` itself.** V1 exposes `a₀` (currently `0.3` on mainnet) as the weight of the pledge bonus inside the SL-D1 reward envelope. As the [stake-cap layer synthesis](pools-distribution/README.md) walks through, raising `a₀` rebalances the formula without making pledge "matter more" — every low-pledge pool earns less before the bonus can recover. CIP-0050 and CIP-0037 add a third lever (clipping σ′ before the formula runs) on top of the existing `a₀` and `k`, but they accept `A(ν, π)` as given. That function carries three structural pathologies the diagnostic surfaces:

- a permanent quadratic `ν²` size penalty applies at *every* pledge ratio — small pools are crushed regardless of how committed the operator is;
- a non-monotonicity in π for sub-half-saturated pools — at ν ≈ 0.03 (Bob's 2 M pool), the optimum pledge ratio is π ≈ 51 %, not π = 1; full self-pledge gives **8.7×** *less* bonus than withholding half the potential pledge. The formula explicitly incentivises small operators to *under-commit*;
- a cubic `ν³` collapse at full self-pledge (π = 1) — at maximum commitment, a saturated operator (Alice) earns **37 595×** more bonus than a 2 M operator (Bob), because the size factor cubes when the pledge factor saturates.

The pledge problem persists despite the capping. The σ′ clip changes *who can earn the V1 reward*, but the relative bonus disparity across operator sizes, the under-commitment incentive at low ν, and the cubic collapse at full pledge all carry through unchanged. Patching around `A` does not repair the pledge signal at its source.

**A genuine V2 stake-cap reform must redesign `A`** with three properties no CIP currently in scope delivers:

- a **smoother operator onset at low ν** — no cubic crush of small pools at the moment they are trying to grow;
- a design that **does not privilege fully-private pools (π = 1)**. The current `A` happens to crush small private pools via `ν³`, but the gradient still pushes large operators toward 100 % self-pledge — that is not the V2 target;
- an explicit reward for the **balanced-commitment regime (e.g. π ≈ 0.5)** — the configuration where pledge serves as a credible signal *and* the pool remains open to delegation.

A second, compounding objection sits on top of the `A` argument: the [capital-capability bias finding](#34-cross-cip-findings) — Custodial-by-extraction stake (57 entities, 2.04 B ₳, ~21 % of productive stake) cannot self-pledge by construction, while Custodial-by-pledge entities (10 entities, 1.59 B ₳) sit *above* any cap regardless of the rule. Even if `A` were repaired, the σ′ primitive would still pressure the wrong segment.

Per-CIP detail: [`cip-0050.md`](pools-distribution/cip-0050.md), [`cip-0037.md`](pools-distribution/cip-0037.md). The full `A`-anatomy walkthrough — heatmaps, scenarios, and the cubic-crush analysis — is in the [stake-cap layer synthesis](pools-distribution/README.md).

### 4.2. CIP-0082

The four-stage package fails on two of its stages, but the underlying intuition on stage 2 is *half-right* and worth naming explicitly — because the principled separation it gets wrong is what the new proposal needs to get right.

**The half that is right: removing `minPoolCost` is the correct move.** The flat-ADA floor is a regressive instrument on both sides of the split. On the delegator side, it pins net ROS at zero for every pool whose epochal reward does not reach the floor (today's Dormant and Sub-block tiers — 100 % fee-consumed). On the operator side, it pins sub-reliable operator income at exactly the floor regardless of stake. CIP-0023 and CIP-0082 both correctly identify `minPoolCost` as a problem.

**The half that is wrong: replacing `minPoolCost` with `minPoolRate = 3 %` bolts a viability function onto a pricing tool.** A rate floor is not a relief mechanism — it is a *commission constraint*. By forcing every operator into a 3 % minimum margin, stage 2 conflates two functions that V2 needs to keep separate:

- **Pricing** (`minPoolCost`, `poolRate`, `minPoolRate`) — the operator's competitive lever. Pricing is what delegators read to distinguish between operators; it should remain a free-market signal that operators set as they choose, including down to zero in markets where the operator is willing to compete on cost alone.
- **Viability** — the structural minimum a productive operator must clear to cover operational cost. This is a backstop, not a price; it must respond to *who is producing blocks*, not *who has registered a fee schedule*.

The principled separation is laid out in [`operator-delegator/README.md` Executive summary](operator-delegator/README.md#executive-summary): pricing tools should remain fully flexible competitive levers; the **viability floor belongs on the reward-distribution layer (pre-split)**, not on the fee-split layer (post-split). Stake-cap instruments ([`pools-distribution/`](pools-distribution/README.md)) act on the right layer — they reshape the reward-eligible stake $\sigma'$ before the formula applies, leaving operator pricing untouched.

The mechanical consequence of mixing pricing and viability is [the viability-inversion finding](#34-cross-cip-findings): Sub-reliable single-pool operators lose **9× revenue** under `minPoolRate = 3 %` versus today's `minPoolCost = 170 ₳`; an 11+-pool MPO entity gains **+200 000 ₳/yr** — because a proportional rate floor multiplies pool reward, and pool reward grows with σ. The reform claims Operator Viability; the mechanical effect is a regressive transfer up the operator-fleet distribution, *because the wrong layer was used*. Detailed mechanics in [`cip-0082.md`](operator-delegator/cip-0082.md).

**Stages 3–4 (`k`: 500 → 750 → 1000 on a 3-epoch cadence)** reproduce the August 2020 outcome under the current weak-pledge regime. The only previous `k` change in Cardano's history (`k: 150 → 500`) produced today's MPO landscape: 83 attributed entities operating 449 productive pools that hold 76.7 % of productive stake. The proposed cadence leaves no window to activate a stake-cap layer in between, so the new pool slots fire in exactly the regressive regime [the 2020-pattern finding](#34-cross-cip-findings) describes. The mechanics are in [`k-parameter.md`](operator-delegator/k-parameter.md).

Stage 1 (floor halving, already shipped) is the only stage that survives this evaluation — and it is also the only stage whose mechanical effect is bounded.

### 4.3. CIP-0023

CIP-0023 introduces `minPoolMargin` — mechanically identical to CIP-0082 stage 2's `minPoolRate`, and credited as the conceptual seed by CIP-0082's own author. It inherits both halves of stage 2's intuition: the *correct* half (the flat-fee `minPoolCost` is a regressive instrument that needs relief at the small-pool end) and the *incorrect* half (the relief is engineered as a margin-floor — a pricing parameter — rather than as a viability primitive on the reward-distribution layer).

The principled critique in [the verdict on CIP-0082](#42-cip-0082) applies in full. CIP-0023's own per-pool data documents the same regressive transfer at smaller calibration: pool-axis amplification of **52×** (Δ at Saturated 357.5 ₳/ep vs Δ at Sub-reliable 6.8 ₳/ep) and operator-fleet amplification of **502×** under the standalone variant (216 298 ₳/yr to an 11+-pool MPO entity vs 431 ₳/yr to a sub-reliable single-pool operator). The full readout is in [`cip-0023.md`](operator-delegator/cip-0023.md), and [the subsumption finding](#34-cross-cip-findings) summarises the structural relation to stage 2.

No independent verdict is needed: if Stage 2 is a no-go, CIP-0023 is too — same conceptual error (pricing-as-viability), less mechanism.

### 4.4. Sub-aspects untouched by the bundle

Even setting the regressions aside, the bundle is **structurally incomplete against V2** — see [the Microeconomics headline](#33-the-microeconomics-headline). Three Microeconomics sub-aspects are entirely uncovered:

- the [structural sub-milestone of Operator Viability](../README.md#312-structural-enforce-the-production-threshold) — production-threshold enforcement;
- [entity-level awareness in reward distribution](../README.md#342-entity-level-awareness-in-reward-distribution) — the multi-pool entity lens the diagnostic surfaced is not present in any candidate;
- [differentiated delegation incentives between titans and micro-delegators](../README.md#343-differentiated-delegation-incentives-titans-versus-micro-delegators) — the delegator side is untouched except as a side-effect of pool-side fee changes.

The four pre-existing CIPs were drafted before V2 surfaced these as separable problems, so this gap is not a failure of the candidates — it is a constraint on what the bundle can deliver at all.

### 4.5. Cumulative read

The four pre-existing CIPs each respond to a partial framing of the problem. Treated as a package, **they do not close the V2 milestone set**, and the pieces that do engage individual milestones do so through mechanisms that regress on milestones they do not target. The bundle is not a viable path to V2 as it stands.

This is not a rejection of the underlying intents. CIP-0050 and CIP-0037 capture a real Pledge milestone goal; CIP-0023 and CIP-0082 stage 2 correctly identify `minPoolCost` as a regressive flat fee that needs to go. What the evaluation rejects is the **mechanical realisation** each picks. The pattern across the bundle is the same: every candidate puts its instrument **on the wrong layer**.

- **Fee-layer CIPs (CIP-0023 / CIP-0082 stage 2)** address viability by tightening pricing parameters (`minPoolMargin`, `minPoolRate`). The viability function belongs on the reward-distribution layer (pre-split); pricing must remain free for operators to compete in an open market. Conflating the two produces the regressive transfer documented in [the verdict on CIP-0082](#42-cip-0082).
- **Stake-cap CIPs (CIP-0050 / CIP-0037)** act on the right layer (pre-split, σ′) but with a primitive that ignores the capital structure of the segments they target — see [the verdict on the stake-cap CIPs](#41-stake-cap-cips-cip-0050-cip-0037).
- **Pool-count expansion (CIP-0082 stages 3–4)** addresses Deconcentration by raising `k` without a stake-cap precondition, so the new pool slots fire in the same MPO-fleet absorption regime that produced today's concentration — see [the verdict on CIP-0082](#42-cip-0082).

The design space therefore needs a fresh proposal that respects three separations: pricing free-market levers stay flexible; the viability backstop lives on the reward-distribution layer; and pool-count expansion is gated on a stake-cap precondition. See [Toward a new proposal](#5-toward-a-new-proposal).

## 5. Toward a new proposal

The structural caveats surfaced by [the Verdict above](#4-verdict-no-go-on-the-existing-bundle) — combined with the V2 milestones the existing bundle does not close ([Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), the entity-level gap inside [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations), and the untouched bonus function `A(ν, π)`) — motivate a new proposal currently in preparation.

> *Draft in preparation. This section will be expanded with a summary and linked to the dedicated proposal page once the draft is ready for review.*

## 6. References

- **V2 specification:** [`../README.md`](../README.md) — Microeconomics & Macroeconomics milestones, evaluation framework.
- **Mainnet diagnostic:** [`../diagnostic/README.md`](../diagnostic/README.md).
- **Mechanism-intent narrative:** [`../the-intended-game/README.md`](../the-intended-game/README.md).
- **Per-layer indexes:** [`pools-distribution/README.md`](pools-distribution/README.md), [`operator-delegator/README.md`](operator-delegator/README.md).
- **Per-CIP evaluations:** [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md), [`operator-delegator/k-parameter.md`](operator-delegator/k-parameter.md).
- **Canonical CIP sources:** [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs) on GitHub; per-CIP page at [cips.cardano.org](https://cips.cardano.org/).

> **Status:** Active 2026/04/22. Working folder evaluating the live CIPs and parameter-level proposals against the V2 specification.
