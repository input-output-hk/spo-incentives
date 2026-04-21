# MPO Entity Profiles

> Annex to §4.3 of `report/mainnet/pools-distribution/README.md`.
> Detailed per-entity descriptions grouped by archetype, including
> historical stake trajectory (epochs 400 / 410 / 584 / 618) and
> pledge-coverage ratio.
>
> Last updated: 2026/03/19. Snapshot epoch: 618.
> Source data: `data/mpo_entity_health_overview_mainnet.csv`,
> `data/mpo_entity_archetypes.csv`.

---

## Exchange Custody (CEX)

CEX entities hold retail or institutional ADA on behalf of their users. Delegation is not a sovereign choice by the ADA owner; pledge is structurally zero; and saturation pressure is absorbed internally. See §4.2 for a full analysis of why this archetype sits outside the protocol's incentive design.

**Coinbase / bison.run** — Coinbase is a publicly listed US exchange and prime brokerage offering retail and institutional products including custody, execution, and staking. Its Cardano presence is hidden behind bison.run and herd.run infrastructure (hashed metadata and relay subdomains): pools carry generic or randomised tickers rather than a Coinbase brand. Koios and BalanceAnalytics surface the cluster as COINBASE (46 pools). 47 active pools (89 total matched), 23 at near-saturation. Attribution: Medium-High confidence (operational cluster, not first-party metadata).
_History:_ 6.60% (ep.400) → 5.50% (ep.410) → 5.71% (ep.584) → **6.38%** (ep.618). Broadly stable as the largest single entity in the set throughout the Shelley era; a mid-period dip around epoch 410 reversed fully.
_Pledge coverage:_ 2.45B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero).

**Binance** — Global exchange with wallet, payments, and Earn products. Cardano pools are clearly branded via the BNP ticker family and Binance-labelled S3 metadata paths; all three major analytics sources converge. 50 active pools (114 total registered). Attribution: High confidence.
_History:_ 7.44% (ep.400) → 4.22% (ep.410) → 2.41% (ep.584) → **1.80%** (ep.618). The steepest and most sustained retreat in the attributed set — lost ~76% of its supply share since epoch 400. This is withdrawal of custodied retail ADA as Binance restructured its Cardano staking product, not organic delegation outflow.
_Pledge coverage:_ 0.69B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero).

**Upbit** — South Korean exchange (Dunamu). All 20 pools carry UPBIT tickers and point to staking-static.upbit.com metadata. 100% on-chain margin: Upbit retains all protocol rewards and pays users a separate exchange-defined APY — the protocol reward signal is fully internalised. Attribution: High confidence.
_History:_ 0.00% (ep.400) → 0.27% (ep.410) → 1.16% (ep.584) → **1.43%** (ep.618). The fastest-growing CEX in the current period — a consistent ramp-up from near-zero to ~1.4% in under two years, entirely driven by exchange deposit growth.
_Pledge coverage:_ 0.55B ₳ delegated / ~4M ₳ pledged = **138:1** (nominal pledge relative to managed stake).

**eToro** — Social trading and investment platform with custody staking. ETO\* tickers, etoro-spo.github.io metadata, and convergent analytics labels make attribution straightforward. 100% margin (same internalised model as Upbit). 24 pools registered but only 12 currently active. Attribution: High confidence.
_History:_ 1.49% (ep.400) → 1.48% (ep.410) → 1.17% (ep.584) → **1.23%** (ep.618). Broadly stable for most of the period; the dip at ep.584 followed by partial recovery is ambiguous — possibly seasonal or a minor product change. The halving of active pools (24 → 12) signals partial wind-down of the Cardano staking product.
_Pledge coverage:_ 0.47B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero).

**YUTA** — Opaque multi-brand cluster attributed to Japanese crypto services including coinzzz.jp, tokyostaker.com, katanapool.com, and popool.net. ZZZ/JAPAN tickers. Koios and BalanceAnalytics group 28–29 pools under a single YUTA umbrella, but no single public-facing brand spans the full cluster. 25 pools active. Attribution: Medium confidence (third-party clustering only).
_History:_ 2.00% (ep.400) → 1.94% (ep.410) → 1.28% (ep.584) → **1.20%** (ep.618). Steady moderate decline across all periods. The gradual nature of the retreat — unlike Binance's sharp drop — suggests organic delegation outflow rather than deliberate pool retirement.
_Pledge coverage:_ 0.47B ₳ delegated / ~1M ₳ pledged = **404:1**.

**StakeBowl** — Operated by neoply.io, a South Korean blockchain platform that ran gaming and staking services. STBL tickers, neoply.io metadata paths, shared reward addresses on two pools. 9 pools active, 80.7% average margin, zero pledge. Attribution: Medium confidence.
_History:_ 0.15% (ep.400) → 0.15% (ep.410) → 0.18% (ep.584) → **0.36%** (ep.618). Very small and flat for most of the period, then doubled between ep.584 and ep.618. The source of this recent growth is unclear.
_Pledge coverage:_ 0.14B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero).

---

## Institutional Validator / Staking-as-a-Service (IVaaS)

IVaaS entities serve institutional clients (asset managers, custodians, wallets) via a staking-as-a-service product. Delegation is at the discretion of the client; pledge is suppressed by scale economics rather than legal constraint. See §4.2 for the pledge-suppression analysis.

**Figment** — Institutional staking provider serving asset managers, custodians, exchanges, and wallets. Koios labels the cluster as FIGMENT; some external analytics surfaces it as Ledger, reflecting Figment's role as back-end provider for Ledger Live's staking product. All metadata hosted on pcpm.s3.amazonaws.com. 36 active pools. Attribution: Medium-High confidence.
_History:_ 0.00% (ep.400) → 0.00% (ep.410) → 1.09% (ep.584) → **2.07%** (ep.618). The most explosive recent growth in the full attributed set — non-existent before ep.584, now the second-largest entity. Reflects rapid institutional ADA inflows through Ledger Live and other custody clients.
_Pledge coverage:_ 0.79B ₳ delegated / ~0 ₳ pledged = **∞** (structurally pledge-zero — IVaaS scale makes pledge premium uneconomic).

**Kiln** — Institutional validator SaaS; on Cardano its pools appeared originally under an Adalite surface (Koios still groups them as ADALITE) but kiln.fi metadata and KILN0–KILN4 tickers provide direct first-party branding. Serves enterprises, financial institutions, and major wallets. 11 pools, all active. Attribution: High confidence.
_History:_ 0.66% (ep.400) → 0.72% (ep.410) → 1.56% (ep.584) → **1.82%** (ep.618). Steady institutional growth throughout — the most consistent growth trajectory in the IVaaS cohort. The acceleration between ep.410 and ep.584 aligns with the broader institutional adoption wave.
_Pledge coverage:_ 0.69B ₳ delegated / ~1M ₳ pledged = **624,000:1**.

**Blockdaemon** — Enterprise blockchain infrastructure combining node/API services, staking, and MPC vault products. cardano.blockdaemon.com metadata and BD\* tickers are first-party signals; all three analytics sources converge. 15 active pools. Attribution: High confidence.
_History:_ 1.31% (ep.400) → 0.93% (ep.410) → 1.50% (ep.584) → **1.46%** (ep.618). A noticeable dip at ep.410 followed by full recovery; otherwise broadly stable at 1.3–1.5%. Minor fluctuations consistent with client portfolio rebalancing.
_Pledge coverage:_ 0.58B ₳ delegated / ~3M ₳ pledged = **251,000:1**.

**Everstake** — Enterprise-grade non-custodial staking provider, founded 2018 by Sergii Vasylchuk (blockchain engineer, formerly Attic Lab). The company started as a block producer on EOS before expanding to multi-chain PoS validation. Registered as Everstake Validation Services LLC in Grand Cayman; ~100 employees, 75% engineers. Leadership includes David Kinitsky (CEO, US operations), Bohdan Opryshko (COO), Iurii Tkachenko (CFO). Self-funded — no external venture rounds disclosed.

_Product surface:_ Validator-as-a-Service (VaaS), Wallet SDK (staking integrations for wallet providers), Yield SDK (stablecoin vaults via Midas), and Solana-specific infrastructure (SWQOS, ShredStream for low-latency data). The company reports $7B+ in total staked value across 130+ PoS networks, 1.6M+ delegators, 40,000+ active validators, 99.98% uptime, and $700M+ in rewards generated. Certifications: SOC 2 Type II, ISO 27001:2022, GDPR, NIST, CCPA.

_Institutional partnerships:_ Zodia Custody (Standard Chartered subsidiary) selected Everstake as validator partner for Cardano, Solana, and Polkadot staking (2025/06). Taurus (FINMA-regulated Swiss custody platform, 24+ global bank clients) integrated Everstake into Taurus-PROTECT for institutional staking on Cardano, Solana, NEAR, and Tezos (2025/12). Trezor integrated Solana staking via Everstake (2025/03). These partnerships position Everstake as a back-end staking layer for regulated financial institutions — Cardano ADA enters through custody platforms, not through direct pool selection.

_Cardano presence:_ everstake.one metadata and EVRST/EVERS/ESTK/EVE ticker family. 15 active pools, 4% margin. 258K delegation addresses averaging ~1,730 ADA each — the largest retail-facing operator in the cell by delegator count, and the sharpest contrast with custodial entities (Coinbase: 403 delegators at 6.1M ADA/deleg). The retail base suggests delegators reach Everstake through wallet integrations and product UX rather than fee-based comparison. Everstake registered as a Cardano DRep (2025/08), committing to data-driven, publicly documented governance voting — a governance footprint beyond pure validation.

_Venture arm:_ Everstake Capital, an early-stage blockchain VC (5 investments in 2024). Vasylchuk also directs the Metaplex Foundation (Solana NFT protocol) and co-initiated Aid For Ukraine with Ukraine's Ministry of Digital Transformation, which raised $60M+ in crypto donations.

Attribution: High confidence (first-party metadata, branded tickers, convergent analytics labels).
_History:_ 1.41% (ep.400) → 1.43% (ep.410) → 1.20% (ep.584) → **1.47%** (ep.618). Remarkably stable across 200+ epochs — the flattest trajectory among IVaaS entities. A slight dip at ep.584 fully reversed. The institutional custody partnerships (Zodia, Taurus) could drive a step-change in delegation volume if bank-mediated staking scales, but this has not yet materialised on-chain.
_Pledge coverage:_ 0.57B ₳ delegated / ~11M ₳ pledged = **51,000:1**. Near-zero self-pledge relative to managed stake — structural for IVaaS scale; pledge economics are dominated by client custody architecture, not operator capital constraints.

**RockX** — Asian institutional validator provider. Near-zero active stake in the current snapshot; included for completeness. Historical presence also near-zero across all measured epochs.
_Pledge coverage:_ ~0 ₳ delegated / ~1M ₳ pledged = **193:1** (pledge exceeds delegation in current state — essentially operating at cost).

---

## Ecosystem Steward

Ecosystem stewards are Cardano founding or governance entities that run pools primarily to stake their own treasury. High pledge, 100% margin, and near-saturation are expected features, not anomalies — these pools are not competing for external delegation.

**Cardano Foundation** — Non-profit steward of the Cardano protocol. All 6 pools are fully self-pledged at z₀ (76M ₳ median pledge) and set 100% margin — a deliberate choice to retain rewards for protocol development rather than to compete for external delegation. All 6 pools sit at near-saturation (CF delegates its own treasury). Attribution: High confidence (CF1–CF6 tickers, cardanofoundation.org metadata, shared reward address).
_History:_ 0.00% (ep.400) → 0.00% (ep.410) → 0.00% (ep.584) → **1.19%** (ep.618). Entirely absent until recently: the Foundation deployed its treasury into its own pools between ep.584 and ep.618. This is the largest single-period stake entry in the full attributed set in absolute terms.
_Pledge coverage:_ 0.46B ₳ delegated / ~392M ₳ pledged = **~1:1** (near-full self-pledge; effectively self-sovereign delegation).

**Emurgo** — Commercial founding entity of Cardano. EMUR\* tickers, pools.emurgo.io metadata, and a secondary SWIM/swimmingpoolop cluster. 48 matched pools but only 11 currently active — a large ghost fleet from the Shelley bootstrapping period. Attribution: High confidence.
_History:_ 1.30% (ep.400) → 1.43% (ep.410) → 0.74% (ep.584) → **0.71%** (ep.618). Peaked at ep.410 then declined sharply to ep.584, stabilising since. The ghost fleet (48 registered vs 11 active) and near-zero self-pledge (500 ₳ median) suggest historical over-registration that was never rationalised.
_Pledge coverage:_ 0.27B ₳ delegated / ~14M ₳ pledged = **19,000:1** (surprisingly high for a founding entity).

**IOG** — Input Output (protocol developer). IOGP tickers, iohk.io / iog.io domains, branded relay hostnames. 65 matched pools, 9 currently active. Attribution: High confidence.
_History:_ 0.72% (ep.400) → 0.72% (ep.410) → 0.57% (ep.584) → **0.03%** (ep.618). A deliberate and accelerating wind-down: held steady through ep.410, began retiring at ep.584, now near-zero. The remaining 9 pools carry high self-pledge (64M ₳ median) — these are the last institutionally-pledged pools before full retirement.
_Pledge coverage:_ 0.013B ₳ delegated / ~325M ₳ pledged = **0.04:1** (pledge greatly exceeds active delegation — retirement in progress, pledge not yet withdrawn).

---

## Platform / Wallet

Platform and wallet operators run pools surfaced through their own product UX. Users typically retain ADA ownership and sovereign delegation rights, but the wallet mediates pool discovery and switching friction.

**NuFi** — Non-custodial wallet and DeFi platform with integrated staking. Users retain ADA ownership and delegate through the wallet UX. NUFI\* tickers, pools-meta.nu.fi metadata; Koios groups the cluster as ADALITE (platform-level surface label shared with Kiln). 18 active pools. Attribution: High confidence.
_History:_ 1.14% (ep.400) → 1.97% (ep.410) → 0.88% (ep.584) → **0.81%** (ep.618). Peaked strongly at ep.410 — consistent with a major wallet adoption wave — then retreated. The decline from 1.97% to 0.81% over ~200 epochs reflects competitive pressure from other DeFi/wallet integrations and some delegation migration to Kiln (which shares the ADALITE Koios surface).
_Pledge coverage:_ 0.31B ₳ delegated / ~18M ₳ pledged = **17,000:1**.

**Adalite platform cluster** — A residual set of 3 pools attributed to the Adalite wallet platform by external analytics (ADALITE group label in Koios/BalanceAnalytics); no first-party assertion that these constitute a single legal operator. Extremely high pledge (71M ₳ median) and 100% margin suggest a large self-pledging entity exposed through the wallet surface rather than a platform-controlled pool set. Attribution: Low-Medium confidence — shown to document ambiguity.
_History:_ 0.40% (ep.400) → 0.40% (ep.410) → 0.41% (ep.584) → **0.41%** (ep.618). The flattest trajectory in the entire set — stationary across all four epochs to two decimal places. This is consistent with a single large self-delegating entity that neither grows nor loses external delegation.
_Pledge coverage:_ 0.16B ₳ delegated / ~147M ₳ pledged = **~1:1** (near-full self-pledge; self-sovereign by configuration).

---

## Independent MPO

Independent MPOs are operators who built multi-pool fleets to serve a broad community delegation base. They are the archetype the protocol's incentive design targets: sovereign delegators, competitive margins, and meaningful self-pledge.

**Wave / Wavepool** — Community pool family with direct first-party branding (wavepool.digital, wavemkr, WAVE tickers). 31 matched pools, 17 active. Meaningful self-pledge (1M ₳ median) — one of the few attributed MPOs that scales while maintaining pledge discipline. Attribution: High confidence.
_History:_ 2.44% (ep.400) → 2.39% (ep.410) → 1.60% (ep.584) → **1.62%** (ep.618). Peaked early and declined significantly through ep.584, then stabilised. The 35% drop from peak reflects organic delegation migration to newer operators and the general competitive pressure on legacy pool families.
_Pledge coverage:_ 0.61B ₳ delegated / ~227M ₳ pledged = **3:1** — the best pledge coverage of any large independent MPO. For every 3 ₳ of delegated stake, 1 ₳ is the operator's own capital.

**1PCT** — Explicitly community-focused operator; the name references the target margin. 1percentpool.eu metadata and 1PCT ticker families across all sources. 30 active pools (out of 31); 12 pools sub-viability. Attribution: High confidence.
_History:_ 1.06% (ep.400) → 1.00% (ep.410) → 0.73% (ep.584) → **0.72%** (ep.618). Steady, gradual decline across all periods — consistent with market pressure on low-margin operators as the competitive landscape has densified. Over-expansion (12 sub-viability pools) amplifies the cost of this drift.
_Pledge coverage:_ 0.27B ₳ delegated / ~1.6M ₳ pledged = **174:1**.

**Bloom** — Community pool family (bloompool.io, BLOOM tickers). 12 matched pools, 7 active. Meaningful self-pledge (1M ₳ median), moderate margin (17.7%). Attribution: High confidence.
_History:_ 0.73% (ep.400) → 0.73% (ep.410) → 0.59% (ep.584) → **0.57%** (ep.618). Slow, consistent decline — flat through ep.410 then a step-down at ep.584 that has since stabilised. Among the best-configured independent MPOs alongside Wave.
_Pledge coverage:_ 0.22B ₳ delegated / ~74M ₳ pledged = **3:1** — same strong pledge ratio as Wave.

**AdaOcean** — Community pool family (adaocean.com, OCEAN/OCEA\* tickers). 12 matched pools, 10 active. Low self-pledge (10K ₳ median). Attribution: High confidence.
_History:_ 0.65% (ep.400) → 0.64% (ep.410) → 0.56% (ep.584) → **0.49%** (ep.618). The most consistent downward trend in the independent MPO group — slow but uninterrupted decline across all periods.
_Pledge coverage:_ 0.19B ₳ delegated / ~0.3M ₳ pledged = **591:1**.

**P2P** — Institutional and community staking operator (p2p.org / p2p.world, P2P/PPCX tickers). 10 matched pools, 6 active. Near-zero self-pledge (1K ₳ median). Attribution: High confidence.
_History:_ 0.16% (ep.400) → 0.14% (ep.410) → 0.38% (ep.584) → **0.26%** (ep.618). Small and stable early, then a significant jump to ep.584 (possibly a specific institutional client onboarding), followed by partial retreat. Current level broadly consistent with a small community presence.
_Pledge coverage:_ 0.10B ₳ delegated / ~0.2M ₳ pledged = **461:1**.

**Spire** — Community operator spanning spirestaking.com and spireblockchain.com. 24 matched pools but only 5 active — the most extreme ghost fleet ratio among independent MPOs. High margin (22.2%), near-zero pledge. Attribution: High confidence.
_History:_ 0.21% (ep.400) → 0.21% (ep.410) → 0.23% (ep.584) → **0.25%** (ep.618). Flat throughout all periods. The operator pre-registered 24 pools but has never attracted more than 0.25% of supply; the ghost fleet (19 inactive pools) has persisted without resolution.
_Pledge coverage:_ 0.10B ₳ delegated / ~1.3M ₳ pledged = **77:1**.

**BigLazyCat** — Small community operator. 3 active pools, 0.34% of supply. Very low margin (0.7%), nominal self-pledge. No historical presence at ep.400–584; current 0.34% is a recent addition to the attributed set.
_Pledge coverage:_ 0.13B ₳ delegated / ~3M ₳ pledged = **43,000:1** (low absolute pledge on a small but growing fleet).

**AutoStake** — Small community operator with 0% margin. 4 active pools, 0.22% of supply. No historical presence in earlier snapshots. Nominal self-pledge (100 ₳).
_Pledge coverage:_ 0.08B ₳ delegated / ~0.4M ₳ pledged = **210,000:1**.

**RAID** — Small community operator. 7 pools registered, near-zero active stake across all measured epochs. Excluded from the distribution figure (below the 0.01% threshold).
_Pledge coverage:_ ~0 ₳ delegated / ~0.2M ₳ pledged = **2:1** (pledge exceeds delegation — pools not yet attracting external delegation).

---

## Opaque / Unresolved

**CHUCK BUX** — The most anomalous entity in the attributed set. 17 pools, 15 active. The cluster carries a STKD ticker, git.io metadata, and staked.cloud relay endpoints — thin first-party evidence. Attribution rests almost entirely on Koios and BalanceAnalytics labelling all 17 pools as CHUCK BUX. The configuration is unlike any other archetype: 94% on-chain margin combined with 73M ₳ median self-pledge. This combination does not fit a CEX (which cannot pledge custodied funds) and does not fit a standard community operator (no competitive margin). The most coherent interpretation is a large ADA holder running self-delegation vehicles — pooling their own stake and retaining 94% of rewards — but this remains unverified. **Treat as flagged; exclude from pledge-coverage analyses; include in stake-coverage analyses with explicit qualification.** Attribution: Low confidence.
_History:_ 0.00% (ep.400) → 0.03% (ep.410) → 1.99% (ep.584) → **2.17%** (ep.618). The most striking trajectory in the set: absent for most of the Shelley era, then a sudden near-full-size entry between ep.410 and ep.584 (from 0.03% to 1.99% in a single inter-epoch measurement window). This pattern — appearing at scale almost instantaneously — is consistent with a single large block of delegation transferred at once, not with gradual retail accumulation. The source of this delegation block is unknown.
_Pledge coverage:_ 0.83B ₳ delegated / ~742M ₳ pledged = **~1:1** (large self-pledge consistent with a whale self-service model; 89% of managed stake is own capital).

---

> Full attribution evidence (tickers, metadata domains, relay fingerprints, example pool IDs, cross-source label convergence) for each entity is in `data/mpo_entity_deep_dive_mainnet.md`, generated by `scripts/build_mpo_entity_deep_dive.py`.
---

## Community Fleets, Multi-Brand Operators, and Other MPOs

The following entities are attributed via `pool_group` or `reward_addr` clustering. They are grouped by sub-type and capital class.

### Capital-sufficient community fleets

**Community Branded Fleet**

**ADV** (ADV) — 4 live pools, 263.2M ADA. Tickers: ADV, ADV2, ADV3, ADV4. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=ADV, shared reward_addr=Yes, meta_domain=adavault.com.

**SECUR** (SECUR) — 5 live pools, 234.4M ADA. Tickers: SECUR. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=SECUR, shared reward_addr=Yes, meta_domain=cardano.securestaking.io.

**CCV** (CCV) — 5 live pools, 177.1M ADA. Tickers: CCV, CCV1, CCV2, CCV3, CCV4. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=CCV, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**MS4** (MS) — 4 live pools, 155.7M ADA. Tickers: MS4, MS5, MS6, MS9. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=MS, shared reward_addr=Yes, meta_domain=git.io.

**TITAN** (TITAN) — 2 live pools, 137.0M ADA. Tickers: TITAN. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=TITAN, shared reward_addr=Yes, meta_domain=titanstaking.io.

**AICHI** (AICHI) — 2 live pools, 123.5M ADA. Tickers: AICHI, TOKAI. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=AICHI, shared reward_addr=Yes, meta_domain=aichi-stakepool.com.

**NEDS1** (NEDS) — 4 live pools, 120.7M ADA. Tickers: NEDS1, NEDS2, NEDS3, NEDS4. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=NEDS, shared reward_addr=No, meta_domain=nedscave.io.

**SIPO** (SIPO) — 3 live pools, 114.4M ADA. Tickers: SIPO, SIPO2, SIPO3. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=SIPO, shared reward_addr=Yes, meta_domain=sipo.tokyo.

**SPS** (SPS) — 5 live pools, 104.6M ADA. Tickers: SPS, SPS2, SPS3, SPS4, SPS5. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=SPS, shared reward_addr=Yes, meta_domain=stakepoolservice.com.

**PILOT** (PILOT) — 2 live pools, 91.7M ADA. Tickers: PILOT. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=PILOT, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**PAUL1** (PAUL) — 2 live pools, 91.6M ADA. Tickers: PAUL, PAUL1. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=PAUL, shared reward_addr=Yes, meta_domain=pool.cardanowithpaul.com.

**ACL** (ACL) — 4 live pools, 84.4M ADA. Tickers: ACL. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=ACL, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**CAFE** (CAFE) — 3 live pools, 80.7M ADA. Tickers: CAFE, CAFE2, CAFE3. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=CAFE, shared reward_addr=Yes, meta_domain=cardanocafe.org.

**SASA** (SASA) — 2 live pools, 74.3M ADA. Tickers: SASA, SASA2. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=SASA, shared reward_addr=Yes, meta_domain=bit.ly, nagamarupanda.github.io.

**RETIR** (BMTXS_GITHUB_IO) — 3 live pools, 73.8M ADA. Tickers: ADALO, RETIR. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=bmtxs.github.io, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.

**BCSH** (WESTBERG) — 8 live pools, 69.3M ADA. Tickers: BCSH, BCSH0, BCSH1, BCSH2, BCSH4, BCSH5, BCSH6, NEWMX. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=WESTBERG, shared reward_addr=Yes, meta_domain=cardanostakehouse.com.

**ONYX** (ONYX) — 4 live pools, 69.2M ADA. Tickers: ONYX. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=ONYX, shared reward_addr=Yes, meta_domain=onyxstakepool.com.

**BRAVO** (BRAVO) — 2 live pools, 68.3M ADA. Tickers: BRAVO. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=BRAVO, shared reward_addr=Yes, meta_domain=bravostakepool.nl.

**VIPER** (VIPER) — 2 live pools, 68.1M ADA. Tickers: VIPER. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=VIPER, shared reward_addr=Yes, meta_domain=viperstaking.com.

**XSP** (XSP) — 2 live pools, 67.1M ADA. Tickers: XSP, XSP2. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=XSP, shared reward_addr=Yes, meta_domain=xstakepool.com.

**PNR39** (STRIXJPN_GITHUB_IO) — 2 live pools, 66.0M ADA. Tickers: PNR39, WBFL. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=strixjpn.github.io, shared reward_addr=Yes, meta_domain=strixjpn.github.io.

**SNAKE** (SNAKEPOOL_LINK) — 2 live pools, 63.3M ADA. Tickers: SNAKE. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=snakepool.link, shared reward_addr=Yes, meta_domain=asnakep.github.io.

**CNODE** (CNODE) — 4 live pools, 61.3M ADA. Tickers: CNODE, FUND, FUND2, FUND3. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=CNODE, shared reward_addr=Yes, meta_domain=cardanode.io.

**STI** (STI) — 3 live pools, 60.9M ADA. Tickers: ADACH, STI, STI2. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=STI, shared reward_addr=Yes, meta_domain=tobg.github.io.

**HODL₳** (HODLA) — 2 live pools, 60.5M ADA. Tickers: HODLA, HODL₳. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=HODLA, shared reward_addr=Yes, meta_domain=git.io.

**ADAOZ** (LINKTR_EE) — 2 live pools, 58.2M ADA. Tickers: ADAOZ, ENVY. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=linktr.ee, shared reward_addr=Yes, meta_domain=cardanode.com.au, tinyurl.com.

**TERA** (TERA) — 3 live pools, 52.9M ADA. Tickers: TERA, TERA2, TERA3. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=TERA, shared reward_addr=Yes, meta_domain=pooltera.github.io.

**ECO** (ECO) — 2 live pools, 50.6M ADA. Tickers: ECO. Sub-type: community_branded_fleet. Capital class: sufficient.
_Signals:_ pool_group=ECO, shared reward_addr=Yes, meta_domain=ecopool.io.

**Multi-Brand Fleet**

**CRDNS** (CRDNS) — 9 live pools, 231.2M ADA. Tickers: CRDN, CRDN1, CRDN2, CRDN3, CRDNS, MANDA, POOLS, nan. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=CRDNS, shared reward_addr=Yes, meta_domain=37.59.55.35, cardanians.io, pool.cardanoyoda.com.

**DAPP** (DAPP) — 8 live pools, 141.2M ADA. Tickers: AZUR, AZUR2, AZUR3, DAPP, LGC, ZILLA, nan. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=DAPP, shared reward_addr=Yes, meta_domain=apexfusionhosting.com, azureada.com, threenext.com.

**ATADA** (ATADA) — 4 live pools, 130.7M ADA. Tickers: ALPEN, ATAD2, ATADA, EGGS. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=ATADA, shared reward_addr=Yes, meta_domain=stakepool.at, tinyurl.com.

**COOL** (COOL) — 6 live pools, 87.0M ADA. Tickers: CALM, COOL, COOL2, COOL3, COOL4, COOL5. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=COOL, shared reward_addr=Yes, meta_domain=stakecool.io.

**FIDA** (FIMI) — 9 live pools, 84.7M ADA. Tickers: AMZ1, ANCO, AOTA, BOOM, ELLY7, FIDA, FIMI, GRAB, nan. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=FIMI, shared reward_addr=Yes, meta_domain=bit.ly, git.io, tinyurl.com.

**ISP** (WEP) — 6 live pools, 84.0M ADA. Tickers: CTAX, DGK, ISP, PSPJ, RANKT, WEP. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=WEP, shared reward_addr=Yes, meta_domain=bit.ly, ranket2.github.io.

**FREE** (ITC) — 5 live pools, 79.9M ADA. Tickers: ALLIN, FREE, ITC, ITC2, ITC3. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=ITC, shared reward_addr=Yes, meta_domain=git.io, raw.githubusercontent.com, tinyurl.com.

**HOPE** (JOY) — 9 live pools, 78.6M ADA. Tickers: CCJ, CCJ2, CCJ3, CCJ4, CCJ5, HOPE, HOPE2, JOY, JOY2. Sub-type: multi_brand_fleet. Capital class: sufficient.
_Signals:_ pool_group=JOY, shared reward_addr=Yes, meta_domain=cardano.ipclub29.com.

**Opaque Fleet**

**NORTH** (NORTH) — 5 live pools, 363.1M ADA. Tickers: NORTH. Sub-type: opaque_fleet. Capital class: sufficient.
_Signals:_ pool_group=NORTH, shared reward_addr=No, meta_domain=bit.ly.

**DIGI** (DIGI) — 6 live pools, 170.9M ADA. Tickers: DIGI, DIGI2, DIGI3, DIGI4, DIGI5, DIGI6. Sub-type: opaque_fleet. Capital class: sufficient.
_Signals:_ pool_group=DIGI, shared reward_addr=No, meta_domain=digi.pro.

**EDEN** (EDEN) — 5 live pools, 170.7M ADA. Tickers: EDEN. Sub-type: opaque_fleet. Capital class: sufficient.
_Signals:_ pool_group=EDEN, shared reward_addr=No, meta_domain=garden-pool.com.

### Capital-insufficient community fleets

**Community Branded Fleet**

**ATLAS** (ATLAS) — 2 live pools, 48.6M ADA. Tickers: ATLAS. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=ATLAS, shared reward_addr=Yes, meta_domain=atlasstakepool.com.

**STSH1** (AWP) — 3 live pools, 47.5M ADA. Tickers: STSH1, STSH2, STSH3. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=AWP, shared reward_addr=Yes, meta_domain=services.atomicwallet.io.

**SUNNY** (SUNNY) — 2 live pools, 45.3M ADA. Tickers: SUNNY. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=SUNNY, shared reward_addr=Yes, meta_domain=metadata.sunshinestakepool.com.

**HRMS** (HRMS) — 2 live pools, 44.3M ADA. Tickers: HRMS, nan. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=HRMS, shared reward_addr=Yes, meta_domain=hermes-stakepool.com.

**KIWI** (KIWI) — 3 live pools, 40.6M ADA. Tickers: KIWI, RAMEN. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=KIWI, shared reward_addr=Yes, meta_domain=tinyurl.com.

**ZETE** (ZETIC) — 2 live pools, 39.2M ADA. Tickers: ZETE, ZETE2. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=ZETIC, shared reward_addr=Yes, meta_domain=zetetic.tech.

**KTO** (KTO) — 10 live pools, 38.0M ADA. Tickers: CRBN, CRTR, KDK, KTO, MORH, MPOL, SMBU1, nan. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=KTO, shared reward_addr=Yes, meta_domain=agoodaycoffee.com, bit.ly, git.io, raw.githubusercontent.com, tinyurl.com.

**ADBV** (ADASTRONG_COM) — 2 live pools, 37.8M ADA. Tickers: ADAST, ADBV. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=adastrong.com, shared reward_addr=Yes, meta_domain=adastrong.com.

**4ADA** (4ADA) — 2 live pools, 37.8M ADA. Tickers: 4ADA, F4ADA. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=4ADA, shared reward_addr=Yes, meta_domain=staking4ada.org.

**NKR** (NKR) — 3 live pools, 36.1M ADA. Tickers: NKR, WWW, ZENA. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=NKR, shared reward_addr=Yes, meta_domain=git.io, raw.githubusercontent.com, tinyurl.com.

**KAIZN** (KAIZN) — 4 live pools, 34.5M ADA. Tickers: KAIZN, KOBE, KRONO, KRSNA. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=KAIZN, shared reward_addr=Yes, meta_domain=meta.pools.pm.

**MUEN** (MUEN) — 3 live pools, 34.2M ADA. Tickers: MUEN, MUEN2, MUEN3. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=MUEN, shared reward_addr=Yes, meta_domain=muen718.github.io.

**COFFE** (COFFEEPOOL_JP) — 2 live pools, 33.7M ADA. Tickers: COFFE, KISSA. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=coffeepool.jp, shared reward_addr=Yes, meta_domain=coffeepool.jp.

**ELITE** (ELITE) — 2 live pools, 31.9M ADA. Tickers: ELITE. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=ELITE, shared reward_addr=Yes, meta_domain=elitestakepool.com.

**WAFFLEPOOL_ORG** (WAFFLEPOOL_ORG) — 2 live pools, 31.8M ADA. Tickers: WFFL, nan. Sub-type: community_branded_fleet. Capital class: insufficient.
_Signals:_ pool_group=wafflepool.org, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com, wafflepool-cardano.github.io.

**Protocol/DeFi Project**

**LQWD** (LIQWID) — 2 live pools, 47.4M ADA. Tickers: LQWD. Sub-type: protocol_project. Capital class: insufficient.
_Signals:_ pool_group=LIQWID, shared reward_addr=Yes, meta_domain=lqwdpool.s3.amazonaws.com.

**XRAY1** (RAY) — 8 live pools, 45.7M ADA. Tickers: XRAY1, XRAY2, XRAY3, XRAY4, XRAY5, XRAY6, XRAY7, XRAY8. Sub-type: protocol_project. Capital class: insufficient.
_Signals:_ pool_group=RAY, shared reward_addr=Yes, meta_domain=xray.app.

**IBEX** (IBEX) — 3 live pools, 44.3M ADA. Tickers: BASHO, IBEX, RKD. Sub-type: protocol_project. Capital class: insufficient.
_Signals:_ pool_group=IBEX, shared reward_addr=Yes, meta_domain=ada.ibexpool.com, ibexpool.com.

**DNEWS** (DNEWS) — 2 live pools, 39.7M ADA. Tickers: DNEWS. Sub-type: protocol_project. Capital class: insufficient.
_Signals:_ pool_group=DNEWS, shared reward_addr=Yes, meta_domain=raw.githubusercontent.com.


