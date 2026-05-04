#!/usr/bin/env python3
"""Build the §5.6 non-participant-levers figure (CEN.5.6).

A single horizontal stacked bar showing where the 14.4 B unstaked ADA
sits — sized proportionally, colour-coded by the one lever that can
reach each sub-population. The dominance of the unregistered-wallet
segment vs the tiny reward-design-reachable sliver is the headline.

Inputs: hard-coded from §5.2 / §5.4 / §5.5 (the values are stable —
this figure is a synthesis, not a re-aggregation).

Writes: figures/non_participant_levers.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

REPORT = Path(__file__).resolve().parent.parent
FIG = REPORT / "figures"

# IOG-aligned palette
BG       = "#FFFFFF"
INK      = "#1A1A1A"
DIM      = "#666666"
GRID     = "#EBEBEB"

# Sub-population colours (semantic — each = one reach mechanism)
GREY     = "#B0B0B0"   # unregistered wallets — user action
AMBER    = "#FFBA36"   # legacy / partly lost
CORAL    = "#FF532C"   # custody — protocol change
PURPLE   = "#A700FF"   # DeFi contract locks
GREEN    = "#00875A"   # reward-design-reachable

# Sub-populations: (label, ada_b, pct, colour, lever_caption)
SUBPOPS = [
    ("Wallets · staking key never registered", 11.800, 82.2, GREY,   "User action — a single registration tx"),
    ("Pre-staking legacy addresses",            1.320,  9.2, AMBER,  "Legacy migration · part permanently lost"),
    ("Exchange & institutional custody",        1.040,  7.2, CORAL,  "Protocol change — let custody addresses stake"),
    ("DeFi contract locks",                     0.180,  1.25, PURPLE, "Contract upgrade — 89 % is one contract"),
    ("Active non-stakers · key registered",     0.0225, 0.16, GREEN,  "Reward design — the only direct lever"),
]
TOTAL_B = sum(s[1] for s in SUBPOPS)  # ~14.36 B

# Bar geometry — minimum widths for tiny segments so they read on the bar
BAR_TOTAL_W = 660  # pixels of horizontal bar
MIN_W = {3: 18, 4: 20}   # indices 3 (purple) and 4 (green) get minimum widths
BIG_INDICES = [0, 1, 2]


def compute_widths():
    used_min = sum(MIN_W.values())
    big_total_b = sum(SUBPOPS[i][1] for i in BIG_INDICES)
    big_share = BAR_TOTAL_W - used_min
    widths = [0.0] * len(SUBPOPS)
    for i in BIG_INDICES:
        widths[i] = SUBPOPS[i][1] / big_total_b * big_share
    for i, w in MIN_W.items():
        widths[i] = float(w)
    return widths


def build():
    FIG.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(11.5, 6.4), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 600)
    ax.axis("off")

    # ── Title ──
    ax.text(40, 565, "Where the 14.4 B of unstaked ADA sits",
            fontsize=18, fontweight="medium", color=INK)
    ax.text(40, 535,
            "39.8 % of supply, by sub-population and what lever can reach each",
            fontsize=12, color=DIM)

    # ── Stacked bar ──
    widths = compute_widths()
    bar_y = 430
    bar_h = 60
    x = 40
    bar_left = x
    rects = []
    for (label, ada_b, pct, colour, _), w in zip(SUBPOPS, widths):
        rect = mpatches.FancyBboxPatch(
            (x, bar_y), w, bar_h,
            boxstyle="round,pad=0,rounding_size=4",
            linewidth=0, facecolor=colour, edgecolor="none",
        )
        ax.add_patch(rect)
        rects.append((x, w, label, ada_b, pct, colour))
        x += w + 2  # 2px hairline gap

    # ── In-bar labels for the three big segments ──
    for i in BIG_INDICES:
        seg_x, w, label, ada_b, pct, _ = rects[i]
        cx = seg_x + w / 2
        if i == 0:
            ada_str = f"{ada_b:.1f} B"
            ax.text(seg_x + 18, bar_y + bar_h - 22, ada_str,
                    fontsize=18, fontweight="medium", color=INK, ha="left")
            ax.text(seg_x + 18, bar_y + 12, f"{pct:.1f} % of unstaked",
                    fontsize=11, color=INK, alpha=0.75, ha="left")
        else:
            ax.text(cx, bar_y + bar_h - 22, f"{ada_b:.2f} B",
                    fontsize=12, fontweight="medium", color=INK, ha="center")
            ax.text(cx, bar_y + 12, f"{pct:.1f} %",
                    fontsize=10, color=INK, alpha=0.75, ha="center")

    # ── Leader lines + callouts for the two tiny segments ──
    for i in (3, 4):
        seg_x, w, label, ada_b, pct, _ = rects[i]
        cx = seg_x + w / 2
        # callout positions
        callout_y = bar_y - 50
        if i == 3:
            cx_label = cx - 100
        else:
            cx_label = cx
        ax.plot([cx, cx, cx_label], [bar_y, bar_y - 18, callout_y],
                color=GRID, linewidth=0.7, solid_capstyle="round")
        ada_str = f"{ada_b * 1000:.1f} M" if ada_b < 1 else f"{ada_b:.2f} B"
        ax.text(cx_label, callout_y - 4, label.split(" · ")[0],
                fontsize=10, color=DIM, ha="center")
        ax.text(cx_label, callout_y - 22, f"{ada_str} · {pct:.2f} %",
                fontsize=12, fontweight="medium", color=INK, ha="center")

    # ── Lever-mechanism table below ──
    table_y = 305
    ax.text(40, table_y + 20,
            "Each sub-population responds to a different lever",
            fontsize=12, color=DIM)

    row_h = 36
    for idx, (label, ada_b, pct, colour, lever) in enumerate(SUBPOPS):
        ry = table_y - idx * row_h
        # color swatch
        ax.add_patch(mpatches.FancyBboxPatch(
            (45, ry - 10), 16, 16, boxstyle="round,pad=0,rounding_size=3",
            linewidth=0, facecolor=colour, edgecolor="none",
        ))
        # sub-population name
        ax.text(72, ry, label, fontsize=12, color=INK)
        # ADA + pct (right-aligned)
        ada_str = f"{ada_b * 1000:.1f} M" if ada_b < 1 else f"{ada_b:.2f} B"
        ax.text(540, ry, f"{ada_str}  ·  {pct:.2f} %",
                fontsize=12, fontweight="medium", color=INK, ha="right")
        # lever caption
        ax.text(560, ry, lever, fontsize=11, color=DIM)

    # ── Bottom punchline (subtle) ──
    ax.add_patch(mpatches.FancyBboxPatch(
        (40, 32), 920, 50,
        boxstyle="round,pad=0,rounding_size=6",
        linewidth=0, facecolor=GREEN, alpha=0.10,
    ))
    ax.text(60, 64, "Only 0.16 % of the unstaked supply is reachable by reward design alone.",
            fontsize=12.5, fontweight="medium", color=GREEN)
    ax.text(60, 44,
            "Everything else needs user action, a protocol change, a contract upgrade — or has been lost since the Byron era.",
            fontsize=11, color=DIM)

    out = FIG / "non_participant_levers.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG, pad_inches=0.05)
    plt.close(fig)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    build()
