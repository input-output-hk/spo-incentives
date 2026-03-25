#!/usr/bin/env python3
"""
Distribution Efficiency — Summary Table (visual PNG).

Renders the §2 waterfall as a structured table with aggregate subtotals,
matching the hierarchical structure: Pools pot → Staked pot → Eligible pot → Distributed.

Outputs: figures/distribution_summary_table.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──
BG              = "#FFFFFF"
INK             = "#1A1A1A"
DIM             = "#666666"
LIGHT_GREY      = "#F5F5F5"
GRID            = "#E0E0E0"
INFARED         = "#E52321"
DAWN            = "#EC641D"
DELIVERED_GREEN = "#00875A"
SOLAR_AMBER     = "#FFBA36"
GREY_MED        = "#999999"
ULTRAVIOLET     = "#A700FF"
CONFISCATED     = "#B71C1C"

# Aggregate row background
AGG_BG          = "#F0F0F0"
AGG_BORDER      = "#CCCCCC"

# Loss row accent colours (left stripe)
ACCENT_PARTICIPATION = SOLAR_AMBER
ACCENT_PLEDGE        = CONFISCATED
ACCENT_BONUS         = INFARED
ACCENT_PERF          = GREY_MED
ACCENT_OVERSAT       = ULTRAVIOLET


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with (DATA_DIR / "reward_anatomy.json").open() as f:
        a = json.load(f)

    pot   = a["R_pools_pot_ada"]
    dist  = a["distributed_ada"]
    epoch = a["epoch"]

    lam_min = a["lambda_min"]
    lam_max = a["lambda_max"]

    base_delivered  = a["sum_base_over_k_pct"] / 100 * pot
    bonus_delivered = a["sum_bonus_over_k_pct"] / 100 * pot
    E_at_pbar1      = a["sum_E_over_k_pct"] / 100 * pot
    perf_loss       = E_at_pbar1 - dist

    base_budget  = lam_min * pot
    bonus_budget = lam_max * pot

    participation_gap  = base_budget - base_delivered - 0.33e6
    pledge_confiscated = 0.32e6
    bonus_unused       = bonus_budget - bonus_delivered
    performance        = perf_loss
    oversaturation     = a.get("base_lost_to_cap_pct", 0) / 100 * pot

    staked_pot  = pot - participation_gap
    eligible_pot = staked_pot - pledge_confiscated
    returned     = bonus_unused + performance + oversaturation

    # ── Table rows ──
    # type: "agg" = aggregate subtotal, "loss" = deduction, "result" = final
    rows = [
        {"type": "agg",    "label": "Pools pot",            "ada": pot,                "pct": 100.0,                      "desc": "Total budget entering the reward formula",          "accent": DELIVERED_GREEN},
        {"type": "loss",   "label": "Participation gap",    "ada": -participation_gap,  "pct": -participation_gap/pot*100, "desc": "ADA not staked — no pool claims this share",        "accent": ACCENT_PARTICIPATION},
        {"type": "agg",    "label": "= Staked pot",         "ada": staked_pot,          "pct": staked_pot/pot*100,         "desc": "Budget claimable by delegated pools",               "accent": None},
        {"type": "loss",   "label": "Pledge-not-met",       "ada": -pledge_confiscated, "pct": -pledge_confiscated/pot*100, "desc": "692 pools produce blocks but receive zero",        "accent": ACCENT_PLEDGE},
        {"type": "agg",    "label": "= Eligible pot",       "ada": eligible_pot,        "pct": eligible_pot/pot*100,       "desc": "Budget entering the reward formula proper",        "accent": None},
        {"type": "loss",   "label": "Bonus budget unused",  "ada": -bonus_unused,       "pct": -bonus_unused/pot*100,      "desc": "Pledge-incentive budget 95.6% uncaptured",         "accent": ACCENT_BONUS},
        {"type": "loss",   "label": "Performance",          "ada": -performance,        "pct": -performance/pot*100,       "desc": "Missed blocks by eligible pools",                   "accent": ACCENT_PERF},
        {"type": "loss",   "label": "Oversaturation",       "ada": -oversaturation,     "pct": -oversaturation/pot*100,    "desc": "7 pools above saturation cap",                     "accent": ACCENT_OVERSAT},
        {"type": "result", "label": "= Distributed",        "ada": dist,                "pct": dist/pot*100,               "desc": "What reaches operators and delegators",            "accent": DELIVERED_GREEN},
    ]

    # ── Figure setup ──
    n_rows = len(rows)
    row_h = 0.55
    header_h = 0.65
    fig_h = header_h + n_rows * row_h + 0.6
    fig_w = 14.5

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    # Column positions (x)
    col_label  = 0.7
    col_ada    = 6.8
    col_pct    = 8.8
    col_bar    = 9.8
    col_desc   = 12.8
    bar_max_w  = 2.6

    # ── Title ──
    ax.text(fig_w / 2, fig_h - 0.25, f"Distribution Efficiency — Summary  (Epoch {epoch})",
            ha="center", va="top", fontsize=14, fontweight="bold", color=INK,
            fontfamily="sans-serif")

    # ── Header row ──
    y_header = fig_h - header_h
    ax.fill_between([0, fig_w], y_header, y_header + 0.45, color="#E8E8E8", zorder=1)
    hdr_y = y_header + 0.22
    ax.text(col_label, hdr_y, "COMPONENT",    ha="left",   va="center", fontsize=8.5, fontweight="bold", color=DIM, fontfamily="sans-serif")
    ax.text(col_ada,   hdr_y, "ADA / EPOCH",  ha="right",  va="center", fontsize=8.5, fontweight="bold", color=DIM, fontfamily="sans-serif")
    ax.text(col_pct,   hdr_y, "% POT",        ha="right",  va="center", fontsize=8.5, fontweight="bold", color=DIM, fontfamily="sans-serif")
    ax.text((col_bar + col_bar + bar_max_w) / 2, hdr_y, "",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=DIM)
    ax.text(col_desc,  hdr_y, "WHAT HAPPENS", ha="left",   va="center", fontsize=8.5, fontweight="bold", color=DIM, fontfamily="sans-serif")

    # ── Draw rows ──
    for i, row in enumerate(rows):
        y_bot = y_header - (i + 1) * row_h
        y_mid = y_bot + row_h / 2

        # Background stripe for aggregate / result rows
        if row["type"] in ("agg", "result"):
            ax.fill_between([0, fig_w], y_bot, y_bot + row_h, color=AGG_BG, zorder=1)
            ax.plot([0, fig_w], [y_bot, y_bot], color=AGG_BORDER, linewidth=0.5, zorder=2)
            ax.plot([0, fig_w], [y_bot + row_h, y_bot + row_h], color=AGG_BORDER, linewidth=0.5, zorder=2)
        else:
            # Light bottom border for loss rows
            ax.plot([0.5, fig_w - 0.5], [y_bot, y_bot], color="#ECECEC", linewidth=0.4, zorder=2)

        # Left accent stripe for loss rows
        if row["type"] == "loss" and row["accent"]:
            stripe_w = 0.12
            ax.fill_between([0.35, 0.35 + stripe_w], y_bot + 0.06, y_bot + row_h - 0.06,
                            color=row["accent"], zorder=3)

        # Label
        is_bold = row["type"] in ("agg", "result")
        indent = col_label if row["type"] != "loss" else col_label + 0.4
        ax.text(indent, y_mid, row["label"],
                ha="left", va="center",
                fontsize=10 if is_bold else 9.5,
                fontweight="bold" if is_bold else "normal",
                color=INK if is_bold else "#333333",
                fontfamily="sans-serif",
                zorder=4)

        # ADA value
        ada_val = row["ada"]
        if ada_val < 0:
            ada_str = f"−{abs(ada_val)/1e6:.2f}M"
        else:
            ada_str = f"{ada_val/1e6:.2f}M"
        ax.text(col_ada, y_mid, ada_str,
                ha="right", va="center",
                fontsize=10 if is_bold else 9.5,
                fontweight="bold" if is_bold else "normal",
                color=INK if is_bold else "#333333",
                fontfamily="monospace",
                zorder=4)

        # Percentage
        pct_val = row["pct"]
        if pct_val < 0:
            pct_str = f"−{abs(pct_val):.1f}%"
        else:
            pct_str = f"{pct_val:.1f}%"
        ax.text(col_pct, y_mid, pct_str,
                ha="right", va="center",
                fontsize=10 if is_bold else 9.5,
                fontweight="bold" if is_bold else "normal",
                color=INK if is_bold else "#333333",
                fontfamily="monospace",
                zorder=4)

        # Horizontal bar
        bar_w = abs(pct_val) / 100.0 * bar_max_w
        bar_color = row["accent"] if row["accent"] else "#888888"
        if row["type"] == "result":
            bar_color = DELIVERED_GREEN
        bar_y = y_mid - 0.09
        bar_h_px = 0.18
        alpha = 0.85 if row["type"] == "loss" else 0.92
        rect = FancyBboxPatch((col_bar, bar_y), bar_w, bar_h_px,
                               boxstyle="round,pad=0.02",
                               facecolor=bar_color, alpha=alpha,
                               edgecolor="none", zorder=3)
        ax.add_patch(rect)

        # Description
        ax.text(col_desc, y_mid, row["desc"],
                ha="left", va="center",
                fontsize=8.5,
                color=DIM,
                fontstyle="italic",
                fontfamily="sans-serif",
                zorder=4)

    # Bottom line
    y_final = y_header - n_rows * row_h
    ax.plot([0, fig_w], [y_final, y_final], color=AGG_BORDER, linewidth=1, zorder=2)

    # Epoch footnote
    ax.text(fig_w / 2, 0.15,
            f"Source: mainnet epoch {epoch}  •  Pools pot = monetary expansion × (1 − τ)",
            ha="center", va="bottom", fontsize=7.5, color="#AAAAAA", fontfamily="sans-serif")

    fig.tight_layout(pad=0.3)
    out = FIG_DIR / "distribution_summary_table.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"✓ Saved {out}")


if __name__ == "__main__":
    main()
