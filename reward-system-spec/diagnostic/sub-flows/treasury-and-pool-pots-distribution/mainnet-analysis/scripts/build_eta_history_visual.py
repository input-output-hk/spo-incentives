#!/usr/bin/env python3
"""
Build a mainnet history visual for eta from Shelley to the current epoch.

Definition from SL-D1:
  eta_epoch = Blocks_produced_epoch / Blocks_expected_epoch

For mainnet, expected blocks per epoch are derived from genesis constants:
  Blocks_expected_epoch = epoch_length_slots * active_slot_coeff

Outputs:
  - scenarii-evaluation/figures/eta_history_mainnet.png
  - scenarii-evaluation/outputs/eta_history_mainnet.md
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
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
    blk_count_epoch: Optional[int]
    expected_blocks_epoch: Optional[float]
    eta_raw: Optional[float]
    eta_capped: Optional[float]


def parse_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    return float(stripped)


def parse_int(value: str | None) -> Optional[int]:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(parsed)


def load_rows(path: Path) -> List[EpochRow]:
    rows: List[EpochRow] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            rows.append(
                EpochRow(
                    epoch_no=int(record["epoch_no"]),
                    start_time_utc=record.get("start_time_utc"),
                    blk_count_epoch=parse_int(record.get("blk_count_epoch")),
                    expected_blocks_epoch=parse_float(record.get("expected_blocks_epoch_mainnet")),
                    eta_raw=parse_float(record.get("eta_mainnet_raw")),
                    eta_capped=parse_float(record.get("eta_mainnet_capped")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    result = np.full(shape=len(values), fill_value=np.nan, dtype=float)
    if len(values) < window:
        return result
    kernel = np.ones(window, dtype=float) / float(window)
    result[window - 1 :] = np.convolve(values, kernel, mode="valid")
    return result


def format_date(iso: Optional[str]) -> str:
    if not iso:
        return "n/a"
    return iso[:10]


def main() -> None:
    REPORT_DIR = Path(__file__).resolve().parent.parent
    data_path = REPORT_DIR / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = REPORT_DIR / "figures" / "eta_history_mainnet.png"
    notes_path = REPORT_DIR / "data" / "eta_history_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    eta_raw = np.array([np.nan if row.eta_raw is None else row.eta_raw for row in rows], dtype=float)
    eta_capped = np.array([np.nan if row.eta_capped is None else row.eta_capped for row in rows], dtype=float)

    # Filter out incomplete/current epoch (last epoch may have partial data)
    if len(epochs) > 0 and epochs[-1] > 623:
        # Only keep up to the last complete epoch with reward data
        mask_complete_data = epochs <= 623
        epochs = epochs[mask_complete_data]
        eta_raw = eta_raw[mask_complete_data]
        eta_capped = eta_capped[mask_complete_data]
        rows = [row for i, row in enumerate(rows) if i < len(rows) and rows[i].epoch_no <= 623]

    current_epoch = int(epochs[-1])
    complete_mask = epochs < current_epoch
    current_mask = epochs == current_epoch

    if not np.any(complete_mask):
        raise RuntimeError("Need at least one complete epoch before the current epoch to build the visual.")

    complete_epochs = epochs[complete_mask]
    complete_eta_raw = eta_raw[complete_mask]
    complete_eta_capped = eta_capped[complete_mask]
    complete_dates = [rows[i].start_time_utc for i in range(len(rows)) if complete_mask[i]]

    roll_window = 12
    roll_eta = rolling_mean(complete_eta_raw, window=roll_window)

    complete_values = complete_eta_raw[~np.isnan(complete_eta_raw)]
    min_eta = float(np.min(complete_values))
    max_eta = float(np.max(complete_values))
    avg_eta = float(mean(float(v) for v in complete_values))
    over_one_count = int(np.sum(complete_eta_raw > 1.0))

    low_indices = np.argsort(complete_eta_raw)[:3]
    high_indices = np.argsort(complete_eta_raw)[-3:][::-1]

    current_epoch_value = float(eta_raw[current_mask][0]) if np.any(current_mask) else float("nan")
    expected_blocks_epoch = rows[0].expected_blocks_epoch
    blk_count_current = rows[-1].blk_count_epoch

    # IOG dark brand colors
    BG_COLOR = "#FFFFFF"
    TEXT_WHITE = "#1A1A1A"
    TEXT_DIM = "#666666"
    GRID_COLOR = "#E0E0E0"
    ELECTRIC_BLUE = "#0DBFB0"
    ACID_GREEN = "#00B35F"
    SOLAR_AMBER = "#FFBA36"
    INFARED = "#E52321"

    # Calculate percentage of potential rewards lost
    potential_lost_pct = (1.0 - avg_eta) * 100.0

    # Create figure with dark background
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(16, 9),
        sharex=False,
        gridspec_kw={"height_ratios": [1.15, 1.0]},
        facecolor=BG_COLOR,
    )

    # Panel 1: Full history with key events
    ax1.set_facecolor(BG_COLOR)
    ax1.plot(
        complete_epochs,
        complete_eta_raw,
        color=ELECTRIC_BLUE,
        linewidth=2.0,
        label="Raw η",
        alpha=0.95,
    )
    ax1.plot(
        complete_epochs,
        complete_eta_capped,
        color=ACID_GREEN,
        linewidth=1.5,
        linestyle="--",
        label="Capped η (used in formula)",
        alpha=0.85,
    )
    ax1.axhline(1.0, color=GRID_COLOR, linestyle=":", linewidth=1.2, alpha=0.6)

    # Annotate anomalies (low eta)
    low_annotation_offsets = [(6, -14), (6, -14), (6, 14)]
    for pos, idx in enumerate(low_indices):
        ax1.scatter(complete_epochs[idx], complete_eta_raw[idx], color=INFARED, s=50, zorder=5, alpha=0.9)
        ax1.annotate(
            f"{complete_epochs[idx]} ({format_date(complete_dates[idx])})\n{complete_eta_raw[idx]:.3f}",
            xy=(complete_epochs[idx], complete_eta_raw[idx]),
            xytext=low_annotation_offsets[pos],
            textcoords="offset points",
            fontsize=7.5,
            ha="left",
            va="bottom" if low_annotation_offsets[pos][1] > 0 else "top",
            color=INFARED,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=BG_COLOR, edgecolor=INFARED, alpha=0.7, linewidth=0.8),
        )

    ax1.set_ylabel("η", fontsize=12, color=TEXT_WHITE, weight="bold")
    ax1.set_title(
        f"Network performance η averages {avg_eta:.3f} — {potential_lost_pct:.1f}% of potential rewards lost",
        fontsize=14,
        color=TEXT_WHITE,
        weight="bold",
        pad=16,
    )
    ax1.set_ylim(min(0.45, float(np.nanmin(complete_eta_raw)) - 0.03), max(1.02, float(np.nanmax(complete_eta_raw)) + 0.005))
    ax1.legend(loc="upper right", framealpha=0.95, facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_WHITE, fontsize=9)

    # Panel 2: Zoom on complete epochs with rolling mean
    ax2.set_facecolor(BG_COLOR)
    ax2.plot(
        complete_epochs,
        complete_eta_raw,
        color=ELECTRIC_BLUE,
        linewidth=2.0,
        label="Raw η on complete epochs",
        alpha=0.8,
    )
    ax2.plot(
        complete_epochs,
        complete_eta_capped,
        color=ACID_GREEN,
        linewidth=1.2,
        linestyle="--",
        alpha=0.65,
        label="min(η, 1) on complete epochs",
    )
    if np.any(~np.isnan(roll_eta)):
        ax2.plot(
            complete_epochs,
            roll_eta,
            color=SOLAR_AMBER,
            linewidth=2.4,
            alpha=0.95,
            label=f"{roll_window}-epoch rolling mean",
            zorder=4,
        )
    ax2.axhline(1.0, color=GRID_COLOR, linestyle=":", linewidth=1.2, alpha=0.6)

    # Mark low and high anomalies
    for idx in low_indices:
        ax2.scatter(complete_epochs[idx], complete_eta_raw[idx], color=INFARED, s=50, zorder=5, alpha=0.9)
    for idx in high_indices:
        ax2.scatter(complete_epochs[idx], complete_eta_raw[idx], color=ACID_GREEN, s=50, zorder=5, alpha=0.7)

    ax2.set_ylabel("η", fontsize=12, color=TEXT_WHITE, weight="bold")
    ax2.set_xlabel("Epoch", fontsize=12, color=TEXT_WHITE, weight="bold")
    ax2.set_title("Zoom on Complete Epochs — Variance Around 1.0", fontsize=13, color=TEXT_WHITE, weight="bold", pad=12)
    ax2.set_ylim(min_eta - 0.01, max_eta + 0.004)
    ax2.legend(loc="lower left", framealpha=0.95, facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_WHITE, fontsize=9)

    # Styling: grid, spines, ticks
    for ax in [ax1, ax2]:
        ax.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.5, alpha=0.4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(GRID_COLOR)
        ax.spines["left"].set_color(GRID_COLOR)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        ax.xaxis.label.set_color(TEXT_WHITE)
        ax.yaxis.label.set_color(TEXT_WHITE)
        add_event_markers(ax, compact=True, y_frac=0.85, alpha=0.4)

    # X-axis labels
    tick_count = min(11, len(complete_epochs))
    tick_idx = np.unique(np.linspace(0, len(complete_epochs) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(complete_epochs[tick_idx])
    ax1.set_xticklabels([f"{complete_epochs[i]}\n{format_date(complete_dates[i])}" for i in tick_idx], fontsize=7)

    tick_count_zoom = min(10, len(complete_epochs))
    tick_idx_zoom = np.unique(np.linspace(0, len(complete_epochs) - 1, num=tick_count_zoom, dtype=int))
    ax2.set_xticks(complete_epochs[tick_idx_zoom])
    ax2.set_xticklabels(
        [f"{complete_epochs[i]}\n{format_date(complete_dates[i])}" for i in tick_idx_zoom], fontsize=7
    )

    # Add insight bar at bottom
    fig.text(
        0.5,
        0.01,
        f"Insight: Network consistently underperforms ideal 1.0 η due to slot leader competition and adversarial conditions. "
        f"Rolling mean highlights sustained recovery patterns.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=SOLAR_AMBER,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.6", facecolor=BG_COLOR, edgecolor=SOLAR_AMBER, alpha=0.6, linewidth=1),
    )

    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(fig_path, dpi=180, facecolor=BG_COLOR)
    plt.close(fig)

    notes_lines = [
        "# Eta History (Mainnet)",
        "",
        "- Definition: `eta_epoch = Blocks_produced_epoch / Blocks_expected_epoch`.",
        "- Mainnet constants from Koios genesis: `active slot coeff = 0.05`, `epoch length = 432000`, so `Blocks_expected_epoch = 21600`.",
        f"- Coverage in the refreshed dataset: epochs **{int(epochs[0])}..{current_epoch}**.",
        f"- Graph shows complete epochs only: **{int(complete_epochs[0])}..{int(complete_epochs[-1])}**.",
        f"- Complete-epoch average eta: **{avg_eta:.6f}**.",
        f"- Complete-epoch minimum eta: **{min_eta:.6f}** at epoch **{int(complete_epochs[low_indices[0]])}** ({format_date(complete_dates[low_indices[0]])}).",
        f"- Complete-epoch maximum eta: **{max_eta:.6f}** at epoch **{int(complete_epochs[high_indices[0]])}** ({format_date(complete_dates[high_indices[0]])}).",
        f"- Complete epochs with `eta > 1`: **{over_one_count}**. These are clipped by `min(eta, 1)` in the reward-pot formula.",
        "",
        "## Lowest complete epochs",
    ]
    for idx in low_indices:
        row_index = int(np.where(epochs == complete_epochs[idx])[0][0])
        row = rows[row_index]
        notes_lines.append(
            f"- Epoch **{row.epoch_no}** ({format_date(row.start_time_utc)}): "
            f"`eta = {complete_eta_raw[idx]:.6f}` from `{row.blk_count_epoch}` blocks out of `{row.expected_blocks_epoch:.0f}` expected."
        )

    notes_lines.extend(
        [
            "",
            "## Highest complete epochs",
        ]
    )
    for idx in high_indices:
        row_index = int(np.where(epochs == complete_epochs[idx])[0][0])
        row = rows[row_index]
        notes_lines.append(
            f"- Epoch **{row.epoch_no}** ({format_date(row.start_time_utc)}): "
            f"`eta = {complete_eta_raw[idx]:.6f}` from `{row.blk_count_epoch}` blocks out of `{row.expected_blocks_epoch:.0f}` expected."
        )

    notes_lines.extend(
        [
            "",
            "## Current partial epoch",
            f"- Epoch **{current_epoch}** ({format_date(rows[-1].start_time_utc)}): "
            f"`eta_so_far = {current_epoch_value:.6f}` from `{blk_count_current}` blocks so far out of `{expected_blocks_epoch:.0f}` expected.",
        ]
    )
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")


if __name__ == "__main__":
    main()
