#!/usr/bin/env python3
"""
Pool Landscape excluding Non-Compliant MPOs.

Produces TWO butterfly charts:
  1. filtered_landscape_spo_only_mainnet.png  — current independent SPO basket
  2. filtered_landscape_mainnet.png           — current filtered basket
     (independent SPOs + retained MPO pools; hatched bars distinguish retained MPOs)
  3. filtered_landscape_history_mainnet.png   — historical evolution of those
     same current baskets, with stance reconstructed from pool update history

Also emits summary CSVs for both variants.

Outputs:
  figures/filtered_landscape_spo_only_mainnet.png
  figures/filtered_landscape_mainnet.png
  figures/filtered_landscape_history_mainnet.png
  data/filtered_landscape_spo_only_summary.csv
  data/filtered_landscape_summary.csv
  data/filtered_landscape_history_key_epochs.csv
"""

from __future__ import annotations

import bisect
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

IMA_END_EPOCH = 583  # Incentive Mechanism Analysis (Lopez de Lara, 2025)
KEY_EPOCHS = [210, 250, 400, 410, 548, 583, 615]


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


def load_mpo_filter_sets():
    """Return current MPO pool sets used by the section-5 filter."""
    archetypes = {}
    with (ENTITY_DATA / "mpo_entity_archetypes.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            archetypes[r["entity_id"]] = r

    mpo_pool_entity = {}
    with (ENTITY_DATA / "mpo_entity_pool_mapping_mainnet.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            mpo_pool_entity[r["pool_id_bech32"]] = r["entity_id"]

    mpo_pool_stance = {}
    with (ENTITY_DATA / "mpo_entity_pool_health_mainnet.csv").open(newline="") as f:
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

    nc_mpo_pools = set()
    retained_mpo_pools = set()
    all_mpo_pools = set()
    for pid, eid in mpo_pool_entity.items():
        all_mpo_pools.add(pid)
        if eid in non_compliant_entities:
            nc_mpo_pools.add(pid)
        else:
            stance = mpo_pool_stance.get(pid, "non_compliant")
            if stance == "non_compliant":
                nc_mpo_pools.add(pid)
            else:
                retained_mpo_pools.add(pid)

    return all_mpo_pools, nc_mpo_pools, retained_mpo_pools


def load_pledge_timelines():
    """Return per-pool historical pledge timelines from pool updates."""
    epochs_by_pool = defaultdict(list)
    pledges_by_pool = defaultdict(list)

    with (DATA_DIR / "koios_pool_updates_mainnet.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            active_epoch = row.get("active_epoch_no") or ""
            if not active_epoch:
                continue
            pool_id = row["pool_id_bech32"]
            epochs_by_pool[pool_id].append(int(active_epoch))
            pledges_by_pool[pool_id].append(float(row.get("pledge_ada") or 0.0))

    result = {}
    for pool_id, epochs in epochs_by_pool.items():
        pairs = sorted(zip(epochs, pledges_by_pool[pool_id]))
        uniq_epochs = []
        uniq_pledges = []
        last_epoch = None
        for epoch_no, pledge_ada in pairs:
            if last_epoch == epoch_no:
                uniq_epochs[-1] = epoch_no
                uniq_pledges[-1] = pledge_ada
            else:
                uniq_epochs.append(epoch_no)
                uniq_pledges.append(pledge_ada)
                last_epoch = epoch_no
        result[pool_id] = (uniq_epochs, uniq_pledges)
    return result


def historical_pledge_ada(pool_id, epoch_no, pledge_timelines):
    epochs, pledges = pledge_timelines.get(pool_id, (None, None))
    if not epochs:
        return 0.0
    idx = bisect.bisect_right(epochs, epoch_no) - 1
    if idx < 0:
        return 0.0
    return pledges[idx]


# ── Tier definitions (shared) ──
TIER_NAMES = [
    "Dormant", "Sub-block", "Sub-reliable", "Healthy",
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
    xlabel_r = ("Share of stake (%) — hatched = retained MPO"
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
                           label="Retained MPO (hatched)")
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


def build_historical_series(
    spo_only_pool_ids,
    filtered_pool_ids,
    current_rows_by_pool,
):
    """Track the current section-5 baskets back through history.

    Basket membership is fixed to the current snapshot so the historical figure answers:
    how did today's filtered populations evolve over time?
    """
    pledge_timelines = load_pledge_timelines()

    view_a = defaultdict(lambda: defaultdict(float))
    view_b = defaultdict(lambda: defaultdict(float))
    epochs_seen = set()

    with (DATA_DIR / "koios_pool_history_mainnet.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            stake_ada = pf(row.get("active_stake_ada"))
            if stake_ada <= 0:
                continue
            epoch_no = int(row["epoch_no"])
            pool_id = row["pool_id_bech32"]
            pct_staked = pf(row.get("active_stake_pct"))
            pledge_ada = historical_pledge_ada(pool_id, epoch_no, pledge_timelines)
            ratio = min(pledge_ada, stake_ada) / stake_ada if stake_ada > 100 else 0.0
            stance = classify_stance(ratio)

            if pool_id in spo_only_pool_ids:
                view_a[epoch_no][stance] += pct_staked
            if pool_id in filtered_pool_ids:
                view_b[epoch_no][stance] += pct_staked
            if pool_id in spo_only_pool_ids or pool_id in filtered_pool_ids:
                epochs_seen.add(epoch_no)

    live_epoch = None
    for pool_id, row in current_rows_by_pool.items():
        if live_epoch is None:
            live_epoch = int(row["epoch"])
        stake_ada = row["stake"]
        if stake_ada <= 0:
            continue
        ratio = min(row["pledge"], stake_ada) / stake_ada if stake_ada > 100 else 0.0
        stance = classify_stance(ratio)
        pct_staked = row["pct_staked"]
        if pool_id in spo_only_pool_ids:
            view_a[live_epoch][stance] += pct_staked
        if pool_id in filtered_pool_ids:
            view_b[live_epoch][stance] += pct_staked
    epochs_seen.add(live_epoch)

    return sorted(epochs_seen), view_a, view_b, live_epoch


def write_history_key_epochs_csv(view_a, view_b, live_epoch):
    out_path = DATA_DIR / "filtered_landscape_history_key_epochs.csv"
    rows = []
    for epoch_no in KEY_EPOCHS + [live_epoch]:
        if epoch_no not in view_a and epoch_no not in view_b:
            continue
        for view_name, data in [
            ("spo_only", view_a.get(epoch_no, {})),
            ("filtered_proxy", view_b.get(epoch_no, {})),
        ]:
            rows.append([
                epoch_no,
                view_name,
                f"{sum(data.get(st, 0.0) for st in STANCE_STACK):.4f}",
                f"{data.get('non_compliant', 0.0):.4f}",
                f"{data.get('marginal', 0.0):.4f}",
                f"{data.get('compliant', 0.0):.4f}",
                f"{data.get('exemplary', 0.0):.4f}",
            ])

    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "epoch_no", "view", "total_pct_staked",
            "non_compliant_pct", "marginal_pct",
            "compliant_pct", "exemplary_pct",
        ])
        w.writerows(rows)
    print(f"✓ Saved {out_path}")


def draw_history_figure(epochs, view_a, view_b, live_epoch):
    out_path = FIG_DIR / "filtered_landscape_history_mainnet.png"
    x = np.array(epochs)

    def stack_arrays(view_dict):
        return np.vstack([
            np.array([view_dict.get(epoch, {}).get(st, 0.0) for epoch in epochs], dtype=float)
            for st in STANCE_STACK
        ])

    a_stack = stack_arrays(view_a)
    b_stack = stack_arrays(view_b)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)

    panel_specs = [
        (
            axes[0],
            a_stack,
            "View A — Independent SPOs only",
            "Current basket = all non-MPO pools that are live in the epoch-618 snapshot",
            view_a,
        ),
        (
            axes[1],
            b_stack,
            "View B — Current filtered proxy basket",
            "Current basket = independent SPOs + retained MPO pools from the section-5 filter",
            view_b,
        ),
    ]

    colors = [STANCE_COLORS[s] for s in STANCE_STACK]

    for ax, stack, title, subtitle, view_dict in panel_specs:
        ax.set_facecolor(BG)
        ax.stackplot(x, stack, colors=colors, alpha=0.88, linewidth=0)
        top = stack.sum(axis=0)
        ax.plot(x, top, color=INK, linewidth=2.1, label="Total basket share")
        ax.axvline(IMA_END_EPOCH, color="#7F8C8D", linestyle=":", linewidth=1.2, alpha=0.9)

        ax.text(
            0.01, 0.97, title,
            transform=ax.transAxes, ha="left", va="top",
            fontsize=12, fontweight="bold", color=INK,
        )
        ax.text(
            0.01, 0.90, subtitle,
            transform=ax.transAxes, ha="left", va="top",
            fontsize=9, color=DIM,
        )

        report_total = sum(view_dict.get(IMA_END_EPOCH, {}).get(st, 0.0) for st in STANCE_STACK)
        live_total = sum(view_dict.get(live_epoch, {}).get(st, 0.0) for st in STANCE_STACK)
        report_quality = (
            view_dict.get(IMA_END_EPOCH, {}).get("compliant", 0.0)
            + view_dict.get(IMA_END_EPOCH, {}).get("exemplary", 0.0)
        )
        live_quality = (
            view_dict.get(live_epoch, {}).get("compliant", 0.0)
            + view_dict.get(live_epoch, {}).get("exemplary", 0.0)
        )
        ax.text(
            0.97, 0.96,
            f"Epoch {IMA_END_EPOCH}: {report_total:.1f}% total\n"
            f"Epoch {live_epoch}: {live_total:.1f}% total\n"
            f"Compliant + exemplary: {report_quality:.1f}% → {live_quality:.1f}%",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            color=INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#D9D9D9", alpha=0.95),
        )

        ax.annotate(
            f"{live_total:.1f}%",
            xy=(live_epoch, live_total),
            xytext=(live_epoch + 1.5, live_total + 0.6),
            fontsize=9,
            color=INK,
            arrowprops=dict(arrowstyle="-", color=INK),
        )
        ax.grid(axis="y", color=GRID, linewidth=0.7)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", colors=DIM)

    axes[1].text(
        IMA_END_EPOCH - 3,
        axes[1].get_ylim()[1] * 0.80 if axes[1].get_ylim()[1] else 1,
        "IMA endpoint\n(epoch 583)",
        ha="right",
        va="top",
        fontsize=9,
        color="#4B5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#D1D5DB", alpha=0.9),
    )

    axes[1].set_xlabel("Epoch", fontsize=11, color=INK)
    for ax in axes:
        ax.set_ylabel("Share of active stake (%)", fontsize=10, color=INK)
        ax.set_xlim(min(epochs), max(epochs) + 6)

    legend_handles = [
        mpatches.Patch(facecolor=STANCE_COLORS[st], alpha=0.88, label=STANCE_LABELS[st])
        for st in reversed(STANCE_STACK)
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=10,
        bbox_to_anchor=(0.5, 0.942),
    )
    fig.suptitle(
        "Historical evolution of the section-5 filtered baskets",
        fontsize=16,
        fontweight="bold",
        color=INK,
        y=0.99,
    )
    fig.text(
        0.5, 0.955,
        f"Fixed current baskets tracked through pool history; stance reconstructed from pool update pledge history · live snapshot at epoch {live_epoch}",
        ha="center", va="top", fontsize=10, color=DIM,
    )

    fig.tight_layout(rect=[0.03, 0.05, 0.97, 0.87])
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


def draw_spo_only_history(epochs, view_a, live_epoch):
    """Single-panel historical chart for SPO-only basket."""
    out_path = FIG_DIR / "spo_only_history_mainnet.png"
    x = np.array(epochs)

    stack = np.vstack([
        np.array([view_a.get(ep, {}).get(st, 0.0) for ep in epochs], dtype=float)
        for st in STANCE_STACK
    ])

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(1, 1, figsize=(15, 6), facecolor=BG)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    colors = [STANCE_COLORS[s] for s in STANCE_STACK]
    ax.stackplot(x, stack, colors=colors, alpha=0.88, linewidth=0)
    top = stack.sum(axis=0)
    ax.plot(x, top, color=INK, linewidth=2.1)

    ax.axvline(IMA_END_EPOCH, color="#7F8C8D", linestyle=":",
               linewidth=1.2, alpha=0.9)

    # Key epoch annotations
    report_total = sum(view_a.get(IMA_END_EPOCH, {}).get(st, 0.0)
                       for st in STANCE_STACK)
    live_total = sum(view_a.get(live_epoch, {}).get(st, 0.0)
                     for st in STANCE_STACK)
    report_nc = view_a.get(IMA_END_EPOCH, {}).get("non_compliant", 0.0)
    live_nc = view_a.get(live_epoch, {}).get("non_compliant", 0.0)
    report_qual = sum(view_a.get(IMA_END_EPOCH, {}).get(st, 0.0)
                      for st in ["compliant", "exemplary"])
    live_qual = sum(view_a.get(live_epoch, {}).get(st, 0.0)
                    for st in ["compliant", "exemplary"])

    ax.text(
        0.97, 0.96,
        f"Epoch {IMA_END_EPOCH}: {report_total:.1f}% of active stake\n"
        f"Epoch {live_epoch}: {live_total:.1f}% of active stake\n"
        f"Zero-pledge: {report_nc:.1f}% → {live_nc:.1f}%\n"
        f"Compliant + exemplary: {report_qual:.1f}% → {live_qual:.1f}%",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color=INK,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#D9D9D9", alpha=0.95),
    )

    ax.annotate(
        f"{live_total:.1f}%",
        xy=(live_epoch, live_total),
        xytext=(live_epoch + 2, live_total + 1),
        fontsize=10, fontweight="bold", color=INK,
        arrowprops=dict(arrowstyle="-", color=INK),
    )

    ax.text(
        IMA_END_EPOCH - 3,
        ax.get_ylim()[1] * 0.50 if ax.get_ylim()[1] else 1,
        "IMA endpoint\n(epoch 583)",
        ha="right", va="top", fontsize=9, color="#4B5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                  edgecolor="#D1D5DB", alpha=0.9),
    )

    ax.set_xlabel("Epoch", fontsize=11, color=INK)
    ax.set_ylabel("Share of active stake (%)", fontsize=10, color=INK)
    ax.set_xlim(min(epochs), max(epochs) + 6)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    for sp in ["top", "right", "left", "bottom"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="both", colors=DIM)

    legend_handles = [
        mpatches.Patch(facecolor=STANCE_COLORS[st], alpha=0.88,
                       label=STANCE_LABELS[st])
        for st in reversed(STANCE_STACK)
    ]
    ax.legend(handles=legend_handles, loc="upper left", ncol=2,
              frameon=True, fontsize=9, framealpha=0.95)

    fig.suptitle(
        "Historical evolution — Independent single-pool operators",
        fontsize=16, fontweight="bold", color=INK, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        f"Fixed basket = today's non-MPO pools tracked backwards · "
        f"pledge stance reconstructed from pool update history · "
        f"epoch {live_epoch} snapshot",
        ha="center", va="top", fontsize=10, color=DIM,
    )

    fig.tight_layout(rect=[0.03, 0.05, 0.97, 0.90])
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓ Saved {out_path}")


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

    all_mpo_pools, nc_mpo_pools, retained_mpo_pools = load_mpo_filter_sets()

    # ── Load all registered pools with stake ──
    all_pools = []
    current_rows_by_pool = {}
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
            is_retained_mpo = pid in retained_mpo_pools
            is_nc_mpo = pid in nc_mpo_pools
            seg = f"mpo_{stance}" if is_retained_mpo else f"spo_{stance}"
            row = {
                "pool_id": pid,
                "epoch": epoch,
                "stake": stake,
                "pledge": pledge,
                "pct_staked": 0.0,  # filled below once the total is known
                "ratio": ratio,
                "stance": stance,
                "is_mpo": is_retained_mpo,
                "is_any_mpo": is_any_mpo,
                "is_nc_mpo": is_nc_mpo,
                "segment": seg,
            }
            all_pools.append(row)
            current_rows_by_pool[pid] = row

    total_stake = sum(p["stake"] for p in all_pools)
    for p in all_pools:
        p["pct_staked"] = p["stake"] / total_stake * 100 if total_stake else 0.0

    # ── Variant 1: SPO-only (no MPOs at all) ──
    spo_only = [p for p in all_pools if not p["is_any_mpo"]]
    spo_only_pool_ids = {p["pool_id"] for p in spo_only}
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
        title="Competitive Landscape — Independent SPOs Only",
        subtitle=(f"Epoch {epoch}  ·  {n1:,} pools  ·  {s1/1e9:.1f}B ADA  "
                  f"·  All {len(all_mpo_pools & {p['pool_id'] for p in all_pools}):,} attributed MPO pools removed"),
        fig_path=FIG_DIR / "filtered_landscape_spo_only_mainnet.png",
        show_mpo_hatch=False,
    )
    write_summary_csv(spo_only, z0,
                      DATA_DIR / "filtered_landscape_spo_only_summary.csv",
                      show_mpo=False)

    # ── Variant 2: SPOs + compliant MPOs (zero-pledge MPOs removed) ──
    with_compliant = [p for p in all_pools if not p["is_nc_mpo"]]
    n2 = len(with_compliant)
    s2 = sum(p["stake"] for p in with_compliant)
    filtered_pool_ids = {p["pool_id"] for p in with_compliant}
    n_mpo = sum(1 for p in with_compliant if p["is_mpo"])
    s_mpo = sum(p["stake"] for p in with_compliant if p["is_mpo"])
    print("=" * 60)
    print(f"VARIANT 2 — CURRENT FILTERED BASKET (independent SPOs + retained MPO pools)")
    print(f"  Pools: {n2:,}  Stake: {s2/1e9:.2f}B ADA")
    print(f"    SPO: {n2 - n_mpo}  stake: {(s2-s_mpo)/1e9:.2f}B")
    print(f"    Retained MPO: {n_mpo}  stake: {s_mpo/1e9:.2f}B")
    for st in STANCE_STACK:
        sp = [p for p in with_compliant if p["stance"] == st]
        print(f"    {st}: {len(sp)} pools, "
              f"{sum(p['stake'] for p in sp)/1e9:.2f}B ({sum(p['stake'] for p in sp)/s2*100:.1f}%)")
    print()

    draw_butterfly(
        with_compliant, z0, epoch,
        title="Competitive Landscape — Independent SPOs + Retained MPO Pools",
        subtitle=(f"Epoch {epoch}  ·  {n2:,} pools  ·  {s2/1e9:.1f}B ADA  "
                  f"·  {len(nc_mpo_pools):,} MPO pools removed by the section-5 filter  "
                  f"·  {n_mpo} retained MPO pools shown hatched"),
        fig_path=FIG_DIR / "filtered_landscape_mainnet.png",
        show_mpo_hatch=True,
    )
    write_summary_csv(with_compliant, z0,
                      DATA_DIR / "filtered_landscape_summary.csv",
                      show_mpo=True)

    # ── Historical evolution of the current section-5 baskets ──
    epochs, view_a, view_b, live_epoch = build_historical_series(
        spo_only_pool_ids,
        filtered_pool_ids,
        current_rows_by_pool,
    )
    draw_history_figure(epochs, view_a, view_b, live_epoch)
    draw_spo_only_history(epochs, view_a, live_epoch)
    write_history_key_epochs_csv(view_a, view_b, live_epoch)


if __name__ == "__main__":
    main()
