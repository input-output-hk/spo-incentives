#!/usr/bin/env python3
"""
Distribution Efficiency — Sequential Waterfall.

Shows the pools pot decomposition as a sequential waterfall matching §2:
  Step 1: Participation gap (unstaked ADA)
  Step 2: Pledge-not-met confiscation
  Step 3a: Bonus budget unused
  Step 3b: Performance loss
  Step 3c: Oversaturation cap
  → Distributed

Outputs: figures/distribution_efficiency_mainnet.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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
DELIVERED_GREEN= "#00875A"
SOLAR_AMBER    = "#FFBA36"
GREY_MED       = "#999999"
ULTRAVIOLET    = "#A700FF"
CONFISCATED    = "#B71C1C"


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with (DATA_DIR / "reward_anatomy.json").open() as f:
        a = json.load(f)

    pot       = a["R_pools_pot_ada"]
    dist      = a["distributed_ada"]
    Pmax      = a["P_max_ada"]
    k         = a["k"]
    lam_min   = a["lambda_min"]
    lam_max   = a["lambda_max"]
    sum_nu    = a["sum_nu"]
    base_pct  = a["sum_base_over_k_pct"]
    bonus_pct = a["sum_bonus_over_k_pct"]
    E_pct     = a["sum_E_over_k_pct"]
    epoch     = a["epoch"]

    base_delivered  = base_pct / 100 * pot
    bonus_delivered = bonus_pct / 100 * pot
    E_at_pbar1      = E_pct / 100 * pot
    perf_loss       = E_at_pbar1 - dist

    base_budget  = lam_min * pot
    bonus_budget = lam_max * pot

    # Sequential flow values
    participation_gap = base_budget - base_delivered - 0.33e6  # minus pledge-unmet base
    pledge_confiscated = 0.32e6  # from epoch 615 data
    bonus_unused = bonus_budget - bonus_delivered
    performance = perf_loss
    oversaturation = a.get("base_lost_to_cap_pct", 0) / 100 * pot

    # ── Build waterfall data ──
    steps = [
        ("Pools pot",              pot,                DELIVERED_GREEN, "start"),
        ("Step 1:\nParticipation\ngap", -participation_gap, SOLAR_AMBER,    "loss"),
        ("Step 2:\nPledge-not-met\nconfiscation", -pledge_confiscated, CONFISCATED, "loss"),
        ("Step 3a:\nBonus budget\nunused", -bonus_unused, INFARED, "loss"),
        ("Step 3b:\nPerformance",  -performance,       GREY_MED,       "loss"),
        ("Step 3c:\nOversaturation", -oversaturation,  ULTRAVIOLET,    "loss"),
        ("Distributed",            dist,               DELIVERED_GREEN, "end"),
    ]

    fig, ax = plt.subplots(figsize=(16, 7), facecolor=BG)
    ax.set_facecolor(BG)

    n = len(steps)
    x = np.arange(n)
    bar_width = 0.6

    running = 0
    bottoms = []
    heights = []
    colors = []
    labels_text = []

    for i, (label, value, color, stype) in enumerate(steps):
        if stype == "start":
            bottom = 0
            height = value
        elif stype == "end":
            bottom = 0
            height = value
        else:  # loss
            bottom = running + value  # value is negative
            height = -value
            running += value

        bottoms.append(bottom)
        heights.append(height)
        colors.append(color)
        labels_text.append(label)

    # Draw bars
    for i in range(n):
        alpha = 0.92 if steps[i][3] in ("start", "end") else 0.78
        edgecolor = DELIVERED_GREEN if steps[i][3] in ("start", "end") else "white"
        ax.bar(x[i], heights[i], bottom=bottoms[i], width=bar_width,
               color=colors[i], alpha=alpha, edgecolor=edgecolor, linewidth=1.5,
               zorder=3)

        # Value label inside or above bar
        val = steps[i][1]
        abs_val = abs(val)
        mid_y = bottoms[i] + heights[i] / 2

        if abs_val >= 0.5e6:
            label_str = f"{abs_val/1e6:.2f}M\n({abs_val/pot*100:.1f}%)"
            text_color = "white" if colors[i] in (DELIVERED_GREEN, INFARED, CONFISCATED) else INK
            ax.text(x[i], mid_y, label_str, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color, zorder=4)
        elif abs_val >= 0.01e6:
            label_str = f"{abs_val/1e6:.2f}M ({abs_val/pot*100:.1f}%)"
            ax.text(x[i], bottoms[i] + heights[i] + 0.15e6, label_str,
                    ha="center", va="bottom", fontsize=8, color=INK, zorder=4)

    # Connector lines between bars
    for i in range(n - 1):
        if steps[i][3] == "start":
            y_connect = bottoms[i] + heights[i]  # top of start bar
        elif steps[i][3] == "loss":
            y_connect = bottoms[i]  # bottom of loss bar = top of remaining
        else:
            continue

        if steps[i+1][3] == "loss":
            y_next = bottoms[i+1] + heights[i+1]  # top of next loss bar
        elif steps[i+1][3] == "end":
            y_next = bottoms[i+1] + heights[i+1]  # top of end bar
        else:
            continue

        ax.plot([x[i] + bar_width/2, x[i+1] - bar_width/2],
                [y_connect, y_connect],
                color=DIM, linewidth=1, linestyle="--", alpha=0.5, zorder=2)

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels([s[0] for s in steps], fontsize=9, color=INK)

    # Y-axis
    ax.set_ylabel("ADA per epoch (millions)", fontsize=11, color=DIM)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1e6:.0f}M"))
    ax.set_ylim(0, pot * 1.08)
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=DIM)

    # Title
    ax.set_title(
        f"Pools Pot Decomposition — Sequential Flow (Epoch {epoch})",
        fontsize=14, fontweight="bold", color=INK, pad=16,
    )

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=DELIVERED_GREEN, alpha=0.92, label="Pot / Distributed"),
        mpatches.Patch(facecolor=SOLAR_AMBER, alpha=0.78, label="Participation gap (unstaked)"),
        mpatches.Patch(facecolor=CONFISCATED, alpha=0.78, label="Pledge-not-met confiscation"),
        mpatches.Patch(facecolor=INFARED, alpha=0.78, label="Bonus budget unused"),
        mpatches.Patch(facecolor=GREY_MED, alpha=0.78, label="Performance loss"),
        mpatches.Patch(facecolor=ULTRAVIOLET, alpha=0.78, label="Oversaturation cap"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8.5,
              framealpha=0.95, ncol=2)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "distribution_efficiency_mainnet.png",
                dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {FIG_DIR / 'distribution_efficiency_mainnet.png'}")


if __name__ == "__main__":
    main()
