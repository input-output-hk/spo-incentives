#!/usr/bin/env python3
"""
Figure 2 — The reward multiplier curve min(1, L·ρ) vs within-pool
pledge ratio, for three L values (10, 100, 1000).

Shows the 'pledge cliff' that CIP-0050 creates at ρ = 1/L, and
marks where the mainnet stake-weighted median pool sits
(ρ = 0.07% per POL.O2.F1).
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
BLUE = '#2C4FFA'
NEUTRAL = '#4a4a4a'
LIGHT_GRID = '#e8e8e8'

# Sweep pledge ratio from 0 to 15%, log-linear
rho = np.linspace(0, 15, 2000)  # percent
multiplier_L100 = np.minimum(1.0, 100 * rho / 100)  # L * rho (rho in %, so /100)
multiplier_L25 = np.minimum(1.0, 25 * rho / 100)
multiplier_L10 = np.minimum(1.0, 10 * rho / 100)
multiplier_L1000 = np.minimum(1.0, 1000 * rho / 100)

fig, ax = plt.subplots(figsize=(10, 5.8), dpi=150)

ax.plot(rho, multiplier_L1000 * 100, color=BLUE, linewidth=2.4,
        label='L = 1 000  (cliff at ρ = 0.1 %)')
ax.plot(rho, multiplier_L100 * 100, color=RED, linewidth=2.8,
        label='L = 100    (cliff at ρ = 1 %,  CIP sweet-spot high)')
ax.plot(rho, multiplier_L25 * 100, color=DAWN, linewidth=2.4,
        label='L = 25      (cliff at ρ = 4 %)')
ax.plot(rho, multiplier_L10 * 100, color=NEUTRAL, linewidth=2.4,
        label='L = 10      (cliff at ρ = 10 %, CIP sweet-spot low)')

# Mark the median mainnet pool
median_rho = 0.07
ax.axvline(median_rho, color='black', linestyle='--', linewidth=1, alpha=0.55)
ax.text(median_rho + 0.15, 85,
        'Stake-weighted\nmedian mainnet pool\n(ρ = 0.07 %, POL.O2.F1)',
        fontsize=9, color='black',
        bbox=dict(facecolor='white', edgecolor='black', alpha=0.92, boxstyle='round,pad=0.35'))

# Mark the median pool's reward at L=100
ax.plot(median_rho, 7, marker='o', color=RED, markersize=10,
        markeredgecolor='black', markeredgewidth=1, zorder=5)
ax.annotate('Median pool at L=100:\n7 % of V1 reward',
            xy=(median_rho, 7), xytext=(2.2, 22),
            fontsize=10, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.4))

ax.set_xlabel('Within-pool pledge ratio  ρ = p / σ  (%)', fontsize=11)
ax.set_ylabel('Reward multiplier min(1, L·ρ)  —  % of V1 reward preserved', fontsize=11)
ax.set_title('CIP-0050 reward multiplier vs within-pool pledge ratio',
             fontsize=13, fontweight='bold', pad=12)
ax.set_xlim(0, 15)
ax.set_ylim(0, 105)
ax.grid(True, linestyle=':', alpha=0.5, color=LIGHT_GRID)
ax.set_axisbelow(True)
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.96, edgecolor='black')
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_02_reward_curve.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
