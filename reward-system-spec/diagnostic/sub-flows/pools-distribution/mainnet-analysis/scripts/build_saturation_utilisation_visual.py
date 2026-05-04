#!/usr/bin/env python3
"""
Build a visual showing saturation utilisation across the pool landscape.
Styled in IOG dark brand palette.

Outputs:
  - figures/saturation_utilisation_mainnet.png

Two panels:
  Top:    Pool stake distribution as % of z₀ (sorted), with saturation line, near-saturation zone, and viability line.
  Bottom: Cumulative stake coverage — how many pools (sorted by size) needed to cover X% of stake.

Brand colours (IOG):
  - Dark background: #0A0A0A
  - Grid: #222222
  - Text: #FFFFFF (primary) / #999999 (secondary)
  - Electric Blue (Research): #16E9D8
  - INFARED (Primary): #E52321
  - DAWN (Warm accent): #EC641D
  - Solar Amber (Tertiary): #FFBA36
  - Ultraviolet (Venture): #A700FF
  - Acid Green (Engineering): #06FF89
  - Volt Yellow (Content): #F2FF58
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# IOG Dark Brand Palette
DARK_BG = "#FFFFFF"
GRID_COLOR = "#E0E0E0"
TEXT_PRIMARY = "#1A1A1A"
TEXT_SECONDARY = "#666666"

# IOG Brand Colours
INFARED = "#E52321"
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
ULTRAVIOLET = "#A700FF"
VOLT_YELLOW = "#F2FF58"
SOLAR_AMBER = "#FFBA36"

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
SNAPSHOT_PATH = REPORT_DIR / "data" / "pool_distribution_snapshot.json"


def parse_float(v, default=0.0):
    if v is None:
        return default
    v = str(v).strip()
    return float(v) if v else default


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with SNAPSHOT_PATH.open() as f:
        snap = json.load(f)
    z0 = snap["z0_ada"]
    k = snap["k"]

    # Load pools
    stakes = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("pool_status") == "registered":
                stake = parse_float(r.get("active_stake")) / 1e6
                if stake > 0:
                    stakes.append(stake)

    stakes.sort(reverse=True)
    stakes = np.array(stakes)
    total_stake = stakes.sum()
    n = len(stakes)

    sat_pct = stakes / z0 * 100  # % of saturation

    # Cumulative stake
    cum_stake = np.cumsum(stakes)
    cum_pct = cum_stake / total_stake * 100

    # --- Figure ---
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(14, 9), gridspec_kw={"height_ratios": [3, 2]}
    )
    fig.patch.set_facecolor(DARK_BG)

    # Top: saturation profile
    x = np.arange(1, n + 1)

    # Area fill for saturation profile (Electric Blue with alpha)
    ax_top.fill_between(x, sat_pct, alpha=0.35, color=ELECTRIC_BLUE)

    # Saturation line at z₀ (100%) — INFARED, dashed
    ax_top.axhline(
        y=100,
        color=INFARED,
        linewidth=2.5,
        linestyle="--",
        label=f"Saturation (z₀ = {z0 / 1e6:.1f}M ADA)",
    )

    # Near-saturation zone at 80% — DAWN
    ax_top.axhline(
        y=80, color=DAWN, linewidth=1.5, linestyle="-", alpha=0.8, label="Near-saturation (80%)"
    )

    # Viability line — SOLAR_AMBER, dotted
    viability_pct = 3_000_000 / z0 * 100
    ax_top.axhline(
        y=viability_pct,
        color=SOLAR_AMBER,
        linewidth=1.5,
        linestyle=":",
        alpha=0.8,
        label=f"Production threshold (3M = {viability_pct:.1f}%)",
    )

    # Mark k=500 — ULTRAVIOLET
    max_sat = snap["max_saturable_pools"]
    ax_top.axvline(x=k, color=ULTRAVIOLET, linewidth=1.5, linestyle="--", alpha=0.7)
    ax_top.text(
        k + 10,
        ax_top.get_ylim()[1] * 0.88,
        f"k = {k}",
        fontsize=10,
        color=ULTRAVIOLET,
        fontweight="bold",
    )

    # Mark max saturable pools
    ax_top.axvline(x=max_sat, color=ULTRAVIOLET, linewidth=1.5, linestyle=":", alpha=0.5)
    ax_top.text(
        max_sat + 10,
        ax_top.get_ylim()[1] * 0.76,
        f"Max saturable ({max_sat})",
        fontsize=9,
        color=ULTRAVIOLET,
        alpha=0.9,
    )

    # Insight title with metric
    n_saturated = np.sum(sat_pct >= 100)
    pct_bound = (n_saturated / n) * 100
    ax_top.set_title(
        f"Only {n_saturated} pools reach saturation — the cap binds for {pct_bound:.1f}% of the network",
        fontsize=14,
        fontweight="bold",
        color=TEXT_PRIMARY,
        pad=16,
    )

    ax_top.set_xlabel("Pool rank (sorted by stake, descending)", color=TEXT_SECONDARY, fontsize=11)
    ax_top.set_ylabel("Stake as % of saturation point (z₀)", color=TEXT_SECONDARY, fontsize=11)
    ax_top.legend(loc="upper right", fontsize=10, framealpha=0.95, facecolor=DARK_BG, edgecolor=GRID_COLOR)
    ax_top.set_xlim(0, min(n + 10, 1500))
    ax_top.set_ylim(0, min(sat_pct.max() * 1.1, 200))

    # Styling: dark theme
    ax_top.set_facecolor(DARK_BG)
    ax_top.spines["top"].set_visible(False)
    ax_top.spines["right"].set_visible(False)
    ax_top.spines["left"].set_color(GRID_COLOR)
    ax_top.spines["bottom"].set_color(GRID_COLOR)
    ax_top.tick_params(colors=TEXT_SECONDARY, labelsize=10)
    ax_top.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)

    # Bottom: cumulative stake coverage
    # Cumulative curve in ACID_GREEN
    ax_bot.fill_between(x, cum_pct, alpha=0.25, color=ACID_GREEN)
    ax_bot.plot(x, cum_pct, color=ACID_GREEN, linewidth=2.5)

    # Reference lines: 50%, 80%, 97.3%
    ax_bot.axhline(y=50, color=GRID_COLOR, linewidth=0.8, linestyle=":", alpha=0.6)
    ax_bot.axhline(y=80, color=GRID_COLOR, linewidth=0.8, linestyle=":", alpha=0.6)
    ax_bot.axhline(
        y=97.3,
        color=SOLAR_AMBER,
        linewidth=1.5,
        linestyle="--",
        alpha=0.8,
        label="Healthy pools (97.3%)",
    )

    # Find how many pools for 50%, 80%, and 97.3%
    idx_50 = np.searchsorted(cum_pct, 50)
    idx_80 = np.searchsorted(cum_pct, 80)
    idx_973 = np.searchsorted(cum_pct, 97.3)

    ax_bot.axvline(x=idx_50 + 1, color=TEXT_SECONDARY, linewidth=0.8, linestyle=":", alpha=0.4)
    ax_bot.text(
        idx_50 + 8, 48, f"{idx_50 + 1}", fontsize=9, color=TEXT_SECONDARY, alpha=0.8
    )

    ax_bot.axvline(x=idx_80 + 1, color=TEXT_SECONDARY, linewidth=0.8, linestyle=":", alpha=0.4)
    ax_bot.text(
        idx_80 + 8, 77, f"{idx_80 + 1}", fontsize=9, color=TEXT_SECONDARY, alpha=0.8
    )

    ax_bot.axvline(x=idx_973 + 1, color=SOLAR_AMBER, linewidth=1, linestyle=":", alpha=0.6)
    ax_bot.text(
        idx_973 + 8,
        95,
        f"{idx_973 + 1} pools",
        fontsize=9,
        color=SOLAR_AMBER,
        fontweight="bold",
    )

    ax_bot.set_xlabel("Number of pools (sorted by stake, descending)", color=TEXT_SECONDARY, fontsize=11)
    ax_bot.set_ylabel("Cumulative share of active stake (%)", color=TEXT_SECONDARY, fontsize=11)
    ax_bot.set_title(
        "Stake Concentration — How Many Pools Cover the Network",
        fontsize=13,
        fontweight="bold",
        color=TEXT_PRIMARY,
        pad=14,
    )
    ax_bot.legend(loc="lower right", fontsize=10, framealpha=0.95, facecolor=DARK_BG, edgecolor=GRID_COLOR)
    ax_bot.set_xlim(0, min(n + 10, 1500))
    ax_bot.set_ylim(0, 105)

    # Styling: dark theme
    ax_bot.set_facecolor(DARK_BG)
    ax_bot.spines["top"].set_visible(False)
    ax_bot.spines["right"].set_visible(False)
    ax_bot.spines["left"].set_color(GRID_COLOR)
    ax_bot.spines["bottom"].set_color(GRID_COLOR)
    ax_bot.tick_params(colors=TEXT_SECONDARY, labelsize=10)
    ax_bot.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)

    plt.tight_layout()
    out_path = FIG_DIR / "saturation_utilisation_mainnet.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    main()
