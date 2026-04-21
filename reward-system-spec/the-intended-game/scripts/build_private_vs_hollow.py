#!/usr/bin/env python3
"""
Private vs Hollow — the two attractors figure for §2.4.2.

Shows the real trade-off: to access the pledge bonus, an operator must
REPLACE delegators with pledge. Delegation space shrinks as pledge grows,
but reward barely moves.

  Panel 1: Pool composition & reward — as pledge increases, delegation
           space collapses while reward barely rises.
  Panel 2: The rational comparison — total operator income under three
           strategies (zero pledge, 50/50, private) vs deploying capital
           as passive delegation elsewhere.

The A(π,ν) function: A = πν − π²(1−ν)
At sub-saturation, increasing π means the operator must provide the stake
themselves — every ADA pledged is one fewer ADA that a delegator occupies.

Outputs: figures/private_vs_hollow.png
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
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
ULTRAVIOLET = "#A700FF"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"
ULTRAVIOLET_DEEP = "#8421A2"


def load_anatomy():
    with (DATA_DIR / "reward_anatomy.json").open() as f:
        return json.load(f)


def pool_reward(pi, nu, P_max, lam_min, lam_max):
    """Pool reward given normalized pledge pi and stake nu."""
    A = pi * nu - pi**2 * (1 - nu)
    return P_max * (lam_min * nu + lam_max * A)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    a = load_anatomy()

    P_max = a["P_max_ada"]
    lam_min = a["lambda_min"]
    lam_max = a["lambda_max"]
    z0 = a["z0_ada"]
    epochs_yr = 73

    # ── Figure setup: 2 panels ──
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5),
                                    gridspec_kw={"width_ratios": [1.2, 1]})
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

    fig.suptitle(
        "Private Pools by Design, Hollow Pools in Practice",
        fontsize=17, fontweight="bold", color=TEXT_COLOR, y=0.97
    )
    fig.text(
        0.5, 0.925,
        f"The pledge-delegation trade-off the mechanism creates  |  Epoch {a['epoch']}",
        ha="center", fontsize=11, color=TEXT_DIM
    )

    # ══════════════════════════════════════════════════════════════════════
    # Panel 1: Pool composition & reward as pledge increases
    # For a 40M ADA pool (realistic, sub-saturated)
    # ══════════════════════════════════════════════════════════════════════

    pool_size_ada = 40e6
    pool_size_m = pool_size_ada / 1e6
    nu = min(pool_size_ada / z0, 1.0)

    # Pledge from 0 to pool_size (can't pledge more than total stake)
    pledge_pcts = np.linspace(0, 100, 500)
    pledge_adas = pledge_pcts / 100 * pool_size_ada
    pis = pledge_adas / z0

    # Delegation = pool_size - pledge
    delegation_adas = pool_size_ada - pledge_adas

    # Reward at each pledge level
    rewards = np.array([pool_reward(pi, nu, P_max, lam_min, lam_max) for pi in pis])

    # Reward at zero pledge (baseline)
    reward_zero = pool_reward(0, nu, P_max, lam_min, lam_max)
    reward_full = pool_reward(nu, nu, P_max, lam_min, lam_max)
    reward_gain = reward_full - reward_zero

    # ── Stacked area: pool composition ──
    ax1.fill_between(pledge_pcts, 0, delegation_adas / 1e6,
                     alpha=0.35, color=ACID_GREEN, label="Delegation")
    ax1.fill_between(pledge_pcts, delegation_adas / 1e6, pool_size_m,
                     alpha=0.35, color=ULTRAVIOLET, label="Pledge")

    # Composition boundary line
    ax1.plot(pledge_pcts, delegation_adas / 1e6, color=ACID_GREEN,
             linewidth=2, alpha=0.7)

    ax1.set_xlabel("Pledge as % of pool", fontsize=11, color=TEXT_DIM)
    ax1.set_ylabel("Pool composition (M ADA)", fontsize=11, color=TEXT_DIM)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, pool_size_m * 1.15)

    # ── Reward overlay on right axis ──
    ax1r = ax1.twinx()
    ax1r.plot(pledge_pcts, rewards, color=INFARED, linewidth=2.5,
              label="Pool reward")
    ax1r.set_ylabel("Pool reward per epoch (ADA)", fontsize=11, color=INFARED)
    ax1r.tick_params(axis='y', colors=INFARED, labelsize=9)
    ax1r.spines['right'].set_color(INFARED)

    # Annotate the reward barely moving
    ax1r.axhline(y=reward_zero, color=INFARED, linewidth=0.8,
                 linestyle=":", alpha=0.3)
    ax1r.axhline(y=reward_full, color=INFARED, linewidth=0.8,
                 linestyle=":", alpha=0.3)

    # At 0% pledge
    ax1r.annotate(
        f"0% pledge\n{reward_zero:,.0f} ADA/ep",
        xy=(0, reward_zero),
        xytext=(8, reward_zero - 800),
        fontsize=9, color=INFARED,
        arrowprops=dict(arrowstyle="->", color=INFARED, alpha=0.4),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=INFARED, alpha=0.85)
    )

    # At 100% pledge (private pool)
    ax1r.annotate(
        f"100% pledge (private pool)\n{reward_full:,.0f} ADA/ep\n"
        f"+{reward_gain:,.0f} ADA/ep (+{reward_gain / reward_zero * 100:.1f}%)",
        xy=(100, reward_full),
        xytext=(50, reward_full + 1500),
        fontsize=9, color=ULTRAVIOLET_DEEP, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=ULTRAVIOLET_DEEP, alpha=0.5,
                        connectionstyle="arc3,rad=-0.2"),
        bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec=ULTRAVIOLET_DEEP, alpha=0.9)
    )

    # At 50% (user's example)
    pledge_50_idx = np.argmin(np.abs(pledge_pcts - 50))
    reward_50 = rewards[pledge_50_idx]
    gain_50 = reward_50 - reward_zero
    ax1r.annotate(
        f"50/50 split\n+{gain_50:,.0f} ADA/ep\n20M locked as pledge",
        xy=(50, reward_50),
        xytext=(62, reward_50 - 1200),
        fontsize=9, color=TEXT_COLOR,
        arrowprops=dict(arrowstyle="->", color=TEXT_DIM, alpha=0.5,
                        connectionstyle="arc3,rad=0.15"),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=TEXT_DIM, alpha=0.85)
    )

    # Insight text
    ax1.text(
        50, pool_size_m * 1.07,
        f"40M ADA pool  —  delegation collapses, reward gains +{reward_gain / reward_zero * 100:.1f}%",
        ha="center", fontsize=10, fontweight="bold", color=TEXT_COLOR,
        bbox=dict(boxstyle="round,pad=0.4", fc="#F9F9F9", ec=GRID_COLOR, alpha=0.9)
    )

    # Composition labels
    ax1.text(15, pool_size_m * 0.25, "Delegation\nspace", fontsize=12,
             fontweight="bold", color=ACID_GREEN, ha="center", alpha=0.8)
    ax1.text(85, pool_size_m * 0.75, "Pledge", fontsize=12,
             fontweight="bold", color=ULTRAVIOLET, ha="center", alpha=0.8)

    ax1.set_title(f"The trade-off: more pledge = less delegation",
                  fontsize=12, color=TEXT_COLOR, pad=12)
    ax1.grid(True, alpha=0.1, color=GRID_COLOR)

    # ══════════════════════════════════════════════════════════════════════
    # Panel 2: The rational comparison
    # What does an operator with 40M ADA actually earn under each strategy?
    # ══════════════════════════════════════════════════════════════════════

    passive_yield_per_epoch = 0.023 / epochs_yr  # ~2.3% annual

    strategies = []

    # Strategy 1: "Hollow" — pledge 100K, delegate rest elsewhere
    pledge_1 = 100_000
    pi_1 = pledge_1 / z0
    pool_reward_1 = pool_reward(pi_1, nu, P_max, lam_min, lam_max)
    # Operator income from pool: assume margin 2% + proportional share of pledge
    # Simplified: operator gets pool reward (they run the pool)
    # But the key metric: what about the 39.9M not pledged?
    remaining_1 = pool_size_ada - pledge_1
    passive_income_1 = remaining_1 * passive_yield_per_epoch  # income from delegating elsewhere
    total_1 = pool_reward_1 + passive_income_1

    strategies.append({
        "name": "Hollow pool\n(100K pledge)",
        "pool_reward": pool_reward_1,
        "passive_income": passive_income_1,
        "pledge_locked": pledge_1,
        "color": ACID_GREEN,
    })

    # Strategy 2: 50/50 — pledge 20M
    pledge_2 = 20e6
    pi_2 = pledge_2 / z0
    pool_reward_2 = pool_reward(pi_2, nu, P_max, lam_min, lam_max)
    remaining_2 = pool_size_ada - pledge_2
    passive_income_2 = remaining_2 * passive_yield_per_epoch
    total_2 = pool_reward_2 + passive_income_2

    strategies.append({
        "name": "50/50 split\n(20M pledge)",
        "pool_reward": pool_reward_2,
        "passive_income": passive_income_2,
        "pledge_locked": pledge_2,
        "color": SOLAR_AMBER,
    })

    # Strategy 3: Private pool — pledge 40M (= pool size)
    pledge_3 = pool_size_ada
    pi_3 = pledge_3 / z0
    pool_reward_3 = pool_reward(pi_3, nu, P_max, lam_min, lam_max)
    remaining_3 = 0
    passive_income_3 = 0
    total_3 = pool_reward_3

    strategies.append({
        "name": "Private pool\n(40M pledge)",
        "pool_reward": pool_reward_3,
        "passive_income": passive_income_3,
        "pledge_locked": pledge_3,
        "color": ULTRAVIOLET,
    })

    # Strategy 4: Pure delegation — don't operate, delegate 40M
    passive_all = pool_size_ada * passive_yield_per_epoch
    strategies.append({
        "name": "Just delegate\n(no pool)",
        "pool_reward": 0,
        "passive_income": passive_all,
        "pledge_locked": 0,
        "color": ELECTRIC_BLUE,
    })

    bar_x = np.arange(len(strategies))
    bar_w = 0.55

    pool_rewards = [s["pool_reward"] for s in strategies]
    passive_incomes = [s["passive_income"] for s in strategies]
    totals = [pr + pi for pr, pi in zip(pool_rewards, passive_incomes)]
    colors = [s["color"] for s in strategies]
    names = [s["name"] for s in strategies]

    # Stacked bars: pool reward (bottom) + passive income (top)
    bars1 = ax2.bar(bar_x, pool_rewards, bar_w, color=colors,
                    edgecolor=BG_COLOR, linewidth=1.5, alpha=0.8,
                    label="Pool reward")
    bars2 = ax2.bar(bar_x, passive_incomes, bar_w, bottom=pool_rewards,
                    color=colors, edgecolor=BG_COLOR, linewidth=1.5,
                    alpha=0.35, hatch="//",
                    label="Passive delegation income")

    # Total labels on top
    for i, (total, pr, pi) in enumerate(zip(totals, pool_rewards, passive_incomes)):
        ax2.text(i, total + 200,
                 f"{total:,.0f}\nADA/ep",
                 ha="center", va="bottom", fontsize=10, fontweight="bold",
                 color=colors[i])
        if pi > 0:
            ax2.text(i, pr + pi / 2,
                     f"+{pi:,.0f}\npassive",
                     ha="center", va="center", fontsize=7.5,
                     color=TEXT_DIM, fontstyle="italic")

    ax2.set_xticks(bar_x)
    ax2.set_xticklabels(names, fontsize=9, color=TEXT_DIM)
    ax2.set_ylabel("Total operator income per epoch (ADA)", fontsize=10, color=TEXT_DIM)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1e3:.0f}K"))

    # Highlight the winner
    winner_idx = np.argmax(totals)
    ax2.annotate(
        "Dominant strategy",
        xy=(winner_idx, totals[winner_idx]),
        xytext=(winner_idx + 0.8, totals[winner_idx] + 1000),
        fontsize=10, color=INFARED, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=INFARED, linewidth=2),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5", ec=INFARED, alpha=0.9)
    )

    ax2.set_title("Total income: 40M ADA, four strategies",
                  fontsize=12, color=TEXT_COLOR, pad=12)
    ax2.grid(True, axis="y", alpha=0.15, color=GRID_COLOR)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=TEXT_DIM, alpha=0.6, label="Pool reward"),
        mpatches.Patch(facecolor=TEXT_DIM, alpha=0.25, hatch="//",
                       label="Passive delegation elsewhere"),
    ]
    ax2.legend(handles=legend_elements, fontsize=9, loc="upper right",
               facecolor="#FFFFFF", edgecolor=GRID_COLOR, labelcolor=TEXT_DIM)

    # ── Bottom insight bar ──
    fig.text(
        0.5, 0.01,
        "Every ADA pledged is one fewer ADA a delegator can occupy.  "
        "The mechanism forces a choice: delegation space or pledge bonus — "
        "and the bonus is never worth the trade.",
        ha="center", fontsize=10, fontstyle="italic", color=SOLAR_AMBER,
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFFF", ec=SOLAR_AMBER, alpha=0.8)
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.9])
    out = FIG_DIR / "private_vs_hollow.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
