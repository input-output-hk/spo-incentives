# Cardano Infrastructure Topology — Concentration Findings

## Executive summary

This pass resolves every registered relay endpoint across the full Cardano
pool population to its hosting provider, ASN, country, and cloud region. The
motivation is the linear-Leios EB voting threshold from CIP-0164. The CIP
leaves the certification threshold &tau; as a governance parameter, but its
own security analysis states verbatim: *"a 26% stake attacker can trivially
attack Leios throughput with a 75% certification threshold."* The
operational reading: with the illustrative &tau;=75%, any failure domain
encompassing &ge;26% of total productive voting stake is a liveness risk.

**No single cloud region holds more than ~5% of total productive stake.** The
largest regional concentration is **GCP europe-west3 (Frankfurt) at 4.67%**,
dominated by Coinbase. AWS ap-northeast-1 (Tokyo) follows at 4.06%;
ap-northeast-2 (Seoul), eu-north-1 (Stockholm), eu-west-1 (Ireland), and
Azure westeurope (Amsterdam) all sit between 2.5 - 3.2%. A single-region
outage cannot by itself threaten the 75% EB quorum.

Provider-level shares are higher: **AWS 22.7%, OVH 11.9%, GCP 11.6%, Hetzner
6.0%, Contabo 4.7%, Azure 4.0%, DigitalOcean 2.4%** of total productive
stake. Hyperscalers together carry 40% of stake; the commodity-VPS layer
carries another 31%. A coordinated outage of AWS + GCP + Azure would silence
~38% of voting power and cross the 25% threshold.

Coverage: **2,915 active pools / 21.13B ADA** — the entire active Cardano
pool population, made up of **85 MPO entities** (~15.76B ADA) plus the long
tail of **2,072 single-pool operators** (~5.39B ADA). All percentages in
this document are computed against this full base unless stated otherwise.

### Concentration at a glance

| Dimension | HHI | Effective number of domains | Top-1 share | Grade |
|---|---:|---:|---:|---|
| Provider | 1,267 | 10.97 | 22.71% | low |
| Region | 449 | 38.16 | 12.73% | low |
| Physical country | 1,074 | 13.89 | 20.43% | low |
| Tier (hyperscaler / commodity-VPS / on-prem) | 2,999 | 3.79 | 40.11% | high |

The provider, region, and physical-country dimensions are antitrust-low
concentration. The tier dimension is high-concentration: ~97% of stake sits
in just three structural layers, so the shared-fate posture is concentrated
even when no individual provider is.

## Method

Pool data is pulled fresh from the public Koios `/pool_list` endpoint (every
active pool's relay set, active stake, ticker, and metadata URL). MPO entity
attribution is layered on top via the diagnostic repo's curated mapping;
pools not in the mapping are self-attributed as single-pool operators.

DNS names are forward-resolved via `socket.getaddrinfo`; every unique IP is
reverse-resolved (PTR) via `dig` against 1.1.1.1, then queried in bulk
against Team Cymru's WHOIS service for ASN, country, and BGP prefix.

Provider attribution combines four signals in priority order: PTR-pattern
matching first (most specific — e.g., `*.eu-west-1.compute.amazonaws.com`
yields AWS + region), then a curated ASN-to-provider lookup, then AS-name
keyword matching. Region attribution uses the AWS PTR for Amazon endpoints,
Google's published `cloud.json` IP-range manifest for GCP, Microsoft's
`ServiceTags_Public` JSON for Azure, and MaxMind GeoLite2-City for OVH /
Hetzner / Contabo / Leaseweb / WorldStream city resolution. A pool's stake
is split evenly across the distinct (provider, region) labels its relays
resolve to, so totals sum to ~100% without double-counting multi-provider
pools.

## Hyperscaler vs commodity vs residential

| Tier | Stake (B ADA) | Share | Entities |
|---|---:|---:|---:|
| Hyperscaler (AWS / GCP / Azure / Oracle / Huawei / Alibaba) | 8.48 | 40.1% | 469 |
| Commodity VPS / bare-metal (OVH / Hetzner / DO / Contabo / Vultr / Leaseweb / Cherry / IONOS / MEVspace / WorldStream / Hostinger / HostHatch / Servers.com / Akamai-Linode) | 6.61 | 31.2% | 868 |
| Other / on-prem (small ASNs, regional hosters, business broadband) | 4.02 | 19.0% | 816 |
| Unresolved (registered relays with no live DNS) | 1.42 | 6.7% | 419 |
| Residential / satellite ISPs (Green.ch / Cogeco / Sunrise / Starlink) | 0.61 | 2.9% | 14 |
| Edge / CDN (Cloudflare) | 0.01 | 0.03% | 6 |

Adding the long tail of single-pool operators on top of the MPO base lowers
the hyperscaler share (single-pool operators run far more on Hetzner /
Contabo / OVH / self-hosted than on AWS / GCP / Azure) and grows the
commodity-VPS slice. The 19% "other / on-prem" is dominated by small ASNs
that don't map to a recognised commercial hoster — bare-metal in residential
or business broadband, regional hosters, and operators behind generic
colocation.

## Single-provider exposure

| Provider | Stake (B ADA) | Share | Entities | Top entities exposed |
|---|---:|---:|---:|---|
| AWS | 4.80 | 22.7% | 249 | Coinbase, CHUCK BUX, Binance, Upbit, YUTA, Adalite, StakeBowl |
| OVH | 2.53 | 11.9% | 120 | Kiln, 1PCT, Emurgo, Everstake (partial) |
| GCP | 2.45 | 11.6% | 145 | Coinbase, Wave, Blockdaemon, NuFi |
| Hetzner | 1.28 | 6.0% | 197 | long tail of single-pool operators |
| Contabo | 0.99 | 4.7% | 276 | NuFi (partial), many single-pool operators |
| Azure | 0.85 | 4.0% | 45 | eToro |
| DigitalOcean | 0.50 | 2.4% | 194 | Bloom, long tail |
| Green.ch | 0.47 | 2.2% | 4 | Cardano Foundation |
| IONOS | 0.33 | 1.6% | 51 | AdaOcean (partial) |
| Oracle Cloud | 0.32 | 1.5% | 31 | Binance (small) |
| Vultr / Choopa | 0.30 | 1.4% | 41 | various |
| WorldStream | 0.20 | 0.9% | 2 | Everstake (partial) |
| Leaseweb | 0.19 | 0.9% | 2 | Everstake (partial) |
| Cogeco (CA cable ISP) | 0.14 | 0.6% | 4 | BigLazyCat |

A complete AWS outage would silence ~23% of total productive stake — sitting
right at the 25% threshold for EB quorum. A coordinated AWS + GCP outage
(~34%) would cross it comfortably. OVH at 12% is the largest single-provider
exposure outside the hyperscalers — a France-wide OVH incident would
matter, though OVH's stake is more geographically dispersed across Roubaix,
Strasbourg, Beauharnois, Frankfurt, and Montréal.

## Hyperscaler region exposure — the Leios-specific cut

| Region | Stake (B ADA) | Share | Entities |
|---|---:|---:|---:|
| gcp:europe-west3 (Frankfurt) | 0.99 | 4.67% | 6 |
| aws:ap-northeast-1 (Tokyo) | 0.86 | 4.06% | 24 |
| aws:ap-northeast-2 (Seoul) | 0.67 | 3.19% | 4 |
| aws:eu-north-1 (Stockholm) | 0.63 | 3.00% | 2 |
| aws:eu-west-1 (Ireland) | 0.62 | 2.92% | 15 |
| azure:westeurope (NL / Amsterdam) | 0.52 | 2.47% | 10 |
| aws:eu-central-1 (Frankfurt) | 0.41 | 1.95% | 20 |
| gcp:europe-west2 (London) | 0.31 | 1.44% | 4 |
| gcp:europe-west4 (NL / Eemshaven) | 0.25 | 1.16% | 8 |
| aws:ap-south-1 (Mumbai) | 0.23 | 1.10% | 9 |
| gcp:asia-northeast1 (Tokyo) | 0.22 | 1.06% | 8 |
| azure:eastus2 (Virginia) | 0.21 | 1.01% | 8 |
| gcp:us-east4 (Virginia) | 0.20 | 0.96% | 2 |
| aws:ap-southeast-2 (Sydney) | 0.18 | 0.87% | 10 |
| aws:us-east-2 (Ohio) | 0.16 | 0.77% | 67 |

Three observations on the regional cut. The top regional concentrations
cluster around Frankfurt, Tokyo, Seoul, Stockholm, Ireland, and Amsterdam —
each within a couple percentage points of the others, each dominated by one
or two entities. A region-level outage is primarily a **single-entity**
event, not a multi-tenant collapse.

Coinbase deliberately spans **six distinct hyperscaler regions across two
providers** (AWS Tokyo / Ireland / Frankfurt; GCP europe-west3, asia-east2,
and others) — its Leios-vote liveness is structurally the most resilient.

The fragile single-region operators are still the same names from the
MPO-only cut: **Upbit** sits almost entirely in AWS Seoul (ap-northeast-2),
**CHUCK BUX** mostly in AWS Stockholm (eu-north-1), and **eToro** entirely
in Azure westeurope.

## Sensitivity to the stake-attribution rule

Every percentage above uses an **even-split** rule: a pool that registers
relays at AWS and Hetzner contributes 50/50 to each, so totals sum to
~100%. To verify the headline numbers are not artefacts of that rule, the
same metrics are re-computed under two alternatives: **majority** (entire
pool stake assigned to the most frequent label among its relays) and
**any-exposure** (pool stake counted in every distinct label it touches —
totals can exceed 100%, useful for "how much stake is at risk if X goes
down").

| Dimension | Key | Even-split | Majority | Any-exposure |
|---|---|---:|---:|---:|
| tier | hyperscaler | 40.1% | 39.8% | 41.7% |
| tier | commodity-vps | 31.2% | 34.0% | 36.1% |
| tier | other-or-onprem | 19.0% | 16.9% | 23.7% |
| tier | unresolved | 6.7% | 6.5% | 7.0% |
| tier | residential/satellite | 2.9% | 2.9% | 2.9% |
| provider | AWS | 22.7% | 22.7% | 22.8% |
| provider | OVH | 11.9% | 14.6% | 16.4% |
| provider | GCP | 11.6% | 11.1% | 12.7% |
| provider | Hetzner | 6.0% | 6.6% | 8.1% |
| provider | Contabo | 4.7% | 6.5% | 7.9% |
| provider | Azure | 4.0% | 4.5% | 4.5% |

Headline numbers are robust: tier shares move by less than three points
across rules; AWS provider share is stable around 22-23%; OVH grows from
12% (even-split) to 16% (any-exposure) because OVH-multi-relay pools also
touch other providers. The any-exposure column is the appropriate read for
the Leios liveness question: even though only 22.7% of stake "belongs" to
AWS under even-split, 22.8% is **exposed** to an AWS outage under
any-exposure — essentially identical, meaning few multi-relay pools mix
AWS with non-AWS infrastructure as a real diversification.

## Cross-checks against curated MPO profiles

| Entity | Curated profile says | Topology pass observes | Verdict |
|---|---|---|---|
| Coinbase | Hidden behind bison.run / herd.run | 51% AWS (Tokyo / Ireland / Frankfurt) + 46% GCP (europe-west3) | Six hyperscaler regions, two providers: most resilient observed |
| Everstake | "Multi-cloud, geo-distributed bare-metal" | OVH 33% / WorldStream 33% / Leaseweb 33% | Multi-provider bare-metal: confirmed |
| Cardano Foundation | (not in curated profiles) | 100% Green.ch (Swiss bare-metal) | Single-provider, Swiss-resident |
| Kiln | "Institutional, dedicated infrastructure" | 95% OVH | Single-provider, French |
| Blockdaemon | "Multi-cloud, SOC 2 / ISO 27001" | 100% GCP on the registered relays | Profile claims wider scope than relays expose |
| Emurgo | (IOG sister entity) | 97% OVH | Single-provider, French |
| Figment | Institutional staking, 70+ PoS networks | 38 SRV records under `*.cardano.aeq5f.com`; none resolve in public DNS | Genuine DNS dead-end (intentional opaque routing) |

Two cross-check gaps are worth flagging. Blockdaemon's curated profile
states multi-cloud infrastructure, but its registered Cardano relays all
PTR-resolve under `*.bc.googleusercontent.com` — either the broader
infrastructure runs producers that are masked behind the GCP-facing relays,
or the Cardano product line specifically runs on GCP. Figment, after a fresh
Koios re-harvest, is confirmed to register 38 SRV records pointing at
`*.cardano.aeq5f.com` hosts that resolve to nothing in public DNS — this is
a deliberate opaque-routing posture, not a data-collection gap, and
Figment's 923M ADA is therefore unattributable from public-relay data alone.

## Joint-failure scenarios — spec-grounded

For each of eleven plausible failure scenarios, the table below reports the
fraction of total productive stake at risk under an *any-exposure* rule
(a pool counts as exposed if any of its registered relays sits inside the
scenario footprint). Scenarios marked BREACH cross the 26% spec-grounded
threshold from CIP-0164.

| Scenario | Stake at risk | % of total | Gap to 26% |
|---|---:|---:|---:|
| Joint hyperscaler outage (AWS + GCP + Azure) | 8.83B ADA | 41.75% | **BREACH −15.75** |
| Correlated AWS + GCP outage | 7.50B ADA | 35.48% | **BREACH −9.48** |
| Complete AWS unavailability | 4.83B ADA | 22.84% | +3.16 |
| Complete OVH outage | 3.48B ADA | 16.45% | +9.55 |
| GCP global IAM / control-plane outage | 2.69B ADA | 12.71% | +13.29 |
| OVH Strasbourg fire (physical FR only) | 2.62B ADA | 12.37% | +13.63 |
| Frankfurt metro-area outage (DE-CIX) | 2.39B ADA | 11.31% | +14.69 |
| Complete Hetzner outage | 1.72B ADA | 8.14% | +17.86 |
| Single-region worst case (GCP europe-west3) | 0.99B ADA | 4.67% | +21.33 |
| Azure westeurope outage | 0.65B ADA | 3.07% | +22.93 |
| AWS us-east-1 cascade | 0.26B ADA | 1.23% | +24.77 |

Two scenarios breach. **Complete AWS unavailability alone sits only 3.16
points below the line** — any concurrent failure in a second cloud or in
OVH pushes Cardano into the contested zone.

## Threshold sensitivity to the governance choice of τ

CIP-0164 does not bind &tau; to a numeric value. The table below shows which
scenarios breach across &tau; &isin; {60%, 70%, 75%, 80%, 90%}. The
adversarial threshold is (100 − &tau;).

| Scenario | τ=60% | τ=70% | τ=75% | τ=80% | τ=90% |
|---|---|---|---|---|---|
| Joint hyperscaler outage (AWS+GCP+Azure) | BREACH | BREACH | BREACH | BREACH | BREACH |
| Correlated AWS + GCP outage | +4.5 | BREACH | BREACH | BREACH | BREACH |
| Complete AWS outage | +17.2 | +7.2 | +2.2 | **BREACH** | BREACH |
| Complete OVH outage | +23.6 | +13.6 | +8.6 | +3.6 | BREACH |
| GCP global IAM outage | +27.3 | +17.3 | +12.3 | +7.3 | BREACH |
| Complete Hetzner outage | +31.9 | +21.9 | +16.9 | +11.9 | +1.9 |

At τ=80%, complete AWS alone breaches. At τ=90%, every major
provider-level outage breaches and even Hetzner sits 1.9 points over the
line. The choice of τ therefore directly trades off Leios safety against
single-provider liveness risk.

## MPO vs single-pool: the asymmetric cohort risk

The headline percentages mix MPO and single-pool stake. The two cohorts
cluster on radically different infrastructure:

| Provider | MPO % of MPO cohort | SPO % of SPO cohort | Asymmetry |
|---|---:|---:|---|
| AWS | 28.3% | 6.3% | MPO-heavy |
| GCP | 14.7% | 2.6% | MPO-heavy |
| OVH | 13.2% | 8.4% | balanced |
| Other / on-prem | 9.6% | 43.6% | SPO-heavy |
| Hetzner | 4.1% | 11.7% | SPO-heavy |
| Contabo | 3.2% | 9.2% | SPO-heavy |
| Azure | 4.7% | 1.9% | balanced |

**Within the MPO cohort alone, AWS holds 28.3% — already over the 26%
threshold.** Single-pool operators run mostly on Hetzner / Contabo / "Other
/ on-prem", which drags the network-wide AWS share down to 22.7%. The long
tail of single-pool operators is therefore a structural liveness asset, not
a decentralisation cost.

## Independent cross-validation

A Cexplorer.io report ([*Cardano infrastructure under
scrutiny*](https://cexplorer.io/article/cardano-infrastructure-under-scrutiny))
gives node-count shares of AWS 16%, Contabo 11%, DigitalOcean 10%, GCP 7%,
self-hosted 6.4%. This pass reports stake-weighted shares of AWS 22.7%,
OVH 11.9%, GCP 11.6%, Contabo 4.7%, DigitalOcean 2.4%. The differences are
**structurally consistent**: AWS and GCP host institutional MPOs with
concentrated stake, so their stake shares exceed their node shares. Contabo
and DigitalOcean host many small single-pool operators with low individual
stakes, so their node shares exceed their stake shares. This is exactly
the asymmetric-cohort effect made explicit in the MPO vs SPO table above.

## Design options for Leios + V2 incentives

1. **Choose τ with an explicit single-cloud safety target.** The
   τ-sensitivity table reads as a direct trade-off. τ=70% leaves a 7-point
   margin against complete-AWS outage; τ=80% reduces it to a BREACH.
   Governance should pick τ explicitly in awareness of the AWS dependency,
   not as a free parameter.

2. **Shared-fate-aware committee sortition.** Persistent + non-persistent
   voter selection is currently stake-weighted and infrastructure-blind. A
   version that down-weights candidate voters whose registered relays
   cluster on already-represented (provider, region) pairs would produce
   committees whose failure modes are de-correlated by construction.

3. **V2 reward modulation against hyperscaler concentration.** If the V2
   reward formula incorporates an infrastructure-diversity coefficient
   (bonus for pools whose registered relays span ≥2 providers, or penalty
   for top-1-provider concentration above a threshold), the incentive to
   diversify becomes direct. The provider-Shannon-entropy *H* computed in
   the profile-diff table is the natural metric.

4. **Transparency on producer-node location.** The 22.84% AWS exposure is
   computed from registered relays only. The actual producer location is
   hidden by every serious operator, so the true concentration could be
   higher or lower. A protocol-level requirement to declare the producer's
   ASN (in the pool registration certificate, hashed if privacy-sensitive)
   would let future analyses ground in producer reality rather than relay
   proxy.

5. **Protect the long tail.** The single-pool cohort's 43.6% "Other /
   on-prem" share is the most valuable diversification Cardano has. V2
   should explicitly recognise this and avoid changes that would push small
   operators into hyperscaler hosting (e.g., per-block compute requirements
   they can only afford on managed cloud).

## Interactive map artefact

A companion interactive Leaflet map is at
[`outputs/mpo_topology_map.html`](../outputs/mpo_topology_map.html). It
plots one pin per active pool with resolvable geography (2,429 of 2,915
pools), colour-coded by dominant provider and sized by log of active stake.
Click any pin to see entity, full provider mix, and registered relay
regions. The provider filter on the side panel toggles individual
provider categories on/off. The map opens directly in any modern browser.

## Implications for linear-Leios EB voting

Three failure modes are worth distinguishing.

Same-region outage (one hyperscaler region): worst case ~5% of total
productive stake silenced (GCP europe-west3 / Frankfurt, dominated by
Coinbase). Well below the 25% threshold. Leios EB voting continues. The
affected entity itself may halt — Upbit if Seoul falls, eToro if Azure
westeurope falls — but the network does not.

Single-provider outage (entire AWS, or entire GCP): AWS alone strips 22.7%
of total productive stake. GCP alone strips 11.6%. AWS alone sits *right
at* the 25% threshold — a second concurrent failure on top of an AWS
incident would tip the network into the contested zone. The any-exposure
cut tells the same story: 22.8% of stake is exposed to an AWS event.

Joint hyperscaler outage (AWS + GCP + Azure): combined hyperscaler share =
40% of total productive stake. A coordinated outage across the three would
silence well above the 25% threshold and stall EB voting. These events are
rare globally but not unprecedented at the regional or control-plane level —
AWS us-east-1 cascades have historically degraded GCP and Azure operations
through shared upstreams (BGP, DNS, certificate-authority dependencies).

The hyperscaler concentration matters less for *probable* outages — modern
cloud providers rarely fail globally — than for *correlated* ones, where one
operator's incident or a shared upstream (BGP route, root-DNS, certificate
authority) takes down peers simultaneously. The relevant risk metric is
therefore not regional concentration but the **shared-fate footprint**:
roughly two-fifths of total productive stake runs on top of a small number
of public-cloud control planes.

## Caveats

The registered-relay set is a public-facing surface. Most serious MPOs hide
their block-producing nodes behind these relays, often in different
facilities. Numbers above are a **lower bound** on operator-side
concentration.

The 6.7% "Unresolved" share is pools whose registered relays no longer
resolve (stale DNS or decommissioned endpoints). It is dominated by small
single-pool operators with stake under 1M ADA each, so the headline
percentages are not meaningfully shifted by it.

Country totals reflect IP-registration country, not physical datacentre.
Region-level numbers (AWS PTR-derived, GCP/Azure IP-range-derived) are the
more faithful physical-location read.

IPv6-only relays, producers behind Cloudflare-style fronting, and operators
running fully private DNS (like Figment's `*.cardano.aeq5f.com` SRV-only
setup) are invisible to this method.

## References

- Koios pool snapshot: [`data/koios_pool_list.json`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/koios_pool_list.json) (built by [`scripts/fetch_koios_pool_list.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/fetch_koios_pool_list.py))
- MPO entity mapping: [`data/mpo_entity_pool_mapping_mainnet.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_entity_pool_mapping_mainnet.csv)
- Per-endpoint output: [`data/mpo_relay_endpoints_resolved.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_relay_endpoints_resolved.csv)
- Concentration tables: `data/mpo_topology_concentration_by_{provider,tier,country,region}.csv`
- Entity profile diff: [`data/mpo_topology_entity_profile_diff.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_topology_entity_profile_diff.csv)
- Sensitivity table: [`data/mpo_topology_sensitivity.csv`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/data/mpo_topology_sensitivity.csv)
- Auto-generated raw tables: [`mpo_topology_tables_auto.md`](mpo_topology_tables_auto.md)
- Pipeline script: [`scripts/build_mpo_topology_concentration.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/build_mpo_topology_concentration.py)
- Sensitivity / profile-diff script: [`scripts/build_mpo_topology_sensitivity.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/build_mpo_topology_sensitivity.py)
- Figure script: [`scripts/build_mpo_topology_figure.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/build_mpo_topology_figure.py)
- PDF script: [`scripts/build_mpo_topology_pdf.py`](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts/build_mpo_topology_pdf.py)
- ASN data: [Team Cymru bulk WHOIS](https://team-cymru.com/community-services/ip-asn-mapping/)
- GCP IP ranges: <https://www.gstatic.com/ipranges/cloud.json>
- Azure ServiceTags: download.microsoft.com (Microsoft public JSON)
- GeoLite2-City: MaxMind (free database via public mirror)
- MPO census narrative: [`README.md`](../README.md) in `mainnet-analysis/`
- MPO entity profiles: [`profiles/`](../profiles/) (Coinbase, Everstake, Kiln, Blockdaemon, etc.)
