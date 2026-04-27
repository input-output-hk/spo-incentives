"""
Nakamoto Coefficient Re-evaluation — Mainnet Snapshot at Epoch 623
==================================================================

Computes the Nakamoto coefficient under multiple, explicit definitions on the
same mainnet snapshot. The goal is not to produce a single number but to
expose how much of the headline figure is driven by definitional choices
(pool-vs-entity unit, threshold filter, treatment of custodial exchange stake).

Inputs (relative to repo root):
  diagnostic/sub-flows/census/mainnet-analysis/data/
    - pool_stake_623.csv             (pool_id, ..., total_ada)
    - mpo_entity_pool_mapping_mainnet.csv (entity_id, pool_id_bech32, ...)
    - mpo_entity_summary_mainnet.csv      (entity_id, category, ...)
    - operator_landscape_history.csv      (epoch_no, productive_pools, ...)

Outputs:
  diagnostic/sub-flows/nakamoto-revaluation/
    - data/entities_active_e623.csv      (resolved entity → stake)
    - outputs/nakamoto_definitions.csv   (one row per definition)
    - outputs/sensitivity_threshold.csv  (NC vs production threshold)

Reproduction:
  python scripts/01_compute_nakamoto.py

The script is deterministic and depends only on the CSV inputs; no network
or database call is made at runtime.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CENSUS_DATA = REPO_ROOT / "diagnostic" / "sub-flows" / "census" / "mainnet-analysis" / "data"
OUT_DIR = REPO_ROOT / "diagnostic" / "sub-flows" / "nakamoto-revaluation"
DATA_OUT = OUT_DIR / "data"
OUT_OUT = OUT_DIR / "outputs"

EPOCH = 623

# ----------------------------------------------------------------------------
# I/O
# ----------------------------------------------------------------------------


def load_pool_stake() -> dict[str, float]:
    """Return pool_id (bech32) → active stake in ADA at epoch 623."""
    path = CENSUS_DATA / "pool_stake_623.csv"
    out: dict[str, float] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id"].strip()
            stake = float(row["total_ada"])
            out[pool_id] = stake
    return out


def load_entity_mapping() -> dict[str, str]:
    """Return pool_id_bech32 → entity_id from the curated MPO mapping."""
    path = CENSUS_DATA / "mpo_entity_pool_mapping_mainnet.csv"
    out: dict[str, str] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id_bech32"].strip()
            entity = row["entity_id"].strip()
            if pool_id and entity:
                out[pool_id] = entity
    return out


def load_entity_categories() -> dict[str, str]:
    """Return entity_id → category for clustered entities only."""
    path = CENSUS_DATA / "mpo_entity_summary_mainnet.csv"
    out: dict[str, str] = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            out[row["entity_id"].strip()] = row["category"].strip()
    return out


def load_threshold_e623() -> float:
    """Return the production threshold at epoch 623, in ADA."""
    path = CENSUS_DATA / "operator_landscape_history.csv"
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["epoch_no"]) == EPOCH:
                return float(row["production_threshold"]) / 1e6  # lovelace → ADA
    raise RuntimeError(f"Epoch {EPOCH} not found in operator_landscape_history.csv")


# ----------------------------------------------------------------------------
# Core algorithm
# ----------------------------------------------------------------------------


def nakamoto_coefficient(stakes: list[float]) -> int:
    """
    Smallest k such that the top-k stakeholders cumulatively control more
    than 50% of the total stake.
    """
    if not stakes:
        return 0
    sorted_stakes = sorted(stakes, reverse=True)
    total = sum(sorted_stakes)
    threshold = total / 2.0
    cumulative = 0.0
    for k, s in enumerate(sorted_stakes, start=1):
        cumulative += s
        if cumulative > threshold:
            return k
    return len(sorted_stakes)


@dataclass
class EntitySnapshot:
    entity_id: str
    stake_ada: float
    pool_count: int
    is_clustered: bool
    category: str | None  # only for clustered entities


def build_entity_snapshot(
    pool_stake: dict[str, float],
    pool_to_entity: dict[str, str],
    entity_categories: dict[str, str],
) -> list[EntitySnapshot]:
    """
    Map every active pool to an entity (clustered → real entity_id; otherwise
    → singleton entity bearing the pool_id as its identifier).
    """
    by_entity: dict[str, list[float]] = {}
    clustered_ids: set[str] = set()
    for pool_id, stake in pool_stake.items():
        entity = pool_to_entity.get(pool_id)
        if entity is not None:
            clustered_ids.add(entity)
        else:
            entity = pool_id  # singleton
        by_entity.setdefault(entity, []).append(stake)

    snapshot: list[EntitySnapshot] = []
    for entity_id, stakes in by_entity.items():
        snapshot.append(
            EntitySnapshot(
                entity_id=entity_id,
                stake_ada=sum(stakes),
                pool_count=len(stakes),
                is_clustered=entity_id in clustered_ids,
                category=entity_categories.get(entity_id),
            )
        )
    return snapshot


# ----------------------------------------------------------------------------
# Definitions D1 — D7
# ----------------------------------------------------------------------------


def filter_pools_by_threshold(
    pool_stake: dict[str, float], threshold_ada: float
) -> dict[str, float]:
    return {p: s for p, s in pool_stake.items() if s >= threshold_ada}


def coalition_subthreshold(
    snapshot: list[EntitySnapshot],
    pool_stake: dict[str, float],
    threshold_ada: float,
) -> list[EntitySnapshot]:
    """
    Worst-case adversarial framing: every pool below the production threshold
    is treated as a single coordinated coalition (one entity).
    """
    above = [
        EntitySnapshot(
            entity_id=p,
            stake_ada=s,
            pool_count=1,
            is_clustered=False,
            category=None,
        )
        for p, s in pool_stake.items()
        if s >= threshold_ada
    ]
    sub_total = sum(s for s in pool_stake.values() if s < threshold_ada)
    sub_count = sum(1 for s in pool_stake.values() if s < threshold_ada)
    coalition = EntitySnapshot(
        entity_id="SUB_THRESHOLD_COALITION",
        stake_ada=sub_total,
        pool_count=sub_count,
        is_clustered=True,
        category="adversarial_coalition",
    )
    # Now apply entity clustering on the above-threshold set: rebuild from
    # the original mapping.
    return above + [coalition]


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------


def run() -> None:
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    OUT_OUT.mkdir(parents=True, exist_ok=True)

    pool_stake = load_pool_stake()
    pool_to_entity = load_entity_mapping()
    entity_categories = load_entity_categories()
    threshold_ada = load_threshold_e623()

    total_pools = len(pool_stake)
    total_stake = sum(pool_stake.values())

    # D1 — pool-level, no clustering, no threshold
    nc_d1 = nakamoto_coefficient(list(pool_stake.values()))

    # D2 — pool-level, productive only
    productive = filter_pools_by_threshold(pool_stake, threshold_ada)
    nc_d2 = nakamoto_coefficient(list(productive.values()))

    # D3 — entity-clustered, no threshold
    snap_d3 = build_entity_snapshot(pool_stake, pool_to_entity, entity_categories)
    nc_d3 = nakamoto_coefficient([e.stake_ada for e in snap_d3])

    # D4 — entity-clustered, productive only (the project status-quo definition)
    snap_d4 = build_entity_snapshot(productive, pool_to_entity, entity_categories)
    nc_d4 = nakamoto_coefficient([e.stake_ada for e in snap_d4])

    # D5 — entity-clustered, productive, exchange/custody removed (cex / opaque_operational)
    cex_categories = {"cex", "opaque_operational"}
    snap_d5 = [
        e
        for e in snap_d4
        if not (e.is_clustered and (e.category in cex_categories))
    ]
    nc_d5 = nakamoto_coefficient([e.stake_ada for e in snap_d5])

    # D6 — entity-clustered productive + sub-threshold treated as a single coalition
    snap_d6 = coalition_subthreshold(snap_d4, pool_stake, threshold_ada)
    # rebuild clustering on the above-threshold subset
    snap_d6_clustered_above = build_entity_snapshot(
        productive, pool_to_entity, entity_categories
    )
    sub_total = sum(s for s in pool_stake.values() if s < threshold_ada)
    sub_count = sum(1 for s in pool_stake.values() if s < threshold_ada)
    snap_d6 = snap_d6_clustered_above + [
        EntitySnapshot(
            entity_id="SUB_THRESHOLD_COALITION",
            stake_ada=sub_total,
            pool_count=sub_count,
            is_clustered=True,
            category="adversarial_coalition",
        )
    ]
    nc_d6 = nakamoto_coefficient([e.stake_ada for e in snap_d6])

    # D7 — entity-clustered, ALL pools (productive + sub-threshold), exchange removed
    snap_d7 = [e for e in snap_d3 if not (e.is_clustered and e.category in cex_categories)]
    nc_d7 = nakamoto_coefficient([e.stake_ada for e in snap_d7])

    # ------------------------------------------------------------------
    # Persist entity snapshot D4 (the canonical project definition)
    # ------------------------------------------------------------------
    snap_d4_sorted = sorted(snap_d4, key=lambda e: e.stake_ada, reverse=True)
    entities_csv = DATA_OUT / "entities_active_e623.csv"
    with entities_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "entity_id",
                "is_clustered",
                "category",
                "active_pools",
                "stake_ada",
                "share_pct",
                "cum_share_pct",
            ]
        )
        productive_total = sum(e.stake_ada for e in snap_d4_sorted)
        cum = 0.0
        for rank, e in enumerate(snap_d4_sorted, start=1):
            cum += e.stake_ada
            writer.writerow(
                [
                    rank,
                    e.entity_id,
                    int(e.is_clustered),
                    e.category or "",
                    e.pool_count,
                    f"{e.stake_ada:.0f}",
                    f"{100 * e.stake_ada / productive_total:.4f}",
                    f"{100 * cum / productive_total:.4f}",
                ]
            )

    # ------------------------------------------------------------------
    # Definitions table
    # ------------------------------------------------------------------
    defs_csv = OUT_OUT / "nakamoto_definitions.csv"
    rows = [
        ("D1", "Pool-level, no clustering, no threshold", nc_d1, total_pools, total_stake),
        ("D2", "Pool-level, productive only (≥ production threshold)", nc_d2, len(productive), sum(productive.values())),
        ("D3", "Entity-clustered (curated MPO map), no threshold", nc_d3, len(snap_d3), sum(e.stake_ada for e in snap_d3)),
        ("D4", "Entity-clustered, productive only — project status-quo", nc_d4, len(snap_d4), sum(e.stake_ada for e in snap_d4)),
        ("D5", "Entity-clustered, productive, exchange-custody removed", nc_d5, len(snap_d5), sum(e.stake_ada for e in snap_d5)),
        ("D6", "Entity-clustered, productive + sub-threshold coalition", nc_d6, len(snap_d6), sum(e.stake_ada for e in snap_d6)),
        ("D7", "Entity-clustered, all pools, exchange-custody removed", nc_d7, len(snap_d7), sum(e.stake_ada for e in snap_d7)),
    ]
    with defs_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["definition", "description", "nakamoto", "n_units", "stake_ada"])
        for d_id, desc, nc, n_units, st in rows:
            writer.writerow([d_id, desc, nc, n_units, f"{st:.0f}"])

    # ------------------------------------------------------------------
    # Threshold sensitivity (entity-clustered)
    # ------------------------------------------------------------------
    sens_csv = OUT_OUT / "sensitivity_threshold.csv"
    sweep = [0.0, 100_000.0, 500_000.0, 1_000_000.0, 2_000_000.0, 5_000_000.0, 10_000_000.0]
    with sens_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["threshold_ada", "n_pools", "n_entities", "nakamoto"])
        for thr in sweep:
            sub = filter_pools_by_threshold(pool_stake, thr)
            snap = build_entity_snapshot(sub, pool_to_entity, entity_categories)
            writer.writerow([f"{thr:.0f}", len(sub), len(snap), nakamoto_coefficient([e.stake_ada for e in snap])])

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print(f"Epoch: {EPOCH}")
    print(f"Production threshold (ADA): {threshold_ada:,.0f}")
    print(f"Total active pools: {total_pools}")
    print(f"Total active stake (ADA): {total_stake:,.0f}")
    print(f"Productive pools (≥ threshold): {len(productive)}")
    print(f"Curated entity mappings: {len(pool_to_entity)} pools across {len(set(pool_to_entity.values()))} entities")
    print()
    print(f"{'Def':<4} {'Description':<60} {'Nakamoto':>10} {'Units':>8}")
    for d_id, desc, nc, n_units, _ in rows:
        print(f"{d_id:<4} {desc:<60} {nc:>10} {n_units:>8}")


if __name__ == "__main__":
    run()
