#!/usr/bin/env python3
"""
Pool Taxonomy visual — tier landscape.

Two mirrored horizontal-bar panels:
  Left:  % of pools in each tier   (bars grow left)
  Right: % of stake in each tier   (bars grow right)

The juxtaposition makes the structural inversion impossible to miss.

Outputs: figures/three_thresholds_mainnet.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──────────────────────────────────────────────────
BG     = "#FFFFFF"
INK    = "#1A1A1A"
DIM    = "#666666"
GRID   = "#EBEBEB"

INFARED      = "#E52321"
DAWN         = "#EC641D"
ACID_GREEN   = "#00B35F"
SOLAR_AMBER  = "#FFBA36"
COBALT_PULSE = "#2C4FFA"
ULTRAVIOLET  = "#A700FF"
TEAL         = "#00897B"
GREY_DARK    = "#555555"


def pf(v, d=0.0):
    if v is None:
        return d
    v = str(v).strip()
    return float(v) if v else d


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load snapshot ──
    with (DATA_DIR / "pool_distribution_snapshot.json").open() as f:
        snap = json.load(f)
    z0    = snap["z0_ada"]
    k     = snap["k"]
    epoch = snap["epoch"]

    # ── Load pool stakes ──
    stakes = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status") != "registered":
                continue
            s = pf(r.get("active_stake")) / 1e6   # ADA
            if s > 0:
                stakes.append(s)

    stakes = np.array(sorted(stakes))
    total  = stakes.sum()
    n      = len(stakes)

    # ── Tier definitions ──
    # 8 non-zero tiers; boundaries in ADA (same units as stakes)
    T_bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95, z0 * 1.05, np.inf]

    tier_names = [
        "Dormant",
        "Sub-block",
        "Sub-reliable",
        "Healthy",
        "Large healthy",
        "Near-saturation",
        "Saturated",
        "Oversaturated",
    ]
    tier_colors = [
        GREY_DARK,       # Dormant
        DAWN,            # Sub-block
        INFARED,         # Sub-reliable
        ACID_GREEN,      # Healthy
        TEAL,            # Large healthy
        SOLAR_AMBER,     # Near-saturation
        COBALT_PULSE,    # Saturated
        ULTRAVIOLET,     # Oversaturated
    ]
    NZ = len(tier_names)

    # Classify pools
    zone_id = np.digitize(stakes, T_bounds[1:])  # 0 … NZ-1

    counts     = []
    stake_sums = []
    for i in range(NZ):
        m = zone_id == i
        counts.append(int(m.sum()))
        stake_sums.append(float(stakes[m].sum()))

    pct_pools = [c / n  * 100 for c in counts]
    pct_stake = [s / total * 100 for s in stake_sums]

    # ── Which tiers have the named thresholds as their upper bound ──
    # Production threshold=3M (95% prob of ≥1 block / λ=3)  →  lower bound of Healthy tier  (tier idx 2)
    # Saturation cap=z0  →  upper bound of Saturated  (tier idx 6)
    # The 1M / λ=1 line is a sub-point inside Sub-block but is not labelled —
    # we don't draw a viability line either: viability is volatile (see §4.1.2.2).
    threshold_after = {
        2: ("Production\nthreshold",   "3M ADA",  INFARED),
        6: ("Saturation\nthreshold", f"{z0/1e6:.0f}M ADA", ULTRAVIOLET),
    }

    # ── Figure layout ──────────────────────────────────────────────────
    # Tiers on y-axis (bottom = dormant, top = oversaturated)
    # Left panel:  pool-count %  (bars grow to the left, x reversed)
    # Right panel: stake %       (bars grow to the right)
    # Middle strip: tier name + colour swatch + threshold labels

    fig = plt.figure(figsize=(18, 7.5), facecolor=BG)

    # Three columns: [left bars | labels | right bars]  proportions 5:4:7
    # (right wider because stake numbers are skewed)
    gs = fig.add_gridspec(1, 3, width_ratios=[5, 4, 7],
                          left=0.03, right=0.97, top=0.85, bottom=0.06,
                          wspace=0.0)
    ax_l  = fig.add_subplot(gs[0])   # pool %  bars
    ax_m  = fig.add_subplot(gs[1])   # tier labels
    ax_r  = fig.add_subplot(gs[2])   # stake %  bars

    for ax in (ax_l, ax_m, ax_r):
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_visible(False)

    y_pos  = np.arange(NZ)
    bar_h  = 0.62

    # ── Left panel — pool count % ──────────────────────────────────────
    for i, (yp, pp, col) in enumerate(zip(y_pos, pct_pools, tier_colors)):
        ax_l.barh(yp, pp, height=bar_h, color=col, alpha=0.88, align="center")
        lbl = f"{counts[i]:,}  ({pp:.0f}%)" if pp >= 1 else (
              f"{counts[i]}" if counts[i] > 0 else "")
        if lbl:
            # Reversed x-axis (xlim = MAX→0): x=0 is the RIGHT edge, x=MAX is LEFT.
            # ha="center" at pp/2  → text centered inside bar, never reaches x=0.
            # ha="right"  at pp+m  → RIGHT edge of text at pp+m (left of bar end),
            #                        text body extends further LEFT — safe from x=0.
            # ha="left" near x=0 is WRONG: text extends toward x=0 and gets clipped.
            if pp >= 15:
                # Wide bar — center white label inside
                ax_l.text(pp / 2, yp, lbl, va="center", ha="center",
                          fontsize=8.5, color=BG, fontweight="bold")
            else:
                # Narrow/medium bar — dark label outside bar, extending leftward
                margin = 2.0
                ax_l.text(pp + margin, yp, lbl, va="center", ha="right",
                          fontsize=8.5, color=INK, fontweight="bold")

    # x-axis: reverse so bars point right→left (pool side is "mirrored")
    max_pool_pct = max(pct_pools) * 1.18
    ax_l.set_xlim(max_pool_pct, 0)
    ax_l.set_ylim(-0.6, NZ - 0.4)
    ax_l.set_yticks([])
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.set_xlabel("Share of all pools  (%)", fontsize=10, color=DIM, labelpad=6)
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Right panel — stake % ──────────────────────────────────────────
    for i, (yp, sp, col) in enumerate(zip(y_pos, pct_stake, tier_colors)):
        ax_r.barh(yp, sp, height=bar_h, color=col, alpha=0.88, align="center")
        if sp >= 2:
            lbl = f"{stake_sums[i]/1e9:.1f}B  ({sp:.1f}%)"
        elif sp >= 0.3:
            lbl = f"{stake_sums[i]/1e6:.0f}M  ({sp:.1f}%)"
        elif sp > 0:
            lbl = f"< 0.1%"   # Dormant / near-zero
        else:
            lbl = ""
        if lbl:
            if sp >= 30:
                # Wide bar — white label centered inside
                ax_r.text(sp / 2, yp, lbl, va="center", ha="center",
                          fontsize=8.5, color=BG, fontweight="bold")
            else:
                # Narrow bar — dark label just outside, extends right
                x_lbl = max(sp, 0.15) + 0.35
                ax_r.text(x_lbl, yp, lbl, va="center", ha="left",
                          fontsize=8.5, color=INK, fontweight="bold")

    ax_r.set_xlim(0, max(pct_stake) * 1.18)
    ax_r.set_ylim(-0.6, NZ - 0.4)
    ax_r.set_yticks([])
    ax_r.xaxis.tick_top()
    ax_r.xaxis.set_label_position("top")
    ax_r.set_xlabel("Share of active stake  (%)", fontsize=10, color=DIM, labelpad=6)
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Middle panel — tier labels & threshold markers ──────────────────
    ax_m.set_xlim(0, 1)
    ax_m.set_ylim(-0.6, NZ - 0.4)
    ax_m.set_yticks([])
    ax_m.set_xticks([])

    for i, (yp, name, col) in enumerate(zip(y_pos, tier_names, tier_colors)):
        # Tier name
        ax_m.text(0.04, yp, name, va="center", ha="left",
                  fontsize=10, color=INK, fontweight="bold")
        # Stake range in small grey text
        lo = T_bounds[i]
        hi = T_bounds[i + 1]
        lo_s = f"{lo/1e6:.0f}M" if lo >= 1e6 else (f"{lo/1e3:.0f}K" if lo > 0 else "0")
        hi_s = (f"{hi/1e6:.0f}M" if hi < np.inf and hi >= 1e6
                else (f"{hi/1e3:.0f}K" if hi < 1e6 else "∞"))
        ax_m.text(0.04, yp - 0.26, f"{lo_s} – {hi_s} ADA",
                  va="center", ha="left", fontsize=7.5, color=DIM)

    # Threshold separators between tiers
    for tier_idx, (t_name, t_detail, t_col) in threshold_after.items():
        # Horizontal line sits between tier_idx and tier_idx+1
        y_sep = tier_idx + 0.5
        for ax in (ax_l, ax_r):
            ax.axhline(y_sep, color=t_col, linewidth=1.5,
                       linestyle="--", alpha=0.7, zorder=5)
        ax_m.axhline(y_sep, color=t_col, linewidth=1.5,
                     linestyle="--", alpha=0.7, zorder=5)
        # Threshold label on middle panel
        ax_m.text(0.5, y_sep + 0.03, f"▲ {t_name}  {t_detail}",
                  va="bottom", ha="center", fontsize=7.5,
                  color=t_col, fontweight="bold", style="italic")

    # ── Titles ─────────────────────────────────────────────────────────
    fig.text(0.5, 0.93,
             "Pool Taxonomy: Three Thresholds Stratify the Landscape",
             ha="center", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.5, 0.895,
             f"{n:,} pools with active stake  ·  {total/1e9:.2f}B ADA  "
             f"·  z₀ = {z0/1e6:.0f}M ADA  ·  k = {k}  ·  epoch {epoch}",
             ha="center", fontsize=10.5, color=DIM)

    # ── Insight footer ──────────────────────────────────────────────────
    insight = (
        f"{sum(counts[:3]):,} pools ({sum(pct_pools[:3]):.0f}%) sit below the production threshold (3M)"
        f" — yet hold only {sum(pct_stake[:3]):.1f}% of active stake"
    )
    fig.text(0.5, 0.005, insight,
             ha="center", fontsize=10.5, fontweight="bold", color=BG,
             bbox=dict(boxstyle="round,pad=0.45",
                       fc=SOLAR_AMBER, ec="none", alpha=0.92))

    # ── Save ────────────────────────────────────────────────────────────
    out = FIG_DIR / "three_thresholds_mainnet.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
