#!/usr/bin/env python3
"""
Figure 10 — Operator decision tree under CIP-0050.

Non-compliant pool at activation: four response paths.
  Option 1 — Accept the cut
  Option 2 — Raise pledge
  Option 3 — Shrink the pool
  Option 4 — Exit
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
GREEN = '#2ecc71'
BLUE = '#2C4FFA'
NEUTRAL = '#4a4a4a'
LIGHT = '#f0f0f0'

fig, ax = plt.subplots(figsize=(13, 9), dpi=150)
ax.set_xlim(0, 13)
ax.set_ylim(0, 11)
ax.axis('off')

def box(x, y, w, h, text, fc=LIGHT, ec='black', fontsize=9.5, fontweight='normal', color='black', rounding=0.15):
    bbox = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad=0.1,rounding_size={rounding}",
                          linewidth=1.2, facecolor=fc, edgecolor=ec)
    ax.add_patch(bbox)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color=color)

def diamond(x, y, w, h, text, fc='#fff3e0', ec=DAWN, fontsize=9.5, fontweight='bold'):
    from matplotlib.patches import Polygon
    pts = [(x, y + h/2), (x + w/2, y), (x, y - h/2), (x - w/2, y)]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.3)
    ax.add_patch(poly)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color='black')

def arrow(x1, y1, x2, y2, label=None, color='black', lw=1.3, label_offset=(0, 0), label_color='black'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))
    if label:
        ax.text((x1 + x2) / 2 + label_offset[0], (y1 + y2) / 2 + label_offset[1],
                label, ha='center', va='center',
                fontsize=9, color=label_color, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.92, pad=1.8))

# Start
box(6.5, 10.2, 6.0, 0.8,
    'Non-compliant pool at CIP-0050 activation  (pledge ratio p/σ < 1/L)',
    fontsize=11, fontweight='bold', fc='#ffe6e6', ec=RED)

# Q1 — Have capital to raise pledge?
diamond(6.5, 8.6, 4.5, 1.0, 'Q1: Have capital to raise\npledge to σ/L?')

arrow(6.5, 9.8, 6.5, 9.1)

# Q1 Yes → Raise pledge (left branch)
arrow(4.3, 8.6, 2.3, 7.6, label='YES', color=GREEN, label_color=GREEN, label_offset=(-0.2, 0))

box(2.3, 6.8, 3.7, 1.6,
    'OPTION 2 — Raise pledge\n\nLock σ/L in pledge\nYield sacrificed:\n0.68 vs 2.3 %/yr (POL.O2.F2)\n→ V1 reward restored',
    fontsize=8.5, fontweight='normal', fc=BLUE, color='white', rounding=0.15)

# Q1 No → Q2
arrow(8.7, 8.6, 8.7, 7.75, label='NO / unwilling', color=RED, label_color=RED, label_offset=(1.0, 0))

# Q2 — Willing to shrink?
diamond(8.7, 7.05, 4.0, 1.0, 'Q2: Willing to shrink\npool to L · p?')

# Q2 Yes → Shrink (right branch)
arrow(10.7, 7.05, 11.3, 6.0, label='YES', color=DAWN, label_color=DAWN, label_offset=(0.2, 0))

box(11.0, 5.0, 3.3, 1.6,
    'OPTION 3 — Shrink\n\nRefuse delegation > L·p\n~93 % of stake must\nrelocate; likely to\nother clipped pools',
    fontsize=8.5, fontweight='normal', fc=DAWN, color='white', rounding=0.15)

# Q2 No → Q3
arrow(8.7, 6.55, 8.7, 5.75, label='NO', color=RED, label_color=RED, label_offset=(0.4, 0))

# Q3 — Accept reward cut?
diamond(8.7, 5.1, 4.0, 1.0, 'Q3: Accept reward cut?')

# Q3 Yes → Accept
arrow(6.7, 5.1, 4.0, 4.0, label='YES', color=NEUTRAL, label_color=NEUTRAL, label_offset=(-0.2, 0))

box(4.0, 3.1, 3.7, 1.6,
    'OPTION 1 — Accept cut\n\nReward falls to min(1, L·ρ)\nof V1  (7 % at L=100,\nmedian retail)\nDelegators likely leave',
    fontsize=8.5, fontweight='normal', fc=NEUTRAL, color='white', rounding=0.15)

# Q3 No → Exit
arrow(8.7, 4.6, 8.7, 3.75, label='NO', color=RED, label_color=RED, label_offset=(0.3, 0))

box(8.7, 3.0, 3.5, 1.4,
    'OPTION 4 — Exit\n\nRetire the pool\nDelegators disperse\n§3.1 attrition',
    fontsize=8.5, fontweight='normal', fc=RED, color='white', rounding=0.15)

# Bottom note
ax.text(6.5, 1.3,
        'Only options 1 and 4 are available to every operator.\n'
        'Options 2 and 3 depend on having capital to lock (POL.O4.F3: 41/48 saturation-scale MPOs\n'
        'already decline, revealed preference) or on accepting a smaller pool in a clipped market.',
        ha='center', va='center', fontsize=9.5, color=NEUTRAL, fontweight='normal',
        bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=10, boxstyle='round,pad=0.4'))

# Title
ax.text(6.5, 10.75,
        'Operator decision tree — the four response paths under CIP-0050',
        ha='center', va='center', fontsize=13, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_10_operator_decision_tree.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
