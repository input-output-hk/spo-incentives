#!/usr/bin/env python3
"""
Foundations overview — every document visible, ★ on novel docs only.

Layout: a single left column with all 12 source documents stacked vertically
(grouped by category headers), The Diagnostic synthesis node centre-right,
V2 Specification on the right. Arrows fan out from input groups to their
destination — no crossing because the input column is alone on the left.

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
        linewidth=1.6, edgecolor=accent,
        linestyle=style,
        facecolor="#000000" if dark else "#FFFFFF",
    )
    ax.add_patch(box)

    title_color = "#FFFFFF" if dark else TEXT_COLOR
    sub_color = "#CCCCCC" if dark else TEXT_DIM

    star = "★ " if novel else ""
    ax.text(
        x_center, y_center + 0.12,
        star + title,
        ha="center", va="center",
        fontsize=10, fontweight="bold", color=title_color,
    )
    if sub:
        ax.text(
            x_center, y_center - 0.14,
            sub,
            ha="center", va="center",
            fontsize=8, color=sub_color, style="italic",
        )


def draw_category_header(ax, x_left, y, text, color, x_right):
    """Header label, left-aligned, with a thin colored underline."""
    ax.text(
        x_left, y, text,
        ha="left", va="center",
        fontsize=10, fontweight="bold", color=color,
    )
    # underline
    ax.plot([x_left, x_right], [y - 0.18, y - 0.18],
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

    fig_w, fig_h = 17.0, 14.0
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
        0.5, 0.94,
        "Solid arrow = substantive dependency  ·  Dashed = inspiration only  ·  ★ = novel companion document written for this spec",
        ha="center", va="center",
        fontsize=11, color=TEXT_DIM, style="italic",
    )

    # Single input column on the left
    col_x = 3.2
    card_w = 5.0
    card_h = 0.75

    col_x_left = col_x - card_w / 2
    col_x_right = col_x + card_w / 2

    # ── Input cards, stacked top to bottom ──
    # Layout structure: list of (kind, ...) entries.
    #   ("section", header_text, color, [(title, sub, novel, dashed), ...])
    sections = [
        ("DESIGN ARTEFACTS", INFARED, [
            ("SL-D1  ·  2019", "Delegation Incentives · Kant · Brünjes · Coutts",
             False, False),
            ("The Intended Game", "normative baseline · written for this spec",
             True, False),
        ]),
        ("RESEARCH PAPERS  ·  inspiration only", RESEARCH_GREY, [
            ("RSS  ·  2020", "Reward Sharing Schemes · Brünjes · Kiayias et al.",
             False, True),
            ("IAPG  ·  2021", "Incentives Against Power Grabs", False, True),
            ("RMPC  ·  2022", "Removing min-pool-cost", False, True),
            ("BPD  ·  2024", "Block Participation × Decentralization", False, True),
        ]),
        ("COMMUNITY ANTECEDENT", DAWN, [
            ("SD-L  ·  2025", "Incentive Mechanism Analysis · Lopez de Lara",
             False, False),
        ]),
        ("DIAGNOSTIC EVIDENCE  ·  4 sub-reports", EVIDENCE_OLIVE, [
            ("Treasury & Pool Pots", "epoch budget · reserve · fees",
             False, False),
            ("Pools Distribution Gaps", "reward curve · pledge · tiers",
             False, False),
            ("The Operator's Cut", "intra-pool split · commission",
             False, False),
            ("The Staking Census", "populations · submitters", False, False),
        ]),
        ("GOVERNANCE", COBALT_PULSE, [
            ("Cardano Constitution v2",
             "tenets · parameter guardrails · ratified epoch 609",
             False, False),
        ]),
    ]

    # Vertical stepping (in axis units, y decreasing downward):
    pad_before_header = 0.55
    pad_after_header  = 0.55       # gap from header baseline to first card top
    card_step         = 0.95       # centre-to-centre between cards

    y = 13.30  # starting y for first header
    category_centroids = {}

    for header_text, color, cards in sections:
        # Header
        draw_category_header(ax, col_x_left, y, header_text, color, col_x_right)
        category_key = header_text.split("  ·  ")[0]
        category_centroids[category_key] = []
        # Move down to first card centre
        y -= pad_after_header + card_h / 2
        for (title, sub, novel, dashed) in cards:
            draw_card(ax, col_x, y, card_w, card_h, title, sub, color,
                      novel=novel, dashed_border=dashed)
            category_centroids[category_key].append(y)
            y -= card_step
        # Section ended — recoup the half-card we owe and add header gap
        y += card_step  # back to last card centre
        y -= card_h / 2 + pad_before_header  # past the bottom of last card

    def centroid(key):
        ys = category_centroids[key]
        return sum(ys) / len(ys)

    # ── Diagnostic synthesis (centre-right) ──
    diag_x = 11.0
    diag_y = 7.0
    draw_card(ax, diag_x, diag_y, 3.6, 1.6,
              "The Diagnostic",
              "holistic audit · problem induction",
              ELECTRIC_BLUE, novel=True)

    # ── V2 Specification (far right) ──
    spec_x = 14.5
    spec_y = 7.0
    draw_card(ax, spec_x, spec_y, 3.0, 1.6,
              "V2 Specification",
              "milestones · KPIs",
              INFARED, dark=True)

    # ── Arrows ──
    spec_left = spec_x - 1.5
    diag_left = diag_x - 1.8
    diag_right = diag_x + 1.8

    # Design → Spec
    arrow(ax,
          (col_x_right, centroid("DESIGN ARTEFACTS")),
          (spec_left, spec_y + 0.6),
          INFARED, curve=-0.10)

    # Research → Spec (dashed)
    arrow(ax,
          (col_x_right, centroid("RESEARCH PAPERS")),
          (spec_left, spec_y + 0.3),
          RESEARCH_GREY, dashed=True, curve=-0.10)

    # Antecedent → Diagnostic
    arrow(ax,
          (col_x_right, centroid("COMMUNITY ANTECEDENT")),
          (diag_left, diag_y + 0.5),
          DAWN, curve=-0.05)

    # Evidence → Diagnostic
    arrow(ax,
          (col_x_right, centroid("DIAGNOSTIC EVIDENCE")),
          (diag_left, diag_y - 0.3),
          EVIDENCE_OLIVE, curve=0.05)

    # Diagnostic → Spec
    arrow(ax,
          (diag_right, diag_y), (spec_left, spec_y),
          ELECTRIC_BLUE)

    # Governance → Spec
    arrow(ax,
          (col_x_right, centroid("GOVERNANCE")),
          (spec_left, spec_y - 0.6),
          COBALT_PULSE, curve=0.10)

    # Caption
    fig.text(
        0.5, 0.045,
        "Each category flows to its destination via a same-colour arrow.  "
        "Community antecedent and diagnostic evidence feed the Diagnostic;  "
        "the Diagnostic + design baseline + Constitution feed the V2 Specification directly;  "
        "research papers contribute as inspiration only (dashed).",
        ha="center", va="center",
        fontsize=10.5, color=TEXT_DIM, style="italic",
    )

    out_path = FIG_DIR / "foundations_overview.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
