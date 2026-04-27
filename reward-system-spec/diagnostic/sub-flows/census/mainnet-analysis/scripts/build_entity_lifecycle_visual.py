#!/usr/bin/env python3
"""
Entity lifecycle analysis — dead and declining entities.

Reads:
  data/entity_stake_history.csv       (output of 04_entity_stake_history.sql)
  data/mpo_entity_archetypes.csv      (entity → archetype mapping)
  data/staking_per_epoch.csv          (total staked per epoch, for threshold)

Outputs:
  data/entity_lifecycle_623.csv       (per-entity lifecycle metrics)
  figures/entity_lifecycle_decline.png (multi-panel decline trajectories)

The script classifies each entity into a lifecycle phase:
  - dead:      all pools below production threshold at epoch 623
  - declining: peak stake > 2× current stake, or productive pool share < 50%
  - stable:    none of the above
  - growing:   current stake > 90% of all-time peak
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

# ── Paths ──
REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
INFARED         = "#E52321"
DELIVERED_GREEN = "#00875A"
ULTRAVIOLET     = "#A700FF"
SOLAR_AMBER     = "#FFBA36"
GREY_LIGHT      = "#B0B0B0"
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"
ELECTRIC_BLUE   = "#16E9D8"
ACID_GREEN      = "#06FF89"
HYPER_PINK      = "#FF79FC"

LOVELACE = 1e6


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load data ──
    history = load_csv(DATA_DIR / "entity_stake_history.csv")
    archetypes_raw = load_csv(DATA_DIR / "mpo_entity_archetypes.csv")
    staking = load_csv(DATA_DIR / "staking_per_epoch.csv")

    archetypes = {r["entity_id"]: r for r in archetypes_raw}

    # Total staked per epoch (for threshold computation)
    total_staked_map = {
        int(r["epoch_no"]): int(r["total_staked"]) / LOVELACE
        for r in staking
    }

    # ── Build per-entity time series ──
    entity_series = defaultdict(dict)  # entity_id -> {epoch: {stake, pools, delegations}}
    for r in history:
        eid = r["entity_id"]
        e = int(r["epoch_no"])
        entity_series[eid][e] = {
            "stake": int(r["total_stake"]) / LOVELACE,
            "pools": int(r["active_pools"]),
            "delegations": int(r["delegation_count"]),
        }

    # ── Compute lifecycle metrics ──
    LATEST_EPOCH = 623
    lifecycle = []

    for eid, series in sorted(entity_series.items()):
        epochs = sorted(series.keys())
        stakes = [series[e]["stake"] for e in epochs]
        pools_ts = [series[e]["pools"] for e in epochs]

        peak_stake = max(stakes)
        peak_epoch = epochs[stakes.index(peak_stake)]
        current = series.get(LATEST_EPOCH, {"stake": 0, "pools": 0, "delegations": 0})
        current_stake = current["stake"]
        current_pools = current["pools"]
        first_epoch = epochs[0]
        last_active_epoch = max(e for e in epochs if series[e]["stake"] > 0) if any(series[e]["stake"] > 0 for e in epochs) else first_epoch

        # Threshold at latest epoch
        threshold = total_staked_map.get(LATEST_EPOCH, 21.75e9) / 21600

        # Decline ratio
        decline_ratio = current_stake / peak_stake if peak_stake > 0 else 0

        # Classification
        if current_stake < threshold:
            phase = "dead"
        elif decline_ratio < 0.25:
            phase = "declining_severe"
        elif decline_ratio < 0.50:
            phase = "declining"
        elif decline_ratio > 0.90:
            phase = "growing"
        else:
            phase = "stable"

        arch = archetypes.get(eid, {})
        display_name = arch.get("display_name", eid)
        archetype = arch.get("archetype_label", "?")

        lifecycle.append({
            "entity_id": eid,
            "display_name": display_name,
            "archetype": archetype,
            "first_epoch": first_epoch,
            "peak_epoch": peak_epoch,
            "peak_stake_ada": round(peak_stake, 0),
            "current_stake_ada": round(current_stake, 0),
            "current_pools": current_pools,
            "decline_ratio": round(decline_ratio, 4),
            "last_active_epoch": last_active_epoch,
            "phase": phase,
        })

    # ── Save lifecycle CSV ──
    out_csv = DATA_DIR / "entity_lifecycle_623.csv"
    fields = list(lifecycle[0].keys())
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(lifecycle)
    print(f"Saved → {out_csv}  ({len(lifecycle)} entities)")

    # ── Summary ──
    from collections import Counter
    phase_counts = Counter(r["phase"] for r in lifecycle)
    print("\nPhase distribution:")
    for phase, count in sorted(phase_counts.items()):
        print(f"  {phase:20s}: {count}")

    # ── Helper: small-multiples chart ──
    def plot_small_multiples(entities, title, filename, phase_colors):
        if not entities:
            print(f"No entities for {filename} — skipping.")
            return
        entities = entities[:16]
        n = len(entities)
        cols = 4
        rows_n = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows_n, cols, figsize=(16, 3.2 * rows_n),
                                  facecolor=BG, squeeze=False)

        for idx, ent in enumerate(entities):
            ax = axes[idx // cols][idx % cols]
            ax.set_facecolor(BG)

            eid = ent["entity_id"]
            series = entity_series[eid]
            epochs_s = sorted(series.keys())
            stakes = np.array([series[e]["stake"] for e in epochs_s]) / 1e6

            color = phase_colors.get(ent["phase"], DIM)
            ax.fill_between(epochs_s, stakes, color=color, alpha=0.3)
            ax.plot(epochs_s, stakes, color=color, linewidth=1.2)

            peak_e = ent["peak_epoch"]
            peak_s = ent["peak_stake_ada"] / 1e6
            ax.plot(peak_e, peak_s, "v", color=INK, markersize=5, zorder=5)

            name = ent["display_name"]
            if len(name) > 20:
                name = name[:18] + "…"
            phase_label = ent["phase"].replace("_", " ").title()
            ax.set_title(f"{name}\n({phase_label})", fontsize=9, color=INK, pad=4)

            ax.set_xlim(210, 630)
            ax.tick_params(labelsize=7, colors=DIM)
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"{v:.0f}M" if v >= 1 else f"{v*1e3:.0f}K")
            )
            ax.grid(axis="y", color=GRID, linewidth=0.4, alpha=0.6)
            for sp in ["top", "right"]:
                ax.spines[sp].set_visible(False)
            ax.spines["left"].set_color(GRID)
            ax.spines["bottom"].set_color(GRID)

        for idx in range(n, rows_n * cols):
            axes[idx // cols][idx % cols].set_visible(False)

        fig.suptitle(title, fontsize=13, fontweight="medium", color=INK, y=1.01)
        fig.tight_layout(rect=[0, 0, 1, 0.97])
        out_fig = FIG_DIR / filename
        fig.savefig(out_fig, dpi=200, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"Saved → {out_fig}")

    # ── Chart 1: declining and dead ──
    decline_entities = [
        r for r in lifecycle
        if r["phase"] in ("dead", "declining", "declining_severe")
    ]
    decline_entities.sort(key=lambda r: -r["peak_stake_ada"])

    decline_colors = {
        "dead": INFARED,
        "declining_severe": DAWN,
        "declining": SOLAR_AMBER,
    }
    plot_small_multiples(
        decline_entities,
        "Entity Lifecycle — Declining and Dead Entities",
        "entity_lifecycle_decline.png",
        decline_colors,
    )

    # ── Chart 2: growing and stable ──
    growth_entities = [
        r for r in lifecycle
        if r["phase"] in ("growing", "stable")
    ]
    growth_entities.sort(key=lambda r: -r["current_stake_ada"])

    growth_colors = {
        "growing": DELIVERED_GREEN,
        "stable": COBALT_PULSE,
    }
    plot_small_multiples(
        growth_entities,
        "Entity Lifecycle — Growing and Stable Entities",
        "entity_lifecycle_growth.png",
        growth_colors,
    )


if __name__ == "__main__":
    main()
