#!/usr/bin/env python3
"""
Macro dashboard loop — the §4 hero diagram.

Four-stage cockpit loop showing how the protocol pilots itself:
    Instruments → Warning lights → Recalibration proposal → Conway pipeline
    └──────────────────── next cycle ────────────────────┘

Outputs: figures/macro_dashboard_loop.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPORT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = REPORT_DIR / "figures"

# ── IOG Brand Palette ──
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#444444"
TEXT_MUTED = "#888888"

INFARED = "#E52321"
DAWN = "#EC641D"
ACID_GREEN = "#00B35F"
ELECTRIC_BLUE = "#0DBFB0"
ULTRAVIOLET = "#A700FF"
VOLT_YELLOW = "#F2FF58"
SOLAR_AMBER = "#FFBA36"
COBALT_PULSE = "#2C4FFA"

# Stage palette — one accent per stage of the loop
STAGES = [
    {
        "key": "INSTRUMENTS",
        "title": "Instruments",
        "subtitle": "per-epoch surveillance",
        "lines": [
            ("§4.1", "pot composition  ·  runway  ·  realisation"),
            ("§4.2", "submitter population  ·  fees  ·  eligibility"),
        ],
        "accent": ELECTRIC_BLUE,
        "soft": "#0DBFB019",
    },
    {
        "key": "WARNINGS",
        "title": "Warning lights",
        "subtitle": "evaluated at cycle boundary",
        "lines": [
            ("§4.1", "trigger fired ?"),
            ("§4.2", "trigger fired ?"),
        ],
        "accent": INFARED,
        "soft": "#E5232119",
    },
    {
        "key": "PROPOSAL",
        "title": "Recalibration proposal",
        "subtitle": "what the cycle outputs",
        "lines": [
            ("·", "parameter scope within constitutional bounds"),
            ("·", "acceptance criterion — §3 KPIs preserved"),
            ("§4.3", "validation under 3 price scenarios"),
        ],
        "accent": SOLAR_AMBER,
        "soft": "#FFBA3619",
    },
    {
        "key": "DOCTRINE",
        "title": "Conway pipeline",
        "subtitle": "§4.4 operational doctrine",
        "lines": [
            ("·", "DRep  ·  Constitutional Committee"),
            ("·", "SPO ratification"),
            ("·", "Parameter Update / CIP / Amendment"),
        ],
        "accent": COBALT_PULSE,
        "soft": "#2C4FFA19",
    },
]


def draw_stage_box(ax, x_center, y_center, width, height, stage):
    """Draw one rounded box with stage content."""
    x_left = x_center - width / 2
    y_bottom = y_center - height / 2

    box = FancyBboxPatch(
        (x_left, y_bottom),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=2.0,
        edgecolor=stage["accent"],
        facecolor=stage["soft"],
    )
    ax.add_patch(box)

    # Accent bar across the top
    bar = mpatches.Rectangle(
        (x_left + 0.10, y_bottom + height - 0.08),
        width - 0.20,
        0.06,
        linewidth=0,
        facecolor=stage["accent"],
    )
    ax.add_patch(bar)

    # Title
    ax.text(
        x_center,
        y_bottom + height - 0.50,
        stage["title"],
        ha="center", va="center",
        fontsize=14, fontweight="bold", color=TEXT_COLOR,
    )

    # Subtitle (small caps via spaced-out letters not used; just lowercase italic)
    ax.text(
        x_center,
        y_bottom + height - 0.85,
        stage["subtitle"],
        ha="center", va="center",
        fontsize=8.5, color=stage["accent"], style="italic",
    )

    # Body lines, left-aligned with §-tag column
    n = len(stage["lines"])
    body_top = y_bottom + height - 1.30
    body_bottom = y_bottom + 0.30
    body_height = body_top - body_bottom
    if n == 1:
        ys = [(body_top + body_bottom) / 2]
    else:
        step = body_height / (n - 1) if n > 1 else 0
        ys = [body_top - i * step for i in range(n)]

    tag_x = x_left + 0.25
    text_x = x_left + 0.85

    for (tag, txt), y in zip(stage["lines"], ys):
        ax.text(
            tag_x, y, tag,
            ha="left", va="center",
            fontsize=9, fontweight="bold", color=stage["accent"],
        )
        ax.text(
            text_x, y, txt,
            ha="left", va="center",
            fontsize=9, color=TEXT_DIM,
        )


def draw_forward_arrow(ax, x_from, x_to, y, label):
    arrow = FancyArrowPatch(
        (x_from, y),
        (x_to, y),
        arrowstyle="-|>,head_length=8,head_width=6",
        linewidth=2.2,
        color=TEXT_DIM,
    )
    ax.add_patch(arrow)
    if label:
        ax.text(
            (x_from + x_to) / 2, y + 0.22,
            label,
            ha="center", va="bottom",
            fontsize=8.5, color=TEXT_MUTED, style="italic",
        )


def draw_loop_arrow(ax, x_from, x_to, y_top, label_y, label):
    arrow = FancyArrowPatch(
        (x_from, y_top),
        (x_to, y_top),
        connectionstyle="arc3,rad=-0.35",
        arrowstyle="-|>,head_length=10,head_width=7",
        linewidth=2.4,
        color=INFARED,
    )
    ax.add_patch(arrow)
    ax.text(
        (x_from + x_to) / 2, label_y, label,
        ha="center", va="center",
        fontsize=11, color=INFARED, fontweight="bold", style="italic",
    )


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 17.5, 8.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.set_aspect("equal")
    ax.axis("off")

    # Header
    fig.text(
        0.5, 0.965,
        "The macro dashboard — piloting the micro-economy through time",
        ha="center", va="center",
        fontsize=15.5, fontweight="bold", color=TEXT_COLOR,
    )
    fig.text(
        0.5, 0.925,
        "Per-epoch surveillance feeds cycle-boundary triggers; fired triggers produce a recalibration proposal; "
        "the Conway pipeline ratifies it; the next cycle resumes surveillance.",
        ha="center", va="center",
        fontsize=10, color=TEXT_DIM, style="italic",
    )

    # ── Layout — 4 boxes in a row with arrow gaps ──
    box_w = 3.5
    box_h = 3.5
    arrow_gap = 0.95
    total_w = 4 * box_w + 3 * arrow_gap
    x_start = (fig_w - total_w) / 2
    y_center = 4.5

    box_centers = []
    for i, stage in enumerate(STAGES):
        x_center = x_start + box_w / 2 + i * (box_w + arrow_gap)
        draw_stage_box(ax, x_center, y_center, box_w, box_h, stage)
        box_centers.append(x_center)

    # Forward arrows in the gaps
    forward_labels = ["publish", "evaluate", "submit"]
    for i in range(3):
        x_from = box_centers[i] + box_w / 2 + 0.12
        x_to = box_centers[i + 1] - box_w / 2 - 0.12
        draw_forward_arrow(ax, x_from, x_to, y_center, forward_labels[i])

    # Loop-back arrow under the row
    x_loop_from = box_centers[-1]
    x_loop_to = box_centers[0]
    y_loop_anchor = y_center - box_h / 2 - 0.10
    y_label = y_center - box_h / 2 - 1.55
    draw_loop_arrow(ax, x_loop_from, x_loop_to, y_loop_anchor, y_label, "next cycle")

    # Footer caption
    fig.text(
        0.5, 0.04,
        "Rhythmed regime — cycles open at fixed intervals, not on every fired trigger.  "
        "Forward path to event-driven cycles described in §4.4.3.",
        ha="center", va="center",
        fontsize=9, color=TEXT_MUTED, style="italic",
    )

    out_path = FIG_DIR / "macro_dashboard_loop.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
