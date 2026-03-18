#!/usr/bin/env python3
"""
Build a mainnet history visual for Fee^epoch_tx since the start of Shelley.

Outputs:
  - scenarii-evaluation/figures/fee_epoch_tx_history_mainnet.png
  - scenarii-evaluation/outputs/fee_epoch_tx_history_mainnet.md
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import List, Optional

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class EpochRow:
    epoch_no: int
    start_time_utc: Optional[str]
    end_time_utc: Optional[str]
    fee_epoch_ada: Optional[float]
    has_total_rewards: bool


def parse_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    return float(stripped)


def parse_bool(value: str | None) -> bool:
    return str(value).strip() == "True"


def parse_utc(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=timezone.utc)


def load_rows(path: Path) -> List[EpochRow]:
    rows: List[EpochRow] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            rows.append(
                EpochRow(
                    epoch_no=int(record["epoch_no"]),
                    start_time_utc=record.get("start_time_utc"),
                    end_time_utc=record.get("end_time_utc"),
                    fee_epoch_ada=parse_float(record.get("Fee_epoch_ada")),
                    has_total_rewards=parse_bool(record.get("has_total_rewards")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def format_date(value: Optional[str]) -> str:
    if not value:
        return "n/a"
    return value[:10]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "fee_epoch_tx_history_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "fee_epoch_tx_history_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    fees = np.array([np.nan if row.fee_epoch_ada is None else row.fee_epoch_ada for row in rows], dtype=float)
    complete_mask = np.array([row.has_total_rewards and row.fee_epoch_ada is not None for row in rows], dtype=bool)
    partial_mask = np.array([not row.has_total_rewards and row.fee_epoch_ada is not None for row in rows], dtype=bool)

    if not np.any(complete_mask):
        raise RuntimeError("No complete fee history found in the dataset.")

    complete_indices = np.where(complete_mask)[0]
    latest_complete_idx = int(complete_indices[-1])
    latest_complete_row = rows[latest_complete_idx]
    latest_complete_end = parse_utc(latest_complete_row.end_time_utc)
    if latest_complete_end is None:
        raise RuntimeError("Latest complete row is missing end_time_utc.")

    window_start = latest_complete_end - timedelta(days=30)
    month_window_indices = [
        i
        for i, row in enumerate(rows)
        if row.has_total_rewards
        and row.fee_epoch_ada is not None
        and parse_utc(row.end_time_utc) is not None
        and parse_utc(row.end_time_utc) > window_start
    ]
    if not month_window_indices:
        raise RuntimeError("No complete epochs found in the last-30-day fee window.")

    month_window_fees = [float(fees[i]) for i in month_window_indices]
    last_month_avg_fee = float(mean(month_window_fees))

    fee_complete = fees[complete_mask]
    min_complete_idx = int(complete_indices[np.nanargmin(fee_complete)])
    max_complete_idx = int(complete_indices[np.nanargmax(fee_complete)])

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=False,
        gridspec_kw={"height_ratios": [1.35, 1.0]},
    )

    ax1.plot(epochs[complete_mask], fees[complete_mask] / 1_000.0, color="#0b4f6c", linewidth=1.8, label=r"Complete epochs: $Fee^{epoch}_{tx}$")
    if np.any(partial_mask):
        ax1.plot(
            epochs[partial_mask],
            fees[partial_mask] / 1_000.0,
            color="#d62728",
            linewidth=1.4,
            linestyle="--",
            marker="D",
            markersize=4,
            label="Current / incomplete epochs",
        )
    ax1.axhline(last_month_avg_fee / 1_000.0, color="#cc7a00", linewidth=1.2, linestyle=":", label="Last 30-day average")

    ax1.scatter(
        [rows[min_complete_idx].epoch_no, rows[max_complete_idx].epoch_no],
        [fees[min_complete_idx] / 1_000.0, fees[max_complete_idx] / 1_000.0],
        color=["#7f3c8d", "#1b9e77"],
        s=36,
        zorder=5,
    )
    ax1.annotate(
        f"low complete\n{rows[min_complete_idx].epoch_no} {format_date(rows[min_complete_idx].start_time_utc)}\n{fees[min_complete_idx]:,.0f} ADA",
        xy=(rows[min_complete_idx].epoch_no, fees[min_complete_idx] / 1_000.0),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="bottom",
        color="#4b1d57",
    )
    ax1.annotate(
        f"high complete\n{rows[max_complete_idx].epoch_no} {format_date(rows[max_complete_idx].start_time_utc)}\n{fees[max_complete_idx]:,.0f} ADA",
        xy=(rows[max_complete_idx].epoch_no, fees[max_complete_idx] / 1_000.0),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="top",
        color="#155d46",
    )

    ax1.set_ylabel("Thousand ADA / epoch")
    ax1.set_title(r"Cardano Mainnet $Fee^{epoch}_{tx}$ Since the Start of Shelley")
    ax1.legend(loc="upper left")
    ax1.text(
        0.01,
        0.98,
        f"Latest complete epoch: {latest_complete_row.epoch_no} ({format_date(latest_complete_row.end_time_utc)} end)\n"
        f"Last 30-day complete window: {format_date(rows[month_window_indices[0]].end_time_utc)} to {format_date(rows[month_window_indices[-1]].end_time_utc)}\n"
        f"Average over that window: {last_month_avg_fee:,.0f} ADA / epoch",
        transform=ax1.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    recent_start_idx = max(0, latest_complete_idx - 47)
    recent_indices = list(range(recent_start_idx, latest_complete_idx + 1))
    recent_epochs = epochs[recent_indices]
    recent_fees = fees[recent_indices] / 1_000.0
    ax2.plot(recent_epochs, recent_fees, color="#0b4f6c", linewidth=1.8, label="Recent complete epochs")
    ax2.axhline(last_month_avg_fee / 1_000.0, color="#cc7a00", linewidth=1.2, linestyle=":", label="Last 30-day average")

    highlight_epochs = [rows[i].epoch_no for i in month_window_indices]
    highlight_fees = [fees[i] / 1_000.0 for i in month_window_indices]
    ax2.scatter(highlight_epochs, highlight_fees, color="#cc7a00", s=28, zorder=5, label="Epochs in last 30-day average")

    ax2.set_ylabel("Thousand ADA / epoch")
    ax2.set_xlabel("Epoch")
    ax2.set_title("Recent Zoom With the Last 30-Day Average Window")
    ax2.legend(loc="upper right")

    tick_count = min(11, len(rows))
    tick_idx = np.unique(np.linspace(0, len(rows) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(epochs[tick_idx])
    ax1.set_xticklabels([f"{epochs[i]}\n{format_date(rows[i].start_time_utc)}" for i in tick_idx])

    zoom_tick_count = min(10, len(recent_indices))
    zoom_tick_idx = np.unique(np.linspace(0, len(recent_indices) - 1, num=zoom_tick_count, dtype=int))
    ax2.set_xticks(recent_epochs[zoom_tick_idx])
    ax2.set_xticklabels(
        [f"{recent_epochs[i]}\n{format_date(rows[recent_indices[i]].start_time_utc)}" for i in zoom_tick_idx]
    )

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)

    notes_lines = [
        "# Fee^epoch_tx History (Mainnet)",
        "",
        f"- Coverage: epochs **{rows[0].epoch_no}..{rows[-1].epoch_no}**.",
        f"- Latest complete epoch: **{latest_complete_row.epoch_no}** ending on **{format_date(latest_complete_row.end_time_utc)}**.",
        f"- Last 30-day average window uses complete epochs **{rows[month_window_indices[0]].epoch_no}..{rows[month_window_indices[-1]].epoch_no}** "
        f"from **{format_date(rows[month_window_indices[0]].end_time_utc)}** through **{format_date(rows[month_window_indices[-1]].end_time_utc)}**.",
        f"- Last 30-day average `Fee^epoch_tx`: **{last_month_avg_fee:,.2f} ADA per epoch**.",
        f"- Lowest complete epoch fee: **{fees[min_complete_idx]:,.2f} ADA** at epoch **{rows[min_complete_idx].epoch_no}** ({format_date(rows[min_complete_idx].start_time_utc)}).",
        f"- Highest complete epoch fee: **{fees[max_complete_idx]:,.2f} ADA** at epoch **{rows[max_complete_idx].epoch_no}** ({format_date(rows[max_complete_idx].start_time_utc)}).",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(f"Last 30-day average Fee_epoch_tx: {last_month_avg_fee:.6f} ADA/epoch")


if __name__ == "__main__":
    main()
