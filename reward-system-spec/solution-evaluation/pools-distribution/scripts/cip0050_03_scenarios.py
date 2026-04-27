#!/usr/bin/env python3
"""
Figure 3 — Three scenarios side by side. Reward preserved at L=100 for:
  A: compliant small pool (ρ = 2 %)
  B: median retail pool (ρ = 0.07 %)
  C: saturated pool (ρ = 1.3 %)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
NEUTRAL = '#4a4a4a'

labels = [
    'A: compliant small\nσ=5 M, ρ=2 %',
    'B: median retail\nσ=15 M, ρ=0.07 %',
    'C: saturated\nσ=77 M, ρ=1.3 %',
]
values = [100, 7, 100]
colors = [NEUTRAL, RED, NEUTRAL]

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
bars = ax.bar(labels, values, color=colors, width=0.55, edgecolor='black', linewidth=0.7)

for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f'{v} %',
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            color=RED if v < 50 else 'black')

# Annotation for scenario B
ax.annotate('93 % cut\n(the median mainnet pool)',
            xy=(1, 7), xytext=(1.3, 55),
            fontsize=10, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

ax.set_ylabel('% of V1 reward preserved under CIP-0050', fontsize=11)
ax.set_title('Pool reward preserved at L = 100 — three scenarios',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 115)
ax.axhline(100, color='black', linestyle=':', linewidth=1, alpha=0.45)
ax.text(2.45, 101, 'V1 baseline', fontsize=9, color='black', va='bottom', ha='right')
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_03_scenarios.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
