#!/usr/bin/env python3
"""
§3.6 — Delegation churn: pool switching behaviour.

Reads:
  data/delegation_churn_per_epoch.csv   (from 08_delegation_churn.sql)
  data/delegation_tenure_distribution.csv (from 08c_tenure_distribution.sql)

Outputs:
  figures/delegation_churn.png
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ──
REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
INFARED         = "#E52321"
DELIVERED_GREEN = "#00875A"
ULTRAVIOLET     = "#A700FF"
SOLAR_AMBER     = "#FFBA36"
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"
ELECTRIC_BLUE   = "#16E9D8"
ACID_GREEN      = "#06FF89"


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def smooth(arr, window=10):
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")


def _format_thousands(x, _):
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.0f}K"
    return f"{x:.0f}"


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load churn per epoch ──
    rows = load_csv(DATA_DIR / "delegation_churn_per_epoch.csv")
    epochs, redel, initial, renewals = [], [], [], []
    for r in rows:
        e = int(r["epoch_no"])
        if e < 210 or e > 623:
            continue
        epochs.append(e)
        redel.append(int(r["redelegations"]))
        initial.append(int(r["initial_delegations"]))
        renewals.append(int(r["renewals"]))

    epochs = np.array(epochs)
    redel = np.array(redel)
    initial = np.array(initial)
    renewals = np.array(renewals)
    total = redel + initial + renewals

    # ── Load tenure distribution ──
    tenure_rows = load_csv(DATA_DIR / "delegation_tenure_distribution.csv")
    tenure_buckets = [r["tenure_bucket"] for r in tenure_rows]
    tenure_counts = [int(r["delegation_count"]) for r in tenure_rows]
    tenure_pcts = [float(r["pct"]) for r in tenure_rows]

    # ── Figure: 3 panels ──
    fig, (ax_comp, ax_rate, ax_tenure) = plt.subplots(
        3, 1, figsize=(14, 14), facecolor=BG,
        gridspec_kw={"height_ratios": [3, 2, 2]},
    )

    # ── Panel 1: stacked certificate composition ──
    ax_comp.set_facecolor(BG)
    ax_comp.fill_between(epochs, 0, initial, color=DELIVERED_GREEN,
                         alpha=0.5, label="Initial delegations", zorder=2)
    ax_comp.fill_between(epochs, initial, initial + redel, color=INFARED,
                         alpha=0.5, label="Redelegations (pool switch)", zorder=2)
    ax_comp.fill_between(epochs, initial + redel, total, color=SOLAR_AMBER,
                         alpha=0.4, label="Renewals (same pool)", zorder=2)

    ax_comp.set_ylabel("Delegation certificates per epoch", fontsize=11, color=DIM)
    ax_comp.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_comp.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_comp.spines[sp].set_visible(False)
    ax_comp.spines["left"].set_color(GRID)
    ax_comp.tick_params(colors=DIM, labelsize=9)
    ax_comp.set_xlim(epochs[0], epochs[-1])

    leg = ax_comp.legend(loc="upper right", fontsize=8.5,
                         framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    total_redel = redel.sum()
    total_initial = initial.sum()
    ax_comp.text(
        0.02, 0.95,
        f"Total certificates: {total.sum():,}  |  "
        f"Initial: {total_initial:,} ({100*total_initial/total.sum():.0f}%)  |  "
        f"Switches: {total_redel:,} ({100*total_redel/total.sum():.0f}%)",
        transform=ax_comp.transAxes, fontsize=8.5, color=DIM,
        verticalalignment="top",
    )

    # ── Panel 2: redelegation rate ──
    ax_rate.set_facecolor(BG)
    ax_rate.bar(epochs, redel, width=0.8, color=INFARED,
                alpha=0.4, label="Redelegations", zorder=2)

    if len(redel) > 10:
        redel_smooth = smooth(redel.astype(float), window=20)
        ax_rate.plot(epochs, redel_smooth, color=INFARED, linewidth=2,
                     alpha=0.85, label="20-epoch MA", zorder=3)

    ax_rate.set_ylabel("Redelegations per epoch", fontsize=11, color=DIM)
    ax_rate.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_rate.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_rate.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_rate.spines[sp].set_visible(False)
    ax_rate.spines["left"].set_color(GRID)
    ax_rate.spines["bottom"].set_color(GRID)
    ax_rate.tick_params(colors=DIM, labelsize=9)
    ax_rate.set_xlim(epochs[0], epochs[-1])

    leg2 = ax_rate.legend(loc="upper right", fontsize=8.5,
                          framealpha=0.95, edgecolor=GRID)
    leg2.get_frame().set_linewidth(0.5)

    # Recent avg annotation
    recent_mask = epochs >= 604
    recent_avg = redel[recent_mask].mean() if recent_mask.any() else 0
    historical_avg = redel.mean()
    ax_rate.text(
        0.02, 0.95,
        f"Historical avg: {historical_avg:,.0f}/epoch  |  "
        f"Recent (ep 604+): {recent_avg:,.0f}/epoch  "
        f"({100*(recent_avg/historical_avg - 1):+.0f}%)",
        transform=ax_rate.transAxes, fontsize=8.5, color=DIM,
        verticalalignment="top",
    )

    # ── Panel 3: tenure distribution ──
    ax_tenure.set_facecolor(BG)
    colours = [ULTRAVIOLET if "201" in b else
               COBALT_PULSE if "101" in b or "51" in b else
               DAWN if "26" in b or "11" in b else
               INFARED for b in tenure_buckets]
    bars = ax_tenure.bar(range(len(tenure_buckets)), tenure_pcts,
                         color=colours, alpha=0.7, zorder=2)

    # Map epoch buckets to human-readable durations (1 epoch = 5 days)
    duration_labels = {
        "0-5":    "≤ 25 days",
        "6-10":   "1–2 months",
        "11-25":  "2–4 months",
        "26-50":  "4–8 months",
        "51-100": "8–17 months",
        "101-200": "1.4–2.7 years",
        "201+":   "> 2.7 years",
    }
    ax_tenure.set_xticks(range(len(tenure_buckets)))
    ax_tenure.set_xticklabels(
        [f"{b} epochs\n({duration_labels.get(b, '')})" for b in tenure_buckets],
        fontsize=8.5, color=DIM,
    )
    ax_tenure.set_ylabel("Share of delegations (%)", fontsize=11, color=DIM)
    ax_tenure.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_tenure.spines[sp].set_visible(False)
    ax_tenure.spines["left"].set_color(GRID)
    ax_tenure.spines["bottom"].set_color(GRID)
    ax_tenure.tick_params(colors=DIM, labelsize=9)

    # Add value labels on bars
    for bar, pct in zip(bars, tenure_pcts):
        ax_tenure.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                       f"{pct:.1f}%", ha="center", va="bottom",
                       fontsize=9, color=DIM, fontweight="medium")

    ax_tenure.set_title("Delegation tenure distribution",
                        fontsize=11, color=DIM, pad=8)

    fig.suptitle(
        "Delegation Churn — Pool Switching Behaviour",
        fontsize=14, fontweight="medium", color=INK, y=0.99,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out = FIG_DIR / "delegation_churn.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
