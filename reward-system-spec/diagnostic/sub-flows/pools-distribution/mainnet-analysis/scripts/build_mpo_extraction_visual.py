#!/usr/bin/env python3
"""
MPO Extraction Visual — before/after tier comparison.

Shows the full landscape with MPO pools shown as the removed hatched portion
in each tier, using the same butterfly layout as Competitive Landscape.

Output:
  figures/mpo_extraction_by_tier_mainnet.png
"""

from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"
ENTITY_DATA = REPORT_DIR.parent.parent / "census" / "mainnet-analysis" / "data"

# ── IOG Brand colours (same as filtered_landscape) ──
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

# ── Tier definitions (identical to filtered_landscape) ──
TIER_NAMES = [
    "Dormant", "Sub-block", "Sub-reliable", "Healthy",
    "Large healthy", "Near-saturation", "Saturated", "Oversaturated",
]
TIER_COLORS = [
    GREY_DARK, DAWN, INFARED, ACID_GREEN,
    TEAL, SOLAR_AMBER, COBALT_PULSE, ULTRAVIOLET,
]
NZ = len(TIER_NAMES)


def muted(hex_color, factor=0.55):
    """Blend a colour toward white."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def load_data():
    """Load pool data and classify by tier / MPO status.

    Canonical productive set = pool_stake_623.csv with stake ≥ 3M ADA.
    Production threshold = ~3M ADA (95% probability of ≥1 block per epoch,
    λ=3 in the Poisson process — POL.O3.F1).
    """
    PRODUCTIVE_THRESHOLD_ADA = 3_000_000
    z0 = 77_000_000
    T_bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95,
                z0 * 1.05, np.inf]

    pool_entity = set()
    with open(ENTITY_DATA / "mpo_entity_pool_mapping_mainnet.csv") as f:
        for row in csv.DictReader(f):
            pool_entity.add(row["pool_id_bech32"])

    pools = []
    with open(ENTITY_DATA / "pool_stake_623.csv") as f:
        for row in csv.DictReader(f):
            stake_ada = float(row["total_ada"])
            if stake_ada < PRODUCTIVE_THRESHOLD_ADA:
                continue
            is_mpo = row["pool_id"] in pool_entity
            pools.append({"stake": stake_ada, "is_mpo": is_mpo})

    stakes = np.array([p["stake"] for p in pools])
    zone_id = np.digitize(stakes, T_bounds[1:])
    n = len(pools)
    total = stakes.sum()

    # Build per-tier pool/stake counts split by SPO vs MPO
    counts      = [0] * NZ
    spo_counts  = [0] * NZ
    mpo_counts  = [0] * NZ
    tier_stake   = [0.0] * NZ
    spo_stake    = [0.0] * NZ
    mpo_stake    = [0.0] * NZ

    for i, p in enumerate(pools):
        t = zone_id[i]
        counts[t] += 1
        tier_stake[t] += p["stake"]
        if p["is_mpo"]:
            mpo_counts[t] += 1
            mpo_stake[t] += p["stake"]
        else:
            spo_counts[t] += 1
            spo_stake[t] += p["stake"]

    return {
        "n": n, "total": total, "z0": z0,
        "counts": counts, "spo_counts": spo_counts, "mpo_counts": mpo_counts,
        "tier_stake": tier_stake, "spo_stake": spo_stake, "mpo_stake": mpo_stake,
        "n_mpo_total": sum(mpo_counts),
    }


# ───────────────────────────────────────────────────────────────────────────
# draw_butterfly — copied from build_filtered_landscape_visual.py and adapted
# to show SPO (solid) + MPO (hatched) instead of incentive-stance stacking.
# ───────────────────────────────────────────────────────────────────────────

def draw_butterfly(data, fig_path):
    """Draw the butterfly chart — identical layout to Competitive Landscape."""

    n       = data["n"]
    total   = data["total"]
    z0      = data["z0"]
    counts  = data["counts"]
    n_mpo   = data["n_mpo_total"]

    spo_c  = np.array(data["spo_counts"], dtype=float)
    mpo_c  = np.array(data["mpo_counts"], dtype=float)
    spo_s  = np.array(data["spo_stake"])
    mpo_s  = np.array(data["mpo_stake"])

    pct_pools_spo = spo_c / n * 100 if n else spo_c
    pct_pools_mpo = mpo_c / n * 100 if n else mpo_c
    pct_pools     = (spo_c + mpo_c) / n * 100 if n else spo_c

    pct_stake_spo = spo_s / total * 100 if total else spo_s
    pct_stake_mpo = mpo_s / total * 100 if total else mpo_s
    pct_stake     = pct_stake_spo + pct_stake_mpo

    T_bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95,
                z0 * 1.05, np.inf]

    # Threshold markers — same as reference
    threshold_after = {
        2: ("Production\nthreshold",   "3M ADA",  INFARED),
        6: ("Saturation\nthreshold", f"{z0/1e6:.0f}M ADA", ULTRAVIOLET),
    }

    # ── Figure — same dimensions & gridspec as reference ──
    fig = plt.figure(figsize=(18, 8.5), facecolor=BG)
    gs = fig.add_gridspec(1, 3, width_ratios=[5, 4, 7],
                          left=0.03, right=0.97, top=0.82, bottom=0.06,
                          wspace=0.0)
    ax_l = fig.add_subplot(gs[0])
    ax_m = fig.add_subplot(gs[1])
    ax_r = fig.add_subplot(gs[2])

    for ax in (ax_l, ax_m, ax_r):
        ax.set_facecolor(BG)
        for sp in ax.spines.values():
            sp.set_visible(False)

    y_pos = np.arange(NZ)
    bar_h = 0.62

    # ── Left panel — pool count % (SPO solid + MPO hatched) ──
    for i in range(NZ):
        col = TIER_COLORS[i]
        # SPO solid segment
        ax_l.barh(y_pos[i], pct_pools_spo[i], height=bar_h,
                  color=col, alpha=0.88, align="center")
        # MPO hatched segment stacked after SPO
        if pct_pools_mpo[i] > 0:
            ax_l.barh(y_pos[i], pct_pools_mpo[i], height=bar_h,
                      left=pct_pools_spo[i],
                      color=muted(col), alpha=0.88, align="center",
                      edgecolor="white", hatch="///", linewidth=0.5)

        # Label — "total → SPO (−X%)" showing extraction effect
        pp = pct_pools[i]
        full_cnt = counts[i]
        spo_cnt = int(spo_c[i])
        mpo_cnt = int(mpo_c[i])
        if full_cnt == 0:
            continue
        drop = f"−{mpo_cnt}" if mpo_cnt > 0 else ""
        if mpo_cnt > 0:
            lbl = f"{full_cnt:,} → {spo_cnt:,}  ({drop})"
        else:
            lbl = f"{full_cnt:,}"
        margin = 2.0
        ax_l.text(pp + margin, y_pos[i], lbl, va="center", ha="right",
                  fontsize=8.5, color=INK, fontweight="bold")

    max_pool_pct = max(pct_pools) * 1.18 if n else 10
    ax_l.set_xlim(max_pool_pct, 0)
    ax_l.set_ylim(-0.6, NZ - 0.4)
    ax_l.set_yticks([])
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.set_xlabel("Share of pools (%)", fontsize=10, color=DIM, labelpad=6)
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Right panel — stake % (SPO solid + MPO hatched, stacked) ──
    for i in range(NZ):
        col = TIER_COLORS[i]
        ax_r.barh(y_pos[i], pct_stake_spo[i], height=bar_h,
                  color=col, alpha=0.88, align="center", zorder=3)
        if pct_stake_mpo[i] > 0:
            ax_r.barh(y_pos[i], pct_stake_mpo[i], height=bar_h,
                      left=pct_stake_spo[i],
                      color=muted(col), alpha=0.88, align="center",
                      edgecolor="white", hatch="///", linewidth=0.5, zorder=3)

        # Label — "full_ada → spo_ada (−X%)" showing extraction effect
        total_pct = pct_stake[i]
        full_ada = data["tier_stake"][i]
        spo_ada_i = spo_s[i]
        mpo_ada_i = mpo_s[i]
        if full_ada <= 0:
            continue

        def _fmt_ada(v):
            if v >= 1e9:
                return f"{v/1e9:.1f}B"
            if v >= 1e6:
                return f"{v/1e6:.0f}M"
            if v >= 1e3:
                return f"{v/1e3:.0f}K"
            return f"{v:.0f}"

        if mpo_ada_i > 0 and total_pct >= 0.3:
            drop_pct = mpo_ada_i / full_ada * 100
            lbl = (f"{_fmt_ada(full_ada)} → {_fmt_ada(spo_ada_i)}"
                   f"  (−{drop_pct:.0f}%)")
        elif total_pct >= 0.3:
            lbl = f"{_fmt_ada(full_ada)}"
        elif total_pct > 0:
            lbl = "< 0.1%"
        else:
            lbl = ""
        if lbl:
            x_lbl = max(total_pct, 0.15) + 0.35
            ax_r.text(x_lbl, y_pos[i], lbl, va="center", ha="left",
                      fontsize=8.5, color=INK, fontweight="bold")

    max_stake_pct = max(pct_stake) * 1.25 if n else 10
    ax_r.set_xlim(0, max_stake_pct)
    ax_r.set_ylim(-0.6, NZ - 0.4)
    ax_r.set_yticks([])
    ax_r.xaxis.tick_top()
    ax_r.xaxis.set_label_position("top")
    ax_r.set_xlabel("Share of stake (%) — hatched = MPO removed",
                    fontsize=10, color=DIM, labelpad=6)
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Middle panel — tier names + ADA ranges + thresholds ──
    ax_m.set_xlim(0, 1)
    ax_m.set_ylim(-0.6, NZ - 0.4)
    ax_m.set_yticks([])
    ax_m.set_xticks([])

    for i, name in enumerate(TIER_NAMES):
        ax_m.text(0.04, y_pos[i], name, va="center", ha="left",
                  fontsize=10, color=INK, fontweight="bold")
        lo, hi = T_bounds[i], T_bounds[i + 1]
        lo_s = f"{lo/1e6:.0f}M" if lo >= 1e6 else (
               f"{lo/1e3:.0f}K" if lo > 0 else "0")
        hi_s = (f"{hi/1e6:.0f}M" if hi < np.inf and hi >= 1e6
                else (f"{hi/1e3:.0f}K" if hi < 1e6 else "∞"))
        ax_m.text(0.04, y_pos[i] - 0.26, f"{lo_s} – {hi_s} ADA",
                  va="center", ha="left", fontsize=7.5, color=DIM)

    for tier_idx, (t_name, t_detail, t_col) in threshold_after.items():
        y_sep = tier_idx + 0.5
        for ax in (ax_l, ax_r):
            ax.axhline(y_sep, color=t_col, linewidth=1.5,
                       linestyle="--", alpha=0.7, zorder=5)
        ax_m.axhline(y_sep, color=t_col, linewidth=1.5,
                     linestyle="--", alpha=0.7, zorder=5)
        ax_m.text(0.5, y_sep + 0.03, f"▲ {t_name}  {t_detail}",
                  va="bottom", ha="center", fontsize=7.5,
                  color=t_col, fontweight="bold", style="italic")

    # ── Legend ──
    spo_patch = mpatches.Patch(facecolor=ACID_GREEN, alpha=0.88,
                                label="Single-pool operators (remain)")
    mpo_patch = mpatches.Patch(facecolor=muted(ACID_GREEN), alpha=0.88,
                                hatch="///", edgecolor="white", linewidth=0.5,
                                label="MPO pools (removed)")
    ax_r.legend(handles=[spo_patch, mpo_patch], loc="lower right",
                fontsize=8, framealpha=0.95, title="Population segment",
                title_fontsize=9)

    # ── Titles ──
    title = "MPO Extraction Effect — Full Landscape vs Single-Pool Operators"
    subtitle = (f"Epoch 623  ·  {n:,} productive pools  ·  {total/1e9:.1f}B ADA  "
                f"·  All {n_mpo:,} attributed MPO pools removed")

    fig.text(0.5, 0.92, title,
             ha="center", va="bottom", fontsize=16, fontweight="bold", color=INK)
    fig.text(0.5, 0.895, subtitle,
             ha="center", va="top", fontsize=10, color=DIM)

    fig.savefig(fig_path, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {fig_path}")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    draw_butterfly(data, FIG_DIR / "mpo_extraction_by_tier_mainnet.png")


if __name__ == "__main__":
    main()
