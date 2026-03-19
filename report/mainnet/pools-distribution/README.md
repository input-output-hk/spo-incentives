# Pools Distribution — Mainnet Analysis

_Built on 2026/03/18 from mainnet data at epoch `618` plus historical analysis from epoch `208` (Shelley inception)._

## Objective

This report analyses the **pool-level reward distribution** — the second stage of Cardano's reward pipeline.

Every epoch, the pools pot (~15.5M ADA at epoch 616) enters this stage. The reward curve allocates it across pools based on their stake, pledge, and block performance. What is not distributed **returns to the reserve**.

At epoch 616, only **43.7%** of the pools pot reached operators and delegators. This report decomposes that inefficiency, identifies the structural thresholds that shape the pool landscape, and documents the mainnet observations that motivate the CIP proposals under evaluation.

All counts and amounts use the latest available pool snapshot (**epoch 618**) and the latest complete epoch with reward data (**epoch 616**) unless stated otherwise.

## Contents

1. [Mainnet Observations](#1-mainnet-observations)
2. [Distribution efficiency](#2-distribution-efficiency)
   - 2.1 [Waste decomposition](#21-waste-decomposition)
   - 2.2 [Within-staked inefficiency](#22-within-staked-inefficiency)
3. [Pool taxonomy](#3-pool-taxonomy)
   - 3.1 [The case for pool categorization](#31-the-case-for-pool-categorization)
   - 3.2 [Structural thresholds](#32-structural-thresholds)
      - 3.2.1 [Production threshold](#321-production-threshold)
      - 3.2.2 [Viability threshold](#322-viability-threshold)
      - 3.2.3 [Saturation threshold](#323-saturation-threshold)
   - 3.3 [Tier definitions](#33-tier-definitions)
   - 3.4 [Pool distribution by tier](#34-pool-distribution-by-tier)
4. [Entity and MPO concentration](#4-entity-and-mpo-concentration)
   - 4.1 [Archetypes](#41-archetypes)
      - 4.1.1 [Classification](#411-classification)
      - 4.1.2 [Current distribution](#412-current-distribution)
      - 4.1.3 [Historical evolution](#413-historical-evolution)
   - 4.2 [From archetype to incentive stance](#42-from-archetype-to-incentive-stance)
      - 4.2.1 [Exchange Custody (CEX)](#421-exchange-custody-cex)
      - 4.2.2 [Institutional Validator (IVaaS)](#422-institutional-validator-ivaas)
      - 4.2.3 [Incentive stance: reclassifying by pledge-bonus capture](#423-incentive-stance-reclassifying-by-pledge-bonus-capture)
   - 4.3 [Within-staked inefficiency: the cost of non-compliance](#43-within-staked-inefficiency-the-cost-of-non-compliance)
   - 4.4 [MPO pool taxonomy by incentive stance](#44-mpo-pool-taxonomy-by-incentive-stance)
   - 4.5 [Conclusion](#45-conclusion)
5. [Pool taxonomy by incentive stance](#5-pool-taxonomy-by-incentive-stance)
   - 5.1 [Stance recap](#51-stance-recap)
   - 5.2 [The full landscape](#52-the-full-landscape)
   - 5.3 [Distribution by stance (all pools)](#53-distribution-by-stance-all-pools)
6. [Reward formula anatomy](#6-reward-formula-anatomy)
   - 6.1 [The full formula](#61-the-full-formula)
   - 6.2 [Factor 1 — Performance ($\bar{p}$)](#62-factor-1--performance-barp)
   - 6.3 [Factor 2 — The ceiling ($P_{\max}$)](#63-factor-2--the-ceiling-p_max)
   - 6.4 [The playing field](#64-the-playing-field)
      - [Three reward tiers](#three-reward-tiers)
      - [The bonus at every scale](#the-bonus-at-every-scale)
      - [What this means](#what-this-means)
   - 6.5 [Factor 3 — The proportioning envelope ($E$)](#65-factor-3--the-proportioning-envelope-e)
      - 6.5.1 [The base: what size alone buys](#651-the-base-what-size-alone-buys)
      - 6.5.2 [The pledge bonus: what commitment adds](#652-the-pledge-bonus-what-commitment-adds)
      - 6.5.3 [Envelope on mainnet](#653-envelope-on-mainnet)
   - 6.6 [Reward efficiency decomposition](#66-reward-efficiency-decomposition)
      - [The base is distribution-neutral](#the-base-is-distribution-neutral)
      - [The bonus is distribution-sensitive](#the-bonus-is-distribution-sensitive)
      - [Decomposition by formula factor](#decomposition-by-formula-factor)
      - [Where the waste lives](#where-the-waste-lives)
      - [Relationship to §2 waste decomposition](#relationship-to-2-waste-decomposition)
7. [Pool landscape](#7-pool-landscape)
   - 7.1 [Current snapshot](#71-current-snapshot)
   - 7.2 [Reward concentration](#72-reward-concentration)
   - 7.3 [Entity and MPO concentration](#73-entity-and-mpo-concentration)
8. [Protocol parameters](#8-protocol-parameters)
9. [Forward-looking](#9-forward-looking)
10. [Reproduction](#10-reproduction)
   - 10.1 [Full rebuild](#101-full-rebuild)
   - 10.2 [Refreshing MPO data](#102-refreshing-mpo-data)
   - 9.1 [Full rebuild](#91-full-rebuild)
   - 9.2 [Refreshing MPO data](#92-refreshing-mpo-data)

---

## 1. Mainnet Observations

| # | Observation | Section | Status |
| --- | --- | --- | --- |
| | **O1 — The pools pot is distributed at 44% efficiency** | | |
| F1.1 | 8.75M ADA/epoch returns to the reserve undistributed — 56% of the pools pot | §2.1 | Epoch 616 |
| F1.2 | 78% of the waste is caused by inactive stake (upstream) — 16.75B ADA not delegated | §2.1 | Capital constraint |
| F1.3 | The remaining 22% (~1.9M ADA/epoch) is distribution inefficiency within staked ADA | §2.2 | Structural — pool landscape |
| | **O2 — Three structural thresholds stratify the pool landscape** | | |
| F2.1 | Regular block production requires ~3M ADA stake (~3 blocks/epoch) — this is the emergent viability boundary | §3.1 | Structural — not a protocol parameter |
| F2.2 | Below 1.1M ADA, the 340 ADA fixed cost exceeds pool reward — operators are in economic loss | §3.2 | 1,987 below-viability pools affected |
| F2.3 | Below-viability pools collectively owe 647K ADA/epoch in fixed costs but earn only 182K ADA — a 358% overdraw | §3.2 | Fixed cost creates a value-destructive layer |
| F2.4 | Only 8 pools reach the saturation threshold (z₀ = 76.99M ADA) — the cap designed for 500 pools is nearly inactive | §3.3 | 1.6% of design target |
| | **O3 — The pledge bonus is functionally irrelevant** | | |
| F3.1 | At median pledge, the bonus adds ~0.006% to pool rewards — undetectable by delegators | §5.5.3 | Structural — a0 curve too flat |
| F3.2 | Only 37 out of 731 healthy pools (5%) receive a pledge bonus above 1% | §5.5.3 | Dominated by high-pledge institutional pools |
| F3.3 | 83% of pools with stake pledge below 100K ADA — well within the flat zone of the a0 curve | §5.5.3 | Pledge has no meaningful effect below ~1M ADA |
| F3.4 | Yield on pledge capital is 0.68%/yr at best (full saturation) — below passive delegation yield of 2.3%/yr | §5.4 | Economically irrational to pledge |
| F3.5 | 3.4M ADA/epoch (22% of pot) is reserved for pledge bonus but returns to reserve unused | §5.6 | Structural cost of maintaining a0 = 0.3 |
| | **O4 — Saturation is structurally unreachable at current participation** | | |
| F4.1 | Active stake fills only 56.5% of theoretical capacity (k × z₀) — at most 282 pools could saturate | §3.3 | Capital constraint |
| F4.2 | 104 pools sit in the near-saturation zone (≥80% z₀) — a thin cluster, not a broad plateau | §3.3 | Far from the k = 500 design |
| F4.3 | k = 500 is feasible only at near-complete participation (~100% of supply staked) | §3.3 | Design assumption unmet |

### The big picture

The pools pot enters this stage as a budget of ~15.5M ADA. Only **6.8M** reaches operators and delegators. The rest returns to the reserve — not because the mechanism is broken, but because **the pool landscape it was designed for does not exist**.

The design assumed 500 well-funded, pledge-committed pools operating near saturation with near-complete staking participation. Mainnet reality is a stratified market where three structural thresholds create distinct tiers: a **production threshold** (~1M ADA) below which pools barely produce blocks, a **viability threshold** (~3M ADA) below which pools produce blocks regularly but cannot cover their fixed costs, and a **saturation threshold** (77M ADA) that almost nothing reaches. Between viability and saturation sits the actual delegation market — 731 pools carrying 97% of stake.

The pledge bonus, designed to differentiate pools by operator commitment, is irrelevant for 95% of the landscape. The saturation cap, designed to prevent concentration, binds for 8 pools. The distribution inefficiency is real but modest (22% of waste) — the dominant loss is upstream: 43.5% of ADA does not participate.

---

## 2. Distribution efficiency

> **56.3% of the pools pot never reaches operators or delegators.** Of the 15.53M ADA entering this stage at epoch 616, only 6.79M ADA was distributed. The rest returned to the reserve.

### 2.1 Waste decomposition

```mermaid
flowchart TD
    A["🏦 **Pools Pot**\n15.53M ADA"] --> B["✅ **Distributed**\n6.79M ADA — 43.7%"]
    A --> C["↩️ **Return to Reserve**\n8.75M ADA — 56.3%"]
    C --> D["💤 **Participation waste**\n6.82M ADA — 78% of waste\n43.5% of ADA never delegated"]
    C --> E["⚙️ **Within-staked inefficiency**\n1.92M ADA — 22% of waste\nPool structure & performance losses"]
```

| Component | ADA/epoch | Share |
| --- | ---: | ---: |
| Pools pot (epoch 616) | 15.53M | — |
| ✅ Distributed to operators & delegators | 6.79M | 43.7% |
| ↩️ **Return to reserve** | **8.75M** | **56.3%** |
| &nbsp;&nbsp;└ Participation waste | 6.82M | 78% of waste |
| &nbsp;&nbsp;└ Within-staked inefficiency | 1.92M | 22% of waste |

**Participation waste** is mechanical and upstream: 43.5% of circulating supply does not delegate, so the reward curve — which is sized for the full supply — distributes proportionally less. This waste passes through this stage transparently and is the same return-to-reserve documented at §1.1 O3.

**Within-staked inefficiency** is the analytically interesting component — the 1.92M ADA lost even among the 21.75B ADA that *does* participate.

### 2.2 Within-staked inefficiency

The **~1.98M ADA/epoch** of within-staked waste has four orthogonal causes, derived from the reward formula $E(\pi, \nu) = \lambda_{\min}\nu + \lambda_{\max}A(\pi, \nu)$.

For each pool, the maximum achievable reward (at full self-pledge $\pi = \nu$, perfect performance, no oversaturation) is $\nu \cdot P_{\max}$. The gap between this maximum and what pools actually earn decomposes as follows.

| Source | Mechanism | ₳/epoch | ₳/year | Share |
| --- | --- | ---: | ---: | ---: |
| 📉 Sub-saturation structural loss | $\lambda_{\max} \sum_i \nu_i(1-\nu_i^2) \cdot P_{\max}$ — the pledge multiplier is structurally suppressed at low $\nu$: even a fully self-pledged pool at 10% saturation captures only 1% of the bonus headroom | **1.09M** | **~79.6M** | **~55%** |
| 🪙 Pledge bonus uncaptured | $\lambda_{\max} \sum_i (\nu_i^3 - A_i) \cdot P_{\max}$ — at each pool's stake level, additional pledge would increase $A(\pi,\nu)$ toward $\nu^3$, but actual mainnet pledge is far below stake | **0.77M** | **~56.2M** | **~39%** |
| 🎯 Performance losses | $\sum_i E_i \cdot (1 - \hat{\eta}_i) \cdot P_{\max}$ — missed blocks reduce reward proportionally. Network-wide $\hat{\eta} = 0.990$ | **78K** | **~5.7M** | **~4%** |
| ✂️ Saturation cap clipping | 7 oversaturated pools have stake above $z_0$; the capped portion earns nothing | **42K** | **~3.1M** | **~2%** |

The sub-saturation and pledge terms are **orthogonal**: they sum exactly to the total E-gap ($\lambda_{\max} \sum_i(\nu_i - A_i) \cdot P_{\max} = 1.86\text{M}$ ADA), with no double-counting.

> [!NOTE]
> **Performance is a minor driver.** With $\hat{\eta} = 0.990$, performance accounts for only ~4% of within-staked waste. The dominant losses are structural — baked into the formula's behaviour at low stake levels — and cannot be resolved by pool operator improvements alone.

> [!NOTE]
> **The dominant loss remains upstream.** Participation waste (~6.8M ADA) dwarfs within-staked inefficiency (~2.0M ADA) by 3.4×. CIPs targeting pool fee structure or reward formula shape address only the ~23% — the ~77% requires increasing staking participation.

> [!WARNING]
> **94% of within-staked inefficiency is structural, not operational.** Sub-saturation loss and uncaptured pledge bonus together account for ~94% of the 1.98M ADA/epoch lost within the staked pool. This is the budget that well-designed incentive reforms can target — and it is the motivation for the scenario evaluations in §6.

---

## 3. Pool taxonomy

### 3.1 The case for pool categorization

The reward curve is continuous — it maps stake to reward without discrete jumps. Yet the pool landscape is not continuous: pools cluster into groups with qualitatively different economic realities, separated by thresholds that emerge from the protocol's own mechanics.

Treating all pools as points on a single spectrum obscures these structural differences. A pool with 50K ADA and one with 50M ADA both participate in the same reward formula, but they inhabit entirely different worlds: one barely produces blocks, the other anchors the delegation market. Applying the same analysis or the same CIP evaluation to both without distinguishing them leads to conclusions that are technically correct and analytically useless.

The taxonomy defined here uses three thresholds derived from protocol parameters and economic constraints — not arbitrary ADA amounts — to partition the pool space into tiers with distinct identities. Each tier has a characteristic behaviour, a characteristic problem (or none), and a characteristic response to parameter changes.

Crucially, these thresholds are **dynamic**. They are functions of active stake, fixed costs, reward rates, and protocol parameters like $k$. When a CIP proposes to change $k$ from 500 to 1000, or when active stake grows from 21B to 35B ADA, the threshold values shift — and so do the tier boundaries. The taxonomy is a framework for reasoning across scenarios, not a snapshot of today's values.

### 3.2 Structural thresholds

Three thresholds emerge from the protocol's mechanics that create qualitatively distinct tiers in the pool landscape.

#### 3.2.1 Production threshold

#### The slot leadership formula

Cardano's Ouroboros Praos assigns block production rights slot by slot. For each of the $L$ slots in an epoch, a pool with relative active stake $\sigma_i$ is elected slot leader with probability:

$$\phi(f, \sigma_i) = 1 - (1-f)^{\sigma_i}$$

where $f$ is the **active slot coefficient** and $\sigma_i = \text{stake}_i / \text{total\_active\_stake}$.

The expected number of blocks for pool $i$ per epoch is:

$$E[\text{blocks}_i] = L \times \phi(f, \sigma_i) = L \times \left(1 - (1-f)^{\sigma_i}\right)$$

For small $\sigma_i$ (all pools below saturation), this is well approximated by the linear form:

$$E[\text{blocks}_i] \approx L \times f \times \sigma_i = \frac{L \times f \times \text{stake}_i}{\text{total\_active\_stake}}$$

#### Current parameters

| Parameter | Symbol | Value | History |
| --- | --- | --- | --- |
| Epoch length | $L$ | 432,000 slots | Protocol constant since Shelley |
| Active slot coefficient | $f$ | 0.05 | Protocol parameter, **never changed** |
| Expected blocks/epoch | $L \times f$ | 21,600 | Consequence of L and f |
| Total active stake (epoch 616) | | 21.57B ADA | Variable — increases with participation |

The threshold for $n$ blocks per epoch follows directly:

$$\text{stake}_{n\text{-blocks}} \approx \frac{n \times \text{total\_active\_stake}}{L \times f}$$

#### What it depends on

The production threshold depends on exactly **three quantities**: epoch length $L$, active slot coefficient $f$, and total active stake. The first two are protocol constants/parameters that have never changed. The third — total active stake — is the only moving part.

This means the production threshold **scales linearly with total active stake**: as more ADA enters staking, every pool needs more stake to produce the same number of blocks. The viability line is not fixed — it rises with participation.

| Total active stake | 1-block threshold | 3-block threshold |
| --- | --- | --- |
| 10B ADA | 0.46M ADA | 1.39M ADA |
| 15B ADA | 0.69M ADA | 2.08M ADA |
| 20B ADA | 0.93M ADA | 2.78M ADA |
| **21.57B ADA** (current) | **0.97M ADA** | **2.92M ADA** |
| 25B ADA | 1.16M ADA | 3.47M ADA |
| 30B ADA | 1.39M ADA | 4.17M ADA |
| 38.49B ADA (full supply) | 1.78M ADA | 5.35M ADA |

If all circulating ADA were staked (full participation), the 3-block threshold would rise to **5.35M ADA** — the viability threshold would shift upward, pushing more pools below viability.

#### Production and variance

Block assignments follow a Bernoulli process across slots. For small $\sigma$, the block count per epoch is approximately **Poisson-distributed** with rate $\lambda = E[\text{blocks}]$. The coefficient of variation is $\text{CV} = 1/\sqrt{\lambda}$.

| Pool stake | E[blocks] | Std dev | CV | Practical meaning |
| --- | --- | --- | --- | --- |
| 100K ADA | 0.10 | 0.32 | 316% | Mostly zero — one block is an event |
| 500K ADA | 0.51 | 0.72 | 139% | One block every ~2 epochs, very noisy |
| **0.97M ADA** | **1.00** | **1.00** | **100%** | **1 block/epoch — Poisson noise dominates** |
| **2.92M ADA** | **3.00** | **1.73** | **58%** | **Regular production begins** |
| 10M ADA | 10.27 | 3.20 | 31% | Stable reward stream |
| 30M ADA | 30.81 | 5.55 | 18% | Reliable production |
| 77M ADA (z₀) | 79.09 | 8.89 | 11% | Near-deterministic |

At **1 block/epoch**, the CV is 100% — the reward is as variable as its own mean. An epoch with 0 blocks is just as likely as one with 2. A delegator observing such a pool sees wild oscillations between zero and double the expected reward.

At **3 blocks/epoch**, the CV drops to 58% — still volatile, but the pool produces blocks in the overwhelming majority of epochs. This is the threshold where a delegator can observe *consistent* performance. It coincides almost exactly with the **3M ADA viability line** identified in the prior report (Lopez de Lara, 2025/11) — not because 3M was chosen arbitrarily, but because regular block production is the minimum condition for a pool to demonstrate reliability.

#### Current landscape

| Threshold | Pools above | Active stake covered |
| --- | --- | --- |
| ≥1 block/epoch (0.97M ADA) | 946 | 99.1% |
| ≥3 blocks/epoch (2.92M ADA) | 729 | 97.3% |
| ≥10 blocks/epoch (10.1M ADA) | 511 | 91.6% |

The production threshold creates a natural cliff: pools below it produce too few blocks for delegators to assess reliability, and their reward variance is too high to sustain consistent yields.

#### 3.2.2 Viability threshold

Block production is necessary but not sufficient. A pool must also cover its operating costs — at minimum, the protocol-enforced **fixed cost** floor.

The reward per ADA staked per epoch is approximately **0.000312 ADA** (annualized: ~2.28%). For a pool with fixed cost of 340 ADA (the dominant setting at 66.3% of pools):

$$\text{Break-even stake} = \frac{\text{Fixed cost}}{\text{Reward per ADA}} = \frac{340}{0.000312} \approx 1.09\text{M ADA}$$

For 170 ADA fixed cost (17.3% of pools): break-even is ~0.54M ADA.

Below break-even, the pool's entire reward — and then some — is consumed by the fixed cost. The delegator receives nothing; the operator extracts more than the pool earns.

**The below-viability problem is severe:**

| Metric | Below viability (<3M) | Healthy (≥3M) |
| --- | --- | --- |
| Pools | 1,987 | 731 |
| Estimated group reward | 182K ADA/epoch | 6.61M ADA/epoch |
| Total fixed costs | 647K ADA/epoch | 1.56M ADA/epoch |
| Average pool reward | 91 ADA/epoch | 9,040 ADA/epoch |
| Fixed cost as % of avg reward | **372%** | 3.8% |
| Operator take | **358%** of group reward | 41.7% |

Below-viability pools collectively owe **647K ADA/epoch** in fixed costs but earn only **182K ADA**. The fixed cost exceeds pool reward by a factor of 3.6×. In aggregate, these pools destroy value: their delegators receive negative net reward (the fixed cost is deducted before any distribution).

This is not a marginal effect. The 1,987 below-viability pools represent 73% of all pools with stake. They exist — and attract delegators — despite being economically irrational for both parties. The persistence of this layer suggests delegators either do not understand the fee mechanics, are staking for non-economic reasons (governance, ideology, wallet defaults), or face friction in redelegating.

#### 3.2.3 Saturation threshold

The saturation point $z_0 = \text{Supply}/k = 76.99\text{M ADA}$ was designed as the central equilibrium mechanism: once a pool reaches z₀, the per-ADA reward for its delegators drops, pushing stake toward smaller pools until all k = 500 pools are equally sized.

| Metric | Value |
| --- | --- |
| Saturation point (z₀) | **76.99M ADA** |
| Theoretical capacity (k × z₀) | **38.49B ADA** |
| Active stake | **21.75B ADA** |
| Capacity utilisation | **56.5%** |
| Max pools that could saturate | **282** |
| Pools at ≥80% saturation | 104 |
| Pools at or above saturation | **8** |
| Design target | **500** |

The saturation cap is nearly inactive. It binds for 8 pools — 1.6% of the design target. The reason is arithmetic: with 21.75B ADA delegated and z₀ at 77M, the system can support at most 282 saturated pools even under perfect redistribution. The k = 500 target implicitly required near-complete participation (~100% of supply). Actual participation at 56.5% makes the target structurally unreachable.

The near-saturation zone (≥80% of z₀) contains 104 pools — a thin cluster rather than the broad plateau the design envisioned. The bulk of the healthy pool landscape sits between 3M and 60M ADA — far below saturation.

### 3.3 Tier definitions

The three thresholds partition the pool space into nine tiers. Each tier is defined by its bounding thresholds, its characteristic block production behaviour, and its economic status.

| Tier | Range (mainnet, epoch 616) | Defining threshold | Block production | Economic status |
| --- | --- | --- | --- | --- |
| **Zero-stake** | 0 ADA | — | None | Not operational |
| **Dormant** | >0 → ~100K ADA | — | < 0.1 blocks/epoch — effectively zero | Registered but inactive |
| **Sub-production** | ~100K → ~1M ADA | Production threshold (lower) | Sporadic — high variance, unreliable | Below break-even; extreme fixed-cost burden |
| **Sub-viable** | ~1M → ~3M ADA | Production threshold (upper) / Viability threshold | Regular but insufficient to cover fixed costs | Economically loss-making for delegators |
| **Healthy** | ~3M → ~38.5M ADA (50% sat) | Viability threshold | Consistent block production | Viable — covers costs, rewards delegators |
| **Large healthy** | ~38.5M → ~61.6M ADA (80% sat) | — | High, stable | Well-capitalised, efficient |
| **Near-saturation** | ~61.6M → ~73.1M ADA (95% sat) | Saturation threshold (approach) | Near-optimal | Close to maximum reward density |
| **Saturated** | ~73.1M → ~80.8M ADA (105% sat) | Saturation threshold | Optimal | Maximum reward; cap binding |
| **Oversaturated** | > ~80.8M ADA | Saturation threshold (exceeded) | Capped | Delegators penalised; stake should migrate |

#### Threshold values are dynamic

The boundary values above are computed from current mainnet conditions (epoch 616, 21.57B ADA active stake). They shift with three inputs:

| Threshold | Depends on | Direction with more participation | Direction with higher $k$ |
| --- | --- | --- | --- |
| Production | Active stake, $L$, $f$ | Rises — pools need more stake to reach same block count | Unchanged |
| Viability | Fixed cost, reward rate per ADA | Rises if rewards per ADA fall (e.g. as reserves deplete) | Unchanged |
| Saturation | Circulating supply, $k$ | Unchanged | Falls — each pool's cap shrinks |

When evaluating a scenario such as $k = 1000$, the saturation threshold halves to ~38.5M ADA — immediately reclassifying every current "large healthy" pool as near-saturation or saturated. The production and viability thresholds are unaffected by $k$ alone. This asymmetry is analytically important: CIPs targeting $k$ reshape the upper tail; CIPs targeting fees or block production reshape the lower tail.

---

### 3.4 Pool distribution by tier

The three thresholds produce a sharply asymmetric distribution: the vast majority of pools cluster at the bottom of the stake scale, while the overwhelming majority of delegated ADA concentrates in the upper tiers.

![Three Thresholds](figures/three_thresholds_mainnet.png)

The inversion is stark: **1,987 pools (73%) sit below the Viability threshold — yet collectively hold only 2.7% of active stake.** The top four tiers (Healthy and above) account for 27% of pools but 96.6% of stake. This structural gap between pool count and stake share is the defining feature of the current landscape and the primary motivation for the CIP proposals evaluated in §6.

---

## 4. Entity and MPO concentration

A significant fraction of the landscape is operated by **Multi-Pool Operators (MPOs)** — entities running two or more registered pools under a shared identity. The attributed entity set covers **901 pools across 85 entities**, holding **16.4B ADA** — **75.4% of participating stake** and 42.6% of circulating supply. Attribution combines public brand declarations, relay and metadata analysis, on-chain ownership clustering, and `pool_group` / `reward_addr` grouping (see `scripts/build_hidden_mpo_discovery.py`). This leaves **2,097 true single-pool SPOs** holding 5.44B ADA (25% of staked supply).

### 4.1 Capital class

Before examining archetypes, one structural distinction cuts across all 85 entities. The critical question is: **can the entity, if it chose to, self-pledge an entire pool to saturation?** The saturation cap $z_0 \approx 77M$ ADA divides the population in two.

**Capital-sufficient** (total stake ≥ z0): **47 entities, 496 live pools, 14.5B ADA.** These operators hold enough stake to fully saturate and self-pledge at least one pool. For them, non-compliance is a *choice* — or a structural constraint like custody — not a lack of resources.

**Capital-insufficient** (total stake < z0): **38 entities, 128 live pools, 1.74B ADA.** These operators run multiple pools but their combined stake falls short of a single saturation cap. Even consolidating everything into one fully self-pledged pool would not reach exemplary status at saturation scale. Their non-compliance is primarily an effect of *scale*, not strategic choice — the pledge bonus is too small at their pool sizes to matter. They are MPOs by structure but their incentive landscape is closer to that of a single SPO.

### 4.2 Archetypes

The 85 entities do not form a homogeneous group. Their motivations, delegation sources, and relationship to the protocol's incentive design differ fundamentally. Eight archetypes emerge, anchored on two axes: **delegation sovereignty** (who controls the delegating ADA and made the staking decision) and **incentive alignment** (can the entity respond to the pledge and saturation signals the protocol sends?).

#### 4.2.1 Classification

| Archetype | Code | Entities | Delegation source | Self-pledge | Incentive alignment |
| --- | --- | ---: | --- | --- | --- |
| Exchange Custody | `cex` | 6 | Retail balances custodied by a centralised exchange | Structurally zero | None |
| Institutional Validator | `ivaas` | 5 | Institutional clients via staking-as-a-service | Near-zero | Partial |
| Ecosystem Steward | `ecosystem` | 3 | Foundation or protocol developer self-stake | High | Mission-driven |
| Platform / Wallet | `platform` | 2 | Wallet users; staking mediated by platform UX | Variable | Partial |
| Community Branded Fleet | `community_branded_fleet` | 43 | Sovereign delegators choosing a branded pool family | Variable | Full |
| Independent MPO | `independent_mpo` | 9 | Sovereign delegators choosing the operator directly | Meaningful | Full |
| Multi-Brand Fleet | `multi_brand_fleet` | 8 | Sovereign delegators across multiple brands | Variable | Full |
| Opaque Fleet | `opaque_fleet` | 4 | Unknown — no public-facing brand | Near-zero | Unknown |
| Protocol / DeFi Project | `protocol_project` | 4 | Protocol users and treasury | Variable | Full |
| Opaque / Unresolved | `opaque` | 1 | Unknown | High | Unknown |

The canonical classification is in `data/mpo_entity_archetypes.csv` and includes `exclude_from_baseline` and `capital_class` fields.

**Snapshot by archetype (epoch 618):**

| Archetype | Entities | Live pools | Stake (B ₳) | % supply | Capital class |
| --- | ---: | ---: | ---: | ---: | --- |
| Exchange Custody (CEX) | 6 | 163 | 4.78 | 12.4% | All sufficient |
| Institutional Validator (IVaaS) | 5 | 88 | 2.63 | 6.8% | 4 suf. / 1 insuf. |
| Community Branded Fleet | 43 | 184 | 4.24 | 11.0% | 16 suf. / 27 insuf. |
| Independent MPO | 9 | 89 | 1.70 | 4.4% | All sufficient |
| Multi-Brand Fleet | 8 | 49 | 0.92 | 2.4% | 5 suf. / 3 insuf. |
| Opaque / Unresolved | 1 | 15 | 0.84 | 2.2% | Sufficient |
| Ecosystem Steward | 3 | 26 | 0.74 | 1.9% | 2 suf. / 1 insuf. |
| Platform / Wallet | 2 | 21 | 0.47 | 1.2% | All sufficient |
| Opaque Fleet | 4 | 22 | 0.71 | 1.8% | 3 suf. / 1 insuf. |
| Protocol / DeFi Project | 4 | 10 | 0.18 | 0.5% | All insufficient |

The **community branded fleet** archetype is the largest by entity count (43 of 85) — these are operators like ADV, SECUR, CCV, SIPO, NEDS, and CAFE who run clearly branded pool families with sequential tickers and dedicated metadata domains. In stake terms, however, CEX and IVaaS still account for **19.2% of supply** across 251 pools with near-zero pledge. The community-facing archetypes (branded fleets, independent MPOs, multi-brand fleets) collectively manage **6.86B ADA (17.8%)** — split roughly evenly between capital-sufficient operators who *could* optimize within the RSS and capital-insufficient ones who face the same scale constraints as single-pool SPOs.

The two archetypes that sit structurally outside the incentive design — Exchange Custody and Institutional Validator — are detailed in §4.3.

#### 4.2.2 Current distribution

![Current MPO entity distribution](figures/mpo_entity_current_distribution_mainnet.png)

Entities with ≥0.01% of circulating supply, grouped and colour-coded by archetype. Per-entity descriptions including pledge-coverage ratios are in the annex: **[docs/mpo_entity_profiles.md](docs/mpo_entity_profiles.md)**.

#### 4.2.3 Historical evolution

The MPO share of circulating supply has been structurally stable across three years of Shelley operation, despite significant internal rotation.

![Historical MPO composition by archetype](figures/mpo_entity_progression_stacked_mainnet.png)

The archetype-level stability masks significant entity-level rotation, visible in the per-entity breakdown below.

![Per-entity progression — share of circulating supply](figures/mpo_entity_progression_stacked_by_entity_mainnet.png)

The entity-level view reveals the dynamics hidden behind the stable aggregate: Binance has retreated from 7.4% (epoch 400) to 1.8% while Coinbase/bison.run held steady; Figment emerged from zero to 2.1% since epoch 584; CHUCK BUX appeared abruptly between epochs 410 and 584. The CEX share as a whole has remained at roughly 12–13% of supply throughout — the entities rotate but the total volume of shadow-custody stake persists.

### 4.3 From archetype to incentive stance

The archetype taxonomy (§4.2.1) answers *who is operating*: an exchange, a staking provider, a community pool family. But for assessing the effectiveness of incentive-parameter adjustments, the more useful question is *how does this entity behave relative to the mechanism's assumptions?*

Examining the pledge-coverage metrics across all 85 attributed entities reveals a pattern that cuts across archetype boundaries. Two archetypes — Exchange Custody and Institutional Validator — sit clearly outside the incentive design, but they are not alone. Many community fleets, an ecosystem steward (Emurgo), and a platform operator (NuFi) also operate at near-zero effective pledge, forfeiting the pledge bonus entirely. The distinction between archetype and incentive behaviour matters because **any proposed parameter adjustment — to $a_0$, $k$, or the pledge-benefit function — will only affect entities that currently capture a non-trivial share of the bonus**. Entities that already forfeit it are structurally insensitive to marginal changes.

This section details the two most clear-cut archetypes outside the design (§4.3.1–4.3.2), then introduces a behavioural reclassification — *incentive stance* — that replaces the identity-based lens with a pledge-bonus-capture lens (§4.3.3).

#### 4.3.1 Exchange Custody (CEX)

The `cex` archetype is the most consequential deviation from the protocol's assumptions. Cardano's incentive mechanism was designed around a principal–agent relationship: an ADA holder (principal) freely delegates to a stake pool operator (agent) whose competitiveness is disciplined by pledge, margin, and saturation pressure. Exchange-custody staking breaks this relationship at every level.

**Why CEX entities cannot respond to protocol incentives:**

**1. Delegation is not a choice by the ADA owner.** Exchange users hold a claim on the exchange's balance sheet, not self-sovereign ADA. The exchange decides which pools to run and how to configure them. The individual "staker" has no visibility into pool parameters and cannot redirect their stake.

**2. Pledge is structurally impossible.** The pledge incentive ($\lambda_{\max} \times A(\pi, \nu)$) rewards pools whose operators commit their own capital. An exchange cannot legally pledge custodied user funds as the operator's own — doing so would commingle customer assets. CEX pools therefore always operate at pledge ≈ 0 and never capture the pledge premium. This is not negligence; it is structural.

**3. Saturation pressure is absorbed, not transmitted.** When a CEX pool approaches z₀, the exchange creates a new pool and silently redistributes internal delegation. The saturation mechanism that was designed to push delegation toward smaller operators never fires — the CEX absorbs it internally.

**4. Revenue model is orthogonal to pool quality.** CEX staking revenue = protocol reward − user payout. The exchange optimises to maximise total reward across its fleet (more pools near z₀) rather than to maximise per-pool quality. Delegators cannot penalise poor pledge because they have no visibility into pool configuration.

**Entity profiles:**

The six CEX entities split into two distinct reward models that illustrate the same structural problem from opposite directions.

_Pass-through model_ (Coinbase, Binance, YUTA, StakeBowl) — pools are set at a low nominal on-chain margin (4–13%), passing most protocol rewards to the user while the exchange earns on custody, trading spread, and service products. The low margin creates the appearance of a competitive pool, but because users cannot identify or switch individual pools, the margin is decorative.

- **Coinbase / bison.run** is the largest single entity in the attributed set at 2.45B ₳ (6.4% of supply) across 47 active pools, 23 of which sit at near-saturation. It operates entirely behind deliberate infrastructure obfuscation: bison.run and herd.run subdomains, hashed metadata, randomised tickers — no first-party Coinbase branding is visible on-chain. Pool creation tracks exchange ADA inflows directly; the 23 near-saturation pools represent the maximum-reward configuration, not a response to delegation demand from external stakers.

- **Binance** registered 114 pools at peak and has since reduced to 50 active. The retreat from 7.4% (epoch 400) to 1.8% (epoch 618) is the steepest in the attributed set and tracks Binance's restructuring of its Earn product, not organic delegation outflow. The 64 dormant pools are a ghost fleet — pre-registered capacity that was never retired after the product scale-back.

- **YUTA** is a multi-brand cluster (coinzzz.jp, tokyostaker.com, katanapool.com, popool.net) aggregated by Koios and BalanceAnalytics under a single operator identity. 25 active pools, gradual decline from 2.0% to 1.2% since epoch 400. The multi-brand structure amplifies the attribution ambiguity inherent to CEX clusters.

- **StakeBowl** (neoply.io) operates 9 pools at 80.7% average margin — the highest within the pass-through group, approaching the full-internalisation model. Recent doubling from 0.18% to 0.36% between epochs 584 and 618 is unexplained.

_Full-internalisation model_ (Upbit, eToro) — pools set 100% on-chain margin, retaining all protocol rewards. The exchange pays users a separate fixed APY from its own treasury. The protocol reward signal is entirely decoupled from the user experience: users earn a yield determined by the exchange's product team, not by pool configuration.

- **Upbit** (Dunamu, South Korea) is the fastest-growing CEX entity: from near-zero at epoch 400 to 1.43% at epoch 618, entirely driven by exchange deposit growth. All 20 pools carry UPBIT tickers and point to staking-static.upbit.com metadata — the most transparent branding of any CEX entity. The 100% margin is not hidden.

- **eToro** has halved its active pool count from 24 to 12 since registration, signalling a partial wind-down of the Cardano staking product. Despite holding 1.23% of supply, 12 pools are dormant — the product is contracting while the stake persists.

#### 4.3.2 Institutional Validator (IVaaS)

IVaaS entities serve institutional clients — asset managers, custodians, exchanges, and wallets — via a staking-as-a-service product. Delegation is at the discretion of the client institution, not a sovereign retail choice. Unlike CEX, the underlying ADA holders could in principle choose another provider; in practice, switching costs and contractual arrangements create similar lock-in.

IVaaS entities could in principle pledge operator equity. The obstacle is scale: to shift the pledge premium $\lambda_{\max} \times (A_{\max} - A_i)$ by a meaningful amount at 500–800M ₳ of managed stake would require self-pledging hundreds of millions of ADA — an unrealistic ask for a staking-infrastructure company whose equity base is a fraction of the ADA it manages. The `cex` and `ivaas` archetypes therefore both suppress the protocol's pledge signal, but IVaaS does so by economic necessity, not by legal constraint.

**Entity profiles:**

- **Figment** is the most striking recent entrant in the full attributed set: non-existent before epoch 584, now at 2.07% with 36 active pools. It operates as the back-end staking provider for Ledger Live, meaning its apparent growth is driven by Ledger hardware wallet adoption rather than direct institutional sales. All metadata is hosted on pcpm.s3.amazonaws.com (no first-party Figment branding on-chain); Koios surfaces the cluster under the FIGMENT label. With 17 pools currently below the viability threshold, capacity was pre-registered ahead of demand.

- **Kiln** serves enterprises and major wallets and is the only IVaaS entity with explicit first-party on-chain branding (KILN0–KILN4 tickers, kiln.fi metadata). Its pools also appear under the ADALITE Koios label due to a legacy surface-level grouping shared with NuFi. All 11 pools are active; 6 sit at near-saturation — the most efficiently deployed fleet among IVaaS entities. Steady growth from 0.66% to 1.82% across the full measurement window, with the strongest acceleration between epochs 410 and 584.

- **Blockdaemon** combines node infrastructure, staking, and MPC vault products for enterprise clients. cardano.blockdaemon.com metadata and BD\* tickers provide clear first-party signals. 15 pools, broadly stable at 1.3–1.5% across all epochs — the flattest institutional trajectory, consistent with a mature, diversified enterprise client base rather than concentrated wallet inflows.

- **Everstake** markets Validator-as-a-Service and wallet/yield SDKs; its EVRST/EVERS/ESTK tickers and everstake.one metadata are unambiguous. 15 active pools, with the most stable share of any IVaaS entity: 1.41% → 1.43% → 1.20% → 1.47% across four epochs. The small dip at epoch 584 reversed fully, suggesting a single client rebalancing event rather than structural outflow. At 2.9% average margin, it operates the lowest-margin fleet in the IVaaS group.

- **RockX** is an Asian institutional validator with near-zero active stake across all measurement periods. Its pledge (≈1M ₳) currently exceeds its managed delegation — pools are registered and maintained but have not attracted meaningful institutional mandates on Cardano.

**Pledge suppression — CEX and IVaaS entities with <10K ₳ median pledge and ≥5 active pools (epoch 618):**

| Entity | Archetype | Pools (act) | Stake (B ₳) | Near-sat | Med. pledge | Margin | Why pledge ≈ 0 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Coinbase / bison.run | CEX | 47 | 2.451 | 23 | 0 | 4.6% | Cannot pledge custodied funds (legal) |
| Binance | CEX | 50 | 0.691 | 1 | 2 ₳ | 6.1% | Cannot pledge custodied funds (legal) |
| Figment | IVaaS | 36 | 0.788 | 4 | 0 | 8.4% | Scale makes pledge premium uneconomic |
| Kiln | IVaaS | 11 | 0.687 | 6 | 100 ₳ | 5.0% | Scale makes pledge premium uneconomic |
| Everstake | IVaaS | 15 | 0.567 | 1 | 1K ₳ | 2.9% | Scale makes pledge premium uneconomic |
| Blockdaemon | IVaaS | 15 | 0.561 | 4 | 200 ₳ | 5.7% | Scale makes pledge premium uneconomic |
| Upbit | CEX | 20 | 0.551 | 0 | 200K ₳ | 100% | Cannot pledge custodied funds (legal) |
| eToro | CEX | 12 | 0.472 | 0 | 0 | 100% | Cannot pledge custodied funds (legal) |
| YUTA | CEX | 25 | 0.465 | 0 | 50K ₳ | 12.6% | Custodial/platform staking |
| StakeBowl | CEX | 9 | 0.140 | 2 | 0 | 80.7% | Custodial/platform staking |

**CEX-adjusted baseline.** When CEX entities are excluded, the attributed set covers **~6.41B ₳ across 20 entities** (16.6% of circulating supply, 29.3% of participating stake). Analyses of pledge coverage, reward efficiency, and concentration risk are materially cleaner against this baseline because it removes structurally pledge-zero, non-sovereign stake from the denominator. The `exclude_from_baseline: true` flag in `data/mpo_entity_archetypes.csv` identifies which entities to drop.

#### 4.3.3 Incentive stance: reclassifying by pledge-bonus capture

The archetype analysis above shows that CEX and IVaaS entities cannot or do not pledge — but it frames the problem as confined to two categories. The pool-level pledge data tells a different story.

**The pledge bonus is linear.** For a saturated pool ($\sigma' = z_0$), the bonus captured scales exactly as $s'/z_0$ — at 1% effective pledge ratio, 1% of the bonus is captured; at 30%, 30%. For a half-saturated pool the relationship is mildly super-linear (30% pledge captures ~51% of that pool's maximum bonus), but the qualitative picture is the same: very low pledge means very low capture, and the reward foregone returns to the reserve as *within-stake inefficiency*.

This linearity creates a natural classification based on how much of the pledge bonus an entity actually captures. We define four **incentive stances** based on the effective pledge ratio ($= \min(\text{declared\_pledge}, \text{active\_stake}) / \text{active\_stake}$, aggregated across all active pools of the entity):

| Stance | Effective pledge ratio | Bonus captured (saturated) | Bonus captured (half-sat) | Interpretation |
| --- | --- | --- | --- | --- |
| **Exemplary** | ≥ 80% | ≥ 80% | ≥ 90% | Captures the vast majority of the bonus. 80/20 principle: the last 20% of pledge captures diminishing marginal returns. |
| **Compliant** | 30–80% | 30–80% | 51–90% | Captures a significant share. Sensitive to parameter changes. |
| **Marginal** | 2–30% | 2–30% | 4–51% | Partial capture. Primary target population for incentive adjustments. |
| **Non-compliant** | < 2% | < 2% | < 4% | Forfeits the bonus entirely. Structurally insensitive to any marginal change to $a_0$ or the pledge function. |

The 2% lower threshold reflects the point below which the bonus captured is indistinguishable from noise (< 2% of the available premium). The 30% threshold is the *median capture point* for half-saturated pools: below 30% pledge, the entity wastes more than half of the bonus available to it. The 80% threshold follows the Pareto principle — at 80% pledge, an entity captures the vast majority of the available bonus; the remaining 20% of pledge effort yields diminishing marginal returns.

**Applied to all 85 MPO entities (epoch 618):**

| Stance | Entities | Stake (B ₳) | % supply | Composition |
| --- | --- | --- | --- | --- |
| **Non-compliant** | 70 | 13.60 | 35.3% | All CEX, all IVaaS, Emurgo, NuFi, and the majority of community fleets and independent MPOs |
| **Marginal** | 7 | 0.45 | 1.2% | ATADA, ACL, CNODE, HODLA, KIWI, and 2 others — entities at the 2–30% pledge boundary |
| **Compliant** | 5 | 1.70 | 4.4% | CHUCK BUX (79.8%), Wave (35.5%), Bloom (33.6%), IOG (38.5%), RAID (56.5%) |
| **Exemplary** | 3 | 0.66 | 1.7% | CF (85.9%), Adalite (93.2%), Liqwid (~95%) |

The critical finding: **70 of 85 entities — 82% — are non-compliant**, holding 13.60B ADA (35.3% of supply). This is not just CEX and IVaaS: it includes most community branded fleets, multi-brand operators, and opaque fleets. Across all archetypes, operators with a pledge ratio below 2% have *chosen* not to play the pledge game — or, in the case of custodial entities, *cannot*. No marginal adjustment to $a_0$ will change this calculus because the pledge bonus they currently capture is effectively zero.

The **marginal class now contains 7 entities** (0.45B ADA) — a thin but non-empty band. These are operators like ATADA (1.92% pledge ratio) and ACL who sit just at the decision boundary. A well-calibrated reform could tip them toward compliance. Their presence reflects the finer-grained pledge ratios of community operators compared to CEX/IVaaS.

The five compliant entities — representing 4.4% of supply — remain the population where parameter adjustments most directly bite. Wave and Bloom exemplify the compliant independent operator: meaningful pledge (34–36% of stake), competitive margin, sovereign delegators. CHUCK BUX (79.8%) sits just below the exemplary threshold. The three exemplary entities (CF, Adalite, Liqwid) at 1.7% of supply are effectively self-staked — they already capture ≥80% of the bonus and would be the least affected by marginal changes.

> [!NOTE]
> **Implication for mechanism-design work.** Any proposed change to $a_0$, $k$, or the pledge-benefit curve should be evaluated against its effect on the *compliant* and *marginal* populations (~5.6% of supply combined), not against the full MPO set. The non-compliant 70 entities (35.3% of supply) are a fixed point — they will not respond. The exemplary population (1.7%) already captures most of the bonus. The within-stake inefficiency generated by non-compliant entities is a structural feature of the current ecosystem, not a parameter to be optimised away by small adjustments.

![MPO attributed stake — archetype vs incentive stance](figures/mpo_entity_stance_distribution_mainnet.png)

The figure decomposes the same attributed stake two ways: top bar by archetype (identity), bottom bar by incentive stance (behaviour). The dominance of the non-compliant segment is immediately visible — nearly 80% of the attributed MPO stake forfeits the pledge bonus entirely.

### 4.4 Within-staked inefficiency: the cost of non-compliance

§2.2 established that the network-wide pledge bonus uncaptured is **~770K ADA/epoch (~56.2M/year)** — the second-largest component of within-staked waste at 39% of the total. The incentive-stance classification allows us to attribute this waste to its sources.

For each MPO pool, we compute three reward levels under the current formula $\hat{f}'(\pi, \nu, \bar{p})$:

- **Actual reward**: using the pool's current effective pledge ($\min(\text{declared}, \text{active\_stake})$)
- **Maximum reward**: assuming full self-pledge ($\pi = \nu$) at the pool's current stake level
- **Lost reward**: the difference — ADA that returns to the reserve instead of being distributed

**MPO entities — reward loss by incentive stance (epoch 618, pools in envelope detail):**

| Stance | Entities | Stake (B ₳) | Lost (₳/epoch) | Lost (₳/year) | Share of MPO loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Non-compliant** | 19 | 8.84 | 178,359 | 13,020,199 | **92.1%** |
| **Compliant** | 5 | 1.68 | 12,452 | 908,984 | 6.4% |
| **Exemplary** | 2 | 0.61 | 2,926 | 213,621 | 1.5% |
| **Subtotal (top 200 pools)** | **26** | **11.13** | **193,737** | **14,142,803** | 100% |

> [!NOTE]
> The table above covers the top 200 pools by stake (the envelope detail dataset). These pools belong to the largest MPO entities and capture the vast majority of MPO-attributable waste. The remaining MPO pools (mostly from community fleets below Near-saturation) contribute additional waste, but the per-pool amounts are small because the pledge bonus scales with stake.

These MPO entities account for **193,737 ADA/epoch** of pledge-bonus waste — **25.2% of the network-wide total** (~770K). The remaining ~75% is distributed across the other active pools (SPOs and smaller MPO pools with low pledge-to-stake ratios at small scale).

The critical number: **92.1% of MPO-attributable waste comes from the non-compliant population**. These entities — holding 8.84B ADA of active stake — collectively forfeit ~178K ADA/epoch (~13M/year) in pledge bonus. This is reward that the protocol *would* distribute if these entities pledged their stake, but which instead returns to the reserve.

**Top five contributors to MPO pledge waste:**

| Entity | Stance | Stake (B ₳) | Lost (₳/epoch) | Lost (₳/year) | % of max reward lost |
| --- | --- | ---: | ---: | ---: | ---: |
| Coinbase / bison.run | Non-compliant | 2.45 | 68,028 | 4,966,071 | 17.2% |
| Kiln | Non-compliant | 0.69 | 21,777 | 1,589,695 | 20.3% |
| Figment | Non-compliant | 0.79 | 16,941 | 1,236,702 | 14.3% |
| Blockdaemon | Non-compliant | 0.58 | 14,921 | 1,089,234 | 16.0% |
| Everstake | Non-compliant | 0.57 | 9,854 | 719,324 | 11.4% |

Coinbase alone accounts for **35% of all MPO pledge waste** (68K/epoch). The top five — all non-compliant — account for 68% of the total. These are large-scale entities where the absolute ADA forfeited is substantial, but as a percentage of their maximum reward it ranges from 11–20% — the "cost of not pledging" is a modest tax on reward, not a punitive penalty. This is precisely why they remain non-compliant: the current $a_0 = 0.3$ makes the pledge bonus a nice-to-have, not a must-have.

> [!NOTE]
> **Connection to §2.2.** The 193,737 ADA/epoch of MPO pledge waste is a subset of the 770K network-wide "pledge bonus uncaptured" identified in §2.2. The MPO entities contribute 25% of this waste because they concentrate large stake volumes at near-zero pledge ratios. The remaining 75% is distributed across thousands of smaller pools where low absolute pledge is more a function of operator capital constraints than of strategic indifference.
>
> **Why this matters for mechanism design.** If a parameter change (e.g., increasing $a_0$) aims to reduce within-staked inefficiency, its impact on the non-compliant MPOs would be *to increase the penalty they already ignore*. The waste would grow in absolute terms, but the entities would not change behaviour — they *cannot* pledge (CEX/IVaaS) or *choose* not to (community fleets, independent MPOs). The reform would effectively transfer more ADA from these entities to the reserve, which may or may not be the intended outcome.

### 4.5 MPO pool taxonomy by incentive stance

Crossing the incentive-stance classification with the pool-size taxonomy (§3) reveals where MPO pledge compliance *actually sits* in the stake landscape — and the picture is more telling than either dimension alone.

![MPO Pool Taxonomy by Incentive Stance](figures/mpo_taxonomy_by_stance_mainnet.png)

The entity-level breakdown below shows exactly who sits where — each sub-bar is one entity's pools within a tier × stance group:

![MPO Tier × Stance × Entity](figures/mpo_tier_stance_entity_mainnet.png)

A third view isolates the non-compliant entities and recolours the bars by **pool-size tier** rather than by stance. The left panel shows fleet composition; the right panel shows where the stake sits:

![Non-compliant MPO entities by pool-size tier](figures/mpo_non_compliant_entity_tier_distribution_mainnet.png)

The most striking observation is that **non-compliance is not a small-pool problem** — it is a *scale* phenomenon. Non-compliant red dominates *every viable-and-above tier*, from Healthy through Oversaturated, accounting for **81% of MPO viable stake**. The intuition that non-compliant pools are marginal, under-resourced operators is flatly contradicted by the data: the largest single non-compliant fleet, **Coinbase / bison.run** (2.45B ADA, 22 of 44 live pools in Near-saturation), is one of the most operationally successful entities on the network.

This non-compliance is also **remarkably dispersed across the tier spectrum**. Across the 19 non-compliant entities, live stake splits between Healthy (2.85B ADA), Large healthy (2.51B), Near-saturation (2.40B), and Saturated or Oversaturated (1.05B). No single size bucket concentrates the problem. This matters for mechanism design: if non-compliance were confined to one tier, a targeted parameter adjustment might address it. Instead, any change to $z_0$, $minPoolCost$, or $a_0$ would ripple across *all* tiers — affecting compliant operators alongside the non-compliant ones it aims to reach.

The entity profiles reinforce this dispersion. **Upbit** and **YUTA** are almost pure Healthy-tier operators. **Binance** is visibly bimodal — a healthy core alongside a long Dormant/Sub-production tail. **Kiln**, **Blockdaemon**, **eToro**, and **Everstake** skew upward into Large healthy, Saturated, or Oversaturated tiers, showing that the pledge signal remains ignored even once pools are already operating at scale.

On the other side of the spectrum, **exemplary compliance exists only at saturation scale**: CF and Adalite self-pledge ≥62M ADA per pool to reach the ≥80% threshold at $z_0 = 77M$. The **compliant class** (Wave, Bloom, CHUCK BUX) appears in Near-saturation and Healthy tiers with 30–80% pledge ratios — proof that meaningful bonus capture *is* feasible at mid-scale, but only for operators who **own** their delegated stake. The **marginal class**, by contrast, is nearly empty among MPOs. Unlike the all-pool analysis (§5) where 637 pools sit in the 2–30% band, MPO entities almost never land there. This confirms the **bimodal behaviour** from §4.3.3: among multi-pool operators, the pledge signal is either fully embraced or entirely ignored. There is very little middle ground.

Taken together, the tier × stance overlay reveals a fundamental asymmetry. The pledge mechanism *works* for the handful of entities that can self-fund at scale — but for the **vast majority of MPO stake**, which is custodial by nature, the mechanism is *architecturally inaccessible*. This is not a calibration gap that parameter tuning can close. It is a structural mismatch between the mechanism's assumptions and the business models that dominate half the staked supply.

### 4.6 Conclusion

The MPO landscape reveals a striking outcome. Many of these entities possess sufficient capital to *fully* optimize their position within the Reward Sharing Scheme — saturating additional pools, leveraging pledge, capturing the bonus. Yet the data is unambiguous: **they deliberately choose not to**.

The cost of that choice is not trivial. As quantified in §4.3, the 19 non-compliant entities collectively forfeit **~178K ADA per epoch — roughly 13M ADA per year** — in pledge bonus that the protocol *would* distribute if they pledged their stake. The top five alone (Coinbase, Kiln, Figment, Blockdaemon, Everstake) account for 68% of this loss. And yet, as a fraction of their maximum reward, the penalty ranges from only 11 to 20%. At the current $a_0 = 0.3$, the pledge bonus is a **nice-to-have, not a must-have** — and these entities have priced it accordingly.

This is not irrational. It is a clear manifestation of what we call ***multi-game optimization***: these actors are not maximizing within the RSS alone — they are optimizing across a broader strategic landscape where other payoffs dominate.

The most obvious driver is **custodial architecture**. Exchange operators like Coinbase, Binance, and Upbit *cannot* pledge customer deposits. Their staking business exists as a value-added layer on top of retail custody — the revenue model is the management fee charged off-chain, not the on-chain pledge bonus. For infrastructure-as-a-service operators (Kiln, Figment, Blockdaemon, Everstake), the constraint is identical: institutional clients retain ownership of delegated stake, making self-pledge structurally impossible. These entities are not *choosing* to ignore the pledge signal. **The signal is architecturally inaccessible to them.**

Beyond custodial constraints, other forces reinforce non-compliance. Saturating additional pools means deploying more infrastructure, managing key rotation across a larger fleet, and coordinating pledge capital — operational costs that, for a 20- to 60-pool operator, may exceed the 11–20% bonus uplift once denominated in fiat. Independent MPOs that *could* pledge more may instead prioritize brand consistency, governance positioning, or delegation relationships that pool consolidation would disrupt. The Chang-era governance framework amplifies this: an entity's DRep registration and voting history creates **reputational capital** that may be worth more than marginal RSS optimization. And several of these operators derive significant revenue from adjacent services — API endpoints, RPC infrastructure, institutional reporting — that are entirely uncorrelated with pledge compliance.

The implication runs deeper than any single parameter. The Reward Sharing Scheme must be understood not as *the* game these actors play, but as **one sub-game embedded within a larger system of incentives**. The RSS design specification (SL-D1) necessarily modelled a single-game world to derive tractable equilibria — this was standard and appropriate. But the on-chain reality is a multi-game environment where roughly 40% of MPO entities, controlling **51% of staked supply**, optimize across dimensions the RSS does not capture. This is not a marginal edge effect. It *fundamentally* limits the predictive power of models that assume single-game rationality, and it explains why the observed pool distribution diverges from the $k$-equilibrium the model predicts.

For mechanism design, the practical consequence is sobering. Increasing $a_0$ to “punish” non-compliance would raise the absolute ADA forfeited by these entities — but the evidence suggests it would **not change their behaviour**. The custodial constraint is structural. The independent MPOs have already revealed that their cross-game payoffs dominate. The reform would simply transfer more ADA to the reserve, *increasing* within-staked waste rather than reducing it. Any future parameter reform must therefore be evaluated against the **actual population structure** documented here — not against the theoretical assumption that all actors respond to marginal incentive changes.

---

## 5. The RSS-responsive landscape

§4 identified **85 MPO entities** (901 pools, 16.4B ADA, 75% of staked supply) and classified them by archetype and capital sufficiency. With this foundation, we can now ask: **what does the pool landscape look like when we set the non-responsive actors aside?** Two complementary views are presented below.

### 5.1 Filtering methodology

Two views of the landscape are constructed from the §4 mapping:

**View A — SPO only.** Removes *every* MPO pool (all 85 entities, 901 pools), regardless of stance or capital class. This isolates the true single-pool independent population: **2,097 pools** carrying **5.44B ADA**.

**View B — RSS-responsive.** Removes only the non-compliant MPO pools (pledge ratio < 2%). Compliant and exemplary MPO pools — from both capital classes — are *retained* but visually distinguished (hatched bars). This yields **2,167 pools** carrying **7.47B ADA**, of which 70 are compliant MPO pools (2.03B ADA).

### 5.2 View A — Independent SPOs only

![Pool Landscape — Independent SPOs Only](figures/filtered_landscape_spo_only_mainnet.png)

Stripping all 85 MPO entities reveals the community operator base in its purest form: **5.44B ADA** across **2,097 pools**. This is the population that is genuinely independent — single operators, small teams, community projects running one or two pools with their own stake and organic delegation.

The landscape is dominated by a **massive Dormant tail** in pool count and a **Healthy-tier core** in stake terms. The Healthy tier (3M–38M ADA) is the undisputed centre of gravity for community operators. Above it, the tiers thin out rapidly — reaching Near-saturation as an independent single-pool operator, without custodial or institutional delegation, is genuinely rare.

**Stance distribution (SPO only):**

| Stance | Pools | Stake (B ₳) | % of SPO stake | Reading |
| --- | ---: | ---: | ---: | --- |
| **Non-compliant** | 905 | 4.25 | 78.1% | The large majority — pledge signal too weak at their scale |
| **Marginal** | 561 | 0.87 | 16.1% | Operators who *partially* pledge (2–30%) — the policy-sensitive population |
| **Exemplary** | 360 | 0.23 | 4.3% | Self-staked micro-pools and a handful of high-pledge community operators |
| **Compliant** | 271 | 0.08 | 1.5% | Mostly very small pools with high pledge ratios but negligible stake |

The SPO-only view makes one thing starkly clear: **without MPO stake, the exemplary and compliant classes are economically negligible** — 5.8% of stake combined. The pledge bonus, at current $a_0$, does not meaningfully reward community operators. Nearly 78% of independent stake is non-compliant — not because operators are irrational, but because the incentive is *correctly priced as irrelevant* at their scale.

### 5.3 View B — RSS-responsive landscape (SPOs + compliant MPOs)

![Pool Landscape — Excluding Non-Compliant MPOs](figures/filtered_landscape_mainnet.png)

Adding back the 70 compliant MPO pools transforms the upper tiers. The Saturated tier, nearly empty in the SPO-only view, now carries significant stake — almost entirely from compliant MPOs (CF, Adalite, Wave, Bloom, CHUCK BUX). These are the entities that *do* self-pledge at scale. Their presence is the empirical proof that the RSS mechanism works when the actor *can* and *chooses to* respond to the pledge signal.

**Stance distribution (RSS-responsive):**

| Stance | Pools | Stake (B ₳) | % filtered stake | Profile |
| --- | ---: | ---: | ---: | --- |
| **Non-compliant** | 905 | 4.25 | 56.9% | Community SPOs — same population as View A |
| **Marginal** | 591 | 1.20 | 16.0% | Expands with compliant MPO marginal pools |
| **Exemplary** | 386 | 1.52 | 20.3% | Now substantial — driven by large self-pledged MPO pools |
| **Compliant** | 285 | 0.51 | 6.8% | Mid-range pledge operators |

The contrast between the two views tells the story. In the SPO-only landscape, the exemplary class holds 0.23B ADA (4.3%). In the RSS-responsive landscape, it holds **1.52B ADA (20.3%)** — a **6.6× increase** almost entirely attributable to compliant MPOs operating at saturation scale. The mechanism's pledge bonus *does* capture significant capital — but only from entities large enough for the bonus to matter in absolute terms.

### 5.4 What the two views reveal together

Reading the two landscapes side by side surfaces three findings that are invisible in the unfiltered data.

First, the **true competitive playing field for community operators** becomes visible. With MPOs accounting for ~75% of staked supply, only 5.44B ADA remains in single-pool hands. The Healthy tier dominates this landscape — and it is here that parameter reform will have its primary effect. The **561 marginal SPOs** (16.1% of SPO stake) sit at the decision boundary: they have already demonstrated willingness to pledge between 2% and 30% of their stake, and a well-calibrated increase in $a_0$ or a reshaped pledge curve could tip them toward compliant. This is where reform has the **highest expected return**.

Second, the **capital-class split clarifies who can respond to what**. The 47 capital-sufficient MPOs (14.5B ADA) could, in theory, optimize within the RSS — but the CEX and IVaaS entities (7.9B ADA combined) are structurally unable to do so, and the capital-sufficient community fleets *choose* not to, as documented in §4.6. On the other side, the 38 capital-insufficient MPOs (1.74B ADA) face the same constraint as most SPOs: the pledge bonus is simply too small at their scale to justify consolidation. Increasing $a_0$ would raise the penalty for capital-sufficient non-compliant operators (who would absorb it as a cost) while having almost no effect on capital-insufficient ones (who are already below the bonus activation threshold).

Third, the **compliant MPOs and independent SPOs occupy different tiers** with minimal overlap. In the RSS-responsive landscape, compliant MPOs concentrate in Saturated and Near-saturation while SPOs dominate Healthy and below. Reforms targeting the Healthy-tier SPO population are unlikely to disrupt compliant MPO operators at the top, and vice versa. This separation means **targeted interventions are feasible**.

> [!NOTE]
> **Why this matters for simulation.** Any RSS parameter change (adjusting $a_0$, reshaping the pledge curve, introducing $minPoolMargin$) should be simulated against the *RSS-responsive* population, not the full landscape, and should model the three segments separately: non-compliant MPOs (fixed background), capital-insufficient MPOs (behave like SPOs), and the 561 marginal SPOs who sit at the tipping point.

---

## 6. Reward formula anatomy

The pool reward curve is the single expression that governs how the pools pot is distributed. Every pool's reward — and every ADA that returns to the reserve — is determined by this formula. This section reads it left to right, factor by factor, to show exactly where value is captured and where it leaks.

### 6.1 The full formula

$$\hat{f}'(\pi, \nu, \bar{p}) = \underbrace{\bar{p}}_{\text{performance}} \;\cdot\; \underbrace{P_{\max}}_{\text{ceiling}} \;\cdot\; \underbrace{\left( \lambda_{\min}\;\nu \;+\; \lambda_{\max}\;A(\pi, \nu) \right)}_{\text{proportioning envelope } E(\pi,\nu)}$$

Three multiplicative factors. Each ranges from 0 to 1 (effectively). When all three equal their maximum, the pool earns the full ceiling $P_{\max}$. Every departure from the ideal is a multiplicative discount — and the uncaptured fraction returns to the reserve.

| Factor | Symbol | What it captures | Ideal value |
| --- | --- | --- | --- |
| Performance | $\bar{p}$ | Did the pool produce its assigned blocks? | 1.0 |
| Ceiling | $P_{\max}$ | Maximum reward for any single pool per epoch | 31K ADA |
| Proportioning envelope | $E(\pi,\nu)$ | How well is the pool sized and pledged? | 1.0 (ν=1, π=1) |

The actual reward = $\bar{p} \times P_{\max} \times E(\pi,\nu)$. The ratio of actual to $P_{\max}$ is the pool's **reward efficiency**: $\eta_i = \bar{p}_i \times E_i$.

### 6.2 Factor 1 — Performance ($\bar{p}$)

The pool's actual block production relative to its VRF-assigned expectation:

$$\bar{p} = \frac{\text{blocks produced}}{\text{blocks expected}} = \frac{n_{\text{actual}}}{L \cdot \phi(f, \sigma_i)}$$

where $L = 21{,}600$ slots/epoch, $f = 0.05$, and $\phi(f, \sigma) = 1 - (1-f)^{\sigma}$ is the slot leadership probability (§5.2).

For a saturated pool (σ ≈ 0.2%), expected blocks ≈ 43/epoch. The Poisson coefficient of variation is $1/\sqrt{43} \approx 15\%$, so epoch-to-epoch variance is moderate. Over a rolling window, $\bar{p}$ converges toward 1.0 for well-operated pools.

**On mainnet:** The network-wide aggregate performance $\hat{\eta}$ averages **0.977** — meaning ~2.3% of the pot is lost to missed blocks. Individual pool performance varies more widely, particularly for sub-production pools where expected block counts are low and variance dominates (§5.2).

$\bar{p}$ is the only factor the operator directly controls through infrastructure quality. The remaining two factors are structural — determined by the pool's stake and pledge relative to protocol parameters.

### 6.3 Factor 2 — The ceiling ($P_{\max}$)

$$P_{\max} = \frac{1}{k} \cdot R = \frac{1}{500} \times 15.53\text{M} \approx 31{,}060\text{ ADA/epoch}$$

where $R = PoolsPot^{\text{epoch}}$ is the total pot available for distribution (after treasury cut and $\eta$ adjustment), and $1/k$ is the share each of the $k = 500$ target pools would receive in the ideal case.

$P_{\max}$ is **not a parameter** — it is an emergent ceiling. It is the reward a single pool earns when $\bar{p} = 1$, $\nu = 1$ (fully saturated), and $\pi = 1$ (fully pledged). No pool can exceed it. It sets the scale of the entire distribution.

(Recall: $z_0 = \text{Supply}/k = 76.99\text{M ADA}$ is the saturation threshold in ADA. Here $1/k = 0.2\%$ is the corresponding share of the pot — the same fraction, expressed as a pot share rather than a stake amount.)

In the ideal design, $k = 500$ pools each earn $P_{\max}$, and the full pot is distributed: $500 \times P_{\max} = R$. On mainnet, the sum of all pool rewards is **6.79M ADA** — only **43.7%** of the 15.53M pot. The gap is the subject of §5.5.

### 6.4 The playing field

Before analysing the envelope's mechanics, it is worth framing the **rules of the game** concretely: what can a pool earn, what does each level cost in capital, and what does the pledge bonus actually buy?

![The Playing Field](figures/playing_field_mainnet.png)

#### Three reward tiers

| Tier | Reward/epoch | Reward/year | What it requires |
| --- | --- | --- | --- |
| **$P_{\max}$** — absolute ceiling | **31,067 ADA** | **2.27M ADA** | 77M ADA stake + 77M ADA pledge + $\bar{p}=1$ |
| **Size ceiling** — zero pledge | **23,898 ADA** | **1.74M ADA** | 77M ADA stake + $\bar{p}=1$. No pledge needed. |
| **Pledge bonus** — the gap | **7,169 ADA** | **523K ADA** | The difference. Requires 77M ADA of *personal* capital pledged. |

The size-only ceiling ($\lambda_{\min} \times P_{\max}$) is what **any** saturated pool earns regardless of pledge commitment. It captures 76.9% of $P_{\max}$. The remaining 23.1% is the pledge bonus — and unlocking it in full requires the operator to **pledge the entire saturation amount** (77M ADA) as personal capital.

The implied yield on that pledge commitment: $523\text{K ADA/yr} \div 77\text{M ADA} = 0.68\%\text{/yr}$. For comparison, the base staking yield (delegator) is ~2.3%/yr. An operator who pledges 77M ADA earns **less incremental return on that capital** than they would by simply delegating it to another pool.

#### The bonus at every scale

| Pool size | ν | Zero-pledge reward | Max pledge (π=ν) reward | Bonus | Relative uplift | Yield on pledge capital |
| --- | --- | --- | --- | --- | --- | --- |
| 3M ADA | 0.039 | 931 ADA/ep | 932 ADA/ep | **+0.4 ADA** | +0.05% | 0.001%/yr |
| 10M ADA | 0.130 | 3,104 ADA/ep | 3,120 ADA/ep | **+16 ADA** | +0.5% | 0.011%/yr |
| 30M ADA | 0.390 | 9,312 ADA/ep | 9,736 ADA/ep | **+424 ADA** | +4.6% | 0.10%/yr |
| 50M ADA | 0.649 | 15,520 ADA/ep | 17,484 ADA/ep | **+1,964 ADA** | +12.7% | 0.29%/yr |
| 77M ADA | 1.000 | 23,898 ADA/ep | 31,067 ADA/ep | **+7,169 ADA** | +30.0% | 0.68%/yr |

Reading the table: a 10M ADA pool where the operator pledges the entire pool (fully self-funded, no delegators) earns 16 ADA more per epoch than the same pool with zero pledge. That is 1,168 ADA/year on a 10M ADA capital lockup — a yield of **0.01%/yr**. The "max pledge" column assumes π = ν (the operator pledges the entire stake — no external delegators), which is the physical maximum for the bonus.

**A typical healthy pool** (30M ADA stake, 100K ADA pledge — the median configuration):

$$E = 76.923\% \times 0.39 + 23.077\% \times A(0.0013, 0.39) = 30.0\% + 0.012\% = 30.01\%$$

Reward: **9,316 ADA/epoch**. The pledge adds **3.6 ADA/epoch** — less than the epoch-to-epoch variance of a single block.

#### What this means

The protocol allocates 23.1% of $P_{\max}$ — equivalent to **3.4M ADA/epoch across all pools** — to incentivise pledge. But the incentive's structure makes it economically irrational to respond to: at every pool size below full saturation, the yield on pledged capital is a fraction of what passive delegation earns. The "game" for operators is overwhelmingly about **size** (ν), not **commitment** (π). The bonus exists in the formula but not in the economics.

### 6.5 Factor 3 — The proportioning envelope ($E$)

$$E(\pi, \nu) = \underbrace{\lambda_{\min} \cdot \nu}_{\text{base}} + \underbrace{\lambda_{\max} \cdot A(\pi, \nu)}_{\text{pledge bonus}}$$

with $\lambda_{\min} = \frac{1}{1+a_0} = 76.923\%$, $\lambda_{\max} = \frac{a_0}{1+a_0} = 23.077\%$, and $A(\pi,\nu) = \pi\nu - \pi^2(1-\nu)$.

The envelope $E$ determines what fraction of $P_{\max}$ the pool can capture. It has two additive components:

| Component | Expression | Driven by | Range |
| --- | --- | --- | --- |
| **Base** | $\lambda_{\min} \cdot \nu = 76.923\% \cdot \nu$ | Pool size only | 0 → 76.923% |
| **Pledge bonus** | $\lambda_{\max} \cdot A(\pi,\nu) = 23.077\% \cdot A$ | Size + pledge | 0 → 23.077% |
| **Envelope total** | $E(\pi,\nu)$ | | 0 → 100% |

#### 6.5.1 The base: what size alone buys

A pool with **zero pledge** (π = 0) has $A(0, \nu) = 0$. Its envelope collapses to:

$$E(0, \nu) = 76.923\% \cdot \nu$$

This is the reward floor — purely proportional to saturation level, independent of pledge. A zero-pledge pool at full saturation (ν = 1) earns $76.923\% \times P_{\max} \approx 23.8\text{K ADA}$. The remaining 23.077% of $P_{\max}$ is structurally inaccessible to it.

At half saturation (ν = 0.5): $E(0, 0.5) = 38.46\%$. At typical healthy-pool sizes (ν = 0.05 to 0.5): $E$ ranges from 3.8% to 38.5% of $P_{\max}$.

#### 6.5.2 The pledge bonus: what commitment adds

The activation function $A(\pi, \nu) = \pi\nu - \pi^2(1-\nu)$ controls access to the remaining 23.077% of $P_{\max}$. Its behaviour:

**Full pledge + full saturation** (π = 1, ν = 1): $A(1,1) = 1$, so $E = 76.923\% + 23.077\% = 100\%$. The pool earns the full $P_{\max}$.

**Full pledge + half saturation** (π = ν = 0.5): $A(0.5, 0.5) = 0.125$, so $E = 38.46\% + 2.88\% = 41.35\%$. The bonus adds **2.88 percentage points** — a 7.5% uplift over the zero-pledge base.

**Physical constraint: π ≤ ν.** Pledge is part of total stake, so π can never exceed ν. The maximum bonus at a given ν is reached when pledge = total stake (π = ν, fully self-funded pool):

$$A(\nu, \nu) = \nu^3 \qquad \Rightarrow \qquad \text{max bonus at } \nu = \lambda_{\max} \cdot \nu^3$$

$$\text{Max relative uplift at } \nu = \frac{\lambda_{\max} \cdot \nu^3}{\lambda_{\min} \cdot \nu} = a_0 \cdot \nu^2$$

| Saturation (ν) | Max $A$ | Bonus (% of $P_{\max}$) | Total $E$ | Relative uplift over zero-pledge |
| --- | --- | --- | --- | --- |
| 1.0 (full) | 1.000 | 23.077% | **100%** | **30.0%** |
| 0.8 | 0.512 | 11.82% | 73.36% | 19.2% |
| 0.5 | 0.125 | 2.88% | 41.35% | **7.50%** |
| 0.3 | 0.027 | 0.62% | 23.70% | 2.70% |
| 0.1 | 0.001 | 0.023% | 7.72% | 0.30% |

The 30% headline bonus requires ν = 1 (77M ADA fully pledged). At typical mainnet sizes (ν = 0.05 to 0.5), even a fully self-funded pool gets between 0.08% and 7.5% relative uplift. The pledge bonus is **structurally suppressed by undersaturation**.

#### 6.5.3 Envelope on mainnet

![Pledge Bonus Activation](figures/pledge_bonus_activation_mainnet.png)

| Pledge | π | $A$ at ν=1 | Bonus (ν=1) | $A$ at ν=0.5 | Bonus (ν=0.5) |
| --- | --- | --- | --- | --- | --- |
| 100 ADA | 0.0000013 | 0.0000013 | 0.000% | 0.0000003 | 0.000% |
| 10K ADA | 0.00013 | 0.00013 | 0.004% | 0.000057 | 0.004% |
| 100K ADA | 0.0013 | 0.0013 | 0.039% | 0.00057 | 0.034% |
| 1M ADA | 0.013 | 0.013 | 0.39% | 0.0056 | 0.34% |
| 10M ADA | 0.13 | 0.13 | 3.90% | 0.0566 | 3.39% |
| 38.5M ADA | 0.50 | 0.50 | 15.0% | **0.125** | **7.50%** ← max at ν=0.5 |
| 50M ADA | 0.65 | 0.65 | 19.5% | — | n/a (π > ν) |
| 77M ADA | 1.00 | **1.00** | **30.0%** | — | n/a (π > ν) |

**Pledge bonus distribution across healthy pools:**

| Statistic | Value |
| --- | --- |
| Median relative bonus | **0.006%** |
| P75 | 0.051% |
| P90 | 0.224% |
| P99 | 29.2% |
| Pools with bonus > 1% | **37** out of 731 (5%) |
| Pools with bonus > 5% | 28 |
| Pools with bonus > 10% | 25 |

The a0 curve is effectively a **step function**: near-zero for pools below ~10M ADA pledge (95% of pools), meaningful only for ~40 institutional/foundation pools that concentrate enough capital to move $A$.

**Pledge band distribution:**

| Pledge band | Pools | % of pools |
| --- | --- | --- |
| Zero (0 ADA) | 226 | 8.3% |
| Micro (<10K ADA) | 1,340 | 49.3% |
| Low (10K–100K ADA) | 696 | 25.6% |
| Modest (100K–1M ADA) | 362 | 13.3% |
| Material (1M–10M ADA) | 54 | 2.0% |
| High (≥10M ADA) | 40 | 1.5% |

83% of pools with stake pledge below 100K ADA. The median pledge-to-stake ratio for healthy pools is **0.14%**. The bonus mechanism was designed for a world where operators commit meaningful capital; the actual landscape is one where it is functionally invisible.

### 6.6 Reward efficiency decomposition

The three factors combine multiplicatively. For each pool $i$:

$$\text{Reward}_i = \bar{p}_i \times P_{\max} \times E(\pi_i, \nu_i)$$

Summing across all pools with stake, the **aggregate distribution efficiency** is:

$$\eta_{\text{dist}} = \frac{\sum_i \bar{p}_i \cdot E_i}{k} = \frac{\text{Total distributed}}{R} = \frac{6.79\text{M}}{15.53\text{M}} = 43.7\%$$

The remaining **56.3% returns to the reserve**. This waste decomposes by formula factor — each factor's shortfall from its ideal maps directly to a structural loss.

![Reward Anatomy](figures/reward_anatomy_mainnet.png)

#### The base is distribution-neutral

A key structural property: the base term $\lambda_{\min} \cdot \nu$ is **linear in ν**. This means:

$$\frac{\sum \text{base}_i}{k} = \frac{\lambda_{\min} \cdot \sum \nu_i}{k} = \frac{76.923\% \times 282.5}{500} = 43.5\%$$

where $\sum \nu_i = \text{total\_stake} / z_0 = 21.75\text{B} / 76.99\text{M} = 282.5$ saturation units. Because the sum is linear, **it does not matter how pools are distributed** — 282 equal pools or 2,718 varied pools produce the same aggregate base (modulo the 7 oversaturated pools losing 0.27% to the cap). The base captures what participation allows and nothing more.

#### The bonus is distribution-sensitive

The bonus term $\lambda_{\max} \cdot A(\pi, \nu)$ is **non-linear** — $A$ depends on the product $\pi\nu$ and is cubic in ν when π = ν. This means the bonus is structurally sensitive to both pool size and pledge level.

$$\frac{\sum \text{bonus}_i}{k} = \frac{\lambda_{\max} \cdot \sum A_i}{k} = 1.00\%$$

The bonus captures only **1.00%** of the pot — out of a theoretical maximum of 23.077% (if all 500 pools were at π = ν = 1). Even under the weaker assumption that every pool maximises its pledge (π = ν for each), the maximum possible bonus would be $\lambda_{\max} \cdot \sum \nu_i^3 / k$, which is small because cubing sub-unit ν values crushes them. The a0 mechanism was designed for a world of 500 saturated, pledged pools; the actual landscape cannot activate it.

#### Decomposition by formula factor

| Formula factor | Contribution to pot | Ideal (500 pools, π=ν=1) | Shortfall |
| --- | --- | --- | --- |
| Base ($\lambda_{\min} \cdot \nu$) | **43.19%** | 76.923% | 33.73% |
| Bonus ($\lambda_{\max} \cdot A$) | **1.00%** | 23.077% | 22.08% |
| **Envelope $E$ (pre-performance)** | **44.19%** | 100% | **55.81%** |
| Performance ($\bar{p}$) | −0.50% | 0% | 0.50% |
| **Actual distributed** | **43.7%** | 100% | **56.3%** |

Reading the table: the base alone captures 43.19% of the pot (driven entirely by participation level). The bonus adds 1.00% (mostly from ~40 high-pledge pools). Performance losses shave off another 0.50%. The rest — 56.3% — returns to the reserve.

#### Where the waste lives

| Waste source | % of pot lost | % of total waste | Mechanism |
| --- | --- | --- | --- |
| **Base shortfall** (participation) | 33.73% | **59.9%** | $\sum \nu_i = 282.5 < k = 500$; not enough stake participates |
| **Bonus shortfall** (pledge + structure) | 22.08% | **39.2%** | π ≈ 0 for most pools; $A$ cubic in ν crushes undersaturated pools |
| **Performance loss** | 0.50% | **0.9%** | Missed blocks ($\bar{p} < 1$) |
| **Total** | **56.31%** | **100%** | |

The bonus shortfall (22.08%) is the second-largest waste source — larger than one might expect for a "negligible" mechanism. This is because the bonus envelope reserves **23.077% of the pot** for pledge activation, but the actual landscape activates almost none of it. This is not idle capacity that could be redirected; under the current formula, it is structurally unreachable.

To make this concrete: the bonus shortfall of 22.08% of the pot equals **~3.4M ADA/epoch** that the formula allocates to the pledge incentive but that returns to the reserve unused. This is the cost of maintaining $a_0 = 0.3$ in a landscape where pledge is functionally irrelevant.

#### Relationship to §2 waste decomposition

The §2 decomposition split waste into participation (78%) and within-staked inefficiency (22%). The formula decomposition offers a finer-grained view:

- The **participation waste** from §2 (78% of waste, 6.82M ADA) maps to most of the base shortfall — but the base shortfall also includes the bonus's dependence on ν. Even under perfect pledge, the bonus is suppressed by low participation because $A(\nu,\nu) = \nu^3$ scales cubically with saturation.
- The **within-staked inefficiency** from §2 (22%, 1.92M ADA) includes both the pledge shortfall at the current participation level and performance losses.

Both views confirm the same conclusion: the dominant loss is participation, the pledge mechanism is inert, and pool structure contributes modest additional waste.

---

## 7. Pool landscape

### 7.1 Current snapshot

![Pool Landscape by Size](figures/pool_landscape_by_size_mainnet.png)

![Saturation Utilisation](figures/saturation_utilisation_mainnet.png)

| Metric | Value |
| --- | --- |
| Circulating supply | **38.49B ADA** |
| Active stake in registered pools | **21.75B ADA** (56.5% of supply) |
| Protocol k | **500** |
| Saturation point (z₀) | **76.99M ADA** |
| Registered pools | **2,948** |
| Pools with stake | **2,718** |
| Healthy pools (≥3M ADA) | **731** (carry 97.3% of active stake) |
| Below viability (<3M ADA) | **1,987** (carry 2.7% of active stake) |
| Near-saturation (≥80% z₀) | **104** |
| At or above saturation | **8** |

Historical reference (canonical landscape report):
- Positive-stake pools peaked at **3,029** in epoch 331; now **2,718**.
- Healthy pools peaked at **851** in epoch 439; now **731**.
- Near-saturation layer peaked at **240** pools in epoch 248; now **104**.

The trend is slow contraction: fewer pools, more stake concentration in the surviving healthy core.

### 7.2 Reward concentration

Recent-window data (epochs 593+) from the canonical reward distribution report:

| Rank | Reward share |
| --- | --- |
| Top 10 pools | 3.1% |
| Top 50 pools | 12.9% |
| Top 100 pools | 23.2% |
| Top 250 pools | 46.9% |

| Category | Reward share | Block share |
| --- | --- | --- |
| Dormant + Sub-production + Sub-viable (<3M) | 2.2% | 2.3% |
| Healthy (3M–30M) | 36.5% | 37.1% |
| Large healthy (30M–60M) | 23.7% | 24.1% |
| Near-saturation (60M–z₀) | 19.4% | 19.5% |
| Saturated (z₀+) | 16.8% | 15.1% |
| Oversaturated | 1.3% | 1.8% |

Reward share tracks block share closely — the reward curve does not dramatically amplify or compress differences in pool scale. The dominant factor in reward allocation is stake size, not pledge or performance.

### 7.3 Entity and MPO concentration

The MPO entity set (§4) covers **901 pools** across **85 entities**, holding **16.4B ADA** — **75.4% of staked supply** (42.6% of circulating supply). The top 5 entities by stake are:

Top 5 entities by stake:

| Entity | Stake (B ADA) | % supply | Pools | Median pledge |
| --- | --- | --- | --- | --- |
| Coinbase / bison.run | 2.45 | 6.37% | 48 | 0 ADA |
| CHUCK BUX | 0.83 | 2.17% | 17 | 73M ADA |
| Figment | 0.79 | 2.05% | 37 | 0 ADA |
| Binance | 0.69 | 1.80% | 53 | 2 ADA |
| Kiln | 0.69 | 1.78% | 11 | 100 ADA |

The largest entities by stake (Coinbase, Figment, Binance, Kiln) operate with near-zero pledge. The pledge mechanism does not differentiate them from solo operators. This is the stable configuration of a staking economy where institutional actors dominate capital deployment.

---

## 8. Protocol parameters

Three protocol parameters directly govern pool-level distribution. All have been constant since reaching their current value.

| Parameter | Symbol | Value | History |
| --- | --- | --- | --- |
| Target pool count | $k$ | 500 | Raised from 150 to 500 at epoch 257, **unchanged since** |
| Pledge influence | $a_0$ | 0.3 | Set at Shelley (epoch 208), **never changed** |
| Saturation point | $z_0$ | 76.99M ADA | Mechanical consequence of k and supply |

---

## 9. Forward-looking

**Capital constraint.** If participation remains at ~56.5%, the maximum number of saturable pools is fixed at ~282 regardless of formula changes. Governance incentives, exchange policy changes, and new delegation products could shift this.

**Pledge reform.** CIP-0050 and CIP-0037 both target the pledge-bonus ineffectiveness (O3) and saturation underutilisation (O4). Their effectiveness depends on whether they can shift the a0 curve from a step function to a gradient that differentiates at realistic pledge levels (100K–10M ADA).

**k parameter.** Any increase in k raises the saturation bar further. k = 1000 would require ~77B ADA in delegation (200% of supply) — clearly infeasible.

**Fixed cost reform.** CIP-0023 and CIP-0082 operate at the downstream operator/delegator layer, but interact with this layer through the fixed-cost floor. Removing or reforming the 340 ADA minimum would directly address the below-viability pool value-destruction documented in §3.2.

---

## 10. Reproduction

### 10.1 Full rebuild

All figures and data summaries rebuild from a single entry point:

```bash
cd scripts/
bash build_all.sh
```

Or selectively:

```bash
python3 build_pool_distribution_snapshot.py   # snapshot JSON + MD
python3 build_reward_anatomy.py               # reward anatomy JSON
python3 build_reward_anatomy_visual.py
python3 build_playing_field_visual.py
python3 build_pledge_bonus_activation_visual.py
python3 build_saturation_utilisation_visual.py
python3 build_pool_landscape_by_size_visual.py
python3 build_three_thresholds_visual.py
python3 build_mpo_entity_deep_dive.py          # fetches Koios — see §9.2
python3 build_mpo_progression_analysis.py      # reads local history CSV
```

**Requirements:** Python 3.9+, `matplotlib`, `numpy`. No other dependencies.

**Static input data** (self-contained in `data/`, no network required):
- `koios_pool_list_mainnet.csv` — current pool snapshot (one row per pool)
- `koios_pool_history_mainnet.csv` — epoch-by-epoch pool stake timeseries
- `pool_reward_pool_summary_mainnet.csv` — aggregated pool-level rewards
- `pool_reward_epoch_summary_mainnet.csv` — epoch-wide reward totals
- `koios_pool_updates_mainnet.csv` — pool registration/update history
- `mainnet_entity_owner_capital_status_quo.csv` — entity attribution

**MPO derived data** (generated by `build_mpo_entity_deep_dive.py`, checked in for offline use):
- `mpo_entity_summary_mainnet.csv` — one row per attributed entity
- `mpo_entity_pool_mapping_mainnet.csv` — pool → entity mapping
- `mpo_entity_health_overview_mainnet.csv` — health metrics per entity
- `mpo_unresolved_group_labels_mainnet.csv` — unresolved Koios group labels
- `mpo_progression_proxy_key_epochs_mainnet.csv` — historical concentration at key epochs

### 10.2 Refreshing MPO data

The MPO scripts (`build_mpo_entity_deep_dive.py` and `build_mpo_progression_analysis.py`) fetch live data from the [Koios REST API](https://api.koios.rest) and require an internet connection. They should be re-run whenever a new epoch's pool snapshot is needed.

**Refresh procedure:**

```bash
cd scripts/

# Step 1 — refresh the base pool list and history (if not already done)
# These come from Koios exports — replace data/koios_pool_list_mainnet.csv
# and data/koios_pool_history_mainnet.csv with updated exports.

# Step 2 — re-run the MPO entity analysis (fetches live Koios data)
python3 build_mpo_entity_deep_dive.py

# Step 3 — re-run the progression analysis (reads local history CSV)
python3 build_mpo_progression_analysis.py
```

`build_mpo_entity_deep_dive.py` calls three Koios endpoints:
- `pool_list` — all registered pools with current stake and metadata
- `pool_groups` — Koios-curated group labels (used as a seed for entity attribution)
- `tip` + `totals` — live epoch number and circulating supply

The entity attribution logic (regex patterns, manual overrides, pledge thresholds) is entirely self-contained in the script — no external configuration file is needed. To add or update an entity cluster, edit the `ENTITY_PATTERNS` block near the top of `build_mpo_entity_deep_dive.py`.

---

_Last updated: 2026/03/18_
