#!/usr/bin/env python3
"""
Build a mainnet time-series visual for Reward^{epoch}_{pools} using the SL-D1 formula.

Formula used (paper-aligned compact form):
  Reward^{epoch}_{pools} = (1 - tau) * (Fee + Deposit + min(eta, 1) * rho * (T_max - T))

With currently available Koios inputs:
  - Fee: from epoch_info/totals
  - T (circulating): from totals.supply
  - rho: from epoch_params.monetary_expand_rate
  - tau: from epoch_params.treasury_growth_rate
  - eta: set to 1.0
  - Deposit: not directly available as epoch-level non-refundable flow -> assumed 0.0

Outputs:
  - scenarii-evaluation/figures/reward_epoch_pools_formula_mainnet.png
  - scenarii-evaluation/outputs/reward_epoch_pools_formula_notes.md
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

MAX_SUPPLY_ADA = 45_000_000_000.0


@dataclass
class EpochRow:
    epoch_no: int
    start_time_utc: Optional[str]
    reward_observed_ada: Optional[float]
    fee_ada: Optional[float]
    supply_ada: Optional[float]
    reserve_ada: Optional[float]  # fallback only
    rho: Optional[float]
    tau: Optional[float]


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
                    reward_observed_ada=parse_float(r["Reward_epoch_pools_ada"]),
                    fee_ada=parse_float(r["Fee_epoch_ada"]),
                    supply_ada=parse_float(r["Supply_ada"]),
                    reserve_ada=parse_float(r["Reserve_ada"]),
                    rho=parse_float(r["rho_monetary_expand_rate"]),
                    tau=parse_float(r["tau_treasury_growth_rate"]),
                )
            )
    rows.sort(key=lambda x: x.epoch_no)
    return rows


def compute_formula_reward_ada(
    fee_ada: float,
    monetary_base_ada: float,
    rho: float,
    tau: float,
    eta: float = 1.0,
    deposit_ada: float = 0.0,
) -> float:
    # Reward^{epoch}_{pools} = (1 - tau) * (Fee + Deposit + min(eta,1) * rho * (T_max - T))
    return (1.0 - tau) * (fee_ada + deposit_ada + min(eta, 1.0) * rho * monetary_base_ada)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "reward_epoch_pools_formula_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "reward_epoch_pools_formula_notes.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([r.epoch_no for r in rows], dtype=int)

    observed = np.array(
        [np.nan if r.reward_observed_ada is None else r.reward_observed_ada for r in rows],
        dtype=float,
    )

    formula_gross = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    comp_fee = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    comp_monetary = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    payout_ratio = np.full(shape=len(rows), fill_value=np.nan, dtype=float)

    for i, r in enumerate(rows):
        if None in (r.fee_ada, r.rho, r.tau):
            continue
        if r.supply_ada is not None:
            monetary_base_ada = max(MAX_SUPPLY_ADA - r.supply_ada, 0.0)
        elif r.reserve_ada is not None:
            # Fallback for robustness if supply is missing in an epoch row.
            monetary_base_ada = r.reserve_ada
        else:
            continue

        fee_term = (1.0 - r.tau) * r.fee_ada
        monetary_term = (1.0 - r.tau) * min(1.0, 1.0) * r.rho * monetary_base_ada
        formula_gross[i] = fee_term + monetary_term  # Deposit term assumed 0.0
        comp_fee[i] = fee_term
        comp_monetary[i] = monetary_term

    overlap_mask = ~np.isnan(observed) & ~np.isnan(formula_gross)
    missing_observed_mask = np.isnan(observed) & ~np.isnan(formula_gross)

    if np.any(overlap_mask):
        payout_ratio[overlap_mask] = observed[overlap_mask] / np.clip(formula_gross[overlap_mask], 1e-9, None)

    mae = float(np.nan)
    mape = float(np.nan)
    if np.any(overlap_mask):
        diff = np.abs(observed[overlap_mask] - formula_gross[overlap_mask])
        mae = float(np.mean(diff))
        den = np.clip(np.abs(observed[overlap_mask]), 1e-9, None)
        mape = float(np.mean(diff / den) * 100.0)

    stable_mask = overlap_mask & (epochs >= 211)
    stable_mae = float(np.nan)
    stable_mape = float(np.nan)
    if np.any(stable_mask):
        stable_diff = np.abs(observed[stable_mask] - formula_gross[stable_mask])
        stable_mae = float(np.mean(stable_diff))
        stable_den = np.clip(np.abs(observed[stable_mask]), 1e-9, None)
        stable_mape = float(np.mean(stable_diff / stable_den) * 100.0)

    ratio_median = float(np.nan)
    ratio_p5 = float(np.nan)
    ratio_p95 = float(np.nan)
    ratio_vals = payout_ratio[overlap_mask]
    if ratio_vals.size > 0:
        ratio_median = float(np.nanmedian(ratio_vals))
        ratio_p5 = float(np.nanpercentile(ratio_vals, 5))
        ratio_p95 = float(np.nanpercentile(ratio_vals, 95))

    # Plot in million ADA for readability (avoid scientific notation ambiguity).
    observed_m = observed / 1_000_000.0
    formula_gross_m = formula_gross / 1_000_000.0
    comp_fee_m = comp_fee / 1_000_000.0
    comp_monetary_m = comp_monetary / 1_000_000.0

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.2]},
    )

    # Top panel: observed vs formula
    ax1.plot(
        epochs,
        formula_gross_m,
        color="#1f77b4",
        linewidth=2.2,
        label=r"Gross pot formula: $(1-\tau)\cdot(\mathrm{Fee}+\rho\cdot(T_{\infty}-T))$",
    )
    ax1.plot(
        epochs,
        observed_m,
        color="#111111",
        linewidth=1.8,
        alpha=0.9,
        label=r"Observed on-chain paid rewards: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{pools}}$",
    )

    if np.any(missing_observed_mask):
        ax1.scatter(
            epochs[missing_observed_mask],
            formula_gross_m[missing_observed_mask],
            color="#d62728",
            s=50,
            zorder=5,
            label="Observed reward missing for these epochs",
        )

    ax1.set_ylabel("Million ADA per epoch")
    ax1.set_title("Mainnet Reward$^{epoch}_{pools}$: SL-D1 Gross Pot vs Observed Paid Rewards")
    ax1.legend(loc="upper right")
    ax1.text(
        0.01,
        0.02,
        f"Assumptions: eta=1.0, Deposit=0.0; T∞=45B ADA; values shown in MILLION ADA\n"
        f"Observed/Gross ratio on overlap: median={ratio_median:.3f}, p5={ratio_p5:.3f}, p95={ratio_p95:.3f}\n"
        f"Gross-vs-observed gap (expected): MAE={mae:,.0f} ADA, MAPE={mape:.2f}% (stable window 211+: {stable_mape:.2f}%)",
        transform=ax1.transAxes,
        fontsize=9,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    # Bottom panel: decomposition of formula terms
    ax2.fill_between(
        epochs,
        0,
        comp_monetary_m,
        color="#ffbb78",
        alpha=0.65,
        label=r"Monetary expansion: $(1-\tau)\rho\cdot(T_{\infty}-T)$",
    )
    ax2.fill_between(
        epochs,
        comp_monetary_m,
        comp_monetary_m + comp_fee_m,
        color="#98df8a",
        alpha=0.65,
        label=r"Fee contribution: $(1-\tau)\cdot\mathrm{Fee}$",
    )

    # Show epoch number and date together for readability.
    tick_count = 14
    tick_idx = np.unique(np.linspace(0, len(rows) - 1, num=min(tick_count, len(rows)), dtype=int))
    tick_epochs = epochs[tick_idx]
    tick_labels = []
    for i in tick_idx:
        iso = rows[int(i)].start_time_utc or ""
        date_label = iso[:10] if len(iso) >= 10 else "n/a"
        tick_labels.append(f"{epochs[int(i)]}\n{date_label}")

    ax2.set_xticks(tick_epochs)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Epoch\nStart date (UTC)")
    ax2.set_ylabel("Million ADA per epoch")
    ax2.set_title("Formula Decomposition (Deposit term omitted due to missing epoch-level input)")
    ax2.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)

    # Write notes summary
    first_epoch = int(epochs.min())
    last_epoch = int(epochs.max())
    overlap_epochs = epochs[overlap_mask]
    overlap_min = int(overlap_epochs.min()) if overlap_epochs.size else None
    overlap_max = int(overlap_epochs.max()) if overlap_epochs.size else None
    missing_epochs = epochs[missing_observed_mask].tolist()

    notes = [
        "# Reward^epoch_pools Formula Reconstruction Notes",
        "",
        f"- Input data: `reward_epoch_pools_mainnet.csv`",
        f"- Epoch span in dataset: **{first_epoch}..{last_epoch}**",
        f"- Overlap (observed + formula): **{overlap_min}..{overlap_max}**",
        f"- Epochs with formula value but missing observed reward: **{missing_epochs}**",
        "",
        "## Formula used",
        r"- $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{pools}} = (1-\tau)\cdot(\mathrm{Fee} + \mathrm{Deposit} + \min(\eta,1)\rho\cdot(T_{\infty}-T))$",
        "",
        "## Assumptions",
        "- `eta = 1.0`",
        "- `Deposit = 0.0` because an epoch-level non-refundable deposit flow is not present in current inputs",
        "- `T∞ = 45,000,000,000 ADA` and `T` is taken from `totals.supply`",
        "",
        "## Fit quality on overlap window",
        f"- MAE: **{mae:,.0f} ADA/epoch**",
        f"- MAPE: **{mape:.2f}%**",
        f"- Stable window (epoch >= 211): MAE **{stable_mae:,.0f} ADA/epoch**, MAPE **{stable_mape:.2f}%**",
        f"- Observed/Gross ratio median: **{ratio_median:.3f}** (p5={ratio_p5:.3f}, p95={ratio_p95:.3f})",
        "",
        "## Interpretation",
        "- The formula line is the **gross reward pot** from SL-D1 (pre pool-level performance and pre return-to-reserves).",
        "- The observed line is on-chain **paid rewards** (`epoch_info.total_rewards`).",
        "- These are not strictly the same quantity, so a persistent gap is expected.",
        "",
        "## Output figure",
        "- `reward_epoch_pools_formula_mainnet.png`",
    ]
    notes_path.write_text("\n".join(notes) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")


if __name__ == "__main__":
    main()
