# Infrastructure Topology — Interactive Map

> **Status** · Live interactive view of the Cardano network's relay
> infrastructure, derived from a fresh Koios `/pool_list` snapshot enriched
> with PTR records, Team Cymru ASN attribution, GCP/Azure published IP-range
> manifests, and MaxMind GeoLite2-City. Companion deliverable to the
> [topology findings narrative](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/docs/mpo_topology_findings.md)
> and the [PDF report](MPO_infrastructure_topology.pdf).

The map covers the **full active Cardano pool population** — both the 83 MPO
entities and the long tail of single-pool operators — so any combination of
filters reads against the network, not against an arbitrary cohort.

## Quick orientation

Three orthogonal controls sit at the top of the map:

- **Browse** — *Entities* groups pools by operator (Coinbase = one pin);
  *Pools* shows every individual pool.
- **Cohort** — *All*, *MPO only*, or *Single-pool only*. Filters who is
  included.
- **Colour by** — *Provider*, *Infrastructure tier*, *Saturation tier*, or
  *Cohort*. Visual encoding only.

Plus two toggles: **Productive (≥ 3M only)** narrows to the diagnostic's
productive segment ([POL.O4.F2](../../pools-distribution/mainnet-analysis/README.md#414-pool-distribution-by-tier)
— 27% of pools, 96.6% of stake), and **Heatmap** overlays a stake-density
heat layer.

## Things to look for

- Switch *Browse* to **Entities** and *Cohort* to **MPO only** — every
  institutional operator collapses to one stake-weighted centroid pin. Click
  any of them to see the **fleet graph**: every one of that operator's pools
  rendered as a node with a line back to the centroid. Coinbase shows 48
  pools radiating from Frankfurt across Tokyo / Ireland / Mumbai. CHUCK BUX
  shows a Stockholm cluster.
- *Colour by → Saturation* applies the diagnostic's
  [9-tier taxonomy](../../pools-distribution/mainnet-analysis/README.md#413-tier-definitions)
  with z₀ = supply / k = 77M ADA. Red = saturated / oversaturated, green =
  healthy, amber/grey = sub-viable.
- *Cohort = Single-pool* + *Productive* filter narrows the 1,728 single-pool
  operators down to the 267 with ≥ 3M ADA — the consensus-relevant subset of
  the long tail.

## Map

<iframe src="mpo_topology_map.html"
        title="Cardano infrastructure topology — interactive map"
        style="width: 100%; height: 80vh; min-height: 700px; border: 1px solid #e5e5e5; border-radius: 4px;"
        loading="lazy"></iframe>

The map opens fullscreen at
[`mpo_topology_map.html`](mpo_topology_map.html) if the embedded view feels
cramped — same data, more screen real estate.

## Source data and reproducibility

- Snapshot: Koios epoch 630 (2026/05/11). Total productive stake covered:
  **21.15B ADA** across **2,915 active pools**.
- z₀ = supply / k = **77.2M ADA** (Koios totals; k = 500).
- Pipeline scripts: [`mainnet-analysis/scripts/build_mpo_topology_*.py`](https://github.com/input-output-hk/spo-incentives/tree/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/scripts).
- CSV exports: [`mainnet-analysis/outputs/csv/`](https://github.com/input-output-hk/spo-incentives/tree/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/outputs/csv).

## Companion deliverables

- [Findings narrative (Markdown)](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/docs/mpo_topology_findings.md) — full prose write-up
- [Auto-generated tables](https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/census/mainnet-analysis/docs/mpo_topology_tables_auto.md) — every concentration aggregation as plain tables
- [PDF report](MPO_infrastructure_topology.pdf) — 16-page IOG-branded report

> Citation note · This page deliberately mirrors the canonical taxonomy from
> the [pools-distribution sub-flow](../../pools-distribution/mainnet-analysis/README.md)
> rather than introducing a parallel one. Tier boundaries, z₀ definition,
> and the 3M-ADA productive-segment cutoff are all imported from there.
