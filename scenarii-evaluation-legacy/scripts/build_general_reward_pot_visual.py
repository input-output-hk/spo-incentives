#!/usr/bin/env python3
"""
Build a mainnet visual for the general reward pot per epoch using current inputs.

Available proxy from current dataset:
  GrossRewardPot_proxy = Fee^epoch_tx + g(d) * min(eta,1) * rho * Reserve
  PoolRewardPot_proxy = (1 - tau) * GrossRewardPot_proxy
  TreasuryCut_proxy = tau * GrossRewardPot_proxy

Important limitation:
  - Deposit^{epoch}_{nonRefundable} is not available as an epoch-level flow in the
    current Koios timeseries, so the deposit component is omitted from the source
    decomposition.

Outputs:
  - scenarii-evaluation/figures/general_reward_pot_mainnet.png
  - scenarii-evaluation/outputs/general_reward_pot_mainnet.md
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
    rho: Optional[float]
    tau: Optional[float]
    eta_capped: Optional[float]
    d: Optional[float]
    observed_paid_ada: Optional[float]
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
                    rho=parse_float(record.get("rho_monetary_expand_rate")),
                    tau=parse_float(record.get("tau_treasury_growth_rate")),
                    eta_capped=parse_float(record.get("eta_mainnet_capped")),
                    d=parse_float(record.get("d_decentralisation")),
                    observed_paid_ada=parse_float(record.get("Reward_epoch_pools_ada")),
                    has_total_rewards=parse_bool(record.get("has_total_rewards")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "general_reward_pot_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "general_reward_pot_mainnet.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    fee = np.array([np.nan if row.fee_epoch_ada is None else row.fee_epoch_ada for row in rows], dtype=float)
    reserve = np.array([np.nan if row.reserve_ada is None else row.reserve_ada for row in rows], dtype=float)
    rho = np.array([np.nan if row.rho is None else row.rho for row in rows], dtype=float)
    tau = np.array([np.nan if row.tau is None else row.tau for row in rows], dtype=float)
    eta = np.array([np.nan if row.eta_capped is None else row.eta_capped for row in rows], dtype=float)
    d = np.array([np.nan if row.d is None else row.d for row in rows], dtype=float)
    observed_paid = np.array([np.nan if row.observed_paid_ada is None else row.observed_paid_ada for row in rows], dtype=float)

    gate = np.where(np.isnan(d), np.nan, np.where(d >= 1.0, 0.0, 1.0))
    reserve_term = gate * eta * rho * reserve
    gross_proxy = fee + reserve_term
    treasury_cut_proxy = tau * gross_proxy
    pool_pot_proxy = (1.0 - tau) * gross_proxy

    current_idx = len(rows) - 1
    current_epoch = int(epochs[current_idx])

    # Exclude current partial epoch from plot data
    plot_mask = np.arange(len(rows)) < current_idx
    plot_epochs = epochs[plot_mask]
    plot_fee = fee[plot_mask]
    plot_reserve_term = reserve_term[plot_mask]
    plot_gross_proxy = gross_proxy[plot_mask]
    plot_treasury_cut_proxy = treasury_cut_proxy[plot_mask]
    plot_pool_pot_proxy = pool_pot_proxy[plot_mask]
    plot_observed_paid = observed_paid[plot_mask]

    verification_mask = (
        (epochs >= 211)
        & (epochs <= 616)
        & ~np.isnan(pool_pot_proxy)
        & ~np.isnan(observed_paid)
    )
    if not np.any(verification_mask):
        raise RuntimeError("No verification window found for pool-pot comparison.")

    gap_to_observed = pool_pot_proxy[verification_mask] - observed_paid[verification_mask]
    median_gap = float(median(float(x) for x in np.abs(gap_to_observed)))

    # IOG Dark Brand Colors
    COLOR_BG = "#0A0A0A"
    COLOR_TEXT = "#FFFFFF"
    COLOR_DIM = "#999999"
    COLOR_GRID = "#222222"
    COLOR_INFARED = "#E52321"
    COLOR_DAWN = "#EC641D"
    COLOR_ACID_GREEN = "#06FF89"
    COLOR_ELECTRIC_BLUE = "#16E9D8"
    COLOR_ULTRAVIOLET = "#A700FF"
    COLOR_SOLAR_AMBER = "#FFBA36"
    COLOR_COBALT_PULSE = "#2C4FFA"
    COLOR_VOLT_YELLOW = "#F2FF58"

    # Calculate early and current averages for insight
    early_mask = plot_epochs <= 100
    if np.any(early_mask):
        early_avg = np.nanmean(plot_gross_proxy[early_mask] / 1_000_000.0)
    else:
        early_avg = np.nanmean(plot_gross_proxy[:max(10, len(plot_gross_proxy) // 10)] / 1_000_000.0)
    current_avg = np.nanmean(plot_gross_proxy[-20:] / 1_000_000.0)

    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(16, 12),
        sharex=False,
        gridspec_kw={"height_ratios": [1.15, 1.0, 1.1]},
        facecolor=COLOR_BG,
    )

    # Panel 1: Gross reward pot by source
    ax1.set_facecolor(COLOR_BG)
    ax1.stackplot(
        plot_epochs,
        plot_fee / 1_000_000.0,
        plot_reserve_term / 1_000_000.0,
        colors=[COLOR_DAWN, COLOR_ELECTRIC_BLUE],
        alpha=0.80,
        labels=[r"Fees: $Fee^{epoch}_{tx}$", r"Monetary expansion: $g(d)\min(\eta,1)\rho \cdot Reserve$"],
    )
    ax1.plot(plot_epochs, plot_gross_proxy / 1_000_000.0, color=COLOR_TEXT, linewidth=2.0, label="Gross reward-pot proxy")

    # Styling
    ax1.set_ylabel("Million ADA / epoch", color=COLOR_TEXT, fontsize=11, fontweight="600")
    ax1.set_title(
        f"The Pot Has Halved Since Shelley — From {early_avg:.1f}M to {current_avg:.1f}M ADA/Epoch",
        color=COLOR_TEXT,
        fontsize=13,
        fontweight="700",
        pad=16,
    )
    ax1.tick_params(axis="y", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax1.tick_params(axis="x", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax1.grid(True, color=COLOR_GRID, linestyle="-", linewidth=0.5, alpha=0.4)
    ax1.set_axisbelow(True)

    # Spines
    for spine in ax1.spines.values():
        spine.set_color(COLOR_GRID)
        spine.set_linewidth(0.8)

    leg1 = ax1.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, framealpha=0.95)
    leg1.get_frame().set_linewidth(0.8)

    ax1.text(
        0.01,
        0.98,
        f"Current partial epoch {current_epoch} ({format_date(rows[current_idx].start_time_utc)}): "
        f"fees={fee[current_idx]:,.0f} ADA | reserve term={reserve_term[current_idx]:,.0f} ADA | gross={gross_proxy[current_idx]:,.0f} ADA\n"
        "Deposit flow is unavailable in the current inputs, so it is omitted from this source decomposition.",
        transform=ax1.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        color=COLOR_TEXT,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=COLOR_BG, edgecolor=COLOR_GRID, alpha=0.95, linewidth=0.8),
    )

    # Panel 2: Treasury vs Pool split
    ax2.set_facecolor(COLOR_BG)
    ax2.stackplot(
        plot_epochs,
        plot_treasury_cut_proxy / 1_000_000.0,
        plot_pool_pot_proxy / 1_000_000.0,
        colors=[COLOR_INFARED, COLOR_ACID_GREEN],
        alpha=0.80,
        labels=["Treasury cut proxy", "Pool-side reward-pot proxy"],
    )
    ax2.plot(plot_epochs, plot_gross_proxy / 1_000_000.0, color=COLOR_TEXT, linewidth=2.0, label="Gross reward-pot proxy")

    ax2.set_ylabel("Million ADA / epoch", color=COLOR_TEXT, fontsize=11, fontweight="600")
    ax2.set_title("Treasury vs Pool: How the Pot is Split", color=COLOR_TEXT, fontsize=13, fontweight="700", pad=16)
    ax2.tick_params(axis="y", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax2.tick_params(axis="x", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax2.grid(True, color=COLOR_GRID, linestyle="-", linewidth=0.5, alpha=0.4)
    ax2.set_axisbelow(True)

    for spine in ax2.spines.values():
        spine.set_color(COLOR_GRID)
        spine.set_linewidth(0.8)

    leg2 = ax2.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, framealpha=0.95)
    leg2.get_frame().set_linewidth(0.8)

    # Panel 3: Pool-side proxy vs observed
    ax3.set_facecolor(COLOR_BG)
    ax3.plot(
        plot_epochs,
        plot_pool_pot_proxy / 1_000_000.0,
        color=COLOR_ACID_GREEN,
        linewidth=2.2,
        label="Pool-side reward-pot proxy",
        zorder=2,
    )
    observed_plot_mask = plot_mask & ~np.isnan(observed_paid)
    ax3.plot(
        epochs[observed_plot_mask],
        observed_paid[observed_plot_mask] / 1_000_000.0,
        color=COLOR_ELECTRIC_BLUE,
        linewidth=2.0,
        label="Observed paid pool rewards",
        zorder=2,
    )
    ax3.fill_between(
        epochs[verification_mask],
        observed_paid[verification_mask] / 1_000_000.0,
        pool_pot_proxy[verification_mask] / 1_000_000.0,
        color=COLOR_INFARED,
        alpha=0.25,
        label="Gap to observed",
        zorder=1,
    )

    ax3.set_ylabel("Million ADA / epoch", color=COLOR_TEXT, fontsize=11, fontweight="600")
    ax3.set_xlabel("Epoch (date)", color=COLOR_TEXT, fontsize=11, fontweight="600")
    ax3.set_title("Proxy vs Reality: Where the Pot Diverges", color=COLOR_TEXT, fontsize=13, fontweight="700", pad=16)
    ax3.tick_params(axis="y", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax3.tick_params(axis="x", labelcolor=COLOR_DIM, colors=COLOR_GRID)
    ax3.grid(True, color=COLOR_GRID, linestyle="-", linewidth=0.5, alpha=0.4)
    ax3.set_axisbelow(True)

    for spine in ax3.spines.values():
        spine.set_color(COLOR_GRID)
        spine.set_linewidth(0.8)

    leg3 = ax3.legend(loc="upper right", frameon=True, facecolor=COLOR_BG, edgecolor=COLOR_GRID, labelcolor=COLOR_TEXT, framealpha=0.95)
    leg3.get_frame().set_linewidth(0.8)

    ax3.text(
        0.01,
        0.98,
        f"Comparison window: epochs 211..616\nMedian absolute gap vs observed paid rewards: {median_gap:,.0f} ADA\n"
        "This gap is expected: inactive stake, performance, pledge misses, caps, timing, and missing deposit flow.",
        transform=ax3.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        color=COLOR_TEXT,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=COLOR_BG, edgecolor=COLOR_GRID, alpha=0.95, linewidth=0.8),
    )

    # Configure x-axis labels with dates
    tick_count = min(11, len(plot_epochs))
    tick_idx = np.unique(np.linspace(0, len(plot_epochs) - 1, num=tick_count, dtype=int))
    tick_epochs = plot_epochs[tick_idx]
    tick_labels = [f"{plot_epochs[i]}\n{format_date(rows[np.where(epochs == plot_epochs[i])[0][0]].start_time_utc)}" for i in tick_idx]
    ax1.set_xticks(tick_epochs)
    ax1.set_xticklabels(tick_labels, fontsize=9)
    ax2.set_xticks(tick_epochs)
    ax2.set_xticklabels(tick_labels, fontsize=9)
    ax3.set_xticks(tick_epochs)
    ax3.set_xticklabels(tick_labels, fontsize=9)

    fig.tight_layout()
    fig.savefig(fig_path, dpi=180, facecolor=COLOR_BG, edgecolor="none")
    plt.close(fig)

    notes_lines = [
        "# General Reward Pot Proxy (Mainnet)",
        "",
        "## Proxy definition from current inputs",
        r"- Gross reward-pot proxy: $Fee^{epoch}_{tx} + g(d)\min(\eta,1)\rho \cdot Reserve$.",
        r"- Treasury cut proxy: $\tau \cdot GrossRewardPot_{proxy}$.",
        r"- Pool-side reward-pot proxy: $(1-\tau)\cdot GrossRewardPot_{proxy}$.",
        r"- Deposit^{epoch}_{nonRefundable} is missing from current Koios inputs and therefore omitted.",
        "",
        "## Current partial epoch",
        f"- Epoch **{current_epoch}** ({format_date(rows[current_idx].start_time_utc)}):",
        f"  - fees = **{fee[current_idx]:,.2f} ADA**",
        f"  - reserve term = **{reserve_term[current_idx]:,.2f} ADA**",
        f"  - gross reward-pot proxy = **{gross_proxy[current_idx]:,.2f} ADA**",
        f"  - treasury cut proxy = **{treasury_cut_proxy[current_idx]:,.2f} ADA**",
        f"  - pool-side reward-pot proxy = **{pool_pot_proxy[current_idx]:,.2f} ADA**",
        "",
        "## Comparison to observed paid rewards",
        "- The pool-side proxy is expected to sit above observed paid rewards because it is still upstream of several loss / return-to-reserve mechanisms.",
        f"- On epochs **211..616**, the median absolute gap between the pool-side proxy and observed paid rewards is **{median_gap:,.2f} ADA**.",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(
        f"Current epoch {current_epoch}: gross={gross_proxy[current_idx]:.6f} treasury={treasury_cut_proxy[current_idx]:.6f} pools={pool_pot_proxy[current_idx]:.6f}"
    )


if __name__ == "__main__":
    main()
