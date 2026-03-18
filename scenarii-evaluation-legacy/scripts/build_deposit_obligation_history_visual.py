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
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "deposit_obligation_history_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "deposit_obligation_history_mainnet.md"

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

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=False,
        gridspec_kw={"height_ratios": [1.35, 1.0]},
    )

    ax1.plot(epochs, total / 1_000_000.0, color="#0b4f6c", linewidth=1.9, label="Total obligation-pot deposits")
    ax1.plot(epochs, stake / 1_000_000.0, color="#2ca02c", linewidth=1.1, alpha=0.8, label="Stake/pool deposits")
    ax1.plot(epochs, drep / 1_000_000.0, color="#9467bd", linewidth=1.1, alpha=0.8, label="DRep deposits")
    ax1.plot(epochs, proposal / 1_000_000.0, color="#cc7a00", linewidth=1.1, alpha=0.8, label="Proposal deposits")
    ax1.axhline(last_month_avg_total / 1_000_000.0, color="#d62728", linewidth=1.2, linestyle=":", label="Last 30-day average")

    ax1.scatter(
        [epochs[min_idx], epochs[max_idx]],
        [total[min_idx] / 1_000_000.0, total[max_idx] / 1_000_000.0],
        color=["#7f3c8d", "#1b9e77"],
        s=38,
        zorder=5,
    )
    ax1.annotate(
        f"low\n{epochs[min_idx]} {format_date(valid_rows[min_idx].start_time_utc)}\n{total[min_idx]:,.0f} ADA",
        xy=(epochs[min_idx], total[min_idx] / 1_000_000.0),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="bottom",
        color="#4b1d57",
    )
    ax1.annotate(
        f"high\n{epochs[max_idx]} {format_date(valid_rows[max_idx].start_time_utc)}\n{total[max_idx]:,.0f} ADA",
        xy=(epochs[max_idx], total[max_idx] / 1_000_000.0),
        xytext=(8, -10),
        textcoords="offset points",
        fontsize=8,
        ha="left",
        va="top",
        color="#155d46",
    )

    ax1.set_ylabel("Million ADA")
    ax1.set_title("Cardano Mainnet Obligation-Pot Deposits Since Shelley")
    ax1.legend(loc="upper left")
    ax1.text(
        0.01,
        0.98,
        "Available proxy only: this is the obligation-pot stock\n"
        "not the exact epoch-level non-refundable deposit flow from the reward formula.\n"
        f"Last 30-day snapshot average: {last_month_avg_total:,.0f} ADA",
        transform=ax1.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    recent_start_idx = max(0, latest_idx - 47)
    recent_indices = list(range(recent_start_idx, latest_idx + 1))
    recent_epochs = epochs[recent_indices]
    recent_total = total[recent_indices] / 1_000_000.0
    ax2.plot(recent_epochs, recent_total, color="#0b4f6c", linewidth=1.8, label="Recent total obligation-pot deposits")
    ax2.axhline(last_month_avg_total / 1_000_000.0, color="#d62728", linewidth=1.2, linestyle=":", label="Last 30-day average")
    ax2.scatter(
        epochs[month_window_indices],
        total[month_window_indices] / 1_000_000.0,
        color="#d62728",
        s=28,
        zorder=5,
        label="Snapshots in last 30-day average",
    )
    ax2.set_ylabel("Million ADA")
    ax2.set_xlabel("Epoch")
    ax2.set_title("Recent Zoom With the Last 30-Day Snapshot Window")
    ax2.legend(loc="upper left")

    tick_count = min(11, len(valid_rows))
    tick_idx = np.unique(np.linspace(0, len(valid_rows) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(epochs[tick_idx])
    ax1.set_xticklabels([f"{epochs[i]}\n{format_date(valid_rows[i].start_time_utc)}" for i in tick_idx])

    zoom_tick_count = min(10, len(recent_indices))
    zoom_tick_idx = np.unique(np.linspace(0, len(recent_indices) - 1, num=zoom_tick_count, dtype=int))
    ax2.set_xticks(recent_epochs[zoom_tick_idx])
    ax2.set_xticklabels(
        [f"{recent_epochs[i]}\n{format_date(valid_rows[recent_indices[i]].start_time_utc)}" for i in zoom_tick_idx]
    )

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
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
