# The Operator's Cut — A Mainnet Analysis of Intra-Pool Reward Sharing

_Built on 2026/03/31 from mainnet data at epoch `614` (settled) plus historical analysis from epoch `211` (405 epochs)._

## Objective

This report analyses the **intra-pool reward split** — the third and final stage of Cardano's reward pipeline — and traces the structural forces that determine how much of each pool's reward reaches delegators versus operators. It extends the empirical baseline established in the [*Analysis of Cardano's Incentive Mechanism*](https://github.com/input-output-hk/spo-incentives/blob/main/report.pdf) (Lopez de Lara, 2025; hereafter the *Incentive Mechanism Analysis*) and operates downstream of the companion reports [*Treasury & Pool Pots Distribution*](../../treasury-and-pool-pots-distribution/mainnet-analysis/) (stage 1) and [*The Pools Pot Distribution Gaps*](../../pools-distribution/mainnet-analysis/) (stage 2).

Every epoch, once the reward curve assigns a total reward $\hat{f}$ to each pool, a second mechanism activates: the **intra-pool split**. The pool operator extracts a fixed cost $c$ and a proportional margin $m$; the remainder is distributed pro-rata among all delegators (including the operator's own stake). At epoch 614, this mechanism processed **6.80M ADA** across 991 rewarded pools — but the headline aggregate (24.6% operator take) conceals three radically different strategies. Adopting the Hollow–Private pledge spectrum from the upstream analysis ([§2.4.2](../../../cardano-reward-analysis.md#242-progression--balanced-as-intended-but-private-by-design)), this report classifies entities by **owner-stake ratio** (owner active stake / pool active stake) across their pool fleets. Three strategies emerge along this spectrum: the **hollow strategy** (owner-stake ratio < 10%, 501 entities, 836 pools, 18.14B ADA, op_take=13.58%) where entities depend entirely on external delegation; the **balanced strategy** (10–95% owner-stake, 95 entities, 109 pools, 0.80B ADA, op_take=14.3%) where entities and delegators share capital with genuine alignment; and the **private strategy** (≥ 95% owner-stake, 13 entities, 46 pools, 2.29B ADA, op_take=99.95%) where entities are operator-funded. Remarkably, 601 of 609 entities (98.7%) apply a single pure strategy across all their pools, demonstrating high strategic consistency. Within hollow-strategy entities, a sub-population of 50 "hollow captive" pools (margin ≥ 99.9%, typically exchanges and custodians) extract 100% via margin, leaving 785 genuine hollow pools at 7.9% operator take. The entity-level analysis reveals that margin competition is broadly active in the genuine hollow market (median entity margin 1.0%, stake-weighted 8.9%) but fixed cost, not margin, is the dominant extraction channel. Balanced-strategy entities form the smallest population but analytically most significant: they are where the pledge mechanism produces genuine alignment, with many pools carrying Material or High pledge tags and median owner-ratio 26.4%.

The argument proceeds in seven steps:

1. **The formula** (§2). The SL-D1 intra-pool reward-sharing specification — from the original design through a reader-friendly rewrite to mainnet parameterization. The mechanism is sequential: fixed cost first, margin on the remainder, then pro-rata distribution. A critical protocol detail: when $\hat{f} < c$, the operator takes $\hat{f}$ (not $c$) — the effective fixed cost is $\min(c, \hat{f})$.

2. **Three strategies** (§3). The 609 entities operating rewarded pools classify into three populations by the owner-stake ratio of their fleet: hollow (< 10%), balanced (10–95%), and private (≥ 95%). This spectrum captures fundamentally different funding structures and competitive positions. The same analytical framework — intra-pool split composition, margin behaviour, fee structure — is then applied to each population separately (§4, §5, §6). Strategy consistency is the key finding: 98.7% of entities apply a single pure strategy across their entire fleet (§3.2).

3. **The hollow strategy market** (§4). The 501 entities following the hollow strategy (836 pools, 18.14B ADA, op_take=13.58%) depend entirely on external delegation, forming the public delegation market, with 50 hollow captive pools (exchanges, custodians: 100% extraction) distorting the aggregate. Excluding them, the genuine market (785 pools) operates at 7.9% operator take — with fixed cost (4.4%) slightly exceeding margin (3.6%). At the entity level, median margin is 1.0% and stake-weighted mean is 8.9%, confirming active margin competition. The dominant extraction in the genuine market is the fixed-cost floor, not margin.

4. **The balanced strategy population** (§5). The 95 entities following the balanced strategy (109 pools, 0.80B ADA, op_take=14.3%) split capital between themselves and delegators with genuine alignment. Median owner-ratio is 26.4%, margins are low, and many pools carry Material or High pledge tags — genuine skin-in-the-game. This is the only population where the pledge mechanism produces meaningful operator alignment.

5. **The private strategy universe** (§6). The 13 entities following the private strategy (46 pools, 2.29B ADA, op_take=99.95%) are operator-funded and absorb 99.95% of their rewards as operator take. Margin is an accounting choice (vast majority set ≥ 99.9%), fixed cost negligible. Paradoxically, entities in this group often carry Low or Zero pledge tags despite owning the capital and facing no custodial constraint — the pledge mechanism does not appear to attract commitment even where conditions are most favourable.

6. **Strategy consistency across fleets** (§3.2). The empirical finding: 601 of 609 entities (98.7%) apply a single pure strategy across all their pools. Only 8 entities are hybrid (operating pools in multiple strategy bins), and they cluster near threshold boundaries. This justifies using entity-level strategy grouping and validates the framing of these as deliberate, coherent strategic choices rather than pool-level accidents.

7. **Structural implications** (§7). The fixed-cost floor creates a regressive tax on small-pool delegators. Margin competition is active in the genuine hollow market (median entity margin 1.0%) but the fixed cost, being a flat ADA amount, penalises small pools disproportionately. The two-regime structure — where fixed cost dominates small pools and margin dominates large pools — has direct consequences for any future mechanism revision.

All counts and amounts use epoch **614** (the latest settled epoch with complete reward data). Source data: `koios_pool_history_mainnet.csv`, `koios_pool_owner_history_mainnet.csv`, `koios_pool_list_mainnet.csv`, `mpo_entity_pool_mapping_mainnet.csv` (Koios + entity attribution from the [*pools-distribution*](../../pools-distribution/mainnet-analysis/) flow).

## Contents

1. [Mainnet Observations](#1-mainnet-observations)
2. [The formula — intra-pool reward sharing](#2-the-formula--intra-pool-reward-sharing)
   - 2.1 [SL-D1 specification](#21-sl-d1-specification)
   - 2.2 [Reader-friendly formulation](#22-reader-friendly-formulation)
   - 2.3 [Mainnet parameterization](#23-mainnet-parameterization)
   - 2.4 [Concept glossary](#24-concept-glossary)
3. [Three strategies](#3-three-strategies)
   - 3.1 [Strategy classification](#31-strategy-classification)
   - 3.2 [Strategy consistency](#32-strategy-consistency)
   - 3.3 [The split at a glance](#33-the-split-at-a-glance)
4. [The hollow strategy](#4-the-hollow-strategy)
   - 4.1 [The hollow captive sub-population](#41-the-hollow-captive-sub-population)
   - 4.2 [The genuine market — current snapshot (epoch 614)](#42-the-genuine-market--current-snapshot-epoch-614)
   - 4.3 [Historical evolution of the split](#43-historical-evolution-of-the-split)
   - 4.4 [The two components — fixed cost vs margin](#44-the-two-components--fixed-cost-vs-margin)
   - 4.5 [The effective tax on delegators](#45-the-effective-tax-on-delegators)
   - 4.6 [Fixed-cost dominance at the small-pool end](#46-fixed-cost-dominance-at-the-small-pool-end)
   - 4.7 [Margin distribution — by pool and by entity](#47-margin-distribution--by-pool-and-by-entity)
   - 4.8 [Fee parameter adoption](#48-fee-parameter-adoption)
   - 4.9 [MPO vs SPO operator take](#49-mpo-vs-spo-operator-take)
   - 4.10 [Top entities by operator take](#410-top-entities-by-operator-take)
   - 4.11 [Key findings — hollow strategy](#411-key-findings--hollow-strategy)
5. [The balanced strategy](#5-the-balanced-strategy)
   - 5.1 [Composition and structure](#51-composition-and-structure)
   - 5.2 [Intra-pool split](#52-intra-pool-split)
   - 5.3 [Margin behaviour](#53-margin-behaviour)
   - 5.4 [The pledge signal — where it works](#54-the-pledge-signal--where-it-works)
   - 5.5 [Key findings — balanced strategy](#55-key-findings--balanced-strategy)
6. [The private strategy](#6-the-private-strategy)
   - 6.1 [Composition](#61-composition)
   - 6.2 [Intra-pool split](#62-intra-pool-split)
   - 6.3 [Margin behaviour](#63-margin-behaviour)
   - 6.4 [Pledge behaviour](#64-pledge-behaviour)
   - 6.5 [Key findings — private strategy](#65-key-findings--private-strategy)
7. [Structural implications](#7-structural-implications)
   - 7.1 [Two regimes, one mechanism](#71-two-regimes-one-mechanism)
   - 7.2 [The fixed-cost floor as a regressive tax on small pools](#72-the-fixed-cost-floor-as-a-regressive-tax-on-small-pools)
   - 7.3 [Margin competition in the hollow strategy market](#73-margin-competition-in-the-hollow-strategy-market)
   - 7.4 [Open questions](#74-open-questions)
8. [Reproduction](#8-reproduction)

## 1. Mainnet Observations

| # | Observation | Section | Nature |
| --- | --- | --- | --- |
| | **O1 — Three disjoint strategies coexist on-chain** | | |
| F1.1 | 501 entities following the hollow strategy (836 pools, 85.1% of pool count) control 18.14B ADA (85.4%), with owner-stake ratio < 10% — these entities depend entirely on external delegation | §3 | Structural |
| F1.2 | 95 entities following the balanced strategy (109 pools, 11.0% of pool count) control 0.80B ADA (3.8%), with owner-stake ratio 10–95% — entities with genuine capital commitment alongside external delegation | §3 | Structural |
| F1.3 | 13 entities following the private strategy (46 pools, 4.6% of pool count) control 2.29B ADA (10.8%), with owner-stake ratio ≥ 95% — operator-funded entities with 99.95% operator take | §3 | Structural |
| F1.4 | 601 of 609 entities (98.7%) apply a single pure strategy across all their pools; only 8 are hybrid (near-threshold edge cases) — strategies are deliberate, coherent choices | §3.2 | Consistency |
| F1.5 | 50 hollow-strategy pools (stakes ≥ 99.9% margin, median owner-ratio ~1.75%) distort the hollow-strategy aggregate from 7.9% to 13.58% operator take | §4.1 | Methodological |
| | **O2 — In the genuine hollow-strategy market, fixed cost slightly exceeds margin** | | |
| F2.1 | Hollow-strategy aggregate (836 pools): 13.58% operator take — distorted by 50 hollow captive pools | §4.2 | Epoch 614 |
| F2.2 | Genuine hollow-strategy market (785 pools): operator take 7.9% — fixed cost 4.4%, margin 3.6% | §4.2 | Fixed cost > margin |
| F2.3 | Delegators receive 4.90M ADA (87.04% of hollow) for pro-rata distribution | §4.2 | Hollow market |
| | **O3 — Entity-level margin analysis reveals broad competition** | | |
| F3.1 | 596 distinct entities operate in the hollow market (79 MPO entities, 517 SPO entities) | §4.7 | Entity-level |
| F3.2 | Entity-level median margin: 1.0%; stake-weighted mean: 8.9% — margin competition active but hollow captive pools distort the weighted average | §4.7 | Low margins |
| F3.3 | 348 entities (58.4%) operate below 2% margin; 62 (10.4%) exceed 5% | §4.7 | Competitive |
| F3.4 | 37 entities use mixed margin policies across their pool fleets | §4.7 | Tiered pricing |
| | **O4 — The fixed cost is a regressive tax on small-pool delegators** | | |
| F4.1 | Effective tax ranges from ~4% (large low-margin pools) to 100% (sub-viable pools where $c \geq \hat{f}$) | §4.5 | Pool-size driven |
| F4.2 | Fixed-cost share follows a hyperbola: $\min(c, \hat{f}) / \hat{f}$, decaying as $1/\sigma$ | §4.6 | Mathematical identity |
| F4.3 | 93.5% of hollow-strategy pools declare the minimum fixed cost (340 ADA) — the floor is the norm | §4.8 | Near-universal |
| | **O5 — SPO pools bear a heavier effective tax than MPO pools** | | |
| F5.1 | Hollow SPO pools (492): 11.1% operator take — driven by higher fixed-cost incidence on smaller pools | §4.9 | Size effect |
| F5.2 | Hollow MPO pools (404): 7.2% operator take — scale dilutes the fixed-cost burden | §4.9 | Economies of scale |
| | **O6 — Balanced-strategy entities are analytically significant despite small share** | | |
| F6.1 | 95 balanced-strategy entities (11.0% of pool count): median owner-ratio 26.4%, many with Material/High pledge tags | §5 | Pledge signal |
| F6.2 | Balanced-strategy operator take 14.3% — fixed cost dominates (13.21%) because pools are small; margin 4.19% low | §5.2 | Structural |
| F6.3 | This is where the pledge mechanism produces meaningful alignment — unique to this population | §5.4 | Incentive design |

### The big picture

**What the formula does.** Once the reward curve assigns a total reward $\hat{f}$ to a pool, the intra-pool split extracts operator compensation in two steps: a **fixed cost** $\min(c, \hat{f})$ subtracted first, then a **proportional margin** $m$ applied to the remainder $\max(\hat{f} - c, 0)$. Everything left is distributed pro-rata among all pool members by stake share — including the operator's own stake.

**Three strategies.** At epoch 614, 609 entities operate rewarded pools — but they do not follow a single template. Following the Hollow–Private pledge spectrum from the upstream analysis, this report classifies entities by **dominant owner-stake ratio** across their fleet: the axis runs from hollow (external delegation dominates) through balanced (genuine capital-sharing) to private (operator-funded). 501 entities follow the hollow strategy (836 pools, 18.14B ADA), 95 follow the balanced strategy (109 pools, 0.80B ADA), and 13 follow the private strategy (46 pools, 2.29B ADA). Remarkably, 98.7% of entities apply a single pure strategy across their entire fleet. The pool-level heterogeneity is strategic consistency at the entity level.

![Three Strategies — Entity-Level View](figures/three_strategies.png)

**Strategy consistency.** Among 609 entities, 601 (98.7%) operate pools that all fall into the same strategy bin. Only 8 entities are hybrid (spanning multiple bins), and they cluster near threshold boundaries. This extraordinary consistency shows that entities choose a fundamental strategy and apply it coherently across their pool fleet. An entity does not run one hollow pool and one private pool — it commits to a strategy.

**The hollow-strategy market — with a caveat.** Among entities following the hollow strategy, operator take is **13.58%** in aggregate (836 pools). But 50 of these pools are *hollow captive* — exchanges and custodians that own almost none of their stake (mean owner-ratio 1.75%) yet set margin ≥ 99.9%, extracting everything. Excluding them, the genuine market (785 pools) operates at **7.9%** operator take — split between fixed cost (4.4%) and margin (3.6%). Fixed cost slightly exceeds margin, reflecting a population where 93.5% declare the minimum 340 ADA cost.

**Entity-level analysis.** Counting by pool overcounts fee policies: entities operating many pools pursue a single (or a few) policy decisions per strategy, not one per pool. Across 596 distinct entities in the hollow market, the median margin is **1.0%** and 58% of entities operate below 2%. Margin competition is broadly active. The dominant extraction in the hollow market is the fixed-cost floor, not margin.

**The balanced-strategy population.** The 95 entities following the balanced strategy (11.0% of pool count, 3.8% of stake, median owner-ratio 26.4%) form an analytically crucial segment where the pledge mechanism produces genuine alignment. Many carry Material or High pledge tags — genuine skin-in-the-game. They are the smallest segment but structurally important: they demonstrate that entities with real capital at stake behave differently and compete fiercely on fees.

**Why it matters for mechanism design.** The two-regime structure reveals that the intra-pool split does not operate as a single, uniform mechanism. The fixed-cost floor creates a regressive tax that penalises small-pool delegators disproportionately, while margin competition functions effectively in the large-pool regime. Any revision to the fee structure should account for this bifurcation — the small-pool regime and the large-pool regime respond to different parameters and require distinct analytical treatment.

## 2. The formula — intra-pool reward sharing

The intra-pool split was specified in [*Design Specification for Delegation and Incentives in Cardano*](https://github.com/IntersectMBO/cardano-ledger/releases/latest/download/shelley-delegation.pdf) (Kant, Brünjes & Coutts, IOHK, 2019 — deliverable **SL-D1**, §5.5.4). The mechanism has been operational on mainnet since the Shelley hard fork on 2020/07/29 and its governing parameters have never been modified by governance action.

### 2.1 SL-D1 specification

Once the reward curve produces a pool's actual (performance-adjusted) reward $\hat{f}(s, \sigma, \bar{p})$, the protocol splits it according to two parameters declared by the operator at pool registration:

- $c$ — the **fixed cost** in ADA per epoch (minimum 340 ADA under the current `minPoolCost` protocol parameter)
- $m$ — the **margin** as a fraction in $[0, 1]$

The split is sequential and deterministic. Critically, the protocol caps the fixed cost at the pool reward:

$$
c_{\text{eff}} = \min(c, \hat{f})
$$

$$
\text{Operator fees} = c_{\text{eff}} + m \cdot (\hat{f} - c_{\text{eff}})
$$

$$
\text{Delegator pot} = (1 - m) \cdot (\hat{f} - c_{\text{eff}})
$$

$$
\text{Delegator}_i\text{'s share} = \frac{s_i}{\sigma} \cdot \text{Delegator pot}
$$

where $s_i$ is the individual delegator's active stake and $\sigma$ is the pool's total active stake (including the operator's own stake). When $\hat{f} \leq c$, the operator receives $\hat{f}$ and delegators receive nothing.

The operator's **total income** from the pool is therefore:

$$
\text{Operator total} = \underbrace{c_{\text{eff}} + m(\hat{f} - c_{\text{eff}})}_{\text{declared fees}} + \underbrace{\frac{s_{\text{owner}}}{\sigma} \cdot (1 - m)(\hat{f} - c_{\text{eff}})}_{\text{pro-rata on own stake}}
$$

If the declared pledge is not met in the epoch, $\hat{f} = 0$ and no rewards are distributed.

### 2.2 Reader-friendly formulation

The split can be understood as a three-step pipeline:

1. **Cost recovery.** The effective fixed cost $c_{\text{eff}} = \min(c, \hat{f})$ is subtracted from the pool reward and paid entirely to the operator. This is intended to compensate for hardware, bandwidth, and operational expenses. The protocol enforces a minimum (`minPoolCost` = 340 ADA) to prevent a race-to-zero that could undermine operational sustainability. For sub-viable pools where $\hat{f} < c$, the operator receives the entire reward and delegators earn nothing.

2. **Margin extraction.** The operator takes a declared percentage $m$ of the remaining reward $(\hat{f} - c_{\text{eff}})$. This is the **competitive parameter** — the lever operators are meant to adjust to attract or retain delegation. A lower margin means more ADA flows to delegators.

3. **Pro-rata distribution.** The remainder $(1 - m)(\hat{f} - c_{\text{eff}})$ is distributed proportionally among all pool members by stake — including the operator's own pledged or staked capital. The operator therefore earns twice: once through fees ($c_{\text{eff}} + m$), and again through their pro-rata share.

### 2.3 Mainnet parameterization

| Parameter | Value | Set by |
| --- | --- | --- |
| `minPoolCost` ($c_{\min}$) | 340 ADA | Protocol parameter (governance) |
| Fixed cost ($c$) | Operator-declared, $\geq c_{\min}$ | Pool registration certificate |
| Margin ($m$) | Operator-declared, $\in [0, 1]$ | Pool registration certificate |

At epoch 614 (hollow-strategy pools): 93.5% of rewarded hollow-strategy pools declare $c = 340$ ADA (the minimum). The median declared margin is 2.0%; the entity-level median is 1.0% and the stake-weighted mean is 3.8%.

### 2.4 Concept glossary

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

## 3. Three strategies

### 3.1 Strategy classification

The upstream analysis ([§2.4.2](../../../cardano-reward-analysis.md#242-progression--balanced-as-intended-but-private-by-design)) defines a five-point pledge-commitment spectrum — from **Hollow** (zero pledge, all self-delegation) to **Private** (100% pledge, no outside delegation) — to characterise how operators allocate capital within a pool. The fundamental axis is the **proportion of owner stake to total active stake**: a private-strategy entity funds its pools entirely; a hollow-strategy entity depends on external delegation.

This report adopts the same axis to classify all 609 entities operating rewarded pools. The classification divides the spectrum into three populations based on a single observable criterion applied at the **entity level**: **dominant owner-stake ratio** (mean owner active stake / mean pool active stake across all pools operated by the entity).

- **Hollow strategy** (owner-stake ratio < 10%, 501 entities): entities that depend entirely on external delegation across their fleet
- **Balanced strategy** (owner-stake ratio 10–95%, 95 entities): entities with genuine capital at stake alongside external delegators
- **Private strategy** (owner-stake ratio ≥ 95%, 13 entities): operator-funded entities where external delegation is negligible

The classification is applied **per entity, not per pool**, and reflects the dominant strategic choice. It captures a fundamentally different dimension than margin: an entity following the balanced strategy can set a competitive margin, or an entity following the hollow strategy can extract via margin. The entity-level framing reflects that these are deliberate, fleet-wide strategic commitments, not accidents of individual pool composition.

### 3.2 Strategy consistency

A critical empirical finding validates the entity-level framing: **entity-level strategies are highly consistent.**

| | Count | Percentage |
| --- | --- | --- |
| **Pure-strategy entities** | | |
| Hollow only | 495 | 81.3% |
| Balanced only | 93 | 15.3% |
| Private only | 13 | 2.1% |
| **Subtotal pure** | **601** | **98.7%** |
| **Hybrid entities** | | |
| Hollow + Balanced | 6 | 1.0% |
| Hollow + Balanced + Private | 2 | 0.3% |
| **Subtotal hybrid** | **8** | **1.3%** |
| **Total** | **609** | **100%** |

Of 609 entities, 601 (98.7%) operate pools that all fall into a single strategy bin. Only 8 entities are hybrid — spanning two strategy bins — and analysis shows they cluster at or near the threshold boundaries (owner-stake ratio ~10% and ~95%), suggesting measurement noise or near-threshold entities rather than deliberate multi-strategy positioning.

This consistency demonstrates that strategy classification at the entity level is not arbitrary: entities choose a dominant strategy and apply it across their entire pool fleet. The three strategies are game-theoretic choices, not pool-level artifacts. An entity commits to hollow strategy (compete for external delegation), balanced strategy (share capital with delegators), or private strategy (self-fund and operate internally) — and follows that choice coherently.

The 8 hybrid entities are edge cases. Examining them reveals:
- Most are near decision boundaries (owner-ratios 8–12% or 93–97%)
- Several have very small secondary-strategy pool(s), suggesting pilot or transitional operations
- None blur the distinction meaningfully — they are boundary anomalies in a highly consistent distribution

This justifies the entity-level strategic framing throughout the rest of this report. When we reference "entities following the hollow strategy," we refer to a coherent, deliberately-chosen business model shared by 495 pure-strategy entities, observed for 601/609 (98.7%) of all entities.

### 3.3 The split at a glance

| | Hollow | Balanced | Private | All |
| --- | --- | --- | --- | --- |
| Entities | 501 | 95 | 13 | 609 |
| Pools | 836 | 109 | 46 | 991 |
| Active stake | 18.14B ADA (85.4%) | 0.80B ADA (3.8%) | 2.29B ADA (10.8%) | 21.23B ADA |
| Owner stake | 0.18B ADA (1.0%) | 0.41B ADA (51.8%) | 2.29B ADA (99.9%) | 2.88B ADA (13.6%) |
| Total rewards | 5,643,575 ADA | 292,588 ADA | 860,906 ADA | 6,797,069 ADA |
| Operator take | 766,565 (13.58%) | 41,831 (14.3%) | 860,469 (99.95%) | 1,668,864 (24.55%) |
| Delegator pot | 4,877,011 (86.42%) | 250,757 (85.7%) | 438 (0.05%) | 5,128,205 (75.45%) |

![Three Strategies — Entity-Level View](figures/three_strategies.png)

The entity-level view clarifies what the pool-level framing obscured. The hollow strategy encompasses 85.4% of delegated stake across 501 entities that collectively operate 836 pools — a coherent market segment. The balanced strategy encompasses 3.8% of stake across 95 entities — analytically small but structurally important (pledge works here). The private strategy encompasses 10.8% of stake across 13 entities that operate 46 pools as internal capital allocation. These are not three arbitrary buckets; they are three radically different models observed with remarkable consistency.

The three strategies operate under different logics — hollow-strategy entities compete for external delegation, balanced-strategy entities split capital with committed delegators, and private-strategy entities are internal accounting operations for self-funded operators. The following three sections apply the same analytical framework to each strategy independently.

## 4. The hollow strategy

All analysis in this section is restricted to the **501 entities following the hollow strategy** (owner-stake ratio < 10%, 836 pools). These entities depend entirely on external delegation and form the public delegation market where fee-competition dynamics apply.

### 4.1 The hollow captive sub-population

Before analysing the hollow-strategy market, a distortion must be isolated. 50 pools operated by hollow-strategy entities set margin ≥ 99.9% despite owning on average only 1.75% of their stake. These are exchanges and custodial operators running captive staking infrastructure: the delegated capital belongs to their users, not to the operator. They are *hollow* in the capital-composition sense — minimal owner stake — yet they extract 100% of rewards via margin.

| | Hollow captive | Genuine hollow | All hollow |
| --- | --- | --- | --- |
| Pools | 50 | 785 | 835 |
| Active stake | 0.98B ADA | 17.13B ADA | 18.11B ADA |
| Total rewards | 308K ADA | 5.32M ADA | 5.63M ADA |
| Operator take | 308K ADA (100.0%) | 422K ADA (7.9%) | 730K ADA (12.96%) |
| Delegator pot | ~0 ADA (0.0%) | 4.90M ADA (92.1%) | 4.90M ADA (87.04%) |

Among hollow captive pools with upstream health metadata: 15 carry Zero pledge, 6 Minimal pledge. The upstream analysis identifies the architectural constraint: custodial operators cannot pledge the capital they manage ([§2.4.3.2](../../../cardano-reward-analysis.md#2432-delegating-is-inherently-less-constraining-than-pledging)). They reached the extraction endpoint without traversing the pledge arc. Their 0.98B ADA in stake exists in the hollow universe by capital composition but outside the fee market by behaviour — their delegators (exchange customers) do not choose pools based on on-chain fee parameters.

All subsequent analysis in this section covers the full 835-pool hollow segment (all pools operated by hollow-strategy entities). Where the hollow captive distortion materially affects an aggregate, it is noted.

### 4.2 The genuine market — current snapshot (epoch 614)

| Component | ADA | Share of hollow distributed |
| --- | --- | --- |
| Total distributed rewards | 5,626,084 | 100% |
| **Operator take** (fees) | **729,257** | **12.96%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 291,187 | 5.18% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 438,070 | 7.79% |
| **Delegator pot** (pro-rata) | **4,896,827** | **87.04%** |

![Intra-Pool Reward Split — Pools Operated by Hollow-Strategy Entities, Epoch 614](figures/reward_split_waterfall.png)

In the full hollow segment (835 pools operated by hollow-strategy entities), operator take is 12.96%. This aggregate is inflated by 50 hollow captive pools (§4.1) that extract 100% via margin despite owning almost none of the stake. In the genuine hollow market (785 pools, excluding hollow captive), operator take is 7.9% — with fixed cost (4.4%) slightly exceeding margin (3.6%). The waterfall above reflects the full 835-pool hollow segment.

### 4.3 Historical evolution of the split

![Reward Split — Pools Operated by Hollow-Strategy Entities, Historical](figures/reward_split_area_timeseries.png)

The stacked-area timeseries decomposes the hollow-segment distributed reward into its three components — effective fixed cost, margin, and delegator pot — across 405 epochs. The delegator pot dominates throughout the observation window. The fixed-cost and margin bands are thin and roughly comparable in magnitude. The absolute size of distributed rewards has declined, tracking the monetary expansion draw (documented in the [*Treasury & Pool Pots*](../../treasury-and-pool-pots-distribution/mainnet-analysis/) companion report).

### 4.4 The two components — fixed cost vs margin

![Operator Take Share — Historical](figures/operator_take_pct_timeseries.png)

The line chart decomposes the operator-take percentage over time for pools operated by hollow-strategy entities:

- **Fixed-cost share (~4–6%)** is slowly rising as per-pool rewards decrease with declining monetary expansion — the flat 340 ADA floor consumes a growing fraction of shrinking rewards.
- **Margin share (~3–4%)** is stable and low, reflecting the competitive dynamics in the hollow-strategy market.
- **Total operator take (hollow, ~8–10%)** is the sum of both, trending slowly upward — driven by the fixed-cost component.

The dotted line shows the all-pools aggregate (including private and balanced) for reference — the gap between the hollow and all-pools lines is entirely attributable to private-strategy-pool absorption.

### 4.5 The effective tax on delegators

The effective tax is defined as the operator take (on-chain `pool_fees`) divided by the total pool reward: $\text{pool\_fees} / \hat{f}$. It measures the fraction of the pool's reward that is extracted before pro-rata distribution.

![Effective Tax on Delegators — Pools Operated by Hollow-Strategy Entities](figures/effective_tax_distribution.png)

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 27.8% |
| Median | 13.5% |
| Stake-weighted mean | 8.4% |
| 10th percentile | 3.7% |
| 90th percentile | 99.2% |

The divergence between unweighted mean (27.8%) and stake-weighted mean (8.4%) reveals the size effect: small pools face high effective tax (driven by the fixed-cost floor) but hold little stake. The bulk of delegated ADA sits in large pools with low effective tax. The median (13.5%) lies between these because small pools are numerous.

### 4.6 Fixed-cost dominance at the small-pool end

![Fixed-Cost Dominance — Pools Operated by Hollow-Strategy Entities](figures/fixed_cost_dominance.png)

The scatter of fixed-cost share versus pool size reveals the structural mechanism at the small-pool end:

$$
\frac{c_{\text{eff}}}{\hat{f}} \approx \frac{c_{\min}}{\sigma \cdot y}
$$

where $\sigma$ is the pool's active stake and $y$ is the per-ADA-per-epoch yield (~0.032% at epoch 614). This is a **hyperbola in pool size** — the fixed cost's share of the reward decays as $1/\sigma$.

The empirical points follow the theoretical curve closely. At 1M ADA stake, the fixed cost consumes ~100% of the reward. At 10M ADA, it consumes ~10%. At the saturation threshold (~77M ADA), it consumes ~1.4%. For pools above ~10M ADA, the fixed-cost share is negligible and margin becomes the dominant extraction. The viability threshold — the stake below which the fixed cost exceeds the total reward — aligns with the ~1.1M ADA boundary identified in the companion [*pools-distribution*](../../pools-distribution/mainnet-analysis/) analysis.

### 4.7 Margin distribution — by pool and by entity

![Margin Rate Distribution — Pool Count vs Entity Count](figures/margin_rate_distribution.png)

**Pool-level statistics (835 pools operated by hollow-strategy entities):**

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 4.0% |
| Median | 2.0% |
| Stake-weighted mean | 3.8% |
| Pools at 0% margin | 21.2% |
| Pools below 2% margin | 49.4% |
| Pools above 5% margin | 7.7% |

**Entity-level statistics (501 hollow-strategy entities):**

| Statistic | Value |
| --- | --- |
| Mean (unweighted) | 3.5% |
| Median | 1.0% |
| Stake-weighted mean | 3.8% |
| Entities at 0% margin | 157 (31.3%) |
| Entities below 2% margin | 348 (69.5%) |
| Entities 2–5% margin | 190 (37.9%) |
| Entities above 5% margin | 62 (12.4%) |

The entity-level view is more informative than the pool-level view because fee-policy decisions are made per entity, not per pool. Entities like Coinbase run many pools at a tiered margin strategy — that is one (or a few) policy decisions, not one per pool. 35 entities use **mixed margin policies** across their pool fleets, typically with slight variation (e.g. Blockdaemon: 3%, 6%, 8%, 10%) that may reflect vintage, client tier, or pricing segmentation.

The median entity margin of 1.0% confirms that margin competition is broadly active in the hollow-strategy market. The bulk of entities cluster at 0–2%, with a thin tail extending to 10%. The stake-weighted mean (3.8%) is close to the unweighted mean (3.5%), indicating that margin policy does not vary dramatically with entity size — a healthy sign of competitive equilibrium.

### 4.8 Fee parameter adoption

![Fee Parameter Evolution — Pools Operated by Hollow-Strategy Entities](figures/fee_parameter_evolution.png)

The historical evolution of fee parameter adoption among pools operated by hollow-strategy entities shows:

- **93.5% of rewarded pools operated by hollow-strategy entities** declare the minimum fixed cost (340 ADA). This fraction has remained stable at ~90% throughout the observation window. Operators treat the minimum as the norm.

- **~20% of rewarded pools operated by hollow-strategy entities** declare 0% margin, a share that has grown slowly over time — a sign of increasing competitive pressure.

The margin-rate evolution panel shows the median (solid) and stake-weighted mean (dashed) margin for hollow-strategy pools. Both have converged toward low single digits, confirming active competition.

### 4.9 MPO vs SPO operator take

![MPO vs SPO Operator Take — Hollow-Strategy Pools](figures/mpo_vs_spo_operator_take.png)

| Entity type | Pools | Total rewards (ADA) | Operator take (ADA) | Operator take (%) |
| --- | --- | --- | --- | --- |
| MPO | 404 | 4,080,568 | 293,724 | 7.2% |
| SPO | 492 | 1,508,029 | 166,672 | 11.1% |

In the hollow-strategy market, **SPO pools bear a higher effective operator take** (11.1% vs 7.2%) — the reverse of the all-pools picture. The explanation is straightforward: SPO pools are smaller on average, and the fixed-cost floor extracts a larger share of their smaller rewards. MPO pools benefit from economies of scale — their larger $\hat{f}$ dilutes the flat 340 ADA cost. This is a structural consequence of the fixed-cost floor, not a margin-competition failure.

### 4.10 Top entities by operator take

![Top 20 Entities by Operator Take — Hollow-Strategy Market](figures/top20_entities_operator_take.png)

The top 20 entities by absolute operator take in the hollow-strategy market are dominated by large MPO operators. The decomposition shows the balance between fixed cost (red) and margin (orange) for each entity. For entities running many pools (e.g. Coinbase: 41 pools), fixed cost accumulates through pool count even at low per-pool cost — this is an entity-level consequence of the cost floor that is invisible at the pool level.

### 4.11 Key findings — hollow strategy

The intra-pool split in the hollow-strategy market operates as a genuine competitive mechanism — but with two distortions. First, 50 hollow captive pools inflate the aggregate operator take from 7.9% to 12.96%; they sit in the hollow universe by capital composition but outside the fee market by behaviour. Second, the fixed-cost floor creates a regressive tax that penalises small-pool delegators: the effective tax for a 3M ADA pool is ~35%, versus ~4% for a large pool. Margin competition is broadly active in the hollow-strategy market (median entity margin 1.0%), but fixed cost — not margin — is the dominant extraction channel in the genuine market. The competitive dynamics envisioned in SL-D1 function in this universe; the structural concern is the cost floor, not the margin mechanism.

## 5. The balanced strategy

All analysis in this section is restricted to the **95 entities following the balanced strategy** (owner-stake ratio 10–95%, 109 pools). These entities have genuine capital commitment and form the segment where the pledge mechanism produces meaningful alignment.

### 5.1 Composition and structure

The 95 entities following the balanced strategy control 0.80B ADA (3.8% of total active stake) and generate 227K ADA/epoch in rewards. The median owner-stake ratio across entities is 26.4%, indicating genuine operator capital commitment. Operator owner-ratio averages 40.0% — these are entities where the operator has real skin in the game.

The population is overwhelmingly single-pool operators: 92 SPO pools versus 15 MPO pools among the 109 pools. Among the 15 pools with upstream category metadata, 7 are declared brands, 6 community-branded fleets, and 2 multi-brand fleets. The remaining 92 pools are unmapped — independent operators outside the upstream entity coverage.

### 5.2 Intra-pool split

| Component | ADA | Share of balanced distributed |
| --- | --- | --- |
| Total distributed rewards | 221,919 | 100% |
| **Operator take** (fees) | **38,626** | **17.41%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 29,319 | 13.21% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 9,307 | 4.19% |
| **Delegator pot** (pro-rata) | **183,292** | **82.59%** |

In the balanced segment (109 pools operated by balanced-strategy entities), operator take is 17.41%. Fixed cost dominates (13.21%) because these pools are smaller on average than the hollow large-pool regime — the 340 ADA floor consumes a larger fraction of smaller rewards. Margin (4.19%) is low, reflecting competitive dynamics and the presence of committed operators with skin-in-the-game.

### 5.3 Margin behaviour

| Margin range | Pools | Stake (B ADA) |
| --- | --- | --- |
| < 2% | 60 (56.1%) | 0.15 |
| 2–5% | 43 (40.2%) | 0.43 |
| > 5% | 4 (3.7%) | 0.03 |

56.1% of pools operated by balanced-strategy entities set margin below 2%, reflecting a population where fee competition is active and operators have committed capital. The median margin is 1.5%, confirming competitive pricing. The 2–5% bracket holds the most stake (0.43B ADA) because it includes several larger balanced-strategy pools with moderate margin policies.

### 5.4 The pledge signal — where it works

Among the 15 pools operated by balanced-strategy entities with upstream health metadata (the coverage is partial — the upstream health dataset maps 466 of 991 rewarded pools):

| Pledge tag | Pools | Stake |
| --- | --- | --- |
| Material pledge | 9 | 0.07B ADA |
| High pledge | 6 | 0.32B ADA |

All 15 mapped pools operated by balanced-strategy entities carry Material or High pledge tags — genuine, formal capital commitment. No Low or Zero pledge tags appear in this population. While the coverage is limited, the pattern is structurally significant: entities following the balanced strategy who are visible in the health dataset consistently pledge meaningfully.

This is the only population where meaningful pledge adoption occurs in tandem with competitive margins (median 1.5%). The entities following the balanced strategy — those with 10–95% owner-stake ratio — demonstrate genuine alignment: they own enough capital to absorb loss, they formally pledge it, and they compete on fees. This population proves that the pledge mechanism *can* work when operators have committed capital.

### 5.5 Key findings — balanced strategy

Entities following the balanced strategy form a tiny segment (3.8% of delegated stake, 95 entities, 109 pools) but are analytically significant: they are the *only* population where the pledge mechanism produces meaningful operator alignment. The presence of high pledge-commitment signals in balanced-strategy entities, paired with aggressive fee competition (median margin 1.5%), demonstrates that when operators have genuine capital at stake, the incentive mechanism works as intended. The network is polarized between hollow (externally-funded) and private (operator-funded) entities, with almost nothing in between — the balanced segment proves that genuinely committed intermediate operators exist but are rare. Their structural behaviour (low margins, high pledge commitment) should inform the design of future incentive mechanisms aimed at attracting committed operators.

## 6. The private strategy

All analysis in this section is restricted to the **13 entities following the private strategy** (owner-stake ratio ≥ 95%, 46 pools). These entities are operator-funded: the owner provides effectively all of the stake, and the intra-pool split is an internal accounting operation rather than a market transaction.

### 6.1 Composition

The 13 entities following the private strategy control 2.29B ADA (10.8% of total active stake) and generate 939K ADA/epoch in rewards. Owner-stake ratio averages 99.5% — outside delegation is negligible.

The population includes branded entities (24 pools), unresolved-label operators (12), platform-cluster pools (3), and protocol projects (2). The MPO/SPO split: 41 pools belong to multi-pool entities (2.17B ADA), 8 are single-pool operators (0.34B ADA). The two largest pools — each near full saturation at ~75M ADA — are declared-brand entities.

### 6.2 Intra-pool split

| Component | ADA | Share of private distributed |
| --- | --- | --- |
| Total distributed rewards | 949,067 | 100% |
| **Operator take** (fees) | **900,981** | **94.9%** |
| · Effective fixed cost ($c_{\text{eff}}$) | 15,080 | 1.6% |
| · Margin ($m \cdot (\hat{f} - c_{\text{eff}})$) | 885,901 | 93.3% |
| **Delegator pot** (pro-rata) | **48,086** | **5.1%** |

The operator extracts 94.9% of rewards. Margin (93.3%) dominates entirely — fixed cost is negligible (1.6%), both because the pools are large (diluting the flat 340 ADA floor) and because extraction is driven by declared margin, not the cost mechanism. The 5.1% that reaches the delegator pot reflects the five private pools with competitive margins (§6.3).

### 6.3 Margin behaviour

| Margin range | Pools | Stake (B ADA) | Operator take |
| --- | --- | --- | --- |
| ≥ 99.9% | 44 (89.8%) | 2.19 | ~100% |
| 2–5% | 3 | 0.15 | 4–5% |
| < 2% | 2 | 0.002 | < 2% |

44 of the 49 pools operated by private-strategy entities set margin ≥ 99.9%, absorbing effectively all rewards through the margin mechanism. This is the expected behaviour: when the operator is the sole funder, margin is an accounting choice — the fee is paid to oneself. Fixed cost is universally at the minimum (340 ADA across all 49 pools).

The five pools operated by private-strategy entities with competitive margins (1–4%) are the structural exception. The two largest — each near saturation at ~75M ADA, owner-ratio ~99% — set 4% margin and distribute ~47K ADA/epoch to the delegator pot. These are self-funded operators that nonetheless participate in the fee market, either to attract marginal external delegation or for signalling purposes. They demonstrate that being private (by capital composition) does not mechanically imply being extractive (by margin choice).

### 6.4 Pledge behaviour

Among the 41 pools operated by private-strategy entities with upstream health metadata:

| Pledge tag | Pools | Stake |
| --- | --- | --- |
| High pledge | 22 | 1.55B ADA |
| Low pledge | 15 | 517M ADA |
| Zero pledge | 3 | 96M ADA |
| Material pledge | 1 | 6M ADA |

22 pools are private in both the capital-composition and pledge-commitment senses — their operators fund the pool *and* formally pledge a significant share. But 18 of 41 (15 Low pledge + 3 Zero pledge) fund the pool from owner wallets without formally pledging the capital. These pools are **private by capital, hollow by pledge** — precisely the pattern the upstream analysis ([§2.4.3](../../../cardano-reward-analysis.md#243-endgame--the-hollow-strategy-is-the-dominant-one)) predicts: pledging imposes liquidity constraints and the pledge-unmet cliff, while the bonus it produces is negligible. Even operators who *could* pledge — they own the capital, there is no custodial constraint — rationally choose not to.

This finding reinforces the upstream observation: the pledge mechanism does not appear to attract commitment — not because operators lack capital, but because the incentive may be too weak to justify the constraints it imposes.

### 6.5 Key findings — private strategy

The intra-pool split at this stage is structurally trivial for entities following the private strategy — the operator funds the pools and collects the reward. Margin is an accounting choice (89.8% at 100%), fixed cost is negligible, and the delegator pot is effectively zero. The mechanism's fee-competition logic does not apply: there is no external delegation to compete for.

The analytical value lies in the pledge dimension. Entities following the private strategy are the population *most able* to pledge — they own the capital, face no custodial constraint, and would benefit most from the pledge bonus (their high owner-stake ratio maximises the bonus function). Yet 44% of mapped private-strategy pools do not pledge meaningfully. The pledge mechanism's limited effectiveness is most visible precisely where conditions for its success are most favourable.

## 7. Structural implications

### 7.1 Two regimes, one mechanism

The hollow-strategy-market data reveal that the intra-pool split operates as **two distinct regimes** depending on pool size:

**The small-pool regime** (below ~10M ADA stake): the 340 ADA fixed cost dominates the effective tax. For a pool at 3M ADA stake, the cost is ~35% of the reward; at 1M ADA, it exceeds the reward entirely. Margin, even when declared, contributes little because the reward after cost deduction is small. This regime affects ~73% of hollow-strategy pools but only a small fraction of delegated stake.

**The large-pool regime** (above ~10M ADA stake): the fixed cost is negligible (< 2% of reward). Margin is the binding parameter. A pool at 60M ADA stake and 3% margin extracts ~560 ADA/epoch through margin — modest but proportional. This regime holds most of the delegated stake and determines the stake-weighted aggregate.

In the genuine hollow-strategy market (excluding hollow captive pools), both regimes produce moderate effective taxes. The aggregate 7.9% operator take is low by design — the competitive dynamics envisioned in SL-D1 function in this universe. The policy concern is concentrated in the small-pool regime, where the cost floor creates disproportionate extraction.

### 7.2 The fixed-cost floor as a regressive tax on small pools

The 340 ADA minimum cost was designed to ensure operational sustainability. In practice, it functions as a **regressive tax on small-pool delegators**:

- At the saturation threshold (~77M ADA, $\hat{f}$ ≈ 24,000 ADA): 1.4% — negligible.
- At 3M ADA stake ($\hat{f}$ ≈ 960 ADA): 35% — material.
- At 1M ADA stake ($\hat{f}$ ≈ 320 ADA): exceeds the reward — the pool is non-viable.

The tax is regressive because it falls disproportionately on delegators in smaller pools — the participants with the least ability to switch (community-attached delegators, delegators who chose small pools for decentralisation reasons) bear the highest proportional extraction.

The entity-level view adds another dimension: entities operating many small pools multiply the cost-floor impact. An entity with 10 pools at 3M ADA stake each pays 3,400 ADA in fixed costs — 35% of its combined reward — while a single pool at 30M ADA pays only 340 ADA (3.5%). The cost floor penalises both small pools and multi-pool entities disproportionately.

### 7.3 Margin competition in the hollow strategy market

With private-strategy entities removed from the picture, the hollow-strategy market shows **healthy margin competition**. The entity-level median margin of 1.0% and the fact that 69.5% of entities operate below 2% indicate that the SL-D1 mechanism creates genuine competitive pressure in the hollow-strategy delegation market.

The small number of entities above 5% margin (62 out of 501) are not analogous to the private-strategy entities — they are hollow-strategy operators choosing to charge higher margins, presumably on differentiated service. The delegation market can discipline these margins if delegators are price-sensitive.

The previous analysis, which mixed private- and hollow-strategy entities, suggested that "margin competition exists where it matters least and fails where it matters most." With the private-strategy confound removed and the hollow and balanced populations distinguished, the revised finding is that margin competition is broadly active in the hollow-strategy market. The absence of competition is restricted to the private-strategy universe, where it is structural and deliberate — not a mechanism shortcoming but an out-of-scope use of pool infrastructure. The balanced-strategy population demonstrates that intermediate operators *can* compete on margins and pledge simultaneously, but they are rare.

### 7.4 Open questions

1. **Captive delegation volume.** What fraction of delegated ADA in the *hollow-strategy* market is subject to soft captivity (exchange-intermediated delegation to hollow-strategy pools at moderate margins)? This would refine the competition analysis.

2. **Delegator price sensitivity.** Do delegators respond to margin differences? Natural experiments exist in pools that changed their margin: measuring delegation flows before and after would reveal whether the competitive mechanism has empirical traction.

3. **Optimal cost floor.** If $c_{\min}$ were reduced below 340 ADA, at what level does operational sustainability begin to erode? Cross-referencing with actual operator infrastructure costs would establish the economically meaningful floor.

4. **Cross-stage interaction.** The fixed-cost tax interacts with the reward curve's unused pledge budget (documented in the companion [*pools-distribution*](../../pools-distribution/mainnet-analysis/) analysis). Pools that already lose rewards through incomplete pledge activation then lose further rewards through the fixed-cost extraction — a double inefficiency for small pools.

5. **Balanced-strategy persistence.** Why are genuinely committed operators (balanced-strategy entities with 10–95% owner-ratio) so rare? Understanding the barriers to entry for this segment would illuminate whether they represent a viable alternative to the hollow–private dichotomy.

## 8. Reproduction

### 8.1 Full rebuild

```bash
cd spo-incentives/report/sub-flows/operator-delegator-distribution/mainnet-analysis
python3 scripts/build_operator_delegator_profile.py
python3 scripts/build_operator_delegator_visuals.py
```

The profiling script automatically selects the second-to-last epoch in the dataset (guaranteed settled, not pending). Entities are classified as hollow (owner-stake ratio < 10%), balanced (10–95%), or private (≥ 95%). Entity-level grouping uses the MPO entity mapping where available; unmapped pools are each treated as their own entity.

### 8.2 Dependencies

Both scripts read from the `pools-distribution/mainnet-analysis/data/` directory (the sister flow). No additional data fetch is required. The profiling script produces five intermediate artefacts consumed by the visual script:

| Artefact | Description |
| --- | --- |
| `data/reward_split_snapshot.csv` | Per-pool reward decomposition at epoch 614: $\hat{f}$, $c_{\text{eff}}$, $m$, operator take (on-chain), delegator pot, population flag (hollow / balanced / private) |
| `data/reward_split_timeseries.csv` | Epoch-level aggregates (all, hollow, balanced, private): fixed cost, margin, delegator pot, operator-take share (405 epochs) |
| `data/margin_fixed_cost_history.csv` | Epoch-level margin and fixed-cost parameter distributions for hollow-strategy pools (percentiles, adoption rates) |
| `data/entity_fee_policies.csv` | Entity-level fee-policy summary (non-private): 596 entities with stake-weighted margin, pool count, margin values, operator take decomposition |
| `data/reward_split_summary.json` | Headline statistics for all, hollow, balanced, and private segments; entity strategy consistency metrics |
| `data/entity_strategy_summary.csv` | Entity-level strategy assignment: dominant strategy, n_strategies, pool count, stake, operator take per entity |

### 8.3 Figures

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
