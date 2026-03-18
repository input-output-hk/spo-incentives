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

    # IOG dark brand colours
    DARK_BG = "#FFFFFF"
    WHITE_TEXT = "#FFFFFF"
    DIM_TEXT = "#666666"
    GRID_COLOR = "#E0E0E0"

    INFARED = "#E52321"
    DAWN = "#EC641D"
    ACID_GREEN = "#00B35F"
    ELECTRIC_BLUE = "#0DBFB0"
    SOLAR_AMBER = "#FFBA36"

    fig, ax1 = plt.subplots(figsize=(14, 6.5), facecolor=DARK_BG)
    ax1.set_facecolor(DARK_BG)

    # Theoretical capacity ceiling: 3.1 TPS realistic × 432,000 s/epoch × 0.19 ADA/tx
    REALISTIC_TPS = 3.1
    EPOCH_SECONDS = 432_000
    AVG_FEE_PER_TX = 0.19  # ADA
    theo_capacity_fee = REALISTIC_TPS * EPOCH_SECONDS * AVG_FEE_PER_TX  # ~254,448 ADA

    # Main line in ELECTRIC_BLUE
    ax1.plot(epochs[complete_mask], fees[complete_mask] / 1_000.0, color=ELECTRIC_BLUE, linewidth=2.0, label=r"Complete epochs: $Fee^{epoch}_{tx}$", zorder=3)

    if np.any(partial_mask):
        ax1.plot(
            epochs[partial_mask],
            fees[partial_mask] / 1_000.0,
            color=INFARED,
            linewidth=1.6,
            linestyle="--",
            marker="D",
            markersize=4,
            label="Current / incomplete epochs",
            zorder=2,
        )

    # Rolling average in SOLAR_AMBER
    ax1.axhline(last_month_avg_fee / 1_000.0, color=SOLAR_AMBER, linewidth=2.0, linestyle="-", label="Last 30-day average", zorder=3)

    # Theoretical capacity ceiling dashed INFARED
    ax1.axhline(
        theo_capacity_fee / 1_000.0,
        color=INFARED,
        linewidth=1.8,
        linestyle="--",
        label=f"Realistic capacity ceiling (~{theo_capacity_fee/1_000:.0f}K ADA at {REALISTIC_TPS} TPS)",
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
        edgecolors=WHITE_TEXT,
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

    ax1.set_ylabel("Thousand ADA / epoch", color=WHITE_TEXT, fontsize=10)
    ax1.set_title("Transaction fees peaked at 308K ADA — now ~25K per epoch", color=WHITE_TEXT, fontsize=12, fontweight="bold", pad=15)
    ax1.legend(loc="upper left", facecolor=DARK_BG, edgecolor=GRID_COLOR, framealpha=0.95, fontsize=9)

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
        f"Latest complete epoch: {latest_complete_row.epoch_no} ({format_date(latest_complete_row.end_time_utc)} end)\n"
        f"Last 30-day complete window: {format_date(rows[month_window_indices[0]].end_time_utc)} to {format_date(rows[month_window_indices[-1]].end_time_utc)}\n"
        f"Average over that window: {last_month_avg_fee:,.0f} ADA / epoch{gap_note}",
        transform=ax1.transAxes,
        fontsize=8,
        va="top",
        ha="left",
        color=WHITE_TEXT,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=GRID_COLOR, edgecolor=SOLAR_AMBER, alpha=0.85),
    )

    ax1.set_xlabel("Epoch", color=WHITE_TEXT, fontsize=10)

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

    # Add insight bar at bottom
    fig.text(0.5, 0.02, "Generated with IOG Research", ha="center", fontsize=7, color=DIM_TEXT, style="italic")

    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(fig_path, dpi=180, facecolor=DARK_BG, edgecolor="none")
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
