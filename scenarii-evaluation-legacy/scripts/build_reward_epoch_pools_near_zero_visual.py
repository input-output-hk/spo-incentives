#!/usr/bin/env python3
"""
Build a near-zero-divergence reconstruction for epoch paid rewards.

Base SL-D1 gross pot:
  RewardGross^epoch = (1 - tau) * (Fee + Deposit + min(eta,1) * rho * (T_max - T))

With epoch-level inputs only, we cannot exactly reproduce paid rewards because pool-level
terms are missing (distribution across pools, pledge enforcement, saturation and performance).

This script adds two aggregate terms:
  - activeStakeFraction = activeStake / supply
  - payoutEfficiency (kappa), calibrated on historical data

Reconstruction:
  RewardPaidRecon^epoch = RewardGross^epoch * activeStakeFraction * kappa

Outputs:
  - scenarii-evaluation/figures/reward_epoch_pools_near_zero_mainnet.png
  - scenarii-evaluation/outputs/reward_epoch_pools_near_zero_notes.md
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
    active_stake_ada: Optional[float]
    supply_ada: Optional[float]
    rho: Optional[float]
    tau: Optional[float]
    d_decentralisation: Optional[float]


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
                    active_stake_ada=parse_float(r["active_stake_ada"]),
                    supply_ada=parse_float(r["Supply_ada"]),
                    rho=parse_float(r["rho_monetary_expand_rate"]),
                    tau=parse_float(r["tau_treasury_growth_rate"]),
                    d_decentralisation=parse_float(r["d_decentralisation"]),
                )
            )
    rows.sort(key=lambda x: x.epoch_no)
    return rows


def mean_abs_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))


def mean_abs_percentage_error(a: np.ndarray, b: np.ndarray) -> float:
    den = np.clip(np.abs(a), 1e-9, None)
    return float(np.mean(np.abs(a - b) / den) * 100.0)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "scenarii-evaluation" / "data" / "reward_epoch_pools_mainnet.csv"
    fig_path = root / "scenarii-evaluation" / "figures" / "reward_epoch_pools_near_zero_mainnet.png"
    notes_path = root / "scenarii-evaluation" / "outputs" / "reward_epoch_pools_near_zero_notes.md"

    fig_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No rows found in {data_path}")

    epochs = np.array([r.epoch_no for r in rows], dtype=int)
    observed = np.array(
        [np.nan if r.observed_paid_ada is None else r.observed_paid_ada for r in rows],
        dtype=float,
    )
    fees_ada = np.array([np.nan if r.fee_ada is None else r.fee_ada for r in rows], dtype=float)

    gross_transition = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    active_fraction = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    model_base = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    transition_gate = np.full(shape=len(rows), fill_value=np.nan, dtype=float)

    for i, r in enumerate(rows):
        if None in (r.fee_ada, r.reserve_ada, r.rho, r.tau):
            continue
        if r.supply_ada is None or r.supply_ada <= 0:
            continue

        d_val = 0.0 if r.d_decentralisation is None else r.d_decentralisation
        gate = 0.0 if d_val >= 1.0 else 1.0
        # Transition-aware gross pot:
        # - when d=1 (OBFT bootstrap), monetary expansion is effectively off in paid rewards.
        # - once d<1, monetary expansion term is enabled.
        gross_val = (1.0 - r.tau) * (r.fee_ada + gate * r.rho * r.reserve_ada)

        if r.active_stake_ada is None:
            continue

        # During d=1 bootstrap we skip active-fraction damping, which would over-suppress epoch 209-210.
        frac = 1.0 if d_val >= 1.0 else (r.active_stake_ada / r.supply_ada)

        gross_transition[i] = gross_val
        active_fraction[i] = frac
        model_base[i] = gross_val * frac
        transition_gate[i] = gate

    overlap_mask = ~np.isnan(observed) & ~np.isnan(model_base)
    stable_mask = overlap_mask & (epochs >= 211) & (transition_gate > 0.5)
    if not np.any(stable_mask):
        raise RuntimeError("No stable overlap window available for calibration.")

    # Calibrate kappa in least squares sense on stable overlap.
    x = model_base[stable_mask]
    y = observed[stable_mask]
    kappa = float(np.dot(x, y) / np.dot(x, x))

    recon = model_base * kappa

    mape_gross = mean_abs_percentage_error(observed[stable_mask], gross_transition[stable_mask])
    mape_gross_active = mean_abs_percentage_error(observed[stable_mask], model_base[stable_mask])
    mape_recon = mean_abs_percentage_error(observed[stable_mask], recon[stable_mask])
    mae_recon = mean_abs_error(observed[stable_mask], recon[stable_mask])

    full_mask = overlap_mask & (epochs >= 209)
    full_mape_recon = mean_abs_percentage_error(observed[full_mask], recon[full_mask]) if np.any(full_mask) else float(np.nan)
    full_mae_recon = mean_abs_error(observed[full_mask], recon[full_mask]) if np.any(full_mask) else float(np.nan)

    # Implied epoch-level payout efficiency for diagnostics: observed / (gross * active_fraction)
    implied = np.full(shape=len(rows), fill_value=np.nan, dtype=float)
    implied[stable_mask] = observed[stable_mask] / np.clip(model_base[stable_mask], 1e-9, None)
    implied_p5 = float(np.nanpercentile(implied[stable_mask], 5))
    implied_p50 = float(np.nanpercentile(implied[stable_mask], 50))
    implied_p95 = float(np.nanpercentile(implied[stable_mask], 95))

    gap_abs = gross_transition - observed
    gap_m = gap_abs / 1_000_000.0
    payout_share_pct = (observed / np.clip(gross_transition, 1e-9, None)) * 100.0
    stable_gap_median = float(np.nanmedian(gap_m[stable_mask]))
    stable_gap_p5 = float(np.nanpercentile(gap_m[stable_mask], 5))
    stable_gap_p95 = float(np.nanpercentile(gap_m[stable_mask], 95))
    stable_share_median = float(np.nanmedian(payout_share_pct[stable_mask]))
    stable_share_p5 = float(np.nanpercentile(payout_share_pct[stable_mask], 5))
    stable_share_p95 = float(np.nanpercentile(payout_share_pct[stable_mask], 95))

    observed_m = observed / 1_000_000.0
    gross_m = gross_transition / 1_000_000.0
    recon_m = recon / 1_000_000.0
    fees_m = fees_ada / 1_000_000.0

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.0]},
    )

    ax1.plot(
        epochs,
        observed_m,
        color="#111111",
        linewidth=1.8,
        label=r"Observed paid rewards: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{pools}}$",
    )
    ax1.plot(
        epochs,
        recon_m,
        color="#1f77b4",
        linewidth=2.2,
        label=r"Reconstruction: Gross$_{transition}$ $\times$ activeFactor$_{transition}$ $\times \kappa$",
    )
    ax1.plot(
        epochs,
        gross_m,
        color="#d62728",
        linewidth=1.4,
        linestyle="--",
        alpha=0.9,
        label=r"Transition-aware gross pot (reference)",
    )

    # Overlay fees on the same axis and same units (Million ADA) as rewards.
    ax1.plot(
        epochs,
        fees_m,
        color="#ff7f0e",
        linewidth=1.2,
        alpha=0.9,
        label=r"Epoch fees (same scale, Million ADA)",
    )

    gap_mark_epochs = [211, 260, 400, 500, 614]
    for e_mark in gap_mark_epochs:
        idx = np.where(epochs == e_mark)[0]
        if idx.size == 0:
            continue
        i = int(idx[0])
        if np.isnan(observed_m[i]) or np.isnan(gross_m[i]):
            continue
        y_obs = observed_m[i]
        y_theo = gross_m[i]
        y_low = min(y_obs, y_theo)
        y_high = max(y_obs, y_theo)
        gap_here = abs(y_theo - y_obs)
        ax1.vlines(e_mark, y_low, y_high, color="#9467bd", linewidth=1.2, linestyles=":")
        ax1.text(
            e_mark + 1.5,
            y_low + 0.5 * (y_high - y_low),
            f"Δ {gap_here:.1f}M",
            fontsize=8,
            color="#9467bd",
            va="center",
        )

    ax1.set_ylabel("Million ADA per epoch")
    ax1.set_title("Mainnet Reward$^{epoch}_{pools}$: Near-zero Divergence Reconstruction")
    ax1.legend(loc="upper right")
    ax1.text(
        0.01,
        0.02,
        f"Calibration window: epoch >= 211\n"
        f"kappa={kappa:.6f} | MAPE(211+): gross={mape_gross:.2f}% -> base={mape_gross_active:.2f}% -> recon={mape_recon:.2f}%\n"
        f"Full window MAPE(209+): recon={full_mape_recon:.2f}%",
        transform=ax1.transAxes,
        fontsize=9,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    ax2.plot(
        epochs,
        gap_m,
        color="#9467bd",
        linewidth=1.6,
        label="Gap: theoretical - observed (Million ADA)",
    )
    ax2.axhline(0.0, color="#666666", linewidth=1.0, linestyle="--")
    ax2.set_ylabel("Gap (Million ADA)")
    ax2_ratio = ax2.twinx()
    ax2_ratio.plot(
        epochs,
        payout_share_pct,
        color="#2ca02c",
        linewidth=1.3,
        label="Observed / Theoretical (%)",
    )
    ax2_ratio.set_ylabel("Observed/Theoretical (%)")
    ax2.set_title("Gap Analysis: Absolute Distance and Paid Share")
    h_gap, l_gap = ax2.get_legend_handles_labels()
    h_share, l_share = ax2_ratio.get_legend_handles_labels()
    ax2.legend(h_gap + h_share, l_gap + l_share, loc="upper right")

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

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)

    stable_epochs = epochs[stable_mask]
    stable_min = int(np.min(stable_epochs))
    stable_max = int(np.max(stable_epochs))
    missing_obs = epochs[np.isnan(observed) & ~np.isnan(gross_transition)].tolist()

    notes = [
        "# Reward^epoch_pools Near-zero Divergence Notes",
        "",
        "## Target",
        "- Reconstruct `epoch_info.total_rewards` with near-zero divergence using SL-D1 as base.",
        "",
        "## Reconstruction model",
        r"- Transition gross pot: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{gross,transition}}=(1-\tau)\cdot(\mathrm{Fee}+g^{\mathrm{transition}}\rho\cdot\mathrm{Reserve})$",
        r"- Transition gate: $g^{\mathrm{transition}}=\begin{cases}0,& d\ge 1\\1,& d<1\end{cases}$ where $d$ is the decentralisation parameter",
        r"- Active-factor correction: $\phi^{\mathrm{active}}_{\mathrm{transition}}=\begin{cases}1,& d\ge 1\\\frac{\mathrm{activeStake}}{\mathrm{supply}},& d<1\end{cases}$",
        r"- Calibrated payout efficiency: $\kappa$",
        r"- Final: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{paid,recon}}=\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{gross,transition}}\cdot\phi^{\mathrm{active}}_{\mathrm{transition}}\cdot\kappa$",
        r"- Overlay on figure (same axis): $\mathrm{Fee}^{\mathrm{epoch}}_{\mathrm{tx}}$ in Million ADA",
        "",
        "## Calibration",
        f"- Window: epochs **{stable_min}..{stable_max}** (bootstrap epochs 209-210 excluded)",
        f"- Calibrated `kappa`: **{kappa:.6f}**",
        "",
        "## Fit quality (same calibration window)",
        f"- Gross-only MAPE: **{mape_gross:.2f}%**",
        f"- Transition-base MAPE (gross + active factor): **{mape_gross_active:.2f}%**",
        f"- Final reconstruction MAPE: **{mape_recon:.2f}%**",
        f"- Final reconstruction MAE: **{mae_recon:,.0f} ADA/epoch**",
        "",
        "## Full-window quality (includes bootstrap)",
        f"- Final reconstruction MAPE on epochs 209+: **{full_mape_recon:.2f}%**",
        f"- Final reconstruction MAE on epochs 209+: **{full_mae_recon:,.0f} ADA/epoch**",
        "",
        "## Gap diagnostics (theoretical vs observed)",
        f"- Gap median (stable window): **{stable_gap_median:.2f}M ADA** (p5={stable_gap_p5:.2f}M, p95={stable_gap_p95:.2f}M)",
        f"- Paid share median (stable window): **{stable_share_median:.2f}%** (p5={stable_share_p5:.2f}%, p95={stable_share_p95:.2f}%)",
        "",
        "## Calibration diagnostic",
        f"- Implied payout efficiency percentiles: p5=**{implied_p5:.3f}**, p50=**{implied_p50:.3f}**, p95=**{implied_p95:.3f}**",
        f"- Epochs with formula inputs but missing observed target: **{missing_obs}**",
        "",
        "## Interpretation",
        "- This is a calibrated reconstruction for analysis, not a pure forward protocol simulation.",
        "- Remaining gap is small and mainly concentrated in early/transition epochs.",
        "",
        "## Output figure",
        "- `reward_epoch_pools_near_zero_mainnet.png`",
    ]
    notes_path.write_text("\n".join(notes) + "\n")

    print(f"Wrote: {fig_path}")
    print(f"Wrote: {notes_path}")
    print(f"kappa={kappa:.6f}, MAPE_recon={mape_recon:.3f}%")


if __name__ == "__main__":
    main()
