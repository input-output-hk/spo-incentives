#!/usr/bin/env python3
"""
MPO Tier × Stance × Entity breakdown.

For each size tier (viable+), shows a horizontal stacked bar decomposed by
stance, with entity names labelled inside or beside each segment.

Outputs: figures/mpo_tier_stance_entity_mainnet.png
"""

from __future__ import annotations
import csv, json
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ENTITY_DIR = Path(__file__).resolve().parent.parent          # census/mainnet-analysis/
DATA_DIR   = ENTITY_DIR / "data"                             # entity data (local)
FIG_DIR    = ENTITY_DIR / "figures"
POOL_DATA  = (ENTITY_DIR.parent.parent / "pools-distribution"
              / "mainnet-analysis" / "data")                  # shared pool data

BG  = "#FAFAFA"
INK = "#1A1A1A"
DIM = "#666666"

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

def classify_stance(ratio):
    if ratio >= 0.80: return "exemplary"
    if ratio >= 0.30: return "compliant"
    if ratio >= 0.02: return "marginal"
    return "non_compliant"


def clean_display_name(value, fallback):
    text = (value or "").strip()
    if not text or text.lower() == "nan":
        return fallback
    return text

def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    snap = json.load((POOL_DATA / "pool_distribution_snapshot.json").open())
    z0 = snap["z0_ada"]
    epoch = snap["epoch"]

    # Canonical productive set: ≥3M ADA at e623 (95% block probability, λ=3 — POL.O3.F1).
    PRODUCTIVE_THRESHOLD_ADA = 3_000_000
    pool_stake_e623 = {}
    with (DATA_DIR / "pool_stake_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            ada = float(r["total_ada"])
            if ada >= PRODUCTIVE_THRESHOLD_ADA:
                pool_stake_e623[r["pool_id"]] = ada
    staked = sum(pool_stake_e623.values())  # productive total — denominator for share

    # Load MPO pool mapping
    mpo_map = {}
    for r in csv.DictReader((DATA_DIR / "mpo_entity_pool_mapping_mainnet.csv").open(newline="")):
        mpo_map[r['pool_id_bech32']] = r.get('entity_id', '')
    archetypes = {r['entity_id']: r for r in csv.DictReader((DATA_DIR / "mpo_entity_archetypes.csv").open(newline=""))}
    if 'BIGLAZY' in archetypes:
        alias = dict(archetypes['BIGLAZY'])
        alias['entity_id'] = 'BIGLAZYCAT'
        archetypes['BIGLAZYCAT'] = alias

    def get_tier(s):
        if s < 3e6: return None  # skip below viability
        if s < z0*0.5: return "healthy"
        if s < z0*0.8: return "large_healthy"
        if s < z0*0.95: return "near_saturation"
        if s < z0*1.05: return "saturated"
        return "oversaturated"

    TIER_ORDER = ["oversaturated", "saturated", "near_saturation", "large_healthy", "healthy"]
    TIER_LABELS = {
        "oversaturated": "Oversaturated\n>81M",
        "saturated": "Saturated\n73–81M",
        "near_saturation": "Near-saturation\n62–73M",
        "large_healthy": "Large healthy\n38–62M",
        "healthy": "Healthy\n3–38M",
    }

    # Pull pledge from koios pool list for the join (registration parameter).
    koios_pledge = {}
    for r in csv.DictReader((POOL_DATA / "koios_pool_list_mainnet.csv").open(newline="")):
        if r['pool_status'] != 'registered':
            continue
        koios_pledge[r['pool_id_bech32']] = float(r.get('pledge','0') or '0') / 1e6

    # Load productive MPO pools (stake from epoch 623, pledge from koios)
    pools = []
    for pid, eid in mpo_map.items():
        stake = pool_stake_e623.get(pid)
        if stake is None:
            continue  # not productive at e623
        tier = get_tier(stake)
        if tier is None:
            continue  # below 3M (Healthy floor — outside this figure's scope)
        pledge = koios_pledge.get(pid, 0.0)
        eff_pledge = min(pledge, stake)
        ratio = eff_pledge / stake if stake > 100 else 0.0
        meta = archetypes.get(eid, {})
        display = clean_display_name(meta.get('display_name'), eid)
        stance = "cant_play" if meta.get("capital_class") != "sufficient" else classify_stance(ratio)
        pools.append({
            'stake': stake, 'ratio': ratio,
            'tier': tier, 'stance': stance,
            'entity': display,
        })

    # Build data: tier → stance → [(entity, stake)]
    tier_stance_entities = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for p in pools:
        tier_stance_entities[p['tier']][p['stance']][p['entity']] += p['stake']

    # ── Plot ──
    n_tiers = len(TIER_ORDER)
    fig, ax = plt.subplots(figsize=(18, n_tiers * 1.8 + 2.5), facecolor=BG)
    ax.set_facecolor(BG)

    y_pos = np.arange(n_tiers)[::-1]  # top = oversaturated
    bar_h = 0.7

    for idx, tier in enumerate(TIER_ORDER):
        yp = y_pos[idx]
        left = 0.0

        for stance in STANCE_STACK:
            entities = tier_stance_entities[tier][stance]
            if not entities:
                continue

            # Sort entities by stake descending within this stance
            sorted_ents = sorted(entities.items(), key=lambda x: -x[1])
            stance_total = sum(v for _, v in sorted_ents)
            color = STANCE_COLORS[stance]

            # Draw one segment per entity within the stance group
            for ent_name, ent_stake in sorted_ents:
                w = ent_stake / staked * 100  # % of productive stake
                if w < 0.01:
                    left += w
                    continue

                ax.barh(yp, w, left=left, height=bar_h,
                       color=color, alpha=0.85, edgecolor="white",
                       linewidth=0.5, zorder=3)

                # Label: entity name inside if wide enough
                if w >= 0.35:
                    # Shorten name if needed
                    label = ent_name
                    if w < 1.0 and len(label) > 12:
                        label = label[:10] + "…"
                    elif w < 0.6 and len(label) > 6:
                        label = label[:5] + "…"

                    fs = 6.5 if w >= 0.8 else 5.5
                    ax.text(left + w/2, yp, label,
                           ha="center", va="center", fontsize=fs,
                           color="white" if stance == "non_compliant" else INK,
                           fontweight="bold", zorder=4,
                           clip_on=True)

                left += w

        # Tier total label on right
        tier_total = sum(
            sum(entities.values())
            for entities in tier_stance_entities[tier].values()
        )
        tier_pct = tier_total / staked * 100
        n_pools = sum(1 for p in pools if p['tier'] == tier)
        ax.text(left + 0.15, yp, f"{tier_total/1e9:.1f}B ({tier_pct:.1f}%)  ·  {n_pools} pools",
               va="center", ha="left", fontsize=9, color=INK, fontweight="bold")

    # Y labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels([TIER_LABELS[t] for t in TIER_ORDER], fontsize=10, fontweight="bold")
    ax.set_xlabel("Share of staked supply (%)", fontsize=11, labelpad=8)

    max_x = max(
        sum(sum(e.values()) for e in tier_stance_entities[t].values()) / staked * 100
        for t in TIER_ORDER
    )
    ax.set_xlim(0, max_x * 1.25)
    ax.set_ylim(min(y_pos) - 0.6, max(y_pos) + 0.6)

    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=STANCE_COLORS[s], alpha=0.85, label=STANCE_LABELS[s])
        for s in reversed(STANCE_STACK)
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9,
             framealpha=0.95, title="Incentive stance", title_fontsize=10)

    ax.set_title(
        f"MPO pools: tier × stance × entity (viable-and-above · epoch {epoch})",
        fontsize=13, fontweight="bold", pad=14,
    )

    fig.text(
        0.01, 0.01,
        "Each coloured sub-bar = one entity's pools within a tier+stance group. "
        "White borders separate entities. Only pools ≥3M ADA (Healthy floor) shown. "
        "Ochre = sub-saturation / can't play. Denominator = productive stake (≥1M ADA at epoch 623).",
        ha="left", va="bottom", fontsize=7.5, color=DIM,
    )

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = FIG_DIR / "mpo_tier_stance_entity_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"✓  {out.name}")


if __name__ == "__main__":
    main()
