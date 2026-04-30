#!/usr/bin/env python3
"""
Foundations overview — what the V2 Specification reasons from.

Rebranded to the Cardano-blue colour family that drives the rest of the
site (cardano.org primary blue + a complementary blue-2 for the synthesis
node). The four diagnostic-evidence cards are now wrapped in a faint
shaded panel so the single arrow into The Diagnostic clearly represents
the GROUP rather than only one card.

Layout:
  · single input column on the left, ordered so spec-bound sections sit
    in the upper half and diag-bound sections sit below.
  · The Diagnostic and V2 Spec on the right; The Diagnostic acts as a
    synthesis bridge for the lower-half inputs.

Outputs: figures/foundations_overview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

REPORT_DIR = Path(__file__).resolve().parent.parent
FIG_DIR = REPORT_DIR / "figures"

# --- Cardano-aligned palette (mirrors assets/site.css :root) -----------
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
TEXT_DIM = "#444444"

# Primary Cardano blues — used for the spec-side flow + the V2 node.
CARDANO_BLUE = "#0033AD"      # primary brand blue
CARDANO_BLUE_2 = "#1F5BC6"    # secondary, paler — the synthesis bridge
CARDANO_BLUE_3 = "#6394E2"    # tertiary, lightest

# Accents kept distinct so each input lane stays readable, but tuned to
# coexist with the blue chrome (no IOG-red domination).
INFARED = "#E52321"           # design artefacts (the spec lineage carrier)
DAWN = "#EC641D"              # community antecedent (warm, prior community work)
EVIDENCE_OLIVE = "#9CAA00"    # diagnostic evidence (Cardano-leaning olive)
GOVERNANCE_NAVY = "#2C4FFA"   # governance — cobalt, sits beside cardano-blue
RESEARCH_GREY = "#888888"     # research papers (inspiration only)


def draw_card(ax, x_center, y_center, w, h, title, sub, accent,
              novel=False, dashed_border=False, dark=False):
    style = "--" if dashed_border else "-"
    box = FancyBboxPatch(
        (x_center - w / 2, y_center - h / 2),
        w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=accent, linestyle=style,
        facecolor=accent if dark else "#FFFFFF",
    )
    ax.add_patch(box)
    title_color = "#FFFFFF" if dark else TEXT_COLOR
    sub_color = "#D4DAE6" if dark else TEXT_DIM
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


def arrow(ax, p_from, p_to, color, dashed=False, curve=0.0, width=2.0):
    style = "--" if dashed else "-"
    a = FancyArrowPatch(
        p_from, p_to,
        arrowstyle="-|>,head_length=12,head_width=8",
        linewidth=width, linestyle=style,
        color=color,
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=4, shrinkB=6,
    )
    ax.add_patch(a)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Try to use Inter (the site body face). Falls back to default sans
    # if Inter isn't installed locally — matplotlib will pick the next
    # available family from the rcParams stack.
    plt.rcParams["font.family"] = ["Inter", "DejaVu Sans", "sans-serif"]

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
        ("GOVERNANCE", GOVERNANCE_NAVY, [
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
    category_bounds = {}  # (top_y, bottom_y) per section — for group panels

    for header_text, color, cards in sections:
        draw_category_header(ax, col_x_left, y, header_text, color, col_x_right)
        key = header_text.split("  ·  ")[0]
        category_centroids[key] = []
        first_card_y = None
        last_card_y = None
        y -= pad_after_header + card_h / 2
        for (title, sub, novel, dashed) in cards:
            draw_card(ax, col_x, y, card_w, card_h, title, sub, color,
                      novel=novel, dashed_border=dashed)
            category_centroids[key].append(y)
            if first_card_y is None:
                first_card_y = y
            last_card_y = y
            y -= card_step
        y += card_step
        # Record top/bottom edges of this group's card stack — used for
        # drawing the faint group panel behind the diagnostic evidence.
        category_bounds[key] = (
            first_card_y + card_h / 2,
            last_card_y - card_h / 2,
        )
        y -= card_h / 2 + pad_before_header

    # Faint shaded panel behind the four diagnostic-evidence cards so the
    # single arrow into The Diagnostic clearly reads as 'all four feed in
    # together'.
    ev_top, ev_bot = category_bounds["DIAGNOSTIC EVIDENCE"]
    panel_pad_x = 0.18
    panel_pad_y = 0.14
    ax.add_patch(Rectangle(
        (col_x_left - panel_pad_x, ev_bot - panel_pad_y),
        card_w + 2 * panel_pad_x,
        (ev_top - ev_bot) + 2 * panel_pad_y,
        facecolor=EVIDENCE_OLIVE, edgecolor="none", alpha=0.05, zorder=0,
    ))

    def centroid(key):
        ys = category_centroids[key]
        return sum(ys) / len(ys)

    # ── The Diagnostic and V2 Spec on the right ──
    diag_x, diag_y = 10.7, 5.0
    spec_x, spec_y = 13.7, 9.5

    # The Diagnostic — synthesis bridge. Cardano blue-2 outline, white
    # fill so it reads as a 'pass-through' on the way to V2.
    draw_card(ax, diag_x, diag_y, 3.4, 1.5,
              "The Diagnostic",
              "holistic audit · problem induction",
              CARDANO_BLUE_2, novel=True)
    # V2 Specification — the destination. Solid Cardano-blue fill so it
    # carries the most visual weight on the canvas.
    draw_card(ax, spec_x, spec_y, 3.0, 1.5,
              "V2 Specification",
              "milestones · KPIs",
              CARDANO_BLUE, dark=True)

    # ── Arrows ──
    spec_left = spec_x - 1.5
    diag_left = diag_x - 1.7
    diag_right = diag_x + 1.7

    # Design → Spec (substantive lineage; arches over Diagnostic)
    arrow(ax,
          (col_x_right, centroid("DESIGN ARTEFACTS")),
          (spec_left, spec_y + 0.55),
          INFARED, curve=-0.10)

    # Research → Spec (dashed, inspiration only)
    arrow(ax,
          (col_x_right, centroid("RESEARCH PAPERS")),
          (spec_left, spec_y + 0.25),
          RESEARCH_GREY, dashed=True, curve=-0.05)

    # Governance → Spec
    arrow(ax,
          (col_x_right, centroid("GOVERNANCE")),
          (spec_left, spec_y - 0.10),
          GOVERNANCE_NAVY, curve=0.00)

    # Antecedent → Diagnostic
    arrow(ax,
          (col_x_right, centroid("COMMUNITY ANTECEDENT")),
          (diag_left, diag_y + 0.30),
          DAWN, curve=-0.05)

    # Evidence (group panel) → Diagnostic. Uses the panel's right edge
    # so the visual claim is 'the four sub-reports as a whole feed in'.
    arrow(ax,
          (col_x_right + panel_pad_x, centroid("DIAGNOSTIC EVIDENCE")),
          (diag_left, diag_y - 0.30),
          EVIDENCE_OLIVE, curve=0.10, width=2.4)

    # Diagnostic → Spec (the synthesis hand-off)
    arrow(ax,
          (diag_right, diag_y), (spec_left, spec_y - 0.40),
          CARDANO_BLUE_2, width=2.4)

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
