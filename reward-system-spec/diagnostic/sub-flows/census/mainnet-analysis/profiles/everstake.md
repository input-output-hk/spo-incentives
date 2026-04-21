# Everstake

> Archetype: **IVaaS** (Institutional Validator / Staking-as-a-Service)
> Website: [everstake.one](https://everstake.one)
> Attribution confidence: High (first-party metadata, branded tickers)

## Identity

Everstake Validation Services LLC, registered in Grand Cayman (Hermes Corporate Services Ltd.). Founded 2018 by Sergii Vasylchuk, a Ukrainian blockchain engineer (MSc Computer Science, Kyiv Polytechnic Institute) with 15+ years of industry experience. The company originated from Attic Lab, a blockchain development studio; the initial plan was a crypto exchange, but the team pivoted to PoS validation — first on EOS, then expanding rapidly across chains.

~100 employees, 75% engineers. Leadership: David Kinitsky (CEO, US operations), Bohdan Opryshko (COO), Iurii Tkachenko (CFO), Anna Petrenko (CBDO). Self-funded — no external venture capital rounds disclosed.

## Scale

| Metric | Value |
| --- | --- |
| Total staked value | $7B+ |
| Delegators (all chains) | 1.6M+ |
| Active validators | 40,000+ |
| PoS networks | 130+ |
| Uptime | 99.98% |
| Rewards generated | $700M+ |

## Products

| Product | Description | Audience |
| --- | --- | --- |
| Institutional staking | Multi-chain validator infrastructure | Custodians, exchanges, asset managers |
| Validator-as-a-Service (VaaS) | Managed validator operations | Institutions without in-house infra |
| Wallet SDK | API toolkit for staking integration | Wallet providers |
| Yield SDK | High-yield stablecoin vault integrations | DeFi / fintech |
| Midas | High-yield stablecoin vaults (midas.app) | Retail / institutional |
| SWQOS | Stake-weighted QoS for Solana | HFT / quant trading |
| ShredStream | Low-latency Solana data paths | Trading engines |

## Compliance and certifications

SOC 2 Type II, ISO 27001:2022, GDPR, NIST Cybersecurity Framework, CCPA/CRPA, ITGC. Multi-cloud, geographically distributed bare-metal infrastructure.

## Institutional partnerships

**Zodia Custody** (Standard Chartered subsidiary) — selected Everstake as validator partner for institutional staking on Cardano, Solana, and Polkadot (first tranche), with Ethereum, NEAR, and Babylon planned. Announced 2025/06.

**Taurus** (FINMA-regulated Swiss custody platform, 24+ global bank clients) — integrated Everstake into Taurus-PROTECT for staking on Cardano, Solana, NEAR, and Tezos. Announced 2025/12. This places Everstake as the back-end staking layer for regulated banks.

**Trezor** — integrated Solana staking via Everstake. Announced 2025/03.

These partnerships mean that institutional ADA entering through custody platforms (Zodia, Taurus) routes to Everstake pools without the end client selecting a pool directly. The delegation appears on-chain as retail-style individual delegation, but the source is institutional custody.

## Venture and governance footprint

**Everstake Capital** — early-stage blockchain VC arm (5 investments in 2024). Invests in blockchain startups and shares infrastructure expertise.

**Metaplex Foundation** — Vasylchuk serves as director of the Metaplex Foundation (Solana NFT protocol).

**Aid For Ukraine** — co-initiated with Ukraine's Ministry of Digital Transformation; raised $60M+ in crypto donations for Ukraine.

**Cardano DRep** — registered as Delegated Representative on Cardano (2025/08). Commits to data-driven, publicly documented governance voting. Non-custodial governance: delegation is independent from staking and reversible.

## Cardano presence

| Metric | Value |
| --- | --- |
| Pools | 15 active (10 in hollow × competitive cell) |
| Total delegated | ~572M ADA |
| Delegators | 258,456 |
| ADA / delegator | ~1,730 |
| Margin | 4.0% |
| Operator take | 6.8% |
| Fee | 4% |
| APR (advertised) | 2.1% |
| Custodial signal | **No** — genuine retail market |

Tickers: EVRST, EVERS, EVE, ESTK, VRSTK, RSTK, EVE1–EVE4, EVE6, EVE7. Metadata domain: everstake.one. Pool hash (reference): `ac2d2d66a30cbb3163e68a7073bcd3f9cdd4a11a8af6e2c5653402c7`.

Everstake is the largest retail-facing operator in the delegation market by delegator count. The 258K addresses averaging 1,730 ADA each are individual retail delegators choosing a pool — not managed institutional capital. The contrast with Coinbase (403 delegators, 6.1M ADA/deleg) or Blockdaemon (47 delegators, 6.1M/deleg) is the sharpest in the cell.

The 4.0% margin is above the cell median of 2.0%, yet delegation volume remains massive. This indicates delegators reach Everstake through wallet integrations and product UX (Wallet SDK, partner wallets) rather than fee comparison. The Zodia/Taurus partnerships could shift the delegation composition from retail to institutional over time, but this has not yet materialised on-chain at epoch 618.

## Historical trajectory

1.41% (ep.400) → 1.43% (ep.410) → 1.20% (ep.584) → **1.47%** (ep.618). Remarkably stable across 200+ epochs — the flattest trajectory among IVaaS entities. The slight dip at epoch 584 fully reversed.

## Pledge

0.57B ADA delegated / ~11M pledged = **51,000:1**. Near-zero self-pledge relative to managed stake — structural for IVaaS scale. Pledge economics are dominated by client custody architecture, not operator capital constraints.

## Analytical significance

Everstake occupies a unique position in the entity landscape: it is classified as IVaaS (institutional infrastructure), yet its on-chain Cardano footprint looks retail. The institutional custody partnerships (Zodia, Taurus) could change this — if bank-mediated ADA staking routes through Everstake pools at scale, the delegation profile would shift toward larger, fewer addresses with custodial characteristics. This makes Everstake a leading indicator for the institutional adoption thesis on Cardano.

The DRep registration adds a governance dimension. Unlike pure-play validators, Everstake is positioning itself as a governance participant — representing delegator interests in Cardano's on-chain governance. Whether this creates delegation stickiness or governance influence worth monitoring is an open question.

## Sources

Web research: everstake.one (homepage, /about, /staking/cardano, /products, /blog), 2026/04/08. Institutional partnership details from Everstake blog, The Block, Chainwire. On-chain data: epoch 618 snapshot.
