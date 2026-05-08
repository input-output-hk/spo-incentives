# Welcome — The Cardano Reward System V2

This is the working website for <img class="cardano-logo-inline" src="assets/cardano/cardano-logomark-white.svg" alt="Cardano" /> **Cardano Reward System V2** — a new specification, in ideation, for a successor to today's reward mechanism. The work is being conducted by the **Cardano Business Unit (CBU)** within <img class="iog-logo-inline" src="assets/iog-full-logo-white.png" alt="Input | Output Group" />. The aim: give the Cardano community a shared empirical and analytical foundation against which any proposal can be evaluated on common ground.

V2 is **not yet a deployed mechanism, nor a finalised proposal**. This site gathers, in one place, the analysis, the evidence, and the directions in ideation that feed the specification effort.

<div class="intro-video-card" markdown="1">
<div class="intro-video-card-frame">
<div class="intro-video-card-icon" aria-hidden="true">▶</div>
<div class="intro-video-card-text">
<div class="intro-video-card-label">Presentation video — coming soon</div>
<div class="intro-video-card-sub">A walkthrough of the diagnostic findings, the V2 Roadmap milestones, and the directions in ideation will be embedded here. Until then, the document index below is a complete substitute.</div>
</div>
</div>
</div>

## Table of Contents

- [1. Why this work exists](#1-why-this-work-exists)
- [2. Tour of the site](#2-tour-of-the-site)
- [3. References](#3-references)

## 1. Why this work exists

Cardano's reward mechanism — the rule that decides every five days how newly minted ADA is shared between the **stake-pool operators** who produce blocks and the **delegators** who back them with their stake — was written in **2019** and went live in **August 2020**. Only a handful of individual parameters have been adjusted since (notably the `k: 150 → 500` raise of August 2020 and the `minPoolCost: 340 → 170` halving in October 2023). The underlying design of the reward formula has **never been revisited**.

The mechanism was, in effect, calibrated for a simpler chain — governed off-chain, with a single kind of participant, no smart contracts, no fee-paying economy, and a reserve large enough that long-term sustainability could be postponed.

#### Five years of on-chain evidence tell a different story.

- The operator population has **stratified into a thin viable tier and a long non-viable tail**.
- **Pledge** — the personal ADA an operator commits to their own pool, designed as the central signal of skin in the game — has become **functionally irrelevant** for most of the network.
- Block production has drifted toward a handful of **concentrated multi-pool entities**, while billions of ADA sit outside consensus, held by accounts that cannot or do not stake.
- The reserve is **depleting on the mathematical schedule set in 2019**, with no transition plan for the moment it runs out.

These outcomes are not parameters tuned to the wrong value. They are **structural consequences of rules designed for a chain, a population, and an institutional context that no longer exist**.

#### What this site does about it.

Three things, in order: **document the drift** rigorously, layer by layer, against on-chain evidence; **evaluate the proposals** already on the governance table against the same evidence; and **carry a path forward** into the V2 Roadmap.

## 2. Tour of the site

The navigation bar at the top is organised **right-to-left**, mirroring the analytical flow from design intent → empirical reality → roadmap → evaluation → welcome.

- **[The Intended Game](../the-intended-game/README.md)** — what V1 was meant to produce. Plain-prose companion to the formal SL-D1 design specification, authored to fill a gap in the original V1 design literature: *who plays, why they enter, how they progress, and what equilibrium the system is supposed to converge toward*.
- **[Mainnet Diagnostic](../diagnostic/README.md)** — five years of on-chain evidence, layer by layer (Treasury & Pool-Pots, Pools-Distribution, Operator-Delegator split, Staking Census). Surfaces the **[9 induced problems](../generated-website/problem-statements.html)** any successor mechanism must address — five micro (μ01–μ05) and four macro (M01–M04), each grounded in observation rather than theory.
- **[V2 Roadmap](../README.md)** — directions of exploration and concrete milestones offered for community shaping, anchored on the 9 induced problems. Priority logic: *root causes before scale-up*.
- **[Existing CIPs against the 9 induced problems](../solution-evaluation/README.md)** — the four pre-existing reward CIPs ([CIP-0023](../solution-evaluation/operator-delegator/cip-0023.md), [CIP-0037](../solution-evaluation/pools-distribution/cip-0037.md), [CIP-0050](../solution-evaluation/pools-distribution/cip-0050.md), [CIP-0082](../solution-evaluation/operator-delegator/cip-0082.md)) evaluated against the same evidence. Bundle no-go; the four-move *gradual* alternative carried forward into Roadmap Milestone 1.
- **Welcome** — you are here.

## 3. References

- **[V2 Roadmap](../README.md)** — the canonical V2 working document.
- **[Mainnet Diagnostic](../diagnostic/README.md)** — observation, problem statements, and per-layer sub-reports.
- **[Induced Problems](../generated-website/problem-statements.html)** — the 9 structural problems the diagnostic surfaces (μ01–μ05 + M01–M04).
- **[The Intended Game](../the-intended-game/README.md)** — plain-prose companion to the formal SL-D1 design specification.
- **[Existing CIPs — Intro & Conclusion](../solution-evaluation/README.md)** — evaluation of the current proposal bundle and the analytical directions discussed in §4.

> **Status:** Active 2026/05/08. Landing page of the Cardano Reward System V2 working website.
