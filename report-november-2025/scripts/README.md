# Reproduction scripts for the November 2025 report

This directory contains every script needed to regenerate the
report's three appendices and fifteen charts from a local Cardano
db-sync instance. It exists to address the auditor's Q2.1–Q2.3 and
Q2.5 requests: identify the script behind each committed artifact and
make each reproducible.

## How this directory is organised

Each artifact in the report (`../appendixA.txt`, `../appendixB.csv`,
`../appendixC.txt`, `../img/*.png`) is paired here with one or two
Python scripts:

- An **`*-original.py`** script — preserved verbatim from the analysis
  working directory at report time, for traceability.
- A **`*-pinned.py`** sibling (where needed) — same script with the
  time-dependent inputs frozen so the artifact reproduces against
  today's db-sync.

The pinned variant exists because the originals contain time-dependent
SQL (e.g. `SELECT MAX(no) FROM epoch`, or `max(registered_tx_id)` with
no time filter) — running them today would shift epoch windows or
pick up a "latest" `pool_update` that didn't exist at report time. The
pinned variants freeze these inputs to the db-sync state on
2025-10-20 (typically `pool_update.b.epoch_no <= 586` for the
snapshot, and 583 for the analysis-window end).

Some scripts already use hardcoded epoch constants and don't need a
`*-pinned.py` sibling; those are committed verbatim.

All scripts connect to `dbname=cexplorer, user=carlos` — edit
`DB_CONFIG` to match your environment.

> **Note on residual drift.** Scripts that hit db-sync may show small
> per-bar or per-point differences (typically ±1–3 pools) against the
> published versions, concentrated at the trailing edge of the
> analysis window. Pools that re-registered, retired, or changed
> parameters near the boundary resolve slightly differently when
> re-run against today's db-sync. Chart shape, scale, axes, and
> overall content match in every case.

---

## Appendix A — pool tier classification (`../appendixA.txt`)

| Script | Output | Relevance |
|---|---|---|
| `appendixa-original.py` | `appendixA_548-583.txt` | Unmodified original (`unviable-pools-abandoned-v4.py` in the analysis directory). |
| `appendixa-pinned.py` | `appendixA-pinned.txt` | Pins five time-dependent inputs to the db-sync state and calendar date at report time (2025-10-20). |

## Appendix B — per-epoch per-pool data (`../appendixB.csv`)

| Script | Output | Relevance |
|---|---|---|
| `appendixb-original.py` | `analysis_results_filtered.csv` | Unmodified original. |
| `appendixb.py` | `appendixB.csv` | Pins the epoch anchor to 586. |
| `appendixb-pinned.py` | `appendixB-pinned.csv` | Above, plus pins the `pool_update` snapshot to epoch ≤ 586. |

## Appendix C — pledge cohort comparison case studies (`../appendixC.txt`)

| Script | Output | Relevance |
|---|---|---|
| `appendixc-original.py` | stdout | Unmodified original (`local_analyse_results_filtered.py`). Reads `analysis_results_filtered.csv`. |
| `appendixc.py` | `appendixC-pinned.txt` | Reads the published `../appendixB.csv`; writes only the case-study section to file. |

---

## Report charts (`../img/*.png`)

| Script | Output chart in `../img/` | Title rendered in the chart |
|---|---|---|
| `pool-size-distribution-pinned.py` | `pool_size_distribution.png` | `Cardano Stake Pool Size Distribution (Excluding 1305 Inactive Pools)` |
| `stake-control-by-size-pinned.py` | `stake_control_by_size.png` | `Total Stake of Active Pools by Size (Excluding 1305 Abandoned Pools)` |
| `wallet-distribution-combined-corrected-pinned.py` | `wallet_distribution_combined_corrected.png` | `Wallet Count and Total Staked ADA by Size` |
| `analyze-data-pinned.py` | `pool_count_epoch.png` | `Block-Producing Pools per Epoch` |
| `analyze-data-pinned.py` | `stake_percentage_epoch.png` | `Percentage of Active Stake in Healthy Pools` |
| `analyze-data-pinned.py` | `active_stake_participation.png` | `Active Stake Participation Rate` |
| `analyze-data-pinned.py` | `block_production_health.png` | `Block Production Health per Epoch` |
| `cumulative-stake-distribution.py` | `cumulative_stake_distribution_epoch_583_annotated.png` | `Cumulative Stake Distribution vs. Ideal Saturation (All Active Pools, Epoch 583)` |
| `pool-registrations-vs-retirements-log-pinned.py` | `pool_registrations_vs_retirements_log.png` | `New Pool Registrations vs. Retirements per Epoch (Log Scale)` |
| `pool-cost-distr-pinned.py` | `pool-cost-distr.png` | `Distribution of Common Fixed Costs by Pool Size (Excluding Inactive pools)` |
| `pool-margin-vs-size-pinned.py` | `pool_margin_vs_size.png` | `Pool Size vs. Margin (Excluding inactive pools)` |
| `pool-cost-vs-margin-pinned.py` | `pool_cost_vs_margin.png` | `Pool Margin vs. Fixed Cost (Excluding Inactive pools)` |
| `mpo-evolution-pinned.py` | `mpo_evolution_pct_circulating.png` | `MPO Stake as % of Circulating Supply (Discovered MPOs with > 5 pools)` |
| `rewards-fees-tx-count-pinned.py` | `rewards_fees_tx_count_last_73_epochs.png` | `Total Rewards, Fees, and Transactions per Epoch (Epoch 519 - 591)` |
| `fees-and-reserves.py` | `sustainability_trends_with_projection_208-583.png` | `Cardano Network Economic Sustainability & Reserve Depletion Projection` |

### Upstream files for `analyze-data-pinned.py`

`analyze-data-pinned.py` is the only chart script that reads a
pre-computed CSV instead of querying db-sync directly. The CSV is the
output of a two-stage pipeline; every step is committed here:

| File | Relevance |
|---|---|
| `abandoned-only.txt` | 1,512 inactive pool IDs (input to `table2.py`). |
| `table2.py` | Queries db-sync for epochs 548-583; writes per-epoch CSVs to `results/`. |
| `combine.py` | Concatenates `results/epoch_*_summary.csv` into `all_epochs_summary.csv`. |
| `all_epochs_summary.csv` | Final input to `analyze-data-pinned.py`. |

> **Note on `abandoned-only.txt`.** This list is a broader version of
> Appendix A's `Inactive` set: it covers pools from multiple
> classification groups, not only Inactive ones. Of its 1,512 pool
> IDs, 1,294 also appear as `Inactive` in Appendix A and the
> remaining 218 fall in the `Struggling` or `Viable but Small`
> tiers. The two filters serve different purposes and are not
> expected to match exactly.

`inactive-pools.txt` (a third input file used by several chart
scripts) is bit-identical to the `Inactive` subset of Appendix A
(1,305 pool IDs).
