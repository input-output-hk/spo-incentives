#!/usr/bin/env python3
"""
§3 — Pool Operators + §4 — Delegators.

Reads:
  data/pool_operator_type.csv        (current SPO/MPO classification)
  data/delegator_pool_count_per_epoch.csv  (active delegators & pools per epoch)
  data/staking_per_epoch.csv         (total staked, delegation_count, pool_count from epoch_stake)

Outputs:
  figures/operator_census_mainnet.png    (§3: pool count over time + SPO/MPO summary)
  figures/delegator_census_mainnet.png   (§4: delegator count + growth rate)
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
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"


def load_csv(path):
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load data ──
    deleg_pool = load_csv(DATA_DIR / "delegator_pool_count_per_epoch.csv")
    staking    = load_csv(DATA_DIR / "staking_per_epoch.csv")
    operators  = load_csv(DATA_DIR / "pool_operator_type.csv")

    # Time-series from delegation-table reconstruction
    dp_epochs = [int(r["epoch_no"]) for r in deleg_pool]
    dp_delegators = [int(r["active_delegators"]) for r in deleg_pool]
    dp_pools  = [int(r["active_pools"]) for r in deleg_pool]

    # Time-series from epoch_stake (different count method, includes stake amounts)
    st_epochs = [int(r["epoch_no"]) for r in staking]
    st_pools  = [int(r["pool_count"]) for r in staking]
    st_deleg  = [int(r["delegation_count"]) for r in staking]

    # SPO/MPO current snapshot
    spo_count = sum(1 for r in operators if r["op_type"] == "SPO")
    mpo_count = sum(1 for r in operators if r["op_type"] == "MPO")
    mpo_entities = len(set(
        tuple(sorted([r2["pool_hash_id"] for r2 in operators
                       if r2["pools_in_entity"] == r["pools_in_entity"]
                       and r2["op_type"] == "MPO"]))
        for r in operators if r["op_type"] == "MPO"
    ))
    # Proper entity count: group by pools_in_entity value → doesn't work.
    # Instead, count unique entity groups
    entity_sizes = {}
    for r in operators:
        if r["op_type"] == "MPO":
            n = int(r["pools_in_entity"])
            entity_sizes[n] = entity_sizes.get(n, 0) + 1
    # entity_sizes: {2: 138, 3: 18, 4: 4, 5: 5} → entities: 138/2=69, 18/3=6, 4/4=1, 5/5=1 = 77
    total_mpo_entities = sum(count // size for size, count in entity_sizes.items())

    # ════════════════════════════════════════════════════════════
    # Figure 1: Pool operator census
    # ════════════════════════════════════════════════════════════
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(14, 9), facecolor=BG,
        gridspec_kw={"height_ratios": [2, 1]}, sharex=True
    )

    # Top: active pool count over time (two sources)
    ax_top.set_facecolor(BG)
    ax_top.plot(dp_epochs, dp_pools, color=ULTRAVIOLET, linewidth=1.8,
                label=f"Active pools — delegation table ({dp_pools[-1]:,})")
    ax_top.plot(st_epochs, st_pools, color=ELECTRIC_BLUE, linewidth=1.2,
                linestyle="--", alpha=0.7,
                label=f"Active pools — epoch_stake ({st_pools[-1]:,})")

    # Peak annotation
    peak_idx = np.argmax(dp_pools)
    ax_top.annotate(f"Peak: {dp_pools[peak_idx]:,} pools (epoch {dp_epochs[peak_idx]})",
                    xy=(dp_epochs[peak_idx], dp_pools[peak_idx]),
                    xytext=(dp_epochs[peak_idx] - 60, dp_pools[peak_idx] + 200),
                    fontsize=8, color=DIM,
                    arrowprops=dict(arrowstyle="->", color=DIM, lw=0.8))

    ax_top.set_ylabel("Active pools", fontsize=11, color=DIM)
    ax_top.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_top.spines[sp].set_visible(False)
    ax_top.spines["left"].set_color(GRID)
    ax_top.tick_params(colors=DIM, labelsize=9)
    leg = ax_top.legend(loc="upper left", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Bottom: SPO/MPO snapshot as text + entity size distribution bar
    ax_bot.set_facecolor(BG)
    ax_bot.axis("off")

    # Summary text
    summary_lines = [
        f"Current snapshot (epoch {dp_epochs[-1]})",
        f"",
        f"Total registered pools: {spo_count + mpo_count:,}",
        f"  Single-pool operators (SPO):  {spo_count:,}  ({spo_count/(spo_count+mpo_count)*100:.1f}%)",
        f"  Multi-pool operators (MPO):   {mpo_count:,} pools across {total_mpo_entities} entities ({mpo_count/(spo_count+mpo_count)*100:.1f}%)",
        f"",
        f"MPO entity breakdown:",
    ]
    for size in sorted(entity_sizes.keys()):
        n_entities = entity_sizes[size] // size
        summary_lines.append(f"    {n_entities} entit{'y' if n_entities == 1 else 'ies'} running {size} pools each ({entity_sizes[size]} pools)")

    text = "\n".join(summary_lines)
    ax_bot.text(0.03, 0.95, text, transform=ax_bot.transAxes,
                fontsize=10, fontfamily="monospace", color=INK,
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8F8F8",
                          edgecolor=GRID, linewidth=0.5))

    ax_top.set_xlim(min(dp_epochs), max(dp_epochs))
    fig.tight_layout()
    out_path = FIG_DIR / "operator_census_mainnet.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out_path}")

    # ════════════════════════════════════════════════════════════
    # Figure 2: Delegator census
    # ════════════════════════════════════════════════════════════
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 9), facecolor=BG,
        gridspec_kw={"height_ratios": [2, 1]}, sharex=True
    )

    # Top: delegator count over time
    ax1.set_facecolor(BG)
    ax1.fill_between(dp_epochs, dp_delegators, color=COBALT_PULSE, alpha=0.15)
    ax1.plot(dp_epochs, dp_delegators, color=COBALT_PULSE, linewidth=1.8,
             label=f"Active delegators — delegation table ({dp_delegators[-1]:,})")
    ax1.plot(st_epochs, st_deleg, color=DELIVERED_GREEN, linewidth=1.2,
             linestyle="--", alpha=0.7,
             label=f"Active delegations — epoch_stake ({st_deleg[-1]:,})")

    ax1.set_ylabel("Active delegators", fontsize=11, color=DIM)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"))
    ax1.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax1.spines[sp].set_visible(False)
    ax1.spines["left"].set_color(GRID)
    ax1.tick_params(colors=DIM, labelsize=9)
    leg1 = ax1.legend(loc="upper left", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg1.get_frame().set_linewidth(0.5)

    # Peak and latest annotations
    peak_idx = np.argmax(dp_delegators)
    ax1.annotate(f"Peak: {dp_delegators[peak_idx]:,} (epoch {dp_epochs[peak_idx]})",
                 xy=(dp_epochs[peak_idx], dp_delegators[peak_idx]),
                 xytext=(dp_epochs[peak_idx] - 80, dp_delegators[peak_idx] + 50000),
                 fontsize=8, color=DIM,
                 arrowprops=dict(arrowstyle="->", color=DIM, lw=0.8))

    # Bottom: epoch-over-epoch growth rate (delegation table)
    growth = [0] + [dp_delegators[i] - dp_delegators[i-1] for i in range(1, len(dp_delegators))]
    colors = [DELIVERED_GREEN if g >= 0 else INFARED for g in growth]

    ax2.set_facecolor(BG)
    ax2.bar(dp_epochs, growth, width=1.0, color=colors, alpha=0.7, linewidth=0)
    ax2.axhline(0, color=DIM, linewidth=0.5)
    ax2.set_ylabel("Epoch-over-epoch Δ", fontsize=10, color=DIM)
    ax2.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e3:+.0f}K" if abs(v) >= 1000 else f"{v:+.0f}"))
    ax2.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.spines["left"].set_color(GRID)
    ax2.spines["bottom"].set_color(GRID)
    ax2.tick_params(colors=DIM, labelsize=9)

    ax1.set_xlim(min(dp_epochs), max(dp_epochs))
    fig.tight_layout()
    out_path = FIG_DIR / "delegator_census_mainnet.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out_path}")

    # Summary stats
    print(f"\nOperator summary:")
    print(f"  SPO: {spo_count:,} pools  |  MPO: {mpo_count:,} pools ({total_mpo_entities} entities)")
    print(f"  Peak active pools: {max(dp_pools):,} (epoch {dp_epochs[np.argmax(dp_pools)]})")
    print(f"  Current active pools: {dp_pools[-1]:,}")
    print(f"\nDelegator summary:")
    print(f"  Peak: {max(dp_delegators):,} (epoch {dp_epochs[np.argmax(dp_delegators)]})")
    print(f"  Current: {dp_delegators[-1]:,}")
    print(f"  Net change last 10 epochs: {dp_delegators[-1] - dp_delegators[-11]:+,}")


if __name__ == "__main__":
    main()
