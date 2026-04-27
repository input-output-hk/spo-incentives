#!/usr/bin/env python3
"""
Foundations overview — every doc visible (research papers collapsed),
★ on novel docs only, arrows reorganised by destination.

Layout: single input column on the left, ordered so that:
  · sections that flow to V2 Spec sit in the upper half
  · sections that flow to The Diagnostic sit in the lower half
The Diagnostic and V2 Spec are vertically centred on the right.

Outputs: figures/foundations_overview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPORT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = REPORT_DIR / "figures"

BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#444444"

INFARED = "#E52321"
DAWN = "#EC641D"
ELECTRIC_BLUE = "#0DBFB0"
COBALT_PULSE = "#2C4FFA"
EVIDENCE_OLIVE = "#9CAA00"
RESEARCH_GREY = "#888888"


def draw_card(ax, x_center, y_center, w, h, title, sub, accent,
              novel=False, dashed_border=False, dark=False):
    style = "--" if dashed_border else "-"
    box = FancyBboxPatch(
        (x_center - w / 2, y_center - h / 2),
        w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=accent, linestyle=style,
        facecolor="#000000" if dark else "#FFFFFF",
    )
    ax.add_patch(box)
    title_color = "#FFFFFF" if dark else TEXT_COLOR
    sub_color = "#CCCCCC" if dark else TEXT_DIM
    star = "★ " if novel else ""
    ax.text(
        x_center, y_center + (0.13 if sub else 0),
        star + title,
        ha="center", va="center",
        fontsize=10.5, fontweight="bold", color=title_color,
    )
    if sub:
        ax.text(
            x_center, y_center - 0.16, sub,
            ha="center", va="center",
            fontsize=8.5, color=sub_color, style="italic",
        )


def draw_category_header(ax, x_left, y, text, color, x_right):
    ax.text(
        x_left, y, text,
        ha="left", va="center",
        fontsize=10, fontweight="bold", color=color,
    )
    ax.plot([x_left, x_right], [y - 0.20, y - 0.20],
            color=color, linewidth=1.2, alpha=0.4)


def arrow(ax, p_from, p_to, color, dashed=False, curve=0.0):
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


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 16.0, 14.0
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
        "Foundations — what the V2 Specification reasons from",
        ha="center", va="center",
        fontsize=17, fontweight="bold", color=TEXT_COLOR,
    )
    fig.text(
        0.5, 0.935,
        "Solid arrow = substantive dependency  ·  Dashed = inspiration only  ·  ★ = novel companion document",
        ha="center", va="center",
        fontsize=11, color=TEXT_DIM, style="italic",
    )

    # ── Input column ──
    col_x = 3.4
    card_w = 5.0
    card_h = 0.75
    col_x_left = col_x - card_w / 2
    col_x_right = col_x + card_w / 2

    # Sections — ordered: spec-bound on top, diag-bound on bottom
    sections = [
        # --- spec-bound (upper half) ---
        ("DESIGN ARTEFACTS", INFARED, [
            ("SL-D1  ·  2019", "Delegation Incentives · Kant · Brünjes · Coutts",
             False, False),
            ("The Intended Game", "normative baseline · written for this spec",
             True, False),
        ]),
        ("RESEARCH PAPERS  ·  inspiration only", RESEARCH_GREY, [
            ("RSS  ·  IAPG  ·  RMPC  ·  BPD", None, False, True),
        ]),
        ("GOVERNANCE", COBALT_PULSE, [
            ("Cardano Constitution v2",
             "tenets · parameter guardrails · ratified epoch 609",
             False, False),
        ]),
        # --- diag-bound (lower half) ---
        ("COMMUNITY ANTECEDENT", DAWN, [
            ("SD-L  ·  2025",
             "Incentive Mechanism Analysis · Lopez de Lara",
             False, False),
        ]),
        ("DIAGNOSTIC EVIDENCE  ·  4 sub-reports", EVIDENCE_OLIVE, [
            ("Treasury & Pool Pots", "epoch budget · reserve · fees", False, False),
            ("Pools Distribution Gaps", "reward curve · pledge · tiers", False, False),
            ("The Operator's Cut", "intra-pool split · commission", False, False),
            ("The Staking Census", "populations · submitters", False, False),
        ]),
    ]

    pad_after_header = 0.55
    pad_before_header = 0.55
    card_step = 0.95

    y = 13.0
    category_centroids = {}

    for header_text, color, cards in sections:
        draw_category_header(ax, col_x_left, y, header_text, color, col_x_right)
        key = header_text.split("  ·  ")[0]
        category_centroids[key] = []
        y -= pad_after_header + card_h / 2
        for (title, sub, novel, dashed) in cards:
            draw_card(ax, col_x, y, card_w, card_h, title, sub, color,
                      novel=novel, dashed_border=dashed)
            category_centroids[key].append(y)
            y -= card_step
        y += card_step
        y -= card_h / 2 + pad_before_header

    def centroid(key):
        ys = category_centroids[key]
        return sum(ys) / len(ys)

    # ── The Diagnostic and V2 Spec on the right ──
    # Aligned vertically with the centroid of their respective inputs.
    diag_x, diag_y = 10.7, 5.0
    spec_x, spec_y = 13.7, 9.5

    draw_card(ax, diag_x, diag_y, 3.4, 1.5,
              "The Diagnostic",
              "holistic audit · problem induction",
              ELECTRIC_BLUE, novel=True)
    draw_card(ax, spec_x, spec_y, 3.0, 1.5,
              "V2 Specification",
              "milestones · KPIs",
              INFARED, dark=True)

    # ── Arrows ──
    spec_left = spec_x - 1.5
    diag_left = diag_x - 1.7
    diag_right = diag_x + 1.7

    # Design → Spec (arches over Diagnostic since both ends are above)
    arrow(ax,
          (col_x_right, centroid("DESIGN ARTEFACTS")),
          (spec_left, spec_y + 0.55),
          INFARED, curve=-0.10)

    # Research → Spec (dashed)
    arrow(ax,
          (col_x_right, centroid("RESEARCH PAPERS")),
          (spec_left, spec_y + 0.25),
          RESEARCH_GREY, dashed=True, curve=-0.05)

    # Governance → Spec
    arrow(ax,
          (col_x_right, centroid("GOVERNANCE")),
          (spec_left, spec_y - 0.10),
          COBALT_PULSE, curve=0.00)

    # Antecedent → Diagnostic
    arrow(ax,
          (col_x_right, centroid("COMMUNITY ANTECEDENT")),
          (diag_left, diag_y + 0.30),
          DAWN, curve=-0.05)

    # Evidence → Diagnostic
    arrow(ax,
          (col_x_right, centroid("DIAGNOSTIC EVIDENCE")),
          (diag_left, diag_y - 0.30),
          EVIDENCE_OLIVE, curve=0.10)

    # Diagnostic → Spec
    arrow(ax,
          (diag_right, diag_y), (spec_left, spec_y - 0.40),
          ELECTRIC_BLUE)

    # Caption
    fig.text(
        0.5, 0.045,
        "Spec-bound inputs (Design, Research, Governance) sit in the upper half and feed V2 Spec.  "
        "Diag-bound inputs (Antecedent, Evidence) sit in the lower half and feed The Diagnostic.  "
        "The Diagnostic synthesises evidence and feeds V2 Spec in turn.  "
        "Research papers contribute as inspiration only (dashed).",
        ha="center", va="center",
        fontsize=10.5, color=TEXT_DIM, style="italic",
    )

    out_path = FIG_DIR / "foundations_overview.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
