#!/usr/bin/env python3
"""
Build pledge-unmet visuals for the mainnet pools-distribution report.

Inputs:
- data/pool_pledge_epoch_summary_mainnet.csv
- data/pool_pledge_pool_summary_mainnet.csv
- data/koios_pool_list_mainnet.csv
- data/mpo_entity_pool_mapping_mainnet.csv
- data/mpo_entity_archetypes.csv

Outputs:
- figures/pledge_unmet_history_mainnet.png
- figures/pledge_unmet_pool_exposure_mainnet.png
- figures/pledge_unmet_mpo_entities_mainnet.png
- data/pledge_unmet_top_pools_mainnet.csv
- data/pledge_unmet_top_entities_mainnet.csv
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
FIG_DIR = REPORT_DIR / "figures"
ENTITY_DATA = REPORT_DIR.parent.parent / "census" / "mainnet-analysis" / "data"

BG = "#FFFFFF"
INK = "#1A1A1A"
DIM = "#666666"
GRID = "#EBEBEB"
INFARED = "#E52321"
TEAL = "#00897B"
ACID_GREEN = "#00B35F"
SOLAR_AMBER = "#FFBA36"
COBALT = "#2C4FFA"
GREY = "#7F8C8D"

MPO_COLOR = INFARED
INDIE_COLOR = ACID_GREEN
REPORT_CHECKPOINT_EPOCH = 583
LIVE_COVERAGE_END_EPOCH = 615

ARCHETYPE_COLORS = {
    "cex": "#E52321",
    "ivaas": "#2C4FFA",
    "capital_insufficient": "#8C6D1F",
    "ecosystem": "#FFBA36",
    "platform": "#16B2A8",
    "independent_mpo": "#00875A",
    "community_branded_fleet": "#06CC6E",
    "multi_brand_fleet": "#0A9E5A",
    "opaque_fleet": "#555555",
    "protocol_project": "#A700FF",
    "opaque": "#78909C",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def parse_float(value: str | None, default: float = 0.0) -> float:
    text = "" if value is None else str(value).strip()
    return float(text) if text else default


def parse_int(value: str | None, default: int = 0) -> int:
    text = "" if value is None else str(value).strip()
    return int(text) if text else default


def clean_text(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text or text.lower() == "nan":
        return fallback
    return text


def short_pool_id(pool_id: str) -> str:
    return f"{pool_id[:10]}...{pool_id[-6:]}"


def add_checkpoint(ax: plt.Axes, *, y: float = 0.97) -> None:
    ax.axvline(REPORT_CHECKPOINT_EPOCH, color=GREY, linestyle=":", linewidth=1.2, alpha=0.9)
    ax.text(
        REPORT_CHECKPOINT_EPOCH + 2,
        y,
        "IMA endpoint\n(epoch 583)",
        transform=ax.get_xaxis_transform(),
        ha="left",
        va="top",
        fontsize=9,
        color="#4B5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#D1D5DB", alpha=0.9),
    )


def load_label_maps():
    pool_labels: dict[str, dict[str, str]] = {}
    for row in load_csv(DATA_DIR / "koios_pool_list_mainnet.csv"):
        pool_labels[row["pool_id_bech32"]] = {
            "ticker": clean_text(row.get("ticker"), ""),
            "pool_group": clean_text(row.get("pool_group"), ""),
        }

    archetypes = {}
    for row in load_csv(ENTITY_DATA / "mpo_entity_archetypes.csv"):
        entity_id = row["entity_id"]
        archetype = row["archetype"]
        if row.get("capital_class") == "insufficient":
            archetype = "capital_insufficient"
        archetypes[entity_id] = {
            "entity_id": entity_id,
            "display_name": clean_text(row.get("display_name"), entity_id),
            "archetype": archetype,
        }

    entity_by_pool = {}
    for row in load_csv(ENTITY_DATA / "mpo_entity_pool_mapping_mainnet.csv"):
        pool_id = row["pool_id_bech32"]
        entity_id = row["entity_id"]
        meta = archetypes.get(entity_id, {})
        entity_by_pool[pool_id] = {
            "entity_id": entity_id,
            "display_name": clean_text(row.get("display_name"), meta.get("display_name", entity_id)),
            "archetype": meta.get("archetype", "opaque"),
        }
    return pool_labels, entity_by_pool


def render_history(epoch_rows: list[dict[str, str]], out_path: Path) -> None:
    epochs = np.array([parse_int(r["epoch_no"]) for r in epoch_rows], dtype=int)
    unmet_pool_share = np.array([100.0 - parse_float(r["pledge_met_share_pct"]) for r in epoch_rows], dtype=float)
    unmet_reward_share = np.array([parse_float(r["reward_share_from_unmet_pct"]) for r in epoch_rows], dtype=float)
    unmet_stake_share = np.array([parse_float(r["active_stake_share_from_unmet_pct"]) for r in epoch_rows], dtype=float)
    unmet_pool_cnt = np.array([parse_float(r["pledge_unmet_pool_cnt"]) for r in epoch_rows], dtype=float)
    observed_pool_cnt = np.array([parse_float(r["pools_with_observed_pledge"]) for r in epoch_rows], dtype=float)
    coverage_ratio = np.array([parse_float(r["median_pledge_coverage_ratio"]) for r in epoch_rows], dtype=float)

    latest = epoch_rows[-1]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.patch.set_facecolor(BG)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", colors=DIM)

    ax1.plot(epochs, unmet_pool_share, color=INFARED, linewidth=2.5, label="Pools below declared pledge (%)")
    ax1.plot(epochs, unmet_reward_share, color=SOLAR_AMBER, linewidth=2.2, label="Reward share from unmet pools (%)")
    ax1.plot(epochs, unmet_stake_share, color=TEAL, linewidth=2.0, label="Active stake share from unmet pools (%)")
    ax1.set_ylabel("Share (%)", color=INK)
    ax1.legend(loc="upper left", ncol=3, frameon=False, fontsize=10)
    add_checkpoint(ax1)
    ax1.annotate(
        f"Epoch {LIVE_COVERAGE_END_EPOCH}\n"
        f"{unmet_pool_share[-1]:.1f}% pools\n"
        f"{unmet_reward_share[-1]:.1f}% rewards",
        xy=(epochs[-1], unmet_pool_share[-1]),
        xytext=(epochs[-1] - 55, unmet_pool_share[-1] + 8),
        arrowprops=dict(arrowstyle="-", color=INFARED),
        fontsize=9,
        color=INK,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#D9D9D9", alpha=0.95),
    )

    ax2.plot(epochs, observed_pool_cnt, color=INK, linewidth=1.9, label="Pools with observed owner history")
    ax2.plot(epochs, unmet_pool_cnt, color=INFARED, linewidth=2.1, label="Unmet pools (count)")
    ax2.set_ylabel("Pool count", color=INK)
    ax2b = ax2.twinx()
    ax2b.plot(epochs, coverage_ratio, color=COBALT, linewidth=1.8, linestyle="--", label="Median coverage ratio (x)")
    ax2b.set_ylabel("Median coverage ratio (x)", color=COBALT)
    ax2b.tick_params(axis="y", labelcolor=COBALT)
    ax2b.spines["top"].set_visible(False)
    ax2b.spines["left"].set_visible(False)
    ax2b.spines["right"].set_visible(False)
    add_checkpoint(ax2)

    handles1, labels1 = ax2.get_legend_handles_labels()
    handles2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(handles1 + handles2, labels1 + labels2, loc="upper left", ncol=3, frameon=False, fontsize=10)
    ax2.set_xlabel("Epoch", color=INK)

    fig.suptitle("Historical pledge-unmet proxy since Shelley", fontsize=17, fontweight="bold", color=INK, y=0.985)
    fig.text(
        0.5,
        0.955,
        "Coverage window available locally: epoch 210-615 · proxy built from owner active stake vs declared pledge by pool and epoch",
        ha="center",
        va="top",
        fontsize=10,
        color=DIM,
    )
    fig.text(
        0.5,
        0.03,
        f"Latest covered epoch {latest['epoch_no']}: {latest['pledge_unmet_pool_cnt']} unmet pools out of {latest['pools_with_observed_pledge']} observed · median coverage {parse_float(latest['median_pledge_coverage_ratio']):.3f}x",
        ha="center",
        va="bottom",
        fontsize=10,
        color=DIM,
    )
    fig.tight_layout(rect=[0.03, 0.06, 0.97, 0.93])
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def write_top_pools_csv(rows: list[dict[str, object]], out_path: Path) -> None:
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_pool_exposure(pool_summary_rows: list[dict[str, str]], pool_labels, entity_by_pool, out_path: Path, out_csv: Path) -> None:
    enriched = []
    for row in pool_summary_rows:
        unmet_epochs = parse_int(row["pledge_unmet_epoch_cnt"])
        if unmet_epochs <= 0:
            continue
        pool_id = row["pool_id_bech32"]
        label_meta = pool_labels.get(pool_id, {})
        entity_meta = entity_by_pool.get(pool_id)
        is_mpo = entity_meta is not None
        ticker = clean_text(label_meta.get("ticker"), "")
        pool_group = clean_text(label_meta.get("pool_group"), "")
        entity_name = "" if entity_meta is None else clean_text(entity_meta.get("display_name"), entity_meta["entity_id"])
        if entity_name and ticker and ticker != entity_name:
            label = f"{entity_name} · {ticker}"
        elif ticker:
            label = ticker
        elif entity_name:
            label = entity_name
        elif pool_group:
            label = pool_group
        else:
            label = short_pool_id(pool_id)
        enriched.append(
            {
                "pool_id_bech32": pool_id,
                "label": label,
                "is_mpo": is_mpo,
                "entity_name": entity_name,
                "ticker": ticker,
                "reward_from_unmet_ada": parse_float(row["reward_from_unmet_ada"]),
                "pledge_unmet_epoch_cnt": unmet_epochs,
                "pledge_met_epoch_share_pct": parse_float(row["pledge_met_epoch_share_pct"]),
                "mean_active_stake_ada": parse_float(row["mean_active_stake_ada"]),
            }
        )

    enriched.sort(key=lambda r: (r["reward_from_unmet_ada"], r["pledge_unmet_epoch_cnt"]), reverse=True)
    top = enriched[:15]
    write_top_pools_csv(top, out_csv)

    band_labels = ["100%", "90-100%", "50-90%", "<50%", "No obs"]
    counts = [0, 0, 0, 0, 0]
    for row in pool_summary_rows:
        observed = parse_int(row["epochs_with_observed_pledge"])
        compliance = parse_float(row["pledge_met_epoch_share_pct"])
        if observed == 0:
            counts[4] += 1
        elif compliance >= 99.999:
            counts[0] += 1
        elif compliance >= 90.0:
            counts[1] += 1
        elif compliance >= 50.0:
            counts[2] += 1
        else:
            counts[3] += 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 8), gridspec_kw={"width_ratios": [1.0, 1.45]})
    fig.patch.set_facecolor(BG)
    for ax in (ax1, ax2):
        ax.set_facecolor(BG)
        ax.grid(axis="x" if ax is ax2 else "y", color=GRID, linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", colors=DIM)

    band_colors = [ACID_GREEN, "#66A61E", SOLAR_AMBER, INFARED, GREY]
    ax1.bar(band_labels, counts, color=band_colors, alpha=0.9)
    ax1.set_title("Lifetime compliance bands", fontsize=13, fontweight="bold", color=INK)
    ax1.set_ylabel("Pool count", color=INK)
    for i, value in enumerate(counts):
        ax1.text(i, value + max(counts) * 0.015, f"{value:,}", ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")

    labels = [r["label"] for r in top][::-1]
    rewards_m = [r["reward_from_unmet_ada"] / 1e6 for r in top][::-1]
    colors = [MPO_COLOR if r["is_mpo"] else INDIE_COLOR for r in top][::-1]
    y = np.arange(len(top))
    ax2.barh(y, rewards_m, color=colors, alpha=0.9)
    ax2.set_yticks(y, labels)
    ax2.set_xlabel("Realized rewards earned during unmet epochs (M ADA)", color=INK)
    ax2.set_title("Top pools by pledge-unmet reward exposure", fontsize=13, fontweight="bold", color=INK)
    for yi, row in zip(y, top[::-1]):
        ax2.text(
            row["reward_from_unmet_ada"] / 1e6 + max(rewards_m) * 0.012,
            yi,
            f"{row['pledge_unmet_epoch_cnt']} unmet ep. · {row['mean_active_stake_ada']/1e6:.1f}M avg stake",
            va="center",
            ha="left",
            fontsize=9,
            color=INK,
        )

    fig.suptitle("Where pledge-not-met exposure accumulates", fontsize=17, fontweight="bold", color=INK, y=0.98)
    fig.text(
        0.5,
        0.945,
        "Left: pool lifetime compliance bands over epoch 210-615 · Right: highest realized reward exposure during pledge-unmet epochs",
        ha="center",
        va="top",
        fontsize=10,
        color=DIM,
    )
    fig.text(0.72, 0.035, "Red = MPO-mapped pool · Green = independent / unmapped pool", fontsize=9, color=DIM, ha="center")
    fig.tight_layout(rect=[0.03, 0.08, 0.97, 0.92])
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def render_entity_exposure(pool_summary_rows: list[dict[str, str]], entity_by_pool, out_path: Path, out_csv: Path) -> None:
    entity_agg: dict[str, dict[str, float | str | int]] = {}
    total_unmet_reward = 0.0
    for row in pool_summary_rows:
        pool_id = row["pool_id_bech32"]
        entity_meta = entity_by_pool.get(pool_id)
        if entity_meta is None:
            continue
        entity_id = entity_meta["entity_id"]
        record = entity_agg.setdefault(
            entity_id,
            {
                "entity_id": entity_id,
                "display_name": entity_meta["display_name"],
                "archetype": entity_meta["archetype"],
                "reward_from_unmet_ada": 0.0,
                "pledge_unmet_epoch_cnt": 0,
                "pool_cnt": 0,
            },
        )
        record["reward_from_unmet_ada"] += parse_float(row["reward_from_unmet_ada"])
        record["pledge_unmet_epoch_cnt"] += parse_int(row["pledge_unmet_epoch_cnt"])
        record["pool_cnt"] += 1
        total_unmet_reward += parse_float(row["reward_from_unmet_ada"])

    rows = list(entity_agg.values())
    rows.sort(key=lambda r: (r["reward_from_unmet_ada"], r["pledge_unmet_epoch_cnt"]), reverse=True)
    top = rows[:15]

    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(top[0].keys()) + ["reward_share_of_mpo_unmet_pct"])
        writer.writeheader()
        for row in top:
            item = dict(row)
            item["reward_share_of_mpo_unmet_pct"] = (
                row["reward_from_unmet_ada"] / total_unmet_reward * 100.0 if total_unmet_reward else 0.0
            )
            writer.writerow(item)

    labels = [clean_text(r["display_name"], r["entity_id"]) for r in top][::-1]
    rewards_m = [r["reward_from_unmet_ada"] / 1e6 for r in top][::-1]
    colors = [ARCHETYPE_COLORS.get(str(r["archetype"]), GREY) for r in top][::-1]
    y = np.arange(len(top))

    fig, ax = plt.subplots(figsize=(14, 8.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", colors=DIM)

    ax.barh(y, rewards_m, color=colors, alpha=0.92)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Realized rewards earned during unmet epochs (M ADA)", color=INK)
    ax.set_title("Top MPO entities by pledge-unmet reward exposure", fontsize=17, fontweight="bold", color=INK, pad=14)
    fig.text(
        0.5,
        0.965,
        "Colors follow the §4 MPO archetype palette · coverage window: epoch 210-615",
        ha="center",
        va="top",
        fontsize=10,
        color=DIM,
    )

    for yi, row in zip(y, top[::-1]):
        ax.text(
            row["reward_from_unmet_ada"] / 1e6 + max(rewards_m) * 0.012,
            yi,
            f"{row['pledge_unmet_epoch_cnt']} unmet pool-epochs · {row['pool_cnt']} pools",
            va="center",
            ha="left",
            fontsize=9,
            color=INK,
        )

    ax.text(
        0.99,
        0.03,
        f"MPO-mapped unmet reward exposure over epoch 210-615: {total_unmet_reward/1e6:.1f}M ADA",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color=DIM,
    )

    fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.94])
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor=BG)
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    epoch_rows = load_csv(DATA_DIR / "pool_pledge_epoch_summary_mainnet.csv")
    pool_rows = load_csv(DATA_DIR / "pool_pledge_pool_summary_mainnet.csv")
    pool_labels, entity_by_pool = load_label_maps()

    render_history(epoch_rows, FIG_DIR / "pledge_unmet_history_mainnet.png")
    render_pool_exposure(
        pool_rows,
        pool_labels,
        entity_by_pool,
        FIG_DIR / "pledge_unmet_pool_exposure_mainnet.png",
        DATA_DIR / "pledge_unmet_top_pools_mainnet.csv",
    )
    render_entity_exposure(
        pool_rows,
        entity_by_pool,
        FIG_DIR / "pledge_unmet_mpo_entities_mainnet.png",
        DATA_DIR / "pledge_unmet_top_entities_mainnet.csv",
    )


if __name__ == "__main__":
    main()
