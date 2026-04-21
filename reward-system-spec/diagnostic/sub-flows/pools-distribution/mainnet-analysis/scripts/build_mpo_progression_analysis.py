#!/usr/bin/env python3
"""
Build a raw-data MPO progression summary and chart.

Outputs:
- scenarii-evaluation/figures/mpo_progression_proxy_mainnet.png
- scenarii-evaluation/outputs/mpo_progression_proxy_mainnet_summary.md
- scenarii-evaluation/outputs/mpo_progression_proxy_key_epochs_mainnet.csv

Method:
- Historical pool stake comes from the local Koios pool history export.
- A reconstructed MPO basket is built from stable metadata/ticker signatures.
- A broad comparator uses Koios `pool_group` labels where a group has at least 2 pools.
- Current epoch values are fetched live from Koios to provide an external check.
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


@dataclass(frozen=True)
class KeyEpochRow:
    epoch_no: int
    source: str
    proxy_stake_b_ada: float
    proxy_pct_supply: float
    broad_pct_supply: float
    top_proxy_groups: str


PROXY_GROUP_PATTERNS: List[Tuple[str, str]] = [
    ("BNP", r"\bBNP\b|binance\.ada|binance\.cardano|binance-ada|bnp_"),
    ("bison.run", r"bison\.run|herd\.run|\bCOINBASE\b"),
    ("1percentpool.eu", r"1percentpool\.eu|\b1PCT"),
    ("stakepool.cloud", r"stakepool\.cloud"),
    ("everstake.one", r"everstake\.one|\bESTK|\bEVERS|\bEVRST"),
    ("IOG_Group", r"iog\.io|iohk\.io|pools\.iohk\.io|\bIOGP?\d*\b"),
    ("emurgo.io", r"emurgo\.io|pools\.emurgo\.io|\bEMUR"),
    ("adaocean.com", r"adaocean\.com|\bOCEA|\bOCEAN"),
    ("DIG_Group", r"digi\.pro|\bDIGI\d*\b"),
    ("BLOO_Group", r"bloompool\.io|\bBLOOM\b"),
    ("kiln.fi", r"kiln\.fi|\bKILN\d*\b"),
    ("SPS", r"stakepoolservice\.com|\bSPS\d*\b"),
    ("NUFI_Group", r"nu\.fi|\bNUFI\d*\b"),
    ("stakecool.io", r"stakecool\.io|\bCOOL\d*\b"),
    ("bluecheesestakehouse.com", r"bluecheesestakehouse\.com|cardanostakehouse\.com|\bBCSH\d*\b"),
    ("upbit.com", r"upbit|\bUPBIT\b"),
    ("xray.app", r"xray\.app|\bXRAY\d*\b"),
    ("COP_Group", r"ada-sweeping-magpie|\bCOP\d*\b"),
    ("p2p.org", r"p2p\.org|p2p\.world|\bP2P\b|\bPPCX\d*\b"),
    ("goatstake.com", r"goatstake\.com"),
    ("SWM", r"swimmingpoolop|\bSWM\d*\b"),
    ("spirestaking.com", r"spirestaking\.com|\bSPIRE\b|\bSPIR\d*\b"),
    ("WAV", r"wavepool\.digital|\bWAV\d*\b"),
    ("spireblockchain.com", r"spireblockchain\.com"),
    ("fimi.vn", r"fimi\.vn|staking-fm\.site|\bFIMI\d*\b"),
    ("rockx.com", r"rockx\.com|\bRX[A-Z]?\b"),
    ("outerspace.money", r"outerspace\.money"),
    ("milpools.com", r"milpools\.com"),
    ("wira.co", r"wira\.co"),
    ("arthurjgoldman.com", r"arthurjgoldman\.com"),
    ("spaas.info", r"spaas\.info"),
    ("RAID", r"\bRAID\d*\b"),
    ("MPN", r"\bMPN\d*\b"),
    ("Ofee.club", r"\b0FEE\d*\b|ofee\.club"),
    ("CMAN", r"\bCMAN\d*\b"),
    ("maladex.com", r"maladex\.com"),
]

MPO_MIN_REGISTERED_POOLS = 2
REPORT_CHECKPOINT_EPOCH = 593
REPORT_CHECKPOINT_LABEL = "IMA checkpoint\n(epoch 593)"


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def load_csv(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def build_proxy_pool_map(pool_list_path: Path) -> Tuple[Dict[str, str], Counter[str]]:
    compiled = [(name, re.compile(pattern, re.I)) for name, pattern in PROXY_GROUP_PATTERNS]
    pool_to_proxy: Dict[str, str] = {}
    counts: Counter[str] = Counter()
    with pool_list_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            haystack = " | ".join(
                [
                    row.get("ticker") or "",
                    row.get("pool_group") or "",
                    row.get("meta_url") or "",
                    row.get("reward_addr") or "",
                    row.get("owners") or "",
                ]
            )
            for name, rx in compiled:
                if rx.search(haystack):
                    pool_to_proxy[row["pool_id_bech32"]] = name
                    counts[name] += 1
                    break
    return pool_to_proxy, counts


def build_broad_pool_map(pool_list_path: Path) -> Tuple[Dict[str, str], Counter[str]]:
    pool_to_group: Dict[str, str] = {}
    counts: Counter[str] = Counter()
    with pool_list_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group = (row.get("pool_group") or "").strip()
            if not group:
                continue
            pool_id = row["pool_id_bech32"]
            pool_to_group[pool_id] = group
            counts[group] += 1
    broad_groups = {group for group, count in counts.items() if count >= MPO_MIN_REGISTERED_POOLS}
    pool_to_broad = {pool_id: group for pool_id, group in pool_to_group.items() if group in broad_groups}
    broad_counts: Counter[str] = Counter()
    for group in pool_to_broad.values():
        broad_counts[group] += 1
    return pool_to_broad, broad_counts


def load_supply_by_epoch() -> Dict[int, float]:
    totals = fetch_json("https://api.koios.rest/api/v1/totals")
    if not isinstance(totals, list):
        raise RuntimeError("Unexpected Koios totals response")
    supply_by_epoch: Dict[int, float] = {}
    for row in totals:
        supply_by_epoch[int(row["epoch_no"])] = int(row["supply"]) / 1_000_000.0
    return supply_by_epoch


def aggregate_history(
    history_path: Path,
    pool_to_proxy: Dict[str, str],
    pool_to_broad: Dict[str, str],
) -> Tuple[Dict[int, float], Dict[int, float], Dict[int, Dict[str, float]]]:
    proxy_by_epoch: Dict[int, float] = defaultdict(float)
    broad_by_epoch: Dict[int, float] = defaultdict(float)
    proxy_groups_by_epoch: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    with history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_stake_ada = row.get("active_stake_ada") or ""
            if not active_stake_ada:
                continue
            pool_id = row["pool_id_bech32"]
            epoch_no = int(row["epoch_no"])
            stake_ada = float(active_stake_ada)
            proxy_group = pool_to_proxy.get(pool_id)
            if proxy_group is not None:
                proxy_by_epoch[epoch_no] += stake_ada
                proxy_groups_by_epoch[epoch_no][proxy_group] += stake_ada
            if pool_id in pool_to_broad:
                broad_by_epoch[epoch_no] += stake_ada
    return proxy_by_epoch, broad_by_epoch, proxy_groups_by_epoch


def fetch_live_pool_list() -> List[dict]:
    rows: List[dict] = []
    offset = 0
    limit = 1000
    while True:
        page = fetch_json(f"https://api.koios.rest/api/v1/pool_list?offset={offset}&limit={limit}")
        if not isinstance(page, list):
            raise RuntimeError("Unexpected Koios pool_list response")
        rows.extend(page)
        if len(page) < limit:
            break
        offset += len(page)
    return rows


def aggregate_live(
    pool_rows: Iterable[dict],
    broad_counts: Counter[str],
) -> Tuple[int, float, float, Dict[str, float], float]:
    compiled = [(name, re.compile(pattern, re.I)) for name, pattern in PROXY_GROUP_PATTERNS]
    proxy_total_ada = 0.0
    broad_total_ada = 0.0
    proxy_group_totals: Dict[str, float] = defaultdict(float)
    for row in pool_rows:
        active_stake = row.get("active_stake")
        if active_stake is None:
            continue
        stake_ada = int(active_stake) / 1_000_000.0
        haystack = " | ".join(
            [
                str(row.get("ticker") or ""),
                str(row.get("pool_group") or ""),
                str(row.get("meta_url") or ""),
                str(row.get("reward_addr") or ""),
                json.dumps(row.get("owners") or []),
            ]
        )
        for name, rx in compiled:
            if rx.search(haystack):
                proxy_total_ada += stake_ada
                proxy_group_totals[name] += stake_ada
                break

        group = row.get("pool_group")
        if group and broad_counts[group] >= MPO_MIN_REGISTERED_POOLS:
            broad_total_ada += stake_ada

    tip = fetch_json("https://api.koios.rest/api/v1/tip")
    if not isinstance(tip, list) or not tip:
        raise RuntimeError("Unexpected Koios tip response")
    live_epoch = int(tip[0]["epoch_no"])
    totals = fetch_json(f"https://api.koios.rest/api/v1/totals?_epoch_no={live_epoch}")
    if not isinstance(totals, list) or not totals:
        raise RuntimeError("Unexpected Koios totals-by-epoch response")
    supply_ada = int(totals[0]["supply"]) / 1_000_000.0
    return live_epoch, proxy_total_ada / supply_ada * 100.0, broad_total_ada / supply_ada * 100.0, proxy_group_totals, supply_ada


def select_stacked_entities(overview_path: Path) -> List[str]:
    rows = load_csv(overview_path)
    return [
        row["display_name"]
        for row in sorted(rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
        if int(row["current_registered_pool_count"]) >= MPO_MIN_REGISTERED_POOLS
    ]


def build_entity_pool_map(mapping_path: Path, included_entities: Iterable[str]) -> Dict[str, str]:
    included = set(included_entities)
    pool_to_entity: Dict[str, str] = {}
    for row in load_csv(mapping_path):
        entity = row["display_name"]
        if entity not in included:
            continue
        pool_to_entity[row["pool_id_bech32"]] = entity
    return pool_to_entity


def aggregate_entity_history(history_path: Path, pool_to_entity: Dict[str, str]) -> Dict[int, Dict[str, float]]:
    entity_by_epoch: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    with history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_stake_ada = row.get("active_stake_ada") or ""
            if not active_stake_ada:
                continue
            entity = pool_to_entity.get(row["pool_id_bech32"])
            if entity is None:
                continue
            epoch_no = int(row["epoch_no"])
            entity_by_epoch[epoch_no][entity] += float(active_stake_ada)
    return entity_by_epoch


def aggregate_live_entity_totals(pool_rows: Iterable[dict], pool_to_entity: Dict[str, str]) -> Dict[str, float]:
    entity_totals: Dict[str, float] = defaultdict(float)
    for row in pool_rows:
        entity = pool_to_entity.get(str(row.get("pool_id_bech32") or ""))
        if entity is None:
            continue
        active_stake = row.get("active_stake")
        if active_stake is None:
            continue
        entity_totals[entity] += int(active_stake) / 1_000_000.0
    return entity_totals


def build_key_epoch_rows(
    proxy_by_epoch: Dict[int, float],
    broad_by_epoch: Dict[int, float],
    proxy_groups_by_epoch: Dict[int, Dict[str, float]],
    supply_by_epoch: Dict[int, float],
    live_epoch: int,
    live_proxy_pct: float,
    live_broad_pct: float,
    live_proxy_groups: Dict[str, float],
) -> List[KeyEpochRow]:
    key_epochs = [220, 250, 400, 410, 584]
    rows: List[KeyEpochRow] = []
    for epoch_no in key_epochs:
        proxy_stake_ada = proxy_by_epoch[epoch_no]
        top_proxy = sorted(proxy_groups_by_epoch[epoch_no].items(), key=lambda x: x[1], reverse=True)[:3]
        rows.append(
            KeyEpochRow(
                epoch_no=epoch_no,
                source="local history",
                proxy_stake_b_ada=proxy_stake_ada / 1_000_000_000.0,
                proxy_pct_supply=proxy_stake_ada / supply_by_epoch[epoch_no] * 100.0,
                broad_pct_supply=broad_by_epoch[epoch_no] / supply_by_epoch[epoch_no] * 100.0,
                top_proxy_groups=", ".join(f"{name} ({stake / 1_000_000_000.0:.2f}B)" for name, stake in top_proxy),
            )
        )

    top_live = sorted(live_proxy_groups.items(), key=lambda x: x[1], reverse=True)[:3]
    rows.append(
        KeyEpochRow(
            epoch_no=live_epoch,
            source="live Koios",
            proxy_stake_b_ada=sum(live_proxy_groups.values()) / 1_000_000_000.0,
            proxy_pct_supply=live_proxy_pct,
            broad_pct_supply=live_broad_pct,
            top_proxy_groups=", ".join(f"{name} ({stake / 1_000_000_000.0:.2f}B)" for name, stake in top_live),
        )
    )
    return rows


def add_report_checkpoint_marker(ax: plt.Axes) -> None:
    ax.axvline(REPORT_CHECKPOINT_EPOCH, color="#7f8c8d", linestyle=":", linewidth=1.2, alpha=0.9)
    ax.text(
        REPORT_CHECKPOINT_EPOCH + 2,
        0.97,
        REPORT_CHECKPOINT_LABEL,
        transform=ax.get_xaxis_transform(),
        ha="left",
        va="top",
        fontsize=9,
        color="#4b5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#d1d5db", alpha=0.9),
    )


def render_chart(
    out_path: Path,
    proxy_by_epoch: Dict[int, float],
    broad_by_epoch: Dict[int, float],
    supply_by_epoch: Dict[int, float],
    live_epoch: int,
    live_proxy_pct: float,
    live_broad_pct: float,
) -> None:
    epochs = sorted(set(proxy_by_epoch) & set(broad_by_epoch) & set(supply_by_epoch))
    proxy_pct = np.array([proxy_by_epoch[epoch] / supply_by_epoch[epoch] * 100.0 for epoch in epochs], dtype=float)
    broad_pct = np.array([broad_by_epoch[epoch] / supply_by_epoch[epoch] * 100.0 for epoch in epochs], dtype=float)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(
        epochs,
        proxy_pct,
        color="#0b4f6c",
        linewidth=2.8,
        label="Reconstructed MPO basket from metadata/ticker signatures",
    )
    ax.plot(
        epochs,
        broad_pct,
        color="#d17b0f",
        linewidth=2.0,
        linestyle="--",
        label="Broad Koios pool_group (>=2 pools)",
    )

    ax.axvspan(400, 410, color="#c7dfe8", alpha=0.45)
    ax.axvline(400, color="#7aa6b8", linewidth=1.3, linestyle=":")
    ax.text(402, max(broad_pct) - 1.0, "Reallocation window around epoch 400", color="#355c6b", fontsize=10)
    add_report_checkpoint_marker(ax)

    ax.scatter([584], [proxy_by_epoch[584] / supply_by_epoch[584] * 100.0], color="#0b4f6c", s=42, zorder=4)
    ax.scatter([584], [broad_by_epoch[584] / supply_by_epoch[584] * 100.0], color="#d17b0f", s=42, zorder=4)
    ax.scatter([live_epoch], [live_proxy_pct], color="#0b4f6c", s=58, marker="D", zorder=5)
    ax.scatter([live_epoch], [live_broad_pct], color="#d17b0f", s=58, marker="D", zorder=5)

    ax.annotate(
        f"Epoch 584\n{proxy_by_epoch[584] / supply_by_epoch[584] * 100.0:.1f}%",
        xy=(584, proxy_by_epoch[584] / supply_by_epoch[584] * 100.0),
        xytext=(560, 22.2),
        arrowprops=dict(arrowstyle="-", color="#0b4f6c"),
        color="#0b4f6c",
        fontsize=10,
    )
    ax.annotate(
        f"Epoch {live_epoch}\n{live_proxy_pct:.1f}%",
        xy=(live_epoch, live_proxy_pct),
        xytext=(595, 20.1),
        arrowprops=dict(arrowstyle="-", color="#0b4f6c"),
        color="#0b4f6c",
        fontsize=10,
    )

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Share of Koios supply (%)")
    ax.set_xlim(min(epochs), max(live_epoch, max(epochs)) + 4)
    ax.set_ylim(0, max(max(broad_pct), live_broad_pct) + 3.0)
    ax.legend(loc="upper right")
    ax.text(
        0.01,
        0.02,
        "Solid line = reconstructed MPO basket: pools linked together from raw metadata/ticker patterns.\n"
        "Dashed line = broader Koios grouping using coarse pool_group labels.",
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def render_entity_stacked_chart(
    out_path: Path,
    entity_order: List[str],
    entity_by_epoch: Dict[int, Dict[str, float]],
    supply_by_epoch: Dict[int, float],
    live_epoch: int,
    live_supply_ada: float,
    live_entity_totals: Dict[str, float],
) -> None:
    history_epochs = sorted(epoch for epoch in entity_by_epoch if epoch in supply_by_epoch)
    epochs = list(history_epochs)
    if live_epoch not in epochs:
        epochs.append(live_epoch)

    series: List[np.ndarray] = []
    for entity in entity_order:
        values = [
            (entity_by_epoch[epoch].get(entity, 0.0) / supply_by_epoch[epoch] * 100.0) if supply_by_epoch[epoch] else 0.0
            for epoch in history_epochs
        ]
        if live_epoch not in history_epochs:
            values.append((live_entity_totals.get(entity, 0.0) / live_supply_ada * 100.0) if live_supply_ada else 0.0)
        series.append(np.array(values, dtype=float))

    total_pct = np.sum(series, axis=0) if series else np.zeros(len(epochs), dtype=float)
    palette = list(plt.get_cmap("tab20").colors) + list(plt.get_cmap("tab20b").colors) + list(plt.get_cmap("tab20c").colors)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(16, 10))

    ax.stackplot(epochs, series, labels=entity_order, colors=palette[: len(entity_order)], alpha=0.95, linewidth=0.0)
    ax.plot(epochs, total_pct, color="#1f2937", linewidth=1.2, alpha=0.85)

    ax.axvspan(400, 410, color="#dbeafe", alpha=0.4, linewidth=0)
    ax.text(401.5, total_pct.max() - 1.3, "Shift around epoch 400", color="#355c7d", fontsize=10)
    add_report_checkpoint_marker(ax)

    if epochs:
        ax.annotate(
            f"Live total {total_pct[-1]:.1f}%",
            xy=(epochs[-1], total_pct[-1]),
            xytext=(epochs[-1] - 48, total_pct[-1] + 2.0),
            arrowprops=dict(arrowstyle="-", color="#1f2937"),
            color="#1f2937",
            fontsize=10,
        )

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Share of circulating supply")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.set_xlim(min(epochs), max(epochs) + 4)
    ax.set_ylim(0, max(total_pct) + 3.0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=4, frameon=True, fontsize=9, title="Entities")
    fig.text(
        0.01,
        0.015,
        "Stacked areas show attributed entities with at least two currently registered pools. "
        "Historical values use local Koios pool history; the last point is a live Koios snapshot.",
        ha="left",
        va="bottom",
        fontsize=9,
    )

    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def write_key_epoch_csv(rows: List[KeyEpochRow], out_path: Path) -> None:
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "epoch_no",
                "source",
                "reconstructed_stake_b_ada",
                "reconstructed_pct_supply",
                "broad_pct_supply",
                "top_reconstructed_groups",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.epoch_no,
                    row.source,
                    f"{row.proxy_stake_b_ada:.3f}",
                    f"{row.proxy_pct_supply:.2f}",
                    f"{row.broad_pct_supply:.2f}",
                    row.top_proxy_groups,
                ]
            )


def write_summary(
    out_path: Path,
    figure_name: str,
    stacked_figure_name: str,
    proxy_counts: Counter[str],
    key_rows: List[KeyEpochRow],
    proxy_by_epoch: Dict[int, float],
    supply_by_epoch: Dict[int, float],
) -> None:
    peak_epoch = max(proxy_by_epoch, key=lambda epoch: proxy_by_epoch[epoch] / supply_by_epoch[epoch])
    peak_pct = proxy_by_epoch[peak_epoch] / supply_by_epoch[peak_epoch] * 100.0
    low_epoch = min(proxy_by_epoch, key=lambda epoch: proxy_by_epoch[epoch] / supply_by_epoch[epoch])
    low_pct = proxy_by_epoch[low_epoch] / supply_by_epoch[low_epoch] * 100.0

    lines = [
        "# MPO progression from raw Koios data",
        "",
        "## Files",
        "",
        f"- Figure: `../figures/{figure_name}`",
        f"- Entity composition figure: `../figures/{stacked_figure_name}`",
        f"- Table CSV: `mpo_progression_proxy_key_epochs_mainnet.csv`",
        "",
        "## Method",
        "",
        "- Historical stake uses the local Koios pool history export.",
        "- Reconstructed MPO basket = pools I can confidently link together from repeated metadata domains, tickers, and related raw registration signatures.",
        "- The broad comparator uses Koios `pool_group` labels whenever a group has at least two pools.",
        "- The final row in the table is a live Koios snapshot fetched at runtime.",
        "",
        "## Key read",
        "",
        f"- Reconstructed basket peak: epoch {peak_epoch} at {peak_pct:.2f}% of Koios supply.",
        f"- Reconstructed basket low: epoch {low_epoch} at {low_pct:.2f}% of Koios supply.",
        f"- Pools matched into the reconstructed basket: {sum(proxy_counts.values())}.",
        "",
        "## Key epochs",
        "",
        "| Epoch | Source | Reconstructed stake (B ADA) | Reconstructed % supply | Broad % supply | Top reconstructed groups |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]

    for row in key_rows:
        lines.append(
            f"| {row.epoch_no} | {row.source} | {row.proxy_stake_b_ada:.3f} | "
            f"{row.proxy_pct_supply:.2f}% | {row.broad_pct_supply:.2f}% | {row.top_proxy_groups} |"
        )

    lines.extend(
        [
            "",
            f"![MPO progression](../figures/{figure_name})",
            "",
            f"![Attributed MPO composition](../figures/{stacked_figure_name})",
            "",
        ]
    )

    out_path.write_text("\n".join(lines))


def main() -> None:
    report_dir   = Path(__file__).resolve().parent.parent   # mainnet-analysis/
    data_dir     = report_dir / "data"
    figures_dir  = report_dir / "figures"
    outputs_dir  = report_dir / "data"                     # local CSVs
    entity_data  = report_dir.parent.parent / "census" / "mainnet-analysis" / "data"
    entity_figs  = report_dir.parent.parent.parent / "entities" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    entity_figs.mkdir(parents=True, exist_ok=True)

    pool_list_path = data_dir / "koios_pool_list_mainnet.csv"
    history_path = data_dir / "koios_pool_history_mainnet.csv"
    overview_path = entity_data / "mpo_entity_health_overview_mainnet.csv"
    mapping_path = entity_data / "mpo_entity_pool_mapping_mainnet.csv"

    proxy_by_pool, proxy_counts = build_proxy_pool_map(pool_list_path)
    broad_by_pool, broad_counts = build_broad_pool_map(pool_list_path)
    supply_by_epoch = load_supply_by_epoch()
    proxy_by_epoch, broad_by_epoch, proxy_groups_by_epoch = aggregate_history(
        history_path,
        proxy_by_pool,
        broad_by_pool,
    )

    live_pool_rows = fetch_live_pool_list()
    live_epoch, live_proxy_pct, live_broad_pct, live_proxy_groups, live_supply_ada = aggregate_live(live_pool_rows, broad_counts)
    supply_by_epoch.setdefault(live_epoch, live_supply_ada)

    stacked_entities = select_stacked_entities(overview_path)
    entity_pool_map = build_entity_pool_map(mapping_path, stacked_entities)
    entity_by_epoch = aggregate_entity_history(history_path, entity_pool_map)
    live_entity_totals = aggregate_live_entity_totals(live_pool_rows, entity_pool_map)

    figure_path = figures_dir / "mpo_progression_proxy_mainnet.png"
    stacked_figure_path = entity_figs / "mpo_entity_progression_stacked_mainnet.png"
    summary_path = outputs_dir / "mpo_progression_proxy_mainnet_summary.md"
    csv_path = outputs_dir / "mpo_progression_proxy_key_epochs_mainnet.csv"

    render_chart(
        figure_path,
        proxy_by_epoch,
        broad_by_epoch,
        supply_by_epoch,
        live_epoch,
        live_proxy_pct,
        live_broad_pct,
    )
    render_entity_stacked_chart(
        stacked_figure_path,
        stacked_entities,
        entity_by_epoch,
        supply_by_epoch,
        live_epoch,
        live_supply_ada,
        live_entity_totals,
    )

    key_rows = build_key_epoch_rows(
        proxy_by_epoch,
        broad_by_epoch,
        proxy_groups_by_epoch,
        supply_by_epoch,
        live_epoch,
        live_proxy_pct,
        live_broad_pct,
        live_proxy_groups,
    )
    write_key_epoch_csv(key_rows, csv_path)
    write_summary(
        summary_path,
        figure_path.name,
        stacked_figure_path.name,
        proxy_counts,
        key_rows,
        proxy_by_epoch,
        supply_by_epoch,
    )

    print(figure_path)
    print(stacked_figure_path)
    print(summary_path)
    print(csv_path)


if __name__ == "__main__":
    main()
