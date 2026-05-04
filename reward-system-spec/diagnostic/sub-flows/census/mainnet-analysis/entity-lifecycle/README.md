# Entity Lifecycle — Growth, Decline, and Exit on Cardano Mainnet

This sub-document of [*The Staking Census*](../README.md) adds the **temporal dimension** to the operator landscape — which identified entities have contracted, which have exited entirely, and what patterns of decline are visible across archetypes. *Where the census itself is a snapshot of who is on the field at epoch 623, this document tracks how the snapshot was made.*

The analysis follows the **85 identified entities** attributed in the census from their first appearance in `epoch_stake` through epoch 623, classifying each into a lifecycle phase based on the ratio between current stake and all-time peak (dead, severe decline, decline, stable, growing).

**Roughly half of identified operators are past their peak and contracting.** The lifecycle classification places **42 of 85 entities** in the dead or declining segments. **Two are dead** (current stake below the production threshold), **11 are in severe decline** (< 25% of peak — collectively shed **8.4B ADA**), and **29 are in moderate decline** (25–50% of peak). The largest individual exits include **IOG** (2.67B → 11.7M, completed steward withdrawal), **Binance** (2.98B → 692M, exchange retreat), and **1PCT** (1.27B → 275M, independent fleet erosion). *Community-branded fleets dominate the declining segment — the median decline ratio in this archetype is ~38%, with no single event explaining the slow, persistent outflow of delegations.*

**The capital did not leave the staking ecosystem; it restructured.** The declining and dead entities collectively shed **~14.6B ADA** from their peaks, but total staked ADA grew from **~12B to ~21.8B** over the same period. The redistribution flowed along three channels: **toward institutional validators** (Figment, Blockdaemon, Everstake, Kiln together hold **2.7B**, almost all accumulated after epoch 300); **toward late-arriving exchanges** (Coinbase entered at epoch 296 and grew to **2.6B**, Upbit entered at epoch 398 and is at all-time high); and **toward the single-pool operator tail** (the 284 unattributed single-pool operators hold **5.28B ADA**, consistent with the community's cultural preference for single-pool delegation).

**The growth pattern selects for late entrants and persistence.** **18 entities** are at or near their all-time peak. Five late institutional entrants alone (Coinbase, Figment, Blockdaemon, Everstake, Upbit) hold **5.0B ADA — more than the entire single-pool operator segment**. Among community operators, the few that grew against the tide share a pattern of **late peaks (epoch 450–623)** rather than the early-Shelley peaks characteristic of declining peers — suggesting that *persistence and operational quality matter more than first-mover advantage in the long run*.

*The staking ecosystem is not shrinking — it is restructuring*, and the structural shift since epoch 300 has been from community-run fleets toward institutional staking infrastructure.

## Table of Contents

- [Data sources](#data-sources)
- [1. Lifecycle classification](#1-lifecycle-classification)
- [2. Dead entities](#2-dead-entities)
  - [2.1. RockX](#21-rockx)
  - [2.2. RAID](#22-raid)
- [3. Severe decline — the large exits](#3-severe-decline-the-large-exits)
  - [3.1. IOG — steward withdrawal](#31-iog-steward-withdrawal)
  - [3.2. Binance — exchange retreat](#32-binance-exchange-retreat)
  - [3.3. 1PCT — independent fleet erosion](#33-1pct-independent-fleet-erosion)
  - [3.4. AdaOcean, HOPE, BCSH, COOL](#34-adaocean-hope-bcsh-cool)
- [4. Moderate decline — the long bleed](#4-moderate-decline-the-long-bleed)
- [5. Growing entities — the capital recipients](#5-growing-entities-the-capital-recipients)
  - [5.1. Late institutional entrants](#51-late-institutional-entrants)
  - [5.2. Exchanges holding ground](#52-exchanges-holding-ground)
  - [5.3. Community operators that grew against the tide](#53-community-operators-that-grew-against-the-tide)
- [6. Stable entities — the plateau](#6-stable-entities-the-plateau)
- [7. Where the capital went](#7-where-the-capital-went)
- [8. Visual summary](#8-visual-summary)


## Data sources

| File | Content |
|---|---|
| `data/entity_stake_history.csv` | Per-entity, per-epoch: active pools, total stake, delegation count (output of `04_entity_stake_history.sql`) |
| `data/entity_lifecycle_623.csv` | Per-entity lifecycle metrics: peak, current, decline ratio, phase classification (output of `build_entity_lifecycle_visual.py`) |
| `data/mpo_entity_archetypes.csv` | Entity-to-archetype mapping |


## 1. Lifecycle classification

Each entity is classified into a **lifecycle phase** by comparing its **current stake** (epoch 623) to its **all-time peak**:

| Phase | Rule | Entities | Combined peak | Combined current |
|---|---|---|---|---|
| **Dead** | Current stake below production threshold (~3M ADA) | 2 | 46M | 0.6M |
| **Declining (severe)** | Current < 25% of peak | 11 | 9,938M | 1,524M |
| **Declining** | Current 25–50% of peak | 29 | 8,445M | 3,207M |
| **Stable** | Current 50–90% of peak | 25 | — | — |
| **Growing** | Current > 90% of peak | 18 | — | — |

The declining and dead segments together account for **42 of 85 entities** — *roughly half of all identified operators are past their peak and contracting*.

The capital they have lost has not vanished: it **migrated to growing entities** (exchanges entering late, IVaaS providers scaling up) or **dispersed into the single-pool operator tail**.


## 2. Dead entities

**Two entities** have fallen below the production threshold across all their pools and no longer participate meaningfully in block production.

### 2.1. RockX

| Metric | Value |
|---|---|
| Archetype | Institutional Validator |
| Pools registered | 10 |
| Peak stake | 37.6M ADA (epoch 481) |
| Current stake | 0.2M ADA |
| Decline ratio | 0.52% of peak |

RockX is a **multi-chain institutional staking provider** (Ethereum, Cosmos, Solana, and others). Its Cardano presence was **never large** — 10 pools registered between epochs 450 and 500, peaking at **37.6M ADA** across a handful of active pools.

Stake drained steadily after the peak, consistent with a **strategic withdrawal** from Cardano rather than organic delegation loss. All 10 pools are now below the production threshold. The entity's infrastructure appears to **remain registered but economically inert**.

### 2.2. RAID

| Metric | Value |
|---|---|
| Archetype | Independent MPO |
| Pools registered | 7 |
| Peak stake | 8.5M ADA (epoch 210) |
| Current stake | 0.4M ADA |
| Decline ratio | 4.79% of peak |

RAID is **one of the earliest multi-pool operators**, active from the Shelley launch (epoch 210). Its peak was **modest** — **8.5M ADA** spread over 7 pools — and erosion began **almost immediately**.

By epoch 300 its stake was already marginal. The entity **never scaled** and appears to have been an **early experiment** that was **quietly abandoned** rather than formally deregistered.


## 3. Severe decline — the large exits

**Eleven entities** have lost **more than 75%** of their peak stake. Together they shed **8.4B ADA** — a **substantial redistribution of capital** away from early and mid-era operators.

### 3.1. IOG — steward withdrawal

| Metric | Value |
|---|---|
| Archetype | Ecosystem Steward |
| Pools registered | 65 |
| Peak stake | 2,670M ADA (epoch 223) |
| Current stake | 11.7M ADA |
| Decline ratio | 0.44% of peak |

Input Output's delegation was a **bootstrapping mechanism**: IOG ran ~20 pools in early Shelley to **seed the network** and incentivise participation.

The withdrawal was **deliberate and public** — IOG progressively redelegated its stake to community pools as the ecosystem matured. The **65 registered pools** are nearly all **legacy registrations**; only **2 are productive** at epoch 623.

*This is not a failure but a completed lifecycle: the steward exited once the network no longer needed bootstrapping support.*

### 3.2. Binance — exchange retreat

| Metric | Value |
|---|---|
| Archetype | Exchange Custody |
| Pools registered | 114 |
| Peak stake | 2,981M ADA (epoch 337) |
| Current stake | 692M ADA |
| Decline ratio | 23.2% of peak |

Binance's Cardano staking peaked around epoch 337 at **nearly 3B ADA** — roughly **14% of the entire staked supply** at the time.

The decline has been **continuous** and is consistent with **two overlapping forces**:

- users **withdrawing ADA from the exchange** (general crypto exchange outflow trend);
- Binance potentially **rebalancing its Cardano staking product**.

The **114 registered pools** (only **20 productive**) suggest **aggressive pool scaling** during the growth phase followed by **no deregistration cleanup**. The entity retains **692M ADA** — still the **second-largest identified entity** by stake.

### 3.3. 1PCT — independent fleet erosion

| Metric | Value |
|---|---|
| Archetype | Independent MPO |
| Pools registered | 30 |
| Peak stake | 1,268M ADA (epoch 222) |
| Current stake | 275M ADA |
| Decline ratio | 21.7% of peak |

1PCT (One Percent Pool) was among the **largest independent multi-pool operators** in early Shelley, competing directly with IOG pools for delegations.

Its decline mirrors the **broader pattern** of early large fleets **losing share** to later entrants and to the growing single-pool operator segment. The decline was **steady rather than abrupt**, suggesting **gradual delegation churn** rather than a single event.

### 3.4. AdaOcean, HOPE, BCSH, COOL

These four entities share a **similar profile**: mid-size independent or community fleets that peaked between epoch 220 and 330 and have since **lost 75–85%** of their stake.

Each held **400–800M ADA** at peak; all now sit between **68M and 188M**. The common pattern is a **rapid growth phase** during early Shelley, a **plateau** during the k=500 expansion, and a **steady bleed** thereafter. *None show signs of active growth or strategic repositioning.*

| Entity | Archetype | Peak | Current | Decline |
|---|---|---|---|---|
| AdaOcean | Independent MPO | 801M (e228) | 188M | 23.4% |
| HOPE | Multi-Brand Fleet | 487M (e231) | 78M | 16.1% |
| BCSH | Community Branded Fleet | 466M (e319) | 69M | 14.7% |
| COOL | Multi-Brand Fleet | 378M (e222) | 86M | 22.8% |


## 4. Moderate decline — the long bleed

**Twenty-nine entities** retain between **25% and 50%** of their peak stake. This is the **largest lifecycle segment** and includes **almost every archetype**:

**Ecosystem stewards:** Emurgo (872M peak → 271M, −69%), the second founding entity after IOG. Unlike IOG's deliberate exit, Emurgo's decline appears to be a mix of strategic pool consolidation and organic delegation loss.

**Exchange custody:** YUTA (1,712M peak → 459M, −73%) — a Japanese exchange/custody entity whose decline is gradual and consistent with exchange-level outflows.

**Platform/wallet:** NuFi (927M peak → 313M, −66%) — a wallet and staking platform whose decline tracks the broader wallet-switching trend as users migrated between wallet providers.

**Community branded fleets:** This archetype **dominates the declining segment**. SPS, SIPO, NEDS, ONYX, RETIR, XSP, CNODE, STSH, ATLAS, STI, KAIZN, SUNNY, 4ADA, ELITE, and others — all community-run multi-pool operators that **grew during the Shelley expansion** and have been **losing delegators steadily**.

The median decline ratio for community branded fleets in this segment is **~38%**. The pattern is **remarkably uniform**: *no single event explains the decline, just a slow, persistent outflow of delegations.*

**Protocol/DeFi projects:** XRAY (in severe decline at 15.5% of peak) and DNEWS, Liqwid — projects that attracted delegations tied to token rewards or community incentive programs that have since wound down.


## 5. Growing entities — the capital recipients

**Eighteen entities** are at or near their all-time peak (current stake > 90% of peak). They collectively control **over 6.2B ADA** — and their growth trajectories **explain where much of the capital lost by declining entities has gone**.

### 5.1. Late institutional entrants

The most striking growth stories belong to entities that **entered Cardano staking well after the Shelley launch** and scaled rapidly through **institutional capital**:

| Entity | Archetype | First epoch | Peak | Current | Note |
|---|---|---|---|---|---|
| Coinbase / bison.run | Exchange Custody | e296 | 2,601M (e390) | 2,376M | Largest identified entity; slight contraction from peak but still growing class |
| Figment | Institutional Validator (IVaaS) | e322 | 883M (e622) | 878M | Near all-time high; pure IVaaS growth — entered mid-era, scaled steadily |
| Blockdaemon | Institutional Validator (IVaaS) | e267 | 614M (e622) | 613M | At peak; institutional staking infrastructure provider |
| Everstake | Institutional Validator (IVaaS) | e210 | 572M (e623) | 572M | At all-time high; one of the earliest IVaaS to enter Cardano, still growing |
| Upbit | Exchange Custody | e398 | 575M (e623) | 575M | At all-time high; Korean exchange, entered late, still scaling |

These **five entities alone** hold **5.0B ADA** — *more than the entire single-pool operator segment (5.28B)*.

Their arrival and growth **post-epoch 300** represents a **structural shift** in the operator landscape from **community-run fleets** toward **institutional staking infrastructure**.

### 5.2. Exchanges holding ground

**Coinbase and Upbit contrast sharply with Binance's retreat.** Coinbase entered at epoch 296, grew aggressively to **2.6B ADA** by epoch 390, and has held most of that position since — the slight decline is well within the "growing" band.

Upbit is a **pure late entrant** (epoch 398) still at its all-time high. The divergence between **growing exchanges** (Coinbase, Upbit) and **declining ones** (Binance, YUTA, eToro) appears to track each exchange's **strategic commitment to Cardano staking as a product line** rather than any protocol-level factor.

### 5.3. Community operators that grew against the tide

Several community branded fleets have defied the archetype's general decline:

| Entity | First epoch | Peak | Current | Decline ratio |
|---|---|---|---|---|
| ADV | e210 | 264M (e619) | 260M | 98.7% |
| TITAN | e210 | 147M (e601) | 136M | 92.8% |
| PILOT | e234 | 98M (e470) | 92M | 93.5% |
| CAFE | e215 | 88M (e454) | 82M | 93.3% |
| MUEN | e266 | 34M (e623) | 34M | 100% |

**ADV is the standout**: a Shelley-launch operator that peaked **just four epochs ago** and remains **essentially at its maximum**.

These entities share a pattern of **late peaks (epoch 450–623)** rather than the early-Shelley peaks characteristic of declining community fleets, suggesting they attracted **second-wave delegators** or **successfully retained existing ones** while peers bled.

**CHUCK BUX** (883M, peak at epoch 620) is classified as growing but its archetype is **"opaque / unresolved"** — the entity structure is **unclear** and the growth pattern is **atypical**, making it difficult to draw structural conclusions.


## 6. Stable entities — the plateau

**Twenty-five entities** hold between **50% and 90%** of their peak stake. This is the **second-largest lifecycle segment** and contains **several notable names**:

| Entity | Archetype | Peak | Current | Ratio |
|---|---|---|---|---|
| Kiln | Institutional Validator | 753M (e615) | 633M | 84.0% |
| Wave / Wavepool | Independent MPO | 999M (e332) | 613M | 61.4% |
| eToro | Exchange Custody | 706M (e260) | 472M | 66.9% |
| Cardano Foundation | Ecosystem Steward | 456M (e617) | 396M | 86.7% |
| SECUR | Community Branded Fleet | 309M (e480) | 231M | 74.9% |

**Kiln** and the **Cardano Foundation** are **recent entrants with late peaks** — their "stable" classification reflects a **slight pullback** from a recent high rather than a long decline.

**Wave/Wavepool** and **eToro**, by contrast, peaked early and have settled into a **slow erosion pattern** that has **not yet crossed the 50% threshold**. The stable phase may be a **waypoint toward decline** for some and a **consolidation plateau** for others — *the trajectory over the next 50–100 epochs will reveal which*.


## 7. Where the capital went

The declining and dead entities collectively shed **approximately 14.6B ADA** from their peaks (**9.9B** severe decline + **5.2B** moderate decline).

This capital **did not leave the staking ecosystem** — the total staked ADA has grown from **~12B to ~21.8B** over the same period. The capital redistributed along **three channels**:

**Toward institutional validators (IVaaS).** Figment, Blockdaemon, Everstake, and Kiln together hold **2.7B ADA**, almost all of it accumulated **after epoch 300**. This capital came partly from **exchanges reducing their staking exposure** and partly from **delegators seeking professional, multi-chain infrastructure**.

**Toward late-arriving exchanges.** Coinbase and Upbit entered **after most community fleets had already peaked**. They attracted **fresh capital** (ADA flowing onto exchanges for the first time) and captured some of the delegation that might otherwise have gone to established community operators.

**Toward the single-pool operator tail.** The **284 unattributed single-pool operators** hold **5.28B ADA** at epoch 623. While the census cannot track this segment historically (individual single-pool operators are not attributed), the growth of total staked ADA alongside the decline of identified multi-pool entities implies that a **significant portion** of the redistributed capital flowed into the long tail. This is consistent with the Cardano community's **strong cultural preference for single-pool delegation**.

> **Observation:** *the staking ecosystem is not shrinking — it is restructuring.*

Capital is moving from **early community fleets** and **retreating exchanges** toward **institutional infrastructure** and the **single-pool operator segment**. The entities that are growing tend to be either **late institutional entrants** with professional infrastructure or **community operators that peaked late**, suggesting that **persistence and operational quality matter more than first-mover advantage** in the long run.


## 8. Visual summary

### Declining and dead entities

![Entity lifecycle — declining and dead entities](../figures/entity_lifecycle_decline.png)

Each panel shows the **total stake history** (in millions of ADA) of an entity classified as **dead, severely declining, or declining**. The inverted triangle marks the **peak epoch**. Colour encodes phase: **red** for dead, **orange** for severe decline, **amber** for moderate decline.

### Growing and stable entities

![Entity lifecycle — growing and stable entities](../figures/entity_lifecycle_growth.png)

Same format as above. **Green** indicates growing entities (current > 90% of peak); **blue** indicates stable entities (50–90% of peak).

The contrast with the decline chart is **striking**: growing entities show **steep ascent curves with late peaks**, while stable entities show **early peaks followed by a long plateau**.

> **Status** — Sub-document of [The Staking Census](../README.md). Built on 2026/04/09 from db-sync snapshot at epoch 623.
