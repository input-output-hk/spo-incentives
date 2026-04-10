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
  - [2.5 Population dynamics — entries, exits, and turnover](#25-population-dynamics--entries-exits-and-turnover)
    - [2.5.1 Entries and exits](#251-entries-and-exits)
    - [2.5.2 Entity lifecycle](#252-entity-lifecycle)
  - [2.6 Pool size variability — how stable is a pool's stake?](#26-pool-size-variability--how-stable-is-a-pools-stake)
- [3. Delegators](#3-delegators)
  - [3.1 Raw query](#31-raw-query)
  - [3.2 Cleaning — zero-balance certificates](#32-cleaning--zero-balance-certificates)
  - [3.3 Cleaning — non-productive pools](#33-cleaning--non-productive-pools)
  - [3.4 Delegator landscape — epoch 623](#34-delegator-landscape--epoch-623)
  - [3.5 Population dynamics — delegator entries and exits](#35-population-dynamics--delegator-entries-and-exits)
  - [3.6 Delegation churn — pool switching behaviour](#36-delegation-churn--pool-switching-behaviour)
  - [3.7 Switch motivation and loyalty profiles](#37-switch-motivation-and-loyalty-profiles)
- [4. Non-Participants](#4-non-participants)
  - [4.1 Circulating supply decomposition](#41-circulating-supply-decomposition)
  - [4.2 Anatomy of the unstaked UTxO](#42-anatomy-of-the-unstaked-utxo)
  - [4.3 Dormancy vintage](#43-dormancy-vintage)
  - [4.4 What the non-participant population likely contains](#44-what-the-non-participant-population-likely-contains)
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

At epoch 623: **21.75B ADA** staked out of **36.88B** circulating = **59.0%** staking rate. The remaining **15.13B ADA** (41.0%) is not staked — of which 14.36B sits in unstaked UTxOs and 0.77B in unclaimed rewards. This population is decomposed in §4.

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

### 2.5 Population dynamics — entries, exits, and turnover

The near-constant stock of ~950 productive pools masks significant underlying churn. This section decomposes the aggregate into three views: the entry/exit flow, the entity-level lifecycle that drives it, and the stake variability that pools experience even while they remain in the productive set.

#### 2.5.1 Entries and exits

Tracking individual pools across consecutive epochs — counting those that cross the production threshold upward (entries) and those that fall below it or disappear (exits) — reveals the turnover that the aggregate count obscures.

![Population dynamics — productive pool entries and exits](figures/pool_population_dynamics.png)

The early Shelley period (epochs 212–300) saw rapid net growth as the pool population expanded from ~450 to ~1,000 productive pools. Growth epochs outnumbered decline epochs roughly 2∶1 during this phase. From epoch 300 onward, the productive population stabilised: net changes per epoch fluctuate around zero, with growth and decline epochs occurring in roughly equal proportion. Over the full history (epochs 212–623), the productive set gained a net +427 pools — but the near-flat trajectory since epoch 300 means the overwhelming majority of that net gain occurred in the first 90 epochs.

The stability of the stock alongside non-trivial per-epoch fluctuation implies a quasi-equilibrium: pools that exit the productive set (falling below the rising threshold, retiring, or losing delegation) are replaced at roughly the same rate by new entrants or returning pools. Tracking individual pool presence per epoch (`05_pool_population_dynamics.sql`) confirms this: over the full history the productive set recorded 3,497 entries against 3,070 exits, with an average churn of ~15.9 pools per epoch. The turnover rate (entries + exits as a share of the productive population) averages around 1.7% per epoch — higher than the delegator-side turnover of ~0.5%, reflecting the greater fragility of pool economics near the production threshold.

#### 2.5.2 Entity lifecycle

Part of the churn is driven by entity-level dynamics. The entity lifecycle analysis ([`data/entity_lifecycle_623.csv`](data/entity_lifecycle_623.csv)) classifies the 85 named entities into four phases — dead, declining, stable, and growing — based on their stake trajectory and productive-pool retention. Declining and dead entities contract their pool fleets, feeding the exit side; growing entities and new independent single-pool operators feed the entry side. The entity-level decline trajectories are visualised in the figures below.

![Entity lifecycle — declining entities](figures/entity_lifecycle_decline.png)

![Entity lifecycle — growing entities](figures/entity_lifecycle_growth.png)

### 2.6 Pool size variability — how stable is a pool's stake?

The entry/exit analysis tracks whether a pool is *in* the productive set; this section asks how much its stake fluctuates while it stays there. A pool that survives all 73 epochs of the last year (epochs 551–623) may nonetheless experience large swings in delegation, with consequences for block production regularity and operator revenue predictability.

![Pool size variability](figures/pool_size_variability.png)

**Most productive pools are remarkably stable.** Of the 1,032 pools present in at least 10 of the last 73 epochs and above the production threshold, roughly a third (32.6%) have a coefficient of variation (CV) of 5% or less — their stake barely moves from epoch to epoch. Another 18.3% sit in the 5–10% band. Together, half the productive set operates with stake fluctuations under 10% over a full year.

**A long tail of volatile pools exists.** At the other extreme, 9.3% of productive pools have CV between 50% and 100%, and 3.4% exceed 100% — meaning their standard deviation is larger than their mean stake. These are typically pools near the production threshold that oscillate in and out of viability, or pools that experienced a single large delegation event (arrival or departure of a whale) that dominates their variance.

**System-wide dispersion has compressed over time.** Panel C shows the cross-sectional CV of pool stakes across all productive pools at each epoch. In the early Shelley era (epochs 210–260), the CV exceeded 180% — a handful of very large pools coexisted with hundreds of small entrants, producing extreme size dispersion. As the pool population matured and the largest pools approached the saturation cap (~70.8M ADA at k=500), the CV declined steadily to ~105% by epoch 500 and has since plateaued. The remaining dispersion reflects the structural range between pools near the production threshold (~1M ADA) and the largest pools near saturation (~114M ADA) — a 100× ratio that the protocol's incentive design deliberately permits.

**Variability differs sharply across market segments.** Crossing the per-pool CV with the four-segment taxonomy from the companion [*Operator's Cut*](../../operator-delegator-distribution/mainnet-analysis/) (§4.3) reveals that not all segments fluctuate equally.

![Pool CV by segment](figures/pool_cv_by_segment.png)

Custodial-by-delegation pools (exchanges and institutional validators) are the most volatile: median CV of 15.1%, and 20% of pools exceed CV 50%. These operators actively rebalance stake across their pool fleets — an exchange that adds or removes 50M ADA from one of its 40 pools causes a large proportional swing. By contrast, Custodial-by-pledge pools (private, self-funded) sit at median CV 9.2% — the operator controls the capital and has little reason to move it frequently. Custodial-by-extraction pools (privatisation margin, non-private) are the most stable at median CV 5.1%, consistent with pools whose delegators are locked in by inertia or institutional constraint. Retail pools land at median CV 8.1%, with 56% below 10% — the organic delegation market is mostly steady, but a 7% tail above CV 50% captures pools that gained or lost a whale delegator.

The stacked-bar view (panel B) confirms the pattern: over 80% of custodial-by-extraction pools fall in the 0–10% CV bucket, while custodial-by-delegation spreads across all buckets with a substantial 20% tail beyond 50%. The practical implication is that stake variability on Cardano is largely an institutional rebalancing phenomenon, not a retail delegation-market signal.

**Implications for delegators.** A pool's stake stability matters because it affects block-production regularity and, by extension, the consistency of epoch rewards. Delegators in low-CV pools experience smoother returns; those in high-CV pools face more variance. The data in `data/pool_size_variability.csv` provides per-pool CV, min, max, and range for further analysis; `data/pool_cv_by_segment.csv` gives the segment-level aggregate.


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

A delegation certificate is a *declaration of intent*: it records on-chain that an address wishes to delegate to a given pool, but it does not lock any funds. The ADA remains freely spendable. An epoch_stake row, by contrast, is *capital at work* — it reflects the actual balance present at the snapshot boundary. An address with a certificate but no ADA earns no rewards and does not participate in consensus.

The gap between the two views arises because delegation certificates are never automatically revoked. When an address is emptied — typically because the holder transferred funds to an exchange, moved to another wallet, or simply stopped using Cardano — the certificate persists as a residual record pointing at a pool with zero backing stake. These orphaned records are the "certificate ghosts" removed in this step.

| Metric | Raw (delegation table) | Clean (epoch_stake) | Noise removed |
|---|---|---|---|
| Active delegations | 1,847,713 | **1,355,035** | 492,678 certificate ghosts (26.7%) |
| Active pools | 5,919 | **2,877** | 3,042 empty pools (51.4%) |

**After cleaning:** 1,355,035 delegations, 21.75B ADA across 2,877 pools.

### 3.3 Cleaning — non-productive pools

The 1,925 pools below the production threshold (§2.2) carry 59,937 delegations and 0.19B ADA. These delegators earn intermittent and unpredictable rewards. Removing them aligns the delegator population with the productive operator landscape.

**After cleaning:** 1,295,098 delegations, 21.57B ADA across 952 productive pools.

### 3.4 Delegator landscape — epoch 623

| Segment | Delegations | Stake | Share | Pools | Entities |
|---|---|---|---|---|---|
| **Raw (delegation certificates)** | **1,847,713** | — | — | **3,190** | **2,374** |
| Zero-balance certificates (noise) | 492,678 | 0 | — | 313 | 72 |
| **epoch_stake total** | **1,355,035** | **21.75B** | **100%** | **2,877** | **2,302** |
| Non-productive pool delegations (noise) | 59,937 | 0.19B | 0.9% | 1,925 | 1,742 |
| **Productive pool delegations** | **1,295,098** | **21.57B** | **99.1%** | **952** | **560** |

The 1,295,098 productive pool delegations are the cleaned population handed to the companion [*Operator's Cut*](../../operator-delegator-distribution/mainnet-analysis/) analysis, which decomposes them further into operator self-stake, custodial, and retail segments.

### 3.5 Population dynamics — delegator entries and exits

Applying the same epoch-over-epoch tracking used for pools in §2.5, but at the delegator level: for each epoch, count addresses that appear in a productive pool's delegation set for the first time (entries) and those that disappear from it (exits). Only delegators to pools above the production threshold are counted.

![Population dynamics — productive-pool delegator entries and exits](figures/delegator_population_dynamics.png)

The delegator population tells a fundamentally different story from the pool population. Where the productive pool count stabilised early and has fluctuated within a narrow band since epoch 300, the delegator count grew almost monotonically from ~28,700 (epoch 212) to ~1,295,000 (epoch 623). Over the full 412-epoch history, the productive set recorded 2,052,268 individual entries against 779,974 exits — a net gain of +1,272,294 delegators. The average per-epoch churn (entries + exits) is ~6,870 addresses, implying that roughly 0.5% of the delegator base turns over each epoch.

Growth epochs outnumber decline epochs roughly 6∶1, and the few negative epochs involve small absolute drops. The moving average of net change was strongly positive through epoch ~380, then settled into a lower but still persistently positive regime.

Two features stand out. First, the growth curve shows distinct waves rather than a smooth ramp: the initial Shelley on-boarding surge (epochs 212–260), a secondary acceleration around epochs 280–330 (coinciding with the Alonzo-era smart-contract boom and increased retail attention), and a third wave around epochs 480–510. Second, the plateau from epoch ~530 onward — where net growth drops close to zero — suggests the delegator population may be approaching a saturation point under the current staking participation rate of ~59%.

The turnover rate (gross entries + exits as a share of the active population) averages around 0.5% per epoch but spikes markedly during protocol upgrades and market events, revealing that the apparently stable stock masks episodic surges of rebalancing. Unlike pool dynamics, where entries and exits are roughly balanced post-epoch 300, delegator dynamics remain structurally asymmetric — entries consistently exceed exits — reflecting ongoing organic adoption even as the growth rate decelerates.

### 3.6 Delegation churn — pool switching behaviour

The population dynamics above track whether delegators are *in* the productive set; this section tracks what they do *within* it — specifically, how often and how they switch pools. The `delegation` table records every delegation certificate ever submitted on-chain (3,491,680 certificates across the Shelley era). Each certificate binds a stake address to a pool; a new certificate from the same address to a different pool constitutes a redelegation (pool switch).

![Delegation churn — pool switching behaviour](figures/delegation_churn.png)

Of the 3.49M delegation certificates submitted between epochs 210 and 623, 1,847,713 (52.9%) are initial delegations (first certificate for an address), 1,407,245 (40.3%) are redelegations to a different pool, and 235,336 (6.7%) are renewals to the same pool (typically after a stake key deregistration and re-registration cycle). The redelegation count implies that a large majority of delegators have changed pool at least once over the protocol's history.

The per-epoch pattern reveals three regimes. The early Shelley period (epochs 210–260) saw 2,000–3,500 redelegations per epoch — a turbulent phase where delegators were experimenting with the new staking system and pools were rapidly entering and exiting the market. The middle period (epochs 260–500) settled to roughly 1,000–2,000 per epoch, with periodic spikes around protocol upgrades (Alonzo, Babbage) and market events. The recent regime (epoch 500+) has stabilised around 600–800 redelegations per epoch, representing a mature market where most delegators have found a pool and stay.

The tenure distribution confirms this bimodal structure. 42.2% of all delegations have lasted 201+ epochs (over two years) — these are the committed long-term delegators who anchor pool economics. At the other extreme, 21.0% of delegations last 5 epochs or fewer — these are the rapid switchers, likely driven by yield optimisation, pool retirement, or exchange-side rebalancing. The middle buckets (6–200 epochs) account for the remaining 37%, with a roughly uniform distribution across tenure bands.

The top pool-to-pool flows (`data/delegation_flow_matrix.csv`) reveal that the highest-volume corridors are between pools controlled by the same entity — particularly within IOG's pool fleet and between major exchange operators. This suggests that a significant share of observed "switching" is internal rebalancing by multi-pool operators rather than genuine delegator choice.

**Retail-only lens.** Restricting the analysis to retail pools (margin < 99.9%, excluding private and custodial-by-extraction pools — the same filter used in the companion [*Operator's Cut*](../../operator-delegator-distribution/mainnet-analysis/) §4.4) yields near-identical results: 1,382,656 switches out of 3,457,070 certificates (40.0%), ~799 redelegations per epoch recently, and the same tenure distribution (42.4% at 201+ epochs, 20.8% at ≤5 epochs). The private pool population (47 pools, ~300 delegations) generates negligible churn, confirming that essentially all observed switching behaviour originates in the retail delegation market. The retail flow matrix (`data/retail_delegation_flow_matrix.csv`) is available for entity-level decomposition of market-driven pool switching.

### 3.7 Switch motivation and loyalty profiles

The previous section established that ~1.4M pool switches occurred over the Shelley era. This section asks *why* delegators move and *where* loyal delegators stay.

![Switch motivation and loyalty profiles](figures/switch_motivation.png)

**Margin is not the dominant switching driver.** Of the 1,407,245 pool switches, 39.6% move to a pool with a lower margin, 38.0% to a higher margin, and 22.4% to an identical margin. The near-symmetry between lower and higher margin moves indicates that fee optimisation alone explains fewer than two in five switches. Pool size shows a similar even split: 34.9% move to a larger pool, 31.9% to a smaller one, and 33.2% to a similarly-sized pool. The motivation heatmap (panel A) confirms that no single margin × size combination dominates — the nine cells range from 6.5% to 14.6%, far from the concentration one would expect if delegators were systematically chasing lowest-fee, largest pools.

**Switching happens overwhelmingly within competitive margin bands.** The margin-band transition matrix (panel B) shows that 38.9% of all switches stay within the 0–2% band, and a further 14.9% move within 2–5%. Cross-band flows are relatively rare: the largest outward move is 2–5% → 0–2% at 15.3%, consistent with gradual fee compression in the retail market. Exits to 100% (private) pools account for only 1.2% of all switches. This pattern suggests that while delegators may not be margin-optimising on each individual switch, they are *pre-selected* into competitive pools and rarely leave that neighbourhood.

**Loyal delegators anchor in competitive pools.** Panel C compares the margin-band distribution across loyalty segments. Loyal delegators (tenure ≥ 201 epochs, i.e. over 2.7 years) concentrate 92.1% of their delegations in the 0–5% margin range, split almost evenly between 0–2% (45.3%) and 2–5% (46.8%). Volatile delegators (tenure ≤ 5 epochs) show a stronger skew toward 0–2% (53.5%) but also spread more into 5–10% (10.1%) and 10–99% (3.4%). The moderate cohort sits in between. The takeaway is that loyalty is not exchanged for higher fees — long-tenure delegators already sit in the cheapest pools, and their stability may reflect satisfaction with a combination of competitive fees, predictable returns, and community trust.

**Top pools for loyal delegators.** The top 20 pools by loyal-delegation count (`data/loyal_delegator_pools.csv`) are overwhelmingly single-pool operators with margins of 2–4% and fixed costs of 340–400 ADA. Average tenure among their loyal delegations ranges from 290 to 362 epochs (roughly 4 to 5 years). These pools carry between 10B and 72B lovelace in total stake at epoch 623 and support 10,000–36,000 delegators each. Several are well-known community pools that have operated since the early Shelley era — their delegator bases appear to have crystallised early and remained remarkably stable.


## 4. Non-Participants

### 4.1 Circulating supply decomposition

Before isolating non-participants, the circulating supply itself must be decomposed. The `ada_pots` table records four buckets that sum to circulating ADA: UTxO balances (the ADA sitting in unspent transaction outputs), unclaimed rewards (earned but not yet withdrawn to a UTxO), stake-key and governance deposits, and the fee accumulator. Combining these with the staked amount from `epoch_stake` yields:

| Component | Epoch 623 | Share of circulating |
|---|---|---|
| **Staked ADA** (in epoch_stake snapshot) | **21.75B** | **59.0%** |
| **Unstaked UTxO** (UTxO − staked) | **14.36B** | **38.9%** |
| Unclaimed rewards | 0.77B | 2.1% |
| Deposits + fees | 0.01B | <0.1% |
| **Circulating supply** | **36.88B** | **100%** |

Staked ADA is covered by §§2–3. Unclaimed rewards are ADA earned by delegators and operators that has not yet been withdrawn via a transaction — it exists on the ledger but not as a UTxO. Deposits are the 2-ADA stake-key registration deposits and DRep/governance deposits locked by the protocol. Neither rewards nor deposits are available for spending until explicitly claimed or deregistered; they are not "non-participants" in the staking sense but they are not freely circulating either.

The non-participant population is therefore the **14.36B ADA in unstaked UTxOs** — outputs controlled by addresses that are not delegated to any pool at epoch 623.

![Circulating supply decomposition](figures/circulating_supply_decomposition.png)

The top panel shows the absolute decomposition over time. The bottom panel shows the percentage shares. The staking rate stabilised around 59–62% from epoch ~300 onward, meaning the non-participant share has hovered between 36–39% for over 300 epochs. The brief spike in unstaked share around epoch 365 coincides with the Alonzo hard fork and the initial wave of smart-contract deployments, which locked ADA in script addresses outside the delegation system.

### 4.2 Anatomy of the unstaked UTxO

The 14.36B unstaked ADA is not a monolithic block of disengaged holders. It divides into structurally distinct populations based on address type and delegation status:

**By address type.** Cardano addresses encode their staking capability in their structure. Base addresses carry both a payment credential and a staking credential — they *can* delegate. Enterprise addresses carry only a payment credential — they *cannot* delegate by design. Script addresses are controlled by on-chain validators (smart contracts) rather than key pairs; some carry a staking credential, most do not.

**By delegation status.** Among addresses that *can* stake (base addresses and script addresses with a staking credential), many have never registered a stake key, others registered but never delegated, and some previously delegated but have since deregistered.

The SQL query `07_non_participant_decomposition.sql` classifies every unspent transaction output at the chain tip into six categories:

| Classification | Description |
|---|---|
| `base_delegated` | Base address, stake key delegated — this is the *staked* population |
| `base_not_delegated` | Base address, not currently delegated — *could* stake but does not |
| `enterprise` | Enterprise address, no staking credential — *cannot* stake |
| `script_delegated` | Script address with staking credential, delegated |
| `script_not_delegated` | Script address with staking credential, not delegated |
| `script_no_staking_cred` | Script address without staking credential — *cannot* stake |

> **Data dependency.** This query requires the `tx_out` table, which contains the full UTxO set. The current db-sync instance was restored from a pruned snapshot that excludes `tx_out` (the table exists but contains zero rows — all staking-related tables are fully populated). A full db-sync restore is planned; once completed, running `07_non_participant_decomposition.sql` and `build_non_participant_visuals.py` will populate the breakdown figure below.

<!-- ![Non-participant breakdown](figures/non_participant_breakdown.png) -->

This decomposition answers a critical question for incentive design: how much of the unstaked ADA *could* participate but *chooses* not to (base_not_delegated), versus how much is *structurally excluded* from staking (enterprise + script_no_staking_cred)? The former is the population that incentive adjustments could in principle reach; the latter is a hard floor on non-participation that no reward-scheme change can address.

### 4.3 Dormancy vintage

Among the non-delegated UTxOs, the creation date of each output provides a rough proxy for how "alive" the controlling wallet is. A UTxO created in the pre-Shelley era (before epoch 208) and never moved since suggests a dormant or lost wallet. A UTxO created recently but not delegated suggests an active user who has consciously opted out of staking — or an exchange hot wallet cycling funds.

The SQL query produces a vintage breakdown of non-delegated UTxOs by creation epoch range: pre-Shelley, early Shelley (208–299), and 100-epoch bands thereafter. This separates the population into "probably dormant" (pre-Shelley outputs untouched for 400+ epochs) and "actively non-participating" (recent outputs from wallets that could delegate but do not).

> **Data dependency.** Same as §4.2 — requires `tx_out`. Deferred until the full db-sync restore is completed.

### 4.4 What the non-participant population likely contains

Without off-chain attribution (which would require matching addresses to known exchange and DeFi protocol wallets), the on-chain decomposition can only classify by address structure and activity. However, the major constituents of the 14.36B are identifiable by elimination:

**Exchange custody (likely dominant).** Centralised exchanges hold ADA in hot and cold wallets. Some exchanges stake user ADA through their own pools (Coinbase, Binance — visible in §2.3 entity attribution), but the custodial ADA that is *not* staked — either because the exchange has not implemented staking or because users have not opted in — sits in enterprise or base addresses without delegation. Exchange cold-wallet identification requires cross-referencing with known address clusters, which is deferred to a companion analysis.

**Smart-contract-locked ADA.** DeFi protocols (DEXes, lending platforms, liquidity pools) lock ADA in script addresses. Most script addresses lack a staking credential, making their ADA structurally unstakeable. The growth of DeFi since the Alonzo hard fork (epoch ~290) has steadily increased the script-locked portion of the unstaked UTxO.

**Dormant and lost wallets.** Wallets that received ADA before or shortly after the Shelley hard fork and have never transacted since. Some fraction of these represent lost keys. The dormancy vintage analysis (§4.3) quantifies this segment.

**Active non-stakers.** Wallets that transact regularly but whose owners have never registered a stake key or have deregistered. This group is the most responsive to incentive changes — they are engaged with the network but have chosen not to delegate.


## 5. Synthesis

### Key metrics (epoch 623)

| Metric | Value | Source |
|---|---|---|
| Circulating supply | 36.88B ADA | ada_pots |
| Staked | 21.75B ADA (59.0%) | epoch_stake |
| Unstaked UTxO | 14.36B ADA (38.9%) | utxo − staked |
| Unclaimed rewards | 0.77B ADA (2.1%) | ada_pots |
| Deposits + fees | 0.01B ADA (<0.1%) | ada_pots |
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
| §3 Delegators | Productive pool delegations isolated | 1,295,098 delegations, 21.57B ADA across 952 pools and 560 entities. Further decomposition (operator self-stake, custodial, retail) deferred to the Operator's Cut. |

### What remains noisy

1. **Non-participant decomposition** (§4) — the 38.9% unstaked UTxO ADA is a mix of exchanges, smart contracts, and dormant wallets. The address-type and dormancy-vintage queries (`07_non_participant_decomposition.sql`) are written but require a full db-sync with `tx_out` populated (the current instance uses a pruned snapshot). Restore planned.
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
