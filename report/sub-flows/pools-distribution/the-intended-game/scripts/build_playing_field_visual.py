#!/usr/bin/env python3
"""
Playing Field visual — the hero chart for §4.4.

Two panels on dark background (IOG brand):
  Left:  Stacked bar showing the three reward tiers at saturation
         (P_max = size ceiling + pledge premium), with ADA amounts
  Right: Reward curve by pool size showing base vs bonus,
         with yield-on-pledge-capital as a secondary axis

Outputs: figures/playing_field_mainnet.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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
VOLT_YELLOW = "#F2FF58"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"

# Softer versions for fills
ACID_GREEN_SOFT = "#06FF8966"
ULTRAVIOLET_SOFT = "#A700FF55"
INFARED_SOFT = "#E5232144"


def load_anatomy():
    with (DATA_DIR / "reward_anatomy.json").open() as f:
        return json.load(f)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    a = load_anatomy()

    P_max = a["P_max_ada"]
    lam_min = a["lambda_min"]
    lam_max = a["lambda_max"]
    z0 = a["z0_ada"]
    k = a["k"]
    epochs_yr = 73

    size_ceiling = lam_min * P_max
    pledge_premium = lam_max * P_max

    # ── Figure setup ──
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5),
                                    gridspec_kw={"width_ratios": [1, 1.6]})
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

    fig.suptitle("The Playing Field", fontsize=18, fontweight="bold",
                 color=TEXT_COLOR, y=0.97)
    fig.text(0.5, 0.925,
             f"What a pool can earn — and what it costs  |  Epoch {a['epoch']}",
             ha="center", fontsize=11, color=TEXT_DIM)

    # ══════════════════════════════════════════════════════════════════════
    # Panel 1: The three tiers — stacked bar at saturation
    # ══════════════════════════════════════════════════════════════════════

    bar_x = [0]
    bar_w = 0.45

    # Size ceiling (base)
    ax1.bar(bar_x, [size_ceiling], bottom=[0], width=bar_w,
            color=ACID_GREEN, edgecolor=BG_COLOR, linewidth=1.5)

    # Pledge premium
    ax1.bar(bar_x, [pledge_premium], bottom=[size_ceiling], width=bar_w,
            color=ULTRAVIOLET, edgecolor=BG_COLOR, linewidth=1.5)

    # P_max line
    ax1.axhline(y=P_max, color=INFARED, linewidth=2, linestyle="--", alpha=0.8)

    # ── Right-side value labels ──
    rx = 0.35  # right edge of bar + gap

    # Size ceiling — centered in green zone
    ax1.text(rx, size_ceiling * 0.55,
             f"  {size_ceiling:,.0f} ADA/ep\n  {size_ceiling * epochs_yr / 1e6:.2f}M/yr",
             ha="left", va="center", fontsize=11, fontweight="bold",
             color=ACID_GREEN, linespacing=1.4)

    # Pledge premium — centered in purple zone
    ax1.text(rx, size_ceiling + pledge_premium * 0.55,
             f"  +{pledge_premium:,.0f} ADA/ep\n  +{pledge_premium * epochs_yr / 1e3:.0f}K/yr",
             ha="left", va="center", fontsize=11, fontweight="bold",
             color="#CC88FF", linespacing=1.4)

    # P_max label above
    ax1.text(0, P_max + 1200,
             f"$P_{{max}}$ = {P_max:,.0f} ADA",
             ha="center", va="bottom", fontsize=14, fontweight="bold",
             color=INFARED)

    # ── Left-side requirement boxes ──
    lx = -0.34

    ax1.text(lx, size_ceiling * 0.35,
             "77M ADA stake\nZero pledge",
             ha="center", va="center", fontsize=8.5, color=TEXT_COLOR,
             linespacing=1.5,
             bbox=dict(boxstyle="round,pad=0.5", fc="#F0FFF0", ec=ACID_GREEN,
                       linewidth=1.2, alpha=0.95))

    ax1.text(lx, size_ceiling + pledge_premium * 0.45,
             "77M ADA pledge\n0.68%/yr yield",
             ha="center", va="center", fontsize=8.5, color=TEXT_COLOR,
             linespacing=1.5,
             bbox=dict(boxstyle="round,pad=0.5", fc="#F5F0FF", ec=ULTRAVIOLET,
                       linewidth=1.2, alpha=0.95))

    # Passive yield reference below
    ax1.text(0, -2800,
             "Passive delegation yield: ~2.3%/yr",
             ha="center", va="top", fontsize=9.5, fontstyle="italic",
             color=SOLAR_AMBER)

    ax1.set_xlim(-0.7, 0.95)
    ax1.set_ylim(-4500, P_max * 1.18)
    ax1.set_xticks([])
    ax1.set_ylabel("Pool reward per epoch (ADA)", fontsize=10, color=TEXT_DIM)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}K"))
    ax1.set_title("Reward tiers at full saturation", fontsize=12,
                   color=TEXT_COLOR, pad=12)

    # ══════════════════════════════════════════════════════════════════════
    # Panel 2: Reward by pool size — base, bonus, yield on pledge
    # ══════════════════════════════════════════════════════════════════════

    sizes_m = np.linspace(0.5, 80, 500)  # pool sizes in M ADA
    nus = np.minimum(sizes_m * 1e6 / z0, 1.0)

    # Zero pledge: reward = P_max * lam_min * nu
    reward_zero = P_max * lam_min * nus

    # Max pledge (pi = nu): A(nu, nu) = nu^3
    As = nus ** 3
    reward_max = P_max * (lam_min * nus + lam_max * As)

    bonus = reward_max - reward_zero

    # Yield on pledge capital: bonus * 73 / (size_ada)
    # At max pledge, pledge = total_stake, so yield = bonus * 73 / stake
    pledge_yield = np.where(sizes_m > 0,
                            bonus * epochs_yr / (sizes_m * 1e6) * 100, 0)

    # Base area fill
    ax2.fill_between(sizes_m, 0, reward_zero, alpha=0.4, color=ACID_GREEN)
    ax2.plot(sizes_m, reward_zero, color=ACID_GREEN, linewidth=2,
             label="Size only (zero pledge)")

    # Bonus area fill
    ax2.fill_between(sizes_m, reward_zero, reward_max, alpha=0.35, color=ULTRAVIOLET)
    ax2.plot(sizes_m, reward_max, color=ULTRAVIOLET, linewidth=2, linestyle="--",
             label="Max pledge (π = ν, fully self-funded)")

    # P_max ceiling
    ax2.axhline(y=P_max, color=INFARED, linewidth=1.5, linestyle=":",
                alpha=0.6, label=f"$P_{{max}}$ = {P_max:,.0f} ADA")

    # Size ceiling at saturation
    ax2.axhline(y=size_ceiling, color=ACID_GREEN, linewidth=1, linestyle=":",
                alpha=0.4)

    # Saturation vertical line
    ax2.axvline(x=z0/1e6, color=INFARED, linewidth=1, linestyle="--", alpha=0.4)
    ax2.text(z0/1e6 + 0.5, P_max * 0.15, f"z₀ = {z0/1e6:.0f}M",
             fontsize=9, color=INFARED, alpha=0.7, rotation=90, va="bottom")

    # Viability line
    ax2.axvline(x=3, color=TEXT_DIM, linewidth=0.8, linestyle="--", alpha=0.4)
    ax2.text(3.5, P_max * 0.92, "Viability\n(3M)", fontsize=8,
             color=TEXT_DIM, alpha=0.6)

    # Annotate specific pool sizes with bonus amounts
    # Place labels INSIDE or immediately adjacent to the purple zone,
    # with short arrows pointing at the midpoint of the bonus band.
    annotations = [
        # (pool_size_M, text_offset_x, text_offset_y)
        (10,  3.5,  900),
        (30,  3.5,  1200),
        (55,  3.5,  1500),
    ]
    for size_m, dx, dy in annotations:
        idx = np.argmin(np.abs(sizes_m - size_m))
        r0 = reward_zero[idx]
        rm = reward_max[idx]
        b = rm - r0
        yld = pledge_yield[idx]

        mid_y = (r0 + rm) / 2
        ax2.annotate(
            f"+{b:,.0f} ADA/ep\n{yld:.2f}%/yr on pledge",
            xy=(size_m, mid_y),
            xytext=(size_m + dx, mid_y + dy),
            fontsize=8, color="#B8860B",
            arrowprops=dict(arrowstyle="->", color="#B8860B", alpha=0.6,
                           lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#B8860B", alpha=0.9))


    ax2.set_xlabel("Pool size (M ADA)", fontsize=10, color=TEXT_DIM)
    ax2.set_ylabel("Pool reward per epoch (ADA)", fontsize=10, color=TEXT_DIM)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e3:.0f}K"))
    ax2.set_xlim(0, 82)
    ax2.set_ylim(0, P_max * 1.15)
    ax2.legend(fontsize=9, loc="upper left",
               facecolor="#FFFFFF", edgecolor=GRID_COLOR, labelcolor=TEXT_DIM)
    ax2.set_title("Reward by pool size: what size buys vs. what pledge adds",
                   fontsize=12, color=TEXT_COLOR, pad=12)
    ax2.grid(True, alpha=0.15, color=GRID_COLOR)

    # ── Bottom insight bar ──
    fig.text(0.5, 0.02,
             "The game is about size (ν), not commitment (π).  "
             "The pledge premium reserves 23% of P_max but yields less than passive delegation at every scale.",
             ha="center", fontsize=10, fontstyle="italic",
             color=SOLAR_AMBER,
             bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFFF", ec=SOLAR_AMBER, alpha=0.8))

    plt.tight_layout(rect=[0, 0.06, 1, 0.9])
    out = FIG_DIR / "playing_field_mainnet.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
