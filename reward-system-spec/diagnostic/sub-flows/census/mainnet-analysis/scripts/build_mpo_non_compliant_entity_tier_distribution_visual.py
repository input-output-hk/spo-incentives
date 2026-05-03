#!/usr/bin/env python3
"""
Zero-pledge MPO entities by pool-size tier.

Focus on the entities whose aggregate effective pledge ratio is <2% across
live pools (>100 ADA). The left panel shows how many live pools each entity
has in each size tier; the right panel shows the corresponding stake carried
by those pools as a share of total staked supply.

Outputs: figures/mpo_non_compliant_entity_tier_distribution_mainnet.png
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


ENTITY_DIR = Path(__file__).resolve().parent.parent          # census/mainnet-analysis/
DATA_DIR = ENTITY_DIR / "data"                               # entity data (local)
FIG_DIR = ENTITY_DIR / "figures"
POOL_DATA = (ENTITY_DIR.parent.parent / "pools-distribution"
             / "mainnet-analysis" / "data")                   # shared pool data

BG = "#FFFFFF"
INK = "#1A1A1A"
DIM = "#666666"
GRID = "#EBEBEB"

INFARED = "#E52321"
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"
ULTRAVIOLET = "#A700FF"
TEAL = "#00897B"
GREY_DARK = "#555555"

LIVE_THRESHOLD_ADA = 100.0
ENTITY_ID_ALIASES = {
    "BIGLAZYCAT": "BIGLAZY",
}

TIER_ORDER = [
    "Dormant",
    "Sub-block",
    "Sub-reliable",
    "Healthy",
    "Large healthy",
    "Near-saturation",
    "Saturated",
    "Oversaturated",
]

TIER_COLORS = {
    "Dormant": GREY_DARK,
    "Sub-block": DAWN,
    "Sub-reliable": INFARED,
    "Healthy": ACID_GREEN,
    "Large healthy": TEAL,
    "Near-saturation": SOLAR_AMBER,
    "Saturated": COBALT_PULSE,
    "Oversaturated": ULTRAVIOLET,
}


def clean_display_name(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text or text.lower() == "nan":
        return fallback
    return text


def classify_entity_stance(pct_pledged: float) -> str:
    if pct_pledged >= 80:
        return "exemplary"
    if pct_pledged >= 30:
        return "compliant"
    if pct_pledged >= 2:
        return "marginal"
    return "non_compliant"


def fmt_ada_short(value_ada: float) -> str:
    if value_ada >= 1e9:
        return f"{value_ada / 1e9:.2f}B"
    if value_ada >= 1e6:
        return f"{value_ada / 1e6:.0f}M"
    if value_ada >= 1e3:
        return f"{value_ada / 1e3:.0f}K"
    return f"{value_ada:.0f}"


def tier_for_stake(stake_ada: float, bounds: list[float]) -> str:
    idx = int(np.digitize(stake_ada, bounds[1:]))
    return TIER_ORDER[idx]


def format_tier_labels(bounds: list[float]) -> dict[str, str]:
    labels = {}
    for i, tier in enumerate(TIER_ORDER):
        lo = bounds[i]
        hi = bounds[i + 1]
        if hi == float("inf"):
            labels[tier] = f"{tier} (>{lo/1e6:.0f}M)"
            continue
        if hi < 1e6:
            labels[tier] = f"{tier} ({lo/1e3:.0f}K–{hi/1e3:.0f}K)"
        else:
            lo_txt = f"{lo/1e6:.0f}M" if lo >= 1e6 else f"{lo/1e3:.0f}K"
            hi_txt = f"{hi/1e6:.0f}M"
            labels[tier] = f"{tier} ({lo_txt}–{hi_txt})"
    labels["Dormant"] = "Dormant (<100K)"
    return labels


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with (POOL_DATA / "pool_distribution_snapshot.json").open() as f:
        snap = json.load(f)
    z0 = float(snap["z0_ada"])
    epoch = int(snap["epoch"])
    total_staked_ada = float(snap["total_active_stake_ada"])

    entity_display_names: dict[str, str] = {}
    entity_capital_class: dict[str, str] = {}
    with (DATA_DIR / "mpo_entity_archetypes.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            entity_id = row["entity_id"]
            entity_display_names[entity_id] = clean_display_name(
                row.get("display_name"),
                entity_id,
            )
            entity_capital_class[entity_id] = row.get("capital_class", "sufficient")
    for alias_id, canonical_id in ENTITY_ID_ALIASES.items():
        if canonical_id in entity_display_names and alias_id not in entity_display_names:
            entity_display_names[alias_id] = entity_display_names[canonical_id]
            entity_capital_class[alias_id] = entity_capital_class.get(canonical_id, "sufficient")

    bounds = [0, 100e3, 1e6, 3e6, z0 * 0.5, z0 * 0.8, z0 * 0.95, z0 * 1.05, float("inf")]
    tier_labels = format_tier_labels(bounds)

    pools_by_entity: dict[str, list[dict[str, str]]] = defaultdict(list)
    with (DATA_DIR / "mpo_entity_pool_health_mainnet.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("pool_status") != "registered":
                continue
            stake_ada = float(row.get("current_active_stake_ada") or 0.0)
            if stake_ada <= LIVE_THRESHOLD_ADA:
                continue
            pools_by_entity[row["entity_id"]].append(row)

    entities = []
    for entity_id, pools in pools_by_entity.items():
        if entity_capital_class.get(entity_id) != "sufficient":
            continue
        total_stake_ada = sum(float(p["current_active_stake_ada"]) for p in pools)
        effective_pledge_ada = sum(
            min(float(p["declared_pledge_ada"]), float(p["current_active_stake_ada"]))
            for p in pools
        )
        pct_pledged = (effective_pledge_ada / total_stake_ada * 100.0) if total_stake_ada else 0.0
        if classify_entity_stance(pct_pledged) != "non_compliant":
            continue

        count_by_tier = {tier: 0 for tier in TIER_ORDER}
        stake_by_tier = {tier: 0.0 for tier in TIER_ORDER}
        for pool in pools:
            stake_ada = float(pool["current_active_stake_ada"])
            tier = tier_for_stake(stake_ada, bounds)
            count_by_tier[tier] += 1
            stake_by_tier[tier] += stake_ada

        entities.append(
            {
                "entity_id": entity_id,
                "display_name": entity_display_names.get(
                    entity_id,
                    clean_display_name(pools[0].get("display_name"), entity_id),
                ),
                "pct_pledged": pct_pledged,
                "total_pools": len(pools),
                "total_stake_ada": total_stake_ada,
                "count_by_tier": count_by_tier,
                "stake_by_tier": stake_by_tier,
            }
        )

    entities.sort(key=lambda row: row["total_stake_ada"], reverse=True)

    n_entities = len(entities)
    total_non_compliant_stake = sum(row["total_stake_ada"] for row in entities)
    total_non_compliant_pools = sum(row["total_pools"] for row in entities)

    fig_h = max(5.5, n_entities * 0.46 + 3.6)
    fig = plt.figure(figsize=(18.5, fig_h), facecolor=BG)
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[4.6, 7.2],
        left=0.27,
        right=0.98,
        top=0.84,
        bottom=0.14,
        wspace=0.08,
    )
    ax_l = fig.add_subplot(gs[0])
    ax_r = fig.add_subplot(gs[1], sharey=ax_l)

    for ax in (ax_l, ax_r):
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_visible(False)

    y_pos = np.arange(n_entities)
    bar_h = 0.66

    max_count_total = max(row["total_pools"] for row in entities) if entities else 1
    max_stake_pct = max(
        row["total_stake_ada"] / total_staked_ada * 100.0 for row in entities
    ) if entities else 1.0

    for i, row in enumerate(entities):
        left_count = 0.0
        left_stake = 0.0

        for tier in TIER_ORDER:
            count = row["count_by_tier"][tier]
            stake_pct = row["stake_by_tier"][tier] / total_staked_ada * 100.0
            color = TIER_COLORS[tier]

            if count > 0:
                ax_l.barh(
                    y_pos[i],
                    count,
                    left=left_count,
                    height=bar_h,
                    color=color,
                    alpha=0.9,
                    edgecolor=BG,
                    linewidth=0.6,
                    zorder=3,
                )
                if count >= 3:
                    ax_l.text(
                        left_count + count / 2,
                        y_pos[i],
                        f"{count}",
                        ha="center",
                        va="center",
                        fontsize=7.5,
                        color=BG if tier in {"Sub-reliable", "Saturated", "Oversaturated"} else INK,
                        fontweight="bold",
                        zorder=4,
                    )
            left_count += count

            if stake_pct > 0:
                ax_r.barh(
                    y_pos[i],
                    stake_pct,
                    left=left_stake,
                    height=bar_h,
                    color=color,
                    alpha=0.9,
                    edgecolor=BG,
                    linewidth=0.6,
                    zorder=3,
                )
            left_stake += stake_pct

        ax_l.text(
            left_count + max_count_total * 0.02,
            y_pos[i],
            f"{row['total_pools']}",
            ha="left",
            va="center",
            fontsize=8.5,
            color=INK,
            fontweight="bold",
        )
        ax_r.text(
            left_stake + max_stake_pct * 0.015,
            y_pos[i],
            fmt_ada_short(row["total_stake_ada"]),
            ha="left",
            va="center",
            fontsize=8.5,
            color=INK,
            fontweight="bold",
        )

    ax_l.set_yticks(y_pos)
    ax_l.set_yticklabels([row["display_name"] for row in entities], fontsize=9, color=INK)
    for tick in ax_l.get_yticklabels():
        tick.set_fontweight("bold")
    ax_l.invert_yaxis()

    ax_l.set_xlim(0, max_count_total * 1.18)
    ax_l.set_xlabel("Live pools by size tier (count)", fontsize=10, color=DIM, labelpad=8)
    ax_l.xaxis.tick_top()
    ax_l.xaxis.set_label_position("top")
    ax_l.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_l.tick_params(axis="y", length=0, pad=6)
    ax_l.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    ax_r.set_xlim(0, max_stake_pct * 1.23)
    ax_r.set_xlabel("Stake by size tier (% of total staked supply)", fontsize=10, color=DIM, labelpad=8)
    ax_r.xaxis.tick_top()
    ax_r.xaxis.set_label_position("top")
    ax_r.tick_params(axis="x", colors=DIM, labelsize=8, top=True, bottom=False)
    ax_r.tick_params(axis="y", left=False, labelleft=False)
    ax_r.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax_r.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)

    legend_handles = [
        mpatches.Patch(facecolor=TIER_COLORS[tier], alpha=0.9, label=tier_labels[tier])
        for tier in TIER_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.62, 0.04),
        ncol=4,
        frameon=False,
        fontsize=8.3,
    )

    fig.suptitle(
        "Zero-pledge saturation-scale MPO entities by pool-size tier",
        fontsize=14,
        fontweight="bold",
        color=INK,
        y=0.93,
    )
    fig.text(
        0.27,
        0.885,
        (
            f"{n_entities} saturation-scale zero-pledge entities (<2% effective pledge) · "
            f"{total_non_compliant_pools} live pools (>100 ADA) · "
            f"{total_non_compliant_stake / 1e9:.2f}B ADA · epoch {epoch}"
        ),
        fontsize=9.2,
        color=DIM,
        ha="left",
    )
    fig.text(
        0.27,
        0.012,
        "Rows are sorted by total live stake. The count panel shows fleet composition; "
        "the stake panel shows where the economic weight sits. Tier thresholds match §3.",
        fontsize=7.8,
        color=DIM,
        ha="left",
    )

    out = FIG_DIR / "mpo_non_compliant_entity_tier_distribution_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓  {out.name}")


if __name__ == "__main__":
    main()
