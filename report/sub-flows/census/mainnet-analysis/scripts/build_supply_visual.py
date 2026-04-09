#!/usr/bin/env python3
"""
§1 — ADA Supply Decomposition + §2 — Staking Rate.

Reads:
  data/supply_decomposition.csv  (from ada_pots)
  data/staking_per_epoch.csv     (from epoch_stake aggregate)

Outputs:
  figures/supply_decomposition_mainnet.png
  figures/staking_rate_mainnet.png
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
GREY_PARTIC     = "#B0B0B0"
ACID_GREEN      = "#06FF89"

LOVELACE = 1e6  # lovelace per ADA
BILLION  = 1e9


def load_csv(path):
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({k: float(v) if k != "epoch_no" else int(v)
                         for k, v in r.items()})
    return rows


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    supply = load_csv(DATA_DIR / "supply_decomposition.csv")

    epochs     = [r["epoch_no"] for r in supply]
    reserve    = [r["reserve"] / LOVELACE / BILLION for r in supply]
    treasury   = [r["treasury"] / LOVELACE / BILLION for r in supply]
    circulating= [r["circulating"] / LOVELACE / BILLION for r in supply]
    total      = [r + t + c for r, t, c in zip(reserve, treasury, circulating)]

    # ── Figure 1: Supply decomposition stacked area ──
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    ax.set_facecolor(BG)

    ax.stackplot(epochs,
                 [circulating, treasury, reserve],
                 labels=[
                     f"Circulating ({circulating[-1]:.1f}B)",
                     f"Treasury ({treasury[-1]:.1f}B)",
                     f"Reserve ({reserve[-1]:.1f}B)",
                 ],
                 colors=[DELIVERED_GREEN, SOLAR_AMBER, GREY_PARTIC],
                 alpha=0.85, linewidth=0)

    # Max supply line
    ax.axhline(45, color=DIM, linewidth=1, linestyle=":", alpha=0.5)
    ax.text(epochs[-1] + 2, 45.1, "Max supply: 45B", fontsize=8,
            color=DIM, va="bottom", ha="right")

    ax.set_xlim(min(epochs), max(epochs))
    ax.set_ylim(0, 48)
    ax.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax.set_ylabel("ADA (billions)", fontsize=11, color=DIM)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}B"))
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)

    leg = ax.legend(loc="center right", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "supply_decomposition_mainnet.png",
                dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {FIG_DIR / 'supply_decomposition_mainnet.png'}")

    # ── Figure 2: Staking rate ──
    staking_file = DATA_DIR / "staking_per_epoch.csv"
    if not staking_file.exists():
        print(f"⏳ {staking_file.name} not ready yet — skipping staking rate visual")
        return

    staking = load_csv(staking_file)

    # Build supply lookup
    supply_map = {r["epoch_no"]: r["circulating"] / LOVELACE for r in supply}

    st_epochs = [r["epoch_no"] for r in staking if r["epoch_no"] in supply_map]
    st_staked = [r["total_staked"] / LOVELACE / BILLION for r in staking if r["epoch_no"] in supply_map]
    st_circ   = [supply_map[r["epoch_no"]] / BILLION for r in staking if r["epoch_no"] in supply_map]
    st_unstaked = [c - s for c, s in zip(st_circ, st_staked)]
    st_rate   = [s / c * 100 for s, c in zip(st_staked, st_circ)]
    st_deleg  = [r["delegation_count"] for r in staking if r["epoch_no"] in supply_map]
    st_pools  = [r["pool_count"] for r in staking if r["epoch_no"] in supply_map]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), facecolor=BG,
                                    gridspec_kw={"height_ratios": [2, 1]},
                                    sharex=True)

    # Top: staked vs unstaked
    ax1.set_facecolor(BG)
    ax1.stackplot(st_epochs,
                  [st_staked, st_unstaked],
                  labels=[
                      f"Staked ({st_staked[-1]:.1f}B)",
                      f"Unstaked ({st_unstaked[-1]:.1f}B)",
                  ],
                  colors=[DELIVERED_GREEN, GREY_PARTIC],
                  alpha=0.85, linewidth=0)
    ax1.set_ylabel("ADA (billions)", fontsize=11, color=DIM)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}B"))
    ax1.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax1.spines[sp].set_visible(False)
    ax1.spines["left"].set_color(GRID)
    ax1.tick_params(colors=DIM, labelsize=9)
    leg1 = ax1.legend(loc="center right", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg1.get_frame().set_linewidth(0.5)

    # Right-axis: staking rate %
    ax1r = ax1.twinx()
    ax1r.plot(st_epochs, st_rate, color=INFARED, linewidth=1.5, alpha=0.8, label="Staking rate")
    ax1r.set_ylabel("Staking rate (%)", fontsize=10, color=INFARED)
    ax1r.set_ylim(0, 100)
    ax1r.tick_params(colors=INFARED, labelsize=8)
    ax1r.spines["right"].set_color(INFARED)
    ax1r.spines["top"].set_visible(False)

    # Bottom: delegation count + pool count
    ax2.set_facecolor(BG)
    ax2.plot(st_epochs, [d / 1e6 for d in st_deleg], color=ELECTRIC_BLUE,
             linewidth=1.5, label=f"Delegations ({st_deleg[-1]/1e6:.2f}M)")
    ax2.set_ylabel("Delegations (millions)", fontsize=10, color=ELECTRIC_BLUE)
    ax2.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax2.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.spines["left"].set_color(GRID)
    ax2.spines["bottom"].set_color(GRID)
    ax2.tick_params(colors=DIM, labelsize=9)

    ax2r = ax2.twinx()
    ax2r.plot(st_epochs, st_pools, color=ULTRAVIOLET, linewidth=1.5, alpha=0.8,
              label=f"Pools ({int(st_pools[-1])})")
    ax2r.set_ylabel("Active pools", fontsize=10, color=ULTRAVIOLET)
    ax2r.tick_params(colors=ULTRAVIOLET, labelsize=8)
    ax2r.spines["right"].set_color(ULTRAVIOLET)
    ax2r.spines["top"].set_visible(False)

    # Legends
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2r.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
               fontsize=8.5, framealpha=0.95, edgecolor=GRID)

    ax1.set_xlim(min(st_epochs), max(st_epochs))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "staking_rate_mainnet.png",
                dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {FIG_DIR / 'staking_rate_mainnet.png'}")

    # Print summary
    print(f"\nSummary (epoch {st_epochs[-1]}):")
    print(f"  Circulating: {st_circ[-1]:.2f}B ADA")
    print(f"  Staked:      {st_staked[-1]:.2f}B ADA ({st_rate[-1]:.1f}%)")
    print(f"  Unstaked:    {st_unstaked[-1]:.2f}B ADA ({100-st_rate[-1]:.1f}%)")
    print(f"  Delegations: {st_deleg[-1]:,.0f}")
    print(f"  Pools:       {int(st_pools[-1])}")


if __name__ == "__main__":
    main()
