#!/usr/bin/env python3
"""
Pass 2 — Delegator segmentation visuals.

Reads:
  data/delegation_size_dist_623.csv   (cross-section at epoch 623)
  data/tier_history.csv               (historical every 10 epochs)

Outputs:
  figures/delegation_concentration_623.png   (bar chart + Lorenz curve)
  figures/delegation_tiers_history.png       (stacked area: count + ADA by tier over time)
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG         = "#FFFFFF"
INK        = "#1A1A1A"
DIM        = "#666666"
GRID       = "#EBEBEB"
INFARED    = "#E52321"
GREEN      = "#00875A"
BLUE       = "#2C4FFA"
VIOLET     = "#A700FF"
AMBER      = "#FFBA36"
TEAL       = "#16E9D8"
PINK       = "#FF79FC"
DAWN       = "#EC641D"
GREY       = "#B0B0B0"
ACID_GREEN = "#06FF89"

TIER_COLOURS = {
    "01_micro":  GREY,
    "02_tiny":   TEAL,
    "03_small":  ACID_GREEN,
    "04_medium": BLUE,
    "05_large":  AMBER,
    "06_whale":  DAWN,
    "07_mega":   VIOLET,
    "08_titan":  INFARED,
}

TIER_LABELS = {
    "01_micro":  "<100",
    "02_tiny":   "100–1K",
    "03_small":  "1K–10K",
    "04_medium": "10K–100K",
    "05_large":  "100K–500K",
    "06_whale":  "500K–1M",
    "07_mega":   "1M–10M",
    "08_titan":  "10M+",
}


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load data ──
    snap = pd.read_csv(DATA_DIR / "delegation_size_dist_623.csv")
    hist = pd.read_csv(DATA_DIR / "tier_history.csv")

    # Normalise tier names: snapshot has long names (01_micro_lt100), history has short (01_micro)
    snap["tier"] = snap["tier"].str.extract(r"(\d{2}_\w+?)(?:_|$)")[0]

    total_deleg = snap["delegation_count"].sum()
    total_ada = snap["total_ada"].sum()

    # ══════════════════════════════════════════════════════════
    # Figure 1: Concentration at epoch 623
    # ══════════════════════════════════════════════════════════
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), facecolor=BG,
                              gridspec_kw={"width_ratios": [1, 1, 1]})

    # Panel A: delegation count by tier
    ax = axes[0]
    ax.set_facecolor(BG)
    tiers = snap["tier"].tolist()
    counts = snap["delegation_count"].tolist()
    colours = [TIER_COLOURS[t] for t in tiers]
    labels = [TIER_LABELS[t] for t in tiers]
    bars = ax.barh(labels, counts, color=colours, alpha=0.8, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("Number of delegations", fontsize=10, color=DIM)
    ax.set_title("Count by tier", fontsize=12, fontweight="medium", color=INK)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e3:.0f}K" if v < 1e6 else f"{v/1e6:.1f}M"))
    ax.tick_params(colors=DIM, labelsize=9)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.invert_yaxis()

    # Percentage annotations
    for bar, cnt in zip(bars, counts):
        pct = cnt / total_deleg * 100
        ax.text(bar.get_width() + total_deleg * 0.01, bar.get_y() + bar.get_height()/2,
                f"{pct:.1f}%", va="center", fontsize=8, color=DIM)

    # Panel B: ADA by tier
    ax = axes[1]
    ax.set_facecolor(BG)
    adas = snap["total_ada"].tolist()
    bars = ax.barh(labels, [a / 1e9 for a in adas], color=colours, alpha=0.8,
                    edgecolor="white", linewidth=0.5)
    ax.set_xlabel("ADA (billions)", fontsize=10, color=DIM)
    ax.set_title("Stake by tier", fontsize=12, fontweight="medium", color=INK)
    ax.tick_params(colors=DIM, labelsize=9)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.invert_yaxis()

    for bar, ada in zip(bars, adas):
        pct = ada / total_ada * 100
        ax.text(bar.get_width() + total_ada / 1e9 * 0.01, bar.get_y() + bar.get_height()/2,
                f"{pct:.1f}%", va="center", fontsize=8, color=DIM)

    # Panel C: Lorenz curve
    ax = axes[2]
    ax.set_facecolor(BG)

    # Build Lorenz from tier aggregates (approximation — actual Lorenz would need individual rows)
    # Sort tiers by size (already sorted small→large)
    cum_count = np.cumsum(counts) / total_deleg
    cum_ada = np.cumsum(adas) / total_ada
    cum_count = np.insert(cum_count, 0, 0)
    cum_ada = np.insert(cum_ada, 0, 0)

    ax.fill_between(cum_count, cum_ada, cum_count, color=INFARED, alpha=0.15, label="Inequality area")
    ax.plot(cum_count, cum_ada, color=INFARED, linewidth=2.5, marker="o", markersize=5)
    ax.plot([0, 1], [0, 1], color=DIM, linewidth=0.8, linestyle="--", label="Perfect equality")

    # Annotate key points
    # Top 0.17% (mega + titan) hold what % of ADA?
    top_count = (snap.loc[snap.tier.isin(["07_mega", "08_titan"]), "delegation_count"].sum())
    top_ada = (snap.loc[snap.tier.isin(["07_mega", "08_titan"]), "total_ada"].sum())
    top_pct_count = top_count / total_deleg * 100
    top_pct_ada = top_ada / total_ada * 100
    ax.annotate(
        f"Top {top_pct_count:.2f}% of delegations\nhold {top_pct_ada:.1f}% of stake",
        xy=(1 - top_count/total_deleg, 1 - top_ada/total_ada),
        xytext=(0.15, 0.75),
        fontsize=9, color=INFARED,
        arrowprops=dict(arrowstyle="->", color=INFARED, lw=1.0))

    # Bottom 59% (micro) hold what?
    micro_pct_count = counts[0] / total_deleg * 100
    micro_pct_ada = adas[0] / total_ada * 100
    ax.annotate(
        f"Bottom {micro_pct_count:.0f}% of delegations\nhold {micro_pct_ada:.2f}% of stake",
        xy=(counts[0]/total_deleg, adas[0]/total_ada),
        xytext=(0.45, 0.10),
        fontsize=9, color=DIM,
        arrowprops=dict(arrowstyle="->", color=DIM, lw=0.8))

    ax.set_xlabel("Cumulative share of delegations", fontsize=10, color=DIM)
    ax.set_ylabel("Cumulative share of stake", fontsize=10, color=DIM)
    ax.set_title("Lorenz curve (tier-aggregated)", fontsize=12, fontweight="medium", color=INK)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    leg = ax.legend(loc="upper left", fontsize=8, framealpha=0.9, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    fig.suptitle("Delegation Stake Concentration — Epoch 623",
                 fontsize=14, fontweight="medium", color=INK, y=1.02)
    fig.tight_layout()
    out1 = FIG_DIR / "delegation_concentration_623.png"
    fig.savefig(out1, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out1}")

    # ══════════════════════════════════════════════════════════
    # Figure 2: Historical tier evolution (stacked areas)
    # ══════════════════════════════════════════════════════════
    pivot_count = hist.pivot_table(index="epoch_no", columns="tier", values="cnt", fill_value=0)
    pivot_ada = hist.pivot_table(index="epoch_no", columns="tier", values="total_ada", fill_value=0)

    tier_order = list(TIER_COLOURS.keys())
    # Ensure columns in order
    pivot_count = pivot_count.reindex(columns=tier_order, fill_value=0)
    pivot_ada = pivot_ada.reindex(columns=tier_order, fill_value=0)

    epochs = pivot_count.index.values

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), facecolor=BG, sharex=True)

    # Top: delegation count by tier (stacked)
    ax1.set_facecolor(BG)
    arrays = [pivot_count[t].values for t in tier_order]
    ax1.stackplot(epochs, *arrays,
                  colors=[TIER_COLOURS[t] for t in tier_order],
                  labels=[TIER_LABELS[t] for t in tier_order],
                  alpha=0.75)
    ax1.set_ylabel("Delegation count", fontsize=11, color=DIM)
    ax1.set_title("Delegation Count by Stake Tier", fontsize=13, fontweight="medium", color=INK)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"))
    ax1.grid(axis="y", color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax1.spines[sp].set_visible(False)
    ax1.spines["left"].set_color(GRID)
    ax1.tick_params(colors=DIM, labelsize=9)
    # Legend in reverse order (titan on top)
    handles, labels_leg = ax1.get_legend_handles_labels()
    leg = ax1.legend(handles[::-1], labels_leg[::-1], loc="upper left", fontsize=8,
                      framealpha=0.95, edgecolor=GRID, ncol=2)
    leg.get_frame().set_linewidth(0.5)

    # Bottom: ADA share by tier (stacked, normalised to 100%)
    ax2.set_facecolor(BG)
    totals = pivot_ada.sum(axis=1).values
    arrays_pct = [(pivot_ada[t].values / totals * 100) for t in tier_order]
    ax2.stackplot(epochs, *arrays_pct,
                  colors=[TIER_COLOURS[t] for t in tier_order],
                  alpha=0.75)
    ax2.set_ylabel("Share of staked ADA (%)", fontsize=11, color=DIM)
    ax2.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax2.set_title("Stake Share by Tier (normalised)", fontsize=13, fontweight="medium", color=INK)
    ax2.set_ylim(0, 100)
    ax2.grid(axis="y", color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.spines["left"].set_color(GRID)
    ax2.spines["bottom"].set_color(GRID)
    ax2.tick_params(colors=DIM, labelsize=9)

    ax1.set_xlim(epochs[0], epochs[-1])
    fig.tight_layout()
    out2 = FIG_DIR / "delegation_tiers_history.png"
    fig.savefig(out2, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out2}")

    # ── Summary stats ──
    print(f"\n{'='*60}")
    print(f"PASS 2 — Delegation segmentation at epoch 623")
    print(f"{'='*60}")
    print(f"Total delegations:  {total_deleg:,}")
    print(f"Total staked ADA:   {total_ada/1e9:.2f}B")
    print()
    for _, row in snap.iterrows():
        t = row["tier"]
        print(f"  {TIER_LABELS[t]:>12s}: {int(row['delegation_count']):>10,} delegations ({row['delegation_count']/total_deleg*100:5.1f}%)  "
              f"| {row['total_ada']/1e9:8.2f}B ADA ({row['total_ada']/total_ada*100:5.1f}%)"
              f"  | median {row['median_ada']:,.0f} ADA")
    print()
    print(f"Concentration:")
    print(f"  Top 0.17% (mega+titan):  {top_pct_ada:.1f}% of stake")
    print(f"  Bottom 59% (micro):      {micro_pct_ada:.2f}% of stake")

    # Gini approximation from tiers
    # Using trapezoidal rule on Lorenz curve
    gini = 1 - 2 * np.trapz(cum_ada, cum_count)
    print(f"  Gini coefficient (tier-approx): {gini:.3f}")


if __name__ == "__main__":
    main()
