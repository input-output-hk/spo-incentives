#!/usr/bin/env python3
"""
Figure 5 — MPO fleet capacity vs number of pools, for a fixed 1 M ₳
pledge budget at L=100.

Illustrates CIP-0050.S1.F2 — pool-splitting is revenue-neutral above
the threshold where L·p (per pool) < 1/k. Fleet-wide reward-eligible
stake plateaus at L·P = 100 M ADA regardless of how pledge is split.
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
NEUTRAL = '#4a4a4a'

L = 100
P = 1_000_000  # total pledge budget in ADA
z0 = 77_000_000  # V1 saturation in ADA

n_pools = [1, 2, 4, 10, 100]
fleet_caps = []
binding_reason = []
for N in n_pools:
    p_per_pool = P / N
    pool_cap = min(z0, L * p_per_pool)  # min of V1 sat and pledge cap
    fleet = pool_cap * N / 1e6  # M ADA
    fleet_caps.append(fleet)
    binding_reason.append('V1 sat (1/k)' if L * p_per_pool >= z0 else 'L · p (pledge cap)')

colors = [DAWN if r.startswith('V1') else RED for r in binding_reason]

fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
bars = ax.bar([f'{n} pool{"s" if n > 1 else ""}' for n in n_pools],
              fleet_caps, color=colors, edgecolor='black', linewidth=0.7, width=0.55)

for bar, v, reason in zip(bars, fleet_caps, binding_reason):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 2.2,
            f'{v:.0f} M\n({reason} binds)',
            ha='center', va='bottom', fontsize=9, fontweight='bold',
            color='black')

# Plateau line
ax.axhline(L * P / 1e6, color=RED, linestyle='--', linewidth=1.5, alpha=0.75)
ax.text(len(n_pools) - 0.3, L * P / 1e6 + 4,
        f'Fleet cap = L · P = {L * P / 1e6:.0f} M ADA',
        fontsize=10, color=RED, fontweight='bold', ha='right',
        bbox=dict(facecolor='white', edgecolor=RED, alpha=0.95, boxstyle='round,pad=0.3'))

ax.set_ylabel('Total fleet reward-eligible stake  (M ADA)', fontsize=11)
ax.set_title('MPO fleet capacity vs number of pools  (1 M ₳ pledge budget, L = 100)',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 135)
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_05_mpo_fleet.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
