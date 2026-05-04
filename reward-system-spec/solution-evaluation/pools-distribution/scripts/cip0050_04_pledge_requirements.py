#!/usr/bin/env python3
"""
Figure 4 — Minimum absolute pledge required to escape CIP-0050 clipping,
by canonical pool-size tier, at L=100 and L=10.

For each tier, p_min = σ / L.  Shown in kilo-ADA on a log scale so the
range across tiers and L values is legible.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'

tiers = [
    ('Sub-reliable\n(2 M)',          2_000_000),
    ('Healthy\n(15 M)',           15_000_000),
    ('Large-healthy\n(50 M)',     50_000_000),
    ('Near-saturation\n(67 M)',   67_000_000),
    ('Saturated\n(77 M)',         77_000_000),
]

labels = [t[0] for t in tiers]
sigmas = np.array([t[1] for t in tiers])

p_L100 = sigmas / 100 / 1000  # kilo-ADA
p_L10 = sigmas / 10 / 1000    # kilo-ADA

x = np.arange(len(tiers))
w = 0.38

fig, ax = plt.subplots(figsize=(10, 5.8), dpi=150)
b1 = ax.bar(x - w/2, p_L100, w, color=DAWN, edgecolor='black', linewidth=0.6,
            label='L = 100  (pledge ratio ≥ 1 %)')
b2 = ax.bar(x + w/2, p_L10, w, color=RED, edgecolor='black', linewidth=0.6,
            label='L = 10   (pledge ratio ≥ 10 %)')

for bar, v in zip(b1, p_L100):
    ax.text(bar.get_x() + bar.get_width() / 2, v * 1.12,
            f'{v:,.0f} k' if v >= 1 else f'{v*1000:.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar, v in zip(b2, p_L10):
    ax.text(bar.get_x() + bar.get_width() / 2, v * 1.12,
            f'{v:,.0f} k' if v >= 1 else f'{v*1000:.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_yscale('log')
ax.set_ylim(10, 30_000)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel('Minimum pledge to escape clipping  (k ADA, log scale)', fontsize=11)
ax.set_title('Minimum absolute pledge required to keep full V1 reward under CIP-0050',
             fontsize=12, fontweight='bold', pad=12)
ax.legend(loc='upper left', fontsize=10, framealpha=0.96, edgecolor='black')
ax.grid(True, axis='y', which='both', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_04_pledge_requirements.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
