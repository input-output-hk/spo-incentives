#!/usr/bin/env python3
"""
Build the pool registrations vs. retirements visual used in the SPO report.

The chart is derived from the Koios pool updates export and highlights the
three lifecycle phases described in the report narrative:
- Boom
- Consolidation
- Equilibrium
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_UPDATES_CSV = PROJECT_ROOT / "scenarii-evaluation/data/koios_pool_updates_mainnet.csv"
DEFAULT_REPORT_OUTPUT = PROJECT_ROOT / "spo_incentives/img/pool_registrations_vs_retirements_log_phases.png"
DEFAULT_DOC_OUTPUT = PROJECT_ROOT / "scenarii-evaluation/figures/pool_registrations_vs_retirements_mainnet.png"
KOIOS_BASE = "https://api.koios.rest/api/v1"
PAGE_SIZE = 1000
REQUEST_DELAY_S = float(os.getenv("KOIOS_REQUEST_DELAY_S", "0.0"))

PHASES = (
    (210, 280, "Boom", "#edf7ee"),
    (280, 400, "Consolidation", "#fff4de"),
    (400, None, "Equilibrium", "#eef3fb"),
)
BOUNDARIES = (280, 400)
ACCENT = "#8e44ad"
REPORT_CHECKPOINT_EPOCH = 593
REPORT_CHECKPOINT_LABEL = "Prior report checkpoint\nNov 6, 2025"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("koios", "csv"), default="koios")
    parser.add_argument("--updates-csv", type=Path, default=DEFAULT_UPDATES_CSV)
    parser.add_argument("--out", dest="out_paths", action="append", type=Path)
    parser.add_argument("--max-epoch", type=int)
    return parser.parse_args()


def fetch_json(url: str, retries: int = 20) -> object:
    for attempt in range(retries):
        try:
            headers = {"accept": "application/json", "content-type": "application/json"}
            token = os.getenv("KOIOS_BEARER_TOKEN") or os.getenv("KOIOS_API_TOKEN")
            if token:
                headers["authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                sleep_s = 75 if exc.code == 429 else min(2**attempt, 30)
                time.sleep(sleep_s)
                continue
            raise
        except urllib.error.URLError:
            if attempt + 1 < retries:
                time.sleep(min(2**attempt, 30))
                continue
            raise


def fetch_tip_epoch() -> int:
    rows = fetch_json(f"{KOIOS_BASE}/tip")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Unexpected Koios tip response.")
    return int(rows[0]["epoch_no"])


def parse_optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return None
        return int(text)
    return int(value)


def update_pool_event_maps(
    rows: list[dict[str, object]],
    *,
    max_epoch: int,
    first_registration_by_pool: dict[str, int],
    latest_retirement_by_pool: dict[str, int],
) -> None:
    for row in rows:
        pool_id = str(row.get("pool_id_bech32") or "").strip()
        if not pool_id:
            continue

        active_epoch = parse_optional_int(row.get("active_epoch_no"))
        if row.get("update_type") == "registration" and active_epoch is not None and active_epoch <= max_epoch:
            previous = first_registration_by_pool.get(pool_id)
            if previous is None or active_epoch < previous:
                first_registration_by_pool[pool_id] = active_epoch

        retiring_epoch = parse_optional_int(row.get("retiring_epoch"))
        if retiring_epoch is not None and retiring_epoch <= max_epoch:
            previous = latest_retirement_by_pool.get(pool_id)
            if previous is None or retiring_epoch > previous:
                latest_retirement_by_pool[pool_id] = retiring_epoch


def build_epoch_series(
    *,
    max_epoch: int,
    first_registration_by_pool: dict[str, int],
    latest_retirement_by_pool: dict[str, int],
) -> tuple[list[int], list[int], list[int]]:
    registrations = Counter(first_registration_by_pool.values())
    retirements = Counter(latest_retirement_by_pool.values())

    start_epoch = min(min(registrations, default=210), min(retirements, default=210))
    epochs = list(range(start_epoch, max_epoch + 1))
    registered_counts = [max(registrations.get(epoch, 0), 1) for epoch in epochs]
    retired_counts = [max(retirements.get(epoch, 0), 1) for epoch in epochs]
    return epochs, registered_counts, retired_counts


def load_epoch_counts_from_csv(path: Path, max_epoch: int) -> tuple[list[int], list[int], list[int]]:
    first_registration_by_pool: dict[str, int] = {}
    latest_retirement_by_pool: dict[str, int] = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        update_pool_event_maps(
            list(reader),
            max_epoch=max_epoch,
            first_registration_by_pool=first_registration_by_pool,
            latest_retirement_by_pool=latest_retirement_by_pool,
        )
    return build_epoch_series(
        max_epoch=max_epoch,
        first_registration_by_pool=first_registration_by_pool,
        latest_retirement_by_pool=latest_retirement_by_pool,
    )


def load_epoch_counts_from_koios(max_epoch: int) -> tuple[list[int], list[int], list[int]]:
    first_registration_by_pool: dict[str, int] = {}
    latest_retirement_by_pool: dict[str, int] = {}
    offset = 0
    select = "pool_id_bech32,active_epoch_no,update_type,retiring_epoch"

    while True:
        query = urllib.parse.urlencode({"offset": offset, "limit": PAGE_SIZE, "select": select})
        rows = fetch_json(f"{KOIOS_BASE}/pool_updates?{query}")
        if not isinstance(rows, list) or not rows:
            break
        update_pool_event_maps(
            rows,
            max_epoch=max_epoch,
            first_registration_by_pool=first_registration_by_pool,
            latest_retirement_by_pool=latest_retirement_by_pool,
        )
        offset += len(rows)
        print(f"koios pool_updates progress: offset={offset}", flush=True)
        if len(rows) < PAGE_SIZE:
            break
        if REQUEST_DELAY_S > 0:
            time.sleep(REQUEST_DELAY_S)

    return build_epoch_series(
        max_epoch=max_epoch,
        first_registration_by_pool=first_registration_by_pool,
        latest_retirement_by_pool=latest_retirement_by_pool,
    )


def add_phase_annotation(ax: plt.Axes, start: int, end: int, y: float, label: str) -> None:
    ax.annotate(
        "",
        xy=(end, y),
        xytext=(start, y),
        xycoords=("data", "axes fraction"),
        textcoords=("data", "axes fraction"),
        arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=2.1, shrinkA=0, shrinkB=0),
        annotation_clip=False,
    )
    text = ax.text(
        (start + end) / 2,
        y + 0.035,
        label,
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="bottom",
        fontsize=20,
        fontweight="bold",
        color=ACCENT,
    )
    text.set_path_effects([pe.withStroke(linewidth=4, foreground="white", alpha=0.95)])


def add_report_checkpoint_marker(ax: plt.Axes) -> None:
    ax.axvline(REPORT_CHECKPOINT_EPOCH, color="#7f8c8d", linestyle=":", linewidth=1.3, alpha=0.9, zorder=2)
    text = ax.text(
        REPORT_CHECKPOINT_EPOCH + 2,
        0.96,
        REPORT_CHECKPOINT_LABEL,
        transform=ax.get_xaxis_transform(),
        ha="left",
        va="top",
        fontsize=9,
        color="#4b5563",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#d1d5db", alpha=0.92),
    )
    text.set_path_effects([pe.withStroke(linewidth=3, foreground="white", alpha=0.9)])


def build_chart(
    epochs: list[int],
    registrations: list[int],
    retirements: list[int],
    out_paths: list[Path],
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(13.5, 8.1))
    ax.set_facecolor("#fcfcfd")

    for start, end, _, color in PHASES:
        phase_end = epochs[-1] if end is None else min(end, epochs[-1])
        if phase_end > start:
            ax.axvspan(start, phase_end, color=color, alpha=0.82, zorder=0)

    ax.plot(
        epochs,
        registrations,
        color="#0b9b2b",
        marker="o",
        markersize=3.2,
        linewidth=1.7,
        label="Newly Registered Pools",
        zorder=3,
    )
    ax.plot(
        epochs,
        retirements,
        color="#ff2f2f",
        marker="x",
        markersize=4.0,
        linewidth=1.5,
        label="Retired Pools",
        zorder=3,
    )

    for boundary in BOUNDARIES:
        ax.axvline(boundary, color=ACCENT, linewidth=1.8, linestyle=(0, (5, 5)), alpha=0.75, zorder=2)

    add_phase_annotation(ax, 210, min(280, epochs[-1]), 0.80, "Boom")
    add_phase_annotation(ax, 280, min(400, epochs[-1]), 0.63, "Consolidation")
    if epochs[-1] > 400:
        add_phase_annotation(ax, 400, epochs[-1], 0.56, "Equilibrium")
    add_report_checkpoint_marker(ax)

    ax.set_yscale("log")
    ax.set_xlim(200, epochs[-1] + 5)
    ax.set_ylim(0.8, max(max(registrations), max(retirements)) * 1.35)
    ax.set_xlabel("Epoch Number", fontsize=15)
    ax.set_ylabel("Number of Pools (Log Scale)", fontsize=15)
    ax.grid(alpha=0.24, which="both")

    legend = ax.legend(loc="upper right", frameon=True, framealpha=0.93, facecolor="white")
    legend.get_frame().set_edgecolor("#d7d7dc")

    fig.tight_layout()
    for out_path in out_paths:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    max_epoch = args.max_epoch
    if max_epoch is None:
        max_epoch = fetch_tip_epoch() if args.source == "koios" else 589

    if args.source == "koios":
        epochs, registrations, retirements = load_epoch_counts_from_koios(max_epoch)
    else:
        epochs, registrations, retirements = load_epoch_counts_from_csv(args.updates_csv, max_epoch)

    out_paths = args.out_paths or [DEFAULT_REPORT_OUTPUT, DEFAULT_DOC_OUTPUT]
    build_chart(epochs, registrations, retirements, out_paths)


if __name__ == "__main__":
    main()
