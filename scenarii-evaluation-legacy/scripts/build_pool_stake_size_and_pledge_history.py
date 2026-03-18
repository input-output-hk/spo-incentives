#!/usr/bin/env python3
"""
Build stacked-area history charts for:
1. total active stake by pool size bucket
2. total active stake by declared pledge bucket

Method:
- local pool history drives epochs 210..615
- declared pledge per epoch is reconstructed from pool_updates
- live Koios pool_list appends a current checkpoint at the current tip

Outputs:
- outputs/pool_active_stake_by_size_history_mainnet.csv
- outputs/pool_active_stake_by_pledge_band_history_mainnet.csv
- outputs/pool_active_stake_size_and_pledge_history_mainnet_summary.md
- figures/pool_active_stake_by_size_history_mainnet.png
- figures/pool_active_stake_by_pledge_band_history_mainnet.png
"""

from __future__ import annotations

import bisect
import csv
import json
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

SIZE_HISTORY_CSV = OUTPUTS_DIR / "pool_active_stake_by_size_history_mainnet.csv"
PLEDGE_HISTORY_CSV = OUTPUTS_DIR / "pool_active_stake_by_pledge_band_history_mainnet.csv"
SUMMARY_MD = OUTPUTS_DIR / "pool_active_stake_size_and_pledge_history_mainnet_summary.md"
SIZE_FIG = FIGURES_DIR / "pool_active_stake_by_size_history_mainnet.png"
PLEDGE_FIG = FIGURES_DIR / "pool_active_stake_by_pledge_band_history_mainnet.png"

SIZE_BUCKETS: List[Tuple[str, float, float]] = [
    ("<3M ADA", 0.0, 3_000_000.0),
    ("3M-10M ADA", 3_000_000.0, 10_000_000.0),
    ("10M-20M ADA", 10_000_000.0, 20_000_000.0),
    ("20M-30M ADA", 20_000_000.0, 30_000_000.0),
    ("30M-40M ADA", 30_000_000.0, 40_000_000.0),
    ("40M-50M ADA", 40_000_000.0, 50_000_000.0),
    ("50M-60M ADA", 50_000_000.0, 60_000_000.0),
    ("60M-70M ADA", 60_000_000.0, 70_000_000.0),
    (">70M ADA", 70_000_000.0, float("inf")),
]

PLEDGE_BUCKETS: List[Tuple[str, float, float]] = [
    ("0 ADA", 0.0, 0.0),
    (">0-1k ADA", 0.0, 1_000.0),
    ("1k-10k ADA", 1_000.0, 10_000.0),
    ("10k-100k ADA", 10_000.0, 100_000.0),
    ("100k-1M ADA", 100_000.0, 1_000_000.0),
    ("1M-10M ADA", 1_000_000.0, 10_000_000.0),
    ("10M-70M ADA", 10_000_000.0, 70_000_000.0),
    (">70M ADA", 70_000_000.0, float("inf")),
]

SIZE_COLORS = [
    "#b30059",
    "#f94144",
    "#f9844a",
    "#f9c74f",
    "#f2f3ae",
    "#b5d86b",
    "#52b788",
    "#119da4",
    "#6a4fb3",
]

PLEDGE_COLORS = [
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


def pledge_bucket_label(pledge_ada: float) -> str:
    if pledge_ada == 0.0:
        return PLEDGE_BUCKETS[0][0]
    for label, lo, hi in PLEDGE_BUCKETS[1:]:
        if pledge_ada >= lo and pledge_ada < hi:
            return label
    return PLEDGE_BUCKETS[-1][0]


def default_metric_row(epoch_no: int, source: str, bucket_labels: Iterable[str]) -> dict:
    row = {
        "epoch_no": epoch_no,
        "source": source,
        "total_active_stake_ada": 0.0,
        "active_pool_count": 0,
    }
    for label in bucket_labels:
        slug = slugify(label)
        row[f"{slug}_stake_ada"] = 0.0
        row[f"{slug}_pool_count"] = 0
    return row


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


def build_local_history(pool_history_path: Path, updates_by_pool: Dict[str, dict]) -> tuple[List[dict], List[dict]]:
    size_metrics: Dict[int, dict] = {}
    pledge_metrics: Dict[int, dict] = {}
    size_labels = [label for label, _, _ in SIZE_BUCKETS]
    pledge_labels = [label for label, _, _ in PLEDGE_BUCKETS]

    with pool_history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch_no = int(row["epoch_no"])
            active_stake_ada = float(row["active_stake_ada"])
            if active_stake_ada <= 0.0:
                continue
            pool_id = row["pool_id_bech32"]

            size_metric = size_metrics.get(epoch_no)
            if size_metric is None:
                size_metric = default_metric_row(epoch_no, "local_history", size_labels)
                size_metrics[epoch_no] = size_metric
            pledge_metric = pledge_metrics.get(epoch_no)
            if pledge_metric is None:
                pledge_metric = default_metric_row(epoch_no, "local_history", pledge_labels)
                pledge_metrics[epoch_no] = pledge_metric

            size_metric["total_active_stake_ada"] += active_stake_ada
            size_metric["active_pool_count"] += 1
            size_label = size_bucket_label(active_stake_ada)
            size_slug = slugify(size_label)
            size_metric[f"{size_slug}_stake_ada"] += active_stake_ada
            size_metric[f"{size_slug}_pool_count"] += 1

            pledge_ada = pledge_at_epoch(updates_by_pool.get(pool_id), epoch_no)
            if pledge_ada is None:
                raise RuntimeError(f"Missing reconstructed pledge for pool {pool_id} at epoch {epoch_no}")
            pledge_metric["total_active_stake_ada"] += active_stake_ada
            pledge_metric["active_pool_count"] += 1
            pledge_label = pledge_bucket_label(pledge_ada)
            pledge_slug = slugify(pledge_label)
            pledge_metric[f"{pledge_slug}_stake_ada"] += active_stake_ada
            pledge_metric[f"{pledge_slug}_pool_count"] += 1

    return [size_metrics[epoch] for epoch in sorted(size_metrics)], [pledge_metrics[epoch] for epoch in sorted(pledge_metrics)]


def build_live_checkpoint() -> tuple[dict, dict]:
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

    size_row = default_metric_row(live_epoch, "live_koios", [label for label, _, _ in SIZE_BUCKETS])
    pledge_row = default_metric_row(live_epoch, "live_koios", [label for label, _, _ in PLEDGE_BUCKETS])

    for row in rows:
        if row.get("pool_status") != "registered":
            continue
        active_stake_ada = int(row.get("active_stake") or 0) / 1_000_000.0
        if active_stake_ada <= 0.0:
            continue

        size_row["total_active_stake_ada"] += active_stake_ada
        size_row["active_pool_count"] += 1
        size_label = size_bucket_label(active_stake_ada)
        size_slug = slugify(size_label)
        size_row[f"{size_slug}_stake_ada"] += active_stake_ada
        size_row[f"{size_slug}_pool_count"] += 1

        pledge_ada = int(row.get("pledge") or 0) / 1_000_000.0
        pledge_row["total_active_stake_ada"] += active_stake_ada
        pledge_row["active_pool_count"] += 1
        pledge_label = pledge_bucket_label(pledge_ada)
        pledge_slug = slugify(pledge_label)
        pledge_row[f"{pledge_slug}_stake_ada"] += active_stake_ada
        pledge_row[f"{pledge_slug}_pool_count"] += 1

    return size_row, pledge_row


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_stacked_area(rows: List[dict], labels: List[str], colors: List[str], title: str, legend_title: str, out_path: Path) -> None:
    epochs = [row["epoch_no"] for row in rows]
    series = [[row[f"{slugify(label)}_stake_ada"] / 1_000_000_000.0 for row in rows] for label in labels]
    total_stake_b = [row["total_active_stake_ada"] / 1_000_000_000.0 for row in rows]

    plt.close("all")
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.stackplot(epochs, series, labels=labels, colors=colors, alpha=0.95)
    ax.plot(epochs, total_stake_b, color="black", linewidth=2.0, linestyle="--", label="Total active stake")
    ax.set_title(title, fontsize=18)
    ax.set_xlabel("Epoch Number")
    ax.set_ylabel("Total Stake (in ADA)")
    ax.grid(alpha=0.25, linestyle=":")
    ax.legend(loc="lower left", title=legend_title, framealpha=0.9)
    ax.ticklabel_format(axis="y", style="plain")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def build_summary(size_rows: List[dict], pledge_rows: List[dict], live_epoch: int) -> str:
    def last(rows: List[dict]) -> dict:
        return rows[-1]

    live_size = last(size_rows)
    live_pledge = last(pledge_rows)

    gt70_live = live_size[f"{slugify('>70M ADA')}_stake_ada"]
    low_pledge_live = (
        live_pledge[f"{slugify('0 ADA')}_stake_ada"]
        + live_pledge[f"{slugify('>0-1k ADA')}_stake_ada"]
        + live_pledge[f"{slugify('1k-10k ADA')}_stake_ada"]
    )

    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Pool Stake Size and Pledge History Summary (Mainnet)

_Built on `{built_at}` from local pool history through epoch `615` plus live Koios epoch `{live_epoch}`._

## What was built

- `pool_active_stake_by_size_history_mainnet.png`: stacked area chart of total active stake split by **current pool size bucket** in each epoch, plus the total active stake line.
- `pool_active_stake_by_pledge_band_history_mainnet.png`: stacked area chart of total active stake split by the pool's **declared pledge band** in each epoch, plus the total active stake line.

## Live checkpoint read

- Live epoch `{live_epoch}` total active stake in registered positive-stake pools: **{live_size['total_active_stake_ada'] / 1_000_000_000.0:.3f}B ADA**
- Live epoch `{live_epoch}` active stake in the `>70M ADA` size band: **{gt70_live / 1_000_000_000.0:.3f}B ADA**
- Live epoch `{live_epoch}` active stake in pledge bands below `10k ADA`: **{low_pledge_live / 1_000_000_000.0:.3f}B ADA**

## Interpretation

- The size chart shows how the head of very large pools expanded and contracted over time relative to the full active stake base.
- The pledge-band chart answers a different question: not how big the pools are, but how much active stake sits behind pools with different declared pledge levels.
- These two lenses are complementary: one is about **pool scale**, the other about **capital commitment posture**.
"""


def main() -> None:
    updates_by_pool = load_updates(POOL_UPDATES_CSV)
    size_rows, pledge_rows = build_local_history(POOL_HISTORY_CSV, updates_by_pool)
    live_size_row, live_pledge_row = build_live_checkpoint()
    size_rows.append(live_size_row)
    pledge_rows.append(live_pledge_row)

    write_csv(SIZE_HISTORY_CSV, size_rows)
    write_csv(PLEDGE_HISTORY_CSV, pledge_rows)

    render_stacked_area(
        size_rows,
        [label for label, _, _ in SIZE_BUCKETS],
        SIZE_COLORS,
        "Total Active Stake of Pools by Size (Local History + Live Checkpoint)",
        "Pool Size Category",
        SIZE_FIG,
    )
    render_stacked_area(
        pledge_rows,
        [label for label, _, _ in PLEDGE_BUCKETS],
        PLEDGE_COLORS,
        "Total Active Stake of Pools by Declared Pledge Band (Local History + Live Checkpoint)",
        "Declared Pledge Category",
        PLEDGE_FIG,
    )

    live_epoch = size_rows[-1]["epoch_no"]
    SUMMARY_MD.write_text(build_summary(size_rows, pledge_rows, live_epoch))
    print(f"Wrote {SIZE_FIG}")
    print(f"Wrote {PLEDGE_FIG}")
    print(f"Wrote {SIZE_HISTORY_CSV}")
    print(f"Wrote {PLEDGE_HISTORY_CSV}")
    print(f"Wrote {SUMMARY_MD}")


if __name__ == "__main__":
    main()
