#!/usr/bin/env python3
"""
Figure 2 (CIP-0037) — side-by-side overlay of CIP-0037 and CIP-0050
saturation curves, showing they are the SAME primitive with CIP-0037
adding a floor at e · orig_sat.

X axis: pledge p (k ADA).
Y axis: reward-eligible stake cap (M ADA), for a large pool
        (σ ≥ orig_sat, so σ does not bind).

Two panels:
  (a) At reference parameters (CIP-0037: ℓ=125; CIP-0050: L=100)
  (b) Overlaid with matched leverage (both at L=ℓ=125) to isolate
      the floor as the sole structural difference
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
BLUE = '#2C4FFA'
GREEN = '#2ecc71'
NEUTRAL = '#4a4a4a'

SUPPLY = 33_719_282_563
K = 500
ORIG_SAT = SUPPLY / K
E = 0.2

def cip50(p, L):
    return np.minimum(ORIG_SAT, L * p)

def cip37(p, ell, e=E):
    floor = e * ORIG_SAT
    return np.minimum(ORIG_SAT, np.maximum(floor, ell * p))

p = np.linspace(0, 900_000, 2000)

fig, axes = plt.subplots(1, 2, figsize=(14.5, 6.0), dpi=150, sharey=True)

# -----------------------------------------------------------------
# Panel (a) — reference parameters: CIP-0037 ℓ=125, CIP-0050 L=100
# -----------------------------------------------------------------
ax = axes[0]
s50 = cip50(p, 100) / 1e6
s37 = cip37(p, 125) / 1e6

ax.plot(p/1000, s50, color=RED, linewidth=2.3, label='CIP-0050 (L=100)', zorder=5)
ax.plot(p/1000, s37, color=BLUE, linewidth=2.3, label='CIP-0037 (ℓ=125, e=0.2)', zorder=5)

# Fill the floor gap where they differ
mask = s37 > s50
ax.fill_between(p/1000, s50, s37, where=mask, color=DAWN, alpha=0.25,
                label='Floor + leverage gap')

ax.axhline(ORIG_SAT/1e6, color=NEUTRAL, linestyle='--', linewidth=1, alpha=0.6)
ax.text(880, ORIG_SAT/1e6 + 1.5, 'orig_sat (V1 cap)',
        ha='right', va='bottom', fontsize=9, color=NEUTRAL)

ax.axhline(E*ORIG_SAT/1e6, color=RED, linestyle=':', linewidth=1, alpha=0.5)
ax.text(880, E*ORIG_SAT/1e6 + 1.2, f'floor = {E*ORIG_SAT/1e6:.1f} M',
        ha='right', va='bottom', fontsize=9, color=RED)

ax.set_xlabel('Pool pledge  p  (k ADA)', fontsize=11)
ax.set_ylabel('Saturation / stake cap  (M ADA)', fontsize=11)
ax.set_title('(a) Reference defaults — different leverage constants',
             fontsize=11.5, fontweight='bold')
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.93)
ax.grid(axis='both', linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
ax.set_xlim(0, 900)
ax.set_ylim(0, 82)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# -----------------------------------------------------------------
# Panel (b) — matched leverage: both at L = ℓ = 125
# -----------------------------------------------------------------
ax = axes[1]
s50_matched = cip50(p, 125) / 1e6
s37_matched = cip37(p, 125) / 1e6

ax.plot(p/1000, s50_matched, color=RED, linewidth=2.3,
        label='CIP-0050 (L=125, no floor)', zorder=5)
ax.plot(p/1000, s37_matched, color=BLUE, linewidth=2.3,
        label='CIP-0037 (ℓ=125, e=0.2)', zorder=5)

mask2 = s37_matched > s50_matched
ax.fill_between(p/1000, s50_matched, s37_matched, where=mask2,
                color=GREEN, alpha=0.25,
                label='Floor — the sole structural difference')

ax.axhline(ORIG_SAT/1e6, color=NEUTRAL, linestyle='--', linewidth=1, alpha=0.6)
ax.axhline(E*ORIG_SAT/1e6, color=RED, linestyle=':', linewidth=1, alpha=0.5)

# Annotate the floor-exit crossover
p_floor_exit = E*ORIG_SAT/125
ax.annotate(f'floor exit\np = {p_floor_exit/1000:.0f} k',
            xy=(p_floor_exit/1000, E*ORIG_SAT/1e6),
            xytext=(p_floor_exit/1000 + 120, 25),
            fontsize=9.5, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=1))

ax.set_xlabel('Pool pledge  p  (k ADA)', fontsize=11)
ax.set_title('(b) Matched leverage — CIP-0037 = CIP-0050 + floor',
             fontsize=11.5, fontweight='bold')
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.93)
ax.grid(axis='both', linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
ax.set_xlim(0, 900)
ax.set_ylim(0, 82)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.suptitle('CIP-0037 vs CIP-0050 — same primitive, CIP-0037 adds a floor',
             fontsize=13, fontweight='bold', y=1.00)
plt.tight_layout()
out_path = os.path.join(OUT, 'cip0037_02_vs_cip0050.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
