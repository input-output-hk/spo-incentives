# MPO Current Manifest

_Updated on 2026-03-09._

## Primary narrative reports

- `../docs/pool-landscape-mainnet.md`
  - Cross-cutting pool landscape report for the whole network.
  - Starts with today's general pool landscape, then adds entity / MPO concentration and history.
- `../docs/mpo-landscape-mainnet.md`
  - MPO / entity-specific companion report.
  - Focuses on attributed clusters rather than the whole pool universe.

## Current canonical outputs

- `mpo_entity_deep_dive_mainnet.md`
  - Main narrative document for MPO entity attribution and evidence.
- `mpo_entity_pool_health_summary_mainnet.md`
  - Current live-health interpretation of the attributed entities.
  - Counts refer to currently registered pools only.
- `mpo_entity_health_overview_mainnet.csv`
  - One row per entity with live stake, pool counts, health tags, and attribution evidence.
  - Counts refer to currently registered pools only.
- `mpo_entity_pool_health_mainnet.csv`
  - One row per pool with stake, pledge, fees, health tags, and attribution fields.
  - Registered pools only. No retired rows.
- `mpo_entity_pool_table_mainnet.md`
  - Human-readable table view of the current registered pools grouped by suspected entity.
- `mpo_entity_pool_mapping_mainnet.csv`
  - Historical pool-to-entity mapping used by the health and deep-dive outputs.
  - This file can include retired pools.
- `mpo_unresolved_group_labels_mainnet.csv`
  - Important unresolved labels kept separate from higher-confidence attributions.

## Current canonical figure

- `../figures/mpo_entity_current_distribution_mainnet.png`

## Current supplemental comparison artifacts

- `zero_pledge_large_pool_history_mainnet_summary.md`
  - Report-vs-current history note for large exact-zero-pledge pools.
- `zero_pledge_large_pool_history_mainnet.csv`
  - Epoch-by-epoch metrics behind the history chart.
- `../figures/zero_pledge_large_pool_history_mainnet.png`
  - History visual using report-style `>70M ADA` plus stricter `>=80%` saturation lines.

## Archived superseded outputs

- `archive/mpo_2026-03-09/`
  - Older progression outputs that used the earlier `proxy` wording.
  - Older entity summary CSV superseded by `mpo_entity_health_overview_mainnet.csv`.

## Practical reading order

1. `mpo_entity_deep_dive_mainnet.md`
2. `mpo_entity_pool_health_summary_mainnet.md`
3. `mpo_entity_health_overview_mainnet.csv`
4. `mpo_entity_pool_health_mainnet.csv`
5. `mpo_entity_pool_table_mainnet.md`
6. `mpo_entity_pool_mapping_mainnet.csv` only if you need the historical attribution set
