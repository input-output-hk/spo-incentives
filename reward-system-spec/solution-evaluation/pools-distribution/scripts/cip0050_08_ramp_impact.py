#!/usr/bin/env python3
"""
Figure 8 — Impact of the CIP-recommended ramp on the stake-weighted
median mainnet pool (ρ = 0.07 %, POL.O2.F1) as L steps down.

V1 → L=10 000 activation → L=1 000 → L=100 target → optional L=25.
Reward multiplier = min(1, L · ρ).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
NEUTRAL = '#4a4a4a'

rho = 0.0007  # 0.07% = 0.0007 as ratio

stages = [
    ('V1 baseline',           None),
    ('Activation\nL=10 000',  10_000),
    ('Stage 1\nL=1 000',       1_000),
    ('Target\nL=100',            100),
    ('Optional\nL=25',            25),
]

labels = [s[0] for s in stages]
rewards_pct = []
for lbl, L in stages:
    if L is None:
        rewards_pct.append(100)
    else:
        rewards_pct.append(min(1.0, L * rho) * 100)

# Colours — neutral at V1 and where reform has little effect, red where severe
colors = []
for r in rewards_pct:
    if r >= 99:
        colors.append(NEUTRAL)
    elif r >= 50:
        colors.append(DAWN)
    else:
        colors.append(RED)

fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
bars = ax.bar(labels, rewards_pct, color=colors, edgecolor='black', linewidth=0.7, width=0.55)

for bar, v in zip(bars, rewards_pct):
    if v < 1:
        text = f'{v:.2f} %'
    elif v < 10:
        text = f'{v:.1f} %'
    else:
        text = f'{v:.0f} %'
    ax.text(bar.get_x() + bar.get_width() / 2, v + 2,
            text, ha='center', va='bottom', fontsize=11, fontweight='bold',
            color=RED if v < 50 else 'black')

# Draw connecting line to emphasise the ramp shape
ax.plot(range(len(labels)), rewards_pct, color='black', linewidth=1.2,
        linestyle=':', alpha=0.55, marker='o', markersize=5, zorder=3)

ax.set_ylabel('Reward preserved for median pool  (% of V1)', fontsize=11)
ax.set_title('CIP-0050 ramp impact on the stake-weighted median mainnet pool  (ρ = 0.07 %)',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 115)
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_08_ramp_impact.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
