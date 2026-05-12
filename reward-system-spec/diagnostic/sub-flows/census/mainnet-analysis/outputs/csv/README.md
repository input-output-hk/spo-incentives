# MPO Infrastructure Topology — CSV exports

The diagnostic's `data/` directory is gitignored project-wide, so the
analytical outputs are mirrored here for direct GitHub access (raw URLs work
for `pandas.read_csv()` and similar). All files are derived deterministically
from the Koios `/pool_list` snapshot via the pipeline scripts under
`../../scripts/`. Re-running `fetch_koios_pool_list.py` followed by
`build_mpo_topology_concentration.py all` regenerates them.

## File reference

| File | Rows | Purpose |
|---|---:|---|
| `mpo_relay_endpoints_resolved.csv` | 5,643 | One row per (pool, IP) endpoint. Per-row: pool_id, ticker, entity_id, display_name, category, cohort, current_active_stake_ada, IP, PTR, ASN, AS-name, BGP country, **physical_country** (region-derived), **provider** (PTR > ASN > AS-name keyword), **tier** (hyperscaler/commodity-VPS/...), **region** (`aws:eu-west-1`, `gcp:europe-west3`, `azure:westeurope`, `ovh:de:frankfurt_am_main`, etc.). The base table for any custom aggregation. |
| `mpo_topology_concentration_by_provider.csv` | 22 | Stake-weighted provider shares (even-split rule). |
| `mpo_topology_concentration_by_tier.csv` | 6 | hyperscaler / commodity-vps / on-prem / residential / unresolved / edge-cdn. |
| `mpo_topology_concentration_by_region.csv` | 70+ | Per-region exposure including AWS/GCP/Azure regions and OVH/Hetzner/Contabo cities. |
| `mpo_topology_concentration_by_country.csv` | 30+ | BGP-registration country (noisy for hyperscalers — see physical_country instead). |
| `mpo_topology_concentration_by_physical_country.csv` | 30+ | Country derived from cloud region (preferred). |
| `mpo_topology_concentration_index.csv` | 4 | HHI + effective-number-of-domains for provider, region, physical_country, tier. |
| `mpo_topology_failure_scenarios.csv` | 11 | Joint-failure scenarios with stake-at-risk under any-exposure rule, gap to 26% threshold. |
| `mpo_topology_tau_sensitivity.csv` | 5 | BREACH / margin per scenario across τ ∈ {60%, 70%, 75%, 80%, 90%}. |
| `mpo_topology_sensitivity.csv` | 26 | Same metrics under three stake-attribution rules (even-split / majority / any-exposure). |
| `mpo_topology_mpo_vs_spo.csv` | 22 | Per-provider stake split by MPO vs single-pool cohort. |
| `mpo_topology_entity_provider_matrix.csv` | 1,800+ | One row per (entity, provider) pair with stake-split ADA. |
| `mpo_topology_entity_profile_diff.csv` | 2,157 | Per-entity dominant provider/region, Shannon entropy of provider mix, full mix string. |

## Conventions

- All ADA values are in **ADA** (already divided by 1e6 from Koios lovelace).
- Stake percentages use the **even-split** rule unless the file name says otherwise: a pool whose registered relays span N distinct (provider, region) labels contributes 1/N of its stake to each. Totals sum to ~100% without double-counting multi-cloud pools. The any-exposure variant in the sensitivity table double-counts so totals exceed 100% — use it for "what's at risk if X fails".
- `region` labels: `aws:<region>`, `gcp:<region>`, `azure:<region-lowercased>` for hyperscalers; `ovh:<cc>:<city>`, `hetzner:<city>`, `contabo:<city>`, etc. for commodity-VPS; `cc:<ISO2>` fallback otherwise.
- `physical_country` is derived from the region (e.g., `aws:eu-west-1` → IE, `gcp:europe-west3` → DE) for hyperscaler endpoints, and from MaxMind GeoLite2-City for commodity-VPS endpoints.
- `cohort` = `mpo` (one of the 85 curated MPO entities) or `single_pool` (long tail).
- `category` matches the diagnostic's MPO census categories (`declared_brand`, `discovered_mpo`, `provider_cluster`, `opaque_operational`, `single_pool`, etc.).

## Snapshot

Built from Koios epoch 630 (2026/05/11). Total productive stake covered:
21.15B ADA across 2,915 active pools. z₀ (saturation point) = supply / k =
77.2M ADA at k=500.
