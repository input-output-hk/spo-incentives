#!/usr/bin/env python3
"""
Build pool-level reward distribution analysis from Koios mainnet pool history.

Required inputs:
- scenarii-evaluation/data/koios_pool_list_mainnet.csv
- scenarii-evaluation/data/koios_pool_history_mainnet.csv
- scenarii-evaluation/data/reward_epoch_pools_mainnet.csv

Outputs:
- scenarii-evaluation/data/pool_reward_epoch_summary_mainnet.csv
- scenarii-evaluation/data/pool_reward_pool_summary_mainnet.csv
- scenarii-evaluation/figures/pool_reward_distribution_by_size_recent_mainnet.png
- scenarii-evaluation/figures/pool_reward_distribution_by_size_mainnet.png
- scenarii-evaluation/figures/pool_reward_concentration_mainnet.png
- scenarii-evaluation/figures/pool_reward_split_mechanics_mainnet.png
- scenarii-evaluation/outputs/pool_reward_distribution_mainnet_summary.md
- scenarii-evaluation/docs/pool-reward-distribution-mainnet.md
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


SIZE_CATEGORIES: List[Tuple[str, str]] = [
    ("Dormant pools", "#f59e0b"),
    ("Subscale pools", "#0284c7"),
    ("Healthy pools", "#16a34a"),
    ("Large healthy pools", "#0f766e"),
    ("Near-saturation pools", "#f97316"),
    ("Saturated pools", "#dc2626"),
    ("Oversaturated pools", "#7c3aed"),
]

REWARD_ANALYSIS_CATEGORIES: List[Tuple[str, str]] = [
    (label, color) for label, color in SIZE_CATEGORIES if label != "Dormant pools"
]

TOP_N_COMPOSITION_BUCKETS: List[Tuple[str, str, set[str]]] = [
    ("Healthy pools", "#16a34a", {"Healthy pools"}),
    ("Large healthy pools", "#0f766e", {"Large healthy pools"}),
    ("Near-saturation pools", "#f97316", {"Near-saturation pools"}),
    ("Saturated and above", "#dc2626", {"Saturated pools", "Oversaturated pools"}),
]

DISPLAY_LABELS = {
    "Dormant pools": "Dormant\npools",
    "Subscale pools": "Subscale\npools",
    "Healthy pools": "Healthy\npools",
    "Large healthy pools": "Large healthy\npools",
    "Near-saturation pools": "Near-saturation\npools",
    "Saturated pools": "Saturated\npools",
    "Oversaturated pools": "Oversaturated\npools",
}

REPORT_CHECKPOINT_EPOCH = 593
REPORT_CHECKPOINT_LABEL = "Prior report checkpoint\nNov 6, 2025"


def size_bucket_label(stake_ada: float, saturation_pct: float) -> str:
    if 0.0 < stake_ada < 100_000.0:
        return "Dormant pools"
    if 100_000.0 <= stake_ada < 3_000_000.0:
        return "Subscale pools"
    if saturation_pct < 50.0:
        return "Healthy pools"
    if saturation_pct < 80.0:
        return "Large healthy pools"
    if saturation_pct < 95.0:
        return "Near-saturation pools"
    if saturation_pct < 105.0:
        return "Saturated pools"
    return "Oversaturated pools"


def format_top_n_category_mix(composition: Dict[str, int]) -> str:
    ordered = sorted(composition.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{count} {label}" for label, count in ordered)


def composition_counts(concentration_stats: Dict[str, object], key: object) -> Dict[str, int]:
    composition = concentration_stats.get("category_composition", {}).get(key, {})
    if isinstance(composition, dict) and "counts" in composition:
        return composition["counts"]
    if isinstance(composition, dict):
        return composition
    return {}


def top_n_bucket_label(size_bucket: str) -> str:
    for label, _, members in TOP_N_COMPOSITION_BUCKETS:
        if size_bucket in members:
            return label
    return "Healthy pools"


def parse_float(value: str) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return float(text)


def read_pool_list(path: Path) -> Dict[str, dict]:
    pools = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pools[row["pool_id_bech32"]] = row
    return pools


def read_reward_epoch_totals(path: Path) -> Dict[int, float]:
    totals = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reward_ada = parse_float(row["Reward_epoch_pools_ada"])
            if reward_ada is not None:
                totals[int(row["epoch_no"])] = reward_ada
    return totals


def read_latest_saturation_point(path: Path) -> float:
    latest_epoch = -1
    latest_supply_ada = 0.0
    latest_k = 0.0
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch_no = int(row["epoch_no"])
            supply_ada = parse_float(row.get("Supply_ada"))
            optimal_pool_count = parse_float(row.get("k_optimal_pool_count"))
            if supply_ada is None or optimal_pool_count in (None, 0.0):
                continue
            if epoch_no > latest_epoch:
                latest_epoch = epoch_no
                latest_supply_ada = supply_ada
                latest_k = optimal_pool_count
    if latest_epoch < 0 or latest_k == 0.0:
        raise RuntimeError("Could not derive latest saturation point from reward_epoch_pools_mainnet.csv")
    return latest_supply_ada / latest_k


def compute_summaries(
    pool_history_path: Path,
) -> tuple[dict, dict, dict, dict]:
    epoch_summary = {}
    pool_summary = {}
    overall_bucket = {
        label: {"active_stake_ada": 0.0, "block_cnt": 0.0, "total_pool_rewards_ada": 0.0}
        for label, _ in SIZE_CATEGORIES
    }
    epoch_bucket_summary = defaultdict(
        lambda: {
            label: {"active_stake_ada": 0.0, "block_cnt": 0.0, "total_pool_rewards_ada": 0.0, "rewarding_pool_cnt": 0}
            for label, _ in SIZE_CATEGORIES
        }
    )

    with pool_history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch_no = int(row["epoch_no"])
            pool_id = row["pool_id_bech32"]
            active_stake_ada = parse_float(row["active_stake_ada"]) or 0.0
            saturation_pct = parse_float(row.get("saturation_pct")) or 0.0
            block_cnt = int(parse_float(row["block_cnt"]) or 0.0)
            pool_fees_ada = parse_float(row["pool_fees_ada"]) or 0.0
            deleg_rewards_ada = parse_float(row["deleg_rewards_ada"]) or 0.0
            member_rewards_ada = parse_float(row["member_rewards_ada"]) or 0.0
            owner_member_rewards_ada = parse_float(row["owner_member_rewards_ada"])
            if owner_member_rewards_ada is None:
                owner_member_rewards_ada = max(deleg_rewards_ada - member_rewards_ada, 0.0)
            total_pool_rewards_ada = parse_float(row["total_pool_rewards_ada"]) or (pool_fees_ada + deleg_rewards_ada)
            bucket = size_bucket_label(active_stake_ada, saturation_pct)

            if epoch_no not in epoch_summary:
                epoch_summary[epoch_no] = {
                    "epoch_no": epoch_no,
                    "active_stake_ada": 0.0,
                    "block_cnt": 0,
                    "pool_fees_ada": 0.0,
                    "deleg_rewards_ada": 0.0,
                    "member_rewards_ada": 0.0,
                    "owner_member_rewards_ada": 0.0,
                    "total_pool_rewards_ada": 0.0,
                    "rewarding_pool_cnt": 0,
                    "pool_row_cnt": 0,
                }
            e = epoch_summary[epoch_no]
            e["active_stake_ada"] += active_stake_ada
            e["block_cnt"] += block_cnt
            e["pool_fees_ada"] += pool_fees_ada
            e["deleg_rewards_ada"] += deleg_rewards_ada
            e["member_rewards_ada"] += member_rewards_ada
            e["owner_member_rewards_ada"] += owner_member_rewards_ada
            e["total_pool_rewards_ada"] += total_pool_rewards_ada
            e["pool_row_cnt"] += 1
            if total_pool_rewards_ada > 0:
                e["rewarding_pool_cnt"] += 1

            p = pool_summary.get(pool_id)
            if p is None:
                p = {
                    "pool_id_bech32": pool_id,
                    "epochs_observed": 0,
                    "sum_active_stake_ada": 0.0,
                    "sum_saturation_pct": 0.0,
                    "total_blocks": 0,
                    "total_pool_fees_ada": 0.0,
                    "total_deleg_rewards_ada": 0.0,
                    "total_member_rewards_ada": 0.0,
                    "total_owner_member_rewards_ada": 0.0,
                    "total_pool_rewards_ada": 0.0,
                }
                pool_summary[pool_id] = p
            p["epochs_observed"] += 1
            p["sum_active_stake_ada"] += active_stake_ada
            p["sum_saturation_pct"] += saturation_pct
            p["total_blocks"] += block_cnt
            p["total_pool_fees_ada"] += pool_fees_ada
            p["total_deleg_rewards_ada"] += deleg_rewards_ada
            p["total_member_rewards_ada"] += member_rewards_ada
            p["total_owner_member_rewards_ada"] += owner_member_rewards_ada
            p["total_pool_rewards_ada"] += total_pool_rewards_ada

            overall_bucket[bucket]["active_stake_ada"] += active_stake_ada
            overall_bucket[bucket]["block_cnt"] += block_cnt
            overall_bucket[bucket]["total_pool_rewards_ada"] += total_pool_rewards_ada
            epoch_bucket_summary[epoch_no][bucket]["active_stake_ada"] += active_stake_ada
            epoch_bucket_summary[epoch_no][bucket]["block_cnt"] += block_cnt
            epoch_bucket_summary[epoch_no][bucket]["total_pool_rewards_ada"] += total_pool_rewards_ada
            if total_pool_rewards_ada > 0:
                epoch_bucket_summary[epoch_no][bucket]["rewarding_pool_cnt"] += 1

    return epoch_summary, pool_summary, overall_bucket, epoch_bucket_summary


def enrich_pool_summary(pool_summary: dict, pool_list: Dict[str, dict], current_saturation_point_ada: float) -> List[dict]:
    rows = []
    for pool_id, row in pool_summary.items():
        meta = pool_list.get(pool_id, {})
        epochs_observed = max(int(row["epochs_observed"]), 1)
        mean_active_stake_ada = row["sum_active_stake_ada"] / epochs_observed
        mean_saturation_pct = row["sum_saturation_pct"] / epochs_observed
        current_active_stake_ada = (parse_float(meta.get("active_stake")) or 0.0) / 1_000_000.0
        current_saturation_pct = (current_active_stake_ada / current_saturation_point_ada * 100.0) if current_saturation_point_ada > 0 else 0.0
        if current_active_stake_ada > 0.0:
            current_size_bucket = size_bucket_label(current_active_stake_ada, current_saturation_pct)
        else:
            current_size_bucket = "Zero-stake pools"
        total_pool_rewards_ada = row["total_pool_rewards_ada"]
        operator_fee_share_pct = (row["total_pool_fees_ada"] / total_pool_rewards_ada * 100.0) if total_pool_rewards_ada > 0 else 0.0
        owner_member_share_pct = (row["total_owner_member_rewards_ada"] / total_pool_rewards_ada * 100.0) if total_pool_rewards_ada > 0 else 0.0
        public_member_share_pct = (row["total_member_rewards_ada"] / total_pool_rewards_ada * 100.0) if total_pool_rewards_ada > 0 else 0.0
        rows.append(
            {
                "pool_id_bech32": pool_id,
                "ticker": meta.get("ticker", "") or "",
                "pool_status_current": meta.get("pool_status", "") or "",
                "active_epoch_no_current": meta.get("active_epoch_no", "") or "",
                "retiring_epoch_current": meta.get("retiring_epoch", "") or "",
                "current_active_stake_ada": current_active_stake_ada,
                "current_saturation_pct": current_saturation_pct,
                "current_size_bucket": current_size_bucket,
                "epochs_observed": epochs_observed,
                "mean_active_stake_ada": mean_active_stake_ada,
                "mean_saturation_pct": mean_saturation_pct,
                "mean_size_bucket": size_bucket_label(mean_active_stake_ada, mean_saturation_pct),
                "total_blocks": row["total_blocks"],
                "total_pool_fees_ada": row["total_pool_fees_ada"],
                "total_deleg_rewards_ada": row["total_deleg_rewards_ada"],
                "total_member_rewards_ada": row["total_member_rewards_ada"],
                "total_owner_member_rewards_ada": row["total_owner_member_rewards_ada"],
                "total_pool_rewards_ada": total_pool_rewards_ada,
                "avg_pool_rewards_epoch_ada": total_pool_rewards_ada / epochs_observed,
                "operator_fee_share_pct": operator_fee_share_pct,
                "owner_member_share_pct": owner_member_share_pct,
                "public_member_share_pct": public_member_share_pct,
            }
        )
    rows.sort(key=lambda x: x["total_pool_rewards_ada"], reverse=True)
    return rows


def write_csv(rows: List[dict], out_path: Path) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write for {out_path}")
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def add_report_checkpoint_marker(ax: plt.Axes) -> None:
    ax.axvline(REPORT_CHECKPOINT_EPOCH, color="#7f8c8d", linestyle=":", linewidth=1.2, alpha=0.9)
    ax.text(
        REPORT_CHECKPOINT_EPOCH - 4,
        0.90,
        REPORT_CHECKPOINT_LABEL,
        transform=ax.get_xaxis_transform(),
        ha="right",
        va="top",
        fontsize=9,
        color="#4b5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#d1d5db", alpha=0.9),
    )


def render_distribution_by_size(
    epoch_summary: dict,
    epoch_bucket_summary: dict,
    out_path: Path,
    *,
    epoch_min: int | None = None,
    window_label: str = "full Shelley window",
    show_checkpoint_marker: bool = True,
    include_aggregate: bool = True,
    include_timeseries: bool = True,
) -> Dict[str, dict]:
    labels = [label for label, _ in REWARD_ANALYSIS_CATEGORIES]
    epochs = sorted(epoch for epoch in epoch_summary if epoch_min is None or epoch >= epoch_min)
    total_stake = sum(epoch_bucket_summary[epoch][label]["active_stake_ada"] for epoch in epochs for label in labels)
    total_blocks = sum(epoch_bucket_summary[epoch][label]["block_cnt"] for epoch in epochs for label in labels)
    total_rewards = sum(epoch_bucket_summary[epoch][label]["total_pool_rewards_ada"] for epoch in epochs for label in labels)

    stake_share = [
        (
            sum(epoch_bucket_summary[epoch][label]["active_stake_ada"] for epoch in epochs) / total_stake * 100.0
        )
        if total_stake
        else 0.0
        for label in labels
    ]
    block_share = [
        (
            sum(epoch_bucket_summary[epoch][label]["block_cnt"] for epoch in epochs) / total_blocks * 100.0
        )
        if total_blocks
        else 0.0
        for label in labels
    ]
    reward_share = [
        (
            sum(epoch_bucket_summary[epoch][label]["total_pool_rewards_ada"] for epoch in epochs) / total_rewards * 100.0
        )
        if total_rewards
        else 0.0
        for label in labels
    ]
    x = np.arange(len(labels))
    width = 0.25

    if include_timeseries and include_aggregate:
        reward_share_series = {
            label: [
                (
                    epoch_bucket_summary[epoch][label]["total_pool_rewards_ada"]
                    / max(epoch_summary[epoch]["total_pool_rewards_ada"], 1e-9)
                    * 100.0
                )
                for epoch in epochs
            ]
            for label in labels
        }

        fig, (ax1, ax2) = plt.subplots(
            2,
            1,
            figsize=(14.5, 10.2),
            sharex=False,
            gridspec_kw={"height_ratios": [1.0, 1.3]},
        )
        ax1.bar(x - width, stake_share, width=width, label="Active stake share", color="#9ecae1")
        ax1.bar(x, block_share, width=width, label="Block share", color="#3182bd")
        ax1.bar(x + width, reward_share, width=width, label="Reward share", color="#08519c")
        ax1.set_xticks(x)
        ax1.set_xticklabels([DISPLAY_LABELS.get(label, label) for label in labels], fontsize=10)
        ax1.set_ylabel(f"Share of {window_label} (%)")
        ax1.grid(axis="y", alpha=0.2)
        ax1.legend(loc="upper left")

        for label, color in REWARD_ANALYSIS_CATEGORIES:
            ax2.plot(epochs, reward_share_series[label], linewidth=1.6, label=label, color=color)
        if show_checkpoint_marker:
            add_report_checkpoint_marker(ax2)
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Reward share in epoch (%)")
        ax2.grid(alpha=0.2)
        ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=4)
    elif include_timeseries:
        reward_share_series = {
            label: [
                (
                    epoch_bucket_summary[epoch][label]["total_pool_rewards_ada"]
                    / max(epoch_summary[epoch]["total_pool_rewards_ada"], 1e-9)
                    * 100.0
                )
                for epoch in epochs
            ]
            for label in labels
        }

        fig, ax1 = plt.subplots(1, 1, figsize=(14.5, 6.6))
        for label, color in REWARD_ANALYSIS_CATEGORIES:
            ax1.plot(epochs, reward_share_series[label], linewidth=1.9, label=label, color=color)
        if show_checkpoint_marker:
            add_report_checkpoint_marker(ax1)
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Reward share in epoch (%)")
        ax1.grid(alpha=0.2)
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=4)
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(14.2, 5.6))
        ax1.bar(x - width, stake_share, width=width, label="Active stake share", color="#9ecae1")
        ax1.bar(x, block_share, width=width, label="Block share", color="#3182bd")
        ax1.bar(x + width, reward_share, width=width, label="Reward share", color="#08519c")
        ax1.set_xticks(x)
        ax1.set_xticklabels([DISPLAY_LABELS.get(label, label) for label in labels], fontsize=10)
        ax1.set_ylabel(f"Share of {window_label} (%)")
        ax1.grid(axis="y", alpha=0.2)
        ax1.legend(loc="upper left")

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    return {
        label: {
            "stake_share_pct": stake,
            "block_share_pct": blocks,
            "reward_share_pct": rewards,
        }
        for label, stake, blocks, rewards in zip(labels, stake_share, block_share, reward_share)
    }


def render_concentration(pool_rows: List[dict], out_path: Path) -> Dict[str, object]:
    rows = [r for r in pool_rows if r["total_pool_rewards_ada"] > 0]
    current_healthy_plus_rows = [
        r
        for r in rows
        if r["pool_status_current"] == "registered"
        and r["current_active_stake_ada"] > 0.0
        and r["current_size_bucket"] in {label for label, _, _ in TOP_N_COMPOSITION_BUCKETS}
    ]
    rewards = np.array([r["total_pool_rewards_ada"] for r in rows], dtype=float)
    stake = np.array([r["mean_active_stake_ada"] for r in rows], dtype=float)
    total_rewards = float(np.sum(rewards))
    total_stake = float(np.sum(stake))
    cum_rewards = np.cumsum(rewards) / total_rewards * 100.0 if total_rewards else np.array([])
    cum_stake = np.cumsum(stake) / total_stake * 100.0 if total_stake else np.array([])
    ranks = np.arange(1, len(rows) + 1)
    top_cutoffs = [10, 50, 100, 250]
    comp_cohorts: List[Tuple[str, int, str | int]] = [
        (f"Top {n}", n, n) for n in top_cutoffs if n <= len(current_healthy_plus_rows)
    ]
    if current_healthy_plus_rows:
        comp_cohorts.append(("All current healthy\nand above", len(current_healthy_plus_rows), "all_healthy_plus"))

    fig, (ax, ax_comp) = plt.subplots(
        1,
        2,
        figsize=(15.6, 8.2),
        gridspec_kw={"width_ratios": [1.85, 1.0]},
    )

    ax.plot(ranks, cum_rewards, color="#d62728", linewidth=2.0, label="Cumulative reward share")
    ax.plot(ranks, cum_stake, color="#111111", linewidth=1.8, label="Cumulative mean active stake share")
    for n in top_cutoffs:
        if n <= len(rows):
            ax.scatter([n], [cum_rewards[n - 1]], color="#d62728", s=28)
            ax.text(n, cum_rewards[n - 1] + 1.5, f"Top {n}: {cum_rewards[n - 1]:.1f}%", fontsize=9)
    ax.set_xscale("log")
    ax.set_xlabel("Top N pools ranked by total rewards")
    ax.set_ylabel("Cumulative share (%)")
    ax.grid(alpha=0.2, which="both")
    ax.legend(loc="lower right")

    comp_labels = [label for label, _, _ in TOP_N_COMPOSITION_BUCKETS]
    comp_colors = {label: color for label, color, _ in TOP_N_COMPOSITION_BUCKETS}
    composition_stats: Dict[object, Dict[str, object]] = {}
    y_positions = np.arange(len(comp_cohorts))
    left = np.zeros(len(comp_cohorts))
    for label in comp_labels:
        widths = []
        counts = []
        for _, cohort_size, _ in comp_cohorts:
            subset = current_healthy_plus_rows[:cohort_size]
            count = sum(1 for row in subset if top_n_bucket_label(row["current_size_bucket"]) == label)
            widths.append(count / cohort_size * 100.0 if cohort_size else 0.0)
            counts.append(count)
        bars = ax_comp.barh(
            y_positions,
            widths,
            left=left,
            color=comp_colors[label],
            edgecolor="white",
            linewidth=0.6,
            label=label,
            height=0.68,
        )
        for bar, width, count in zip(bars, widths, counts):
            if width >= 12.0:
                ax_comp.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    bar.get_y() + bar.get_height() / 2.0,
                    str(count),
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                    fontweight="bold",
                )
        left += np.array(widths)

    for cohort_label, cohort_size, cohort_key in comp_cohorts:
        subset = current_healthy_plus_rows[:cohort_size]
        category_counts = {}
        for label in comp_labels:
            count = sum(1 for row in subset if top_n_bucket_label(row["current_size_bucket"]) == label)
            if count:
                category_counts[label] = count
        composition_stats[cohort_key] = {
            "label": cohort_label,
            "size": cohort_size,
            "counts": category_counts,
        }

    ax_comp.set_xlim(0, 100)
    ax_comp.set_xticks([0, 25, 50, 75, 100])
    ax_comp.set_xlabel("Share of pools in cohort (%)")
    ax_comp.set_yticks(y_positions)
    ax_comp.set_yticklabels([label for label, _, _ in comp_cohorts])
    ax_comp.invert_yaxis()
    ax_comp.grid(axis="x", alpha=0.2)
    ax_comp.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    stats: Dict[str, object] = {"category_composition": composition_stats}
    stats["healthy_plus_pool_count"] = len(current_healthy_plus_rows)
    for n in top_cutoffs:
        if n <= len(rows):
            stats[f"top{n}_reward_share_pct"] = float(cum_rewards[n - 1])
            stats[f"top{n}_stake_share_pct"] = float(cum_stake[n - 1])
    return stats


def render_split_mechanics(pool_rows: List[dict], out_path: Path) -> Dict[str, dict]:
    labels = [label for label, _ in REWARD_ANALYSIS_CATEGORIES]
    bucket_summary = {}
    fee_share = []
    owner_share = []
    public_share = []
    median_reward_epoch = []

    scatter_rows = [r for r in pool_rows if r["total_pool_rewards_ada"] > 0]

    for label in labels:
        subset = [r for r in pool_rows if r["mean_size_bucket"] == label and r["total_pool_rewards_ada"] > 0]
        if subset:
            fee_vals = np.array([r["operator_fee_share_pct"] for r in subset], dtype=float)
            owner_vals = np.array([r["owner_member_share_pct"] for r in subset], dtype=float)
            public_vals = np.array([r["public_member_share_pct"] for r in subset], dtype=float)
            reward_vals = np.array([r["avg_pool_rewards_epoch_ada"] for r in subset], dtype=float)
            fee_share.append(float(np.median(fee_vals)))
            owner_share.append(float(np.median(owner_vals)))
            public_share.append(float(np.median(public_vals)))
            median_reward_epoch.append(float(np.median(reward_vals)))
            bucket_summary[label] = {
                "median_operator_fee_share_pct": float(np.median(fee_vals)),
                "median_owner_member_share_pct": float(np.median(owner_vals)),
                "median_public_member_share_pct": float(np.median(public_vals)),
                "median_reward_epoch_ada": float(np.median(reward_vals)),
                "n_pools": len(subset),
            }
        else:
            fee_share.append(0.0)
            owner_share.append(0.0)
            public_share.append(0.0)
            median_reward_epoch.append(0.0)
            bucket_summary[label] = {
                "median_operator_fee_share_pct": 0.0,
                "median_owner_member_share_pct": 0.0,
                "median_public_member_share_pct": 0.0,
                "median_reward_epoch_ada": 0.0,
                "n_pools": 0,
            }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5))
    x = np.arange(len(labels))
    ax1.bar(x, fee_share, color="#e15759", label="Operator fees")
    ax1.bar(x, owner_share, bottom=fee_share, color="#f28e2b", label="Owner member-like rewards")
    ax1.bar(x, public_share, bottom=np.array(fee_share) + np.array(owner_share), color="#4e79a7", label="Public delegator/member rewards")
    ax1.set_xticks(x)
    ax1.set_xticklabels([DISPLAY_LABELS.get(label, label) for label in labels], fontsize=10)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Median share of pool reward (%)")
    ax1.grid(axis="y", alpha=0.2)
    ax1.legend(loc="upper right", fontsize=9)
    ax1b = ax1.twinx()
    ax1b.plot(x, median_reward_epoch, color="#111111", linewidth=1.8, marker="o")
    ax1b.set_ylabel("Median pool reward per epoch (ADA)")

    ax2.scatter(
        [r["mean_active_stake_ada"] for r in scatter_rows],
        [r["operator_fee_share_pct"] for r in scatter_rows],
        s=16,
        alpha=0.45,
        color="#3182bd",
    )
    ax2.set_xscale("log")
    ax2.set_xlabel("Mean active stake (ADA, log scale)")
    ax2.set_ylabel("Operator fee share of total pool reward (%)")
    ax2.grid(alpha=0.2, which="both")
    ax2.axhline(50.0, color="#777777", linestyle="--", linewidth=1.0)

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    return bucket_summary


def write_summary(
    epoch_rows: List[dict],
    pool_rows: List[dict],
    bucket_distribution: Dict[str, dict],
    concentration_stats: Dict[str, float],
    split_stats: Dict[str, dict],
    reward_epoch_totals: Dict[int, float],
    out_path: Path,
) -> None:
    total_rewards = float(np.sum([r["total_pool_rewards_ada"] for r in epoch_rows]))
    total_operator_fees = float(np.sum([r["pool_fees_ada"] for r in epoch_rows]))
    total_public_member_rewards = float(np.sum([r["member_rewards_ada"] for r in epoch_rows]))
    total_owner_member_rewards = float(np.sum([r["owner_member_rewards_ada"] for r in epoch_rows]))

    diffs = []
    for row in epoch_rows:
        epoch_no = int(row["epoch_no"])
        if epoch_no in reward_epoch_totals:
            diffs.append(row["total_pool_rewards_ada"] - reward_epoch_totals[epoch_no])
    median_abs_diff = float(np.median(np.abs(diffs))) if diffs else math.nan
    max_abs_diff = float(np.max(np.abs(diffs))) if diffs else math.nan

    md = [
        "# Pool Reward Distribution Summary (Mainnet)",
        "",
        f"- Pool-history epochs covered: **{min(r['epoch_no'] for r in epoch_rows)}..{max(r['epoch_no'] for r in epoch_rows)}**",
        f"- Pools with reward history: **{len(pool_rows):,}**",
        f"- Epoch rows in summary: **{len(epoch_rows):,}**",
        f"- Total realized pool rewards since Shelley: **{total_rewards/1_000_000:.2f}M ADA**",
        "",
        "## Exact split from Koios pool history",
        f"- Operator fees: **{total_operator_fees/1_000_000:.2f}M ADA**",
        f"- Owner member-like rewards: **{total_owner_member_rewards/1_000_000:.2f}M ADA**",
        f"- Public delegator/member rewards: **{total_public_member_rewards/1_000_000:.2f}M ADA**",
        "",
        "## Cross-check against epoch-wide reward totals",
        "- `koios_pool_history_mainnet.csv` is summed by epoch and compared with `reward_epoch_pools_mainnet.csv`.",
        f"- Median absolute epoch difference: **{median_abs_diff:.4f} ADA**",
        f"- Max absolute epoch difference: **{max_abs_diff:.4f} ADA**",
        "",
        "## Reward concentration",
        f"- Top 10 pools captured **{concentration_stats.get('top10_reward_share_pct', 0.0):.1f}%** of all realized rewards since Shelley.",
        f"- Top 50 pools captured **{concentration_stats.get('top50_reward_share_pct', 0.0):.1f}%**.",
        f"- Top 100 pools captured **{concentration_stats.get('top100_reward_share_pct', 0.0):.1f}%**.",
        f"- Top 250 pools captured **{concentration_stats.get('top250_reward_share_pct', 0.0):.1f}%**.",
        f"- Top 10 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 10))}**.",
        f"- Top 50 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 50))}**.",
        f"- Top 100 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 100))}**.",
        f"- Top 250 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 250))}**.",
        f"- All current healthy-and-above pools (`n={int(concentration_stats.get('healthy_plus_pool_count', 0))}`) bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 'all_healthy_plus'))}**.",
        "",
        "## Distribution by size category",
    ]

    for label, _ in REWARD_ANALYSIS_CATEGORIES:
        stats = bucket_distribution[label]
        md.append(
            f"- `{label}`: active stake share **{stats['stake_share_pct']:.1f}%**, "
            f"block share **{stats['block_share_pct']:.1f}%**, "
            f"reward share **{stats['reward_share_pct']:.1f}%**"
        )

    md.extend(["", "## Exact reward split by size category"])
    for label, _ in REWARD_ANALYSIS_CATEGORIES:
        stats = split_stats[label]
        md.append(
            f"- `{label}` (`n={stats['n_pools']}`): operator fees **{stats['median_operator_fee_share_pct']:.1f}%**, "
            f"owner member-like rewards **{stats['median_owner_member_share_pct']:.1f}%**, "
            f"public delegator/member rewards **{stats['median_public_member_share_pct']:.1f}%**, "
            f"median pool reward **{stats['median_reward_epoch_ada']:.1f} ADA/epoch**"
        )

    md.extend(
        [
            "",
            "## What this unlocks next",
            "- We now have exact realized pool-level reward splits from Shelley to current tip.",
            "- The next step is pledge compliance and parameter-change analysis using `pool_owner_history` and `pool_updates`.",
            "",
        ]
    )
    out_path.write_text("\n".join(md))


def write_doc(
    recent_bucket_distribution: Dict[str, dict],
    bucket_distribution: Dict[str, dict],
    concentration_stats: Dict[str, float],
    split_stats: Dict[str, dict],
    fig_distribution_recent_path: Path,
    fig_distribution_path: Path,
    fig_concentration_path: Path,
    fig_split_path: Path,
    summary_path: Path,
    out_path: Path,
) -> None:
    lines = [
        "# Pool Reward Distribution Analysis (Mainnet)",
        "",
        r"Target quantity: realized pool-level rewards since Shelley using Koios `pool_history`.",
        "",
        "## Objective",
        "Go one level below the epoch-wide reward pot and inspect how realized rewards were distributed across pools from the start of Shelley to current mainnet tip.",
        "",
        "## Data source",
        "- `koios_pool_history_mainnet.csv` provides pool-by-pool, epoch-by-epoch realized rewards, operator fees, member rewards, block counts, and active stake.",
        "- `koios_pool_list_mainnet.csv` provides current pool metadata and ticker/status enrichment.",
        "- `reward_epoch_pools_mainnet.csv` is used only as a cross-check against the epoch-wide pool reward total.",
        "",
        "## Exact split now available",
        r"- Total pool reward: $Reward^{pool}_{actual}=Fee^{operator}_{pool}+Reward^{delegators}_{pool}$",
        r"- Public delegator/member rewards come from `member_rewards`.",
        r"- Owner member-like rewards are inferred as $Reward^{delegators}_{pool}-Reward^{members}_{pool}$ when `member_rewards` is available.",
        "",
        f"[Summary]({summary_path.name})",
        "",
        "## Graph 1: Reward Distribution Since the Prior Report Checkpoint",
        f"Window: epochs `{REPORT_CHECKPOINT_EPOCH}..latest`.",
        "",
        f"![Distribution by size since checkpoint](../figures/{fig_distribution_recent_path.name})",
        "",
        "## Graph 2: Reward Distribution Across the Full Shelley Window",
        "Top panel: full-window distribution of stake, blocks, and rewards by reward-bearing size categories.",
        "Bottom panel: how reward share by reward-bearing size categories evolved over time.",
        "",
        f"![Distribution by size](../figures/{fig_distribution_path.name})",
        "",
        "## Graph 3: Reward Concentration",
        "Pools are ranked by total realized rewards since Shelley.",
        "",
        f"![Reward concentration](../figures/{fig_concentration_path.name})",
        "",
        "## Graph 4: Exact Reward Split Mechanics",
        "Left panel: median exact split of pool reward by size category.",
        "Right panel: operator fee share as a function of pool scale.",
        "",
        f"![Reward split](../figures/{fig_split_path.name})",
        "",
        "## First read (full Shelley window)",
    ]

    for label, _ in REWARD_ANALYSIS_CATEGORIES:
        stats = bucket_distribution[label]
        lines.append(
            f"- `{label}`: reward share **{stats['reward_share_pct']:.1f}%**, "
            f"block share **{stats['block_share_pct']:.1f}%**"
        )

    lines.extend(["", "## Recent-window read (since prior report checkpoint)"])
    for label, _ in REWARD_ANALYSIS_CATEGORIES:
        stats = recent_bucket_distribution[label]
        lines.append(
            f"- `{label}`: reward share **{stats['reward_share_pct']:.1f}%**, "
            f"block share **{stats['block_share_pct']:.1f}%**"
        )

    lines.extend(
        [
            f"- Top 10 pools captured **{concentration_stats.get('top10_reward_share_pct', 0.0):.1f}%** of realized rewards.",
            f"- Top 50 pools captured **{concentration_stats.get('top50_reward_share_pct', 0.0):.1f}%**.",
            f"- Top 100 pools captured **{concentration_stats.get('top100_reward_share_pct', 0.0):.1f}%**.",
            f"- Top 250 pools captured **{concentration_stats.get('top250_reward_share_pct', 0.0):.1f}%**.",
            f"- Top 10 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 10))}**.",
            f"- Top 50 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 50))}**.",
            f"- Top 100 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 100))}**.",
            f"- Top 250 bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 250))}**.",
            f"- All current healthy-and-above pools (`n={int(concentration_stats.get('healthy_plus_pool_count', 0))}`) bucket mix: **{format_top_n_category_mix(composition_counts(concentration_stats, 'all_healthy_plus'))}**.",
            "",
            "## Exact split by size",
        ]
    )

    for label, _ in REWARD_ANALYSIS_CATEGORIES:
        stats = split_stats[label]
        lines.append(
            f"- `{label}`: operator fees **{stats['median_operator_fee_share_pct']:.1f}%**, "
            f"public delegator/member rewards **{stats['median_public_member_share_pct']:.1f}%**, "
            f"median pool reward **{stats['median_reward_epoch_ada']:.1f} ADA/epoch**"
        )

    lines.extend(
        [
            "",
            "## Next level down",
            "- Add `pool_updates` to make size-category and fee-regime transitions explicit over time.",
            "- Add `pool_owner_history` to test pledge compliance and owner-capital effects directly.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "scenarii-evaluation" / "data"
    figures_dir = root / "scenarii-evaluation" / "figures"
    outputs_dir = root / "scenarii-evaluation" / "outputs"
    docs_dir = root / "scenarii-evaluation" / "docs"

    pool_list_path = data_dir / "koios_pool_list_mainnet.csv"
    pool_history_path = data_dir / "koios_pool_history_mainnet.csv"
    reward_epoch_totals_path = data_dir / "reward_epoch_pools_mainnet.csv"

    if not pool_list_path.exists() or not pool_history_path.exists():
        raise RuntimeError("Run fetch_pool_history_mainnet.py first.")

    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    epoch_summary_path = data_dir / "pool_reward_epoch_summary_mainnet.csv"
    pool_summary_path = data_dir / "pool_reward_pool_summary_mainnet.csv"
    fig_distribution_recent_path = figures_dir / "pool_reward_distribution_by_size_recent_mainnet.png"
    fig_distribution_path = figures_dir / "pool_reward_distribution_by_size_mainnet.png"
    fig_concentration_path = figures_dir / "pool_reward_concentration_mainnet.png"
    fig_split_path = figures_dir / "pool_reward_split_mechanics_mainnet.png"
    summary_path = outputs_dir / "pool_reward_distribution_mainnet_summary.md"
    doc_path = docs_dir / "pool-reward-distribution-mainnet.md"

    pool_list = read_pool_list(pool_list_path)
    reward_epoch_totals = read_reward_epoch_totals(reward_epoch_totals_path) if reward_epoch_totals_path.exists() else {}
    current_saturation_point_ada = read_latest_saturation_point(reward_epoch_totals_path) if reward_epoch_totals_path.exists() else 0.0
    epoch_summary, pool_summary, overall_bucket, epoch_bucket_summary = compute_summaries(pool_history_path)
    pool_rows = enrich_pool_summary(pool_summary, pool_list, current_saturation_point_ada)
    epoch_rows = [epoch_summary[epoch] for epoch in sorted(epoch_summary)]

    write_csv(epoch_rows, epoch_summary_path)
    write_csv(pool_rows, pool_summary_path)

    plt.style.use("seaborn-v0_8-whitegrid")
    recent_bucket_distribution = render_distribution_by_size(
        epoch_summary,
        epoch_bucket_summary,
        fig_distribution_recent_path,
        epoch_min=REPORT_CHECKPOINT_EPOCH,
        window_label="recent window",
        show_checkpoint_marker=False,
        include_timeseries=False,
    )
    bucket_distribution = render_distribution_by_size(
        epoch_summary,
        epoch_bucket_summary,
        fig_distribution_path,
        window_label="full Shelley window",
        show_checkpoint_marker=True,
        include_aggregate=False,
    )
    concentration_stats = render_concentration(pool_rows, fig_concentration_path)
    split_stats = render_split_mechanics(pool_rows, fig_split_path)
    write_summary(epoch_rows, pool_rows, bucket_distribution, concentration_stats, split_stats, reward_epoch_totals, summary_path)
    write_doc(
        recent_bucket_distribution,
        bucket_distribution,
        concentration_stats,
        split_stats,
        fig_distribution_recent_path,
        fig_distribution_path,
        fig_concentration_path,
        fig_split_path,
        summary_path,
        doc_path,
    )

    print(f"Wrote: {epoch_summary_path}")
    print(f"Wrote: {pool_summary_path}")
    print(f"Wrote: {fig_distribution_recent_path}")
    print(f"Wrote: {fig_distribution_path}")
    print(f"Wrote: {fig_concentration_path}")
    print(f"Wrote: {fig_split_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {doc_path}")


if __name__ == "__main__":
    main()
