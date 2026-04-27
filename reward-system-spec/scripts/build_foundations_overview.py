#!/usr/bin/env python3
"""
Foundations overview — the §1 hero diagram.

Maps the documents the V2 Specification reasons from:
  · Design artefacts (SL-D1, The Intended Game)
  · Research papers (RSS, IAPG, RMPC, BPD)
  · Community antecedent (SD-L)
  · Diagnostic sub-reports (TPP, PDG, OC, SC) → The Diagnostic
  · Cardano Constitution v2

All flow into the V2 Specification node on the right.
The dashed arrow marks the research papers as 'inspiration only'.
The ★ marks the two novel companion documents.

Outputs: figures/foundations_overview.png
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
ELECTRIC_BLUE = "#0DBFB0"
COBALT_PULSE = "#2C4FFA"
EVIDENCE_OLIVE = "#9CAA00"
RESEARCH_GREY = "#888888"


def draw_node(ax, x, y, w, h, title, sub_lines, accent, fill, novel=False, dark=False):
    """Draw a single rounded node with title + subtitle lines."""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w, h,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=2.0 if dark else 1.6,
        edgecolor=accent,
        facecolor=fill,
    )
    ax.add_patch(box)

    title_color = "#FFFFFF" if dark else TEXT_COLOR
    sub_color = "#CCCCCC" if dark else TEXT_DIM

    # Title — at top of box
    star = "★ " if novel else ""
    ax.text(
        x, y + h / 2 - 0.32,
        star + title,
        ha="center", va="center",
        fontsize=10, fontweight="bold", color=title_color,
    )

    # Subtitle lines, distributed in remaining space
    n = len(sub_lines)
    if n == 0:
        return
    body_top = y + h / 2 - 0.65
    body_bottom = y - h / 2 + 0.18
    if n == 1:
        ys = [(body_top + body_bottom) / 2]
    else:
        step = (body_top - body_bottom) / (n - 1)
        ys = [body_top - i * step for i in range(n)]

    for txt, y_line in zip(sub_lines, ys):
        ax.text(
            x, y_line, txt,
            ha="center", va="center",
            fontsize=8, color=sub_color, style="italic",
        )


def category_label(ax, x_left, y, label, color):
    """Small caps category label on the left margin."""
    ax.text(
        x_left, y, label,
        ha="left", va="center",
        fontsize=9.5, fontweight="bold", color=color,
    )


def arrow(ax, p_from, p_to, label=None, dashed=False, color=None,
          label_pos=0.5, label_offset=(0, 0.18), curve=0.0):
    color = color or TEXT_DIM
    style = "--" if dashed else "-"
    a = FancyArrowPatch(
        p_from, p_to,
        arrowstyle="-|>,head_length=8,head_width=5.5",
        linewidth=1.5,
        linestyle=style,
        color=color,
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=3, shrinkB=4,
    )
    ax.add_patch(a)
    if label:
        mx = p_from[0] + (p_to[0] - p_from[0]) * label_pos + label_offset[0]
        my = p_from[1] + (p_to[1] - p_from[1]) * label_pos + label_offset[1]
        ax.text(
            mx, my, label,
            ha="center", va="center",
            fontsize=8, color=color, style="italic",
            bbox=dict(facecolor=BG_COLOR, edgecolor="none", pad=1.5),
        )


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig_w, fig_h = 17.0, 11.0
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
        fontsize=16, fontweight="bold", color=TEXT_COLOR,
    )
    fig.text(
        0.5, 0.935,
        "Solid arrows = substantive dependencies   ·   Dashed = inspiration only   ·   ★ = novel companion document written for this spec",
        ha="center", va="center",
        fontsize=10, color=TEXT_DIM, style="italic",
    )

    # ── Column layout ──
    # Col A (x ≈ 2.3): left sources — design, research, antecedent, governance
    # Col B (x ≈ 7.0): evidence sub-reports
    # Col C (x ≈ 11.5): The Diagnostic (synthesizer)
    # Col D (x ≈ 15.2): V2 Specification (target)

    col_a_x = 2.7
    col_b_x = 7.5
    col_c_x = 11.7
    col_d_x = 15.0

    node_w_a = 3.6
    node_h_a = 1.20

    # ── Column A — ordered top to bottom ──
    # 1. Design artefacts (2 nodes)
    cat_y = 9.7
    category_label(ax, 0.4, cat_y, "DESIGN ARTEFACTS", INFARED)
    draw_node(
        ax, col_a_x, 9.10, node_w_a, node_h_a,
        "SL-D1  ·  2019",
        ["Delegation Incentives Design Spec",
         "Kant · Brünjes · Coutts"],
        accent=INFARED, fill="#FFE9E8",
    )
    draw_node(
        ax, col_a_x, 7.70, node_w_a, node_h_a,
        "The Intended Game",
        ["normative baseline",
         "written for this spec"],
        accent=INFARED, fill="#FFE9E8", novel=True,
    )

    # 2. Research papers (4 nodes — compact pair)
    cat_y = 6.85
    category_label(ax, 0.4, cat_y, "RESEARCH PAPERS", RESEARCH_GREY)
    research = [
        ("RSS  ·  2020", "Reward Sharing Schemes"),
        ("IAPG  ·  2021", "Incentives Against Power Grabs"),
        ("RMPC  ·  2022", "Removing min-pool-cost"),
        ("BPD  ·  2024", "Participation × Decentralization"),
    ]
    for i, (title, sub) in enumerate(research):
        rx = col_a_x - 0.95 + (i % 2) * 1.95
        ry = 6.30 - (i // 2) * 0.65
        ax.text(
            rx, ry + 0.13, title,
            ha="center", va="center",
            fontsize=8.5, fontweight="bold", color=TEXT_COLOR,
        )
        ax.text(
            rx, ry - 0.13, sub,
            ha="center", va="center",
            fontsize=7.5, color=TEXT_DIM, style="italic",
        )

    # 3. Community antecedent
    cat_y = 4.65
    category_label(ax, 0.4, cat_y, "COMMUNITY ANTECEDENT", DAWN)
    draw_node(
        ax, col_a_x, 4.05, node_w_a, node_h_a,
        "SD-L  ·  2025",
        ["Incentive Mechanism Analysis",
         "Carlos Lopez de Lara"],
        accent=DAWN, fill="#FFEFD9",
    )

    # 4. Governance
    cat_y = 2.55
    category_label(ax, 0.4, cat_y, "GOVERNANCE", COBALT_PULSE)
    draw_node(
        ax, col_a_x, 1.95, node_w_a, node_h_a,
        "Cardano Constitution v2",
        ["tenets · parameter guardrails",
         "ratified epoch 609"],
        accent=COBALT_PULSE, fill="#E8ECFF",
    )

    # ── Column B — evidence sub-reports ──
    cat_y = 9.7
    category_label(ax, col_b_x - 1.9, cat_y, "DIAGNOSTIC SUB-REPORTS", EVIDENCE_OLIVE)
    evidence = [
        ("Treasury & Pool Pots", "epoch budget · reserve · fees", "backs §1.1"),
        ("Pools Distribution Gaps", "reward curve · pledge · tiers", "backs §1.2"),
        ("The Operator's Cut", "intra-pool split · commission", "backs §1.3"),
        ("The Staking Census", "populations · submitters", "backs §2.1–§2.2"),
    ]
    evidence_centers = []
    for i, (title, sub, backs) in enumerate(evidence):
        ey = 8.85 - i * 1.55
        draw_node(
            ax, col_b_x, ey, 4.0, 1.20,
            title,
            [sub, backs],
            accent=EVIDENCE_OLIVE, fill="#FCFFE0",
        )
        evidence_centers.append((col_b_x, ey))

    # ── Column C — The Diagnostic ──
    diag_y = 5.5
    category_label(ax, col_c_x - 1.5, 9.7, "DIAGNOSTIC SYNTHESIS", ELECTRIC_BLUE)
    draw_node(
        ax, col_c_x, diag_y, 3.0, 2.2,
        "The Diagnostic",
        ["holistic audit",
         "problem induction",
         "written for this spec"],
        accent=ELECTRIC_BLUE, fill="#DFFAF7", novel=True,
    )

    # ── Column D — V2 Specification ──
    spec_y = 5.5
    category_label(ax, col_d_x - 1.2, 9.7, "TARGET", INFARED)
    draw_node(
        ax, col_d_x, spec_y, 2.6, 2.2,
        "V2 Specification",
        ["milestones",
         "KPIs"],
        accent=INFARED, fill="#000000", dark=True,
    )

    # ── Arrows ──
    # Design → Spec
    arrow(ax,
          (col_a_x + node_w_a / 2, 9.10), (col_d_x - 1.3, spec_y + 0.7),
          label="original design", color=INFARED,
          label_pos=0.7, label_offset=(0, 0.20), curve=-0.1)
    arrow(ax,
          (col_a_x + node_w_a / 2, 7.70), (col_d_x - 1.3, spec_y + 0.4),
          label="intended equilibrium", color=INFARED,
          label_pos=0.7, label_offset=(0, 0.20), curve=-0.05)

    # Research → Spec (combined dashed arrow from research block centroid)
    arrow(ax,
          (col_a_x + node_w_a / 2, 6.0), (col_d_x - 1.3, spec_y + 0.15),
          label="light inspiration", dashed=True, color=RESEARCH_GREY,
          label_pos=0.6, label_offset=(0, 0.18), curve=-0.05)

    # Antecedent → Diagnostic
    arrow(ax,
          (col_a_x + node_w_a / 2, 4.05), (col_c_x - 1.5, diag_y - 0.6),
          label="starting point · extended by", color=DAWN,
          label_pos=0.55, label_offset=(0, -0.22), curve=0.05)

    # Evidence → Diagnostic (4 arrows)
    for ec in evidence_centers:
        arrow(ax,
              (ec[0] + 2.0, ec[1]), (col_c_x - 1.5, diag_y),
              color=EVIDENCE_OLIVE)

    # Diagnostic → Spec
    arrow(ax,
          (col_c_x + 1.5, diag_y), (col_d_x - 1.3, spec_y),
          label="induced problems", color=ELECTRIC_BLUE,
          label_pos=0.5, label_offset=(0, 0.20))

    # Governance → Spec
    arrow(ax,
          (col_a_x + node_w_a / 2, 1.95), (col_d_x - 1.3, spec_y - 0.7),
          label="tenets & guardrails", color=COBALT_PULSE,
          label_pos=0.65, label_offset=(0, -0.22), curve=0.10)

    # ── Legend ──
    legend_y = 0.45
    items = [
        ("design / spec", INFARED),
        ("antecedent", DAWN),
        ("evidence", EVIDENCE_OLIVE),
        ("diagnostic (novel)", ELECTRIC_BLUE),
        ("governance", COBALT_PULSE),
        ("research", RESEARCH_GREY),
    ]
    x = 0.6
    for label, color in items:
        ax.add_patch(mpatches.Rectangle((x, legend_y), 0.32, 0.18, color=color))
        ax.text(x + 0.45, legend_y + 0.09, label,
                fontsize=8.5, color=TEXT_DIM, va="center")
        x += 2.2 if label != "diagnostic (novel)" else 2.6

    out_path = FIG_DIR / "foundations_overview.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
