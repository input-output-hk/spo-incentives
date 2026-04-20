#!/usr/bin/env python3
"""Build dormancy vintage figure from definitive epoch 623 data."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPORT = Path(__file__).resolve().parent.parent
DATA   = REPORT / "data"
FIG    = REPORT / "figures"

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

VINTAGE_COLOURS = {
    "null_vintage":     GREY,
    "pre_shelley":      INFARED,
    "shelley_allegra":  SOLAR,
    "mary":             DAWN,
    "alonzo_early":     COBALT,
    "alonzo_babbage":   ELEC,
    "early_conway":     ULTRA,
    "late_conway":      ACID,
}

VINTAGE_LABELS = {
    "null_vintage":     "Byron-era (null epoch)",
    "pre_shelley":      "Pre-Shelley (ep 0\u2013207)\nDormant / lost",
    "shelley_allegra":  "Shelley / Allegra (ep 208\u2013250)",
    "mary":             "Mary (ep 251\u2013299)",
    "alonzo_early":     "Early Alonzo (ep 300\u2013349)",
    "alonzo_babbage":   "Alonzo + Babbage (ep 350\u2013449)",
    "early_conway":     "Early Conway (ep 450\u2013549)",
    "late_conway":      "Late Conway (ep 550\u2013623)",
}

ORDER = ["null_vintage", "pre_shelley", "shelley_allegra", "mary",
         "alonzo_early", "alonzo_babbage", "early_conway", "late_conway"]

def main():
    rows = {}
    with (DATA / "dormancy_vintage_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows[r["vintage"]] = r

    ordered = [rows[k] for k in ORDER if k in rows]
    labels = [VINTAGE_LABELS.get(r["vintage"], r["vintage"]) for r in ordered]
    values_ada = [int(r["total_lovelace"]) / 1e6 for r in ordered]
    values_b = [v / 1e9 for v in values_ada]
    colors = [VINTAGE_COLOURS.get(r["vintage"], GREY) for r in ordered]
    total = sum(values_ada)

    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor=BG)
    ax.set_facecolor(BG)

    bars = ax.barh(labels, values_b, color=colors, alpha=0.85,
                   edgecolor=BG, linewidth=0.8, height=0.6)

    for bar, val_b, val_ada in zip(bars, values_b, values_ada):
        pct = val_ada / total * 100
        if val_b > 0.02:
            label = f"{val_ada/1e6:.0f}M ADA ({pct:.1f}%)"
        else:
            label = f"{val_ada/1e6:.1f}M ADA ({pct:.1f}%)"
        ax.text(val_b + 0.01, bar.get_y() + bar.get_height() / 2,
                label, fontsize=9, color=DIM, va="center")

    ax.set_xlabel("ADA (billions)", fontsize=10, color=DIM)
    ax.set_title("Dormancy Vintage \u2014 No-Credential UTxOs at Epoch 623",
                 fontsize=13, fontweight="medium", color=INK, pad=16)
    ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=9)
    ax.set_xlim(0, max(values_b) * 1.45)

    dormant_ada = sum(v for r, v in zip(ordered, values_ada)
                      if r["vintage"] in ("pre_shelley", "null_vintage"))
    dormant_pct = dormant_ada / total * 100
    ax.annotate(
        f"Probably dormant / lost:\n{dormant_ada/1e6:.0f}M ADA ({dormant_pct:.1f}%)",
        xy=(0.62, 1.3), xytext=(0.85, 0.5),
        fontsize=9, color=INFARED, fontweight="medium",
        arrowprops=dict(arrowstyle="->", color=INFARED, lw=1),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5", ec=INFARED, lw=0.8),
    )

    fig.tight_layout()
    out = FIG / "dormancy_vintage_623.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")

if __name__ == "__main__":
    main()
