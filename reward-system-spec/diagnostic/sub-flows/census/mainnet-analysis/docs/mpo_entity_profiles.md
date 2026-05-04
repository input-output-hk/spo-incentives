# MPO Entity Profiles — A Per-Entity Annex to the Mainnet Census

This annex to the [pools-distribution mainnet analysis](../../../pools-distribution/mainnet-analysis/README.md) describes every identified multi-pool operator (MPO) in detail, grouped by archetype, with historical stake trajectory across four reference epochs (400 / 410 / 584 / 618) and pledge-coverage ratio. *Where the census itself reports population-level structure, this document zooms in to the entity level.*

**The MPO landscape is not a single competitive field — it is a stack of five archetypes that play by different rules.** Exchange custodians (CEX), institutional staking-as-a-service providers (IVaaS), ecosystem stewards, platform/wallet operators, and independent community MPOs each combine pledge, margin, and delegation in characteristic ways. Mixing them in a single ranking obscures the structural differences that the protocol's incentive design depends on.

**Pledge coverage separates the archetypes more cleanly than any other single signal.** Custodial entities sit at structurally infinite pledge-to-stake ratios (they cannot pledge customer funds). IVaaS providers cluster at 50,000:1 to 600,000:1 — pledge is suppressed by scale economics, not by legal constraint. Ecosystem stewards (Cardano Foundation, IOG) and the strongest independent MPOs (Wave, Bloom) sit closest to 1:1 — the configuration the incentive design targets. Most other entities sit far above that, with pledge functioning as a registration formality rather than as a commitment signal.

**The trajectory data shows the institutional shift in real time.** Between epoch 400 and epoch 618, two CEXes (Binance, YUTA) and one ecosystem steward (IOG) shed the largest absolute share of supply, while two IVaaS providers (Figment, Kiln) and two CEXes (Coinbase, Upbit) absorbed the bulk of the redistributed delegation. The independent MPO segment — the archetype the protocol's reward curve was designed to favour — has lost ground in aggregate across the same window.

**One entity (CHUCK BUX) does not fit any archetype** and is flagged for separate treatment: a 94% on-chain margin combined with a 73M ₳ median self-pledge is consistent with a large ADA holder running self-delegation vehicles, not with any standard operator profile. Pledge-coverage analyses exclude it; stake-coverage analyses include it with explicit qualification.

## Table of Contents

- [1. How to read these profiles](#1-how-to-read-these-profiles)
- [2. Exchange Custody (CEX)](#2-exchange-custody-cex)
  - [2.1. Coinbase / bison.run](#21-coinbase-bisonrun)
  - [2.2. Binance](#22-binance)
  - [2.3. Upbit](#23-upbit)
  - [2.4. eToro](#24-etoro)
  - [2.5. YUTA](#25-yuta)
  - [2.6. StakeBowl](#26-stakebowl)
- [3. Institutional Validator / Staking-as-a-Service (IVaaS)](#3-institutional-validator-staking-as-a-service-ivaas)
  - [3.1. Figment](#31-figment)
  - [3.2. Kiln](#32-kiln)
  - [3.3. Blockdaemon](#33-blockdaemon)
  - [3.4. Everstake](#34-everstake)
  - [3.5. RockX](#35-rockx)
- [4. Ecosystem Steward](#4-ecosystem-steward)
  - [4.1. Cardano Foundation](#41-cardano-foundation)
  - [4.2. Emurgo](#42-emurgo)
  - [4.3. IOG](#43-iog)
- [5. Platform / Wallet](#5-platform-wallet)
  - [5.1. NuFi](#51-nufi)
  - [5.2. Adalite platform cluster](#52-adalite-platform-cluster)
- [6. Independent MPO](#6-independent-mpo)
  - [6.1. Wave / Wavepool](#61-wave-wavepool)
  - [6.2. 1PCT](#62-1pct)
  - [6.3. Bloom](#63-bloom)
  - [6.4. AdaOcean](#64-adaocean)
  - [6.5. P2P](#65-p2p)
  - [6.6. Spire](#66-spire)
  - [6.7. BigLazyCat](#67-biglazycat)
  - [6.8. AutoStake](#68-autostake)
  - [6.9. RAID](#69-raid)
- [7. Opaque / Unresolved](#7-opaque-unresolved)
  - [7.1. CHUCK BUX](#71-chuck-bux)
- [8. Community fleets, multi-brand operators, and other MPOs](#8-community-fleets-multi-brand-operators-and-other-mpos)
  - [8.1. Saturation-scale community fleets](#81-saturation-scale-community-fleets)
  - [8.2. Sub-saturation community fleets](#82-sub-saturation-community-fleets)


## 1. How to read these profiles

Each named entity in sections 2–7 carries a compact metric block followed by descriptive prose. The metric block uses the same four fields throughout:

| Field | What it captures |
|---|---|
| **Confidence** | Strength of attribution. *High* = first-party metadata, branded tickers, and convergent third-party analytics. *Medium* = third-party clustering only. *Low* = limited signals; treated as flagged. |
| **Active pools** | Currently producing pools versus total registered (where the gap is informative — ghost fleets indicate historical over-registration that was never rationalised). |
| **Trajectory** | Share of total supply at four reference epochs: 400, 410, 584, 618. Bold values mark the latest reading. |
| **Pledge coverage** | Delegated stake ÷ pledge. Read as a multiplier: *3:1* means three units of delegated stake per unit of pledge. ∞ marks structurally pledge-zero entities (custodial models). Values near 1:1 indicate near-full self-pledge — effectively self-sovereign delegation. |

Section 8 describes the wider community-fleet population using a more compact, list-based format because the per-entity public information thins out beyond the named operators.


## 2. Exchange Custody (CEX)

CEX entities hold retail or institutional ADA on behalf of their users. Delegation is not a sovereign choice by the ADA owner; pledge is structurally zero; and saturation pressure is absorbed internally. The pools-distribution analysis (§4.2) sets out why this archetype sits outside the protocol's incentive design.

### 2.1. Coinbase / bison.run

| Field | Value |
|---|---|
| Confidence | Medium-High (operational cluster, not first-party metadata) |
| Active pools | 47 active / 89 total matched · 23 at near-saturation |
| Trajectory | 6.60% (ep.400) → 5.50% (ep.410) → 5.71% (ep.584) → **6.38%** (ep.618) |
| Pledge coverage | 2.45B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero) |

Coinbase is a publicly listed US exchange and prime brokerage offering retail and institutional products including custody, execution, and staking. Its Cardano presence is hidden behind bison.run and herd.run infrastructure (hashed metadata and relay subdomains): pools carry generic or randomised tickers rather than a Coinbase brand. Koios and BalanceAnalytics surface the cluster as COINBASE (46 pools).

Broadly stable as the largest single entity in the set throughout the Shelley era; a mid-period dip around epoch 410 reversed fully.

### 2.2. Binance

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 50 active / 114 total registered |
| Trajectory | 7.44% (ep.400) → 4.22% (ep.410) → 2.41% (ep.584) → **1.80%** (ep.618) |
| Pledge coverage | 0.69B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero) |

Global exchange with wallet, payments, and Earn products. Cardano pools are clearly branded via the BNP ticker family and Binance-labelled S3 metadata paths; all three major analytics sources converge.

The steepest and most sustained retreat in the attributed set — the cluster has lost roughly 76% of its supply share since epoch 400. This is withdrawal of custodied retail ADA as Binance restructured its Cardano staking product, not organic delegation outflow.

### 2.3. Upbit

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 20 active · 100% on-chain margin |
| Trajectory | 0.00% (ep.400) → 0.27% (ep.410) → 1.16% (ep.584) → **1.43%** (ep.618) |
| Pledge coverage | 0.55B ₳ delegated / ~4M ₳ pledged = **138:1** (nominal pledge relative to managed stake) |

South Korean exchange (Dunamu). All 20 pools carry UPBIT tickers and point to staking-static.upbit.com metadata. Upbit retains all protocol rewards at 100% margin and pays users a separate exchange-defined APY — the protocol reward signal is fully internalised.

The fastest-growing CEX in the current period — a consistent ramp-up from near-zero to ~1.4% in under two years, entirely driven by exchange deposit growth.

### 2.4. eToro

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 12 active / 24 registered · 100% margin (internalised model, same as Upbit) |
| Trajectory | 1.49% (ep.400) → 1.48% (ep.410) → 1.17% (ep.584) → **1.23%** (ep.618) |
| Pledge coverage | 0.47B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero) |

Social trading and investment platform with custody staking. ETO\* tickers, etoro-spo.github.io metadata, and convergent analytics labels make attribution straightforward.

Broadly stable for most of the period; the dip at epoch 584 followed by partial recovery is ambiguous — possibly seasonal or a minor product change. The halving of active pools (24 → 12) signals partial wind-down of the Cardano staking product.

### 2.5. YUTA

| Field | Value |
|---|---|
| Confidence | Medium (third-party clustering only) |
| Active pools | 25 active / 28–29 matched |
| Trajectory | 2.00% (ep.400) → 1.94% (ep.410) → 1.28% (ep.584) → **1.20%** (ep.618) |
| Pledge coverage | 0.47B ₳ delegated / ~1M ₳ pledged = **404:1** |

Opaque multi-brand cluster attributed to Japanese crypto services including coinzzz.jp, tokyostaker.com, katanapool.com, and popool.net. ZZZ/JAPAN tickers. Koios and BalanceAnalytics group the pools under a single YUTA umbrella, but no single public-facing brand spans the full cluster.

Steady moderate decline across all periods. The gradual nature of the retreat — unlike Binance's sharp drop — suggests organic delegation outflow rather than deliberate pool retirement.

### 2.6. StakeBowl

| Field | Value |
|---|---|
| Confidence | Medium |
| Active pools | 9 active · 80.7% average margin · zero pledge |
| Trajectory | 0.15% (ep.400) → 0.15% (ep.410) → 0.18% (ep.584) → **0.36%** (ep.618) |
| Pledge coverage | 0.14B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero) |

Operated by neoply.io, a South Korean blockchain platform that ran gaming and staking services. STBL tickers, neoply.io metadata paths, shared reward addresses on two pools.

Very small and flat for most of the period, then doubled between epoch 584 and epoch 618. The source of this recent growth is unclear.


## 3. Institutional Validator / Staking-as-a-Service (IVaaS)

IVaaS entities serve institutional clients (asset managers, custodians, wallets) via a staking-as-a-service product. Delegation is at the discretion of the client; pledge is suppressed by scale economics rather than legal constraint. The pledge-suppression analysis is in the pools-distribution analysis (§4.2).

### 3.1. Figment

| Field | Value |
|---|---|
| Confidence | Medium-High |
| Active pools | 36 active · all metadata hosted on pcpm.s3.amazonaws.com |
| Trajectory | 0.00% (ep.400) → 0.00% (ep.410) → 1.09% (ep.584) → **2.07%** (ep.618) |
| Pledge coverage | 0.79B ₳ delegated / ~0 ₳ pledged = **∞** (IVaaS scale makes pledge premium uneconomic) |

Institutional staking provider serving asset managers, custodians, exchanges, and wallets. Koios labels the cluster as FIGMENT; some external analytics surface it as Ledger, reflecting Figment's role as back-end provider for Ledger Live's staking product.

The most explosive recent growth in the full attributed set — non-existent before epoch 584, now the second-largest entity. The trajectory reflects rapid institutional ADA inflows through Ledger Live and other custody clients.

### 3.2. Kiln

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 11 active (all registered pools live) |
| Trajectory | 0.66% (ep.400) → 0.72% (ep.410) → 1.56% (ep.584) → **1.82%** (ep.618) |
| Pledge coverage | 0.69B ₳ delegated / ~1M ₳ pledged = **624,000:1** |

Institutional validator SaaS; on Cardano, pools appeared originally under an Adalite surface (Koios still groups them as ADALITE) but kiln.fi metadata and KILN0–KILN4 tickers provide direct first-party branding. Serves enterprises, financial institutions, and major wallets.

The most consistent growth trajectory in the IVaaS cohort; the acceleration between epoch 410 and epoch 584 aligns with the broader institutional adoption wave.

### 3.3. Blockdaemon

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 15 active |
| Trajectory | 1.31% (ep.400) → 0.93% (ep.410) → 1.50% (ep.584) → **1.46%** (ep.618) |
| Pledge coverage | 0.58B ₳ delegated / ~3M ₳ pledged = **251,000:1** |

Enterprise blockchain infrastructure combining node/API services, staking, and MPC vault products. cardano.blockdaemon.com metadata and BD\* tickers are first-party signals; all three analytics sources converge.

A noticeable dip at epoch 410 followed by full recovery; otherwise broadly stable at 1.3–1.5%. Minor fluctuations consistent with client portfolio rebalancing.

### 3.4. Everstake

| Field | Value |
|---|---|
| Confidence | High (first-party metadata, branded tickers, convergent analytics labels) |
| Active pools | 15 active · 4% margin · 258K delegation addresses |
| Trajectory | 1.41% (ep.400) → 1.43% (ep.410) → 1.20% (ep.584) → **1.47%** (ep.618) |
| Pledge coverage | 0.57B ₳ delegated / ~11M ₳ pledged = **51,000:1** |

Enterprise-grade non-custodial staking provider, founded 2018 by Sergii Vasylchuk (blockchain engineer, formerly Attic Lab). The company started as a block producer on EOS before expanding to multi-chain PoS validation. Registered as Everstake Validation Services LLC in Grand Cayman; ~100 employees, 75% engineers. Leadership includes David Kinitsky (CEO, US operations), Bohdan Opryshko (COO), Iurii Tkachenko (CFO). Self-funded — no external venture rounds disclosed.

_Product surface:_ Validator-as-a-Service (VaaS), Wallet SDK (staking integrations for wallet providers), Yield SDK (stablecoin vaults via Midas), and Solana-specific infrastructure (SWQOS, ShredStream for low-latency data). Reported metrics: \$7B+ total staked across 130+ PoS networks, 1.6M+ delegators, 40,000+ active validators, 99.98% uptime, \$700M+ in rewards generated. Certifications: SOC 2 Type II, ISO 27001:2022, GDPR, NIST, CCPA.

_Institutional partnerships:_ Zodia Custody (Standard Chartered subsidiary) selected Everstake as validator partner for Cardano, Solana, and Polkadot staking (2025/06). Taurus (FINMA-regulated Swiss custody platform, 24+ global bank clients) integrated Everstake into Taurus-PROTECT for institutional staking on Cardano, Solana, NEAR, and Tezos (2025/12). Trezor integrated Solana staking via Everstake (2025/03). These partnerships position Everstake as a back-end staking layer for regulated financial institutions — Cardano ADA enters through custody platforms, not through direct pool selection.

_Cardano presence:_ everstake.one metadata and EVRST/EVERS/ESTK/EVE ticker family. The 258K delegation addresses average ~1,730 ADA each — the largest retail-facing operator in the cell by delegator count, and the sharpest contrast with custodial entities (Coinbase: 403 delegators at 6.1M ADA/deleg). The retail base suggests delegators reach Everstake through wallet integrations and product UX rather than fee-based comparison. Everstake registered as a Cardano DRep (2025/08), committing to data-driven, publicly documented governance voting — a governance footprint beyond pure validation.

_Venture arm:_ Everstake Capital, an early-stage blockchain VC (5 investments in 2024). Vasylchuk also directs the Metaplex Foundation (Solana NFT protocol) and co-initiated Aid For Ukraine with Ukraine's Ministry of Digital Transformation, which raised \$60M+ in crypto donations.

The trajectory is remarkably stable across 200+ epochs — the flattest among IVaaS entities. A slight dip at epoch 584 fully reversed. The institutional custody partnerships (Zodia, Taurus) could drive a step-change in delegation volume if bank-mediated staking scales, but this has not yet materialised on-chain. Pledge coverage remains near-zero relative to managed stake — structural for IVaaS scale; pledge economics are dominated by client custody architecture, not operator capital constraints.

### 3.5. RockX

| Field | Value |
|---|---|
| Confidence | Medium |
| Active pools | Near-zero active stake in the current snapshot |
| Trajectory | Near-zero across all measured epochs |
| Pledge coverage | ~0 ₳ delegated / ~1M ₳ pledged = **193:1** (pledge exceeds delegation; essentially operating at cost) |

Asian institutional validator provider. Included for completeness; no historical scale.


## 4. Ecosystem Steward

Ecosystem stewards are Cardano founding or governance entities that run pools primarily to stake their own treasury. High pledge, 100% margin, and near-saturation are expected features, not anomalies — these pools are not competing for external delegation.

### 4.1. Cardano Foundation

| Field | Value |
|---|---|
| Confidence | High (CF1–CF6 tickers, cardanofoundation.org metadata, shared reward address) |
| Active pools | 6 pools, all near-saturation · 100% margin · 76M ₳ median pledge |
| Trajectory | 0.00% (ep.400) → 0.00% (ep.410) → 0.00% (ep.584) → **1.19%** (ep.618) |
| Pledge coverage | 0.46B ₳ delegated / ~392M ₳ pledged = **~1:1** (near-full self-pledge; effectively self-sovereign delegation) |

Non-profit steward of the Cardano protocol. All 6 pools are fully self-pledged at z₀ and set 100% margin — a deliberate choice to retain rewards for protocol development rather than to compete for external delegation. CF delegates its own treasury into these pools.

Entirely absent until recently: the Foundation deployed its treasury into its own pools between epoch 584 and epoch 618. This is the largest single-period stake entry in the full attributed set in absolute terms.

### 4.2. Emurgo

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 11 active / 48 matched (large ghost fleet from the Shelley bootstrapping period) · 500 ₳ median self-pledge |
| Trajectory | 1.30% (ep.400) → 1.43% (ep.410) → 0.74% (ep.584) → **0.71%** (ep.618) |
| Pledge coverage | 0.27B ₳ delegated / ~14M ₳ pledged = **19,000:1** (surprisingly high for a founding entity) |

Commercial founding entity of Cardano. EMUR\* tickers, pools.emurgo.io metadata, plus a secondary SWIM/swimmingpoolop cluster.

Peaked at epoch 410 then declined sharply to epoch 584, stabilising since. The ghost fleet (48 registered vs 11 active) and near-zero self-pledge suggest historical over-registration that was never rationalised.

### 4.3. IOG

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 9 active / 65 matched · 64M ₳ median self-pledge on the survivors |
| Trajectory | 0.72% (ep.400) → 0.72% (ep.410) → 0.57% (ep.584) → **0.03%** (ep.618) |
| Pledge coverage | 0.013B ₳ delegated / ~325M ₳ pledged = **0.04:1** (pledge greatly exceeds active delegation — retirement in progress, pledge not yet withdrawn) |

Input Output (protocol developer). IOGP tickers, iohk.io / iog.io domains, branded relay hostnames.

A deliberate and accelerating wind-down: the cluster held steady through epoch 410, began retiring at epoch 584, and is now near-zero. The remaining 9 pools carry high self-pledge — the last institutionally-pledged pools before full retirement.


## 5. Platform / Wallet

Platform and wallet operators run pools surfaced through their own product UX. Users typically retain ADA ownership and sovereign delegation rights, but the wallet mediates pool discovery and switching friction.

### 5.1. NuFi

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 18 active · NUFI\* tickers, pools-meta.nu.fi metadata · grouped under ADALITE in Koios |
| Trajectory | 1.14% (ep.400) → 1.97% (ep.410) → 0.88% (ep.584) → **0.81%** (ep.618) |
| Pledge coverage | 0.31B ₳ delegated / ~18M ₳ pledged = **17,000:1** |

Non-custodial wallet and DeFi platform with integrated staking. Users retain ADA ownership and delegate through the wallet UX.

Peaked strongly at epoch 410 — consistent with a major wallet adoption wave — then retreated. The decline from 1.97% to 0.81% over ~200 epochs reflects competitive pressure from other DeFi/wallet integrations and some delegation migration to Kiln (which shares the ADALITE Koios surface).

### 5.2. Adalite platform cluster

| Field | Value |
|---|---|
| Confidence | Low-Medium (shown to document ambiguity) |
| Active pools | 3 attributed by external analytics · 71M ₳ median pledge · 100% margin |
| Trajectory | 0.40% (ep.400) → 0.40% (ep.410) → 0.41% (ep.584) → **0.41%** (ep.618) |
| Pledge coverage | 0.16B ₳ delegated / ~147M ₳ pledged = **~1:1** (near-full self-pledge; self-sovereign by configuration) |

A residual set of 3 pools attributed to the Adalite wallet platform by external analytics (ADALITE group label in Koios/BalanceAnalytics); no first-party assertion that these constitute a single legal operator. Extremely high pledge and 100% margin suggest a large self-pledging entity exposed through the wallet surface rather than a platform-controlled pool set.

The flattest trajectory in the entire set — stationary across all four epochs to two decimal places. This is consistent with a single large self-delegating entity that neither grows nor loses external delegation.


## 6. Independent MPO

Independent MPOs are operators who built multi-pool fleets to serve a broad community delegation base. They are the archetype the protocol's incentive design targets: sovereign delegators, competitive margins, and meaningful self-pledge.

### 6.1. Wave / Wavepool

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 17 active / 31 matched · 1M ₳ median self-pledge |
| Trajectory | 2.44% (ep.400) → 2.39% (ep.410) → 1.60% (ep.584) → **1.62%** (ep.618) |
| Pledge coverage | 0.61B ₳ delegated / ~227M ₳ pledged = **3:1** — the best pledge coverage of any large independent MPO |

Community pool family with direct first-party branding (wavepool.digital, wavemkr, WAVE tickers). One of the few attributed MPOs that scales while maintaining pledge discipline.

Peaked early and declined significantly through epoch 584, then stabilised. The 35% drop from peak reflects organic delegation migration to newer operators and the general competitive pressure on legacy pool families.

### 6.2. 1PCT

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 30 active / 31 · 12 pools sub-viability |
| Trajectory | 1.06% (ep.400) → 1.00% (ep.410) → 0.73% (ep.584) → **0.72%** (ep.618) |
| Pledge coverage | 0.27B ₳ delegated / ~1.6M ₳ pledged = **174:1** |

Explicitly community-focused operator; the name references the target margin. 1percentpool.eu metadata and 1PCT ticker families across all sources.

Steady, gradual decline across all periods — consistent with market pressure on low-margin operators as the competitive landscape has densified. Over-expansion (12 sub-viability pools) amplifies the cost of this drift.

### 6.3. Bloom

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 7 active / 12 matched · 1M ₳ median self-pledge · 17.7% margin |
| Trajectory | 0.73% (ep.400) → 0.73% (ep.410) → 0.59% (ep.584) → **0.57%** (ep.618) |
| Pledge coverage | 0.22B ₳ delegated / ~74M ₳ pledged = **3:1** — same strong pledge ratio as Wave |

Community pool family (bloompool.io, BLOOM tickers).

Slow, consistent decline — flat through epoch 410 then a step-down at epoch 584 that has since stabilised. Among the best-configured independent MPOs alongside Wave.

### 6.4. AdaOcean

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 10 active / 12 matched · 10K ₳ median self-pledge |
| Trajectory | 0.65% (ep.400) → 0.64% (ep.410) → 0.56% (ep.584) → **0.49%** (ep.618) |
| Pledge coverage | 0.19B ₳ delegated / ~0.3M ₳ pledged = **591:1** |

Community pool family (adaocean.com, OCEAN/OCEA\* tickers).

The most consistent downward trend in the independent MPO group — slow but uninterrupted decline across all periods.

### 6.5. P2P

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 6 active / 10 matched · 1K ₳ median self-pledge |
| Trajectory | 0.16% (ep.400) → 0.14% (ep.410) → 0.38% (ep.584) → **0.26%** (ep.618) |
| Pledge coverage | 0.10B ₳ delegated / ~0.2M ₳ pledged = **461:1** |

Institutional and community staking operator (p2p.org / p2p.world, P2P/PPCX tickers).

Small and stable early, then a significant jump to epoch 584 (possibly a specific institutional client onboarding), followed by partial retreat. Current level broadly consistent with a small community presence.

### 6.6. Spire

| Field | Value |
|---|---|
| Confidence | High |
| Active pools | 5 active / 24 matched (most extreme ghost fleet ratio among independent MPOs) · 22.2% margin |
| Trajectory | 0.21% (ep.400) → 0.21% (ep.410) → 0.23% (ep.584) → **0.25%** (ep.618) |
| Pledge coverage | 0.10B ₳ delegated / ~1.3M ₳ pledged = **77:1** |

Community operator spanning spirestaking.com and spireblockchain.com.

Flat throughout all periods. The operator pre-registered 24 pools but has never attracted more than 0.25% of supply; the ghost fleet (19 inactive pools) has persisted without resolution.

### 6.7. BigLazyCat

| Field | Value |
|---|---|
| Confidence | Medium |
| Active pools | 3 active · 0.7% margin · nominal self-pledge |
| Trajectory | No historical presence at ep.400–584 · **0.34%** (ep.618) |
| Pledge coverage | 0.13B ₳ delegated / ~3M ₳ pledged = **43,000:1** |

Small community operator. Recent addition to the attributed set.

### 6.8. AutoStake

| Field | Value |
|---|---|
| Confidence | Medium |
| Active pools | 4 active · 0% margin · 100 ₳ nominal self-pledge |
| Trajectory | No historical presence in earlier snapshots · **0.22%** (ep.618) |
| Pledge coverage | 0.08B ₳ delegated / ~0.4M ₳ pledged = **210,000:1** |

Small community operator with 0% margin.

### 6.9. RAID

| Field | Value |
|---|---|
| Confidence | Medium |
| Active pools | 7 registered · near-zero active stake |
| Trajectory | Near-zero across all measured epochs (excluded from the distribution figure, below the 0.01% threshold) |
| Pledge coverage | ~0 ₳ delegated / ~0.2M ₳ pledged = **2:1** (pledge exceeds delegation — pools not yet attracting external delegation) |

Small community operator.


## 7. Opaque / Unresolved

### 7.1. CHUCK BUX

| Field | Value |
|---|---|
| Confidence | Low (Koios + BalanceAnalytics labelling only; thin first-party evidence) |
| Active pools | 15 active / 17 matched · STKD ticker · git.io metadata · staked.cloud relay endpoints |
| Trajectory | 0.00% (ep.400) → 0.03% (ep.410) → 1.99% (ep.584) → **2.17%** (ep.618) |
| Pledge coverage | 0.83B ₳ delegated / ~742M ₳ pledged = **~1:1** (89% of managed stake is own capital) |

The most anomalous entity in the attributed set. The configuration is unlike any other archetype: 94% on-chain margin combined with 73M ₳ median self-pledge. This combination does not fit a CEX (which cannot pledge custodied funds) and does not fit a standard community operator (no competitive margin). The most coherent interpretation is a large ADA holder running self-delegation vehicles — pooling their own stake and retaining 94% of rewards — but this remains unverified.

The trajectory is the most striking in the set: absent for most of the Shelley era, then a sudden near-full-size entry between epoch 410 and epoch 584 (from 0.03% to 1.99% in a single inter-epoch measurement window). This pattern — appearing at scale almost instantaneously — is consistent with a single large block of delegation transferred at once, not with gradual retail accumulation. The source of this delegation block is unknown.

**Treat as flagged; exclude from pledge-coverage analyses; include in stake-coverage analyses with explicit qualification.**

> Full attribution evidence (tickers, metadata domains, relay fingerprints, example pool IDs, cross-source label convergence) for each entity above is in [`data/mpo_entity_deep_dive_mainnet.md`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_entity_deep_dive_mainnet.md), generated by [`scripts/build_mpo_entity_deep_dive.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/build_mpo_entity_deep_dive.py).


## 8. Community fleets, multi-brand operators, and other MPOs

The following entities are attributed via `pool_group` or `reward_addr` clustering. They are grouped by sub-type and capital class. Per-entity public information thins out beyond the named operators above, so this section uses a more compact list-based format.

### 8.1. Saturation-scale community fleets

**Community-branded fleet**

**ADV** (ADV) — 4 live pools, 263.2M ADA. Tickers: ADV, ADV2, ADV3, ADV4. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ADV, shared reward_addr=Yes, meta_domain=adavault.com.

**SECUR** (SECUR) — 5 live pools, 234.4M ADA. Tickers: SECUR. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=SECUR, shared reward_addr=Yes, meta_domain=cardano.securestaking.io.

**CCV** (CCV) — 5 live pools, 177.1M ADA. Tickers: CCV, CCV1, CCV2, CCV3, CCV4. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=CCV, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**MS4** (MS) — 4 live pools, 155.7M ADA. Tickers: MS4, MS5, MS6, MS9. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=MS, shared reward_addr=Yes, meta_domain=git.io.

**TITAN** (TITAN) — 2 live pools, 137.0M ADA. Tickers: TITAN. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=TITAN, shared reward_addr=Yes, meta_domain=titanstaking.io.

**AICHI** (AICHI) — 2 live pools, 123.5M ADA. Tickers: AICHI, TOKAI. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=AICHI, shared reward_addr=Yes, meta_domain=aichi-stakepool.com.

**NEDS1** (NEDS) — 4 live pools, 120.7M ADA. Tickers: NEDS1, NEDS2, NEDS3, NEDS4. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=NEDS, shared reward_addr=No, meta_domain=nedscave.io.

**SIPO** (SIPO) — 3 live pools, 114.4M ADA. Tickers: SIPO, SIPO2, SIPO3. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=SIPO, shared reward_addr=Yes, meta_domain=sipo.tokyo.

**SPS** (SPS) — 5 live pools, 104.6M ADA. Tickers: SPS, SPS2, SPS3, SPS4, SPS5. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=SPS, shared reward_addr=Yes, meta_domain=stakepoolservice.com.

**PILOT** (PILOT) — 2 live pools, 91.7M ADA. Tickers: PILOT. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=PILOT, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**PAUL1** (PAUL) — 2 live pools, 91.6M ADA. Tickers: PAUL, PAUL1. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=PAUL, shared reward_addr=Yes, meta_domain=pool.cardanowithpaul.com.

**ACL** (ACL) — 4 live pools, 84.4M ADA. Tickers: ACL. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ACL, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**CAFE** (CAFE) — 3 live pools, 80.7M ADA. Tickers: CAFE, CAFE2, CAFE3. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=CAFE, shared reward_addr=Yes, meta_domain=cardanocafe.org.

**SASA** (SASA) — 2 live pools, 74.3M ADA. Tickers: SASA, SASA2. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=SASA, shared reward_addr=Yes, meta_domain=bit.ly, nagamarupanda.github.io.

**RETIR** (BMTXS_GITHUB_IO) — 3 live pools, 73.8M ADA. Tickers: ADALO, RETIR. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=bmtxs.github.io, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**BCSH** (WESTBERG) — 8 live pools, 69.3M ADA. Tickers: BCSH, BCSH0, BCSH1, BCSH2, BCSH4, BCSH5, BCSH6, NEWMX. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=WESTBERG, shared reward_addr=Yes, meta_domain=cardanostakehouse.com.

**ONYX** (ONYX) — 4 live pools, 69.2M ADA. Tickers: ONYX. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ONYX, shared reward_addr=Yes, meta_domain=onyxstakepool.com.

**BRAVO** (BRAVO) — 2 live pools, 68.3M ADA. Tickers: BRAVO. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=BRAVO, shared reward_addr=Yes, meta_domain=bravostakepool.nl.

**VIPER** (VIPER) — 2 live pools, 68.1M ADA. Tickers: VIPER. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=VIPER, shared reward_addr=Yes, meta_domain=viperstaking.com.

**XSP** (XSP) — 2 live pools, 67.1M ADA. Tickers: XSP, XSP2. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=XSP, shared reward_addr=Yes, meta_domain=xstakepool.com.

**PNR39** (STRIXJPN_GITHUB_IO) — 2 live pools, 66.0M ADA. Tickers: PNR39, WBFL. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=strixjpn.github.io, shared reward_addr=Yes, meta_domain=strixjpn.github.io.

**SNAKE** (SNAKEPOOL_LINK) — 2 live pools, 63.3M ADA. Tickers: SNAKE. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=snakepool.link, shared reward_addr=Yes, meta_domain=asnakep.github.io.

**CNODE** (CNODE) — 4 live pools, 61.3M ADA. Tickers: CNODE, FUND, FUND2, FUND3. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=CNODE, shared reward_addr=Yes, meta_domain=cardanode.io.

**STI** (STI) — 3 live pools, 60.9M ADA. Tickers: ADACH, STI, STI2. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=STI, shared reward_addr=Yes, meta_domain=tobg.github.io.

**HODL₳** (HODLA) — 2 live pools, 60.5M ADA. Tickers: HODLA, HODL₳. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=HODLA, shared reward_addr=Yes, meta_domain=git.io.

**ADAOZ** (LINKTR_EE) — 2 live pools, 58.2M ADA. Tickers: ADAOZ, ENVY. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=linktr.ee, shared reward_addr=Yes, meta_domain=cardanode.com.au, tinyurl.com.

**TERA** (TERA) — 3 live pools, 52.9M ADA. Tickers: TERA, TERA2, TERA3. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=TERA, shared reward_addr=Yes, meta_domain=pooltera.github.io.

**ECO** (ECO) — 2 live pools, 50.6M ADA. Tickers: ECO. Sub-type: community_branded_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ECO, shared reward_addr=Yes, meta_domain=ecopool.io.

**Multi-brand fleet**

**CRDNS** (CRDNS) — 9 live pools, 231.2M ADA. Tickers: CRDN, CRDN1, CRDN2, CRDN3, CRDNS, MANDA, POOLS, nan. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=CRDNS, shared reward_addr=Yes, meta_domain=37.59.55.35, cardanians.io, pool.cardanoyoda.com.

**DAPP** (DAPP) — 8 live pools, 141.2M ADA. Tickers: AZUR, AZUR2, AZUR3, DAPP, LGC, ZILLA, nan. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=DAPP, shared reward_addr=Yes, meta_domain=apexfusionhosting.com, azureada.com, threenext.com.

**ATADA** (ATADA) — 4 live pools, 130.7M ADA. Tickers: ALPEN, ATAD2, ATADA, EGGS. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ATADA, shared reward_addr=Yes, meta_domain=stakepool.at, tinyurl.com.

**COOL** (COOL) — 6 live pools, 87.0M ADA. Tickers: CALM, COOL, COOL2, COOL3, COOL4, COOL5. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=COOL, shared reward_addr=Yes, meta_domain=stakecool.io.

**FIDA** (FIMI) — 9 live pools, 84.7M ADA. Tickers: AMZ1, ANCO, AOTA, BOOM, ELLY7, FIDA, FIMI, GRAB, nan. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=FIMI, shared reward_addr=Yes, meta_domain=bit.ly, git.io, tinyurl.com.

**ISP** (WEP) — 6 live pools, 84.0M ADA. Tickers: CTAX, DGK, ISP, PSPJ, RANKT, WEP. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=WEP, shared reward_addr=Yes, meta_domain=bit.ly, ranket2.github.io.

**FREE** (ITC) — 5 live pools, 79.9M ADA. Tickers: ALLIN, FREE, ITC, ITC2, ITC3. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=ITC, shared reward_addr=Yes, meta_domain=git.io, raw.githubusercontent.com, tinyurl.com.

**HOPE** (JOY) — 9 live pools, 78.6M ADA. Tickers: CCJ, CCJ2, CCJ3, CCJ4, CCJ5, HOPE, HOPE2, JOY, JOY2. Sub-type: multi_brand_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=JOY, shared reward_addr=Yes, meta_domain=cardano.ipclub29.com.

**Opaque fleet**

**NORTH** (NORTH) — 5 live pools, 363.1M ADA. Tickers: NORTH. Sub-type: opaque_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=NORTH, shared reward_addr=No, meta_domain=bit.ly.

**DIGI** (DIGI) — 6 live pools, 170.9M ADA. Tickers: DIGI, DIGI2, DIGI3, DIGI4, DIGI5, DIGI6. Sub-type: opaque_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=DIGI, shared reward_addr=No, meta_domain=digi.pro.

**EDEN** (EDEN) — 5 live pools, 170.7M ADA. Tickers: EDEN. Sub-type: opaque_fleet. Scale class: saturation-scale.
_Signals:_ pool_group=EDEN, shared reward_addr=No, meta_domain=garden-pool.com.

### 8.2. Sub-saturation community fleets

**Community-branded fleet**

**ATLAS** (ATLAS) — 2 live pools, 48.6M ADA. Tickers: ATLAS. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=ATLAS, shared reward_addr=Yes, meta_domain=atlasstakepool.com.

**STSH1** (AWP) — 3 live pools, 47.5M ADA. Tickers: STSH1, STSH2, STSH3. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=AWP, shared reward_addr=Yes, meta_domain=services.atomicwallet.io.

**SUNNY** (SUNNY) — 2 live pools, 45.3M ADA. Tickers: SUNNY. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=SUNNY, shared reward_addr=Yes, meta_domain=metadata.sunshinestakepool.com.

**HRMS** (HRMS) — 2 live pools, 44.3M ADA. Tickers: HRMS, nan. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=HRMS, shared reward_addr=Yes, meta_domain=hermes-stakepool.com.

**KIWI** (KIWI) — 3 live pools, 40.6M ADA. Tickers: KIWI, RAMEN. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=KIWI, shared reward_addr=Yes, meta_domain=tinyurl.com.

**ZETE** (ZETIC) — 2 live pools, 39.2M ADA. Tickers: ZETE, ZETE2. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=ZETIC, shared reward_addr=Yes, meta_domain=zetetic.tech.

**KTO** (KTO) — 10 live pools, 38.0M ADA. Tickers: CRBN, CRTR, KDK, KTO, MORH, MPOL, SMBU1, nan. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=KTO, shared reward_addr=Yes, meta_domain=agoodaycoffee.com, bit.ly, git.io, raw.githubusercontent.com, tinyurl.com.

**ADBV** (ADASTRONG_COM) — 2 live pools, 37.8M ADA. Tickers: ADAST, ADBV. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=adastrong.com, shared reward_addr=Yes, meta_domain=adastrong.com.

**4ADA** (4ADA) — 2 live pools, 37.8M ADA. Tickers: 4ADA, F4ADA. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=4ADA, shared reward_addr=Yes, meta_domain=staking4ada.org.

**NKR** (NKR) — 3 live pools, 36.1M ADA. Tickers: NKR, WWW, ZENA. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=NKR, shared reward_addr=Yes, meta_domain=git.io, raw.githubusercontent.com, tinyurl.com.

**KAIZN** (KAIZN) — 4 live pools, 34.5M ADA. Tickers: KAIZN, KOBE, KRONO, KRSNA. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=KAIZN, shared reward_addr=Yes, meta_domain=meta.pools.pm.

**MUEN** (MUEN) — 3 live pools, 34.2M ADA. Tickers: MUEN, MUEN2, MUEN3. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=MUEN, shared reward_addr=Yes, meta_domain=muen718.github.io.

**COFFE** (COFFEEPOOL_JP) — 2 live pools, 33.7M ADA. Tickers: COFFE, KISSA. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=coffeepool.jp, shared reward_addr=Yes, meta_domain=coffeepool.jp.

**ELITE** (ELITE) — 2 live pools, 31.9M ADA. Tickers: ELITE. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=ELITE, shared reward_addr=Yes, meta_domain=elitestakepool.com.

**WAFFLEPOOL_ORG** (WAFFLEPOOL_ORG) — 2 live pools, 31.8M ADA. Tickers: WFFL, nan. Sub-type: community_branded_fleet. Scale class: sub-saturation.
_Signals:_ pool_group=wafflepool.org, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com, wafflepool-cardano.github.io.

**Protocol / DeFi project**

**LQWD** (LIQWID) — 2 live pools, 47.4M ADA. Tickers: LQWD. Sub-type: protocol_project. Scale class: sub-saturation.
_Signals:_ pool_group=LIQWID, shared reward_addr=Yes, meta_domain=lqwdpool.s3.amazonaws.com.

**XRAY1** (RAY) — 8 live pools, 45.7M ADA. Tickers: XRAY1, XRAY2, XRAY3, XRAY4, XRAY5, XRAY6, XRAY7, XRAY8. Sub-type: protocol_project. Scale class: sub-saturation.
_Signals:_ pool_group=RAY, shared reward_addr=Yes, meta_domain=xray.app.

**IBEX** (IBEX) — 3 live pools, 44.3M ADA. Tickers: BASHO, IBEX, RKD. Sub-type: protocol_project. Scale class: sub-saturation.
_Signals:_ pool_group=IBEX, shared reward_addr=Yes, meta_domain=ada.ibexpool.com, ibexpool.com.

**DNEWS** (DNEWS) — 2 live pools, 39.7M ADA. Tickers: DNEWS. Sub-type: protocol_project. Scale class: sub-saturation.
_Signals:_ pool_group=DNEWS, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.


> **Status** — Last updated 2026/03/19. Snapshot epoch: 618. Source data: [`data/mpo_entity_health_overview_mainnet.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_entity_health_overview_mainnet.csv), [`data/mpo_entity_archetypes.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_entity_archetypes.csv).
