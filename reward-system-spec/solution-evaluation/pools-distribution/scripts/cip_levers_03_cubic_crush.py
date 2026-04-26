#!/usr/bin/env python3
"""
Figure 3 (cip_levers) — visualising the cubic ν³ crush.

The pledge bonus at full self-pledge collapses to A(ν, ν) = ν³.  A cube of
a sub-unit number is a destruction operator: 0.03³ = 0.000027.  This figure
shows what the cubic actually does and what alternatives would look like.

Panel (a): A(ν, ν) curves on LINEAR axes for ν ∈ [0, 1] — the cubic crush
           is visually obvious because ν³ is essentially flat-zero until
           ν > 0.5, then it leaps to 1.

Panel (b): same curves on LOG axes — shows the multiplicative gap at small
           ν.  Bob, Charles, Alice are marked on each curve so the reader
           sees how each operator would be paid under each kernel.

Panel (c): bar chart — Bob's bonus under the current cubic vs three
           alternatives (ν², ν, scale-free π/ν).  The current rule pays
           Bob 14 ADA/year; a linear A would pay him 462 000 ADA/year.
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
GREEN = '#1e6b1e'
NEUTRAL = '#4a4a4a'
GREY = '#808080'

SUPPLY = 33_719_282_563
K = 500
ORIG_SAT = SUPPLY / K
A0 = 0.3
LAM_PLEDGE = A0 / (1.0 + A0)
P_MAX = 31_082
EPY = 73

# Three operators, full self-pledge
ops = [
    ('Bob',     2_000_000,   '#909090'),
    ('Charles', 15_000_000,  DAWN),
    ('Alice',   67_000_000,  RED),
]

nu_axis = np.linspace(0.001, 1.0, 500)
A_cubic = nu_axis ** 3                # current
A_quad  = nu_axis ** 2                # alt 1
A_lin   = nu_axis                     # alt 2 — "fair share"
# Scale-free: A(ν, ν) = 1 (independent of pool size) — clip at 1
A_flat  = np.ones_like(nu_axis)

fig = plt.figure(figsize=(16.5, 11.5), dpi=150)
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], width_ratios=[1.0, 1.0],
                     hspace=0.36, wspace=0.28,
                     bottom=0.10, top=0.94)

# ===================================================================
# Panel (a) — LINEAR axes, ν³ vs alternatives
# ===================================================================
ax = fig.add_subplot(gs[0, 0])

ax.plot(nu_axis, A_cubic, color=RED, lw=2.8, label='current  A(ν, ν) = ν³')
ax.plot(nu_axis, A_quad, color=DAWN, lw=2.2, ls='--', label='alt. quadratic  ν²')
ax.plot(nu_axis, A_lin, color=GREEN, lw=2.2, ls='-.', label='alt. linear  ν   ("fair share")')

# Mark the three operators
for name, sigma, color in ops:
    nu = sigma / ORIG_SAT
    if nu > 1: nu = 1
    ax.plot(nu, nu**3, 'o', markersize=10,
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.8, zorder=10)

# Annotations — show ν values for each
ax.annotate('Bob\nν = 0.03\n(2 M pool)',
            xy=(0.03, 0.001), xytext=(0.16, 0.18),
            fontsize=9, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=0.9))
ax.annotate('Charles\nν = 0.22\n(15 M pool)',
            xy=(0.22, 0.011), xytext=(0.32, 0.30),
            fontsize=9, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=0.9))
ax.annotate('Alice\nν ≈ 1\n(67 M pool)',
            xy=(1.0, 1.0), xytext=(0.65, 0.85),
            fontsize=9, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=0.9))

ax.set_xlabel('Pool size  ν = σ / orig_sat   (0 = empty pool, 1 = saturated)', fontsize=10.5)
ax.set_ylabel('A(ν, ν)  at full self-pledge', fontsize=10.5)
ax.set_title('(a) The cubic ν³ on LINEAR axes — the curve hugs zero until ν ≈ 0.5',
             fontsize=11, fontweight='bold')
ax.legend(loc='upper left', fontsize=9.5, framealpha=0.93)
ax.grid(linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
ax.set_xlim(0, 1.05)
ax.set_ylim(0, 1.05)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# ===================================================================
# Panel (b) — LOG axes, same curves
# ===================================================================
ax = fig.add_subplot(gs[0, 1])

ax.plot(nu_axis, A_cubic, color=RED, lw=2.8, label='current  ν³')
ax.plot(nu_axis, A_quad, color=DAWN, lw=2.2, ls='--', label='quadratic  ν²')
ax.plot(nu_axis, A_lin, color=GREEN, lw=2.2, ls='-.', label='linear  ν')

for name, sigma, color in ops:
    nu = sigma / ORIG_SAT
    if nu > 1: nu = 1
    ax.plot(nu, nu**3, 'o', markersize=9,
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.7, zorder=10)
    ax.text(nu, nu**3 * 0.45, name,
            ha='center', va='top', fontsize=8.6, color=color, fontweight='bold')

# Highlight the gap between cubic and linear at Bob's ν — annotation moved to
# the upper-left empty area on log axes (clear of all curves)
nu_bob = 2e6 / ORIG_SAT
ax.annotate('', xy=(nu_bob, nu_bob), xytext=(nu_bob, nu_bob**3),
            arrowprops=dict(arrowstyle='<->', color=RED, lw=1.8))
ax.annotate(f'For Bob:\ncubic gives {nu_bob**3:.1e}\nlinear would give {nu_bob:.3f}\nratio: {nu_bob/nu_bob**3:,.0f}×',
            xy=(nu_bob, np.sqrt(nu_bob * nu_bob**3)),
            xytext=(0.012, 0.4),
            fontsize=9, color=RED, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor=RED, pad=4, boxstyle='round,pad=0.3'),
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.0))

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(0.005, 1.1)
ax.set_ylim(1e-7, 2)
ax.set_xlabel('Pool size  ν = σ / orig_sat   (log)', fontsize=10.5)
ax.set_ylabel('A(ν, ν)  at full self-pledge   (log)', fontsize=10.5)
ax.set_title('(b) Same curves on LOG axes — gap is multiplicative, not additive',
             fontsize=11, fontweight='bold')
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.93)
ax.grid(True, which='both', linestyle=':', alpha=0.30)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# ===================================================================
# Panel (c) — Bob's bonus under current vs alternative kernels (bar chart)
# ===================================================================
ax = fig.add_subplot(gs[1, :])

nu_bob = 2e6 / ORIG_SAT
# Compute Bob's bonus under each kernel for FULL self-pledge
kernels = [
    ('current\nA = ν³', nu_bob**3, RED),
    ('alt. quadratic\nA = ν²', nu_bob**2, DAWN),
    ('alt. linear\nA = ν   ("fair share")', nu_bob, GREEN),
    ('alt. scale-free\nA = 1  (max bonus)', 1.0, BLUE),
]
labels, A_values, colors = zip(*kernels)
bonuses = np.array([LAM_PLEDGE * a * P_MAX * EPY for a in A_values])

bars = ax.bar(labels, bonuses, color=colors, edgecolor='black', linewidth=0.8, width=0.62)

for bar, v in zip(bars, bonuses):
    if v < 100:
        text = f'{v:,.1f} ₳/yr\n≈ ${v*0.25:,.2f}'
    elif v < 1e6:
        text = f'{v:,.0f} ₳/yr\n≈ ${v*0.25:,.0f}'
    else:
        text = f'{v:,.0f} ₳/yr\n≈ ${v*0.25/1e6:,.2f} M'
    ax.text(bar.get_x() + bar.get_width()/2, v * 1.6,
            text, ha='center', va='bottom',
            fontsize=10.5, fontweight='bold',
            color='black')

# Reference: passive delegation yield on Bob's 2M
passive = 2_000_000 * 0.023            # 2.3 % yr
ax.axhline(passive, color=BLUE, ls='--', lw=1.5, alpha=0.85)
ax.text(3.4, passive * 0.7,
        f'passive-delegation yield on Bob\'s 2 M:\n{passive:,.0f} ₳/yr  (the opportunity cost)',
        ha='right', va='top', fontsize=9.5, color=BLUE, fontweight='bold')

ax.set_yscale('log')
ax.set_ylim(1, 5e6)
ax.set_ylabel('Bob\'s yearly pledge bonus  (ADA / year, log scale)', fontsize=10.5)
ax.set_title('(c) Bob\'s bonus for fully self-pledging his 2 M pool, under different A kernels',
             fontsize=11.5, fontweight='bold')
ax.grid(axis='y', linestyle=':', alpha=0.4, which='both')
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Long takeaway moved to figure footer)

plt.suptitle('The cubic crush — why ν³ structurally suppresses small-pool pledge',
             fontsize=13.5, fontweight='bold', y=0.985)

# Footer takeaway — placed BELOW the panels, no chart overlap
fig.text(0.5, 0.025,
         'Under the current cubic, Bob\'s 2 M of locked pledge yields 14 ₳/yr — less than 0.001 % of his pledge.   '
         'Under a linear "fair-share" A, the same act would yield 462 000 ₳/yr — roughly his pool\'s share of the network.',
         ha='center', va='bottom',
         fontsize=10.5, fontweight='bold', color=NEUTRAL,
         bbox=dict(facecolor='#fff3f3', edgecolor=RED, pad=6, boxstyle='round,pad=0.4'))

out_path = os.path.join(OUT, 'cip_levers_03_cubic_crush.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
print('---')
for label, A_val, _ in kernels:
    bonus = LAM_PLEDGE * A_val * P_MAX * EPY
    print(f'  {label.replace(chr(10), " "):45s}  bonus = {bonus:>15,.1f} ADA/yr')
