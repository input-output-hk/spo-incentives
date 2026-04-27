#!/usr/bin/env python3
"""
Build a focused history for the reserve stock and reserve-sourced monetary expansion.

Definitions used:
  Reserve_epoch = T_max - T
  MonetaryExpansionNominal_epoch = rho * Reserve_epoch
  MonetaryExpansionEtaAdjusted_epoch = min(eta, 1) * rho * Reserve_epoch
  MonetaryExpansionPoolSide_epoch = (1 - tau) * gate(d) * min(eta, 1) * rho * Reserve_epoch

Outputs:
  - scenarii-evaluation/figures/monetary_expansion_reserve_history_mainnet.png
  - scenarii-evaluation/outputs/monetary_expansion_reserve_history_mainnet.md
  - scenarii-evaluation/outputs/monetary_expansion_reserve_history_mainnet.csv
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
    reserve_ada: Optional[float]
    rho: Optional[float]
    tau: Optional[float]
    d: Optional[float]
    eta_capped: Optional[float]


def parse_float(value: str | None) -> Optional[float]:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    return float(stripped)


def load_rows(path: Path) -> List[EpochRow]:
    rows: List[EpochRow] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for record in reader:
            rows.append(
                EpochRow(
                    epoch_no=int(record["epoch_no"]),
                    start_time_utc=record.get("start_time_utc"),
                    reserve_ada=parse_float(record.get("Reserve_ada")),
                    rho=parse_float(record.get("rho_monetary_expand_rate")),
                    tau=parse_float(record.get("tau_treasury_growth_rate")),
                    d=parse_float(record.get("d_decentralisation")),
                    eta_capped=parse_float(record.get("eta_mainnet_capped")),
                )
            )
    rows.sort(key=lambda row: row.epoch_no)
    return rows


def format_date(iso: Optional[str]) -> str:
    if not iso:
        return "n/a"
    return iso[:10]


def to_billion(values: np.ndarray) -> np.ndarray:
    return values / 1_000_000_000.0


def to_million(values: np.ndarray) -> np.ndarray:
    return values / 1_000_000.0


def main() -> None:
    REPORT_DIR = Path(__file__).resolve().parent.parent
    data_path = REPORT_DIR / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = REPORT_DIR / "figures" / "monetary_expansion_reserve_history_mainnet.png"
    notes_path = REPORT_DIR / "data" / "monetary_expansion_reserve_history_mainnet.md"
    csv_path = REPORT_DIR / "data" / "monetary_expansion_reserve_history_mainnet.csv"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([row.epoch_no for row in rows], dtype=int)
    reserve = np.array([np.nan if row.reserve_ada is None else row.reserve_ada for row in rows], dtype=float)
    rho = np.array([np.nan if row.rho is None else row.rho for row in rows], dtype=float)
    tau = np.array([np.nan if row.tau is None else row.tau for row in rows], dtype=float)
    eta = np.array([np.nan if row.eta_capped is None else row.eta_capped for row in rows], dtype=float)
    d = np.array([np.nan if row.d is None else row.d for row in rows], dtype=float)

    # Filter out incomplete/current epoch (last epoch may have partial data)
    if len(epochs) > 0 and epochs[-1] > 623:
        # Only keep up to the last complete epoch with reward data
        mask_complete = epochs <= 623
        epochs = epochs[mask_complete]
        reserve = reserve[mask_complete]
        rho = rho[mask_complete]
        tau = tau[mask_complete]
        eta = eta[mask_complete]
        d = d[mask_complete]
        rows = [row for i, row in enumerate(rows) if i < len(rows) and rows[i].epoch_no <= 623]

    gate = np.where(np.isnan(d), np.nan, np.where(d >= 1.0, 0.0, 1.0))
    nominal = rho * reserve
    eta_adjusted = eta * nominal
    pool_side = (1.0 - tau) * gate * eta_adjusted

    current_epoch = int(epochs[-1])
    complete_mask = epochs < current_epoch
    valid_reserve_mask = complete_mask & ~np.isnan(reserve)
    valid_nominal_mask = complete_mask & ~np.isnan(nominal)
    valid_pool_mask = complete_mask & ~np.isnan(pool_side)

    if not np.any(valid_reserve_mask):
        raise RuntimeError("No complete reserve history available.")

    first_complete_idx = int(np.where(valid_reserve_mask)[0][0])
    last_complete_idx = int(np.where(valid_reserve_mask)[0][-1])

    reserve_complete = reserve[valid_reserve_mask]
    nominal_complete = nominal[valid_nominal_mask]
    pool_complete = pool_side[valid_pool_mask]

    reserve_start = float(reserve[first_complete_idx])
    reserve_end = float(reserve[last_complete_idx])
    reserve_change = reserve_end - reserve_start
    reserve_pct_change = (reserve_change / reserve_start) * 100.0

    nominal_start = float(nominal[np.where(valid_nominal_mask)[0][0]])
    nominal_end = float(nominal[np.where(valid_nominal_mask)[0][-1]])
    pool_start_idx = int(np.where(valid_pool_mask)[0][0])
    pool_end_idx = int(np.where(valid_pool_mask)[0][-1])
    pool_start = float(pool_side[pool_start_idx])
    pool_end = float(pool_side[pool_end_idx])

    low_pool_idx = int(np.where(valid_pool_mask)[0][np.nanargmin(pool_complete)])
    high_pool_idx = int(np.where(valid_pool_mask)[0][np.nanargmax(pool_complete)])

    out_rows = []
    for i, row in enumerate(rows):
        out_rows.append(
            {
                "epoch_no": row.epoch_no,
                "start_date_utc": format_date(row.start_time_utc),
                "reserve_ada": None if np.isnan(reserve[i]) else f"{reserve[i]:.6f}",
                "rho_rate": None if np.isnan(rho[i]) else f"{rho[i]:.6f}",
                "eta_capped": None if np.isnan(eta[i]) else f"{eta[i]:.6f}",
                "tau_rate": None if np.isnan(tau[i]) else f"{tau[i]:.6f}",
                "d_decentralisation": None if np.isnan(d[i]) else f"{d[i]:.6f}",
                "transition_gate": None if np.isnan(gate[i]) else f"{gate[i]:.0f}",
                "monetary_expansion_nominal_ada": None if np.isnan(nominal[i]) else f"{nominal[i]:.6f}",
                "monetary_expansion_eta_adjusted_ada": None if np.isnan(eta_adjusted[i]) else f"{eta_adjusted[i]:.6f}",
                "monetary_expansion_pool_side_ada": None if np.isnan(pool_side[i]) else f"{pool_side[i]:.6f}",
                "is_current_partial_epoch": "True" if row.epoch_no == current_epoch else "False",
            }
        )

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    # IOG light brand palette
    LIGHT_BG = "#FAFAFA"
    TEXT_DARK = "#1A1A1A"
    TEXT_DIM = "#666666"
    GRID_COLOR = "#E0E0E0"
    INFARED = "#E52321"
    DAWN = "#EC641D"
    ACID_GREEN = "#06FF89"
    ELECTRIC_BLUE = "#16E9D8"
    ULTRAVIOLET = "#A700FF"
    SOLAR_AMBER = "#FFBA36"
    COBALT_PULSE = "#2C4FFA"

    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(16, 12),
        sharex=True,
        gridspec_kw={"height_ratios": [1.1, 1.0, 1.0]},
        facecolor=LIGHT_BG,
    )

    # Panel 1: Reserve stock depletion in ELECTRIC_BLUE
    ax1.set_facecolor(LIGHT_BG)
    ax1.plot(epochs, to_billion(reserve), color=ELECTRIC_BLUE, linewidth=2.2, label="Reserve stock")
    ax1.fill_between(epochs, to_billion(reserve), alpha=0.15, color=ELECTRIC_BLUE)
    ax1.set_ylabel("Billion ADA", color=TEXT_DARK, fontsize=11, fontweight="500")
    ax1.set_title(f"Reserve has halved — from {reserve_start/1e9:.1f}B to {reserve_end/1e9:.1f}B ADA since Shelley",
                  color=TEXT_DARK, fontsize=14, fontweight="600", pad=16)
    ax1.legend(loc="upper right", framealpha=0.95, facecolor=LIGHT_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_DARK, fontsize=9)
    ax1.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.6)
    ax1.tick_params(axis="y", labelcolor=TEXT_DIM, labelsize=9)
    ax1.tick_params(axis="x", labelcolor=TEXT_DIM, labelsize=9)
    for spine in ax1.spines.values():
        spine.set_edgecolor(GRID_COLOR)
        spine.set_linewidth(0.5)

    ax1.text(
        0.01,
        0.08,
        f"Complete window: epochs {rows[first_complete_idx].epoch_no}–{rows[last_complete_idx].epoch_no} | "
        f"Depletion: {reserve_pct_change:.1f}%",
        transform=ax1.transAxes,
        fontsize=8,
        va="bottom",
        ha="left",
        color=TEXT_DIM,
    )
    add_event_markers(ax1, compact=True, y_frac=0.85)

    # Panel 2: Nominal vs performance-adjusted expansion
    ax2.set_facecolor(LIGHT_BG)
    ax2.plot(epochs, to_million(nominal), color=INFARED, linewidth=1.9, label="Nominal expansion")
    ax2.plot(
        epochs,
        to_million(eta_adjusted),
        color=DAWN,
        linewidth=1.6,
        linestyle="--",
        label="Performance-adjusted expansion",
    )
    ax2.set_ylabel("Million ADA / epoch", color=TEXT_DARK, fontsize=11, fontweight="500")
    ax2.legend(loc="upper right", framealpha=0.95, facecolor=LIGHT_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_DARK, fontsize=9)
    ax2.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.6)
    ax2.tick_params(axis="y", labelcolor=TEXT_DIM, labelsize=9)
    ax2.tick_params(axis="x", labelcolor=TEXT_DIM, labelsize=9)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_COLOR)
        spine.set_linewidth(0.5)
    add_event_markers(ax2, compact=True, y_frac=0.85)

    # Panel 3: Pool-side reserve term in ACID_GREEN
    ax3.set_facecolor(LIGHT_BG)
    ax3.plot(
        epochs,
        to_million(pool_side),
        color=ACID_GREEN,
        linewidth=1.9,
        label="Pool-side expansion",
    )
    ax3.scatter(
        [rows[low_pool_idx].epoch_no, rows[high_pool_idx].epoch_no],
        [to_million(np.array([pool_side[low_pool_idx], pool_side[high_pool_idx]]))[0], to_million(np.array([pool_side[low_pool_idx], pool_side[high_pool_idx]]))[1]],
        color=[SOLAR_AMBER, COBALT_PULSE],
        s=48,
        zorder=5,
        edgecolor=TEXT_DARK,
        linewidth=1.0,
    )
    ax3.annotate(
        f"low\nepoch {rows[low_pool_idx].epoch_no}\n{pool_side[low_pool_idx]/1e6:.2f}M",
        xy=(rows[low_pool_idx].epoch_no, pool_side[low_pool_idx] / 1_000_000.0),
        xytext=(10, -14),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=8,
        color=SOLAR_AMBER,
    )
    ax3.annotate(
        f"high\nepoch {rows[high_pool_idx].epoch_no}\n{pool_side[high_pool_idx]/1e6:.2f}M",
        xy=(rows[high_pool_idx].epoch_no, pool_side[high_pool_idx] / 1_000_000.0),
        xytext=(10, 12),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=8,
        color=COBALT_PULSE,
    )
    ax3.set_ylabel("Million ADA / epoch", color=TEXT_DARK, fontsize=11, fontweight="500")
    ax3.set_xlabel("Epoch", color=TEXT_DARK, fontsize=11, fontweight="500")
    ax3.legend(loc="upper right", framealpha=0.95, facecolor=LIGHT_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_DARK, fontsize=9)
    ax3.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.6)
    ax3.tick_params(axis="y", labelcolor=TEXT_DIM, labelsize=9)
    ax3.tick_params(axis="x", labelcolor=TEXT_DIM, labelsize=9)
    for spine in ax3.spines.values():
        spine.set_edgecolor(GRID_COLOR)
        spine.set_linewidth(0.5)
    add_event_markers(ax3, compact=True, y_frac=0.95)

    tick_count = min(11, len(rows))
    tick_idx = np.unique(np.linspace(0, len(rows) - 1, num=tick_count, dtype=int))
    ax3.set_xticks(epochs[tick_idx])
    ax3.set_xticklabels([f"{epochs[i]}\n{format_date(rows[i].start_time_utc)}" for i in tick_idx], color=TEXT_DIM, fontsize=9)

    fig.tight_layout(rect=[0, 0, 1, 1])
    fig.savefig(fig_path, dpi=180, facecolor=LIGHT_BG, edgecolor="none")
    plt.close(fig)

    notes_lines = [
        "# Monetary Expansion Reserve History (Mainnet)",
        "",
        "This output separates three different quantities that are often conflated:",
        "",
        r"- Reserve stock: $Reserve = T_{\infty} - T$.",
        r"- Nominal reserve draw: $\rho \cdot Reserve$.",
        r"- Pool-side reserve contribution: $(1-\tau)\,g(d)\,\min(\eta,1)\rho \cdot Reserve$.",
        "",
        f"- Dataset coverage: epochs **{rows[0].epoch_no}..{rows[-1].epoch_no}**.",
        f"- Complete-history window used for stock comparisons: **{rows[first_complete_idx].epoch_no}..{rows[last_complete_idx].epoch_no}**.",
        f"- `rho` is constant at **{rho[valid_nominal_mask][0]:.3f}** in this dataset.",
        f"- `tau` is constant at **{tau[valid_nominal_mask][0]:.1f}** in this dataset.",
        "",
        "## Reserve stock",
        f"- First complete reserve point: epoch **{rows[first_complete_idx].epoch_no}** ({format_date(rows[first_complete_idx].start_time_utc)}) = **{reserve_start:,.0f} ADA**.",
        f"- Last complete reserve point: epoch **{rows[last_complete_idx].epoch_no}** ({format_date(rows[last_complete_idx].start_time_utc)}) = **{reserve_end:,.0f} ADA**.",
        f"- Change over the complete window: **{reserve_change:,.0f} ADA** ({reserve_pct_change:.2f}%).",
        "",
        "## Reserve-sourced monetary expansion",
        f"- Nominal `rho * reserve` fell from **{nominal_start:,.0f} ADA/epoch** to **{nominal_end:,.0f} ADA/epoch** over the complete window.",
        f"- Pool-side reserve term fell from **{pool_start:,.0f} ADA/epoch** at epoch **{rows[pool_start_idx].epoch_no}** "
        f"to **{pool_end:,.0f} ADA/epoch** at epoch **{rows[pool_end_idx].epoch_no}**.",
        "",
        "## Extremes on complete epochs for the pool-side reserve term",
        f"- Lowest complete epoch: **{rows[low_pool_idx].epoch_no}** ({format_date(rows[low_pool_idx].start_time_utc)}) = **{pool_side[low_pool_idx]:,.0f} ADA/epoch**.",
        f"- Highest complete epoch: **{rows[high_pool_idx].epoch_no}** ({format_date(rows[high_pool_idx].start_time_utc)}) = **{pool_side[high_pool_idx]:,.0f} ADA/epoch**.",
        "",
        "## Current partial epoch",
        f"- Epoch **{current_epoch}** ({format_date(rows[-1].start_time_utc)}) currently shows:",
        f"  - reserve stock = **{reserve[-1]:,.0f} ADA**",
        f"  - nominal `rho * reserve` = **{nominal[-1]:,.0f} ADA/epoch**",
        f"  - pool-side reserve term so far = **{pool_side[-1]:,.0f} ADA/epoch**",
        "",
        "The focused table is available in the CSV output next to this note.",
    ]
    notes_path.write_text("\n".join(notes_lines) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(f"Wrote: {csv_path}")
    print(f"Reserve start/end: {reserve_start:.0f} -> {reserve_end:.0f}")
    print(f"Nominal start/end: {nominal_start:.0f} -> {nominal_end:.0f}")
    print(f"Pool-side start/end: {pool_start:.0f} -> {pool_end:.0f}")


if __name__ == "__main__":
    main()
