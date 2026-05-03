#!/usr/bin/env python3
"""
Build a mainnet treasury-per-epoch visual with source decomposition and data checks.

Available decomposition from current inputs:
  - Treasury from fees: tau * Fee^epoch_tx
  - Treasury from monetary expansion: tau * g(d) * min(eta,1) * rho * Reserve

Important limitation:
  - Deposit^{epoch}_{nonRefundable} is not available as an epoch-level flow in the
    current Koios inputs, so the deposit component cannot be decomposed directly.

Verification:
  - Compare the treasury inflow proxy above to the observed treasury stock delta
    between epochs. Mismatches are expected when treasury outflows occur and when
    the deposit flow is missing.

Outputs:
  - scenarii-evaluation/figures/treasury_epoch_source_mainnet.png
  - scenarii-evaluation/outputs/treasury_epoch_source_mainnet.md
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import median
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
    fee_epoch_ada: Optional[float]
    reserve_ada: Optional[float]
    treasury_ada: Optional[float]
    rho: Optional[float]
    tau: Optional[float]
    eta_capped: Optional[float]
    d: Optional[float]
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
                    fee_epoch_ada=parse_float(record.get("Fee_epoch_ada")),
                    reserve_ada=parse_float(record.get("Reserve_ada")),
                    treasury_ada=parse_float(record.get("Treasury_ada")),
                    rho=parse_float(record.get("rho_monetary_expand_rate")),
                    tau=parse_float(record.get("tau_treasury_growth_rate")),
                    eta_capped=parse_float(record.get("eta_mainnet_capped")),
                    d=parse_float(record.get("d_decentralisation")),
                    has_total_rewards=parse_bool(record.get("has_total_rewards")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def main() -> None:
    REPORT_DIR = Path(__file__).resolve().parent.parent
    data_path = REPORT_DIR / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = REPORT_DIR / "figures" / "treasury_epoch_source_mainnet.png"
    notes_path = REPORT_DIR / "data" / "treasury_epoch_source_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    fee = np.array([np.nan if row.fee_epoch_ada is None else row.fee_epoch_ada for row in rows], dtype=float)
    reserve = np.array([np.nan if row.reserve_ada is None else row.reserve_ada for row in rows], dtype=float)
    treasury_stock = np.array([np.nan if row.treasury_ada is None else row.treasury_ada for row in rows], dtype=float)
    rho = np.array([np.nan if row.rho is None else row.rho for row in rows], dtype=float)
    tau = np.array([np.nan if row.tau is None else row.tau for row in rows], dtype=float)
    eta = np.array([np.nan if row.eta_capped is None else row.eta_capped for row in rows], dtype=float)
    d = np.array([np.nan if row.d is None else row.d for row in rows], dtype=float)

    # Filter out incomplete/current epoch (last epoch may have partial data)
    if len(epochs) > 0 and epochs[-1] > 623:
        # Only keep up to the last complete epoch with reward data
        mask_complete = epochs <= 623
        epochs = epochs[mask_complete]
        fee = fee[mask_complete]
        reserve = reserve[mask_complete]
        treasury_stock = treasury_stock[mask_complete]
        rho = rho[mask_complete]
        tau = tau[mask_complete]
        eta = eta[mask_complete]
        d = d[mask_complete]
        rows = [row for i, row in enumerate(rows) if i < len(rows) and rows[i].epoch_no <= 623]

    gate = np.where(np.isnan(d), np.nan, np.where(d >= 1.0, 0.0, 1.0))
    treasury_from_fee = tau * fee
    treasury_from_reserve = tau * gate * eta * rho * reserve
    treasury_total_proxy = treasury_from_fee + treasury_from_reserve

    treasury_delta = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    prev_stock = np.nan
    for i, value in enumerate(treasury_stock):
        if np.isnan(value):
            continue
        if not np.isnan(prev_stock):
            treasury_delta[i] = value - prev_stock
        prev_stock = value

    verification_mask = (
        (epochs >= 211)
        & (epochs <= 623)
        & ~np.isnan(treasury_total_proxy)
        & ~np.isnan(treasury_delta)
    )
    if not np.any(verification_mask):
        raise RuntimeError("No verification window available.")

    verification_errors = treasury_delta[verification_mask] - treasury_total_proxy[verification_mask]
    verification_abs_errors = np.abs(verification_errors)
    median_abs_error = float(median(float(x) for x in verification_abs_errors))
    count_within_100k = int(np.sum(verification_abs_errors <= 100_000.0))
    total_verified = int(np.sum(verification_mask))
    negative_delta_epochs = int(np.sum(treasury_delta[verification_mask] < 0.0))

    current_idx = len(rows) - 1
    current_epoch = int(epochs[current_idx])
    current_fee_cut = float(treasury_from_fee[current_idx])
    current_reserve_cut = float(treasury_from_reserve[current_idx])
    current_total_proxy = float(treasury_total_proxy[current_idx])

    # Exclude current partial epoch from plot data
    plot_mask = np.arange(len(rows)) < current_idx
    plot_epochs = epochs[plot_mask]
    plot_treasury_from_fee = treasury_from_fee[plot_mask]
    plot_treasury_from_reserve = treasury_from_reserve[plot_mask]
    plot_treasury_total_proxy = treasury_total_proxy[plot_mask]

    # IOG light brand palette
    BACKGROUND = "#FAFAFA"
    GRID_COLOR = "#E0E0E0"
    TEXT_COLOR = "#1A1A1A"
    DIM_TEXT = "#666666"
    ELECTRIC_BLUE = "#16E9D8"  # Monetary expansion component
    DAWN = "#EC641D"  # Fee component
    ACID_GREEN = "#06FF89"  # Total
    INFARED = "#E52321"  # Negative deltas
    SOLAR_AMBER = "#FFBA36"  # Insight bar

    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(16, 12),
        sharex=False,
        gridspec_kw={"height_ratios": [1.2, 0.9, 1.1]},
        facecolor=BACKGROUND,
    )

    # Panel 1: Stacked area for treasury inflow sources
    ax1.set_facecolor(BACKGROUND)
    ax1.stackplot(
        plot_epochs,
        plot_treasury_from_fee / 1_000_000.0,
        plot_treasury_from_reserve / 1_000_000.0,
        colors=[DAWN, ELECTRIC_BLUE],
        alpha=0.85,
        labels=["Transaction fees", "Reserve expansion"],
    )
    ax1.plot(
        plot_epochs,
        plot_treasury_total_proxy / 1_000_000.0,
        color=ACID_GREEN,
        linewidth=2.0,
        label="Treasury share",
    )
    ax1.set_ylabel("Million ADA / epoch", color=TEXT_COLOR, fontsize=11, fontweight="500")
    ax1.set_title(
        "Treasury inflow: Fee and monetary expansion components",
        color=TEXT_COLOR,
        fontsize=13,
        fontweight="600",
        pad=16,
    )
    ax1.legend(loc="upper right", framealpha=0.92, facecolor=BACKGROUND, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=9)
    ax1.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)
    ax1.tick_params(colors=DIM_TEXT, labelsize=10)
    ax1.spines["top"].set_color(GRID_COLOR)
    ax1.spines["right"].set_color(GRID_COLOR)
    ax1.spines["left"].set_color(GRID_COLOR)
    ax1.spines["bottom"].set_color(GRID_COLOR)
    add_event_markers(ax1, compact=True, y_frac=0.85, alpha=0.4)

    # Panel 2: Fee-side treasury cut recent window
    fee_focus_start_idx = max(0, current_idx - 95)
    fee_focus_indices = list(range(fee_focus_start_idx, current_idx))
    ax2.set_facecolor(BACKGROUND)
    ax2.plot(
        epochs[fee_focus_indices],
        treasury_from_fee[fee_focus_indices] / 1_000.0,
        color=DAWN,
        linewidth=2.2,
        label="Fee-side treasury share",
        marker="o",
        markersize=4,
        alpha=0.9,
    )
    ax2.set_ylabel("Thousand ADA / epoch", color=TEXT_COLOR, fontsize=11, fontweight="500")
    ax2.set_title("Treasury from fees (95-epoch window)", color=TEXT_COLOR, fontsize=13, fontweight="600", pad=14)
    ax2.legend(loc="upper right", framealpha=0.92, facecolor=BACKGROUND, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=9)
    ax2.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)
    ax2.tick_params(colors=DIM_TEXT, labelsize=10)
    ax2.spines["top"].set_color(GRID_COLOR)
    ax2.spines["right"].set_color(GRID_COLOR)
    ax2.spines["left"].set_color(GRID_COLOR)
    ax2.spines["bottom"].set_color(GRID_COLOR)
    add_event_markers(ax2, compact=True, y_frac=0.85, alpha=0.4)

    # Panel 3: Verification — proxy vs observed treasury stock delta
    positive_mask = ~np.isnan(treasury_delta) & (treasury_delta >= 0.0)
    negative_mask = ~np.isnan(treasury_delta) & (treasury_delta < 0.0)
    ax3.set_facecolor(BACKGROUND)
    ax3.bar(
        epochs[positive_mask],
        treasury_delta[positive_mask] / 1_000_000.0,
        color=ELECTRIC_BLUE,
        width=0.9,
        label="Treasury stock delta (positive)",
        alpha=0.8,
    )
    ax3.bar(
        epochs[negative_mask],
        treasury_delta[negative_mask] / 1_000_000.0,
        color=INFARED,
        width=0.9,
        label="Treasury stock delta (negative)",
        alpha=0.85,
    )
    ax3.plot(
        plot_epochs,
        plot_treasury_total_proxy / 1_000_000.0,
        color=ACID_GREEN,
        linewidth=2.0,
        label="Treasury share (computed)",
    )
    ax3.axhline(0.0, color=GRID_COLOR, linewidth=1.2, alpha=0.6)
    ax3.set_ylabel("Million ADA / epoch", color=TEXT_COLOR, fontsize=11, fontweight="500")
    ax3.set_xlabel("Epoch", color=TEXT_COLOR, fontsize=11, fontweight="500")
    ax3.set_title("Proxy validation vs observed stock changes", color=TEXT_COLOR, fontsize=13, fontweight="600", pad=14)
    ax3.legend(loc="upper right", framealpha=0.92, facecolor=BACKGROUND, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=9)
    ax3.grid(True, color=GRID_COLOR, alpha=0.3, linestyle="-", linewidth=0.5)
    ax3.tick_params(colors=DIM_TEXT, labelsize=10)
    ax3.spines["top"].set_color(GRID_COLOR)
    ax3.spines["right"].set_color(GRID_COLOR)
    ax3.spines["left"].set_color(GRID_COLOR)
    ax3.spines["bottom"].set_color(GRID_COLOR)
    add_event_markers(ax3, compact=True, y_frac=0.95, alpha=0.4)

    # Insight bar for verification metrics
    ax3.text(
        0.01,
        0.95,
        f"Window: epochs 211–623 | Median error: {median_abs_error:,.0f} ADA | Within 100k ADA: {count_within_100k}/{total_verified} | Negative deltas: {negative_delta_epochs}",
        transform=ax3.transAxes,
        fontsize=10,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.5", facecolor=SOLAR_AMBER, edgecolor="none", alpha=0.15),
        color=TEXT_COLOR,
    )

    tick_count = min(11, len(plot_epochs))
    tick_idx = np.unique(np.linspace(0, len(plot_epochs) - 1, num=tick_count, dtype=int))
    ax1.set_xticks(plot_epochs[tick_idx])
    ax1.set_xticklabels([f"{plot_epochs[i]}\n{format_date(rows[np.where(epochs == plot_epochs[i])[0][0]].start_time_utc)}" for i in tick_idx])

    tick_count_fee = min(9, len(fee_focus_indices))
    fee_tick_idx = np.unique(np.linspace(0, len(fee_focus_indices) - 1, num=tick_count_fee, dtype=int))
    ax2.set_xticks(epochs[fee_focus_indices][fee_tick_idx])
    ax2.set_xticklabels(
        [f"{epochs[fee_focus_indices[i]]}\n{format_date(rows[fee_focus_indices[i]].start_time_utc)}" for i in fee_tick_idx]
    )

    ax3.set_xticks(plot_epochs[tick_idx])
    ax3.set_xticklabels([f"{plot_epochs[i]}\n{format_date(rows[np.where(epochs == plot_epochs[i])[0][0]].start_time_utc)}" for i in tick_idx])

    fig.tight_layout()
    fig.savefig(fig_path, dpi=180, facecolor=BACKGROUND)
    plt.close(fig)

    notes_lines = [
        "# Treasury Per-Epoch Source Decomposition (Mainnet)",
        "",
        "## What is directly decomposed from current inputs",
        r"- Treasury from fees: $\tau \cdot Fee^{epoch}_{tx}$.",
        r"- Treasury from monetary expansion: $\tau g(d)\min(\eta,1)\rho \cdot Reserve$.",
        r"- Treasury from deposits: not directly available because `Deposit^{epoch}_{nonRefundable}` is not present as an epoch flow in the current Koios dataset.",
        "",
        "## Current partial epoch",
        f"- Epoch **{current_epoch}** ({format_date(rows[current_idx].start_time_utc)}):",
        f"  - fee-side treasury cut = **{current_fee_cut:,.2f} ADA**",
        f"  - reserve-side treasury cut = **{current_reserve_cut:,.2f} ADA**",
        f"  - total treasury inflow proxy = **{current_total_proxy:,.2f} ADA**",
        "",
        "## Verification against treasury stock data",
        "- Observed stock data used for the check: `Treasury_ada` from the timeseries.",
        "- Verification compares the source-based inflow proxy to the net stock delta between epochs.",
        "- They do not match exactly when treasury outflows happen and when the deposit flow is missing from inputs.",
        f"- Window used: epochs **211..623**.",
        f"- Median absolute gap between proxy inflow and treasury stock delta: **{median_abs_error:,.2f} ADA**.",
        f"- Epochs within **100k ADA** of the stock delta: **{count_within_100k}/{total_verified}**.",
        f"- Epochs with negative treasury stock delta in that window: **{negative_delta_epochs}**.",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(f"Current epoch {current_epoch} treasury proxy: fee={current_fee_cut:.6f} reserve={current_reserve_cut:.6f} total={current_total_proxy:.6f}")
    print(f"Verification median abs gap: {median_abs_error:.6f} ADA | within 100k: {count_within_100k}/{total_verified}")


if __name__ == "__main__":
    main()
