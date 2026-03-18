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
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "treasury_epoch_source_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "treasury_epoch_source_mainnet.md"

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
        & (epochs <= 616)
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

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(14, 12),
        sharex=False,
        gridspec_kw={"height_ratios": [1.2, 0.9, 1.1]},
    )

    ax1.stackplot(
        plot_epochs,
        plot_treasury_from_fee / 1_000_000.0,
        plot_treasury_from_reserve / 1_000_000.0,
        colors=["#ff7f0e", "#1f77b4"],
        alpha=0.78,
        labels=[r"Treasury from fees: $\tau \cdot Fee^{epoch}_{tx}$", r"Treasury from monetary expansion: $\tau g(d)\min(\eta,1)\rho \cdot Reserve$"],
    )
    ax1.plot(plot_epochs, plot_treasury_total_proxy / 1_000_000.0, color="#111111", linewidth=1.3, label="Total treasury inflow proxy")
    ax1.set_ylabel("Million ADA / epoch")
    ax1.set_title("Treasury Inflow Proxy by Source Since Shelley")
    ax1.legend(loc="upper right")
    ax1.text(
        0.01,
        0.98,
        f"Current partial epoch {current_epoch} ({format_date(rows[current_idx].start_time_utc)}): "
        f"fee={current_fee_cut:,.0f} ADA | reserve={current_reserve_cut:,.0f} ADA | total={current_total_proxy:,.0f} ADA\n"
        "Deposit flow unavailable in current inputs, so it is omitted from the source stack.",
        transform=ax1.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    fee_focus_start_idx = max(0, current_idx - 95)
    fee_focus_indices = list(range(fee_focus_start_idx, current_idx))
    ax2.plot(
        epochs[fee_focus_indices],
        treasury_from_fee[fee_focus_indices] / 1_000.0,
        color="#ff7f0e",
        linewidth=1.8,
        label=r"Fee-side treasury cut: $\tau \cdot Fee^{epoch}_{tx}$",
    )
    ax2.set_ylabel("Thousand ADA / epoch")
    ax2.set_title("Fee-Side Treasury Cut (Recent Window)")
    ax2.legend(loc="upper right")

    positive_mask = ~np.isnan(treasury_delta) & (treasury_delta >= 0.0)
    negative_mask = ~np.isnan(treasury_delta) & (treasury_delta < 0.0)
    ax3.bar(
        epochs[positive_mask],
        treasury_delta[positive_mask] / 1_000_000.0,
        color="#bbbbbb",
        width=0.9,
        label="Observed treasury stock delta (positive)",
    )
    ax3.bar(
        epochs[negative_mask],
        treasury_delta[negative_mask] / 1_000_000.0,
        color="#e15759",
        width=0.9,
        label="Observed treasury stock delta (negative)",
    )
    ax3.plot(
        plot_epochs,
        plot_treasury_total_proxy / 1_000_000.0,
        color="#111111",
        linewidth=1.4,
        label="Treasury inflow proxy from available sources",
    )
    ax3.axhline(0.0, color="#666666", linewidth=0.9)
    ax3.set_ylabel("Million ADA / epoch")
    ax3.set_xlabel("Epoch")
    ax3.set_title("Verification Against Treasury Stock Data")
    ax3.legend(loc="upper right")
    ax3.text(
        0.01,
        0.98,
        f"Verification window: epochs 211..616\n"
        f"Median absolute gap between proxy inflow and treasury stock delta: {median_abs_error:,.0f} ADA\n"
        f"Epochs within 100k ADA: {count_within_100k}/{total_verified} | negative treasury-stock delta epochs: {negative_delta_epochs}",
        transform=ax3.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
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
    fig.savefig(fig_path, dpi=220)
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
        f"- Window used: epochs **211..616**.",
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
