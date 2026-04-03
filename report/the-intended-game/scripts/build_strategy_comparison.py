#!/usr/bin/env python3
"""
Strategy comparison — the rational path to hollow pools.

For five named strategies (Hollow → Private), shows:
  Panel 1: Pool reward vs opportunity cost (bar chart)
           At saturation (77M) — pledge premium vs delegation foregone
  Panel 2: Same at 40M (sub-saturated) — concavity makes it worse

Each strategy pair shows the pledge premium gained (positive) and the
passive delegation income foregone (negative), making the net loss visible.

Outputs: figures/strategy_comparison.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"

# ── IOG Brand Palette ──
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#666666"
GRID_COLOR = "#E0E0E0"

INFARED = "#E52321"
ACID_GREEN = "#00B35F"
ULTRAVIOLET = "#A700FF"
SOLAR_AMBER = "#FFBA36"
ULTRAVIOLET_DEEP = "#8421A2"


def load_anatomy():
    with (DATA_DIR / "reward_anatomy.json").open() as f:
        return json.load(f)


def A_func(pi, nu):
    return pi * nu - pi**2 * (1 - nu)


def pool_reward(pi, nu, P_max, lam_min, lam_max):
    return P_max * (lam_min * nu + lam_max * A_func(pi, nu))


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    a = load_anatomy()

    P_max = a["P_max_ada"]
    lam_min = a["lambda_min"]
    lam_max = a["lambda_max"]
    z0 = a["z0_ada"]
    epochs_yr = 73
    passive_annual = 0.023

    strategies = [
        ("Hollow\n(0/100)", 0.0),
        ("Healthy\ndelegation\n(20/80)", 0.2),
        ("Balanced\n(50/50)", 0.5),
        ("Healthy\npledge\n(80/20)", 0.8),
        ("Private\n(100/0)", 1.0),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5),
                                    gridspec_kw={"width_ratios": [1, 1]})
    fig.patch.set_facecolor(BG_COLOR)

    fig.suptitle(
        "Five Strategies, One Direction",
        fontsize=17, fontweight="bold", color=TEXT_COLOR, y=0.97
    )
    fig.text(
        0.5, 0.925,
        "Pledge premium gained vs. delegation income foregone  |  "
        f"Epoch {a['epoch']}",
        ha="center", fontsize=11, color=TEXT_DIM
    )

    panels = [
        (ax1, 77e6, "At saturation (77M ₳, ν = 1)"),
        (ax2, 40e6, "At 40M ₳ (ν ≈ 0.52)"),
    ]

    for ax, pool_size, title in panels:
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

        nu = min(pool_size / z0, 1.0)
        r_hollow = pool_reward(0, nu, P_max, lam_min, lam_max)

        bar_x = np.arange(len(strategies))
        bar_w = 0.35

        premiums = []
        opp_costs = []
        net_gains = []

        for name, ratio in strategies:
            pledge = ratio * pool_size
            pi = pledge / z0
            r = pool_reward(pi, nu, P_max, lam_min, lam_max)
            premium = r - r_hollow
            opp_cost = pledge * passive_annual / epochs_yr
            premiums.append(premium)
            opp_costs.append(opp_cost)
            net_gains.append(premium - opp_cost)

        # Premium bars (positive, purple)
        bars_p = ax.bar(bar_x - bar_w / 2, premiums, bar_w,
                        color=ULTRAVIOLET, alpha=0.75,
                        edgecolor=BG_COLOR, linewidth=1.5,
                        label="Pledge premium gained")

        # Opportunity cost bars (negative, shown as positive in green)
        bars_o = ax.bar(bar_x + bar_w / 2, [-c for c in opp_costs], bar_w,
                        color=INFARED, alpha=0.6,
                        edgecolor=BG_COLOR, linewidth=1.5,
                        label="Delegation income foregone")

        # Net gain line
        ax.plot(bar_x, net_gains, 'o-', color=SOLAR_AMBER,
                linewidth=2.5, markersize=8, zorder=5,
                label="Net gain (premium − cost)")

        # Zero line
        ax.axhline(y=0, color=TEXT_DIM, linewidth=1, alpha=0.5)

        # Value labels on net gain
        for i, (ng, prem, opp) in enumerate(zip(net_gains, premiums, opp_costs)):
            if i == 0:
                continue  # skip hollow (0/0)
            # Net label
            ax.text(i, ng - 800, f"net: {ng:+,.0f}",
                    ha="center", va="top", fontsize=8, fontweight="bold",
                    color=SOLAR_AMBER)
            # Premium label
            if prem > 0:
                ax.text(i - bar_w / 2, prem + 200,
                        f"+{prem:,.0f}",
                        ha="center", va="bottom", fontsize=7.5,
                        color=ULTRAVIOLET_DEEP)
            # Opp cost label
            if opp > 0:
                ax.text(i + bar_w / 2, -opp - 200,
                        f"−{opp:,.0f}",
                        ha="center", va="top", fontsize=7.5,
                        color=INFARED)

        # Ratio annotation for the worst case
        if pool_size > 50e6:
            worst_ratio = opp_costs[-1] / premiums[-1] if premiums[-1] > 0 else 0
            ax.text(
                len(strategies) - 1, net_gains[-1] - 2500,
                f"Cost/premium\nratio: {worst_ratio:.1f}×",
                ha="center", fontsize=9, fontweight="bold", color=INFARED,
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5",
                          ec=INFARED, alpha=0.9)
            )
        else:
            worst_ratio = opp_costs[-1] / premiums[-1] if premiums[-1] > 0 else 0
            ax.text(
                len(strategies) - 1, net_gains[-1] - 1800,
                f"Cost/premium\nratio: {worst_ratio:.1f}×",
                ha="center", fontsize=9, fontweight="bold", color=INFARED,
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5",
                          ec=INFARED, alpha=0.9)
            )

        names = [s[0] for s in strategies]
        ax.set_xticks(bar_x)
        ax.set_xticklabels(names, fontsize=8.5, color=TEXT_DIM)
        ax.set_ylabel("ADA per epoch", fontsize=10, color=TEXT_DIM)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{x / 1e3:+.1f}K" if abs(x) >= 1000
                                  else f"{x:+,.0f}")
        )
        ax.set_title(title, fontsize=12, color=TEXT_COLOR, pad=12)
        ax.legend(fontsize=8, loc="lower left",
                  facecolor="#FFFFFF", edgecolor=GRID_COLOR, labelcolor=TEXT_DIM)
        ax.grid(True, axis="y", alpha=0.15, color=GRID_COLOR)

    # ── Bottom insight bar ──
    fig.text(
        0.5, 0.01,
        "At every pledge level, the opportunity cost exceeds the premium.  "
        "The rational trajectory leads monotonically toward the Hollow strategy.",
        ha="center", fontsize=10, fontstyle="italic", color=SOLAR_AMBER,
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFFF", ec=SOLAR_AMBER, alpha=0.8)
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.9])
    out = FIG_DIR / "strategy_comparison.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
