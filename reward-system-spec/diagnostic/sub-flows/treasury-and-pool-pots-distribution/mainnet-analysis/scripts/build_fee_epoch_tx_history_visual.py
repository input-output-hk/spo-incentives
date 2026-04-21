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

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
from cardano_events import add_event_markers


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
    REPORT_DIR = Path(__file__).resolve().parent.parent
    data_path = REPORT_DIR / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = REPORT_DIR / "figures" / "fee_epoch_tx_history_mainnet.png"
    notes_path = REPORT_DIR / "data" / "fee_epoch_tx_history_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    fees = np.array([np.nan if row.fee_epoch_ada is None else row.fee_epoch_ada for row in rows], dtype=float)

    # Filter out incomplete/current epoch (last epoch may have partial data)
    if len(epochs) > 0 and epochs[-1] > 623:
        # Only keep up to the last complete epoch with reward data
        mask_complete_data = epochs <= 623
        epochs = epochs[mask_complete_data]
        fees = fees[mask_complete_data]
        rows = [row for i, row in enumerate(rows) if i < len(rows) and rows[i].epoch_no <= 623]

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

    # IOG light brand colours
    LIGHT_BG = "#FAFAFA"
    TEXT_DARK = "#1A1A1A"
    DIM_TEXT = "#666666"
    GRID_COLOR = "#E0E0E0"

    INFARED = "#E52321"
    DAWN = "#EC641D"
    ACID_GREEN = "#06FF89"
    ELECTRIC_BLUE = "#16E9D8"
    SOLAR_AMBER = "#FFBA36"

    fig, ax1 = plt.subplots(figsize=(14, 6.5), facecolor=LIGHT_BG)
    ax1.set_facecolor(LIGHT_BG)

    # Theoretical capacity ceiling: 3.1 TPS realistic × 432,000 s/epoch × 0.19 ADA/tx
    REALISTIC_TPS = 3.1
    EPOCH_SECONDS = 432_000
    AVG_FEE_PER_TX = 0.19  # ADA
    theo_capacity_fee = REALISTIC_TPS * EPOCH_SECONDS * AVG_FEE_PER_TX  # ~254,448 ADA

    # Main line in ELECTRIC_BLUE
    ax1.plot(epochs[complete_mask], fees[complete_mask] / 1_000.0, color=ELECTRIC_BLUE, linewidth=2.0, label="Transaction fees", zorder=3)

    # Rolling average in SOLAR_AMBER
    ax1.axhline(last_month_avg_fee / 1_000.0, color=SOLAR_AMBER, linewidth=2.0, linestyle="-", label="Last 30-day average", zorder=3)

    # Theoretical capacity ceiling dashed INFARED
    ax1.axhline(
        theo_capacity_fee / 1_000.0,
        color=INFARED,
        linewidth=1.8,
        linestyle="--",
        label=f"Capacity ceiling",
        zorder=2,
    )
    ax1.axhspan(
        theo_capacity_fee * 0.85 / 1_000.0,
        theo_capacity_fee * 1.15 / 1_000.0,
        color=INFARED,
        alpha=0.06,
        zorder=1,
    )

    ax1.scatter(
        [rows[min_complete_idx].epoch_no, rows[max_complete_idx].epoch_no],
        [fees[min_complete_idx] / 1_000.0, fees[max_complete_idx] / 1_000.0],
        color=[ACID_GREEN, DAWN],
        s=48,
        zorder=5,
        edgecolors=TEXT_DARK,
        linewidths=0.8,
    )
    ax1.annotate(
        f"low complete\n{rows[min_complete_idx].epoch_no} {format_date(rows[min_complete_idx].start_time_utc)}\n{fees[min_complete_idx]:,.0f} ADA",
        xy=(rows[min_complete_idx].epoch_no, fees[min_complete_idx] / 1_000.0),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="bottom",
        color=ACID_GREEN,
    )
    ax1.annotate(
        f"high complete\n{rows[max_complete_idx].epoch_no} {format_date(rows[max_complete_idx].start_time_utc)}\n{fees[max_complete_idx]:,.0f} ADA",
        xy=(rows[max_complete_idx].epoch_no, fees[max_complete_idx] / 1_000.0),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="top",
        color=DAWN,
    )

    ax1.set_ylabel("Thousand ADA / epoch", color=TEXT_DARK, fontsize=10)
    ax1.set_xlabel("Epoch", color=TEXT_DARK, fontsize=10)
    ax1.set_title("Transaction fees peaked at 308K ADA — now ~25K per epoch", color=TEXT_DARK, fontsize=12, fontweight="bold", pad=15)
    ax1.legend(loc="upper left", facecolor=LIGHT_BG, edgecolor=GRID_COLOR, framealpha=0.95, fontsize=9, labelcolor=TEXT_DARK)

    # Compute current reserve expansion term for the gap note
    latest_complete_reserve = None
    latest_complete_eta = None
    for row in reversed(rows):
        if row.has_total_rewards:
            # Find matching reserve from CSV
            break
    # Read reserve from CSV for the latest complete epoch
    with data_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            if int(record["epoch_no"]) == latest_complete_row.epoch_no:
                latest_complete_reserve = float(record["Reserve_ada"])
                latest_complete_eta = float(record["eta_mainnet_raw"])
                break
    if latest_complete_reserve and latest_complete_eta:
        reserve_term = min(latest_complete_eta, 1.0) * 0.003 * latest_complete_reserve
        capacity_vs_expansion = theo_capacity_fee / reserve_term * 100
        gap_note = f"\nRealistic capacity covers only ~{capacity_vs_expansion:.1f}% of reserve expansion"
    else:
        gap_note = ""

    ax1.text(
        0.01,
        0.98,
        f"Latest complete: epoch {latest_complete_row.epoch_no} | Last 30-day avg: {last_month_avg_fee:,.0f} ADA/epoch",
        transform=ax1.transAxes,
        fontsize=8,
        va="top",
        ha="left",
        color=DIM_TEXT,
    )

    # Style axes
    ax1.tick_params(colors=DIM_TEXT, labelsize=9)
    ax1.spines['bottom'].set_color(GRID_COLOR)
    ax1.spines['left'].set_color(GRID_COLOR)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)

    tick_count = min(11, len(rows))
    tick_idx = np.unique(np.linspace(0, len(rows) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(epochs[tick_idx])
    ax1.set_xticklabels([f"{epochs[i]}\n{format_date(rows[i].start_time_utc)}" for i in tick_idx], fontsize=8, color=DIM_TEXT)

    add_event_markers(ax1, compact=True, y_frac=0.95)

    fig.tight_layout(rect=[0, 0, 1, 1])
    fig.savefig(fig_path, dpi=180, facecolor=LIGHT_BG, edgecolor="none")
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
