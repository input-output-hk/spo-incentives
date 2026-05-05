# Solution Evaluation — Do the Existing CIPs Solve What V2 Names?

The Cardano network has been observed in detail through a multi-stage [mainnet diagnostic](../diagnostic/README.md) — covering the Treasury & Pool-Pots layer, the Pools-Distribution layer, the Operator-Delegator split, and the Staking Census. The diagnostic surfaced a small set of **structural problems** in the current reward system, each grounded in mainnet evidence rather than theory:

- **A large share of productive operators sits below the viability line** — 73 % of productive pools sit below the ~3 M ADA viability line; no single-pool retail operator earns a competitive wage at current ADA prices, irrespective of how reliably they produce blocks.
- **Pledge no longer functions as a binding signal of operator commitment** — 78 % of staked ADA sits in pools with pledge ratio under 1 %, and 42 of 48 saturation-scale multi-pool operators forfeit the pledge bonus. The formula prices pledge as a small smooth nudge (pledge yield 0.68 %/yr vs ~2.3 %/yr from passive delegation) that the operator population has rationally chosen to ignore.
- **Delegator yield is barely differentiated by pool quality** — today's delegator fee-rate dispersion across the productive range is **38×** (27.3 % at Sub-reliable pools vs 0.71 % at saturation); the dispersion delegators see is dominated by fee structure, not by performance, and delegation flow does not track yield.
- **Stake concentration bypasses the anti-Sybil mechanics at the entity level** — 83 attributed entities operating 449 productive pools today control 76.7 % of productive stake; multi-pool operators capture a majority, the very pattern the formula's pledge term was meant to discourage.

The [V2 specification](../README.md) turns each of those problems into a **named milestone** — a concrete outcome the next generation of the reward system must deliver. Four are foreground microeconomics — [Operator Viability](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [Pledge](../README.md#32-restore-the-notion-of-pledge-among-operators), [Delegator Yield](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield), [Deconcentration](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations) — and four are macroeconomics or transversal — [Pot Survival](../README.md#41-the-staking-pot-must-survive-reserve-depletion), [Fee Policy](../README.md#42-the-fee-generating-population-must-expand), [Price Robustness](../README.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios), and the [Recalibration Pipeline](../README.md#44-the-mechanism-must-be-governable). The dependency chain is strict: Operator Viability → Pledge → Delegator Yield → Deconcentration → Pot Survival → Fee Policy.

**But the CIP backlog already contained proposals before this diagnostic was performed.** [CIP-0023](operator-delegator/cip-0023.md) (2021), [CIP-0037](pools-distribution/cip-0037.md) (2021), [CIP-0050](pools-distribution/cip-0050.md) (2021), and [CIP-0082](operator-delegator/cip-0082.md) (2024) were each drafted with their own framing, their own evidence, and their own design choices. Most are still on the table for governance ratification today. None of them were written with the V2 specification in hand, because V2 did not exist yet.

*The question this folder asks: do those pre-existing proposals — written before the diagnostic — actually deliver the milestones V2 names? Partially? Not at all? Or do some of them, by side-effect, regress on a milestone they don't claim to address?*

# Table of Contents

- [1. How this evaluation works](#1-how-this-evaluation-works)
- [2. The candidates by layer](#2-the-candidates-by-layer)
  - [2.1. Stake-cap layer — CIP-0050 / CIP-0037](#21-stake-cap-layer-cip-0050-cip-0037)
  - [2.2. Fee layer — CIP-0023 / CIP-0082](#22-fee-layer-cip-0023-cip-0082)
- [3. Conclusion](#3-conclusion)
- [4. Recommendations on adjustments to the current mechanism](#4-recommendations-on-adjustments-to-the-current-mechanism)
- [5. References](#5-references)

# 1. How this evaluation works

Each candidate is taken on its own terms. The method is the same for every CIP:

- **Read what the proposal itself says it does.** Its rationale, its parameters, its claimed effects — straight from the canonical CIP source.
- **Map it against the V2 milestones.** Which milestone is the primary intent? Which is touched as a side-effect? Which is left untouched?
- **Quantify the mechanical effect on mainnet.** Using the same nine-tier pool-size taxonomy and n-MPO operator-fleet brackets the diagnostic uses, every per-CIP file produces a row-by-row readout of who gains, who loses, and by how much, at current mainnet parameters.
- **Surface verdicts as Delivers / Regresses / Blind spot.** Every quantified finding gets one of three tags, tied to a specific formula property or a specific mainnet measurement. *Delivers* — the proposal achieves what it claims. *Regresses* — the proposal worsens an unrelated milestone by side-effect. *Blind spot* — the proposal depends on a behavioural response the diagnostic does not strongly support.

# 2. The candidates by layer

The reward pipeline has **two independent layers**. The four pre-existing CIPs distribute across them. Each subsection below lists the candidates, summarises what they share, and carries the verdict; the structural arguments live in the dedicated layer-synthesis pages.

## 2.1. Stake-cap layer — CIP-0050 / CIP-0037

The stake-cap layer modifies the reward-eligible pool stake $\sigma'$ used inside the SL-D1 reward formula — *upstream* of the operator/member split. → [`pools-distribution/`](pools-distribution/README.md)

<div class="cand-grid" markdown="1">
<div class="cand-card" markdown="1">
<a class="cand-card-title" href="stake-cap.html">CIP-0050 — Pledge Leverage-Based Staking Rewards</a>
<div class="cand-card-body" markdown="1">Pledge-leverage cap `L` — a one-scalar hard cap proportional to pledge.</div>
<div class="cand-card-source"><span class="cand-card-source-label">Source</span> <a href="https://cips.cardano.org/cip/CIP-0050">CIP-0050</a> · PR <a href="https://github.com/cardano-foundation/CIPs/pull/242">#242</a>, <a href="https://github.com/cardano-foundation/CIPs/pull/1042">#1042</a></div>
</div>
<div class="cand-card" markdown="1">
<a class="cand-card-title" href="stake-cap.html">CIP-0037 — Dynamic Saturation Based on Pledge</a>
<div class="cand-card-body" markdown="1">Pledge-linked saturation curve — three anchors: a 20 % floor, a linear slope through the mid-pledge range, and the V1 cap as ceiling.</div>
<div class="cand-card-source"><span class="cand-card-source-label">Source</span> <a href="https://cips.cardano.org/cip/CIP-0037">CIP-0037</a> · PR <a href="https://github.com/cardano-foundation/CIPs/pull/163">#163</a></div>
</div>
</div>

Both CIPs target a real broken signal: pledge no longer functions as a binding signal of operator commitment. **78 % of staked ADA sits in pools with pledge ratio under 1 %**; **42 of the 48 largest multi-pool operators forfeit the pledge bonus**; pledged ADA yields 0.68 %/yr while passive delegation yields ~2.3 %/yr. Both respond with a σ′ clip that makes pledge bind the reward-eligible stake.

**Verdict on both: ▼ no-go**, for two stacked reasons.

The load-bearing piece is the bonus function `A(ν, π)` inside the SL-D1 reward envelope, and neither CIP touches it. `A` produces today's equilibrium: it carries a quadratic `ν²` size penalty at every pledge ratio, a non-monotonicity in π that incentivises small operators to *under-commit* (a 2 M operator earns 8.7× more bonus by pledging 51 % than 100 %), and a cubic `ν³` collapse at full self-pledge. The σ′ clip changes *who can earn the V1 reward*; it does not repair what `A` does to the pledge signal.

A second objection compounds: capital-capability bias. Custodial-by-extraction stake (~21 % of productive stake) legally cannot self-pledge — the cap collapses their reward with no recourse. The 10 largest Custodial-by-pledge entities (1.59 B ADA) sit *above* any cap regardless. The reform pressures the wrong segment.

→ Full argument, the three properties a genuine V2 stake-cap reform must deliver, and the Appendix-A walkthrough of `A`: [stake-cap layer synthesis](pools-distribution/README.md). Per-CIP detail: [`cip-0050.md`](pools-distribution/cip-0050.md), [`cip-0037.md`](pools-distribution/cip-0037.md).

## 2.2. Fee layer — CIP-0023 / CIP-0082

The fee layer modifies the operator/member split *after* the per-pool reward has been computed. The reward envelope itself is untouched. → [`operator-delegator/`](operator-delegator/README.md)

<div class="cand-grid" markdown="1">
<div class="cand-card" markdown="1">
<a class="cand-card-title" href="fee-layer.html">CIP-0023 — Fair Min Fees</a>
<div class="cand-card-body" markdown="1">`minPoolMargin` floor — a margin floor on the operator/member split.</div>
<div class="cand-card-source"><span class="cand-card-source-label">Source</span> <a href="https://cips.cardano.org/cip/CIP-0023">CIP-0023</a> · PR <a href="https://github.com/cardano-foundation/CIPs/pull/66">#66</a></div>
</div>
<div class="cand-card" markdown="1">
<a class="cand-card-title" href="fee-layer.html">CIP-0082 — Improved Rewards Scheme Parameters</a>
<div class="cand-card-body" markdown="1">Four-stage package: stage 1 floor halving (shipped at epoch 445), stage 2 margin swap (`minPoolCost` → `minPoolRate = 3 %`, hard fork), stages 3–4 `k`-raises (500 → 750 → 1000). The standalone analysis of stages 3–4 lives in [cip-0082 §B.3](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive).</div>
<div class="cand-card-source"><span class="cand-card-source-label">Source</span> <a href="https://cips.cardano.org/cip/CIP-0082">CIP-0082</a></div>
</div>
</div>

Both CIPs target the priority-1 problem the diagnostic identifies: **small-operator viability**. **73 % of productive pools sit below the ~3 M ADA viability line**; no single-pool retail operator earns a competitive wage at current prices (median 12 410 ADA/yr covers infrastructure but not 5–15 hrs/month of skilled labour).

**Verdict on both: ▼ no-go**, for one structural reason.

The two CIPs correctly identify the target but mechanically address ROS *attractiveness*, not profitability *structure*. Fee-layer tightening makes small pools more ROS-attractive to delegators; it does not raise what a small-pool operator earns at constant size. The reforms therefore depend on delegation actually migrating from large pools to small ones — and the diagnostic does not support that migration: observed delegation flow tracks brand, wallet integration, and visibility, not yield.

If the migration does not happen, the reforms invert their intent: sub-reliable operator revenue **−9×** under the Margin swap (12 410 → 1 365 ADA/yr); the transfer compounds with fleet size, **+200 K ADA/yr per 11+ pool MPO entity vs −11 K ADA/yr per sub-reliable single-pool operator** — exactly the regressive direction `minPoolRate` was meant to correct.

The principled separation: `minPoolCost` and `minPoolRate` are **pricing tools** that should stay flexible competitive levers; the **viability floor** is a different function and belongs on the reward-distribution layer (pre-split), not bolted into the fee-split. Stake-cap instruments act on the correct layer.

→ Full argument, the principled separation, and the standalone k-lever deep dive for stages 3–4: [fee-layer synthesis](operator-delegator/README.md). Per-CIP detail: [`cip-0023.md`](operator-delegator/cip-0023.md), [`cip-0082.md`](operator-delegator/cip-0082.md).

# 3. Conclusion

None of the candidates closes the V2 milestone gap, and the objections are structural — not parameters to tune. The structural reasons by layer are in [§2.1](#21-stake-cap-layer-cip-0050-cip-0037) and [§2.2](#22-fee-layer-cip-0023-cip-0082); the synoptic verdict:

| Candidate | Verdict | Why |
|---|:---:|---|
| [**CIP-0050**](pools-distribution/cip-0050.md) | ▼ No-go | Patches around `A(ν, π)` — pledge pathology unfixed; capital-capability bias compounds |
| [**CIP-0037**](pools-distribution/cip-0037.md) | ▼ No-go | Same as CIP-0050 — `A` still unmodified; 20 % floor softens the σ′ clip but not the bottleneck |
| [**CIP-0023**](operator-delegator/cip-0023.md) | ⊂ Moot | Subsumed by CIP-0082 stage 2 — same pricing/viability conflation, less mechanism |
| [**CIP-0082 stage 2**](operator-delegator/cip-0082.md) | ▼ No-go | Conflates **pricing** with **viability** — `minPoolRate` bolts viability onto commission (Sub-reliable **−9×**, **+200 k ₳/yr** to MPO entities) |
| [**CIP-0082 stages 3–4**](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive) | ▼ No-go | `k`-raise on a 3-epoch cadence regenerates the 2020 MPO-fleet absorption pattern |

This is not a rejection of the underlying intents. CIP-0050 and CIP-0037 capture a real Pledge milestone goal; CIP-0023 and CIP-0082 stage 2 correctly identify `minPoolCost` as a regressive flat fee that needs to go. What the evaluation rejects is the **mechanical realisation** each picks. The pattern across the bundle is the same: every candidate puts its instrument **on the wrong layer**.

- **Fee-layer CIPs (CIP-0023 / CIP-0082 stage 2)** address viability by tightening pricing parameters (`minPoolMargin`, `minPoolRate`). The viability function belongs on the reward-distribution layer (pre-split); pricing must remain free for operators to compete in an open market. Conflating the two produces the regressive transfer documented in [§2.2](#22-fee-layer-cip-0023-cip-0082).
- **Stake-cap CIPs (CIP-0050 / CIP-0037)** act on the right layer (pre-split, σ′) but with a primitive that ignores the capital structure of the segments they target — see [§2.1](#21-stake-cap-layer-cip-0050-cip-0037).
- **Pool-count expansion (CIP-0082 stages 3–4)** addresses Deconcentration by raising `k` without a stake-cap precondition, so the new pool slots fire in the same MPO-fleet absorption regime that produced today's concentration — see [cip-0082 §B.3](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive).

The design space therefore points toward parameter-level adjustments that respect three separations: pricing free-market levers stay flexible; the viability backstop lives on the reward-distribution layer; and pool-count expansion is gated on a stake-cap precondition.

# 4. Recommendations on adjustments to the current mechanism

A set of parameter-level recommendations is in preparation by IO Research, targeting end of 2026, respecting the three separations isolated in [§3 Conclusion](#3-conclusion).

> *In preparation. This section will be expanded with a summary and linked to the dedicated proposal page once the recommendations are ready for review.*

# 5. References

- **V2 specification:** [`../README.md`](../README.md) — Microeconomics & Macroeconomics milestones, evaluation framework.
- **Mainnet diagnostic:** [`../diagnostic/README.md`](../diagnostic/README.md).
- **Mechanism-intent narrative:** [`../the-intended-game/README.md`](../the-intended-game/README.md).
- **Per-layer indexes:** [`pools-distribution/README.md`](pools-distribution/README.md), [`operator-delegator/README.md`](operator-delegator/README.md).
- **Per-CIP evaluations:** [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md) (with §B.3 carrying the standalone k-lever deep dive that supports the verdict on stages 3–4).
- **Canonical CIP sources:** [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs) on GitHub; per-CIP page at [cips.cardano.org](https://cips.cardano.org/).

> **Status:** Active 2026/04/22. Working folder evaluating the live CIPs and parameter-level proposals against the V2 specification.
