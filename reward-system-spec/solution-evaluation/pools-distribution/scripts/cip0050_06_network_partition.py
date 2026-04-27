#!/usr/bin/env python3
"""
Figure 6 — Network-wide partition of productive stake under CIP-0050 at L=100.

Horizontal stacked-bar showing which segments are unaffected vs clipped.
Stake volumes from operator-delegator §4.3.3 (custodial decomposition)
and POL.O5.F2 / POL.O2.F1 (retail compliance).
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
NEUTRAL_GREEN = '#2ecc71'
NEUTRAL_DARK = '#4a4a4a'

segments = [
    ('Custodial-by-pledge\n(10 ent. · 36 pools)',     1.59, NEUTRAL_GREEN, 'Unaffected'),
    ('Custodial-by-extraction\n(57 ent. · 79 pools)', 2.04, RED,           'Clipped to ~0'),
    ('Custodial-by-delegation\n(15 ent. · 28 pools)', 0.92, DAWN,          'Mixed'),
    ('Retail compliant\n(ρ ≥ 1 %)',                    0.99, NEUTRAL_GREEN, 'Unaffected'),
    ('Retail non-compliant\n(ρ < 1 %)',               16.0, RED,           'Clipped 0–93 %'),
]

labels = [s[0] for s in segments]
stakes = [s[1] for s in segments]
colors = [s[2] for s in segments]
effects = [s[3] for s in segments]

fig, ax = plt.subplots(figsize=(11, 5.8), dpi=150)
bars = ax.bar(labels, stakes, color=colors, edgecolor='black', linewidth=0.7, width=0.6)

for bar, v, eff in zip(bars, stakes, effects):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.2,
            f'{v} B ₳\n({eff})',
            ha='center', va='bottom', fontsize=9.5, fontweight='bold')

total_clipped = sum(s for s, c in zip(stakes, colors) if c == RED)
ax.annotate(f'Clipped: {total_clipped:.2f} B ADA\n({total_clipped / sum(stakes) * 100:.0f} % of productive stake)',
            xy=(4, 16.0), xytext=(2.7, 13.5),
            fontsize=11, color=RED, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor=RED, alpha=0.95, boxstyle='round,pad=0.4'))

ax.set_ylabel('Stake  (B ADA)', fontsize=11)
ax.set_title('Network-wide effect of CIP-0050 at L = 100 — productive mainnet partition',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 19)
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_06_network_partition.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
