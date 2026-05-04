#!/usr/bin/env python3
"""
Experiment: side-by-side donut charts — MPO vs SPO tier composition.
Two donuts showing stake distribution by tier for each population.
"""

import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"
ENTITY_DATA = REPORT_DIR.parent.parent / "census" / "mainnet-analysis" / "data"

# ── IOG Brand colours ──
BG     = "#FFFFFF"
INK    = "#1A1A1A"
DIM    = "#666666"

INFARED      = "#E52321"
DAWN         = "#EC641D"
ACID_GREEN   = "#00B35F"
SOLAR_AMBER  = "#FFBA36"
COBALT_PULSE = "#2C4FFA"
ULTRAVIOLET  = "#A700FF"
TEAL         = "#00897B"
GREY_DARK    = "#555555"
GREY_MID     = "#AAAAAA"

# Display order: top tiers first (most interesting at 12 o'clock)
# Dormant excluded — near-zero stake inflates pool counts misleadingly
TIER_NAMES = [
    "Oversaturated", "Saturated", "Near-saturation", "Large healthy",
    "Healthy", "Sub-reliable", "Sub-block",
]
TIER_COLORS_MAP = {
    "Dormant":          GREY_DARK,
    "Sub-block":   DAWN,
    "Sub-reliable":       INFARED,
    "Healthy":          ACID_GREEN,
    "Large healthy":    TEAL,
    "Near-saturation":  SOLAR_AMBER,
    "Saturated":        COBALT_PULSE,
    "Oversaturated":    ULTRAVIOLET,
}

# Internal tier order for digitize (low→high)
TIER_INTERNAL = [
    "Dormant", "Sub-block", "Sub-reliable", "Healthy",
    "Large healthy", "Near-saturation", "Saturated", "Oversaturated",
]


def load_data():
    LOVELACE = 1_000_000
    z0 = 77_000_000
    T_bounds = [0, 100e3, 1e6, 3e6, z0*0.5, z0*0.8, z0*0.95, z0*1.05, np.inf]

    pool_entity = set()
    with open(ENTITY_DATA / "mpo_entity_pool_mapping_mainnet.csv") as f:
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
            stake = float(raw) / LOVELACE
            if stake <= 0:
                continue
            pools.append({"stake": stake, "is_mpo": row["pool_id_bech32"] in pool_entity})

    stakes = np.array([p["stake"] for p in pools])
    zones = np.digitize(stakes, T_bounds[1:])

    mpo_stake = {t: 0.0 for t in TIER_INTERNAL}
    spo_stake = {t: 0.0 for t in TIER_INTERNAL}
    mpo_pools = {t: 0 for t in TIER_INTERNAL}
    spo_pools = {t: 0 for t in TIER_INTERNAL}

    for i, p in enumerate(pools):
        t = TIER_INTERNAL[zones[i]]
        if p["is_mpo"]:
            mpo_stake[t] += p["stake"]
            mpo_pools[t] += 1
        else:
            spo_stake[t] += p["stake"]
            spo_pools[t] += 1

    # Exclude Dormant — near-zero stake inflates pool counts misleadingly
    for d in (mpo_stake, spo_stake, mpo_pools, spo_pools):
        d.pop("Dormant", None)

    return mpo_stake, spo_stake, mpo_pools, spo_pools


def _fmt_ada(v):
    if v >= 1e9:
        return f"{v/1e9:.1f}B"
    if v >= 1e6:
        return f"{v/1e6:.0f}M"
    if v >= 1e3:
        return f"{v/1e3:.0f}K"
    return f"{v:.0f}"


def draw_donut(ax, data_dict, title, subtitle_line1, subtitle_line2):
    """Draw a single donut chart on the given axes."""
    # Collect slices in display order
    sizes  = [data_dict[t] for t in TIER_NAMES]
    colors = [TIER_COLORS_MAP[t] for t in TIER_NAMES]
    total  = sum(sizes)

    # Filter zero slices
    nonzero = [(s, c, t) for s, c, t in zip(sizes, colors, TIER_NAMES) if s > 0]
    if not nonzero:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, fontsize=14, color=DIM)
        return
    sz, cl, names = zip(*nonzero)

    wedges, _ = ax.pie(
        sz, colors=cl,
        startangle=90, counterclock=False,
        wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2),
        pctdistance=0.78,
    )

    # Add labels with leader lines for slices ≥ 2%
    for wedge, s, name in zip(wedges, sz, names):
        pct = s / total * 100
        if pct < 1.5:
            continue
        ang = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.deg2rad(ang))
        y = np.sin(np.deg2rad(ang))

        # Label position outside the donut
        label_r = 1.25
        lx, ly = label_r * x, label_r * y
        ha = "left" if x >= 0 else "right"

        ada_str = _fmt_ada(s)
        lbl = f"{name}\n{ada_str} ({pct:.0f}%)"

        ax.annotate(
            lbl,
            xy=(0.82 * x, 0.82 * y),
            xytext=(lx, ly),
            ha=ha, va="center",
            fontsize=9, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=GREY_MID, lw=0.8),
            linespacing=1.4,
        )

    # Centre text
    ax.text(0, 0.06, subtitle_line1, ha="center", va="center",
            fontsize=13, fontweight="bold", color=INK)
    ax.text(0, -0.10, subtitle_line2, ha="center", va="center",
            fontsize=10, color=DIM)

    ax.set_title(title, fontsize=14, fontweight="bold", color=INK, pad=20)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    mpo_stake, spo_stake, mpo_pools, spo_pools = load_data()

    n_mpo = sum(mpo_pools.values())
    n_spo = sum(spo_pools.values())
    s_mpo = sum(mpo_stake.values())
    s_spo = sum(spo_stake.values())

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(18, 9), facecolor=BG)
    fig.patch.set_facecolor(BG)

    draw_donut(ax_l, mpo_stake,
               "MPO fleet",
               f"{_fmt_ada(s_mpo)} ADA",
               f"{n_mpo:,} pools")

    draw_donut(ax_r, spo_stake,
               "Single-pool operators",
               f"{_fmt_ada(s_spo)} ADA",
               f"{n_spo:,} pools")

    fig.suptitle(
        "Stake distribution by tier — MPO fleet vs Single-pool operators",
        fontsize=18, fontweight="bold", color=INK, y=0.97,
    )
    fig.text(0.5, 0.925,
             "Epoch 618  ·  Dormant pools excluded  ·  Where does each population's stake sit?",
             ha="center", fontsize=11, color=DIM)

    # Shared legend at bottom
    handles = [mpatches.Patch(facecolor=TIER_COLORS_MAP[t], edgecolor="white",
                               linewidth=1.5, label=t) for t in TIER_NAMES]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=9,
               frameon=False, bbox_to_anchor=(0.5, 0.02))

    fig.tight_layout(rect=[0.01, 0.07, 0.99, 0.90])
    out = FIG_DIR / "experiment_pie_mpo_vs_spo.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {out}")


if __name__ == "__main__":
    main()
