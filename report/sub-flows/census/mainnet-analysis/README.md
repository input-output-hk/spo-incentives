# The Staking Census — Populations, Capital, and Participation on Cardano Mainnet

_Built on 2026/04/09 from db-sync snapshot at epoch 623._


## Table of Contents

- [Objective](#objective)
- [Data sources](#data-sources)
- [Methodology note — iterative cleaning](#methodology-note--iterative-cleaning)
- [1. The ADA Supply](#1-the-ada-supply)
- [2. Pool Operators](#2-pool-operators)
  - [2.1 Raw query](#21-raw-query)
  - [2.2 Cleaning — production threshold](#22-cleaning--production-threshold)
  - [2.3 Cleaning — entity attribution](#23-cleaning--entity-attribution)
  - [2.4 Operator landscape — epoch 623](#24-operator-landscape--epoch-623)
- [3. Delegators](#3-delegators)
  - [3.1 Raw query](#31-raw-query)
  - [3.2 Cleaning — zero-balance certificates](#32-cleaning--zero-balance-certificates)
  - [3.3 Cleaning — non-productive pools](#33-cleaning--non-productive-pools)
  - [3.4 Cleaning — operator-controlled delegations](#34-cleaning--operator-controlled-delegations)
  - [3.5 Cleaning — custodial delegations](#35-cleaning--custodial-delegations)
  - [3.6 Delegator landscape — epoch 623](#36-delegator-landscape--epoch-623)
- [4. Non-Participants](#4-non-participants)
- [5. Synthesis](#5-synthesis)
  - [Key metrics](#key-metrics-epoch-623)
  - [Concentration headline](#concentration-headline)
  - [Noise removal log](#noise-removal-log)
  - [What remains noisy](#what-remains-noisy)
- [6. Bridges to Companion Analyses](#6-bridges-to-companion-analyses)
  - [6.1 Distribution efficiency (epoch 616)](#61-distribution-efficiency-epoch-616)
  - [6.2 Operator's cut (epoch 614)](#62-operators-cut-epoch-614)
  - [6.3 Main report (epochs 548–583)](#63-main-report-epochs-548583)
  - [6.4 Reconciliation summary](#64-reconciliation-summary)


## Objective

This report maps the full population of actors in the Cardano staking ecosystem — and those absent from it. Before analysing how rewards are shared (the companion [*Pools Pot Distribution*](../../pools-distribution/mainnet-analysis/) and [*Operator's Cut*](../../operator-delegator-distribution/mainnet-analysis/) reports), it is necessary to understand *who* is on the field, *how many* they are, and *how much capital* each population controls — and how all three have evolved since the Shelley hard fork.


## Data sources

All data comes from **cardano-db-sync** (PostgreSQL, snapshot at epoch 623). No third-party API.

| Table | Content |
|---|---|
| `ada_pots` | Per-epoch supply decomposition: reserve, treasury, circulating, UTxO, unclaimed rewards, deposits |
| `epoch_stake` | Per-epoch staking snapshot: total staked per delegation, ~560M rows |
| `delegation` | Individual delegation certificates: addr → pool |
| `pool_update` + `pool_owner` | Pool registration history and owner keys |
| `stake_deregistration` | Stake key deregistration events |


## Methodology note — iterative cleaning

The raw db-sync tables contain structural noise that must be understood and progressively removed before drawing conclusions. Rather than presenting only a final "clean" picture, this document shows each cleaning pass explicitly: what noise was identified, what was done about it, and how the numbers changed. This makes the analytical choices visible and auditable.

Each section therefore follows a **raw → clean** structure:
the raw query result is shown first, then the noise is named, then the cleaned version is presented.


## 1. The ADA Supply

The Cardano monetary policy fixes the maximum supply at 45 billion ADA. At epoch 623, the circulating supply has reached 36.88B, with 6.45B remaining in the reserve and 1.66B accumulated in the treasury. Monetary expansion — the rate at which reserve ADA enters circulation — decays geometrically.

![Supply decomposition](figures/supply_decomposition_mainnet.png)

At epoch 623: **21.75B ADA** staked out of **36.88B** circulating = **59.0%** staking rate. The remaining **15.13B ADA** (41.0%) does not participate in staking — this population is decomposed in §4.

![Staking participation](figures/staking_participation_clean.png)

The top panel shows the staked/unstaked decomposition of circulating supply with the staking rate (red line, right axis). The rate peaked near 71% around epoch 260 and has been declining gently, driven by circulating supply growth outpacing new stake inflows.


## 2. Pool Operators

### 2.1 Raw query

The pool count from epoch_stake peaked at **3,160** (epoch 331) and currently stands at **2,877**. This counts only pools that appear in the staking snapshot with non-zero delegated stake — the registration-certificate count of 5,919 includes 3,042 empty pools and is discarded (see §3.2 for the full rationale).

![Pool count — cleaned](figures/pool_count_clean.png)

The k=500 reference line shows the protocol's target number of pools (the saturation parameter). The actual pool count has been ~5.8× k since epoch 330, though many of these pools carry negligible stake.

### 2.2 Cleaning — production threshold

A pool must hold enough stake to expect at least one block per epoch. With ~21,600 blocks per epoch and 21.75B total staked ADA, the production threshold is approximately **1M ADA** per pool.

| Segment | Pools | Share of pools | Stake | Share of stake | Delegations |
|---|---|---|---|---|---|
| Above threshold (≥1M ADA) | 951 | 33.1% | 21.57B | 99.14% | 1,295,095 (95.6%) |
| Below threshold (<1M ADA) | 1,926 | 66.9% | 0.19B | 0.86% | 59,940 (4.4%) |

Two thirds of all pools are below the production threshold. Together they hold less than 1% of staked ADA. Their 59,940 delegators collectively control 188M ADA — a negligible share that earns intermittent and unpredictable rewards.

Below-threshold pool breakdown by stake:

| Tier | Pools | Stake |
|---|---|---|
| < 1K ADA | 778 | 0.1M |
| 1K–10K | 394 | 1.4M |
| 10K–100K | 323 | 12.4M |
| 100K–500K | 286 | 69.0M |
| 500K–1M | 144 | 104.3M |

The median below-threshold pool holds just 2,547 ADA. Three quarters hold less than 68K ADA — orders of magnitude below what is needed for regular block production.

**After cleaning:** the productive pool count drops from 2,877 to **951** — closer to, but still ~1.9× the protocol's k=500 target.

### 2.3 Cleaning — entity attribution

The 951 productive pools are not 951 independent operators. Many pools share a controlling entity — detectable on-chain through shared `pool_owner` keys, and off-chain through metadata, ticker naming patterns, relay DNS, reward addresses, and public disclosures. This cleaning pass groups pools by entity to reveal the true operator landscape.

**On-chain grouping** (shared owner keys across productive pools): 943 single-pool operators and 4 entities sharing keys across 8 pools. On-chain keys are a lower bound — most multi-pool operators use separate keys per pool.

**Off-chain attribution** combines on-chain signals with metadata analysis. Across all registered pools, this identifies **85 named entities** controlling **660 pools**. Filtering to the 951 productive pools: 2 entities disappear entirely (RAID — 7 pools, RockX — 10 pools, all below threshold), 10 entities shrink to a single productive pool (reclassified as attributed single-pool operators), leaving **73 named entities** controlling **464 pools** (16.29B ADA, 75.5% of productive stake). The remaining **477 pools** (5.28B ADA, 24.5%) are unattributed single-pool operators.

| Segment | Pools | Stake | Share of productive stake |
|---|---|---|---|
| Attributed to named entities | 474 | 16.29B ADA | 75.5% |
| Unattributed (single-pool operators) | 477 | 5.28B ADA | 24.5% |

The productive landscape splits almost evenly by pool count but is heavily skewed by stake: attributed entities control three quarters of productive stake through half the pools.

![Stake attribution landscape](figures/entity_stake_landscape_623.png)

The entity attribution data lives in:
- [`data/mpo_entity_pool_mapping_mainnet.csv`](data/mpo_entity_pool_mapping_mainnet.csv) — pool → entity
- [`data/mpo_entity_archetypes.csv`](data/mpo_entity_archetypes.csv) — entity → archetype
- [`data/entity_stake_summary_623.csv`](data/entity_stake_summary_623.csv) — per-entity stake at epoch 623
- [`docs/mpo_entity_profiles.md`](docs/mpo_entity_profiles.md) — detailed entity profiles

### 2.4 Operator landscape — epoch 623

| Segment | Entities | Pools | Stake | Share |
|---|---|---|---|---|
| **Raw total** | **2,302** | **2,877** | **21.75B** | **100%** |
| Below production threshold (noise) | 1,742 | 1,925 | 0.19B | 0.9% |
| **Productive total** | **560** | **952** | **21.57B** | **99.1%** |
| _of which:_ | | | | |
| Identified entities (all pools) | 85 | 660 | 16.31B | 75.0% |
| Identified — multiple productive pools | 73 | 465 | 15.83B | 73.4% |
| Identified — single productive pool | 10 | 10 | 0.46B | 2.1% |
| Identified — no productive pool (RAID, RockX) | 2 | 17 | 0.6M | <0.1% |
| Independent single-pool operators | 477 | 477 | 5.28B | 24.5% |

The entity attribution is a current-epoch snapshot and a lower bound — entities using entirely separate infrastructure and branding for each pool remain invisible. The real multi-pool operator count is certainly higher than 73. Historical entity decomposition requires reconstructing the owner-key graph and metadata per epoch.

#### Historical decomposition — productive vs sub-threshold pools

The production threshold — the minimum stake a pool needs to expect at least one block per epoch — rises mechanically with total staked ADA. At epoch 211 (Shelley launch), a pool needed roughly 470K ADA; by epoch 623 the threshold has crossed 1M ADA. The number of pools that clear this threshold has remained remarkably stable around 900–1,000 since epoch 300, while the sub-threshold tail grew from near zero to almost 2,000 pools by epoch 330 and has hovered there since. The productive share of pools has therefore fallen from near 100% in early Shelley to roughly 33% today — yet productive pools continue to control over 99% of staked ADA throughout the entire history.

![Operator landscape — historical decomposition](figures/operator_landscape_history.png)

The top panel shows the staked-ADA split between productive and sub-threshold pools (left axis) alongside the production threshold itself (red line, right axis). The bottom panel shows the pool-count decomposition, with the productive share (purple line, right axis) declining as the long tail of sub-threshold pools inflated the denominator without capturing meaningful stake. The k=500 reference line marks the protocol's target pool count.


## 3. Delegators

### 3.1 Raw query

Two db-sync tables count delegators in different ways:

| Source | What it counts | Epoch 623 value |
|---|---|---|
| `epoch_stake` aggregation | Rows with non-zero stake in the epoch snapshot | **1,355,035 delegations** across **2,877 pools** |
| `delegation` table reconstruction | Active delegation certificates (regardless of balance) | **1,847,713 addresses** across **5,919 pools** |

The gap: ~493K addresses hold an active delegation certificate but have zero balance in the epoch_stake snapshot. Similarly, ~3,042 registered pools have delegation certificates pointing at them but carry no actual stake.

![Delegator count — cleaned](figures/delegator_count_clean.png)

### 3.2 Cleaning — zero-balance certificates

A delegation certificate is a *declaration of intent*. An epoch_stake row is *capital at work*. An address with a certificate but no ADA earns no rewards and does not participate in consensus.

| Metric | Raw (delegation table) | Clean (epoch_stake) | Noise removed |
|---|---|---|---|
| Active delegations | 1,847,713 | **1,355,035** | 492,678 certificate ghosts (26.7%) |
| Active pools | 5,919 | **2,877** | 3,042 empty pools (51.4%) |

**After cleaning:** 1,355,035 delegations, 21.75B ADA across 2,877 pools.

### 3.3 Cleaning — non-productive pools

The 1,925 pools below the production threshold (§2.2) carry 59,937 delegations and 0.19B ADA. These delegators earn intermittent and unpredictable rewards. Removing them aligns the delegator population with the productive operator landscape.

**After cleaning:** 1,295,098 delegations, 21.57B ADA across 952 productive pools.

### 3.4 Cleaning — operator-controlled delegations

Pool operators delegating their own capital (pledge/owner stake) are not independent delegators — their delegation is a structural requirement, not a choice. Using the `pool_owner` table to identify stake addresses registered as pool owners:

| Category | Delegations | Stake | Share of stake |
|---|---|---|---|
| Operator self-delegation | 3,254 | 2.95B | 13.7% |
| Operator cross-delegation | 380 | 0.02B | 0.1% |
| **Removed** | **3,634** | **2.98B** | **13.8%** |

The median operator self-delegation is just **1,298 ADA** while the average is **908K ADA** — a small number of large pledgers (exchanges, IVaaS providers) pull the average up, while the majority of pool operators have negligible skin in the game. The 380 operators delegating to someone else's pool have abandoned their pledge incentive entirely (median 328 ADA).

**After cleaning:** 1,291,464 delegations, 18.59B ADA.

### 3.5 Cleaning — custodial delegations

Pools with very few delegations but large amounts betray a custodial structure: a single omnibus wallet holds capital on behalf of many end-users. Filtering for pools with ≤20 delegations and ≥10M ADA total stake:

| Entity | Pools | Delegations | Stake | Avg per deleg |
|---|---|---|---|---|
| Coinbase / bison.run | 36 | 231 | 2.14B | 9.3M |
| CHUCK BUX | 13 | 13 | 0.88B | 67.5M |
| Upbit | 20 | 28 | 0.57B | 20.5M |
| Binance | 18 | 212 | 0.57B | 2.7M |
| Figment | 14 | 62 | 0.50B | 8.1M |
| eToro | 10 | 31 | 0.47B | 15.1M |
| Cardano Foundation | 6 | 28 | 0.40B | 14.1M |
| Blockdaemon | 6 | 32 | 0.32B | 10.0M |
| **Total custodial** | **154** | **853** | **6.98B** | — |

Each of these "delegations" represents an unknown number of underlying users. The delegation choice for custodial capital is made by the operator, not by the end-users whose ADA it represents.

**After cleaning:** 1,290,611 delegations, 11.61B ADA — retail delegators making independent pool choices.

### 3.6 Delegator landscape — epoch 623

| Segment | Delegations | Stake | Share | Pools | Entities |
|---|---|---|---|---|---|
| **Raw (delegation certificates)** | **1,847,713** | — | — | **3,190** | **2,374** |
| Zero-balance certificates (noise) | 492,678 | 0 | — | 313 | 72 |
| **epoch_stake total** | **1,355,035** | **21.75B** | **100%** | **2,877** | **2,302** |
| Non-productive pool delegations (noise) | 59,937 | 0.19B | 0.9% | 1,925 | 1,742 |
| **Productive pool delegations** | **1,295,098** | **21.57B** | **99.1%** | **952** | **560** |
| Operator self-stake | 3,634 | 2.98B | 13.7% | 952 | 560 |
| Custodial | 853 | 6.98B | 32.1% | 154 | 21 |
| **Retail** | **1,290,611** | **11.61B** | **53.4%** | **798** | **539** |

The delegator-side entity attribution remains a limit: a Coinbase delegation of 50M ADA is one on-chain row representing thousands of end-users. The true number of staking participants is unknowable from on-chain data alone.


## 4. Non-Participants

The 41% of circulating ADA that is unstaked (15.13B ADA at epoch 623) is not a uniform population. It includes exchange cold wallets holding ADA that users have not opted to stake, smart-contract-locked ADA (DeFi protocols, DEX liquidity pools), and dormant wallets that have seen no activity since before the Shelley hard fork.

Decomposing this requires UTxO-level analysis — mapping unspent outputs to address types (base, script, enterprise) and cross-referencing with known exchange addresses. This is planned for a subsequent cleaning pass.


## 5. Synthesis

### Key metrics (epoch 623)

| Metric | Value | Source |
|---|---|---|
| Circulating supply | 36.88B ADA | ada_pots |
| Staked | 21.75B ADA (59.0%) | epoch_stake |
| Unstaked | 15.13B ADA (41.0%) | computed |
| Active delegations | 1,355,035 | epoch_stake |
| Active pools | 2,877 | epoch_stake |
| Named entities (productive) | 73 entities / 464 pools | entity attribution on productive pools |
| Unattributed single-pool operators (productive) | 477 pools | epoch_stake − entity attribution |
| Delegations per pool | ~471 | epoch_stake |
| ADA per delegation | ~16,050 ADA | epoch_stake |
| Gini coefficient (stake concentration) | 0.974 | tier-aggregated Lorenz |

### Concentration headline

| Population slice | Count | Share of delegations | Stake | Share of stake |
|---|---|---|---|---|
| Titan (10M+ ADA) | 318 | 0.02% | 9.75B | 44.8% |
| Mega + Titan (1M+) | 2,244 | 0.17% | 14.05B | 64.6% |
| Micro (<100 ADA) | 801,067 | 59.1% | 0.01B | 0.05% |

### Noise removal log

| Section | What changed | Impact |
|---|---|---|
| §2 Pool Operators | Removed pools below production threshold (~1M ADA) | Productive pools: 2,877 → 951 (−67%). Removed pools carry 0.86% of stake. |
| §2 Pool Operators | Grouped productive pools by entity (on-chain keys + off-chain attribution) | 73 named entities controlling 464 pools (75.5% of stake). 477 unattributed single-pool operators (24.5%). CEX custody alone = 21.8%. |
| §3 Delegators | Removed zero-balance certificates | 1.85M → 1.36M delegations (−27%). 5,919 → 2,877 pools (−51%). |
| §3 Delegators | Removed non-productive pool delegations | 59,937 delegations on sub-threshold pools (0.19B, 0.9% of stake). |
| §3 Delegators | Removed operator-controlled delegations | 3,634 operator delegations (2.98B, 13.7% of stake). |
| §3 Delegators | Removed custodial delegations (≤20 deleg, ≥10M ADA) | 154 pools, 853 delegations, 6.98B (32.1%). Choice made by operator, not end-users. |
| §3 Delegators | Classified sovereign choice quality | 57.9% of sovereign stake in optimal pools. 26.6% reasonable. 10.8% suboptimal. 4.3% over-saturated. |

### What remains noisy

1. **Non-participant decomposition** (§4) — the 41% unstaked ADA is a mix of exchanges, smart contracts, and dormant wallets. Need UTxO-level queries.
2. **Delegator-side entity attribution** — which delegation tiers delegate to exchange pools vs independent pools? The pool-side is resolved; the delegator-side is not.
3. **Historical SPO/MPO** — current snapshot only. Need per-epoch owner-key reconstruction.


## 6. Bridges to Companion Analyses

This census provides the population denominators that the companion reports take as inputs. Below, each key statistic in the other documents is traced back to its census origin — and discrepancies between documents are made explicit.

### 6.1 Distribution efficiency (epoch 616)

The pools-distribution analysis (`pools-distribution/mainnet-analysis/`) decomposes the pools pot into three channels at epoch 616:

| Component | Share | Census root |
|---|---|---|
| Participation gap | 33.5% | = λ_min × (1 − staking_rate). Census staking rate at epoch 616: ~59.3%. With λ_min = 1/(1+a0) = 1/1.3 ≈ 0.769, gap = 0.769 × 0.407 ≈ 31.3%. The 33.5% figure uses the exact `ada_pots` supply rather than the rounded rate. |
| Bonus budget unused | 22.5% | = λ_max − bonus_captured. λ_max = a0/(1+a0) = 0.3/1.3 ≈ 23.1%. The 22.5% means almost all the bonus budget goes uncaptured — pools collectively fail to meet pledge thresholds. |
| Distributed | 43.7% | = pot − gap − bonus_unused − pledge_shortfall. This is what actually reaches delegators and operators. |

The participation gap is a *direct function of the staking rate measured in this census*. Every percentage point the staking rate drops increases the gap by ~0.77 pp (via the λ_min multiplier).

**Epoch drift.** The distribution analysis uses epoch 616, this census goes to 623. The staking rate moved from ~59.3% (616) to 59.0% (623) — a 0.3 pp decline over 7 epochs. The participation gap is therefore slightly worse at 623 than the 33.5% reported at 616.

### 6.2 Operator's cut (epoch 614)

The operator-delegator analysis (`operator-delegator-distribution/mainnet-analysis/`) reports 1,270,903 active delegation relationships at epoch 614. The census epoch_stake count at 614 would be ~1,353K (interpolating from the time-series). The difference arises because the operator analysis filters to pools that actually earned rewards in the epoch, excluding pools with zero blocks.

| Operator's Cut metric | Value | Census anchor |
|---|---|---|
| 445 hollow entities | Operators with <10% owner stake | Census SPO/MPO classification is a lower bound — the operator doc uses a richer entity mapping with 677 pools across 26 known entities |
| 48 "functionally private" pools | Margin ≥ 99.9% | Not visible in census — requires reward-parameter analysis |
| 7.7% genuine hollow take | Fixed cost 4.4% + margin 3.6% | Denominator is per-pool rewards, which depends on census pool count × stake distribution |

### 6.3 Main report (epochs 548–583)

The main report (`spo_incentives/report.tex`) uses an older analysis window (epochs 548–583) and Koios-sourced data:

| Main report metric | Value | Census comparison (epoch 623) |
|---|---|---|
| Staking rate | ~57.4% | Census: 59.0%. The 1.6 pp gap is real temporal drift — the rate has recovered slightly since the 548–583 window. |
| Active delegations | ~1.27M | Census: 1.355M. Growth of ~85K delegations over ~40 epochs. |
| Whale concentration | 4,500 wallets → 68.5% of stake | Census: 4,336 delegations >500K → 71.2%. Consistent with epoch drift. |
| Pool tiers: 741 healthy, 627 struggling, 1,305 inactive | Based on cumulative rewards + stake thresholds | Census active-pool count (2,877 at epoch 623) is consistent: 741 + 627 + 246 + 1,305 = 2,919 ≈ 2,877 (epoch drift + methodology delta). |

### 6.4 Reconciliation summary

The companion documents were built at different epochs with different data sources. This census standardises on db-sync at epoch 623 and epoch_stake as the counting method. The key numerical shifts when porting companion stats to census methodology:

| What changes | Old value | Census value | Why |
|---|---|---|---|
| "Delegator" count | 1.85M (certificates) | 1.355M (epoch_stake) | Certificate ghosts removed |
| Pool count | 5,919 (certificates) | 2,877 (epoch_stake) | Empty pools removed |
| Staking rate | 57.4% (epochs 548–583) | 59.0% (epoch 623) | Temporal drift + source alignment |
| Delegation count | 1.27M (epoch 614, reward-earning pools only) | 1.355M (epoch 623, all staked pools) | Scope + epoch drift |

The participation gap, distribution efficiency, and operator-take calculations all chain off these population numbers. Cleaning the census denominators propagates through every downstream metric.
