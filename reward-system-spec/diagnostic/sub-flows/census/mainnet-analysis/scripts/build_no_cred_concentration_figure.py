#!/usr/bin/env python3
"""Build no-credential ADA concentration figure (CEN.5.4).

Two panels:
  (left)  Distribution of no-cred holders by size bucket — coloured by
          address type (enterprise_key, enterprise_script, byron, other).
  (right) Top-N concentration curve — share of total no-cred ADA captured
          as you walk down the ranked address list.

Reads:
  data/no_cred_size_distribution.csv — bucketed totals per type
  data/no_cred_top200.csv            — top-200 ranked no-cred holders

Writes:
  figures/no_cred_concentration.png
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

# IOG palette
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

TYPE_COLOUR = {
    "enterprise_script": INFARED,   # DeFi & contracts
    "enterprise_key":    DAWN,      # exchanges & custody
    "byron":             SOLAR,     # legacy
    "other":             GREY,
}
TYPE_LABEL = {
    "enterprise_script": "Enterprise script (addr1w)",
    "enterprise_key":    "Enterprise key (addr1v)",
    "byron":             "Byron legacy (Ae2/DdzFF)",
    "other":             "Other",
}

BUCKET_ORDER = [
    "00_under_1_ada", "01_1_to_10_ada", "02_10_to_100_ada",
    "03_100_to_1k_ada", "04_1k_to_10k_ada", "05_10k_to_100k_ada",
    "06_100k_to_1m_ada", "07_1m_to_10m_ada", "08_10m_to_100m_ada",
    "09_above_100m_ada",
]
BUCKET_LABELS = [
    "<1", "1–10", "10–100", "100–1k", "1k–10k",
    "10k–100k", "100k–1M", "1M–10M", "10M–100M", "≥100M",
]


def load_size():
    rows = []
    with (DATA / "no_cred_size_distribution.csv").open() as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_top():
    rows = []
    with (DATA / "no_cred_top200.csv").open() as f:
        for r in csv.DictReader(f):
            r["lovelace"] = int(r["lovelace"])
            r["ada"] = float(r["ada"])
            r["pct"] = float(r["pct_of_no_cred"])
            rows.append(r)
    return rows


def build():
    FIG.mkdir(parents=True, exist_ok=True)
    size_rows = load_size()
    top_rows = load_top()

    # ─── pivot size distribution: bucket × type → ADA ───
    pivot = {b: {t: 0 for t in TYPE_COLOUR} for b in BUCKET_ORDER}
    for r in size_rows:
        b = r["size_bucket"]
        t = r["address_type"]
        if b in pivot and t in pivot[b]:
            pivot[b][t] = int(r["total_ada"])

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(15, 6.2), facecolor=BG,
                                     gridspec_kw={"width_ratios": [1.15, 1]})

    # ════════════════════════════════════════════════════════
    # Left panel — stacked bars (ADA by bucket × type)
    # ════════════════════════════════════════════════════════
    ax_l.set_facecolor(BG)
    x = np.arange(len(BUCKET_ORDER))
    width = 0.7
    bottom = np.zeros(len(BUCKET_ORDER))
    types_in_order = ["enterprise_script", "enterprise_key", "byron", "other"]
    for t in types_in_order:
        vals = np.array([pivot[b][t] / 1e6 for b in BUCKET_ORDER])  # M ADA
        ax_l.bar(x, vals, width, bottom=bottom,
                 color=TYPE_COLOUR[t], label=TYPE_LABEL[t],
                 edgecolor=BG, linewidth=0.5)
        bottom += vals

    total_by_bucket = bottom
    grand_total = total_by_bucket.sum()  # M ADA
    for xi, total in enumerate(total_by_bucket):
        if total > grand_total * 0.012:
            ax_l.text(xi, total + grand_total * 0.012,
                      f"{total/1000:.2f}B" if total >= 1000 else f"{total:.0f}M",
                      ha="center", fontsize=8, color=DIM)

    ax_l.set_xticks(x)
    ax_l.set_xticklabels(BUCKET_LABELS, fontsize=9, color=DIM)
    ax_l.set_xlabel("Holder size bucket (ADA)", fontsize=10, color=DIM)
    ax_l.set_ylabel("Total ADA (millions)", fontsize=10, color=DIM)
    ax_l.set_title("No-Credential ADA — distribution by holder size",
                   fontsize=12, fontweight="medium", color=INK, pad=12)
    ax_l.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_l.spines[sp].set_visible(False)
    ax_l.spines["bottom"].set_color(GRID)
    ax_l.spines["left"].set_color(GRID)
    ax_l.tick_params(colors=DIM, labelsize=9)
    ax_l.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1000:.0f}B" if v >= 1000 else f"{v:.0f}M"))
    leg = ax_l.legend(loc="upper left", fontsize=8.5, framealpha=0.95, edgecolor=GRID)
    leg.get_frame().set_linewidth(0.5)

    # ════════════════════════════════════════════════════════
    # Right panel — Top-N cumulative concentration
    # ════════════════════════════════════════════════════════
    ax_r.set_facecolor(BG)
    ranks = [r["rank"] for r in top_rows]
    cum = np.cumsum([r["pct"] for r in top_rows])
    ax_r.fill_between(ranks, cum, color=INFARED, alpha=0.18)
    ax_r.plot(ranks, cum, color=INFARED, lw=2)

    # Type-coloured dots for the top 30
    for r in top_rows[:30]:
        c = TYPE_COLOUR.get(r["address_type"], GREY)
        ax_r.scatter(int(r["rank"]), float(cum[int(r["rank"])-1]),
                     s=18, color=c, edgecolor=BG, linewidth=0.6, zorder=4)

    # Annotations at key ranks
    for rk in [1, 3, 10, 50, 100, 200]:
        if rk <= len(cum):
            v = cum[rk-1]
            ax_r.annotate(
                f"top-{rk}: {v:.1f}%",
                xy=(rk, v), xytext=(rk + 6, v - 4),
                fontsize=8.5, color=DIM,
                arrowprops=dict(arrowstyle="-", color=GRID, lw=0.7),
            )

    ax_r.set_xlim(0, 210)
    ax_r.set_ylim(0, max(cum) * 1.08 if len(cum) else 100)
    ax_r.set_xlabel("Address rank (no-credential holders)", fontsize=10, color=DIM)
    ax_r.set_ylabel("Cumulative share of no-cred ADA (%)", fontsize=10, color=DIM)
    ax_r.set_title("Top-N concentration — who holds the no-credential ADA",
                   fontsize=12, fontweight="medium", color=INK, pad=12)
    ax_r.grid(color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_r.spines[sp].set_visible(False)
    ax_r.spines["bottom"].set_color(GRID)
    ax_r.spines["left"].set_color(GRID)
    ax_r.tick_params(colors=DIM, labelsize=9)
    ax_r.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))

    fig.tight_layout()
    out = FIG / "no_cred_concentration.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    build()
