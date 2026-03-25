#!/usr/bin/env python3
"""
Pledge-bonus activation visual — redesigned for clarity.

Panel 1 (left):  "The cliff" — every healthy pool sorted by bonus descending.
                 Shows the binary nature: a long flat floor at ~0% then a
                 sudden spike for ~40 high-pledge pools.
Panel 2 (right): Pledge band distribution — how many pools sit in each band.

Outputs: figures/pledge_bonus_activation_mainnet.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
SNAPSHOT_PATH = DATA_DIR / "pool_distribution_snapshot.json"

# IOG Dark Brand
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#666666"
GRID_COLOR = "#E0E0E0"

INFARED = "#E52321"
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
ULTRAVIOLET = "#A700FF"
VOLT_YELLOW = "#F2FF58"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"


def parse_float(v, default=0.0):
    if v is None:
        return default
    v = str(v).strip()
    return float(v) if v else default


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with SNAPSHOT_PATH.open() as f:
        snap = json.load(f)
    z0 = snap["z0_ada"]
    a0 = snap["a0"]
    lam_min = 1.0 / (1.0 + a0)
    lam_max = a0 / (1.0 + a0)

    # Load pools
    pools = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status") != "registered":
                continue
            stake = parse_float(r.get("active_stake")) / 1e6
            pledge = parse_float(r.get("pledge")) / 1e6
            if stake <= 0:
                continue
            pools.append((pledge, stake))

    viability = 3_000_000
    healthy = [(pl, st) for pl, st in pools if st >= viability]

    # Compute actual bonus for each healthy pool
    pool_data = []
    for pl, st in healthy:
        nu = min(st / z0, 1.0)
        pi = min(pl / z0, 1.0)
        base = lam_min * nu
        if base > 0:
            A = pi * nu - pi**2 * (1.0 - nu)
            bonus_pct = lam_max * A / base * 100.0
        else:
            bonus_pct = 0.0
        pool_data.append({
            "pledge": pl,
            "stake": st,
            "bonus_pct": bonus_pct,
            "nu": nu,
        })

    # Sort by bonus descending
    pool_data.sort(key=lambda p: p["bonus_pct"], reverse=True)
    n = len(pool_data)
    bonuses = [p["bonus_pct"] for p in pool_data]

    # Stats
    gt_1pct = sum(1 for b in bonuses if b > 1.0)
    gt_5pct = sum(1 for b in bonuses if b > 5.0)
    median_bonus = sorted(bonuses)[n // 2]

    # All pool pledges for histogram
    all_pledges = [pl for pl, st in pools]

    # ── Figure ──
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                    gridspec_kw={"width_ratios": [1.4, 1]})
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

    fig.suptitle("The a₀ Curve Is a Step Function",
                 fontsize=17, fontweight="bold", color=TEXT_COLOR, y=0.97)
    fig.text(0.5, 0.92, f"Pledge bonus across {n} healthy pools  |  "
             f"Median bonus: {median_bonus:.3f}%  |  "
             f"Only {gt_1pct} pools ({gt_1pct/n*100:.0f}%) above 1%",
             ha="center", fontsize=10.5, color=TEXT_DIM)

    # ══════════════════════════════════════════════════════════════════
    # Panel 1: "The cliff" — every healthy pool sorted by bonus
    # ══════════════════════════════════════════════════════════════════

    x = np.arange(n)

    # Color each bar: green if bonus < 1%, amber if 1-10%, red if > 10%
    colors = []
    for b in bonuses:
        if b >= 10:
            colors.append(INFARED)
        elif b >= 1:
            colors.append(SOLAR_AMBER)
        else:
            colors.append(ACID_GREEN)

    ax1.bar(x, bonuses, width=1.0, color=colors, edgecolor="none", alpha=0.85)

    # Reference lines
    ax1.axhline(y=1.0, color=SOLAR_AMBER, linewidth=1.2, linestyle="--", alpha=0.6)
    ax1.text(n * 0.65, 1.3, "1% bonus threshold", fontsize=9, color=SOLAR_AMBER, alpha=0.8)

    ax1.axhline(y=30.0, color=INFARED, linewidth=1, linestyle=":", alpha=0.4)
    ax1.text(n * 0.65, 30.5, "Theoretical max (30%)", fontsize=9, color=INFARED, alpha=0.6)

    # Annotate the cliff
    ax1.annotate(
        f"{gt_1pct} pools above 1%\n({gt_1pct/n*100:.0f}% of healthy pools)",
        xy=(gt_1pct / 2, bonuses[gt_1pct - 1] if gt_1pct > 0 else 0),
        xytext=(n * 0.35, 22),
        fontsize=10, color="#B8860B", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#B8860B", alpha=0.6,
                       connectionstyle="arc3,rad=-0.2"),
        bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#B8860B", alpha=0.9))

    # Annotate the floor
    ax1.annotate(
        f"{n - gt_1pct} pools below 1%\nMedian: {median_bonus:.3f}%",
        xy=(n * 0.7, 0.2),
        xytext=(n * 0.55, 12),
        fontsize=10, color=ACID_GREEN,
        arrowprops=dict(arrowstyle="->", color=ACID_GREEN, alpha=0.5,
                       connectionstyle="arc3,rad=0.2"),
        bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec=ACID_GREEN, alpha=0.9))

    ax1.set_xlabel("Healthy pools (sorted by bonus, descending)", fontsize=10, color=TEXT_DIM)
    ax1.set_ylabel("Pledge bonus over base reward (%)", fontsize=10, color=TEXT_DIM)
    ax1.set_xlim(0, n)
    ax1.set_ylim(0, 35)
    ax1.set_title("Every healthy pool's actual bonus", fontsize=12,
                   color=TEXT_COLOR, pad=10)
    ax1.grid(axis="y", color=GRID_COLOR, alpha=0.2, linewidth=0.5)

    # ══════════════════════════════════════════════════════════════════
    # Panel 2: Pledge band distribution
    # ══════════════════════════════════════════════════════════════════

    bins = [0, 1e-6, 10_000, 100_000, 1_000_000, 10_000_000, z0 * 1.01]
    bin_labels = ["Zero", "<10K", "10K–\n100K", "100K–\n1M", "1M–\n10M", "≥10M"]
    counts = []
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]
        if i == 0:
            cnt = sum(1 for p in all_pledges if p == 0)
        elif i == len(bins) - 2:
            cnt = sum(1 for p in all_pledges if p >= lo and p > 0)
        else:
            cnt = sum(1 for p in all_pledges if lo <= p < hi and p > 0)
        counts.append(cnt)

    bar_colors = [INFARED, DAWN, SOLAR_AMBER, ELECTRIC_BLUE, COBALT_PULSE, ULTRAVIOLET]
    bars = ax2.barh(range(len(counts)), counts, color=bar_colors,
                    edgecolor=BG_COLOR, linewidth=1)

    ax2.set_yticks(range(len(counts)))
    ax2.set_yticklabels(bin_labels, fontsize=10, color=TEXT_COLOR)
    ax2.set_xlabel("Number of pools", fontsize=10, color=TEXT_DIM)
    ax2.set_title("Pledge distribution (all pools with stake)", fontsize=12,
                   color=TEXT_COLOR, pad=10)
    ax2.invert_yaxis()

    # Label with counts
    total = len(all_pledges)
    for bar, cnt in zip(bars, counts):
        pct = cnt / total * 100 if total > 0 else 0
        ax2.text(bar.get_width() + 15, bar.get_y() + bar.get_height() / 2,
                 f"{cnt:,}  ({pct:.0f}%)",
                 ha="left", va="center", fontsize=10, fontweight="bold",
                 color=TEXT_COLOR)

    ax2.set_xlim(0, max(counts) * 1.35)
    ax2.grid(axis="x", color=GRID_COLOR, alpha=0.2, linewidth=0.5)

    # Highlight the "zero bonus zone"
    # Draw a bracket showing 83% below 100K
    below_100k = counts[0] + counts[1] + counts[2]
    below_100k_pct = below_100k / total * 100
    ax2.annotate(
        f"← {below_100k_pct:.0f}% below 100K\n   (zero bonus zone)",
        xy=(counts[2] * 0.5, 2.5),
        xytext=(max(counts) * 0.5, 3.8),
        fontsize=9.5, color=SOLAR_AMBER, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=SOLAR_AMBER, alpha=0.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=SOLAR_AMBER, alpha=0.9))

    # ── Insight bar ──
    fig.text(0.5, 0.02,
             "The protocol reserves 23% of the pot for pledge incentives — "
             "but 95% of pools operate as if a₀ = 0",
             ha="center", fontsize=10.5, fontweight="bold", color=BG_COLOR,
             bbox=dict(boxstyle="round,pad=0.5", fc=SOLAR_AMBER, ec="none", alpha=0.9))

    plt.tight_layout(rect=[0, 0.06, 1, 0.88])
    out = FIG_DIR / "pledge_bonus_activation_mainnet.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
