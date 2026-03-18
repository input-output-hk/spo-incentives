#!/usr/bin/env python3
"""
Build pledge-compliance and pool-update analysis from Koios mainnet datasets.

Required inputs:
- scenarii-evaluation/data/koios_pool_history_mainnet.csv
- scenarii-evaluation/data/koios_pool_updates_mainnet.csv
- scenarii-evaluation/data/koios_pool_owner_history_mainnet.csv

Outputs:
- scenarii-evaluation/data/pool_pledge_epoch_summary_mainnet.csv
- scenarii-evaluation/data/pool_pledge_pool_summary_mainnet.csv
- scenarii-evaluation/data/pool_update_epoch_summary_mainnet.csv
- scenarii-evaluation/figures/pool_pledge_compliance_mainnet.png
- scenarii-evaluation/figures/pool_fee_regime_state_mainnet.png
- scenarii-evaluation/figures/pool_pledge_pool_distribution_mainnet.png
- scenarii-evaluation/outputs/pool_pledge_and_updates_mainnet_summary.md
- scenarii-evaluation/docs/pool-pledge-and-updates-mainnet.md
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


SIZE_BUCKETS: List[Tuple[str, float, float]] = [
    ("<3M", 0.0, 3_000_000.0),
    ("3M-10M", 3_000_000.0, 10_000_000.0),
    ("10M-30M", 10_000_000.0, 30_000_000.0),
    ("30M-70M", 30_000_000.0, 70_000_000.0),
    (">70M", 70_000_000.0, math.inf),
]
REPORT_CHECKPOINT_EPOCH = 593
REPORT_CHECKPOINT_LABEL = "Prior report checkpoint\nNov 6, 2025"


def size_bucket_label(stake_ada: float) -> str:
    for label, lo, hi in SIZE_BUCKETS:
        if stake_ada >= lo and stake_ada < hi:
            return label
    return SIZE_BUCKETS[-1][0]


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return float(text)


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return int(text)


def median_or_none(values: List[float]) -> float | None:
    if not values:
        return None
    return float(np.median(np.array(values, dtype=float)))


def load_owner_history_agg(path: Path) -> tuple[dict, int]:
    agg = {}
    row_count = 0
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            key = (row["pool_id_bech32"], int(row["epoch_no"]))
            entry = agg.get(key)
            if entry is None:
                entry = {
                    "declared_pledge_lovelace": 0,
                    "owner_active_stake_lovelace": 0,
                }
                agg[key] = entry
            declared_pledge = parse_int(row["declared_pledge_lovelace"]) or 0
            owner_active_stake = parse_int(row["owner_active_stake_lovelace"]) or 0
            entry["declared_pledge_lovelace"] = max(entry["declared_pledge_lovelace"], declared_pledge)
            entry["owner_active_stake_lovelace"] += owner_active_stake
    return agg, row_count


def load_pool_updates(path: Path) -> tuple[dict, dict, int]:
    updates_by_pool = defaultdict(list)
    epoch_events = defaultdict(
        lambda: {
            "epoch_no": 0,
            "update_cnt": 0,
            "registration_update_cnt": 0,
            "deregistration_update_cnt": 0,
            "pool_ids": set(),
        }
    )
    row_count = 0
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            active_epoch_no = parse_int(row["active_epoch_no"])
            if active_epoch_no is None:
                continue
            pool_id = row["pool_id_bech32"]
            update_type = (row.get("update_type") or "").strip()
            update = {
                "active_epoch_no": active_epoch_no,
                "block_time": parse_int(row["block_time"]) or 0,
                "margin": parse_float(row["margin"]),
                "fixed_cost_ada": parse_float(row["fixed_cost_ada"]),
                "pledge_lovelace": parse_int(row["pledge_lovelace"]),
                "update_type": update_type,
                "retiring_epoch": parse_int(row["retiring_epoch"]),
            }
            updates_by_pool[pool_id].append(update)

            event = epoch_events[active_epoch_no]
            event["epoch_no"] = active_epoch_no
            event["update_cnt"] += 1
            event["pool_ids"].add(pool_id)
            if update_type == "registration":
                event["registration_update_cnt"] += 1
            elif update_type == "deregistration":
                event["deregistration_update_cnt"] += 1

    for updates in updates_by_pool.values():
        updates.sort(key=lambda row: (row["active_epoch_no"], row["block_time"]))
    return updates_by_pool, epoch_events, row_count


def default_epoch_summary() -> dict:
    return {
        "epoch_no": 0,
        "pool_cnt": 0,
        "total_pool_rewards_ada": 0.0,
        "total_active_stake_ada": 0.0,
        "pools_with_observed_pledge": 0,
        "pledge_met_pool_cnt": 0,
        "pledge_unmet_pool_cnt": 0,
        "reward_from_unmet_ada": 0.0,
        "active_stake_from_unmet_ada": 0.0,
        "blocks_from_unmet": 0,
        "_margin_rates": [],
        "_fixed_cost_adas": [],
        "_coverage_ratios": [],
    }


def finalize_epoch_row(epoch_row: dict, update_event: dict | None) -> dict:
    observed_pools = epoch_row["pools_with_observed_pledge"]
    total_rewards = epoch_row["total_pool_rewards_ada"]
    total_active_stake = epoch_row["total_active_stake_ada"]
    margin_rates = epoch_row.pop("_margin_rates")
    fixed_cost_adas = epoch_row.pop("_fixed_cost_adas")
    coverage_ratios = epoch_row.pop("_coverage_ratios")

    row = dict(epoch_row)
    row["pledge_met_share_pct"] = (row["pledge_met_pool_cnt"] / observed_pools * 100.0) if observed_pools else 0.0
    row["pledge_unmet_share_pct"] = (row["pledge_unmet_pool_cnt"] / observed_pools * 100.0) if observed_pools else 0.0
    row["reward_share_from_unmet_pct"] = (row["reward_from_unmet_ada"] / total_rewards * 100.0) if total_rewards else 0.0
    row["active_stake_share_from_unmet_pct"] = (row["active_stake_from_unmet_ada"] / total_active_stake * 100.0) if total_active_stake else 0.0
    row["median_margin_rate"] = median_or_none(margin_rates)
    row["median_margin_pct"] = None if row["median_margin_rate"] is None else row["median_margin_rate"] * 100.0
    row["median_fixed_cost_ada"] = median_or_none(fixed_cost_adas)
    row["pct_fixed_cost_340"] = (
        sum(1 for value in fixed_cost_adas if abs(value - 340.0) < 1e-9) / len(fixed_cost_adas) * 100.0 if fixed_cost_adas else 0.0
    )
    row["median_pledge_coverage_ratio"] = median_or_none(coverage_ratios)
    row["update_cnt"] = 0 if update_event is None else update_event["update_cnt"]
    row["registration_update_cnt"] = 0 if update_event is None else update_event["registration_update_cnt"]
    row["deregistration_update_cnt"] = 0 if update_event is None else update_event["deregistration_update_cnt"]
    row["distinct_updated_pool_cnt"] = 0 if update_event is None else len(update_event["pool_ids"])
    return row


def process_pool_rows(
    pool_rows: List[dict],
    updates_by_pool: dict,
    owner_history_agg: dict,
    epoch_summary: dict,
) -> dict:
    pool_id = pool_rows[0]["pool_id_bech32"]
    rows = sorted(pool_rows, key=lambda row: int(row["epoch_no"]))
    updates = updates_by_pool.get(pool_id, [])
    update_idx = -1
    current_update = None

    pool_summary = {
        "pool_id_bech32": pool_id,
        "epochs_observed": 0,
        "epochs_with_observed_pledge": 0,
        "pledge_met_epoch_cnt": 0,
        "pledge_unmet_epoch_cnt": 0,
        "sum_active_stake_ada": 0.0,
        "total_pool_rewards_ada": 0.0,
        "reward_from_unmet_ada": 0.0,
        "sum_margin_rate": 0.0,
        "margin_observation_cnt": 0,
    }

    for row in rows:
        epoch_no = int(row["epoch_no"])
        while update_idx + 1 < len(updates) and updates[update_idx + 1]["active_epoch_no"] <= epoch_no:
            update_idx += 1
            current_update = updates[update_idx]

        active_stake_ada = parse_float(row["active_stake_ada"]) or 0.0
        total_pool_rewards_ada = parse_float(row["total_pool_rewards_ada"]) or 0.0
        block_cnt = int(parse_float(row["block_cnt"]) or 0.0)

        owner_obs = owner_history_agg.get((pool_id, epoch_no))
        declared_pledge_lovelace = None
        owner_active_stake_lovelace = None
        if owner_obs is not None:
            declared_pledge_lovelace = owner_obs["declared_pledge_lovelace"]
            owner_active_stake_lovelace = owner_obs["owner_active_stake_lovelace"]
        elif current_update is not None:
            declared_pledge_lovelace = current_update["pledge_lovelace"]

        pledge_met = None
        coverage_ratio = None
        if declared_pledge_lovelace is not None and owner_active_stake_lovelace is not None:
            if declared_pledge_lovelace <= 0:
                pledge_met = True
                coverage_ratio = 1.0
            else:
                pledge_met = owner_active_stake_lovelace >= declared_pledge_lovelace
                coverage_ratio = owner_active_stake_lovelace / declared_pledge_lovelace

        margin_rate = None if current_update is None else current_update["margin"]
        fixed_cost_ada = None if current_update is None else current_update["fixed_cost_ada"]

        epoch_entry = epoch_summary.get(epoch_no)
        if epoch_entry is None:
            epoch_entry = default_epoch_summary()
            epoch_entry["epoch_no"] = epoch_no
            epoch_summary[epoch_no] = epoch_entry

        epoch_entry["pool_cnt"] += 1
        epoch_entry["total_pool_rewards_ada"] += total_pool_rewards_ada
        epoch_entry["total_active_stake_ada"] += active_stake_ada
        if margin_rate is not None:
            epoch_entry["_margin_rates"].append(margin_rate)
        if fixed_cost_ada is not None:
            epoch_entry["_fixed_cost_adas"].append(fixed_cost_ada)
        if coverage_ratio is not None:
            epoch_entry["_coverage_ratios"].append(coverage_ratio)
        if pledge_met is not None:
            epoch_entry["pools_with_observed_pledge"] += 1
            if pledge_met:
                epoch_entry["pledge_met_pool_cnt"] += 1
            else:
                epoch_entry["pledge_unmet_pool_cnt"] += 1
                epoch_entry["reward_from_unmet_ada"] += total_pool_rewards_ada
                epoch_entry["active_stake_from_unmet_ada"] += active_stake_ada
                epoch_entry["blocks_from_unmet"] += block_cnt

        pool_summary["epochs_observed"] += 1
        pool_summary["sum_active_stake_ada"] += active_stake_ada
        pool_summary["total_pool_rewards_ada"] += total_pool_rewards_ada
        if margin_rate is not None:
            pool_summary["sum_margin_rate"] += margin_rate
            pool_summary["margin_observation_cnt"] += 1
        if pledge_met is not None:
            pool_summary["epochs_with_observed_pledge"] += 1
            if pledge_met:
                pool_summary["pledge_met_epoch_cnt"] += 1
            else:
                pool_summary["pledge_unmet_epoch_cnt"] += 1
                pool_summary["reward_from_unmet_ada"] += total_pool_rewards_ada

    epochs_observed = max(pool_summary["epochs_observed"], 1)
    mean_active_stake_ada = pool_summary["sum_active_stake_ada"] / epochs_observed
    observed_pledge_epochs = pool_summary["epochs_with_observed_pledge"]
    pool_summary["mean_active_stake_ada"] = mean_active_stake_ada
    pool_summary["mean_size_bucket"] = size_bucket_label(mean_active_stake_ada)
    pool_summary["avg_pool_rewards_epoch_ada"] = pool_summary["total_pool_rewards_ada"] / epochs_observed
    pool_summary["mean_margin_pct"] = (
        pool_summary["sum_margin_rate"] / pool_summary["margin_observation_cnt"] * 100.0 if pool_summary["margin_observation_cnt"] else None
    )
    pool_summary["pledge_met_epoch_share_pct"] = (
        pool_summary["pledge_met_epoch_cnt"] / observed_pledge_epochs * 100.0 if observed_pledge_epochs else 0.0
    )
    pool_summary["reward_share_when_unmet_pct"] = (
        pool_summary["reward_from_unmet_ada"] / pool_summary["total_pool_rewards_ada"] * 100.0 if pool_summary["total_pool_rewards_ada"] else 0.0
    )

    del pool_summary["sum_active_stake_ada"]
    del pool_summary["sum_margin_rate"]
    del pool_summary["margin_observation_cnt"]
    return pool_summary


def build_summaries(pool_history_path: Path, updates_by_pool: dict, owner_history_agg: dict) -> tuple[List[dict], List[dict]]:
    epoch_summary = {}
    pool_summary_rows = []

    current_pool_id = None
    current_pool_rows: List[dict] = []
    with pool_history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id_bech32"]
            if current_pool_id is None:
                current_pool_id = pool_id
            if pool_id != current_pool_id:
                pool_summary_rows.append(process_pool_rows(current_pool_rows, updates_by_pool, owner_history_agg, epoch_summary))
                current_pool_rows = []
                current_pool_id = pool_id
            current_pool_rows.append(row)

    if current_pool_rows:
        pool_summary_rows.append(process_pool_rows(current_pool_rows, updates_by_pool, owner_history_agg, epoch_summary))

    return [epoch_summary[epoch] for epoch in sorted(epoch_summary)], pool_summary_rows


def build_update_epoch_rows(epoch_rows: List[dict]) -> List[dict]:
    rows = []
    for row in epoch_rows:
        rows.append(
            {
                "epoch_no": row["epoch_no"],
                "update_cnt": row["update_cnt"],
                "registration_update_cnt": row["registration_update_cnt"],
                "deregistration_update_cnt": row["deregistration_update_cnt"],
                "distinct_updated_pool_cnt": row["distinct_updated_pool_cnt"],
                "median_margin_pct": row["median_margin_pct"],
                "median_fixed_cost_ada": row["median_fixed_cost_ada"],
                "pct_fixed_cost_340": row["pct_fixed_cost_340"],
            }
        )
    return rows


def write_csv(rows: List[dict], out_path: Path) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write for {out_path}")
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def add_report_checkpoint_marker(ax: plt.Axes, *, show_label: bool = False) -> None:
    ax.axvline(REPORT_CHECKPOINT_EPOCH, color="#7f8c8d", linestyle=":", linewidth=1.2, alpha=0.9)
    if show_label:
        ax.text(
            REPORT_CHECKPOINT_EPOCH + 2,
            0.97,
            REPORT_CHECKPOINT_LABEL,
            transform=ax.get_xaxis_transform(),
            ha="left",
            va="top",
            fontsize=9,
            color="#4b5563",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#d1d5db", alpha=0.9),
        )


def render_pledge_compliance(epoch_rows: List[dict], out_path: Path) -> Dict[str, float]:
    epochs = [row["epoch_no"] for row in epoch_rows]
    pledge_met_share = [row["pledge_met_share_pct"] for row in epoch_rows]
    reward_unmet_share = [row["reward_share_from_unmet_pct"] for row in epoch_rows]
    stake_unmet_share = [row["active_stake_share_from_unmet_pct"] for row in epoch_rows]
    observed_pools = [row["pools_with_observed_pledge"] for row in epoch_rows]
    unmet_pools = [row["pledge_unmet_pool_cnt"] for row in epoch_rows]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    ax1.plot(epochs, pledge_met_share, color="#1b9e77", linewidth=2.0, label="Pools meeting pledge (%)")
    ax1.plot(epochs, reward_unmet_share, color="#d95f02", linewidth=1.8, label="Reward share from unmet pools (%)")
    ax1.plot(epochs, stake_unmet_share, color="#7570b3", linewidth=1.6, label="Active stake share from unmet pools (%)")
    ax1.set_ylabel("Share (%)")
    ax1.grid(alpha=0.2)
    ax1.legend(
        loc="center left",
        bbox_to_anchor=(0.02, 0.46),
        frameon=True,
        framealpha=0.95,
        facecolor="white",
        edgecolor="#d1d5db",
    )
    add_report_checkpoint_marker(ax1, show_label=True)

    ax2.plot(epochs, observed_pools, color="#111111", linewidth=1.8, label="Pools with observed owner history")
    ax2.plot(epochs, unmet_pools, color="#e7298a", linewidth=1.8, label="Pools below declared pledge")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Pool count")
    ax2.grid(alpha=0.2)
    ax2.legend(loc="upper left", frameon=True, framealpha=0.95, facecolor="white", edgecolor="#d1d5db")
    add_report_checkpoint_marker(ax2)

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    return {
        "median_pledge_met_share_pct": float(np.median(np.array(pledge_met_share, dtype=float))),
        "max_reward_unmet_share_pct": float(np.max(np.array(reward_unmet_share, dtype=float))),
        "latest_pledge_met_share_pct": float(pledge_met_share[-1]),
        "latest_reward_unmet_share_pct": float(reward_unmet_share[-1]),
    }


def render_fee_regimes(epoch_rows: List[dict], out_path: Path) -> Dict[str, float]:
    epochs = [row["epoch_no"] for row in epoch_rows]
    margin_pct = [np.nan if row["median_margin_pct"] is None else row["median_margin_pct"] for row in epoch_rows]
    pct_fixed_cost_340 = [row["pct_fixed_cost_340"] for row in epoch_rows]
    registration_updates = [row["registration_update_cnt"] for row in epoch_rows]
    deregistration_updates = [row["deregistration_update_cnt"] for row in epoch_rows]
    other_updates = [row["update_cnt"] - row["registration_update_cnt"] - row["deregistration_update_cnt"] for row in epoch_rows]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    ax1.plot(epochs, margin_pct, color="#1f78b4", linewidth=2.0, label="Median active margin (%)")
    ax1.set_ylabel("Median margin (%)", color="#1f78b4")
    ax1.tick_params(axis="y", labelcolor="#1f78b4")
    ax1.grid(alpha=0.2)
    ax1b = ax1.twinx()
    ax1b.plot(epochs, pct_fixed_cost_340, color="#33a02c", linewidth=1.8, label="Pools at 340 ADA fixed cost (%)")
    ax1b.set_ylabel("340 ADA share (%)", color="#33a02c")
    ax1b.tick_params(axis="y", labelcolor="#33a02c")
    add_report_checkpoint_marker(ax1, show_label=True)

    ax2.bar(epochs, registration_updates, color="#4daf4a", width=0.9, label="Registration updates")
    ax2.bar(epochs, other_updates, bottom=np.array(registration_updates), color="#377eb8", width=0.9, label="Parameter updates")
    ax2.bar(
        epochs,
        deregistration_updates,
        bottom=np.array(registration_updates) + np.array(other_updates),
        color="#e41a1c",
        width=0.9,
        label="Deregistration updates",
    )
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Updates activating in epoch")
    ax2.grid(alpha=0.2)
    ax2.legend(loc="upper right")
    add_report_checkpoint_marker(ax2)

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    margin_array = np.array([value for value in margin_pct if not np.isnan(value)], dtype=float)
    return {
        "median_of_epoch_median_margin_pct": float(np.median(margin_array)) if len(margin_array) else math.nan,
        "latest_median_margin_pct": float(margin_pct[-1]) if not np.isnan(margin_pct[-1]) else math.nan,
        "latest_pct_fixed_cost_340": float(pct_fixed_cost_340[-1]),
        "total_updates": float(np.sum(np.array(registration_updates) + np.array(other_updates) + np.array(deregistration_updates))),
    }


def render_pool_distribution(pool_rows: List[dict], out_path: Path) -> Dict[str, float]:
    compliance_labels = ["100%", "90-100%", "50-90%", "<50%", "No obs"]
    counts = [0, 0, 0, 0, 0]
    stake_vals = []
    compliance_vals = []
    reward_vals = []

    for row in pool_rows:
        observed = int(row["epochs_with_observed_pledge"])
        compliance = float(row["pledge_met_epoch_share_pct"])
        if observed == 0:
            counts[4] += 1
        elif compliance >= 99.999:
            counts[0] += 1
        elif compliance >= 90.0:
            counts[1] += 1
        elif compliance >= 50.0:
            counts[2] += 1
        else:
            counts[3] += 1
        if observed > 0:
            stake_vals.append(float(row["mean_active_stake_ada"]))
            compliance_vals.append(compliance)
            reward_vals.append(float(row["total_pool_rewards_ada"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    ax1.bar(compliance_labels, counts, color=["#1b9e77", "#66a61e", "#e6ab02", "#d95f02", "#999999"])
    ax1.set_ylabel("Pool count")
    ax1.set_title("Pool Compliance Bands Since Shelley")
    ax1.grid(axis="y", alpha=0.2)

    scatter = ax2.scatter(stake_vals, compliance_vals, c=reward_vals, cmap="viridis", s=18, alpha=0.55)
    ax2.set_xscale("log")
    ax2.set_xlabel("Mean active stake (ADA, log scale)")
    ax2.set_ylabel("Pledge-met epoch share (%)")
    ax2.set_title("Pool Scale vs Pledge Compliance")
    ax2.grid(alpha=0.2, which="both")
    cbar = fig.colorbar(scatter, ax=ax2)
    cbar.set_label("Total realized pool rewards (ADA)")

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)

    return {
        "perfect_compliance_pool_cnt": float(counts[0]),
        "sub_90_compliance_pool_cnt": float(counts[2] + counts[3]),
        "no_observation_pool_cnt": float(counts[4]),
    }


def write_summary(
    *,
    epoch_rows: List[dict],
    pool_rows: List[dict],
    owner_history_row_count: int,
    pool_updates_row_count: int,
    pledge_stats: Dict[str, float],
    fee_stats: Dict[str, float],
    pool_dist_stats: Dict[str, float],
    out_path: Path,
) -> None:
    total_rewards = float(np.sum([row["total_pool_rewards_ada"] for row in epoch_rows]))
    total_rewards_from_unmet = float(np.sum([row["reward_from_unmet_ada"] for row in epoch_rows]))
    total_observed_pools = float(np.sum([row["pools_with_observed_pledge"] for row in epoch_rows]))
    total_unmet_pools = float(np.sum([row["pledge_unmet_pool_cnt"] for row in epoch_rows]))
    latest = epoch_rows[-1]

    lines = [
        "# Pool Pledge and Updates Summary (Mainnet)",
        "",
        f"- Reward-history epochs covered: **{epoch_rows[0]['epoch_no']}..{epoch_rows[-1]['epoch_no']}**",
        f"- Pools with reward history: **{len(pool_rows):,}**",
        f"- Raw `pool_owner_history` rows: **{owner_history_row_count:,}**",
        f"- Raw `pool_updates` rows: **{pool_updates_row_count:,}**",
        "",
        "## Pledge compliance proxy",
        f"- Median epoch pledge-met share: **{pledge_stats['median_pledge_met_share_pct']:.1f}%** of pools with observed owner history.",
        f"- Latest epoch pledge-met share: **{pledge_stats['latest_pledge_met_share_pct']:.1f}%**.",
        f"- Max epoch reward share from pledge-unmet pools: **{pledge_stats['max_reward_unmet_share_pct']:.2f}%**.",
        f"- Latest epoch reward share from pledge-unmet pools: **{pledge_stats['latest_reward_unmet_share_pct']:.2f}%**.",
        f"- Full-window realized rewards linked to pledge-unmet pool-epochs: **{total_rewards_from_unmet/1_000_000:.2f}M ADA** "
        f"({(total_rewards_from_unmet / total_rewards * 100.0) if total_rewards else 0.0:.2f}% of realized pool rewards).",
        "",
        "## Fee/update regime",
        f"- Median of epoch-median active margin: **{fee_stats['median_of_epoch_median_margin_pct']:.2f}%**.",
        f"- Latest median active margin: **{fee_stats['latest_median_margin_pct']:.2f}%**.",
        f"- Latest share of pools at 340 ADA fixed cost: **{fee_stats['latest_pct_fixed_cost_340']:.1f}%**.",
        f"- Total pool updates observed: **{int(fee_stats['total_updates']):,}**.",
        "",
        "## Pool distribution",
        f"- Pools with perfect observed compliance: **{int(pool_dist_stats['perfect_compliance_pool_cnt']):,}**.",
        f"- Pools below 90% observed compliance: **{int(pool_dist_stats['sub_90_compliance_pool_cnt']):,}**.",
        f"- Pools with no owner-history observations in the reward window: **{int(pool_dist_stats['no_observation_pool_cnt']):,}**.",
        "",
        "## Reading caveat",
        "- This is a same-epoch operational proxy built from Koios `pool_history`, `pool_owner_history`, and `pool_updates` labels.",
        "- It is useful for incentive analysis and anomaly hunting, but it is not a direct proof that a ledger reward should or should not have been zeroed.",
        "",
        "## Latest epoch snapshot",
        f"- Epoch: **{latest['epoch_no']}**",
        f"- Pools with observed owner history: **{latest['pools_with_observed_pledge']}**",
        f"- Pools below declared pledge: **{latest['pledge_unmet_pool_cnt']}**",
        f"- Median pledge coverage ratio: **{latest['median_pledge_coverage_ratio']:.3f}x**" if latest["median_pledge_coverage_ratio"] is not None else "- Median pledge coverage ratio: **n/a**",
        "",
    ]
    out_path.write_text("\n".join(lines))


def write_doc(
    *,
    summary_path: Path,
    fig_pledge_path: Path,
    fig_fee_path: Path,
    fig_pool_dist_path: Path,
    out_path: Path,
) -> None:
    lines = [
        "# Pool Pledge and Updates Analysis (Mainnet)",
        "",
        "## Objective",
        "Go one level deeper than realized pool rewards and inspect two governance-relevant mechanics:",
        "1. whether owner stake appears to meet declared pledge over time,",
        "2. how fee regimes and update activity evolved across the Shelley window.",
        "",
        "## Raw sources",
        "- `koios_pool_history_mainnet.csv`: realized pool rewards, active stake, block counts.",
        "- `koios_pool_owner_history_mainnet.csv`: owner stake by epoch and declared pledge.",
        "- `koios_pool_updates_mainnet.csv`: active parameter changes and deregistration/registration history.",
        "",
        "## Compliance proxy",
        r"- Per pool and epoch, the proxy tests $Stake^{owners}_{active} \geq Pledge_{declared}$ when owner history is observed.",
        r"- If owner history is not observed but `pool_updates` gives a pledge amount, the pledge target is still known but not the coverage ratio.",
        r"- This is a same-epoch Koios join, useful for incentive analysis but not a direct ledger-validity proof.",
        "",
        f"[Summary]({summary_path.name})",
        "",
        "## Graph 1: Pledge Compliance Proxy",
        "Top panel: share of pools meeting pledge, plus reward/stake share linked to pledge-unmet pool-epochs.",
        "Bottom panel: observed pool count and non-compliant pool count.",
        "",
        f"![Pledge compliance](../figures/{fig_pledge_path.name})",
        "",
        "## Graph 2: Active Fee Regimes and Update Pressure",
        "Top panel: median active margin and share of pools at 340 ADA fixed cost.",
        "Bottom panel: registrations, deregistrations, and other parameter updates activating by epoch.",
        "",
        f"![Fee regimes](../figures/{fig_fee_path.name})",
        "",
        "## Graph 3: Pool-Level Compliance Distribution",
        "Left panel: pool counts by compliance band across the full window.",
        "Right panel: stake scale versus pledge-met epoch share, colored by realized pool rewards.",
        "",
        f"![Pool distribution](../figures/{fig_pool_dist_path.name})",
        "",
        "## Interpretation",
        "- This dataset can now support CIP-level arguments about whether stronger skin-in-the-game rules would bind often or rarely.",
        "- It also gives a concrete baseline for talking about fee-regime changes without relying on anecdotal pool examples.",
        "",
    ]
    out_path.write_text("\n".join(lines))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "scenarii-evaluation" / "data"
    figures_dir = root / "scenarii-evaluation" / "figures"
    outputs_dir = root / "scenarii-evaluation" / "outputs"
    docs_dir = root / "scenarii-evaluation" / "docs"
    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    pool_history_path = data_dir / "koios_pool_history_mainnet.csv"
    pool_updates_path = data_dir / "koios_pool_updates_mainnet.csv"
    pool_owner_history_path = data_dir / "koios_pool_owner_history_mainnet.csv"

    owner_history_agg, owner_history_row_count = load_owner_history_agg(pool_owner_history_path)
    updates_by_pool, update_events, pool_updates_row_count = load_pool_updates(pool_updates_path)
    raw_epoch_rows, pool_rows = build_summaries(pool_history_path, updates_by_pool, owner_history_agg)

    epoch_rows = [finalize_epoch_row(row, update_events.get(row["epoch_no"])) for row in raw_epoch_rows]
    pool_rows.sort(key=lambda row: row["total_pool_rewards_ada"], reverse=True)
    update_epoch_rows = build_update_epoch_rows(epoch_rows)

    epoch_summary_path = data_dir / "pool_pledge_epoch_summary_mainnet.csv"
    pool_summary_path = data_dir / "pool_pledge_pool_summary_mainnet.csv"
    update_epoch_summary_path = data_dir / "pool_update_epoch_summary_mainnet.csv"
    fig_pledge_path = figures_dir / "pool_pledge_compliance_mainnet.png"
    fig_fee_path = figures_dir / "pool_fee_regime_state_mainnet.png"
    fig_pool_dist_path = figures_dir / "pool_pledge_pool_distribution_mainnet.png"
    summary_path = outputs_dir / "pool_pledge_and_updates_mainnet_summary.md"
    doc_path = docs_dir / "pool-pledge-and-updates-mainnet.md"

    write_csv(epoch_rows, epoch_summary_path)
    write_csv(pool_rows, pool_summary_path)
    write_csv(update_epoch_rows, update_epoch_summary_path)

    plt.style.use("seaborn-v0_8-whitegrid")
    pledge_stats = render_pledge_compliance(epoch_rows, fig_pledge_path)
    fee_stats = render_fee_regimes(epoch_rows, fig_fee_path)
    pool_dist_stats = render_pool_distribution(pool_rows, fig_pool_dist_path)
    write_summary(
        epoch_rows=epoch_rows,
        pool_rows=pool_rows,
        owner_history_row_count=owner_history_row_count,
        pool_updates_row_count=pool_updates_row_count,
        pledge_stats=pledge_stats,
        fee_stats=fee_stats,
        pool_dist_stats=pool_dist_stats,
        out_path=summary_path,
    )
    write_doc(
        summary_path=summary_path,
        fig_pledge_path=fig_pledge_path,
        fig_fee_path=fig_fee_path,
        fig_pool_dist_path=fig_pool_dist_path,
        out_path=doc_path,
    )

    print(f"Wrote: {epoch_summary_path}")
    print(f"Wrote: {pool_summary_path}")
    print(f"Wrote: {update_epoch_summary_path}")
    print(f"Wrote: {fig_pledge_path}")
    print(f"Wrote: {fig_fee_path}")
    print(f"Wrote: {fig_pool_dist_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {doc_path}")


if __name__ == "__main__":
    main()
