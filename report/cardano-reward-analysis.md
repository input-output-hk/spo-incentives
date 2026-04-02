# Cardano Reward Pipeline: From Design Intent to Mainnet Reality

# Motivation

The *Shelley-era Delegation and Incentives Design Specification* (SL-D1) defined the economic rules that were meant to guide Cardano toward a stable, decentralized equilibrium of $k$ well-funded stake pools.
Five years of mainnet operation have exposed significant divergences between those design intentions and the on-chain reality.
The *Analysis of Cardano's Incentive Mechanism* (Lopez de Lara, 2025; hereafter the *Incentive Mechanism Analysis*) documented the key findings empirically: a stratified equilibrium with 873 active operators below the 3M ADA viability threshold, a pledge mechanism that is functionally irrelevant for most pools, and a capital-constrained environment where ~16B ADA remains outside consensus.

This document decomposes the SL-D1 reward pipeline into three stages and, for each stage, follows the same analytical arc: describe the intended design, confront it with mainnet observations, synthesise the observations into a *problem statement*, and verify whether a formal *Cardano Problem Statement* (CPS) exists for that problem in the CIP governance process. Where a CPS exists, the document evaluates the CIPs proposed as solutions against it. Where no CPS exists, the document identifies the gap and produces one.

Each pipeline stage is backed by a dedicated sub-report containing the formula derivations, mainnet observations, and empirical evidence that grounds the corresponding CPS.

# Table of Contents

- [1. Treasury & Pool Pots Distribution](#1-treasury--pool-pots-distribution)
  - [1.1 Flow Overview](#11-flow-overview)
  - [1.2 Mainnet Observations](#12-mainnet-observations) 
  - [1.3 Problem Induction → Funding the Protocol Without a Reserve](#13-problem-induction--funding-the-protocol-without-a-reserve)
- [2. Pools Distribution](#2-pools-distribution)
  - [2.1 Flow Overview](#21-flow-overview)
  - [2.2 Mainnet Observations](#22-mainnet-observations)
  - [2.3 Problem Induction → Closing the Consensus Incentive Gap](#23-problem-induction--closing-the-consensus-incentive-gap)
  - [2.4 The Divergent Operator Experience](#24-the-divergent-operator-experience)
    - [2.4.1 Entry — below 1M ₳, too committed to just delegate, too small to operate](#241-entry--below-1m--too-committed-to-just-delegate-too-small-to-operate)
      - [2.4.1.1 The structural floor](#2411-the-structural-floor)
      - [2.4.1.2 A gate with no sign](#2412-a-gate-with-no-sign)
      - [2.4.1.3 Capital over competence](#2413-capital-over-competence)
      - [2.4.1.4 A gap worth exploring](#2414-a-gap-worth-exploring)
    - [2.4.2 Progression — balanced as intended, but private by design](#242-progression--balanced-as-intended-but-private-by-design)
      - [2.4.2.1 The three strategies](#2421-the-three-strategies)
        - [2.4.2.1.1 The common endgame — saturate, then become an MPO](#24211-the-common-endgame--saturate-then-become-an-mpo)
        - [2.4.2.1.2 The degree of freedom](#24212-the-degree-of-freedom)
        - [2.4.2.1.3 The balanced strategy](#24213-the-balanced-strategy)
        - [2.4.2.1.4 The private strategy](#24214-the-private-strategy)
        - [2.4.2.1.5 The hollow strategy](#24215-the-hollow-strategy)
      - [2.4.2.2 Why balanced should be the intended equilibrium](#2422-why-balanced-should-be-the-intended-equilibrium)
      - [2.4.2.3 The current design incentivises the private strategy](#2423-the-current-design-incentivises-the-private-strategy)
    - [2.4.3 Endgame — the hollow strategy is the dominant one](#243-endgame--the-hollow-strategy-is-the-dominant-one)
      - [2.4.3.1 What mainnet reveals](#2431-what-mainnet-reveals)
      - [2.4.3.2 Delegating is inherently less constraining than pledging](#2432-delegating-is-inherently-less-constraining-than-pledging)
      - [2.4.3.3 The reward structure weights size, not commitment](#2433-the-reward-structure-weights-size-not-commitment)
      - [2.4.3.4 The pledge bonus is inoperative at realistic scale](#2434-the-pledge-bonus-is-inoperative-at-realistic-scale)
      - [2.4.3.5 The size-visibility-delegation loop](#2435-the-size-visibility-delegation-loop)
      - [2.4.3.6 The inversion](#2436-the-inversion)
  - [2.5 Proposed Solutions Evaluation](#25-proposed-solutions-evaluation)
    - [2.5.1 CIP-0050 — Pledge Leverage Cap](#251-cip-0050--pledge-leverage-cap)
    - [2.5.2 CIP-0037 — Dynamic Pledge-Linked Saturation](#252-cip-0037--dynamic-pledge-linked-saturation)
- [3. Operator / Delegator Distribution](#3-operator--delegator-distribution)
  - [3.1 Flow Overview](#31-flow-overview)
  - [3.2 Formulas](#32-formulas)
    - [3.2.1 SL-D1 (Original)](#321-sl-d1-original)
    - [3.2.2 Residual split decomposition](#322-residual-split-decomposition)
    - [3.2.3 Reader-Friendly](#323-reader-friendly)
  - [3.3 Structural Decomposition](#33-structural-decomposition)
  - [3.4 Mainnet Observations](#34-mainnet-observations)
  - [3.5 Problems](#35-problems)
  - [3.6 Prior Art & Cited Solutions](#36-prior-art--cited-solutions)
  - [3.7 CIP Evaluation: Fee Structure Adjustments](#37-cip-evaluation-fee-structure-adjustments)
    - [3.7.1 CIP-0023 — Fair Min Fees](#371-cip-0023--fair-min-fees)
    - [3.7.2 CIP-0082 — Improved Rewards Scheme](#372-cip-0082--improved-rewards-scheme)
- [Sub-reports](#sub-reports)

# 1. Treasury & Pool Pots Distribution

## 1.1 Flow Overview

Before any individual pool receives rewards, the protocol must first answer one question:
**how much ADA is available for distribution this epoch?**

This stage assembles the **epoch pot** from three on-chain sources — transaction fees, non-refundable deposits, and a monetary expansion draw from the reserve — then splits it in two: a fixed share goes to the **treasury**, and the remainder becomes the **pools pot**, the total budget that the next stage (§2) will distribute across individual pools.

Two design choices embedded at this stage matter for the rest of the analysis:

- **Cooperative-behavior gate.** The monetary expansion draw is scaled by the ratio of blocks actually produced to blocks expected. If pools collectively miss slots, the entire epoch pot shrinks. This discourages sabotage but also means the pot depends on aggregate network health.

- **Fixed split rule.** The treasury/pools ratio is a protocol constant ($\tau$), not a function of network activity or reserve level. It does not adapt as the balance between fees and expansion shifts over time.

> **Formulas.** The epoch-pot assembly and treasury/pools split formulas — from the original SL-D1 notation through a reader-friendly rewrite to mainnet parameterization — are in the dedicated sub-report: [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) — §2.1.

## 1.2 Mainnet Observations

The epoch-level analysis (epochs 208–617) yields four observations at this pipeline stage. The full data, visuals, and methodology are in the dedicated sub-report: [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md).

| # | Observation | Summary |
| --- | --- | --- |
| **O1** | **The epoch pot is a single-source budget** | Monetary expansion provides ~99.8% of the pot. Fees cover ~0.19%; self-sufficiency would require 12–16× current capacity. Block production is reliable (η ≈ 0.977). |
| **O2** | **The reserve has crossed its half-life** | Reserve is half-depleted (13.29B → 6.53B ADA) in 5.5 years. Significant reward pressure expected at epochs 1000–1200 (~2028–2029). |
| **O3** | **The reward mechanism operates at ~44% of its potential** | Only ~6.8M of ~15.5M ADA pools pot reaches operators/delegators — the rest returns to reserve. 4.55B ADA cumulative (~70% of current reserve) exists because of this. Root cause: ~17B ADA (~44%) does not participate in delegation. |
| **O4** | **Reward parameters have never been adjusted** | $\rho = 0.3\%$ and $\tau = 20\%$ are unchanged since Shelley. Neither has been subject to a governance proposal. |

> **Scope note.** Observations O1–O4 are structural to the epoch-budget layer. No existing CIP targets this stage — they all operate downstream (§2, §3). These observations document the sustainability context within which all downstream proposals operate.

## 1.3 Problem Induction → Funding the Protocol Without a Reserve

Each observation above constrains what the system can do. Read together, they reveal what it *cannot* do.

The epoch pot is funded almost entirely by monetary expansion from the reserve (O1). That reserve is finite and has already crossed its half-life (O2). Transaction fees — the only sustainable alternative — cover ~0.19% of the pot today, and even at full realistic throughput would reach only ~1.3% (O1). Closing this gap requires 12–16× today's capacity, implying both a throughput upgrade (Leios) and a structural increase in transaction demand — neither of which is on a defined timeline. Meanwhile, the two parameters governing the draw ($\rho$, $\tau$) have never been reviewed since Shelley launch (O4), and no governance process exists to do so.

These constraints compose into a single structural problem: **the reward system has no viable path from reserve-funded to fee-funded sustainability.** The reserve is depleting on a known schedule, the only alternative revenue source is orders of magnitude too small, and the parameters governing the transition have never been subject to governance. This is not a failure of any individual parameter — it is a *design gap* at the epoch-budget layer. No protocol-level or governance-level instrument currently exists to manage this transition.

O3 — the ~44% distribution efficiency — is not a problem *at this layer*. It is a consequence of participation levels, which are shaped by incentives defined downstream (§2, §3). But it interacts directly with the sustainability problem: activating inactive ADA would improve distribution efficiency while accelerating reserve consumption. Any solution to the epoch-budget problem must account for this tension — and any change to the downstream incentive structure (§2, §3) that affects participation will feed back into reserve dynamics here.

**CPS identified.** No *Cardano Problem Statement* (CPS) has been formally written for this problem. The CIP governance process requires that solutions (CIPs) be scoped against a well-defined problem statement (CPS). This foundational sustainability problem has remained formally unstated. This analysis identifies the gap and produces the missing CPS — *Funding the Protocol Without a Reserve* — derived from the mainnet evidence in the dedicated [sub-report](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) and defined in [`sub-flows/treasury-and-pool-pots-distribution/cps/`](sub-flows/treasury-and-pool-pots-distribution/cps/).

The epoch budget sets the ceiling for everything that follows. But how that budget reaches individual participants — and whether the distribution mechanism itself works as intended — is a separate question. That is the subject of §2.

# 2. Pools Distribution

## 2.1 Flow Overview

This stage takes the **pools pot** ($PoolsPot^{\text{epoch}}$) produced by §1 and distributes it across individual pools. The output is a per-pool allocation ($PoolPot^{\text{actual}}_i$) that feeds into §3 (operator/delegator split).

For each pool $i$, the protocol performs three steps:

1. **Saturation clipping.** Both total stake ($\sigma_i$) and pledge ($s_i$) are capped at the saturation threshold $z_0 = 1/k$. This prevents any single pool from capturing a disproportionate share.

2. **Reward curve evaluation.** A reward function $f$ computes the pool's *optimal* allocation from its clipped stake and pledge. The curve has two components: a **base stake term** (proportional to delegation) and a **pledge-bonus term** (nonlinear, governed by $a_0$). The pledge bonus is meant to reward operator commitment ("skin in the game").

3. **Performance adjustment.** The optimal allocation is scaled by apparent performance $\bar{p}_i$ to produce the *actual* allocation. Pools that miss blocks receive less. If the registered pledge is not met, the allocation is zeroed entirely.

Any rewards not distributed (because $\sum_i \hat{f}_i < R$) return to the reserve — this is the mechanism behind O3 in §2.

Two design choices matter for the rest of the analysis:

- **Pledge sensitivity via $a_0$.** The parameter $a_0$ controls how much additional reward a pool can earn through pledge. At $a_0 = 0.3$, the pledge bonus represents at most ~23% of the optimal allocation. Whether this is sufficient to meaningfully incentivise pledge is a central question at this layer.

- **Uniform saturation threshold.** All pools share the same cap $z_0 = 1/k$. There is no mechanism to differentiate saturation based on pledge level or pool characteristics.

> **Formulas.** The pool-level reward formulas — from the original SL-D1 reward curve through the normalized saturation coordinates rewrite to mainnet parameterization — are in the dedicated sub-report: [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md) — §2.3.

## 2.2 Mainnet Observations

The pool-level analysis (epochs 208–618) yields four observations at this pipeline stage. The full data, figures, entity analysis, and reproduction scripts are in the dedicated sub-report: [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md).

| # | Observation | Summary |
| --- | --- | --- |
| **O1** | **The pledge bonus is functionally irrelevant at realistic pledge levels** | At median pledge the bonus adds ~0.006% to rewards — undetectable. Yield on pledge capital (0.68%/yr at best) is below passive delegation yield (~2.3%/yr). 22.1% of the pools pot (~3.4M ADA/epoch) returns to reserve unused because the $a_0$ curve is too flat. |
| **O2** | **The pool landscape is stratified far from the k = 500 design target** | 73% of pools (1,987) sit below the 3M ADA viability line, carrying only 2.7% of active stake. Only 7 pools reach saturation — 1.4% of the k = 500 target. |
| **O3** | **Saturation is structurally underutilised** | Active stake fills 56.5% of theoretical capacity (k × z₀). At most 282 pools could saturate under perfect redistribution. The near-saturation zone holds only 104 pools. |
| **O4** | **The delegation market is capital-constrained** | 16.75B ADA (43.5%) does not participate in delegation — this is the binding constraint. k = 500 is feasible only at full participation. 85 MPO entities control ~51% of staked ADA. |

> **Scope note.** Observations O1–O3 are structural to the pool-distribution layer. O4 (capital constraint) is the same upstream condition documented at §1 O3 — it sets the playing field within which the reward curve operates.

## 2.3 Problem Induction → Closing the Consensus Incentive Gap

Each observation above constrains what the reward curve can accomplish. Read together, they reveal a gap between the equilibrium the mechanism was designed to produce and the equilibrium it actually produces.

The pledge bonus is functionally irrelevant (O1): at realistic pledge levels it adds ~0.006% to rewards, invisible to delegators and uneconomic for operators. The pool landscape is stratified far from the $k = 500$ target (O2): 73% of pools sit below viability, and only 7 reach saturation. Saturation capacity is structurally underutilised (O3): active stake fills 56.5% of theoretical capacity, so at most 282 pools could saturate. And the delegation market is capital-constrained (O4): 16.75B ADA (43.5%) does not participate, which is the binding constraint on everything the reward curve can accomplish.

The pool reward curve is not merely a reward-distribution mechanism. It is the protocol's only tool for shaping the operator ecosystem that secures consensus. Its purpose is to produce an *incentive-compatible equilibrium*: a state where rational, self-interested participants — operators competing on pledge commitment, delegators rewarding the most committed operators — collectively maintain the security invariants the consensus layer depends on (decentralisation, Sybil resistance, accountability).

The formal game-theoretic properties of this mechanism were established in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020), which proves that $k$ pools is a Nash equilibrium under certain assumptions. The engineering specification *SL-D1* translates those results into protocol-level formulas. However, neither document provides a **narrative description of the game as it should play out** — the players, their motivations, how they enter and progress, and the equilibrium they should converge toward. Evaluating whether the mechanism works requires a clear picture of what working looks like. That narrative description is produced in a dedicated companion document: [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md).

The observations above, confronted with this intended design, reveal two interrelated failures:

**The playing field is half the size the design assumed.** $k = 500$ implicitly required near-complete participation. At 56.5%, the target is structurally unreachable — at most 282 pools could saturate (O3). The saturation cap binds for only 7 pools (O2). No formula change at this layer can close this gap; it requires upstream intervention to bring inactive ADA into delegation.

**The incentive game does not converge toward the intended equilibrium.** The reward curve's theoretical optimum ($\pi = 1, \nu = 1$) is a fully-pledged private pool with no delegator — eliminating the accountability mechanism at the endgame. Reaching it requires 77M ADA at a yield of ~0.68%/yr, below passive delegation (~2.3%/yr) — making the endgame economically irrational. The progression is invisible: the pledge bonus adds ~0.006% at median pledge, undetectable by delegators (O1). The entry creates a viability cliff, not a ramp (O2). The dominant strategy at every level — entry, progression, endgame — is to maximise delegation and minimise pledge, the exact opposite of what consensus security requires. The full analysis of these distortions from the operator's perspective is in §2.4 below.

The evidence confirms this at scale: 95.6% of the pledge-bonus budget returns to reserve unused (O1), the independent operator base has collapsed to 283 viable operators (O5), the incentive-responsive field holds only 36% of active stake (O6), and structural populations totalling 7.39B ADA cannot pledge by architectural constraint (O4).

**CPS identified.** No *Cardano Problem Statement* (CPS) has been formally written for this problem. CIP-0050 and CIP-0037 both propose modifications to the reward curve at this layer — but they were designed without a shared, formal problem definition to scope them against. This analysis identifies the gap and produces the missing CPS — *Closing the Consensus Incentive Gap* — derived from the mainnet evidence in the dedicated [sub-report](sub-flows/pools-distribution/mainnet-analysis/README.md) and defined in [`sub-flows/pools-distribution/cps/`](sub-flows/pools-distribution/cps/). The CPS evaluation of CIP-0050 and CIP-0037 follows in §2.5.

## 2.4 The Divergent Operator Experience

The observations above document *what* the reward curve produces. This section examines *why* — by following an operator through the trajectory the mechanism promises (entry → progression → endgame) and identifying the point at which the reward curve stops rewarding the intended strategy. The baseline for this analysis is [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md), which describes the game as it should play out.

### 2.4.1 Entry — below 1M ₳, too committed to just delegate, too small to operate

An operator registers a pool, pledges what they can — say 50K ADA — and starts looking for delegators.

The promise ([*The Intended Game* §3.2](sub-flows/pools-distribution/the-intended-game/README.md#32-operators)) is clear: pledge commitment is the competitive dimension, and increasing it should produce visible, measurable advantages that attract delegation. The game should feel like a ramp — each step forward in commitment unlocking the next level of reward and reputation.

The first step is high.

#### 2.4.1.1 The structural floor

Block production is a Poisson process, and below ~1M ₳ in total stake a pool expects less than one block per epoch. Reward variance equals its own mean — yield is noise, not signal.

This is the *production threshold* (F3.1): a hard structural floor set by the physics of the consensus protocol, not by a tuneable parameter.

Above that sits the *viability threshold* (~3M ₳, F3.2): below it, the 340 ₳ fixed cost per epoch exceeds the pool's expected reward. This second boundary is softer — it depends on the reward curve's parameters and narrows over time as node implementations improve and hardware costs decline.

But the production threshold is irreducible.

#### 2.4.1.2 A gate with no sign

Crucially, the mechanism does not communicate this floor. Nothing in the protocol tells a prospective operator "do not register a pool below 1M ₳ — it will not produce blocks." Registration is open at any amount.

The game lets participants in, takes their operational costs, and gives nothing in return.

The result is visible on mainnet: 73% of pools sit below the viability threshold.

These pools have no reason to exist — not from a consensus perspective (they contribute negligibly to block production), not from an investment perspective (they destroy value for their delegators), not from any perspective.

And the damage extends beyond the pools themselves. They pollute the landscape for every other participant.

Delegators browsing a pool explorer must navigate hundreds of sub-viable pools that look superficially legitimate but cannot deliver reliable yield. Wallet developers building staking features must decide how to present a pool set where the majority are economically inert. Viable operators must compete for visibility in a catalogue diluted by pools that the mechanism should never have admitted.

The signal-to-noise ratio of the entire pool marketplace degrades — making delegation decisions harder, accountability less effective, and the competitive environment less legible for everyone.

They are artifacts of a mechanism that defines a structural floor but does not signal it. The protocol silently accepts participants it cannot serve — and in doing so, degrades the experience for those it can.

#### 2.4.1.3 Capital over competence

Below the structural floor, the rational move is to delegate — not operate. An operator can still accumulate the deflationary asset, but as a passive participant.

Delegation earns yield, but it does not earn the *leverage* that comes with consensus participation. The skin in the game is capital; it is not *commitment* to the network.

A prospective operator may have exceptional technical knowledge — capable of running a reliable, performant node — but the mechanism does not value knowledge. It values capital at scale.

An operator with deep expertise and 100K ₳ is invisible to the reward curve. A capital holder with no expertise and 5M ₳ can hire the expertise.

The game's entry filter selects for capital, not for the operational competence the protocol actually needs.

#### 2.4.1.4 A gap worth exploring

The current mechanism offers two modes — delegate or operate — with nothing in between. A participant who is ready to commit beyond passive delegation but cannot meet the production threshold has no path forward.

Concepts like *pool alliances* — mechanisms that would let smaller stakeholders combine their commitment to participate at a higher level of engagement — represent a design space worth exploring.

They would not lower the production threshold itself (that is structural), but they could create an intermediate tier of participation where conviction and competence find expression before capital alone permits full operation.

This is not a detailed proposal — it is an observation that the gap between delegation and operation is where the protocol currently loses participants it could benefit from retaining.

### 2.4.2 Progression — balanced as intended, but private by design

An operator has crossed the production threshold. The pool produces blocks, earns rewards, and the deflationary accumulation thesis from [*The Intended Game* §2.2.1](sub-flows/pools-distribution/the-intended-game/README.md#221-an-open-seat-at-the-deflationary-table) is finally in play. The question becomes: how does the operator grow?

The mechanism's answer ([*The Intended Game* §3.2.2](sub-flows/pools-distribution/the-intended-game/README.md#322-progression)) is *pledge*. Increasing personal commitment should produce a measurable competitive advantage — visible to delegators, economically meaningful to the operator — creating a legible progression from "new pool" to "established pool" to "fully committed pool."

Before examining what the pledge mechanism delivers in practice, it is worth mapping the strategic landscape it creates.

#### 2.4.2.1 The three strategies

Every entity that crosses the production threshold enters a game defined by two structural facts: a shared endgame that all entities converge on, and a single degree of freedom that separates their paths. Together, these two facts define the full strategic landscape.

##### 2.4.2.1.1 The common endgame — saturate, then become an MPO

The reward formula caps individual pool rewards at $P_{\max}$: once a pool reaches the saturation point ($\sigma = z_0 \approx$ 77M ₳), every additional ADA of stake produces *zero* marginal reward. Worse — it dilutes the per-ADA yield for every existing participant, operator and delegator alike. The saturation cap is a hard ceiling, not a soft one.

An entity whose capital or delegation-attracting capacity exceeds $z_0$ therefore faces a binary choice: stop growing, or register a second pool. Since the entity's motivation for entering the game — the deflationary accumulation thesis ([*The Intended Game* §2.2.1](sub-flows/pools-distribution/the-intended-game/README.md#221-an-open-seat-at-the-deflationary-table)) — is driven by continuous compounding, stopping is irrational. The mechanism's natural growth path is not deeper commitment to a single pool; it is fleet expansion: becoming a multi-pool operator (MPO). Saturate the current pool, register a new one, repeat.

This endgame is strategy-independent. Whether an entity fills pools with personal capital, with external delegation, or with a mix of both, the saturation cap forces the same MPO trajectory. The distinction between entities lies not in the destination but in how they staff each pool along the way. And it is worth noting that the mechanism says nothing about this transition — there is no special reward for operating a single pool, no penalty for splitting across many. The formula evaluates each pool independently. The entity-level strategy that spans multiple pools is invisible to the protocol.

##### 2.4.2.1.2 The degree of freedom

Within the shared endgame, an entity retains one strategic variable per pool: the ratio between *owner commitment* (pledge and self-delegation) and *third-party delegation*. This ratio defines the entity's posture — the answer to the question "who funds this pool, and therefore who benefits from it?"

The spectrum is continuous. At one extreme, the operator funds the entire pool with personal capital — no delegator plays any role. At the other, the operator contributes nothing but infrastructure and a registration certificate — every ADA in the pool belongs to someone else. Between these poles lies every possible split.

The reward formula is sensitive to this ratio through the pledge bonus ($\lambda_{\max} \cdot A(\pi, \nu)$), which increases with the pledge fraction $\pi = \lambda / z_0$. In principle, the bonus should pull operators toward higher commitment. Whether it does so in practice — with sufficient force to overcome the costs it imposes — is the question the rest of this section examines.

Three archetypes capture the essential strategic postures along this spectrum. They are not discrete options — real operators occupy every point on the continuum — but they define the poles and the centre in terms that map cleanly onto the security properties the protocol depends on.

##### 2.4.2.1.3 The balanced strategy

The balanced strategy maintains a meaningful owner-stake ratio while leaving substantial room for delegation. Both the operator and external delegators contribute to the pool's stake. The exact split — whether 20/80, 50/50, or 80/20 in favour of owner commitment — varies across entities, but the defining characteristic is that neither party fills the pool alone.

The economic logic is partnership: the operator commits personal capital and operational infrastructure; delegators provide the remaining stake that carries the pool toward saturation. The operator earns the fixed fee, the margin, *and* a share of the pool's size-based reward on their own stake, plus whatever the pledge bonus adds. Delegators earn the residual yield after the operator's cut. Both parties have a reason to remain — and both have a credible exit option that the other must respect.

This is the posture the mechanism was designed to encourage. The operator's progression described in [*The Intended Game* §3.2](sub-flows/pools-distribution/the-intended-game/README.md#32-operators) — build reputation, attract delegation, deepen pledge, compound — presupposes a balanced configuration where increasing commitment produces a measurable competitive edge.

##### 2.4.2.1.4 The private strategy

The operator pledges and self-delegates the majority or totality of the pool's stake, minimising or eliminating external delegation. The pool operates as a closed vehicle: the operator funds it, produces blocks, and collects the full reward.

The economic logic is self-sufficiency: the operator needs no one else. There is no margin to set (the operator captures everything), no delegator to attract (or lose), no reputation to build in the marketplace. The pool's competitiveness is a function of one variable — the operator's treasury size.

The reward formula explicitly endorses this posture. The maximum pool reward $P_{\max}$ is defined at $\pi = 1$ and $\nu = 1$: the operator pledges the entire saturation amount, the pool is full, and the operator is the sole beneficiary. This is not an incidental corner case — it is the *designed optimum* of the reward curve. The formula's "dream" is a pool where the operator funds everything and needs nobody.

Private pools are therefore not deviations from the mechanism's intent — they are its literal target. The tension this creates with the security properties the protocol depends on (which require delegation to be present and pledge to be an active competitive dimension, not a wealth filter) is the subject of §2.4.2.2.

##### 2.4.2.1.5 The hollow strategy

The operator pledges nothing or near-nothing and fills the pool entirely through external delegation. The pool operates at zero or near-zero owner commitment — block-production rewards are generated almost entirely from third-party stake.

The economic logic is leverage: the operator contributes infrastructure and a registration certificate, then captures the fixed fee plus margin on *other people's capital*. In the current parameter regime (340 ₳ fixed cost, typical margins of 1–5%), this means the operator extracts a guaranteed income stream without committing personal capital to the pool. The opportunity cost is zero — the operator's own ADA can be delegated elsewhere, used as collateral, or held liquid. The only "pledge" is whatever token amount the operator registers to satisfy the certificate requirement.

This is the rational response when the pledge bonus is too small to justify the costs it imposes (liquidity lock-up, pledge-unmet risk — detailed in §2.4.3). If deepening commitment earns nothing detectable, the dominant move is to minimise commitment and maximise the capital base over which the operator extracts fees. It is also the only available strategy for custodial operators (exchanges, staking-as-a-service providers) who cannot pledge the capital they manage for legal and fiduciary reasons — a population examined in §2.4.2.3.

These three archetypes span the full spectrum of the pledge/delegation ratio. They are not equally desirable. A network of balanced pools and a network of hollow pools may look similar on a pool explorer — both have delegation, both produce blocks — but their security properties are fundamentally different. The section that follows evaluates each against the invariants the consensus layer depends on.

#### 2.4.2.2 Why balanced should be the intended equilibrium

The consensus layer does not care which strategy operators prefer. It cares whether the resulting equilibrium preserves a set of structural properties without which the security model breaks down.

[*The Intended Game* §3.4](sub-flows/pools-distribution/the-intended-game/README.md#34-the-security-properties-the-equilibrium-must-satisfy) derives four such properties from the formal literature and the SL-D1 specification: **accountability** (block producers must bear a real economic cost for misbehaviour), **delegation as counter-power** (delegators must have the leverage to discipline operators through credible exit), **Sybil resistance** (creating additional block-producing identities must carry a cost that scales through the *mechanism*, not merely through wealth), and **decentralisation** (the entry barrier must admit diverse, independent operators rather than concentrating production among the capital-rich or the brand-dominant). These properties are not independent — accountability requires delegation to have an enforcer, delegation requires accountability to have consequence, Sybil resistance and decentralisation must be jointly calibrated — and the structural requirement they impose is that **each pool must combine meaningful operator commitment with meaningful external delegation** ([§3.4.6](sub-flows/pools-distribution/the-intended-game/README.md#346-the-structural-requirement)).

The three strategies defined above map directly onto this framework. The question is which, if any, produces an equilibrium that satisfies all four properties simultaneously.

##### What happens if the equilibrium is not balanced

The argument is sharpened by examining the alternatives as *systemic* outcomes — not as individual pool strategies, but as the equilibrium the entire network converges toward.

**If the equilibrium is all-private:** every pool is funded entirely by its operator. The operator landscape shrinks to the few dozen entities with enough capital to saturate a pool (~77M ₳ each). Delegators are excluded from consensus entirely — they can still delegate, but no pool needs their stake. The accountability mechanism collapses: operators answer only to themselves. The network is secure against external Sybil attacks (the capital barrier is enormous) but has no defence against collusion among the small set of plutocratic operators. Consensus power is concentrated by construction. The protocol has produced a permissioned system with extra steps.

**If the equilibrium is all-hollow:** every pool operates at zero or near-zero pledge. Registering a new pool costs nothing beyond infrastructure — the Sybil defence is gone. A well-capitalised attacker can register hundreds of pools, attract delegation through marketing or exchange integration, and accumulate consensus power without committing personal capital. The accountability mechanism is formally present (delegators can exit) but economically inverted: the operator has nothing at risk, so the "consequence" of delegator exit is that the operator loses a revenue stream they can rebuild by registering another pool. Delegation concentration follows brand and convenience, producing the oligopoly pattern visible on mainnet today. The protocol has produced a system where the entities with the most consensus power are the ones with the least to lose.

**If the equilibrium is balanced:** operators commit meaningful personal capital (the bond exists), delegators provide the growth path and the continuous oversight (the enforcement mechanism exists), fragmentation is costly because it dilutes pledge across pools (the Sybil tax operates), and the entry barrier is calibrated to admit operators of moderate means (the operator set is diverse). All four properties hold simultaneously. The balanced equilibrium is not a compromise between private and hollow — it is the *only* configuration in which the dependency chain described in [*The Intended Game* §2.4](sub-flows/pools-distribution/the-intended-game/README.md#24-the-dependency-chain) functions as designed.

##### Evaluation against the four properties

The following table evaluates each strategy against the security properties. Each cell contains the *reasoning*, not just the conclusion.

| Property | Balanced | Private | Hollow |
| --- | --- | --- | --- |
| **Accountability** | Operator commits meaningful capital — a legible bond that is costly to abandon. The bond exists independently of delegator attention, providing a baseline cost of misbehaviour even when oversight is imperfect. | Maximal capital exposure, but self-referential. The operator is accountable only to themselves. In a system without slashing, self-accountability has no enforcement mechanism — the operator both commits the offence and decides the penalty. No external interest is at risk. | Eliminated. Zero pledge means zero cost of exit. The operator can abandon a misbehaving pool and register a new one without forfeiting anything. The accountability structure exists on paper but has no economic content. |
| **Delegation as counter-power** | Delegators are present and their departure is costly to the operator — the pool shrinks, rewards drop, competitive position degrades. The feedback loop is intact: delegator exit is a *credible threat* because the operator depends on delegation for a material share of pool stake. | No delegators, no exit threat. The pool is a closed system. The operator can degrade performance, raise margin to 100%, or go offline — the only consequence is self-inflicted. The disciplinary mechanism has no input. | Formally present but *inverted*. Delegators provide all capital, but the operator has nothing at stake. If delegators exit, the operator loses a revenue stream — but can rebuild it by registering a new pool at near-zero cost. The exit cost falls on the delegator (search cost, epoch delay) more than on the operator. The power asymmetry runs the wrong way. |
| **Sybil resistance** | Real cost of fragmentation: splitting into $n$ pools requires dividing pledge across $n$ certificates, diluting the bonus per pool and reducing competitiveness in each. The Sybil tax operates *through the mechanism* — it is the pledge bonus that makes fragmentation suboptimal. | High capital cost per pool, but the constraint is *wealth*, not the pledge mechanism. An entity with enough capital can operate as many saturated pools as their treasury permits. The pledge bonus is negligible relative to the capital deployed; what prevents fragmentation is running out of money, not forfeiting a bonus. The mechanism's Sybil defence is irrelevant — raw wealth does the work. | Near zero. Registering a new pool requires only infrastructure and a certificate fee. The 85 MPO entities on mainnet — some operating dozens of pools with minimal or zero pledge — demonstrate that fragmentation is cheap when no pledge is required. The mechanism's Sybil defence is absent. |
| **Decentralisation** | Capital is shared between operator and delegators — the entry barrier admits operators of moderate means. Operators compete on commitment and community trust, not on treasury size alone. The competitive field is wide enough for diverse, independent operators to coexist. | Concentrated among the capital-rich. The effective entry barrier is the saturation cap (~77M ₳ per pool). The operator set is bounded by the number of entities with eight-figure treasuries — a vanishingly small population. Block production is permissioned by wealth. | Entry barrier near zero, but delegation flows to the most *visible*, not the most *committed*. Exchange pools, custodial services, and brand-driven fleets attract delegation through convenience. Concentration emerges through market dynamics: 85 MPO entities control ~51% of staked ADA. The long tail of independent operators is structurally starved. |

The balanced strategy is the only one that satisfies all four properties simultaneously — not as a theoretical possibility, but as a stable configuration in which each property *reinforces* the others. The private strategy preserves accountability in a narrow, self-referential sense but eliminates the delegation feedback loop, renders the Sybil mechanism redundant, and concentrates production among the capital-rich. The hollow strategy preserves the *appearance* of delegation but strips it of disciplinary power, removes every cost that the consensus layer depends on, and produces concentration through market dynamics rather than capital barriers.

The question that follows — and that the rest of this section examines — is whether the current mechanism actually *produces* this balanced equilibrium, or whether its parameter regime drives rational actors toward one of the alternatives.

#### 2.4.2.3 The current design incentivises the private strategy

The maximum pool reward $P_{\max}$ is defined at $\pi = 1$ and $\nu = 1$: the operator pledges the entire saturation amount ($z_0 \approx$ 77M ₳) and the pool is fully saturated. Since pledge counts as stake, this means the operator funds the entire pool with personal capital. There are no delegators. The reward curve's global maximum is a closed vehicle where the operator is the sole funder, the sole block producer, and the sole beneficiary.

This is not an incidental corner case or a mathematical artefact. It is the *explicit target* of the reward function — the point toward which the formula's gradient pulls any rational operator. The entire reward surface is oriented so that increasing $\pi$ and increasing $\nu$ both increase the reward, and the global maximum sits at the intersection of both maxima: full pledge, full saturation, zero delegation.

The endgame the mechanism defines — reached by every operator who follows the formula's gradient to its conclusion — requires ~77M ₳ (~30M USD) of personal capital, locked. The total yield on a fully-pledged saturated pool is ~2.95%/yr, of which only +0.68%/yr comes from the pledge bonus above the ~2.27%/yr base. The mechanism's ideal operator is not the committed community member who grew from a modest start; it is a solitary whale who locks a fortune for a marginal uplift to run a pool that no one else participates in.

This creates a direct contradiction with the security requirement established in §2.4.2.2. The equilibrium the formula optimises for — $k$ private pools, each fully funded by a single wealthy operator, with no delegator participation — is precisely the all-private scenario that eliminates delegation as counter-power, restricts participation to the capital-rich, and concentrates consensus among a small plutocratic set. The formula's designed optimum breaks two of the four security properties it was supposed to preserve.

The formula says: *the best pool is a private pool.* The security model says: *the best pool is a balanced pool.* The mechanism is at war with itself.

![The Playing Field — what a pool can earn vs. what it costs (epoch 616)](sub-flows/pools-distribution/the-intended-game/figures/playing_field_mainnet.png)
*Figure 1 — Left: reward composition at full saturation — the ceiling is $P_{\max}$ at full pledge, full saturation. Right: reward by pool size, comparing size-only reward (green) to the pledge premium (purple). The left panel shows where the formula points; the right panel shows why the journey there is irrelevant. Data: epoch 616.*

### 2.4.3 Endgame — the hollow strategy is the dominant one

The formula points toward private (§2.4.2.3). Mainnet converges on hollow. This section explains the gap — not as a single failure, but as a series of compounding factors that make hollow the rational outcome at every decision point an operator faces. The argument builds in layers: first, what the network actually looks like; then, why the game's structure favours delegation over pledge *before* any reward calculation enters the picture; then, why the reward formula reinforces rather than counteracts this default; and finally, why the resulting dynamic is self-reinforcing.

#### 2.4.3.1 What mainnet reveals

The distribution of strategies on mainnet is not ambiguous. Of the 609 entities operating active stake pools at epoch 618, 501 (82.3%) are classified as hollow — their dominant strategy is to minimise pledge and fill their pools through external delegation. 95 entities (15.6%) operate as balanced, and 13 (2.1%) as private.

The stake-weighted picture is sharper still. Hollow entities control 18.14B ₳ of active stake (85.4% of total), with a collective owner-ratio of 0.98% — meaning that for every 100 ADA staked in hollow pools, less than 1 ADA comes from the operator. Private entities control 2.29B ₳ (10.8%), almost entirely self-funded. Balanced entities hold 0.80B ₳ (3.8%).

The pool-level data confirms the pattern. Of 2,718 pools with active stake, 2,262 (83.2%) pledge less than 100K ₳. The median pledge-to-stake ratio across healthy pools is 0.14% — the median pool pledges roughly one ADA for every 700 it manages. 226 pools declare zero pledge outright.

Among multi-pool operators — the entities that have scaled beyond a single pool and thus revealed a deliberate growth strategy — the skew is even more pronounced. Of 75 MPOs, 67 (89.3%) are hollow. 3 (4.0%) operate as balanced. 5 (6.7%) as private. The entities that have *chosen* how to grow have overwhelmingly chosen to grow through delegation, not pledge.

The pledge bonus mechanism — the formula's entire budget for making the degree of freedom identified in §2.4.2.1.2 consequential — captures 1.0% of its theoretical allocation (epoch 616 data). 95.6% of the pledge-bonus budget returns to the reserve pool unused every epoch, not because operators are unaware of it, but because the cost of capturing it exceeds its value at every realistic operating point.

This is the outcome the following sub-sections explain.

#### 2.4.3.2 Delegating is inherently less constraining than pledging

Before examining the reward formula, a prior question must be settled: if two operators hold the same amount of ADA and face the same pool, and the only difference is whether they *pledge* that ADA or *delegate* it, which action is less costly? The answer is unambiguous, and it holds regardless of any bonus the formula may attach to pledge.

**Liquidity.** Pledged ADA must remain in the operator's wallet for the duration of the pool's operation. It is registered on-chain as a commitment to the pool certificate and cannot be redeployed, used as collateral, lent, or moved to another pool without modifying the certificate. Delegated ADA, by contrast, remains fully liquid. The holder can redirect it to another pool at any epoch boundary, use it in DeFi protocols, or sell it — the delegation is a preference signal, not a capital lock. For an operator managing a treasury, pledging transforms a liquid asset into a frozen one. Delegating does not.

**Reversibility.** Delegation is revocable within a single epoch boundary — the delegator signs a new delegation certificate and the redirect takes effect at the next snapshot. De-pledging is formally possible but operationally fraught: the operator must update the pool certificate to lower the declared pledge, and the change takes effect at the next epoch boundary. During the transition, any fluctuation in the pledged UTxO set that brings the balance below the *still-active* declared amount triggers the pledge-unmet penalty. The act of *reducing* commitment is itself a risk event. Delegation carries no equivalent penalty for changing one's mind.

**Risk profile.** The protocol imposes a binary, catastrophic penalty on pledge shortfalls: if the on-chain pledge balance drops below the declared amount at any snapshot during an epoch — due to a transaction, a wallet synchronisation issue, or any fluctuation — the pool's *entire* reward for that epoch is zeroed. Not the pledge bonus — the entire reward, size component included, for the operator and every delegator in the pool. The penalty is not proportional to the shortfall. One ADA below threshold triggers the same total loss as a complete withdrawal. Delegation carries no protocol-level penalty of any kind. A delegator who withdraws or redirects ADA does not trigger any penalty — neither for themselves nor for the pool.

The asymmetry is structural: the more an operator pledges, the larger the balance that must remain untouched, and the more catastrophic the penalty if anything goes wrong. The upside is a small, linear bonus; the downside is a total, binary wipe. Pledging is the only action in the Cardano staking protocol where the risk profile is *inversely* proportional to the reward. Delegating has no risk profile at all.

**Opportunity cost.** ADA delegated to a pool earns the same base yield as the pool delivers to all participants — and the holder retains all other options. ADA pledged to a pool earns the same base yield *plus* a marginal pledge bonus — but the holder forfeits every other use. In a protocol ecosystem with growing DeFi activity, lending markets, and liquidity provision opportunities, the opportunity cost of locking capital as pledge is real and increasing. The bonus would need to exceed not just zero, but the *best alternative return* available to that capital — a threshold that rises as the ecosystem matures.

**Custodial exclusion.** A significant class of operators — exchanges, custodial wallets, institutional funds, staking-as-a-service providers — manages capital that is not their own. For these entities, pledging is not a question of incentive but of legal possibility. Pledged capital must remain in the operator's wallet; capital held on behalf of clients must be returnable on demand. The constraint is categorical: custodial operators cannot pledge the capital they manage, regardless of how attractive the mechanism makes it. They are not choosing to ignore pledge — they are architecturally excluded from it. The reward formula asks them to play a game whose rules they cannot legally follow. On mainnet, these entities — exchanges like Coinbase, Binance, Upbit, eToro; institutional validators like Figment, Kiln, Blockdaemon, Everstake — collectively manage billions of ADA in pools with near-zero pledge. Their strategy is hollow not by choice but by constraint.

**The rational default.** Each of these asymmetries — liquidity, reversibility, risk, opportunity cost, legal constraint — pushes independently toward delegation over pledge. Taken together, they define a *prior*: before any reward is calculated, before any bonus is evaluated, the rational default for any ADA holder deciding how to participate in a pool is to delegate rather than pledge. Pledging is the strictly more constrained action. It carries costs that delegation does not, risks that delegation does not, and restrictions that delegation does not. The only reason to pledge rather than delegate is if the reward formula compensates for all of these asymmetries — if the pledge bonus is large enough to overcome the liquidity cost, the reversal risk, the cliff penalty exposure, and the opportunity cost of locking capital.

The question that follows is whether the formula actually provides this compensation. The answer, as the following sub-sections show, is that it does not — and not by a narrow margin.

#### 2.4.3.3 The reward structure weights size, not commitment

The degree of freedom — the pledge/delegation ratio — is governed by a single component of the reward formula: the pledge bonus ($\lambda_{\max} \cdot A(\pi, \nu)$). Everything else in the pool's reward is sensitive to *size* ($\nu$), not to *commitment* ($\pi$).

The structural weight tells the story. The size-only component ($\lambda_{\min} \cdot \nu$, where $\lambda_{\min} \approx 76.9\%$ of $P_{\max}$) represents ~77% of the maximum reward. The pledge component ($\lambda_{\max} \cdot A(\pi, \nu)$, where $\lambda_{\max} \approx 23.1\%$) represents the remaining ~23%. A pool that grows from 5M to 30M ₳ in total stake sees its per-epoch reward climb from ~2,000 to ~12,000 ADA — entirely from the size fraction, entirely insensitive to pledge.

The right panel of Figure 1 makes this visible. The green area — reward earned from stake size alone, with zero pledge — dominates at every scale. An operator who pledges nothing and one who pledges everything earn the same green area. The only strategic variable that moves this component is *delegation attraction* — and delegation responds to yield, brand, and convenience, not to pledge.

The signal the mechanism sends is unambiguous: ~77% of the maximum reward is reserved for growing the pool; ~23% for deepening commitment within it. Given the inherent asymmetry established in §2.4.3.2 — that pledging is the strictly more constrained action — the formula needed to weight commitment *more* heavily than size to overcome the natural gravitational pull toward delegation. Instead, it weights size more than three to one. The formula does not counteract the prior; it reinforces it.

#### 2.4.3.4 The pledge bonus is inoperative at realistic scale

The 23% allocated to the pledge component is the mechanism's *entire* budget for making commitment matter. Whether the degree of freedom is real or illusory depends on whether this budget produces detectable economic differences between strategies at the scales operators actually operate.

The following tables trace the pledge bonus across four pool sizes — from the production threshold to full saturation — for five allocation strategies within a pool of fixed total size.

**At 1M ₳ (production threshold, ν ≈ 0.013):**

| Strategy | Pledge | Self-delegation | Pool reward | Pledge bonus | Total yield | Bonus yield on pledge | Yield uplift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Hollow** (0/100) | 0 | 1M | 310.4 ADA/ep | — | 2.27%/yr | — | baseline |
| **Healthy delegation** (20/80) | 200K | 800K | 310.6 ADA/ep | +0.2 ADA/ep | 2.27%/yr | 0.007%/yr | +0.06% |
| **Balanced** (50/50) | 500K | 500K | 310.7 ADA/ep | +0.3 ADA/ep | 2.27%/yr | 0.004%/yr | +0.10% |
| **Healthy pledge** (80/20) | 800K | 200K | 310.6 ADA/ep | +0.2 ADA/ep | 2.27%/yr | 0.002%/yr | +0.07% |
| **Private** (100/0) | 1M | 0 | 310.4 ADA/ep | <0.1 ADA/ep | 2.27%/yr | <0.001%/yr | <0.01% |

At the production threshold, the pledge bonus is undetectable. Every strategy yields 2.27%/yr. The best bonus — Balanced, at +0.3 ADA per five-day epoch — is buried so far below block-production variance that no delegator, and no operator, can observe it. Private is *worse* than Balanced and Healthy pledge: the concavity of $A(\pi, \nu)$ at low saturation means the bonus peaks around $r^* = 1/(2(1-\nu)) \approx 0.51$ and declines beyond. Full commitment already destroys bonus value at this scale.

**At 20M ₳ (ν ≈ 0.26):**

| Strategy | Pledge | Self-delegation | Pool reward | Pledge bonus | Total yield | Bonus yield on pledge | Yield uplift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Hollow** (0/100) | 0 | 20M | 6,208 ADA/ep | — | 2.27%/yr | — | baseline |
| **Healthy delegation** (20/80) | 4M | 16M | 6,291 ADA/ep | +82 ADA/ep | 2.30%/yr | 0.15%/yr | +1.3% |
| **Balanced** (50/50) | 10M | 10M | 6,361 ADA/ep | +152 ADA/ep | 2.32%/yr | 0.11%/yr | +2.5% |
| **Healthy pledge** (80/20) | 16M | 4M | 6,366 ADA/ep | +158 ADA/ep | 2.32%/yr | 0.07%/yr | +2.5% |
| **Private** (100/0) | 20M | 0 | 6,334 ADA/ep | +126 ADA/ep | 2.31%/yr | 0.05%/yr | +2.0% |

The bonus becomes visible but reveals a structural inversion: **Private earns less bonus than Healthy pledge and Balanced.** The operator who pledges everything — the strategy the formula's global maximum endorses — earns +126 ADA/ep, while the one who pledges 80% earns +158 ADA/ep. Beyond the concavity peak ($r^* \approx 0.68$ at this saturation level), each additional ADA pledged *reduces* the total bonus. The formula punishes the very commitment its optimum was designed to incentivise.

**At 40M ₳ (ν ≈ 0.52):**

| Strategy | Pledge | Self-delegation | Pool reward | Pledge bonus | Total yield | Bonus yield on pledge | Yield uplift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Hollow** (0/100) | 0 | 40M | 12,416 ADA/ep | — | 2.27%/yr | — | baseline |
| **Healthy delegation** (20/80) | 8M | 32M | 12,766 ADA/ep | +350 ADA/ep | 2.33%/yr | 0.32%/yr | +2.8% |
| **Balanced** (50/50) | 20M | 20M | 13,151 ADA/ep | +735 ADA/ep | 2.40%/yr | 0.27%/yr | +5.9% |
| **Healthy pledge** (80/20) | 32M | 8M | 13,369 ADA/ep | +953 ADA/ep | 2.44%/yr | 0.22%/yr | +7.7% |
| **Private** (100/0) | 40M | 0 | 13,422 ADA/ep | +1,006 ADA/ep | 2.45%/yr | 0.18%/yr | +8.1% |

The concavity peak has moved past $r = 1$ at this saturation ($r^* \approx 1.04$), so Private no longer loses to Healthy pledge in absolute bonus. But the bonus yield per pledged ADA continues to decline: from 0.32%/yr (Healthy delegation) to 0.18%/yr (Private). The total yield spread from Hollow to Private is 0.18%/yr — for locking 40M ₳ as pledge.

**At saturation (77M ₳, ν = 1) — the theoretical ceiling:**

| Strategy | Pledge | Self-delegation | Pool reward | Pledge bonus | Total yield | Bonus yield on pledge | Yield uplift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Hollow** (0/100) | 0 | 77M | 23,898 ADA/ep | — | 2.27%/yr | — | baseline |
| **Healthy delegation** (20/80) | 15.4M | 61.6M | 25,332 ADA/ep | +1,434 ADA/ep | 2.40%/yr | 0.68%/yr | +6.0% |
| **Balanced** (50/50) | 38.5M | 38.5M | 27,483 ADA/ep | +3,585 ADA/ep | 2.61%/yr | 0.68%/yr | +15.0% |
| **Healthy pledge** (80/20) | 61.6M | 15.4M | 29,634 ADA/ep | +5,736 ADA/ep | 2.81%/yr | 0.68%/yr | +24.0% |
| **Private** (100/0) | 77M | 0 | 31,068 ADA/ep | +7,170 ADA/ep | 2.95%/yr | 0.68%/yr | +30.0% |

Only at full saturation does $A(\pi, 1) = \pi$ become linear, eliminating the concavity penalty. The bonus yield stabilises at 0.68%/yr per pledged ADA regardless of allocation. This is the best case the mechanism offers — and it requires 77M ₳ (~30M USD) of personal capital. The total yield from Hollow to Private moves from 2.27% to 2.95%: a +0.68%/yr uplift for locking the entire saturation cap.

Reading the four tables together, the pattern is clear. At the production threshold the bonus does not exist. As the pool grows it emerges but remains small, concave, and — below saturation — *inverted* at the extreme the formula was designed to optimise. Only at the unreachable limit of full saturation does the bonus behave as intended, and even there the uplift is modest.

#### 2.4.3.5 The size-visibility-delegation loop

The preceding sub-sections explain why an operator would *not* pledge. The mechanism the formula does not model explains why an operator *would* invest in delegation instead.

Delegators choosing a pool observe yield, reliability, and brand — all of which are functions of pool *size*, not pledge. A large hollow pool and a large pledged pool deliver nearly identical yields to their delegators (the pledge bonus is ~23% of the reward weight, split across all participants). From the delegator's perspective, pool size is the signal; pledge is noise.

This creates a self-reinforcing loop: large pools attract more delegation, which makes them larger, which makes them more visible and more reliable, which attracts more delegation. Pledge is orthogonal to this dynamic. An operator who invests effort in delegation attraction — through brand, exchange partnerships, or multi-pool infrastructure — enters this virtuous cycle. An operator who invests capital in pledge does not.

The result is not that pledging is a bad investment in the traditional sense — the bonus is positive. It is that pledging is a *dominated strategy*: the same capital and effort, deployed toward delegation attraction, generate returns that compound through the size-visibility-delegation loop, while the pledge bonus remains flat, small, and constrained by costs the formula ignores.

#### 2.4.3.6 The inversion

The mechanism was designed to reward commitment: pledge more, earn more, compound the advantage. The intended arc runs from Hollow toward Balanced — with the formula's gradient pointing beyond, toward Private (§2.4.2.3).

The actual incentive arc runs in the opposite direction. At the foundation, delegating is inherently less constraining than pledging — the rational default before any reward enters the picture (§2.4.3.2). The formula reinforces this default by weighting size over commitment by more than three to one (§2.4.3.3). The 23% it allocates to pledge is inoperative at every realistic scale (§2.4.3.4). And the size-visibility-delegation loop turns the initial advantage of delegation into a compounding one (§2.4.3.5).

A competing operator who pledges nothing and deploys that capital toward marketing, multi-pool infrastructure, or exchange partnerships will enter the snowball dynamic: more delegation → more size → more visibility → more delegation. An operator who pledges the same capital earns a small, flat bonus that does not compound and does not attract anyone.

The mechanism has inverted its own logic. The formula points toward private (§2.4.2.3); the game converges on hollow. The strategy the formula was supposed to make suboptimal — capital deployed outside the pledge mechanism toward delegation growth — is the one that dominates. The mainnet data in §2.4.3.1 is not a failure of adoption. It is the rational response to a mechanism at war with itself.

## 2.5 Proposed Solutions Evaluation

CIP-0050 and CIP-0037 are listed as *Proposed Solutions* in the CPS [*Closing the Consensus Incentive Gap*](sub-flows/pools-distribution/cps/README.md). Both modify the reward curve at this layer — CIP-0050 by capping pledge leverage, CIP-0037 by linking saturation to pledge. They were authored before the CPS existed: each proposal defines its own local problem statement and evaluates itself against it. This section evaluates them against the CPS instead.

Evaluating a CIP against a CPS requires a shared understanding of what the mechanism *should* produce — the intended game, its players, their progression, and the equilibrium they should converge toward. The formal game-theoretic foundation exists in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020), which proves that $k$ pools is a Nash equilibrium under certain assumptions. SL-D1 translates those results into formulas. But neither document provides a narrative description of how the game should play out in practice — the kind of description needed to assess whether a proposed curve modification actually moves the equilibrium in the right direction. That narrative is produced in [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md), which serves as the evaluation baseline for the CIP assessments below.

The evaluation criteria derive directly from the CPS goals: does the proposal align the endgame with the security model? Does it make pledge a legible competitive dimension? Does it create a credible entry-to-endgame progression? Does it ensure the dominant strategy aligns with consensus security? And does it work within the participation constraint (~56.5% active stake)?

### 2.5.1 CIP-0050 — Pledge Leverage Cap

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the sub-report formulas)
  3. Which problems from §2.3 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. parametrization of L)
-->

### 2.5.2 CIP-0037 — Dynamic Pledge-Linked Saturation

<!-- TODO: same structure as 2.5.1 -->

# 3. Operator / Delegator Distribution

## 3.1 Flow Overview

These formulas define how a pool's realized allocation is split between the operator and the rest of the pool participants.
The split happens only after the pool-level reward has already been computed and adjusted by apparent performance.

The distribution logic is sequential:

- first, the operator fixed cost is covered
- second, the operator margin is applied to the remaining amount
- finally, the residual reward is distributed proportionally across stake holders

In this final step, the operator still receives a stake-proportional share through the pledge held inside the pool, while delegators receive the complementary share.

## 3.2 Formulas

The operator and member rewards are two complementary views of the same split rule applied to the realized pool allocation.
Once the pool-level reward has been computed, the split follows the same sequence:

- cover the operator fixed cost first
- apply the operator margin to the remaining amount
- distribute the residual proportionally across stake holders

Under this rule, the operator receives both the explicit operator share and the stake-proportional share attached to the pledge held inside the pool, while each member receives a stake-proportional share of the residual amount.

### 3.2.1 SL-D1 (Original)

Operator reward, using the operator stake-share ratio $\frac{s}{\sigma}$ as a single input:

$$
r_{\text{operator}}\left(\hat f,c,m,\frac{s}{\sigma}\right)=
\begin{cases}
\hat f, & \hat f \le c \\
 c + (\hat f-c)\left(m + (1-m)\frac{s}{\sigma}\right), & \hat f > c
\end{cases}
$$

Member reward, using the member stake-share ratio $\frac{t}{\sigma}$ as a single input:

$$
r_{\text{member}}\left(\hat f,c,m,\frac{t}{\sigma}\right)=
\begin{cases}
0, & \hat f \le c \\
(\hat f-c)(1-m)\frac{t}{\sigma}, & \hat f > c
\end{cases}
$$

### 3.2.2 Residual split decomposition

Before switching to reader-friendly variable names, it is useful to separate the split rule into the two regimes induced by the fixed operator cost $c$. Let

$$
\rho_{\text{operator}} = \frac{s}{\sigma}, \qquad
\rho_{\text{member}} = \frac{t}{\sigma}
$$

denote the operator and member pool-share ratios.

If the realized pool allocation does not cover the fixed cost,

$$
\hat f \le c
$$

then the operator absorbs the full realized reward and members receive nothing:

$$
r_{\text{operator}}(\hat f,c,m,\rho_{\text{operator}}) = \hat f,
\qquad
r_{\text{member}}(\hat f,c,m,\rho_{\text{member}}) = 0
$$

If instead the realized pool allocation is large enough to cover the fixed cost,

$$
\hat f > c
$$

let

$$
\mu(\hat f,c,m) := m(\hat f-c),
\qquad
\psi(\hat f,c,m) := (1-m)(\hat f-c)
$$

where $\mu(\hat f,c,m)$ is the operator margin extracted from the residual reward and $\psi(\hat f,c,m)$ is the remaining amount to be shared proportionally across stake holders.

The split then becomes

$$
r_{\text{operator}}(\hat f,c,m,\rho_{\text{operator}})
= c + \mu(\hat f,c,m) + \psi(\hat f,c,m)\,\rho_{\text{operator}}
$$

$$
r_{\text{member}}(\hat f,c,m,\rho_{\text{member}})
= \psi(\hat f,c,m)\,\rho_{\text{member}}
$$

This makes the three-layer structure explicit: fixed cost first, operator margin second, proportional sharing of the remainder third.

### 3.2.3 Reader-Friendly

Let the operator and member pool-share ratios be defined as:

$$
\rho^{\text{operator}}_{i} := \frac{\pi^{\text{pledged}}_{i}}{\sigma^{\text{totalStaked}}_{i}},
\qquad
\rho^{\text{member}}_{i} := \frac{\sigma^{\text{poolMember}}_{\text{delegated},i}}{\sigma^{\text{totalStaked}}_{i}}
$$

If the realized pool allocation does not cover the fixed cost,

$$
PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}}
$$

then the operator absorbs the full realized reward and members receive nothing:

$$
Reward^{\text{operator}} = PoolPot^{\text{actual}}_{i}
$$

$$
Reward^{\text{member}} = 0
$$

If instead the realized pool allocation is large enough to cover the fixed cost, define the three layers of the split directly as:

$$
Cost := Cost^{\text{operator}}_{\text{fixed}}
$$

$$
Margin := \mu^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}
\right)
$$

$$
Share := \left(1-\mu^{\text{operator}}\right)
\left(
PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}
\right)
$$

Then the split becomes:

$$
Reward^{\text{operator}} = Cost + Margin + Share\,\rho^{\text{operator}}_{i}
$$

$$
Reward^{\text{member}} = Share\,\rho^{\text{member}}_{i}
$$

This makes the split easy to read: fixed cost first, operator margin second, and proportional sharing of the remainder third.

## 3.3 Structural Decomposition

<!-- TODO: decompose the split into its three layers and their economic roles -->
<!-- Key axes: fixed cost as base compensation, margin as proportional take, residual as delegator yield -->

## 3.4 Mainnet Observations

<!-- TODO: integrate data from pool-landscape-mainnet.md -->
<!-- Key patterns: minPoolCost usage, margin distribution, fee-war dynamics, ROS variance across pool tiers -->

## 3.5 Problems

<!-- TODO: clearly define each problem with evidence -->
<!-- Expected problems at this layer:
  - minPoolCost distortion: 170 ADA fixed cost penalizes small pools relative to their total reward
  - Fee wars: zero-margin race to bottom erodes operator sustainability
  - ROS inequality: delegator return varies significantly by pool despite similar performance
  - Operator insolvency: break-even threshold sits at ~3M ADA under current fee structure
-->

## 3.6 Prior Art & Cited Solutions

<!-- TODO: cite solutions from the report and community discussions that are outside stream scope -->
<!-- e.g. minPoolMargin community consensus, two-stage parameter introduction via hardfork -->

## 3.7 CIP Evaluation: Fee Structure Adjustments

> Both CIP-0023 and CIP-0082 operate at this layer.
> They modify the operator/member split rule without changing the pool-level reward curve.

### 3.7.1 CIP-0023 — Fair Min Fees

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the cleaned formulas)
  3. Which problems from §3.5 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. what value for minPoolRate?)
-->

### 3.7.2 CIP-0082 — Improved Rewards Scheme

<!-- TODO: same structure as 3.7.1, note the staged approach -->

# Sub-reports

Each pipeline stage is backed by a dedicated empirical analysis containing the formula derivations, mainnet data, figures, and reproduction scripts.

| Stage | Sub-report | Scope |
| --- | --- | --- |
| §1 Treasury & Pool Pots | [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) | Epoch-pot assembly, reserve trajectory, fee analysis, return-to-reserve mechanism |
| §2 Pools Distribution | [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md) | Reward curve formulas, distribution efficiency, pool landscape, entity analysis |
| §3 Operator / Delegator | *Not yet extracted* | Fee-split formulas remain in this document (§3.2) pending sub-report creation |
