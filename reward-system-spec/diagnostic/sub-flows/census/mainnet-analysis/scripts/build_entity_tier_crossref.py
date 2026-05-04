#!/usr/bin/env python3
"""
Pass 3 — Cross-reference entity attribution with pool stake.

Links named MPO entities (from entity mapping) to their aggregate stake at
epoch 623 (from pool_stake_623.csv), filtered to productive pools (≥1M ADA),
then decomposes the productive staking landscape into: attributed MPO stake,
unattributed pool stake, and per-archetype breakdown.

Reads:
  data/mpo_entity_pool_mapping_mainnet.csv   (pool → entity)
  data/mpo_entity_archetypes.csv             (entity → archetype)
  data/pool_stake_623.csv                    (pool → stake at epoch 623)
  data/delegation_size_dist_623.csv          (tier distribution)

Outputs:
  data/entity_stake_summary_623.csv          (per-entity stake summary)
  figures/entity_stake_landscape_623.png     (attributed vs unattributed)
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# IOG Brand colours
BG         = "#FFFFFF"
INK        = "#1A1A1A"
DIM        = "#666666"
GRID       = "#EBEBEB"
INFARED    = "#E52321"
GREEN      = "#00875A"
BLUE       = "#2C4FFA"
VIOLET     = "#A700FF"
AMBER      = "#FFBA36"
TEAL       = "#16E9D8"
PINK       = "#FF79FC"
DAWN       = "#EC641D"
GREY       = "#B0B0B0"
ACID_GREEN = "#06FF89"

ARCHETYPE_COLOURS = {
    "community_branded_fleet": BLUE,
    "independent_mpo":        VIOLET,
    "multi_brand_fleet":      TEAL,
    "cex_custody":            INFARED,
    "ivaas":                  DAWN,
    "opaque_fleet":           GREY,
    "protocol_project":       ACID_GREEN,
    "ecosystem_steward":      AMBER,
    "platform_wallet":        PINK,
    "unresolved_label":       "#999999",
}


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load entity mapping ──
    mapping = pd.read_csv(DATA_DIR / "mpo_entity_pool_mapping_mainnet.csv")
    pool_to_entity = dict(zip(mapping["pool_id_bech32"], mapping["entity_id"]))
    entity_to_display = dict(zip(mapping["entity_id"], mapping["display_name"]))

    # ── Load archetypes ──
    archetypes = pd.read_csv(DATA_DIR / "mpo_entity_archetypes.csv")
    entity_to_archetype = dict(zip(archetypes["entity_id"], archetypes["archetype"]))

    # ── Load pool stake (filter to productive pools ≥1M ADA) ──
    pool_stake_all = pd.read_csv(DATA_DIR / "pool_stake_623.csv")
    # Canonical production threshold: 3M ADA (95% probability of ≥1 block per
    # epoch, λ=3 — POL.O3.F1). Older runs used 1M (λ=1 expected); the diagnostic
    # standard is now 3M and Census aligns with pools-distribution / operator.
    PRODUCTION_THRESHOLD = 3_000_000
    pool_stake = pool_stake_all[pool_stake_all["total_ada"] >= PRODUCTION_THRESHOLD].copy()
    pool_stake_map = dict(zip(pool_stake["pool_id"], pool_stake["total_ada"]))
    pool_deleg_map = dict(zip(pool_stake["pool_id"], pool_stake["delegation_count"]))

    total_staked = pool_stake["total_ada"].sum()

    # ── Build entity summaries ──
    entity_stats = defaultdict(lambda: {"pools": 0, "stake": 0.0, "delegations": 0})
    attributed_pools = set()

    for pool_id, entity_id in pool_to_entity.items():
        if pool_id in pool_stake_map:
            entity_stats[entity_id]["pools"] += 1
            entity_stats[entity_id]["stake"] += pool_stake_map[pool_id]
            entity_stats[entity_id]["delegations"] += pool_deleg_map.get(pool_id, 0)
            attributed_pools.add(pool_id)

    # Sort by stake descending
    sorted_entities = sorted(entity_stats.items(), key=lambda x: x[1]["stake"], reverse=True)

    # Save entity stake summary
    out_csv = DATA_DIR / "entity_stake_summary_623.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "display_name", "archetype", "active_pools", "delegations",
                     "total_ada", "pct_of_staked"])
        for eid, stats in sorted_entities:
            w.writerow([
                eid,
                entity_to_display.get(eid, eid),
                entity_to_archetype.get(eid, "unknown"),
                stats["pools"],
                stats["delegations"],
                f"{stats['stake']:.2f}",
                f"{stats['stake'] / total_staked * 100:.2f}",
            ])
    print(f"✓ {out_csv}")

    # ── Aggregate by archetype ──
    archetype_stake = defaultdict(float)
    archetype_pools = defaultdict(int)
    archetype_entities = defaultdict(set)
    for eid, stats in entity_stats.items():
        arch = entity_to_archetype.get(eid, "unknown")
        archetype_stake[arch] += stats["stake"]
        archetype_pools[arch] += stats["pools"]
        archetype_entities[arch].add(eid)

    attributed_stake = sum(s["stake"] for s in entity_stats.values())
    unattributed_stake = total_staked - attributed_stake
    attributed_pools_count = len(attributed_pools)
    unattributed_pools_count = len(pool_stake) - attributed_pools_count

    # ══════════════════════════════════════════════════════════
    # Figure: Staking landscape — attributed vs unattributed
    # ══════════════════════════════════════════════════════════
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 8), facecolor=BG,
                                              gridspec_kw={"width_ratios": [1, 1.3]})

    # Left: pie chart — attributed vs unattributed
    ax_left.set_facecolor(BG)
    sizes = [attributed_stake, unattributed_stake]
    labels_pie = [
        f"Attributed to named entities\n{attributed_stake/1e9:.2f}B ADA ({attributed_stake/total_staked*100:.1f}%)\n{len(entity_stats)} entities, {attributed_pools_count} pools",
        f"Unattributed\n{unattributed_stake/1e9:.2f}B ADA ({unattributed_stake/total_staked*100:.1f}%)\n{unattributed_pools_count} pools",
    ]
    colours_pie = [INFARED, GREY]
    wedges, texts = ax_left.pie(sizes, labels=labels_pie, colors=colours_pie,
                                 startangle=90, textprops={"fontsize": 9, "color": INK},
                                 wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax_left.set_title("Stake Attribution — Productive Pools — Epoch 623", fontsize=12, fontweight="medium", color=INK)

    # Right: horizontal bar — top 15 entities by stake
    ax_right.set_facecolor(BG)
    top_n = 20
    top_entities = sorted_entities[:top_n]
    names = [entity_to_display.get(eid, eid) for eid, _ in top_entities]
    stakes = [s["stake"] / 1e9 for _, s in top_entities]
    archs = [entity_to_archetype.get(eid, "unknown") for eid, _ in top_entities]
    bar_colours = [ARCHETYPE_COLOURS.get(a, GREY) for a in archs]

    y_pos = np.arange(len(names))
    bars = ax_right.barh(y_pos, stakes, color=bar_colours, alpha=0.85,
                          edgecolor="white", linewidth=0.5)
    ax_right.set_yticks(y_pos)
    ax_right.set_yticklabels(names, fontsize=9)
    ax_right.invert_yaxis()
    ax_right.set_xlabel("Staked ADA (billions)", fontsize=10, color=DIM)
    ax_right.set_title(f"Top {top_n} Entities by Stake", fontsize=12, fontweight="medium", color=INK)

    for bar, (eid, stats) in zip(bars, top_entities):
        pct = stats["stake"] / total_staked * 100
        ax_right.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                      f"{pct:.1f}% ({stats['pools']}p)",
                      va="center", fontsize=8, color=DIM)

    ax_right.grid(axis="x", color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax_right.spines[sp].set_visible(False)
    ax_right.spines["bottom"].set_color(GRID)
    ax_right.spines["left"].set_color(GRID)
    ax_right.tick_params(colors=DIM, labelsize=9)

    fig.tight_layout()
    out_fig = FIG_DIR / "entity_stake_landscape_623.png"
    fig.savefig(out_fig, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out_fig}")

    # ── Archetype breakdown figure ──
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    ax.set_facecolor(BG)

    sorted_archs = sorted(archetype_stake.items(), key=lambda x: x[1], reverse=True)
    arch_names = [a.replace("_", " ").title() for a, _ in sorted_archs]
    arch_stakes = [s / 1e9 for _, s in sorted_archs]
    arch_colours = [ARCHETYPE_COLOURS.get(a, GREY) for a, _ in sorted_archs]
    arch_entity_counts = [len(archetype_entities[a]) for a, _ in sorted_archs]

    bars = ax.barh(arch_names, arch_stakes, color=arch_colours, alpha=0.85,
                    edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Staked ADA (billions)", fontsize=10, color=DIM)
    ax.set_title("Stake by Entity Archetype — Epoch 623", fontsize=13, fontweight="medium", color=INK)

    for bar, (arch, stake), n_ent in zip(bars, sorted_archs, arch_entity_counts):
        pct = stake / total_staked * 100
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f"{pct:.1f}% ({n_ent} entities, {archetype_pools[arch]} pools)",
                va="center", fontsize=8, color=DIM)

    ax.grid(axis="x", color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    fig.tight_layout()
    out_fig2 = FIG_DIR / "archetype_stake_breakdown_623.png"
    fig.savefig(out_fig2, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ {out_fig2}")

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"PASS 3 — Entity attribution cross-reference — productive pools (epoch 623)")
    print(f"{'='*60}")
    print(f"Total staked:       {total_staked/1e9:.2f}B ADA across {len(pool_stake)} pools")
    print(f"Attributed:         {attributed_stake/1e9:.2f}B ADA ({attributed_stake/total_staked*100:.1f}%) — "
          f"{len(entity_stats)} entities, {attributed_pools_count} pools")
    print(f"Unattributed:       {unattributed_stake/1e9:.2f}B ADA ({unattributed_stake/total_staked*100:.1f}%) — "
          f"{unattributed_pools_count} pools")
    print()
    print("Archetype breakdown:")
    for arch, stake in sorted_archs:
        n_ent = len(archetype_entities[arch])
        n_pool = archetype_pools[arch]
        pct = stake / total_staked * 100
        print(f"  {arch:<30s} {stake/1e9:8.2f}B ADA ({pct:5.1f}%) — {n_ent} entities, {n_pool} pools")
    print()
    print("Top 5 entities:")
    for eid, stats in sorted_entities[:5]:
        name = entity_to_display.get(eid, eid)
        pct = stats["stake"] / total_staked * 100
        print(f"  {name:<30s} {stats['stake']/1e9:8.2f}B ADA ({pct:5.1f}%) — {stats['pools']} pools, {stats['delegations']:,} delegations")


if __name__ == "__main__":
    main()
