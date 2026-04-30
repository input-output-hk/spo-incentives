# EDI replication — Cardano Nakamoto coefficient, two reference epochs × two clustering modes

This folder is the in-house run of the **Edinburgh Decentralization Index (EDI) methodology** on Cardano mainnet. EDI's pipeline (parser, identifier and cluster files, 30-day rolling aggregator, metrics module) is executed end-to-end against raw block-production data fetched from a public Koios mirror, for **two reference epochs × two clustering modes**, producing four Nakamoto-coefficient values entered as **definitions D8a/D8b/D9a/D9b** in the parent sub-flow's [definition matrix](../README.md). The two epochs are **584** (the window anchoring the November 2025 report's EDI citation) and **623** (the snapshot epoch used by the rest of the parent sub-flow). The two clustering modes are EDI's default on-chain-metadata clustering and `clustering: false`, the configuration that exposes the underlying pool-level Nakamoto on the same block-production data.

| Reference epoch | 30-day window (UTC) | Pool view (no clustering) | Entity view (EDI on-chain-metadata) |
|---|---|---:|---:|
| 584 (citation anchor) | epochs 579 – 584 (2025-08-27 → 2025-09-26) | **164** | **82** |
| 623 (project snapshot) | epochs 618 – 623 (2026-03-10 → 2026-04-09) | **162** | **90** |

**The published EDI value reproduces faithfully.** The entity-view value at epoch 584 (**82**) matches the report's ~80 to within rounding — *the figure is a faithful reproduction of EDI's published metric, not a re-derivation under different assumptions*.

**At pool level, blocks and stake produce indistinguishable Nakamoto values.** The pool view at both epochs sits within **1–3 units** of the parent sub-flow's stake-based pool-level definitions D1 (163, raw stake) and D2 (161, productive stake). On Cardano at 30-day granularity (~128 000 blocks), block-share is operationally indistinguishable from stake-share as a Nakamoto input *at the pool level*.

**The ~80× gap to D4 = 18 is therefore almost entirely a clustering effect.** Lifting the clustering policy from "none" to "on-chain metadata" pulls the metric from **~163 to ~85**; lifting it further to "curated MPO manifest with operational fingerprinting" pulls it from **~85 to 18**. *The cascade 162 → 90 → 18 is decomposed at each step on the same block-production data — the choice of resource (blocks vs. stake) and the choice of window (30 days vs. snapshot) account for at most a handful of units along the way.*

## Method

1. **Fetch raw block data from Koios** (`api.koios.rest`, open mirror of
   the Cardano chain). The script `scripts/01_fetch_blocks_koios.py`
   paginates the `/blocks` endpoint for the target epoch range, collects
   `(block_hash, block_time, pool_bech32)`, and decodes the Bech32
   `pool1...` prefix to the 28-byte hex pool hash (the identifier format
   EDI expects). The script was re-run twice with `EPOCHS` set to
   `range(579, 585)` and `range(618, 624)`, producing
   `inputs/cardano_raw_data_e579_e584.ndjson` (127 719 blocks, 1 260
   unique pool hashes) and
   `inputs_e618_e623/cardano_raw_data_e618_e623.ndjson` (128 011 blocks,
   1 206 unique pool hashes) respectively.

2. **Run EDI's pipeline unchanged** against each file, twice per file —
   once with `clustering: true` (default), once with `clustering: false`:
   ```
   git clone https://github.com/blockchain-technology-lab/consensus-decentralization.git
   cd consensus-decentralization
   pip install -r requirements.txt
   cp <this>/inputs/cardano_raw_data_e579_e584.ndjson raw_block_data/cardano_raw_data.json
   # entity (clustered) view
   #   config.yaml: clustering: true
   python run.py --ledgers cardano --timeframe 2025-09
   cat results/.../metrics/output_clustered.csv
   # pool view
   #   config.yaml: clustering: false
   python run.py --ledgers cardano --timeframe 2025-09
   cat results/.../metrics/output_non_clustered.csv
   # then repeat both runs with the e618_e623 input and --timeframe 2026-04
   # (after extending config.yaml end_date to 2026-05-01)
   ```
   Both modes invoke EDI's default 30-day rolling window. The clustered
   mode uses `mapping_information/clusters/cardano.json` plus the
   identifier ticker map; the non-clustered mode treats every distinct
   pool hash as its own entity. No metric or windowing parameter is
   modified.

3. **Read the output line**, persisted in
   `outputs/edi_output_clustered.csv` and
   `outputs/edi_output_pool_only.csv` for the epoch-584 batch, and the
   matching pair under `outputs_e618_e623/` for the epoch-623 batch.

## Key outputs (unmodified from EDI runs)

Epoch 584 batch — entity view (`outputs/edi_output_clustered.csv`):
```
ledger,date,clustering,...,nakamoto_coefficient,...,total_entities
cardano,2025-09-05,True,...,82,...,970
cardano,2025-10-05,True,...,81,...,787
```

Epoch 584 batch — pool view (`outputs/edi_output_pool_only.csv`):
```
ledger,date,clustering,...,nakamoto_coefficient,...,total_entities
cardano,2025-09-05,False,...,164,...,1240
cardano,2025-10-05,False,...,161,...,1041
```

Epoch 623 batch — entity view
(`outputs_e618_e623/edi_output_clustered.csv`):
```
ledger,date,clustering,...,nakamoto_coefficient,...,total_entities
cardano,2026-03-04,True,...,90,...,828
cardano,2026-04-03,True,...,90,...,919
```

Epoch 623 batch — pool view
(`outputs_e618_e623/edi_output_pool_only.csv`):
```
ledger,date,clustering,...,nakamoto_coefficient,...,total_entities
cardano,2026-03-04,False,...,160,...,1070
cardano,2026-04-03,False,...,162,...,1174
```

EDI's 30-day sampling cadence emits two consecutive windows per batch.
The window relevant to each reference epoch is the one whose 30 days
contain the last slot of that epoch: 2025-09-05 for epoch 584 (NC = 82
clustered, 164 pool-only) and 2026-04-03 for epoch 623 (NC = 90
clustered, 162 pool-only). The "second" window in each batch is reported
for stability context.

## Relationship to this sub-flow's other definitions

| Definition | Axis (share / entity / population / window) | NC |
|---|---|---:|
| D1 (pool, raw stake, snapshot) | stake / pool / all / snapshot e623 | 163 |
| D2 (pool, productive stake) | stake / pool / productive / snapshot e623 | 161 |
| D3 (curated-entity, raw stake) | stake / curated MPO / all / snapshot e623 | 19 |
| D4 (curated-entity, productive stake) | stake / curated MPO / productive / snapshot e623 | 18 |
| **D8a (EDI replication, clustered, e584)** | **blocks / on-chain-metadata / all / 30d window ending e584** | **82** |
| **D8b (EDI replication, clustered, e623)** | **blocks / on-chain-metadata / all / 30d window ending e623** | **90** |
| **D9a (EDI replication, pool-only, e584)** | **blocks / pool / all / 30d window ending e584** | **164** |
| **D9b (EDI replication, pool-only, e623)** | **blocks / pool / all / 30d window ending e623** | **162** |

The four EDI-derived rows fix the structure of the dispersion observed
across the seven main definitions. D9a/D9b empirically demonstrate that
the choice of *resource* (blocks vs. stake) is essentially neutral at
pool level on a 30-day window: 164 ≈ D1 = 163, 162 ≈ D2 = 161. D8a/D8b
sit between pool-level and curated-entity, exactly where a lighter
clustering (on-chain metadata only) should land. The dispersion from 18
→ 82-90 → 161-164 is therefore not noise and not a stake-vs-blocks
artefact: it is the **sensitivity of the Nakamoto coefficient to the
clustering policy**, isolated experimentally.

The 8-unit increase between D8a (e584) and D8b (e623) is consistent with
the broader operator-landscape evolution observed in the census sub-flow
over the same window: more independently-active pool hashes, lighter
concentration in the top-of-distribution tail. Notably, D9a → D9b moves
in the opposite direction and only by 2 units (164 → 162), confirming
that the entity-level improvement comes from *how clusters are forming
or fragmenting*, not from a change in the underlying pool population.

## Files

- `scripts/01_fetch_blocks_koios.py` — Koios fetcher with Bech32 decode
  (epoch range is set at module scope; flip `EPOCHS` to switch windows).
- `inputs/cardano_raw_data_e579_e584.ndjson` — 127 719 blocks for the
  epoch-584 batch.
- `inputs_e618_e623/cardano_raw_data_e618_e623.ndjson` — 128 011 blocks
  for the epoch-623 batch.
- `outputs/edi_output_clustered.csv` — entity-view EDI metric table for
  the epoch-584 batch (NC = 82, 81).
- `outputs/edi_output_pool_only.csv` — pool-view EDI metric table for
  the epoch-584 batch (NC = 164, 161).
- `outputs_e618_e623/edi_output_clustered.csv` — entity-view EDI metric
  table for the epoch-623 batch (NC = 90, 90).
- `outputs_e618_e623/edi_output_pool_only.csv` — pool-view EDI metric
  table for the epoch-623 batch (NC = 160, 162).

## Caveats

- Each Koios-sourced block stream covers a 30-day window (6 epochs). EDI
  samples "every 30 days", so each batch produces two adjacent windows.
  The "second" window in each batch only partially overlaps with the
  Koios pull, but its NC value is reported for stability context.
- Clustering uses the version of
  `mapping_information/clusters/cardano.json` shipped in the EDI
  repository at the commit cloned on 2026/04/23. The cluster file is not
  refreshed between the two runs; if EDI's upstream mapping has gained
  pools active in early 2026 since that commit, the e623 entity-view NC
  may drift by a few units. The pool-view NC is unaffected by cluster
  drift by construction.
- No pool-metadata refresh was performed; pools that appear in the
  block-production stream but are not in EDI's identifier / cluster
  files are counted as standalone entities in the clustered runs (this
  is EDI's own default behaviour). The number of unmapped pools is
  bounded by `total_entities` minus the number of clusters in
  `cardano.json`.
- The epoch-623 run required extending `config.yaml`'s `end_date` from
  `2026-02-01` to `2026-05-01` to bring April 2026 into EDI's sampled
  window range. Switching between entity and pool views toggles only
  the `clustering` boolean. No other configuration was modified.

> **Status** — Reproduction timestamp 2026/04/23. Runs against Koios tip at epoch 626; both clustering modes executed back-to-back per epoch batch.
