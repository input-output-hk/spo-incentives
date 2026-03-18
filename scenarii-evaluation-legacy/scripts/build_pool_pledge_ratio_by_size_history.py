#!/usr/bin/env python3
"""
Build a history visual for active stake split by pledge-to-stake ratio
within each pool size category.

Interpretation:
- x-axis: epoch
- y-axis: active stake in ADA
- one panel per pool size category
- stacked areas: declared pledge / active stake ratio bands
- dashed black line: total active stake in that size category

Outputs:
- outputs/pool_pledge_ratio_by_size_history_mainnet.csv
- outputs/pool_pledge_ratio_by_size_history_mainnet_summary.md
- figures/pool_pledge_ratio_by_size_history_mainnet.png
"""

from __future__ import annotations

import bisect
import csv
import json
import math
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
FIGURES_DIR = ROOT / "figures"

POOL_HISTORY_CSV = DATA_DIR / "koios_pool_history_mainnet.csv"
POOL_UPDATES_CSV = DATA_DIR / "koios_pool_updates_mainnet.csv"

OUT_CSV = OUTPUTS_DIR / "pool_pledge_ratio_by_size_history_mainnet.csv"
OUT_SUMMARY = OUTPUTS_DIR / "pool_pledge_ratio_by_size_history_mainnet_summary.md"
OUT_FIG = FIGURES_DIR / "pool_pledge_ratio_by_size_history_mainnet.png"

SIZE_BUCKETS: List[Tuple[str, float, float]] = [
    ("<3M ADA", 0.0, 3_000_000.0),
    ("3M-10M ADA", 3_000_000.0, 10_000_000.0),
    ("10M-30M ADA", 10_000_000.0, 30_000_000.0),
    ("30M-70M ADA", 30_000_000.0, 70_000_000.0),
    (">70M ADA", 70_000_000.0, math.inf),
]

RATIO_BUCKETS: List[Tuple[str, float, float]] = [
    ("0%", 0.0, 0.0),
    (">0-0.001%", 0.0, 0.001),
    ("0.001%-0.01%", 0.001, 0.01),
    ("0.01%-0.1%", 0.01, 0.1),
    ("0.1%-1%", 0.1, 1.0),
    ("1%-10%", 1.0, 10.0),
    ("10%-50%", 10.0, 50.0),
    (">50%", 50.0, math.inf),
]

RATIO_COLORS = [
    "#7f0000",
    "#b30000",
    "#e34a33",
    "#fc8d59",
    "#fdcc8a",
    "#9ecae1",
    "#3182bd",
    "#08519c",
]


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(">", "gt_")
        .replace("<", "lt_")
        .replace("%", "pct")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
        .replace(".", "")
    )


def load_updates(path: Path) -> Dict[str, dict]:
    updates_by_pool: Dict[str, list[tuple[int, int, float]]] = defaultdict(list)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_epoch = str(row.get("active_epoch_no") or "").strip()
            if not active_epoch:
                continue
            updates_by_pool[row["pool_id_bech32"]].append(
                (
                    int(active_epoch),
                    int(row.get("block_time") or 0),
                    float(row.get("pledge_ada") or 0.0),
                )
            )

    out: Dict[str, dict] = {}
    for pool_id, updates in updates_by_pool.items():
        updates.sort(key=lambda item: (item[0], item[1]))
        out[pool_id] = {
            "epochs": [item[0] for item in updates],
            "pledges_ada": [item[2] for item in updates],
        }
    return out


def pledge_at_epoch(pool_updates: dict | None, epoch_no: int) -> float | None:
    if pool_updates is None:
        return None
    epochs = pool_updates["epochs"]
    idx = bisect.bisect_right(epochs, epoch_no) - 1
    if idx < 0:
        return None
    return pool_updates["pledges_ada"][idx]


def size_bucket_label(stake_ada: float) -> str:
    for label, lo, hi in SIZE_BUCKETS:
        if stake_ada >= lo and stake_ada < hi:
            return label
    return SIZE_BUCKETS[-1][0]


def ratio_bucket_label(ratio_pct: float) -> str:
    if ratio_pct == 0.0:
        return RATIO_BUCKETS[0][0]
    for label, lo, hi in RATIO_BUCKETS[1:]:
        if ratio_pct >= lo and ratio_pct < hi:
            return label
    return RATIO_BUCKETS[-1][0]


def default_row(epoch_no: int, source: str, size_label: str) -> dict:
    row = {
        "epoch_no": epoch_no,
        "source": source,
        "size_bucket": size_label,
        "total_active_stake_ada": 0.0,
        "active_pool_count": 0,
    }
    for label, _, _ in RATIO_BUCKETS:
        slug = slugify(label)
        row[f"{slug}_stake_ada"] = 0.0
        row[f"{slug}_pool_count"] = 0
    return row


def build_local_rows(updates_by_pool: Dict[str, dict]) -> List[dict]:
    metrics: Dict[tuple[int, str], dict] = {}
    with POOL_HISTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch_no = int(row["epoch_no"])
            active_stake_ada = float(row["active_stake_ada"])
            if active_stake_ada <= 0.0:
                continue
            pledge_ada = pledge_at_epoch(updates_by_pool.get(row["pool_id_bech32"]), epoch_no)
            if pledge_ada is None:
                raise RuntimeError(f"Missing reconstructed pledge for {row['pool_id_bech32']} at epoch {epoch_no}")
            ratio_pct = (pledge_ada / active_stake_ada * 100.0) if active_stake_ada > 0 else 0.0

            size_label = size_bucket_label(active_stake_ada)
            ratio_label = ratio_bucket_label(ratio_pct)
            key = (epoch_no, size_label)
            metric = metrics.get(key)
            if metric is None:
                metric = default_row(epoch_no, "local_history", size_label)
                metrics[key] = metric
            metric["total_active_stake_ada"] += active_stake_ada
            metric["active_pool_count"] += 1
            ratio_slug = slugify(ratio_label)
            metric[f"{ratio_slug}_stake_ada"] += active_stake_ada
            metric[f"{ratio_slug}_pool_count"] += 1

    rows = [metrics[key] for key in sorted(metrics, key=lambda item: (item[0], item[1]))]
    return rows


def build_live_rows() -> List[dict]:
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

    metrics = {label: default_row(live_epoch, "live_koios", label) for label, _, _ in SIZE_BUCKETS}

    for row in rows:
        if row.get("pool_status") != "registered":
            continue
        active_stake_ada = int(row.get("active_stake") or 0) / 1_000_000.0
        if active_stake_ada <= 0.0:
            continue
        pledge_ada = int(row.get("pledge") or 0) / 1_000_000.0
        ratio_pct = pledge_ada / active_stake_ada * 100.0 if active_stake_ada > 0 else 0.0
        size_label = size_bucket_label(active_stake_ada)
        ratio_label = ratio_bucket_label(ratio_pct)
        metric = metrics[size_label]
        metric["total_active_stake_ada"] += active_stake_ada
        metric["active_pool_count"] += 1
        ratio_slug = slugify(ratio_label)
        metric[f"{ratio_slug}_stake_ada"] += active_stake_ada
        metric[f"{ratio_slug}_pool_count"] += 1

    return [metrics[label] for label, _, _ in SIZE_BUCKETS]


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_figure(rows: List[dict], out_path: Path) -> None:
    ratio_labels = [label for label, _, _ in RATIO_BUCKETS]
    size_labels = [label for label, _, _ in SIZE_BUCKETS]
    rows_by_size: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        rows_by_size[row["size_bucket"]].append(row)
    for label in size_labels:
        rows_by_size[label].sort(key=lambda row: row["epoch_no"])

    plt.close("all")
    fig, axes = plt.subplots(3, 2, figsize=(18, 13), sharex=True)
    axes_list = axes.flatten()

    for idx, size_label in enumerate(size_labels):
        ax = axes_list[idx]
        size_rows = rows_by_size[size_label]
        epochs = [row["epoch_no"] for row in size_rows]
        stacked = [[row[f"{slugify(ratio_label)}_stake_ada"] / 1_000_000_000.0 for row in size_rows] for ratio_label in ratio_labels]
        totals = [row["total_active_stake_ada"] / 1_000_000_000.0 for row in size_rows]
        ax.stackplot(epochs, stacked, colors=RATIO_COLORS, alpha=0.96)
        ax.plot(epochs, totals, color="black", linestyle="--", linewidth=1.8)
        ax.set_title(size_label)
        ax.grid(alpha=0.22, linestyle=":")
        ax.set_ylabel("Stake (B ADA)")

    legend_ax = axes_list[-1]
    legend_ax.axis("off")
    handles = [plt.Line2D([], [], color=color, linewidth=8) for color in RATIO_COLORS]
    labels = ratio_labels[:]
    handles.append(plt.Line2D([], [], color="black", linestyle="--", linewidth=2))
    labels.append("Total active stake")
    legend_ax.legend(handles, labels, loc="center", framealpha=0.95, title="Pledge / active stake ratio")

    for ax in axes[-1]:
        if ax is not legend_ax:
            ax.set_xlabel("Epoch Number")
    fig.suptitle("Active Stake by Pledge-to-Stake Ratio Within Each Pool Size Category", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def build_summary(rows: List[dict]) -> str:
    live_epoch = max(int(row["epoch_no"]) for row in rows if row["source"] == "live_koios")
    live_rows = [row for row in rows if row["source"] == "live_koios"]
    size_map = {row["size_bucket"]: row for row in live_rows}
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    gt70 = size_map[">70M ADA"]
    lt1bp_slug = slugify(">0-0.001%")
    high_slug = slugify(">50%")
    return f"""# Pool Pledge Ratio by Size History Summary (Mainnet)

_Built on `{built_at}` from local pool history through epoch `615` plus live Koios epoch `{live_epoch}`._

## What this chart shows

- Each panel is a **pool size category**.
- The stacked colors show how much **active stake** sits in pools with different **declared pledge / active stake ratios**.
- The dashed black line is the **total active stake** in that size category.

## Live read

- In the `>70M ADA` size bucket at live epoch `{live_epoch}`, active stake totals **{gt70['total_active_stake_ada'] / 1_000_000_000.0:.3f}B ADA**.
- Within that same `>70M ADA` bucket, active stake in the tiny-but-nonzero pledge-ratio band `>0-0.001%` is **{gt70[f'{lt1bp_slug}_stake_ada'] / 1_000_000_000.0:.3f}B ADA**.
- Within that same `>70M ADA` bucket, active stake in the very high pledge-ratio band `>50%` is **{gt70[f'{high_slug}_stake_ada'] / 1_000_000_000.0:.3f}B ADA**.

## Interpretation

- This is a better lens than a pure pledge-amount chart when you want to compare small and large pools on the same economic footing.
- A pool with `100 ADA` pledge means something very different at `1M ADA` stake than at `70M ADA` stake.
- The chart therefore normalizes pledge against pool scale instead of looking at absolute pledge only.
"""


def main() -> None:
    updates_by_pool = load_updates(POOL_UPDATES_CSV)
    rows = build_local_rows(updates_by_pool)
    rows.extend(build_live_rows())
    write_csv(OUT_CSV, rows)
    render_figure(rows, OUT_FIG)
    OUT_SUMMARY.write_text(build_summary(rows))
    print(f"Wrote {OUT_FIG}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
