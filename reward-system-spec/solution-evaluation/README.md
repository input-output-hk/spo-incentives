# The four pre-existing CIPs against the 9 induced problems

The Cardano network has been observed in detail through a multi-stage [mainnet diagnostic](../diagnostic/README.md) — covering the Treasury & Pool-Pots layer, the Pools-Distribution layer, the Operator-Delegator split, and the Staking Census.

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
<div class="cps-stage cps-stage-current" title="You are here — CIPs Evaluation">
<span class="cps-stage-num">Stage 05</span>
<span class="cps-stage-label">CIPs (Evaluation)</span>
<span class="cps-stage-meta">IntersectMBO governance &middot; this page</span>
</div>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-future" href="build-scoping.html" title="Build Estimation / Scoping — sizing the build for the V2 stage-1 reform">
<span class="cps-stage-num">Stage 06</span>
<span class="cps-stage-label">Build Estimation / Scoping</span>
<span class="cps-stage-meta">Build sizing</span>
</a>
</div>

<nav class="cps-sublocation" aria-label="Within the CIPs evaluation">
<span class="cps-sublocation-current">Existing CIPs</span> <span class="cps-sublocation-sep" aria-hidden="true">&middot;</span> overview across the <a href="stake-cap.html">Stake-Cap</a> and <a href="fee-layer.html">Fee</a> layers
</nav>

The diagnostic surfaces **9 induced problems** — five micro (μ01–μ05) and four macro (M01–M04) — each grounded in mainnet evidence rather than theory. Four of them are central to the candidate CIPs evaluated in this folder:

- **[μ02 — Operator viability across the productive population](../generated-website/problem-statements.html#problem-1-3-3-1).** 73 % of productive pools sit below the ~3 M ADA viability line; no single-pool retail operator earns a competitive wage at current ADA prices, irrespective of how reliably they produce blocks.
- **[μ01 — The pledge paradox](../generated-website/problem-statements.html#problem-1-2-3).** 78 % of staked ADA sits in pools with pledge ratio under 1 %, and 42 of 48 saturation-scale multi-pool operators forgo the pledge bonus. The formula prices pledge as a small smooth nudge (pledge yield 0.68 %/yr vs ~2.3 %/yr from passive delegation) that the operator population has rationally chosen to ignore.
- **[μ03 — Competitive delegator yield](../generated-website/problem-statements.html#problem-1-3-3-2).** Today's delegator fee-rate dispersion across the productive range is **38×** (27.3 % at Sub-reliable pools vs 0.71 % at saturation); the dispersion delegators see is dominated by fee structure, not by performance, and delegation flow does not track yield.
- **[μ04 — Entity-level concentration](../generated-website/problem-statements.html#problem-2-1-3-1).** 83 attributed entities operating 449 productive pools today control 76.7 % of productive stake; multi-pool operators capture a majority, the very pattern the formula's pledge term was meant to discourage.

The [Solution Design](../README.md) carries this work forward, prioritised *root-causes-before-scale-up* — μ01 / μ02 bundled in Milestone 1 ahead of yield diversification (M2), Pool Alliance (M3), and non-participant scale-up (M4), with a research axis on concentration covering the supply-side (μ04) and demand-side (μ05) questions.

**But the CIP backlog already contained proposals before this diagnostic was performed.** [CIP-0023](operator-delegator/cip-0023.md) (2021), [CIP-0037](pools-distribution/cip-0037.md) (2021), [CIP-0050](pools-distribution/cip-0050.md) (2021), and [CIP-0082](operator-delegator/cip-0082.md) (2024) were each drafted with their own framing, their own evidence, and their own design choices. Each was designed against a partial reading of the problem space. Most are still on the table for governance ratification today. None was written with the Solution Design in hand, because the Solution Design did not exist yet.

*The question this folder asks: each pre-existing proposal names a real pathology and points in a credible direction — so where does each fit once a root-level solution is on the table? Which milestone does it advance directly, which does it reach at the symptom rather than the source, and how is it best sequenced alongside a fix that works at the cause?*

> **Headline finding — the problems are validated, and a root-level solution now exists.** Every one of the four CIPs identifies a genuine pathology the mainnet diagnostic independently confirms: the broken pledge signal (CIP-0050, CIP-0037) and small-operator viability (CIP-0023, CIP-0082). The proposals are directionally right, and the momentum behind them is well-placed. What the diagnostic adds is *depth*: all four act outside the central reward-distribution layer where μ01 and μ02 are actually produced, so each reaches the problem at the gate rather than at its source. The research has now isolated that source — the bonus function `A(ν, π)` and the envelope weights around it — and a **four-move root-level package** repairs it directly (see [§4 Recommendations](#4-recommendations-on-adjustments-to-the-current-mechanism), carried into [Solution Design Milestone 1 — Repair pledge, sustain the small SPO base](../README.md#21-milestone-1-repair-pledge-sustain-the-small-spo-base)). **Recommendation for every CIP in the bundle: deploy the root-level fix first, for efficient and optimal progress, then assess whether each proposal is still needed as a secondary step.** The governance momentum these proposals carry is real — this evaluation channels it toward the root cause rather than spending it at the surface.

# Table of Contents

- [1. How this evaluation works](#1-how-this-evaluation-works)
- [2. The candidates by layer](#2-the-candidates-by-layer)
  - [2.1. Stake-cap layer — CIP-0050 / CIP-0037](#21-stake-cap-layer-cip-0050-cip-0037)
  - [2.2. Fee layer — CIP-0023 / CIP-0082](#22-fee-layer-cip-0023-cip-0082)
- [3. Conclusion](#3-conclusion)
  - [3.1. Direct engagement with the Cardano Incentives Working Group's coordinated proposal set](#31-direct-engagement-with-the-cardano-incentives-working-groups-coordinated-proposal-set)
- [4. Recommendations on adjustments to the current mechanism](#4-recommendations-on-adjustments-to-the-current-mechanism)
  - [4.1. Why gradual, not radical](#41-why-gradual-not-radical)
  - [4.2. Four moves on the reward-distribution layer](#42-four-moves-on-the-reward-distribution-layer)
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

**Assessment on both — problem validated · root-level solution researched · recommendation: repair the pledge signal at its source first, then assess whether a σ′ cap is still needed as a secondary step.**

The exciting part comes first: the diagnostic has traced this broken signal to its source — the bonus function `A(ν, π)` inside the SL-D1 reward envelope — and a **root-level fix repairs `A` directly**. A redesigned `A` gives a smoother operator onset at low ν, drops the design preference for fully-private pools, and explicitly rewards balanced commitment; reducing `λ_size` then lets the commitment axis carry more of the signal; and the same move **reactivates the `λ_pledge` budget that already returns to reserve unused** (POL.O1.F3: 95.6 %) — *not new ADA, unused ADA already inside the formula's envelope*. This is the gradual, source-level path the [stake-cap layer synthesis](pools-distribution/README.md) develops and [Solution Design Milestone 1](../README.md#21-milestone-1-repair-pledge-sustain-the-small-spo-base) carries forward.

Read against that source-level fix, CIP-0050 and CIP-0037 act one step downstream. Both add a σ′ cap *before* the formula runs but leave `A` — the mechanism that produced today's non-pledging equilibrium — untouched: the clip changes *who can earn the V1 reward*; it does not repair what `A` does to the pledge signal. And applied to today's regime, where almost no one pledges at scale (median π = 0.07 %, 78 % of stake below 1 %, 42 of 48 saturation MPOs forfeit), a hard cap binds on **every** operator segment at once — small / single-pool retail, multi-pool entities, and custodial-by-extraction (~21 % of productive stake, which legally cannot self-pledge custodied retail funds). That is why the cap is most constructive *after* the pledge signal has been repaired and the population can actually comply — exactly the sequencing [μ02 — Guarantee operator viability](../generated-website/problem-statements.html#problem-1-3-3-1) and [Solution Design Milestone 1](../README.md#21-milestone-1-repair-pledge-sustain-the-small-spo-base) call for.

→ Full argument, the four-move gradual path, and the Appendix-A walkthrough of `A`: [stake-cap layer synthesis](pools-distribution/README.md). Per-CIP detail: [`cip-0050.md`](pools-distribution/cip-0050.md), [`cip-0037.md`](pools-distribution/cip-0037.md).

> *Counter-argument engaged.* This evaluation responds directly to the [CIP-50 Rebirth proposal](https://incentives.solutions/cip-50-rebirth/), which advocates the cap (L = 10–100) paired with a `k`-raise to 2 000 as a Sybil-resistance and decentralisation instrument. The mechanical claims their case rests on are correct (zero pledge → zero reward; pool-splitting revenue-neutral); the diagnostic disagrees on what those claims accomplish in today's regime. The detailed engagement lives in [`cip-0050.md`](pools-distribution/cip-0050.md): the Sybil-framing context (§2), the RSS-simulation reality-check (§4), the k-synergy framing (§A.10), and the three findings cards (Appendix B).

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

**Assessment on both — problem validated · root-level solution researched · recommendation: place viability at the source first, then assess whether a fee-layer margin floor is still needed as a secondary step.**

The constructive answer leads: small-operator viability is best delivered **on the reward-distribution layer (pre-split)**, through a conditional `λ_viability` sub-budget that gives a pool a structural path to productive scale when its operator pledges to a defined schedule — funded from the `λ_size` reduction, **without raising the total pool pot**. That keeps the two functions cleanly separated: `minPoolCost` and `minPoolRate` stay **flexible pricing levers** operators compete on, while the viability backstop lives where it belongs. This is the path the [fee-layer synthesis](operator-delegator/README.md) develops.

Read against that, CIP-0023 and CIP-0082 correctly identify the target — they just address ROS *attractiveness* rather than profitability *structure*. Fee-layer tightening makes small pools more ROS-attractive to delegators but does not raise what a small-pool operator earns at constant size, so the reforms depend on delegation actually migrating from large pools to small ones — a response the diagnostic does not observe (flow tracks brand, wallet integration, and visibility, not yield). Absent that migration, a flat-rate margin floor can run the other way: sub-reliable operator revenue **−9×** under the Margin swap (12 410 → 1 365 ADA/yr), compounding with fleet size to **+200 K ADA/yr per 11+ pool MPO entity vs −11 K ADA/yr per sub-reliable single-pool operator**. Placing viability at the source first avoids that inversion and lets a margin floor, if still wanted, be assessed as a complementary pricing choice.

→ Full argument, the principled separation, and the standalone k-lever deep dive for stages 3–4: [fee-layer synthesis](operator-delegator/README.md). Per-CIP detail: [`cip-0023.md`](operator-delegator/cip-0023.md), [`cip-0082.md`](operator-delegator/cip-0082.md).

# 3. Conclusion

Each candidate names a validated problem and points in a credible direction; what the evaluation adds is that none of them reaches the *source* where the milestone gap is produced — and a root-level package now does. The recommendation is therefore the same across the bundle: **deploy the root-level fix first, for efficient and optimal progress, then assess whether each CIP is still needed as a secondary step.** The per-layer reasoning is in [§2.1](#21-stake-cap-layer-cip-0050-cip-0037) and [§2.2](#22-fee-layer-cip-0023-cip-0082); the synoptic view:

| Candidate | Assessment | Where it fits relative to the root-level fix |
|---|:---:|---|
| [**CIP-0050**](pools-distribution/cip-0050.md) | Problem validated → root-level fix first | Names a real pledge-signal pathology; the σ′ cap sits one step downstream of `A(ν, π)`. Most constructive once the signal is repaired and operators can comply |
| [**CIP-0037**](pools-distribution/cip-0037.md) | Problem validated → root-level fix first | Same target as CIP-0050; the 20 % floor softens the σ′ clip, but `A` is still the deeper lever to move first |
| [**CIP-0023**](operator-delegator/cip-0023.md) | Problem validated → folds into CIP-0082 stage 2 | Same margin-floor primitive as CIP-0082 stage 2 at a smaller calibration; viability is best placed on the reward-distribution layer |
| [**CIP-0082 stage 2**](operator-delegator/cip-0082.md) | Problem validated → root-level fix first | Correctly flags `minPoolCost` as a regressive flat fee; viability sits more cleanly pre-split than bolted onto commission (Sub-reliable **−9×**, **+200 k ₳/yr** to MPO entities if delegation does not migrate) |
| [**CIP-0082 stages 3–4**](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive) | Problem validated → sequence after a stake-cap precondition | A `k`-raise deconcentrates once a stake-cap precondition prevents the 2020-style MPO-fleet absorption |

This is emphatically not a rejection of the underlying intents. CIP-0050 and CIP-0037 capture a real Pledge milestone goal; CIP-0023 and CIP-0082 stage 2 correctly identify `minPoolCost` as a regressive flat fee that needs to go. What the evaluation refines is the **sequencing and the layer**: every candidate acts one step away from the source, so the root-level fix should land first and each proposal be reassessed against it. The pattern across the bundle is the same — and it is addressable.

- **Fee-layer CIPs (CIP-0023 / CIP-0082 stage 2)** address viability by tightening pricing parameters (`minPoolMargin`, `minPoolRate`). The viability function belongs on the reward-distribution layer (pre-split); pricing must remain free for operators to compete in an open market. Conflating the two produces the regressive transfer documented in [§2.2](#22-fee-layer-cip-0023-cip-0082).
- **Stake-cap CIPs (CIP-0050 / CIP-0037)** act on the right layer (pre-split, σ′) but apply a hard cap *on top of* a broken pledge signal: the bonus function `A(ν, π)` that produced today's non-pledging equilibrium is left untouched, and the cap then hits every operator segment at once — destabilisation risk for consensus itself. The fix is at the source (`A` redesign + envelope rebalancing), not at the gate — see [§2.1](#21-stake-cap-layer-cip-0050-cip-0037).
- **Pool-count expansion (CIP-0082 stages 3–4)** addresses Deconcentration by raising `k` without a stake-cap precondition, so the new pool slots fire in the same MPO-fleet absorption regime that produced today's concentration — see [cip-0082 §B.3](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive).

The design space therefore points toward parameter-level adjustments that respect three separations: pricing free-market levers stay flexible; the viability backstop lives on the reward-distribution layer; and pool-count expansion is gated on a stake-cap precondition.

## 3.1. Direct engagement with the Cardano Incentives Working Group's coordinated proposal set

Beyond the four CIPs evaluated above, the **Cardano Incentives Working Group** ([incentives.solutions](https://incentives.solutions)) has authored an adjacent set of proposals — overlapping at points, orthogonal at others. The three pieces this evaluation engages directly:

- **[CIP-50 Rebirth](https://incentives.solutions/cip-50-rebirth/)** — modernised case for CIP-0050. Engaged at length in the per-CIP file [`cip-0050.md`](pools-distribution/cip-0050.md): the Sybil-framing context (§2), the RSS-simulation reality-check (§4), the k-synergy framing (§A.10), and the three findings cards (Appendix B).
- **[K=1000 governance action draft](https://incentives.solutions/k-1-000-gov-action-draft/)** *(2025/12/13)* — a proposal to raise `stakePoolTargetNum` from 500 to 1 000.
- **[CIP-163 — Time-Bound Delegation with Dynamic Rewards](https://cips.cardano.org/cip/CIP-163)** — inactive-stake expiration paired with full-pot rewards distribution.

#### Underlying premise — pledge is one signal of commitment, not the only one.

The Working Group's coordinated set rests on a single foundational premise: the pledge ratio is the binding signal of operator commitment, and the population of multi-pool fleets that has rationally chosen to forgo the pledge bonus must therefore be treated as Sybil-adjacent and capped at the σ′ layer. Every proposal in the set — the pledge-leverage cap (CIP-50 Rebirth), K=1000, CIP-163's redistribution to active stake — inherits this premise.

Pledge *is* an important signal of commitment; this evaluation does not contest that. The diagnostic puts it at the centre of the reform: the wasted `λ_pledge` envelope ([POL.O1](diagnostic/README.md#122-mainnet-observations).F3: 95.6 % returns to reserve) is the headline finding the four-move package targets, and a redesigned bonus function `A(ν, π)` is the first move of that package.

The premise that breaks down is the move from *one signal* to *only signal*. A multi-pool fleet that has run reliable infrastructure for years, attracted and retained delegators on the open market, built tooling and services on top of Cardano, and brought enterprise integrations into the ecosystem has placed substantial assets beyond pledge into the consensus equation — revenue streams, brand capital, operational know-how, customer relationships. From a consensus-economics standpoint these are also skin in the game: losing them is costly, and that cost is what makes honest behaviour rational. The pledge ratio captures self-stake. It does not capture the rest.

The diagnostic's framing follows from this. The problem is not that the multi-pool-fleet population *exists* or that it is concentrated — it is that the formula no longer **balances** its weight against the smaller-pool contribution it was meant to coexist with. There is too much of one pole relative to the others, and the pledge signal that should counterweigh it is unrecognised. A radical budget reduction targeting this population — without redesigning `A(ν, π)`, and without using the levers the envelope already provides (`λ_size`, `λ_pledge`, the unused viability budget) — does not restore that balance. It tilts the imbalance from the other side.

The three engagements below apply this lens to the Working Group's specific proposals.

#### On the K=1000 simulation result.

The K=1000 draft cites a forward-looking Reward-Sharing Simulation result: *"K=1,000 would almost double our Nakamoto coefficient compared to K=500's baseline of 116, achieving approximately 226 at K=1,000."* This is a markedly stronger claim than the +1-entity result the same advocates published in their CIP-50 Rebirth FAQ (where L's marginal effect at k=2 000 was ~159 → ~160).

This evaluation's position remains as documented in [cip-0082 §B.3](operator-delegator/cip-0082.md#b3-standalone-k-lever-deep-dive): the **2020 `k: 150 → 500`** raise is the only natural experiment Cardano has run on `k` at scale, and it produced today's MPO landscape ([POL.O5](diagnostic/README.md#122-mainnet-observations).F1: 83 entities, 449 productive pools, 76.7 % of productive stake). The forward-looking RSS run and the backward-looking mainnet record are not reconciled by either side. Absent a stake-cap precondition that prevents fleet absorption — and absent a viability instrument protecting the small-pool tail while the cap bites — the 2020 evidence weighs heavier.

#### Cross-position confirmation of the viability gap.

The K=1000 draft acknowledges, in its own words, that *"873 active operators (54 % of the total) remain below the 3 M ADA threshold required for consistent block production"* and flags this as *"high social risk"* from *"operator disillusionment"* about the *"viability gap"*.

This matches the diagnostic's finding ([POL.O6](diagnostic/README.md#122-mainnet-observations): 73 % of productive pools below the ~3 M ADA viability line) and is consistent across both positions. What differs is the **response**: the K=1000 proposal does not address the gap directly, while the [recommendations in §4](#4-recommendations-on-adjustments-to-the-current-mechanism) place a viability instrument (the conditional `λ_viability` sub-budget) on the reward-distribution layer as the precondition for any constructive `k`-raise.

#### CIP-163 — orthogonal to the formula-distortion analysis.

CIP-163 targets the **participation gap** the diagnostic also documents ([POL.O1](diagnostic/README.md#122-mainnet-observations).F2: 31.6 % of the pool pot returns to reserve due to unstaked ADA — an upstream cause, outside formula control). Mechanism: inactive stake stops earning rewards; the freed budget redistributes to active pools via full-pot rewards.

CIP-163 does **not** address the bonus function `A(ν, π)`, the size-vs-commitment weighting, or the wasted pledge-bonus budget. If CIP-163 ships, the absolute pool pot reaching active operators grows, but the structural distortions the [recommendations in §4](#4-recommendations-on-adjustments-to-the-current-mechanism) target are unchanged.

**The reserve return is a diagnostic instrument, not a leak.** Cardano's reward circuit carries a built-in audit signal: the share of the pool pot that the formula does not allocate to active operators returns to the reserve. That return is not the network leaking value — it is the network measuring its own misallocation and **withholding payment until the misallocation gets fixed**. The mainnet diagnostic that backs this work was, in substance, an exercise in reading that signal: 31.6 % of the pool pot returning ([POL.O1](diagnostic/README.md#122-mainnet-observations).F2) surfaced the participation gap; 95.6 % of the `λ_pledge` envelope returning ([POL.O1](diagnostic/README.md#122-mainnet-observations).F3) surfaced the bonus-function distortion. Without the reserve-return channel, neither finding would have a quantitative anchor.

CIP-163 redistributes that signal rather than acting on it. The unstaked-ADA share is captured and pushed back into active-pool rewards via full-pot distribution; what the system was withholding becomes a yield boost handed to the same pools whose absorption pattern produced the misallocation. From the audit standpoint this is *sweeping the inefficiency under the rug* — paying out before correcting, which is precisely the discipline the reserve-return mechanism was designed to enforce. In this evaluation's view, that is a <span class="red-flag">red flag</span>.

**Downstream — uncontrolled delegation rebalancing.** The yield boost lands unevenly: pools positioned to absorb the redirected flows experience an unearned euphoria moment the formula does not justify. Delegation movement under those conditions tracks absolute yield deltas rather than relative pool quality, and the resulting stake-rebalancing is potentially uncontrolled.

The reform conversation depends on the population reading distortion as distortion. A window of apparent prosperity competes against that and momentarily crowds out structural diagnosis — which is why CIP-163 reads better as a coordinated companion to the four-move package than as a standalone deployment ahead of it.

The two proposal sets are therefore **complements, not competitors**: CIP-163 fixes what the formula does *not* control (upstream participation); the four-move package fixes what it *does* control (downstream allocation). Sequencing matters: deploying the formula reform alongside (or ahead of) the participation fix preserves the diagnostic clarity the reform case rests on.

# 4. Recommendations on adjustments to the current mechanism

A set of parameter-level recommendations is in preparation by IO Research, targeting end of 2026. The recommendations respect the **three layer separations** isolated in [§3 Conclusion](#3-conclusion) — pricing levers stay flexible, viability lives on the reward-distribution layer, pool-count expansion is gated on a stake-cap precondition — and propose a **gradual path** that reinforces the pledge signal at its source rather than gating it.

> **Where this sits in the V2 work.** The four-move package developed below is the candidate solution carried into [Analysis — Milestone 1 — Repair pledge, sustain the small SPO base](../README.md#21-milestone-1-repair-pledge-sustain-the-small-spo-base). The Analysis section reframes this analytical work as a milestone with explicit constitutional alignment (Tenets 9 and 4), an explicit *root-causes-before-scale-up* sequencing argument, and integration with the rest of the V2 priority order — operator viability bundled with the pledge paradox, downstream milestones (Pool Alliance, non-participant scale-up) sequenced after this one. This section remains **the analytical foundation those four moves rest on**.

## 4.1. Why gradual, not radical

A hard pledge cap (CIP-0050 / CIP-0037 style) lands on a regime where almost no one pledges at scale today: **median pool pledge ratio = 0.07 %**, **78 %** of staked ADA below 1 %, **42 of 48** saturation MPOs forfeit the pledge bonus. We do not actually know how much of the SPO landscape *can* comply if a hard cap is switched on — and what mainnet shows so far is *almost no one*.

Switching on the cap in that regime hits **every** segment at once — small / single-pool retail (no liquid capital), multi-pool entities (clipped per-pool axis, can't comply across all pools), custodial-by-extraction (cannot self-pledge by construction). The resulting reward collapse risks **destabilising consensus itself**: if most operators see income fall sharply at once, infrastructure gets reduced or shut down and Cardano's block-production reliability degrades. A reform meant to *strengthen* commitment ends up *weakening* basic operation.

The fix is **at the source**, not at the gate. Repair the formula bottleneck first, let the pledge signal recover *with* the operator population, then a pledge-binding instrument becomes constructive rather than a clip on a broken regime.

## 4.2. Four moves on the reward-distribution layer

The recommendations propose the four moves below, applied in this order. None requires a hard fork beyond a coordinated formula change at the activation epoch.

### 1. Repair `A(ν, π)` so pledge stops being a dominated strategy

The bonus function `A(ν, π)` inside the SL-D1 reward envelope produces today's non-pledging equilibrium. Three structural pathologies in the current `A` (full anatomy in the [stake-cap layer synthesis](pools-distribution/README.md)):

- a **quadratic `ν²` size penalty** that crushes small pools at every pledge ratio;
- a **non-monotonicity in π** for sub-half-saturated pools — at ν ≈ 0.03 a 2 M operator earns **8.7×** more bonus by pledging 51 % than by pledging 100 % (the formula explicitly *incentivises small operators to under-commit*);
- a **cubic `ν³` collapse at full self-pledge** — at maximum commitment, a saturated operator earns 37 595× more bonus than a 2 M operator at the same pledge ratio.

A repaired `A` must deliver three properties no current CIP delivers:

- a **smoother operator onset at low ν** — no cubic crush of small pools as they grow;
- a design that **does not privilege fully-private pools (π = 1)** — V2's target is not "everyone runs a 100 % self-pledged pool";
- explicit reward for the **balanced-commitment regime (π ≈ 0.5)** — pledge serving as a credible signal *and* the pool remaining open to delegation.

### 2. Reduce `λ_size` so the commitment axis carries more of the signal

The reward envelope is `E(ν, π) = λ_size·ν + λ_pledge·A(ν, π)`. Today `λ_size ≈ 76.9 %` and `λ_pledge ≈ 23.1 %` (set by `a₀ = 0.3`). The size axis dominates; the commitment axis is a small smooth nudge.

Reducing `λ_size` (equivalently, raising `a₀`) lets the *commitment* axis (π) carry more of the signal and the *size* axis (ν) carry less. The calibration only makes sense **after `A` is repaired** — applied to today's broken `A`, raising `a₀` amplifies the existing bias rather than correcting it (see [Appendix A — Why V1's pledge incentive doesn't work](pools-distribution/README.md#appendix-a-why-v1s-pledge-incentive-doesnt-work) in the stake-cap synthesis).

The size-weight cut **does double duty**: it reduces what low-pledge pools currently extract through the size axis, *and* the freed weight funds the viability slice in move 3 below.

### 3. Add a viability package for pools entering the lifecycle — open a new `λ_viability` sub-budget

Today the reward envelope is split **two ways** (`λ_size + λ_pledge`). The recommendation is a **three-way split**: `λ_size + λ_pledge + λ_viability`, **without raising the total pool pot**. While transaction-fee inflows are still small, the global allocation stays where it is; it grows back naturally as Tx fees mature into a larger share of the pot. **The funding source for `λ_viability` is the `λ_size` reduction in move 2** — nothing new is taken from elsewhere; nothing is asked from the reserve.

`λ_viability` is **conditional**, not unconditional: a pool benefits from the viability slice **only if its operator pledges according to rules to be specified** (e.g. a minimum pledge ratio or a pledge-growth schedule across lifecycle stages). This gives new operators a structural path to productive scale without trapping them in V1's `minPoolCost` floor at small sizes — *and* it preserves the principled separation the [fee-layer synthesis](operator-delegator/README.md) lays out: viability lives on the **reward-distribution layer (pre-split)**, pricing tools (`minPoolCost`, margin, rate) stay free as competitive levers.

### 4. Activate the `λ_pledge` budget that has been underused for years

POL.O1.F3 documents that **95.6 % of the pledge-bonus budget already returns to the reserve unused every epoch** — that is **3.43 M ADA/epoch** (≈ 250 M ADA/yr), **22.1 %** of the entire pool pot, *the single largest addressable inefficiency in the reward pipeline today*.

A repaired `A` with a reduced `λ_size` is what activates this budget. **It is not new ADA — it is unused ADA already inside the formula's envelope.** A gradual reform that successfully restores commitment-as-signal will, by the same act, also recover the largest inefficiency the diagnostic flags. A radical cap on top of today's regime does the opposite: it sends an even larger share of the pool pot back to the reserve and worsens viability for every SPO segment at once.

# 5. References

- **Analysis:** [`../README.md`](../README.md) — directions of exploration and concrete milestones, anchored on the 9 induced problems.
- **Induced Problems:** [`../generated-website/problem-statements.html`](../generated-website/problem-statements.html) — the 9 structural problems the diagnostic surfaces, the empirical anchor every CIP evaluation cites against.
- **Mainnet diagnostic:** [`../diagnostic/README.md`](../diagnostic/README.md).
- **Mechanism-intent narrative:** [`../the-intended-game/README.md`](../the-intended-game/README.md).
- **Per-layer indexes:** [`pools-distribution/README.md`](pools-distribution/README.md), [`operator-delegator/README.md`](operator-delegator/README.md).
- **Per-CIP evaluations:** [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md) (with §B.3 carrying the standalone k-lever deep dive that supports the verdict on stages 3–4).
- **Canonical CIP sources:** [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs) on GitHub; per-CIP page at [cips.cardano.org](https://cips.cardano.org/).
- **External advocate publication engaged in this evaluation:** [CIP-50 Rebirth — Claims, Problems, and Evidence](https://incentives.solutions/cip-50-rebirth/) (Liesenfelt et al., on `incentives.solutions`) — published case for CIP-0050 paired with a `k`-raise. The radical-vs-gradual reframing in [§2.1](#21-stake-cap-layer-cip-0050-cip-0037) engages directly with this proposal; [`cip-0050.md`](pools-distribution/cip-0050.md) §A.10 addresses the k-synergy framing it advances, and §4 references the Edinburgh Reward-Sharing Simulation results it cites.

> **Status:** Active 2026/04/22. Working folder evaluating the live CIPs and parameter-level proposals against the [Solution Design](../README.md) and the 9 induced problems.
