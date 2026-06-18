This page picks up where [Induced Problems](problem-statements.html) leaves off and asks the next question in the chain: *given these 9 structural problems, in what order does the system evolve toward a coherent V2?*

Reaching that order is not a ranking exercise. The 9 problems are pitched at very different levels of abstraction — some are foundational concerns about what the protocol *is for*, others are specific quantitative shortfalls, still others are lens-of-view framings that re-illuminate the same underlying issue from different angles. A flat numeric ranking would miss those distinctions and would produce a roadmap that wastes effort on the wrong scale of fix.

The bet of this page is that **a clear priority order makes solutions emerge**. Once the 9 problems are mapped — by abstraction level, by hierarchical dependence, by the lens-of-view relationships that bind some of them together — candidate designs cluster around the high-priority items naturally, and the V2 work stops looking like a flat list of fixes and starts looking like a *sequenced roadmap* that the system can actually evolve along.

**The page is offered as an ideation document**, not as a closed proposal. The directions and milestones below are starting points for community shaping — to be refined, challenged, sequenced, or replaced through the conversation that builds V2.

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
<div class="cps-stage cps-stage-current" title="You are here — Solution Design">
<span class="cps-stage-num">Stage 04</span>
<span class="cps-stage-label">Solution Design</span>
<span class="cps-stage-meta">Directions &amp; milestones &middot; this page</span>
</div>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-future" href="solution-evaluation.html" title="Evaluation of the four reward-related CIPs against the nine induced problems">
<span class="cps-stage-num">Stage 05</span>
<span class="cps-stage-label">CIPs (Evaluation)</span>
<span class="cps-stage-meta">IntersectMBO governance</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-future" href="build-scoping.html" title="Build Estimation / Scoping — sizing the build for the V2 stage-1 reform">
<span class="cps-stage-num">Stage 06</span>
<span class="cps-stage-label">Build Estimation / Scoping</span>
<span class="cps-stage-meta">Build sizing</span>
</a>
</div>

The 9 problems below are the starting point — repeated here so the chain of reasoning stays in view, and so each can be opened in its own card on [Induced Problems](problem-statements.html) for the full evidence and observations.

<nav class="findings-toc" aria-label="Induced problems — starting point for V2 prioritisation">
<div class="findings-toc-group">
<div class="findings-toc-group-head"><span class="findings-toc-group-label">Microeconomics <span class="findings-toc-group-count">5</span></span></div>
<div class="findings-toc-group-meta">Participant-level gaps</div>
<div class="findings-toc-group-list">
<a class="findings-toc-item" href="problem-statements.html#problem-1-2-3"><span class="findings-toc-num">μ01</span><span class="findings-toc-title">Closing the Consensus Incentive Gap: The pledge paradox &amp; Non-Participant problem</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-1-3-3-1"><span class="findings-toc-num">μ02</span><span class="findings-toc-title">Guarantee operator viability across the productive population</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-1-3-3-2"><span class="findings-toc-num">μ03</span><span class="findings-toc-title">Restore a competitive delegator yield — soon to fall below 2% AYI</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-2-1-3-1"><span class="findings-toc-num">μ04</span><span class="findings-toc-title">SPO (Supply-side) — fewer and fewer entities participate in consensus</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-2-1-3-2"><span class="findings-toc-num">μ05</span><span class="findings-toc-title">Delegator (Arbiter-side) — titans move the disciplining capital, but not on yield</span></a>
</div>
</div>
<div class="findings-toc-group">
<div class="findings-toc-group-head"><span class="findings-toc-group-label">Macroeconomics <span class="findings-toc-group-count">4</span></span></div>
<div class="findings-toc-group-meta">System-level gaps</div>
<div class="findings-toc-group-list">
<a class="findings-toc-item" href="problem-statements.html#problem-1-1-3"><span class="findings-toc-num">M01</span><span class="findings-toc-title">Funding the Protocol Without a Reserve</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-2-2-3"><span class="findings-toc-num">M02</span><span class="findings-toc-title">Tx Submitter (Demand-side) — fees, the canonical answer to M01, are not growing fast enough at current throughput</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-3-1-1"><span class="findings-toc-num">M03</span><span class="findings-toc-title">A deflationist ₳ — what mechanisms can complement finite supply?</span></a>
<a class="findings-toc-item" href="problem-statements.html#problem-3-1-2"><span class="findings-toc-num">M04</span><span class="findings-toc-title">₳/Fiat volatility — what instruments can wire governance to price observations?</span></a>
</div>
</div>
</nav>

# Table of Contents

- [1. Constitutional framework](#1-constitutional-framework)
  - [1.1. The normative foundation — Tenets 4, 9, 10](#11-the-normative-foundation-tenets-4-9-10)
    - [1.1.1. Tenet 4 — Fair compensation](#111-tenet-4-fair-compensation)
    - [1.1.2. Tenet 9 — Fair treatment](#112-tenet-9-fair-treatment)
    - [1.1.3. Tenet 10 — Monetary stability](#113-tenet-10-monetary-stability)
  - [1.2. The governance pathway — parameter updates within guardrails](#12-the-governance-pathway-parameter-updates-within-guardrails)
    - [1.2.1. Per-parameter detail](#121-per-parameter-detail)
  - [1.3. The entity gap — a pool-level Constitution meeting an entity-level problem](#13-the-entity-gap-a-pool-level-constitution-meeting-an-entity-level-problem)
  - [1.4. How the priority work below cites the Constitution](#14-how-the-priority-work-below-cites-the-constitution)
- [2. Microeconomics — participant incentives and market structure](#2-microeconomics-participant-incentives-and-market-structure)
  - [2.1. Milestone 1 — Repair pledge, sustain the small SPO base](#21-milestone-1-repair-pledge-sustain-the-small-spo-base)
    - [2.1.1. Why this bundle, and why it comes first](#211-why-this-bundle-and-why-it-comes-first)
    - [2.1.2. The proposed direction — a coordinated four-move repair on the reward-distribution layer](#212-the-proposed-direction-a-coordinated-four-move-repair-on-the-reward-distribution-layer)
  - [2.2. Milestone 2 — Maintain and diversify a competitive delegator yield](#22-milestone-2-maintain-and-diversify-a-competitive-delegator-yield)
    - [2.2.1. The three faces of the yield problem](#221-the-three-faces-of-the-yield-problem)
    - [2.2.2. What smart contracts unlock — diversification and programmable pledge](#222-what-smart-contracts-unlock-diversification-and-programmable-pledge)
  - [2.3. Milestone 3 — A Pool Alliance, rocket-pool-like for Cardano](#23-milestone-3-a-pool-alliance-rocket-pool-like-for-cardano)
    - [2.3.1. Why the production threshold deserves reinforcing](#231-why-the-production-threshold-deserves-reinforcing)
    - [2.3.2. The two-step plan — make the threshold explicit, and build the Pool Alliance below it](#232-the-two-step-plan-make-the-threshold-explicit-and-build-the-pool-alliance-below-it)
  - [2.4. Milestone 4 — Scale up with the non-participant population](#24-milestone-4-scale-up-with-the-non-participant-population)
  - [2.5. Research axis — reduce the concentration effects that distort both populations](#25-research-axis-reduce-the-concentration-effects-that-distort-both-populations)
    - [2.5.1. Entity-level awareness — the supply-side question](#251-entity-level-awareness-the-supply-side-question)
    - [2.5.2. Titan-tier differentiation — the demand-side question](#252-titan-tier-differentiation-the-demand-side-question)
- [3. Macro-economics — instrumentation, recalibration, and the path to auto-regulation](#3-macro-economics-instrumentation-recalibration-and-the-path-to-auto-regulation)
  - [3.1. Milestone 1 — Reward System Extension — A Governance Dashboard for the System Properties & Populations](#31-milestone-1-reward-system-extension-a-governance-dashboard-for-the-system-properties-populations)
    - [3.1.1. The four surveillance lines, and what each one watches](#311-the-four-surveillance-lines-and-what-each-one-watches)
    - [3.1.2. From governed interventionism to gradual auto-regulation](#312-from-governed-interventionism-to-gradual-auto-regulation)
  - [3.2. Research axis — deflationist ADA and its volatility](#32-research-axis-deflationist-ada-and-its-volatility)
    - [3.2.1. The deflationist promise — complementary monetary properties beyond finite supply](#321-the-deflationist-promise-complementary-monetary-properties-beyond-finite-supply)
    - [3.2.2. Wiring governance to macro signals — recalibration against price observations](#322-wiring-governance-to-macro-signals-recalibration-against-price-observations)

Three working axes anchor the reasoning over these 9 problems.

*Abstract vs actionable.* Some are foundational design concerns — *Funding the Protocol Without a Reserve* (M01) is the canonical example. Others are specific quantitative shortfalls — *Restore a competitive delegator yield* (μ03) is the canonical actionable problem. Tackling the abstract ones requires a foundational design effort; tackling the actionable ones can proceed with parameter-level work. A priority order that treats them as siblings misallocates effort.

*Hierarchical dependence.* Several problems are specific directions of broader ones. M02, M03 and M04 are three directions inside M01 — fee growth, complementary monetary properties, macro-feedback instruments. Listing the four as peers loses the implication chain.

*Lens-of-view problems.* μ01 is not a discrete problem but a lens of view over the entire reward mechanism: *does reward distribution produce the operator equilibrium it was designed to produce?* Most other μ-problems can be re-expressed as instances of it. Treating μ01 as an item alongside its own instances is a category error.

These three axes — abstraction, dependence, and lens-of-view — are the working tools. The priority order they produce, and the candidate solutions that cluster against it, are what the rest of this page will turn into as the work proceeds.

# 1. Constitutional framework

Before any priority order is committed, the [Cardano Constitution v2](https://github.com/IntersectMBO/cardano-constitution/tree/main/cardano-constitution-2) (ratified at epoch 609) sets the boundaries the work has to respect. It provides both the **normative foundation** — what the protocol owes to its participants — and the **governance pathway** — what can be changed through Parameter Update actions versus what would require constitutional evolution.

The 9 induced problems are not equally constrained by this framework. Some directly invoke ratified tenets and can be advanced through existing governance machinery; others touch parameters within explicit guardrail ranges; one (entity-level dynamics, surfaced through μ04) sits in a constitutional gap that has to be resolved one way or another before its candidate solutions become actionable.

## 1.1. The normative foundation — Tenets 4, 9, 10

Three tenets of the Constitution are directly relevant to the 9 induced problems. Each is explored in its own sub-section below: which problems it grounds, where the current mechanism falls short of it, and what a candidate solution has to demonstrate to remain compliant.

### 1.1.1. Tenet 4 — Fair compensation

> *Operators and delegators who maintain the network are entitled to fair compensation for their contribution.*

This tenet grounds three induced problems:

- [μ02 — Guarantee operator viability across the productive population](problem-statements.html#problem-1-3-3-1);
- [μ03 — Restore a competitive delegator yield — soon to fall below 2% AYI](problem-statements.html#problem-1-3-3-2);
- [M01 — Funding the Protocol Without a Reserve](problem-statements.html#problem-1-1-3) — the long-term funding pathway through which compensation is delivered.

Any mechanism that **systematically under-compensates productive participants** violates the Constitution's own standard.

### 1.1.2. Tenet 9 — Fair treatment

> *All participants in the Cardano ecosystem shall be treated fairly and shall not be subject to unjustifiable discrimination.*

Two features of the current mechanism fall short of this standard:

- the fee structure imposes a **48% effective cost on sub-reliable operators** while charging **1.5% near saturation** ([OPE.O1](diagnostic.html#132-mainnet-observations));
- the pledge mechanism provides **no material reward for commitment** ([POL.O7](diagnostic.html#122-mainnet-observations)).

Three induced problems address this gap, each along a different dimension:

- [μ01 — Closing the Consensus Incentive Gap: The pledge paradox & Non-Participant problem](problem-statements.html#problem-1-2-3) — the pledge dimension and the inclusion-of-outside-participants face;
- [μ02 — Guarantee operator viability across the productive population](problem-statements.html#problem-1-3-3-1) — the fee-structure dimension;
- [μ04 — SPO (Supply-side) — fewer and fewer entities participate in consensus](problem-statements.html#problem-2-1-3-1) — the entity-level distortion that pool-level fairness cannot address on its own.

### 1.1.3. Tenet 10 — Monetary stability

> *The protocol shall not dilute or inflate ada in a manner that is inconsistent with the long-term sustainability and integrity of the ecosystem.*

This tenet constrains:

- [M01 — Funding the Protocol Without a Reserve](problem-statements.html#problem-1-1-3) — the funding-model transition;
- [M03 — A deflationist ₳ — what mechanisms can complement finite supply?](problem-statements.html#problem-3-1-1) — complementary monetary properties beyond the supply cap;
- [M04 — ₳/Fiat volatility — what instruments can wire governance to price observations?](problem-statements.html#problem-3-1-2) — macro-feedback instruments and any tool that draws on the **reserve or treasury** to fund operator support.

## 1.2. The governance pathway — parameter updates within guardrails

The Constitution also defines the **governance pathway**.

Five parameters shape the reward mechanism. Each is bounded by a **guardrail range** and modifiable through **Parameter Update governance actions**:

| Parameter | What it controls | Current value (mainnet) | Guardrail range | CIP range |
| --- | --- | --- | --- | --- |
| $minPoolCost$ | Flat-fee floor every pool charges from its rewards before margin is applied | 170 ADA | $[0, 500]$ ADA | MPC-01 to MPC-03 |
| $a_0$ | Pledge-influence factor — weight the reward formula gives to operator self-pledge | 0.30 (Shelley default) | $[0.1, 1.0]$ | PPI-01 to PPI-04 |
| $k$ | Optimal/saturation pool count — the network is "calibrated" for $k$ saturated pools, each holding $\approx 1/k$ of total stake | 500 (Shelley default) | $[250, 2000]$ | SPTN-01 to SPTN-04 |
| $\rho$ | Per-epoch monetary expansion rate — the slice of the reserve drawn into the epoch pot every epoch | 0.003 (0.3 %, Shelley default) | $[0.001, 0.005]$ | ME-01 to ME-05 |
| $\tau$ | Treasury cut — fraction of the epoch pot routed to the treasury before pool distribution | 0.20 (20 %, Shelley default) | $[0.1, 0.3]$ | TC-01 to TC-05 |

Parameter Updates require a **51–75 % approval threshold** depending on the parameter class. Changes to critical parameters must additionally observe a **90-day publication-to-submission timeline**.

This is a lower bar than Constitutional amendment (Article IV). Several of the 9 induced problems can, in principle, be advanced through the existing governance machinery **without amending the Constitution itself**.

### 1.2.1. Per-parameter detail

**`minPoolCost` — the flat-fee floor.** The only one of the five that has been adjusted post-Shelley: cut from 340 to 170 ADA in epoch 445 by [CIP-0082](cip-0082.html) stage 1, after years of debate over its regressive effect on small operators. Inside the current guardrail [0, 500] ADA, parameter updates can move it further down (toward 0) or back up to the ceiling. The flat fee follows a $1/\sigma$ hyperbola: it absorbs **47.5 % of pool reward at the sub-reliable tier** but only **1.5 % near saturation** ([OPE.O1](diagnostic.html#132-mainnet-observations)). Touches:

- [μ02 — operator viability](problem-statements.html#problem-1-3-3-1) directly — the corridor where pools produce blocks but cannot sustain operators *is* the flat-fee corridor;
- [μ03 — delegator yield](problem-statements.html#problem-1-3-3-2) indirectly — at small pools, every additional ADA the operator absorbs as flat fee is taken out of the delegator's net return.

**$a_0$ — pledge-influence factor.** Set by Shelley at 0.3, unchanged since. In the reward envelope $E(\nu, \pi) = \lambda_{\text{size}}\,\nu + \lambda_{\text{pledge}}\,A(\nu, \pi)$, $a_0 = 0.3$ implies $\lambda_{\text{size}} \approx 76.9 \%$ and $\lambda_{\text{pledge}} \approx 23.1 \%$ — the size axis dominates, the commitment axis is a small smooth nudge. Inside its guardrail [0.1, 1.0], parameter updates can shift more weight to either axis, but the **structure of the bonus function $A(\nu, \pi)$ itself is fixed** — $a_0$ only re-weights it. Touches:

- [μ01 — Closing the Consensus Incentive Gap](problem-statements.html#problem-1-2-3) directly — $a_0$ is the lever that determines how much the reward formula weights pledge versus pool size; with the current $A$ structure, even raising $a_0$ amplifies the existing non-monotonicity rather than fixing it ([POL.O7](diagnostic.html#122-mainnet-observations));
- [μ04 — SPO supply side](problem-statements.html#problem-2-1-3-1) indirectly — pledge weight changes the strategic calculus of new entrants and of consolidators.

**$k$ — optimal/saturation pool count.** Set by Shelley at 500, unchanged since. With ~22 B ADA staked, the per-pool saturation point sits at ~44 M ADA. [CIP-0082](cip-0082.html) stages 3–4 propose raising $k$ to 750 then 1000 (well inside the [250, 2000] guardrail). Higher $k$ means more pools can saturate and earn maximal reward density, but also a smaller average pool size — which compounds the flat-fee drag in the absence of complementary `minPoolCost` work. Touches:

- [μ04 — SPO supply side](problem-statements.html#problem-2-1-3-1) directly — $k$ controls how many "slots" the network can sustain at saturation, and therefore the structural ceiling on entity dispersion;
- [μ02 — operator viability](problem-statements.html#problem-1-3-3-1) — average pool size scales as $1/k$, so raising $k$ in isolation can *deepen* the viability gap rather than close it.

**$\rho$ — monetary expansion rate.** Set by Shelley at 0.003 (0.3 % per epoch), unchanged since. $\rho$ controls how fast the reserve is drawn into the epoch pot, and therefore the entire emission trajectory. Inside its guardrail [0.001, 0.005], parameter updates can slow expansion (extending the reserve runway and softening dilution) or accelerate it (front-loading rewards at the cost of an earlier exhaustion date). Touches:

- [M01 — Funding the Protocol Without a Reserve](problem-statements.html#problem-1-1-3) directly — $\rho$ is *the* lever on the source side of the funding question, and any V2 transition plan has to declare what happens to $\rho$ as fees grow;
- [M03 — A deflationist ₳](problem-statements.html#problem-3-1-1) — $\rho$ shapes the supply trajectory toward the cap and is therefore one of the levers a deflationist mechanism can complement;
- [M04 — ₳/Fiat volatility](problem-statements.html#problem-3-1-2) — $\rho$ is the natural target for any macro-feedback instrument that adjusts emission against price observations.

**$\tau$ — treasury cut.** Set by Shelley at 0.20 (20 % of the epoch pot), unchanged since. $\tau$ routes a slice of the epoch pot into the treasury before pool distribution. Inside its guardrail [0.1, 0.3], parameter updates can grow the treasury's share (more headroom for treasury-funded interventions, less left for pool rewards) or shrink it (the inverse trade). Touches:

- [M01 — Funding the Protocol Without a Reserve](problem-statements.html#problem-1-1-3) — the treasury is one of the three protocol-level resources any post-reserve funding model can draw on (alongside fees and a redesigned emission curve);
- [M04 — ₳/Fiat volatility](problem-statements.html#problem-3-1-2) — treasury operations are one candidate macro-feedback instrument (treasury-funded operator support during sustained price downturns is a frequently-cited example).

**Where this lands for the priority work.** The fact that all five parameters sit inside guardrails the Constitution already approves means that for several of the 9 induced problems, candidate solutions are at most a Parameter Update away from being tractable — μ02 and μ03 most directly, since both are moved by `minPoolCost` and `k` inside their guardrails. The harder problems are the ones whose candidate solutions require *new instruments* the Constitution doesn't yet name: M03 (complementary monetary properties beyond finite supply) and M04 (macro-feedback wiring) both fall in this class. They sit closer to the entity-gap question of §1.3.

## 1.3. The entity gap — a pool-level Constitution meeting an entity-level problem

The Constitution operates at the **pool level**: it governs pool parameters and pool-level constraints.

The concept of operator *entity* — a cluster of pools sharing a common controller — has **no constitutional anchor**.

[μ04 — SPO (Supply-side) — fewer and fewer entities participate in consensus](problem-statements.html#problem-2-1-3-1) therefore occupies a distinct position. It can be resolved along one of two paths:

- **constitutional evolution** — recognise entities as first-class participants;
- a **protocol-level mechanism** — achieve entity-level accounting within the existing constitutional framework.

The choice between these two paths is itself a priority question: constitutional evolution is the higher-bar path (Article IV amendment), but a protocol-level workaround can drift if entity attribution remains best-effort. Both options stay open at this stage.

## 1.4. How the priority work below cites the Constitution

The priority order over the 9 induced problems — and the candidate solutions that cluster against it — will reference their constitutional grounding explicitly:

- where a tenet supports addressing a problem, it is cited;
- where a guardrail constrains the parameter space available to a candidate solution, the bounds are noted;
- where a gap exists (entity-level concerns, monetary instruments not yet wired in), it is identified and the resolution path (constitutional evolution vs protocol workaround) is named.

**The Constitution is not decoration** — it is the governance instrument through which the priority work below becomes actionable.

# 2. Microeconomics — participant incentives and market structure

The first group of milestones addresses the **microeconomics** of the mechanism: the participant-level incentive structures that shape **operator behaviour**, **pledge commitment**, **delegator yield**, and **market concentration**. These are the problems that manifest at the individual actor level — the reward curve, the fee structure, the pledge function, and the entity-recognition gap.

The framing here departs slightly from a milestone-per-problem decomposition. Several of the 9 induced problems are tightly coupled at the reward-distribution layer — repairs to one without the others tend to undo themselves. Where that coupling is real, the milestone bundles them; where it is loose, downstream milestones address the remaining faces in turn.

## 2.1. Milestone 1 — Repair pledge, sustain the small SPO base

This milestone bundles two of the 9 induced problems whose repairs share a single mechanism layer:

- the **pledge paradox** dimension of [μ01 — Closing the Consensus Incentive Gap](problem-statements.html#problem-1-2-3) — the operator side of the broken commitment signal: pledge yield 0.68 %/yr against ~2.3 %/yr from passive delegation, 78 % of staked ADA in pools below 1 % pledge, 42 of 48 saturation-scale MPOs forfeiting the bonus;
- [μ02 — Guarantee operator viability across the productive population](problem-statements.html#problem-1-3-3-1) — the corridor where 73 % of pools sit below the viability line and no single-pool retail operator earns a competitive wage.

### 2.1.1. Why this bundle, and why it comes first

Both problems sit on the same layer (the reward-distribution layer, *upstream* of the operator/member fee split), and both call for the same kind of fix — a coordinated repair of the reward envelope that simultaneously rebalances the pledge axis and opens a viability sub-budget. **Splitting the fix across separate milestones produces partial repairs that mutually undermine each other.** Raising `k` without addressing the flat-fee drag deepens the viability gap; raising `a_0` without repairing `A(ν, π)` amplifies the existing non-monotonicity; bolting viability into pricing tools (CIP-0023 / CIP-0082 stage 2 style) regresses delegator yield ([fee-layer synthesis](fee-layer.html)). The bundle is mechanical, not editorial.

The **non-participant** dimension of μ01 (bringing reachable but inert ADA back into staking) and the **strengthening of the productive threshold** are addressed in their own milestones below — Milestone 3 (Pool Alliance) and Milestone 4 (non-participant scale-up) — not folded into this one. **The order is critical: before scaling up, the root causes have to be fixed.** Pulling more participants into the staking system, or making it easier for new operators to clear the productive threshold, *while the pledge signal is still broken and the small-SPO viability gap is still open*, does not dilute the existing concentration — it amplifies it: the new capital and the new entrants both flow toward the dominant fleets and the visibility-driven defaults that today's distortions reward. Milestone 1 fixes the structural ground; Milestones 3 and 4 grow on it. Reversing the sequence is a recipe for enlarging the very pathologies the diagnostic surfaces.

**Constitutional alignment.** Tenet 9 (fair treatment) is the central anchor: the current $1/\sigma$ flat-fee structure imposes a 48 % effective cost on sub-reliable operators while charging 1.5 % near saturation ([OPE.O1](diagnostic.html#132-mainnet-observations)) — a textbook *unjustifiable discrimination* against small operators. Tenet 4 (fair compensation) compounds this: under-compensated single-pool operators (median ~25 K ADA/yr, ~$6.25 K at $0.25/ADA) violate the Constitution's own standard of fair compensation. The relevant governance parameters — `minPoolCost` (MPC-01 to MPC-03), `a_0` (PPI-01 to PPI-04), and `k` (SPTN-01 to SPTN-04) — are all modifiable through Parameter Update actions inside their ratified guardrails, making the directions below **actionable within the existing governance framework**.

### 2.1.2. The proposed direction — a coordinated four-move repair on the reward-distribution layer

The candidate solution this milestone reprises is the **four-move gradual path** developed in the [Solution Evaluation §4 — Recommendations on adjustments to the current mechanism](solution-evaluation.html#4-recommendations-on-adjustments-to-the-current-mechanism). The four moves act on the reward-distribution layer (pre-split), at the source of the broken signals, without touching the fee-pricing layer that should remain a free competitive lever:

1. **Repair `A(ν, π)`** — the pledge-bonus structure inside the SL-D1 reward envelope. Three pathologies in the current `A` produce today's non-pledging equilibrium: a quadratic `ν²` size penalty that crushes small pools, a non-monotonicity in `π` that incentivises sub-half-saturated operators to *under-commit*, and a cubic `ν³` collapse at full self-pledge. A repaired `A` must (a) smooth the operator onset at low `ν`, (b) avoid privileging fully-private pools (`π = 1`), and (c) reward the balanced-commitment regime (`π ≈ 0.5`).

2. **Reduce `λ_size` so the commitment axis carries more of the signal.** Today `λ_size ≈ 76.9 %` against `λ_pledge ≈ 23.1 %` (set by `a_0 = 0.3`). The size axis dominates; the commitment axis is a small smooth nudge. Reducing `λ_size` (equivalently, raising `a_0` toward the [0.1, 1.0] guardrail's upper half) lets the commitment signal weigh more — but the calibration only makes sense **after `A` is repaired**; raising `a_0` against today's broken `A` amplifies the existing bias rather than correcting it.

3. **Add a `λ_viability` sub-budget for pools entering the lifecycle.** A three-way split of the reward envelope — `λ_size + λ_pledge + λ_viability` — without raising the total pool pot. The viability slice is **conditional**: a pool benefits from it only if its operator pledges according to a rule to be specified (e.g. a minimum pledge ratio or a pledge-growth schedule across lifecycle stages). This gives new operators a structural path to productive scale without trapping them in V1's `minPoolCost` floor at small sizes — *and* preserves the principled separation that `minPoolCost` and `minPoolMargin` stay flexible competitive levers ([fee-layer synthesis](fee-layer.html)). Funding for `λ_viability` comes from the `λ_size` reduction in move 2.

4. **Activate the `λ_pledge` budget that has been underused for years.** [POL.O1.F3](diagnostic.html#122-mainnet-observations) documents that **95.6 % of the pledge-bonus budget already returns to the reserve unused every epoch** — 3.43 M ADA/epoch (≈ 250 M ADA/yr), 22.1 % of the entire pool pot, the single largest addressable inefficiency in the reward pipeline today. A repaired `A` with a reduced `λ_size` is what activates this budget. **It is not new ADA — it is unused ADA already inside the formula's envelope.**

The four moves are sequenced: **1 then 2 then 3 then 4** is not arbitrary — each step requires the previous to have landed before its calibration becomes meaningful.

## 2.2. Milestone 2 — Maintain and diversify a competitive delegator yield

This milestone takes up [μ03 — Restore a competitive delegator yield — soon to fall below 2% AYI](problem-statements.html#problem-1-3-3-2). The work has two dimensions, captured in the title: **maintain** the absolute return at a level that keeps staking competitive with on-chain alternatives, and **diversify** the delegation offer so the yield comes from more than a single depleting source.

**V1 was designed before the tools V2 inherits existed.** The reward mechanism on mainnet today was specified in 2019 and went live in August 2020 — *before* Plutus (smart contracts arrived with the Alonzo hard fork in September 2021), *before* on-chain governance (Conway, 2024), and before a smart-contract-driven fee economy of any size. Within those constraints, a single conservative yield architecture was chosen: a base return derived from monetary expansion (`ρ`) modulated by the participation rate, distributed through pure on-chain delegation with no lockup, no slashing, no programmable variants. *That was the right choice for the chain that existed in 2020.*

[§1.3.3.2 of the diagnostic](diagnostic.html#1332-restore-a-competitive-delegator-yield-soon-to-fall-below-2-ayi) names the trade-off cleanly: *"what Cardano gains in design (no lockup, no slashing, no minimum, no custodial transfer) it pays for in yield: delegation is a conviction bet on ADA appreciation, not a yield-seeking decision."* At today's level the trade-off begins to bite — the 2.0 % yield sits below the USD risk-free rate (4.3 %) and at the bottom of the PoS chains' yield ladder, with only the S&P 500 dividend yield lower ([OPE.O9](diagnostic.html#132-mainnet-observations)). V2's design surface — *with* smart contracts and on-chain governance now in place — has the room to keep the maximally-flexible default *and* expose optional products that recover the yield premium for delegators willing to commit. That is the substantive shift this milestone proposes.

### 2.2.1. The three faces of the yield problem

The problem decomposes along three dimensions, each of which a candidate solution has to address jointly:

- **Competitive as an investment.** Staking competes for capital with DeFi, lending markets, and off-chain alternatives. If the absolute return is not attractive, rational capital migrates and the consensus layer loses the participation it depends on.
- **Rewarding the right operators.** Today the yield spread between balanced and hollow operators at equivalent pool sizes is **0.39 pp** — noise ([OPE.O5](diagnostic.html#132-mainnet-observations)). Half of all pool switches produce zero yield change ([CEN.O6](diagnostic.html#212-mainnet-observations)), and delegation follows visibility rather than yield ([OPE.O7](diagnostic.html#132-mainnet-observations)) — a signal-quality problem the mechanism has the surface to repair.
- **A product range frozen in 2020.** In Shelley's era no smart-contract capability existed — the only delegation product was, and still is, liquid delegation at a uniform yield. Plutus and the extended UTXO model now provide the infrastructure for a richer staking market that V2 has not yet exploited.

### 2.2.2. What smart contracts unlock — diversification and programmable pledge

The diversify direction is the operative content of this milestone — three product types that build above the baseline liquid-delegation default:

- **Lock-up tiers with differentiated APY.** Delegators who commit capital for a defined period (e.g. 6, 36, 73 epochs) accept reduced liquidity in exchange for a yield premium. The result is a **term structure** that rewards long-horizon commitment and stabilises the stake base single-pool operators depend on.
- **Liquid staking derivatives.** Smart-contract wrappers that issue transferable tokens representing staked ADA, letting delegators maintain liquidity (trade, lend, use as collateral in DeFi) while the underlying stake continues to earn rewards and contribute to consensus security. This is the product that brings capital currently parked in DeFi back into the staking pool.
- **Automated delegation strategies.** Programmable vaults that rebalance across pools according to defined criteria (yield optimisation, decentralisation weighting, entity-level quality scores), lowering the information and operational burden on individual delegators.

The baseline liquid delegation **remains**. These products build *above* it, so the delegation market offers a *spectrum of commitment–remuneration profiles* rather than a single undifferentiated choice. *Higher commitment — longer lock-up, less liquidity — earns a higher return.* That is the relationship through which the delegation market becomes a market in the economic sense: multiple products, multiple risk–return points, and a price signal that reflects the value of the commitment each delegator makes.

**Pledge handled as programmable commitment, not a binary cliff.** The current pledge mechanism's pledge-not-met cliff (the entire pool's rewards go to zero for the epoch — 2.1 % of the pot today, [POL.O1](diagnostic.html#122-mainnet-observations)) was the cleanest enforcement available with Shelley's certificate primitives. With a Plutus-based pledge layer built *on top of Milestone 1's reward-formula repair*, the same commitment can be expressed with **graduated rules** — proportional rewards, partial unwinds, time-vested attestations — and pledged capital can remain composable with the smart-contract ecosystem rather than being frozen out of it. The asymmetries that smart-contract primitives can resolve are documented in detail at [§1.2.4.3.2 — Delegating is inherently less constraining than pledging](diagnostic.html#12432-delegating-is-inherently-less-constraining-than-pledging) and [§1.2.4.3.4 — The pledge bonus is inoperative at realistic scale](diagnostic.html#12434-the-pledge-bonus-is-inoperative-at-realistic-scale).

**Constitutional alignment.** Tenet 4 (fair compensation) extends to delegators: participants who commit capital to consensus security are entitled to a return that reflects that contribution. Tenet 10 (monetary stability) constrains the obvious lever — raising `ρ` to compensate for declining real yield would inflate ADA against the long-term sustainability standard. Smart-contract-based instruments fit that constraint cleanly: they redistribute capital *behaviour* (lock-up window, programmable commitment) without inflating supply.

This milestone sequences after Milestone 1 because the active-player split (operators vs delegators) cannot be repaired at the delegator end while the operator end is still in the flat-fee corridor — any yield raise that doesn't first repair the operator-viability gap simply expands the regressive transfer the diagnostic documents ([OPE.O5](diagnostic.html#132-mainnet-observations)).

## 2.3. Milestone 3 — A Pool Alliance, rocket-pool-like for Cardano

This milestone outlines a concrete candidate solution along **two reinforcing steps** the diagnostic already lays out: make the production threshold explicit at the protocol level, and build a Rocket-Pool-like *Pool Alliance* below it so that enforcement opens a structural entry path rather than closing one. It addresses two of the 9 induced problems together:

- [μ02 — Guarantee operator viability](problem-statements.html#problem-1-3-3-1) — the production/viability threshold gap that today's lone entrant has to clear unaided;
- [μ04 — SPO (Supply-side) — fewer and fewer entities participate in consensus](problem-statements.html#problem-2-1-3-1) — the contraction of the single-pool operator base from 555 to 291 pools, while multi-pool fleets grew from 23 to 85 entities ([CEN.O1](diagnostic.html#212-mainnet-observations)).

### 2.3.1. Why the production threshold deserves reinforcing

The diagnostic shows that **1,987 of 2,718 pools (73 %) sit below the 95 %-block-probability bar at ~3 M ADA**: they collectively hold only 2.7 % of stake and produce blocks too sporadically to carry a meaningful consensus signal ([POL.O4](diagnostic.html#122-mainnet-observations)). The diagnostic's own framing is direct — this segment is *"ghost capacity"* and *"noise-dominated"*: pools that exist on-chain, draw operator and infrastructure effort, and muddy the pool marketplace for delegators, without contributing measurably to the security output. From the protocol's point of view, this is signal noise the network is paying for.

The diagnostic also names the underlying gap concisely: between registration and the production threshold lies a corridor the mechanism does not bridge — *"an open door that leads to an empty room"* ([§1.2.4.1.4](diagnostic.html#12414-the-sub-threshold-problem-what-rocket-pool-tells-us)). The intended-game narrative is explicit about what should be there instead: a new operator's entry should be *individually rational* and the path from new pool, to established pool, to fully committed pool should be a *legible arc* both operators and delegators can follow ([*The Intended Game* §3.2 — Operators from first pledge to full commitment](intended-game.html#32-operators-from-first-pledge-to-full-commitment)). The 73 % sub-block tail is the empirical record of what happens when participants try to walk that arc without scaffolding.

### 2.3.2. The two-step plan — make the threshold explicit, and build the Pool Alliance below it

**Step 1 — Make the production threshold explicit (`σ_min`).** Ethereum's Beacon Chain requires exactly **32 ETH** to activate a validator — an explicit threshold enforced at the protocol level. Cardano's production threshold is *implicit*, emergent from Poisson statistics rather than declared as a parameter. Promoting it to a declared minimum at the pool-registration boundary cleans the marketplace: pools below the threshold no longer register, the 73 % tail compresses, and delegators see a marketplace where every visible pool actually carries consensus weight.

The cleanup is sharp because the cost is concentrated: today **2,144 of 2,877 pools (75 %)** sit below the production threshold and together hold only **2.7 % of active stake** ([POL.O4](diagnostic.html#122-mainnet-observations)). The 2,146 pools removed from the visible marketplace carry **9.4 % of delegations** but **almost no stake-weight** — the delegations they hold are the micro-delegator residuals that today feed into noise. After enforcement, the marketplace shrinks from **~2,877 visible pools to ~731 productive pools**, every one of which produces ≥1 block per epoch with ≥95 % probability. The stake those 2,146 pools currently warehouse (~600 M ADA cumulatively) is freed to flow toward the productive set or, via the Pool Alliance below, toward new entrants on a structural growth path.

**Step 2 — Build the Pool Alliance below the threshold so enforcement opens a path.** Ethereum's Rocket Pool demonstrates this primitive at scale: a permissionless, decentralised liquid-staking protocol where an operator bonds as little as **4 ETH** alongside pooled capital from passive stakers, and a smart contract assembles a full 32 ETH validator — producing **~4 000 independent node operators** and **~800 K ETH staked** by participants who would never have crossed the solo-validator threshold alone ([§1.2.4.4.1](diagnostic.html#12441-enforce-the-production-threshold-build-a-rocket-pool-for-cardano)).

Adapted to Cardano's distinctive properties (no lockup, no slashing, no minimum stake for delegation), a **Pool Alliance** would expose the same primitive at the SPO entry path:

- an **operator bond** — a technically capable participant pledges what they can (the diagnostic offers ~100 K ADA as a working figure) and commits to running infrastructure; this is their skin-in-the-game, analogous to Rocket Pool's operator bond;
- **capital matching** — delegators who want to support decentralisation at a level above passive delegation contribute to the alliance, the pooled stake crosses the production threshold, the operator runs the pool;
- **shared infrastructure** — monitoring, key management, attestation tooling that today fall on the lone entrant become alliance-level services.

The two steps reinforce each other. Enforcing `σ_min` cleans the marketplace; the Pool Alliance ensures that enforcement opens a legitimate route rather than closing one. Together they recover what the intended-game calls the *"open seat at the deflationary table"* — a credible entry path for participants with skill and partial capital, so consensus participation no longer requires either pre-existing personal wealth or a custodial mandate.

> **A side note on technical complexity.** The two-step plan is straightforward to state but involves several non-trivial design decisions the next phase of work has to commit on: the `σ_min` enforcement model (block at registration vs continuous requirement with grace period), the Pool Alliance materialisation (native ledger primitive vs Plutus service layer vs hybrid), the migration path for the ~2,144 currently-registered sub-threshold pools, and — most consequentially — **the MPO-at-saturation question**.
>
> Under `σ_min`, an MPO whose pool saturates faces several new options where today they face essentially one. *Stop expanding* (the intended Sybil defence reactivated). *Commit fresh `σ_min` as genuine pledge per new pool* (real economic cost, no longer ~500 ADA per certificate). *Join the Pool Alliance with a smaller operator bond plus capital matching* (the legitimate sub-`σ_min` path). And a fourth candidate worth flagging: **register the new pool as an on-chain cellular division of the saturated one** — the saturation event itself becomes the moment at which the MPO declares an explicit entity link, the new pool inherits its lineage in the on-chain record, and the protocol gains the entity-level attribution it lacks today. The biological metaphor is the right one: cells divide *transparently*, with every daughter cell traceable to its parent. The same primitive turns the saturation event from an opaque fragmentation (today's pattern, where an entity registers a fresh pool with no on-chain link to the saturated one) into a transparent expansion.
>
> Read this way, **cellular division is more than a candidate primitive — it is a *pressure instrument* that reintroduces the notion of entity into the protocol**, incentive-compatible and without requiring either a constitutional amendment for new entity primitives or off-chain clustering. The MPO chooses to declare the entity link because the alternative (stop expanding, or commit a fresh `σ_min` of pledge per pool) is more costly. The mechanism's entity surface emerges incrementally from each legitimate growth act, declaration by declaration. The [entity-level research axis (§2.5.1)](#251-entity-level-awareness-the-supply-side-question) develops this further as a concrete protocol-level mechanism for entity awareness.
>
> Each option above is a real design question; together they map the technical layer this milestone has to resolve. They are flagged here as the next layer of work, not as blockers.

**Constitutional alignment.** Tenet 9 (fair treatment) is the central anchor: today's implicit capital threshold acts as a *de facto* barrier that excludes operators with skill but not capital, while custodial entities holding 21 % of productive stake clear it by virtue of their mandate ([OPE.O3](diagnostic.html#132-mainnet-observations)). Making the threshold explicit and pairing it with a structural sub-threshold path opens consensus participation along the inclusivity arc the intended-game describes, while removing the noise the residual sub-block tail injects into the security signal.

This milestone sequences after Milestone 1 because the alliance economics depend on the reward-distribution layer being repaired first — a Rocket-Pool-like collective layered on top of today's flat-fee corridor would mutualise the regressive cost rather than remove it. With the corridor closed by M1, the alliance becomes a structurally healthy entry path rather than a workaround for a corridor still in place.

## 2.4. Milestone 4 — Scale up with the non-participant population

This milestone takes up the **second face of [μ01](problem-statements.html#problem-1-2-3)** — the non-participant population that Milestone 1 deliberately leaves untouched: the 39.8 % of circulating supply outside delegation, of which only 0.37 % is reachable by reward-design changes alone ([CEN.O7](diagnostic.html#212-mainnet-observations)). The remaining 39.4 % sits in addresses that **cannot delegate without a protocol-level change** — exchange hot wallets, institutional cold storage, pre-staking-era legacy wallets, DeFi script addresses without staking parts.

The composition matters for what the milestone has to deliver. The 2.5 B residual is concentrated, not diffuse: 246 wallets hold 74 % of it, the top 10 hold 41.6 %. Re-engaging this pool is therefore not a retail-recruitment problem but a **protocol-architecture problem** with a small, identifiable counterparty list. Three protocol-level instruments shape the candidate solution space:

- enabling exchange-style and custodial address shapes to delegate;
- mandating staking-capable script standards in DeFi (a single 80 M-ADA contract holds 89 % of the DeFi-without-staking residual);
- introducing delegation-by-default for newly-minted wallets.

**Constitutional alignment.** Tenet 9 (fair treatment) has a less obvious application here: participants who hold ADA but cannot delegate by virtue of the address shape they were issued are *structurally excluded* from the rewards their capital underwrites — a discrimination by inheritance, not by behaviour. Closing that gap aligns the participation surface with the Constitution's standard.

This milestone is sequenced last among the microeconomic milestones for the reason the diagnostic spells out explicitly: expanding the participant pool *before* the active-player dynamics are repaired enlarges the existing concentration rather than diluting it. Once Milestones 1, 2, and 3 have set the active-player ground straight, scaling the participant base becomes a coherent move rather than a concentration-amplifier.

## 2.5. Research axis — reduce the concentration effects that distort both populations

This section is **a research axis**, not a committed milestone. The substantive question — *can the mechanism reduce the concentration effects that distort both sides of the staking market?* — is real and well-evidenced, but the candidate instruments need more analysis and design work before they can be promoted to a milestone with a specific direction.

The diagnostic documents concentration on **two fronts**:

- **Supply side.** **83 attributed entities** control **76.7 %** of productive stake through **449 productive pools** ([POL.O5](diagnostic.html#122-mainnet-observations)), while single-pool operators have contracted from 555 to 291 productive pools ([POL.O6](diagnostic.html#122-mainnet-observations)). The reward formula evaluates pools *independently* — it does not see that twenty pools share the same controller. Saturation, intended to prevent concentration, fragments *pools* but not *entities*.
- **Demand side.** **1,000 delegators (0.07 % of the base) control 57 % of staked ADA**; the Gini coefficient is **0.976** ([CEN.O3](diagnostic.html#212-mainnet-observations)). Concentration crystallised by epoch 300 and 9× population growth has not budged the top-1 % share.

Both concentrations are *structural*, both *crystallised early*, and *neither responds* to the current incentive design. Milestones 1–4 set up the conditions in which a deconcentration intervention becomes coherent — but they do not, in themselves, deliver it. That is the work this research axis names.

The **constitutional question** is part of why this is staged as a research axis rather than a milestone. As §1.3 of this analysis notes, the Constitution operates at the **pool level** — its guardrails govern pool parameters (`k`, `a_0`, `minPoolCost`), not entity-level or delegator-tier constructs. Reducing concentration can in principle be reached along three paths:

- **Within the existing perimeter** — a calibrated reward curve that makes pledge dilution across multiple pools carry real economic cost, working through the parameters the Constitution already approves.
- **Through constitutional evolution** — introducing entity-level primitives directly via Article IV amendment, recognising entities as first-class participants alongside pools.
- **Through incentive-compatible pressure instruments** — getting the protocol to entity awareness *organically*, by making entity declaration the natural cost of legitimate growth, without amending the Constitution. The **cellular-division candidate developed in [Milestone 3](#23-milestone-3-a-pool-alliance-rocket-pool-like-for-cardano)** is the canonical example: under `σ_min`, an MPO whose pool saturates can register a new pool only by declaring the entity link to the parent pool on-chain. The MPO chooses to declare because the alternative (stop expanding, or commit a fresh `σ_min` of genuine pledge per pool) is more costly. The mechanism's entity surface then emerges incrementally — declaration by declaration — from the operator lifecycle itself.

Choosing between these three paths — or combining them — is itself a design decision the research axis has to mature. The third path is particularly promising because it carries the lowest constitutional bar while still producing the entity-level attribution surface the protocol needs.

### 2.5.1. Entity-level awareness — the supply-side question

The reward formula's unit of accounting is the pool. The economic actor making strategic decisions is the *entity* — a cluster of pools sharing a common controller. An entity operating twenty pools with negligible pledge in each is **indistinguishable, at the formula level**, from twenty single-pool operators each pledging the same total.

This is the structural root of the Sybil-tax failure documented in [the multi-pool entity analysis](diagnostic.html#12443-multi-pool-operators-and-the-need-for-anti-monopoly-countermeasures): the marginal cost of an additional pool is roughly the certificate registration fee, while the marginal reward is a full share of the curve. The Sybil tax exists in the formula but is *inoperative* at the pool level. Reactivating it requires evaluating pledge, saturation, and reward-scaling at the entity level — directly via on-chain entity primitives, or indirectly via a reward curve calibrated so that pledge dilution across `n` pools carries a real economic cost.

Open research questions for this axis:

- **What does an on-chain entity primitive look like?** The existing owner-key registration provides one attribution surface; a richer primitive would let the protocol evaluate aggregate pledge, aggregate stake, and fleet structure at the entity level. One concrete candidate, surfaced in [Milestone 3's MPO-at-saturation discussion](#232-the-two-step-plan-make-the-threshold-explicit-and-build-the-pool-alliance-below-it), is **on-chain cellular division at the saturation event** — register a new pool as an explicit daughter of the saturated parent, so the entity tree is built incrementally from each legitimate expansion act. The framing matters: this is **a pressure instrument**, not a mandate. The protocol does not force MPOs to declare entities directly; it makes the declaration the natural cost of legitimate growth under `σ_min`, so the entity tree emerges organically as MPOs walk the lifecycle. *That is how the notion of entity gets reintroduced into the protocol — incentive-compatible, without a constitutional amendment for new primitives, and without relying on best-effort off-chain clustering.* The trade-off between attribution rigour and operator privacy is part of the open work.
- **Can the same outcome be approximated within the current pool-level perimeter?** A reward curve that makes pledge dilution costly per-pool (rather than cost-free) may approximate entity-level accounting through pool-level instruments alone — but the parameter space the existing `a_0` and `k` guardrails open has to be mapped against the empirical fleet structure to know whether the approximation is tight enough.
- **What does the saturation cap mean at entity level?** An entity-wide saturation ceiling, a graduated penalty for fleet expansion, or a cap on the number of fully-rewarded pools per entity — each is a different design point with different governance implications. The interaction with Milestone 1's `A(ν, π)` repair is also open: the four-move repair changes the gradient operators face per pool, which changes the calculus of fleet expansion.

The principle this axis preserves: **entities remain free to operate multiple pools.** The research is not about prohibiting fleets but about ensuring that the economic advantage of fleet expansion *decreases* rather than *increases* with fleet size — the opposite of today's regime.

### 2.5.2. Titan-tier differentiation — the demand-side question

The mechanism today treats a 32-ADA micro-delegation and a 50 M-ADA titan delegation **identically**: same proportional return, same per-ADA governance weight, no incentive differentiated by size, tenure, or governance engagement.

The diagnostic surfaces what the demand-side concentration looks like in motion. **Titan delegators** (1 M+ ADA) average **3.06 lifetime pool switches** against **0.67** for micro-delegators ([CEN.O5](diagnostic.html#212-mainnet-observations)). They hold ~11 B of 21.8 B staked ADA, but only **38 %** of their stake sits in loyal delegations: capital is *disproportionately mobile*. Yet that mobility does not produce competitive pressure — half of all switches produce zero yield change, and the only asymmetric signal driving redelegation is **pool size**, not commitment ([CEN.O6](diagnostic.html#212-mainnet-observations)). The population with the *power* to discipline operators has no structured *reason* to exercise it; the population the protocol depends on for *broad participation* receives no signal that its commitment matters.

Open research questions for this axis:

- **What does delegation-tier differentiation look like in practice?** Tenure-weighted yield, governance-participation rebates, titan-specific channels through Milestone 2's lock-up and liquid-staking-derivative products — these are candidate instruments, not yet committed. The interaction with [Milestone 2](#22-milestone-2-maintain-and-diversify-a-competitive-delegator-yield) is direct: M2 builds the product spectrum, this axis explores how to differentiate access across tiers.
- **How is titan governance influence channelled toward decentralisation?** A 50 M-ADA delegation is not merely a larger version of a 32-ADA delegation — it carries qualitatively different consequences for pool selection, operator viability, and Conway-era governance outcomes. Candidate instruments include delegation-weighted governance signals, transparency requirements for large delegations, and incentive structures that reward titans who spread capital across multiple single-pool operators rather than concentrating in a single fleet.
- **How does micro-delegation stay viable as a participation channel?** The median 32-ADA delegator earns ~0.64 ADA/yr in staking rewards — economically negligible, but the participation it represents is not. Any titan-tier instrument has to be designed without making micro-delegation more costly to express.

**Sequencing.** This research axis sits *after* Milestones 1–4 because every candidate instrument it might commit to depends on the active-player ground being repaired first. With pledge re-armed (M1), delegator yield diversified (M2), the productive threshold reinforced (M3), and the participant base grown coherently (M4), a deconcentration intervention finds the mechanism in the state where its effects are interpretable. Started earlier, the same intervention layered on top of today's distortions risks amplifying what it is meant to reduce.

# 3. Macro-economics — instrumentation, recalibration, and the path to auto-regulation

Where [§2 Microeconomics](#2-microeconomics-participant-incentives-and-market-structure) addresses the participant-level incentives that shape operator behaviour, pledge commitment, delegator yield, and market structure, **§3 Macro-economics addresses the system-level conditions that keep those participant-level incentives operating correctly through time**. Micro is *what the mechanism does at any given epoch*; macro is *how the protocol observes itself, anticipates drift, and recalibrates when conditions move*.

The Conway-era governance pipeline (2024) is the infrastructure V1 did not have: a community-driven process for adjusting parameters within constitutional guardrails. V2's macro chapter is, in large part, about **using that pipeline well** — equipping it with the instruments to see what the mechanism is doing, the triggers to act when it drifts, and the discipline to gradually retire manual intervention as the ecosystem matures.

The framing this chapter takes seriously: **Cardano is a mature blockchain, but the reward mechanism is not yet auto-regulating**. The path from today's heavy parameter inertia (`ρ`, `τ`, `a_0`, `k` unchanged since Shelley) to a self-regulating mechanism passes through a phase of **informed, governed interventionism** — and the work this chapter scopes is the instrumentation and recalibration discipline that makes that phase legible. As new protocol features land (Leios for throughput, tier-pricing for fee structure, the broader fee-economy expansion the M2 / Tx Submitter line addresses), the manual layer can lighten. Until they do, the dashboard and trigger discipline named below are the difference between a protocol that pilots itself with instruments and one that flies blind.

## 3.1. Milestone 1 — Reward System Extension — A Governance Dashboard for the System Properties & Populations

This milestone outlines a single, foundational macro instrument: **a governance dashboard that monitors the four player populations of the staking pipeline, anticipates structural drift, and triggers a community-driven recalibration process when defined conditions are crossed**. The dashboard is not itself a recalibration mechanism — Conway's parameter-update process already provides that. The dashboard is the *surveillance and trigger layer* that makes the recalibration process *informed* and *timely* rather than ad-hoc.

The four player populations the diagnostic surfaces — operators (Supply-side), delegators (Arbiter-side), submitters (Demand-side), non-participants — each have their own **structural KPIs**, their own **threat patterns**, and their own **recalibration parameters** the Conway pipeline can move. Pieces of this surveillance already exist across the ecosystem, and **the milestone is a structured extension of that foundation, not a replacement**:

- **[IntersectMBO's Cardano Governance Health Dashboard](https://gov-health.intersectmbo.org/)** — developed by the Governance Health Working Group (GHWG) under CIP-1694, it already operationalises a structured KPI framework across *Ada Holder Participation*, *DRep Activity*, and *SPO Participation*, with trend lines, drill-downs, and a system-status header. This is the closest existing analog to what the milestone proposes.
- **[SanchoNet's GovTool](https://gov.tools/)** — the testbed and operational interface for Conway-era governance actions, where DReps, committees, and ada holders coordinate.
- **Community-built pool and reward analytics** — [PoolTool](https://pooltool.io/), [AdaStat](https://adastat.net/), [Cexplorer](https://cexplorer.io/), the [Cardano reward calculator](https://github.com/cardano-foundation/cardano-reward-calculator) — that surface live pool-level metrics, performance trends, and reward projections, and form the de-facto observability layer SPOs and delegators already use.
- **The diagnostic this analysis is anchored on** is itself one such piece, run on demand from on-chain data with off-chain processing — a snapshot-style instrument rather than a continuous one.

What the milestone proposes is to **extend and consolidate that foundation along three complementary axes**: *(a)* extend the surveillance from the three governance-health dimensions to the **four player populations** the staking pipeline depends on (adding the demand-side / submitters and the non-participants explicitly); *(b)* tie each KPI to **named trigger conditions** that route to a defined community process when crossed, rather than leaving the signal as observation-only; and *(c)* align the surveillance with the V2 microeconomic milestones, so that what the dashboard watches is precisely what those milestones move. The work is consolidation and structured extension, not duplication.

**Constitutional alignment.** Tenet 10 (monetary stability) is the central anchor. *"The protocol shall not dilute or inflate ada in a manner that is inconsistent with the long-term sustainability and integrity of the ecosystem"* presupposes that the protocol can *observe* whether dilution is consistent with the standard. Without instrumentation, that observation is impossible — the standard is unenforceable in practice. The dashboard is the surface on which Tenet 10 becomes operational. The Conway-era governance pipeline, in turn, provides the legitimate path through which the dashboard's trigger conditions translate into action.

### 3.1.1. The four surveillance lines, and what each one watches

Each line corresponds to one of the four player populations and tracks the structural KPIs the diagnostic uses to evaluate the equilibrium the mechanism is producing. Where the [microeconomic milestones](#2-microeconomics-participant-incentives-and-market-structure) act on those equilibria, this milestone watches them.

- **Supply-side surveillance — operator viability and entity structure.** Tracks the productive-pool count, the sub-viability tail share, the median single-pool retail wage, the entity-level Herfindahl, and the share of saturation-scale MPOs holding non-zero pledge. Trigger conditions detect drift toward the patterns the [pledge-repair milestone (§2.1)](#21-milestone-1-repair-pledge-sustain-the-small-spo-base) closes (the flat-fee corridor, the broken pledge equilibrium) and the entity-concentration patterns the [§2.5 research axis](#25-research-axis-reduce-the-concentration-effects-that-distort-both-populations) tracks.
- **Arbiter-side surveillance — delegator yield and concentration.** Tracks the absolute delegator AYI (current ~2 % and falling), the yield spread between balanced and hollow operators (current 0.39 pp, target >1 pp from the [delegator-yield milestone (§2.2)](#22-milestone-2-maintain-and-diversify-a-competitive-delegator-yield)), the Gini of stake concentration, the delegation-tier participation rate (lock-up, liquid-staking-derivative adoption from §2.2), and the redelegation responsiveness signal.
- **Demand-side surveillance — fee economy and submitter base.** Tracks fee revenue as a share of the epoch pot (today ~0.19 %, the [induced-problem M02 / Tx Submitter line](problem-statements.html#problem-2-2-3) addresses growth), distinct fee-paying addresses per epoch, the script-vs-key submitter split, and the gap between current fee throughput and self-sufficiency.
- **Non-participant surveillance — outside-the-game dynamics.** Tracks the staking rate (today 60 %, falling), the addressable-vs-structural split inside the non-participant pool, and the rate at which protocol-level interventions from the [non-participant scale-up milestone (§2.4)](#24-milestone-4-scale-up-with-the-non-participant-population) actually re-engage capital.

Each line's KPIs feed two consumers: the **community process** (when a trigger fires, the relevant constituency is alerted to consider a recalibration), and **the diagnostic itself** (the dashboard becomes the running record of how the mechanism evolves epoch by epoch, replacing the snapshot-style diagnostics like the one this analysis is anchored on with a continuous instrument).

### 3.1.2. From governed interventionism to gradual auto-regulation

The dashboard is explicitly designed as a **transitional instrument**. The trajectory it serves has three phases:

- **Phase 1 — heavy governed interventionism (today and the V2 transition).** Parameters are static, the Conway pipeline is fresh, the dashboard does not yet exist. Manual community process carries the entire recalibration load. This is where the milestone starts.
- **Phase 2 — informed governed interventionism (after the dashboard lands).** The dashboard runs, triggers fire when conditions cross structural thresholds, the community process is alerted on a defined cadence rather than ad-hoc. The intervention is still manual but it is *informed* — proposals to move `ρ`, `τ`, `minPoolCost`, `a_0`, `k` come anchored on the surveillance evidence rather than on a generic argument.
- **Phase 3 — gradual auto-regulation (as Leios, tier-pricing, and the fee economy mature).** As new protocol features absorb load — Leios increases throughput and therefore the fee base, tier-pricing differentiates the fee economy, the microeconomic milestones reduce the dependency on monetary expansion — the manual layer can lighten. Some trigger conditions become *automatic recalibrations* within pre-agreed envelopes; others remain manual because they touch constitutional concerns. The dashboard remains the surveillance layer; the *intervention* layer increasingly retires.

**Cardano is a mature blockchain, but the reward mechanism is not yet auto-regulating.** This milestone names the transition path explicitly — and the dashboard is what makes Phase 2 (and eventually Phase 3) reachable. Started without instruments, the recalibration work either does not happen (the V1 inertia we have today) or happens reactively after damage. With the dashboard, the work happens preventively, on the structural thresholds the diagnostic has identified.

This milestone sits **somewhat in parallel** to the microeconomic milestones rather than after them — the surveillance plumbing can be built while the participant-level work is in progress, and the diagnostic instruments themselves are largely already prototyped (this analysis is anchored on them). The full *value* of the milestone, however, depends on the microeconomic milestones landing: a dashboard that surveils a static, unchanging mechanism is a less useful instrument than one that surveils a mechanism that has just been recalibrated and needs to be observed under its new behaviour.

## 3.2. Research axis — deflationist ADA and its volatility

This section bundles two macro induced problems whose candidate solutions are still in the design-question stage. Both bear directly on **Tenet 10 (monetary stability)**, and both share the same constraint: the valid design space is narrower than it first appears, because every candidate instrument has to remain consistent with long-term sustainability and *must not* be a stealth-inflationary lever in disguise. That is part of why the work belongs in the research-axis register rather than in a committed milestone.

The diagnostic frames both as open questions, not as failures the mechanism must repair. *"Pre-Conway, scarcity-as-only-lever was a forced choice — there was no on-chain governance pipeline to add complementary properties. Post-Conway, it is a design gap."* Closing the gap is what the design work this research axis names is for.

### 3.2.1. The deflationist promise — complementary monetary properties beyond finite supply

This research thread takes up [M03 — A deflationist ₳: what mechanisms can complement finite supply?](problem-statements.html#problem-3-1-1). The protocol's only deflationary property today is the **supply cap**. The diagnostic's reading is that the cap is *necessary but not sufficient*: appreciation in real terms requires demand growth to exceed supply growth, and demand for ADA is a function of on-chain utility (transaction throughput, DeFi activity, application adoption, institutional custody, speculative interest) — *none of which are protocol parameters*. The cap is a static scarcity lever; it does not, on its own, drive demand.

What V2 can usefully explore is a second class of monetary properties that *complement* the cap without inflating supply. Candidate families worth dedicated analysis:

- **Treasury operations as a demand-side lever.** The treasury accumulates ADA at rate `τ`. Treasury-funded ecosystem development (grants, infrastructure, application incentives) directly increases on-chain utility, which feeds back into ADA demand. The trade-off between treasury accumulation (a Tenet 10 sustainability concern) and treasury deployment (an ecosystem-growth lever) is itself a research question — and the post-Conway governance pipeline is the natural surface on which to make that trade-off explicit.
- **Targeted burn mechanisms.** Transaction-fee burn (à la EIP-1559), governance-triggered burn, or burn-on-specific-actions would make ADA structurally deflationary along a second axis beyond the cap. Each carries Tenet 10 implications, governance-design choices, and trade-offs against the fee economy the [Tx Submitter milestone work](problem-statements.html#problem-2-2-3) depends on.
- **Demand-side tokenomic instruments.** Programmable-pledge composability ([§2.2's smart-contract layer](#22-milestone-2-maintain-and-diversify-a-competitive-delegator-yield)), liquid-staking-derivative yield, ADA-as-DeFi-collateral integrations — each makes ADA more *useful*, increasing demand without touching supply. The interaction with the microeconomic milestones is direct.

Each is a design space, not a committed direction. Choosing among them — or combining them — is part of the work this research thread will mature.

### 3.2.2. Wiring governance to macro signals — recalibration against price observations

This research thread takes up [M04 — ₳/Fiat volatility: what instruments can wire governance to price observations?](problem-statements.html#problem-3-1-2). Whatever direction the ADA/fiat exchange rate moves, the mechanism today absorbs the consequence passively — there is no on-chain instrument that responds to price observations, redirects emission, or recalibrates fees against real-economy conditions.

The diagnostic articulates three macro conditions the reward pipeline's long-term viability requires, and they do not move independently:

- **operator and delegator real revenue must remain viable** (deflationary ADA price);
- **the fee input must grow** and the submitter population must expand;
- **the fiat cost of transacting must remain low enough** to keep activity on Cardano.

A rising ADA price preserves operator and delegator viability but raises the fiat cost of transacting, suppressing fee volume. A falling ADA price lowers the fiat cost of transacting but compresses operator and delegator real revenue. A stable ADA price satisfies neither extreme. *The ₳/fiat exchange rate is the hidden variable connecting all three, and the protocol today has no instrument to manage them.*

Pre-Conway, the absence of an instrument was forced. Post-Conway, the governance pipeline can wire one in — but the design choices are open:

- **Oracle integration.** What price oracles does the protocol trust, at what cadence, with what tolerance for transient noise versus structural moves? The integration boundary (native ledger feature vs Plutus-based service vs hybrid) is itself a design decision.
- **Trigger conditions for recalibration.** When does the protocol recalibrate — against what threshold, with what governance approval bar, with what cadence? The dashboard from [§3.1](#31-milestone-1-reward-system-extension-a-governance-dashboard-for-the-system-properties-populations) is the surface on which trigger conditions get evaluated; this thread asks what *macro-signal* triggers belong on that surface.
- **Treasury-funded volatility absorption.** Treasury support for operators during sustained ADA-price downturns is a frequently-cited candidate. The trade-off between treasury size, deployment scope, and Tenet 10 monetary-stability constraints is the design question.
- **Price-feedback components in the emission curve.** Adjusting `ρ` against price observations under defined trigger conditions is the most direct candidate. It interacts both with §3.2.1's deflationist work (any emission adjustment is also a deflationist lever) and with Tenet 10's sustainability boundary.

Each is a design space, not a committed direction. The interaction with §3.2.1 is direct: any volatility instrument has to be consistent with the deflationist framing, and any deflationist instrument has to be robust across the volatility range.

**Interaction with [Milestone 1 (the governance dashboard)](#31-milestone-1-reward-system-extension-a-governance-dashboard-for-the-system-properties-populations).** The dashboard is the natural surface on which deflationist and volatility instruments would be observed *if* they were eventually deployed. Building the dashboard early — even before the M03 / M04 candidate solutions mature — pays off twice: first as the surveillance layer the recalibration discipline rests on, and second as the observation layer any future macro instrument has to be evaluated against. The same KPIs the dashboard tracks (staking rate, fee-revenue share, operator real wage in fiat terms) are the inputs that make this research thread evaluable in the first place.

> **Status:** Ideation in progress, started 2026/05/08. This page is the canonical V2 working document — directions of exploration and milestones offered for community shaping, anchored on the 9 induced problems.
