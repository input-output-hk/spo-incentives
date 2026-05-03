#!/usr/bin/env python3
"""
MPO Pool Taxonomy by Pledge Compliance.

Same butterfly layout as taxonomy_by_stance_mainnet.png but filtered to
the pools belonging to attributed MPO entities only.

Outputs: figures/mpo_taxonomy_by_stance_mainnet.png
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
ENTITY_DATA = REPORT_DIR.parent.parent / "census" / "mainnet-analysis" / "data"

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

# Stance
STANCE_COLORS = {
    "cant_play":     "#8C6D1F",
    "exemplary":     "#06FF89",
    "compliant":     "#16E9D8",
    "marginal":      "#FFBA36",
    "non_compliant": "#E52321",
}
STANCE_LABELS = {
    "cant_play":     "Can't play (sub-saturation)",
    "exemplary":     "Exemplary (≥80%)",
    "compliant":     "Compliant (30–80%)",
    "marginal":      "Marginal (2–30%)",
    "non_compliant": "Zero-pledge (<2%)",
}
STANCE_STACK = ["cant_play", "non_compliant", "marginal", "compliant", "exemplary"]


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

    with (DATA_DIR / "pool_distribution_snapshot.json").open() as f:
        snap = json.load(f)
    z0    = snap["z0_ada"]
    epoch = snap["epoch"]

    # ── Canonical productive set ──
    # Production threshold = ~3M ADA (95% probability of ≥1 block per epoch,
    # λ=3 in the Poisson process). Per-pool stake is sourced from the e623
    # snapshot (pool_stake_623.csv). Pledge is still pulled from koios since
    # it's a registration parameter that doesn't drift epoch-to-epoch.
    PRODUCTIVE_THRESHOLD_ADA = 3_000_000

    pool_stake_e623 = {}
    with (ENTITY_DATA / "pool_stake_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            ada = float(r["total_ada"])
            if ada >= PRODUCTIVE_THRESHOLD_ADA:
                pool_stake_e623[r["pool_id"]] = ada
    productive_total = sum(pool_stake_e623.values())

    archetype_meta = {
        r["entity_id"]: r
        for r in csv.DictReader((ENTITY_DATA / "mpo_entity_archetypes.csv").open(newline=""))
    }
    if "BIGLAZY" in archetype_meta:
        alias = dict(archetype_meta["BIGLAZY"])
        alias["entity_id"] = "BIGLAZYCAT"
        archetype_meta["BIGLAZYCAT"] = alias

    # Load MPO pool IDs
    pool_to_entity = {
        r["pool_id_bech32"]: r["entity_id"]
        for r in csv.DictReader((ENTITY_DATA / "mpo_entity_pool_mapping_mainnet.csv").open(newline=""))
    }
    mpo_pool_ids = set(pool_to_entity)

    # Pull pledge from koios pool list for the join
    koios_pledge = {}
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status") != "registered":
                continue
            koios_pledge[r["pool_id_bech32"]] = pf(r.get("pledge")) / 1e6

    # Build productive MPO pool list (stake from epoch 623, pledge from koios)
    pools = []
    entity_ids = set()
    for pool_id, entity_id in pool_to_entity.items():
        stake = pool_stake_e623.get(pool_id)
        if stake is None:
            continue  # not productive at epoch 623
        entity_ids.add(entity_id)
        pledge = koios_pledge.get(pool_id, 0.0)
        eff_pledge = min(pledge, stake)
        ratio = eff_pledge / stake if stake > 100 else 0.0
        capital_class = archetype_meta.get(entity_id, {}).get("capital_class", "sufficient")
        pools.append({
            "stake": stake,
            "ratio": ratio,
            "stance": "cant_play" if capital_class != "sufficient" else classify_stance(ratio),
        })

    # Denominator for stake-share is the productive total (matches Census F2/F7).
    total_staked = productive_total

    stakes_arr = np.array([p["stake"] for p in pools])
    total_mpo = stakes_arr.sum()
    n = len(pools)

    # Tier definitions
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

    zone_id = np.digitize(stakes_arr, T_bounds[1:])

    counts = [int((zone_id == i).sum()) for i in range(NZ)]
    pct_pools = [c / n * 100 if n > 0 else 0 for c in counts]

    # Per-tier per-stance stake
    tier_stance_stake = defaultdict(lambda: defaultdict(float))
    tier_stake_total = defaultdict(float)
    for i, p in enumerate(pools):
        t = zone_id[i]
        tier_stance_stake[t][p["stance"]] += p["stake"]
        tier_stake_total[t] += p["stake"]

    # Use staked supply as denominator (not just MPO total)
    pct_stake_by_stance = {}
    for t in range(NZ):
        pct_stake_by_stance[t] = {}
        for s in STANCE_STACK:
            pct_stake_by_stance[t][s] = tier_stance_stake[t][s] / total_staked * 100

    threshold_after = {
        2: ("Production\nthreshold",   "3M ADA",  INFARED),
        6: ("Saturation\nthreshold", f"{z0/1e6:.0f}M ADA", ULTRAVIOLET),
    }

    # ── Figure ──
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

    # Left: pool count %
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

    max_pool_pct = max(pct_pools) * 1.18 if max(pct_pools) > 0 else 10
    ax_l.set_xlim(max_pool_pct, 0)
    ax_l.set_ylim(-0.6, NZ - 0.4)
    ax_l.set_yticks([])
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.set_xlabel("Share of MPO pools (%)", fontsize=10, color=DIM, labelpad=6)
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # Right: stake % stacked by stance (denominator = total staked supply)
    max_stake_pct = max(
        sum(pct_stake_by_stance[t][s] for s in STANCE_STACK) for t in range(NZ)
    ) if n > 0 else 10

    for i in range(NZ):
        left = 0.0
        for s in STANCE_STACK:
            w = pct_stake_by_stance[i][s]
            if w > 0:
                ax_r.barh(y_pos[i], w, left=left, height=bar_h,
                         color=STANCE_COLORS[s], alpha=0.88, align="center", zorder=3)
            left += w
        total_pct = sum(pct_stake_by_stance[i][s] for s in STANCE_STACK)
        total_ada = tier_stake_total[i]
        if total_pct >= 0.5:
            lbl = f"{total_ada/1e9:.1f}B  ({total_pct:.1f}%)"
        elif total_pct >= 0.05:
            lbl = f"{total_ada/1e6:.0f}M  ({total_pct:.1f}%)"
        elif total_pct > 0:
            lbl = "< 0.1%"
        else:
            lbl = ""
        if lbl:
            x_lbl = max(total_pct, 0.1) + 0.2
            ax_r.text(x_lbl, y_pos[i], lbl, va="center", ha="left",
                      fontsize=8.5, color=INK, fontweight="bold")

    ax_r.set_xlim(0, max_stake_pct * 1.30)
    ax_r.set_ylim(-0.6, NZ - 0.4)
    ax_r.set_yticks([])
    ax_r.xaxis.tick_top()
    ax_r.xaxis.set_label_position("top")
    ax_r.set_xlabel("Share of productive stake (%) — coloured by pledge compliance",
                    fontsize=10, color=DIM, labelpad=6)
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # Middle: tier labels
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

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=STANCE_COLORS[s], alpha=0.88, label=STANCE_LABELS[s])
        for s in reversed(STANCE_STACK)
    ]
    ax_r.legend(handles=legend_elements, loc="lower right",
                fontsize=8.5, framealpha=0.95, title="Pledge compliance",
                title_fontsize=9)

    # Title
    fig.text(0.5, 0.92,
             "MPO Pools — Pledge Compliance × Pool Tier",
             ha="center", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.5, 0.88,
             f"{n:,} productive MPO pools  ·  {total_mpo/1e9:.2f}B ADA ({total_mpo/total_staked*100:.1f}% of productive stake)  "
             f"·  {len(entity_ids)} entities  ·  epoch {epoch}",
             ha="center", fontsize=10.5, color=DIM)

    # Insight footer
    nc_viable = sum(p["stake"] for p in pools if p["stance"] == "non_compliant" and p["stake"] >= 3e6)
    viable_total = sum(
        p["stake"]
        for p in pools
        if p["stance"] != "cant_play" and p["stake"] >= 3e6
    )
    nc_pct = nc_viable / viable_total * 100 if viable_total > 0 else 0

    fig.text(0.5, 0.015,
             f"Among saturation-scale MPO pools, zero-pledge red still holds {nc_pct:.0f}% of viable-and-above stake. "
             f"Ochre isolates sub-saturation fleets that cannot fully play the saturation-scale pledge game.",
             ha="center", fontsize=9.5, color=INFARED,
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3CD",
                       edgecolor=SOLAR_AMBER, alpha=0.95))

    out = FIG_DIR / "mpo_taxonomy_by_stance_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓  {out.name}")


if __name__ == "__main__":
    main()
