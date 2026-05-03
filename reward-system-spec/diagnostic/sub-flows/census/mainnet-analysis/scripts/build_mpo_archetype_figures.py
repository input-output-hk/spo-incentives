#!/usr/bin/env python3
"""
Generate archetype-aware MPO visualisations for §4 of the pools-distribution report.

Outputs (both written to report/mainnet/pools-distribution/figures/):
  mpo_entity_current_distribution_mainnet.png  -- redesigned current snapshot,
                                                   entities grouped by archetype
  mpo_entity_progression_stacked_mainnet.png   -- archetype-level stacked area
                                                   (replaces per-entity spaghetti)

Data inputs (all in data/):
  mpo_entity_health_overview_mainnet.csv       -- current stats per entity
  mpo_entity_archetypes.csv                    -- entity → archetype mapping
  mpo_entity_pool_mapping_mainnet.csv          -- pool → entity mapping
  koios_pool_history_mainnet.csv               -- per-pool per-epoch active stake

No network calls; all data is local.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from matplotlib.ticker import PercentFormatter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from cardano_events import add_event_markers

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ENTITY_DIR   = Path(__file__).resolve().parent.parent          # census/mainnet-analysis/
DATA_DIR     = ENTITY_DIR / "data"                             # entity data (local)
FIGURES_DIR  = ENTITY_DIR / "figures"
POOL_DATA    = (ENTITY_DIR.parent.parent / "pools-distribution"
                / "mainnet-analysis" / "data")                 # shared pool data

# ---------------------------------------------------------------------------
# Supply constants (epoch 618)
# ---------------------------------------------------------------------------
import json as _json
_snap = _json.load((POOL_DATA / "pool_distribution_snapshot.json").open())
STAKED_SUPPLY_ADA = float(_snap.get("total_active_stake_ada", 0))  # ~21.75B
CIRCULATING_SUPPLY_ADA = float(_snap.get("supply_ada", 0))        # ~38.49B

# ---------------------------------------------------------------------------
# IOG brand palette – archetype colour assignments
# ---------------------------------------------------------------------------
ARCHETYPE_COLORS: Dict[str, str] = {
    "cex":                      "#E52321",  # INFARED
    "ivaas":                    "#2C4FFA",  # COBALT PULSE
    "capital_insufficient":     "#8C6D1F",  # ochre-brown
    "ecosystem":                "#FFBA36",  # SOLAR AMBER
    "platform":                 "#16B2A8",  # teal variant
    "independent_mpo":          "#00875A",  # muted Acid Green
    "community_branded_fleet":  "#06CC6E",  # lighter Acid Green
    "multi_brand_fleet":        "#0A9E5A",  # mid Acid Green
    "opaque_fleet":             "#555555",  # dark grey
    "protocol_project":         "#A700FF",  # Ultraviolet
    "opaque":                   "#78909C",  # neutral grey
}

ARCHETYPE_LABELS: Dict[str, str] = {
    "cex":                      "Exchange Custody (CEX)",
    "ivaas":                    "Institutional Validator (IVaaS)",
    "capital_insufficient":     "Sub-saturation fleet",
    "ecosystem":                "Ecosystem Steward",
    "platform":                 "Platform / Wallet",
    "independent_mpo":          "Independent MPO",
    "community_branded_fleet":  "Community Branded Fleet",
    "multi_brand_fleet":        "Multi-Brand Fleet",
    "opaque_fleet":             "Opaque Fleet",
    "protocol_project":         "Protocol / DeFi Project",
    "opaque":                   "Opaque / Unresolved",
}

ARCHETYPE_INLINE_LABELS: Dict[str, str] = {
    "cex":                     "CEX",
    "ivaas":                   "IVaaS",
    "capital_insufficient":    "Cap.-insuf.",
    "community_branded_fleet": "Branded",
    "independent_mpo":         "Indep. MPO",
    "multi_brand_fleet":       "Multi-brand",
    "opaque":                  "Opaque",
    "ecosystem":               "Ecosystem",
    "platform":                "Platform",
    "opaque_fleet":            "Opaque fleet",
    "protocol_project":        "Protocol",
}

# Display order for groups in the bar chart (largest / most relevant first)
ARCHETYPE_ORDER: List[str] = [
    "cex",
    "ivaas",
    "capital_insufficient",
    "community_branded_fleet",
    "independent_mpo",
    "multi_brand_fleet",
    "opaque",
    "ecosystem",
    "platform",
    "opaque_fleet",
    "protocol_project",
]

# ---------------------------------------------------------------------------
# Incentive-stance classification (pledge-bonus capture)
# ---------------------------------------------------------------------------
# Thresholds on effective pledge ratio (= min(pledge, stake) / stake).
# Grounded in the pledge-bonus function: for a half-saturated pool,
# 30% pledged ≈ 50% of bonus captured (the median capture point).

STANCE_THRESHOLDS = [
    (0.80, "exemplary"),       # ≥80%: captures the vast majority of the bonus (80/20)
    (0.30, "compliant"),       # 30–80%: incentive-compatible strategy
    (0.02, "marginal"),        # 2–30%: at the margin, target of adjustments
    (0.00, "non_compliant"),   # <2%: does not play the induced strategy
]

STANCE_LABELS: Dict[str, str] = {
    "cant_play":       "Can't play",
    "exemplary":      "Exemplary",
    "compliant":      "Compliant",
    "marginal":       "Marginal",
    "non_compliant":  "Zero-pledge",
}

STANCE_INLINE_LABELS: Dict[str, str] = {
    "cant_play":      "Can't play",
    "non_compliant":  "Zero-pledge",
    "marginal":       "Marginal",
    "compliant":      "Compliant",
    "exemplary":      "Exemplary",
}

STANCE_COLORS: Dict[str, str] = {
    "cant_play":       "#8C6D1F",  # same structural bucket as archetype
    "exemplary":      "#06FF89",  # Acid Green  – best-in-class
    "compliant":      "#16E9D8",  # Electric Blue – solid
    "marginal":       "#FFBA36",  # Solar Amber – room to improve
    "non_compliant":  "#E52321",  # Infared – forfeiting bonus
}

STANCE_ORDER: List[str] = ["exemplary", "compliant", "marginal", "non_compliant", "cant_play"]

ENTITY_ID_ALIASES: Dict[str, str] = {
    "BIGLAZYCAT": "BIGLAZY",
}


def classify_stance(pct_pledged: float, archetype: str | None = None) -> str:
    """Classify an entity or pool by pledge-bonus capture stance."""
    if archetype == "capital_insufficient":
        return "cant_play"
    ratio = pct_pledged / 100.0
    for threshold, label in STANCE_THRESHOLDS:
        if ratio >= threshold:
            return label
    return "non_compliant"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def clean_display_name(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text or text.lower() == "nan":
        return fallback
    return text


def derive_archetype(row: Dict[str, str]) -> str:
    if row.get("capital_class") == "insufficient":
        return "capital_insufficient"
    return row["archetype"]


def load_archetype_lookups() -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    rows = load_csv(DATA_DIR / "mpo_entity_archetypes.csv")
    by_entity: Dict[str, Dict[str, str]] = {}
    by_display: Dict[str, Dict[str, str]] = {}

    for row in rows:
        entity_id = row["entity_id"]
        display_name = clean_display_name(row.get("display_name"), entity_id)
        record = dict(row)
        record["display_name"] = display_name
        record["archetype_base"] = row["archetype"]
        record["archetype"] = derive_archetype(row)
        by_entity[entity_id] = record
        by_display[display_name] = record

    for alias_id, canonical_id in ENTITY_ID_ALIASES.items():
        canonical = by_entity.get(canonical_id)
        if canonical and alias_id not in by_entity:
            alias = dict(canonical)
            alias["entity_id"] = alias_id
            by_entity[alias_id] = alias

    return by_entity, by_display


def load_archetypes() -> Dict[str, str]:
    """Return entity_id → archetype mapping."""
    by_entity, _ = load_archetype_lookups()
    return {entity_id: row["archetype"] for entity_id, row in by_entity.items()}


def load_entity_stats() -> List[Dict[str, str]]:
    by_entity, _ = load_archetype_lookups()
    stake_by_entity: Dict[str, float] = defaultdict(float)

    for row in load_csv(DATA_DIR / "mpo_entity_pool_health_mainnet.csv"):
        if row.get("pool_status") != "registered":
            continue
        stake_ada = float(row.get("current_active_stake_ada") or 0.0)
        if stake_ada <= 100.0:
            continue
        entity_id = row["entity_id"]
        stake_by_entity[entity_id] += stake_ada

    entity_rows: List[Dict[str, str]] = []
    for entity_id, stake_ada in sorted(stake_by_entity.items(), key=lambda item: item[1], reverse=True):
        meta = by_entity.get(entity_id, {})
        display_name = meta.get("display_name") or clean_display_name(entity_id, entity_id)
        entity_rows.append(
            {
                "entity_id": entity_id,
                "display_name": display_name,
                "current_stake_ada": f"{stake_ada:.6f}",
                "current_pct_supply": f"{(stake_ada / CIRCULATING_SUPPLY_ADA * 100.0) if CIRCULATING_SUPPLY_ADA else 0.0:.6f}",
            }
        )

    return entity_rows


def load_pool_to_entity() -> Dict[str, str]:
    """Return pool_id_bech32 → entity_id mapping."""
    rows = load_csv(DATA_DIR / "mpo_entity_pool_mapping_mainnet.csv")
    # The mapping CSV uses entity_id as first column; fall back to display_name if needed
    result: Dict[str, str] = {}
    for r in rows:
        pool_id = r.get("pool_id_bech32", "")
        entity_id = r.get("entity_id", "") or r.get("display_name", "")
        if pool_id and entity_id:
            result[pool_id] = entity_id
    return result


def build_pool_to_archetype(
    pool_to_entity: Dict[str, str],
    entity_to_archetype: Dict[str, str],
) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for pool_id, entity_id in pool_to_entity.items():
        archetype = entity_to_archetype.get(entity_id)
        if archetype:
            result[pool_id] = archetype
    return result


def scan_pool_history(
    pool_to_archetype: Dict[str, str],
    pool_to_entity: Dict[str, str],
) -> Tuple[Dict[int, Dict[str, float]], Dict[int, float], Dict[int, Dict[str, float]]]:
    """
    Single-pass scan of koios_pool_history_mainnet.csv.

    Returns:
        archetype_by_epoch  – {epoch: {archetype: total_active_stake_ada}}
        total_by_epoch      – {epoch: sum_all_active_stake_ada}
        entity_by_epoch     – {epoch: {entity_id: total_active_stake_ada}}
    """
    history_path = POOL_DATA / "koios_pool_history_mainnet.csv"
    archetype_by_epoch: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    entity_by_epoch: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    total_by_epoch: Dict[int, float] = defaultdict(float)

    with history_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stake_str = row.get("active_stake_ada", "") or ""
            if not stake_str:
                continue
            try:
                stake = float(stake_str)
                epoch = int(row["epoch_no"])
            except (ValueError, KeyError):
                continue

            total_by_epoch[epoch] += stake

            pool_id = row["pool_id_bech32"]
            archetype = pool_to_archetype.get(pool_id)
            if archetype:
                archetype_by_epoch[epoch][archetype] += stake

            entity = pool_to_entity.get(pool_id)
            if entity:
                entity_by_epoch[epoch][entity] += stake

    return archetype_by_epoch, total_by_epoch, entity_by_epoch


# ---------------------------------------------------------------------------
# Figure 1: Current entity distribution grouped by archetype
# ---------------------------------------------------------------------------

def _load_entity_pool_metrics() -> Dict[str, Dict[str, float]]:
    """Compute per-entity aggregate metrics from pool-level health data.

    Returns {entity_id: {pct_pledged, pct_delegated, avg_margin,
                         n_live_pools, n_dormant_pools}}.

    "Live" = registered with active_stake > 100 ADA (excludes zero-stake
    ghost pools and near-zero residual pools).
    "Dormant" = registered with active_stake ≤ 100 ADA (zero-stake +
    near-zero residual).
    Metrics (pledge ratio, margin) are computed only over live pools.
    """
    pool_rows = load_csv(DATA_DIR / "mpo_entity_pool_health_mainnet.csv")
    from collections import defaultdict as _dd

    LIVE_THRESHOLD = 100.0  # ADA – below this the pool is dormant

    entity_live: Dict[str, List[Dict[str, str]]] = _dd(list)
    entity_dormant_count: Dict[str, int] = _dd(int)

    for r in pool_rows:
        if r.get("pool_status") != "registered":
            continue
        stake = float(r.get("current_active_stake_ada", 0) or 0)
        eid = r["entity_id"]
        if stake > LIVE_THRESHOLD:
            entity_live[eid].append(r)
        else:
            entity_dormant_count[eid] += 1

    result: Dict[str, Dict[str, float]] = {}
    all_entity_ids = set(entity_live) | set(entity_dormant_count)
    for eid in all_entity_ids:
        pools = entity_live.get(eid, [])
        n_dormant = entity_dormant_count.get(eid, 0)
        if not pools:
            result[eid] = {
                "pct_pledged": 0.0, "pct_delegated": 100.0,
                "avg_margin": 0.0, "n_live_pools": 0,
                "n_dormant_pools": n_dormant,
            }
            continue
        total_stake = sum(float(p["current_active_stake_ada"]) for p in pools)
        # Per-pool: cap effective_pledge at pool active_stake so that
        # near-retired pools with declared_pledge >> active_stake don't
        # produce >100% ratios.
        effective_pledge = sum(
            min(float(p["declared_pledge_ada"]), float(p["current_active_stake_ada"]))
            for p in pools
        )
        avg_margin = sum(float(p["margin_pct"]) for p in pools) / len(pools)
        pct_pledged = effective_pledge / total_stake * 100 if total_stake > 0 else 0
        result[eid] = {
            "pct_pledged": pct_pledged,
            "pct_delegated": 100.0 - pct_pledged,
            "avg_margin": avg_margin,
            "n_live_pools": len(pools),
            "n_dormant_pools": n_dormant,
            "total_pledge_ada": effective_pledge,
        }
    return result


def figure_current_distribution(
    entity_stats: List[Dict[str, str]],
    entity_to_archetype: Dict[str, str],
) -> None:
    out_path = FIGURES_DIR / "mpo_entity_current_distribution_mainnet.png"

    # Load per-entity pool-level metrics (pledge, delegation, margin)
    entity_pool_metrics = _load_entity_pool_metrics()
    stake_by_entity = {
        row["entity_id"]: float(row.get("current_stake_ada", 0) or 0)
        for row in entity_stats
    }

    # Build entity → archetype and current % supply
    entity_rows: List[Dict] = []
    for row in entity_stats:
        pct = float(row.get("current_pct_supply", 0) or 0)
        # Drop entities with negligible / inactive stake (< 0.01% of supply).
        if pct < 0.01:
            continue
        entity_rows.append({
            "entity_id": row["entity_id"],
            "display_name": row["display_name"],
            "pct_supply": pct,
        })

    for r in entity_rows:
        eid = r["entity_id"]
        r["archetype"] = entity_to_archetype.get(eid, "opaque")
        metrics = entity_pool_metrics.get(eid, {})
        r["pct_pledged"] = metrics.get("pct_pledged", 0.0)
        r["pct_delegated"] = metrics.get("pct_delegated", 100.0)
        r["avg_margin"] = metrics.get("avg_margin", 0.0)
        r["n_live_pools"] = int(metrics.get("n_live_pools", 0))
        r["n_dormant_pools"] = int(metrics.get("n_dormant_pools", 0))
        r["total_pledge_ada"] = metrics.get("total_pledge_ada", 0.0)
        r["stance"] = classify_stance(r["pct_pledged"], r["archetype"])
        stake_ada = stake_by_entity.get(eid, 0.0)
        r["stake_ada"] = stake_ada
        r["pct_staked"] = stake_ada / STAKED_SUPPLY_ADA * 100 if STAKED_SUPPLY_ADA > 0 else 0.0

    # Sort: archetype order first, then stake descending within group
    archetype_rank = {a: i for i, a in enumerate(ARCHETYPE_ORDER)}
    entity_rows.sort(key=lambda r: (archetype_rank.get(r["archetype"], 99), -r["pct_staked"]))

    # Gather y-positions with gaps between archetype groups
    labels, values, colors = [], [], []
    group_boundaries: List[Tuple[float, float, str, float]] = []  # (y_top, y_bot, archetype, group_pct)

    current_archetype = None
    group_start_idx = 0
    group_pct = 0.0
    y = 0

    # We'll insert a gap (0.6 units) between archetype groups, entity bars are 1 unit each
    GAP = 0.6

    positions: List[float] = []
    group_info: List[Tuple[int, int, str]] = []  # (start_pos_idx, end_pos_idx, archetype)

    pos = 0.0
    group_start_pos = 0.0
    current_arch = None
    arch_start = 0

    for i, r in enumerate(entity_rows):
        arch = r["archetype"]
        if arch != current_arch:
            if current_arch is not None:
                group_info.append((arch_start, len(positions) - 1, current_arch))
                pos += GAP
            current_arch = arch
            arch_start = len(positions)
            group_start_pos = pos
        positions.append(pos)
        pos += 1.0

    if current_arch is not None:
        group_info.append((arch_start, len(positions) - 1, current_arch))

    # Reverse order so top entity is at top of chart
    positions = [max(positions) - p for p in positions]

    # Compute group label positions and totals
    # group_info is in reverse order now (we reversed positions)
    archetype_totals: Dict[str, float] = defaultdict(float)
    for r in entity_rows:
        archetype_totals[r["archetype"]] += r["pct_supply"]

    # Build group band info (center y-pos, archetype)
    group_bands: List[Tuple[float, str]] = []
    for start_i, end_i, arch in group_info:
        # positions[start_i..end_i] — take the middle
        mid_pos = (positions[start_i] + positions[end_i]) / 2
        group_bands.append((mid_pos, arch))

    # ---- Compute archetype-level aggregates for the metrics table ----
    archetype_agg: Dict[str, Dict[str, float]] = {}
    for arch in ARCHETYPE_ORDER:
        arch_entities = [r for r in entity_rows if r["archetype"] == arch]
        if not arch_entities:
            continue
        # Weighted averages by pct_supply (proxy for stake weight)
        total_w = sum(r["pct_supply"] for r in arch_entities)
        if total_w > 0:
            w_pledged = sum(r["pct_pledged"] * r["pct_supply"] for r in arch_entities) / total_w
            w_delegated = sum(r["pct_delegated"] * r["pct_supply"] for r in arch_entities) / total_w
            w_margin = sum(r["avg_margin"] * r["pct_supply"] for r in arch_entities) / total_w
        else:
            w_pledged = w_delegated = w_margin = 0.0
        total_staked_w = sum(r["pct_staked"] for r in arch_entities)
        archetype_agg[arch] = {
            "pct_pledged": w_pledged,
            "pct_delegated": w_delegated,
            "avg_margin": w_margin,
            "n_entities": len(arch_entities),
            "total_pct_supply": total_w,
            "total_pct_staked": total_staked_w,
        }

    # ---- Plot: two-panel figure (bar chart top, metrics table bottom) ----
    bar_height_chart = max(8.0, len(entity_rows) * 0.52 + len(group_info) * 0.3 + 1.5)
    # Table: entity rows + archetype summary rows + header
    n_arch_present = len(archetype_agg)
    table_row_count = len(entity_rows) + n_arch_present + 1  # +1 for header
    table_height = max(3.5, table_row_count * 0.28 + 1.0)
    fig_height = bar_height_chart + table_height + 0.5

    fig = plt.figure(figsize=(14, fig_height))
    fig.patch.set_facecolor("#FAFAFA")

    # GridSpec: bar chart on top (larger), table on bottom
    gs = fig.add_gridspec(2, 1, height_ratios=[bar_height_chart, table_height], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])
    ax.set_facecolor("#FAFAFA")
    ax_table.set_facecolor("#FAFAFA")

    bar_height = 0.75

    for i, r in enumerate(entity_rows):
        arch = r["archetype"]
        color = ARCHETYPE_COLORS[arch]
        pct = r["pct_staked"]
        yp = positions[i]

        ax.barh(yp, pct, height=bar_height, color=color, alpha=0.88, zorder=3)

        # Value label
        label_text = f"{pct:.2f}%"
        if pct >= 2.0:
            ax.text(pct - 0.12, yp, label_text, va="center", ha="right",
                    fontsize=8.5, color="white", fontweight="bold", zorder=4)
        else:
            ax.text(pct + 0.08, yp, label_text, va="center", ha="left",
                    fontsize=8.5, color="#1a1a1a", zorder=4)

    # Entity name labels on y-axis
    ax.set_yticks(positions)
    ax.set_yticklabels([r["display_name"] for r in entity_rows], fontsize=9.5)

    # Archetype group bands: shaded background + right-side label
    for start_i, end_i, arch in group_info:
        y_top = positions[start_i] + bar_height / 2 + 0.25
        y_bot = positions[end_i] - bar_height / 2 - 0.25
        # Subtle background band
        ax.axhspan(y_bot, y_top, xmin=0, xmax=1, color=ARCHETYPE_COLORS[arch], alpha=0.06, zorder=1)
        # Archetype label on the right outside the plot
        y_mid = (y_top + y_bot) / 2
        total_pct = sum(entity_rows[j]["pct_staked"] for j in range(start_i, end_i + 1))
        label = f"{ARCHETYPE_LABELS[arch]}\n{total_pct:.2f}% staked"
        ax.annotate(
            label,
            xy=(1.01, y_mid),
            xycoords=ax.get_yaxis_transform(),
            va="center", ha="left",
            fontsize=7.8,
            color=ARCHETYPE_COLORS[arch],
            fontweight="bold",
            linespacing=1.4,
            annotation_clip=False,
        )

    ax.set_xlabel("Share of staked supply (%)", fontsize=11, labelpad=8)
    ax.set_xlim(0, max(r["pct_staked"] for r in entity_rows) * 1.12)
    ax.set_ylim(min(positions) - 0.7, max(positions) + 0.7)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    ax.set_title(
        "MPO entities by archetype — sub-saturation isolated (epoch 618)",
        fontsize=12, fontweight="bold", pad=14,
    )

    # ---- Metrics table ----
    ax_table.axis("off")
    ax_table.set_title(
        "Per-entity and per-archetype metrics: pledge coverage, delegation, margin",
        fontsize=10.5, fontweight="bold", pad=10, loc="left",
    )

    # Total dormant pools across all entities
    total_dormant = sum(r["n_dormant_pools"] for r in entity_rows)

    # Build table data: entity rows grouped by archetype, with archetype summary rows
    # No Stance column here — the concept is introduced later in §4.2.3.
    col_labels = ["Entity", "Live", "Dormant", "% Staked",
                   "Stake (B ₳)", "Pledge (M ₳)", "% Pledged", "Avg Margin"]
    n_cols = len(col_labels)
    cell_text = []
    cell_colors = []
    WHITE = "#FFFFFF"
    LIGHT_GREY = "#F0F0F0"

    current_arch_for_table = None
    for r in entity_rows:
        arch = r["archetype"]
        # Insert archetype summary row before first entity of a new group
        if arch != current_arch_for_table:
            if arch in archetype_agg:
                a = archetype_agg[arch]
                n_live = sum(er["n_live_pools"] for er in entity_rows if er["archetype"] == arch)
                n_dorm = sum(er["n_dormant_pools"] for er in entity_rows if er["archetype"] == arch)
                arch_stake_b = sum(er["stake_ada"] for er in entity_rows if er["archetype"] == arch) / 1e9
                arch_pledge_m = sum(er["total_pledge_ada"] for er in entity_rows if er["archetype"] == arch) / 1e6
                cell_text.append([
                    f"  {ARCHETYPE_LABELS[arch]}",
                    str(n_live),
                    str(n_dorm),
                    f"{a['total_pct_staked']:.2f}%",
                    f"{arch_stake_b:.2f}",
                    f"{arch_pledge_m:.0f}",
                    f"{a['pct_pledged']:.2f}%",
                    f"{a['avg_margin']:.1f}%",
                ])
                cell_colors.append(["summary_" + arch] * n_cols)
            current_arch_for_table = arch

        stake_b = r["stake_ada"] / 1e9
        pledge_m = r["total_pledge_ada"] / 1e6
        cell_text.append([
            f"    {r['display_name']}",
            str(r["n_live_pools"]),
            str(r["n_dormant_pools"]),
            f"{r['pct_staked']:.2f}%",
            f"{stake_b:.2f}",
            f"{pledge_m:.1f}",
            f"{r['pct_pledged']:.2f}%",
            f"{r['avg_margin']:.1f}%",
        ])
        cell_colors.append([WHITE] * n_cols)

    table = ax_table.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="upper center",
        colWidths=[0.22, 0.05, 0.06, 0.09, 0.10, 0.12, 0.09, 0.09],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1.0, 1.25)

    # Style header
    for j in range(n_cols):
        cell = table[0, j]
        cell.set_facecolor("#2a2a2a")
        cell.set_text_props(color="white", fontweight="bold", fontsize=8)

    # Column indices for conditional formatting
    COL_PLEDGED = col_labels.index("% Pledged")
    WARN_RED_BG = "#FDECEC"       # very light red background
    WARN_RED_TEXT = "#B71C1C"      # dark red text

    # Style body cells
    for i in range(len(cell_text)):
        for j in range(n_cols):
            cell = table[i + 1, j]
            tag = cell_colors[i][0]
            if tag.startswith("summary_"):
                # Archetype summary row
                arch_key = tag.split("_", 1)[1]
                cell.set_facecolor(ARCHETYPE_COLORS.get(arch_key, "#cccccc"))
                cell.set_alpha(0.12)
                cell.set_text_props(fontweight="bold", fontsize=7.5)
            else:
                base_bg = WHITE if i % 2 == 0 else LIGHT_GREY
                # Highlight cells that signal poor pledge discipline:
                # % Pledged < 2% → red tint
                cell_val = cell_text[i][j]
                is_warn = False
                if j == COL_PLEDGED:
                    try:
                        v = float(cell_val.replace("%", ""))
                        if v < 2.0:
                            is_warn = True
                    except ValueError:
                        pass

                if is_warn:
                    cell.set_facecolor(WARN_RED_BG)
                    cell.set_text_props(color=WARN_RED_TEXT, fontweight="bold")
                else:
                    cell.set_facecolor(base_bg)
            # Left-align entity names
            if j == 0:
                cell.set_text_props(ha="left")

    fig.text(
        0.01, 0.005,
        "Entities with ≥2 registered pools and ≥0.01% of circulating supply. "
        "Live = registered pools with >100 ₳ active stake. "
        "Dormant = registered pools with ≤100 ₳ (zero-stake + near-zero residual). "
        f"Total dormant across all entities: {total_dormant}. "
        "% Pledged = min(pledge, stake) / stake. Avg Margin = unweighted mean across live pools. "
        "Archetype rows = stake-weighted averages.",
        ha="left", va="bottom", fontsize=6.5, color="#555555",
    )

    fig.subplots_adjust(left=0.14, right=0.84, top=0.97, bottom=0.03, hspace=0.04)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"✓  {out_path.name}")


# ---------------------------------------------------------------------------
# Figure 2: Archetype progression stacked area
# ---------------------------------------------------------------------------

def figure_archetype_progression(
    archetype_by_epoch: Dict[int, Dict[str, float]],
    total_by_epoch: Dict[int, float],
) -> None:
    out_path = FIGURES_DIR / "mpo_entity_progression_stacked_mainnet.png"

    # Only use epochs where we have supply data
    all_epochs = sorted(set(archetype_by_epoch) & set(total_by_epoch))

    # Focus on Shelley era (epoch 208+) where attributable MPO data is meaningful
    epochs = [e for e in all_epochs if e >= 208]
    if not epochs:
        print("  No epoch data found for progression chart")
        return

    # Build per-archetype series (% of total delegated stake)
    series: Dict[str, np.ndarray] = {}
    for arch in ARCHETYPE_ORDER:
        vals = []
        for e in epochs:
            total = total_by_epoch.get(e, 0.0)
            arch_stake = archetype_by_epoch.get(e, {}).get(arch, 0.0)
            vals.append(arch_stake / total * 100.0 if total > 0 else 0.0)
        series[arch] = np.array(vals, dtype=float)

    total_attributed = sum(series[a] for a in ARCHETYPE_ORDER)

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    # Stack areas in reverse order so CEX is at top (most prominent)
    stack_order = list(reversed(ARCHETYPE_ORDER))
    stack_data = [series[a] for a in stack_order]
    stack_colors = [ARCHETYPE_COLORS[a] for a in stack_order]
    stack_labels = [ARCHETYPE_LABELS[a] for a in stack_order]

    ax.stackplot(
        epochs,
        stack_data,
        labels=stack_labels,
        colors=stack_colors,
        alpha=0.82,
        linewidth=0.0,
    )

    # Total attributed line
    ax.plot(epochs, total_attributed, color="#1a1a1a", linewidth=1.5,
            linestyle="-", alpha=0.7, label="_nolegend_")

    # Add Cardano event markers
    add_event_markers(ax, compact=False, y_frac=0.85, alpha=0.4)

    # ---- Annotations ----
    # Epoch 400 reallocation window
    ax.axvspan(395, 415, color="#d0d0d0", alpha=0.4, linewidth=0)
    ax.text(416, total_attributed.max() * 0.96,
            "Epoch ~400\nreallocation",
            ha="left", va="top", fontsize=8.5, color="#444444",
            style="italic")

    # Mark current epoch
    last_e = epochs[-1]
    last_total = total_attributed[-1]
    ax.scatter([last_e], [last_total], color="#1a1a1a", s=50, zorder=5)
    ax.annotate(
        f"Epoch {last_e}\n{last_total:.1f}% attributed",
        xy=(last_e, last_total),
        xytext=(last_e - 60, last_total + 2.5),
        arrowprops=dict(arrowstyle="-", color="#444444", lw=1.0),
        fontsize=9, color="#1a1a1a",
    )

    # CEX band annotation (approximate midpoint of CEX band at current epoch)
    cex_top = series["cex"][-1]
    if cex_top > 1.0:
        # CEX is the top of the stack since we reversed the order
        # Actually in stackplot, the order is bottom to top = stack_order[0] to stack_order[-1]
        # We reversed ARCHETYPE_ORDER, so cex is last in stack_order = plotted on TOP
        # The CEX band top is at approximately total_attributed[-1]
        # The CEX band bottom is at total_attributed[-1] - cex_top
        cex_y_mid = last_total - cex_top / 2
        ax.annotate(
            f"CEX: {cex_top:.1f}%",
            xy=(last_e + 1, cex_y_mid),
            xytext=(last_e + 8, cex_y_mid),
            arrowprops=None,
            fontsize=8.5, color="#E52321", fontweight="bold",
            va="center",
        )

    ax.set_xlabel("Epoch", fontsize=11, labelpad=8)
    ax.set_ylabel("Share of total delegated ADA (%)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.set_xlim(epochs[0], epochs[-1] + 20)
    ax.set_ylim(0, total_attributed.max() + 5.0)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.xaxis.grid(True, linestyle="--", alpha=0.3, zorder=0)

    ax.set_title(
        "MPO attributed stake by archetype — share of total delegated ADA",
        fontsize=12, fontweight="bold", pad=14,
    )

    # Legend: reverse order so CEX appears first in legend (matches visual top)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        list(reversed(handles)),
        list(reversed(labels)),
        loc="upper left",
        fontsize=9,
        framealpha=0.9,
        ncol=2,
        title="Archetype",
        title_fontsize=9,
    )

    fig.text(
        0.01, 0.01,
        "Stacked areas = attributed entity pools only (pools in mpo_entity_pool_mapping_mainnet.csv). "
        "Y-axis = archetype stake / total delegated ADA. Historical data from local Koios pool history export.",
        ha="left", va="bottom", fontsize=8, color="#555555",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"✓  {out_path.name}")


# ---------------------------------------------------------------------------
# Figure 3: Per-entity stacked area (same style as legacy pool-landscape)
# ---------------------------------------------------------------------------

def figure_entity_progression(
    entity_by_epoch: Dict[int, Dict[str, float]],
    total_by_epoch: Dict[int, float],
    entity_to_archetype: Dict[str, str],
) -> None:
    out_path = FIGURES_DIR / "mpo_entity_progression_stacked_by_entity_mainnet.png"

    # Load display names from archetype CSV
    metadata_by_entity, _ = load_archetype_lookups()
    entity_id_to_display: Dict[str, str] = {
        entity_id: row["display_name"] for entity_id, row in metadata_by_entity.items()
    }

    # Focus on Shelley era
    all_epochs = sorted(set(entity_by_epoch) & set(total_by_epoch))
    epochs = [e for e in all_epochs if e >= 208]
    if not epochs:
        print("  No epoch data found for entity progression chart")
        return

    # Build per-entity series as % of circulating supply
    entity_series: Dict[str, np.ndarray] = {}
    for entity_id in entity_to_archetype:
        vals = []
        for e in epochs:
            total = total_by_epoch.get(e, 0.0)
            entity_stake = entity_by_epoch.get(e, {}).get(entity_id, 0.0)
            vals.append(entity_stake / total * 100.0 if total > 0 else 0.0)
        entity_series[entity_id] = np.array(vals, dtype=float)

    # Order: by archetype group, then by current stake descending (largest at bottom)
    archetype_rank = {a: i for i, a in enumerate(ARCHETYPE_ORDER)}

    def sort_key(eid: str):
        arch = entity_to_archetype.get(eid, "opaque")
        return (archetype_rank.get(arch, 99), -entity_series[eid][-1])

    entity_order = sorted(entity_series, key=sort_key)

    # Build stacked series and labels
    stack_data: List[np.ndarray] = []
    stack_labels: List[str] = []
    stack_colors: List[str] = []

    # Use tab20 + tab20b + tab20c for 60 distinct colours (matching legacy)
    palette = (
        list(plt.get_cmap("tab20").colors)
        + list(plt.get_cmap("tab20b").colors)
        + list(plt.get_cmap("tab20c").colors)
    )

    for i, eid in enumerate(entity_order):
        stack_data.append(entity_series[eid])
        stack_labels.append(entity_id_to_display.get(eid, eid))
        stack_colors.append(palette[i % len(palette)])

    total_pct = np.sum(stack_data, axis=0) if stack_data else np.zeros(len(epochs))

    # ---- Plot ----
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.stackplot(
        epochs,
        stack_data,
        labels=stack_labels,
        colors=stack_colors,
        alpha=0.95,
        linewidth=0.0,
    )
    # Total outline
    ax.plot(epochs, total_pct, color="#1f2937", linewidth=1.2, alpha=0.85)

    # Add Cardano event markers
    add_event_markers(ax, compact=False, y_frac=0.85, alpha=0.4)

    # ---- Annotations ----
    # Epoch 400 reallocation window
    ax.axvspan(400, 410, color="#dbeafe", alpha=0.4, linewidth=0)
    ax.text(401.5, total_pct.max() - 1.3, "Shift around epoch 400",
            color="#355c7d", fontsize=10)

    # Live total annotation
    if epochs:
        ax.annotate(
            f"Live total {total_pct[-1]:.1f}%",
            xy=(epochs[-1], total_pct[-1]),
            xytext=(epochs[-1] - 48, total_pct[-1] + 2.0),
            arrowprops=dict(arrowstyle="-", color="#1f2937"),
            color="#1f2937", fontsize=10,
        )

    ax.set_xlabel("Epoch", fontsize=11)
    ax.set_ylabel("Share of circulating supply", fontsize=11)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.set_xlim(min(epochs), max(epochs) + 4)
    ax.set_ylim(0, max(total_pct) + 3.0)

    # Legend below the chart (matching legacy style)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=5,
        frameon=True,
        fontsize=8.5,
        title="Entities",
        title_fontsize=9,
    )

    fig.text(
        0.01, 0.015,
        "Stacked areas show attributed entities with ≥2 registered pools. "
        "Historical values from local Koios pool history export.",
        ha="left", va="bottom", fontsize=9, color="#555555",
    )

    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✓  {out_path.name}")


# ---------------------------------------------------------------------------
# Figure 4: Incentive-stance distribution (same entities, grouped by stance)
# ---------------------------------------------------------------------------

def figure_stance_distribution(
    entity_stats: List[Dict[str, str]],
    entity_to_archetype: Dict[str, str],
) -> None:
    """Readable two-row summary: stacked bars on the left, clean readout panels on the right."""
    out_path = FIGURES_DIR / "mpo_entity_stance_distribution_mainnet.png"

    entity_pool_metrics = _load_entity_pool_metrics()

    entity_rows: List[Dict] = []
    for row in entity_stats:
        pct = float(row.get("current_pct_supply", 0) or 0)
        eid = row["entity_id"]
        metrics = entity_pool_metrics.get(eid, {})
        pct_pledged = metrics.get("pct_pledged", 0.0)
        stake_ada = float(row.get("current_stake_ada", 0) or 0)
        archetype = entity_to_archetype.get(eid, "opaque")
        pct_staked = stake_ada / STAKED_SUPPLY_ADA * 100 if STAKED_SUPPLY_ADA > 0 else 0.0
        entity_rows.append({
            "entity_id": eid,
            "display_name": row["display_name"],
            "pct_supply": pct,
            "pct_staked": pct_staked,
            "archetype": archetype,
            "stance": classify_stance(pct_pledged, archetype),
            "pct_pledged": pct_pledged,
            "n_live_pools": int(metrics.get("n_live_pools", 0)),
        })

    # ---- Aggregate by archetype and by stance ----
    arch_totals: Dict[str, float] = defaultdict(float)
    arch_entities: Dict[str, int] = defaultdict(int)
    stance_totals: Dict[str, float] = defaultdict(float)
    stance_entities: Dict[str, List[str]] = defaultdict(list)

    for r in entity_rows:
        arch_totals[r["archetype"]] += r["pct_staked"]
        arch_entities[r["archetype"]] += 1
        stance_totals[r["stance"]] += r["pct_staked"]
        stance_entities[r["stance"]].append(r["display_name"])

    def _segment_text(ax, x: float, y: float, text: str, fontsize: float = 10.0) -> None:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=fontsize,
            color="white",
            fontweight="bold",
            zorder=5,
            linespacing=1.15,
            path_effects=[
                pe.Stroke(linewidth=2.2, foreground="black", alpha=0.20),
                pe.Normal(),
            ],
        )

    def _draw_readout_panel(
        ax: plt.Axes,
        title: str,
        keys: List[str],
        totals: Dict[str, float],
        labels: Dict[str, str],
        colors: Dict[str, str],
        counts: Dict[str, int],
    ) -> None:
        ax.set_facecolor("#FFFFFF")
        ax.axis("off")
        ax.text(0.0, 1.02, title, transform=ax.transAxes, fontsize=10, fontweight="bold", color="#222222")

        visible_keys = [key for key in keys if totals.get(key, 0.0) > 0]
        step = 0.082 if len(visible_keys) >= 9 else 0.11
        y = 0.92
        for key in visible_keys:
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (0.00, y - 0.020),
                    0.038,
                    0.038,
                    transform=ax.transAxes,
                    boxstyle="round,pad=0.004,rounding_size=0.008",
                    linewidth=0,
                    facecolor=colors[key],
                    alpha=0.95,
                    clip_on=False,
                )
            )
            ax.text(
                0.055,
                y,
                labels[key],
                transform=ax.transAxes,
                ha="left",
                va="center",
                fontsize=8.7,
                color="#222222",
                fontweight="bold",
            )
            ax.text(
                0.99,
                y,
                f"{totals[key]:.1f}% · {counts[key]} ent.",
                transform=ax.transAxes,
                ha="right",
                va="center",
                fontsize=8.5,
                color="#555555",
            )
            y -= step

    # ---- Plot: wider layout with side readouts ----
    fig = plt.figure(figsize=(18, 7.8), facecolor="#FFFFFF")
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[5.8, 2.4],
        height_ratios=[1, 1],
        hspace=0.44,
        wspace=0.06,
    )

    ax0 = fig.add_subplot(gs[0, 0])
    ax0_info = fig.add_subplot(gs[0, 1])
    ax1 = fig.add_subplot(gs[1, 0])
    ax1_info = fig.add_subplot(gs[1, 1])

    for ax in (ax0, ax1):
        ax.set_facecolor("#FFFFFF")
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, linestyle="--", alpha=0.18, color="#BDBDBD")
        for spine in ax.spines.values():
            spine.set_visible(False)

    bar_height = 0.62
    inline_threshold = 6.2

    # --- Row 0: by archetype ---
    arch_keys = [arch for arch in ARCHETYPE_ORDER if arch_totals.get(arch, 0.0) > 0]
    left = 0.0
    for arch in arch_keys:
        width = arch_totals[arch]
        ax0.barh(0, width, left=left, height=bar_height, color=ARCHETYPE_COLORS[arch], alpha=0.92, zorder=3)
        if width >= inline_threshold:
            _segment_text(
                ax0,
                left + width / 2,
                0,
                f"{ARCHETYPE_INLINE_LABELS.get(arch, ARCHETYPE_LABELS[arch])}\n{width:.1f}%",
                fontsize=10.2 if width >= 9 else 9.2,
            )
        left += width
    total_width = left

    # --- Row 1: by stance ---
    stance_keys = [stance for stance in reversed(STANCE_ORDER) if stance_totals.get(stance, 0.0) > 0]
    left = 0.0
    for stance in stance_keys:
        width = stance_totals[stance]
        n_entities = len(stance_entities.get(stance, []))
        ax1.barh(0, width, left=left, height=bar_height, color=STANCE_COLORS[stance], alpha=0.90, zorder=3)
        if width >= inline_threshold:
            _segment_text(
                ax1,
                left + width / 2,
                0,
                f"{STANCE_INLINE_LABELS.get(stance, STANCE_LABELS[stance])}\n{width:.1f}% · {n_entities} ent.",
                fontsize=10.0 if width >= 9 else 9.0,
            )
        left += width
    total_stance_width = left

    common_width = max(total_width, total_stance_width)

    # --- Axis formatting ---
    ax0.set_xlim(0, common_width * 1.01)
    ax1.set_xlim(0, common_width * 1.01)

    ax0.set_yticks([0])
    ax0.set_yticklabels(["By archetype"], fontsize=12, fontweight="bold")
    ax1.set_yticks([0])
    ax1.set_yticklabels(["By stance"], fontsize=12, fontweight="bold")

    for ax in (ax0, ax1):
        ax.set_ylim(-0.55, 0.55)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", labelsize=10, colors="#333333")

    ax0.tick_params(axis="x", bottom=False, labelbottom=False)
    ax1.set_xlabel("Share of staked supply (%)", fontsize=11, labelpad=8, color="#333333")

    _draw_readout_panel(
        ax0_info,
        "Archetype Breakdown",
        arch_keys,
        arch_totals,
        ARCHETYPE_LABELS,
        ARCHETYPE_COLORS,
        arch_entities,
    )
    _draw_readout_panel(
        ax1_info,
        "Stance Breakdown",
        stance_keys,
        stance_totals,
        STANCE_LABELS,
        STANCE_COLORS,
        {stance: len(names) for stance, names in stance_entities.items()},
    )

    fig.suptitle(
        "MPO attributed stake — archetype vs incentive stance · share of staked supply (epoch 618)",
        fontsize=14, fontweight="bold", y=0.97,
    )
    fig.text(
        0.5,
        0.928,
        f"Same 85 attributed entities, decomposed two ways · total attributed = {common_width:.1f}% of staked supply",
        ha="center",
        va="center",
        fontsize=10,
        color="#666666",
    )

    fig.text(
        0.01, 0.01,
        "Same 85 entities decomposed two ways. Top = structural archetype. Bottom = incentive accessibility + bonus capture. "
        "Can't play = sub-saturation (< z0 total stake); remaining classes use effective pledge ratio: "
        "Zero-pledge <2% | Marginal 2–30% | Compliant 30–80% | Exemplary ≥80%.",
        ha="left", va="bottom", fontsize=8, color="#555555",
    )

    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"✓  {out_path.name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading entity stats and archetype classification…")
    entity_stats      = load_entity_stats()
    entity_to_archetype = load_archetypes()

    print("Figure 1: current distribution by archetype…")
    figure_current_distribution(entity_stats, entity_to_archetype)

    print("Building pool → archetype / entity maps…")
    pool_to_entity   = load_pool_to_entity()
    pool_to_archetype = build_pool_to_archetype(pool_to_entity, entity_to_archetype)
    print(f"  {len(pool_to_archetype):,} pools mapped to an archetype")

    print("Scanning pool history (this may take a moment for the 218 MB file)…")
    archetype_by_epoch, total_by_epoch, entity_by_epoch = scan_pool_history(
        pool_to_archetype, pool_to_entity,
    )
    print(f"  {len(total_by_epoch):,} epochs found in pool history")

    print("Figure 4: incentive-stance distribution…")
    figure_stance_distribution(entity_stats, entity_to_archetype)

    print("Figure 2: archetype progression stacked area…")
    figure_archetype_progression(archetype_by_epoch, total_by_epoch)

    print("Figure 3: per-entity progression lines…")
    figure_entity_progression(entity_by_epoch, total_by_epoch, entity_to_archetype)

    print("Done.")


if __name__ == "__main__":
    main()
