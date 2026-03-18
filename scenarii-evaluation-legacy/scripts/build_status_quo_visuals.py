#!/usr/bin/env python3
"""
Build strong "Status Quo" visuals for SPO incentives using the core model:
- ROI
- Skin in the Game
- Decentralization Quality

Data sources:
- spo_incentives/active_pool_details_epoch_589.csv
- spo_incentives/appendixB.csv

Notes:
- This script reuses the operator/delegator reward split logic from the reward
  calculator app (fixed fee + variable margin + owner-share of remaining
  rewards), adapted for aggregate epoch-level analysis.
"""

from __future__ import annotations

import csv
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class PoolSnapshot:
    pool_id: str
    ticker: str
    stake_ada: float
    pledge_ada: float
    owner_stake_ada: float
    fixed_cost_ada: float
    margin_rate: float


@dataclass
class PoolDerived:
    pool_id: str
    ticker: str
    stake_ada: float
    pledge_ada: float
    leverage: float
    avg_reward_epoch_ada: float
    operator_reward_epoch_ada: float
    delegator_reward_epoch_ada: float
    delegator_stake_ada: float
    delegator_roa_annual_pct: float


def read_active_snapshot(path: Path) -> Dict[str, PoolSnapshot]:
    pools: Dict[str, PoolSnapshot] = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["poolId"]
            pools[pool_id] = PoolSnapshot(
                pool_id=pool_id,
                ticker=row["ticker"],
                stake_ada=float(row["epoch_stake_ada"]),
                pledge_ada=float(row["pledge_ada"]),
                owner_stake_ada=float(row["owner_stake_ada"]),
                fixed_cost_ada=float(row["fixed_cost_ada"]),
                margin_rate=float(row["margin_percent"]) / 100.0,
            )
    return pools


def read_reward_totals(path: Path) -> Tuple[Dict[str, float], int]:
    rewards_ada: Dict[str, float] = defaultdict(float)
    epochs = set()

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id"]
            epochs.add(int(row["epoch_no"]))
            rewards_ada[pool_id] += float(row["rewards_earned_in_epoch"]) / 1_000_000.0

    return rewards_ada, len(epochs)


def derive_status_quo_rows(
    pools: Dict[str, PoolSnapshot],
    rewards_ada: Dict[str, float],
    n_epochs: int,
) -> List[PoolDerived]:
    rows: List[PoolDerived] = []

    for pool in pools.values():
        avg_reward_epoch_ada = rewards_ada.get(pool.pool_id, 0.0) / max(n_epochs, 1)

        owner_share = 0.0
        if pool.stake_ada > 0:
            owner_share = max(0.0, min(1.0, pool.owner_stake_ada / pool.stake_ada))

        # Reward split logic aligned with the calculator:
        # fixed fee first, then variable margin, then owner stake share.
        remaining_after_fixed = max(avg_reward_epoch_ada - pool.fixed_cost_ada, 0.0)
        operator_reward_epoch_ada = (
            min(avg_reward_epoch_ada, pool.fixed_cost_ada)
            + remaining_after_fixed * pool.margin_rate
            + remaining_after_fixed * (1.0 - pool.margin_rate) * owner_share
        )
        delegator_reward_epoch_ada = max(avg_reward_epoch_ada - operator_reward_epoch_ada, 0.0)
        delegator_stake_ada = max(pool.stake_ada - pool.owner_stake_ada, 1e-9)
        delegator_roa_annual_pct = (delegator_reward_epoch_ada / delegator_stake_ada) * 73.0 * 100.0

        leverage = math.inf
        if pool.pledge_ada > 0:
            leverage = pool.stake_ada / pool.pledge_ada

        rows.append(
            PoolDerived(
                pool_id=pool.pool_id,
                ticker=pool.ticker,
                stake_ada=pool.stake_ada,
                pledge_ada=pool.pledge_ada,
                leverage=leverage,
                avg_reward_epoch_ada=avg_reward_epoch_ada,
                operator_reward_epoch_ada=operator_reward_epoch_ada,
                delegator_reward_epoch_ada=delegator_reward_epoch_ada,
                delegator_stake_ada=delegator_stake_ada,
                delegator_roa_annual_pct=delegator_roa_annual_pct,
            )
        )

    return rows


def compute_concentration(stakes: np.ndarray, top_n: int) -> float:
    if stakes.size == 0:
        return 0.0
    total = float(np.sum(stakes))
    if total <= 0:
        return 0.0
    sorted_stakes = np.sort(stakes)[::-1]
    return float(np.sum(sorted_stakes[:top_n]) / total)


def compute_hhi(stakes: np.ndarray) -> float:
    total = float(np.sum(stakes))
    if total <= 0:
        return 0.0
    shares = stakes / total
    return float(np.sum(shares * shares))


def render_roi_viability(rows: List[PoolDerived], out_path: Path) -> None:
    stakes = np.array([r.stake_ada for r in rows if r.stake_ada > 0])
    op_reward = np.array([r.operator_reward_epoch_ada for r in rows if r.stake_ada > 0])

    profitable_250 = op_reward >= 250.0
    profitable_156 = op_reward >= 156.0
    under_3m = stakes < 3_000_000

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.scatter(
        stakes[~profitable_250],
        op_reward[~profitable_250],
        s=16,
        alpha=0.55,
        color="#d62728",
        label="Below 250 ADA/epoch",
    )
    ax.scatter(
        stakes[profitable_250],
        op_reward[profitable_250],
        s=16,
        alpha=0.55,
        color="#2ca02c",
        label="At/above 250 ADA/epoch",
    )

    ax.axhline(156, color="#ff7f0e", linestyle="--", linewidth=1.6, label="156 ADA baseline")
    ax.axhline(250, color="#8c564b", linestyle="--", linewidth=1.6, label="250 ADA baseline")
    ax.axvline(3_000_000, color="#1f77b4", linestyle="--", linewidth=1.6, label="3M ADA line")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Pool Stake (ADA, log scale)")
    ax.set_ylabel("Estimated Operator Reward per Epoch (ADA, log scale)")
    ax.set_title("Status Quo ROI Pressure: Operator Viability vs Pool Stake")
    ax.grid(alpha=0.2, which="both")
    ax.legend(loc="lower right")

    n = stakes.size
    text = (
        f"Pools below 250 ADA: {np.sum(~profitable_250):,}/{n:,} "
        f"({np.mean(~profitable_250)*100:.1f}%)\n"
        f"Pools below 156 ADA: {np.sum(~profitable_156):,}/{n:,} "
        f"({np.mean(~profitable_156)*100:.1f}%)\n"
        f"Pools below 3M stake: {np.sum(under_3m):,}/{n:,} "
        f"({np.mean(under_3m)*100:.1f}%)"
    )
    ax.text(
        0.02,
        0.98,
        text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def render_roi_fairness(rows: List[PoolDerived], out_path: Path) -> None:
    buckets = [
        ("<1M", 0, 1_000_000),
        ("1M-3M", 1_000_000, 3_000_000),
        ("3M-10M", 3_000_000, 10_000_000),
        ("10M-30M", 10_000_000, 30_000_000),
        ("30M-70M", 30_000_000, 70_000_000),
        (">70M", 70_000_000, math.inf),
    ]

    grouped: List[np.ndarray] = []
    labels: List[str] = []
    medians: List[float] = []
    counts: List[int] = []

    for label, lo, hi in buckets:
        vals = [
            r.delegator_roa_annual_pct
            for r in rows
            if r.stake_ada >= lo and r.stake_ada < hi and r.delegator_stake_ada > 0
        ]
        arr = np.array(vals, dtype=float)
        if arr.size == 0:
            arr = np.array([0.0])
        grouped.append(arr)
        labels.append(label)
        medians.append(float(np.median(arr)))
        counts.append(int(arr.size))

    fig, ax = plt.subplots(figsize=(12, 8))
    bp = ax.boxplot(grouped, tick_labels=labels, showfliers=False, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set(facecolor="#9ecae1", alpha=0.75)
    ax.plot(range(1, len(medians) + 1), medians, color="#08306b", marker="o", linewidth=1.8, label="Median")

    ax.set_ylabel("Delegator Annualized ROA (%)")
    ax.set_xlabel("Pool Stake Bucket")
    ax.set_title("Status Quo ROI Fairness: Delegator ROA by Pool Size")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper right")

    for i, n in enumerate(counts, start=1):
        ax.text(i, ax.get_ylim()[0], f"n={n}", ha="center", va="bottom", fontsize=9, color="#555555")

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def render_skin_in_game(rows: List[PoolDerived], out_path: Path) -> None:
    non_zero_pledge = [r for r in rows if r.pledge_ada > 0 and r.stake_ada > 0]
    zero_pledge = [r for r in rows if r.pledge_ada <= 0 and r.stake_ada > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    # Left: pledge vs stake with leverage guide-lines.
    x = np.array([r.pledge_ada for r in non_zero_pledge], dtype=float)
    y = np.array([r.stake_ada for r in non_zero_pledge], dtype=float)
    ax1.scatter(x, y, s=14, alpha=0.45, color="#1f77b4", label="Pools with non-zero pledge")

    xs = np.logspace(0, 8, 200)
    for lev, color in [(10, "#2ca02c"), (100, "#ff7f0e"), (1000, "#d62728"), (10000, "#9467bd")]:
        ax1.plot(xs, xs * lev, linestyle="--", linewidth=1.4, color=color, label=f"{lev:,}x leverage")

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("Pledge (ADA, log scale)")
    ax1.set_ylabel("Pool Stake (ADA, log scale)")
    ax1.set_title("Skin in the Game: Stake vs Pledge")
    ax1.grid(alpha=0.2, which="both")
    ax1.legend(loc="lower right", fontsize=9)

    # Right: stake share by leverage band.
    total_stake = sum(max(r.stake_ada, 0.0) for r in rows)
    bands = [
        ("Zero pledge", lambda r: math.isinf(r.leverage)),
        (">10,000x", lambda r: (not math.isinf(r.leverage)) and r.leverage > 10_000),
        ("1,000x-10,000x", lambda r: (not math.isinf(r.leverage)) and 1_000 < r.leverage <= 10_000),
        ("100x-1,000x", lambda r: (not math.isinf(r.leverage)) and 100 < r.leverage <= 1_000),
        ("10x-100x", lambda r: (not math.isinf(r.leverage)) and 10 < r.leverage <= 100),
        ("<=10x", lambda r: (not math.isinf(r.leverage)) and r.leverage <= 10),
    ]
    stake_shares = []
    pool_counts = []
    labels = []
    for label, fn in bands:
        stake = sum(r.stake_ada for r in rows if fn(r))
        count = sum(1 for r in rows if fn(r))
        stake_shares.append((stake / total_stake * 100.0) if total_stake > 0 else 0.0)
        pool_counts.append(count)
        labels.append(label)

    y_pos = np.arange(len(labels))
    colors = ["#b2182b", "#d6604d", "#f4a582", "#92c5de", "#4393c3", "#2166ac"]
    ax2.barh(y_pos, stake_shares, color=colors, alpha=0.9)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels)
    ax2.invert_yaxis()
    ax2.set_xlabel("Share of Total Stake (%)")
    ax2.set_title("Skin in the Game: Stake Concentration by Leverage Band")
    ax2.grid(axis="x", alpha=0.2)

    for i, (share, cnt) in enumerate(zip(stake_shares, pool_counts)):
        ax2.text(share + 0.3, i, f"{share:.1f}% ({cnt} pools)", va="center", fontsize=9)

    note = f"Zero-pledge pools: {len(zero_pledge)} / {len(rows)}"
    ax2.text(
        0.02,
        0.02,
        note,
        transform=ax2.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def render_decentralization_quality(rows: List[PoolDerived], out_path: Path) -> None:
    stakes = np.array([max(r.stake_ada, 0.0) for r in rows if r.stake_ada > 0], dtype=float)
    total = float(np.sum(stakes)) if stakes.size else 0.0
    sorted_stakes = np.sort(stakes)[::-1]
    cum_share = np.cumsum(sorted_stakes) / total if total > 0 else np.array([])

    # Bucket comparison: pool share vs stake share.
    buckets = [
        ("<3M", 0, 3_000_000),
        ("3M-10M", 3_000_000, 10_000_000),
        ("10M-30M", 10_000_000, 30_000_000),
        ("30M-70M", 30_000_000, 70_000_000),
        (">70M", 70_000_000, math.inf),
    ]
    pool_share = []
    stake_share = []
    labels = []
    for label, lo, hi in buckets:
        pool_subset = [r for r in rows if r.stake_ada >= lo and r.stake_ada < hi]
        subset_stake = sum(r.stake_ada for r in pool_subset)
        pool_share.append((len(pool_subset) / len(rows)) * 100.0 if rows else 0.0)
        stake_share.append((subset_stake / total) * 100.0 if total > 0 else 0.0)
        labels.append(label)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    x = np.arange(len(labels))
    width = 0.38
    ax1.bar(x - width / 2, pool_share, width=width, label="Pool share (%)", color="#6baed6")
    ax1.bar(x + width / 2, stake_share, width=width, label="Stake share (%)", color="#08519c")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Share (%)")
    ax1.set_title("Decentralization Quality: Pool Count vs Stake Control")
    ax1.grid(axis="y", alpha=0.2)
    ax1.legend()

    ranks = np.arange(1, len(sorted_stakes) + 1)
    ax2.plot(ranks, cum_share * 100.0, color="#d62728", linewidth=2.0)
    for n in [10, 50, 100, 500]:
        if n <= len(cum_share):
            share = cum_share[n - 1] * 100.0
            ax2.scatter([n], [share], color="#111111", s=24)
            ax2.text(n, share + 1.2, f"Top {n}: {share:.1f}%", fontsize=9)

    hhi = compute_hhi(stakes)
    ax2.set_xscale("log")
    ax2.set_xlabel("Top N Pools (log scale)")
    ax2.set_ylabel("Cumulative Stake Share (%)")
    ax2.set_title("Decentralization Quality: Stake Concentration Curve")
    ax2.grid(alpha=0.2, which="both")
    ax2.text(
        0.02,
        0.98,
        f"HHI (pool-level): {hhi:.4f}",
        transform=ax2.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def write_summary(rows: List[PoolDerived], n_epochs: int, out_path: Path) -> None:
    stakes = np.array([r.stake_ada for r in rows if r.stake_ada > 0], dtype=float)
    operator_rewards = np.array([r.operator_reward_epoch_ada for r in rows if r.stake_ada > 0], dtype=float)
    total_stake = float(np.sum(stakes)) if stakes.size else 0.0

    below_250 = int(np.sum(operator_rewards < 250.0))
    below_156 = int(np.sum(operator_rewards < 156.0))
    lt_3m = int(np.sum(stakes < 3_000_000))
    zero_pledge = [r for r in rows if r.pledge_ada <= 0 and r.stake_ada > 0]
    zero_pledge_stake = float(np.sum([r.stake_ada for r in zero_pledge]))

    top10 = compute_concentration(stakes, 10) * 100.0
    top50 = compute_concentration(stakes, 50) * 100.0
    top100 = compute_concentration(stakes, 100) * 100.0
    hhi = compute_hhi(stakes)

    md = [
        "# Status Quo Summary (Core Model)",
        "",
        f"- Data window: {n_epochs} epochs from `appendixB.csv` (average per epoch), joined with active pool snapshot epoch 589.",
        f"- Pools analyzed: {len(rows):,}",
        "",
        "## ROI",
        f"- Pools below 250 ADA/epoch operator revenue: **{below_250:,} / {len(rows):,}** ({below_250/len(rows)*100:.1f}%)",
        f"- Pools below 156 ADA/epoch operator revenue: **{below_156:,} / {len(rows):,}** ({below_156/len(rows)*100:.1f}%)",
        f"- Pools below 3M ADA stake: **{lt_3m:,} / {len(rows):,}** ({lt_3m/len(rows)*100:.1f}%)",
        "",
        "## Skin in the Game",
        f"- Zero-pledge pools: **{len(zero_pledge):,}**",
        f"- Stake controlled by zero-pledge pools: **{(zero_pledge_stake/total_stake*100.0 if total_stake else 0.0):.1f}%**",
        "",
        "## Decentralization Quality (pool-level)",
        f"- Top 10 pools stake share: **{top10:.1f}%**",
        f"- Top 50 pools stake share: **{top50:.1f}%**",
        f"- Top 100 pools stake share: **{top100:.1f}%**",
        f"- HHI (pool-level): **{hhi:.4f}**",
        "",
        "## Generated figures",
        "- `status_quo_roi_viability.png`",
        "- `status_quo_roi_fairness.png`",
        "- `status_quo_skin_in_the_game.png`",
        "- `status_quo_decentralization_quality.png`",
        "",
        "_Note:_ This is a pool-level baseline. Entity-level concentration requires ownership clustering data not present in these two CSV files.",
        "",
    ]

    out_path.write_text("\n".join(md))


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "spo_incentives"
    figures_dir = repo_root / "scenarii-evaluation" / "figures"
    outputs_dir = repo_root / "scenarii-evaluation" / "outputs"
    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    active_path = src_dir / "active_pool_details_epoch_589.csv"
    appendix_b_path = src_dir / "appendixB.csv"

    pools = read_active_snapshot(active_path)
    rewards_ada, n_epochs = read_reward_totals(appendix_b_path)
    rows = derive_status_quo_rows(pools, rewards_ada, n_epochs)

    render_roi_viability(rows, figures_dir / "status_quo_roi_viability.png")
    render_roi_fairness(rows, figures_dir / "status_quo_roi_fairness.png")
    render_skin_in_game(rows, figures_dir / "status_quo_skin_in_the_game.png")
    render_decentralization_quality(rows, figures_dir / "status_quo_decentralization_quality.png")
    write_summary(rows, n_epochs, outputs_dir / "status_quo_summary.md")

    print("Generated:")
    print(f"- {figures_dir / 'status_quo_roi_viability.png'}")
    print(f"- {figures_dir / 'status_quo_roi_fairness.png'}")
    print(f"- {figures_dir / 'status_quo_skin_in_the_game.png'}")
    print(f"- {figures_dir / 'status_quo_decentralization_quality.png'}")
    print(f"- {outputs_dir / 'status_quo_summary.md'}")


if __name__ == "__main__":
    main()
