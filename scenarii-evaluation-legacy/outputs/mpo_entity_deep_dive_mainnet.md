# MPO Entity Attribution Deep Dive (Mainnet)

_Snapshot built from live Koios data at epoch `618` on `2026-03-12 09:54 UTC` plus local historical pool history._

## Objective

Move from pool-level concentration toward entity-level concentration, while being explicit about what is proved, what is inferred, and what remains unresolved.

## Why this is hard

Cardano pool registration data does not contain a canonical `legal_entity_id` field. Multi-pool operator (MPO) analysis therefore has to reconstruct operator clusters from observable signals.

The document distinguishes four different outcomes:

| Outcome | Meaning | Example |
| --- | --- | --- |
| Declared MPO | Public brand appears directly in metadata, ticker families, and cross-source labels. | Binance, IOG, 1PCT |
| Opaque operational cluster | Pools are clearly linked operationally, but the public brand is muted or hidden. | Coinbase / bison.run |
| Provider / platform cluster | Common staking provider or wallet surface is visible, but not always one legal operator. | Figment, Kiln, NuFi, Adalite surface |
| Unresolved label | Third-party clustering says the pools belong together, but first-party evidence is weak. | CHUCK BUX |

## Evidence hierarchy used here

| Strength | What counts as evidence | How it is used |
| --- | --- | --- |
| Strong | First-party metadata domains, branded ticker family, branded relay DNS, shared reward address where public branding also exists | Enough to attribute a declared MPO |
| Medium | Convergent third-party labels across Koios, AdaStat, and BalanceAnalytics | Supports attribution or upgrades confidence |
| Medium | Shared hosted metadata / relay infrastructure with repeated hashed subdomains | Supports an operational cluster, not necessarily a legal-entity claim |
| Weak / excluded alone | Generic shorteners, generic code hosting, generic cloud buckets, common hosting platforms | Not used on their own to claim same entity |

## What I deliberately do not use alone

- `tinyurl.com`, `git.io`, `raw.githubusercontent.com`, and similar generic shorteners / code hosting.
- Shared hosting surfaces such as generic metadata platforms, unless a branded domain or cross-source group labels also exist.
- A single external group label with no supporting metadata, unless the cluster is kept explicitly in an unresolved bucket.

## Current distribution

- Koios supply used for percentages: **38.494B ADA**
- Declared MPO share captured in this document: **13.23%**
- Opaque operational clusters captured here: **7.95%**
- Provider / platform clusters captured here: **5.11%**
- Unresolved external-label clusters captured here: **2.18%**

![Current MPO entity distribution](../figures/mpo_entity_current_distribution_mainnet.png)

## Summary table

| Entity / cluster | Type | Active pools | Current stake (B ADA) | Current % supply | Epoch 400 % | Epoch 410 % | Epoch 584 % | Confidence | Why linked |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Coinbase / bison.run | Opaque operational cluster | 47 | 2.457 | 6.38% | 6.60% | 5.50% | 5.71% | Medium-High | The pools are tied together by hashed bison.run and herd.run metadata / relay hosts, while Koios and BalanceAnalytics surface the operator label as Coinbase. |
| CHUCK BUX | Unresolved external label | 15 | 0.839 | 2.18% | 0.00% | 0.03% | 1.99% | Low | The cluster is visible in BalanceAnalytics / Koios labels, but public first-party branding is weak or absent across most pools. |
| Figment | Provider cluster | 37 | 0.798 | 2.07% | 0.00% | 0.00% | 1.09% | Medium-High | Koios and BalanceAnalytics identify the cluster as Figment, while some external views surface Ledger as the client-facing brand on top of the same provider layer. |
| Kiln | Provider cluster | 11 | 0.699 | 1.82% | 0.66% | 0.72% | 1.56% | High | kiln.fi metadata and KILN tickers provide direct branding even where Koios groups them under an Adalite surface. |
| Binance | Declared MPO | 50 | 0.691 | 1.80% | 7.44% | 4.22% | 2.41% | High | BNP ticker family and Binance-branded metadata paths are first-party signals; Koios, AdaStat, and BalanceAnalytics all label the cluster as Binance. |
| Wave / Wavepool | Declared MPO | 17 | 0.623 | 1.62% | 2.44% | 2.39% | 1.60% | High | The operator is visible through wavepool.digital / wavemkr metadata, WAVE labels, and consistent third-party groupings. |
| Everstake | Declared MPO | 15 | 0.568 | 1.48% | 1.41% | 1.43% | 1.20% | High | everstake.one metadata plus EVRST / EVERS / ESTK ticker family provide direct brand continuity across pools. |
| Blockdaemon | Declared MPO | 15 | 0.561 | 1.46% | 1.31% | 0.93% | 1.50% | High | The cluster exposes cardano.blockdaemon.com metadata together with BD tickers and matching third-party labels. |
| Upbit | Declared MPO | 20 | 0.554 | 1.44% | 0.00% | 0.27% | 1.16% | High | The cluster is directly branded by UPBIT tickers and upbit.com metadata endpoints, with Koios / AdaStat corroboration. |
| eToro | Declared MPO | 12 | 0.472 | 1.23% | 1.49% | 1.48% | 1.17% | High | ETO* tickers, etoro-branded metadata, and matching Koios / AdaStat / BalanceAnalytics labels make this a straightforward attribution. |
| YUTA | Opaque operational cluster | 25 | 0.464 | 1.20% | 2.00% | 1.94% | 1.28% | Medium | The YUTA label links multiple domains and brands together across Koios / BalanceAnalytics, suggesting one managed umbrella rather than one public-facing brand. |
| Cardano Foundation | Declared MPO | 6 | 0.456 | 1.19% | 0.00% | 0.00% | 0.00% | High | CF tickers, cardanofoundation.org metadata, and a shared reward address make the attribution explicit. |
| NuFi | Provider cluster | 18 | 0.313 | 0.81% | 1.14% | 1.97% | 0.88% | High | NuFi metadata and NUFI ticker family make the provider explicit. |
| 1PCT | Declared MPO | 30 | 0.276 | 0.72% | 1.06% | 1.00% | 0.73% | High | 1PCT ticker family, 1percentpool.eu metadata, and convergence across all group-label sources make the cluster explicit. |
| Emurgo | Declared MPO | 11 | 0.272 | 0.71% | 1.30% | 1.43% | 0.74% | High | EMUR* tickers, pools.emurgo.io metadata, and third-party group labels all point to the same public brand. |
| Bloom | Declared MPO | 7 | 0.221 | 0.57% | 0.73% | 0.73% | 0.59% | High | Bloompool metadata and BLOOM labels provide first-party continuity. |
| AdaOcean | Declared MPO | 10 | 0.190 | 0.49% | 0.65% | 0.64% | 0.56% | High | OCEAN / OCEA ticker family and adaocean.com metadata align across the cluster. |
| Adalite platform cluster | Platform-mediated cluster | 3 | 0.158 | 0.41% | 0.40% | 0.40% | 0.41% | Low-Medium | The ADALITE label appears to aggregate pools exposed through a wallet / platform surface, including pools that are better attributed to brands like Kiln or NuFi. |
| StakeBowl | Opaque operational cluster | 9 | 0.140 | 0.36% | 0.15% | 0.15% | 0.18% | Medium | SBP1 and SBP2 share the same reward address, relay endpoint, paired neoply.io metadata paths, and a stable STBL grouping, which together indicate one operator cluster historically surfaced as StakeBowl. |
| P2P | Declared MPO | 6 | 0.101 | 0.26% | 0.16% | 0.14% | 0.38% | High | P2P / PPCX tickers and p2p.org / p2p.world metadata make the provider explicit. |
| Spire | Declared MPO | 5 | 0.097 | 0.25% | 0.21% | 0.21% | 0.23% | High | spirestaking.com / spireblockchain.com metadata and SPIRE labels show direct public continuity. |
| IOG | Declared MPO | 9 | 0.013 | 0.03% | 0.72% | 0.72% | 0.57% | High | IOG pools publicly identify through IOG tickers, iohk.io / iog.io domains, and branded relay hostnames. |

## Detailed profiles

### Coinbase / bison.run

- Type: **Opaque operational cluster**
- Visibility: **Hidden behind hosted metadata / relay infrastructure**
- Claim level: **Same operational cluster**
- Confidence: **Medium-High**
- Live active pools: **47** out of **89** matched pool ids
- Live active stake: **2.457B ADA** (**6.38%** of Koios supply)
- Historical markers: epoch 400 = **6.60%**, epoch 410 = **5.50%**, epoch 584 = **5.71%** of supply
- Deduction: The pools are tied together by hashed bison.run and herd.run metadata / relay hosts, while Koios and BalanceAnalytics surface the operator label as Coinbase.
- Caution: This is strong evidence of common operational control, but the legal attribution to Coinbase comes from third-party group labels rather than first-party pool metadata.
- Tickers seen: N/A (16), RRC (1), OOH (1), TIA (1), CVM (1), GCN (1)
- Metadata domains: 33cb114a.cardano-metadata.bison.run (1), ranchcrypto.io (1), 53e378bf.cardano-metadata.bison.run (1), 3b92579e.cardano-metadata.bison.run (1)
- Koios `pool_group`: COINBASE (46)
- AdaStat group: n/a
- BalanceAnalytics group: COINBASE (44)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: 49.206.31.38 (2), 33cb114a.cardano-relay.bison.run (1), 53e378bf.cardano-relay.bison.run (1), 3b92579e.cardano-relay.bison.run (1)
- Example pools: pool12m7z9p7jqymxrvvp6z7vmfdu6j6u6y43p0m6y4xalz43sc8s4t9, pool197na7w0h8hjc8wdvwys7nsalhtpctefa3m23udeqxpfk6nzq8l9, pool1fl20ddkpvnstlx63fal6e3ku46r76nk2s4mqtk5jnyxn2vt7hg6

### CHUCK BUX

- Type: **Unresolved external label**
- Visibility: **External label only**
- Claim level: **Unresolved cluster label**
- Confidence: **Low**
- Live active pools: **15** out of **17** matched pool ids
- Live active stake: **0.839B ADA** (**2.18%** of Koios supply)
- Historical markers: epoch 400 = **0.00%**, epoch 410 = **0.03%**, epoch 584 = **1.99%** of supply
- Deduction: The cluster is visible in BalanceAnalytics / Koios labels, but public first-party branding is weak or absent across most pools.
- Caution: This cluster is important economically but should not be overclaimed as a proved single legal entity from the raw data alone.
- Tickers seen: STKD (1)
- Metadata domains: git.io (1)
- Koios `pool_group`: CHUCK BUX (17)
- AdaStat group: stake1u8ww9v63kydymm7hslk4mxyte36str9ehdz06lzsu5r4jlq0e2shk (2)
- BalanceAnalytics group: CHUCK BUX (17)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: cardano.staked.cloud (1), 25.cardano.staked.cloud (1), 26.cardano.staked.cloud (1), 27.cardano.staked.cloud (1)
- Example pools: pool1r99a6puhdv2xzcfw05jjqvks3xhmy2l4wsndx9hmhudvu4yevz5, pool1vhz87537anw4u0ruqsyuftyh7zxnrxptr4nnv0m6mjgeu8kp83z, pool1yafxktvszg85t5m20l8q8sufgcae6cxlk8cx96wrt8cdva7aknf

### Figment

- Type: **Provider cluster**
- Visibility: **Provider-mediated cluster**
- Claim level: **Same provider cluster**
- Confidence: **Medium-High**
- Live active pools: **37** out of **38** matched pool ids
- Live active stake: **0.798B ADA** (**2.07%** of Koios supply)
- Historical markers: epoch 400 = **0.00%**, epoch 410 = **0.00%**, epoch 584 = **1.09%** of supply
- Deduction: Koios and BalanceAnalytics identify the cluster as Figment, while some external views surface Ledger as the client-facing brand on top of the same provider layer.
- Caution: This looks like a common managed-staking provider cluster; the end-client retail brand is not always the same as the operator brand.
- Tickers seen: FGMTD (2), zzcf1 (1), gjp7a (1), BTV1 (1), BTV2 (1), BTV3 (1)
- Metadata domains: pcpm.s3.amazonaws.com (37), figment.io (1)
- Koios `pool_group`: FIGMENT (37)
- AdaStat group: ledger.com (37)
- BalanceAnalytics group: FIGMENT (9), SINGLEPOOL (1)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: relays-1a.cardano.figment.io (1), relays-1b.cardano.figment.io (1)
- Example pools: pool19yzqr3meksnvzdxh5xf6aknfhldyqdj7eaquxgcjva4mzt5kg3v, pool1f2wfjqkf2wx6jq93pdck6hgmy9zgw32lmvrq9zejl7scqxjqfze, pool1ra2su7cvnmr83pu9nvvz4a9carsgc9egc3e5fuk7h9pycyp5ela

### Kiln

- Type: **Provider cluster**
- Visibility: **Open provider brand**
- Claim level: **Same provider cluster**
- Confidence: **High**
- Live active pools: **11** out of **11** matched pool ids
- Live active stake: **0.699B ADA** (**1.82%** of Koios supply)
- Historical markers: epoch 400 = **0.66%**, epoch 410 = **0.72%**, epoch 584 = **1.56%** of supply
- Deduction: kiln.fi metadata and KILN tickers provide direct branding even where Koios groups them under an Adalite surface.
- Caution: Some third-party sources place these pools under ADALITE, so the provider brand and platform surface should not be conflated.
- Tickers seen: KILN0 (1), KILN1 (1), KILN2 (1), KILN3 (1), KILN4 (1), TW001 (1)
- Metadata domains: tinyurl.com (11)
- Koios `pool_group`: ADALITE (10)
- AdaStat group: kiln.fi (9)
- BalanceAnalytics group: ADALITE (9)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: relay-kiln-0-0.cardano.mainnet.kiln.fi (1), relay-kiln-0-1.cardano.mainnet.kiln.fi (1), relay-kiln-0-2.cardano.mainnet.kiln.fi (1), relay-kiln-1-0.cardano.mainnet.kiln.fi (1)
- Example pools: pool1gaztx97t53k47fr7282d70tje8323vvzx8pshgts30t9krw62tm, pool1k3nkfa5ugavrpd9nwd3s6yyx454qxnquxwmux4rzfunl7q0z38t, pool10d6mmw3mn9ku3r7uqqye672dz3sv76lh5kvh5rdpr9l5ug5yknr

### Binance

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **50** out of **114** matched pool ids
- Live active stake: **0.691B ADA** (**1.80%** of Koios supply)
- Historical markers: epoch 400 = **7.44%**, epoch 410 = **4.22%**, epoch 584 = **2.41%** of supply
- Deduction: BNP ticker family and Binance-branded metadata paths are first-party signals; Koios, AdaStat, and BalanceAnalytics all label the cluster as Binance.
- Caution: Some historical pools are only weakly labeled in current snapshots, but the branded metadata paths keep the attribution stable.
- Tickers seen: BNP (77), IFS1 (1), KKS (1), BOOBS (1)
- Metadata domains: s3.amazonaws.com (32), s3-us-west-2.amazonaws.com (19), s3-ap-southeast-1.amazonaws.com (15), s3.us-east-2.amazonaws.com (15)
- Koios `pool_group`: BINANCE (96)
- AdaStat group: binance.com (93), infstones.com (2)
- BalanceAnalytics group: BINANCE (95), SINGLEPOOL (1)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: 54.84.119.195 (13), 52.6.109.221 (2), 170.106.9.190 (2), 170.106.160.40 (2)
- Example pools: pool1vkc0dvuf8rxrch87umfayacgglrh8f88ef0f64xrdue5u2xjwfm, pool1fd0q9h8974y6psejmzczlywy8fgxxy07rn2ynrwu734aqwq540p, pool1lnr8t7pxvq3vfg8c5lc7yjcq39haws4ntu28xpxzx4zyya9ntny

### Wave / Wavepool

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **17** out of **31** matched pool ids
- Live active stake: **0.623B ADA** (**1.62%** of Koios supply)
- Historical markers: epoch 400 = **2.44%**, epoch 410 = **2.39%**, epoch 584 = **1.60%** of supply
- Deduction: The operator is visible through wavepool.digital / wavemkr metadata, WAVE labels, and consistent third-party groupings.
- Caution: A few pool tickers differ from the WAV* family, so the group label matters more than ticker uniformity.
- Tickers seen: WAVE (1), WAV2 (1), WAV6 (1), WAV4 (1), WAV8 (1), WAV9 (1)
- Metadata domains: meta.wavepool.digital (22), raw.githubusercontent.com (6), monitoring.wavelovelace.com (2), git.io (1)
- Koios `pool_group`: WAVE (18)
- AdaStat group: wavepool.digital (16), wavemkr.github.io (2)
- BalanceAnalytics group: WAVE (17), SINGLEPOOL (2)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: relays.wavepool.digital (22), relays.wavegp.com (5), relays.wavelovelace.com (2), relay1.cardanowave.com (1)
- Example pools: pool1l0m820vyqh5pp2yzpw973qzz23neqqd977u0uczh9fs9zqvg0je, pool1ljqjqskd4f4zekzddw204u5xtzhyz2cllq5v5dmn27zdwf9c70f, pool1w4cetqsly2cz9fq2te95tnk2r56mh6ew6dmpyfctv2ldv8xuj9g

### Everstake

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **15** out of **16** matched pool ids
- Live active stake: **0.568B ADA** (**1.48%** of Koios supply)
- Historical markers: epoch 400 = **1.41%**, epoch 410 = **1.43%**, epoch 584 = **1.20%** of supply
- Deduction: everstake.one metadata plus EVRST / EVERS / ESTK ticker family provide direct brand continuity across pools.
- Caution: Some pools only keep the brand in metadata rather than in the group label.
- Tickers seen: EVE6 (2), EVRST (1), EVERS (1), ESTK (1), EVE (1), VRSTK (1)
- Metadata domains: everstake.one (15), git.io (1)
- Koios `pool_group`: EVE (15)
- AdaStat group: everstake.one (15)
- BalanceAnalytics group: EVE (11)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: cardano-main.everstake.one (16), cardano-main2.everstake.one (16), cardano-relay1.everstake.one (16), cardano-relay2.everstake.one (16)
- Example pools: pool1n0uxgs5qfk5n9xl7qvq9jt8zuu02cntrsjnjayjlqtejyffnemj, pool1sysgx87cwxnqy0pqn8g97gdhd0dmre9rw3jvpn2k7apuwa7cgkn, pool1zgxvcqf0dvh0ze56ev2ayjvuex3zdd3hgxzdrcezkx497mv3l7s

### Blockdaemon

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **15** out of **18** matched pool ids
- Live active stake: **0.561B ADA** (**1.46%** of Koios supply)
- Historical markers: epoch 400 = **1.31%**, epoch 410 = **0.93%**, epoch 584 = **1.50%** of supply
- Deduction: The cluster exposes cardano.blockdaemon.com metadata together with BD tickers and matching third-party labels.
- Caution: Some current rows no longer expose metadata, but the branding is consistent on the rest.
- Tickers seen: BD0 (1), BD1 (1), BD2 (1), BD3 (1), BD4 (1), CLS1 (1)
- Metadata domains: cardano.blockdaemon.com (9), pcpm.s3.amazonaws.com (1)
- Koios `pool_group`: BD (14), FIGMENT (1)
- AdaStat group: blockdaemon.com (8), ledger.com (1)
- BalanceAnalytics group: BD (15)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: bd-cardano-main-relay-5-a.bdnodes.net (1), bd-cardano-main-relay-5-b.bdnodes.net (1), bd-cardano-main-relay-12-a.bdnodes.net (1), bd-cardano-main-relay-12-b.bdnodes.net (1)
- Example pools: pool1mfyzxyggryp0jhgghvzas7qjdyz2rcfnm5rfq8s9uefvukrlps5, pool1xsj9s3mfpztls97x7jjql0msmeh5v3wa5vyqhmmmsx8jzsqxrsv, pool1zgjk3dzwcwd02juqntuzknr368hvxjxy8l8uzkxvgu4252d7ekf

### Upbit

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **20** out of **20** matched pool ids
- Live active stake: **0.554B ADA** (**1.44%** of Koios supply)
- Historical markers: epoch 400 = **0.00%**, epoch 410 = **0.27%**, epoch 584 = **1.16%** of supply
- Deduction: The cluster is directly branded by UPBIT tickers and upbit.com metadata endpoints, with Koios / AdaStat corroboration.
- Caution: None beyond normal snapshot limitations.
- Tickers seen: UPBIT (20)
- Metadata domains: staking-static.upbit.com (20)
- Koios `pool_group`: UPBIT (20)
- AdaStat group: upbit.com (15)
- BalanceAnalytics group: UPBIT (10)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: cardano-relay-1.upbit.com (20), cardano-relay-2.upbit.com (20), cardano-relay-3.upbit.com (20)
- Example pools: pool1ua5exfeju4jc95yy595cykjh4x46998g8hrrvw2v5h9k7987a44, pool1sjnh0ymk9fhhnusm7uksux5yhpfyhjfmseq5nuupsj6ezskc0pj, pool1r9kse9x8ja0ajkyw8w96zw5c2aqeey6j85nmyqxhwt0rs090fu4

### eToro

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **12** out of **24** matched pool ids
- Live active stake: **0.472B ADA** (**1.23%** of Koios supply)
- Historical markers: epoch 400 = **1.49%**, epoch 410 = **1.48%**, epoch 584 = **1.17%** of supply
- Deduction: ETO* tickers, etoro-branded metadata, and matching Koios / AdaStat / BalanceAnalytics labels make this a straightforward attribution.
- Caution: Some older rows are partially unlabeled, but the branded pools anchor the cluster.
- Tickers seen: ETO1 (1), ETO2 (1), ETO3 (1), ETO4 (1), ETO5 (1), ETO6 (1)
- Metadata domains: etoro-spo.github.io (14), bit.ly (7)
- Koios `pool_group`: ETORO (24)
- AdaStat group: etoro.com (24)
- BalanceAnalytics group: ETORO (16), SINGLEPOOL (1)
- Repeated reward addresses: 1 repeated addresses across the cluster
- Relay hints: 20.61.229.103 (14), 20.61.228.218 (14), 108.142.42.221 (14), 108.142.42.161 (14)
- Example pools: pool1xt7mjrtnsew3v33lu8sf93upf20sxhmcrfnpm82ra46yxk7uy45, pool16eua0zalaln7q0s9u7jzlyygqad0pu2l2qdxx8r8ueqrw2jdhqf, pool19l206haluae6wyzm7tjpt3gln9paa5m9s4fedec2u09fqz300ht

### YUTA

- Type: **Opaque operational cluster**
- Visibility: **Multi-brand operator cluster**
- Claim level: **Same managed cluster**
- Confidence: **Medium**
- Live active pools: **25** out of **29** matched pool ids
- Live active stake: **0.464B ADA** (**1.20%** of Koios supply)
- Historical markers: epoch 400 = **2.00%**, epoch 410 = **1.94%**, epoch 584 = **1.28%** of supply
- Deduction: The YUTA label links multiple domains and brands together across Koios / BalanceAnalytics, suggesting one managed umbrella rather than one public-facing brand.
- Caution: This is not a first-party self-declared umbrella. The attribution relies on third-party clustering plus repeated multi-brand grouping.
- Tickers seen: ZZZ (1), ZZZ3 (1), ZZZ2 (1), ZZZ4 (1), ZZZ5 (1), JAPAN (1)
- Metadata domains: coinzzz.jp (5), tokyostaker.com (5), katanapool.com (4), popool.net (4)
- Koios `pool_group`: YUTA (28)
- AdaStat group: coinzzz.jp (5), tokyostaker.com (5), katanapool.com (4)
- BalanceAnalytics group: YUTA (29)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: asia.jazzstakepool.net (4), 3.111.14.60 (4), asia-pacific-relay.jpn-sp.net (2), asia-pacific-japan.popsp.net (2)
- Example pools: pool1pvu2zdexh8wr4ggmuz90jvqrua6an43qj9m9urs785p8kwjzqwl, pool1k0xrqp03mn9u3q3sadndd6vu9udl5v38xpzyw0shm8sskuxw2av, pool14mm59ntjqzphjr6chrww639cdr3yjce4qcwzc5jkk38y22u7uc6

### Cardano Foundation

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **6** out of **6** matched pool ids
- Live active stake: **0.456B ADA** (**1.19%** of Koios supply)
- Historical markers: epoch 400 = **0.00%**, epoch 410 = **0.00%**, epoch 584 = **0.00%** of supply
- Deduction: CF tickers, cardanofoundation.org metadata, and a shared reward address make the attribution explicit.
- Caution: This is a governance / institutional cluster rather than a hidden operator cluster.
- Tickers seen: CF1 (1), CF2 (1), CF3 (1), CF4 (1), CF5 (1), CF6 (1)
- Metadata domains: mainnet.pool.cardanofoundation.org (6)
- Koios `pool_group`: cardanofoundation.org (6)
- AdaStat group: cardanofoundation.org (6)
- BalanceAnalytics group: n/a
- Repeated reward addresses: 1 repeated addresses across the cluster
- Relay hints: cf1r1.mainnet.pool.cardanofoundation.org (1), cf1r2.mainnet.pool.cardanofoundation.org (1), cf2r1.mainnet.pool.cardanofoundation.org (1), cf2r2.mainnet.pool.cardanofoundation.org (1)
- Example pools: pool18rjrygm3knlt67n3r3prlhnzcjxun7wa8d3l8w9nmlpasquv4au, pool1n6erydn8x79sa3fmrqmj7mcyqa9em5fppr447j6d9k0xwfl7sc5, pool1xmlq3sgssww6kwu8dupgxukzhlk77j40p9c4r3qux3j5z2ysk2c

### NuFi

- Type: **Provider cluster**
- Visibility: **Open provider brand**
- Claim level: **Same provider cluster**
- Confidence: **High**
- Live active pools: **18** out of **24** matched pool ids
- Live active stake: **0.313B ADA** (**0.81%** of Koios supply)
- Historical markers: epoch 400 = **1.14%**, epoch 410 = **1.97%**, epoch 584 = **0.88%** of supply
- Deduction: NuFi metadata and NUFI ticker family make the provider explicit.
- Caution: Some Koios labels group these pools under ADALITE, which appears to be a platform-level surface rather than a legal-entity claim.
- Tickers seen: NUFI (1), NUFI2 (1), NUFI3 (1), NUFI4 (1), NUFI5 (1), NUFI6 (1)
- Metadata domains: pools-meta.nu.fi (21), tinyurl.com (2), adalite.io (1)
- Koios `pool_group`: ADALITE (18)
- AdaStat group: nu.fi (18)
- BalanceAnalytics group: ADALITE (18)
- Repeated reward addresses: 2 repeated addresses across the cluster
- Relay hints: cardano-relays-1.nu.fi (23), cardano-relays-2.nu.fi (23), 54.228.75.154 (2), 34.249.11.89 (2)
- Example pools: pool15d62znf04qymt6ve536tt5y9ky979ly4um5zmgz9m850vu7wuv7, pool1f8erepj5w5nth5xfxgxnwpz59jzywt6zdwfr50jzjwfwksmg9ek, pool1qnrqc7zpwye2r9wtkayh2dryvfqs7unp99f2039duljrsaffq5c

### 1PCT

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **30** out of **31** matched pool ids
- Live active stake: **0.276B ADA** (**0.72%** of Koios supply)
- Historical markers: epoch 400 = **1.06%**, epoch 410 = **1.00%**, epoch 584 = **0.73%** of supply
- Deduction: 1PCT ticker family, 1percentpool.eu metadata, and convergence across all group-label sources make the cluster explicit.
- Caution: None beyond normal snapshot limitations.
- Tickers seen: 1PCT (3), 1PCT1 (3), 1PCT2 (3), 1PCT3 (3), 1PCT4 (3), 1PCT5 (3)
- Metadata domains: www.1percentpool.eu (28), www.epicpool.eu (1), 1pct.net (1), git.io (1)
- Koios `pool_group`: 1PCT (29)
- AdaStat group: 1percentpool.eu (28)
- BalanceAnalytics group: 1PCT (29), SINGLEPOOL (1)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: r1.1percentpool.eu (28), r2.1percentpool.eu (28), relay1.epicpool.eu (1), relay2.epicpool.eu (1)
- Example pools: pool1gclysx2h7fndj0jdajlmwvqr8q9tzu3rurjknacu0ff954fsg9a, pool1z7n2ruhmxmv77f6cqhd3wsy6774h2wuay77agxuf2y9mj8q55vw, pool1w8ham64lthvzzxzn5hknq4yrj8xt2nark409s2xmntlwvt4ag3r

### Emurgo

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **11** out of **48** matched pool ids
- Live active stake: **0.272B ADA** (**0.71%** of Koios supply)
- Historical markers: epoch 400 = **1.30%**, epoch 410 = **1.43%**, epoch 584 = **0.74%** of supply
- Deduction: EMUR* tickers, pools.emurgo.io metadata, and third-party group labels all point to the same public brand.
- Caution: Some BalanceAnalytics rows are sparse, but the branded metadata is enough on its own.
- Tickers seen: EMUR5 (3), EMUR6 (2), SWIM (1), EMUR (1), SWIM2 (1), SHARK (1)
- Metadata domains: pools.emurgo.io (18), swimmingpoolop.github.io (12), emurgo.github.io (9), kficz.github.io (2)
- Koios `pool_group`: EMURGO (13)
- AdaStat group: swimmingpoolop.github.io (11), emurgo.io (9), theswim.net (2)
- BalanceAnalytics group: EMURGO (24), SINGLEPOOL (2)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: relays.pools.emurgo.io (19), 141.95.64.58 (3), 141.95.64.50 (3), 51.195.91.118 (2)
- Example pools: pool1m0drnjxsvnlesq0rwmur2rh6lenuql57jfzd6cf6aegj2cv7ugy, pool192pfftt48zc4x5aellvpufk6l6zxllpldw0rx82vrhqrqfhhqs2, pool1pmm654jfx088td54ekkkd0j28x6r5gnjdhnutzggursrxjnpk2y

### Bloom

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **7** out of **12** matched pool ids
- Live active stake: **0.221B ADA** (**0.57%** of Koios supply)
- Historical markers: epoch 400 = **0.73%**, epoch 410 = **0.73%**, epoch 584 = **0.59%** of supply
- Deduction: Bloompool metadata and BLOOM labels provide first-party continuity.
- Caution: The public brand is smaller than the largest custodial clusters, but the identity evidence is clean.
- Tickers seen: BLOOM (8), IRISH (1), DARK (1), CWHP (1)
- Metadata domains: bloompool.io (10), raw.githubusercontent.com (1), t.co (1)
- Koios `pool_group`: BLOOM (7)
- AdaStat group: bloompool.io (6)
- BalanceAnalytics group: BLOOM (7)
- Repeated reward addresses: 1 repeated addresses across the cluster
- Relay hints: 157.245.228.134 (8), 159.89.120.164 (8), 209.97.186.44 (8), eu.bloompool.io (3)
- Example pools: pool13c9mnvfx4nvwvkszxcprwlv60fh3tteef50hhhv9yxptsua2v70, pool13crd2ljx87988umk22er6ynwadfwdqupdpcq6prc6v59z62kxse, pool12vs4c3cm0tr49c7alrevfs0xa5g3s4al4fn46h33e69uusat04v

### AdaOcean

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **10** out of **12** matched pool ids
- Live active stake: **0.190B ADA** (**0.49%** of Koios supply)
- Historical markers: epoch 400 = **0.65%**, epoch 410 = **0.64%**, epoch 584 = **0.56%** of supply
- Deduction: OCEAN / OCEA ticker family and adaocean.com metadata align across the cluster.
- Caution: Some pools use OCEA* suffixes instead of a single ticker family root.
- Tickers seen: SAFE (1), OCEAN (1), OCEA2 (1), OCEA3 (1), OCEA4 (1), OCEA5 (1)
- Metadata domains: adaocean.com (10), jolly-ocean-0bab2f303.azurestaticapps.net (1), cybercyclone.github.io (1)
- Koios `pool_group`: OCEAN (8), SAFEBLOCK (1)
- AdaStat group: adaocean.com (8)
- BalanceAnalytics group: OCEAN (8), SINGLEPOOL (2)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: relay1.adaocean.com (10), relay2.adaocean.com (10), relay3.adaocean.com (10), relay4.adaocean.com (10)
- Example pools: pool1ell3xjtspzzz4vtsatscan6rheltf7j3hh2s8qsam2h3jvcxzm9, pool1ctzja2cdwyeqnvehmrlclc5wrn9w9acwklk3acn73jrx56d66vs, pool1vc8jp7uagxgh8trzx7r260ndcydz89ges8sws05cyv7jj8q8gqs

### Adalite platform cluster

- Type: **Platform-mediated cluster**
- Visibility: **Platform-mediated cluster**
- Claim level: **Not asserted as same legal entity**
- Confidence: **Low-Medium**
- Live active pools: **3** out of **3** matched pool ids
- Live active stake: **0.158B ADA** (**0.41%** of Koios supply)
- Historical markers: epoch 400 = **0.40%**, epoch 410 = **0.40%**, epoch 584 = **0.41%** of supply
- Deduction: The ADALITE label appears to aggregate pools exposed through a wallet / platform surface, including pools that are better attributed to brands like Kiln or NuFi.
- Caution: This profile is shown to document ambiguity, not to claim one underlying legal entity.
- Tickers seen: n/a
- Metadata domains: n/a
- Koios `pool_group`: ADALITE (3)
- AdaStat group: n/a
- BalanceAnalytics group: ADALITE (3)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: 13.211.73.179 (1), 13.236.12.204 (1)
- Example pools: pool1r9fpxs4kcn80kylsjxs8tg3p50nk2s66qerfqtw4x70n5740nj9, pool1kmmahq4upmm5j8fkh3xa9vd7gdffkp8pd4axucfh4w4dw549yqe, pool1yraracv4ntq9azvjw2nkw8g4xluujalz8fpt2stz8rw6k0zueuv

### StakeBowl

- Type: **Opaque operational cluster**
- Visibility: **Muted public brand**
- Claim level: **Same operator cluster**
- Confidence: **Medium**
- Live active pools: **9** out of **10** matched pool ids
- Live active stake: **0.140B ADA** (**0.36%** of Koios supply)
- Historical markers: epoch 400 = **0.15%**, epoch 410 = **0.15%**, epoch 584 = **0.18%** of supply
- Deduction: SBP1 and SBP2 share the same reward address, relay endpoint, paired neoply.io metadata paths, and a stable STBL grouping, which together indicate one operator cluster historically surfaced as StakeBowl.
- Caution: The current live metadata is not explicitly stakebowl.io-branded, so the public brand continuity relies partly on historical registration metadata rather than on the current metadata host alone.
- Tickers seen: STBL3 (1), STBL2 (1), STBL1 (1), STBL4 (1), STBL5 (1), SBP1 (1)
- Metadata domains: stake-bowl.s3.us-west-2.amazonaws.com (5), d2x5gxgj1srogu.cloudfront.net (3), neoply.io (2)
- Koios `pool_group`: STBL (10)
- AdaStat group: neoply.io (10)
- BalanceAnalytics group: STBL (5), SINGLEPOOL (3), STAKEBOWL (2)
- Repeated reward addresses: 2 repeated addresses across the cluster
- Relay hints: 35.164.48.223 (5), 3.35.204.131 (3), 35.75.32.253 (2)
- Example pools: pool18gk8kvd9qf829nldqus92q9y640e6u0jdyfz04mmktwxvglgt06, pool1fpvs8h5q5kwpz4k2yd0vw90dgdxacr3ef508tzzewm0kysdt4eq, pool1m7eljcrzd593cawzwpts00mmnxnj52kr9da8r264r7c4kfd4m0h

### P2P

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **6** out of **10** matched pool ids
- Live active stake: **0.101B ADA** (**0.26%** of Koios supply)
- Historical markers: epoch 400 = **0.16%**, epoch 410 = **0.14%**, epoch 584 = **0.38%** of supply
- Deduction: P2P / PPCX tickers and p2p.org / p2p.world metadata make the provider explicit.
- Caution: None beyond normal snapshot limitations.
- Tickers seen: P2P (2), K8S (1), PPCX1 (1), PPCX2 (1), SHIB (1), PPCX3 (1)
- Metadata domains: cardano.p2p.org (5), k8s-pool.subnet.dev (1), static.cardano.p2p.world (1), git.io (1)
- Koios `pool_group`: P2P (6)
- AdaStat group: p2p.org (6)
- BalanceAnalytics group: P2P (3), SINGLEPOOL (1)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: 170.23.181.50 (6), 89.217.176.121 (4), relay1.ppcx1.mainnet.cardano.p2p.org (3), 130.162.35.253 (3)
- Example pools: pool1lu2luhmkyayq9njh848kfknn6evwzmn3gzsxar7z3sttg7grxcm, pool1c2wf97p3j9gfvfjshj99ufxerpy3aznm8tzr2fd0ua465s26th4, pool1x0qm7xsyh2za3ltprxsgael544je4hg8tc3q3v5gv232z8jt4wp

### Spire

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **5** out of **24** matched pool ids
- Live active stake: **0.097B ADA** (**0.25%** of Koios supply)
- Historical markers: epoch 400 = **0.21%**, epoch 410 = **0.21%**, epoch 584 = **0.23%** of supply
- Deduction: spirestaking.com / spireblockchain.com metadata and SPIRE labels show direct public continuity.
- Caution: The cluster spans two closely related branded domains, but both are clearly operator-controlled.
- Tickers seen: SPIRE (1), SPIR2 (1), DJED1 (1), NETA3 (1), NETA (1), NETA1 (1)
- Metadata domains: www.spirestaking.com (13), data.spireblockchain.com (7), data.spirestaking.com (2), bit.ly (2)
- Koios `pool_group`: SPIRE (6)
- AdaStat group: anetabtc.io (4), spirestaking.com (2)
- BalanceAnalytics group: SPIRE (5)
- Repeated reward addresses: 0 repeated addresses across the cluster
- Relay hints: c1r1.spirestaking.com (13), c1r2.spirestaking.com (13), r1.spireblockchain.com (6), r2.spireblockchain.com (3)
- Example pools: pool16agnvfan65ypnswgg6rml52lqtcqe5guxltexkn82sqgj2crqtx, pool1yj9xduuwzvdkcwm2mc9x893zq684x7pyah4ja8zmzplgvxz6wgk, pool1072lq3k32sfxs96s9qhrx3s9la2t68vrqwfsp7h9qnwk56yr2mv

### IOG

- Type: **Declared MPO**
- Visibility: **Open public brand**
- Claim level: **Same operator cluster**
- Confidence: **High**
- Live active pools: **9** out of **65** matched pool ids
- Live active stake: **0.013B ADA** (**0.03%** of Koios supply)
- Historical markers: epoch 400 = **0.72%**, epoch 410 = **0.72%**, epoch 584 = **0.57%** of supply
- Deduction: IOG pools publicly identify through IOG tickers, iohk.io / iog.io domains, and branded relay hostnames.
- Caution: None beyond normal snapshot limitations.
- Tickers seen: IOGP (34), IOG2 (2), IOHK (1), IOG1 (1), IOG3 (1), IOG4 (1)
- Metadata domains: pools.iohk.io (50), raw.githubusercontent.com (4), iog1.cardano.iog.io (1), iogp2.cardano.iog.io (1)
- Koios `pool_group`: IOG (35)
- AdaStat group: iohk.io (34)
- BalanceAnalytics group: IOG (35), SINGLEPOOL (3)
- Repeated reward addresses: 1 repeated addresses across the cluster
- Relay hints: relays-new.cardano-mainnet.iohk.io (59), iog1-relays.cardano.iog.io (1), 165.232.38.143 (1), iogp2-relays.cardano.iog.io (1)
- Example pools: pool1mxqjlrfskhd5kql9kak06fpdh8xjwc76gec76p3taqy2qmfzs5z, pool1lx7hdfz430vmrwhkrdgxu8c0xclffltavmkejpqzzz4ax0lnfvd, pool1vp5fev56urx924nyxj5qjvzcsh76e47c4lc8xruh0rdlv0n2kvt

## Hidden / unresolved side of the MPO problem

Not every economically significant cluster is self-declared. That is precisely why a Sybil / MPO lens matters: pool count alone can overstate decentralization if multiple pools are under one operational umbrella.

The unresolved list below keeps large third-party group labels separate when the public branding is too weak for a stronger same-entity claim.

| Unresolved label | Active pools | Current stake (B ADA) | Current % supply | Sample domains | AdaStat labels | BalanceAnalytics labels |
| --- | ---: | ---: | ---: | --- | --- | --- |
| NORTH | 5 | 0.367 | 0.95% | bit.ly (5) | nordicpool.org (5) | NORTH (5) |
| ADV | 4 | 0.264 | 0.69% | adavault.com (4) | adavault.com (4) | ADV (4) |
| SECUR | 5 | 0.236 | 0.61% | cardano.securestaking.io (5) | cardano.securestaking.io (5) | SECUR (5) |
| CRDNS | 9 | 0.228 | 0.59% | cardanians.io (7), 37.59.55.35 (1), pool.cardanoyoda.com (1) | cardanians.io (8) | CRDNS (8), SINGLEPOOL (1) |
| CCV | 5 | 0.178 | 0.46% | raw.githubusercontent.com (5) | ccv3000.github.io (5) | CCV (5) |
| DIGI | 6 | 0.171 | 0.44% | digi.pro (6) | digi.pro (6) | DIGI (6) |
| EDEN | 5 | 0.165 | 0.43% | garden-pool.com (5) | garden-pool.com (5) | EDEN (5) |
| MS | 4 | 0.156 | 0.40% | git.io (4) | moonstake.io (4) | MS (4) |
| DAPP | 8 | 0.141 | 0.37% | azureada.com (4), apexfusionhosting.com (3), www.threenext.com (1) | dappcentral.net (8) | AZUR (3), DAPP (3) |
| TITAN | 2 | 0.137 | 0.36% | www.titanstaking.io (2) | titanstaking.io (2) | TITAN (2) |

## Sybil / decentralization interpretation

- MPO concentration is not automatically a malicious Sybil attack. Exchanges, foundations, and providers can operate many pools for legitimate reasons.
- The decentralization problem appears when pool-level diversity is mistaken for operator-level diversity.
- Hidden or weakly branded clusters are the most concerning for measurement because delegators and researchers cannot audit unique control as easily.
- Platform clusters need extra care: a common wallet or staking surface can make several pools look like one entity even when they are not.

## Relationship to the progression chart

The historical concentration trend is covered separately in `../figures/mpo_entity_progression_stacked_mainnet.png`. The stacked view keeps the attribution layer visible over time, while this document focuses on **who** the clusters appear to be and **why** the linkage is credible or not.

![Historical MPO composition](../figures/mpo_entity_progression_stacked_mainnet.png)

## Bottom line

The strongest same-entity attributions are the openly branded MPOs where metadata domains, ticker families, and external group labels all converge. The next tier is opaque but operationally coherent clusters such as Coinbase / bison.run. Everything else should be kept explicitly qualified as provider-mediated, platform-mediated, or unresolved rather than folded into a single hard number without explanation.
