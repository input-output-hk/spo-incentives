#!/usr/bin/env python3
"""
Build a pool-level analysis of how the epoch reward pot is distributed across pools.

This pass stays aligned with the report-era local data already present in the repo:
- spo_incentives/appendixB.csv
- spo_incentives/active_pool_details_epoch_589.csv

Outputs:
- scenarii-evaluation/data/pool_epoch_reward_distribution_549_584.csv
- scenarii-evaluation/data/pool_reward_distribution_549_584.csv
- scenarii-evaluation/figures/pool_reward_distribution_by_size_549_584.png
- scenarii-evaluation/figures/pool_reward_concentration_549_584.png
- scenarii-evaluation/figures/pool_reward_split_mechanics_549_584.png
- scenarii-evaluation/outputs/pool_reward_distribution_summary.md
- scenarii-evaluation/docs/pool-reward-distribution-analysis.md

Important limitations:
- Pool fixed cost, margin, pledge, ticker, and saturation come from the epoch-589 snapshot.
- Owner stake comes from appendixB per epoch.
- The operator/delegator split is therefore "snapshot-parameter based", not a full
  per-epoch ledger replay of pool parameter updates.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


EPOCHS_IN_WINDOW = 36
SIZE_BUCKETS: List[Tuple[str, float, float]] = [
    ("<3M", 0.0, 3_000_000.0),
    ("3M-10M", 3_000_000.0, 10_000_000.0),
    ("10M-30M", 10_000_000.0, 30_000_000.0),
    ("30M-70M", 30_000_000.0, 70_000_000.0),
    (">70M", 70_000_000.0, math.inf),
]


@dataclass
class PoolSnapshot:
    pool_id: str
    ticker: str
    stake_ada_snapshot: float
    pledge_ada_snapshot: float
    owner_stake_ada_snapshot: float
    fixed_cost_ada_snapshot: float
    margin_rate_snapshot: float
    saturation_level_snapshot: float


@dataclass
class PoolEpochRow:
    epoch_no: int
    pool_id: str
    ticker: str
    has_snapshot_metadata: bool
    delegated_stake_ada: float
    block_count: int
    reward_ada: float
    owner_stake_ada: float
    owner_share: float
    pledge_ada_snapshot: Optional[float]
    fixed_cost_ada_snapshot: Optional[float]
    margin_rate_snapshot: Optional[float]
    saturation_level_snapshot: Optional[float]
    fixed_component_ada: Optional[float]
    margin_component_ada: Optional[float]
    owner_member_component_ada: Optional[float]
    delegator_component_ada: Optional[float]
    size_bucket: str


@dataclass
class PoolAggregate:
    pool_id: str
    ticker: str
    has_snapshot_metadata: bool
    epochs_observed: int
    total_reward_ada_window: float
    total_blocks_window: int
    avg_reward_epoch_ada_window: float
    avg_blocks_epoch_window: float
    mean_stake_ada_in_rows: float
    mean_owner_stake_ada_in_rows: float
    mean_owner_share_in_rows: float
    stake_ada_snapshot: Optional[float]
    pledge_ada_snapshot: Optional[float]
    fixed_cost_ada_snapshot: Optional[float]
    margin_rate_snapshot: Optional[float]
    saturation_level_snapshot: Optional[float]
    fixed_component_ada_window: Optional[float]
    margin_component_ada_window: Optional[float]
    owner_member_component_ada_window: Optional[float]
    delegator_component_ada_window: Optional[float]
    operator_take_pct_of_reward: Optional[float]
    fixed_cost_burden_pct: Optional[float]
    reference_stake_ada: float
    reference_size_bucket: str
    local_viability_tier: str


def size_bucket_label(stake_ada: float) -> str:
    for label, lo, hi in SIZE_BUCKETS:
        if stake_ada >= lo and stake_ada < hi:
            return label
    return SIZE_BUCKETS[-1][0]


def read_active_snapshot(path: Path) -> Dict[str, PoolSnapshot]:
    snapshots: Dict[str, PoolSnapshot] = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["poolId"]
            snapshots[pool_id] = PoolSnapshot(
                pool_id=pool_id,
                ticker=row["ticker"],
                stake_ada_snapshot=float(row["epoch_stake_ada"]),
                pledge_ada_snapshot=float(row["pledge_ada"]),
                owner_stake_ada_snapshot=float(row["owner_stake_ada"]),
                fixed_cost_ada_snapshot=float(row["fixed_cost_ada"]),
                margin_rate_snapshot=float(row["margin_percent"]) / 100.0,
                saturation_level_snapshot=float(row["saturation_level"]),
            )
    return snapshots


def read_appendix_b(path: Path) -> List[dict]:
    deduped: Dict[Tuple[int, str], dict] = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["epoch_no"]), row["pool_id"])
            # Duplicate rows are exact duplicates in this dataset. Keep the first.
            if key not in deduped:
                deduped[key] = row
    return [deduped[key] for key in sorted(deduped)]


def derive_epoch_rows(snapshot_by_id: Dict[str, PoolSnapshot], appendix_rows: Iterable[dict]) -> List[PoolEpochRow]:
    rows: List[PoolEpochRow] = []
    for raw in appendix_rows:
        pool_id = raw["pool_id"]
        snap = snapshot_by_id.get(pool_id)
        delegated_stake_ada = int(raw["total_delegated_stake"]) / 1_000_000.0
        reward_ada = int(raw["rewards_earned_in_epoch"]) / 1_000_000.0
        owner_stake_ada = int(raw["pool_owners_cumulative_stake"]) / 1_000_000.0
        owner_share = 0.0
        if delegated_stake_ada > 0:
            owner_share = max(0.0, min(1.0, owner_stake_ada / delegated_stake_ada))

        fixed_component = None
        margin_component = None
        owner_member_component = None
        delegator_component = None
        ticker = ""
        fixed_cost = None
        margin_rate = None
        pledge = None
        saturation = None

        if snap is not None:
            ticker = snap.ticker
            fixed_cost = snap.fixed_cost_ada_snapshot
            margin_rate = snap.margin_rate_snapshot
            pledge = snap.pledge_ada_snapshot
            saturation = snap.saturation_level_snapshot
            fixed_component = min(reward_ada, fixed_cost)
            remainder = max(reward_ada - fixed_cost, 0.0)
            margin_component = remainder * margin_rate
            owner_member_component = remainder * (1.0 - margin_rate) * owner_share
            delegator_component = max(
                reward_ada - fixed_component - margin_component - owner_member_component,
                0.0,
            )

        rows.append(
            PoolEpochRow(
                epoch_no=int(raw["epoch_no"]),
                pool_id=pool_id,
                ticker=ticker,
                has_snapshot_metadata=snap is not None,
                delegated_stake_ada=delegated_stake_ada,
                block_count=int(raw["total_block_count_for_epoch"]),
                reward_ada=reward_ada,
                owner_stake_ada=owner_stake_ada,
                owner_share=owner_share,
                pledge_ada_snapshot=pledge,
                fixed_cost_ada_snapshot=fixed_cost,
                margin_rate_snapshot=margin_rate,
                saturation_level_snapshot=saturation,
                fixed_component_ada=fixed_component,
                margin_component_ada=margin_component,
                owner_member_component_ada=owner_member_component,
                delegator_component_ada=delegator_component,
                size_bucket=size_bucket_label(delegated_stake_ada),
            )
        )
    return rows


def aggregate_pools(
    snapshot_by_id: Dict[str, PoolSnapshot],
    epoch_rows: List[PoolEpochRow],
) -> List[PoolAggregate]:
    grouped: Dict[str, dict] = {}

    def ensure(pool_id: str) -> dict:
        if pool_id not in grouped:
            snap = snapshot_by_id.get(pool_id)
            grouped[pool_id] = {
                "pool_id": pool_id,
                "ticker": "" if snap is None else snap.ticker,
                "has_snapshot_metadata": snap is not None,
                "epochs_observed": 0,
                "total_reward_ada_window": 0.0,
                "total_blocks_window": 0,
                "sum_stake_ada": 0.0,
                "sum_owner_stake_ada": 0.0,
                "sum_owner_share": 0.0,
                "fixed_component_ada_window": 0.0 if snap is not None else None,
                "margin_component_ada_window": 0.0 if snap is not None else None,
                "owner_member_component_ada_window": 0.0 if snap is not None else None,
                "delegator_component_ada_window": 0.0 if snap is not None else None,
                "stake_ada_snapshot": None if snap is None else snap.stake_ada_snapshot,
                "pledge_ada_snapshot": None if snap is None else snap.pledge_ada_snapshot,
                "fixed_cost_ada_snapshot": None if snap is None else snap.fixed_cost_ada_snapshot,
                "margin_rate_snapshot": None if snap is None else snap.margin_rate_snapshot,
                "saturation_level_snapshot": None if snap is None else snap.saturation_level_snapshot,
            }
        return grouped[pool_id]

    for row in epoch_rows:
        g = ensure(row.pool_id)
        g["ticker"] = g["ticker"] or row.ticker
        g["epochs_observed"] += 1
        g["total_reward_ada_window"] += row.reward_ada
        g["total_blocks_window"] += row.block_count
        g["sum_stake_ada"] += row.delegated_stake_ada
        g["sum_owner_stake_ada"] += row.owner_stake_ada
        g["sum_owner_share"] += row.owner_share

        if g["fixed_component_ada_window"] is not None and row.fixed_component_ada is not None:
            g["fixed_component_ada_window"] += row.fixed_component_ada
            g["margin_component_ada_window"] += row.margin_component_ada
            g["owner_member_component_ada_window"] += row.owner_member_component_ada
            g["delegator_component_ada_window"] += row.delegator_component_ada

    # Add pools that exist in the snapshot but never appear in the reward window.
    for pool_id in snapshot_by_id:
        ensure(pool_id)

    aggregates: List[PoolAggregate] = []
    for pool_id, g in grouped.items():
        epochs_observed = int(g["epochs_observed"])
        mean_stake_ada = (g["sum_stake_ada"] / epochs_observed) if epochs_observed > 0 else 0.0
        mean_owner_stake_ada = (g["sum_owner_stake_ada"] / epochs_observed) if epochs_observed > 0 else 0.0
        mean_owner_share = (g["sum_owner_share"] / epochs_observed) if epochs_observed > 0 else 0.0
        total_reward_ada = float(g["total_reward_ada_window"])
        fixed_component = g["fixed_component_ada_window"]
        margin_component = g["margin_component_ada_window"]
        owner_member_component = g["owner_member_component_ada_window"]
        delegator_component = g["delegator_component_ada_window"]

        operator_take_pct = None
        fixed_cost_burden_pct = None
        if total_reward_ada > 0 and fixed_component is not None:
            operator_total = fixed_component + margin_component + owner_member_component
            operator_take_pct = (operator_total / total_reward_ada) * 100.0
            fixed_cost_burden_pct = (fixed_component / total_reward_ada) * 100.0

        reference_stake = g["stake_ada_snapshot"]
        if reference_stake is None or reference_stake <= 0:
            reference_stake = mean_stake_ada

        if total_reward_ada <= 0:
            local_viability_tier = "zeroReward"
        elif reference_stake >= 3_000_000.0:
            local_viability_tier = "healthy"
        elif total_reward_ada >= 5_500.0:
            local_viability_tier = "viableSmall"
        else:
            local_viability_tier = "struggling"

        aggregates.append(
            PoolAggregate(
                pool_id=pool_id,
                ticker=g["ticker"],
                has_snapshot_metadata=bool(g["has_snapshot_metadata"]),
                epochs_observed=epochs_observed,
                total_reward_ada_window=total_reward_ada,
                total_blocks_window=int(g["total_blocks_window"]),
                avg_reward_epoch_ada_window=total_reward_ada / EPOCHS_IN_WINDOW,
                avg_blocks_epoch_window=float(g["total_blocks_window"]) / EPOCHS_IN_WINDOW,
                mean_stake_ada_in_rows=mean_stake_ada,
                mean_owner_stake_ada_in_rows=mean_owner_stake_ada,
                mean_owner_share_in_rows=mean_owner_share,
                stake_ada_snapshot=g["stake_ada_snapshot"],
                pledge_ada_snapshot=g["pledge_ada_snapshot"],
                fixed_cost_ada_snapshot=g["fixed_cost_ada_snapshot"],
                margin_rate_snapshot=g["margin_rate_snapshot"],
                saturation_level_snapshot=g["saturation_level_snapshot"],
                fixed_component_ada_window=fixed_component,
                margin_component_ada_window=margin_component,
                owner_member_component_ada_window=owner_member_component,
                delegator_component_ada_window=delegator_component,
                operator_take_pct_of_reward=operator_take_pct,
                fixed_cost_burden_pct=fixed_cost_burden_pct,
                reference_stake_ada=float(reference_stake),
                reference_size_bucket=size_bucket_label(float(reference_stake)),
                local_viability_tier=local_viability_tier,
            )
        )

    aggregates.sort(key=lambda x: (x.total_reward_ada_window, x.reference_stake_ada), reverse=True)
    return aggregates


def write_epoch_rows_csv(rows: List[PoolEpochRow], out_path: Path) -> None:
    fieldnames = [
        "epoch_no",
        "pool_id",
        "ticker",
        "has_snapshot_metadata",
        "delegated_stake_ada",
        "block_count",
        "reward_ada",
        "owner_stake_ada",
        "owner_share",
        "pledge_ada_snapshot",
        "fixed_cost_ada_snapshot",
        "margin_rate_snapshot",
        "saturation_level_snapshot",
        "fixed_component_ada",
        "margin_component_ada",
        "owner_member_component_ada",
        "delegator_component_ada",
        "size_bucket",
    ]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_pool_aggregates_csv(rows: List[PoolAggregate], out_path: Path) -> None:
    fieldnames = [
        "pool_id",
        "ticker",
        "has_snapshot_metadata",
        "epochs_observed",
        "total_reward_ada_window",
        "total_blocks_window",
        "avg_reward_epoch_ada_window",
        "avg_blocks_epoch_window",
        "mean_stake_ada_in_rows",
        "mean_owner_stake_ada_in_rows",
        "mean_owner_share_in_rows",
        "stake_ada_snapshot",
        "pledge_ada_snapshot",
        "fixed_cost_ada_snapshot",
        "margin_rate_snapshot",
        "saturation_level_snapshot",
        "fixed_component_ada_window",
        "margin_component_ada_window",
        "owner_member_component_ada_window",
        "delegator_component_ada_window",
        "operator_take_pct_of_reward",
        "fixed_cost_burden_pct",
        "reference_stake_ada",
        "reference_size_bucket",
        "local_viability_tier",
    ]
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def render_distribution_by_size(epoch_rows: List[PoolEpochRow], out_path: Path) -> Dict[str, dict]:
    bucket_stats: Dict[str, dict] = {
        label: {"stake": 0.0, "blocks": 0.0, "rewards": 0.0}
        for label, _, _ in SIZE_BUCKETS
    }
    total_stake = 0.0
    total_blocks = 0.0
    total_rewards = 0.0
    for row in epoch_rows:
        bucket_stats[row.size_bucket]["stake"] += row.delegated_stake_ada
        bucket_stats[row.size_bucket]["blocks"] += row.block_count
        bucket_stats[row.size_bucket]["rewards"] += row.reward_ada
        total_stake += row.delegated_stake_ada
        total_blocks += row.block_count
        total_rewards += row.reward_ada

    labels = [label for label, _, _ in SIZE_BUCKETS]
    stake_share = [
        (bucket_stats[label]["stake"] / total_stake) * 100.0 if total_stake > 0 else 0.0
        for label in labels
    ]
    block_share = [
        (bucket_stats[label]["blocks"] / total_blocks) * 100.0 if total_blocks > 0 else 0.0
        for label in labels
    ]
    reward_share = [
        (bucket_stats[label]["rewards"] / total_rewards) * 100.0 if total_rewards > 0 else 0.0
        for label in labels
    ]

    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.bar(x - width, stake_share, width=width, label="Stake share", color="#9ecae1")
    ax.bar(x, block_share, width=width, label="Block share", color="#3182bd")
    ax.bar(x + width, reward_share, width=width, label="Reward share", color="#08519c")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Share of report window (%)")
    ax.set_title("How the Reward Pot Is Distributed Across Pool Sizes")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper left")
    ax.text(
        0.01,
        0.98,
        "Window: epochs 549-584, deduped by (epoch, pool_id)\n"
        "Buckets use per-epoch delegated stake from appendixB",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.9, edgecolor="#cccccc"),
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    out: Dict[str, dict] = {}
    for label, s, b, r in zip(labels, stake_share, block_share, reward_share):
        out[label] = {"stake_share_pct": s, "block_share_pct": b, "reward_share_pct": r}
    return out


def render_concentration(aggregates: List[PoolAggregate], out_path: Path) -> Dict[str, float]:
    rewarding = [r for r in aggregates if r.total_reward_ada_window > 0]
    rewarding.sort(key=lambda x: x.total_reward_ada_window, reverse=True)

    rewards = np.array([r.total_reward_ada_window for r in rewarding], dtype=float)
    stake = np.array([r.reference_stake_ada for r in rewarding], dtype=float)
    total_rewards = float(np.sum(rewards))
    total_stake = float(np.sum(stake))
    cum_rewards = np.cumsum(rewards) / total_rewards * 100.0 if total_rewards > 0 else np.array([])
    cum_stake = np.cumsum(stake) / total_stake * 100.0 if total_stake > 0 else np.array([])
    ranks = np.arange(1, len(rewarding) + 1)

    fig, ax = plt.subplots(figsize=(13, 8))
    ax.plot(ranks, cum_rewards, color="#d62728", linewidth=2.0, label="Cumulative reward share")
    ax.plot(ranks, cum_stake, color="#111111", linewidth=1.8, label="Cumulative stake share")
    for n in [10, 50, 100, 250]:
        if n <= len(rewarding):
            ax.scatter([n], [cum_rewards[n - 1]], color="#d62728", s=28)
            ax.text(n, cum_rewards[n - 1] + 1.3, f"Top {n}: {cum_rewards[n - 1]:.1f}%", fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("Top N pools ranked by total rewards in the window")
    ax.set_ylabel("Cumulative share (%)")
    ax.set_title("Reward Concentration vs Stake Concentration")
    ax.grid(alpha=0.2, which="both")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    stats = {}
    for n in [10, 50, 100, 250]:
        if n <= len(rewarding):
            stats[f"top{n}_reward_share_pct"] = float(cum_rewards[n - 1])
            stats[f"top{n}_stake_share_pct"] = float(cum_stake[n - 1])
    return stats


def render_split_mechanics(aggregates: List[PoolAggregate], out_path: Path) -> Dict[str, dict]:
    labels = [label for label, _, _ in SIZE_BUCKETS]
    fixed_share_median = []
    margin_share_median = []
    owner_share_median = []
    delegator_share_median = []
    median_reward_epoch = []

    scatter_x = []
    scatter_y = []
    scatter_colors = []

    palette = {
        "<3M": "#e15759",
        "3M-10M": "#f28e2b",
        "10M-30M": "#76b7b2",
        "30M-70M": "#59a14f",
        ">70M": "#4e79a7",
    }

    bucket_summary: Dict[str, dict] = {}

    for label in labels:
        subset = [
            r
            for r in aggregates
            if r.reference_size_bucket == label
            and r.avg_reward_epoch_ada_window > 0
            and r.fixed_component_ada_window is not None
        ]
        if subset:
            fixed_vals = []
            margin_vals = []
            owner_vals = []
            delegator_vals = []
            reward_vals = []
            for row in subset:
                reward_epoch = row.avg_reward_epoch_ada_window
                fixed_epoch = row.fixed_component_ada_window / EPOCHS_IN_WINDOW
                margin_epoch = row.margin_component_ada_window / EPOCHS_IN_WINDOW
                owner_epoch = row.owner_member_component_ada_window / EPOCHS_IN_WINDOW
                delegator_epoch = row.delegator_component_ada_window / EPOCHS_IN_WINDOW
                fixed_vals.append((fixed_epoch / reward_epoch) * 100.0)
                margin_vals.append((margin_epoch / reward_epoch) * 100.0)
                owner_vals.append((owner_epoch / reward_epoch) * 100.0)
                delegator_vals.append((delegator_epoch / reward_epoch) * 100.0)
                reward_vals.append(reward_epoch)
                scatter_x.append(row.reference_stake_ada)
                scatter_y.append((fixed_epoch / reward_epoch) * 100.0)
                scatter_colors.append(palette[label])

            fixed_share_median.append(float(np.median(fixed_vals)))
            margin_share_median.append(float(np.median(margin_vals)))
            owner_share_median.append(float(np.median(owner_vals)))
            delegator_share_median.append(float(np.median(delegator_vals)))
            median_reward_epoch.append(float(np.median(reward_vals)))
            bucket_summary[label] = {
                "median_fixed_share_pct": float(np.median(fixed_vals)),
                "median_margin_share_pct": float(np.median(margin_vals)),
                "median_owner_member_share_pct": float(np.median(owner_vals)),
                "median_delegator_share_pct": float(np.median(delegator_vals)),
                "median_reward_epoch_ada": float(np.median(reward_vals)),
                "n_pools": len(subset),
            }
        else:
            fixed_share_median.append(0.0)
            margin_share_median.append(0.0)
            owner_share_median.append(0.0)
            delegator_share_median.append(0.0)
            median_reward_epoch.append(0.0)
            bucket_summary[label] = {
                "median_fixed_share_pct": 0.0,
                "median_margin_share_pct": 0.0,
                "median_owner_member_share_pct": 0.0,
                "median_delegator_share_pct": 0.0,
                "median_reward_epoch_ada": 0.0,
                "n_pools": 0,
            }

    x = np.arange(len(labels))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5))

    ax1.bar(x, fixed_share_median, color="#b2182b", label="Fixed cost")
    ax1.bar(x, margin_share_median, bottom=fixed_share_median, color="#ef8a62", label="Operator margin")
    ax1.bar(
        x,
        owner_share_median,
        bottom=np.array(fixed_share_median) + np.array(margin_share_median),
        color="#67a9cf",
        label="Owner member-like share",
    )
    ax1.bar(
        x,
        delegator_share_median,
        bottom=np.array(fixed_share_median) + np.array(margin_share_median) + np.array(owner_share_median),
        color="#2166ac",
        label="Delegator share",
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Median share of pool reward (%)")
    ax1.set_title("How a Pool Reward Is Split by Pool Size")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(axis="y", alpha=0.2)

    ax1b = ax1.twinx()
    ax1b.plot(x, median_reward_epoch, color="#111111", marker="o", linewidth=1.8)
    ax1b.set_ylabel("Median pool reward per epoch (ADA)")

    ax2.scatter(scatter_x, scatter_y, s=16, alpha=0.55, c=scatter_colors)
    ax2.set_xscale("log")
    ax2.set_xlabel("Reference pool stake (ADA, log scale)")
    ax2.set_ylabel("Fixed-cost burden inside pool reward (%)")
    ax2.set_title("Why Small Pools Lose More of Their Reward to Fixed Cost")
    ax2.grid(alpha=0.2, which="both")
    ax2.axhline(50.0, color="#777777", linestyle="--", linewidth=1.1)
    ax2.text(0.02, 0.03, "Color = stake bucket", transform=ax2.transAxes, fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    return bucket_summary


def write_summary(
    aggregates: List[PoolAggregate],
    epoch_rows: List[PoolEpochRow],
    bucket_distribution: Dict[str, dict],
    concentration_stats: Dict[str, float],
    split_stats: Dict[str, dict],
    out_path: Path,
) -> None:
    rewarding_pools = [r for r in aggregates if r.total_reward_ada_window > 0]
    zero_reward_pools = [r for r in aggregates if r.total_reward_ada_window <= 0]
    missing_snapshot_rewarding = [r for r in rewarding_pools if not r.has_snapshot_metadata]
    total_reward_window = float(np.sum([r.total_reward_ada_window for r in aggregates]))
    total_reward_epoch = total_reward_window / EPOCHS_IN_WINDOW
    total_blocks_window = int(np.sum([r.total_blocks_window for r in aggregates]))
    avg_reward_below_170 = sum(1 for r in rewarding_pools if r.avg_reward_epoch_ada_window < 170.0)
    avg_reward_below_340 = sum(1 for r in rewarding_pools if r.avg_reward_epoch_ada_window < 340.0)
    tier_counts = defaultdict(int)
    for row in aggregates:
        tier_counts[row.local_viability_tier] += 1

    md = [
        "# Pool Reward Distribution Summary",
        "",
        f"- Report window: epochs **549..584** (**{EPOCHS_IN_WINDOW}** epochs).",
        "- Data sources: `appendixB.csv` + `active_pool_details_epoch_589.csv`.",
        f"- Pool-epoch rows after deduplication: **{len(epoch_rows):,}**",
        f"- Pools in epoch-589 snapshot: **{sum(1 for r in aggregates if r.has_snapshot_metadata):,}**",
        f"- Pools with non-zero rewards in the window: **{len(rewarding_pools):,}**",
        f"- Pools with zero rewards in the window: **{len(zero_reward_pools):,}**",
        f"- Reward-window pools missing epoch-589 snapshot metadata: **{len(missing_snapshot_rewarding):,}**",
        "",
        "## What this reproduces from the report",
        "- The same 36-epoch reward window used by the report.",
        "- A local viability lens based on stake and realized rewards, not the report's full inactivity heuristics.",
        f"- Local healthy pools (`stake >= 3M` with rewards): **{tier_counts['healthy']:,}**",
        f"- Local viable-small pools (`stake < 3M` and `window rewards >= 5,500 ADA`): **{tier_counts['viableSmall']:,}**",
        f"- Local struggling pools (`stake < 3M` and `window rewards < 5,500 ADA`): **{tier_counts['struggling']:,}**",
        f"- Zero-reward pools in the snapshot join: **{tier_counts['zeroReward']:,}**",
        "",
        "## Reward pot distribution",
        f"- Total rewards distributed to pools over the window: **{total_reward_window/1_000_000:.2f}M ADA**",
        f"- Average rewards distributed to pools per epoch: **{total_reward_epoch/1_000_000:.2f}M ADA**",
        f"- Total blocks in the window: **{total_blocks_window:,}**",
        f"- Top 10 pools captured **{concentration_stats.get('top10_reward_share_pct', 0.0):.1f}%** of rewards.",
        f"- Top 50 pools captured **{concentration_stats.get('top50_reward_share_pct', 0.0):.1f}%** of rewards.",
        f"- Top 100 pools captured **{concentration_stats.get('top100_reward_share_pct', 0.0):.1f}%** of rewards.",
        "",
        "### Size-bucket view",
    ]

    for label, _, _ in SIZE_BUCKETS:
        stats = bucket_distribution[label]
        md.append(
            f"- `{label}`: stake share **{stats['stake_share_pct']:.1f}%**, "
            f"block share **{stats['block_share_pct']:.1f}%**, "
            f"reward share **{stats['reward_share_pct']:.1f}%**"
        )

    md.extend(
        [
            "",
            "## How rewards work for pools",
            "- Approximate split uses actual pool reward from `appendixB.csv` and epoch-589 fixed cost / margin from the snapshot.",
            "- Owner stake share is taken from `appendixB.csv` per epoch.",
            f"- Rewarding pools with average reward below `170 ADA/epoch`: **{avg_reward_below_170:,}**",
            f"- Rewarding pools with average reward below `340 ADA/epoch`: **{avg_reward_below_340:,}**",
            "",
            "### Median split by size bucket",
        ]
    )

    for label, _, _ in SIZE_BUCKETS:
        stats = split_stats[label]
        md.append(
            f"- `{label}` (`n={stats['n_pools']}`): fixed cost **{stats['median_fixed_share_pct']:.1f}%**, "
            f"margin **{stats['median_margin_share_pct']:.1f}%**, "
            f"owner member-like share **{stats['median_owner_member_share_pct']:.1f}%**, "
            f"delegator share **{stats['median_delegator_share_pct']:.1f}%**, "
            f"median pool reward **{stats['median_reward_epoch_ada']:.1f} ADA/epoch**"
        )

    md.extend(
        [
            "",
            "## Missing data for the next level down",
            "- Per-epoch pool parameter history: fixed cost, margin, pledge updates.",
            "- Per-epoch pledge compliance flag, not just owner stake amount.",
            "- Apparent performance or expected-slot data per pool, to separate performance losses from pure scale effects.",
            "- Pool retirement / registration update history during the window.",
            "- Entity clustering if the next question is MPO-level concentration rather than pool-level concentration.",
            "",
        ]
    )

    out_path.write_text("\n".join(md))


def write_doc(
    bucket_distribution: Dict[str, dict],
    concentration_stats: Dict[str, float],
    split_stats: Dict[str, dict],
    summary_path: Path,
    fig_dist_path: Path,
    fig_concentration_path: Path,
    fig_split_path: Path,
    out_path: Path,
) -> None:
    lines = [
        "# Pool Reward Distribution Analysis",
        "",
        r"Target quantity: the distribution of $Reward^{epoch}_{pools}$ across individual pools.",
        "",
        "## Objective",
        "Move one layer below the epoch-wide reward pot and inspect how realized pool rewards are distributed across pools, sizes, and operator/delegator splits.",
        "",
        "## Data used in this pass",
        "- `appendixB.csv`: per-pool, per-epoch delegated stake, blocks, realized rewards, and owner cumulative stake for the report window.",
        "- `active_pool_details_epoch_589.csv`: ticker, fixed cost, margin, pledge, owner stake, and saturation snapshot.",
        "- This reproduces the report window first, before introducing live-mainnet fetches.",
        "",
        "## Core reconstruction",
        r"1. Realized pool reward comes directly from `appendixB.csv`: $Reward^{pool}_{actual}$.",
        r"2. Fixed cost comes first: $Reward^{operator}_{fixed}=\min(Reward^{pool}_{actual}, Cost^{operator}_{fixed})$.",
        r"3. The remainder is $Reward^{pool}_{remainder}=\max(Reward^{pool}_{actual}-Cost^{operator}_{fixed}, 0)$.",
        r"4. Margin is applied on the remainder: $Reward^{operator}_{margin}=\mu^{operator}\cdot Reward^{pool}_{remainder}$.",
        r"5. The owner also receives a member-like share on the remaining delegator-style pot according to $ownerShare=\frac{ownerStake}{stake}$.",
        r"6. Delegators receive what remains after fixed cost, margin, and owner member-like share.",
        "",
        "This is an approximation because the reward window is joined to the epoch-589 snapshot for pool parameters.",
        "",
        "## What we can already retrieve from the report",
        "- The same 36-epoch reward window.",
        "- The shape of reward distribution across pool sizes.",
        "- A local viability split based on realized rewards and stake size.",
        "- Reward concentration among the top pools.",
        "",
        f"[Summary]({summary_path.name})",
        "",
        "## Graph 1: Reward Pot Distribution by Pool Size",
        "This compares stake share, block share, and reward share over the report window using per-epoch delegated stake buckets.",
        "",
        f"![Reward distribution by size](../figures/{fig_dist_path.name})",
        "",
        "## Graph 2: Reward Concentration",
        "Pools are ranked by total rewards over the 36-epoch window. The red curve shows cumulative reward share and the black curve shows cumulative stake share.",
        "",
        f"![Reward concentration](../figures/{fig_concentration_path.name})",
        "",
        "## Graph 3: How Pool Rewards Are Split",
        "Left panel: median reward composition by size bucket.",
        "Right panel: fixed-cost burden inside the pool reward for individual pools.",
        "",
        f"![Reward split mechanics](../figures/{fig_split_path.name})",
        "",
        "## First read",
    ]

    for label, _, _ in SIZE_BUCKETS:
        stats = bucket_distribution[label]
        lines.append(
            f"- `{label}` pools: stake share **{stats['stake_share_pct']:.1f}%**, "
            f"reward share **{stats['reward_share_pct']:.1f}%**"
        )

    lines.extend(
        [
            f"- Top 10 pools capture **{concentration_stats.get('top10_reward_share_pct', 0.0):.1f}%** of rewards.",
            f"- Top 50 pools capture **{concentration_stats.get('top50_reward_share_pct', 0.0):.1f}%** of rewards.",
            "",
            "## Pool reward mechanics by size",
        ]
    )

    for label, _, _ in SIZE_BUCKETS:
        stats = split_stats[label]
        lines.append(
            f"- `{label}`: median fixed-cost share **{stats['median_fixed_share_pct']:.1f}%**, "
            f"median delegator share **{stats['median_delegator_share_pct']:.1f}%**, "
            f"median pool reward **{stats['median_reward_epoch_ada']:.1f} ADA/epoch**"
        )

    lines.extend(
        [
            "",
            "## What is still missing for deeper pool-level reward analysis",
            "- Epoch-specific parameter history, so the split is exact instead of snapshot-based.",
            "- Pool apparent performance or expected block assignment, so performance losses can be separated from size effects.",
            "- Pledge-compliance state and retirement history by epoch.",
            "- Live pool metadata if the next step is to move from report-era analysis to current mainnet.",
            "",
        ]
    )

    out_path.write_text("\n".join(lines))


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "spo_incentives"
    data_dir = repo_root / "scenarii-evaluation" / "data"
    figures_dir = repo_root / "scenarii-evaluation" / "figures"
    outputs_dir = repo_root / "scenarii-evaluation" / "outputs"
    docs_dir = repo_root / "scenarii-evaluation" / "docs"

    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = src_dir / "active_pool_details_epoch_589.csv"
    appendix_b_path = src_dir / "appendixB.csv"

    epoch_csv_path = data_dir / "pool_epoch_reward_distribution_549_584.csv"
    pool_csv_path = data_dir / "pool_reward_distribution_549_584.csv"
    fig_dist_path = figures_dir / "pool_reward_distribution_by_size_549_584.png"
    fig_concentration_path = figures_dir / "pool_reward_concentration_549_584.png"
    fig_split_path = figures_dir / "pool_reward_split_mechanics_549_584.png"
    summary_path = outputs_dir / "pool_reward_distribution_summary.md"
    doc_path = docs_dir / "pool-reward-distribution-analysis.md"

    snapshot_by_id = read_active_snapshot(snapshot_path)
    appendix_rows = read_appendix_b(appendix_b_path)
    epoch_rows = derive_epoch_rows(snapshot_by_id, appendix_rows)
    aggregates = aggregate_pools(snapshot_by_id, epoch_rows)

    write_epoch_rows_csv(epoch_rows, epoch_csv_path)
    write_pool_aggregates_csv(aggregates, pool_csv_path)

    plt.style.use("seaborn-v0_8-whitegrid")
    bucket_distribution = render_distribution_by_size(epoch_rows, fig_dist_path)
    concentration_stats = render_concentration(aggregates, fig_concentration_path)
    split_stats = render_split_mechanics(aggregates, fig_split_path)
    write_summary(aggregates, epoch_rows, bucket_distribution, concentration_stats, split_stats, summary_path)
    write_doc(
        bucket_distribution,
        concentration_stats,
        split_stats,
        summary_path,
        fig_dist_path,
        fig_concentration_path,
        fig_split_path,
        doc_path,
    )

    print(f"Wrote: {epoch_csv_path}")
    print(f"Wrote: {pool_csv_path}")
    print(f"Wrote: {fig_dist_path}")
    print(f"Wrote: {fig_concentration_path}")
    print(f"Wrote: {fig_split_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {doc_path}")


if __name__ == "__main__":
    main()
