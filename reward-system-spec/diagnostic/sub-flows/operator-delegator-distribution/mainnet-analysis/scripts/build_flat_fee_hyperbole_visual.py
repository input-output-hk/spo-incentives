#!/usr/bin/env python3
"""
The Regressive Geometry of Flat Fees — visual.

Shows how a fixed flat fee (170 or 340 ADA) consumes a disproportionate share
of pool reward for small pools, creating a structural barrier to entry.

Two theoretical hyperbolas (c / (stake × yield)) at the current and former
minPoolCost floor, overlaid with actual pool scatter data from epoch 623.

Output: figures/flat_fee_hyperbole.png
"""

from __future__ import annotations
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
BG             = "#FFFFFF"
INK            = "#1A1A1A"
DIM            = "#666666"
GRID           = "#EBEBEB"
INFARED        = "#E52321"
DAWN           = "#EC641D"
ELECTRIC_BLUE  = "#16E9D8"
ACID_GREEN     = "#06FF89"
COBALT_PULSE   = "#2C4FFA"
SOLAR_AMBER    = "#FFBA36"
EMBER_ORANGE   = "#FF532C"


def main():
    FIG_DIR.mkdir(exist_ok=True)

    # ── Load data ──
    snap = pd.read_csv(DATA_DIR / "reward_split_snapshot_623.csv")

    # Filter: non-private pools with positive rewards
    pub = snap[
        (snap["pool_class"] != "private")
        & (snap["total_pool_rewards_ada"] > 0)
    ].copy()

    # Compute flat-fee share of reward
    pub["flat_fee_pct"] = pub["fixed_cost_ada"] / pub["total_pool_rewards_ada"] * 100
    pub["stake_m"] = pub["active_stake_ada"] / 1e6

    # Network average reward yield per ADA per epoch
    per_ada = pub["total_pool_rewards_ada"].sum() / pub["active_stake_ada"].sum()

    # Separate by declared flat fee
    at_170 = pub[pub["fixed_cost_ada"] == 170]
    at_340 = pub[pub["fixed_cost_ada"] == 340]
    other  = pub[(pub["fixed_cost_ada"] != 170) & (pub["fixed_cost_ada"] != 340)]

    # ── Theoretical curves ──
    x_th = np.linspace(0.5, 80, 500)
    y_170 = 170 / (x_th * 1e6 * per_ada) * 100
    y_340 = 340 / (x_th * 1e6 * per_ada) * 100

    # ── Figure ──
    fig, ax = plt.subplots(figsize=(14, 7.5), facecolor=BG)
    ax.set_facecolor(BG)

    # Sub-reliable zone (< 3M ADA)
    ax.axvspan(0, 3, color=INFARED, alpha=0.06, zorder=0)
    ax.axvline(3, color=INFARED, linewidth=0.7, linestyle=":", alpha=0.5, zorder=1)
    ax.text(1.5, 52, "Sub-reliable\nzone", fontsize=8, color=INFARED,
            ha="center", va="bottom", alpha=0.7, fontstyle="italic")

    # Reference lines
    ax.axhline(10, color=DIM, linewidth=0.5, linestyle=":", alpha=0.3, zorder=0)
    ax.text(79, 10.8, "10%", fontsize=7.5, color=DIM, ha="right", alpha=0.5)

    ax.axhline(5, color=DIM, linewidth=0.5, linestyle=":", alpha=0.3, zorder=0)
    ax.text(79, 5.8, "5%", fontsize=7.5, color=DIM, ha="right", alpha=0.5)

    # Theoretical curves — bold, the story
    ax.plot(x_th, y_340.clip(max=55), color=DAWN, linewidth=2.5,
            label="340 ADA (former floor)", zorder=4, solid_capstyle="round")
    ax.plot(x_th, y_170.clip(max=55), color=COBALT_PULSE, linewidth=2.5,
            label="170 ADA (current floor)", zorder=4, solid_capstyle="round")

    # Scatter — actual pools, smaller and translucent so curves dominate
    ax.scatter(at_340["stake_m"], at_340["flat_fee_pct"].clip(upper=55),
               s=12, alpha=0.4, color=DAWN, edgecolors="none",
               zorder=5, label=f"Pools at 340 ADA (n={len(at_340)})")
    ax.scatter(at_170["stake_m"], at_170["flat_fee_pct"].clip(upper=55),
               s=12, alpha=0.4, color=COBALT_PULSE, edgecolors="none",
               zorder=5, label=f"Pools at 170 ADA (n={len(at_170)})")
    if len(other) > 0:
        ax.scatter(other["stake_m"], other["flat_fee_pct"].clip(upper=55),
                   s=10, alpha=0.35, color=DIM, edgecolors="none",
                   marker="D", zorder=5, label=f"Other flat fee (n={len(other)})")

    # Annotate the "materiality floor" — below 5% the flat fee is negligible
    ax.fill_between([40, 80], 0, 5, color=ACID_GREEN, alpha=0.08, zorder=0)
    ax.text(60, 2.2, "Flat fee < 5% of reward", fontsize=8, color=DIM,
            ha="center", fontstyle="italic", alpha=0.6)

    # ── Axes ──
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 55)
    ax.set_xlabel("Active stake (M ADA)", fontsize=11, color=DIM)
    ax.set_ylabel("Flat fee as % of pool reward", fontsize=11, color=DIM)

    ax.tick_params(colors=DIM, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.6, zorder=0)
    ax.grid(axis="x", color=GRID, linewidth=0.4, alpha=0.4, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

    # Legend — outside the data area
    leg = ax.legend(fontsize=9, loc="upper right", framealpha=0.95,
                    edgecolor=GRID, borderpad=0.8, labelspacing=0.6)
    leg.get_frame().set_linewidth(0.5)

    # Title
    ax.set_title(
        f"The Regressive Geometry of Flat Fees\n"
        f"Fixed cost as share of pool reward at epoch 623  —  yield {per_ada*100:.4f}% / epoch",
        fontsize=13, fontweight="medium", color=INK, pad=14,
        linespacing=1.6,
    )

    fig.tight_layout()

    out = FIG_DIR / "flat_fee_hyperbole.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
