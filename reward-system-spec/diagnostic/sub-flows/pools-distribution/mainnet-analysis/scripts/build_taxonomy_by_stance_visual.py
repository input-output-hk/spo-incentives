#!/usr/bin/env python3
"""
Pool Taxonomy filtered by Incentive Stance.

Same butterfly layout as three_thresholds_mainnet.png, but the right-side
stake bars are stacked by stance (Zero-pledge / Marginal / Compliant / Exemplary).
This reveals how pledge-bonus compliance distributes across the size landscape.

Outputs: figures/taxonomy_by_stance_mainnet.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
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

# Stance colours and order (same as build_mpo_archetype_figures.py)
STANCE_COLORS = {
    "exemplary":     "#06FF89",
    "compliant":     "#16E9D8",
    "marginal":      "#FFBA36",
    "non_compliant": "#E52321",
}
STANCE_LABELS = {
    "exemplary":     "Exemplary (≥80%)",
    "compliant":     "Compliant (30–80%)",
    "marginal":      "Marginal (2–30%)",
    "non_compliant": "Zero-pledge (<2%)",
}
# Stacking order: zero-pledge at base, exemplary on top
STANCE_STACK = ["non_compliant", "marginal", "compliant", "exemplary"]


def pf(v, d=0.0):
    if v is None:
        return d
    v = str(v).strip()
    return float(v) if v else d


def classify_stance(pledge_ratio: float) -> str:
    if pledge_ratio >= 0.80:
        return "exemplary"
    if pledge_ratio >= 0.30:
        return "compliant"
    if pledge_ratio >= 0.02:
        return "marginal"
    return "non_compliant"


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load snapshot ──
    with (DATA_DIR / "pool_distribution_snapshot.json").open() as f:
        snap = json.load(f)
    z0    = snap["z0_ada"]
    k     = snap["k"]
    epoch = snap["epoch"]

    # ── Load pool data ──
    pools = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status") != "registered":
                continue
            stake = pf(r.get("active_stake")) / 1e6  # lovelace → ADA
            pledge = pf(r.get("pledge")) / 1e6
            if stake <= 0:
                continue
            eff_pledge = min(pledge, stake)
            ratio = eff_pledge / stake if stake > 100 else 0.0
            pools.append({
                "stake": stake,
                "pledge": pledge,
                "ratio": ratio,
                "stance": classify_stance(ratio),
            })

    stakes = np.array([p["stake"] for p in pools])
    total  = stakes.sum()
    n      = len(pools)

    # ── Tier definitions ──
    T_bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95, z0 * 1.05, np.inf]

    tier_names = [
        "Dormant", "Sub-block", "Sub-reliable", "Healthy",
        "Large healthy", "Near-saturation", "Saturated", "Oversaturated",
    ]
    tier_colors = [
        GREY_DARK, DAWN, INFARED, ACID_GREEN,
        TEAL, SOLAR_AMBER, COBALT_PULSE, ULTRAVIOLET,
    ]
    NZ = len(tier_names)

    # Classify each pool into a tier
    stake_arr = np.array([p["stake"] for p in pools])
    zone_id = np.digitize(stake_arr, T_bounds[1:])  # 0 … NZ-1

    # Per-tier pool counts
    counts = [int((zone_id == i).sum()) for i in range(NZ)]
    pct_pools = [c / n * 100 for c in counts]

    # Per-tier per-stance stake sums
    tier_stance_stake = defaultdict(lambda: defaultdict(float))
    tier_stake_total = defaultdict(float)
    for i, p in enumerate(pools):
        t = zone_id[i]
        tier_stance_stake[t][p["stance"]] += p["stake"]
        tier_stake_total[t] += p["stake"]

    # Per-tier per-stance pool counts
    tier_stance_count = defaultdict(lambda: defaultdict(int))
    for i, p in enumerate(pools):
        t = zone_id[i]
        tier_stance_count[t][p["stance"]] += 1

    # Convert to % of total staked
    pct_stake_by_stance = {}
    for t in range(NZ):
        pct_stake_by_stance[t] = {}
        for s in STANCE_STACK:
            pct_stake_by_stance[t][s] = tier_stance_stake[t][s] / total * 100

    # ── Threshold markers ──
    threshold_after = {
        2: ("Production\nthreshold",   "3M ADA",  INFARED),
        6: ("Saturation\nthreshold", f"{z0/1e6:.0f}M ADA", ULTRAVIOLET),
    }

    # ── Figure layout ──
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

    # ── Left panel — pool count % (same as original, colored by tier) ──
    for i, (yp, pp, col) in enumerate(zip(y_pos, pct_pools, tier_colors)):
        ax_l.barh(yp, pp, height=bar_h, color=col, alpha=0.88, align="center")
        lbl = f"{counts[i]:,}  ({pp:.0f}%)" if pp >= 1 else (
              f"{counts[i]}" if counts[i] > 0 else "")
        if lbl:
            if pp >= 15:
                ax_l.text(pp / 2, yp, lbl, va="center", ha="center",
                          fontsize=8.5, color=BG, fontweight="bold")
            else:
                margin = 2.0
                ax_l.text(pp + margin, yp, lbl, va="center", ha="right",
                          fontsize=8.5, color=INK, fontweight="bold")

    max_pool_pct = max(pct_pools) * 1.18
    ax_l.set_xlim(max_pool_pct, 0)
    ax_l.set_ylim(-0.6, NZ - 0.4)
    ax_l.set_yticks([])
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.set_xlabel("Share of all pools (%)", fontsize=10, color=DIM, labelpad=6)
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Right panel — stake % stacked by stance ──
    max_stake_pct = max(sum(pct_stake_by_stance[t][s] for s in STANCE_STACK) for t in range(NZ))

    for i in range(NZ):
        left = 0.0
        for s in STANCE_STACK:
            w = pct_stake_by_stance[i][s]
            if w > 0:
                ax_r.barh(y_pos[i], w, left=left, height=bar_h,
                         color=STANCE_COLORS[s], alpha=0.88, align="center", zorder=3)
            left += w

        # Total label
        total_pct = sum(pct_stake_by_stance[i][s] for s in STANCE_STACK)
        total_ada = tier_stake_total[i]
        if total_pct >= 2:
            lbl = f"{total_ada/1e9:.1f}B  ({total_pct:.1f}%)"
        elif total_pct >= 0.3:
            lbl = f"{total_ada/1e6:.0f}M  ({total_pct:.1f}%)"
        elif total_pct > 0:
            lbl = "< 0.1%"
        else:
            lbl = ""
        if lbl:
            x_lbl = max(total_pct, 0.15) + 0.35
            ax_r.text(x_lbl, y_pos[i], lbl, va="center", ha="left",
                      fontsize=8.5, color=INK, fontweight="bold")

    ax_r.set_xlim(0, max_stake_pct * 1.25)
    ax_r.set_ylim(-0.6, NZ - 0.4)
    ax_r.set_yticks([])
    ax_r.xaxis.tick_top()
    ax_r.xaxis.set_label_position("top")
    ax_r.set_xlabel("Share of staked supply (%) — coloured by incentive stance", fontsize=10, color=DIM, labelpad=6)
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Middle panel — tier labels & thresholds ──
    ax_m.set_xlim(0, 1)
    ax_m.set_ylim(-0.6, NZ - 0.4)
    ax_m.set_yticks([])
    ax_m.set_xticks([])

    for i, (yp, name) in enumerate(zip(y_pos, tier_names)):
        ax_m.text(0.04, yp, name, va="center", ha="left",
                  fontsize=10, color=INK, fontweight="bold")
        lo = T_bounds[i]
        hi = T_bounds[i + 1]
        lo_s = f"{lo/1e6:.0f}M" if lo >= 1e6 else (f"{lo/1e3:.0f}K" if lo > 0 else "0")
        hi_s = (f"{hi/1e6:.0f}M" if hi < np.inf and hi >= 1e6
                else (f"{hi/1e3:.0f}K" if hi < 1e6 else "∞"))
        ax_m.text(0.04, yp - 0.26, f"{lo_s} – {hi_s} ADA",
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

    # ── Stance legend ──
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=STANCE_COLORS[s], alpha=0.88, label=STANCE_LABELS[s])
        for s in reversed(STANCE_STACK)
    ]
    ax_r.legend(handles=legend_elements, loc="lower right",
                fontsize=8.5, framealpha=0.95, title="Incentive stance",
                title_fontsize=9)

    # ── Titles ──
    fig.text(0.5, 0.92,
             "Pool Taxonomy by Incentive Stance",
             ha="center", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.5, 0.88,
             f"{n:,} pools with active stake  ·  {total/1e9:.2f}B ADA  "
             f"·  z₀ = {z0/1e6:.0f}M ADA  ·  k = {k}  ·  epoch {epoch}",
             ha="center", fontsize=10.5, color=DIM)

    # ── Insight footer ──
    # Compute zero-pledge share of viable+ stake
    viable_plus = [p for p in pools if p["stake"] >= 3e6]
    nc_viable = sum(p["stake"] for p in viable_plus if p["stance"] == "non_compliant")
    total_viable = sum(p["stake"] for p in viable_plus)
    nc_pct = nc_viable / total_viable * 100 if total_viable > 0 else 0

    marginal_total = sum(p["stake"] for p in pools if p["stance"] == "marginal" and p["stake"] > 100)
    marginal_count = sum(1 for p in pools if p["stance"] == "marginal" and p["stake"] > 100)

    fig.text(0.5, 0.015,
             f"Zero-pledge pools hold {nc_pct:.0f}% of viable-and-above stake. "
             f"The marginal class — {marginal_count} pools, {marginal_total/1e9:.1f}B ADA — "
             f"is the target population for incentive-parameter adjustments.",
             ha="center", fontsize=9.5, color=INFARED,
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3CD",
                       edgecolor=SOLAR_AMBER, alpha=0.95))

    out = FIG_DIR / "taxonomy_by_stance_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓  {out.name}")


if __name__ == "__main__":
    main()
