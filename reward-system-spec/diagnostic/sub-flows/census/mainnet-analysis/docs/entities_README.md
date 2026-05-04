# Entities

This folder is the **centralised entity research** for the SPO Incentives analysis. It is referenced from pools distribution, operator-delegator distribution, and the main report.

## The landscape at a glance

The attribution engine identifies **83 attributed entities** (73 strict multi-pool fleets + 10 attributed single-pool operators)
controlling **449 productive pools** and **~16.24B ADA** — 75.5% of the 21.18B ADA productive set
actively staked at epoch 618. The remaining 25% sits in **2,097 single-pool
operators** (see `single-spo/`).

**By archetype:**

| Archetype | Entities | Description |
| --- | --- | --- |
| Community branded fleet | 43 | Visible brand, community-operated multi-pool sets |
| Independent MPO | 9 | Self-sovereign operators running multiple pools under one identity |
| Multi-brand fleet | 8 | Several pool brands traced to a single operator |
| CEX (exchange custody) | 6 | Retail ADA staked by exchange; delegation is not sovereign |
| IVaaS (institutional validator) | 5 | Staking-as-a-service for institutional clients |
| Opaque fleet | 4 | No public-facing brand; operator unknown |
| Protocol project | 4 | Protocol-adjacent projects staking treasury or ecosystem funds |
| Ecosystem steward | 3 | Founding entities (CF, Emurgo, IOG) |
| Platform / wallet | 2 | Wallet-mediated delegation (NuFi, Adalite) |
| Opaque / unresolved | 1 | Unclassified |

**By capital class:** 48 saturation-scale entities (could pledge at scale)
vs 37 sub-saturation (cannot). Of the 48 sufficient, 41 are
zero-pledge — a revealed preference, not a calibration gap.

Detailed per-entity narrative profiles are in
[`docs/mpo_entity_profiles.md`](docs/mpo_entity_profiles.md).
Per-entity research cards with web-sourced business context are in
[`profiles/`](profiles/).

## Layout

| Directory | Contents |
| --- | --- |
| `data/` | Machine-readable entity datasets — archetypes, pool mappings, health overview, summaries, capital status. |
| `docs/` | Narrative documentation — entity profiles grouped by archetype, deep-dive notes. |
| `figures/` | Generated visualisations — distribution charts, progression, stance, tier breakdowns. |
| `profiles/` | Per-entity markdown research cards (business model, product surface, web research). |
| `scripts/` | All entity-centric build scripts — attribution engine, archetype figures, tier/stance visuals. |
| `single-spo/` | The single-pool operator segment — the other side of the landscape. |

## Scripts

| Script | Purpose | Key inputs | Outputs |
| --- | --- | --- | --- |
| `build_mpo_entity_deep_dive.py` | Core entity attribution engine — matches pools to named entities via metadata/ticker/relay patterns. Fetches live data from Koios. | Live Koios API, `koios_pool_history_mainnet.csv` (pools-distribution) | `data/mpo_entity_pool_mapping_mainnet.csv`, `data/mpo_entity_summary_mainnet.csv`, `figures/mpo_entity_current_distribution_mainnet.png` |
| `build_mpo_archetype_figures.py` | Archetype-aware entity visualisations — current snapshot and historical progression. | `data/mpo_entity_*.csv`, `koios_pool_history_mainnet.csv` (pools-distribution) | `figures/mpo_entity_current_distribution_*.png`, `figures/mpo_entity_progression_*.png`, `figures/mpo_entity_stance_distribution_mainnet.png` |
| `build_mpo_tier_stance_entity_visual.py` | Tier × stance × entity breakdown. | `data/mpo_entity_pool_mapping_mainnet.csv`, `data/mpo_entity_archetypes.csv`, pool snapshot (pools-distribution) | `figures/mpo_tier_stance_entity_mainnet.png` |
| `build_mpo_non_compliant_entity_tier_distribution_visual.py` | Zero-pledge entity pool-tier distribution. | `data/mpo_entity_archetypes.csv`, `data/mpo_entity_pool_health_mainnet.csv`, pool snapshot (pools-distribution) | `figures/mpo_non_compliant_entity_tier_distribution_mainnet.png` |
| `build_entity_profiles.py` | Generates per-entity profile cards from reward-split snapshot + archetypes. | `reward_split_snapshot.csv` (operator-delegator), `data/mpo_entity_archetypes.csv` | `data/entity_profile_hollow_competitive.csv` |

## Data files

| File | Description | Epoch |
| --- | --- | --- |
| `mpo_entity_archetypes.csv` | Entity → archetype classification with reasoning | 618 |
| `mpo_entity_archetypes_updated.csv` | Updated archetype classification | 618 |
| `mpo_entity_pool_mapping_mainnet.csv` | Pool → entity mapping (all attributed pools) | 618 |
| `mpo_entity_summary_mainnet.csv` | Per-entity summary metrics | 618 |
| `mpo_entity_health_overview_mainnet.csv` | Per-entity health status across categories | 618 |
| `mpo_entity_pool_health_mainnet.csv` | Pool-level health details for entity pools | 618 |
| `mainnet_entity_owner_capital_status_quo.csv` | Scale class classification | 618 |
| `entity_profile_hollow_competitive.csv` | Entity profile cards for hollow × competitive cell | 618 |

## Cross-references

Several scripts in `sub-flows/pools-distribution/mainnet-analysis/scripts/`
consume entity data from this folder (via `ENTITY_DATA` path). The entity
data is authoritative here; pools-distribution scripts read it, not the
reverse.

> **Status** — Last updated 2026/04/08. Snapshot epoch: 618.
