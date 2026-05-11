# MPO Infrastructure Topology — Concentration Findings

_Snapshot: derived from `mpo_entity_pool_mapping_mainnet.csv` (registered pools only)._

- Pools covered: **2915**, total active stake **21.15B ADA**
- Endpoint rows (pool, ip): **5643**

## Top providers (stake-split, %)

| Provider | Pools exposed | Stake (B ADA) | Stake share | Entities |
|---|---:|---:|---:|---:|
| AWS | 403 | 4.80 | 22.7% | 249 |
| Other / on-prem | 858 | 3.87 | 18.3% | 812 |
| OVH | 228 | 2.53 | 11.9% | 120 |
| GCP | 221 | 2.45 | 11.6% | 145 |
| Unresolved | 497 | 1.42 | 6.7% | 419 |
| Hetzner | 223 | 1.28 | 6.0% | 197 |
| Contabo | 314 | 0.99 | 4.7% | 276 |
| Azure | 68 | 0.85 | 4.0% | 45 |

## Top countries (stake-split, %)

| ISO2 | Pools exposed | Stake (B ADA) | Stake share | Entities |
|---|---:|---:|---:|---:|
| US | 1326 | 10.35 | 48.9% | 1018 |
| DE | 600 | 2.77 | 13.1% | 516 |
| FR | 216 | 2.31 | 10.9% | 119 |
|  | 532 | 1.65 | 7.8% | 453 |
| GB | 78 | 0.61 | 2.9% | 68 |
| CA | 118 | 0.60 | 2.8% | 100 |
| CH | 24 | 0.56 | 2.6% | 19 |
| AT | 92 | 0.55 | 2.6% | 81 |

## AWS regions (where PTR exposes region code)

| Region | Pools exposed | Stake (B ADA) | Stake share | Entities |
|---|---:|---:|---:|---:|
| aws:ap-northeast-1 | 40 | 0.86 | 4.1% | 24 |
| aws:ap-northeast-2 | 27 | 0.67 | 3.2% | 4 |
| aws:eu-north-1 | 11 | 0.63 | 3.0% | 2 |
| aws:eu-west-1 | 27 | 0.62 | 2.9% | 15 |
| aws:eu-central-1 | 29 | 0.41 | 2.0% | 20 |
| aws:ap-south-1 | 20 | 0.23 | 1.1% | 9 |
| aws:ap-southeast-2 | 12 | 0.18 | 0.9% | 10 |
| aws:us-east-2 | 77 | 0.16 | 0.8% | 67 |

## Method (one-paragraph)

Each registered pool's `relay_hints` (from the diagnostic mapping CSV) is parsed into a set of IPv4 / IPv6 / DNS endpoints. DNS names are forward-resolved via `socket.getaddrinfo`; every unique IP is then reverse-resolved (PTR) and queried against Team Cymru's bulk WHOIS for ASN, country, and BGP prefix. Provider attribution combines a PTR-pattern table (most specific) with an ASN-to-provider lookup (fallback) and AS-name keyword matching (last resort). AWS region is extracted from the PTR record when present. A pool's stake is split evenly across the distinct (provider, region) labels its relays resolve to, so totals sum to ~100%.

## Caveats

- Registered relays ≠ block-producing node. Most serious MPOs hide producers behind public-facing relays, often in different facilities. Numbers below are a **lower bound** on operator-side concentration.
- Multi-relay pools registering across providers get their stake split, so a pool that relays at AWS and Hetzner contributes 50/50.
- Cloudflare / generic CDN PTRs mask the real upstream; small fraction.
