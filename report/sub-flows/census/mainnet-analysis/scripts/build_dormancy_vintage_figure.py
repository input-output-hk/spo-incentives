#!/usr/bin/env python3
"""
Build the dormancy vintage figure from Instance B epoch 376 data.

Reads:  dormancy_vintage_376.csv
Writes: figures/dormancy_vintage_376.png

Single-panel horizontal bar chart showing UTxO value by creation-era vintage.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Paths ──
REPORT = Path(__file__).resolve().parent.parent
DATA   = REPORT / "data"
FIG    = REPORT / "figures"

# ── IOG brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
INFARED         = "#E52321"
DAWN            = "#EC641D"
SOLAR_AMBER     = "#FFBA36"
COBALT_PULSE    = "#2C4FFA"
ELECTRIC_BLUE   = "#16E9D8"
ULTRAVIOLET     = "#A700FF"
ACID_GREEN      = "#06FF89"
GREY_LIGHT      = "#B0B0B0"

VINTAGE_COLOURS = {
    "pre_shelley":      INFARED,
    "shelley_allegra":  SOLAR_AMBER,
    "mary":             DAWN,
    "alonzo_early":     COBALT_PULSE,
    "alonzo_babbage":   ELECTRIC_BLUE,
    "null_vintage":     GREY_LIGHT,
}

VINTAGE_LABELS = {
    "pre_shelley":      "Pre-Shelley (ep 0–207)\nDormant / lost",
    "shelley_allegra":  "Shelley / Allegra (ep 208–250)",
    "mary":             "Mary (ep 251–299)",
    "alonzo_early":     "Early Alonzo (ep 300–349)",
    "alonzo_babbage":   "Late Alonzo + Babbage (ep 350–376)",
    "null_vintage":     "Byron-era (null epoch)",
}


def load_data():
    rows = []
    with (DATA / "dormancy_vintage_376.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def build_figure(rows):
    FIG.mkdir(parents=True, exist_ok=True)

    # Order: pre-Shelley at top, then chronological
    order = ["null_vintage", "pre_shelley", "shelley_allegra", "mary", "alonzo_early", "alonzo_babbage"]
    ordered = []
    for key in order:
        for r in rows:
            if r["vintage"] == key:
                ordered.append(r)
                break

    labels = [VINTAGE_LABELS.get(r["vintage"], r["vintage"]) for r in ordered]
    values_ada = [int(r["total_lovelace"]) / 1e6 for r in ordered]  # ADA
    values_b = [v / 1e9 for v in values_ada]  # billions
    colors = [VINTAGE_COLOURS.get(r["vintage"], GREY_LIGHT) for r in ordered]
    total = sum(values_ada)

    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor=BG)
    ax.set_facecolor(BG)

    bars = ax.barh(labels, values_b, color=colors, alpha=0.85,
                   edgecolor=BG, linewidth=0.8, height=0.6)

    for bar, val_b, val_ada in zip(bars, values_b, values_ada):
        pct = val_ada / total * 100
        if val_b > 0.1:
            label = f"{val_ada/1e6:.0f}M ADA ({pct:.1f}%)"
        else:
            label = f"{val_ada/1e6:.1f}M ADA ({pct:.1f}%)"
        ax.text(val_b + 0.02, bar.get_y() + bar.get_height() / 2,
                label, fontsize=9, color=DIM, va="center")

    ax.set_xlabel("ADA (billions)", fontsize=10, color=DIM)
    ax.set_title("Dormancy Vintage — No-Credential UTxOs at Epoch 376",
                 fontsize=13, fontweight="medium", color=INK, pad=16)
    ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    ax.set_xlim(0, max(values_b) * 1.45)

    # Annotate dormant fraction
    dormant_ada = sum(v for r, v in zip(ordered, values_ada)
                      if r["vintage"] in ("pre_shelley", "null_vintage"))
    dormant_pct = dormant_ada / total * 100
    ax.annotate(
        f"Probably dormant / lost:\n{dormant_ada/1e6:.0f}M ADA ({dormant_pct:.1f}%)",
        xy=(0.85, 1.3), xytext=(1.35, 0.5),
        fontsize=9, color=INFARED, fontweight="medium",
        arrowprops=dict(arrowstyle="->", color=INFARED, lw=1),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5", ec=INFARED, lw=0.8),
    )

    fig.tight_layout()
    out = FIG / "dormancy_vintage_376.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")


def main():
    rows = load_data()
    build_figure(rows)


if __name__ == "__main__":
    main()
