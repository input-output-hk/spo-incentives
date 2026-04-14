# The Operator's Cut — A Mainnet Analysis of Intra-Pool Reward Sharing

_Built on 2026/04/14 from mainnet data at epoch `623` plus historical analysis from epoch `211` (413 epochs)._

## Objective

This report analyses the **intra-pool reward split** — the third and final stage of Cardano's reward pipeline — and traces the structural forces that determine how much of each pool's reward reaches delegators versus operators. It extends the empirical baseline established in the [*Analysis of Cardano's Incentive Mechanism*](https://github.com/input-output-hk/spo-incentives/blob/main/report.pdf) (Lopez de Lara, 2025; hereafter the *Incentive Mechanism Analysis*) and operates downstream of the companion reports [*Treasury & Pool Pots Distribution*](../../treasury-and-pool-pots-distribution/mainnet-analysis/) (stage 1) and [*The Pools Pot Distribution Gaps*](../../pools-distribution/mainnet-analysis/) (stage 2).

Every epoch, once the reward curve assigns a total reward $\hat{f}$ to each pool, a second mechanism activates: the **intra-pool split**. The pool operator extracts a fixed cost $c$ and a proportional margin $m$; the remainder is distributed pro-rata among all delegators (including the operator's own stake). At epoch 614, this mechanism processed **6.75M ADA** across 875 rewarded pools — but the headline aggregate (24.3% operator take) conceals three radically different strategies. Adopting the Hollow–Private pledge spectrum from the upstream analysis ([§2.4.2](../../../README.md#242-progression--balanced-as-intended-but-private-by-design)), this report classifies entities by **owner-stake ratio** (owner active stake / pool active stake) across their pool fleets. Three strategies emerge along this spectrum: the **hollow strategy** (owner-stake ratio < 10%, 445 entities, 771 pools, 18.10B ADA, op_take=13.34%) where entities depend entirely on external delegation; the **balanced strategy** (10–95% owner-stake, 46 entities, 60 pools, 0.77B ADA, op_take=10.75%) where entities and delegators share capital with genuine alignment; and the **private strategy** (≥ 95% owner-stake, 11 entities, 44 pools, 2.29B ADA, op_take=99.97%) where entities are operator-funded. Remarkably, 495 of 502 entities (98.6%) apply a single pure strategy across all their pools, demonstrating high strategic consistency. Within hollow-strategy entities, a sub-population of 48 "functionally private" pools (margin ≥ 99.9%, typically exchanges and custodians) extract 100% via margin, leaving 723 genuine hollow pools at 7.7% operator take. The entity-level analysis reveals that margin competition is broadly active in the genuine hollow market (median entity margin 1.0%, stake-weighted 8.9%) but fixed cost, not margin, is the dominant extraction channel. Balanced-strategy entities form the smallest population but analytically most significant: they are where the pledge mechanism produces genuine alignment, with many pools carrying Material or High pledge tags and median owner-ratio 26.4%.

The argument proceeds in four parts:

1. **The formula** (§2). The SL-D1 intra-pool reward-sharing specification — from the original design through a residual-split decomposition to a reader-friendly rewrite and mainnet parameterization. The mechanism is sequential: fixed cost first, margin on the remainder, then pro-rata distribution. A critical protocol detail: when $\hat{f} < c$, the operator takes $\hat{f}$ (not $c$) — the effective fixed cost is $\min(c, \hat{f})$.

2. **Fee parameters** (§3). The fee-parameter landscape — fixed cost adoption and margin categorisation across 875 rewarded pools.

3. **The delegation landscape** (§4). Who are the 1.27M delegators? 80% of delegation relationships land in the hollow × competitive cell. 30% of stake is custodial — 12% custodial by pledge (private-strategy entities self-delegating their own capital) and 18% custodial by delegation (hollow-strategy entities routing client capital through operator-controlled addresses). Together, 35 entities control 6.42B ADA through 1,125 delegation addresses. The remaining 70% is retail, but concentrated: two entities (Everstake, Atomic Wallet) account for a quarter of all delegations through wallet integrations.

4. **The delegator's strategy** (§5). The delegator's action space reduces to a single decision — which pool — governed by two criteria: yield (annualised ROS) and the ethics of pool selection (commitment, independence, transparency). The yield trajectory is declining predictably (halving every ~3 years, R²=0.99 fit to reserve depletion), and Cardano's 2.01% sits below the risk-free rate and most PoS peers. Within the pool landscape, the yield surface is remarkably flat: the 30–77M bucket where 70% of delegation lives shows a middle-half spread of just 0.46pp, and the fixed-cost floor — not margin — is the dominant differentiator. When yield cannot meaningfully distinguish pools, the delegator's choice becomes partly an expression of values.

All counts and amounts use epoch **614** (the latest settled epoch with complete reward data). Source data: `koios_pool_history_mainnet.csv`, `koios_pool_owner_history_mainnet.csv`, `koios_pool_list_mainnet.csv`, `mpo_entity_pool_mapping_mainnet.csv` (Koios + entity attribution from the [*pools-distribution*](../../pools-distribution/mainnet-analysis/) flow).

## Contents

1. [Mainnet Observations](#1-mainnet-observations)
2. [The formula — intra-pool reward sharing](#2-the-formula--intra-pool-reward-sharing)
   - 2.1 [SL-D1 (Original)](#21-sl-d1-original)
   - 2.2 [Residual split decomposition](#22-residual-split-decomposition)
   - 2.3 [Reader-friendly formulation](#23-reader-friendly-formulation)
   - 2.4 [Mainnet parameterization](#24-mainnet-parameterization)
   - 2.5 [Concept glossary](#25-concept-glossary)
3. [The productive and viable populations](#3-the-productive-and-viable-populations)
   - 3.1 [Operators](#31-operators)
      - 3.1.1 [From raw to productive](#311-from-raw-to-productive)
      - 3.1.2 [From productive to viable](#312-from-productive-to-viable)
   - 3.2 [Delegators](#32-delegators)
      - 3.2.1 [From raw to productive](#321-from-raw-to-productive)
      - 3.2.2 [From productive to viable](#322-from-productive-to-viable)
4. [The pricing plan landscape](#4-the-pricing-plan-landscape)
   - 4.1 [The flat fee (fixed cost)](#41-the-flat-fee-fixed-cost)
   - 4.2 [The commission (margin)](#42-the-commission-margin)
   - 4.3 [Custodial versus retail](#43-custodial-versus-retail)
      - 4.3.1 [Clear custodial — by pledge and by extraction](#431-clear-custodial--by-pledge-and-by-extraction)
      - 4.3.2 [Custodial by delegation — the high-concentration signal](#432-custodial-by-delegation--the-high-concentration-signal)
      - 4.3.3 [Summary](#433-summary)
   - 4.4 [Operator profitability versus delegator return](#44-operator-profitability-versus-delegator-return)

## 1. Mainnet Observations

| # | Observation | Summary |
| --- | --- | --- |
| O1 | **The fixed-cost floor exhibits striking inertia** | The protocol floor $c_{\min}$ was reduced from 340 to 170 ADA at epoch 445 (2023/10/27). 169 epochs later, 564 pools (64.5%) still declare 340 ADA — the former floor. Only 217 pools (24.8%) have adopted the current floor. 89.3% of pools sit at one of the two floor values; the remaining 10.7% range from 190 to 999,999 ADA. The inertia is consistent across all three strategy populations: operators overwhelmingly anchor to the floor (or the former floor), and the 564-pool residual has a material yield cost for small pools — a pool at 340 ADA pays double the minimum, eroding delegator yield by an amount that scales inversely with pool size. |
| O2 | **Margin competition is active but masked by a high-margin tail** | Margin is bimodal: 50.7% of pools declare ≤ 2%, while 11.8% declare ≥ 99% (private + functionally private). The median margin has been stable at 2.0% for 405 epochs, but the stake-weighted mean has risen from 4.2% to 18.9% — driven by the growing weight of private and captive pools in the stake distribution, not by fee increases in the competitive market. Any analysis that relies on mean or stake-weighted margin without accounting for this bimodality will overstate the fee burden on the typical delegator. |
| O3 | **Three disjoint strategies coexist on-chain with near-perfect consistency** | 445 entities follow the hollow strategy (771 pools, 18.10B ADA, < 10% owner-stake), 46 follow balanced (60 pools, 0.77B ADA, 10–95%), and 11 follow private (44 pools, 2.29B ADA, ≥ 95%). 98.6% of entities apply a single pure strategy across their entire fleet. 48 functionally private pools (exchanges, custodians at ≥ 99.9% margin) distort the hollow aggregate from 7.7% to 13.34% operator take. |
| O4 | **In the genuine hollow market, fixed cost slightly exceeds margin** | Excluding 48 captive pools, the genuine hollow market (723 pools) operates at 7.7% operator take — fixed cost 4.4%, margin 3.6%. Delegators receive 4.89M ADA (87.3% of hollow rewards) for pro-rata distribution. Entity-level median margin is 1.0%; 56.4% of entities operate below 2%. Margin competition is broadly active. |
| O5 | **The fixed cost is a regressive tax on small-pool delegators** | Effective tax ranges from ~4% (large low-margin pools) to 100% (sub-viable pools where $c \geq \hat{f}$). The fixed-cost share follows a $1/\sigma$ hyperbola. 88.8% of hollow pools declare the minimum cost — the floor is the norm. SPO pools bear a heavier effective tax (13.4% operator take) than MPO pools (12.5%) because scale dilutes the fixed-cost burden. |
| O6 | **Balanced-strategy entities are analytically significant despite small share** | 46 entities (6.9% of pool count, median owner-ratio 26.4%) form the only population where the pledge mechanism produces meaningful alignment. Many carry Material or High pledge tags — genuine skin-in-the-game. Operator take is 12.8%, dominated by fixed cost because pools tend to be small; margins are low. |
| O7 | **The delegator yield is declining on a predictable trajectory** | Stake-weighted hollow-market yield at epoch 614: 2.01% annualised (≈201 ADA/year per 10k ADA). Yield tracks reserve depletion with R²=0.99 and halves roughly every 3 years. Projected threshold crossings: < 2% in ~0.4yr, < 1.5% in ~1.7yr, < 1% in ~3.5yr, < 0.5% in ~6.7yr. The trajectory assumes constant active stake and no governance action. |
| O8 | **Cardano's yield sits below the risk-free rate and most PoS peers** | Among major PoS chains, only the S&P 500 dividend yield sits below Cardano's staking return; Ethereum delivers 1.5–2×, higher-inflation chains 3–10×. Three evaluation frames apply: same-asset (always positive), cross-asset (requires ADA price appreciation to match Treasuries), and DeFi (native staking as the risk-free rate of the ADA economy). What Cardano loses in yield it gains in design: no lockup, no slashing, no minimum, no custodial transfer. |
| O9 | **The yield spread between well-run pools is narrow** | Hollow and balanced yields correlate at 0.97 over 405 epochs — both strategies track reserve depletion in lockstep. The balanced-hollow trailing-year gap has fluctuated between 0.12pp and 0.36pp since epoch 365 — not a reliable premium. In the 30–77M bucket (70% of hollow delegation), the middle-half spread is just 0.46pp; 70.2% of delegated stake sits within ±0.5pp of the median. SPO vs MPO yield difference is negligible (2.05% vs 2.00%). |
| O10 | **Fixed cost, not margin, is the dominant yield differentiator** | The fixed-cost floor acts as a regressive levy: 54.3% effective tax for sub-3M pools, collapsing to 4.7% in the 30–77M band. A counterfactual removing the floor flattens the yield surface entirely — median yield rises +1.0pp for < 3M pools but only +0.05pp for 30–77M pools. The aggregate fixed-cost share has tripled from 1.6% (epoch 250) to 4.9% (epoch 614). Among large pools, moving from 0% to 3% margin costs only 0.07pp; small pools charge *lower* margins than large ones, so margins attenuate the size gradient rather than reinforce it. |
| O11 | **Block luck dominates single-epoch variance; structure emerges only over time** | Block-production luck explains R²=0.41 of single-epoch yield variance among large hollow pools. Over a full year, the structural spread is an order of magnitude smaller than single-epoch noise (hollow SW std dev: 0.10pp across 73 trailing epochs). Epoch-to-epoch movement is noise, not signal. |

**Scope note.** O1–O2 cover fee parameter adoption (§3). O3–O6 are structural to the intra-pool split (§3.2.3–§3.2.4). O7–O11 characterise the delegator's yield landscape (§5).

### The big picture

**What the formula does.** Once the reward curve assigns a total reward $\hat{f}$ to a pool, the intra-pool split extracts operator compensation in two steps: a **fixed cost** $\min(c, \hat{f})$ subtracted first, then a **proportional margin** $m$ applied to the remainder $\max(\hat{f} - c, 0)$. Everything left is distributed pro-rata among all pool members by stake share — including the operator's own stake.

**Three operator strategies.** At epoch 614, 502 entities operate rewarded pools — but they do not follow a single template. Following the Hollow–Private pledge spectrum from the upstream analysis, this report classifies entities by **dominant owner-stake ratio** across their fleet: the axis runs from hollow (external delegation dominates) through balanced (genuine capital-sharing) to private (operator-funded). 445 entities follow the hollow strategy (771 pools, 18.10B ADA), 46 follow the balanced strategy (60 pools, 0.77B ADA), and 11 follow the private strategy (44 pools, 2.29B ADA). Remarkably, 98.6% of entities apply a single pure strategy across their entire fleet. The pool-level heterogeneity is strategic consistency at the entity level.

![Three Strategies — Entity-Level View](figures/three_strategies.png)

**Strategy consistency.** Among 502 entities, 495 (98.6%) operate pools that all fall into the same strategy bin. Only 7 entities are hybrid (spanning multiple bins), and they cluster near threshold boundaries. This extraordinary consistency shows that entities choose a fundamental strategy and apply it coherently across their pool fleet. An entity does not run one hollow pool and one private pool — it commits to a strategy.

**The hollow-strategy market — with a caveat.** Among entities following the hollow strategy, operator take is **13.34%** in aggregate (771 pools). But 48 of these pools are *functionally private* — exchanges and custodians that own almost none of their stake (mean owner-ratio 1.75%) yet set margin ≥ 99.9%, extracting everything. Excluding them, the genuine market (723 pools) operates at **7.7%** operator take — split between fixed cost (4.4%) and margin (3.6%). Fixed cost slightly exceeds margin, reflecting a population where 91.6% declare the minimum 340 ADA cost.

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

The intra-pool split was specified in [*Design Specification for Delegation and Incentives in Cardano*](https://github.com/IntersectMBO/cardano-ledger/releases/latest/download/shelley-delegation.pdf) (Kant, Brünjes & Coutts, IOHK, 2019 — deliverable **SL-D1**, §4.5.4). The mechanism has been operational on mainnet since the Shelley hard fork on 2020/07/29 and its governing parameters have never been modified by governance action.

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
| $c_{\min}$ | Minimum pool cost | Protocol-enforced floor on $c$ (currently 170 ADA; formerly 340 ADA) |
| Operator take | $c_{\text{eff}} + m(\hat{f} - c_{\text{eff}})$ | Total declared-fee extraction (= on-chain `pool_fees`) |
| Delegator pot | $(1-m)(\hat{f} - c_{\text{eff}})$ | Amount entering pro-rata distribution |
| Effective tax | Operator take / $\hat{f}$ | Fraction of pool reward extracted before pro-rata |

## 3. The productive and viable populations

All analysis from §4 onwards operates on the **productive population** at epoch **623** — the subset of pools, operators, and delegations that clear the production threshold and generate meaningful rewards. Two thresholds filter the raw population. The **production threshold** (~1M ADA) is the minimum stake a pool needs to expect at least one block per epoch. The **viable threshold** (~3M ADA) separates pools that produce blocks but cannot absorb the flat fee from those where the fee structure produces meaningful delegator returns. This section establishes both populations for the two sides of the market.

### 3.1 Operators

#### 3.1.1 From raw to productive

| Segment | Entities | Pools | Stake | Share |
|---|---:|---:|---:|---:|
| **Raw total (`epoch_stake`)** | **2,302** | **2,877** | **21.75B** | **100%** |
| Below production threshold (noise) | 1,742 | 1,925 | 0.19B | 0.9% |
| **Productive total** | **582** | **952** | **21.57B** | **99.1%** |
| *of which:* | | | | |
|   Identified entities | 83 | 453 | 15.73B | 72.3% |
|     — multiple productive pools | 73 | 443 | 15.27B | 70.2% |
|     — single productive pool | 10 | 10 | 0.46B | 2.1% |
|   Independent single-pool operators | 499 | 499 | 5.83B | 26.8% |

Entity attribution is a lower bound — operators using entirely separate infrastructure and branding for each pool remain invisible.

#### 3.1.2 From productive to viable

| Segment | Entities | Pools | Stake | Share |
|---|---:|---:|---:|---:|
| **Productive total** | **582** | **952** | **21.57B** | **100%** |
| Sub-viable (1M–3M ADA) | 213 | 219 | 0.39B | 1.8% |
| **Viable total (≥3M ADA)** | **383** | **733** | **21.18B** | **98.2%** |
| *of which:* | | | | |
|   Identified entities | 83 | 433 | 15.70B | 72.8% |
|     — multiple viable pools | 71 | 421 | 15.20B | 70.5% |
|     — single viable pool | 12 | 12 | 0.50B | 2.3% |
|   Independent single-pool operators | 300 | 300 | 5.48B | 25.4% |

The 219 sub-viable pools are productive but economically marginal: 91% are independent single-pool operators, 117 still declare 340 ₳ flat fee, and 9 reach 100% effective price — the flat fee alone consumes the entire pool reward. The 733 viable pools carry 98.2% of productive stake.

### 3.2 Delegators

The delegation pipeline starts from 1.85M raw delegation certificates and removes two layers of noise: zero-balance certificates (27% of raw — delegation records with no ADA behind them) and delegations to non-productive pools.

#### 3.2.1 From raw to productive

| Segment | Delegations | Stake | Share | Pools |
|---|---:|---:|---:|---:|
| **Raw (delegation certificates)** | **1,847,713** | **—** | **—** | **3,190** |
| Zero-balance certificates (noise) | 492,678 | 0 | — | 313 |
| **`epoch_stake` total** | **1,355,035** | **21.75B** | **100%** | **2,877** |
| Non-productive pool delegations (noise) | 59,937 | 0.19B | 0.9% | 1,925 |
| **Productive pool delegations** | **1,295,098** | **21.57B** | **99.1%** | **952** |
| *of which:* | | | | |
|   Identified entity pools | 910,509 | 15.73B | 72.3% | 453 |
|   Independent single-pool operators | 384,589 | 5.83B | 26.8% | 499 |

#### 3.2.2 From productive to viable

| Segment | Delegations | Stake | Share | Pools |
|---|---:|---:|---:|---:|
| **Productive pool delegations** | **1,295,098** | **21.57B** | **100%** | **952** |
| Sub-viable pool delegations (1M–3M) | 67,817 | 0.39B | 1.8% | 219 |
| **Viable pool delegations (≥3M)** | **1,227,281** | **21.18B** | **98.2%** | **733** |
| *of which:* | | | | |
|   Identified entity pools | 904,850 | 15.70B | 72.8% | 433 |
|   Independent single-pool operators | 322,431 | 5.48B | 25.4% | 300 |

67,817 delegations (5.2% of productive) sit in sub-viable pools where the flat fee's regressive geometry erodes most or all delegator returns — 92% of those land in independent single-pool operators. The **1,227,281 delegations** in viable pools are where the pricing plan produces meaningful outcomes. The downstream analysis (§5) decomposes the productive population into operator self-stake, custodial, and retail segments.

The companion [*Staking Census*](../../census/mainnet-analysis/) documents the full cleaning pipeline. All counts and amounts reference epoch **623** unless otherwise noted.

## 4. The pricing plan landscape

The formula gives operators two extraction channels: a fixed cost $c$ (on-chain parameter `minPoolCost`) and a proportional margin $m$ (on-chain parameter `margin`). In pricing terms, the fixed cost functions as a **flat fee** — a fixed ADA amount per epoch, independent of pool size — and the margin functions as a **commission** — a proportional share of the reward after the flat fee is deducted. Together they compose the operator's pricing plan; their sum, the **operator take**, is the effective price the delegator faces. This section categorises the pool population along each pricing channel before §5 classifies the delegation side and the downstream analysis crosses both.

### 4.1 The flat fee (fixed cost)

The flat fee is the ADA amount deducted from every pool's reward before commission and pro-rata distribution (on-chain: `minPoolCost` / declared fixed cost $c$). It is constrained by the protocol floor $c_{\min}$, currently 170 ₳ (reduced from 340 ₳ at epoch 445, on 2023/10/27). No other major PoS protocol uses a flat fee — Cosmos, Solana, Polkadot, Ethereum, and Tezos all use either a single proportional commission or no protocol-level fee at all. The flat fee is unique to Cardano and its economic weight follows a $1/\sigma$ hyperbola: confiscatory for small pools, invisible for large ones.

At epoch 623, 89.5% of the 952 productive pools declare one of the two floor values — 170 ₳ or 340 ₳. The remaining 10.5% (100 pools) declare other values. Decomposing this population reveals that the "custom" label conceals three structurally distinct behaviours: near-floor inertia (Binance at 345 ₳, Everstake at 400 ₳, OCEAN at 500 ₳), extraction (11 pools with FC > 500 ₳ and commission ≥ 99%), and a handful of independent operators at intermediate values.

| Flat-fee strategy | Definition | Pools | Share | Entities | Stake (B) | Stake share | Delegators | Del. share |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Adopted** | $c = 170$ ₳ (current floor) | 244 | 25.6% | 186 | 5.13 | 23.8% | 223,419 | 17.2% |
| **Legacy** | $c = 340$ ₳ (former floor) | 608 | 63.9% | 350 | 14.38 | 66.7% | 679,158 | 52.4% |
| **Near-floor** | $171 < c \leq 500$, $c \neq 170, 340$ | 84 | 8.8% | 48 | 1.82 | 8.4% | 381,652 | 29.5% |
| **Extraction** | $c > 500$ | 16 | 1.7% | 14 | 0.24 | 1.1% | 10,869 | 0.8% |

The inertia is structural: 70% of floor-declaring stake remains at 340 ₳, 178 epochs after the reduction, driven by the largest entities (Coinbase, Kiln, Upbit, eToro, Wave) which have not updated. Among the 219 sub-viable pools (1M–3M ADA), the distribution mirrors the productive population (84 adopted, 117 legacy) — but the economic meaning is different. At this tier, a 170 ₳ flat fee absorbs ~27% of pool reward and a 340 ₳ fee absorbs ~54%. The adopted/legacy distinction, which is a governance-responsiveness signal for viable pools, becomes a confiscation-severity signal for sub-viable ones.

### 4.2 The commission (margin)

The commission is the operator's proportional share of the reward after the flat fee is deducted (on-chain: `margin` $m \in [0, 1]$). Unlike the flat fee, which clusters at two protocol-floor values, the commission is continuously variable and has no enforced floor or ceiling. It is the only fully unconstrained parameter in the intra-pool split, and the one that most directly expresses the operator's pricing intent.

The commission distribution is bimodal: the median is 2.0% and has been stable for over 400 epochs. The distribution clusters at round values — 1%, 2%, 3%, 5%, 10% account for the bulk of the competitive band.

| Band | Range | Pools | Share | Stake (B) | Stake share | Delegators | Del. share | Economic logic |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **No-commission** | $m = 0\%$ | 170 | 17.9% | 2.70 | 12.5% | 146,931 | 11.3% | Flat-fee-only pricing — the operator earns through the flat fee and pro-rata owner share only |
| **Competitive** | $0 < m \leq 10\%$ | 658 | 69.1% | 15.23 | 70.6% | 1,125,795 | 86.9% | The market norm — operators blend flat fee and commission. The upper end (6–10%) includes institutional operators: Binance, Figment, Blockdaemon, Kiln |
| **No man's land** | $10\% < m < 99\%$ | 12 | 1.3% | 0.09 | 0.4% | 331 | <0.1% | Structurally empty — 12 isolated pools scattered across an 89pp range |
| **Privatisation** | $m \geq 99\%$ | 112 | 11.8% | 3.55 | 16.5% | 22,041 | 1.7% | Total extraction — de facto private operation. Top entities: CHUCK BUX, Upbit, eToro |

87% of pools price at or below 10%; density drops to near zero above 10% and resurfaces only at 99–100%. No man's land makes the bimodality explicit: the 89pp gap between competitive pricing and privatisation is a desert — an operator pricing above 10% is either extracting (and would go to 99%+) or running a niche service (and would not need more than 10%).

**Commission bands × owner-stake strategy.** The bands cross-cut the three owner-stake strategies. The hollow segment fills all four bands. Balanced pools concentrate in no-commission and competitive with marginal presence in privatisation. Private pools occupy only competitive (3 pools — Wave and one anonymous) and privatisation — private × no-commission is empty because an operator who funds the pool has no reason to set commission to zero.


### 4.3 Custodial versus retail

Not all staked ADA is delegated by independent participants choosing a pool on the open market. A significant share is **custodial** — controlled by operators rather than by the on-chain delegators themselves. Identifying these pools is necessary before the profitability analysis (§4.4) can isolate the genuine pricing market.

#### 4.3.1 Clear custodial — by pledge and by extraction

Two mechanisms produce unambiguous custodial outcomes, detectable from a single on-chain observable.

**Custodial by pledge** — private-strategy entities (owner-stake ≥ 95%) that fund their pools with their own capital. The operator *is* the delegator. The commission (typically 100%) is self-directed — it never leaves the operator's control.

**Custodial by extraction** — non-private pools that declare a privatisation commission (≥ 99%). The operator does not fund the pool but captures virtually all rewards through the commission. Delegators earn near-zero yield; whether they remain through inertia, ignorance, or institutional constraint, their delegation is not a meaningful market signal.

#### 4.3.2 Custodial by delegation — the high-concentration signal

The third mechanism is more subtle. Some pools appear hollow to the protocol (low owner-stake, competitive commission) but their delegation is concentrated in few, large addresses — the hallmark of operator-routed capital. The signal is the **ADA per delegation** (APD): when the average delegation in a pool exceeds 100K ADA, the capital is unlikely to be retail. A typical retail wallet holds well under 100K ADA; an APD above this threshold indicates exchange routing, institutional validators, or whale self-delegation.

At epoch 623, 227 pools (across 106 entities) exceed 100K ADA per delegation. They split at the 1M ₳/delegation mark into two sub-populations:

| Sub-type | Entities | Pools | Stake (B) | Delegators | Profile |
|---|---:|---:|---:|---:|---|
| **APD ≥ 1M ₳/d** | 26 | 105 | 4.77 | 1,087 | Exchanges and institutional validators routing client capital through few, large addresses. Top entities: Coinbase (41p, 5.8M/d), Blockdaemon (12p, 2.3M/d), Binance (17p, 744K/d), Kiln (7p, 1.4M/d), Figment (16p, 2.7M/d), NuFi (3p, 1.5M/d). Also includes whale SPOs with 2–16 delegators |
| **APD 100K–1M ₳/d** | 88 | 122 | 2.37 | 10,389 | The concentration grey zone — pools where the average delegation exceeds what a typical retail wallet holds. Includes YUTA (18p, 173K/d), Wave (6p, 551K/d), and 74 single-pool operators with elevated APD from a mix of large delegators and partial self-delegation |

The ≥1M sub-population is unambiguously custodial: 1,087 delegators for 4.77B ADA — an average of 4.4M per delegation address. The 100K–1M sub-population is the boundary layer between institutional routing and concentrated retail. Its inclusion in the custodial classification is conservative — some of these pools may serve a small number of genuine high-net-worth delegators — but the APD signal is strong enough to separate them from the retail market where delegation reflects independent choice.

#### 4.3.3 Summary

The table below continues the population decomposition from §3:

| Segment | Entities | Pools | Share | Stake (B) | Stake share | Delegations | Del. share |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Productive total** | **582** | **952** | **100%** | **21.57** | **100%** | **1,295,098** | **100%** |
| Custodial by pledge | 10 | 36 | 3.8% | 1.59 | 7.4% | 122 | <0.1% |
| Custodial by extraction | 57 | 79 | 8.3% | 2.04 | 9.5% | 21,982 | 1.7% |
| Custodial by delegation (APD ≥ 100K) | 106 | 227 | 23.8% | 7.14 | 33.1% | 11,476 | 0.9% |
|   ↳ APD ≥ 1M ₳/d | 26 | 105 | 11.0% | 4.77 | 22.1% | 1,087 | 0.1% |
|   ↳ APD 100K–1M ₳/d | 88 | 122 | 12.8% | 2.37 | 11.0% | 10,389 | 0.8% |
| **Total custodial** | **165** | **342** | **35.9%** | **10.77** | **49.9%** | **33,580** | **2.6%** |
| **Retail market** | **435** | **610** | **64.1%** | **10.80** | **50.1%** | **1,261,518** | **97.4%** |

Half the productive stake is custodial. But the asymmetry is extreme: custodial pools hold 49.9% of stake through 2.6% of delegation relationships, while the retail market holds 50.1% of stake through 97.4% of delegations. The retail market — 610 pools, 435 entities, 10.80B ADA, 1,261,518 delegators — is the population where the pricing plan produces a genuine market outcome.

### 4.4 Operator profitability versus delegator return

The effective price is only meaningful in the retail market — where the operator does not control the delegator addresses. In custodial pools, the "price" is an internal transfer; it carries no information about market competition. This section analyses the **610 retail pools** (435 entities, 10.80B ADA, 1,261,518 delegators) identified in §4.3.

The central question is what the pricing plan produces for each side of the market. The operator earns a revenue (the operator take, annualised in ₳/year); the delegator receives a return (the net ROS, after fees). If the mechanism worked as intended, these two quantities would be linked: operators who charge more would earn more, and delegators would see a meaningful ROS difference that informs their delegation choice. The table below tests this assumption.

| Operator type | Entities | Pools | Delegators | Del. share | Stake (B) | Flat fee | Commission | Gross ROS | Net ROS | Med. entity revenue (₳/yr) | ROS drag | Reward share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Hollow SPO** | **343** | **343** | **398,983** | **31.6%** | **4.34** | **7.0%** | **1.2%** | **2.51%** | **2.11%** | **24,884** | **48 bps** | **40.2%** |
|   ↳ Sub-viable (<3M) | 143 | 143 | 52,452 | 4.2% | 0.25 | 47.8% | 0.7% | 3.96% | 2.04% | 24,820 | 167 bps | 2.3% |
|   ↳ Healthy (3–38.5M) | 161 | 161 | 220,072 | 17.4% | 1.82 | 8.2% | 1.6% | 2.35% | 2.07% | 26,235 | 32 bps | 16.9% |
|   ↳ Large healthy (38.5–62M) | 25 | 25 | 90,458 | 7.2% | 1.30 | 1.6% | 1.2% | 2.38% | 2.32% | 31,757 | 6 bps | 12.0% |
|   ↳ Near-saturation (62–77M) | 14 | 14 | 36,001 | 2.9% | 0.96 | 1.3% | 0.3% | 2.33% | 2.29% | 27,244 | 4 bps | 8.9% |
| **Hollow MPO** | **50** | **215** | **836,857** | **66.3%** | **6.17** | **3.4%** | **2.2%** | **2.33%** | **2.19%** | **112,980** | **14 bps** | **57.1%** |
|   ↳ 2-pool | 15 | 30 | 101,533 | 8.0% | 1.09 | 2.5% | 1.2% | 2.27% | 2.20% | 66,836 | 10 bps | 10.1% |
|   ↳ 3–5 pool | 26 | 102 | 345,579 | 27.4% | 2.98 | 3.4% | 2.4% | 2.33% | 2.18% | 132,851 | 15 bps | 27.6% |
|   ↳ 6–10 pool | 6 | 39 | 73,866 | 5.9% | 1.04 | 3.5% | 2.4% | 2.40% | 2.26% | 227,186 | 16 bps | 9.6% |
|   ↳ 11+ pool | 3 | 44 | 315,879 | 25.0% | 1.07 | 4.5% | 2.5% | 2.31% | 2.17% | 505,478 | 20 bps | 9.9% |
| **Balanced** | **42** | **44** | **18,094** | **1.4%** | **0.20** | **19.1%** | **1.5%** | **3.08%** | **2.03%** | **24,820** | **107 bps** | **1.8%** |
|   ↳ SPO sub-viable (<3M) | 27 | 27 | 5,041 | 0.4% | 0.04 | 49.4% | 1.0% | 3.70% | 1.95% | 23,513 | 219 bps | 0.4% |
|   ↳ SPO healthy (≥3M) | 11 | 11 | 3,896 | 0.3% | 0.08 | 11.2% | 0.8% | 2.43% | 2.27% | 15,825 | 43 bps | 0.7% |
|   ↳ MPO | 4 | 6 | 9,157 | 0.7% | 0.08 | 9.7% | 2.5% | 2.95% | 2.22% | 61,427 | 106 bps | 0.7% |
| **Retail total** | **435** | **610** | **1,261,518** | **100%** | **10.80** | **5.2%** | **1.8%** | **2.47%** | **2.13%** | **25,006** | **43 bps** | **100%** |

The table reads left to right: operator type → population → pricing channels (flat fee + commission as % of pool reward) → what the pool produces (gross ROS) → what the delegator receives (net ROS) → what the operator earns (median entity revenue annualised) → the cost to the delegator (ROS drag) → share of total retail pool rewards.

Three observations emerge from this decomposition.

**Operator revenue does not track the effective price.** Hollow SPOs charge between 1.3% and 47.8% effective price across tiers — a 37× spread — yet median revenue is flat at 24,820–31,757 ₳/yr. The flat fee inflates the effective price for sub-viable pools without generating proportionally more revenue: 143 sub-viable SPOs absorb 47.8% of their pools' output as fees but operate on just 2.3% of total retail rewards. Meanwhile, hollow MPOs earn 5–20× more (67k–505k ₳/yr) at a lower effective price (2.5–4.5%) — the scaling is horizontal (more pools) rather than vertical (higher extraction). The reward share column makes the structural imbalance explicit: 50 hollow MPOs operate on 57.1% of the retail economy; 343 hollow SPOs share 40.2%; 42 balanced operators share 1.8%.

**Delegator returns are near-identical regardless of operator type.** Net ROS ranges from 1.95% (balanced SPO sub-viable) to 2.32% (hollow SPO large healthy) — a 37 bps spread across the entire retail market. The flat fee creates large differences in effective price without producing corresponding differences in delegator return. Sub-viable pools generate the highest gross ROS (3.70–3.96% — the reward curve is generous per ADA at small pool sizes) but the flat fee erases the surplus: 167–219 bps of drag. Above the viable threshold, drag collapses to 4–43 bps. For MPOs, drag rises gently with fleet size (10–20 bps) as the commission channel takes over from the flat fee. The delegator cannot meaningfully distinguish operators by return.

**Delegation concentration does not follow return.** 66.3% of retail delegators sit in hollow MPO pools at 2.19% net ROS, while hollow SPO near-saturation pools offer 2.29% — 10 bps more — and hold only 2.9% of delegators. The 3–5 pool MPOs alone concentrate 27.4% of all retail delegators (345,579) on 27.6% of rewards. This concentration reflects visibility and wallet-integration defaults, not yield optimisation.

| Entity | Type | Pools | Delegators | Stake (M) | Effective price | Net ROS | ROS drag | Revenue (₳/yr) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Everstake | 11p-MPO | 11 | 264,997 | 566.6 | 5.4% | 2.17% | 13 bps | 717,323 |
| AWP / Atomic Wallet | 3p-MPO | 3 | 83,802 | 47.5 | 11.5% | 2.06% | 27 bps | 127,112 |
| BERRY | SPO | 1 | 22,053 | 32.9 | 4.7% | 2.48% | 12 bps | 35,941 |
| Emurgo | 8p-MPO | 8 | 15,334 | 269.4 | 3.3% | 2.31% | 8 bps | 210,097 |

Everstake dominates the retail market: 264,997 delegators (21% of retail) across 11 pools at 5.4% effective price — a competitive deal. AWP / Atomic Wallet shows the wallet-integration effect: 83,802 delegators routed by the app into 3 pools at 11.5% effective price and the lowest net ROS among top entities (2.06%). BERRY is the counter-example — a single-pool operator that attracts 22,053 delegators at the highest net ROS in the table (2.48%) through community visibility rather than platform integration. The three entities illustrate three delegation mechanisms: institutional routing (Everstake), app defaults (AWP), and community reputation (BERRY).


