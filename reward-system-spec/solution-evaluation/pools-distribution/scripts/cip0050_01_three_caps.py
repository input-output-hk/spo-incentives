#!/usr/bin/env python3
"""
Figure 1 — Which cap binds under CIP-0050 for the median retail pool.

Shows the three candidate caps (σ, 1/k, L·p) as bars, highlights
the minimum (which is L·p for the median retail pool at L=100).

Scenario: σ=15 M ADA (Healthy tier), pledge ratio 0.07% (POL.O2.F1
stake-weighted median), L=100.
  p = 0.07% × 15M = 10.5 k ADA
  L·p = 100 × 10.5 k = 1.05 M ADA
  1/k × Supply at k=500 ≈ 77 M ADA
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

# IOG palette
RED = '#E52321'
DAWN = '#EC641D'
NEUTRAL = '#4a4a4a'
LIGHT = '#dcdcdc'

labels = ['σ\n(actual stake)', '1/k\n(V1 saturation)', 'L · p\n(NEW pledge cap)']
values = [15.0, 77.0, 1.05]  # millions of ADA
# Highlight the smallest bar (the one that binds)
binding_idx = values.index(min(values))
colors = [NEUTRAL, NEUTRAL, NEUTRAL]
colors[binding_idx] = RED

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor='black', linewidth=0.7)

# Annotate each bar with its value
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f'{v:.2f} M',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Annotate the binding bar
ax.annotate('σ\u2032 = min of the three = 1.05 M\n(L · p binds — stake clipped to 7% of actual)',
            xy=(binding_idx, values[binding_idx]),
            xytext=(binding_idx + 0.4, 35),
            fontsize=10, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

ax.set_ylabel('ADA (millions)', fontsize=11)
ax.set_title('Which cap binds? — Median retail pool (σ=15 M, ρ=0.07 %, L=100)',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 90)
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_01_three_caps.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
