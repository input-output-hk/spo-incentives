#!/usr/bin/env python3
"""
Macro dashboard loop — minimal version.

Four-stage cockpit loop. The body of each stage (KPIs, triggers, parameters)
lives in the prose; the figure carries only the structural skeleton.

Outputs: figures/macro_dashboard_loop.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPORT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = REPORT_DIR / "figures"

BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#444444"
TEXT_MUTED = "#888888"

INFARED = "#E52321"
ELECTRIC_BLUE = "#0DBFB0"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"

STAGES = [
    ("Instruments",       "per-epoch surveillance",         ELECTRIC_BLUE),
    ("Warning lights",    "evaluated at cycle boundary",    INFARED),
    ("Recalibration",     "what the cycle outputs",          SOLAR_AMBER),
    ("Conway pipeline",   "ratification & action class",    COBALT_PULSE),
]

ARROW_LABELS = ["publish", "evaluate", "submit"]


def draw_box(ax, x_center, y_center, w, h, title, subtitle, accent):
    box = FancyBboxPatch(
        (x_center - w / 2, y_center - h / 2),
        w, h,
        boxstyle="round,pad=0.02,rounding_size=0.18",
        linewidth=2.2, edgecolor=accent,
        facecolor="#FFFFFF",
    )
    ax.add_patch(box)

    # accent bar across the top
    bar = mpatches.Rectangle(
        (x_center - w / 2 + 0.15, y_center + h / 2 - 0.18),
        w - 0.30, 0.10,
        linewidth=0, facecolor=accent,
    )
    ax.add_patch(bar)

    ax.text(
        x_center, y_center + 0.20,
        title,
        ha="center", va="center",
        fontsize=15, fontweight="bold", color=TEXT_COLOR,
    )
    ax.text(
        x_center, y_center - 0.30,
        subtitle,
        ha="center", va="center",
        fontsize=10.5, color=accent, style="italic",
    )


def draw_forward_arrow(ax, x_from, x_to, y, label, label_y):
    a = FancyArrowPatch(
        (x_from, y), (x_to, y),
        arrowstyle="-|>,head_length=14,head_width=10",
        linewidth=3.0, color=TEXT_DIM,
    )
    ax.add_patch(a)
    ax.text(
        (x_from + x_to) / 2, label_y,
        label,
        ha="center", va="center",
        fontsize=12, color=TEXT_DIM, fontweight="bold",
    )


def draw_loop(ax, x_from, x_to, y_top, y_label, label):
    a = FancyArrowPatch(
        (x_from, y_top), (x_to, y_top),
        connectionstyle="arc3,rad=-0.32",
        arrowstyle="-|>,head_length=16,head_width=11",
        linewidth=3.2, color=INFARED,
    )
    ax.add_patch(a)
    ax.text(
        (x_from + x_to) / 2, y_label, label,
        ha="center", va="center",
        fontsize=15, color=INFARED, fontweight="bold", style="italic",
    )


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 16.0, 7.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.set_aspect("equal")
    ax.axis("off")

    # Header
    fig.text(
        0.5, 0.95,
        "The macro dashboard — piloting the micro-economy through time",
        ha="center", va="center",
        fontsize=15, fontweight="bold", color=TEXT_COLOR,
    )

    # Layout
    box_w, box_h = 3.4, 1.9
    gap = 0.65
    total_w = 4 * box_w + 3 * gap
    x_start = (fig_w - total_w) / 2
    y_center = 4.0

    box_centers = []
    for i, (title, subtitle, accent) in enumerate(STAGES):
        xc = x_start + box_w / 2 + i * (box_w + gap)
        draw_box(ax, xc, y_center, box_w, box_h, title, subtitle, accent)
        box_centers.append(xc)

    label_y = y_center + box_h / 2 + 0.45  # well above the box tops
    for i in range(3):
        x_from = box_centers[i] + box_w / 2 + 0.05
        x_to = box_centers[i + 1] - box_w / 2 - 0.05
        draw_forward_arrow(ax, x_from, x_to, y_center, ARROW_LABELS[i], label_y)

    # Loop arrow under the row
    y_loop_anchor = y_center - box_h / 2 - 0.25
    y_label = y_center - box_h / 2 - 1.40
    draw_loop(ax, box_centers[-1], box_centers[0], y_loop_anchor, y_label, "next cycle")

    out_path = FIG_DIR / "macro_dashboard_loop.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
