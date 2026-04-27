#!/usr/bin/env python3
"""
Build the non-participant decomposition figure from Koios + Instance A data.

Reads:  data/non_participant_decomposition_623.csv
Writes: figures/non_participant_decomposition.png

Two-panel figure:
  (left)  Donut chart — full circulation breakdown by stake-credential category
  (right) Horizontal bar — zoom on the non-participant portion
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
REPORT = Path(__file__).resolve().parent.parent
DATA   = REPORT / "data"
FIG    = REPORT / "figures"

# ── IOG brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
GRID            = "#EBEBEB"
INFARED         = "#E52321"
DELIVERED_GREEN = "#00875A"
COBALT_PULSE    = "#2C4FFA"
DAWN            = "#EC641D"
SOLAR_AMBER     = "#FFBA36"
ELECTRIC_BLUE   = "#16E9D8"
ULTRAVIOLET     = "#A700FF"
ULTRAVIOLET_DEEP = "#8421A2"
GREY_LIGHT      = "#B0B0B0"
ACID_GREEN      = "#06FF89"

CATEGORY_META = {
    "delegated":                 ("Delegated (key)",           DELIVERED_GREEN),
    "delegated_key":             ("Delegated — key",           DELIVERED_GREEN),
    "delegated_script":          ("Delegated — script",        ELECTRIC_BLUE),
    "registered_not_delegated":  ("Registered, not delegated", COBALT_PULSE),
    "registered_not_delegated_key":    ("Reg. not del. — key",    COBALT_PULSE),
    "registered_not_delegated_script": ("Reg. not del. — script", ULTRAVIOLET),
    "deposits":                  ("Deposits",                  GREY_LIGHT),
    "no_stake_credential":       ("No stake credential",       DAWN),
}


def load_decomposition():
    rows = []
    with (DATA / "non_participant_decomposition_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def build_figure(rows):
    FIG.mkdir(parents=True, exist_ok=True)
    fig, (ax_donut, ax_bar) = plt.subplots(
        1, 2, figsize=(16, 7.5), facecolor=BG,
        gridspec_kw={"width_ratios": [1.1, 1]},
    )

    # ════════════════════════════════════════════════════════
    # Left panel — donut of full circulation
    # ════════════════════════════════════════════════════════
    ax_donut.set_facecolor(BG)

    # Merge delegated key+script for the donut (keep it readable)
    donut_items = []
    delegated_total = 0
    for r in rows:
        cat = r["category"]
        lv = int(r["total_lovelace"])
        if cat.startswith("delegated"):
            delegated_total += lv
        else:
            meta = CATEGORY_META.get(cat, (cat, GREY_LIGHT))
            donut_items.append((meta[0], lv, meta[1]))
    donut_items.insert(0, ("Delegated (staked)", delegated_total, DELIVERED_GREEN))

    labels = [d[0] for d in donut_items]
    sizes  = [d[1] / 1e6 for d in donut_items]  # ADA
    colors = [d[2] for d in donut_items]
    total  = sum(sizes)

    wedges, texts, autotexts = ax_donut.pie(
        sizes, labels=None, colors=colors,
        autopct=lambda pct: f"{pct:.1f}%" if pct > 1 else "",
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.42, edgecolor=BG, linewidth=1.5),
        textprops=dict(fontsize=8.5, color=INK),
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color(DIM)

    # Centre text
    ax_donut.text(0, 0.06, f"{total/1e9:.1f}B ADA", ha="center", va="center",
                  fontsize=16, fontweight="bold", color=INK)
    ax_donut.text(0, -0.08, "circulation", ha="center", va="center",
                  fontsize=10, color=DIM)

    # Legend
    legend_labels = []
    for lab, sz, _ in donut_items:
        pct = sz / total * 100
        if sz > 1e9:
            legend_labels.append(f"{lab}\n{sz/1e9:.2f}B ADA ({pct:.1f}%)")
        elif sz > 1e6:
            legend_labels.append(f"{lab}\n{sz/1e6:.1f}M ADA ({pct:.2f}%)")
        else:
            legend_labels.append(f"{lab}\n{sz/1e3:.0f}K ADA ({pct:.3f}%)")

    leg = ax_donut.legend(
        wedges, legend_labels, loc="center left",
        bbox_to_anchor=(-0.42, 0.5), fontsize=8,
        framealpha=0.95, edgecolor=GRID, handlelength=1.2,
    )
    leg.get_frame().set_linewidth(0.5)

    ax_donut.set_title("Circulation by Stake-Credential Category",
                       fontsize=12, fontweight="medium", color=INK, pad=18)

    # ════════════════════════════════════════════════════════
    # Right panel — zoom on non-participant breakdown
    # ════════════════════════════════════════════════════════
    ax_bar.set_facecolor(BG)

    # All rows except delegated
    bar_items = []
    for r in rows:
        cat = r["category"]
        cred = r.get("credential_type", "")
        lv = int(r["total_lovelace"])
        ada = lv / 1e6

        if cat == "delegated":
            if cred == "script":
                bar_items.append(("Delegated — script", ada, ELECTRIC_BLUE))
            continue  # skip delegated key from bar chart
        elif cat == "registered_not_delegated":
            if cred == "key":
                bar_items.append(("Registered, not del. — key\n(23,074 accounts)", ada, COBALT_PULSE))
            else:
                bar_items.append(("Registered, not del. — script\n(1,102 accounts)", ada, ULTRAVIOLET))
        elif cat == "deposits":
            bar_items.append(("Deposits (stake/DRep/gov)", ada, GREY_LIGHT))
        elif cat == "no_stake_credential":
            bar_items.append(("No stake credential\n(enterprise + unregistered + script)", ada, DAWN))

    # Sort by value
    bar_items.sort(key=lambda x: x[1])

    bar_labels = [b[0] for b in bar_items]
    bar_values = [b[1] / 1e9 for b in bar_items]  # billions
    bar_colors = [b[2] for b in bar_items]

    bars = ax_bar.barh(bar_labels, bar_values, color=bar_colors, alpha=0.8,
                       edgecolor=BG, linewidth=0.8, height=0.6)

    for bar, val, raw in zip(bars, bar_values, [b[1] for b in bar_items]):
        if val > 0.5:
            ax_bar.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
                        f"{val:.2f}B", fontsize=9, color=DIM, va="center")
        else:
            ax_bar.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                        f"{raw/1e6:.1f}M", fontsize=8, color=DIM, va="center")

    ax_bar.set_xlabel("ADA (billions)", fontsize=10, color=DIM)
    ax_bar.set_title("Non-Participant Breakdown (excl. delegated key)",
                     fontsize=12, fontweight="medium", color=INK, pad=18)
    ax_bar.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7, zorder=0)
    for sp in ["top", "right"]:
        ax_bar.spines[sp].set_visible(False)
    ax_bar.spines["bottom"].set_color(GRID)
    ax_bar.spines["left"].set_color(GRID)
    ax_bar.tick_params(colors=DIM, labelsize=9)
    ax_bar.set_xlim(0, max(bar_values) * 1.25)

    # Annotation: addressable pool
    addressable_ada = sum(b[1] for b in bar_items
                          if "Registered" in b[0]) / 1e9
    ax_bar.annotate(
        f"Addressable pool:\n{addressable_ada*1e3:.0f}M ADA (0.37%)",
        xy=(addressable_ada, 1.5), xytext=(2, 2.5),
        fontsize=8.5, color=INFARED, fontweight="medium",
        arrowprops=dict(arrowstyle="->", color=INFARED, lw=1),
        bbox=dict(boxstyle="round,pad=0.3", fc="#FFF5F5", ec=INFARED, lw=0.8),
    )

    fig.suptitle(
        "Non-Participant Decomposition — Epoch 623",
        fontsize=14, fontweight="medium", color=INK, y=1.01,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out = FIG / "non_participant_decomposition.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {out}")


def main():
    rows = load_decomposition()
    build_figure(rows)


if __name__ == "__main__":
    main()
