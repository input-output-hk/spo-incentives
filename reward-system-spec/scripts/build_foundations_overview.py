#!/usr/bin/env python3
"""
Foundations overview — minimal version.

Five inputs feed the V2 Specification, mediated by the Diagnostic.
The detail (which paper, which sub-report) lives in the prose; the figure
carries only the structural skeleton.

Outputs: figures/foundations_overview.png
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
TEXT_DIM = "#555555"

INFARED = "#E52321"
DAWN = "#EC641D"
ELECTRIC_BLUE = "#0DBFB0"
COBALT_PULSE = "#2C4FFA"
RESEARCH_GREY = "#888888"
EVIDENCE_OLIVE = "#9CAA00"


def draw_node(ax, x, y, w, h, title, subtitle, accent, novel=False, dark=False):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w, h,
        boxstyle="round,pad=0.02,rounding_size=0.14",
        linewidth=2.2, edgecolor=accent,
        facecolor="#000000" if dark else "#FFFFFF",
    )
    ax.add_patch(box)

    title_color = "#FFFFFF" if dark else TEXT_COLOR
    sub_color = "#CCCCCC" if dark else TEXT_DIM

    star = "★ " if novel else ""
    ax.text(
        x, y + 0.18,
        star + title,
        ha="center", va="center",
        fontsize=14, fontweight="bold", color=title_color,
    )
    ax.text(
        x, y - 0.28,
        subtitle,
        ha="center", va="center",
        fontsize=10, color=sub_color, style="italic",
    )


def arrow(ax, p_from, p_to, label, color, dashed=False, curve=0.0,
          label_pos=0.5, label_offset=(0, 0.30)):
    style = "--" if dashed else "-"
    a = FancyArrowPatch(
        p_from, p_to,
        arrowstyle="-|>,head_length=12,head_width=8",
        linewidth=2.0, linestyle=style,
        color=color,
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=4, shrinkB=6,
    )
    ax.add_patch(a)
    if label:
        mx = p_from[0] + (p_to[0] - p_from[0]) * label_pos + label_offset[0]
        my = p_from[1] + (p_to[1] - p_from[1]) * label_pos + label_offset[1]
        ax.text(
            mx, my, label,
            ha="center", va="center",
            fontsize=10, color=color, style="italic",
            bbox=dict(facecolor=BG_COLOR, edgecolor="none", pad=2.0),
        )


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 16.0, 11.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.text(
        0.5, 0.96,
        "Foundations — what the V2 Specification reasons from",
        ha="center", va="center",
        fontsize=16, fontweight="bold", color=TEXT_COLOR,
    )
    fig.text(
        0.5, 0.928,
        "Solid arrow = substantive dependency  ·  Dashed = inspiration only  ·  ★ = novel companion document",
        ha="center", va="center",
        fontsize=10.5, color=TEXT_DIM, style="italic",
    )

    # Layout: 3 columns
    col_left = 3.0
    col_mid = 8.5
    col_right = 13.5

    node_w, node_h = 4.6, 1.0

    # LEFT — five input categories, vertically stacked
    inputs = [
        ("Design baseline",     "SL-D1 · The Intended Game",            INFARED, True),
        ("Research papers",     "RSS · IAPG · RMPC · BPD",              RESEARCH_GREY, False),
        ("Community antecedent","SD-L · 2025",                          DAWN, False),
        ("Diagnostic evidence", "4 sub-reports · findings → observations", EVIDENCE_OLIVE, False),
        ("Cardano Constitution v2", "tenets · parameter guardrails",     COBALT_PULSE, False),
    ]

    y_top = 9.5
    y_step = 1.7
    input_centers = []
    for i, (title, sub, color, novel) in enumerate(inputs):
        y = y_top - i * y_step
        draw_node(ax, col_left, y, node_w, node_h, title, sub, color, novel=novel)
        input_centers.append((col_left, y, color, title))

    # MID — The Diagnostic
    diag_y = (y_top + (y_top - 4 * y_step)) / 2  # vertical centre of the inputs
    draw_node(
        ax, col_mid, diag_y, 3.6, 1.4,
        "The Diagnostic",
        "holistic audit · problem induction",
        ELECTRIC_BLUE, novel=True,
    )

    # RIGHT — V2 Specification
    spec_y = diag_y
    draw_node(
        ax, col_right, spec_y, 3.4, 1.6,
        "V2 Specification",
        "milestones · KPIs",
        INFARED, dark=True,
    )

    # Arrows from inputs — no labels, colour matches source box
    diag_left = col_mid - 1.8
    spec_left = col_right - 1.7
    diag_right = col_mid + 1.8

    # Design → Spec (direct, solid red)
    arrow(ax,
          (col_left + node_w / 2, input_centers[0][1]), (spec_left, spec_y + 0.45),
          None, INFARED, curve=-0.15)

    # Research → Spec (dashed grey)
    arrow(ax,
          (col_left + node_w / 2, input_centers[1][1]), (spec_left, spec_y + 0.20),
          None, RESEARCH_GREY, dashed=True, curve=-0.10)

    # Antecedent → Diagnostic
    arrow(ax,
          (col_left + node_w / 2, input_centers[2][1]), (diag_left, diag_y + 0.10),
          None, DAWN, curve=0.05)

    # Evidence → Diagnostic
    arrow(ax,
          (col_left + node_w / 2, input_centers[3][1]), (diag_left, diag_y - 0.10),
          None, EVIDENCE_OLIVE, curve=-0.05)

    # Diagnostic → Spec
    arrow(ax,
          (diag_right, diag_y), (spec_left, spec_y),
          None, ELECTRIC_BLUE)

    # Constitution → Spec (governance)
    arrow(ax,
          (col_left + node_w / 2, input_centers[4][1]), (spec_left, spec_y - 0.45),
          None, COBALT_PULSE, curve=0.10)

    # Caption explaining the flow
    fig.text(
        0.5, 0.04,
        "Each input flows to its destination via a same-colour arrow.  "
        "Three sources feed the Diagnostic (community antecedent, evidence sub-reports);  "
        "the Diagnostic + Design baseline + Constitution feed the V2 Specification directly;  "
        "research papers contribute as inspiration only (dashed).",
        ha="center", va="center",
        fontsize=10, color=TEXT_DIM, style="italic",
        wrap=True,
    )

    out_path = FIG_DIR / "foundations_overview.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
