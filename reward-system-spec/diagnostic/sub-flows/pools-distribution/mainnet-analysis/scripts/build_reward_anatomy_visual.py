#!/usr/bin/env python3
"""
Visualise the reward formula anatomy: waterfall decomposition + per-pool envelope distribution.

Panel 1 (left): Waterfall chart showing how the pools pot decomposes into
                 distributed rewards vs waste by formula factor.
Panel 2 (right): Distribution of per-pool envelope E(π,ν) for pools with stake,
                 showing how far most pools are from the P_max ceiling.

Outputs: figures/reward_anatomy_mainnet.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"

# IOG Dark Brand Colors
BG_COLOR = "#FFFFFF"
TEXT_WHITE = "#1A1A1A"
TEXT_DIM = "#666666"
GRID_COLOR = "#E0E0E0"
INFARED = "#E52321"
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
ULTRAVIOLET = "#A700FF"
VOLT_YELLOW = "#F2FF58"
SOLAR_AMBER = "#FFBA36"


def load_anatomy():
    with (DATA_DIR / "reward_anatomy.json").open() as f:
        return json.load(f)


def load_pool_envelopes():
    """Load per-pool E values from the detail CSV."""
    pools = []
    with (DATA_DIR / "pool_envelope_detail.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            pools.append({
                "E": float(r["E"]),
                "base": float(r["base"]),
                "bonus": float(r["bonus"]),
                "nu": float(r["nu"]),
                "stake": float(r["stake_ada"]),
            })
    return pools


def load_all_pools():
    """Load all pools with stake for the full envelope distribution."""
    anatomy = load_anatomy()
    z0 = anatomy["z0_ada"]
    a0 = anatomy["a0"]
    lam_min = 1.0 / (1.0 + a0)
    lam_max = a0 / (1.0 + a0)

    pools = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status", "") != "registered":
                continue
            stake_str = r.get("active_stake", "").strip()
            pledge_str = r.get("pledge", "").strip()
            if not stake_str:
                continue
            stake = float(stake_str) / 1e6
            if stake <= 0:
                continue
            pledge = float(pledge_str) / 1e6 if pledge_str else 0

            nu = min(stake / z0, 1.0)
            pi = min(pledge / z0, nu)
            A = pi * nu - pi**2 * (1 - nu)
            base = lam_min * nu
            bonus = lam_max * A
            E = base + bonus
            pools.append({
                "E": E,
                "base": base,
                "bonus": bonus,
                "nu": nu,
                "stake": stake,
            })
    return pools, anatomy


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pools, anatomy = load_all_pools()

    R = anatomy["R_pools_pot_ada"]
    k = anatomy["k"]
    lam_min = anatomy["lambda_min"]
    lam_max = anatomy["lambda_max"]
    dist = anatomy["distributed_ada"]

    base_captured = anatomy["sum_base_over_k_pct"]
    bonus_captured = anatomy["sum_bonus_over_k_pct"]
    perf_waste = anatomy["performance_waste_pct"]
    base_waste = lam_min * 100 - base_captured
    bonus_waste = lam_max * 100 - bonus_captured
    distributed_pct = dist / R * 100
    reserve_pct = 100.0 - distributed_pct

    # Calculate key insight: reserve percentage
    reserve_insight = f"{reserve_pct:.0f}% of the pot returns to reserve"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5))
    fig.patch.set_facecolor(BG_COLOR)

    # ── Waterfall title with insight ──
    fig.text(0.255, 0.97, "Reward Pot Decomposition",
             fontsize=13, fontweight="bold", color=TEXT_WHITE, ha="center")

    # ── Panel 1: Waterfall ──
    positions = range(5)
    colors_bars = []
    bottoms = []
    heights = []

    running = 100.0

    # Bar 0: full pot
    bottoms.append(0)
    heights.append(100.0)
    colors_bars.append(GRID_COLOR)

    # Bar 1: base waste (falls from 100)
    bottoms.append(running - base_waste)
    heights.append(base_waste)
    colors_bars.append(INFARED)
    running -= base_waste

    # Bar 2: bonus waste
    bottoms.append(running - bonus_waste)
    heights.append(bonus_waste)
    colors_bars.append(DAWN)
    running -= bonus_waste

    # Bar 3: perf waste
    bottoms.append(running - perf_waste)
    heights.append(perf_waste)
    colors_bars.append(VOLT_YELLOW)
    running -= perf_waste

    # Bar 4: distributed (from 0 up)
    bottoms.append(0)
    heights.append(running)
    colors_bars.append(ACID_GREEN)

    labels = [
        "Pools Pot\n(100%)",
        f"Base\nShortfall\n−{base_waste:.1f}%",
        f"Bonus\nShortfall\n−{bonus_waste:.1f}%",
        f"Performance\nLoss\n−{perf_waste:.1f}%",
        f"Distributed\n{distributed_pct:.1f}%",
    ]

    bars = ax1.bar(positions, heights, bottom=bottoms, color=colors_bars,
                   edgecolor=TEXT_WHITE, linewidth=1.2, width=0.65)

    # Connect lines between bars (dashed, dim)
    for i in range(3):
        level = bottoms[i + 1] + heights[i + 1]
        ax1.plot([i + 0.35, i + 0.65], [level, level], color=TEXT_DIM,
                 linewidth=0.8, linestyle="--", alpha=0.6)

    # Add ADA amounts as white bold annotations
    amounts = [
        f"{R/1e6:.1f}M ADA",
        f"−{base_waste/100*R/1e6:.1f}M ADA",
        f"−{bonus_waste/100*R/1e6:.1f}M ADA",
        f"−{perf_waste/100*R/1e3:.0f}K ADA",
        f"{dist/1e6:.1f}M ADA",
    ]
    for i, (b, h, amt) in enumerate(zip(bottoms, heights, amounts)):
        y_pos = b + h / 2
        text_color = TEXT_WHITE
        ax1.text(i, y_pos, amt, ha="center", va="center",
                 fontsize=9, fontweight="bold", color=text_color)

    # Style Panel 1
    ax1.set_xticks(positions)
    ax1.set_xticklabels(labels, fontsize=9, color=TEXT_WHITE)
    ax1.set_ylabel("% of Pools Pot", fontsize=10, color=TEXT_WHITE)
    ax1.set_ylim(0, 110)
    ax1.set_xlim(-0.6, 4.6)

    # Dark theme
    ax1.set_facecolor(BG_COLOR)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color(GRID_COLOR)
    ax1.spines["bottom"].set_color(GRID_COLOR)
    ax1.tick_params(colors=TEXT_WHITE, labelsize=9)
    ax1.grid(axis="y", color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)
    ax1.set_axisbelow(True)

    # ── Panel 2: Envelope distribution ──
    pools_sorted = sorted(pools, key=lambda p: p["stake"], reverse=True)
    x_rank = np.arange(len(pools_sorted))
    base_sorted = np.array([p["base"] * 100 for p in pools_sorted])
    E_sorted = np.array([p["E"] * 100 for p in pools_sorted])

    # Fill between for envelope components
    ax2.fill_between(x_rank, 0, base_sorted, alpha=0.7, color=ELECTRIC_BLUE, label="Base (stake only)")
    ax2.fill_between(x_rank, base_sorted, E_sorted, alpha=0.7, color=ULTRAVIOLET, label="Bonus (pledge)")

    # Ceilings: dashed for P_max, dotted for zero-pledge
    ax2.axhline(y=100, color=INFARED, linewidth=1.8, linestyle="--", label="P_max ceiling", alpha=0.8)
    ax2.axhline(y=lam_min * 100, color=DAWN, linewidth=1.2, linestyle=":", label=f"Zero-pledge ceiling ({lam_min*100:.1f}%)", alpha=0.8)

    # Production threshold (3M)
    viability_idx = sum(1 for p in pools_sorted if p["stake"] >= 3e6)
    if viability_idx > 0 and viability_idx < len(pools_sorted):
        ax2.axvline(x=viability_idx, color=TEXT_DIM, linewidth=0.8, linestyle="--", alpha=0.4)
        ax2.text(viability_idx + 30, 85, f"Healthy tier floor\n(~{viability_idx} pools)",
                 fontsize=8, color=TEXT_DIM, va="top", style="italic")

    # Style Panel 2
    ax2.set_xlabel("Pool rank (by stake, descending)", fontsize=10, color=TEXT_WHITE)
    ax2.set_ylabel("Envelope E(ν,π) — % of P_max", fontsize=10, color=TEXT_WHITE)
    ax2.set_xlim(0, min(len(pools_sorted), 1500))
    ax2.set_ylim(0, 110)

    # Dark theme
    ax2.set_facecolor(BG_COLOR)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color(GRID_COLOR)
    ax2.spines["bottom"].set_color(GRID_COLOR)
    ax2.tick_params(colors=TEXT_WHITE, labelsize=9)
    ax2.grid(axis="y", color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)
    ax2.set_axisbelow(True)

    # Legend
    legend = ax2.legend(fontsize=8.5, loc="upper right", framealpha=0.95, fancybox=False, edgecolor=GRID_COLOR)
    legend.get_frame().set_facecolor(BG_COLOR)
    for text in legend.get_texts():
        text.set_color(TEXT_WHITE)

    # ── Insight bar at bottom ──
    fig.text(0.5, 0.02, reserve_insight,
             fontsize=11, fontweight="bold", color=BG_COLOR, ha="center",
             bbox=dict(boxstyle="round,pad=0.6", facecolor=SOLAR_AMBER, edgecolor="none", alpha=0.9))

    plt.tight_layout(rect=[0, 0.06, 1, 0.96])
    out = FIG_DIR / "reward_anatomy_mainnet.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
