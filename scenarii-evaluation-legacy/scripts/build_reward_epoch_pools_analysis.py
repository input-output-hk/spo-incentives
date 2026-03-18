#!/usr/bin/env python3
"""
Build Reward^epoch_pools analysis visuals and explanatory markdown notes.

This script focuses on:
1) Theoretical epoch reward pot vs observed paid rewards
2) The seven ledger-level reasons why a gap can exist
3) The subset we can currently quantify from this dataset:
   - Reason 1 proxy: inactive / non-eligible stake
   - Reasons 2-7 residual bucket: performance, pledge misses, caps, transition, timing, missing deposit flow
4) Reserve/Treasury mechanics time series

Assumptions:
- Deposit_nonRefundable is missing at epoch granularity in current inputs -> set to 0.
- eta uses mainnet-derived values from Koios data (`eta_mainnet_capped`).
- Byron/Shelley transition handled with a gate based on d:
  monetary term enabled only once d < 1.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class EpochRow:
    epoch_no: int
    start_time_utc: Optional[str]
    observed_paid_ada: Optional[float]
    fee_ada: Optional[float]
    reserve_ada: Optional[float]
    supply_ada: Optional[float]
    active_stake_ada: Optional[float]
    treasury_ada: Optional[float]
    rho: Optional[float]
    tau: Optional[float]
    d_decentralisation: Optional[float]
    eta_mainnet_capped: Optional[float]


def parse_float(value: str) -> Optional[float]:
    if value is None:
        return None
    v = str(value).strip()
    if v == "":
        return None
    return float(v)


def load_rows(path: Path) -> List[EpochRow]:
    rows: List[EpochRow] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                EpochRow(
                    epoch_no=int(r["epoch_no"]),
                    start_time_utc=r.get("start_time_utc"),
                    observed_paid_ada=parse_float(r["Reward_epoch_pools_ada"]),
                    fee_ada=parse_float(r["Fee_epoch_ada"]),
                    reserve_ada=parse_float(r["Reserve_ada"]),
                    supply_ada=parse_float(r["Supply_ada"]),
                    active_stake_ada=parse_float(r["active_stake_ada"]),
                    treasury_ada=parse_float(r["Treasury_ada"]),
                    rho=parse_float(r["rho_monetary_expand_rate"]),
                    tau=parse_float(r["tau_treasury_growth_rate"]),
                    d_decentralisation=parse_float(r["d_decentralisation"]),
                    eta_mainnet_capped=parse_float(r["eta_mainnet_capped"]),
                )
            )
    rows.sort(key=lambda x: x.epoch_no)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_gap_path = root / "scenarii-evaluation" / "figures" / "reward_epoch_pools_gap_decomposition_mainnet.png"
    fig_reserve_path = root / "scenarii-evaluation" / "figures" / "reward_epoch_pools_reserve_mechanics_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "reward_epoch_pools_gap_decomposition_notes.md"
    doc_path = root / "scenarii-evaluation" / "docs" / "reward-epoch-pools-analysis.md"

    fig_gap_path.parent.mkdir(parents=True, exist_ok=True)
    fig_reserve_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([r.epoch_no for r in rows], dtype=int)
    dates = [r.start_time_utc[:10] if r.start_time_utc else "n/a" for r in rows]

    observed = np.array([np.nan if r.observed_paid_ada is None else r.observed_paid_ada for r in rows], dtype=float)
    fee = np.array([np.nan if r.fee_ada is None else r.fee_ada for r in rows], dtype=float)
    reserve = np.array([np.nan if r.reserve_ada is None else r.reserve_ada for r in rows], dtype=float)
    supply = np.array([np.nan if r.supply_ada is None else r.supply_ada for r in rows], dtype=float)
    active = np.array([np.nan if r.active_stake_ada is None else r.active_stake_ada for r in rows], dtype=float)
    treasury = np.array([np.nan if r.treasury_ada is None else r.treasury_ada for r in rows], dtype=float)
    rho = np.array([np.nan if r.rho is None else r.rho for r in rows], dtype=float)
    tau = np.array([np.nan if r.tau is None else r.tau for r in rows], dtype=float)
    d = np.array([np.nan if r.d_decentralisation is None else r.d_decentralisation for r in rows], dtype=float)
    eta = np.array([np.nan if r.eta_mainnet_capped is None else r.eta_mainnet_capped for r in rows], dtype=float)

    # Transition gate: when d == 1 (bootstrap), disable monetary expansion in this approximation.
    gate = np.where(np.isnan(d), np.nan, np.where(d >= 1.0, 0.0, 1.0))

    # Gross pot before treasury and theoretical pool pot after treasury.
    eta_eff = np.where(np.isnan(eta), 1.0, eta)
    gross_before_treasury = fee + gate * eta_eff * rho * reserve  # Deposit term omitted (unknown in current dataset)
    theoretical_pot = (1.0 - tau) * gross_before_treasury
    treasury_cut = tau * gross_before_treasury

    active_share_transition = np.where(d >= 1.0, 1.0, active / np.clip(supply, 1e-9, None))

    gap = theoretical_pot - observed
    gap = np.where(np.isnan(gap), np.nan, np.maximum(gap, 0.0))

    # Reason 1: inactive / reward-ineligible stake proxy.
    loss_unstaked_proxy = theoretical_pot * (1.0 - active_share_transition)
    loss_unstaked_proxy = np.where(np.isnan(loss_unstaked_proxy), np.nan, np.maximum(loss_unstaked_proxy, 0.0))

    # Reasons 2-7: residual bucket for all remaining effects.
    loss_other = gap - loss_unstaked_proxy
    loss_other = np.where(np.isnan(loss_other), np.nan, np.maximum(loss_other, 0.0))

    analysis_mask = (~np.isnan(gap)) & (~np.isnan(loss_unstaked_proxy)) & (~np.isnan(loss_other)) & (epochs >= 211)
    if not np.any(analysis_mask):
        raise RuntimeError("No analysis window available.")

    total_gap = float(np.nansum(gap[analysis_mask]))
    total_unstaked = float(np.nansum(loss_unstaked_proxy[analysis_mask]))
    total_other = float(np.nansum(loss_other[analysis_mask]))
    share_unstaked = (total_unstaked / total_gap) * 100.0 if total_gap > 0 else np.nan
    share_other = (total_other / total_gap) * 100.0 if total_gap > 0 else np.nan

    paid_share_pct = 100.0 * observed / np.clip(theoretical_pot, 1e-9, None)
    gap_median_m = float(np.nanmedian(gap[analysis_mask] / 1_000_000.0))

    d0_idx = np.where(d == 0.0)[0]
    d0_epoch = int(epochs[d0_idx[0]]) if d0_idx.size else None
    d0_date = dates[d0_idx[0]] if d0_idx.size else None

    observed_m = observed / 1_000_000.0
    theoretical_m = theoretical_pot / 1_000_000.0
    fee_m = fee / 1_000_000.0
    gap_m = gap / 1_000_000.0
    unstaked_m = loss_unstaked_proxy / 1_000_000.0
    other_m = loss_other / 1_000_000.0
    treasury_cut_m = treasury_cut / 1_000_000.0
    reserve_b = reserve / 1_000_000_000.0
    treasury_b = treasury / 1_000_000_000.0

    plt.style.use("seaborn-v0_8-whitegrid")

    # Figure 1: overview + gap decomposition
    fig1, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(15, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.2]},
    )

    ax1.plot(epochs, theoretical_m, color="#d62728", linestyle="--", linewidth=1.6, label="Theoretical pot (SL-D1)")
    ax1.plot(epochs, observed_m, color="#111111", linewidth=1.9, label="Observed paid rewards")
    ax1.plot(epochs, fee_m, color="#ff7f0e", linewidth=1.2, alpha=0.9, label="Fees")

    mark_epochs = [211, 260, 400, 500, 614]
    for e_mark in mark_epochs:
        idx = np.where(epochs == e_mark)[0]
        if idx.size == 0:
            continue
        i = int(idx[0])
        if np.isnan(theoretical_m[i]) or np.isnan(observed_m[i]):
            continue
        y_low = min(theoretical_m[i], observed_m[i])
        y_high = max(theoretical_m[i], observed_m[i])
        ax1.vlines(e_mark, y_low, y_high, color="#9467bd", linewidth=1.2, linestyles=":")
        ax1.text(
            e_mark + 1.5,
            y_low + 0.5 * (y_high - y_low),
            f"Δ {abs(theoretical_m[i]-observed_m[i]):.1f}M",
            color="#9467bd",
            fontsize=8,
            va="center",
        )

    if d0_epoch is not None:
        ax1.axvline(d0_epoch, color="#2ca02c", linestyle="--", linewidth=1.1, alpha=0.8)
        ax1.text(d0_epoch + 2, np.nanmax(theoretical_m) * 0.92, f"d=0 ({d0_date})", color="#2ca02c", fontsize=8)

    ax1.set_ylabel("Million ADA per epoch")
    ax1.set_title(r"$Reward^{epoch}_{pools}$: Theoretical Pot vs Observed Paid Rewards")
    ax1.legend(loc="upper right")
    ax1.text(
        0.01,
        0.02,
        f"Assumptions: $\\eta$=mainnet derived, $Deposit_{{nonRefund}}=0.0$ (unknown), transition gate by $d$\n"
        f"Analysis window 211+: median gap={gap_median_m:.2f}M ADA | "
        f"Current split: reason 1 proxy={share_unstaked:.1f}% / reasons 2-7 residual={share_other:.1f}%",
        transform=ax1.transAxes,
        fontsize=9,
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    ax2.fill_between(
        epochs,
        0,
        unstaked_m,
        color="#4c78a8",
        alpha=0.75,
        label="Reason 1 proxy: inactive / non-eligible stake",
    )
    ax2.fill_between(
        epochs,
        unstaked_m,
        unstaked_m + other_m,
        color="#f58518",
        alpha=0.75,
        label="Reasons 2-7 residual bucket",
    )
    ax2.plot(epochs, gap_m, color="#9467bd", linewidth=1.6, label="Total gap (theoretical - observed)")
    ax2.set_ylabel("Gap (Million ADA)")
    ax2.set_title("Gap Decomposition: Reason 1 vs Reasons 2-7")
    ax2.legend(loc="upper right")
    ax2.text(
        0.01,
        0.98,
        "Reasons 2-7: performance | pledge miss | saturation/caps\n"
        "Byron->Shelley d | timing/rounding | missing Deposit_nonRefund flow",
        transform=ax2.transAxes,
        fontsize=8.5,
        va="top",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    tick_count = 14
    tick_idx = np.unique(np.linspace(0, len(rows) - 1, num=min(tick_count, len(rows)), dtype=int))
    tick_epochs = epochs[tick_idx]
    tick_labels = [f"{epochs[i]}\n{dates[i]}" for i in tick_idx]
    ax2.set_xticks(tick_epochs)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Epoch\nStart date (UTC)")

    fig1.tight_layout()
    fig1.savefig(fig_gap_path, dpi=220)
    plt.close(fig1)

    # Figure 2: reserve/treasury mechanics
    fig2, (bx1, bx2) = plt.subplots(
        2,
        1,
        figsize=(15, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [1.2, 1.3]},
    )

    bx1.plot(epochs, reserve_b, color="#1f77b4", linewidth=1.9, label="Reserve (B ADA)")
    bx1.plot(epochs, treasury_b, color="#2ca02c", linewidth=1.9, label="Treasury (B ADA)")
    bx1.set_ylabel("Billion ADA")
    bx1.set_title("System Stocks: Reserve and Treasury")
    bx1.legend(loc="upper right")

    bx2.plot(epochs, theoretical_m, color="#d62728", linestyle="--", linewidth=1.6, label="Theoretical pool pot")
    bx2.plot(epochs, observed_m, color="#111111", linewidth=1.8, label="Observed paid rewards")
    bx2.plot(epochs, gap_m, color="#9467bd", linewidth=1.5, label="Returned-to-reserve proxy (gap)")
    bx2.plot(epochs, treasury_cut_m, color="#17becf", linewidth=1.3, label="Treasury cut proxy")
    bx2.set_ylabel("Million ADA per epoch")
    bx2.set_title("Per-Epoch Flows (How Reserve/Treasury Interact with Rewards)")
    bx2.legend(loc="upper right")
    bx2.set_xticks(tick_epochs)
    bx2.set_xticklabels(tick_labels)
    bx2.set_xlabel("Epoch\nStart date (UTC)")

    fig2.tight_layout()
    fig2.savefig(fig_reserve_path, dpi=220)
    plt.close(fig2)

    first_epoch = int(np.nanmin(epochs))
    last_epoch = int(np.nanmax(epochs))
    seven_reason_lines = [
        "## Seven reasons why a gap exists",
        "- Reason 1. Inactive / reward-ineligible stake: Byron-era funds, undelegated stake, retired pools, and other stake not participating in the reward mechanism.",
        r"- Reason 2. Pool performance losses: $\bar{p}<1$ due to missed blocks, forks, or underperformance, so actual paid rewards are below optimal rewards.",
        r"- Reason 3. Unmet pledge: if pledge is not respected, the pool reward collapses to zero for that epoch.",
        r"- Reason 4. Saturation / cap effects: $\sigma'=\min(\sigma,z_0)$ and $s'=\min(s,z_0)$ cap the reward-relevant stake and pledge terms.",
        r"- Reason 5. Byron -> Shelley transition: early epochs are affected by the decentralisation parameter $d$ and the OBFT/Praos transition.",
        "- Reason 6. Ledger timing and rounding: reward accounting is epoch-shifted and uses integer lovelace arithmetic.",
        r"- Reason 7. Incomplete $Deposit_{nonRefund}$ measurement: if the true per-epoch non-refundable deposit flow is unavailable, the theoretical pot is only approximate.",
        "",
        "## What is quantified here",
        "- The current dataset supports a direct proxy only for reason 1.",
        "- Reasons 2-7 remain grouped in one residual bucket in the graph.",
        r"- Reason 5 is partially reflected through the transition gate based on $d$.",
        r"- Reason 7 is explicitly present as a limitation because the analysis sets $Deposit_{nonRefund}=0$.",
    ]
    notes_lines = [
        "# Epoch Pool Reward Gap Decomposition Notes",
        "",
        r"Target quantity: $Reward^{epoch}_{pools}$",
        "",
        f"- Dataset window: **{first_epoch}..{last_epoch}**",
        "- Analysis window for quantification: **epoch >= 211**",
        "",
        "## Core formulas",
        r"- Theoretical pool pot: $R^{epoch}_{pot}=(1-\tau)\cdot(Fee+\eta\cdot\rho\cdot Reserve\cdot g^{transition})$",
        r"- Transition gate: $g^{transition}=0$ if $d\ge 1$, else $1$",
        r"- Total gap: $Gap=R^{epoch}_{pot}-R^{epoch}_{paid}$",
        r"- Reason 1 proxy: $Gap_{unstaked}=R^{epoch}_{pot}\cdot(1-\phi^{active}_{transition})$",
        r"- with $\phi^{active}_{transition}=1$ if $d\ge 1$, else $\frac{activeStake}{supply}$",
        r"- Reasons 2-7 residual bucket: $Gap_{residual}=Gap-Gap_{unstaked}$",
        "",
    ]
    notes_lines.extend(seven_reason_lines)
    notes_lines.extend(
        [
        "",
        "## Quantification (epoch >= 211)",
        f"- Total gap: **{total_gap/1_000_000:.2f}M ADA**",
        f"- Reason 1 proxy (inactive / non-eligible stake): **{total_unstaked/1_000_000:.2f}M ADA** (**{share_unstaked:.1f}%** of gap)",
        f"- Reasons 2-7 residual bucket: **{total_other/1_000_000:.2f}M ADA** (**{share_other:.1f}%** of gap)",
        f"- Median per-epoch gap: **{gap_median_m:.2f}M ADA**",
        "",
        "## Caveats",
        r"- $Deposit_{nonRefund}$ is set to 0 in this approximation (epoch-level direct flow unavailable here).",
        r"- If $\eta_{mainnet,capped}$ is missing in any epoch row, the script falls back to 1.0 for that row.",
        "- Reason 1 remains a proxy, not a direct ledger-identity attribution.",
        "- The residual bucket groups reasons 2-7 and therefore is not a full causal attribution.",
        ]
    )
    notes_path.write_text("\n".join(notes_lines) + "\n")

    # Analysis document with embedded graphs
    doc_lines = [
        "# Epoch Pool Reward Analysis (Mainnet)",
        "",
        r"Target quantity: $Reward^{epoch}_{pools}$",
        "",
        "## Objective",
        "Understand why observed paid rewards are below the theoretical epoch reward pot, identify the seven ledger-level causes of the gap, and separate them from the subset that can currently be quantified from the available mainnet dataset.",
        "",
        "## What the reserve does",
        "In SL-D1, the reserve is the long-term monetary source used by monetary expansion.",
        r"Each epoch, a part of rewards comes from fees and a part from reserve via $\eta\cdot\rho$.",
        r"Then treasury takes $\tau$ from the gross reward sources, and pool rewards are paid from the remaining pot.",
        "If actual paid rewards are below this pot, the remainder is returned to reserve (not to treasury).",
        "",
        "## Formula Layer",
        r"1. Gross sources (approximation here): $Gross = Fee + \eta\cdot\rho\cdot Reserve\cdot g^{transition}$",
        r"2. Theoretical pool pot: $R^{epoch}_{pot}=(1-\tau)\cdot Gross$",
        r"3. Observed paid rewards: $R^{epoch}_{paid}$",
        r"4. Gap: $Gap=R^{epoch}_{pot}-R^{epoch}_{paid}$",
        "",
        "Transition gate used in this report:",
        r"$g^{transition}=0$ when $d\ge1$ (bootstrap), otherwise $g^{transition}=1$.",
        "",
        "## Seven reasons why a gap exists",
        "| Reason | Mechanism | Status in this report |",
        "| --- | --- | --- |",
        "| 1 | Inactive / reward-ineligible stake: Byron funds, undelegated stake, retired pools, and similar non-participating stake. | Approximated directly with an active-stake proxy. |",
        r"| 2 | Pool performance losses: $\bar{p}<1$ because of missed blocks, forks, or underperformance. | Residual bucket only. |",
        "| 3 | Unmet pledge: if pledge is not respected, pool reward can collapse to zero for the epoch. | Residual bucket only. |",
        r"| 4 | Saturation / cap effects: $\sigma'=\min(\sigma,z_0)$ and $s'=\min(s,z_0)$. | Residual bucket only. |",
        r"| 5 | Byron -> Shelley transition: early epochs depend on $d$ and the OBFT/Praos transition. | Partially modeled via the transition gate. |",
        "| 6 | Ledger timing and rounding: epoch offsets and integer lovelace arithmetic. | Residual bucket only. |",
        r"| 7 | Incomplete $Deposit_{nonRefund}$ measurement when the true epoch flow is unavailable. | Explicit limitation; currently set to 0. |",
        "",
        "This means the current graph is not a seven-way attribution. It is a one-way measured proxy plus a residual block that still contains reasons 2-7.",
        "",
        "## Graph 1: Pot vs Paid + Gap Decomposition",
        "The top panel shows theoretical pot and observed paid rewards.",
        "Purple markers annotate the absolute gap at selected epochs.",
        "The bottom panel quantifies the gap into two measurable buckets:",
        "- Bucket A: reason 1 proxy, inactive / non-eligible stake.",
        "- Bucket B: residual bucket containing reasons 2-7.",
        "",
        f"![Gap decomposition](../figures/{fig_gap_path.name})",
        "",
        "## Current quantification (epoch >= 211)",
        f"- Total gap: **{total_gap/1_000_000:.2f}M ADA**",
        f"- Reason 1 proxy: **{total_unstaked/1_000_000:.2f}M ADA** (**{share_unstaked:.1f}%**) ",
        f"- Reasons 2-7 residual bucket: **{total_other/1_000_000:.2f}M ADA** (**{share_other:.1f}%**) ",
        "",
        "## Graph 2: Reserve/Treasury Mechanics",
        "Top panel: stock variables (reserve and treasury) through time.",
        "Bottom panel: per-epoch flow view to read how the reward pot, treasury cut, paid rewards, and return-to-reserve proxy interact.",
        "",
        f"![Reserve mechanics](../figures/{fig_reserve_path.name})",
        "",
        "## Interpretation",
        "- A near-parallel shape between theoretical and observed curves means the model captures dynamics, but there is a structural offset.",
        "- In this window, most of the offset is consistent with the inactive / non-eligible stake proxy, and the rest is a stable residual block containing reasons 2-7.",
        "- To break the residual further, the next step is pool-level data: performance, pledge compliance, saturation state, and exact non-refundable deposit flow.",
        "",
        "## Assumptions and limitations",
        r"- $Deposit_{nonRefund}$ is not directly available at epoch-level in this dataset and is set to 0.",
        r"- $\eta$ uses mainnet-derived values from epoch block counts ($\eta_{mainnet,capped}$).",
        "- Gap decomposition is an analytical proxy, not a full ledger-state replay or full seven-way attribution.",
    ]
    doc_path.write_text("\n".join(doc_lines) + "\n")

    print(f"Wrote: {fig_gap_path}")
    print(f"Wrote: {fig_reserve_path}")
    print(f"Wrote: {notes_path}")
    print(f"Wrote: {doc_path}")
    print(f"Gap split (epoch>=211): unstaked={share_unstaked:.2f}% other={share_other:.2f}%")


if __name__ == "__main__":
    main()
