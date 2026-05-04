#!/usr/bin/env python3
"""
Population funnel — Raw → Productive at the 3M production threshold.

Single-stage filter (was Raw → Productive(≥1M) → Viable(≥3M); the new
canonical framing collapses both into a single ≥3M cut, the 95%-block-
probability bar from POL.O3.F1).

Outputs: figures/population_funnel.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

REPORT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = REPORT_DIR / "figures"

# IOG brand
BG = "#FFFFFF"
INK = "#1A1A1A"
DIM = "#666666"
INFARED = "#E52321"
ACID_GREEN = "#00B35F"
COBALT = "#2C4FFA"

LBL_FONT = 11
NUM_FONT = 30
SUB_FONT = 9


def boxed(ax, x, y, w, h, color, n, title, sub):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor=color, edgecolor="none", alpha=0.92, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2 + 0.04, n, ha="center", va="center",
            fontsize=NUM_FONT, fontweight="bold", color="white", zorder=3)
    ax.text(x + w / 2, y - 0.08, title, ha="center", va="top",
            fontsize=LBL_FONT, fontweight="bold", color=INK, zorder=3)
    ax.text(x + w / 2, y - 0.22, sub, ha="center", va="top",
            fontsize=SUB_FONT, color=DIM, fontstyle="italic", zorder=3)


def arrow(ax, x0, y, x1, label_top, label_bottom):
    ax.annotate(
        "", xy=(x1, y), xytext=(x0, y),
        arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                        color=DIM, lw=2),
    )
    mid = (x0 + x1) / 2
    ax.text(mid, y + 0.12, label_top, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=INFARED)
    ax.text(mid, y + 0.05, label_bottom, ha="center", va="bottom",
            fontsize=9, color=INFARED)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor=BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.set_facecolor(BG)
    ax.axis("off")

    # Stage 1 — Registered (large)
    boxed(ax, x=0.4, y=1.3, w=2.5, h=2.2,
          color=COBALT, n="2,877",
          title="Registered (epoch 623)",
          sub="2,302 raw entities")

    # Arrow with filter info
    arrow(ax, x0=3.0, x1=4.4, y=2.4,
          label_top="−2,144 (75%)",
          label_bottom="below 3M ADA")

    # Stage 2 — Productive (≥3M)
    boxed(ax, x=4.6, y=1.3, w=4.6, h=2.2,
          color=ACID_GREEN, n="733",
          title="Productive (≥ 3M ₳)",
          sub="383 entities · 21.18B ₳ (97.4% of staked)")

    # Sub-tail annotations underneath
    ax.text(1.65, 0.65,
            "1,925 sub-block (< 1M ₳, 0.19B)\n"
            "+ 219 sub-reliable (1M–3M ₳, 0.39B)\n"
            "characterised in pools-distribution POL.O4",
            ha="center", va="top", fontsize=8.5, color=DIM, fontstyle="italic")

    out = FIG_DIR / "population_funnel.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
