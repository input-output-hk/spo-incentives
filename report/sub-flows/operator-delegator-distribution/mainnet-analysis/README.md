# The Operator's Cut — A Mainnet Analysis of Intra-Pool Reward Sharing

_Built on 2026/03/31 from mainnet data at epoch `614` (settled) plus historical analysis from epoch `211` (405 epochs)._

## Objective

This report analyses the **intra-pool reward split** — the third and final stage of Cardano's reward pipeline — and traces the structural forces that determine how much of each pool's reward reaches delegators versus operators. It extends the empirical baseline established in the [*Analysis of Cardano's Incentive Mechanism*](https://github.com/input-output-hk/spo-incentives/blob/main/report.pdf) (Lopez de Lara, 2025; hereafter the *Incentive Mechanism Analysis*) and operates downstream of the companion reports [*Treasury & Pool Pots Distribution*](../../treasury-and-pool-pots-distribution/mainnet-analysis/) (stage 1) and [*The Pools Pot Distribution Gaps*](../../pools-distribution/mainnet-analysis/) (stage 2).

Every epoch, once the reward curve assigns a total reward $\hat{f}$ to each pool, a second mechanism activates: the **intra-pool split**. The pool operator extracts a fixed cost $c$ and a proportional margin $m$; the remainder is distributed pro-rata among all delegators (including the operator's own stake). At epoch 614, this mechanism processed **6.75M ADA** across 875 rewarded pools — but the headline aggregate (24.3% operator take) conceals three radically different strategies. Adopting the Hollow–Private pledge spectrum from the upstream analysis ([§2.4.2](../../../README.md#242-progression--balanced-as-intended-but-private-by-design)), this report classifies entities by **owner-stake ratio** (owner active stake / pool active stake) across their pool fleets. Three strategies emerge along this spectrum: the **hollow strategy** (owner-stake ratio < 10%, 445 entities, 771 pools, 18.10B ADA, op_take=13.34%) where entities depend entirely on external delegation; the **balanced strategy** (10–95% owner-stake, 46 entities, 60 pools, 0.77B ADA, op_take=10.75%) where entities and delegators share capital with genuine alignment; and the **private strategy** (≥ 95% owner-stake, 11 entities, 44 pools, 2.29B ADA, op_take=99.97%) where entities are operator-funded. Remarkably, 495 of 502 entities (98.6%) apply a single pure strategy across all their pools, demonstrating high strategic consistency. Within hollow-strategy entities, a sub-population of 48 "hollow captive" pools (margin ≥ 99.9%, typically exchanges and custodians) extract 100% via margin, leaving 723 genuine hollow pools at 7.7% operator take. The entity-level analysis reveals that margin competition is broadly active in the genuine hollow market (median entity margin 1.0%, stake-weighted 8.9%) but fixed cost, not margin, is the dominant extraction channel. Balanced-strategy entities form the smallest population but analytically most significant: they are where the pledge mechanism produces genuine alignment, with many pools carrying Material or High pledge tags and median owner-ratio 26.4%.

The argument proceeds in six steps:

1. **The formula** (§2). The SL-D1 intra-pool reward-sharing specification — from the original design through a residual-split decomposition to a reader-friendly rewrite and mainnet parameterization. The mechanism is sequential: fixed cost first, margin on the remainder, then pro-rata distribution. A critical protocol detail: when $\hat{f} < c$, the operator takes $\hat{f}$ (not $c$) — the effective fixed cost is $\min(c, \hat{f})$.

2. **Three operator strategies** (§3). The 502 entities operating rewarded pools classify into three populations by the owner-stake ratio of their fleet: hollow (< 10%), balanced (10–95%), and private (≥ 95%). Strategy classification and consistency are documented in the upstream analysis ([§2.4.3.1](../../../README.md#2431-what-mainnet-reveals)); this report applies the same framework and adds the reward-split decomposition per population (§5 private, §6 balanced, §7 hollow).

3. **The delegator's strategy** (§4). The delegator's action space reduces to a single decision — which pool — governed by two criteria: yield (annualised ROS, driven by pool performance, fees, and saturation) and the ethics of pool selection (commitment, independence, transparency). The yield spread between well-run pools is narrow, making the delegator's choice partly an expression of values — supporting commitment and decentralisation beyond what the formula prices.

4. **The private strategy universe** (§5). The 11 entities following the private strategy (44 pools, 2.29B ADA, op_take=99.97%) are operator-funded and absorb 99.97% of their rewards as operator take. Margin is an accounting choice (vast majority set ≥ 99.9%), fixed cost negligible. Paradoxically, entities in this group often carry Low or Zero pledge tags despite owning the capital and facing no custodial constraint — the pledge mechanism does not appear to attract commitment even where conditions are most favourable. The intra-pool split is structurally trivial here; the analytical value lies in the pledge dimension.

5. **The balanced strategy population** (§6). The 46 entities following the balanced strategy (60 pools, 0.77B ADA, op_take=10.75%) split capital between themselves and delegators with genuine alignment. Margins are low and many pools carry Material or High pledge tags — genuine skin-in-the-game. This is the only population where the pledge mechanism produces meaningful operator alignment.

6. **The hollow strategy market** (§7). The 445 entities following the hollow strategy (771 pools, 18.10B ADA, op_take=13.34%) depend entirely on external delegation, forming the public delegation market, with 48 hollow captive pools (exchanges, custodians: 100% extraction) distorting the aggregate. Excluding them, the genuine market (723 pools) operates at 7.7% operator take — with fixed cost (4.9%) slightly exceeding margin (2.8%). At the entity level, median margin is 1.5% and stake-weighted mean is 8.9%, confirming active margin competition. The dominant extraction in the genuine market is the fixed-cost floor, not margin.

7. **Structural implications** (§8). The fixed-cost floor creates a regressive tax on small-pool delegators. Margin competition is active in the genuine hollow market (median entity margin 1.5%) but the fixed cost, being a flat ADA amount, penalises small pools disproportionately. The two-regime structure — where fixed cost dominates small pools and margin dominates large pools — has direct consequences for any future mechanism revision.

All counts and amounts use epoch **614** (the latest settled epoch with complete reward data). Source data: `koios_pool_history_mainnet.csv`, `koios_pool_owner_history_mainnet.csv`, `koios_pool_list_mainnet.csv`, `mpo_entity_pool_mapping_mainnet.csv` (Koios + entity attribution from the [*pools-distribution*](../../pools-distribution/mainnet-analysis/) flow).

## Contents

1. [Mainnet Observations](#1-mainnet-observations)
2. [The formula — intra-pool reward sharing](#2-the-formula--intra-pool-reward-sharing)
   - 2.1 [SL-D1 (Original)](#21-sl-d1-original)
   - 2.2 [Residual split decomposition](#22-residual-split-decomposition)
   - 2.3 [Reader-friendly formulation](#23-reader-friendly-formulation)
   - 2.4 [Mainnet parameterization](#24-mainnet-parameterization)
   - 2.5 [Concept glossary](#25-concept-glossary)
3. [Three operator strategies](#3-three-operator-strategies)
   - 3.1 [Strategy classification and consistency](#31-strategy-classification)
   - 3.2 [The split at a glance](#32-the-split-at-a-glance)
4. [The delegator's strategy](#4-the-delegators-strategy)
   - 4.1 [What the formula offers](#41-what-the-formula-offers)
   - 4.2 [The yield criterion](#42-the-yield-criterion)
     - 4.2.1 [How much does a delegator earn?](#421-how-much-does-a-delegator-earn)
     - 4.2.2 [Where does Cardano stand? — the yield in context](#422-where-does-cardano-stand--the-yield-in-context)
     - 4.2.3 [Three frames for evaluating the yield](#423-three-frames-for-evaluating-the-yield)
     - 4.2.4 [The yield is declining — and the trajectory is predictable](#424-the-yield-is-declining--and-the-trajectory-is-predictable)
     - 4.2.5 [The yield spread — how different are pools?](#425-the-yield-spread--how-different-are-pools)
       - 4.2.5.1 [Cross-strategy trajectory](#4251-cross-strategy-trajectory)
       - 4.2.5.2 [Inside the hollow market](#4252-inside-the-hollow-market)
       - 4.2.5.3 [The balanced premium — real or artefact?](#4253-the-balanced-premium--real-or-artefact)
       - 4.2.5.4 [Dead pools — hollow in name, zero in yield](#4254-dead-pools--hollow-in-name-zero-in-yield)
       - 4.2.5.5 [SPO versus MPO](#4255-spo-versus-mpo)
       - 4.2.5.6 [Oversaturation drag](#4256-oversaturation-drag)
       - 4.2.5.7 [Variance decomposition — luck versus structure](#4257-variance-decomposition--luck-versus-structure)
     - 4.2.6 [What drives the structural spread?](#426-what-drives-the-structural-spread)
     - 4.2.7 [The narrowness of the yield surface](#427-the-narrowness-of-the-yield-surface)
   - 4.3 [Beyond yield — the ethics of pool selection](#43-beyond-yield--the-ethics-of-pool-selection)
   - 4.4 [Myopic and non-myopic delegation](#44-myopic-and-non-myopic-delegation)
   - 4.5 [The delegator's leverage](#45-the-delegators-leverage)
5. [The private strategy](#5-the-private-strategy)
   - 5.1 [Composition](#51-composition)
   - 5.2 [Intra-pool split](#52-intra-pool-split)
   - 5.3 [Margin behaviour](#53-margin-behaviour)
   - 5.4 [Pledge behaviour](#54-pledge-behaviour)
   - 5.5 [Key findings — private strategy](#55-key-findings--private-strategy)
6. [The balanced strategy](#6-the-balanced-strategy)
   - 6.1 [Composition and structure](#61-composition-and-structure)
   - 6.2 [Intra-pool split](#62-intra-pool-split)
   - 6.3 [Margin behaviour](#63-margin-behaviour)
   - 6.4 [The pledge signal — where it works](#64-the-pledge-signal--where-it-works)
   - 6.5 [Key findings — balanced strategy](#65-key-findings--balanced-strategy)
7. [The hollow strategy](#7-the-hollow-strategy)
   - 7.1 [The hollow captive sub-population](#71-the-hollow-captive-sub-population)
   - 7.2 [The genuine market — current snapshot (epoch 614)](#72-the-genuine-market--current-snapshot-epoch-614)
   - 7.3 [Historical evolution of the split](#73-historical-evolution-of-the-split)
   - 7.4 [The two components — fixed cost vs margin](#74-the-two-components--fixed-cost-vs-margin)
   - 7.5 [The effective tax on delegators](#75-the-effective-tax-on-delegators)
   - 7.6 [Fixed-cost dominance at the small-pool end](#76-fixed-cost-dominance-at-the-small-pool-end)
   - 7.7 [Margin distribution — by pool and by entity](#77-margin-distribution--by-pool-and-by-entity)
   - 7.8 [Fee parameter adoption](#78-fee-parameter-adoption)
   - 7.9 [MPO vs SPO operator take](#79-mpo-vs-spo-operator-take)
   - 7.10 [Top entities by operator take](#710-top-entities-by-operator-take)
   - 7.11 [Key findings — hollow strategy](#711-key-findings--hollow-strategy)
8. [Structural implications](#8-structural-implications)
   - 8.1 [Two regimes, one mechanism](#81-two-regimes-one-mechanism)
   - 8.2 [The fixed-cost floor as a regressive tax on small pools](#82-the-fixed-cost-floor-as-a-regressive-tax-on-small-pools)
   - 8.3 [Margin competition in the hollow strategy market](#83-margin-competition-in-the-hollow-strategy-market)
   - 8.4 [Open questions](#84-open-questions)
9. [Reproduction](#9-reproduction)

## 1. Mainnet Observations

| # | Observation | Section | Nature |
| --- | --- | --- | --- |
| | **O1 — Three disjoint strategies coexist on-chain** | | |
| F1.1 | 445 entities following the hollow strategy (771 pools, 88.1% of pool count) control 18.10B ADA (85.6%), with owner-stake ratio < 10% — these entities depend entirely on external delegation | §3 | Structural |
| F1.2 | 46 entities following the balanced strategy (60 pools, 6.9% of pool count) control 0.77B ADA (3.6%), with owner-stake ratio 10–95% — entities with genuine capital commitment alongside external delegation | §3 | Structural |
| F1.3 | 11 entities following the private strategy (44 pools, 5.0% of pool count) control 2.29B ADA (10.8%), with owner-stake ratio ≥ 95% — operator-funded entities with 99.97% operator take | §3 | Structural |
| F1.4 | 495 of 502 entities (98.6%) apply a single pure strategy across all their pools; only 7 are hybrid (near-threshold edge cases) — strategies are deliberate, coherent choices | §3.2 | Consistency |
| F1.5 | 48 hollow-strategy pools (stakes ≥ 99.9% margin, median owner-ratio ~1.75%) distort the hollow-strategy aggregate from 7.7% to 12.72% operator take | §7.1 | Methodological |
| | **O2 — In the genuine hollow-strategy market, fixed cost slightly exceeds margin** | | |
| F2.1 | Hollow-strategy aggregate (771 pools): 13.34% operator take — distorted by 48 hollow captive pools | §7.2 | Epoch 614 |
| F2.2 | Genuine hollow-strategy market (723 pools): operator take 7.7% — fixed cost 4.4%, margin 3.6% | §7.2 | Fixed cost > margin |
| F2.3 | Delegators receive 4.89M ADA (87.28% of hollow) for pro-rata distribution | §7.2 | Hollow market |
| | **O3 — Entity-level margin analysis reveals broad competition** | | |
| F3.1 | 491 distinct entities operate in the hollow market (78 MPO entities, 413 SPO entities) | §7.7 | Entity-level |
| F3.2 | Entity-level median margin: 1.0%; stake-weighted mean: 8.9% — margin competition active but hollow captive pools distort the weighted average | §7.7 | Low margins |
| F3.3 | 277 entities (56.4%) operate below 2% margin; 59 (12.0%) exceed 5% | §7.7 | Competitive |
| F3.4 | 35 entities use mixed margin policies across their pool fleets | §7.7 | Tiered pricing |
| | **O4 — The fixed cost is a regressive tax on small-pool delegators** | | |
| F4.1 | Effective tax ranges from ~4% (large low-margin pools) to 100% (sub-viable pools where $c \geq \hat{f}$) | §7.5 | Pool-size driven |
| F4.2 | Fixed-cost share follows a hyperbola: $\min(c, \hat{f}) / \hat{f}$, decaying as $1/\sigma$ | §7.6 | Mathematical identity |
| F4.3 | 91.6% of hollow-strategy pools declare the minimum fixed cost (340 ADA) — the floor is the norm | §7.8 | Near-universal |
| | **O5 — SPO pools bear a heavier effective tax than MPO pools** | | |
| F5.1 | Hollow SPO pools (413): 13.44% operator take — driven by higher fixed-cost incidence on smaller pools | §7.9 | Size effect |
| F5.2 | Hollow MPO pools (415): 12.46% operator take — scale dilutes the fixed-cost burden | §7.9 | Economies of scale |
| | **O6 — Balanced-strategy entities are analytically significant despite small share** | | |
| F6.1 | 46 balanced-strategy entities (6.9% of pool count): median owner-ratio 26.4%, many with Material/High pledge tags | §6 | Pledge signal |
| F6.2 | Balanced-strategy operator take 12.8% — fixed cost dominates because pools are small; margin low | §6.2 | Structural |
| F6.3 | This is where the pledge mechanism produces meaningful alignment — unique to this population | §6.4 | Incentive design |

### The big picture

**What the formula does.** Once the reward curve assigns a total reward $\hat{f}$ to a pool, the intra-pool split extracts operator compensation in two steps: a **fixed cost** $\min(c, \hat{f})$ subtracted first, then a **proportional margin** $m$ applied to the remainder $\max(\hat{f} - c, 0)$. Everything left is distributed pro-rata among all pool members by stake share — including the operator's own stake.

**Three operator strategies.** At epoch 614, 502 entities operate rewarded pools — but they do not follow a single template. Following the Hollow–Private pledge spectrum from the upstream analysis, this report classifies entities by **dominant owner-stake ratio** across their fleet: the axis runs from hollow (external delegation dominates) through balanced (genuine capital-sharing) to private (operator-funded). 445 entities follow the hollow strategy (771 pools, 18.10B ADA), 46 follow the balanced strategy (60 pools, 0.77B ADA), and 11 follow the private strategy (44 pools, 2.29B ADA). Remarkably, 98.6% of entities apply a single pure strategy across their entire fleet. The pool-level heterogeneity is strategic consistency at the entity level.

![Three Strategies — Entity-Level View](figures/three_strategies.png)

**Strategy consistency.** Among 502 entities, 495 (98.6%) operate pools that all fall into the same strategy bin. Only 7 entities are hybrid (spanning multiple bins), and they cluster near threshold boundaries. This extraordinary consistency shows that entities choose a fundamental strategy and apply it coherently across their pool fleet. An entity does not run one hollow pool and one private pool — it commits to a strategy.

**The hollow-strategy market — with a caveat.** Among entities following the hollow strategy, operator take is **13.34%** in aggregate (771 pools). But 48 of these pools are *hollow captive* — exchanges and custodians that own almost none of their stake (mean owner-ratio 1.75%) yet set margin ≥ 99.9%, extracting everything. Excluding them, the genuine market (723 pools) operates at **7.7%** operator take — split between fixed cost (4.4%) and margin (3.6%). Fixed cost slightly exceeds margin, reflecting a population where 91.6% declare the minimum 340 ADA cost.

**Entity-level analysis.** Counting by pool overcounts fee policies: entities operating many pools pursue a single (or a few) policy decisions per strategy, not one per pool. Across 491 distinct entities in the hollow market, the median margin is **1.0%** and 56.4% of entities operate below 2%. Margin competition is broadly active. The dominant extraction in the hollow market is the fixed-cost floor, not margin.

**The balanced-strategy population.** The 46 entities following the balanced strategy (6.9% of pool count, 3.6% of stake, median owner-ratio 26.4%) form an analytically crucial segment where the pledge mechanism produces genuine alignment. Many carry Material or High pledge tags — genuine skin-in-the-game. They are the smallest segment but structurally important: they demonstrate that entities with real capital at stake behave differently and compete fiercely on fees.

**Why it matters for mechanism design.** The two-regime structure reveals that the intra-pool split does not operate as a single, uniform mechanism. The fixed-cost floor creates a regressive tax that penalises small-pool delegators disproportionately, while margin competition functions effectively in the large-pool regime. Any revision to the fee structure should account for this bifurcation — the small-pool regime and the large-pool regime respond to different parameters and require distinct analytical treatment.

## 2. The formula — intra-pool reward sharing

These formulas define how a pool's realized allocation is split between the operator and the rest of the pool participants.
The split happens only after the pool-level reward has already been computed and adjusted by apparent performance.

The distribution logic is sequential:

- first, the operator fixed cost is covered
- second, the operator margin is applied to the remaining amount
- finally, the residual reward is distributed proportionally across stake holders

In this final step, the operator still receives a stake-proportional share through the pledge held inside the pool, while delegators receive the complementary share.

The intra-pool split was specified in [*Design Specification for Delegation and Incentives in Cardano*](https://github.com/IntersectMBO/cardano-ledger/releases/latest/download/shelley-delegation.pdf) (Kant, Brünjes & Coutts, IOHK, 2019 — deliverable **SL-D1**, §5.5.4). The mechanism has been operational on mainnet since the Shelley hard fork on 2020/07/29 and its governing parameters have never been modified by governance action.

### 2.1 SL-D1 (Original)

The operator and member rewards are two complementary views of the same split rule applied to the realized pool allocation.
Once the pool-level reward has been computed, the split follows the same sequence:

- cover the operator fixed cost first
- apply the operator margin to the remaining amount
- distribute the residual proportionally across stake holders

Under this rule, the operator receives both the explicit operator share and the stake-proportional share attached to the pledge held inside the pool, while each member receives a stake-proportional share of the residual amount.

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

### 2.2 Residual split decomposition

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

### 2.3 Reader-friendly formulation

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

A fundamental property becomes visible in this form. The operator's reward has two structurally distinct components:

$$
Reward^{\text{operator}} = \underbrace{Cost + Margin}_{\text{extracted from the pool's total reward}} + \underbrace{Share\,\rho^{\text{operator}}_{i}}_{\text{earned exactly as a delegator would}}
$$

The third term — $Share\,\rho^{\text{operator}}_{i}$ — is identical in form to any member's reward: a pro-rata share of the residual, proportional to the stake contributed. For the capital the operator pledges into the pool, the protocol treats the operator *exactly* as it treats a delegator. There is no special reward channel for pledge at this stage — the operator earns the same per-ADA yield as every other participant in the pool.

What distinguishes the operator from a delegator is the first two terms: $Cost$ and $Margin$. These are the only channels through which the operator can redirect part of the reward flow that is generated by *other participants' stake*. The fixed cost is a flat extraction; the margin is a proportional extraction. Both apply to the pool's total reward before pro-rata distribution, and both reduce the yield that delegators receive.

In other words: the operator's *own* capital is rewarded identically to delegated capital. The operator's *privilege* — the compensation for running infrastructure, bearing the pledge risk, and maintaining the pool — is expressed entirely through cost and margin. The split formula does not reward the operator *for pledging*; it rewards the operator *for operating*. The pledge mechanism that makes commitment economically significant lives upstream, in the reward curve (§2 of the [main report](../../../README.md#2-pools-distribution)), not in the intra-pool split.

### 2.4 Mainnet parameterization

| Parameter | Value | Set by |
| --- | --- | --- |
| `minPoolCost` ($c_{\min}$) | 340 ADA | Protocol parameter (governance) |
| Fixed cost ($c$) | Operator-declared, $\geq c_{\min}$ | Pool registration certificate |
| Margin ($m$) | Operator-declared, $\in [0, 1]$ | Pool registration certificate |

At epoch 614 (hollow-strategy pools): 93.5% of rewarded hollow-strategy pools declare $c = 340$ ADA (the minimum). The median declared margin is 2.0%; the entity-level median is 1.0% and the stake-weighted mean is 3.8%.

### 2.5 Concept glossary

| Symbol | Name | Definition |
| --- | --- | --- |
| $\hat{f}$ | Actual pool reward | Performance-adjusted output of the reward curve (stage 2) |
| $c$ | Declared fixed cost | Operator-declared flat ADA, $\geq c_{\min}$ |
| $c_{\text{eff}}$ | Effective fixed cost | $\min(c, \hat{f})$ — the actual ADA deducted |
| $m$ | Margin | Operator's declared share of reward after cost deduction |
| $c_{\min}$ | Minimum pool cost | Protocol-enforced floor on $c$ (currently 340 ADA) |
| Operator take | $c_{\text{eff}} + m(\hat{f} - c_{\text{eff}})$ | Total declared-fee extraction (= on-chain `pool_fees`) |
| Delegator pot | $(1-m)(\hat{f} - c_{\text{eff}})$ | Amount entering pro-rata distribution |
| Effective tax | Operator take / $\hat{f}$ | Fraction of pool reward extracted before pro-rata |

## 3. Three operator strategies

### 3.1 Strategy classification

This report classifies entities using the **owner-stake ratio** spectrum defined in the upstream analysis ([§2.4.2.1](../../../README.md#2421-the-three-strategies), [§2.4.3.1](../../../README.md#2431-what-mainnet-reveals)). The classification is applied at the **entity level** (dominant owner-stake ratio across the entity's pool fleet) and divides the 502 entities operating rewarded pools into three populations: **hollow** (< 10%, 445 entities), **balanced** (10–95%, 46 entities), and **private** (≥ 95%, 11 entities). Strategy consistency is high: 495 of 502 entities (98.6%) apply a single pure strategy across their entire fleet ([§2.4.3.1.2](../../../README.md#24312-strategies-are-entity-level-commitments-not-pool-level-accidents)). This justifies the entity-level framing used throughout the rest of this report.

### 3.2 The split at a glance

| | Hollow | Balanced | Private | All |
| --- | --- | --- | --- | --- |
| Entities | 445 | 46 | 11 | 502 |
| Pools | 771 | 60 | 44 | 875 |
| Active stake | 18.10B ADA (85.6%) | 0.77B ADA (3.6%) | 2.29B ADA (10.8%) | 21.16B ADA |
| Owner stake | 0.18B ADA (1.0%) | 0.40B ADA (52.5%) | 2.29B ADA (100.0%) | 2.87B ADA (13.6%) |
| Total rewards | 5,618,212 ADA | 272,854 ADA | 860,280 ADA | 6,751,346 ADA |
| Operator take | 749,373 (13.34%) | 29,320 (10.75%) | 860,000 (99.97%) | 1,638,693 (24.27%) |
| Delegator pot | 4,868,839 (86.66%) | 243,534 (89.25%) | 280 (0.03%) | 5,112,653 (75.73%) |

![Three Strategies — Entity-Level View](figures/three_strategies.png)

The entity-level view clarifies what the pool-level framing obscured. The hollow strategy encompasses 85.6% of delegated stake across 445 entities that collectively operate 771 pools — a coherent market segment. The balanced strategy encompasses 3.6% of stake across 46 entities — analytically small but structurally important (pledge works here). The private strategy encompasses 10.8% of stake across 11 entities that operate 44 pools as internal capital allocation. These are not three arbitrary buckets; they are three radically different models observed with remarkable consistency.

The three strategies operate under different logics — private-strategy entities are internal accounting operations for self-funded operators, balanced-strategy entities split capital with committed delegators, and hollow-strategy entities compete for external delegation. The following three sections (§5, §6, §7) apply the same analytical framework to each strategy independently, progressing from the structurally simplest case to the richest delegation market.

## 4. The delegator's strategy

The three strategies above describe the operator's side of the split. The delegator's side is simpler — not because the decision is trivial, but because the formula gives delegators a narrower action space.

### 4.1 What the formula offers

A delegator who stakes $t$ ADA in a pool receives:

$$
Reward^{\text{member}} = Share\,\rho^{\text{member}}_{i} = (1-\mu^{\text{operator}})\left(PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}\right) \cdot \frac{t}{\sigma^{\text{totalStaked}}_{i}}
$$

The delegator controls $t$ (the amount staked) and the choice of pool. Everything else — the pool reward $PoolPot^{\text{actual}}_{i}$, the fixed cost, the margin, and the total stake $\sigma$ — is set by the operator or determined by the protocol. The delegator's entire strategic space reduces to a single decision: *which pool to delegate to*.

### 4.2 The yield criterion

From the formula, the delegator's per-ADA yield depends on three factors, none of which the delegator controls directly:

- **Pool performance.** A pool that misses blocks produces a lower $PoolPot^{\text{actual}}_{i}$. Reliable infrastructure matters.
- **Operator fees.** The effective tax — $Cost + Margin$ extracted before pro-rata — reduces the delegator's share. Lower cost and lower margin mean higher yield.
- **Pool saturation.** A pool near or above saturation dilutes the per-ADA reward. Oversaturated pools actively destroy delegator yield.

A rational, yield-maximising delegator therefore seeks pools that are reliable, reasonably priced, and not oversaturated. The annualised return on stake (ROS) — the single metric that aggregates all three factors into a comparable number — is the natural selection criterion.

#### 4.2.1 How much does a delegator earn?

At epoch 614, a delegator in the genuine hollow market (723 pools, excluding hollow captive) earns a stake-weighted annualised ROS of **2.10%**. A delegation of 10,000 ADA produces approximately **210 ADA/year**, or ~2.9 ADA per epoch. The median pool delivers 2.00% and the stake-weighted average 2.10% — the difference reflects the fact that most delegated stake sits in large, competitively priced pools.

This yield has been declining steadily since the Shelley launch, tracking the depletion of the monetary expansion reserve:

| Period | Epochs | Reserve (start) | ME per epoch | Hollow stake-weighted annual yield |
| --- | --- | --- | --- | --- |
| Year 1 (ep 211–284) | 73 | 13.3B ADA | 31.4M ADA | 4.75% |
| Year 2 (ep 284–357) | 73 | — | — | 3.68% |
| Year 3 (ep 357–430) | 73 | — | — | 3.15% |
| Year 4 (ep 430–503) | 73 | 9.4B ADA | 22.0M ADA | 2.69% |
| Year 5 (ep 503–576) | 73 | — | — | 2.33% |
| Recent year (ep 541–614) | 73 | 6.6B ADA | 15.6M ADA | 2.16% |

The decline is structural: the reserve feeds the epoch pot through a fixed draw rate ($\rho = 0.003$), but each draw reduces the remaining reserve, which reduces the next draw. The delegator's yield compresses mechanically over time regardless of pool selection — the entire yield surface descends together.

#### 4.2.2 Where does Cardano stand? — the yield in context

At ~2.1% annualised ROS, Cardano's native staking yield sits at the lower end of the PoS landscape and below the risk-free rate in traditional finance.

| Benchmark | Annualised yield | Nature |
| --- | --- | --- |
| **Cardano delegation** | **~2.1%** | **Native PoS, liquid, non-custodial** |
| Ethereum staking | 3.3–4.5% | PoS, 32 ETH lockup (solo) or liquid staking |
| Avalanche delegation | 4.5–7.7% | PoS, 14-day unbonding |
| Polkadot staking | 5–6% | PoS, 28-day unbonding (post-2026 halving) |
| Solana staking | 5.9–6.6% | PoS, liquid staking variants available |
| Cosmos staking | 14–20% | PoS, 21-day unbonding, inflationary |
| US 10-Year Treasury | ~4.3% | Risk-free, USD-denominated |
| US high-yield savings | 4.2–5.0% | Risk-free, USD-denominated, liquid |
| S&P 500 dividend yield | ~1.2% | Equity risk, USD-denominated |

Three observations emerge from this comparison.

**Cardano pays less than most PoS peers.** Among major PoS chains, only the S&P 500 dividend yield sits below Cardano's staking return. Ethereum, with comparable market maturity, delivers 1.5–2× the yield. Higher-inflation chains (Cosmos, Solana) pay 3–10× more, though part of that yield is offset by token dilution — a distinction Cardano's low-inflation design avoids.

**Cardano pays less than the risk-free rate.** A US Treasury or a high-yield savings account — zero-volatility, zero-counterparty-risk instruments — offers 4–5% annually. A Cardano delegator earns 2.1% *in ADA terms*, bearing full price volatility on the underlying asset. The participation constraint (§2.2.2 of [*The Intended Game*](../../../the-intended-game/README.md#222-the-participation-constraint)) — the condition that the expected staking reward must exceed the opportunity cost of holding idle ADA — is satisfied only if the delegator's thesis includes ADA price appreciation, not yield alone.

**Cardano offers an unmatched convenience premium.** What Cardano's delegation mechanism loses in yield, it gains in liquidity and simplicity. There is no lockup period, no unbonding delay, no slashing risk, no minimum delegation threshold, and no custodial transfer. A delegator can move stake at any epoch boundary (~5 days) without the operator's consent. No other major PoS chain offers this combination. The low yield is the price of a design that prioritises liquid, non-custodial participation — a deliberate trade-off, not an oversight.

The competitive position of Cardano's yield is therefore a structural feature of its design: low inflation preserves token value at the cost of nominal yield, while liquid delegation preserves delegator sovereignty at the cost of lockup-based yield premiums. Whether this trade-off is attractive depends on the delegator's time horizon and conviction about the underlying asset — a question the formula does not answer but the delegator must.

#### 4.2.3 Three frames for evaluating the yield

Whether the yield is "good enough" depends on what the delegator compares it to. Three frames produce three different answers.

**Frame 1 — staking vs idle ADA (same-asset).** A delegator who already holds ADA and intends to hold it has a simple decision: stake or not. The staking premium is unconditionally positive (~2.1%/year). Every ADA held idle is diluted by the monetary expansion that funds the epoch pot; every ADA staked captures a share of that expansion. The rational ADA holder should always delegate, regardless of the absolute yield level. There is no threshold at which delegation becomes irrational in this frame — the premium is always positive.

**Frame 2 — ADA staking vs risk-free alternatives (cross-asset, USD terms).** A delegator choosing between ADA staking and a USD-denominated instrument (Treasury, high-yield savings) faces a different calculus. The staking yield is denominated in ADA, which bears full price volatility. To match a risk-free alternative, the total return — yield *plus* ADA price change — must exceed the alternative's yield:

| Alternative | Yield | Required ADA appreciation |
| --- | --- | --- |
| US 10-Year Treasury | ~4.3% | ≥ +2.1%/year |
| US high-yield savings | ~4.5% | ≥ +2.3%/year |
| Ethereum staking (in USD) | ~3.5% | ≥ +1.3%/year |
| Solana staking (in USD) | ~6.0% | ≥ +3.9%/year |

In this frame, **Cardano delegation is not a yield play — it is a conviction bet on the underlying asset.** The yield is a bonus on top of a price thesis, not a substitute for one. A delegator who does not believe in ADA appreciation has no rational reason to hold ADA at all, staked or not; and a delegator who does believe in it should always stake (frame 1).

**Frame 3 — native staking vs Cardano DeFi (same-asset, different risk).** A delegator who holds ADA and seeks higher yield can access DeFi protocols (liquidity provision, lending, yield farming) within the Cardano ecosystem. These typically offer higher nominal yields, but they carry smart-contract risk, impermanent loss, and protocol-specific counterparty risk that native staking does not. Native staking is the *risk-free rate of the ADA economy*: the baseline yield that any higher-risk strategy must beat by a margin sufficient to compensate for the additional risk. The threshold is delegator-specific — it depends on risk tolerance and the ability to evaluate DeFi protocol security.

#### 4.2.4 The yield is declining — and the trajectory is predictable

Because the yield is mechanically tied to the reserve ($\text{yield} \propto \text{reserve} / \text{active stake}$), and the reserve depletes at a fixed rate ($\rho = 0.003$ per epoch), the future trajectory is predictable. A simple model — yield at epoch $t$ equals the current yield scaled by the ratio of future reserve to current reserve — fits the historical data with $R^2 = 0.99$:

| Horizon | Projected ROS | Reserve |
| --- | --- | --- |
| Now (epoch 614) | 2.16% | 6.55B ADA |
| +1 year (epoch ~687) | 1.73% | 5.26B ADA |
| +2 years (epoch ~760) | 1.39% | 4.22B ADA |
| +3 years (epoch ~833) | 1.12% | 3.39B ADA |
| +5 years (epoch ~979) | 0.72% | 2.19B ADA |
| +7 years (epoch ~1125) | 0.47% | 1.41B ADA |

The yield crosses key thresholds at predictable dates:

| Threshold | Horizon | Meaning |
| --- | --- | --- |
| ROS < 2.0% | ~0.4 years | Below the current level of most indexed estimates |
| ROS < 1.5% | ~1.7 years | Below the S&P 500 dividend yield |
| ROS < 1.0% | ~3.5 years | Approaching negligibility for retail delegators |
| ROS < 0.5% | ~6.7 years | Delegation premium becomes symbolic |

This projection assumes constant active stake and no governance action on fee parameters. Both assumptions will eventually break — the active stake may decline as yield compresses (reducing staking attractiveness), and the community may revise protocol parameters (the reserve draw rate, the fixed-cost floor, or the fee structure) before the yield reaches negligibility. But the trajectory establishes the default path: absent intervention, the native staking yield will halve roughly every 3 years, reaching sub-1% within a single governance cycle.

The declining yield also tightens the participation constraint for operators (§5, §6, §7): as the epoch pot shrinks, the operator's margin and cost premium — the only compensation for running infrastructure — shrinks proportionally. At some point, operating a pool becomes unprofitable at any margin the delegation market will bear. This is the downstream dependency that the main report ([§2.4.4.4](../../../README.md#2444-the-downstream-dependency)) identifies: the reward curve's failure to target the balanced strategy propagates through the intra-pool split to reduce both delegator yield and operator viability.

#### 4.2.5 The yield spread — how different are pools?

The more important question for the delegator is not the absolute level but the *spread* — how much yield varies across the pools available for delegation. The answer depends on which segment of the pool landscape the delegator is looking at, and it changes over time as the reserve depletes. What follows is a per-strategy decomposition of the yield surface, grounded in 405 epochs of mainnet history (epochs 211–615).

##### 4.2.5.1 Cross-strategy trajectory

The figure below tracks the stake-weighted average delegator yield for each strategy across 405 epochs of mainnet history. The solid lines show single-epoch yields; the dashed lines show the trailing-year (73-epoch) average, which smooths out block-production noise. The shaded area between the two curves is the balanced-hollow gap.

![Delegator Yield by Strategy — Historical Trajectory](figures/yield_trajectory_by_strategy.png)

Three patterns are visible across the full history:

1. **Both strategies track the reserve depletion in near-lockstep.** The epoch-to-epoch correlation between hollow and balanced yields is 0.97. The delegator yield is overwhelmingly driven by a single macro-factor — the shrinking reserve — not by strategy-level differences. Over the full 405-epoch span, hollow pools averaged 3.20% and balanced pools 3.46%.

2. **The gap between strategies is narrow and unstable.** It opened at nearly 1pp in the early Shelley era, compressed to near-zero by 2024, then reopened slightly to 0.25pp at epoch 614. The trailing-year average gap has fluctuated between 0.12pp and 0.36pp since epoch 365. This is not a reliable premium — it is noise on a small sample of balanced pools.

3. **The pool count is diverging.** Hollow pools peaked at 904 (epoch 400) and have since declined to 771. Balanced pools have declined more steeply, from 119 to 57 — a 52% drop. The balanced strategy is thinning out as yields compress.

Private pools are excluded from the figure: they have negligible third-party delegation by definition and their per-delegator yield is meaningless at the aggregate level.

At the most recent closed epoch (614), the hollow market is where almost all delegation lives: 17.75B ADA across 765 pools, with a stake-weighted average yield of 2.01%. The middle half of hollow pools fall between 1.39% and 2.38% — a spread of just 1.00 percentage point. Balanced pools (57 pools, 0.31B ADA) show a headline spread more than twice as wide (2.36pp), but this is misleading — the dispersion is driven by small-pool block luck rather than structural factors, as §4.2.5.3 explains. Private pools (47) have negligible third-party delegation.

Six additional pools are structurally hollow by their owner-stake ratio but operationally dead — they hold 0.22B ADA in nominal delegation yet pay 0% yield. They are not participants in the delegation market; §4.2.5.4 discusses them separately. The 765 hollow pools referenced above exclude these six.

##### 4.2.5.2 Inside the hollow market

Within these 765 hollow pools, yield is overwhelmingly determined by pool size — specifically, by the interaction between the 340 ADA fixed-cost floor and total pool rewards. The figure below shows the median yield (bar height) and the middle-half range (25th–75th percentile, vertical line) for each size bucket at epoch 614. The annotation above each bar indicates how much delegation and how many pools each bucket contains.

![Delegator Yield by Pool Size — Hollow Pools](figures/yield_by_size_bucket.png)

Two patterns emerge:

1. **Yield rises monotonically with size** up to the saturation point. The median ROS doubles from 1.12% in the smallest bucket to 2.18% in the 30–77M bucket. This is almost entirely a fixed-cost effect: the 340 ADA floor consumes 100% of rewards for pools near 1M ADA but only ~3.5% for pools at 30M ADA (§4.2.6).

2. **Variance collapses as pools grow.** The middle-half spread drops from 2.25pp for sub-3M pools to 0.46pp in the 30–77M band — a fivefold narrowing. Small pools are dominated by block-production luck: a pool expecting two blocks per epoch may mint zero or four, creating wild single-epoch swings that have nothing to do with pool quality. Large pools, minting 20+ blocks per epoch, converge on their expected share and the remaining spread becomes structural.

The 30–77M bucket carries 70% of all hollow delegation (12.43B ADA). This is the segment most delegators actually inhabit, and it is the flattest part of the yield surface.

##### 4.2.5.3 The balanced premium — real or artefact?

At epoch 614, balanced pools report a stake-weighted average yield of 4.08% — nearly double the hollow average of 2.01%. The historical trajectory in §4.2.5.1 shows the gap has fluctuated between −0.03pp and +0.93pp over 405 epochs, with a trailing-year average that has hovered around 0.12–0.36pp since the pool landscape stabilised. The single-epoch snapshot overstates the structural difference.

Two factors explain the inflated epoch-614 number:

1. **Small-pool block luck.** Of the 57 balanced pools, 39 (68%) have active stake below 5M ADA. At this size, a pool expects fewer than two blocks per epoch. A single lucky epoch — three blocks minted instead of one — can push the annualised yield above 6%. The high average is driven by a handful of balanced pools that happened to overproduce blocks at epoch 614.

2. **Mechanical delegation-base effect.** In a balanced pool, the operator absorbs a larger share of rewards through the proportional (ρ_operator) term of the SL-D1 split. The remaining rewards are divided among fewer delegated ADA, sometimes producing a higher per-ADA yield for the delegator.

A fair comparison controls for size. Among pools with 10–50M ADA active stake at epoch 614, balanced pools show a stake-weighted average of 3.01% versus 2.04% for hollow — a ~0.9pp premium (right panel below). But the sample is just 11 balanced pools, and the historical trajectory in §4.2.5.1 shows this gap is not stable across epochs. A delegator cannot rely on a persistent balanced premium.

##### 4.2.5.4 Dead pools — hollow in name, zero in yield

Six pools classified as hollow by their owner-stake ratio (<10%) have two or fewer delegators and pay exactly 0% delegator yield. The operator controls each pool entirely and extracts all rewards through the cost-plus-margin mechanism, leaving nothing for the residual delegation slot. Together they hold 0.22B ADA in nominal delegation — stake that earns zero return.

These pools are not competitive participants in the delegation market. They serve as a reminder that the structural label alone does not guarantee a functioning delegator relationship. A delegator who selects a pool purely on declared parameters without checking the actual yield history risks a complete loss of staking return. The phenomenon is analysed in detail in §7 (the hollow strategy).

##### 4.2.5.5 SPO versus MPO

Among hollow pools, single-pool operators (SPOs) and multi-pool operators (MPOs) deliver near-identical stake-weighted yields. The left panel of the figure below shows the comparison at epoch 614.

![SPO vs MPO and Hollow vs Balanced — Epoch 614](figures/spo_mpo_and_balanced_comparison.png)

SPOs charge lower margins (median 1.0% vs 3.0%) but tend to run smaller pools, so the fixed-cost floor erodes more of their reward. MPO pools are typically larger, which offsets their higher margins. The net effect: from the delegator's perspective, the yield difference between SPO and MPO is negligible at the portfolio level (2.05% vs 2.00%). The choice between them is driven by decentralisation preferences (§4.3) rather than return.

##### 4.2.5.6 Oversaturation drag

Six hollow pools operate above the saturation threshold (~77M ADA), with active stakes ranging from 83M to 122M ADA (108–158% saturation). Their yields range from 1.30% to 2.03%, consistently below the 2.18% median of the 30–77M bucket.

The drag is mechanical: the reward formula caps the pool's reward at the saturation level, but the rewards are still divided across all delegated ADA. Every ADA above the cap dilutes returns for all delegators in the pool. The most oversaturated pool (158% saturation) delivers only 1.56% ROS — equivalent to a normally saturated pool in the 10–30M range. A delegator in an oversaturated pool would improve their yield by roughly 0.5–0.9pp simply by moving to a non-saturated pool of any size above 10M ADA.

##### 4.2.5.7 Variance decomposition — luck versus structure

Much of the within-epoch spread overstates the *structural* differences between pools. Among 443 hollow pools above 10M ADA at epoch 614, the correlation between blocks-per-ADA and single-epoch yield is 0.64 (R² = 0.41). Block-production luck accounts for roughly 41% of single-epoch yield variance.

The historical data confirms this at the aggregate level: the standard deviation of the hollow stake-weighted yield across 73 trailing epochs is just 0.10pp. Epoch-to-epoch changes in the aggregate hollow yield average −0.008pp (the secular decline) with a standard deviation of 0.075pp — meaning most of the epoch-to-epoch movement is noise rather than signal. Over a full year (73 epochs), block luck averages out and the structural spread that persists — the part driven by pool size and operator fees — is an order of magnitude smaller than the single-epoch noise. This is the core finding that §4.2.7 synthesises.

#### 4.2.6 What drives the structural spread?

The size-bucket analysis in §4.2.5.2 demonstrates *that* yield rises with pool size; the question here is *why*. Two factors account for nearly all persistent yield variation among hollow pools.

**The fixed-cost hyperbola.** The 340 ADA minimum cost consumes a fraction of the pool reward that depends entirely on pool size. At current reward levels, a 3M ADA pool loses 35% of its reward to the floor (leaving ~1.6% annual yield at 0% margin), while a 30M pool loses only 3.5% (yielding ~2.4%). A delegator in the smaller pool sacrifices ~0.8pp of annual yield — entirely because of the fixed cost, not because of any difference in operator quality or margin. In effective-tax terms, the 340 ADA floor acts as a regressive levy: 54.3% for pools below 3M ADA, collapsing to 4.7% in the 30–77M band.

This effect is growing over time. The figure below shows the fixed-cost share of hollow-pool rewards rising steadily across the full mainnet history, while the margin share has fluctuated without a clear trend.

![The Growing Fixed-Cost Burden — Hollow Pools](figures/fixed_cost_share_growth.png)

The aggregate fixed-cost share has tripled from 1.6% at epoch 250 to 4.9% at epoch 614, and will continue climbing as the reserve depletes. The hyperbolic penalty that today penalises sub-3M pools will, within a few years, begin to erode yields for pools in the 5–10M range that are currently viable.

**Margin.** Among large pools where the fixed cost is negligible, margin is the residual differentiator — but its impact is small. On a 30M ADA pool, moving from 0% to 3% margin reduces the delegator's annual yield by 0.07pp (from 2.37% to 2.30%). Moving from 0% to 10% costs 0.24pp. Margin explains the remaining spread once size is controlled for, but that remaining spread is narrow.

#### 4.2.7 The narrowness of the yield surface

The per-strategy decomposition in §4.2.5 and the structural analysis in §4.2.6 converge on a single conclusion: the delegator's yield surface is remarkably flat. Among hollow pools, 70.2% of delegated stake sits within ±0.5 percentage points of the median yield (1.96%). The middle-half spread in the 30–77M band — where 70% of delegation lives — is just 0.46pp. Once block-production noise is averaged over a year (§4.2.5.7), the structural spread that persists across epochs is an order of magnitude smaller than the single-epoch noise.

The narrowness is not a bug — it is a direct consequence of a reward curve that distributes rewards roughly proportional to stake. The fixed-cost hyperbola penalises only small pools (§4.2.6), margin competition has compressed fees in the large-pool regime, block production is proportional to stake, and the SPO/MPO distinction has no net yield effect (§4.2.5.5). The only pools that offer materially different returns are those the delegator should avoid: dead pools that extract 100% of rewards (§4.2.5.4), oversaturated pools (penalty of 0.5–0.9pp), and sub-3M pools (median 1.12%).

A rational, yield-maximising delegator scanning the pool landscape finds that — after excluding these edge cases — most pools offer nearly identical returns. This is the structural condition that opens the door to the second criterion: when yield cannot meaningfully differentiate pools, the delegator's choice becomes partly an expression of values.

### 4.3 Beyond yield — the ethics of pool selection

The yield criterion is necessary but not sufficient. Two pools that offer identical ROS may differ in ways the formula does not capture but that matter to the delegator and to the network:

**Commitment.** A balanced-strategy pool where the operator has pledged meaningful personal capital is structurally more aligned with the delegator's long-term interest than a hollow pool of equal yield. The operator has more to lose, the accountability channel is active, and the pool is less likely to change strategy abruptly. The formula does not reward the delegator for choosing this pool over a hollow alternative — the yield may even be marginally lower — but the security properties of the network are better served.

**Independence.** Delegating to an independent single-pool operator contributes to decentralisation in a way that delegating to the tenth pool of a large MPO fleet does not. The protocol does not distinguish between the two — the formula treats every pool identically — but the delegator who values a decentralised network may deliberately choose the independent operator, accepting equal or slightly lower yield in exchange for the systemic property their delegation supports.

**Transparency and conduct.** Operators differ in how they communicate fee changes, how they maintain infrastructure, how they engage with the community. These are reputational signals that the protocol does not encode but that delegators can observe and act on. A delegator who exits a pool after a surprise margin increase is exercising the accountability mechanism described in [*The Intended Game* §2.3](../../../the-intended-game/README.md#23-delegators--the-oversight-layer) — even if the formal yield difference is negligible.

### 4.4 Myopic and non-myopic delegation

The formal literature distinguishes two delegator models that map directly onto the yield-vs-ethics tension above.

A **myopic** delegator optimises for the *current epoch*. The decision is purely backward-looking: which pool delivered the highest ROS last epoch? The myopic delegator treats delegation as a spot market — move to the best-yielding pool, every epoch, ignoring second-order effects. Under this model, delegation flows toward the largest, most reliable, lowest-fee pools — which are overwhelmingly hollow. The myopic delegator has no reason to consider pledge, operator commitment, or network-level properties: none of these affect the per-ADA yield in the next five days.

A **non-myopic** delegator anticipates the *downstream effects* of delegation decisions. This delegator recognises that moving stake into a pool changes the pool's size, affects its yield (through saturation dynamics), and — in aggregate — shapes the pool landscape. Brünjes & Kiayias (2020) prove that the $k$-pool equilibrium holds under non-myopic play: delegators who factor in the long-term consequences of their delegation converge on a distribution of $k$ pools. The non-myopic delegator is the one for whom the ethics of pool selection (§4.3) are not a luxury but a rational strategy: supporting committed, independent operators produces a more decentralised, more accountable network — which is a more valuable network — which sustains the yield the delegator depends on.

The distinction matters because the mechanism implicitly *assumes* non-myopic delegation. The equilibrium results in the formal literature require delegators who look past the current epoch. But the information environment the mechanism creates — where yield differences between pools are negligible, where pledge is invisible, where pool size is the dominant signal — rewards myopic behaviour. A delegator who delegates to the largest hollow pool is making the rational myopic choice. A delegator who deliberately chooses a smaller balanced pool, accepting marginally lower yield to support commitment and decentralisation, is making the rational non-myopic choice — but the mechanism gives no visible reward for it.

This is the core tension in the delegator's strategy. The mechanism needs non-myopic delegators to reach its intended equilibrium, but it provides myopic delegators with no reason to become non-myopic. The ethics of pool selection are real and consequential — but they operate outside the formula, sustained only by the delegator's understanding that the network they help shape is the network they depend on.

### 4.5 The delegator's leverage

The delegator's single decision — which pool — is also the protocol's primary accountability instrument. Liquid delegation means that capital can move freely, at any epoch boundary, without the operator's consent. This makes every delegation a *continuous approval signal* and every withdrawal a *credible exit threat*.

But this leverage only works if delegators actually exercise it. The formula structure creates a tension: because yield differences between well-run pools are small, the *economic* incentive to switch is weak. The *systemic* incentive — supporting commitment, independence, decentralisation — is real but does not appear in the delegator's per-ADA return. The mechanism relies on non-myopic delegators — those willing to factor commitment, independence, and network health into a decision the formula prices as nearly indifferent.

This is the delegator's strategic position: a narrow yield optimisation on the surface, resting on a deeper choice about what kind of network the delegator wants to sustain.

## 5. The private strategy

All analysis in this section is restricted to the **11 entities following the private strategy** (owner-stake ratio ≥ 95%, 44 pools). These entities are operator-funded: the owner provides effectively all of the stake, and the intra-pool split is an internal accounting operation rather than a market transaction.

### 5.1 Composition

The 11 entities following the private strategy control 2.29B ADA (10.8% of total active stake) and generate 860K ADA/epoch in rewards. Owner-stake ratio averages 99.5% — outside delegation is negligible.

The population is predominantly multi-pool entities operating across the 44 pools. These private-strategy pools represent operator-funded infrastructure with minimal external delegation, reflecting pure self-provisioning of stake and rewards.

### 5.2 Intra-pool split

| Component | ADA | Share of private distributed |
| --- | --- | --- |
| Total distributed rewards | 948,441 | 100% |
| **Operator take** (fees) | **900,508** | **94.95%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 14,610 | 1.54% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 885,898 | 93.41% |
| **Delegator pot** (pro-rata) | **47,932** | **5.05%** |

The operator extracts 94.95% of rewards. Margin (93.41%) dominates entirely — fixed cost is negligible (1.54%), both because the pools are large (diluting the flat 340 ADA floor) and because extraction is driven by declared margin, not the cost mechanism. The 5.05% that reaches the delegator pot reflects the few private pools with competitive margins (§5.3).

### 5.3 Margin behaviour

| Margin range | Pools | Stake (B ADA) | Operator take |
| --- | --- | --- | --- |
| ≥ 99.9% | 44 (93.6%) | 2.19 | ~100% |
| 2–5% | 2 | 0.08 | 4–5% |
| < 2% | 1 | 0.001 | < 2% |

44 of the 47 pools operated by private-strategy entities set margin ≥ 99.9%, absorbing effectively all rewards through the margin mechanism. This is the expected behaviour: when the operator is the sole funder, margin is an accounting choice — the fee is paid to oneself. Fixed cost is universally at the minimum (340 ADA across all 47 pools).

The three pools operated by private-strategy entities with competitive margins (1–4%) are the structural exception. These are self-funded operators that nonetheless participate in the fee market, either to attract marginal external delegation or for signalling purposes. They demonstrate that being private (by capital composition) does not mechanically imply being extractive (by margin choice).

### 5.4 Pledge behaviour

Among the 41 pools operated by private-strategy entities with upstream health metadata:

| Pledge tag | Pools | Stake |
| --- | --- | --- |
| High pledge | 22 | 1.55B ADA |
| Low pledge | 15 | 517M ADA |
| Zero pledge | 3 | 96M ADA |
| Material pledge | 1 | 6M ADA |

22 pools are private in both the capital-composition and pledge-commitment senses — their operators fund the pool *and* formally pledge a significant share. But 18 of 41 (15 Low pledge + 3 Zero pledge) fund the pool from owner wallets without formally pledging the capital. These pools are **private by capital, hollow by pledge** — precisely the pattern the upstream analysis ([§2.4.3](../../../README.md#243-endgame--the-hollow-strategy-is-the-dominant-one)) predicts: pledging imposes liquidity constraints and the pledge-unmet cliff, while the bonus it produces is negligible. Even operators who *could* pledge — they own the capital, there is no custodial constraint — rationally choose not to.

This finding reinforces the upstream observation: the pledge mechanism does not appear to attract commitment — not because operators lack capital, but because the incentive may be too weak to justify the constraints it imposes.

### 5.5 Key findings — private strategy

The intra-pool split at this stage is structurally trivial for entities following the private strategy — the operator funds the pools and collects the reward. Margin is an accounting choice (93.6% at ≥99.9%), fixed cost is negligible, and the delegator pot is effectively zero. The mechanism's fee-competition logic does not apply: there is no external delegation to compete for.

The analytical value lies in the pledge dimension. Entities following the private strategy are the population *most able* to pledge — they own the capital, face no custodial constraint, and would benefit most from the pledge bonus (their high owner-stake ratio maximises the bonus function). Yet a significant portion of mapped private-strategy pools do not pledge meaningfully. The pledge mechanism's limited effectiveness is most visible precisely where conditions for its success are most favourable.

## 6. The balanced strategy

All analysis in this section is restricted to the **46 entities following the balanced strategy** (owner-stake ratio 10–95%, 60 pools). These entities have genuine capital commitment and form the segment where the pledge mechanism produces meaningful alignment.

### 6.1 Composition and structure

The 46 entities following the balanced strategy control 0.77B ADA (3.6% of total active stake) and generate 273K ADA/epoch in rewards. The median owner-stake ratio across entities is 26.4%, indicating genuine operator capital commitment. Operator owner-ratio averages 40.0% — these are entities where the operator has real skin in the game.

The population is predominantly single-pool operators across the 60 pools. These independent operators form a segment where committed capital and competitive participation coexist, demonstrating genuine skin-in-the-game alignment.

### 6.2 Intra-pool split

| Component | ADA | Share of balanced distributed |
| --- | --- | --- |
| Total distributed rewards | 201,558 | 100% |
| **Operator take** (fees) | **25,809** | **12.8%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 16,581 | 8.23% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 9,228 | 4.58% |
| **Delegator pot** (pro-rata) | **175,749** | **87.2%** |

In the balanced segment (60 pools operated by balanced-strategy entities), operator take is 12.8%. Fixed cost dominates (8.23%) because these pools are smaller on average than the hollow large-pool regime — the 340 ADA floor consumes a larger fraction of smaller rewards. Margin (4.58%) is low, reflecting competitive dynamics and the presence of committed operators with skin-in-the-game.

### 6.3 Margin behaviour

| Margin range | Pools | Stake (B ADA) |
| --- | --- | --- |
| < 2% | 25 (43.9%) | 0.14 |
| 2–5% | 28 (49.1%) | 0.48 |
| > 5% | 4 (7.0%) | 0.02 |

43.9% of pools operated by balanced-strategy entities set margin below 2%, reflecting a population where fee competition is active and operators have committed capital. The median margin is 1.5%, confirming competitive pricing. The 2–5% bracket holds the most stake (0.48B ADA) because it includes several larger balanced-strategy pools with moderate margin policies.

### 6.4 The pledge signal — where it works

Among the 15 pools operated by balanced-strategy entities with upstream health metadata (the coverage is partial — the upstream health dataset maps 466 of 875 rewarded pools):

| Pledge tag | Pools | Stake |
| --- | --- | --- |
| Material pledge | 9 | 0.07B ADA |
| High pledge | 6 | 0.32B ADA |

All 15 mapped pools operated by balanced-strategy entities carry Material or High pledge tags — genuine, formal capital commitment. No Low or Zero pledge tags appear in this population. While the coverage is limited, the pattern is structurally significant: entities following the balanced strategy who are visible in the health dataset consistently pledge meaningfully.

This is the only population where meaningful pledge adoption occurs in tandem with competitive margins (median 1.5%). The entities following the balanced strategy — those with 10–95% owner-stake ratio — demonstrate genuine alignment: they own enough capital to absorb loss, they formally pledge it, and they compete on fees. This population proves that the pledge mechanism *can* work when operators have committed capital.

### 6.5 Key findings — balanced strategy

Entities following the balanced strategy form a tiny segment (3.6% of delegated stake, 46 entities, 60 pools) but are analytically significant: they are the *only* population where the pledge mechanism produces meaningful operator alignment. The presence of high pledge-commitment signals in balanced-strategy entities, paired with aggressive fee competition (median margin 1.5%), demonstrates that when operators have genuine capital at stake, the incentive mechanism works as intended. The network is polarized between hollow (externally-funded) and private (operator-funded) entities, with almost nothing in between — the balanced segment proves that genuinely committed intermediate operators exist but are rare. Their structural behaviour (low margins, high pledge commitment) should inform the design of future incentive mechanisms aimed at attracting committed operators.

## 7. The hollow strategy

All analysis in this section is restricted to the **445 entities following the hollow strategy** (owner-stake ratio < 10%, 771 pools). These entities depend entirely on external delegation and form the public delegation market where fee-competition dynamics apply.

### 7.1 The hollow captive sub-population

Before analysing the hollow-strategy market, a distortion must be isolated. 48 pools operated by hollow-strategy entities set margin ≥ 99.9% despite owning on average only 1.75% of their stake. These are exchanges and custodial operators running captive staking infrastructure: the delegated capital belongs to their users, not to the operator. They are *hollow* in the capital-composition sense — minimal owner stake — yet they extract 100% of rewards via margin.

| | Hollow captive | Genuine hollow | All hollow |
| --- | --- | --- | --- |
| Pools | 48 | 723 | 771 |
| Active stake | 0.98B ADA | 17.10B ADA | 18.07B ADA |
| Total rewards | 307K ADA | 5.29M ADA | 5.60M ADA |
| Operator take | 307K ADA (100.0%) | 405K ADA (7.7%) | 712K ADA (12.72%) |
| Delegator pot | ~0 ADA (0.0%) | 4.89M ADA (92.3%) | 4.89M ADA (87.28%) |

Among hollow captive pools with upstream health metadata: 15 carry Zero pledge, 6 Minimal pledge. The upstream analysis identifies the architectural constraint: custodial operators cannot pledge the capital they manage ([§2.4.3.2](../../../README.md#2432-delegating-is-inherently-less-constraining-than-pledging)). They reached the extraction endpoint without traversing the pledge arc. Their 0.98B ADA in stake exists in the hollow universe by capital composition but outside the fee market by behaviour — their delegators (exchange customers) do not choose pools based on on-chain fee parameters.

All subsequent analysis in this section covers the full 771-pool hollow segment (all pools operated by hollow-strategy entities). Where the hollow captive distortion materially affects an aggregate, it is noted.

### 7.2 The genuine market — current snapshot (epoch 614)

| Component | ADA | Share of hollow distributed |
| --- | --- | --- |
| Total distributed rewards | 5,601,347 | 100% |
| **Operator take** (fees) | **712,372** | **12.72%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 274,798 | 4.91% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 437,573 | 7.81% |
| **Delegator pot** (pro-rata) | **4,888,975** | **87.28%** |

![Intra-Pool Reward Split — Pools Operated by Hollow-Strategy Entities, Epoch 614](figures/reward_split_waterfall.png)

In the full hollow segment (771 pools operated by hollow-strategy entities), operator take is 12.72%. This aggregate is inflated by 48 hollow captive pools (§7.1) that extract 100% via margin despite owning almost none of the stake. In the genuine hollow market (723 pools, excluding hollow captive), operator take is 7.7% — with fixed cost (4.9%) slightly exceeding margin (2.8%). The waterfall above reflects the full 771-pool hollow segment.

### 7.3 Historical evolution of the split

![Reward Split — Pools Operated by Hollow-Strategy Entities, Historical](figures/reward_split_area_timeseries.png)

The stacked-area timeseries decomposes the hollow-segment distributed reward into its three components — effective fixed cost, margin, and delegator pot — across 405 epochs. The delegator pot dominates throughout the observation window. The fixed-cost and margin bands are thin and roughly comparable in magnitude. The absolute size of distributed rewards has declined, tracking the monetary expansion draw (documented in the [*Treasury & Pool Pots*](../../treasury-and-pool-pots-distribution/mainnet-analysis/) companion report).

### 7.4 The two components — fixed cost vs margin

![Operator Take Share — Historical](figures/operator_take_pct_timeseries.png)

The line chart decomposes the operator-take percentage over time for pools operated by hollow-strategy entities:

- **Fixed-cost share (~4–6%)** is slowly rising as per-pool rewards decrease with declining monetary expansion — the flat 340 ADA floor consumes a growing fraction of shrinking rewards.
- **Margin share (~3–4%)** is stable and low, reflecting the competitive dynamics in the hollow-strategy market.
- **Total operator take (hollow, ~8–10%)** is the sum of both, trending slowly upward — driven by the fixed-cost component.

The dotted line shows the all-pools aggregate (including private and balanced) for reference — the gap between the hollow and all-pools lines is entirely attributable to private-strategy-pool absorption.

### 7.5 The effective tax on delegators

The effective tax is defined as the operator take (on-chain `pool_fees`) divided by the total pool reward: $\text{pool\_fees} / \hat{f}$. It measures the fraction of the pool's reward that is extracted before pro-rata distribution.

![Effective Tax on Delegators — Pools Operated by Hollow-Strategy Entities](figures/effective_tax_distribution.png)

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 25.4% |
| Median | 11.1% |
| Stake-weighted mean | 13.0% |
| 10th percentile | 3.2% |
| 90th percentile | 100.0% |

The divergence between unweighted mean (25.4%) and stake-weighted mean (13.0%) reveals the size effect: small pools face high effective tax (driven by the fixed-cost floor) but hold little stake. The bulk of delegated ADA sits in large pools with low effective tax. The median (11.1%) lies between these because small pools are numerous.

### 7.6 Fixed-cost dominance at the small-pool end

![Fixed-Cost Dominance — Pools Operated by Hollow-Strategy Entities](figures/fixed_cost_dominance.png)

The scatter of fixed-cost share versus pool size reveals the structural mechanism at the small-pool end:

$$
\frac{c_{\text{eff}}}{\hat{f}} \approx \frac{c_{\min}}{\sigma \cdot y}
$$

where $\sigma$ is the pool's active stake and $y$ is the per-ADA-per-epoch yield (~0.032% at epoch 614). This is a **hyperbola in pool size** — the fixed cost's share of the reward decays as $1/\sigma$.

The empirical points follow the theoretical curve closely. At 1M ADA stake, the fixed cost consumes ~100% of the reward. At 10M ADA, it consumes ~10%. At the saturation threshold (~77M ADA), it consumes ~1.4%. For pools above ~10M ADA, the fixed-cost share is negligible and margin becomes the dominant extraction. The viability threshold — the stake below which the fixed cost exceeds the total reward — aligns with the ~1.1M ADA boundary identified in the companion [*pools-distribution*](../../pools-distribution/mainnet-analysis/) analysis.

### 7.7 Margin distribution — by pool and by entity

![Margin Rate Distribution — Pool Count vs Entity Count](figures/margin_rate_distribution.png)

**Pool-level statistics (771 pools operated by hollow-strategy entities):**

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 10.1% |
| Median | 2.0% |
| Stake-weighted mean | 9.0% |
| Pools at 0% margin | 18.2% |
| Pools below 2% margin | 43.8% |
| Pools above 5% margin | 14.5% |

**Entity-level statistics (445 hollow-strategy entities):**

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 9.6% |
| Median | 1.5% |
| Stake-weighted mean | 8.9% |
| Entities at 0% margin | 121 (27.2%) |
| Entities below 2% margin | 277 (62.3%) |
| Entities 2–5% margin | 155 (34.8%) |
| Entities above 5% margin | 59 (13.3%) |

The entity-level view is more informative than the pool-level view because fee-policy decisions are made per entity, not per pool. Entities like Coinbase run many pools at a tiered margin strategy — that is one (or a few) policy decisions, not one per pool. 35 entities use **mixed margin policies** across their pool fleets, typically with slight variation (e.g. Blockdaemon: 3%, 6%, 8%, 10%) that may reflect vintage, client tier, or pricing segmentation.

The median entity margin of 1.5% confirms that margin competition is broadly active in the hollow-strategy market. The bulk of entities cluster at 0–2%, with a thin tail extending to 10%. The stake-weighted mean (8.9%) is close to the unweighted mean (9.6%), indicating that margin policy does not vary dramatically with entity size — a healthy sign of competitive equilibrium.

### 7.8 Fee parameter adoption

![Fee Parameter Evolution — Pools Operated by Hollow-Strategy Entities](figures/fee_parameter_evolution.png)

The historical evolution of fee parameter adoption among pools operated by hollow-strategy entities shows:

- **91.6% of rewarded pools operated by hollow-strategy entities** declare the minimum fixed cost (340 ADA). This fraction has remained stable at ~90% throughout the observation window. Operators treat the minimum as the norm.

- **~20% of rewarded pools operated by hollow-strategy entities** declare 0% margin, a share that has grown slowly over time — a sign of increasing competitive pressure.

The margin-rate evolution panel shows the median (solid) and stake-weighted mean (dashed) margin for hollow-strategy pools. Both have converged toward low single digits, confirming active competition.

### 7.9 MPO vs SPO operator take

![MPO vs SPO Operator Take — Hollow-Strategy Pools](figures/mpo_vs_spo_operator_take.png)

| Entity type | Pools | Total rewards (ADA) | Operator take (ADA) | Operator take (%) |
| --- | --- | --- | --- | --- |
| MPO | 415 | 4,268,576 | 531,908 | 12.46% |
| SPO | 413 | 1,534,328 | 206,273 | 13.44% |

In the hollow-strategy market, **SPO pools bear a higher effective operator take** (13.44% vs 12.46%) — the reverse of the all-pools picture. The explanation is straightforward: SPO pools are smaller on average, and the fixed-cost floor extracts a larger share of their smaller rewards. MPO pools benefit from economies of scale — their larger $\hat{f}$ dilutes the flat 340 ADA cost. This is a structural consequence of the fixed-cost floor, not a margin-competition failure.

### 7.10 Top entities by operator take

![Top 20 Entities by Operator Take — Hollow-Strategy Market](figures/top20_entities_operator_take.png)

The top 20 entities by absolute operator take in the hollow-strategy market are dominated by large MPO operators. The decomposition shows the balance between fixed cost (red) and margin (orange) for each entity. For entities running many pools (e.g. Coinbase: 41 pools), fixed cost accumulates through pool count even at low per-pool cost — this is an entity-level consequence of the cost floor that is invisible at the pool level.

### 7.11 Key findings — hollow strategy

The intra-pool split in the hollow-strategy market operates as a genuine competitive mechanism — but with two distortions. First, 48 hollow captive pools inflate the aggregate operator take from 7.7% to 12.72%; they sit in the hollow universe by capital composition but outside the fee market by behaviour. Second, the fixed-cost floor creates a regressive tax that penalises small-pool delegators: the effective tax for a 3M ADA pool is ~35%, versus ~4% for a large pool. Margin competition is broadly active in the hollow-strategy market (median entity margin 1.5%), but fixed cost — not margin — is the dominant extraction channel in the genuine market. The competitive dynamics envisioned in SL-D1 function in this universe; the structural concern is the cost floor, not the margin mechanism.

## 8. Structural implications

### 8.1 Two regimes, one mechanism

The hollow-strategy-market data reveal that the intra-pool split operates as **two distinct regimes** depending on pool size:

**The small-pool regime** (below ~10M ADA stake): the 340 ADA fixed cost dominates the effective tax. For a pool at 3M ADA stake, the cost is ~35% of the reward; at 1M ADA, it exceeds the reward entirely. Margin, even when declared, contributes little because the reward after cost deduction is small. This regime affects ~73% of hollow-strategy pools but only a small fraction of delegated stake.

**The large-pool regime** (above ~10M ADA stake): the fixed cost is negligible (< 2% of reward). Margin is the binding parameter. A pool at 60M ADA stake and 3% margin extracts ~560 ADA/epoch through margin — modest but proportional. This regime holds most of the delegated stake and determines the stake-weighted aggregate.

In the genuine hollow-strategy market (excluding hollow captive pools), both regimes produce moderate effective taxes. The aggregate 7.7% operator take is low by design — the competitive dynamics envisioned in SL-D1 function in this universe. The policy concern is concentrated in the small-pool regime, where the cost floor creates disproportionate extraction.

### 8.2 The fixed-cost floor as a regressive tax on small pools

The 340 ADA minimum cost was designed to ensure operational sustainability. In practice, it functions as a **regressive tax on small-pool delegators**:

- At the saturation threshold (~77M ADA, $\hat{f}$ ≈ 24,000 ADA): 1.4% — negligible.
- At 3M ADA stake ($\hat{f}$ ≈ 960 ADA): 35% — material.
- At 1M ADA stake ($\hat{f}$ ≈ 320 ADA): exceeds the reward — the pool is non-viable.

The tax is regressive because it falls disproportionately on delegators in smaller pools — the participants with the least ability to switch (community-attached delegators, delegators who chose small pools for decentralisation reasons) bear the highest proportional extraction.

The entity-level view adds another dimension: entities operating many small pools multiply the cost-floor impact. An entity with 10 pools at 3M ADA stake each pays 3,400 ADA in fixed costs — 35% of its combined reward — while a single pool at 30M ADA pays only 340 ADA (3.5%). The cost floor penalises both small pools and multi-pool entities disproportionately.

### 8.3 Margin competition in the hollow strategy market

With private-strategy entities removed from the picture, the hollow-strategy market shows **healthy margin competition**. The entity-level median margin of 1.0% and the fact that 56.4% of entities operate below 2% indicate that the SL-D1 mechanism creates genuine competitive pressure in the hollow-strategy delegation market.

The small number of entities above 5% margin (59 out of 445) are not analogous to the private-strategy entities — they are hollow-strategy operators choosing to charge higher margins, presumably on differentiated service. The delegation market can discipline these margins if delegators are price-sensitive.

The previous analysis, which mixed private- and hollow-strategy entities, suggested that "margin competition exists where it matters least and fails where it matters most." With the private-strategy confound removed and the hollow and balanced populations distinguished, the revised finding is that margin competition is broadly active in the hollow-strategy market. The absence of competition is restricted to the private-strategy universe, where it is structural and deliberate — not a mechanism shortcoming but an out-of-scope use of pool infrastructure. The balanced-strategy population demonstrates that intermediate operators *can* compete on margins and pledge simultaneously, but they are rare.

### 8.4 Open questions

1. **Captive delegation volume.** What fraction of delegated ADA in the *hollow-strategy* market is subject to soft captivity (exchange-intermediated delegation to hollow-strategy pools at moderate margins)? This would refine the competition analysis.

2. **Delegator price sensitivity.** Do delegators respond to margin differences? Natural experiments exist in pools that changed their margin: measuring delegation flows before and after would reveal whether the competitive mechanism has empirical traction.

3. **Optimal cost floor.** If $c_{\min}$ were reduced below 340 ADA, at what level does operational sustainability begin to erode? Cross-referencing with actual operator infrastructure costs would establish the economically meaningful floor.

4. **Cross-stage interaction.** The fixed-cost tax interacts with the reward curve's unused pledge budget (documented in the companion [*pools-distribution*](../../pools-distribution/mainnet-analysis/) analysis). Pools that already lose rewards through incomplete pledge activation then lose further rewards through the fixed-cost extraction — a double inefficiency for small pools.

5. **Balanced-strategy persistence.** Why are genuinely committed operators (balanced-strategy entities with 10–95% owner-ratio) so rare? Understanding the barriers to entry for this segment would illuminate whether they represent a viable alternative to the hollow–private dichotomy.

## 9. Reproduction

### 9.1 Full rebuild

```bash
cd spo-incentives/report/sub-flows/operator-delegator-distribution/mainnet-analysis
python3 scripts/build_operator_delegator_profile.py
python3 scripts/build_operator_delegator_visuals.py
```

The profiling script automatically selects the second-to-last epoch in the dataset (guaranteed settled, not pending). Entities are classified as hollow (owner-stake ratio < 10%), balanced (10–95%), or private (≥ 95%). Entity-level grouping uses the MPO entity mapping where available; unmapped pools are each treated as their own entity.

### 9.2 Dependencies

Both scripts read from the `pools-distribution/mainnet-analysis/data/` directory (the sister flow). No additional data fetch is required. The profiling script produces five intermediate artefacts consumed by the visual script:

| Artefact | Description |
| --- | --- |
| `data/reward_split_snapshot.csv` | Per-pool reward decomposition at epoch 614: $\hat{f}$, $c_{\text{eff}}$, $m$, operator take (on-chain), delegator pot, population flag (hollow / balanced / private) |
| `data/reward_split_timeseries.csv` | Epoch-level aggregates (all, hollow, balanced, private): fixed cost, margin, delegator pot, operator-take share (405 epochs) |
| `data/margin_fixed_cost_history.csv` | Epoch-level margin and fixed-cost parameter distributions for hollow-strategy pools (percentiles, adoption rates) |
| `data/entity_fee_policies.csv` | Entity-level fee-policy summary (non-private): 491 entities with stake-weighted margin, pool count, margin values, operator take decomposition |
| `data/reward_split_summary.json` | Headline statistics for all, hollow, balanced, and private segments; entity strategy consistency metrics |
| `data/entity_strategy_summary.csv` | Entity-level strategy assignment: dominant strategy, n_strategies, pool count, stake, operator take per entity |

### 9.3 Figures

| Figure | Description |
| --- | --- |
| `three_strategies.png` | Triptych — entity count, stake, and operator take (%) for hollow, balanced, and private strategies |
| `reward_split_waterfall.png` | Waterfall decomposition: hollow-strategy $\hat{f} \to c_{\text{eff}} \to m \to$ delegator pot (epoch 614) |
| `reward_split_area_timeseries.png` | Stacked area — hollow-strategy fixed cost, margin, delegator pot over time |
| `operator_take_pct_timeseries.png` | Line chart — operator-take share (%) for hollow-strategy pools with all-pools reference |
| `effective_tax_distribution.png` | Histogram — effective tax on delegators across hollow-strategy pools |
| `margin_rate_distribution.png` | Paired histograms — margin rate by pool count vs entity count (hollow-strategy) |
| `fixed_cost_dominance.png` | Scatter — fixed-cost share vs pool size with theoretical hyperbolic curve (hollow-strategy) |
| `fee_parameter_evolution.png` | Two-panel — margin rate percentiles and fee-parameter adoption over time (non-private) |
| `mpo_vs_spo_operator_take.png` | Grouped bars — MPO vs SPO reward and operator-take comparison (hollow-strategy) |
| `top20_entities_operator_take.png` | Horizontal bars — top 20 entities by operator take, decomposed into fixed cost and margin (hollow-strategy) |
| `yield_trajectory_by_strategy.png` | Line chart — hollow vs balanced stake-weighted delegator yield across epochs 211–615, with trailing-year averages |
| `yield_by_size_bucket.png` | Bar chart — median delegator yield and middle-half range by pool-size bucket (hollow pools, epoch 614) |
| `spo_mpo_and_balanced_comparison.png` | Dual-panel bars — SPO vs MPO yield (left) and hollow vs balanced at same size (right), epoch 614 |
| `fixed_cost_share_growth.png` | Line chart — fixed-cost and margin share of hollow rewards over epochs 211–615 |
