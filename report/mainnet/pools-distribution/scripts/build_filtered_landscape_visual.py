#!/usr/bin/env python3
"""
Pool Landscape excluding Non-Compliant MPOs.

Produces TWO butterfly charts:
  1. filtered_landscape_spo_only_mainnet.png  — SPOs only (all MPOs removed)
  2. filtered_landscape_mainnet.png           — SPOs + compliant/exemplary MPOs
     (hatched bars distinguish compliant MPOs from independent SPOs)

Also emits summary CSVs for both variants.

Outputs:
  figures/filtered_landscape_spo_only_mainnet.png
  figures/filtered_landscape_mainnet.png
  data/filtered_landscape_spo_only_summary.csv
  data/filtered_landscape_summary.csv
"""

from __future__ import annotations

import csv
import json
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
    "non_compliant": "Non-compliant (<2%)",
}
STANCE_STACK = ["non_compliant", "marginal", "compliant", "exemplary"]

# Segment colours — darker shades for MPO pools
SEG_COLORS = {
    "spo_exemplary":     "#06FF89",
    "spo_compliant":     "#16E9D8",
    "spo_marginal":      "#FFBA36",
    "spo_non_compliant": "#E52321",
    "mpo_exemplary":     "#048A4E",
    "mpo_compliant":     "#0E8A7A",
    "mpo_marginal":      "#C08A1A",
}
SEG_STACK = [
    "spo_non_compliant", "spo_marginal", "spo_compliant", "spo_exemplary",
    "mpo_marginal", "mpo_compliant", "mpo_exemplary",
]


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


# ── Tier definitions (shared) ──
TIER_NAMES = [
    "Dormant", "Sub-production", "Sub-viable", "Healthy",
    "Large healthy", "Near-saturation", "Saturated", "Oversaturated",
]
TIER_COLORS = [
    GREY_DARK, DAWN, INFARED, ACID_GREEN,
    TEAL, SOLAR_AMBER, COBALT_PULSE, ULTRAVIOLET,
]
NZ = len(TIER_NAMES)


def draw_butterfly(pools, z0, epoch, title, subtitle, fig_path,
                   show_mpo_hatch=False):
    """Draw the butterfly chart for a given pool subset."""

    stakes = np.array([p["stake"] for p in pools])
    total  = stakes.sum()
    n      = len(pools)

    T_bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95,
                z0 * 1.05, np.inf]

    stake_arr = np.array([p["stake"] for p in pools])
    zone_id   = np.digitize(stake_arr, T_bounds[1:])

    counts   = [int((zone_id == i).sum()) for i in range(NZ)]
    pct_pools = [c / n * 100 if n else 0 for c in counts]

    # Per-tier stake by stance or segment
    tier_stake_total = defaultdict(float)
    if show_mpo_hatch:
        tier_seg_stake = defaultdict(lambda: defaultdict(float))
        for i, p in enumerate(pools):
            t = zone_id[i]
            tier_seg_stake[t][p["segment"]] += p["stake"]
            tier_stake_total[t] += p["stake"]
        stack_keys = SEG_STACK
        pct_stake = {}
        for t in range(NZ):
            pct_stake[t] = {}
            for s in stack_keys:
                pct_stake[t][s] = tier_seg_stake[t][s] / total * 100 if total else 0
    else:
        tier_stance_stake = defaultdict(lambda: defaultdict(float))
        for i, p in enumerate(pools):
            t = zone_id[i]
            tier_stance_stake[t][p["stance"]] += p["stake"]
            tier_stake_total[t] += p["stake"]
        stack_keys = STANCE_STACK
        pct_stake = {}
        for t in range(NZ):
            pct_stake[t] = {}
            for s in stack_keys:
                pct_stake[t][s] = tier_stance_stake[t][s] / total * 100 if total else 0

    # Threshold markers
    threshold_after = {
        1: ("Production\nthreshold",  "1M ADA",  DAWN),
        2: ("Viability\nthreshold",   "3M ADA",  INFARED),
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

    # ── Left panel — pool count % ──
    for i, (yp, pp, col) in enumerate(zip(y_pos, pct_pools, TIER_COLORS)):
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

    max_pool_pct = max(pct_pools) * 1.18 if pct_pools else 10
    ax_l.set_xlim(max_pool_pct, 0)
    ax_l.set_ylim(-0.6, NZ - 0.4)
    ax_l.set_yticks([])
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.set_xlabel("Share of pools (%)", fontsize=10, color=DIM, labelpad=6)
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Right panel — stake % stacked ──
    max_stake_pct = max(
        sum(pct_stake[t][s] for s in stack_keys) for t in range(NZ)
    ) if n else 10

    for i in range(NZ):
        left = 0.0
        for s in stack_keys:
            w = pct_stake[i][s]
            if w > 0:
                if show_mpo_hatch and s.startswith("mpo"):
                    ax_r.barh(y_pos[i], w, left=left, height=bar_h,
                             color=SEG_COLORS[s], alpha=0.88, align="center",
                             edgecolor="white", hatch="///", linewidth=0.5,
                             zorder=3)
                else:
                    col = SEG_COLORS.get(s, STANCE_COLORS.get(s, "#888"))
                    ax_r.barh(y_pos[i], w, left=left, height=bar_h,
                             color=col, alpha=0.88, align="center", zorder=3)
            left += w

        total_pct = sum(pct_stake[i][s] for s in stack_keys)
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
    xlabel_r = ("Share of stake (%) — hatched = compliant MPO"
                if show_mpo_hatch else "Share of stake (%) — by incentive stance")
    ax_r.set_xlabel(xlabel_r, fontsize=10, color=DIM, labelpad=6)
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    # ── Middle panel ──
    ax_m.set_xlim(0, 1)
    ax_m.set_ylim(-0.6, NZ - 0.4)
    ax_m.set_yticks([])
    ax_m.set_xticks([])

    for i, (yp, name) in enumerate(zip(y_pos, TIER_NAMES)):
        ax_m.text(0.04, yp, name, va="center", ha="left",
                  fontsize=10, color=INK, fontweight="bold")
        lo, hi = T_bounds[i], T_bounds[i + 1]
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

    # ── Legend ──
    legend_elements = []
    for st in reversed(STANCE_STACK):
        legend_elements.append(
            mpatches.Patch(facecolor=STANCE_COLORS[st], alpha=0.88,
                           label=STANCE_LABELS[st])
        )
    if show_mpo_hatch:
        legend_elements.append(
            mpatches.Patch(facecolor="#0E8A7A", alpha=0.88, hatch="///",
                           edgecolor="white", linewidth=0.5,
                           label="Compliant MPO (hatched)")
        )
    ax_r.legend(handles=legend_elements, loc="lower right",
                fontsize=8, framealpha=0.95, title="Population segment",
                title_fontsize=9)

    # ── Titles ──
    fig.text(0.5, 0.92, title,
             ha="center", va="bottom", fontsize=16, fontweight="bold", color=INK)
    fig.text(0.5, 0.895, subtitle,
             ha="center", va="top", fontsize=10, color=DIM)

    fig.savefig(fig_path, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {fig_path}")


def write_summary_csv(pools, z0, csv_path, show_mpo=False):
    """Write per-tier summary CSV."""
    stakes = np.array([p["stake"] for p in pools])
    total  = stakes.sum()
    T_bounds = [0, 100e3, 1e6, 3e6, z0*0.5, z0*0.8, z0*0.95, z0*1.05, np.inf]
    zone_id = np.digitize(stakes, T_bounds[1:])

    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        cols = ["tier", "pools", "stake_b_ada", "pct_stake",
                "exemplary_pct", "compliant_pct", "marginal_pct", "non_compliant_pct"]
        if show_mpo:
            cols += ["spo_pools", "spo_stake_b", "mpo_pools", "mpo_stake_b"]
        w.writerow(cols)

        for t in range(NZ):
            mask = zone_id == t
            tier_pools = [p for i, p in enumerate(pools) if mask[i]]
            cnt = len(tier_pools)
            ts  = sum(p["stake"] for p in tier_pools)
            row = [
                TIER_NAMES[t], cnt, f"{ts/1e9:.3f}", f"{ts/total*100:.1f}" if total else "0",
            ]
            for st in ["exemplary", "compliant", "marginal", "non_compliant"]:
                ss = sum(p["stake"] for p in tier_pools if p["stance"] == st)
                row.append(f"{ss/ts*100:.1f}" if ts > 0 else "0")
            if show_mpo:
                spo = [p for p in tier_pools if not p["is_mpo"]]
                mpo = [p for p in tier_pools if p["is_mpo"]]
                row += [len(spo), f"{sum(p['stake'] for p in spo)/1e9:.3f}",
                        len(mpo), f"{sum(p['stake'] for p in mpo)/1e9:.3f}"]
            w.writerow(row)
    print(f"✓ Saved {csv_path}")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load snapshot ──
    with (DATA_DIR / "pool_distribution_snapshot.json").open() as f:
        snap = json.load(f)
    z0, epoch = snap["z0_ada"], snap["epoch"]

    # ── Load MPO data ──
    archetypes = {}
    with (DATA_DIR / "mpo_entity_archetypes.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            archetypes[r["entity_id"]] = r

    mpo_pool_entity = {}
    with (DATA_DIR / "mpo_entity_pool_mapping_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            mpo_pool_entity[r["pool_id_bech32"]] = r["entity_id"]

    mpo_pool_stance = {}
    with (DATA_DIR / "mpo_entity_pool_health_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            pid = r["pool_id_bech32"]
            stake = pf(r.get("current_active_stake_ada"))
            pledge = pf(r.get("declared_pledge_ada"))
            ratio = min(pledge, stake) / stake if stake > 100 else 0.0
            mpo_pool_stance[pid] = classify_stance(ratio)

    non_compliant_entities = {
        eid for eid, a in archetypes.items()
        if a.get("incentive_alignment") == "none"
    }

    # Classify every MPO pool
    nc_mpo_pools = set()      # non-compliant MPO pools (to exclude)
    compliant_mpo_pools = set()  # compliant/exemplary MPO pools (to keep & tag)
    all_mpo_pools = set()     # all MPO pools
    for pid, eid in mpo_pool_entity.items():
        all_mpo_pools.add(pid)
        if eid in non_compliant_entities:
            nc_mpo_pools.add(pid)
        else:
            stance = mpo_pool_stance.get(pid, "non_compliant")
            if stance == "non_compliant":
                nc_mpo_pools.add(pid)
            else:
                compliant_mpo_pools.add(pid)

    # ── Load all registered pools with stake ──
    all_pools = []
    with (DATA_DIR / "koios_pool_list_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pool_status") != "registered":
                continue
            pid   = r["pool_id_bech32"]
            stake = pf(r.get("active_stake")) / 1e6
            pledge = pf(r.get("pledge")) / 1e6
            if stake <= 0:
                continue
            eff_pledge = min(pledge, stake)
            ratio  = eff_pledge / stake if stake > 100 else 0.0
            stance = classify_stance(ratio)
            is_any_mpo = pid in all_mpo_pools
            is_compliant_mpo = pid in compliant_mpo_pools
            is_nc_mpo = pid in nc_mpo_pools
            seg = f"mpo_{stance}" if is_compliant_mpo else f"spo_{stance}"
            all_pools.append({
                "pool_id": pid,
                "stake": stake,
                "pledge": pledge,
                "ratio": ratio,
                "stance": stance,
                "is_mpo": is_compliant_mpo,
                "is_any_mpo": is_any_mpo,
                "is_nc_mpo": is_nc_mpo,
                "segment": seg,
            })

    # ── Variant 1: SPO-only (no MPOs at all) ──
    spo_only = [p for p in all_pools if not p["is_any_mpo"]]
    n1 = len(spo_only)
    s1 = sum(p["stake"] for p in spo_only)
    print("=" * 60)
    print(f"VARIANT 1 — SPO ONLY (all MPOs removed)")
    print(f"  Pools: {n1:,}  Stake: {s1/1e9:.2f}B ADA")
    for st in STANCE_STACK:
        sp = [p for p in spo_only if p["stance"] == st]
        print(f"    {st}: {len(sp)} pools, "
              f"{sum(p['stake'] for p in sp)/1e9:.2f}B ({sum(p['stake'] for p in sp)/s1*100:.1f}%)")
    print()

    draw_butterfly(
        spo_only, z0, epoch,
        title="Pool Landscape — Independent SPOs Only",
        subtitle=(f"Epoch {epoch}  ·  {n1:,} pools  ·  {s1/1e9:.1f}B ADA  "
                  f"·  All {len(all_mpo_pools):,} attributed MPO pools removed"),
        fig_path=FIG_DIR / "filtered_landscape_spo_only_mainnet.png",
        show_mpo_hatch=False,
    )
    write_summary_csv(spo_only, z0,
                      DATA_DIR / "filtered_landscape_spo_only_summary.csv",
                      show_mpo=False)

    # ── Variant 2: SPOs + compliant MPOs (non-compliant MPOs removed) ──
    with_compliant = [p for p in all_pools if not p["is_nc_mpo"]]
    n2 = len(with_compliant)
    s2 = sum(p["stake"] for p in with_compliant)
    n_mpo = sum(1 for p in with_compliant if p["is_mpo"])
    s_mpo = sum(p["stake"] for p in with_compliant if p["is_mpo"])
    print("=" * 60)
    print(f"VARIANT 2 — SPOs + COMPLIANT MPOs (non-compliant MPOs removed)")
    print(f"  Pools: {n2:,}  Stake: {s2/1e9:.2f}B ADA")
    print(f"    SPO: {n2 - n_mpo}  stake: {(s2-s_mpo)/1e9:.2f}B")
    print(f"    Compliant MPO: {n_mpo}  stake: {s_mpo/1e9:.2f}B")
    for st in STANCE_STACK:
        sp = [p for p in with_compliant if p["stance"] == st]
        print(f"    {st}: {len(sp)} pools, "
              f"{sum(p['stake'] for p in sp)/1e9:.2f}B ({sum(p['stake'] for p in sp)/s2*100:.1f}%)")
    print()

    draw_butterfly(
        with_compliant, z0, epoch,
        title="Pool Landscape — Excluding Non-Compliant MPOs",
        subtitle=(f"Epoch {epoch}  ·  {n2:,} pools  ·  {s2/1e9:.1f}B ADA  "
                  f"·  {len(nc_mpo_pools):,} non-compliant MPO pools removed  "
                  f"·  {n_mpo} compliant MPO pools retained (hatched)"),
        fig_path=FIG_DIR / "filtered_landscape_mainnet.png",
        show_mpo_hatch=True,
    )
    write_summary_csv(with_compliant, z0,
                      DATA_DIR / "filtered_landscape_summary.csv",
                      show_mpo=True)


if __name__ == "__main__":
    main()
