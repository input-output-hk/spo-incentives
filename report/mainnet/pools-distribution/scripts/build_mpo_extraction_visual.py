#!/usr/bin/env python3
"""
MPO Extraction Visual — before/after tier comparison.

Shows the full landscape vs single-pool-only landscape side by side,
with MPO pools shown as the removed portion in each tier.

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

# ── IOG Brand colours ──
BG          = "#FFFFFF"
INK         = "#1A1A1A"
DIM         = "#666666"
GRID        = "#EBEBEB"
INFARED     = "#E52321"
DAWN        = "#EC641D"
ACID_GREEN  = "#00B35F"
SOLAR_AMBER = "#FFBA36"
COBALT      = "#2C4FFA"
ULTRAVIOLET = "#A700FF"
TEAL        = "#16E9D8"
GREY_DARK   = "#999999"
GREY_MID    = "#BBBBBB"

TIER_NAMES = [
    "Oversaturated", "Saturated", "Near-saturation", "Large healthy",
    "Healthy", "Sub-viable", "Sub-production", "Dormant",
]

# Colours per tier (reversed order — top-down from Oversaturated)
TIER_COLORS_MAP = {
    "Dormant":          GREY_DARK,
    "Sub-production":   DAWN,
    "Sub-viable":       INFARED,
    "Healthy":          ACID_GREEN,
    "Large healthy":    TEAL,
    "Near-saturation":  SOLAR_AMBER,
    "Saturated":        COBALT,
    "Oversaturated":    ULTRAVIOLET,
}


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
    z0 = 77_000_000
    LOVELACE = 1_000_000
    T_bounds = [0, 100, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95, z0 * 1.05, np.inf]
    TIER_ORDER = [
        "Dormant", "Sub-production", "Sub-viable", "Healthy",
        "Large healthy", "Near-saturation", "Saturated", "Oversaturated",
    ]

    pool_entity = set()
    with open(DATA_DIR / "mpo_entity_pool_mapping_mainnet.csv") as f:
        for row in csv.DictReader(f):
            pool_entity.add(row["pool_id_bech32"])

    pools = []
    with open(DATA_DIR / "koios_pool_list_mainnet.csv") as f:
        for row in csv.DictReader(f):
            if row["pool_status"] != "registered":
                continue
            raw = row["active_stake"]
            if not raw or not raw.replace(".", "").replace("-", "").isdigit():
                continue
            stake_ada = float(raw) / LOVELACE
            if stake_ada <= 0:
                continue
            is_mpo = row["pool_id_bech32"] in pool_entity
            pools.append({"stake": stake_ada, "is_mpo": is_mpo})

    stakes = np.array([p["stake"] for p in pools])
    zones = np.digitize(stakes, T_bounds[1:])

    result = {}
    for i, name in enumerate(TIER_ORDER):
        idx = [j for j in range(len(pools)) if zones[j] == i]
        fp = len(idx)
        fs = sum(pools[j]["stake"] for j in idx)
        sp = len([j for j in idx if not pools[j]["is_mpo"]])
        ss = sum(pools[j]["stake"] for j in idx if not pools[j]["is_mpo"])
        mp = fp - sp
        ms = fs - ss
        result[name] = {
            "full_pools": fp, "full_stake": fs,
            "spo_pools": sp, "spo_stake": ss,
            "mpo_pools": mp, "mpo_stake": ms,
        }
    return result


def build_figure(data):
    """
    Two-panel horizontal stacked bar chart:
      Left:  Pool count  (single-pool solid + MPO hatched)
      Right: Stake in B ADA (single-pool solid + MPO hatched)

    Top-down order: Oversaturated → Dormant (gravity = top tiers at top).
    """
    n = len(TIER_NAMES)
    fig, (ax_pools, ax_stake) = plt.subplots(
        1, 2, figsize=(16, 7.5),
        gridspec_kw={"wspace": 0.05, "left": 0.20, "right": 0.96,
                     "top": 0.80, "bottom": 0.13}
    )
    fig.patch.set_facecolor(BG)

    y = np.arange(n)
    bar_h = 0.62

    spo_p = np.array([data[t]["spo_pools"] for t in TIER_NAMES])
    mpo_p = np.array([data[t]["mpo_pools"] for t in TIER_NAMES])
    spo_s = np.array([data[t]["spo_stake"] / 1e9 for t in TIER_NAMES])
    mpo_s = np.array([data[t]["mpo_stake"] / 1e9 for t in TIER_NAMES])
    colors = [TIER_COLORS_MAP[t] for t in TIER_NAMES]
    muted_colors = [muted(TIER_COLORS_MAP[t]) for t in TIER_NAMES]

    # ── Left panel: Pool count ──
    ax_pools.set_facecolor(BG)
    ax_pools.barh(y, spo_p, height=bar_h, color=colors,
                  edgecolor="white", linewidth=0.5, zorder=3)
    ax_pools.barh(y, mpo_p, height=bar_h, left=spo_p,
                  color=muted_colors, edgecolor="white", linewidth=0.5,
                  hatch="///", zorder=3)

    for i in range(n):
        total = spo_p[i] + mpo_p[i]
        if total == 0:
            continue
        # Always place label outside right edge for clarity
        label_parts = []
        if spo_p[i] > 0:
            label_parts.append(f"{int(spo_p[i]):,}")
        if mpo_p[i] > 0:
            label_parts.append(f"+{int(mpo_p[i]):,}")
        label = "  |  ".join(label_parts) if len(label_parts) == 2 else label_parts[0]
        # Large bars: labels inside; small bars: labels outside
        if total > 100:
            if spo_p[i] > 60:
                ax_pools.text(spo_p[i] * 0.5, y[i], f"{int(spo_p[i]):,}",
                             ha="center", va="center", fontsize=8.5,
                             fontweight="bold", color="white", zorder=5)
            if mpo_p[i] > 40:
                ax_pools.text(spo_p[i] + mpo_p[i] * 0.5, y[i],
                             f"+{int(mpo_p[i]):,}",
                             ha="center", va="center", fontsize=7.5,
                             color=INK, style="italic", zorder=5)
            elif mpo_p[i] > 0:
                ax_pools.text(total + 8, y[i], f"+{int(mpo_p[i])}",
                             ha="left", va="center", fontsize=7.5,
                             color=DIM, zorder=5)
        else:
            # Small bars — all labels outside
            ax_pools.text(total + 8, y[i], label,
                         ha="left", va="center", fontsize=8,
                         color=INK, zorder=5)

    ax_pools.set_xlabel("Pool count", fontsize=10.5, color=INK, labelpad=10)
    ax_pools.set_title("Pool Count", fontsize=12.5, fontweight="bold",
                       color=INK, pad=12)

    # ── Right panel: Stake ──
    ax_stake.set_facecolor(BG)
    ax_stake.barh(y, spo_s, height=bar_h, color=colors,
                  edgecolor="white", linewidth=0.5, zorder=3)
    ax_stake.barh(y, mpo_s, height=bar_h, left=spo_s,
                  color=muted_colors, edgecolor="white", linewidth=0.5,
                  hatch="///", zorder=3)

    def fmt_stake(v):
        if v >= 1.0:
            return f"{v:.1f}B"
        if v >= 0.01:
            return f"{v:.2f}B"
        if v >= 0.001:
            return f"{v:.3f}B"
        return f"{v * 1000:.1f}M"

    for i in range(n):
        total_s = spo_s[i] + mpo_s[i]
        if total_s < 0.0001:
            continue
        # Large bars: labels inside; small bars: labels outside
        if total_s > 0.5:
            if spo_s[i] > 0.25:
                ax_stake.text(spo_s[i] * 0.5, y[i], fmt_stake(spo_s[i]),
                             ha="center", va="center", fontsize=8.5,
                             fontweight="bold", color="white", zorder=5)
            if mpo_s[i] > 0.4:
                ax_stake.text(spo_s[i] + mpo_s[i] * 0.5, y[i],
                             f"+{fmt_stake(mpo_s[i])}",
                             ha="center", va="center", fontsize=7.5,
                             color=INK, style="italic", zorder=5)
            elif mpo_s[i] > 0.005:
                ax_stake.text(total_s + 0.08, y[i],
                             f"+{fmt_stake(mpo_s[i])}",
                             ha="left", va="center", fontsize=7.5,
                             color=DIM, zorder=5)
        else:
            # Small bars — all labels outside
            parts = []
            if spo_s[i] > 0.0001:
                parts.append(fmt_stake(spo_s[i]))
            if mpo_s[i] > 0.0001:
                parts.append(f"+{fmt_stake(mpo_s[i])}")
            label = "  |  ".join(parts) if len(parts) == 2 else (parts[0] if parts else "")
            ax_stake.text(total_s + 0.08, y[i], label,
                         ha="left", va="center", fontsize=8,
                         color=INK, zorder=5)

    ax_stake.set_xlabel("Stake (B ADA)", fontsize=10.5, color=INK, labelpad=10)
    ax_stake.set_title("Stake", fontsize=12.5, fontweight="bold",
                       color=INK, pad=12)

    # ── Shared formatting ──
    for ax in (ax_pools, ax_stake):
        ax.set_yticks(y)
        ax.set_ylim(-0.5, n - 0.5)
        ax.invert_yaxis()
        ax.grid(axis="x", color=GRID, linewidth=0.5, zorder=0)
        ax.tick_params(axis="both", colors=INK, labelsize=9.5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        # Ensure x-axis has room for outside labels
        xmax = ax.get_xlim()[1]
        ax.set_xlim(right=xmax * 1.25)

    # Tier labels on left axis — include MPO % in parentheses
    tier_labels = []
    for t in TIER_NAMES:
        pct = data[t]["mpo_pools"] / data[t]["full_pools"] * 100 if data[t]["full_pools"] > 0 else 0
        tier_labels.append(f"{t}  ({pct:.0f}% MPO)")
    ax_pools.set_yticklabels(tier_labels, fontsize=10, fontweight="bold", color=INK)
    ax_stake.set_yticklabels([""] * n)

    # Viability threshold line (between Healthy idx=4 and Sub-viable idx=5 in TIER_NAMES)
    via_y = 4.5
    for ax in (ax_pools, ax_stake):
        ax.axhline(via_y, color=INFARED, linewidth=1.8, linestyle="--",
                   alpha=0.8, zorder=4)

    # Place viability label in the stake panel (more room there)
    # With inverted y-axis, "above" the line visually = smaller y value
    ax_stake.text(ax_stake.get_xlim()[0] + 0.02, via_y - 0.25,
                  "VIABILITY THRESHOLD  (3 M ADA)",
                  ha="left", va="bottom", fontsize=8, color=INFARED,
                  fontweight="bold", fontstyle="italic")

    # ── Legend ──
    spo_patch = mpatches.Patch(facecolor=ACID_GREEN, edgecolor="white",
                               label="Single-pool operators  (remain)")
    mpo_patch = mpatches.Patch(facecolor=muted(ACID_GREEN), edgecolor=DIM,
                               hatch="///",
                               label="Multi-pool operator pools  (removed by attribution)")
    fig.legend(handles=[spo_patch, mpo_patch], loc="lower center",
               ncol=2, fontsize=10, frameon=False,
               bbox_to_anchor=(0.55, 0.01))

    # ── Summary box at top ──
    viable_tiers = ["Healthy", "Large healthy", "Near-saturation",
                    "Saturated", "Oversaturated"]
    full_v_p = sum(data[t]["full_pools"] for t in viable_tiers)
    spo_v_p  = sum(data[t]["spo_pools"]  for t in viable_tiers)
    full_v_s = sum(data[t]["full_stake"]  for t in viable_tiers) / 1e9
    spo_v_s  = sum(data[t]["spo_stake"]   for t in viable_tiers) / 1e9

    lines = [
        f"Viable+ pools:  {full_v_p:,}  \u2192  {spo_v_p:,}   "
        f"(\u2212{full_v_p - spo_v_p:,} pools,  \u2212{(full_v_p - spo_v_p) / full_v_p * 100:.0f}%)",
        f"Viable+ stake:  {full_v_s:.1f} B  \u2192  {spo_v_s:.1f} B ADA   "
        f"(\u2212{full_v_s - spo_v_s:.1f} B,  \u2212{(full_v_s - spo_v_s) / full_v_s * 100:.0f}%)",
    ]
    summary = "\n".join(lines)
    fig.text(0.55, 0.96, summary, ha="center", va="top",
             fontsize=10, color=INK, fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#F7F7F7",
                       edgecolor="#DDDDDD", linewidth=0.8))

    fig.suptitle(
        "MPO Extraction Effect \u2014 Full Landscape vs Single-Pool Operators",
        fontsize=14, fontweight="bold", color=INK, y=1.01,
    )

    return fig


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    fig = build_figure(data)
    out = FIG_DIR / "mpo_extraction_by_tier_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
