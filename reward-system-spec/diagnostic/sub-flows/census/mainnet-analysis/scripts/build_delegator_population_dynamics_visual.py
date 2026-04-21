#!/usr/bin/env python3
"""
§3.5 — Delegator population dynamics: entries and exits among productive pools.

Reads:
  data/delegator_population_dynamics.csv  (output of 06_delegator_population_dynamics.sql)

If the SQL output is not yet available, falls back to
  data/operator_landscape_history.csv
and computes the net change in productive-pool delegations per epoch.
The fallback cannot decompose into gross entries and exits.
Rerun after the SQL export for the full picture.

Outputs:
  figures/delegator_population_dynamics.png
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
GREY_LIGHT      = "#B0B0B0"
DAWN            = "#EC641D"
COBALT_PULSE    = "#2C4FFA"
ELECTRIC_BLUE   = "#16E9D8"

LOVELACE = 1e6


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def load_exact():
    """Load the SQL-exported per-epoch delegator birth/death decomposition."""
    rows = load_csv(DATA_DIR / "delegator_population_dynamics.csv")
    epochs, entries, exits, survivors, net = [], [], [], [], []
    for r in rows:
        e = int(r["epoch_no"])
        if e < 212:
            continue
        epochs.append(e)
        entries.append(int(r["entries"]))
        exits.append(int(r["exits"]))
        survivors.append(int(r["survivors"]))
        net.append(int(r["net_change"]))
    return (
        np.array(epochs),
        np.array(entries),
        np.array(exits),
        np.array(survivors),
        np.array(net),
    )


def load_from_landscape():
    """
    Fallback: derive net change from operator_landscape_history.csv.
    Uses the productive_delegations column.
    """
    rows = load_csv(DATA_DIR / "operator_landscape_history.csv")
    epochs, prod_deleg = [], []
    for r in rows:
        e = int(r["epoch_no"])
        if e < 211:
            continue
        epochs.append(e)
        prod_deleg.append(int(r["productive_delegations"]))

    epochs = np.array(epochs)
    prod_deleg = np.array(prod_deleg)

    net = np.diff(prod_deleg)
    ep_net = epochs[1:]
    return ep_net, net, prod_deleg[1:]


def smooth(arr, window=10):
    """Simple moving average."""
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")


def _format_thousands(x, _):
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.0f}K"
    return f"{x:.0f}"


def plot_exact(epochs, entries, exits, survivors, net):
    """Full decomposition: delegator entries and exits."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, (ax_flow, ax_stock) = plt.subplots(
        2, 1, figsize=(14, 10), facecolor=BG,
        gridspec_kw={"height_ratios": [3, 2]}, sharex=True,
    )

    # ── Top panel: entries / exits bar chart ──
    ax_flow.set_facecolor(BG)
    bar_w = 0.8

    ax_flow.bar(epochs, entries, width=bar_w, color=DELIVERED_GREEN,
                alpha=0.65, label="Entries (new productive-pool delegators)", zorder=2)
    ax_flow.bar(epochs, -exits, width=bar_w, color=INFARED,
                alpha=0.65, label="Exits (delegators leaving productive set)", zorder=2)

    if len(net) > 10:
        net_smooth = smooth(net.astype(float), window=10)
        ax_flow.plot(epochs, net_smooth, color=COBALT_PULSE, linewidth=2,
                     alpha=0.85, label="Net change (10-epoch MA)", zorder=3)
    ax_flow.axhline(0, color=INK, linewidth=0.6, alpha=0.4, zorder=1)

    ax_flow.set_ylabel("Delegators per epoch", fontsize=11, color=DIM)
    ax_flow.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_flow.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_flow.spines[sp].set_visible(False)
    ax_flow.spines["left"].set_color(GRID)
    ax_flow.tick_params(colors=DIM, labelsize=9)

    leg = ax_flow.legend(loc="upper right", fontsize=8.5,
                         framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Summary annotation
    total_entries = entries.sum()
    total_exits = exits.sum()
    avg_churn = (entries + exits).mean()
    ax_flow.text(
        0.02, 0.95,
        f"Total entries: {total_entries:,.0f}  |  Total exits: {total_exits:,.0f}  |  "
        f"Avg churn: {avg_churn:,.0f} delegators/epoch",
        transform=ax_flow.transAxes, fontsize=8.5, color=DIM,
        verticalalignment="top",
    )

    # ── Bottom panel: cumulative delegator stock ──
    ax_stock.set_facecolor(BG)
    stock = survivors + entries
    ax_stock.fill_between(epochs, stock, color=ULTRAVIOLET, alpha=0.2, zorder=2)
    ax_stock.plot(epochs, stock, color=ULTRAVIOLET, linewidth=1.4,
                  alpha=0.85, zorder=3,
                  label=f"Productive-pool delegators ({stock[-1]:,})")

    # Turnover rate on secondary axis
    turnover = (entries + exits) / np.maximum(stock, 1) * 100
    if len(turnover) > 10:
        turnover_smooth = smooth(turnover, window=10)
        ax_turn = ax_stock.twinx()
        ax_turn.plot(epochs, turnover_smooth, color=DAWN, linewidth=1.4,
                     alpha=0.8, label="Turnover rate (10-epoch MA)")
        ax_turn.set_ylabel("Turnover (%)", fontsize=10, color=DAWN)
        ax_turn.tick_params(axis="y", colors=DAWN, labelsize=9)
        ax_turn.spines["right"].set_color(DAWN)
        ax_turn.spines["right"].set_alpha(0.3)
        for sp in ["top", "left"]:
            ax_turn.spines[sp].set_visible(False)
        h2, l2 = ax_turn.get_legend_handles_labels()
    else:
        h2, l2 = [], []

    ax_stock.set_ylabel("Delegator count", fontsize=11, color=DIM)
    ax_stock.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_stock.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_stock.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_stock.spines[sp].set_visible(False)
    ax_stock.spines["left"].set_color(GRID)
    ax_stock.spines["bottom"].set_color(GRID)
    ax_stock.tick_params(colors=DIM, labelsize=9)

    h1, l1 = ax_stock.get_legend_handles_labels()
    leg2 = ax_stock.legend(h1 + h2, l1 + l2, loc="upper left",
                           fontsize=8.5, framealpha=0.95, edgecolor=GRID)
    leg2.get_frame().set_linewidth(0.5)

    ax_flow.set_xlim(epochs[0], epochs[-1])

    fig.suptitle(
        "Population Dynamics — Delegator Entries and Exits (productive pools)",
        fontsize=14, fontweight="medium", color=INK, y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out = FIG_DIR / "delegator_population_dynamics.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")


def plot_net_only(epochs, net, prod_deleg):
    """Fallback: net change only (no entry/exit decomposition)."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, (ax_net, ax_stock) = plt.subplots(
        2, 1, figsize=(14, 10), facecolor=BG,
        gridspec_kw={"height_ratios": [3, 2]}, sharex=True,
    )

    # ── Top panel: net change bar chart ──
    ax_net.set_facecolor(BG)
    colours = [DELIVERED_GREEN if v >= 0 else INFARED for v in net]
    ax_net.bar(epochs, net, width=0.8, color=colours, alpha=0.6, zorder=2)

    if len(net) > 10:
        net_smooth = smooth(net.astype(float), window=10)
        ax_net.plot(epochs, net_smooth, color=COBALT_PULSE, linewidth=2,
                    alpha=0.85, label="Net change (10-epoch MA)", zorder=3)

    ax_net.axhline(0, color=INK, linewidth=0.6, alpha=0.4, zorder=1)

    ax_net.set_ylabel("Net change in productive-pool delegators", fontsize=11, color=DIM)
    ax_net.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_net.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_net.spines[sp].set_visible(False)
    ax_net.spines["left"].set_color(GRID)
    ax_net.tick_params(colors=DIM, labelsize=9)

    leg = ax_net.legend(loc="upper right", fontsize=8.5,
                        framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Summary
    pos_epochs = (net > 0).sum()
    neg_epochs = (net < 0).sum()
    ax_net.text(
        0.02, 0.95,
        f"Growth epochs: {pos_epochs}  |  Decline epochs: {neg_epochs}  |  "
        f"Net over period: {net.sum():+,}",
        transform=ax_net.transAxes, fontsize=8.5, color=DIM,
        verticalalignment="top",
    )

    # ── Bottom panel: delegator stock ──
    ax_stock.set_facecolor(BG)
    ax_stock.fill_between(epochs, prod_deleg, color=ULTRAVIOLET,
                          alpha=0.2, zorder=2)
    ax_stock.plot(epochs, prod_deleg, color=ULTRAVIOLET, linewidth=1.4,
                  alpha=0.85, zorder=3,
                  label=f"Productive-pool delegators ({prod_deleg[-1]:,})")

    ax_stock.set_ylabel("Delegator count", fontsize=11, color=DIM)
    ax_stock.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_stock.yaxis.set_major_formatter(mticker.FuncFormatter(_format_thousands))
    ax_stock.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_stock.spines[sp].set_visible(False)
    ax_stock.spines["left"].set_color(GRID)
    ax_stock.spines["bottom"].set_color(GRID)
    ax_stock.tick_params(colors=DIM, labelsize=9)
    ax_stock.legend(loc="upper left", fontsize=8.5,
                    framealpha=0.95, edgecolor=GRID).get_frame().set_linewidth(0.5)

    ax_net.set_xlim(epochs[0], epochs[-1])

    fig.suptitle(
        "Population Dynamics — Net Change in Productive-Pool Delegators (fallback)",
        fontsize=14, fontweight="medium", color=INK, y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out = FIG_DIR / "delegator_population_dynamics.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")
    print("  ⚠  Fallback mode: showing net change only (no entry/exit decomposition).")
    print("     Run 06_delegator_population_dynamics.sql and rerun for the full picture.")


def main():
    exact_path = DATA_DIR / "delegator_population_dynamics.csv"
    if exact_path.exists():
        print("Loading exact SQL output …")
        epochs, entries, exits, survivors, net = load_exact()
        plot_exact(epochs, entries, exits, survivors, net)
    else:
        print("SQL output not found — falling back to net-change-only …")
        ep_net, net, prod_deleg = load_from_landscape()
        plot_net_only(ep_net, net, prod_deleg)


if __name__ == "__main__":
    main()
