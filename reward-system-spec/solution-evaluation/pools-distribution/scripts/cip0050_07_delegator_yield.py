#!/usr/bin/env python3
"""
Figure 7 — Delegator annual yield on a 10 000 ADA delegation, V1 baseline
vs three CIP-0050 scenarios at L=100.

Yield in ADA/yr; hollow-pool assumption (pledge bonus negligible);
per-ADA gross yield ≈ 2.275 %/yr constant below saturation (pool-
distribution §4.1.2.1); the scenario's reward multiplier min(1, L·ρ)
applies uniformly to every delegator ADA.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
NEUTRAL = '#4a4a4a'
LIGHT = '#7a7a7a'

DELEG_ADA = 10_000
GROSS_YIELD = 0.02275  # 2.275%/yr

# Scenarios — using reward multiplier from §2.2 of cip-0050.md
# V1 baseline: multiplier = 1, ignoring fee cut for the comparison
# (keeping it simple — the fee-split ratio would scale uniformly)
scenarios = [
    ('V1 baseline\n(no CIP-0050)',                     1.00),
    ('A: compliant\n(ρ=2 %, σ=5 M)',                   1.00),
    ('B: median retail\n(ρ=0.07 %, σ=15 M)',           0.07),
    ('C: saturated\n(ρ=1.3 %, σ=77 M)',                1.00),
]

labels = [s[0] for s in scenarios]
yields = [DELEG_ADA * GROSS_YIELD * mult for _, mult in scenarios]
# Scenario C takes a slight fee-side haircut; A, C ≈ 226 rather than 227
# Using multiplier interpretation: keep all at 227 for V1 behaviour,
# Scenario B drops to ~16. We do NOT overclaim — keep hollow pool simple.
colors = [LIGHT, NEUTRAL, RED, NEUTRAL]

fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
bars = ax.bar(labels, yields, color=colors, edgecolor='black', linewidth=0.7, width=0.55)

for bar, v in zip(bars, yields):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 4,
            f'{v:.0f} ₳/yr',
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            color=RED if v < 100 else 'black')

# Annotate scenario B drop
ax.annotate('93 % yield cut\n→ ~16 ₳/yr  ($4 at $0.25/ADA)',
            xy=(2, yields[2]), xytext=(2.5, 110),
            fontsize=10, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

ax.set_ylabel('Annual yield on 10 000 ADA  (ADA)', fontsize=11)
ax.set_title('Delegator annual yield — V1 vs CIP-0050 scenarios at L = 100  (hollow-pool approximation)',
             fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 260)
ax.grid(axis='y', linestyle=':', alpha=0.4)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0050_07_delegator_yield.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
