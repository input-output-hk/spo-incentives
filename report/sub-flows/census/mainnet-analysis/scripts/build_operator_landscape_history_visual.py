#!/usr/bin/env python3
"""
§2.4 historical — Operator landscape evolution.

Reads:
  data/operator_landscape_history.csv   (output of 03_operator_landscape_history.sql)

If the SQL output is not yet available, falls back to
  data/staking_per_epoch.csv
and estimates the productive / sub-threshold split using the known
epoch-623 ratios (productive_pools/total_pools ≈ 33.1%, but
productive_stake/total_stake ≈ 99.1%).  The fallback produces a
structurally correct chart with approximate values — rerun after the
SQL export for exact numbers.

Outputs:
  figures/operator_landscape_history.png
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ──
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
ULTRAVIOLET     = "#A700FF"
SOLAR_AMBER     = "#FFBA36"
GREY_LIGHT      = "#B0B0B0"
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"

LOVELACE = 1e6


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def load_exact():
    """Load the SQL-exported per-epoch decomposition."""
    rows = load_csv(DATA_DIR / "operator_landscape_history.csv")
    epochs = []
    total_pools = []
    total_staked = []
    prod_pools = []
    prod_stake = []
    sub_pools = []
    sub_stake = []
    threshold = []
    for r in rows:
        e = int(r["epoch_no"])
        if e < 211:
            continue
        epochs.append(e)
        total_pools.append(int(r["total_pools"]))
        total_staked.append(int(r["total_staked"]) / LOVELACE)
        prod_pools.append(int(r["productive_pools"]))
        prod_stake.append(int(r["productive_stake"]) / LOVELACE)
        sub_pools.append(int(r["subthreshold_pools"]))
        sub_stake.append(int(r["subthreshold_stake"]) / LOVELACE)
        threshold.append(int(r["production_threshold"]) / LOVELACE)
    return (
        np.array(epochs),
        np.array(total_pools), np.array(total_staked),
        np.array(prod_pools), np.array(prod_stake),
        np.array(sub_pools), np.array(sub_stake),
        np.array(threshold),
    )


def load_estimated():
    """
    Fallback: estimate from staking_per_epoch.csv.
    Uses the production threshold formula and the known epoch-623 ratio
    of productive-pools-share (~33%) to approximate the split.
    """
    rows = load_csv(DATA_DIR / "staking_per_epoch.csv")
    epochs = []
    total_pools = []
    total_staked = []
    prod_pools = []
    prod_stake = []
    sub_pools = []
    sub_stake = []
    threshold = []

    # Known anchor: epoch 623
    # 951 productive / 2877 total = 33.06% of pools
    # 21.57B productive / 21.75B total = 99.14% of stake
    ANCHOR_POOL_RATIO = 951 / 2877
    ANCHOR_STAKE_RATIO = 0.9914

    for r in rows:
        e = int(r["epoch_no"])
        if e < 211:
            continue
        tp = int(r["pool_count"])
        ts = int(r["total_staked"]) / LOVELACE
        thr = ts / 21600  # ADA

        # Estimate productive pool count.
        # Early epochs had fewer pools and higher average stake per pool,
        # so the productive fraction was higher. Use a simple model:
        # productive_ratio approaches ANCHOR_POOL_RATIO as pool count grows.
        # When pools < k (500), almost all are productive.
        k = 500
        if tp <= k:
            pr = min(0.95, 1.0)
        else:
            # Linear interpolation: at k pools -> ~90%, at 3160 (peak) -> ~30%
            pr = max(ANCHOR_POOL_RATIO, 1.0 - 0.7 * (tp - k) / (3160 - k))

        pp = int(round(tp * pr))
        # Productive stake is always the vast majority
        sr = min(0.999, ANCHOR_STAKE_RATIO + (1 - ANCHOR_STAKE_RATIO) * (1 - pr))
        ps = ts * sr

        epochs.append(e)
        total_pools.append(tp)
        total_staked.append(ts)
        prod_pools.append(pp)
        prod_stake.append(ps)
        sub_pools.append(tp - pp)
        sub_stake.append(ts - ps)
        threshold.append(thr)

    return (
        np.array(epochs),
        np.array(total_pools), np.array(total_staked),
        np.array(prod_pools), np.array(prod_stake),
        np.array(sub_pools), np.array(sub_stake),
        np.array(threshold),
    )


def plot(epochs, total_pools, total_staked,
         prod_pools, prod_stake,
         sub_pools, sub_stake,
         threshold, estimated=False):

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), facecolor=BG,
                              gridspec_kw={"height_ratios": [1, 1]},
                              sharex=True)
    ax_stake, ax_pools = axes

    # ── Top panel: staked ADA — productive vs sub-threshold ──
    ax_stake.set_facecolor(BG)
    ax_stake.stackplot(
        epochs,
        prod_stake / 1e9,
        sub_stake / 1e9,
        colors=[DELIVERED_GREEN, GREY_LIGHT],
        alpha=0.6,
        labels=["Productive stake (above threshold)", "Sub-threshold stake"],
    )
    ax_stake.plot(epochs, total_staked / 1e9, color=INK, linewidth=0.8,
                  linestyle=":", alpha=0.4, label="Total staked")

    # Threshold on secondary axis
    ax_thr = ax_stake.twinx()
    ax_thr.plot(epochs, threshold / 1e6, color=INFARED, linewidth=1.4,
                alpha=0.8, label="Production threshold")
    ax_thr.set_ylabel("Threshold (M ADA)", fontsize=10, color=INFARED)
    ax_thr.tick_params(axis="y", colors=INFARED, labelsize=9)
    ax_thr.spines["right"].set_color(INFARED)
    ax_thr.spines["right"].set_alpha(0.3)
    for sp in ["top", "left"]:
        ax_thr.spines[sp].set_visible(False)

    ax_stake.set_ylabel("Staked ADA (billions)", fontsize=11, color=DIM)
    ax_stake.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_stake.spines[sp].set_visible(False)
    ax_stake.spines["left"].set_color(GRID)
    ax_stake.tick_params(colors=DIM, labelsize=9)

    # Merged legend
    h1, l1 = ax_stake.get_legend_handles_labels()
    h2, l2 = ax_thr.get_legend_handles_labels()
    leg = ax_stake.legend(h1 + h2, l1 + l2, loc="upper left",
                          fontsize=8.5, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Latest-epoch annotation
    last_e = epochs[-1]
    last_ps = prod_stake[-1] / 1e9
    last_ts = total_staked[-1] / 1e9
    pct = prod_stake[-1] / total_staked[-1] * 100
    ax_stake.annotate(
        f"Epoch {last_e}: {last_ps:.2f}B productive / {last_ts:.2f}B total ({pct:.1f}%)",
        xy=(last_e, last_ps),
        xytext=(last_e - 140, last_ps - 3),
        fontsize=8, color=DIM,
        arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7),
    )

    # ── Bottom panel: pool counts — productive vs sub-threshold ──
    ax_pools.set_facecolor(BG)
    ax_pools.stackplot(
        epochs,
        prod_pools,
        sub_pools,
        colors=[COBALT_PULSE, SOLAR_AMBER],
        alpha=0.6,
        labels=[
            f"Productive pools ({prod_pools[-1]:,})",
            f"Sub-threshold pools ({sub_pools[-1]:,})",
        ],
    )
    ax_pools.plot(epochs, total_pools, color=INK, linewidth=0.8,
                  linestyle=":", alpha=0.4, label=f"Total pools ({total_pools[-1]:,})")

    # k=500 reference line
    ax_pools.axhline(500, color=INFARED, linewidth=0.9, linestyle="--", alpha=0.5)
    ax_pools.text(epochs[5], 530, "k = 500", fontsize=8, color=INFARED, alpha=0.7)

    # Productive share on secondary axis
    ax_pct = ax_pools.twinx()
    prod_share = prod_pools / total_pools * 100
    ax_pct.plot(epochs, prod_share, color=ULTRAVIOLET, linewidth=1.4, alpha=0.8,
                label="Productive pool share (%)")
    ax_pct.set_ylabel("Productive share (%)", fontsize=10, color=ULTRAVIOLET)
    ax_pct.tick_params(axis="y", colors=ULTRAVIOLET, labelsize=9)
    ax_pct.set_ylim(0, 100)
    ax_pct.spines["right"].set_color(ULTRAVIOLET)
    ax_pct.spines["right"].set_alpha(0.3)
    for sp in ["top", "left"]:
        ax_pct.spines[sp].set_visible(False)

    ax_pools.set_ylabel("Pool count", fontsize=11, color=DIM)
    ax_pools.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_pools.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_pools.spines[sp].set_visible(False)
    ax_pools.spines["left"].set_color(GRID)
    ax_pools.spines["bottom"].set_color(GRID)
    ax_pools.tick_params(colors=DIM, labelsize=9)

    h3, l3 = ax_pools.get_legend_handles_labels()
    h4, l4 = ax_pct.get_legend_handles_labels()
    leg2 = ax_pools.legend(h3 + h4, l3 + l4, loc="upper left",
                            fontsize=8.5, framealpha=0.95, edgecolor=GRID)
    leg2.get_frame().set_linewidth(0.5)

    ax_stake.set_xlim(epochs[0], epochs[-1])

    suffix = " (estimated)" if estimated else ""
    fig.suptitle(
        f"Operator Landscape — Historical Decomposition{suffix}",
        fontsize=14, fontweight="medium", color=INK, y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out = FIG_DIR / "operator_landscape_history.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")
    if estimated:
        print("  ⚠  Using estimated split (staking_per_epoch fallback).")
        print("     Rerun after 03_operator_landscape_history.sql for exact values.")


def main():
    exact_path = DATA_DIR / "operator_landscape_history.csv"
    if exact_path.exists():
        print("Loading exact SQL output …")
        data = load_exact()
        plot(*data, estimated=False)
    else:
        print("SQL output not found — falling back to estimation …")
        data = load_estimated()
        plot(*data, estimated=True)


if __name__ == "__main__":
    main()
