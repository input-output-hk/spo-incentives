#!/usr/bin/env python3
"""
Figure 9 — σ' decision: the three-way min and its three binding cases.

A flowchart-style diagram showing how σ' = min(σ, 1/k, L·p) is computed
and which cap binds in which regime, with the resulting pool reward.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
GREEN = '#2ecc71'
NEUTRAL = '#4a4a4a'
LIGHT = '#f0f0f0'

fig, ax = plt.subplots(figsize=(12, 8.5), dpi=150)
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

def box(x, y, w, h, text, fc=LIGHT, ec='black', fontsize=10, fontweight='normal', color='black'):
    bbox = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.1,rounding_size=0.15",
                          linewidth=1.2, facecolor=fc, edgecolor=ec)
    ax.add_patch(bbox)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color=color)

def arrow(x1, y1, x2, y2, label=None, color='black', label_offset=(0, 0), label_fontsize=8.5, label_color='black'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.4))
    if label:
        ax.text((x1 + x2) / 2 + label_offset[0], (y1 + y2) / 2 + label_offset[1],
                label, ha='center', va='center',
                fontsize=label_fontsize, color=label_color,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.88, pad=1.5))

# Top node — input
box(6, 9.3, 4.2, 0.7, 'Pool i   σ = total stake,   p = pledge', fontsize=11, fontweight='bold')

# Middle node — the min
box(6, 7.8, 4.2, 0.7, "σ' = min(σ,   1/k,   L · p)",
    fontsize=12, fontweight='bold', fc='#fff3e0')

# Arrow from top to middle
arrow(6, 8.9, 6, 8.2)

# Three branches
# Left: L·p binds → clipped
# Middle: σ binds → unaffected
# Right: 1/k binds → V1 saturation

# Condition boxes
box(2, 5.8, 3.3, 1.0,
    'L · p is smallest\n(pledge ratio p/σ < 1/L)',
    fontsize=9.5, fontweight='bold', fc='#ffe6e6', ec=RED, color=RED)
box(6, 5.8, 3.3, 1.0,
    'σ is smallest\n(pledge ratio p/σ ≥ 1/L\nand σ ≤ 1/k)',
    fontsize=9.5, fontweight='bold', fc='#e6ffe6', ec=GREEN, color='#1e6b1e')
box(10, 5.8, 3.3, 1.0,
    '1/k is smallest\n(σ ≥ 1/k,\npool at V1 saturation)',
    fontsize=9.5, fontweight='bold', fc='#fff0dc', ec=DAWN, color='#a04a0e')

# Arrows from min to conditions
arrow(5.5, 7.45, 2.3, 6.35)
arrow(6, 7.45, 6, 6.35)
arrow(6.5, 7.45, 9.7, 6.35)

# Effect boxes
box(2, 3.8, 3.3, 1.0,
    "CLIPPED\nσ' = L · p",
    fontsize=10.5, fontweight='bold', fc=RED, color='white')
box(6, 3.8, 3.3, 1.0,
    "UNAFFECTED\nσ' = σ",
    fontsize=10.5, fontweight='bold', fc=GREEN, color='white')
box(10, 3.8, 3.3, 1.0,
    "V1 SATURATION\nσ' = 1/k",
    fontsize=10.5, fontweight='bold', fc=DAWN, color='white')

arrow(2, 5.25, 2, 4.35)
arrow(6, 5.25, 6, 4.35)
arrow(10, 5.25, 10, 4.35)

# Reward boxes
box(2, 1.8, 3.3, 1.2,
    'Pool reward\n= V1 × (L · p / σ)\nREDUCED proportionally',
    fontsize=9.5, fontweight='bold', fc='white', ec=RED, color=RED)
box(6, 1.8, 3.3, 1.2,
    'Pool reward\n= V1 baseline\nFULL reward',
    fontsize=9.5, fontweight='bold', fc='white', ec=GREEN, color='#1e6b1e')
box(10, 1.8, 3.3, 1.2,
    'Pool reward\n= V1 baseline\nFULL reward',
    fontsize=9.5, fontweight='bold', fc='white', ec=DAWN, color='#a04a0e')

arrow(2, 3.25, 2, 2.45)
arrow(6, 3.25, 6, 2.45)
arrow(10, 3.25, 10, 2.45)

# Title
ax.text(6, 9.85,
        "σ' computation under CIP-0050 — three-way min and its binding cases",
        ha='center', va='center', fontsize=13, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_09_sigma_prime_decision.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
