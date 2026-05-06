# Welcome — The Cardano Reward System V2

You are on the **landing page** of a working website that gathers, in one place, **the analysis, the evidence, and the recommendations** for an upcoming revision of Cardano's reward mechanism.

This work is being conducted by the **Cardano Business Unit (CBU)** within <img class="iog-logo-inline" src="assets/iog-full-logo-white.png" alt="Input | Output Group" />. The aim: give the Cardano community a shared empirical and analytical foundation against which any proposal can be evaluated on common ground.

The body of work has a name: <img class="cardano-logo-inline" src="assets/cardano/cardano-logomark-white.svg" alt="Cardano" /> **Cardano Reward System V2**.

It is **not yet a deployed mechanism, nor a finalised proposal**. It is a *new specification* we are authoring — one that defines what a successor to today's reward mechanism must satisfy. The site you are on is where that specification, the evidence behind it, and the analysis around it all live.

<div class="intro-video-card" markdown="1">
<div class="intro-video-card-frame">
<div class="intro-video-card-icon" aria-hidden="true">▶</div>
<div class="intro-video-card-text">
<div class="intro-video-card-label">Presentation video — coming soon</div>
<div class="intro-video-card-sub">A walkthrough of the diagnostic findings, the V2 milestones, and the directions in ideation will be embedded here. Until then, the document index below is a complete substitute.</div>
</div>
</div>
</div>

## Table of Contents

- [1. Why this work exists](#1-why-this-work-exists)
- [2. What you'll find here — a tour of the five parts](#2-what-youll-find-here-a-tour-of-the-five-parts)
  - [2.1. The Intended Game — what V1 was meant to produce](#21-the-intended-game-what-v1-was-meant-to-produce)
  - [2.2. Mainnet Diagnostic — the empirical foundation](#22-mainnet-diagnostic-the-empirical-foundation)
  - [2.3. V2 Specification — the destination](#23-v2-specification-the-destination)
  - [2.4. Existing CIPs — what's already on the governance table](#24-existing-cips-whats-already-on-the-governance-table)
  - [2.5. What's next? — you are here](#25-whats-next-you-are-here)
- [3. Looking ahead — three directions in ideation](#3-looking-ahead-three-directions-in-ideation)
  - [3.1. Direction 1 — Micro-economic re-alignment of the reward distribution](#31-direction-1-micro-economic-re-alignment-of-the-reward-distribution)
  - [3.2. Direction 2 — Pool alliances to concentrate the productive population](#32-direction-2-pool-alliances-to-concentrate-the-productive-population)
  - [3.3. Direction 3 — Macroeconomic shields against ADA price volatility](#33-direction-3-macroeconomic-shields-against-ada-price-volatility)
- [4. References](#4-references)

## 1. Why this work exists

Cardano's reward mechanism is the rule that decides, every five days, how newly-minted ADA is shared among the participants who keep the network running — the **stake-pool operators** who produce blocks, and the **delegators** who back them with their stake.

Those rules were written in **2019** and went live in **August 2020**. Only a handful of individual parameters have been adjusted since — notably the `k: 150 → 500` raise of August 2020 and the `minPoolCost 340 → 170` halving in October 2023. The **underlying design** of the reward formula has **never been revisited**.

For most of that period the surrounding protocol was unfinished:

- Smart contracts had not yet arrived.
- There was no on-chain governance to adjust anything.
- The fee-paying economy that smart contracts would later generate did not exist.
- The reserve from which rewards are minted was large enough that long-term sustainability could be postponed.

The mechanism was, in effect, **calibrated for a simpler chain** — governed off-chain, with a single kind of participant, and a runway measured in decades.

#### Five years of on-chain evidence tell a different story.

- The operator population has **stratified into a thin viable tier and a long non-viable tail**.
- **Pledge** — the personal ADA an operator commits to their own pool, designed as the central signal of skin in the game — has become **functionally irrelevant** for most of the network.
- Block production has drifted toward a handful of **concentrated multi-pool entities**, while billions of ADA sit outside consensus, held by accounts that cannot or do not stake.
- The reserve is **depleting on the mathematical schedule set in 2019**, with no transition plan for the moment it runs out.

These outcomes are not parameters tuned to the wrong value. They are **structural consequences of rules designed for a chain, a population, and an institutional context that no longer exist**.

#### What this site does about it.

Three things, in order:

- **Documents the drift** rigorously, layer by layer, against on-chain evidence.
- **Evaluates the proposals** already on the governance table against the same evidence.
- **Recommends a path forward** — gradual, principled, and grounded in what the evidence actually supports.

## 2. What you'll find here — a tour of the five parts

The website is organised into **five entry points**, each reachable from the navigation bar at the top.

Read the navbar **right-to-left** following the arrows — it mirrors the analytical flow from design intent, to empirical reality, to specification, to evaluation, to next steps.

### 2.1. The Intended Game — what V1 was meant to produce

Before the diagnostic, before V2 — there is the **design baseline** itself. **[The Intended Game](intended-game.html)** is a plain-prose narrative we authored to fill a gap in the original V1 design literature.

The two foundational design papers — *Reward Sharing Schemes for Stake Pools* (Brünjes & Kiayias et al., 2020) and the *SL-D1* specification (Kant, Brünjes & Coutts, 2019) — prove the mathematical properties of the reward curve and translate them into protocol formulas. **Neither tells the story of the game the mechanism is meant to produce** — who plays, why they enter, how they progress, and what equilibrium the system is supposed to converge toward. This document is an attempt to supply that missing baseline.

It covers:

- **Three player classes** locked in a strict dependency chain — transaction submitters, operators, delegators — each entering with a different motivation and a different strategic instrument.
- **Two pillars of the security model** — pledge as the operator's commitment bond, liquid delegation as the community's continuous approval signal.
- **The self-reinforcing cycle** the design intends to produce when all three trajectories function as expected.

The Intended Game is the **normative reference** the Mainnet Diagnostic measures every divergence against, and the design objective the V2 Specification reasons toward.

**→ Read this first** if you want the design baseline before reading what mainnet actually does.

### 2.2. Mainnet Diagnostic — the empirical foundation

A multi-stage observatory of Cardano's reward pipeline as it actually behaves on mainnet today, answering four operational questions:

- **Who participates?**
- **Where does stake concentrate?**
- **How is the epoch pot distributed at each stage?**
- **How does operator income compare to delegator yield?**

The diagnostic is a *new analytical artifact* we authored on top of five years of on-chain data. It surfaces the **structural problems** any successor mechanism must address — each grounded in observation, not theory.

**→ Start here:** [The Diagnostic](diagnostic/README.md).

The four sub-reports drill down into:

- **[The staking census](diagnostic/sub-flows/census/mainnet-analysis/README.md)** — who the participants are.
- **[Reserves & pool pots](diagnostic/sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md)** — how the epoch budget is assembled.
- **[The pools-distribution layer](diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md)** — how reward is allocated across pools.
- **[The operator/delegator split](diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md)** — how a pool's reward is divided between its operator and its delegators.

The induced problem statements derived from the evidence are summarised in [Induced Problems](problem-statements.html).

### 2.3. V2 Specification — the destination

The [V2 Specification](v2-spec.md) is a *new document* we authored, sitting alongside the diagnostic.

It names the **eight milestones** the next reward mechanism must deliver, split across two layers.

**Microeconomics** — participant incentives and market structure:

- [Operator Viability](v2-spec.md#31-guarantee-operator-viability-across-the-entire-productive-population)
- [Pledge](v2-spec.md#32-restore-the-notion-of-pledge-among-operators)
- [Delegator Yield](v2-spec.md#33-maintain-and-diversify-a-competitive-delegator-yield)
- [Deconcentration](v2-spec.md#34-reduce-the-concentration-effects-that-distort-both-populations)

**Macroeconomics** — system sustainability and governability:

- [Pot Survival](v2-spec.md#41-the-staking-pot-must-survive-reserve-depletion)
- [Fee Policy](v2-spec.md#42-the-fee-generating-population-must-expand)
- [Price Robustness](v2-spec.md#43-the-mechanism-must-function-across-a-range-of-ada-price-scenarios)
- [Recalibration Pipeline](v2-spec.md#44-the-mechanism-must-be-governable)

Each milestone is a **problem paired with a measurable acceptance criterion**.

The spec **does not prescribe** a new reward curve, new parameter values, or a specific implementation. It defines the **outcomes** any successor must achieve.

The aim is **common ground** on which candidate designs can be proposed, compared, and evaluated against the same yardstick — rather than debated in the abstract.

### 2.4. Existing CIPs — what's already on the governance table

A **Cardano Improvement Proposal (CIP)** is the standard format the Cardano community uses to propose changes to the protocol.

Four reward-related CIPs were drafted *before* this diagnostic was performed and are still on the governance table today:

- **[CIP-0023](solution-evaluation/operator-delegator/cip-0023.md)** — Fair Min Fees
- **[CIP-0037](solution-evaluation/pools-distribution/cip-0037.md)** — Dynamic Saturation Based on Pledge
- **[CIP-0050](solution-evaluation/pools-distribution/cip-0050.md)** — Pledge Leverage-Based Staking Rewards
- **[CIP-0082](solution-evaluation/operator-delegator/cip-0082.md)** — Improved Rewards Scheme Parameters

Each has been evaluated against the V2 milestones along the same nine-tier pool taxonomy and n-MPO operator-fleet brackets the diagnostic uses.

**→ Read the synthesis:** [Intro & Conclusion of the 4 CIPs](solution-evaluation/README.md).

**Verdict: bundle no-go.** Each candidate puts its instrument on the wrong layer; the mechanical effects regress on milestones the candidates do not target.

The cumulative read in [§3 Conclusion](solution-evaluation/README.md#3-conclusion) names the layer-misuse pattern that ties the bundle together.

### 2.5. What's next? — you are here

The directions we are exploring for V2 — three lines of analytical work, presented in [§3 below](#3-looking-ahead-three-directions-in-ideation) as exploratory thinking rather than committed deliverables.

## 3. Looking ahead — three directions in ideation

Three directions frame the broader scope V2 may eventually need to address. They are shared here to give the community visibility into the analytical work in motion — *as exploratory thinking, not as commitments*. **No priority, sequencing, or timing has been set across them**; the depth of analysis simply reflects how mature each line of thinking is today.

### 3.1. Direction 1 — Micro-economic re-alignment of the reward distribution

This package addresses the **microeconomic foundations** of the reward distribution: what each pool earns, how that reward is split between the operator and the delegators, and how the unused pledge-bonus budget can be put back to work.

Four moves on the reward-distribution layer, applied in sequence:

- **Repair `A(ν, π)`** — the bonus function that controls how a pool's reward depends on its size (ν) and pledge ratio (π). Today's `A` makes pledging a dominated strategy at most operator sizes; the repair restores a meaningful gradient.
- **Reduce `λ_size`** — the weight on the size axis in the reward envelope — so the *commitment* axis carries more of the signal and the *size* axis carries less. The size-weight cut also funds the next move.
- **Open a new `λ_viability` sub-budget** — a three-way envelope split (`λ_size + λ_pledge + λ_viability`), **without raising the total pool pot**. Funded by the `λ_size` reduction; conditional access tied to a pledge rule to be specified.
- **Activate the `λ_pledge` budget** that has been underused for years — POL.O1.F3 documents 95.6 % of it already returns to reserve unused (the single largest addressable inefficiency in the system). *Not new ADA — unused ADA already inside the envelope.*

The path is **gradual** by design: repair the formula bottleneck first, let the pledge signal recover *with* the operator population (not against it), and only then revisit pool-count expansion or stake-cap instruments. A radical hard cap on top of today's regime would, by contrast, send an even larger share of the pool pot back to the reserve and worsen viability for every SPO segment at once.

→ Detailed thinking in [§4 of the Existing CIPs evaluation](solution-evaluation/README.md#4-recommendations-on-adjustments-to-the-current-mechanism).

### 3.2. Direction 2 — Pool alliances to concentrate the productive population

A second direction we are exploring would let stake-pool operators **federate** — pooling their pledge, infrastructure, and brand into shared structures. The motivation: many of today's small productive pools sit individually below the consensus and economic viability thresholds. Rather than seeing them attrition out one by one, the protocol could enable them to **combine into alliances** that, together, clear the productive bar.

The reference design point is the kind of pool-of-pools / staking-DAO model already in production on other chains (Rocket Pool on Ethereum is the canonical example). Translating that pattern to Cardano's Praos consensus, pledge mechanics, and identity model is non-trivial — and is the work that would sit behind this milestone if it is prioritised.

This is a **structural addition to V2**, not a parameter change.

### 3.3. Direction 3 — Macroeconomic shields against ADA price volatility

A third direction is the **macroeconomic resilience** of the reward mechanism against ADA price shocks. The current reward formula is denominated in ADA at every stage, so participants experience their income in fiat terms — and the effective compensation for running infrastructure, or for delegating stake, swings with the ADA / USD rate.

The V2 specification already names *Price Robustness* as one of its eight milestones; this package would turn that milestone into **instrumented tooling**: hedging mechanisms, fee-revenue smoothing, treasury-side stabilisers — concrete instruments that absorb price shocks rather than passing them straight through to the participant population.

This is a **macroeconomic line of thinking** that would complement the microeconomic re-alignment in Direction 1.

## 4. References

- **[V2 Specification](v2-spec.md)** — eight milestones and the constitutional framework.
- **[Mainnet Diagnostic](diagnostic/README.md)** — observation, problem statements, and per-layer sub-reports.
- **[The Intended Game](intended-game.html)** — plain-prose companion to the formal SL-D1 design specification, on what the original V1 was meant to produce and where the equilibrium drifted.
- **[Existing CIPs — Intro & Conclusion](solution-evaluation/README.md)** — evaluation of the current proposal bundle and the analytical directions discussed in §4.
- **[Induced Problems](problem-statements.html)** — Cardano Problem Statements (CPSs) in formation, derived from the diagnostic.

> **Status:** Active 2026/05/06. Landing page of the Cardano Reward System V2 working website.
