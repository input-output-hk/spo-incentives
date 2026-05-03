#!/usr/bin/env python3
"""
Build a mainnet history visual for the obligation-pot deposit stocks since Shelley.

Important:
This is not the exact epoch-level Deposit^{epoch}_{nonRefundable} flow used in the
reward-pot formula. It is the available proxy from current Koios inputs:

  deposits_total = deposits_stake + deposits_drep + deposits_proposal

Outputs:
  - scenarii-evaluation/figures/deposit_obligation_history_mainnet.png
  - scenarii-evaluation/outputs/deposit_obligation_history_mainnet.md
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
    deposit_stake_ada: Optional[float]
    deposit_drep_ada: Optional[float]
    deposit_proposal_ada: Optional[float]


def parse_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    return float(stripped)


def parse_lovelace_to_ada(value: str | None) -> Optional[float]:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return parsed / 1_000_000.0


def parse_utc(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=timezone.utc)


def format_date(value: Optional[str]) -> str:
    if not value:
        return "n/a"
    return value[:10]


def load_rows(path: Path) -> List[EpochRow]:
    rows: List[EpochRow] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            rows.append(
                EpochRow(
                    epoch_no=int(record["epoch_no"]),
                    start_time_utc=record.get("start_time_utc"),
                    deposit_stake_ada=parse_lovelace_to_ada(record.get("Deposit_stake_lovelace")),
                    deposit_drep_ada=parse_lovelace_to_ada(record.get("Deposit_drep_lovelace")),
                    deposit_proposal_ada=parse_lovelace_to_ada(record.get("Deposit_proposal_lovelace")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def main() -> None:
    REPORT_DIR = Path(__file__).resolve().parent.parent
    data_path = REPORT_DIR / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = REPORT_DIR / "figures" / "deposit_obligation_history_mainnet.png"
    notes_path = REPORT_DIR / "data" / "deposit_obligation_history_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    valid_rows = [
        row
        for row in rows
        if row.deposit_stake_ada is not None
        and row.deposit_drep_ada is not None
        and row.deposit_proposal_ada is not None
        and row.start_time_utc is not None
        and row.epoch_no <= 623  # Filter out incomplete epochs
    ]
    if not valid_rows:
        raise RuntimeError("No obligation-pot deposit rows found in the dataset.")

    epochs = np.array([row.epoch_no for row in valid_rows], dtype=int)
    stake = np.array([row.deposit_stake_ada for row in valid_rows], dtype=float)
    drep = np.array([row.deposit_drep_ada for row in valid_rows], dtype=float)
    proposal = np.array([row.deposit_proposal_ada for row in valid_rows], dtype=float)
    total = stake + drep + proposal

    latest_idx = len(valid_rows) - 1
    latest_dt = parse_utc(valid_rows[latest_idx].start_time_utc)
    if latest_dt is None:
        raise RuntimeError("Latest valid deposit row is missing start_time_utc.")

    window_start = latest_dt - timedelta(days=30)
    month_window_indices = [
        i
        for i, row in enumerate(valid_rows)
        if parse_utc(row.start_time_utc) is not None and parse_utc(row.start_time_utc) >= window_start
    ]
    if not month_window_indices:
        raise RuntimeError("No deposit snapshot rows found in the last-30-day window.")

    last_month_avg_total = float(mean(float(total[i]) for i in month_window_indices))

    min_idx = int(np.argmin(total))
    max_idx = int(np.argmax(total))

    # IOG dark brand colours
    DARK_BG = "#FFFFFF"
    WHITE_TEXT = "#FFFFFF"
    DIM_TEXT = "#666666"
    GRID_COLOR = "#E0E0E0"

    INFARED = "#E52321"
    DAWN = "#EC641D"
    ACID_GREEN = "#00B35F"
    ELECTRIC_BLUE = "#0DBFB0"
    ULTRAVIOLET = "#A700FF"

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 9.5),
        sharex=False,
        gridspec_kw={"height_ratios": [1.35, 1.0]},
        facecolor=DARK_BG,
    )
    ax1.set_facecolor(DARK_BG)
    ax2.set_facecolor(DARK_BG)

    # DRep deposits in ELECTRIC_BLUE, proposal deposits in DAWN, total in ACID_GREEN
    ax1.plot(epochs, drep / 1_000_000.0, color=ELECTRIC_BLUE, linewidth=1.4, alpha=0.9, label="DRep deposits", zorder=3)
    ax1.plot(epochs, proposal / 1_000_000.0, color=DAWN, linewidth=1.4, alpha=0.9, label="Proposal deposits", zorder=3)
    ax1.plot(epochs, stake / 1_000_000.0, color="#777777", linewidth=1.0, alpha=0.7, label="Stake/pool deposits", zorder=2)
    ax1.plot(epochs, total / 1_000_000.0, color=ACID_GREEN, linewidth=2.0, label="Total obligation-pot deposits", zorder=4)
    ax1.axhline(last_month_avg_total / 1_000_000.0, color="#555555", linewidth=1.4, linestyle="--", label="Last 30-day average", zorder=2)

    ax1.scatter(
        [epochs[min_idx], epochs[max_idx]],
        [total[min_idx] / 1_000_000.0, total[max_idx] / 1_000_000.0],
        color=[ELECTRIC_BLUE, ACID_GREEN],
        s=48,
        zorder=5,
        edgecolors=WHITE_TEXT,
        linewidths=0.8,
    )
    ax1.annotate(
        f"low\n{epochs[min_idx]} {format_date(valid_rows[min_idx].start_time_utc)}\n{total[min_idx]:,.0f} ADA",
        xy=(epochs[min_idx], total[min_idx] / 1_000_000.0),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="bottom",
        color=ELECTRIC_BLUE,
    )
    ax1.annotate(
        f"high\n{epochs[max_idx]} {format_date(valid_rows[max_idx].start_time_utc)}\n{total[max_idx]:,.0f} ADA",
        xy=(epochs[max_idx], total[max_idx] / 1_000_000.0),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="top",
        color=ACID_GREEN,
    )

    ax1.set_ylabel("Million ADA", color=WHITE_TEXT, fontsize=10)
    ax1.set_title("Governance deposits surge with DRep and proposal activity", color=WHITE_TEXT, fontsize=12, fontweight="bold", pad=15)
    ax1.legend(loc="upper left", facecolor=DARK_BG, edgecolor=GRID_COLOR, framealpha=0.95, fontsize=9)

    # Style ax1
    ax1.tick_params(colors=DIM_TEXT, labelsize=9)
    ax1.spines['bottom'].set_color(GRID_COLOR)
    ax1.spines['left'].set_color(GRID_COLOR)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)

    recent_start_idx = max(0, latest_idx - 47)
    recent_indices = list(range(recent_start_idx, latest_idx + 1))
    recent_epochs = epochs[recent_indices]
    recent_total = total[recent_indices] / 1_000_000.0
    ax2.plot(recent_epochs, recent_total, color=ACID_GREEN, linewidth=2.0, label="Recent total obligation-pot deposits", zorder=3)
    ax2.axhline(last_month_avg_total / 1_000_000.0, color="#555555", linewidth=1.4, linestyle="--", label="Last 30-day average", zorder=2)
    ax2.scatter(
        epochs[month_window_indices],
        total[month_window_indices] / 1_000_000.0,
        color=DAWN,
        s=32,
        zorder=5,
        edgecolors=WHITE_TEXT,
        linewidths=0.6,
        label="Snapshots in last 30-day average",
    )
    ax2.set_ylabel("Million ADA", color=WHITE_TEXT, fontsize=10)
    ax2.set_xlabel("Epoch", color=WHITE_TEXT, fontsize=10)
    ax2.set_title("Recent Trend: Last 48 Epochs", color=WHITE_TEXT, fontsize=11, fontweight="bold", pad=12)
    ax2.legend(loc="upper left", facecolor=DARK_BG, edgecolor=GRID_COLOR, framealpha=0.95, fontsize=9)

    # Style ax2
    ax2.tick_params(colors=DIM_TEXT, labelsize=9)
    ax2.spines['bottom'].set_color(GRID_COLOR)
    ax2.spines['left'].set_color(GRID_COLOR)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)

    # Add event markers to both axes
    add_event_markers(ax1, compact=True, y_frac=0.85, alpha=0.3)
    add_event_markers(ax2, compact=True, y_frac=0.95, alpha=0.3)

    tick_count = min(11, len(valid_rows))
    tick_idx = np.unique(np.linspace(0, len(valid_rows) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(epochs[tick_idx])
    ax1.set_xticklabels([f"{epochs[i]}\n{format_date(valid_rows[i].start_time_utc)}" for i in tick_idx], fontsize=8, color=DIM_TEXT)

    zoom_tick_count = min(10, len(recent_indices))
    zoom_tick_idx = np.unique(np.linspace(0, len(recent_indices) - 1, num=zoom_tick_count, dtype=int))
    ax2.set_xticks(recent_epochs[zoom_tick_idx])
    ax2.set_xticklabels(
        [f"{recent_epochs[i]}\n{format_date(valid_rows[recent_indices[i]].start_time_utc)}" for i in zoom_tick_idx],
        fontsize=8,
        color=DIM_TEXT,
    )

    fig.text(0.5, 0.01, "Generated with IOG Research", ha="center", fontsize=7, color=DIM_TEXT, style="italic")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(fig_path, dpi=180, facecolor=DARK_BG, edgecolor="none")
    plt.close(fig)

    notes_lines = [
        "# Obligation-Pot Deposit History (Mainnet)",
        "",
        "- This is the available proxy from current Koios inputs:",
        "  - `deposits_stake + deposits_drep + deposits_proposal`",
        "- It is not the exact `Deposit^{epoch}_{nonRefundable}` flow from the reward-pot formula.",
        f"- Coverage: epochs **{valid_rows[0].epoch_no}..{valid_rows[-1].epoch_no}**.",
        f"- Latest available snapshot: epoch **{valid_rows[-1].epoch_no}** on **{format_date(valid_rows[-1].start_time_utc)}**.",
        f"- Last 30-day snapshot window uses epochs **{valid_rows[month_window_indices[0]].epoch_no}..{valid_rows[month_window_indices[-1]].epoch_no}** "
        f"from **{format_date(valid_rows[month_window_indices[0]].start_time_utc)}** through **{format_date(valid_rows[month_window_indices[-1]].start_time_utc)}**.",
        f"- Last 30-day average total obligation-pot deposits: **{last_month_avg_total:,.2f} ADA**.",
        f"- Lowest snapshot total: **{total[min_idx]:,.2f} ADA** at epoch **{epochs[min_idx]}** ({format_date(valid_rows[min_idx].start_time_utc)}).",
        f"- Highest snapshot total: **{total[max_idx]:,.2f} ADA** at epoch **{epochs[max_idx]}** ({format_date(valid_rows[max_idx].start_time_utc)}).",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(f"Last 30-day average total deposits proxy: {last_month_avg_total:.6f} ADA")


if __name__ == "__main__":
    main()
