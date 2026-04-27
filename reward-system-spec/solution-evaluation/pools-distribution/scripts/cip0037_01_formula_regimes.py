#!/usr/bin/env python3
"""
Figure 1 (CIP-0037) — sat(p) as clamp(ℓ·p, e·orig_sat, orig_sat).

Plots the three regimes (floor / slope / ceiling) against pledge,
with vertical markers at the floor-exit (108 k) and ceiling-entry (540 k)
thresholds at reference parameters.
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

# Reference CIP-0037 parameters
SUPPLY = 33_719_282_563
K = 500
ORIG_SAT = SUPPLY / K               # 67.44 M
E = 0.2
ELL = 125

FLOOR_VAL = E * ORIG_SAT            # 13.49 M
P_FLOOR_EXIT = FLOOR_VAL / ELL      # 108 k
P_CEILING = ORIG_SAT / ELL          # 540 k

def sat(p):
    return np.minimum(ORIG_SAT, np.maximum(FLOOR_VAL, ELL * p))

# Pledge range: 0 to 900 k ADA
p = np.linspace(0, 900_000, 2000)
s = sat(p) / 1e6  # in millions of ADA

fig, ax = plt.subplots(figsize=(11, 6.2), dpi=150)

# Shaded regime bands
ax.axvspan(0, P_FLOOR_EXIT / 1000, color=RED, alpha=0.10, label='_nolegend_')
ax.axvspan(P_FLOOR_EXIT / 1000, P_CEILING / 1000, color=DAWN, alpha=0.10, label='_nolegend_')
ax.axvspan(P_CEILING / 1000, 900, color=GREEN, alpha=0.10, label='_nolegend_')

# The curve
ax.plot(p / 1000, s, color='black', linewidth=2.6, zorder=5)

# Horizontal reference lines
ax.axhline(FLOOR_VAL / 1e6, color=RED, linestyle='--', linewidth=1.2, alpha=0.8)
ax.axhline(ORIG_SAT / 1e6, color=GREEN, linestyle='--', linewidth=1.2, alpha=0.8)

# Vertical markers
ax.axvline(P_FLOOR_EXIT / 1000, color=NEUTRAL, linestyle=':', linewidth=1.0, alpha=0.7)
ax.axvline(P_CEILING / 1000, color=NEUTRAL, linestyle=':', linewidth=1.0, alpha=0.7)

# Labels on the y-axis lines
ax.text(880, FLOOR_VAL / 1e6 + 1.8,
        f'floor  e · orig_sat = {FLOOR_VAL/1e6:.2f} M',
        ha='right', va='bottom', fontsize=10, color=RED, fontweight='bold')
ax.text(880, ORIG_SAT / 1e6 + 1.8,
        f'ceiling  orig_sat = {ORIG_SAT/1e6:.2f} M',
        ha='right', va='bottom', fontsize=10, color='#1e6b1e', fontweight='bold')

# Regime labels — placed at distinct y-levels so the formula box (top-left)
# never overlaps them. FLOOR in the lower-left band (above floor line, below
# slope crossing), SLOPE rides along the slope, CEILING at the top of its band.
ax.text(P_FLOOR_EXIT / 2 / 1000, 6.5, 'FLOOR',
        ha='center', va='center', fontsize=11, fontweight='bold', color=RED,
        bbox=dict(facecolor='white', edgecolor=RED, pad=4, boxstyle='round,pad=0.3'))
ax.text(360, 32, 'SLOPE  sat = ℓ · p',
        ha='center', va='center', fontsize=11, fontweight='bold', color=DAWN,
        rotation=42,
        bbox=dict(facecolor='white', edgecolor=DAWN, pad=4, boxstyle='round,pad=0.3'))
ax.text((P_CEILING + 900_000) / 2 / 1000, 75, 'CEILING',
        ha='center', va='center', fontsize=11, fontweight='bold', color='#1e6b1e',
        bbox=dict(facecolor='white', edgecolor=GREEN, pad=4, boxstyle='round,pad=0.3'))

# Annotate threshold values on x-axis
ax.annotate(f'p_floor\n{P_FLOOR_EXIT/1000:.0f} k ADA',
            xy=(P_FLOOR_EXIT / 1000, 0), xytext=(P_FLOOR_EXIT / 1000 + 45, 10),
            fontsize=9.5, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=1))
ax.annotate(f'p_100%\n{P_CEILING/1000:.0f} k ADA',
            xy=(P_CEILING / 1000, ORIG_SAT / 1e6), xytext=(P_CEILING / 1000 - 180, 52),
            fontsize=9.5, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=1))

# Data points from CIP-0037's own example table
cip_points = [
    (50_000,  FLOOR_VAL),
    (100_000, FLOOR_VAL),
    (150_000, 18_750_000),
    (250_000, 31_250_000),
    (500_000, 62_500_000),
    (750_000, ORIG_SAT),
]
for px, py in cip_points:
    ax.plot(px / 1000, py / 1e6, 'o', markersize=6,
            markerfacecolor=BLUE, markeredgecolor='black', markeredgewidth=0.6, zorder=6)

# Legend box with equations — bottom-right corner, in the empty area
# below the ceiling-region curve. Free of all regime labels and curve elements.
eq_box = (
    'CIP-0037 formula (simplified):\n'
    '  sat(p) = clamp(ℓ · p,  e · orig_sat,  orig_sat)\n'
    'Reference: e = 0.2,  ℓ = 125,  k = 500\n'
    'Blue dots: CIP-0037 §Specification example'
)
ax.text(0.98, 0.04, eq_box,
        transform=ax.transAxes,
        ha='right', va='bottom', fontsize=9.5, fontweight='normal',
        bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))

ax.set_xlabel('Pool pledge  p  (k ADA)', fontsize=11)
ax.set_ylabel('Saturation cap  sat(p)  (M ADA)', fontsize=11)
ax.set_title('CIP-0037 saturation curve — three regimes: floor, slope, ceiling',
             fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 900)
ax.set_ylim(0, 82)
ax.grid(axis='both', linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out_path = os.path.join(OUT, 'cip0037_01_formula_regimes.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
