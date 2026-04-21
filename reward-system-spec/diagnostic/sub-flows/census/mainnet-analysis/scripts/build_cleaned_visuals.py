#!/usr/bin/env python3
"""
Cleaning pass 1 — epoch_stake as single source of truth.

Raw data stays in data/.
Cleaned visuals go in figures/ with _clean suffix.

Noise removed:
  - delegation-table counts (certificates ≠ active stake) replaced by epoch_stake
  - dual-source confusion eliminated: one line per metric, not two
  - last epoch excluded if incomplete (checked: 623 is stable, keep it)
  - Y-axes start at meaningful baselines, not zero, to reveal structure

Reads:
  data/supply_decomposition.csv
  data/staking_per_epoch.csv
  data/pool_operator_type.csv

Outputs:
  figures/staking_participation_clean.png   (§1+§2 combined: supply + participation)
  figures/pool_count_clean.png              (§3: pool count, epoch_stake only)
  figures/delegator_count_clean.png         (§4: delegation count, epoch_stake only)
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
INFARED         = "#E52321"
DELIVERED_GREEN = "#00875A"
ELECTRIC_BLUE   = "#16E9D8"
ULTRAVIOLET     = "#A700FF"
SOLAR_AMBER     = "#FFBA36"
GREY_LIGHT      = "#B0B0B0"
ACID_GREEN      = "#06FF89"
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"
HYPER_PINK      = "#FF79FC"

LOVELACE = 1e6


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    supply = load_csv(DATA_DIR / "supply_decomposition.csv")
    staking = load_csv(DATA_DIR / "staking_per_epoch.csv")
    operators = load_csv(DATA_DIR / "pool_operator_type.csv")

    # ── Align on common epoch range ──
    # supply: 209→623, staking: 210→623
    # Use 211→623 (Shelley active staking starts at 211)
    supply_map = {int(r["epoch_no"]): r for r in supply}
    staking_map = {int(r["epoch_no"]): r for r in staking}

    epochs = sorted(set(supply_map.keys()) & set(staking_map.keys()))
    epochs = [e for e in epochs if e >= 211]

    # ── Build aligned arrays ──
    circulating = np.array([int(supply_map[e]["circulating"]) / LOVELACE for e in epochs])
    reserve     = np.array([int(supply_map[e]["reserve"]) / LOVELACE for e in epochs])
    treasury    = np.array([int(supply_map[e]["treasury"]) / LOVELACE for e in epochs])
    staked      = np.array([int(staking_map[e]["total_staked"]) / LOVELACE for e in epochs])
    unstaked    = circulating - staked
    rate_pct    = staked / circulating * 100

    n_deleg     = np.array([int(staking_map[e]["delegation_count"]) for e in epochs])
    n_pools     = np.array([int(staking_map[e]["pool_count"]) for e in epochs])

    ep = np.array(epochs)

    # ══════════════════════════════════════════════════════════
    # Figure 1: Staking participation (combined §1+§2)
    # ══════════════════════════════════════════════════════════
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), facecolor=BG,
                              gridspec_kw={"height_ratios": [2, 1]}, sharex=True)
    ax1, ax2 = axes

    # Top: stacked area — staked vs unstaked
    ax1.set_facecolor(BG)
    ax1.stackplot(ep,
                  staked / 1e9,
                  unstaked / 1e9,
                  colors=[DELIVERED_GREEN, GREY_LIGHT],
                  alpha=0.55,
                  labels=["Staked", "Unstaked (circulating − staked)"])
    ax1.plot(ep, circulating / 1e9, color=INK, linewidth=1.0, linestyle=":", alpha=0.5,
             label="Circulating supply")

    # Staking rate on secondary axis
    ax1r = ax1.twinx()
    ax1r.plot(ep, rate_pct, color=INFARED, linewidth=1.8, alpha=0.85)
    ax1r.set_ylabel("Staking rate (%)", fontsize=10, color=INFARED)
    ax1r.tick_params(axis="y", colors=INFARED, labelsize=9)
    ax1r.set_ylim(40, 75)
    ax1r.spines["right"].set_color(INFARED)
    ax1r.spines["right"].set_alpha(0.3)
    for sp in ["top", "left"]:
        ax1r.spines[sp].set_visible(False)

    ax1.set_ylabel("ADA (billions)", fontsize=11, color=DIM)
    ax1.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax1.spines[sp].set_visible(False)
    ax1.spines["left"].set_color(GRID)
    ax1.tick_params(colors=DIM, labelsize=9)
    leg = ax1.legend(loc="upper left", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Latest stats annotation
    last_e = epochs[-1]
    ax1.annotate(
        f"Epoch {last_e}: {staked[-1]/1e9:.2f}B staked / {circulating[-1]/1e9:.2f}B circulating = {rate_pct[-1]:.1f}%",
        xy=(last_e, staked[-1] / 1e9),
        xytext=(last_e - 120, staked[-1] / 1e9 + 4),
        fontsize=8.5, color=DIM,
        arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7))

    # Bottom: pool count + delegations (epoch_stake only)
    ax2.set_facecolor(BG)
    ax2.plot(ep, n_deleg, color=COBALT_PULSE, linewidth=1.8,
             label=f"Active delegations ({n_deleg[-1]:,})")
    ax2.set_ylabel("Active delegations", fontsize=10, color=COBALT_PULSE)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"))
    ax2.tick_params(axis="y", colors=COBALT_PULSE, labelsize=9)

    ax2r = ax2.twinx()
    ax2r.plot(ep, n_pools, color=ULTRAVIOLET, linewidth=1.5,
              label=f"Active pools ({n_pools[-1]:,})")
    ax2r.set_ylabel("Active pools", fontsize=10, color=ULTRAVIOLET)
    ax2r.tick_params(axis="y", colors=ULTRAVIOLET, labelsize=9)
    ax2r.spines["right"].set_color(ULTRAVIOLET)
    ax2r.spines["right"].set_alpha(0.3)

    ax2.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax2.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.spines["left"].set_color(COBALT_PULSE)
    ax2.spines["left"].set_alpha(0.3)
    ax2.spines["bottom"].set_color(GRID)
    for sp in ["top", "left"]:
        ax2r.spines[sp].set_visible(False)

    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2r.get_legend_handles_labels()
    leg2 = ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
                       fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg2.get_frame().set_linewidth(0.5)

    ax1.set_xlim(ep[0], ep[-1])
    fig.suptitle("Staking Participation on Cardano Mainnet",
                 fontsize=14, fontweight="medium", color=INK, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out1 = FIG_DIR / "staking_participation_clean.png"
    fig.savefig(out1, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out1}")

    # ══════════════════════════════════════════════════════════
    # Figure 2: Pool count — clean (epoch_stake only)
    # ══════════════════════════════════════════════════════════
    fig, ax = plt.subplots(figsize=(14, 5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.fill_between(ep, n_pools, color=ULTRAVIOLET, alpha=0.12)
    ax.plot(ep, n_pools, color=ULTRAVIOLET, linewidth=2.0)

    # Key milestones
    peak_idx = np.argmax(n_pools)
    ax.annotate(f"Peak: {n_pools[peak_idx]:,} (epoch {ep[peak_idx]})",
                xy=(ep[peak_idx], n_pools[peak_idx]),
                xytext=(ep[peak_idx] - 80, n_pools[peak_idx] + 150),
                fontsize=9, color=DIM,
                arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7))

    # k=500 saturation line
    ax.axhline(500, color=DAWN, linewidth=1.0, linestyle="--", alpha=0.6)
    ax.text(ep[5], 520, "k = 500", fontsize=8, color=DAWN, alpha=0.8)

    ax.set_ylabel("Active pools (epoch_stake)", fontsize=11, color=DIM)
    ax.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax.set_title("Active Pool Count — Mainnet", fontsize=13, fontweight="medium", color=INK)
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    ax.set_xlim(ep[0], ep[-1])

    out2 = FIG_DIR / "pool_count_clean.png"
    fig.savefig(out2, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out2}")

    # ══════════════════════════════════════════════════════════
    # Figure 3: Delegator count — clean (epoch_stake only)
    # ══════════════════════════════════════════════════════════
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(14, 8), facecolor=BG,
        gridspec_kw={"height_ratios": [2.5, 1]}, sharex=True)

    # Top: delegation count
    ax_top.set_facecolor(BG)
    ax_top.fill_between(ep, n_deleg, color=COBALT_PULSE, alpha=0.12)
    ax_top.plot(ep, n_deleg, color=COBALT_PULSE, linewidth=2.0)
    ax_top.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:.0f}K"))
    ax_top.set_ylabel("Active delegations (epoch_stake)", fontsize=11, color=DIM)
    ax_top.set_title("Active Delegation Count — Mainnet", fontsize=13,
                      fontweight="medium", color=INK)
    ax_top.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_top.spines[sp].set_visible(False)
    ax_top.spines["left"].set_color(GRID)
    ax_top.tick_params(colors=DIM, labelsize=9)

    # Annotation at latest
    ax_top.annotate(f"{n_deleg[-1]:,} (epoch {ep[-1]})",
                    xy=(ep[-1], n_deleg[-1]),
                    xytext=(ep[-1] - 100, n_deleg[-1] + 40000),
                    fontsize=9, color=DIM,
                    arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7))

    # Bottom: epoch-over-epoch delta
    delta = np.diff(n_deleg, prepend=n_deleg[0])
    delta[0] = 0
    colors = [DELIVERED_GREEN if d >= 0 else INFARED for d in delta]

    ax_bot.set_facecolor(BG)
    ax_bot.bar(ep, delta, width=1.0, color=colors, alpha=0.65, linewidth=0)
    ax_bot.axhline(0, color=DIM, linewidth=0.5)
    ax_bot.set_ylabel("Epoch Δ delegations", fontsize=10, color=DIM)
    ax_bot.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_bot.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e3:+.1f}K" if abs(v) >= 1000 else f"{v:+.0f}"))
    ax_bot.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_bot.spines[sp].set_visible(False)
    ax_bot.spines["left"].set_color(GRID)
    ax_bot.spines["bottom"].set_color(GRID)
    ax_bot.tick_params(colors=DIM, labelsize=9)

    # Rolling average line
    window = 10
    if len(delta) > window:
        rolling = np.convolve(delta, np.ones(window)/window, mode="valid")
        ax_bot.plot(ep[window-1:], rolling, color=DAWN, linewidth=1.5, alpha=0.8,
                    label=f"{window}-epoch rolling avg")
        leg = ax_bot.legend(loc="upper left", fontsize=8, framealpha=0.9, edgecolor=GRID)
        leg.get_frame().set_linewidth(0.5)

    ax_top.set_xlim(ep[0], ep[-1])
    fig.tight_layout()
    out3 = FIG_DIR / "delegator_count_clean.png"
    fig.savefig(out3, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out3}")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"CLEAN PASS 1 — epoch_stake as single source of truth")
    print(f"{'='*60}")
    print(f"Epoch range: {ep[0]}→{ep[-1]}")
    print(f"\nSupply (epoch {ep[-1]}):")
    print(f"  Circulating:  {circulating[-1]/1e9:.2f}B ADA")
    print(f"  Staked:       {staked[-1]/1e9:.2f}B ADA ({rate_pct[-1]:.1f}%)")
    print(f"  Unstaked:     {unstaked[-1]/1e9:.2f}B ADA ({100-rate_pct[-1]:.1f}%)")
    print(f"\nPools (epoch_stake):")
    print(f"  Current:      {n_pools[-1]:,}")
    print(f"  Peak:         {n_pools[peak_idx]:,} (epoch {ep[peak_idx]})")
    print(f"\nDelegations (epoch_stake):")
    print(f"  Current:      {n_deleg[-1]:,}")
    print(f"  Peak:         {n_deleg[np.argmax(n_deleg)]:,} (epoch {ep[np.argmax(n_deleg)]})")
    print(f"  Δ last 10 ep: {n_deleg[-1] - n_deleg[-11]:+,}")
    print(f"\nNOISE REMOVED:")
    print(f"  Delegation-table 'delegators':     1,847,713  → dropped (certificate ghosts)")
    print(f"  Delegation-table 'pools':           5,919     → dropped (empty pools)")
    print(f"  Now using epoch_stake exclusively:  {n_deleg[-1]:,} delegations, {n_pools[-1]:,} pools")


if __name__ == "__main__":
    main()
