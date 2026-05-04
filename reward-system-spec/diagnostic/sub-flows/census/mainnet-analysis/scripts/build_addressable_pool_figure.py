#!/usr/bin/env python3
"""Build the addressable-pool decomposition figure (CEN.5.5).

Three small panels in one figure:
  (left)   size distribution by credential type — where does the addressable
           ADA actually sit?
  (middle) registration vintage — when did these holders opt in to the
           staking system without ever delegating?
  (right)  lifecycle — never-delegated vs ex-delegators who undelegated.

Reads:
  data/addressable_pool_size.csv
  data/addressable_pool_vintage.csv
  data/addressable_pool_lifecycle.csv

Writes:
  figures/addressable_pool.png
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPORT = Path(__file__).resolve().parent.parent
DATA = REPORT / "data"
FIG = REPORT / "figures"

BG       = "#FFFFFF"
INK      = "#1A1A1A"
DIM      = "#666666"
GRID     = "#EBEBEB"
INFARED  = "#E52321"
DAWN     = "#EC641D"
SOLAR    = "#FFBA36"
COBALT   = "#2C4FFA"
ELEC     = "#16E9D8"
GREY     = "#B0B0B0"
ACID     = "#06FF89"
ULTRA    = "#A700FF"
VOLT     = "#F2FF58"

KEY_C = COBALT
SCRIPT_C = ULTRA

SIZE_BUCKETS = [
    "00_zero", "01_under_10_ada", "02_10_to_100_ada",
    "03_100_to_1k_ada", "04_1k_to_10k_ada",
    "05_10k_to_100k_ada", "06_100k_to_1m_ada",
    "07_1m_to_10m_ada", "08_above_10m_ada",
]
SIZE_LABELS = [
    "0", "<10", "10–100", "100–1k", "1k–10k",
    "10k–100k", "100k–1M", "1M–10M", "≥10M",
]

VINTAGE_ORDER = [
    "01_shelley_allegra_208_249",
    "02_mary_250_289",
    "03_alonzo_290_349",
    "04_babbage_350_449",
    "05_early_conway_450_549",
    "06_late_conway_550_plus",
]
VINTAGE_LABELS = [
    "Shelley/\nAllegra",
    "Mary",
    "Alonzo",
    "Babbage",
    "Early\nConway",
    "Late\nConway",
]


def load_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def build():
    FIG.mkdir(parents=True, exist_ok=True)
    size_rows = load_csv(DATA / "addressable_pool_size.csv")
    vint_rows = load_csv(DATA / "addressable_pool_vintage.csv")
    life_rows = load_csv(DATA / "addressable_pool_lifecycle.csv")

    fig, (ax_size, ax_vint, ax_life) = plt.subplots(
        1, 3, figsize=(17, 5.6), facecolor=BG,
        gridspec_kw={"width_ratios": [1.2, 1.0, 0.9]},
    )

    # ════════════════════════════════════════════════
    # Left — size distribution (account count, log scale on y)
    # ════════════════════════════════════════════════
    ax_size.set_facecolor(BG)
    pivot_count = {b: {"key": 0, "script": 0} for b in SIZE_BUCKETS}
    pivot_ada = {b: {"key": 0, "script": 0} for b in SIZE_BUCKETS}
    for r in size_rows:
        b = r["size_bucket"]
        c = r["credential_type"]
        if b in pivot_count:
            pivot_count[b][c] = int(r["account_count"])
            pivot_ada[b][c] = int(r["total_ada"])

    x = np.arange(len(SIZE_BUCKETS))
    w = 0.36
    counts_key = [pivot_count[b]["key"] for b in SIZE_BUCKETS]
    counts_scr = [pivot_count[b]["script"] for b in SIZE_BUCKETS]
    ax_size.bar(x - w/2, counts_key, w, color=KEY_C, label="key", edgecolor=BG, linewidth=0.5)
    ax_size.bar(x + w/2, counts_scr, w, color=SCRIPT_C, label="script", edgecolor=BG, linewidth=0.5)

    # ADA labels above bars where significant
    for xi, b in enumerate(SIZE_BUCKETS):
        ada_k = pivot_ada[b]["key"]
        if ada_k >= 1_000_000:
            ax_size.text(xi - w/2, counts_key[xi] * 1.08 if counts_key[xi] else 1.5,
                         f"{ada_k/1e6:.0f}M ADA", fontsize=7, color=DIM, ha="center")
        elif ada_k >= 1_000:
            ax_size.text(xi - w/2, counts_key[xi] * 1.08 if counts_key[xi] else 1.5,
                         f"{ada_k/1e3:.0f}k ADA", fontsize=7, color=DIM, ha="center")
        ada_s = pivot_ada[b]["script"]
        if ada_s >= 1_000_000:
            ax_size.text(xi + w/2, counts_scr[xi] * 1.08 if counts_scr[xi] else 1.5,
                         f"{ada_s/1e6:.0f}M ADA", fontsize=7, color=DIM, ha="center")

    ax_size.set_yscale("log")
    ax_size.set_xticks(x)
    ax_size.set_xticklabels(SIZE_LABELS, fontsize=9, color=DIM)
    ax_size.set_xlabel("Balance bucket (ADA per account)", fontsize=10, color=DIM)
    ax_size.set_ylabel("Account count (log scale)", fontsize=10, color=DIM)
    ax_size.set_title("Addressable pool — balance distribution",
                      fontsize=12, fontweight="medium", color=INK, pad=12)
    ax_size.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0, which="both")
    for sp in ["top", "right"]:
        ax_size.spines[sp].set_visible(False)
    ax_size.spines["bottom"].set_color(GRID)
    ax_size.spines["left"].set_color(GRID)
    ax_size.tick_params(colors=DIM, labelsize=9)
    leg = ax_size.legend(title="credential", loc="upper right", fontsize=9, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # ════════════════════════════════════════════════
    # Middle — registration vintage
    # ════════════════════════════════════════════════
    ax_vint.set_facecolor(BG)
    pivot_v = {v: {"key": 0, "script": 0} for v in VINTAGE_ORDER}
    for r in vint_rows:
        v = r["reg_vintage"]
        c = r["credential_type"]
        if v in pivot_v:
            pivot_v[v][c] = int(r["account_count"])

    x_v = np.arange(len(VINTAGE_ORDER))
    counts_kv = [pivot_v[v]["key"] for v in VINTAGE_ORDER]
    counts_sv = [pivot_v[v]["script"] for v in VINTAGE_ORDER]
    ax_vint.bar(x_v - w/2, counts_kv, w, color=KEY_C, edgecolor=BG, linewidth=0.5)
    ax_vint.bar(x_v + w/2, counts_sv, w, color=SCRIPT_C, edgecolor=BG, linewidth=0.5)

    for xi, v in enumerate(VINTAGE_ORDER):
        if counts_kv[xi] > 0:
            ax_vint.text(xi - w/2, counts_kv[xi] * 1.05,
                         f"{counts_kv[xi]:,}", fontsize=8, color=DIM, ha="center")
        if counts_sv[xi] > 0:
            ax_vint.text(xi + w/2, counts_sv[xi] * 1.05,
                         f"{counts_sv[xi]:,}", fontsize=8, color=DIM, ha="center")

    ax_vint.set_xticks(x_v)
    ax_vint.set_xticklabels(VINTAGE_LABELS, fontsize=9, color=DIM)
    ax_vint.set_xlabel("Registration vintage", fontsize=10, color=DIM)
    ax_vint.set_ylabel("Accounts registered", fontsize=10, color=DIM)
    ax_vint.set_title("Addressable pool — opt-in vintage",
                      fontsize=12, fontweight="medium", color=INK, pad=12)
    ax_vint.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_vint.spines[sp].set_visible(False)
    ax_vint.spines["bottom"].set_color(GRID)
    ax_vint.spines["left"].set_color(GRID)
    ax_vint.tick_params(colors=DIM, labelsize=9)

    # ════════════════════════════════════════════════
    # Right — lifecycle (donut)
    # ════════════════════════════════════════════════
    ax_life.set_facecolor(BG)
    sizes = []
    labels = []
    colours = []
    total_ada = 0
    for r in life_rows:
        cnt = int(r["account_count"])
        ada = int(r["total_ada"])
        c = r["credential_type"]
        lc = r["lifecycle"]
        col = KEY_C if c == "key" else SCRIPT_C
        if lc == "ex_delegator_undelegated":
            col = "#7FA0FF" if c == "key" else "#D69CF0"
        sizes.append(cnt)
        labels.append(
            f"{c.capitalize()} · "
            f"{'Ex-delegator' if lc.startswith('ex_') else 'Never delegated'}\n"
            f"{cnt:,} accts · "
            f"{ada/1e6:.0f}M ADA" if ada >= 1_000_000 else
            f"{c.capitalize()} · "
            f"{'Ex-delegator' if lc.startswith('ex_') else 'Never delegated'}\n"
            f"{cnt:,} accts · "
            f"{ada/1e3:.0f}k ADA"
        )
        colours.append(col)
        total_ada += ada

    wedges, _ = ax_life.pie(
        sizes, labels=None, colors=colours, startangle=90,
        wedgeprops=dict(width=0.40, edgecolor=BG, linewidth=1.2),
    )
    ax_life.text(0, 0.06, f"{sum(sizes):,}", ha="center", va="center",
                 fontsize=14, fontweight="bold", color=INK)
    ax_life.text(0, -0.10, "addressable\naccounts", ha="center", va="center",
                 fontsize=8.5, color=DIM)
    ax_life.set_title("Addressable pool — lifecycle",
                      fontsize=12, fontweight="medium", color=INK, pad=12)
    leg = ax_life.legend(wedges, labels, loc="center left",
                         bbox_to_anchor=(0.95, 0.5), fontsize=7.5, framealpha=0.95,
                         edgecolor=GRID, handlelength=1.0)
    leg.get_frame().set_linewidth(0.5)

    fig.tight_layout()
    out = FIG / "addressable_pool.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    build()
