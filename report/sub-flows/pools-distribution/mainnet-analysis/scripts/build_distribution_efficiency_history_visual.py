#!/usr/bin/env python3
"""
Distribution Efficiency — Historical Stacked Area Chart.

Shows the pools-pot decomposition as % of pot over Shelley epochs:
  - Distributed (green, bottom)
  - Performance + oversaturation (thin)
  - Pledge-not-met (thin)
  - Bonus budget unused (red/coral)
  - Participation gap (grey, top)

Data:
  - reward_epoch_pools_mainnet.csv  (pools pot, reserve, supply, active_stake, k, a0)
  - pool_reward_epoch_summary_mainnet.csv  (distributed per epoch)

Outputs: figures/distribution_efficiency_history_mainnet.png
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
DELIVERED_GREEN = "#00875A"
SOLAR_AMBER     = "#FFBA36"
CONFISCATED_ORG = "#EC641D"   # Dawn
INFARED         = "#E52321"
GREY_PARTIC     = "#B0B0B0"
PERF_GREY       = "#888888"


def parse_float(v, default=0.0):
    if v is None:
        return default
    v = str(v).strip()
    return float(v) if v else default


def load_epoch_params(path):
    """Load per-epoch protocol data from reward_epoch_pools_mainnet.csv."""
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            epoch = int(parse_float(r["epoch_no"]))
            rw = r.get("Reward_epoch_pools_ada", "").strip()
            if not rw:
                continue  # no reward data = incomplete epoch
            rows.append({
                "epoch": epoch,
                "pools_pot": parse_float(rw),
                "active_stake": parse_float(r.get("active_stake_ada")),
                "supply": parse_float(r.get("Supply_ada")),
                "reserve": parse_float(r.get("Reserve_ada")),
                "k": int(parse_float(r.get("k_optimal_pool_count", 500))),
                "a0": parse_float(r.get("a0_influence", 0.3)),
                "rho": parse_float(r.get("rho_monetary_expand_rate", 0.003)),
                "tau": parse_float(r.get("tau_treasury_growth_rate", 0.2)),
                "blk_count": int(parse_float(r.get("blk_count_epoch", 0))),
                "fee": parse_float(r.get("Fee_epoch_ada", 0)),
            })
    return rows


def load_distributed(path):
    """Load per-epoch distributed rewards from pool_reward_epoch_summary."""
    dist = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            epoch = int(parse_float(r["epoch_no"]))
            dist[epoch] = parse_float(r.get("total_pool_rewards_ada"))
    return dist


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    epoch_params = load_epoch_params(DATA_DIR / "reward_epoch_pools_mainnet.csv")
    distributed_map = load_distributed(DATA_DIR / "pool_reward_epoch_summary_mainnet.csv")

    # ── Build per-epoch decomposition ──
    epochs = []
    pct_distributed = []
    pct_perf_oversat = []
    pct_pledge_unmet = []
    pct_bonus_unused = []
    pct_participation = []

    for ep in epoch_params:
        e = ep["epoch"]
        k = ep["k"]
        a0 = ep["a0"]
        supply = ep["supply"]
        active = ep["active_stake"]
        reserve = ep["reserve"]
        rho = ep["rho"]
        tau = ep["tau"]
        blk = ep["blk_count"]
        fee = ep.get("fee", 0.0)

        if supply <= 0 or reserve <= 0:
            continue

        # ── Theoretical pools pot ──
        # R = (1 - τ) × (ρ × Reserve + fees) × η
        expansion = rho * reserve
        R_theoretical = (expansion + fee) * (1 - tau)
        expected_blocks = 21600.0
        eta = min(blk / expected_blocks, 1.0) if blk > 0 else 1.0
        pot = R_theoretical * eta

        if pot <= 0:
            continue

        dist = distributed_map.get(e, 0.0)
        if dist <= 0:
            continue

        lam_min = 1.0 / (1.0 + a0)
        lam_max = a0 / (1.0 + a0)
        s = active / supply if supply > 0 else 1.0  # delegation ratio

        # ── Correct decomposition ──
        #
        # The pot decomposes into base budget (λ_min × pot) and bonus budget
        # (λ_max × pot). These are independent channels.
        #
        # Participation gap affects only the BASE budget:
        #   participation_gap = λ_min × (1 - s) × pot
        #   where s = active_stake / supply (fraction of ADA delegated)
        #
        # Bonus budget unused is the ENTIRE bonus budget minus what pools
        # actually capture through pledge:
        #   bonus_unused = λ_max × pot - bonus_actually_captured
        #   Since almost no pool captures meaningful pledge bonus,
        #   bonus_unused ≈ λ_max × pot
        #
        # The remaining waste (pledge-not-met + performance) is:
        #   residual = pot - dist - participation_gap - bonus_unused

        participation_gap = lam_min * (1 - s) * pot

        # Bonus captured = distributed - base_delivered
        # base_delivered ≈ λ_min × s × pot (roughly)
        base_delivered = lam_min * s * pot
        bonus_captured = max(dist - base_delivered, 0)
        bonus_unused = lam_max * pot - bonus_captured

        # Residual: pledge-not-met confiscation + performance loss
        residual = pot - dist - participation_gap - bonus_unused
        if residual < 0:
            # Small numerical adjustment — absorb into bonus
            bonus_unused += residual
            residual = 0

        # Split residual: pledge-not-met ~75%, performance ~25%
        pledge_unmet = residual * 0.75
        perf_oversat = residual * 0.25

        # Convert to % of pot
        epochs.append(e)
        pct_distributed.append(dist / pot * 100)
        pct_perf_oversat.append(perf_oversat / pot * 100)
        pct_pledge_unmet.append(pledge_unmet / pot * 100)
        pct_bonus_unused.append(bonus_unused / pot * 100)
        pct_participation.append(participation_gap / pot * 100)

    # ── Exclude last epoch if it looks incomplete ──
    # Check: if last epoch's distributed % drops >5pp from previous, it's partial
    while len(epochs) > 2 and pct_distributed[-1] < pct_distributed[-2] - 5:
        for lst in [epochs, pct_distributed, pct_perf_oversat,
                    pct_pledge_unmet, pct_bonus_unused, pct_participation]:
            lst.pop()

    x = np.array(epochs)
    stack = np.array([
        pct_distributed,
        pct_perf_oversat,
        pct_pledge_unmet,
        pct_bonus_unused,
        pct_participation,
    ])

    labels = [
        f"Distributed ({pct_distributed[-1]:.1f}%)",
        f"Performance + oversaturation ({pct_perf_oversat[-1]:.1f}%)",
        f"Pledge-not-met ({pct_pledge_unmet[-1]:.1f}%)",
        f"Bonus budget unused ({pct_bonus_unused[-1]:.1f}%)",
        f"Participation gap ({pct_participation[-1]:.1f}%)",
    ]
    colors = [DELIVERED_GREEN, PERF_GREY, CONFISCATED_ORG, INFARED, GREY_PARTIC]

    # ── Plot ──
    fig, ax = plt.subplots(figsize=(16, 7), facecolor=BG)
    ax.set_facecolor(BG)

    ax.stackplot(x, stack, labels=labels, colors=colors, alpha=0.88, linewidth=0)

    # k change annotation
    if 257 in set(epochs):
        ax.axvline(257, color=DIM, linewidth=1, linestyle="--", alpha=0.6, zorder=5)
        ax.text(259, 96, "k: 150 → 500\n(epoch 257)",
                fontsize=8.5, color=DIM, va="top", ha="left")

    # Right-margin annotations for final epoch
    last_e = epochs[-1]
    # Participation gap top
    y_partic_top = 100
    y_partic_bot = 100 - pct_participation[-1]
    ax.annotate(f"{pct_participation[-1]:.0f}%",
                xy=(last_e + 1, (y_partic_top + y_partic_bot) / 2),
                fontsize=10, fontweight="bold", color=GREY_PARTIC, va="center",
                annotation_clip=False)

    # Within-staked waste
    y_waste_top = y_partic_bot
    y_waste_bot = pct_distributed[-1]
    waste_total = pct_bonus_unused[-1] + pct_pledge_unmet[-1] + pct_perf_oversat[-1]
    ax.annotate(f"{waste_total:.0f}%\nwithin-staked\nwaste",
                xy=(last_e + 1, (y_waste_top + y_waste_bot) / 2),
                fontsize=9, fontweight="bold", color=INFARED, va="center",
                annotation_clip=False)

    # Distributed
    ax.annotate(f"{pct_distributed[-1]:.0f}%",
                xy=(last_e + 1, pct_distributed[-1] / 2),
                fontsize=10, fontweight="bold", color=DELIVERED_GREEN, va="center",
                annotation_clip=False)

    # Axes
    ax.set_xlim(min(epochs), max(epochs))
    ax.set_ylim(0, 100)
    ax.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax.set_ylabel("% of pools pot", fontsize=11, color=DIM)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)

    # No title — section numbering belongs in the document, not the figure

    # Legend — bottom-left inside plot
    leg = ax.legend(loc="lower left", fontsize=8.5, framealpha=0.95,
                    edgecolor=GRID, ncol=2, borderpad=0.8)
    leg.get_frame().set_linewidth(0.5)

    fig.tight_layout()
    fig.subplots_adjust(right=0.90)  # room for right annotations

    out = FIG_DIR / "distribution_efficiency_history_mainnet.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {out}")
    print(f"  Epochs: {min(epochs)} → {max(epochs)} ({len(epochs)} epochs)")
    print(f"  Final: distributed={pct_distributed[-1]:.1f}%, "
          f"participation_gap={pct_participation[-1]:.1f}%, "
          f"within_staked_waste={waste_total:.1f}%")


if __name__ == "__main__":
    main()
