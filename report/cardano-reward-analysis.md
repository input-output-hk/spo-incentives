# Cardano Reward Pipeline: From Design Intent to Mainnet Reality

## Motivation

The *Shelley-era Delegation and Incentives Design Specification* (SL-D1) defined the economic rules that were meant to guide Cardano toward a stable, decentralized equilibrium of $k$ well-funded stake pools.
Five years of mainnet operation have exposed significant divergences between those design intentions and the on-chain reality.
The *Analysis of Cardano's Incentive Mechanism* (Lopez de Lara, 2025; hereafter the *Incentive Mechanism Analysis*) documented the key findings empirically: a stratified equilibrium with 873 active operators below the 3M ADA viability threshold, a pledge mechanism that is functionally irrelevant for most pools, and a capital-constrained environment where ~16B ADA remains outside consensus.

This document decomposes the SL-D1 reward pipeline into three stages and, for each stage, follows the same analytical arc: describe the intended design, confront it with mainnet observations, synthesise the observations into a *problem statement*, and verify whether a formal *Cardano Problem Statement* (CPS) exists for that problem in the CIP governance process. Where a CPS exists, the document evaluates the CIPs proposed as solutions against it. Where no CPS exists, the document identifies the gap and produces one.

Each pipeline stage is backed by a dedicated sub-report containing the formula derivations, mainnet observations, and empirical evidence that grounds the corresponding CPS.

## Canonical sources

- **SL-D1**: *Engineering Design Specification for Delegation and Incentives in Cardano-Shelley* (Kant et al.).
- **Empirical baseline**: *Analysis of Cardano's Incentive Mechanism* (Lopez de Lara, 2025).
- **CIP/CPS process**: [CIP-0001](https://cips.cardano.org/cip/CIP-0001) (CIP Process), [CIP-9999](https://cips.cardano.org/cips/cip9999) (Cardano Problem Statements).


## Table of Contents

- [1. Reward Flow](#1-reward-flow)
  - [1.1 Treasury & Pool Pots Distribution](#11-treasury--pool-pots-distribution)
    - [1.1.1 Flow Overview](#111-flow-overview)
    - [1.1.2 Mainnet Observations](#112-mainnet-observations) 
    - [1.1.3 Problem Induction → CPS: Funding the Protocol Without a Reserve](#113-problem-induction--cps-funding-the-protocol-without-a-reserve)
  - [1.2 Pools Distribution](#12-pools-distribution)
    - [1.2.1 Flow Overview](#121-flow-overview)
    - [1.2.2 Mainnet Observations](#122-mainnet-observations) 
    - [1.2.3 Problem Induction → CPS: Closing the Consensus Incentive Gap](#123-problem-induction--cps-closing-the-consensus-incentive-gap)
    - [1.2.4 Proposed Solutions Evaluation](#124-proposed-solutions-evaluation)
      - [1.2.4.1 CIP-0050 — Pledge Leverage Cap](#1241-cip-0050--pledge-leverage-cap)
      - [1.2.4.2 CIP-0037 — Dynamic Pledge-Linked Saturation](#1242-cip-0037--dynamic-pledge-linked-saturation)
  - [1.3 Operator / Delegator Distribution](#13-operator--delegator-distribution)
    - [1.3.1 Flow Overview](#131-flow-overview)
    - [1.3.2 Formulas](#132-formulas)
      - [1.3.2.1 SL-D1 (Original)](#1321-sl-d1-original)
      - [1.3.2.2 Residual split decomposition](#1322-residual-split-decomposition)
      - [1.3.2.3 Reader-Friendly](#1323-reader-friendly)
    - [1.3.3 Structural Decomposition](#133-structural-decomposition)
    - [1.3.4 Mainnet Observations](#134-mainnet-observations)
    - [1.3.5 Problems](#135-problems)
    - [1.3.6 Prior Art & Cited Solutions](#136-prior-art--cited-solutions)
    - [1.3.7 CIP Evaluation: Fee Structure Adjustments](#137-cip-evaluation-fee-structure-adjustments)
      - [1.3.7.1 CIP-0023 — Fair Min Fees](#1371-cip-0023--fair-min-fees)
      - [1.3.7.2 CIP-0082 — Improved Rewards Scheme](#1372-cip-0082--improved-rewards-scheme)
- [Sub-reports](#sub-reports)
- [Appendices](#appendices)
  - [A. Notation Convention](#a-notation-convention)
  - [B. Symbol Mapping (SL-D1 → Reader-Friendly)](#b-symbol-mapping-sl-d1--reader-friendly)
  - [C. Detailed Variable Glossary](#c-detailed-variable-glossary)
- [Sandbox](#sandbox) *(draft material)*

## 1. Reward Flow

### 1.1 Treasury & Pool Pots Distribution

#### 1.1.1 Flow Overview

Before any individual pool receives rewards, the protocol must first answer one question:
**how much ADA is available for distribution this epoch?**

This stage assembles the **epoch pot** from three on-chain sources — transaction fees, non-refundable deposits, and a monetary expansion draw from the reserve — then splits it in two: a fixed share goes to the **treasury**, and the remainder becomes the **pools pot**, the total budget that the next stage (§1.2) will distribute across individual pools.

Two design choices embedded at this stage matter for the rest of the analysis:

- **Cooperative-behavior gate.** The monetary expansion draw is scaled by the ratio of blocks actually produced to blocks expected. If pools collectively miss slots, the entire epoch pot shrinks. This discourages sabotage but also means the pot depends on aggregate network health.

- **Fixed split rule.** The treasury/pools ratio is a protocol constant ($\tau$), not a function of network activity or reserve level. It does not adapt as the balance between fees and expansion shifts over time.

> **Formulas.** The epoch-pot assembly and treasury/pools split formulas — from the original SL-D1 notation through a reader-friendly rewrite to mainnet parameterization — are in the dedicated sub-report: [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) — §2.1.

#### 1.1.2 Mainnet Observations

The epoch-level analysis (epochs 208–617) yields four observations at this pipeline stage. The full data, visuals, and methodology are in the dedicated sub-report: [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md).

| # | Observation | Summary |
| --- | --- | --- |
| **O1** | **The epoch pot is a single-source budget** | Monetary expansion provides ~99.8% of the pot. Fees cover ~0.19%; self-sufficiency would require 12–16× current capacity. Block production is reliable (η ≈ 0.977). |
| **O2** | **The reserve has crossed its half-life** | Reserve is half-depleted (13.29B → 6.53B ADA) in 5.5 years. Significant reward pressure expected at epochs 1000–1200 (~2028–2029). |
| **O3** | **The reward mechanism operates at ~44% of its potential** | Only ~6.8M of ~15.5M ADA pools pot reaches operators/delegators — the rest returns to reserve. 4.55B ADA cumulative (~70% of current reserve) exists because of this. Root cause: ~17B ADA (~44%) does not participate in delegation. |
| **O4** | **Reward parameters have never been adjusted** | $\rho = 0.3\%$ and $\tau = 20\%$ are unchanged since Shelley. Neither has been subject to a governance proposal. |

> **Scope note.** Observations O1–O4 are structural to the epoch-budget layer. No existing CIP targets this stage — they all operate downstream (§1.2, §1.3). These observations document the sustainability context within which all downstream proposals operate.

#### 1.1.3 Problem Induction → CPS: Funding the Protocol Without a Reserve

Each observation above constrains what the system can do. Read together, they reveal what it *cannot* do.

The epoch pot is funded almost entirely by monetary expansion from the reserve (O1). That reserve is finite and has already crossed its half-life (O2). Transaction fees — the only sustainable alternative — cover ~0.19% of the pot today, and even at full realistic throughput would reach only ~1.3% (O1). Closing this gap requires 12–16× today's capacity, implying both a throughput upgrade (Leios) and a structural increase in transaction demand — neither of which is on a defined timeline. Meanwhile, the two parameters governing the draw ($\rho$, $\tau$) have never been reviewed since Shelley launch (O4), and no governance process exists to do so.

These constraints compose into a single structural problem: **the reward system has no viable path from reserve-funded to fee-funded sustainability.** The reserve is depleting on a known schedule, the only alternative revenue source is orders of magnitude too small, and the parameters governing the transition have never been subject to governance. This is not a failure of any individual parameter — it is a *design gap* at the epoch-budget layer. No protocol-level or governance-level instrument currently exists to manage this transition.

O3 — the ~44% distribution efficiency — is not a problem *at this layer*. It is a consequence of participation levels, which are shaped by incentives defined downstream (§1.2, §1.3). But it interacts directly with the sustainability problem: activating inactive ADA would improve distribution efficiency while accelerating reserve consumption. Any solution to the epoch-budget problem must account for this tension — and any change to the downstream incentive structure (§1.2, §1.3) that affects participation will feed back into reserve dynamics here.

**CPS identified.** No *Cardano Problem Statement* (CPS) has been formally written for this problem. The CIP governance process requires that solutions (CIPs) be scoped against a well-defined problem statement (CPS). This foundational sustainability problem has remained formally unstated. This analysis identifies the gap and produces the missing CPS — *Funding the Protocol Without a Reserve* — derived from the mainnet evidence in the dedicated [sub-report](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) and defined in [`sub-flows/treasury-and-pool-pots-distribution/cps/`](sub-flows/treasury-and-pool-pots-distribution/cps/).

The epoch budget sets the ceiling for everything that follows. But how that budget reaches individual participants — and whether the distribution mechanism itself works as intended — is a separate question. That is the subject of §1.2.

### 1.2 Pools Distribution

#### 1.2.1 Flow Overview

This stage takes the **pools pot** ($PoolsPot^{\text{epoch}}$) produced by §1.1 and distributes it across individual pools. The output is a per-pool allocation ($PoolPot^{\text{actual}}_i$) that feeds into §1.3 (operator/delegator split).

For each pool $i$, the protocol performs three steps:

1. **Saturation clipping.** Both total stake ($\sigma_i$) and pledge ($s_i$) are capped at the saturation threshold $z_0 = 1/k$. This prevents any single pool from capturing a disproportionate share.

2. **Reward curve evaluation.** A reward function $f$ computes the pool's *optimal* allocation from its clipped stake and pledge. The curve has two components: a **base stake term** (proportional to delegation) and a **pledge-bonus term** (nonlinear, governed by $a_0$). The pledge bonus is meant to reward operator commitment ("skin in the game").

3. **Performance adjustment.** The optimal allocation is scaled by apparent performance $\bar{p}_i$ to produce the *actual* allocation. Pools that miss blocks receive less. If the registered pledge is not met, the allocation is zeroed entirely.

Any rewards not distributed (because $\sum_i \hat{f}_i < R$) return to the reserve — this is the mechanism behind O3 in §1.1.2.

Two design choices matter for the rest of the analysis:

- **Pledge sensitivity via $a_0$.** The parameter $a_0$ controls how much additional reward a pool can earn through pledge. At $a_0 = 0.3$, the pledge bonus represents at most ~23% of the optimal allocation. Whether this is sufficient to meaningfully incentivise pledge is a central question at this layer.

- **Uniform saturation threshold.** All pools share the same cap $z_0 = 1/k$. There is no mechanism to differentiate saturation based on pledge level or pool characteristics.

> **Formulas.** The pool-level reward formulas — from the original SL-D1 reward curve through the normalized saturation coordinates rewrite to mainnet parameterization — are in the dedicated sub-report: [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md) — §2.3.

#### 1.2.2 Mainnet Observations

The pool-level analysis (epochs 208–618) yields four observations at this pipeline stage. The full data, figures, entity analysis, and reproduction scripts are in the dedicated sub-report: [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md).

| # | Observation | Summary |
| --- | --- | --- |
| **O1** | **The pledge bonus is functionally irrelevant at realistic pledge levels** | At median pledge the bonus adds ~0.006% to rewards — undetectable. Yield on pledge capital (0.68%/yr at best) is below passive delegation yield (~2.3%/yr). 22.1% of the pools pot (~3.4M ADA/epoch) returns to reserve unused because the $a_0$ curve is too flat. |
| **O2** | **The pool landscape is stratified far from the k = 500 design target** | 73% of pools (1,987) sit below the 3M ADA viability line, carrying only 2.7% of active stake. Only 7 pools reach saturation — 1.4% of the k = 500 target. |
| **O3** | **Saturation is structurally underutilised** | Active stake fills 56.5% of theoretical capacity (k × z₀). At most 282 pools could saturate under perfect redistribution. The near-saturation zone holds only 104 pools. |
| **O4** | **The delegation market is capital-constrained** | 16.75B ADA (43.5%) does not participate in delegation — this is the binding constraint. k = 500 is feasible only at full participation. 85 MPO entities control ~51% of staked ADA. |

> **Scope note.** Observations O1–O3 are structural to the pool-distribution layer. O4 (capital constraint) is the same upstream condition documented at §1.1 O3 — it sets the playing field within which the reward curve operates.

#### 1.2.3 Problem Induction → CPS: Closing the Consensus Incentive Gap

Each observation above constrains what the reward curve can accomplish. Read together, they reveal a gap between the equilibrium the mechanism was designed to produce and the equilibrium it actually produces.

The pledge bonus is functionally irrelevant (O1): at realistic pledge levels it adds ~0.006% to rewards, invisible to delegators and uneconomic for operators. The pool landscape is stratified far from the $k = 500$ target (O2): 73% of pools sit below viability, and only 7 reach saturation. Saturation capacity is structurally underutilised (O3): active stake fills 56.5% of theoretical capacity, so at most 282 pools could saturate. And the delegation market is capital-constrained (O4): 16.75B ADA (43.5%) does not participate, which is the binding constraint on everything the reward curve can accomplish.

The pool reward curve is not merely a reward-distribution mechanism. It is the protocol's only tool for shaping the operator ecosystem that secures consensus. Its purpose is to produce an *incentive-compatible equilibrium*: a state where rational, self-interested participants — operators competing on pledge commitment, delegators rewarding the most committed operators — collectively maintain the security invariants the consensus layer depends on (decentralisation, Sybil resistance, accountability).

The formal game-theoretic properties of this mechanism were established in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020), which proves that $k$ pools is a Nash equilibrium under certain assumptions. The engineering specification *SL-D1* translates those results into protocol-level formulas. However, neither document provides a **narrative description of the game as it should play out** — the players, their motivations, how they enter and progress, and the equilibrium they should converge toward. Evaluating whether the mechanism works requires a clear picture of what working looks like. That narrative description is produced in a dedicated companion document: [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md).

The observations above, confronted with this intended design, reveal two interrelated failures:

**The playing field is half the size the design assumed.** $k = 500$ implicitly required near-complete participation. At 56.5%, the target is structurally unreachable — at most 282 pools could saturate (O3). The saturation cap binds for only 7 pools (O2). No formula change at this layer can close this gap; it requires upstream intervention to bring inactive ADA into delegation.

**The incentive game does not converge toward the intended equilibrium.** The reward curve's theoretical optimum ($\pi = 1, \nu = 1$) is a fully-pledged private pool with no delegator — eliminating the accountability mechanism at the endgame. Reaching it requires 77M ADA at a yield of ~0.68%/yr, below passive delegation (~2.3%/yr) — making the endgame economically irrational. The progression is invisible: the pledge bonus adds ~0.006% at median pledge, undetectable by delegators (O1). The entry creates a viability cliff, not a ramp (O2). The dominant strategy at every level — entry, progression, endgame — is to maximise delegation and minimise pledge, the exact opposite of what consensus security requires. The full analysis of these distortions, from endgame down to entry, is in [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md) §5.

The evidence confirms this at scale: 95.6% of the pledge-bonus budget returns to reserve unused (O1), the independent operator base has collapsed to 283 viable operators (O5), the incentive-responsive field holds only 36% of active stake (O6), and structural populations totalling 7.39B ADA cannot pledge by architectural constraint (O4).

**CPS identified.** No *Cardano Problem Statement* (CPS) has been formally written for this problem. CIP-0050 and CIP-0037 both propose modifications to the reward curve at this layer — but they were designed without a shared, formal problem definition to scope them against. This analysis identifies the gap and produces the missing CPS — *Closing the Consensus Incentive Gap* — derived from the mainnet evidence in the dedicated [sub-report](sub-flows/pools-distribution/mainnet-analysis/README.md) and defined in [`sub-flows/pools-distribution/cps/`](sub-flows/pools-distribution/cps/). The CPS evaluation of CIP-0050 and CIP-0037 follows in §1.2.4.

#### 1.2.4 Proposed Solutions Evaluation

CIP-0050 and CIP-0037 are listed as *Proposed Solutions* in the CPS [*Closing the Consensus Incentive Gap*](sub-flows/pools-distribution/cps/README.md). Both modify the reward curve at this layer — CIP-0050 by capping pledge leverage, CIP-0037 by linking saturation to pledge. They were authored before the CPS existed: each proposal defines its own local problem statement and evaluates itself against it. This section evaluates them against the CPS instead.

Evaluating a CIP against a CPS requires a shared understanding of what the mechanism *should* produce — the intended game, its players, their progression, and the equilibrium they should converge toward. The formal game-theoretic foundation exists in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020), which proves that $k$ pools is a Nash equilibrium under certain assumptions. SL-D1 translates those results into formulas. But neither document provides a narrative description of how the game should play out in practice — the kind of description needed to assess whether a proposed curve modification actually moves the equilibrium in the right direction. That narrative is produced in [*The Intended Game*](sub-flows/pools-distribution/the-intended-game/README.md), which serves as the evaluation baseline for the CIP assessments below.

The evaluation criteria derive directly from the CPS goals: does the proposal align the endgame with the security model? Does it make pledge a legible competitive dimension? Does it create a credible entry-to-endgame progression? Does it ensure the dominant strategy aligns with consensus security? And does it work within the participation constraint (~56.5% active stake)?

##### 1.2.4.1 CIP-0050 — Pledge Leverage Cap

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the sub-report formulas)
  3. Which problems from §1.2.3 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. parametrization of L)
-->

##### 1.2.4.2 CIP-0037 — Dynamic Pledge-Linked Saturation

<!-- TODO: same structure as 1.2.4.1 -->

### 1.3 Operator / Delegator Distribution

#### 1.3.1 Flow Overview

These formulas define how a pool's realized allocation is split between the operator and the rest of the pool participants.
The split happens only after the pool-level reward has already been computed and adjusted by apparent performance.

The distribution logic is sequential:

- first, the operator fixed cost is covered
- second, the operator margin is applied to the remaining amount
- finally, the residual reward is distributed proportionally across stake holders

In this final step, the operator still receives a stake-proportional share through the pledge held inside the pool, while delegators receive the complementary share.

#### 1.3.2 Formulas

The operator and member rewards are two complementary views of the same split rule applied to the realized pool allocation.
Once the pool-level reward has been computed, the split follows the same sequence:

- cover the operator fixed cost first
- apply the operator margin to the remaining amount
- distribute the residual proportionally across stake holders

Under this rule, the operator receives both the explicit operator share and the stake-proportional share attached to the pledge held inside the pool, while each member receives a stake-proportional share of the residual amount.

##### 1.3.2.1 SL-D1 (Original)

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


##### 1.3.2.2 Residual split decomposition

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

##### 1.3.2.3 Reader-Friendly

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

#### 1.3.3 Structural Decomposition

<!-- TODO: decompose the split into its three layers and their economic roles -->
<!-- Key axes: fixed cost as base compensation, margin as proportional take, residual as delegator yield -->

#### 1.3.4 Mainnet Observations

<!-- TODO: integrate data from pool-landscape-mainnet.md -->
<!-- Key patterns: minPoolCost usage, margin distribution, fee-war dynamics, ROS variance across pool tiers -->

#### 1.3.5 Problems

<!-- TODO: clearly define each problem with evidence -->
<!-- Expected problems at this layer:
  - minPoolCost distortion: 170 ADA fixed cost penalizes small pools relative to their total reward
  - Fee wars: zero-margin race to bottom erodes operator sustainability
  - ROS inequality: delegator return varies significantly by pool despite similar performance
  - Operator insolvency: break-even threshold sits at ~3M ADA under current fee structure
-->

#### 1.3.6 Prior Art & Cited Solutions

<!-- TODO: cite solutions from the report and community discussions that are outside stream scope -->
<!-- e.g. minPoolMargin community consensus, two-stage parameter introduction via hardfork -->

#### 1.3.7 CIP Evaluation: Fee Structure Adjustments

> Both CIP-0023 and CIP-0082 operate at this layer.
> They modify the operator/member split rule without changing the pool-level reward curve.

##### 1.3.7.1 CIP-0023 — Fair Min Fees

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the cleaned formulas)
  3. Which problems from §1.3.5 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. what value for minPoolRate?)
-->

##### 1.3.7.2 CIP-0082 — Improved Rewards Scheme

<!-- TODO: same structure as 1.3.7.1, note the staged approach -->

---

## Sub-reports

Each pipeline stage is backed by a dedicated empirical analysis containing the formula derivations, mainnet data, figures, and reproduction scripts.

| Stage | Sub-report | Scope |
| --- | --- | --- |
| §1.1 Treasury & Pool Pots | [`Treasury & Pool Pots Distribution`](sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) | Epoch-pot assembly, reserve trajectory, fee analysis, return-to-reserve mechanism |
| §1.2 Pools Distribution | [`The Pools Pot Distribution Gaps`](sub-flows/pools-distribution/mainnet-analysis/README.md) | Reward curve formulas, distribution efficiency, pool landscape, entity analysis |
| §1.3 Operator / Delegator | *Not yet extracted* | Fee-split formulas remain in this document (§1.3.2) pending sub-report creation |

---

## Appendices

### A. Notation Convention

<!-- TODO: migrate from sandbox §8 -->

### B. Symbol Mapping (SL-D1 → Reader-Friendly)

<!-- TODO: migrate from sandbox §9 -->

### C. Detailed Variable Glossary

<!-- TODO: migrate from sandbox §10 -->

---

## Sandbox

> **Everything below this line is draft / work-in-progress material.**
> It will be restructured and integrated into the main document as sections are finalized.

---

## [SANDBOX] Cross-Cutting Analysis

### 2.1 Problem–Pipeline Map

<!-- TODO: table mapping each identified problem to the pipeline stage(s) where it originates -->
<!-- Columns: Problem | Pipeline Stage | Root Cause | Addressed by CIP(s) -->

### 2.2 CIP Coverage Matrix

<!-- TODO: matrix showing which CIPs address which problems, and whether they are complements or substitutes -->
<!-- Reuse the combination logic from the sandbox material -->

### 2.3 Combination Logic

<!-- TODO: migrate and clean up the combination compatibility analysis from sandbox §7 -->
<!-- Fee layer × Stake-cap layer independence, clean combinations, edge cases -->

### 2.4 Gaps & Open Questions

<!-- TODO: problems that no CIP addresses, parametrization unknowns, simulation needs -->

---

## 2. Fee Structure Adjustments equivalence

### 2.1 CIP-0023 margin floor

#### 2.1.1 Formulas

##### 2.1.1.1 SL-D1 (Original)

$$
m_{\text{eff}} := \max(m, m_{\min})
$$

##### 2.1.1.2 Reader-Friendly

$$
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, \mu^{\text{operator}}_{\text{min}})
$$

### 2.2 CIP-0023 operator/member substitution

#### 2.2.1 Formulas

##### 2.2.1.1 SL-D1 (Original)

$$
r_{\text{operator}}^{(23)} = r_{\text{operator}}(\hat f,c,m_{\text{eff}},s,\sigma),\qquad
r_{\text{member}}^{(23)} = r_{\text{member}}(\hat f,c,m_{\text{eff}},t,\sigma)
$$

##### 2.2.1.2 Reader-Friendly

$$
{Reward^{\text{operator}}}^{(23)} =
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(23)} =
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

### 2.3 CIP-0082 Stage 1

#### 2.3.1 Formulas

##### 2.3.1.1 SL-D1 (Original)

$$
c := 170
$$

##### 2.3.1.2 Reader-Friendly

$$
Cost^{\text{operator}}_{\text{fixed}} := 170
$$

### 2.4 CIP-0082 Stage 2

#### 2.4.1 Formulas

##### 2.4.1.1 SL-D1 (Original)

$$
c := 0,\qquad m_{\text{eff}} := \max(m, 0.03)
$$

##### 2.4.1.2 Reader-Friendly

$$
Cost^{\text{operator}}_{\text{fixed}} := 0,\qquad
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, 0.03)
$$

##### 2.4.1.3 SL-D1 (Original)

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

##### 2.4.1.4 Reader-Friendly

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

### 2.5 CIP-0082 Stage 3 and Stage 4

#### 2.5.1 Formulas

##### 2.5.1.1 SL-D1 (Original)

$$
k:=750 \Rightarrow z_0=\frac{1}{750},\qquad
k:=1000 \Rightarrow z_0=\frac{1}{1000}
$$

##### 2.5.1.2 Reader-Friendly

$$
k^{\text{protocol}}_{\text{targetPools}}:=750 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{750},\qquad
k^{\text{protocol}}_{\text{targetPools}}:=1000 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{1000}
$$

## 3. Pledge & Curve Adjustments equivalence

### 3.1 CIP-0050 capped eligible stake

#### 3.1.1 Formulas

##### 3.1.1.1 SL-D1 (Original)

$$
\sigma'_L := \min(\sigma, z_0, Ls)
$$

##### 3.1.1.2 Reader-Friendly

$$
\sigma^{\text{totalStaked},(L)}_{\text{capped}} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

### 3.2 CIP-0050 reward curve substitution

#### 3.2.1 Formulas

##### 3.2.1.1 SL-D1 (Original)

$$
f^{(50)}(s,\sigma)
= \frac{R}{1+a_0}
\left(
\sigma'_L + s'a_0\cdot\frac{\sigma'_L - s'\left(\frac{z_0-\sigma'_L}{z_0}\right)}{z_0}
\right)
$$

##### 3.2.1.2 Reader-Friendly

$$
PoolPot^{\text{optimal},(50)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(L)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

### 3.3 CIP-0037 dynamic saturation

#### 3.3.1 Formulas

##### 3.3.1.1 SL-D1 (Original)

$$
z_{\text{dyn}}(s) := z_0 \cdot \phi(s)
$$

##### 3.3.1.2 Reader-Friendly

$$
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})
:=
k^{\text{protocol}}_{\text{saturation}}\cdot \phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
$$

##### 3.3.1.3 SL-D1 (Original)

$$
\phi(s)=\max\!\left(\epsilon,\min\!\left(1,\frac{s}{s_{\text{ref}}}\right)\right)
$$

##### 3.3.1.4 Reader-Friendly

$$
\phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
= \max\left(
\epsilon^{\text{protocol}}_{\text{saturationFloor}},
\min\left(1,\frac{\pi^{\text{pledged}}}{\sigma^{\text{owner}}_{\text{pledgeRef}}}\right)
\right)
$$

### 3.4 CIP-0037 capped stake and reward curve substitution

#### 3.4.1 Formulas

##### 3.4.1.1 SL-D1 (Original)

$$
\sigma'_{37}:=\min(\sigma,z_{\text{dyn}}(s))
$$

##### 3.4.1.2 Reader-Friendly

$$
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

##### 3.4.1.3 SL-D1 (Original)

$$
f^{(37)}(s,\sigma)
= \frac{R}{1+a_0}
\left(
\sigma'_{37} + s'a_0\cdot\frac{\sigma'_{37} - s'\left(\frac{z_0-\sigma'_{37}}{z_0}\right)}{z_0}
\right)
$$

##### 3.4.1.4 Reader-Friendly

$$
PoolPot^{\text{optimal},(37)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(37)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

## 4. Status Quo

Status quo summary:

- Every pool faces the same global saturation threshold, $k^{\text{protocol}}_{\text{saturation}}=\frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$.
- Pool reward production depends on capped stake, capped pledge, and the global skin-in-the-game factor $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$.
- After performance adjustment, the realized pool allocation is split by fixed cost first, then by operator margin and stake ownership.
- If the operator fails to meet the registered pledge in an epoch, the pool allocation is zeroed.

### 4.1 Treasury & Pool Pots Distribution

These formulas define the epoch-level reward budget before any pool-level reward curve is applied.
They first build the gross pot from fees, non-refundable deposits, and reserve-sourced monetary expansion, then split that budget between the treasury and the pool side.

#### 4.1.1 Formulas

##### 4.1.1.1 Reader-Friendly

$$
Pot^{\text{epoch}}
= Fee^{\text{epoch}}_{\text{tx}}
+
Deposit^{\text{epoch}}_{\text{nonRefundable}}
+
\min\left(\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}},1\right)\rho^{\text{monetaryExpansion}}_{\text{rate}}(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

$$
PoolsPot^{\text{epoch}}
:=
(1-\tau^{\text{treasury}}_{\text{rate}})\,Pot^{\text{epoch}}
$$

$$
TreasuryPot^{\text{epoch}}
:=
\tau^{\text{treasury}}_{\text{rate}}\,Pot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} + TreasuryPot^{\text{epoch}}
= Pot^{\text{epoch}}
$$

##### 4.1.1.2 Mainnet Reader-Friendly

$$
Pot^{\text{epoch}}
= Fee^{\text{epoch}}_{\text{tx}}
+
Deposit^{\text{epoch}}_{\text{nonRefundable}}
+
\min\left(\frac{Blocks^{\text{epoch}}_{\text{produced}}}{21{,}600},1\right)\cdot 0.3\% \cdot \left(45\,\text{billion} - Supply^{\text{system}}_{\text{circulating}}\right)
$$

$$
PoolsPot^{\text{epoch}}
:=
80\% \cdot Pot^{\text{epoch}}
$$

$$
TreasuryPot^{\text{epoch}}
:=
20\% \cdot Pot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} + TreasuryPot^{\text{epoch}}
= Pot^{\text{epoch}}
$$

##### 4.1.1.3 Concept glossary

**Pot^{epoch}**  
Total reward pot available for distribution at the end of the epoch. It aggregates transaction fees, non‑refundable deposits, and the monetary expansion drawn from the reserve.

**Fee^{epoch}_{tx}**  
Total transaction fees collected during the epoch from all transactions included in blocks.

**Deposit^{epoch}_{nonRefundable}**  
Deposits that become permanently locked or effectively removed from circulation during the epoch (for example deposits that are not reclaimed).

**Blocks^{epoch}_{produced}**  
Number of blocks actually produced on chain during the epoch.

**Blocks^{epoch}_{expected}**  
Expected number of blocks during an epoch according to the protocol parameters.

**ρ^{monetaryExpansion}_{rate}**  
Monetary expansion rate controlling how much ADA is drawn from the reserve to fund epoch rewards.

**Supply^{system}_{total}**  
Maximum ADA supply defined by the protocol.

**Supply^{system}_{circulating}**  
Current circulating supply of ADA already issued into the system.

**T_∞**  
Maximum ADA supply defined by the protocol (same conceptual quantity as the total supply limit).

**T**  
Current circulating supply used when computing the remaining reserve.

**τ^{treasury}_{rate}**  
Treasury tax rate applied to the epoch pot before rewards are distributed to pools and delegators.

**PoolsPot^{epoch}**  
Portion of the epoch reward pot allocated to stake pools and delegators after the treasury share is taken.

**TreasuryPot^{epoch}**  
Portion of the epoch reward pot allocated to the treasury.

### 4.2 Pools Distribution

These formulas define how the epoch-level pools pot is distributed across individual pools before the operator/member split.
For each pool $i$, they first compute the theoretical pool entitlement from stake, pledge, and saturation, then apply apparent performance to obtain the actual pool allocation.

#### 4.2.1 Formulas

##### 4.2.1.1 Reader-Friendly

$$
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked}}_{\text{capped},i}
+
\pi^{\text{pledged}}_{\text{capped},i}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked}}_{\text{capped},i}
-
\pi^{\text{pledged}}_{\text{capped},i}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked}}_{\text{capped},i}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

$$
PoolPot^{\text{actual}}_{i}
:=
\bar p^{\text{pool}}_{\text{apparent},i}
\cdot
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
$$

$$
\sum_i PoolPot^{\text{actual}}_{i} \le PoolsPot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} - \sum_i PoolPot^{\text{actual}}_{i}
\quad \text{is not paid out and remains accounted in } (Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

##### 4.2.1.2 Mainnet Reader-Friendly

$$
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
= \frac{PoolsPot^{\text{epoch}}}{1+30\%}
\left(
\sigma^{\text{totalStaked}}_{\text{capped},i}
+
\pi^{\text{pledged}}_{\text{capped},i}\cdot 30\%
\cdot
\frac{
\sigma^{\text{totalStaked}}_{\text{capped},i}
-
\pi^{\text{pledged}}_{\text{capped},i}
\left(
\frac{0.2\%-\sigma^{\text{totalStaked}}_{\text{capped},i}}{0.2\%}
\right)
}{
0.2\%
}
\right)
$$

$$
PoolPot^{\text{actual}}_{i}
:=
\bar p^{\text{pool}}_{\text{apparent},i}
\cdot
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
$$

$$
\sum_i PoolPot^{\text{actual}}_{i} \le PoolsPot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} - \sum_i PoolPot^{\text{actual}}_{i}
\quad \text{is not paid out and remains accounted in } (Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

##### 4.2.1.3 Concept glossary

| Reader-Friendly | Meaning | Mainnet baseline |
| --- | --- | --- |
| $PoolsPot^{\text{epoch}}$ | Pool-side budget entering the pool reward curve | Inherited from section `4.1` |
| $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Skin-in-the-game effect strength | $30\%$ |
| $k^{\text{protocol}}_{\text{saturation}}$ | Pool saturation threshold | $0.2\%$ |
| $\sigma^{\text{totalStaked}}_{i}$ | Pool $i$ total-staked share, i.e. pledged $+$ delegated, before the saturation cap is applied | Dynamic |
| $\pi^{\text{pledged}}_{i}$ | Pool $i$ pledged share inside $\sigma^{\text{totalStaked}}_{i}$, before the saturation cap is applied | Dynamic |
| $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | Pool $i$ total-staked share after saturation cap | $\min(\sigma^{\text{totalStaked}}_{i},0.2\%)$ |
| $\pi^{\text{pledged}}_{\text{capped},i}$ | Pool $i$ pledged share after saturation cap | $\min(\pi^{\text{pledged}}_{i},0.2\%)$ |
| $PoolPot^{\text{optimal}}_{i}$ | Theoretical pool-$i$ allocation before performance adjustment | Dynamic |
| $\bar p^{\text{pool}}_{\text{apparent},i}$ | Apparent performance multiplier for pool $i$ | No fixed baseline; pool- and epoch-specific, typically near $1$ over time for a well-performing pool |
| $PoolPot^{\text{actual}}_{i}$ | Actual pool-$i$ allocation after performance adjustment | Dynamic |
| $\sum_i PoolPot^{\text{actual}}_{i}$ | Total actual allocations distributed across all pools | Dynamic |
| $PoolsPot^{\text{epoch}}-\sum_i PoolPot^{\text{actual}}_{i}$ | Undistributed remainder not paid out to pools. SL-D1 says it is "sent back to the reserves"; read that here as remaining accounted in $(T_{\infty}-T)$ / $(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})$, not as a literal round-trip transfer. | Dynamic |

### 4.3 Operator reward

$$
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
= \begin{cases}
PoolPot^{\text{actual}}_{i}, & PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}} \\
Cost^{\text{operator}}_{\text{fixed}}
+
\left(PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}\right)
\left(
\mu^{\text{operator}}
+
\left(1-\mu^{\text{operator}}\right)\frac{\pi^{\text{pledged}}_{i}}{\sigma^{\text{totalStaked}}_{i}}
\right), & PoolPot^{\text{actual}}_{i} > Cost^{\text{operator}}_{\text{fixed}}
\end{cases}
$$

### 4.4 Member reward

$$
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
= \begin{cases}
0, & PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}} \\
\left(PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}\right)\left(1-\mu^{\text{operator}}\right)\frac{\sigma^{\text{poolMember}}_{\text{delegated},i}}{\sigma^{\text{totalStaked}}_{i}},
& PoolPot^{\text{actual}}_{i} > Cost^{\text{operator}}_{\text{fixed}}
\end{cases}
$$

### 4.5 Pledge enforcement

$$
\text{if pledged amount is not met in epoch } \Rightarrow PoolPot^{\text{actual}}_{i} = 0
$$

---

## 5. Fee Structure Adjustments

### 5.1 CIP-0023 (minimum operator margin floor)

Proposal summary:

- CIP-0023 introduces a protocol minimum operator margin, $\mu^{\text{operator}}_{\text{min}}$.
- It does not change reward production, saturation, or the fixed fee.
- The only change is in the operator/member split: if a pool registers a lower margin, the protocol clamps it up to the minimum during reward calculation.
- The policy intent is to reduce zero-margin fee wars while preserving the rest of the Shelley reward pipeline.

Reward production is unchanged. Fee split uses margin floor:

$$
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, \mu^{\text{operator}}_{\text{min}})
$$

Use $\mu^{\text{operator}}_{\text{floored}}$ in operator/member formulas:

$$
{Reward^{\text{operator}}}^{(23)} =
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(23)} =
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

Practical effect:
If a pool advertises a margin below the protocol floor, delegators still generate the same pool allocation as under status quo, but a larger share of that allocation is redirected to the operator through $\mu^{\text{operator}}_{\text{floored}}$.

---

### 5.2 CIP-0082 (staged fee-floor and k changes)

Proposal summary:

- CIP-0082 is a staged reform rather than a single formula swap.
- Stage 1 lowers the protocol fixed-fee floor to 170 ADA.
- Stage 2 removes the fixed-fee floor and replaces it with a minimum operator rate of 3%.
- Stages 3 and 4 increase the target number of pools, which lowers the saturation threshold from $\frac{1}{500}$ to $\frac{1}{750}$ and then $\frac{1}{1000}$ if those governance decisions are adopted.

#### 5.2.1 Stage 1

Stage 1 keeps the same reward equations, but reduces the protocol floor applied to fixed operator cost:

$$
Cost^{\text{operator}}_{\text{fixed}} := 170
$$

#### 5.2.2 Stage 2

Stage 2 is the core mechanism change: the fixed-fee floor is removed, and a minimum operator rate is enforced in the split formula.

$$
Cost^{\text{operator}}_{\text{fixed}} := 0,\qquad
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, 0.03)
$$

Equivalent CIP statement:

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

Use $Cost^{\text{operator}}_{\text{fixed}}=0$ and $\mu^{\text{operator}}_{\text{floored}}$ in the same split functions:

$$
{Reward^{\text{operator}}}^{(82,\text{Stage 2})}
= Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
0,
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(82,\text{Stage 2})}
= Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
0,
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

#### 5.2.3 Stage 3 and Stage 4

Stages 3 and 4 do not change the reward split logic directly. They change the protocol target pool count, so the same baseline reward function is recomputed with a smaller saturation size:

$$
k^{\text{protocol}}_{\text{targetPools}}:=750 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{750},\qquad
k^{\text{protocol}}_{\text{targetPools}}:=1000 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{1000}
$$

Recompute:

$$
\sigma^{\text{totalStaked}}_{\text{capped}}=\min(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}}),\qquad
\pi^{\text{pledged}}_{\text{capped}}=\min(\pi^{\text{pledged}},k^{\text{protocol}}_{\text{saturation}})
$$

in the same baseline reward function.

Practical effect:
Stage 2 shifts operator compensation away from fixed-fee protection and toward proportional fees, while Stages 3 and 4 make saturation tighter by design so the same total stake is spread across more target pools.

---

## 6. Pledge & Curve Adjustments

### 6.1 CIP-0050 (pledge leverage cap)

Proposal summary:

- CIP-0050 introduces a new leverage parameter, $L^{\text{protocol}}_{\text{pledgeLeverage}}$.
- A pool can only earn full rewards on stake that is supported by both the global saturation threshold and enough pledge.
- In practice, reward-eligible stake is capped at $L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}$ in addition to the normal saturation cap.
- The policy intent is to penalize large under-pledged pools and reduce MPO leverage without imposing a blanket penalty on small pools that are not over-leveraged.

Introduce pledge leverage:

$$
\sigma^{\text{totalStaked},(L)}_{\text{capped}} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by $\sigma^{\text{totalStaked},(L)}_{\text{capped}}$:

$$
PoolPot^{\text{optimal},(50)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(L)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

Then:

$$
PoolPot^{\text{actual},(50)}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal},(50)}_{i}
$$

with the same operator/member split forms.

Practical effect:
Once a pool grows beyond the leverage-supported level, additional stake no longer increases rewards. Delegators then have an incentive to move to pools whose pledge still supports full reward earning.

---

### 6.2 CIP-0037 (dynamic pledge-linked saturation)

Proposal summary:

- CIP-0037 replaces the single global saturation threshold with a pool-specific saturation threshold that depends on pledge.
- Low-pledge pools saturate earlier, while high-pledge pools preserve more headroom up to the global cap.
- The scaling rule uses a reference pledge level, $\sigma^{\text{owner}}_{\text{pledgeRef}}$, and a minimum floor, $\epsilon^{\text{protocol}}_{\text{saturationFloor}}$, so small pools are not forced all the way down to zero effective saturation.
- The policy intent is to make growth capacity depend more directly on capital commitment rather than only on raw delegated stake.

Dynamic saturation depends on pledge:

$$
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})
:=
k^{\text{protocol}}_{\text{saturation}}\cdot \phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
$$

$$
\phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
= \max\left(
\epsilon^{\text{protocol}}_{\text{saturationFloor}},
\min\left(1,\frac{\pi^{\text{pledged}}}{\sigma^{\text{owner}}_{\text{pledgeRef}}}\right)
\right)
$$

Capped pool stake becomes:

$$
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by $\sigma^{\text{totalStaked},(37)}_{\text{capped}}$ in the same baseline reward function:

$$
PoolPot^{\text{optimal},(37)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(37)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

and:

$$
PoolPot^{\text{actual},(37)}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal},(37)}_{i}
$$

Practical effect:
Unlike CIP-0050, which adds an extra leverage cap, CIP-0037 changes the saturation threshold itself. The reward curve therefore becomes pool-specific: the same delegated stake can be fully rewarded in one pool but oversaturated in another depending on pledge.

---

## 7. Combination Logic

### 7.1 Combination compatibility (technical only)

This section is purely technical. It only describes which formulas can be combined cleanly in this document, and which combinations require an additional composition rule to be defined explicitly.

Two independent layers are modified across these proposals:

- Fee layer: the operator/member split after the per-pool allocation has already been computed. This is where `baseline`, `CIP-0023`, and `CIP-0082` operate.
- Stake-cap layer: the reward-eligible pool stake used inside $PoolPot^{\text{optimal}}_{i}$. This is where `baseline`, `CIP-0050`, and `CIP-0037` operate.

Because the two layers are independent in the current formulation, one rule from each layer can be combined directly.

#### 7.1.1 Clean combinations already defined in this document

| Fee rule | Stake-cap rule | Technical status | Meaning |
| --- | --- | --- | --- |
| baseline | baseline | Defined | Status quo |
| CIP-0023 | baseline | Defined | Minimum operator margin floor only |
| CIP-0082 | baseline | Defined | Fee reform only |
| baseline | CIP-0050 | Defined | Pledge leverage cap only |
| baseline | CIP-0037 | Defined | Dynamic pledge-linked saturation only |
| CIP-0023 | CIP-0050 | Defined by composition | Margin floor + leverage cap |
| CIP-0023 | CIP-0037 | Defined by composition | Margin floor + dynamic saturation |
| CIP-0082 | CIP-0050 | Defined by composition | Fee reform + leverage cap |
| CIP-0082 | CIP-0037 | Defined by composition | Fee reform + dynamic saturation |

#### 7.1.2 Same-layer combinations that are not canonical in this document

- `CIP-0023 + CIP-0082` is not treated as a standard combination here because both proposals modify the fee layer. A single effective fee rule must be chosen for the split step.
- `CIP-0050 + CIP-0037` is not treated as a standard combination here because both proposals modify the stake-cap layer. The document currently models them as alternative ways to redefine reward-eligible stake.

#### 7.1.3 Technically possible but requiring an explicit extra definition

The main advanced case is `CIP-0050 + CIP-0037`. If both are applied together, the natural composite capped stake is:

$$
\sigma^{\text{totalStaked},(50+37)}_{\text{capped}}
:=
\min\left(
\sigma^{\text{totalStaked}},
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}),
L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}
\right)
$$

This combined cap can then replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ in the same baseline reward function. However, this document does not treat it as canonical unless that composite rule is explicitly adopted.

For `CIP-0023 + CIP-0082`, a combination is also technically possible, but only after defining precedence for the fee layer. In practice that means deciding whether `CIP-0082` supersedes `CIP-0023`, or whether one rule contributes parameters to a single merged effective fee rule.

---

### 7.2 Composition rule (combined scenarios)

- In the default formulation of this document, choose exactly one stake-cap rule: baseline / CIP-0050 / CIP-0037.
- Choose exactly one fee rule: baseline / CIP-0023 / CIP-0082.
- Cross-layer combinations are obtained by applying both selected rules in the same canonical pipeline.
- Same-layer combinations require an explicit extra definition before they become canonical formulas in this document.
- Apply the selected rules in the same canonical pipeline:

$$
Pot^{\text{epoch}}
\rightarrow
\left(TreasuryPot^{\text{epoch}},PoolsPot^{\text{epoch}}\right)
\rightarrow
PoolPot^{\text{optimal}}_{i}
\rightarrow
PoolPot^{\text{actual}}_{i}
\rightarrow
\left(Reward^{\text{operator}},Reward^{\text{member}}\right)
$$

## 8. Notation convention

- Player/entity goes in superscript: $x^{\text{player}}$
- Variable role/type goes in subscript: $x_{\text{role}}$
- Example used in this document: $\mu^{\text{operator}}$
- Greek base-symbol semantics used here:
  - $\sigma$: stake share variables (pronounced "SIG-muh" in English)
  - $\pi$: pledge share variables (pronounced "pie" in English)
  - $\bar p$: apparent performance factor
  - $\mu$: margin variables (pronounced "myoo" in English)

## 9. Symbol mapping (SL-D1 -> Reader-Friendly)

| SL-D1 symbol | Reader-Friendly symbol | Mapping detail |
| --- | --- | --- |
| $k$ | $k^{\text{protocol}}_{\text{targetPools}}$ | Direct rename |
| $z_0$ | $k^{\text{protocol}}_{\text{saturation}}$ | $k^{\text{protocol}}_{\text{saturation}} := \frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$ |
| $\sigma$ | $\sigma^{\text{totalStaked}}_{i}$ | $\sigma$ is reserved for total-staked-share variables (relative stake fractions), pronounced "SIG-muh" in English. The index $i$ identifies the pool. |
| $s$ | $\pi^{\text{pledged}}_{i}$ | $\pi$ is used for pledged-share variables to distinguish pledged stake from the full pool stake, pronounced "pie" in English. The index $i$ identifies the pool. |
| $\sigma'$ | $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | $\sigma^{\text{totalStaked}}_{\text{capped},i} := \min(\sigma^{\text{totalStaked}}_{i}, k^{\text{protocol}}_{\text{saturation}})$ |
| $s'$ | $\pi^{\text{pledged}}_{\text{capped},i}$ | $\pi^{\text{pledged}}_{\text{capped},i} := \min(\pi^{\text{pledged}}_{i}, k^{\text{protocol}}_{\text{saturation}})$ |
| $a_0$ | $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Direct rename |
| $R$ | $PoolsPot^{\text{epoch}}$ | Renamed for semantic precision: this is the post-treasury pool budget entering the reward curve, not the amount ultimately paid out. |
| $f$ | $PoolPot^{\text{optimal}}_{i}$ | Renamed to make the per-pool allocation explicit and indexed by pool $i$. |
| $\bar p$ | $\bar p^{\text{pool}}_{\text{apparent},i}$ | $p$ denotes performance; the bar denotes apparent/realized performance multiplier for pool $i$. |
| $\hat f$ | $PoolPot^{\text{actual}}_{i}$ | Renamed to make the realized per-pool allocation explicit and indexed by pool $i$. |
| $c$ | $Cost^{\text{operator}}_{\text{fixed}}$ | Direct rename |
| $m$ | $\mu^{\text{operator}}$ | $\mu$ denotes margin (pronounced "myoo" in English). |
| $t$ | $\sigma^{\text{poolMember}}_{\text{delegated},i}$ | Direct rename with pool index $i$. |

Additional reward-pot terms:

| SL-D1 symbol | Reader-Friendly symbol | Mapping detail |
| --- | --- | --- |
| $\tau$ | $\tau^{\text{treasury}}_{\text{rate}}$ | Direct rename |
| $F$ | $Fee^{\text{epoch}}_{\text{tx}}$ | Direct rename |
| $D$ | $Deposit^{\text{epoch}}_{\text{nonRefundable}}$ | Direct rename |
| $\eta$ | $\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}}$ | Keep the epoch block-production ratio explicit rather than introducing a standalone named symbol. |
| $\rho$ | $\rho^{\text{monetaryExpansion}}_{\text{rate}}$ | Monetary expansion parameter in SL-D1. |
| $T_{\infty}$ | $Supply^{\text{system}}_{\text{total}}$ | Total supply cap/reference |
| $T$ | $Supply^{\text{system}}_{\text{circulating}}$ | Current circulating supply |

## 10. Detailed variable glossary

Conventions:

| Rule | Meaning |
| --- | --- |
| $\sigma$ variables | Relative stake shares (fractions of total active stake), not absolute ADA |
| $Reward_{\cdot}$, $Cost_{\cdot}$, $Fee_{\cdot}$, $Deposit_{\cdot}$, $Reserve_{\cdot}$ | ADA-denominated quantities |
| $\tau^{\text{treasury}}_{\text{rate}}$, $\rho^{\text{monetaryExpansion}}_{\text{rate}}$, $\mu^{\text{operator}}$ | Unitless rates/fractions |

Core protocol control variables:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $k^{\text{protocol}}_{\text{targetPools}}$ | Protocol target number of pools (SL-D1 $k$) | Integer, $>0$ | Decentralization target anchor |
| $k^{\text{protocol}}_{\text{saturation}}$ | Saturation threshold per pool | Relative share | $k^{\text{protocol}}_{\text{saturation}}=\frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$ |
| $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Skin-in-the-game effect strength (SL-D1 $a_0$) | Fraction, $\ge 0$ | Higher value increases pledge sensitivity |

Pool stake and pledge state:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\sigma^{\text{totalStaked}}_{i}$ | Total staked share in pool $i$ | Relative share | Total staked means pledged + delegated stake before the saturation cap is applied |
| $\pi^{\text{pledged}}_{i}$ | Pool-$i$ pledged share | Relative share | Pledged component inside $\sigma^{\text{totalStaked}}_{i}$ |
| $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | Pool-$i$ total-staked share after saturation cap | Relative share | $\min(\sigma^{\text{totalStaked}}_{i},k^{\text{protocol}}_{\text{saturation}})$ |
| $\pi^{\text{pledged}}_{\text{capped},i}$ | Pool-$i$ pledged share after saturation cap | Relative share | $\min(\pi^{\text{pledged}}_{i},k^{\text{protocol}}_{\text{saturation}})$ |
| $\sigma^{\text{poolMember}}_{\text{delegated},i}$ | Single member stake delegated into pool $i$ | Relative share | Split term uses $\sigma^{\text{poolMember}}_{\text{delegated},i}/\sigma^{\text{totalStaked}}_{i}$ |

Epoch reward-pot inputs:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\tau^{\text{treasury}}_{\text{rate}}$ | Treasury take rate | Fraction | Applied before pool distribution |
| $Fee^{\text{epoch}}_{\text{tx}}$ | Epoch transaction fees | ADA | Reward-pot input |
| $Deposit^{\text{epoch}}_{\text{nonRefundable}}$ | Epoch non-refundable deposits | ADA | Reward-pot input |
| $Blocks^{\text{epoch}}_{\text{produced}}$ | Blocks produced during the epoch | Count | Used in the SL-D1 performance ratio $\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}}$ |
| $Blocks^{\text{epoch}}_{\text{expected}}$ | Expected blocks for the epoch under ideal conditions | Count / expectation | Kept explicit to avoid treating $\eta$ as a standalone protocol parameter |
| $Supply^{\text{system}}_{\text{circulating}}$ | Current circulating supply | ADA | Used as the $T$ term in $T_{\infty}-T$ |
| $\rho^{\text{monetaryExpansion}}_{\text{rate}}$ | Monetary expansion rate | Fraction | Scales the monetary-expansion term $\left(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}}\right)$ |
| $Supply^{\text{system}}_{\text{total}}$ | Total supply cap/reference | ADA | Used as the $T_{\infty}$ term; $Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}}$ is the reserve balance entering the formula |
| $Pot^{\text{epoch}}$ | Epoch gross reward pot before treasury split | ADA | Helper concept: fee + deposits + reserve-sourced monetary expansion |
| $PoolsPot^{\text{epoch}}$ | Epoch pool pot after treasury split | ADA | Net pool budget entering the reward curve before pool-level underdistribution |
| $TreasuryPot^{\text{epoch}}$ | Epoch treasury pot | ADA | Treasury share cut from the same gross pot before pool distribution |

Pool performance and payout split:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\bar p^{\text{pool}}_{\text{apparent},i}$ | Apparent pool-$i$ performance multiplier | Fraction | Typically near $[0,1]$ |
| $PoolPot^{\text{optimal}}_{i}$ | Optimal pool-$i$ allocation before performance adjustment | ADA | Reward-curve output for pool $i$ before performance adjustment |
| $PoolPot^{\text{actual}}_{i}$ | Actual pool-$i$ allocation | ADA | $PoolPot^{\text{actual}}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal}}_{i}$ |
| $Cost^{\text{operator}}_{\text{fixed}}$ | Fixed operator fee | ADA/epoch | Charged first from the pool-$i$ allocation |
| $\mu^{\text{operator}}$ | Operator variable margin | Fraction | Usually in $[0,1]$ |
| $Reward^{\text{operator}}$ | Total operator reward | ADA | Fixed cost + margin + owner share |
| $Reward^{\text{member}}$ | Member/delegator reward | ADA | Remainder after fixed cost and margin split |

CIP-specific extension variables:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\mu^{\text{operator}}_{\text{min}}$ | Minimum operator margin floor | Fraction | CIP-0023 / CIP-0082 |
| $\mu^{\text{operator}}_{\text{floored}}$ | Effective operator margin | Fraction | $\max(\mu^{\text{operator}},\mu^{\text{operator}}_{\text{min}})$ |
| $L^{\text{protocol}}_{\text{pledgeLeverage}}$ | Pledge leverage multiplier | Scalar | CIP-0050 cap with $L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}$ |
| $\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})$ | Dynamic saturation threshold | Relative share | CIP-0037 pledge-dependent saturation |
| $\sigma^{\text{owner}}_{\text{pledgeRef}}$ | Reference pledge level | Relative share | CIP-0037 normalization anchor |
| $\epsilon^{\text{protocol}}_{\text{saturationFloor}}$ | Minimum floor for dynamic saturation scale | Fraction | Floor in $\phi^{\text{protocol}}_{\text{saturationScale}}$ |
