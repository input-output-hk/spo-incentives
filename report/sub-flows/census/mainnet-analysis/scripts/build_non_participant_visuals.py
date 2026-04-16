#!/usr/bin/env python3
"""
§4 — Non-participants: where is the unstaked ADA?

Always produces (from existing CSVs):
  figures/circulating_supply_decomposition.png
    Stacked-area history of circulating ADA broken into:
      staked | unstaked UTxO | unclaimed rewards | deposits

When SQL output is available, additionally produces:
  figures/non_participant_breakdown.png
    Two-panel figure:
      (left)  UTxO decomposition by address type × delegation status
      (right) Dormancy vintage of non-delegated UTxOs

Reads:
  data/supply_decomposition.csv     (always)
  data/staking_per_epoch.csv        (always)
  data/utxo_address_type_decomposition.csv  (optional — from 07_non_participant_decomposition.sql)
  data/non_participant_dormancy.csv         (optional — from 07_non_participant_decomposition.sql)
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
ACID_GREEN      = "#06FF89"
HYPER_PINK      = "#FF79FC"
EMBER_ORANGE    = "#FF532C"
ULTRAVIOLET_DEEP = "#8421A2"

LOVELACE = 1e6


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


# ═══════════════════════════════════════════════════════════════
# Figure 1 — Historical supply decomposition (always produced)
# ═══════════════════════════════════════════════════════════════

def build_historical_figure():
    """Stacked-area of circulating ADA: staked, unstaked UTxO, rewards, deposits."""
    supply = load_csv(DATA_DIR / "supply_decomposition.csv")
    staking = load_csv(DATA_DIR / "staking_per_epoch.csv")

    # Build a lookup: epoch → total_staked
    staked_by_epoch = {int(r["epoch_no"]): int(r["total_staked"]) for r in staking}

    epochs = []
    s_staked = []
    s_unstaked_utxo = []
    s_rewards = []
    s_deposits = []
    s_circulating = []

    for r in supply:
        e = int(r["epoch_no"])
        if e < 211 or e not in staked_by_epoch:
            continue

        circ = int(r["circulating"])
        utxo = int(r["utxo"])
        rewards = int(r["unclaimed_rewards"])
        deposits = int(r["deposits"])
        staked = staked_by_epoch[e]

        # fees_pot = circ - utxo - rewards - deposits  (tiny, fold into deposits)
        fees = circ - utxo - rewards - deposits
        deposits += fees

        unstaked_utxo = utxo - staked

        epochs.append(e)
        s_staked.append(staked)
        s_unstaked_utxo.append(unstaked_utxo)
        s_rewards.append(rewards)
        s_deposits.append(deposits)
        s_circulating.append(circ)

    epochs = np.array(epochs)
    s_staked = np.array(s_staked, dtype=float) / 1e6  # → ADA
    s_unstaked_utxo = np.array(s_unstaked_utxo, dtype=float) / 1e6
    s_rewards = np.array(s_rewards, dtype=float) / 1e6
    s_deposits = np.array(s_deposits, dtype=float) / 1e6
    s_circulating = np.array(s_circulating, dtype=float) / 1e6

    # Convert to billions for display
    B = 1e9
    fig, (ax_abs, ax_pct) = plt.subplots(
        2, 1, figsize=(14, 10), facecolor=BG,
        gridspec_kw={"height_ratios": [3, 2]}, sharex=True,
    )

    # ── Top: absolute stacked area ──
    ax_abs.set_facecolor(BG)
    ax_abs.stackplot(
        epochs,
        s_staked / B,
        s_unstaked_utxo / B,
        s_rewards / B,
        s_deposits / B,
        colors=[DELIVERED_GREEN, COBALT_PULSE, SOLAR_AMBER, GREY_LIGHT],
        alpha=0.6,
        labels=[
            "Staked ADA",
            "Unstaked UTxO (non-participants)",
            "Unclaimed rewards",
            "Deposits + fees",
        ],
    )
    ax_abs.plot(epochs, s_circulating / B, color=INK, linewidth=0.8,
                linestyle=":", alpha=0.4, label="Circulating supply")

    ax_abs.set_ylabel("ADA (billions)", fontsize=11, color=DIM)
    ax_abs.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_abs.spines[sp].set_visible(False)
    ax_abs.spines["left"].set_color(GRID)
    ax_abs.tick_params(colors=DIM, labelsize=9)

    leg = ax_abs.legend(loc="upper left", fontsize=8.5,
                        framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # Latest-epoch annotation
    last_e = epochs[-1]
    last_unstaked = s_unstaked_utxo[-1] / B
    last_circ = s_circulating[-1] / B
    pct_unstaked = s_unstaked_utxo[-1] / s_circulating[-1] * 100
    ax_abs.annotate(
        f"Epoch {last_e}: {last_unstaked:.2f}B unstaked UTxO ({pct_unstaked:.1f}% of circulating)",
        xy=(last_e, (s_staked[-1] + s_unstaked_utxo[-1]) / B),
        xytext=(last_e - 160, last_circ / B - 5),
        fontsize=8, color=DIM,
        arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7),
    )

    # ── Bottom: percentage shares ──
    ax_pct.set_facecolor(BG)
    pct_staked = s_staked / s_circulating * 100
    pct_unstaked_utxo = s_unstaked_utxo / s_circulating * 100
    pct_rewards = s_rewards / s_circulating * 100
    pct_deposits = s_deposits / s_circulating * 100

    ax_pct.stackplot(
        epochs,
        pct_staked,
        pct_unstaked_utxo,
        pct_rewards,
        pct_deposits,
        colors=[DELIVERED_GREEN, COBALT_PULSE, SOLAR_AMBER, GREY_LIGHT],
        alpha=0.6,
    )

    ax_pct.set_ylabel("Share of circulating (%)", fontsize=11, color=DIM)
    ax_pct.set_xlabel("Epoch", fontsize=11, color=DIM)
    ax_pct.set_ylim(0, 100)
    ax_pct.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_pct.spines[sp].set_visible(False)
    ax_pct.spines["left"].set_color(GRID)
    ax_pct.spines["bottom"].set_color(GRID)
    ax_pct.tick_params(colors=DIM, labelsize=9)

    # Annotate final percentages
    y_cursor = 0
    for label, pct_val, colour in [
        ("Staked", pct_staked[-1], DELIVERED_GREEN),
        ("Unstaked UTxO", pct_unstaked_utxo[-1], COBALT_PULSE),
        ("Rewards", pct_rewards[-1], SOLAR_AMBER),
        ("Deposits", pct_deposits[-1], GREY_LIGHT),
    ]:
        mid = y_cursor + pct_val / 2
        if pct_val > 2:  # only label if visible
            ax_pct.text(
                last_e + 3, mid,
                f"{pct_val:.1f}%",
                fontsize=8, color=colour, fontweight="medium",
                verticalalignment="center", clip_on=False,
            )
        y_cursor += pct_val

    ax_abs.set_xlim(epochs[0], epochs[-1])

    fig.suptitle(
        "Circulating Supply Decomposition — Where Does the ADA Live?",
        fontsize=14, fontweight="medium", color=INK, y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out = FIG_DIR / "circulating_supply_decomposition.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")

    # Return latest-epoch numbers for README prose
    return {
        "epoch": int(last_e),
        "circulating_ada": s_circulating[-1],
        "staked_ada": s_staked[-1],
        "unstaked_utxo_ada": s_unstaked_utxo[-1],
        "rewards_ada": s_rewards[-1],
        "deposits_ada": s_deposits[-1],
        "pct_staked": pct_staked[-1],
        "pct_unstaked_utxo": pct_unstaked_utxo[-1],
        "pct_rewards": pct_rewards[-1],
        "pct_deposits": pct_deposits[-1],
    }


# ═══════════════════════════════════════════════════════════════
# Figure 2 — Current-epoch UTxO breakdown (when SQL output exists)
# ═══════════════════════════════════════════════════════════════

# Friendly labels and colours for address-type classifications
ADDR_TYPE_META = {
    "base_delegated":          ("Base — delegated (staked)",       DELIVERED_GREEN),
    "base_not_delegated":      ("Base — not delegated",            COBALT_PULSE),
    "enterprise":              ("Enterprise (no staking cred)",    DAWN),
    "script_delegated":        ("Script — delegated",              ELECTRIC_BLUE),
    "script_not_delegated":    ("Script — not delegated",          ULTRAVIOLET),
    "script_no_staking_cred":  ("Script — no staking cred",       ULTRAVIOLET_DEEP),
}

DORMANCY_META = {
    "pre_shelley":           ("Pre-Shelley (< epoch 208)",     INFARED),
    "early_shelley_208_299": ("Early Shelley (208–299)",        DAWN),
    "epoch_300_399":         ("Epochs 300–399",                 SOLAR_AMBER),
    "epoch_400_499":         ("Epochs 400–499",                 COBALT_PULSE),
    "epoch_500_599":         ("Epochs 500–599",                 ELECTRIC_BLUE),
    "epoch_600_plus":        ("Epochs 600+",                    DELIVERED_GREEN),
}


def build_breakdown_figure():
    """Two-panel figure: address-type pie + dormancy bar."""
    addr_path = DATA_DIR / "utxo_address_type_decomposition.csv"
    dorm_path = DATA_DIR / "non_participant_dormancy.csv"

    if not addr_path.exists():
        print("  utxo_address_type_decomposition.csv not found — skipping breakdown figure.")
        return None

    addr_rows = load_csv(addr_path)
    if not addr_rows:
        print("  utxo_address_type_decomposition.csv is empty — skipping breakdown figure.")
        return None
    has_dormancy = dorm_path.exists()
    dorm_rows = load_csv(dorm_path) if has_dormancy else []

    ncols = 2 if has_dormancy else 1
    fig, axes = plt.subplots(1, ncols, figsize=(7 * ncols, 7), facecolor=BG)
    if ncols == 1:
        axes = [axes]

    # ── Left panel: address-type donut ──
    ax_addr = axes[0]
    ax_addr.set_facecolor(BG)

    labels, sizes, colours = [], [], []
    for r in sorted(addr_rows, key=lambda x: int(x["total_lovelace"]), reverse=True):
        cls = r["classification"]
        ada = int(r["total_lovelace"]) / LOVELACE
        meta = ADDR_TYPE_META.get(cls, (cls, GREY_LIGHT))
        labels.append(meta[0])
        sizes.append(ada)
        colours.append(meta[1])

    total = sum(sizes)
    wedges, texts, autotexts = ax_addr.pie(
        sizes, labels=None, colors=colours, autopct="",
        startangle=90, pctdistance=0.8,
        wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=1.5),
    )
    # Custom labels: name + ADA + %
    legend_labels = [
        f"{l}\n{s / 1e9:.2f}B ADA ({s / total * 100:.1f}%)"
        for l, s in zip(labels, sizes)
    ]
    ax_addr.legend(wedges, legend_labels, loc="center left",
                   bbox_to_anchor=(-0.35, 0.5), fontsize=8.5,
                   framealpha=0.95, edgecolor=GRID)
    ax_addr.set_title("UTxO by Address Type", fontsize=12,
                      fontweight="medium", color=INK, pad=15)

    # ── Right panel: dormancy vintage ──
    if has_dormancy:
        ax_dorm = axes[1]
        ax_dorm.set_facecolor(BG)

        d_labels, d_sizes, d_colours = [], [], []
        for r in dorm_rows:
            v = r["vintage"]
            ada = int(r["total_lovelace"]) / LOVELACE
            meta = DORMANCY_META.get(v, (v, GREY_LIGHT))
            d_labels.append(meta[0])
            d_sizes.append(ada / 1e9)  # billions
            d_colours.append(meta[1])

        bars = ax_dorm.barh(d_labels, d_sizes, color=d_colours, alpha=0.7,
                            edgecolor=BG, linewidth=0.5)
        for bar, val in zip(bars, d_sizes):
            ax_dorm.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                         f"{val:.2f}B", fontsize=9, color=DIM, va="center")

        ax_dorm.set_xlabel("ADA (billions)", fontsize=10, color=DIM)
        ax_dorm.set_title("Non-Delegated UTxO by Creation Vintage",
                          fontsize=12, fontweight="medium", color=INK, pad=15)
        ax_dorm.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
        for sp in ["top", "right"]:
            ax_dorm.spines[sp].set_visible(False)
        ax_dorm.spines["bottom"].set_color(GRID)
        ax_dorm.spines["left"].set_color(GRID)
        ax_dorm.tick_params(colors=DIM, labelsize=9)
        ax_dorm.invert_yaxis()

    fig.suptitle(
        "Non-Participant Decomposition — Current UTxO Snapshot",
        fontsize=14, fontweight="medium", color=INK, y=1.02,
    )
    fig.tight_layout()

    out = FIG_DIR / "non_participant_breakdown.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")
    return addr_rows


def main():
    print("Building historical supply decomposition …")
    stats = build_historical_figure()

    print(f"\n  Epoch {stats['epoch']}:")
    print(f"    Circulating:    {stats['circulating_ada'] / 1e9:.2f}B ADA")
    print(f"    Staked:         {stats['staked_ada'] / 1e9:.2f}B ({stats['pct_staked']:.1f}%)")
    print(f"    Unstaked UTxO:  {stats['unstaked_utxo_ada'] / 1e9:.2f}B ({stats['pct_unstaked_utxo']:.1f}%)")
    print(f"    Rewards:        {stats['rewards_ada'] / 1e9:.2f}B ({stats['pct_rewards']:.1f}%)")
    print(f"    Deposits:       {stats['deposits_ada'] / 1e9:.2f}B ({stats['pct_deposits']:.1f}%)")

    print("\nChecking for SQL output …")
    result = build_breakdown_figure()
    if result is None:
        print("  Run 07_non_participant_decomposition.sql for the address-type breakdown.")


if __name__ == "__main__":
    main()
