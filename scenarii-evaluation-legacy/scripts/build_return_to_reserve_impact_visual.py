#!/usr/bin/env python3
"""
Build a visual for the per-epoch return-to-reserve proxy and its effect on reserve stock.

Definitions used from currently available inputs:
  GrossRewardPot_proxy = Fee + g(d) * min(eta,1) * rho * Reserve
  PoolSidePot_proxy = (1 - tau) * GrossRewardPot_proxy
  ReturnedToReserve_proxy = max(PoolSidePot_proxy - ObservedPaidRewards, 0)

Important limitations:
  - Deposit^{epoch}_{nonRefundable} is missing from current inputs and is omitted.
  - Returned-to-reserve is a proxy derived from the gap between the pool-side pot proxy and
    observed paid rewards, not a direct ledger-state replay.

Outputs:
  - scenarii-evaluation/figures/return_to_reserve_impact_mainnet.png
  - scenarii-evaluation/outputs/return_to_reserve_impact_mainnet.md
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
    observed_paid_ada: Optional[float]
    fee_ada: Optional[float]
    reserve_ada: Optional[float]
    rho: Optional[float]
    tau: Optional[float]
    d: Optional[float]
    eta_capped: Optional[float]
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
                    observed_paid_ada=parse_float(record.get("Reward_epoch_pools_ada")),
                    fee_ada=parse_float(record.get("Fee_epoch_ada")),
                    reserve_ada=parse_float(record.get("Reserve_ada")),
                    rho=parse_float(record.get("rho_monetary_expand_rate")),
                    tau=parse_float(record.get("tau_treasury_growth_rate")),
                    d=parse_float(record.get("d_decentralisation")),
                    eta_capped=parse_float(record.get("eta_mainnet_capped")),
                    has_total_rewards=parse_bool(record.get("has_total_rewards")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "return_to_reserve_impact_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "return_to_reserve_impact_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    observed_paid = np.array([np.nan if row.observed_paid_ada is None else row.observed_paid_ada for row in rows], dtype=float)
    fee = np.array([np.nan if row.fee_ada is None else row.fee_ada for row in rows], dtype=float)
    reserve = np.array([np.nan if row.reserve_ada is None else row.reserve_ada for row in rows], dtype=float)
    rho = np.array([np.nan if row.rho is None else row.rho for row in rows], dtype=float)
    tau = np.array([np.nan if row.tau is None else row.tau for row in rows], dtype=float)
    d = np.array([np.nan if row.d is None else row.d for row in rows], dtype=float)
    eta = np.array([np.nan if row.eta_capped is None else row.eta_capped for row in rows], dtype=float)

    gate = np.where(np.isnan(d), np.nan, np.where(d >= 1.0, 0.0, 1.0))
    gross_proxy = fee + gate * eta * rho * reserve
    pool_side_proxy = (1.0 - tau) * gross_proxy
    return_to_reserve_proxy = np.where(
        np.isnan(pool_side_proxy) | np.isnan(observed_paid),
        np.nan,
        np.maximum(pool_side_proxy - observed_paid, 0.0),
    )

    analysis_mask = (
        (epochs >= 211)
        & (epochs <= 616)
        & ~np.isnan(return_to_reserve_proxy)
        & ~np.isnan(reserve)
    )
    if not np.any(analysis_mask):
        raise RuntimeError("No analysis window available for return-to-reserve.")

    analysis_indices = np.where(analysis_mask)[0]
    analysis_epochs = epochs[analysis_mask]
    analysis_rows = [rows[i] for i in analysis_indices]
    analysis_observed = observed_paid[analysis_mask]
    analysis_pool_side = pool_side_proxy[analysis_mask]
    analysis_return = return_to_reserve_proxy[analysis_mask]
    analysis_reserve = reserve[analysis_mask]

    cumulative_return = np.cumsum(analysis_return)
    reserve_no_return_counterfactual = analysis_reserve - cumulative_return

    median_return = float(median(float(x) for x in analysis_return))
    total_return = float(cumulative_return[-1])
    last_complete_reserve = float(analysis_reserve[-1])
    counterfactual_last_reserve = float(reserve_no_return_counterfactual[-1])

    max_return_idx_local = int(np.argmax(analysis_return))
    max_return_epoch = int(analysis_epochs[max_return_idx_local])
    max_return_value = float(analysis_return[max_return_idx_local])
    max_return_date = format_date(analysis_rows[max_return_idx_local].start_time_utc)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(14, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.1, 1.0, 1.1])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])

    ax1.plot(analysis_epochs, analysis_pool_side / 1_000_000.0, color="#2ca02c", linewidth=1.8, label="Pool-side pot proxy")
    ax1.plot(analysis_epochs, analysis_observed / 1_000_000.0, color="#111111", linewidth=1.6, label="Observed paid rewards")
    ax1.fill_between(
        analysis_epochs,
        analysis_observed / 1_000_000.0,
        analysis_pool_side / 1_000_000.0,
        color="#9467bd",
        alpha=0.24,
        label="Returned-to-reserve proxy",
    )
    ax1.set_ylabel("Million ADA / epoch")
    ax1.set_title("What Returns From the Pool-Side Pot Each Epoch")
    ax1.legend(loc="upper right")
    ax1.text(
        0.01,
        0.98,
        "Returned-to-reserve proxy = max(pool-side pot proxy - observed paid rewards, 0)\n"
        "Deposit flow is unavailable in current inputs and is omitted from the proxy.",
        transform=ax1.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    ax2.bar(
        analysis_epochs,
        analysis_return / 1_000_000.0,
        color="#9467bd",
        width=0.9,
        alpha=0.72,
        label="Returned-to-reserve proxy per epoch",
    )
    ax2_twin = ax2.twinx()
    ax2_twin.plot(
        analysis_epochs,
        cumulative_return / 1_000_000_000.0,
        color="#d62728",
        linewidth=1.7,
        label="Cumulative returned-to-reserve proxy",
    )
    ax2.set_ylabel("Million ADA / epoch")
    ax2_twin.set_ylabel("Cumulative Billion ADA")
    ax2.set_title("Per-Epoch Return and Its Cumulative Effect")
    lines_1, labels_1 = ax2.get_legend_handles_labels()
    lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")
    ax2.text(
        0.01,
        0.98,
        f"Median per-epoch return proxy: {median_return:,.0f} ADA\n"
        f"Cumulative return proxy by epoch {analysis_epochs[-1]}: {total_return/1_000_000_000:.3f}B ADA\n"
        f"Largest return proxy: epoch {max_return_epoch} ({max_return_date}) = {max_return_value/1_000_000:.2f}M ADA",
        transform=ax2.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    ax3.plot(analysis_epochs, analysis_reserve / 1_000_000_000.0, color="#1f77b4", linewidth=1.9, label="Actual reserve stock")
    ax3.plot(
        analysis_epochs,
        reserve_no_return_counterfactual / 1_000_000_000.0,
        color="#ff7f0e",
        linewidth=1.7,
        linestyle="--",
        label="Counterfactual reserve without returned-to-reserve proxy",
    )
    ax3.fill_between(
        analysis_epochs,
        reserve_no_return_counterfactual / 1_000_000_000.0,
        analysis_reserve / 1_000_000_000.0,
        color="#17becf",
        alpha=0.18,
        label="Reserve supported by returned-to-reserve proxy",
    )
    ax3.set_ylabel("Billion ADA")
    ax3.set_xlabel("Epoch")
    ax3.set_title("Impact on the Monetary Expansion Reserve")
    ax3.legend(loc="upper right")
    ax3.text(
        0.01,
        0.98,
        f"At epoch {analysis_epochs[-1]} ({format_date(analysis_rows[-1].start_time_utc)}), actual reserve = {last_complete_reserve/1_000_000_000:.3f}B ADA\n"
        f"Counterfactual without returned-to-reserve proxy = {counterfactual_last_reserve/1_000_000_000:.3f}B ADA",
        transform=ax3.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#cccccc", alpha=0.92),
    )

    tick_count = min(11, len(analysis_epochs))
    tick_idx = np.unique(np.linspace(0, len(analysis_epochs) - 1, num=tick_count, dtype=int))
    tick_epochs = analysis_epochs[tick_idx]
    tick_labels = [f"{analysis_epochs[i]}\n{format_date(analysis_rows[i].start_time_utc)}" for i in tick_idx]
    ax1.set_xticks(tick_epochs)
    ax1.set_xticklabels(tick_labels)
    ax2.set_xticks(tick_epochs)
    ax2.set_xticklabels(tick_labels)
    ax3.set_xticks(tick_epochs)
    ax3.set_xticklabels(tick_labels)

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)

    notes_lines = [
        "# Return-to-Reserve Impact (Mainnet)",
        "",
        "## Proxy definition",
        r"- Gross reward-pot proxy: $Fee + g(d)\min(\eta,1)\rho \cdot Reserve$.",
        r"- Pool-side pot proxy: $(1-\tau)\cdot GrossRewardPot_{proxy}$.",
        r"- Returned-to-reserve proxy: $\max(PoolSidePot_{proxy} - ObservedPaidRewards, 0)$.",
        r"- Deposit^{epoch}_{nonRefundable} is missing from current inputs and is omitted.",
        "",
        "## Analysis window",
        f"- Epochs **{analysis_epochs[0]}..{analysis_epochs[-1]}**.",
        f"- Later epochs are not included because observed paid rewards are not yet available there.",
        "",
        "## Headline numbers",
        f"- Median per-epoch returned-to-reserve proxy: **{median_return:,.2f} ADA**.",
        f"- Cumulative returned-to-reserve proxy by epoch **{analysis_epochs[-1]}**: **{total_return:,.2f} ADA**.",
        f"- Largest epoch return proxy: epoch **{max_return_epoch}** ({max_return_date}) = **{max_return_value:,.2f} ADA**.",
        "",
        "## Reserve impact",
        f"- Actual reserve at epoch **{analysis_epochs[-1]}**: **{last_complete_reserve:,.2f} ADA**.",
        f"- Counterfactual reserve without returned-to-reserve proxy: **{counterfactual_last_reserve:,.2f} ADA**.",
        "- This counterfactual is a simplified accounting illustration, not a full ledger replay.",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(
        f"Cumulative return proxy: {total_return:.6f} ADA | actual reserve: {last_complete_reserve:.6f} | counterfactual: {counterfactual_last_reserve:.6f}"
    )


if __name__ == "__main__":
    main()
