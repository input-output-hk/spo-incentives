#!/usr/bin/env python3
"""
Build a visual showing the pool landscape by size category.

Outputs:
  - figures/pool_landscape_by_size_mainnet.png

Two panels (IOG dark brand style):
  Top:    Horizontal bars of pool counts by size category.
  Bottom: Horizontal bars of stake share by size category.

Uses IOG brand colors and dark background (#0A0A0A) with white text.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
SNAPSHOT_PATH = REPORT_DIR / "data" / "pool_distribution_snapshot.json"

# IOG Brand Colors
DARK_BG = "#FFFFFF"
TEXT_WHITE = "#1A1A1A"
TEXT_DIM = "#666666"
GRID_COLOR = "#E0E0E0"
INFARED = "#E52321"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
COBALT_PULSE = "#2C4FFA"
ULTRAVIOLET = "#A700FF"
SOLAR_AMBER = "#FFBA36"

SIZE_CATS = [
    ("Sub-reliable (<3M)", 0, 3_000_000, INFARED),
    ("Healthy (3M–30M)", 3_000_000, 30_000_000, ACID_GREEN),
    ("Large healthy (30M–60M)", 30_000_000, 60_000_000, ELECTRIC_BLUE),
    ("Near-saturation (60M–z₀)", 60_000_000, None, COBALT_PULSE),
    ("Saturated (≥z₀)", None, None, ULTRAVIOLET),
]


def parse_float(v, default=0.0):
    if v is None:
        return default
    v = str(v).strip()
    return float(v) if v else default


def categorize(stake: float, z0: float) -> int:
    if stake < 3_000_000:
        return 0
    elif stake < 30_000_000:
        return 1
    elif stake < 60_000_000:
        return 2
    elif stake < z0:
        return 3
    else:
        return 4


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with SNAPSHOT_PATH.open() as f:
        snap = json.load(f)
    z0 = snap["z0_ada"]

    # Load pools
    pools = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("pool_status") == "registered":
                stake = parse_float(r.get("active_stake")) / 1e6
                if stake > 0:
                    pools.append(stake)

    pools.sort(reverse=True)
    total_stake = sum(pools)

    # Categorize
    cat_counts = [0] * 5
    cat_stakes = [0.0] * 5
    for s in pools:
        idx = categorize(s, z0)
        cat_counts[idx] += 1
        cat_stakes[idx] += s

    cat_pcts = [c / len(pools) * 100 for c in cat_counts]
    stake_pcts = [s / total_stake * 100 for s in cat_stakes]

    labels = [c[0] for c in SIZE_CATS]
    colors = [c[3] for c in SIZE_CATS]

    # --- Figure (IOG Dark Brand Style) ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), facecolor=DARK_BG)

    # Configure axes background
    for ax in [ax1, ax2]:
        ax.set_facecolor(DARK_BG)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(GRID_COLOR)
        ax.spines["bottom"].set_color(GRID_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=10)

    # Top: pool counts by category
    bars1 = ax1.barh(range(5), cat_counts, color=colors, edgecolor="none")
    ax1.set_yticks(range(5))
    ax1.set_yticklabels(labels, fontsize=11, color=TEXT_WHITE, fontweight="bold")
    ax1.set_xlabel("Number of pools", fontsize=11, color=TEXT_DIM, labelpad=12)
    ax1.set_title("Pool Counts by Size Category", fontsize=14, fontweight="bold", color=TEXT_WHITE, pad=20)

    # Annotations on bars (bold white text)
    for bar, cnt, pct in zip(bars1, cat_counts, cat_pcts):
        width = bar.get_width()
        x_pos = width * 0.5
        ax1.text(x_pos, bar.get_y() + bar.get_height() / 2,
                 f"{cnt:,} ({pct:.0f}%)", va="center", ha="center",
                 fontsize=11, fontweight="bold", color=TEXT_WHITE)

    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.15, axis="x", color=GRID_COLOR, linestyle="-", linewidth=0.5)
    ax1.set_axisbelow(True)

    # Bottom: stake share by category
    bars2 = ax2.barh(range(5), stake_pcts, color=colors, edgecolor="none")
    ax2.set_yticks(range(5))
    ax2.set_yticklabels(labels, fontsize=11, color=TEXT_WHITE, fontweight="bold")
    ax2.set_xlabel("Share of active stake (%)", fontsize=11, color=TEXT_DIM, labelpad=12)
    ax2.set_title("Stake Distribution by Size Category", fontsize=14, fontweight="bold", color=TEXT_WHITE, pad=20)

    # Annotations on bars (bold white text)
    for bar, pct, stake in zip(bars2, stake_pcts, cat_stakes):
        width = bar.get_width()
        x_pos = width * 0.5
        ax2.text(x_pos, bar.get_y() + bar.get_height() / 2,
                 f"{pct:.1f}% ({stake / 1e9:.2f}B)", va="center", ha="center",
                 fontsize=11, fontweight="bold", color=TEXT_WHITE)

    ax2.invert_yaxis()
    ax2.set_xlim(0, max(110, max(stake_pcts) * 1.15))
    ax2.grid(True, alpha=0.15, axis="x", color=GRID_COLOR, linestyle="-", linewidth=0.5)
    ax2.set_axisbelow(True)

    # Insight bar at bottom
    fig.text(0.05, 0.02, "73% of pools are subscale — but carry only 2.7% of stake",
             fontsize=12, fontweight="bold", color=DARK_BG,
             bbox=dict(boxstyle="round,pad=0.8", facecolor=SOLAR_AMBER, edgecolor="none"))

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    out_path = FIG_DIR / "pool_landscape_by_size_mainnet.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    main()
