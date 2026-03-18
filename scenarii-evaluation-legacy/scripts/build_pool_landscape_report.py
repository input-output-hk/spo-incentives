#!/usr/bin/env python3
"""
Build a general pool landscape report for mainnet.

This is the canonical merged report:
- all current registered pools first
- pool parameters second
- entity / MPO concentration as a later section
- history after the current snapshot

Output:
- docs/pool-landscape-mainnet.md
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUTPUTS_DIR = ROOT / "outputs"
DATA_DIR = ROOT / "data"
FIGURES_DIR = ROOT / "figures"

OUT_DOC = DOCS_DIR / "pool-landscape-mainnet.md"
SNAPSHOT_FIG = FIGURES_DIR / "pool_network_snapshot_mainnet.png"
POOL_SIZE_CATEGORY_FIG = FIGURES_DIR / "pool_size_category_thresholds_mainnet.png"
POOL_SIZE_RAW_FIG = FIGURES_DIR / "pool_stake_by_size_category_mainnet.png"
POOL_SIZE_MIX_FIG = FIGURES_DIR / "pool_mix_by_size_mainnet.png"
PLEDGE_RATIO_HEALTHY_CORE_FIG = FIGURES_DIR / "pool_pledge_to_active_ratio_healthy_core_mainnet.png"
PLEDGE_RATIO_SUBSCALE_ACTIVE_FIG = FIGURES_DIR / "pool_pledge_to_active_ratio_subscale_active_mainnet.png"
POOL_SIZE_COUNT_HISTORY_FIG = FIGURES_DIR / "pool_positive_pool_count_by_size_history_mainnet.png"
POOL_SATURATION_COUNT_HISTORY_FIG = FIGURES_DIR / "pool_positive_pool_count_by_saturation_history_mainnet.png"
MPO_OVERVIEW_CSV = OUTPUTS_DIR / "mpo_entity_health_overview_mainnet.csv"
MPO_POOL_HEALTH_CSV = OUTPUTS_DIR / "mpo_entity_pool_health_mainnet.csv"
MPO_POOL_MAPPING_CSV = OUTPUTS_DIR / "mpo_entity_pool_mapping_mainnet.csv"
POOL_REWARD_SUMMARY_MD = OUTPUTS_DIR / "pool_reward_distribution_mainnet_summary.md"
POOL_PLEDGE_SUMMARY_MD = OUTPUTS_DIR / "pool_pledge_and_updates_mainnet_summary.md"
LOW_PLEDGE_HISTORY_CSV = OUTPUTS_DIR / "zero_pledge_large_pool_history_mainnet.csv"
POOL_HISTORY_CSV = DATA_DIR / "koios_pool_history_mainnet.csv"

MARKER_EPOCHS = [400, 410, 584]
KEY_HISTORY_EPOCHS = [400, 410, 441, 448, 583, 615, 617]
MPO_MIN_REGISTERED_POOLS = 2
REPORT_CHECKPOINT_EPOCH = 593
REPORT_CHECKPOINT_LABEL = "Prior report checkpoint\nNov 6, 2025"

POOL_SIZE_COUNT_CATEGORIES = [
    ("Dormant pools", "#f59e0b"),
    ("Subscale pools", "#0284c7"),
    ("Healthy pools", "#16a34a"),
    ("Large healthy pools", "#0f766e"),
    ("Near-saturation pools", "#f97316"),
    ("Saturated pools", "#dc2626"),
    ("Oversaturated pools", "#7c3aed"),
]

CURRENT_SIZE_CATEGORIES = [
    ("Zero-stake pools", "#6b7280"),
    ("Dormant pools", "#f59e0b"),
    ("Subscale pools", "#0284c7"),
    ("Healthy pools", "#16a34a"),
    ("Large healthy pools", "#0f766e"),
    ("Near-saturation pools", "#f97316"),
    ("Saturated pools", "#dc2626"),
    ("Oversaturated pools", "#7c3aed"),
]

POOL_SATURATION_THRESHOLDS = [50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
POOL_SATURATION_THRESHOLD_COLORS = [
    "#16a34a",
    "#22c55e",
    "#0284c7",
    "#f59e0b",
    "#dc2626",
    "#7c3aed",
]

CATEGORY_LABELS = {
    "declared_brand": "Declared MPO",
    "opaque_operational": "Opaque operational cluster",
    "provider_cluster": "Provider cluster",
    "platform_cluster": "Platform cluster",
    "unresolved_label": "Unresolved external label",
}

PRESSURE_LABELS = {
    "Very high": "Very high",
    "High": "High",
    "Moderate": "Moderate",
    "Limited": "Limited",
}

CURRENT_PLEDGE_BANDS = [
    ("0", "#7f1d1d", lambda value: value == 0.0),
    (">0 to <10k", "#dc2626", lambda value: 0.0 < value < 10_000.0),
    ("10k to <100k", "#f97316", lambda value: 10_000.0 <= value < 100_000.0),
    ("100k to <1M", "#f59e0b", lambda value: 100_000.0 <= value < 1_000_000.0),
    ("1M to <10M", "#14b8a6", lambda value: 1_000_000.0 <= value < 10_000_000.0),
    (">=10M", "#15803d", lambda value: value >= 10_000_000.0),
]

PLEDGE_RATIO_BANDS = [
    ("0%", "#7f1d1d", lambda value: value == 0.0),
    (">0 to <0.01%", "#dc2626", lambda value: 0.0 < value < 0.01),
    ("0.01% to <0.1%", "#f97316", lambda value: 0.01 <= value < 0.1),
    ("0.1% to <1%", "#f59e0b", lambda value: 0.1 <= value < 1.0),
    ("1% to <5%", "#84cc16", lambda value: 1.0 <= value < 5.0),
    ("5% to <10%", "#14b8a6", lambda value: 5.0 <= value < 10.0),
    ("10% to <25%", "#22c55e", lambda value: 10.0 <= value < 25.0),
    ("25% to <50%", "#16a34a", lambda value: 25.0 <= value < 50.0),
    ("50% to <100%", "#15803d", lambda value: 50.0 <= value < 100.0),
    (">=100%", "#166534", lambda value: value >= 100.0),
]

ENTITY_ACTIVITY_BULLETS = [
    "`Coinbase / bison.run`: exchange, custody, and institutional prime brokerage. The public business is [Coinbase Prime](https://www.coinbase.com/prime), not `bison.run`; Cardano staking sits alongside execution, financing, custody, and dedicated-validator products.",
    "`Binance`: global exchange plus custody, wallet, payments, and [Earn](https://www.binance.com/en/earn/version) products. The Cardano pools look more like exchange inventory than like a standalone SPO business.",
    "`Kiln`: institutional validator and staking infrastructure. [Kiln](https://www.kiln.fi/) sells staking, DeFi, and onchain asset infrastructure to enterprises and institutions.",
    "`Figment`: institutional staking provider. [Figment](https://figment.io/company/about/) serves asset managers, custodians, exchanges, wallets, and foundations with staking, APIs, reporting, and related infrastructure.",
    "`Blockdaemon`: institutional blockchain infrastructure. [Blockdaemon](https://www.blockdaemon.com/) combines node and API infrastructure, staking, DeFi access, and MPC wallet / vault products.",
    "`Everstake`: yield and validator infrastructure rather than a Cardano-only operator. [Everstake](https://everstake.one/) markets institutional staking, Validator-as-a-Service, and wallet / yield SDKs.",
    "`P2P`: staking-as-a-business infrastructure. [P2P.org](https://www.p2p.org/) focuses on APIs, white-label staking, and related products for wallets, exchanges, custodians, and asset managers.",
    "`Emurgo`: Cardano's commercial and venture arm rather than a pure SPO. [EMURGO](https://www.emurgo.io/about/) spans fintech, ventures, tokenization, and products such as Yoroi, USDA, and Anzens.",
    "`AutoStake`: small multi-chain validator operator. [AutoStake](https://autostake.com/) presents itself as a bare-metal validator business across several PoS networks, not just Cardano.",
    "`StakeBowl`: small staking and asset-services operator. [StakeBowl](https://stakebowl.io/) describes node operation, digital asset storage, investment, and asset management beyond Cardano pool operation.",
    "`BigLazyCat`: community and content-led operator. [BigLazyCat](https://www.biglazycat.com/stake-ada.html) combines an ADA pool with DRep activity, multi-chain validators, and community-facing content and token activity.",
    "`CHUCK BUX`: still low-confidence. The public first-party identity is weak; the strongest surviving signal is legacy `Staked / staked.cloud` metadata in the local registration history, which suggests institutional staking infrastructure rather than a transparent retail SPO brand.",
]


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def load_live_pool_rows() -> tuple[List[dict], Dict[str, dict], int, float, int]:
    rows: List[dict] = []
    offset = 0
    limit = 1000
    while True:
        page = fetch_json(f"https://api.koios.rest/api/v1/pool_list?offset={offset}&limit={limit}")
        if not isinstance(page, list):
            raise RuntimeError("Unexpected pool_list response")
        rows.extend(page)
        if len(page) < limit:
            break
        offset += len(page)

    tip = fetch_json("https://api.koios.rest/api/v1/tip")
    if not isinstance(tip, list) or not tip:
        raise RuntimeError("Unexpected tip response")
    live_epoch = int(tip[0]["epoch_no"])

    totals = fetch_json(f"https://api.koios.rest/api/v1/totals?_epoch_no={live_epoch}")
    if not isinstance(totals, list) or not totals:
        raise RuntimeError("Unexpected totals response")
    supply_ada = int(totals[0]["supply"]) / 1_000_000.0

    params = fetch_json(f"https://api.koios.rest/api/v1/epoch_params?_epoch_no={live_epoch}")
    if not isinstance(params, list) or not params:
        raise RuntimeError("Unexpected epoch_params response")
    optimal_pool_count = int(params[0]["optimal_pool_count"])

    return rows, {row["pool_id_bech32"]: row for row in rows}, live_epoch, supply_ada, optimal_pool_count


def load_supply_by_epoch() -> Dict[int, float]:
    totals = fetch_json("https://api.koios.rest/api/v1/totals")
    if not isinstance(totals, list):
        raise RuntimeError("Unexpected totals history response")
    return {int(row["epoch_no"]): int(row["supply"]) / 1_000_000.0 for row in totals}


def load_csv(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def registered_only(rows: Iterable[dict]) -> List[dict]:
    return [row for row in rows if str(row.get("pool_status") or "") == "registered"]


def positive_only(rows: Iterable[dict]) -> List[dict]:
    return [row for row in registered_only(rows) if stake_ada(row) > 0.0]


def stake_ada(row: dict) -> float:
    return int(row.get("active_stake") or 0) / 1_000_000.0


def pledge_ada(row: dict) -> float:
    return int(row.get("pledge") or 0) / 1_000_000.0


def margin_pct(row: dict) -> float:
    return float(row.get("margin") or 0.0) * 100.0


def fixed_cost_ada(row: dict) -> float:
    return int(row.get("fixed_cost") or 0) / 1_000_000.0


def median_or_zero(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def format_count(value: int) -> str:
    return f"{value:,}"


def format_pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}%"


def format_b_ada(value: float) -> str:
    return f"{value / 1_000_000_000.0:.3f}"


def format_m_ada(value: float) -> str:
    return f"{value / 1_000_000.0:.2f}"


def format_ada(value: float) -> str:
    if value == 0.0:
        return "0"
    if value < 0.001:
        return "<0.001"
    if value >= 1.0 and float(value).is_integer():
        return f"{value:,.0f}"
    if value >= 10_000.0:
        return f"{value:,.0f}"
    if value >= 1.0:
        return f"{value:,.3f}"
    return f"{value:.6f}"


def short_pool_id(pool_id: str) -> str:
    return pool_id if len(pool_id) <= 18 else f"{pool_id[:12]}...{pool_id[-6:]}"


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def format_compact_pct(value: float) -> str:
    return f"{value:.1f}%"


def add_report_checkpoint_marker(
    ax: plt.Axes,
    *,
    x: float = REPORT_CHECKPOINT_EPOCH,
    text_x_offset: float = 2.0,
    show_label: bool = True,
) -> None:
    ax.axvline(x, color="#7f8c8d", linestyle=":", linewidth=1.2, alpha=0.9, zorder=1)
    if show_label:
        ax.text(
            x + text_x_offset,
            0.97,
            REPORT_CHECKPOINT_LABEL,
            transform=ax.get_xaxis_transform(),
            ha="left",
            va="top",
            fontsize=9,
            color="#4b5563",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#d1d5db", alpha=0.92),
        )


def pool_size_count_bucket_label(stake_value_ada: float, saturation_pct: float) -> str:
    if 0.0 < stake_value_ada < 100_000.0:
        return "Dormant pools"
    if 100_000.0 <= stake_value_ada < 3_000_000.0:
        return "Subscale pools"
    if saturation_pct < 50.0:
        return "Healthy pools"
    if saturation_pct < 80.0:
        return "Large healthy pools"
    if saturation_pct < 95.0:
        return "Near-saturation pools"
    if saturation_pct < 105.0:
        return "Saturated pools"
    return "Oversaturated pools"


def current_size_category_label(stake_value_ada: float, saturation_point_ada: float) -> str:
    if stake_value_ada == 0.0:
        return "Zero-stake pools"
    saturation_pct = stake_value_ada / saturation_point_ada * 100.0 if saturation_point_ada else 0.0
    return pool_size_count_bucket_label(stake_value_ada, saturation_pct)


def pool_size_history_counts(
    live_rows: List[dict],
    live_epoch: int,
    saturation_point_ada: float,
) -> Dict[int, Dict[str, int]]:
    epoch_counts: Dict[int, Dict[str, int]] = defaultdict(
        lambda: {label: 0 for label, _ in POOL_SIZE_COUNT_CATEGORIES}
    )

    with POOL_HISTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_stake_ada = float(row.get("active_stake_ada") or 0.0)
            if active_stake_ada <= 0.0:
                continue
            epoch_no = int(row["epoch_no"])
            saturation_pct = float(row.get("saturation_pct") or 0.0)
            epoch_counts[epoch_no][pool_size_count_bucket_label(active_stake_ada, saturation_pct)] += 1

    live_counts = {label: 0 for label, _ in POOL_SIZE_COUNT_CATEGORIES}
    for row in positive_only(live_rows):
        live_saturation_pct = stake_ada(row) / saturation_point_ada * 100.0 if saturation_point_ada else 0.0
        live_counts[pool_size_count_bucket_label(stake_ada(row), live_saturation_pct)] += 1
    epoch_counts[live_epoch] = live_counts

    return {epoch: dict(counts) for epoch, counts in epoch_counts.items()}


def pool_size_history_stats(epoch_counts: Dict[int, Dict[str, int]], live_epoch: int) -> dict:
    epochs = sorted(epoch_counts)
    total_counts = {epoch: sum(epoch_counts[epoch].values()) for epoch in epochs}
    healthy_plus_labels = [
        "Healthy pools",
        "Large healthy pools",
        "Near-saturation pools",
        "Saturated pools",
        "Oversaturated pools",
    ]
    near_plus_labels = ["Near-saturation pools", "Saturated pools", "Oversaturated pools"]
    healthy_plus_counts = {
        epoch: sum(epoch_counts[epoch][label] for label in healthy_plus_labels)
        for epoch in epochs
    }
    near_plus_counts = {
        epoch: sum(epoch_counts[epoch][label] for label in near_plus_labels)
        for epoch in epochs
    }
    peak_total_epoch = max(epochs, key=lambda epoch: total_counts[epoch])
    peak_healthy_plus_epoch = max(epochs, key=lambda epoch: healthy_plus_counts[epoch])
    peak_near_plus_epoch = max(epochs, key=lambda epoch: near_plus_counts[epoch])
    peak_total_count = total_counts[peak_total_epoch]
    live_total_count = total_counts[live_epoch]
    return {
        "peak_total_epoch": peak_total_epoch,
        "peak_total_count": peak_total_count,
        "live_total_count": live_total_count,
        "live_vs_peak_total_pct": (live_total_count / peak_total_count * 100.0) if peak_total_count else 0.0,
        "peak_healthy_plus_epoch": peak_healthy_plus_epoch,
        "peak_healthy_plus_count": healthy_plus_counts[peak_healthy_plus_epoch],
        "live_healthy_plus_count": healthy_plus_counts[live_epoch],
        "peak_near_plus_epoch": peak_near_plus_epoch,
        "peak_near_plus_count": near_plus_counts[peak_near_plus_epoch],
        "live_near_plus_count": near_plus_counts[live_epoch],
    }


def build_pool_size_count_history_visual(
    live_rows: List[dict],
    live_epoch: int,
    saturation_point_ada: float,
    out_path: Path = POOL_SIZE_COUNT_HISTORY_FIG,
) -> Path:
    epoch_counts = pool_size_history_counts(live_rows, live_epoch, saturation_point_ada)
    epochs = sorted(epoch_counts)
    labels = [label for label, _ in POOL_SIZE_COUNT_CATEGORIES]
    series = {label: [epoch_counts[epoch].get(label, 0) for epoch in epochs] for label in labels}
    lower_regime_labels = ["Dormant pools", "Subscale pools"]
    upper_tail_labels = [label for label in labels if label not in lower_regime_labels]
    lower_regime_max = max(max(series[label]) for label in lower_regime_labels)
    upper_tail_max = max(max(series[label]) for label in upper_tail_labels)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(15.2, 9.2),
        sharex=True,
        gridspec_kw={"height_ratios": [2.25, 1.15], "hspace": 0.08},
    )
    fig.subplots_adjust(top=0.82, bottom=0.12, left=0.075, right=0.98)

    line_handles = []
    for label, color in POOL_SIZE_COUNT_CATEGORIES:
        if label in lower_regime_labels:
            line, = ax_top.plot(epochs, series[label], label=label, color=color, linewidth=2.5, alpha=0.98)
        else:
            line, = ax_bottom.plot(epochs, series[label], label=label, color=color, linewidth=2.1, alpha=0.96)
        line_handles.append(line)

    add_report_checkpoint_marker(ax_top, text_x_offset=1.8, show_label=True)
    add_report_checkpoint_marker(ax_bottom, text_x_offset=1.8, show_label=False)
    ax_top.set_title("Dormant and subscale pools", fontsize=13, loc="left", pad=10)
    ax_bottom.set_title("Healthy to oversaturated pools (zoomed)", fontsize=13, loc="left", pad=8)
    ax_top.set_ylabel("Pool count", fontsize=12.5)
    ax_bottom.set_ylabel("Pool count", fontsize=12.5)
    ax_bottom.set_xlabel("Epoch Number", fontsize=12.5)
    ax_top.set_xlim(min(epochs) - 5, max(epochs) + 15)
    ax_top.set_ylim(0, lower_regime_max * 1.06)
    ax_bottom.set_ylim(0, upper_tail_max * 1.18)
    if upper_tail_max <= 600:
        ax_bottom.set_yticks([0, 100, 200, 300, 400, 500, 600])
    ax_top.grid(alpha=0.28, linestyle=":")
    ax_bottom.grid(alpha=0.28, linestyle=":")
    fig.legend(
        handles=line_handles,
        labels=labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=4,
        framealpha=0.95,
        facecolor="white",
        edgecolor="#d1d5db",
        title="Pool size category",
        fontsize=10.5,
        title_fontsize=11.5,
    )
    for ax in (ax_top, ax_bottom):
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_pool_saturation_threshold_history_visual(
    live_rows: List[dict],
    live_epoch: int,
    saturation_point_ada: float,
    out_path: Path = POOL_SATURATION_COUNT_HISTORY_FIG,
) -> Path:
    threshold_counts: Dict[int, Dict[float, int]] = defaultdict(
        lambda: {threshold: 0 for threshold in POOL_SATURATION_THRESHOLDS}
    )

    with POOL_HISTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_stake_ada = float(row.get("active_stake_ada") or 0.0)
            if active_stake_ada <= 0.0:
                continue
            epoch_no = int(row["epoch_no"])
            saturation_pct = float(row.get("saturation_pct") or 0.0)
            for threshold in POOL_SATURATION_THRESHOLDS:
                if saturation_pct >= threshold:
                    threshold_counts[epoch_no][threshold] += 1

    live_counts = {threshold: 0 for threshold in POOL_SATURATION_THRESHOLDS}
    for row in positive_only(live_rows):
        live_saturation_pct = stake_ada(row) / saturation_point_ada * 100.0 if saturation_point_ada else 0.0
        for threshold in POOL_SATURATION_THRESHOLDS:
            if live_saturation_pct >= threshold:
                live_counts[threshold] += 1
    threshold_counts[live_epoch] = live_counts

    epochs = sorted(threshold_counts)
    labels = [f">={int(threshold)}% saturation" for threshold in POOL_SATURATION_THRESHOLDS]
    series = {
        label: [threshold_counts[epoch][threshold] for epoch in epochs]
        for label, threshold in zip(labels, POOL_SATURATION_THRESHOLDS)
    }

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(15.2, 7.8))
    fig.subplots_adjust(top=0.90, bottom=0.13, left=0.075, right=0.98)

    line_handles = []
    for label, color in zip(labels, POOL_SATURATION_THRESHOLD_COLORS):
        line, = ax.plot(epochs, series[label], label=label, color=color, linewidth=2.35, alpha=0.97)
        line_handles.append(line)

    add_report_checkpoint_marker(ax, text_x_offset=1.8, show_label=True)
    ax.set_xlabel("Epoch Number", fontsize=12.5)
    ax.set_ylabel("Pool count", fontsize=12.5)
    ax.set_xlim(min(epochs) - 5, max(epochs) + 15)
    ax.grid(alpha=0.28, linestyle=":")
    ax.legend(
        handles=line_handles,
        labels=labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        framealpha=0.95,
        facecolor="white",
        edgecolor="#d1d5db",
        title="Saturation threshold",
        fontsize=10.5,
        title_fontsize=11.5,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def current_snapshot(rows: List[dict], supply_ada: float, saturation_point_ada: float) -> dict:
    registered = registered_only(rows)
    positive = positive_only(rows)
    active_stake_ada = sum(stake_ada(row) for row in positive)
    sat95_ada = saturation_point_ada * 0.95
    sat105_ada = saturation_point_ada * 1.05
    large = [
        row for row in registered
        if saturation_point_ada and 50.0 <= stake_ada(row) / saturation_point_ada * 100.0 < 80.0
    ]
    ge80 = [
        row for row in registered
        if saturation_point_ada and stake_ada(row) / saturation_point_ada * 100.0 >= 80.0
    ]
    near = [
        row for row in registered
        if saturation_point_ada and 80.0 <= stake_ada(row) / saturation_point_ada * 100.0 < 95.0
    ]
    saturated = [
        row for row in registered
        if saturation_point_ada and sat95_ada <= stake_ada(row) < sat105_ada
    ]
    oversaturated = [
        row for row in registered
        if saturation_point_ada and stake_ada(row) >= sat105_ada
    ]
    return {
        "registered": len(registered),
        "positive": len(positive),
        "active_stake_ada": active_stake_ada,
        "active_stake_pct_supply": active_stake_ada / supply_ada * 100.0 if supply_ada else 0.0,
        "healthy": sum(1 for row in registered if stake_ada(row) >= 3_000_000.0),
        "subscale": sum(1 for row in registered if 100_000.0 <= stake_ada(row) < 3_000_000.0),
        "dormant": sum(1 for row in registered if 0.0 < stake_ada(row) < 100_000.0),
        "zero_stake": sum(1 for row in registered if stake_ada(row) == 0.0),
        "large": len(large),
        "near_saturation_ge80": len(ge80),
        "near_saturation": len(near),
        "saturated": len(saturated),
        "oversaturated": len(oversaturated),
        "zero_pledge": sum(1 for row in registered if pledge_ada(row) == 0.0),
        "very_low_pledge": sum(1 for row in registered if pledge_ada(row) < 10_000.0),
        "pledge_ada": sum(pledge_ada(row) for row in registered),
        "median_pledge_ada": median_or_zero([pledge_ada(row) for row in registered]),
        "median_margin_pct": median_or_zero([margin_pct(row) for row in registered]),
        "avg_margin_pct": statistics.mean([margin_pct(row) for row in registered]) if registered else 0.0,
        "median_fixed_cost_ada": median_or_zero([fixed_cost_ada(row) for row in registered]),
    }


def current_pledge_band_distribution(rows: List[dict]) -> List[dict]:
    registered = registered_only(rows)
    total_registered = len(registered)
    distribution: List[dict] = []
    for label, color, predicate in CURRENT_PLEDGE_BANDS:
        count = sum(1 for row in registered if predicate(pledge_ada(row)))
        distribution.append(
            {
                "label": label,
                "count": count,
                "share_pct": count / total_registered * 100.0 if total_registered else 0.0,
                "color": color,
            }
        )
    return distribution


def current_pledge_ratio_distribution(rows: List[dict], predicate: Callable[[dict], bool]) -> dict:
    registered = [row for row in registered_only(rows) if predicate(row)]
    positive = [row for row in registered if stake_ada(row) > 0.0]
    total_pools = len(positive)
    total_stake_ada = sum(stake_ada(row) for row in positive)
    ratios_pct = [pledge_ada(row) / stake_ada(row) * 100.0 for row in positive if stake_ada(row) > 0.0]

    distribution: List[dict] = []
    for label, color, predicate in PLEDGE_RATIO_BANDS:
        matched = [row for row in positive if predicate(pledge_ada(row) / stake_ada(row) * 100.0)]
        active_stake_ada = sum(stake_ada(row) for row in matched)
        distribution.append(
            {
                "label": label,
                "pool_count": len(matched),
                "pool_share_pct": len(matched) / total_pools * 100.0 if total_pools else 0.0,
                "active_stake_ada": active_stake_ada,
                "active_stake_share_pct": active_stake_ada / total_stake_ada * 100.0 if total_stake_ada else 0.0,
                "color": color,
            }
        )

    return {
        "bands": distribution,
        "registered_pool_count": len(registered),
        "positive_pool_count": total_pools,
        "zero_stake_excluded_count": len(registered) - total_pools,
        "median_ratio_pct": median_or_zero(ratios_pct),
        "mean_ratio_pct": statistics.mean(ratios_pct) if ratios_pct else 0.0,
        "active_stake_ada": total_stake_ada,
    }


def pledge_ratio_band_by_label(ratio_distribution: dict, label: str) -> dict:
    for row in ratio_distribution["bands"]:
        if row["label"] == label:
            return row
    raise KeyError(label)


def upper_tail_ratio_summary(ratio_distribution: dict) -> dict:
    upper_labels = ["10% to <25%", "25% to <50%", "50% to <100%", ">=100%"]
    upper_rows = [pledge_ratio_band_by_label(ratio_distribution, label) for label in upper_labels]
    return {
        "pool_count": sum(row["pool_count"] for row in upper_rows),
        "pool_share_pct": sum(row["pool_share_pct"] for row in upper_rows),
        "active_stake_ada": sum(row["active_stake_ada"] for row in upper_rows),
        "active_stake_share_pct": sum(row["active_stake_share_pct"] for row in upper_rows),
        "bands": upper_rows,
    }


def ratio_band_detail_line(row: dict) -> str:
    return (
        f"**{row['label']}**: {format_count(row['pool_count'])} pools ({format_pct(row['pool_share_pct'])}), "
        f"{format_b_ada(row['active_stake_ada'])}B ADA ({format_pct(row['active_stake_share_pct'])})"
    )


def build_snapshot_visual(
    snapshot: dict,
    supply_ada: float,
    live_epoch: int,
    saturation_point_ada: float,
    optimal_pool_count: int,
    out_path: Path = SNAPSHOT_FIG,
) -> Path:
    remaining_supply_ada = max(supply_ada - snapshot["active_stake_ada"], 0.0)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax_supply = plt.subplots(figsize=(13.5, 3.6))
    fig.subplots_adjust(top=0.94, bottom=0.20, left=0.06, right=0.98)

    active_pct = snapshot["active_stake_pct_supply"]
    inactive_pct = max(100.0 - active_pct, 0.0)
    ax_supply.barh([0], [active_pct], color="#0f766e", height=0.42)
    ax_supply.barh([0], [inactive_pct], left=[active_pct], color="#d1d5db", height=0.42)
    ax_supply.set_xlim(0, 100)
    ax_supply.set_yticks([])
    ax_supply.set_xticks([0, 25, 50, 75, 100])
    ax_supply.set_xticklabels([f"{tick}%" for tick in [0, 25, 50, 75, 100]])
    ax_supply.text(
        max(active_pct / 2.0, 5.0),
        0,
        f"{format_b_ada(snapshot['active_stake_ada'])}B ADA\n{format_pct(active_pct)} active",
        ha="center",
        va="center",
        fontsize=12,
        color="white",
        fontweight="bold",
    )
    ax_supply.text(
        active_pct + inactive_pct / 2.0,
        0,
        f"{format_b_ada(remaining_supply_ada)}B ADA\nrest of supply",
        ha="center",
        va="center",
        fontsize=11,
        color="#1f2937",
        fontweight="bold",
    )
    for spine in ax_supply.spines.values():
        spine.set_visible(False)

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_pool_size_category_visual(
    break_even_stake_ada: float,
    sat50_ada: float,
    sat80_ada: float,
    sat95_ada: float,
    sat105_ada: float,
    live_epoch: int,
    saturation_point_ada: float,
    out_path: Path = POOL_SIZE_CATEGORY_FIG,
) -> Path:
    bottom_rows = [
        ("Healthy pools", "#16a34a", break_even_stake_ada, sat50_ada),
        ("Large healthy pools", "#0f766e", sat50_ada, sat80_ada),
        ("Near-saturation pools", "#f97316", sat80_ada, sat95_ada),
        ("Saturated pools", "#dc2626", sat95_ada, sat105_ada),
    ]

    oversat_end = sat105_ada + max(8_000_000.0, 0.18 * sat105_ada)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(15.2, 6.15),
        gridspec_kw={"height_ratios": [0.95, 1.15]},
    )
    fig.subplots_adjust(top=0.94, bottom=0.10, left=0.05, right=0.985, hspace=0.16)

    for ax in (ax_top, ax_bottom):
        ax.set_ylim(0.0, 1.0)
        ax.axis("off")

    ax_bottom.set_xlim(break_even_stake_ada, oversat_end)

    ax_top.text(
        0.0,
        0.95,
        "0 ADA to the 3M viability line",
        transform=ax_top.transAxes,
        fontsize=11.5,
        color="#334155",
        fontweight="bold",
        ha="left",
        va="center",
    )
    ax_bottom.text(
        0.0,
        0.95,
        "Saturation-based upper tail",
        transform=ax_bottom.transAxes,
        fontsize=11.5,
        color="#334155",
        fontweight="bold",
        ha="left",
        va="center",
    )

    def draw_range_bar(ax: plt.Axes, x0: float, x1: float, y: float, height: float, color: str) -> None:
        patch = FancyBboxPatch(
            (x0, y - height / 2.0),
            x1 - x0,
            height,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            facecolor=color,
            edgecolor="white",
            linewidth=1.5,
            alpha=0.98,
            transform=ax.transData,
            clip_on=False,
        )
        ax.add_patch(patch)

    def draw_axes_bar(ax: plt.Axes, x0: float, x1: float, y: float, height: float, color: str) -> None:
        patch = Rectangle(
            (x0, y - height / 2.0),
            x1 - x0,
            height,
            facecolor=color,
            edgecolor="none",
            linewidth=0.0,
            alpha=0.98,
            transform=ax.transAxes,
            clip_on=False,
        )
        ax.add_patch(patch)

    def draw_thresholds(ax: plt.Axes, markers: List[tuple[float, str]]) -> None:
        x_start = markers[0][0]
        x_end = markers[-1][0]
        ax.plot([x_start, x_end], [0.24, 0.24], color="#cbd5e1", lw=1.2)
        for x, label in markers:
            ax.plot([x, x], [0.24, 0.47], color="#94a3b8", lw=1.35)
            ax.scatter([x], [0.24], s=30, color="#334155", zorder=5)
            ax.text(
                x,
                0.10,
                label,
                ha="center",
                va="top",
                fontsize=9.7,
                color="#334155",
            )

    top_zero_x0 = 0.02
    top_zero_x1 = 0.12
    top_zero_anchor = (top_zero_x0 + top_zero_x1) / 2.0
    top_dormant_x0 = top_zero_x1
    top_dormant_x1 = 0.255
    top_subscale_x0 = top_dormant_x1
    top_subscale_x1 = 0.97

    draw_axes_bar(ax_top, top_zero_x0, top_zero_x1, 0.58, 0.22, "#6b7280")
    draw_axes_bar(ax_top, top_dormant_x0, top_dormant_x1, 0.58, 0.22, "#f59e0b")
    draw_axes_bar(ax_top, top_subscale_x0, top_subscale_x1, 0.58, 0.22, "#0284c7")
    ax_top.text(
        (top_zero_x0 + top_zero_x1) / 2.0,
        0.60,
        "Zero-stake\npools",
        transform=ax_top.transAxes,
        ha="center",
        va="center",
        fontsize=9.8,
        color="white",
        fontweight="bold",
    )
    ax_top.text(
        (top_dormant_x0 + top_dormant_x1) / 2.0,
        0.60,
        "Dormant\npools",
        transform=ax_top.transAxes,
        ha="center",
        va="center",
        fontsize=9.8,
        color="white",
        fontweight="bold",
    )
    ax_top.text(
        (top_subscale_x0 + top_subscale_x1) / 2.0,
        0.60,
        "Subscale pools",
        transform=ax_top.transAxes,
        ha="center",
        va="center",
        fontsize=13.2,
        color="white",
        fontweight="bold",
    )

    wrapped_bottom_labels = {
        "Near-saturation pools": "Near-saturation\npools",
        "Saturated pools": "Saturated\npools",
        "Oversaturated pools": "Oversaturated\npools",
    }

    for label, color, x0, x1 in bottom_rows:
        draw_range_bar(ax_bottom, x0, x1, 0.58, 0.22, color)
        mid = (x0 + x1) / 2.0
        width = x1 - x0
        font_size = 11.7
        if width < 12_000_000.0:
            font_size = 10.6
        if width < 9_000_000.0:
            font_size = 9.7
        display_label = wrapped_bottom_labels.get(label, label)
        ax_bottom.text(
            mid,
            0.60,
            display_label,
            ha="center",
            va="center",
            fontsize=font_size,
            color="white",
            fontweight="bold",
        )

    draw_range_bar(ax_bottom, sat105_ada, oversat_end, 0.58, 0.22, "#7c3aed")
    ax_bottom.text(
        sat105_ada + (oversat_end - sat105_ada) * 0.46,
        0.60,
        "Oversaturated\npools",
        ha="center",
        va="center",
        fontsize=10.4,
        color="white",
        fontweight="bold",
    )
    ax_bottom.annotate(
        "",
        xy=(oversat_end, 0.58),
        xytext=(sat105_ada + (oversat_end - sat105_ada) * 0.78, 0.58),
        arrowprops={"arrowstyle": "->", "lw": 2.0, "color": "#7c3aed"},
    )

    ax_top.plot([top_zero_anchor, top_subscale_x1], [0.24, 0.24], color="#cbd5e1", lw=1.2, transform=ax_top.transAxes)
    for x in (top_zero_anchor, top_dormant_x1, top_subscale_x1):
        ax_top.plot([x, x], [0.24, 0.47], color="#94a3b8", lw=1.35, transform=ax_top.transAxes)
        ax_top.scatter([x], [0.24], s=30, color="#334155", zorder=5, transform=ax_top.transAxes)
    ax_top.text(top_zero_anchor, 0.10, "0 ADA", transform=ax_top.transAxes, ha="center", va="top", fontsize=9.7, color="#334155")
    ax_top.text(top_dormant_x1, 0.10, "100k ADA", transform=ax_top.transAxes, ha="center", va="top", fontsize=9.7, color="#334155")
    ax_top.text(
        top_subscale_x1,
        0.10,
        f"{format_m_ada(break_even_stake_ada)}M ADA\nviability line",
        transform=ax_top.transAxes,
        ha="center",
        va="top",
        fontsize=9.7,
        color="#334155",
    )
    draw_thresholds(
        ax_bottom,
        [
            (break_even_stake_ada, f"{format_m_ada(break_even_stake_ada)}M ADA\nviability line"),
            (sat50_ada, f"50% sat\n~{format_m_ada(sat50_ada)}M ADA"),
            (sat80_ada, f"80% sat\n~{format_m_ada(sat80_ada)}M ADA"),
            (sat95_ada, f"95% sat\n~{format_m_ada(sat95_ada)}M ADA"),
            (sat105_ada, f"105% sat\n~{format_m_ada(sat105_ada)}M ADA"),
        ],
    )

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_pool_size_mix_visual(
    size_distribution: List[dict],
    live_epoch: int,
    out_path: Path = POOL_SIZE_MIX_FIG,
) -> Path:
    labels = [row["label"] for row in size_distribution]
    pool_shares = [row["share_pct"] for row in size_distribution]
    stake_shares = [row["active_stake_share_pct"] for row in size_distribution]
    colors = [
        "#6b7280",
        "#f59e0b",
        "#0284c7",
        "#16a34a",
        "#0f766e",
        "#f97316",
        "#dc2626",
        "#7c3aed",
    ][: len(size_distribution)]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.2, 7.8), sharey=True)
    fig.subplots_adjust(top=0.94, bottom=0.14, left=0.28, right=0.97, wspace=0.22)

    bars1 = ax1.barh(labels, pool_shares, color=colors, height=0.66)
    ax1.set_title("Share of pools", fontsize=13, loc="left")
    ax1.set_xlabel("% of currently registered pools", fontsize=10.5)
    ax1.set_xlim(0, max(50.0, max(pool_shares, default=0.0) + 8.0))
    ax1.invert_yaxis()
    for bar, row in zip(bars1, size_distribution):
        ax1.text(
            bar.get_width() + 0.9,
            bar.get_y() + bar.get_height() / 2.0,
            f"{format_count(row['count'])} ({format_compact_pct(row['share_pct'])})",
            va="center",
            fontsize=10.5,
            color="#111827",
            fontweight="bold",
        )

    bars2 = ax2.barh(labels, stake_shares, color=colors, height=0.66)
    ax2.set_title("Share of active stake", fontsize=13, loc="left")
    ax2.set_xlabel("% of current active stake", fontsize=10.5)
    ax2.set_xlim(0, max(40.0, max(stake_shares, default=0.0) + 8.0))
    for bar, row in zip(bars2, size_distribution):
        ax2.text(
            bar.get_width() + 0.9,
            bar.get_y() + bar.get_height() / 2.0,
            f"{format_b_ada(row['active_stake_ada'])}B ({format_compact_pct(row['active_stake_share_pct'])})",
            va="center",
            fontsize=10.5,
            color="#111827",
            fontweight="bold",
        )

    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_pool_size_raw_visual(
    rows: List[dict],
    saturation_point_ada: float,
    sat50_ada: float,
    sat80_ada: float,
    sat95_ada: float,
    sat105_ada: float,
    out_path: Path = POOL_SIZE_RAW_FIG,
) -> Path:
    registered = registered_only(rows)
    colors = {label: color for label, color in CURRENT_SIZE_CATEGORIES}
    max_stake_ada = max((stake_ada(row) for row in registered), default=sat105_ada)
    linear_tick_step = 10_000_000.0
    x_axis_max = max(max_stake_ada * 1.03, sat105_ada * 1.08)
    tick_count = int(math.ceil(x_axis_max / linear_tick_step))
    x_ticks = [idx * linear_tick_step for idx in range(tick_count + 1)]
    x_tick_labels = ["0 ADA"] + [f"{int(tick / 1_000_000):d}M" for tick in x_ticks[1:]]
    threshold_lines = [100_000.0, 3_000_000.0, sat50_ada, sat80_ada, sat95_ada, sat105_ada]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(15.2, 4.9))
    fig.subplots_adjust(top=0.82, bottom=0.24, left=0.06, right=0.98)

    category_stakes: Dict[str, List[float]] = defaultdict(list)
    for row in sorted(registered, key=stake_ada):
        category_stakes[current_size_category_label(stake_ada(row), saturation_point_ada)].append(stake_ada(row))

    for label, _ in CURRENT_SIZE_CATEGORIES:
        stakes = category_stakes.get(label, [])
        if not stakes:
            continue
        y_values = [0.38 * math.sin((idx + 1) * 12.9898) for idx in range(len(stakes))]
        ax.scatter(
            stakes,
            y_values,
            s=18,
            color=colors[label],
            alpha=0.60,
            edgecolors="none",
            zorder=3,
            label=label,
        )

    for x in threshold_lines:
        ax.axvline(x, color="#cbd5e1", linewidth=1.0, linestyle="--", alpha=0.85, zorder=0)

    ax.set_xlim(-500_000.0, x_axis_max)
    ax.set_ylim(-0.48, 0.48)
    ax.set_yticks([])
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels, fontsize=10)
    ax.set_xlabel("Current active stake per registered pool (ADA; dashed lines mark category thresholds)", fontsize=10.5)
    ax.grid(axis="x", alpha=0.18)
    ax.grid(axis="y", alpha=0.0)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.16),
        ncol=4,
        frameon=True,
        facecolor="white",
        edgecolor="#d1d5db",
        fontsize=10,
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_pledge_ratio_visual(
    ratio_distribution: dict,
    title_prefix: str,
    subtitle: str,
    live_epoch: int,
    out_path: Path,
) -> Path:
    bands = ratio_distribution["bands"]
    labels = [row["label"] for row in bands]
    colors = [row["color"] for row in bands]
    pool_shares = [row["pool_share_pct"] for row in bands]
    stake_shares = [row["active_stake_share_pct"] for row in bands]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.2, 7.8), sharey=True)
    fig.subplots_adjust(top=0.95, bottom=0.18, left=0.20, right=0.97, wspace=0.22)

    bars1 = ax1.barh(labels, pool_shares, color=colors, height=0.66)
    ax1.set_title("Share of pools", fontsize=13, loc="left")
    ax1.set_xlabel("% of positive-stake registered pools", fontsize=10.5)
    ax1.set_xlim(0, max(50.0, max(pool_shares, default=0.0) + 8.0))
    ax1.invert_yaxis()
    for bar, row in zip(bars1, bands):
        ax1.text(
            bar.get_width() + 1.0,
            bar.get_y() + bar.get_height() / 2.0,
            f"{format_count(row['pool_count'])} ({format_compact_pct(row['pool_share_pct'])})",
            va="center",
            fontsize=10.5,
            color="#111827",
            fontweight="bold",
        )

    bars2 = ax2.barh(labels, stake_shares, color=colors, height=0.66)
    ax2.set_title("Share of current active stake", fontsize=13, loc="left")
    ax2.set_xlabel("% of active stake in positive-stake pools", fontsize=10.5)
    ax2.set_xlim(0, max(35.0, max(stake_shares, default=0.0) + 8.0))
    for bar, row in zip(bars2, bands):
        ax2.text(
            bar.get_width() + 0.9,
            bar.get_y() + bar.get_height() / 2.0,
            f"{format_b_ada(row['active_stake_ada'])}B ({format_compact_pct(row['active_stake_share_pct'])})",
            va="center",
            fontsize=10.5,
            color="#111827",
            fontweight="bold",
        )

    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_visible(False)

    fig.text(
        0.20,
        0.08,
        f"Median ratio: {format_pct(ratio_distribution['median_ratio_pct'])}   |   Pools covered: {format_count(ratio_distribution['positive_pool_count'])}   |   Active stake covered: {format_b_ada(ratio_distribution['active_stake_ada'])}B ADA",
        fontsize=10.5,
        color="#475569",
    )

    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path


def band_distribution(
    rows: List[dict],
    active_stake_total_ada: float,
    supply_ada: float,
    bands: List[tuple[str, Callable[[dict], bool]]],
) -> List[dict]:
    total_registered = len(rows)
    distribution: List[dict] = []
    for label, predicate in bands:
        matched = [row for row in rows if predicate(row)]
        stake_total = sum(stake_ada(row) for row in matched)
        distribution.append(
            {
                "label": label,
                "count": len(matched),
                "share_pct": len(matched) / total_registered * 100.0 if total_registered else 0.0,
                "active_stake_ada": stake_total,
                "active_stake_share_pct": stake_total / active_stake_total_ada * 100.0 if active_stake_total_ada else 0.0,
                "supply_share_pct": stake_total / supply_ada * 100.0 if supply_ada else 0.0,
            }
        )
    return distribution


def band_rows(
    rows: List[dict],
    active_stake_total_ada: float,
    supply_ada: float,
    bands: List[tuple[str, Callable[[dict], bool]]],
) -> List[List[str]]:
    out: List[List[str]] = []
    for row in band_distribution(rows, active_stake_total_ada, supply_ada, bands):
        out.append(
            [
                row["label"],
                format_count(row["count"]),
                format_pct(row["share_pct"]),
                format_b_ada(row["active_stake_ada"]),
                format_pct(row["active_stake_share_pct"]),
                format_pct(row["supply_share_pct"]),
            ]
        )
    return out


def load_entity_by_pool() -> Dict[str, str]:
    return {row["pool_id_bech32"]: row["display_name"] for row in load_csv(MPO_POOL_HEALTH_CSV)}


def current_top_pools(rows: List[dict], entity_by_pool: Dict[str, str], saturation_point_ada: float) -> List[List[str]]:
    ranked = sorted(registered_only(rows), key=stake_ada, reverse=True)
    out: List[List[str]] = []
    for row in ranked[:20]:
        out.append(
            [
                entity_by_pool.get(row["pool_id_bech32"], "-"),
                str(row.get("ticker") or "N/A"),
                short_pool_id(row["pool_id_bech32"]),
                format_m_ada(stake_ada(row)),
                format_pct(stake_ada(row) / saturation_point_ada * 100.0 if saturation_point_ada else 0.0),
                format_ada(pledge_ada(row)),
                format_pct(margin_pct(row)),
                format_ada(fixed_cost_ada(row)),
            ]
        )
    return out


def top_pool_concentration(rows: List[dict], active_stake_total_ada: float, supply_ada: float) -> dict[int, dict[str, float]]:
    ranked = sorted((stake_ada(row) for row in positive_only(rows)), reverse=True)
    out: dict[int, dict[str, float]] = {}
    for n in (10, 50, 100):
        subtotal = sum(ranked[:n])
        out[n] = {
            "stake_ada": subtotal,
            "share_active_stake_pct": subtotal / active_stake_total_ada * 100.0 if active_stake_total_ada else 0.0,
            "share_supply_pct": subtotal / supply_ada * 100.0 if supply_ada else 0.0,
        }
    return out


def entity_context_from_pools(current_pool_rows: List[dict]) -> Dict[str, dict]:
    context: Dict[str, dict] = {}
    for row in current_pool_rows:
        context.setdefault(
            row["display_name"],
            {
                "category": row["category"],
                "confidence": row["confidence"],
                "claim_type": row["claim_type"],
            },
        )
    return context


def current_entity_rows(overview_rows: List[dict], context_by_entity: Dict[str, dict]) -> List[List[str]]:
    ranked = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    out: List[List[str]] = []
    for row in ranked:
        context = context_by_entity[row["display_name"]]
        out.append(
            [
                row["display_name"],
                CATEGORY_LABELS.get(context["category"], context["category"]),
                row["current_registered_pool_count"],
                row["current_live_positive_pool_count"],
                format_b_ada(float(row["current_stake_ada"])),
                format_pct(float(row["current_pct_supply"])),
                row["healthy_core_pool_count"],
                row["near_saturation_pool_count"],
                format_ada(float(row["median_live_pledge_ada"])),
                format_pct(float(row["avg_live_margin_pct"])),
                PRESSURE_LABELS.get(row["decentralization_pressure_tag"], row["decentralization_pressure_tag"]),
            ]
        )
    return out


def low_pledge_entity_rows(
    current_pool_rows: List[dict],
    live_rows_by_id: Dict[str, dict],
    saturation_point_ada: float,
) -> List[List[str]]:
    per_entity: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in current_pool_rows:
        entity = row["display_name"]
        live = live_rows_by_id[row["pool_id_bech32"]]
        pledge = pledge_ada(live)
        active = stake_ada(live)
        near = (active / saturation_point_ada * 100.0) >= 80.0 if saturation_point_ada else False
        per_entity[entity]["registered"] += 1
        if pledge < 10_000.0:
            per_entity[entity]["very_low_count"] += 1
            per_entity[entity]["very_low_stake_ada"] += active
            if near:
                per_entity[entity]["very_low_near_count"] += 1
                per_entity[entity]["very_low_near_stake_ada"] += active
        if pledge == 0.0:
            per_entity[entity]["zero_count"] += 1

    ranked = sorted(per_entity.items(), key=lambda item: item[1].get("very_low_near_stake_ada", 0.0), reverse=True)
    out: List[List[str]] = []
    for entity, stats in ranked[:12]:
        if stats.get("very_low_count", 0.0) == 0.0:
            continue
        out.append(
            [
                entity,
                format_count(int(stats["registered"])),
                format_count(int(stats["zero_count"])),
                format_count(int(stats["very_low_count"])),
                format_b_ada(stats["very_low_stake_ada"]),
                format_count(int(stats.get("very_low_near_count", 0.0))),
                format_b_ada(stats.get("very_low_near_stake_ada", 0.0)),
            ]
        )
    return out


def attributed_top_pools(current_pool_rows: List[dict], live_rows_by_id: Dict[str, dict]) -> List[List[str]]:
    ranked = sorted(current_pool_rows, key=lambda row: float(row["current_active_stake_ada"]), reverse=True)
    out: List[List[str]] = []
    for row in ranked[:20]:
        live = live_rows_by_id[row["pool_id_bech32"]]
        out.append(
            [
                row["display_name"],
                row["ticker"] or "N/A",
                short_pool_id(row["pool_id_bech32"]),
                format_m_ada(float(row["current_active_stake_ada"])),
                format_pct(float(row["current_pct_saturation"])),
                format_ada(pledge_ada(live)),
                format_pct(float(row["margin_pct"])),
                format_ada(float(row["fixed_cost_ada"])),
            ]
        )
    return out


def current_pressure_bullets(overview_rows: List[dict]) -> List[str]:
    rows = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    bullets: List[str] = []
    if rows:
        top = rows[0]
        bullets.append(
            f"{top['display_name']} remains the largest cluster with {format_pct(float(top['current_pct_supply']))} of supply "
            f"and {top['current_registered_pool_count']} registered pools."
        )
    high_margin = sorted(
        [row for row in overview_rows if float(row["avg_live_margin_pct"]) >= 90.0],
        key=lambda row: float(row["current_pct_supply"]),
        reverse=True,
    )
    if high_margin:
        bullets.append(
            "The clusters with very high average margin are "
            + ", ".join(
                f"{row['display_name']} ({format_pct(float(row['avg_live_margin_pct']))}, {format_pct(float(row['current_pct_supply']))} of supply)"
                for row in high_margin[:5]
            )
            + "."
        )
    thin = [row for row in rows if int(row["current_live_positive_pool_count"]) < int(row["current_registered_pool_count"])]
    if thin:
        bullets.append(
            "The landscape is not homogeneous: "
            + ", ".join(
                f"{row['display_name']} ({row['current_live_positive_pool_count']}/{row['current_registered_pool_count']} with stake)"
                for row in thin[:4]
            )
            + "."
        )
    return bullets


def attributed_set_summary(overview_rows: List[dict], network_snapshot_row: dict, supply_ada: float) -> dict:
    stake_ada = sum(float(row["current_stake_ada"]) for row in overview_rows)
    registered = sum(int(row["current_registered_pool_count"]) for row in overview_rows)
    near_sat = sum(int(row["near_saturation_pool_count"]) for row in overview_rows)
    return {
        "stake_ada": stake_ada,
        "registered": registered,
        "share_supply_pct": stake_ada / supply_ada * 100.0 if supply_ada else 0.0,
        "share_registered_pct": registered / network_snapshot_row["registered"] * 100.0 if network_snapshot_row["registered"] else 0.0,
        "share_near_sat_pct": near_sat / network_snapshot_row["near_saturation_ge80"] * 100.0 if network_snapshot_row["near_saturation_ge80"] else 0.0,
    }


def stacked_graph_snapshot(
    overview_rows: List[dict],
    current_pool_rows: List[dict],
    live_rows_by_id: Dict[str, dict],
    supply_ada: float,
    network_snapshot_row: dict,
) -> dict:
    selected_entities = {
        row["display_name"]
        for row in overview_rows
        if int(row["current_registered_pool_count"]) >= MPO_MIN_REGISTERED_POOLS
    }
    selected_rows: List[dict] = []
    seen_pool_ids: set[str] = set()
    for row in current_pool_rows:
        if row["display_name"] not in selected_entities:
            continue
        pool_id = row["pool_id_bech32"]
        if pool_id in seen_pool_ids:
            continue
        seen_pool_ids.add(pool_id)
        live = live_rows_by_id[pool_id]
        if str(live.get("pool_status") or "") != "registered":
            continue
        selected_rows.append(live)

    stake_total = sum(stake_ada(row) for row in selected_rows)
    pledge_total = sum(pledge_ada(row) for row in selected_rows)
    return {
        "entities": len(selected_entities),
        "registered_pools": len(selected_rows),
        "stake_ada": stake_total,
        "stake_pct_consensus": stake_total / network_snapshot_row["active_stake_ada"] * 100.0 if network_snapshot_row["active_stake_ada"] else 0.0,
        "stake_pct_supply": stake_total / supply_ada * 100.0 if supply_ada else 0.0,
        "pledge_ada": pledge_total,
        "pledge_pct_network": pledge_total / network_snapshot_row["pledge_ada"] * 100.0 if network_snapshot_row["pledge_ada"] else 0.0,
        "pledge_pct_supply": pledge_total / supply_ada * 100.0 if supply_ada else 0.0,
        "active_over_pledge": stake_total / pledge_total if pledge_total else 0.0,
    }


def pick_summary_lines(path: Path, prefixes: List[str]) -> List[str]:
    lines = path.read_text().splitlines()
    return [line for line in lines if any(line.startswith(prefix) for prefix in prefixes)]


def load_low_pledge_history() -> Dict[int, dict]:
    return {int(row["epoch_no"]): row for row in load_csv(LOW_PLEDGE_HISTORY_CSV)}


def key_history_rows(low_pledge_history: Dict[int, dict]) -> List[List[str]]:
    rows: List[List[str]] = []
    for epoch_no in KEY_HISTORY_EPOCHS:
        row = low_pledge_history.get(epoch_no)
        if row is None:
            continue
        source_label = {
            "local_history": "local history",
            "live_koios": "live snapshot",
        }.get(row["source"], row["source"])
        rows.append(
            [
                str(epoch_no),
                source_label,
                row["gt70_pool_count"],
                row["very_low_pledge_gt70_pool_count"],
                row["zero_pledge_gt70_pool_count"],
                row["very_low_pledge_ge80sat_pool_count"],
                row["zero_pledge_ge80sat_pool_count"],
            ]
        )
    return rows


def build_history_markers(mapping_rows: List[dict], supply_by_epoch: Dict[int, float]) -> tuple[dict[str, dict[int, float]], dict[int, float]]:
    pool_to_entity = {row["pool_id_bech32"]: row["display_name"] for row in mapping_rows}
    entity_epoch_stake: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    total_by_epoch: dict[int, float] = defaultdict(float)

    with POOL_HISTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity_name = pool_to_entity.get(row["pool_id_bech32"])
            if entity_name is None:
                continue
            epoch_no = int(row["epoch_no"])
            if epoch_no not in MARKER_EPOCHS:
                continue
            active_stake_ada = float(row["active_stake_ada"])
            entity_epoch_stake[entity_name][epoch_no] += active_stake_ada
            total_by_epoch[epoch_no] += active_stake_ada

    entity_markers: dict[str, dict[int, float]] = defaultdict(dict)
    total_markers: dict[int, float] = {}
    entities = {row["display_name"] for row in mapping_rows}
    for epoch_no in MARKER_EPOCHS:
        supply_ada = supply_by_epoch[epoch_no]
        total_markers[epoch_no] = total_by_epoch[epoch_no] / supply_ada * 100.0 if supply_ada else 0.0
        for entity_name in entities:
            stake_total = entity_epoch_stake[entity_name].get(epoch_no, 0.0)
            entity_markers[entity_name][epoch_no] = stake_total / supply_ada * 100.0 if supply_ada else 0.0
    return entity_markers, total_markers


def entity_history_rows(overview_rows: List[dict], entity_markers: dict[str, dict[int, float]], top_n: int = 15) -> List[List[str]]:
    ranked = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    rows: List[List[str]] = []
    for row in ranked[:top_n]:
        current_pct = float(row["current_pct_supply"])
        rows.append(
            [
                row["display_name"],
                format_pct(entity_markers[row["display_name"]].get(400, 0.0)),
                format_pct(entity_markers[row["display_name"]].get(410, 0.0)),
                format_pct(entity_markers[row["display_name"]].get(584, 0.0)),
                format_pct(current_pct),
                f"{current_pct - entity_markers[row['display_name']].get(400, 0.0):+.2f} pts",
            ]
        )
    return rows


def entity_history_shift_bullets(overview_rows: List[dict], entity_markers: dict[str, dict[int, float]]) -> List[str]:
    diffs_400: List[tuple[float, str]] = []
    diffs_584: List[tuple[float, str]] = []
    for row in overview_rows:
        name = row["display_name"]
        current_pct = float(row["current_pct_supply"])
        diffs_400.append((current_pct - entity_markers[name].get(400, 0.0), name))
        diffs_584.append((current_pct - entity_markers[name].get(584, 0.0), name))

    down_400 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_400)[:5])
    up_400 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_400, reverse=True)[:5])
    down_584 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_584)[:5])
    up_584 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_584, reverse=True)[:5])
    return [
        f"Since epoch 400, the largest declines are {down_400}.",
        f"Since epoch 400, the largest increases are {up_400}.",
        f"Since epoch 584, the declines are more limited: {down_584}.",
        f"Since epoch 584, the most visible increases are {up_584}.",
    ]


def write_report() -> Path:
    live_rows, live_by_id, live_epoch, supply_ada, optimal_pool_count = load_live_pool_rows()
    registered_rows = registered_only(live_rows)
    saturation_point_ada = supply_ada / optimal_pool_count
    break_even_stake_ada = 3_000_000.0
    sat50_ada = saturation_point_ada * 0.50
    sat80_ada = saturation_point_ada * 0.80
    sat95_ada = saturation_point_ada * 0.95
    sat105_ada = saturation_point_ada * 1.05
    size_bands = [
        ("Zero-stake pools (0 ADA)", lambda row: stake_ada(row) == 0.0),
        ("Dormant pools (>0 to <100k ADA)", lambda row: 0.0 < stake_ada(row) < 100_000.0),
        (f"Subscale pools (100k to <{format_m_ada(break_even_stake_ada)}M ADA)", lambda row: 100_000.0 <= stake_ada(row) < break_even_stake_ada),
        (
            f"Healthy pools ({format_m_ada(break_even_stake_ada)}M ADA to <50% saturation)",
            lambda row: break_even_stake_ada <= stake_ada(row) < sat50_ada,
        ),
        ("Large healthy pools (50% to <80% saturation)", lambda row: sat50_ada <= stake_ada(row) < sat80_ada),
        ("Near-saturation pools (80% to <95% saturation)", lambda row: sat80_ada <= stake_ada(row) < sat95_ada),
        ("Saturated pools (95% to <105% saturation)", lambda row: sat95_ada <= stake_ada(row) < sat105_ada),
        ("Oversaturated pools (>=105% saturation)", lambda row: stake_ada(row) >= sat105_ada),
    ]

    snapshot = current_snapshot(live_rows, supply_ada, saturation_point_ada)
    entity_by_pool = load_entity_by_pool()
    current_pool_rows = load_csv(MPO_POOL_HEALTH_CSV)
    overview_rows = load_csv(MPO_OVERVIEW_CSV)
    mapping_rows = load_csv(MPO_POOL_MAPPING_CSV)
    attributed = attributed_set_summary(overview_rows, snapshot, supply_ada)
    stacked_graph = stacked_graph_snapshot(overview_rows, current_pool_rows, live_by_id, supply_ada, snapshot)
    supply_by_epoch = load_supply_by_epoch()
    entity_markers, total_markers = build_history_markers(mapping_rows, supply_by_epoch)
    low_pledge_history = load_low_pledge_history()
    context_by_entity = entity_context_from_pools(current_pool_rows)
    pressure_bullets = current_pressure_bullets(overview_rows)
    history_shift_bullets = entity_history_shift_bullets(overview_rows, entity_markers)
    healthy_core_ratio_distribution = current_pledge_ratio_distribution(
        live_rows,
        lambda row: stake_ada(row) >= 3_000_000.0,
    )
    subscale_active_ratio_distribution = current_pledge_ratio_distribution(
        live_rows,
        lambda row: 100_000.0 <= stake_ada(row) < 3_000_000.0,
    )
    build_snapshot_visual(snapshot, supply_ada, live_epoch, saturation_point_ada, optimal_pool_count)
    build_pool_size_category_visual(
        break_even_stake_ada,
        sat50_ada,
        sat80_ada,
        sat95_ada,
        sat105_ada,
        live_epoch,
        saturation_point_ada,
    )
    build_pool_size_raw_visual(
        live_rows,
        saturation_point_ada,
        sat50_ada,
        sat80_ada,
        sat95_ada,
        sat105_ada,
    )
    size_distribution = band_distribution(
        registered_rows,
        snapshot["active_stake_ada"],
        supply_ada,
        size_bands,
    )
    zero_dist, dormant_dist, subscale_dist, healthy_dist, large_dist, near_dist, saturated_dist, oversaturated_dist = size_distribution
    live_low_count = zero_dist["count"] + dormant_dist["count"] + subscale_dist["count"]
    live_low_share_pct = zero_dist["share_pct"] + dormant_dist["share_pct"] + subscale_dist["share_pct"]
    live_low_stake_share_pct = dormant_dist["active_stake_share_pct"] + subscale_dist["active_stake_share_pct"]
    live_healthy_plus_count = healthy_dist["count"] + large_dist["count"] + near_dist["count"] + saturated_dist["count"] + oversaturated_dist["count"]
    live_healthy_plus_stake_share_pct = healthy_dist["active_stake_share_pct"] + large_dist["active_stake_share_pct"] + near_dist["active_stake_share_pct"] + saturated_dist["active_stake_share_pct"] + oversaturated_dist["active_stake_share_pct"]
    live_near_plus_count = near_dist["count"] + saturated_dist["count"] + oversaturated_dist["count"]
    live_near_plus_stake_ada = near_dist["active_stake_ada"] + saturated_dist["active_stake_ada"] + oversaturated_dist["active_stake_ada"]
    live_near_plus_stake_share_pct = near_dist["active_stake_share_pct"] + saturated_dist["active_stake_share_pct"] + oversaturated_dist["active_stake_share_pct"]
    build_pool_size_mix_visual(size_distribution, live_epoch)
    build_pool_size_count_history_visual(live_rows, live_epoch, saturation_point_ada)
    size_history_stats = pool_size_history_stats(pool_size_history_counts(live_rows, live_epoch, saturation_point_ada), live_epoch)
    build_pledge_ratio_visual(
        healthy_core_ratio_distribution,
        "Healthy Pools",
        "Current registered pools at or above the viability line (~3M ADA).",
        live_epoch,
        PLEDGE_RATIO_HEALTHY_CORE_FIG,
    )
    build_pledge_ratio_visual(
        subscale_active_ratio_distribution,
        "Subscale Pools",
        "Current registered pools with 100k to below the viability line (~3M ADA).",
        live_epoch,
        PLEDGE_RATIO_SUBSCALE_ACTIVE_FIG,
    )
    healthy_core_upper_tail = upper_tail_ratio_summary(healthy_core_ratio_distribution)
    subscale_active_upper_tail = upper_tail_ratio_summary(subscale_active_ratio_distribution)

    pledge_table = markdown_table(
        ["Declared pledge band", "Pools", "% registered pools", "Active stake (B ADA)", "% current active stake", "% supply"],
        band_rows(
            registered_rows,
            snapshot["active_stake_ada"],
            supply_ada,
            [
                ("Zero-pledge pools (0 ADA)", lambda row: pledge_ada(row) == 0.0),
                ("Micro-pledge pools (>0 to <10k ADA)", lambda row: 0.0 < pledge_ada(row) < 10_000.0),
                ("Low-pledge pools (10k to <100k ADA)", lambda row: 10_000.0 <= pledge_ada(row) < 100_000.0),
                ("Modest-pledge pools (100k to <1M ADA)", lambda row: 100_000.0 <= pledge_ada(row) < 1_000_000.0),
                ("Material-pledge pools (1M to <10M ADA)", lambda row: 1_000_000.0 <= pledge_ada(row) < 10_000_000.0),
                ("High-pledge pools (>=10M ADA)", lambda row: pledge_ada(row) >= 10_000_000.0),
            ],
        ),
    )

    margin_table = markdown_table(
        ["Margin band", "Pools", "% registered pools", "Active stake (B ADA)", "% current active stake", "% supply"],
        band_rows(
            registered_rows,
            snapshot["active_stake_ada"],
            supply_ada,
            [
                ("Zero-margin pools (0%)", lambda row: margin_pct(row) == 0.0),
                ("Low-margin pools (>0 to <3%)", lambda row: 0.0 < margin_pct(row) < 3.0),
                ("Standard-margin pools (3% to <5%)", lambda row: 3.0 <= margin_pct(row) < 5.0),
                ("Elevated-margin pools (5% to <10%)", lambda row: 5.0 <= margin_pct(row) < 10.0),
                ("High-margin pools (10% to <100%)", lambda row: 10.0 <= margin_pct(row) < 100.0),
                ("Private-margin pools (100%)", lambda row: margin_pct(row) == 100.0),
            ],
        ),
    )

    fixed_cost_table = markdown_table(
        ["Fixed cost regime", "Pools", "% registered pools", "Active stake (B ADA)", "% current active stake", "% supply"],
        band_rows(
            registered_rows,
            snapshot["active_stake_ada"],
            supply_ada,
            [
                ("Min-cost pools (170 ADA)", lambda row: fixed_cost_ada(row) == 170.0),
                ("Standard-cost pools (340 ADA)", lambda row: fixed_cost_ada(row) == 340.0),
                ("Non-standard-cost pools (other)", lambda row: fixed_cost_ada(row) not in {170.0, 340.0}),
            ],
        ),
    )

    pledge_category_definition_table = markdown_table(
        ["Category", "Definition used downstream"],
        [
            ["Zero-pledge pools", "Declared pledge exactly `0 ADA`."],
            ["Micro-pledge pools", "Declared pledge `>0` and `<10k ADA`."],
            ["Low-pledge pools", "Declared pledge `10k` to `<100k ADA`."],
            ["Modest-pledge pools", "Declared pledge `100k` to `<1M ADA`."],
            ["Material-pledge pools", "Declared pledge `1M` to `<10M ADA`."],
            ["High-pledge pools", "Declared pledge `>=10M ADA`."],
        ],
    )

    margin_category_definition_table = markdown_table(
        ["Category", "Definition used downstream"],
        [
            ["Zero-margin pools", "Declared margin exactly `0%`."],
            ["Low-margin pools", "Declared margin `>0` and `<3%`."],
            ["Standard-margin pools", "Declared margin `3%` to `<5%`."],
            ["Elevated-margin pools", "Declared margin `5%` to `<10%`."],
            ["High-margin pools", "Declared margin `10%` to `<100%`."],
            ["Private-margin pools", "Declared margin exactly `100%`."],
        ],
    )

    fixed_cost_category_definition_table = markdown_table(
        ["Category", "Definition used downstream"],
        [
            ["Min-cost pools", "Declared fixed cost exactly `170 ADA`."],
            ["Standard-cost pools", "Declared fixed cost exactly `340 ADA`."],
            ["Non-standard-cost pools", "Declared fixed cost outside the `170 / 340 ADA` regimes."],
        ],
    )

    entity_table = markdown_table(
        [
            "Entity / cluster",
            "Type",
            "Registered pools",
            "Pools with stake",
            "Stake (B ADA)",
            "% supply",
            "Healthy core",
            "Near sat",
            "Median pledge",
            "Avg margin",
            "Pressure",
        ],
        current_entity_rows(overview_rows, context_by_entity),
    )

    low_pledge_entity_table = markdown_table(
        [
            "Entity / cluster",
            "Registered pools",
            "Zero pledge",
            "<10k pledge",
            "Stake <10k (B)",
            "<10k & >=80% sat",
            "Stake <10k & >=80% sat (B)",
        ],
        low_pledge_entity_rows(current_pool_rows, live_by_id, saturation_point_ada),
    )

    attributed_top_pools_table = markdown_table(
        ["Entity", "Ticker", "Pool", "Stake (M ADA)", "% sat", "Pledge", "Margin", "Fixed cost"],
        attributed_top_pools(current_pool_rows, live_by_id),
    )

    entity_history_table = markdown_table(
        ["Entity / cluster", "Epoch 400", "Epoch 410", "Epoch 584", f"Epoch {live_epoch}", "Delta 400 -> live"],
        entity_history_rows(overview_rows, entity_markers),
    )

    low_pledge_key_epochs_table = markdown_table(
        ["Epoch", "Source", ">70M pools", ">70M & pledge <10k", ">70M & zero pledge", ">=80% sat & pledge <10k", ">=80% sat & zero pledge"],
        key_history_rows(low_pledge_history),
    )

    pledge_compliance_lines = pick_summary_lines(
        POOL_PLEDGE_SUMMARY_MD,
        [
            "- Median epoch pledge-met share",
            "- Latest epoch pledge-met share",
            "- Full-window realized rewards linked to pledge-unmet pool-epochs",
            "- Pools with perfect observed compliance",
            "- Pools below 90% observed compliance",
        ],
    )
    margin_history_lines = pick_summary_lines(POOL_PLEDGE_SUMMARY_MD, ["- Latest median active margin"])
    fixed_cost_history_lines = pick_summary_lines(POOL_PLEDGE_SUMMARY_MD, ["- Latest share of pools at 340 ADA fixed cost"])
    update_history_lines = pick_summary_lines(POOL_PLEDGE_SUMMARY_MD, ["- Total pool updates observed"])

    now_dt = datetime.now(timezone.utc)
    now_utc = now_dt.strftime("%Y-%m-%d %H:%M UTC")
    snapshot_label = f"{now_dt.strftime('%B')} {now_dt.day}, {now_dt.year}"
    toc_entries = [
        {
            "number": "1",
            "title": "Network statistics",
            "anchor": "1-network-statistics",
            "children": [],
        },
        {
            "number": "2",
            "title": "Stake and rewards",
            "anchor": "2-stake-and-rewards",
            "children": [
                {
                    "number": "2.1",
                    "title": "Categorization",
                    "anchor": "21-categorization",
                    "children": [],
                },
                {
                    "number": "2.2",
                    "title": "Pool mix by size",
                    "anchor": "22-pool-mix-by-size",
                    "children": [
                        {"number": "2.2.1", "title": "Live", "anchor": "221-live", "children": []},
                        {"number": "2.2.2", "title": "Historical", "anchor": "222-historical", "children": []},
                    ],
                },
                {
                    "number": "2.3",
                    "title": "Reward distribution",
                    "anchor": "23-reward-distribution",
                    "children": [
                        {"number": "2.3.1", "title": "Live", "anchor": "231-live", "children": []},
                        {"number": "2.3.2", "title": "Historical", "anchor": "232-historical", "children": []},
                    ],
                },
            ],
        },
        {
            "number": "3",
            "title": "Entity and MPO concentration",
            "anchor": "3-entity-and-mpo-concentration",
            "children": [
                {"number": "3.1", "title": "Entity landscape", "anchor": "31-entity-landscape", "children": []},
                {"number": "3.2", "title": "MPO low-pledge pattern", "anchor": "32-mpo-low-pledge-pattern", "children": []},
                {
                    "number": "3.3",
                    "title": "Historical entity and MPO concentration history",
                    "anchor": "33-historical-entity-and-mpo-concentration-history",
                    "children": [],
                },
            ],
        },
        {
            "number": "4",
            "title": "Operator fees",
            "anchor": "4-operator-fees",
            "children": [
                {
                    "number": "4.1",
                    "title": "Margin",
                    "anchor": "41-margin",
                    "children": [
                        {
                            "number": "4.1.1",
                            "title": "Current margin regimes",
                            "anchor": "411-current-margin-regimes",
                            "children": [],
                        },
                        {"number": "4.1.2", "title": "Margin read", "anchor": "412-margin-read", "children": []},
                        {
                            "number": "4.1.3",
                            "title": "Historical margin read",
                            "anchor": "413-historical-margin-read",
                            "children": [],
                        },
                    ],
                },
                {
                    "number": "4.2",
                    "title": "Fixed cost",
                    "anchor": "42-fixed-cost",
                    "children": [
                        {
                            "number": "4.2.1",
                            "title": "Current fixed-cost regimes",
                            "anchor": "421-current-fixed-cost-regimes",
                            "children": [],
                        },
                        {"number": "4.2.2", "title": "Fixed-cost read", "anchor": "422-fixed-cost-read", "children": []},
                        {
                            "number": "4.2.3",
                            "title": "Historical fixed-cost read",
                            "anchor": "423-historical-fixed-cost-read",
                            "children": [],
                        },
                    ],
                },
            ],
        },
        {
            "number": "5",
            "title": "Pledge",
            "anchor": "5-pledge",
            "children": [
                {"number": "5.1", "title": "Current pledge bands", "anchor": "51-current-pledge-bands", "children": []},
                {
                    "number": "5.2",
                    "title": "Declared pledge relative to current active stake by pool scale",
                    "anchor": "52-declared-pledge-relative-to-current-active-stake-by-pool-scale",
                    "children": [],
                },
                {"number": "5.3", "title": "Historical pledge compliance", "anchor": "53-historical-pledge-compliance", "children": []},
                {
                    "number": "5.4",
                    "title": "Historical large low-pledge pool history",
                    "anchor": "54-historical-large-low-pledge-pool-history",
                    "children": [],
                },
            ],
        },
        {"number": "6", "title": "Method and caution", "anchor": "6-method-and-caution", "children": []},
        {"number": "7", "title": "Companion documents", "anchor": "7-companion-documents", "children": []},
    ]

    def render_toc(entries: List[dict], indent: str = "") -> List[str]:
        lines: List[str] = []
        for entry in entries:
            number = entry["number"]
            title = entry["title"]
            anchor = entry["anchor"]
            if indent:
                lines.append(f"{indent}- [{title}](#{anchor})")
            else:
                lines.append(f"{number}. [{title}](#{anchor})")
            children = entry.get("children", [])
            if children:
                lines.extend(render_toc(children, indent + "   "))
        return lines

    toc = "\n".join(render_toc(toc_entries))

    doc = f"""# Pool Landscape Report (Mainnet) - Snapshot {snapshot_label}

_Built on {now_utc} from live mainnet data at epoch `{live_epoch}` plus the local historical analysis already present in this workspace._

## Objective

This is the **single canonical landscape report** for current pool structure, pool parameters, entity / MPO concentration, and history.
It opens with a dated **network statistics** snapshot, then moves into overall stake structure, pool parameters, entity concentration, and history.

All current counts below use **currently registered pools only**.
Retired pools are excluded from current pool counts and from current live stake totals.

The pool operating parameters explicitly analyzed here are **declared pledge**, **margin**, and **fixed cost**. Other fields such as owners, reward addresses, relays, and metadata URLs are used for attribution rather than treated as headline operating parameters.

## Contents

{toc}

## 1. Network statistics

- Live epoch: **{live_epoch}**
- Circulating supply used here: **{format_b_ada(supply_ada)}B ADA**
- Current live active stake in registered pools: **{format_b_ada(snapshot['active_stake_ada'])}B ADA** (**{format_pct(snapshot['active_stake_pct_supply'])}** of supply)
- Protocol `k`: **{optimal_pool_count}**
- Approximate saturation point: **{format_m_ada(saturation_point_ada)}M ADA per pool**

![Current network snapshot at a glance](../figures/pool_network_snapshot_mainnet.png)

## 2. Stake and rewards

### 2.1 Categorization

The report uses the prior report’s **`3M ADA` viability line** plus a small set of saturation anchors to describe the upper tail.

Here, the `3M ADA` viability line keeps the prior report’s meaning: it marks the shift from sporadic block production toward more regular rewards. It is not presented here as a universal profitability guarantee.

At epoch `{live_epoch}`, the saturation point used here is approximately **{format_m_ada(saturation_point_ada)}M ADA per pool**.

![Pool size category thresholds](../figures/pool_size_category_thresholds_mainnet.png)

### 2.2 Pool mix by size

#### 2.2.1 Live

- **{format_count(live_low_count)}** pools (**{format_pct(live_low_share_pct)}**) sit at zero stake, dormant, or subscale levels; together they carry only **{format_pct(live_low_stake_share_pct)}** of current active stake.
- The **{format_count(live_healthy_plus_count)}** pools at or above the viability line carry **{format_pct(live_healthy_plus_stake_share_pct)}** of current active stake.
- The **{format_count(live_near_plus_count)}** pools from near-saturation upward carry **{format_b_ada(live_near_plus_stake_ada)}B ADA** (**{format_pct(live_near_plus_stake_share_pct)}** of current active stake).

![Current registered pools by stake and size category](../figures/pool_stake_by_size_category_mainnet.png)

![Pool mix by size](../figures/pool_mix_by_size_mainnet.png)

#### 2.2.2 Historical

- Positive-stake pools peaked at **{format_count(size_history_stats['peak_total_count'])}** in epoch `{size_history_stats['peak_total_epoch']}`; the live point is **{format_count(size_history_stats['live_total_count'])}** at epoch `{live_epoch}` (**{format_pct(size_history_stats['live_vs_peak_total_pct'])}** of that peak).
- Pools at or above the viability line peaked at **{format_count(size_history_stats['peak_healthy_plus_count'])}** in epoch `{size_history_stats['peak_healthy_plus_epoch']}`; the live point is **{format_count(size_history_stats['live_healthy_plus_count'])}**.
- Under each epoch's own saturation point, the near-saturation-and-above layer peaked at **{format_count(size_history_stats['peak_near_plus_count'])}** pools in epoch `{size_history_stats['peak_near_plus_epoch']}`; the live point is **{format_count(size_history_stats['live_near_plus_count'])}**.

![Positive-stake pool count by size](../figures/pool_positive_pool_count_by_size_history_mainnet.png)

### 2.3 Reward distribution

#### 2.3.1 Live

![Recent reward distribution by size](../figures/pool_reward_distribution_by_size_recent_mainnet.png)

#### 2.3.2 Historical

![Reward distribution by size](../figures/pool_reward_distribution_by_size_mainnet.png)

## 3. Entity and MPO concentration

This theme isolates the attributed entity layer rather than treating pools only as standalone registrations.
The attributed entity set currently covers **{format_count(attributed['registered'])}** registered pools, or **{format_pct(attributed['share_registered_pct'])}** of registered pools by count, but **{format_pct(attributed['share_supply_pct'])}** of total supply by stake.
It also captures **{format_pct(attributed['share_near_sat_pct'])}** of near-saturation pools.

![Current MPO entity distribution](../figures/mpo_entity_current_distribution_mainnet.png)

### 3.1 Entity landscape

{entity_table}

Current read:
"""
    doc += "\n".join(f"- {line}" for line in pressure_bullets)
    doc += f"""

#### What these entities do beyond SPO

The largest names in the attributed MPO layer are not homogeneous. Some are exchanges and custodians, some are institutional validator providers, and only a smaller tail looks like classic retail or community pool operation.

"""
    doc += "\n".join(f"- {line}" for line in ENTITY_ACTIVITY_BULLETS)
    doc += f"""

### 3.2 MPO low-pledge pattern

The next table isolates the current low-pledge pattern inside the attributed set. This is the configuration that usually drives MPO concern: many registered pools, low declared pledge, and still meaningful delegated stake.

{low_pledge_entity_table}

The largest current pools inside the attributed set are summarized below.
These rows use the live pledge field directly, which avoids conflating a true exact zero with a tiny non-zero micro-pledge.

{attributed_top_pools_table}

### 3.3 Historical entity and MPO concentration history

Across the current attributed entity set, the combined share was:

- **{format_pct(total_markers[400])}** at epoch `400`
- **{format_pct(total_markers[410])}** at epoch `410`
- **{format_pct(total_markers[584])}** at epoch `584`
- **{format_pct(attributed['share_supply_pct'])}** at live epoch `{live_epoch}`

The stacked composition view below shows how that total was internally distributed across the attributed entities with at least two currently registered pools.

![Historical MPO composition](../figures/mpo_entity_progression_stacked_mainnet.png)

On the same `>=2 pools` basis, this cohort currently covers **{format_count(stacked_graph['registered_pools'])} pools** across **{stacked_graph['entities']} entities** and represents:

- **{format_b_ada(stacked_graph['stake_ada'])}B ADA** of active stake, equal to **{format_pct(stacked_graph['stake_pct_consensus'])}** of stake currently participating in consensus (**{format_pct(stacked_graph['stake_pct_supply'])}** of circulating supply)
- **{format_b_ada(stacked_graph['pledge_ada'])}B ADA** of declared pledge, equal to **{format_pct(stacked_graph['pledge_pct_network'])}** of all declared pledge across currently registered pools (**{format_pct(stacked_graph['pledge_pct_supply'])}** of circulating supply)
- roughly **{stacked_graph['active_over_pledge']:.2f}x** active stake over declared pledge

{entity_history_table}

"""
    doc += "\n".join(f"- {line}" for line in history_shift_bullets)
    doc += f"""

## 4. Operator fees

Margin is the operator's variable skim on pool rewards. It is analytically distinct from pledge and from fixed cost, so it is treated on its own here.

### 4.1 Margin

#### 4.1.1 Current margin regimes

{margin_table}

#### 4.1.2 Margin read

- Median margin today is **{format_pct(snapshot['median_margin_pct'])}**.
- Average margin today is **{format_pct(snapshot['avg_margin_pct'])}**.
- A non-trivial fraction of stake still sits in `100%` margin pools, even though these are a minority of pools by count.

#### 4.1.3 Historical margin read

"""
    doc += "\n".join(margin_history_lines)
    doc += f"""
- The median active margin remained structurally low, around **2%**, even while low-pledge pools remained common.

### 4.2 Fixed cost

Fixed cost is the flat fee floor on pool rewards. It should be read separately from margin because it bites small pools differently from large pools, so it is treated on its own here.

#### 4.2.1 Current fixed-cost regimes

{fixed_cost_table}

#### 4.2.2 Fixed-cost read

- Median fixed cost today is **{format_ada(snapshot['median_fixed_cost_ada'])} ADA**.
- `340 ADA` remains the dominant fixed-cost regime.

#### 4.2.3 Historical fixed-cost read

"""
    doc += "\n".join(fixed_cost_history_lines)
    doc += f"""
- The fixed-cost baseline converged strongly around **340 ADA**.

## 5. Pledge

This section isolates declared pledge as its own analytical surface and starts with the current pledge-band view before moving into ratio and history.

### 5.1 Current pledge bands

{pledge_table}

### 5.2 Declared pledge relative to current active stake by pool scale

#### Healthy pools (>= viability line, ~3M ADA)

![Healthy pools pledge ratio](../figures/pool_pledge_to_active_ratio_healthy_core_mainnet.png)

- The median live ratio is **{format_pct(healthy_core_ratio_distribution['median_ratio_pct'])}** across **{format_count(healthy_core_ratio_distribution['positive_pool_count'])}** healthy-core pools.
- **>=10% combined**: **{format_count(healthy_core_upper_tail['pool_count'])}** pools (**{format_pct(healthy_core_upper_tail['pool_share_pct'])}**), carrying **{format_b_ada(healthy_core_upper_tail['active_stake_ada'])}B ADA** (**{format_pct(healthy_core_upper_tail['active_stake_share_pct'])}**).
- {ratio_band_detail_line(pledge_ratio_band_by_label(healthy_core_ratio_distribution, '10% to <25%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(healthy_core_ratio_distribution, '25% to <50%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(healthy_core_ratio_distribution, '50% to <100%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(healthy_core_ratio_distribution, '>=100%'))}

#### Subscale pools (100k to < viability line, ~3M ADA)

![Subscale pools pledge ratio](../figures/pool_pledge_to_active_ratio_subscale_active_mainnet.png)

- The median live ratio is **{format_pct(subscale_active_ratio_distribution['median_ratio_pct'])}** across **{format_count(subscale_active_ratio_distribution['positive_pool_count'])}** subscale-active pools.
- **>=10% combined**: **{format_count(subscale_active_upper_tail['pool_count'])}** pools (**{format_pct(subscale_active_upper_tail['pool_share_pct'])}**), carrying **{format_b_ada(subscale_active_upper_tail['active_stake_ada'])}B ADA** (**{format_pct(subscale_active_upper_tail['active_stake_share_pct'])}**).
- {ratio_band_detail_line(pledge_ratio_band_by_label(subscale_active_ratio_distribution, '10% to <25%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(subscale_active_ratio_distribution, '25% to <50%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(subscale_active_ratio_distribution, '50% to <100%'))}
- {ratio_band_detail_line(pledge_ratio_band_by_label(subscale_active_ratio_distribution, '>=100%'))}

### 5.3 Historical pledge compliance

![Pledge compliance](../figures/pool_pledge_compliance_mainnet.png)

"""
    doc += "\n".join(pledge_compliance_lines)
    doc += f"""

Historical read:

- The pledge proxy does not show a world where non-compliance dominates rewards, but it is still large enough to matter analytically.
- Low pledge and failed pledge are not the same thing: one is a choice of declared skin in the game, the other is a failure to meet a declared threshold.

### 5.4 Historical large low-pledge pool history

![Low-pledge large-pool history](../figures/zero_pledge_large_pool_history_mainnet.png)

{low_pledge_key_epochs_table}

Historical read:

- The major structural break is the jump beginning at **epoch 441** and extending through roughly **epoch 448**.
- By epoch `583`, the report-comparable `>70M ADA` bucket already contained **34** pools below **10k ADA** pledge and **24** exact zero-pledge pools.
- Live epoch `{live_epoch}` remains in the same broad regime rather than showing a brand-new recent explosion.

## 6. Method and caution

- The live sections use the current mainnet snapshot at epoch `{live_epoch}` on **{snapshot_label}**.
- Current counts keep only **currently registered** pools. Retired pools are intentionally excluded from "today" counts.
- Entity attribution inherits the current MPO mapping and deep-dive work. It is strongest where first-party metadata, branded tickers, and repeated relay or domain signals converge.
- The stacked historical MPO figure keeps only attributed entities with **at least two currently registered pools**.
- `Zero pledge` means exact zero in the raw pledge field. Tiny non-zero micro-pledges are not counted as zero.
- `Very low pledge` means declared pledge strictly below **10,000 ADA**.
- The live pledge-ratio figures use **declared pledge / current active stake** as the current proxy. Zero-stake registered pools are excluded from that ratio because the denominator is zero.
- Historical entity markers are reconstructed from the local pool history export plus epoch supply.
- The large-pool low-pledge history uses pledge declaration updates, not just owner snapshots, because owner snapshots materially undercount many large low-pledge pools.

## 7. Companion documents

- `../docs/pool-reward-distribution-mainnet.md`
- `../docs/pool-pledge-and-updates-mainnet.md`
- `../outputs/mpo_entity_deep_dive_mainnet.md`
- `../outputs/mpo_entity_pool_table_mainnet.md`
- `../outputs/mpo_entity_pool_health_mainnet.csv`
"""

    OUT_DOC.write_text(doc)
    return OUT_DOC


def main() -> None:
    out_path = write_report()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
