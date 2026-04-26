#!/usr/bin/env python3
"""
Figure 4 (cip_levers) — STRUCTURAL anatomy of A(π, ν), before plugging
in any numbers.

Two structural pathologies to surface BEFORE the Bob/Charles/Alice scenarios:

Panel (a) — the valid domain of A is a TRIANGLE, not a rectangle.
            π ≤ ν is forced by the protocol (pledge cannot exceed stake),
            so half the formal domain is unreachable.  A well-designed
            two-variable function would not have this structural smell.

Panel (b) — A is NON-MONOTONE in π for any ν < 0.5.  At fixed ν, A is a
            concave parabola in π with maximum at π* = ν / (2(1−ν)).
            For ν < 0.5, the maximum sits INSIDE the valid domain — so
            increasing pledge BEYOND π* actually DECREASES the bonus.
            The formula punishes full self-pledge for any pool below
            half-saturation.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.lines import Line2D

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
BLUE = '#2C4FFA'
GREEN = '#1e6b1e'
NEUTRAL = '#4a4a4a'
GREY = '#808080'

def A_func(pi, nu):
    return pi * nu - pi**2 * (1 - nu)

fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.6), dpi=150,
                          gridspec_kw={'bottom': 0.22, 'top': 0.92})

# ====================================================================
# Panel (a) — the valid domain is a triangle
# ====================================================================
ax = axes[0]

# Invalid region (π > ν)
invalid_tri = Polygon([(0, 0), (1, 1), (0, 1)],
                      facecolor='#dddddd', edgecolor='none',
                      hatch='///', alpha=0.55, zorder=1)
ax.add_patch(invalid_tri)

# Valid region (π ≤ ν)
valid_tri = Polygon([(0, 0), (1, 1), (1, 0)],
                    facecolor='#e7f7e7', edgecolor=GREEN,
                    linewidth=1.5, alpha=0.65, zorder=2)
ax.add_patch(valid_tri)

# Diagonal π = ν
ax.plot([0, 1], [0, 1], color=GREEN, lw=2.5, zorder=4,
        label='π = ν   full self-pledge boundary')

# Region labels — kept compact to leave room for diagonal markers
ax.text(0.78, 0.28, 'VALID  (π ≤ ν)',
        ha='center', va='center', fontsize=11.5, color=GREEN,
        fontweight='bold',
        bbox=dict(facecolor='white', edgecolor=GREEN, pad=4, boxstyle='round,pad=0.3'))
ax.text(0.28, 0.78, 'INVALID  (π > ν)',
        ha='center', va='center', fontsize=11.5, color=NEUTRAL,
        fontweight='bold',
        bbox=dict(facecolor='white', edgecolor=NEUTRAL, pad=4, boxstyle='round,pad=0.3'))

# Mark mainnet operating zone (π/ν << 1, very low ratio)
mainnet_zone = Polygon([(0, 0), (0.0007, 0.001), (0.05, 1), (0, 1)],
                       facecolor=DAWN, edgecolor=DAWN, alpha=0.30, zorder=3)
# Simpler: mark a thin vertical strip near π = 0
ax.add_patch(Rectangle((0, 0), 0.005, 1, facecolor=DAWN, edgecolor='none',
                        alpha=0.55, zorder=3))
ax.text(0.015, 1.04, 'mainnet operating zone   (median  π/ν = 0.07 %)',
        ha='left', va='bottom', fontsize=8.8, color=DAWN, fontweight='bold')

# Three reference operators on the diagonal (full self-pledge)
operators = [
    ('Bob ν=0.03', 0.0297),
    ('Charles ν=0.22', 0.222),
    ('Alice ν=1.0', 1.00),
]
for name, nu in operators:
    ax.plot(nu, nu, 'o', markersize=8,
            markerfacecolor=RED, markeredgecolor='black', markeredgewidth=0.7,
            zorder=10)
    # Push labels to the lower-right of each marker, away from chart elements
    ax.text(nu + 0.04, nu - 0.06, name,
            fontsize=8.8, color=RED, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=1.5, alpha=0.9))

ax.set_xlim(-0.02, 1.10)
ax.set_ylim(-0.02, 1.12)
ax.set_xlabel('Stake saturation level   ν = σ / z₀', fontsize=10.5)
ax.set_ylabel('Pledge saturation level   π = p / z₀', fontsize=10.5)
ax.set_title('(a) The valid domain of A(π, ν) — a triangle, not a rectangle',
             fontsize=11.5, fontweight='bold')
ax.set_aspect('equal')
ax.grid(linestyle=':', alpha=0.30)
ax.set_axisbelow(True)
ax.legend(loc='upper left', fontsize=9.5, framealpha=0.93)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Long explanation moved to figure footer to avoid overlap)

# ====================================================================
# Panel (b) — A is NON-MONOTONE in π for ν < 0.5
# ====================================================================
ax = axes[1]

nu_levels = [
    (0.10, '#bababa'),
    (0.20, GREY),
    (0.30, DAWN),
    (0.50, '#2ecc71'),
    (0.70, BLUE),
    (1.00, RED),
]

for nu, color in nu_levels:
    # π only goes up to ν (valid domain)
    pi_valid = np.linspace(0, nu, 400)
    A_valid = A_func(pi_valid, nu)
    ax.plot(pi_valid, A_valid, color=color, lw=2.4,
            label=f'ν = {nu:.2f}')
    # Mark the boundary endpoint (π = ν, full self-pledge)
    ax.plot(nu, nu**3, 's', markersize=9,
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.8,
            zorder=10)
    # Mark the interior maximum if it exists in valid domain
    pi_star = nu / (2 * (1 - nu)) if nu < 0.5 else nu
    if nu < 0.5 and pi_star < nu:
        A_star = A_func(pi_star, nu)
        ax.plot(pi_star, A_star, '*', markersize=14,
                markerfacecolor='gold', markeredgecolor='black', markeredgewidth=0.8,
                zorder=11)

# Annotate the pathology for ν = 0.3 — labels placed in the empty
# bottom-right region to avoid colliding with curves
nu_demo = 0.3
pi_star_demo = nu_demo / (2 * (1 - nu_demo))
A_star_demo = A_func(pi_star_demo, nu_demo)
A_full_demo = nu_demo**3

ax.annotate(f'★ MAX  π* = {pi_star_demo:.3f}\n     A = {A_star_demo:.4f}',
            xy=(pi_star_demo, A_star_demo),
            xytext=(0.55, 0.13),
            fontsize=9, color='black', fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='black', pad=3, boxstyle='round,pad=0.25'),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.0))
ax.annotate(f'■ full self-pledge  π = ν = {nu_demo}\n     A = {A_full_demo:.4f}   (16 % BELOW max)',
            xy=(nu_demo, A_full_demo),
            xytext=(0.55, 0.06),
            fontsize=9, color=DAWN, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor=DAWN, pad=3, boxstyle='round,pad=0.25'),
            arrowprops=dict(arrowstyle='->', color=DAWN, lw=1.0))

ax.set_xlim(0, 1.05)
ax.set_ylim(0, 0.27)
ax.set_xlabel('Pledge saturation level   π = p / z₀', fontsize=10.5)
ax.set_ylabel('A(π, ν)   pledge-bonus value', fontsize=10.5)
ax.set_title('(b) A is NON-MONOTONE in π for any ν < 0.5 — pledging more can pay LESS',
             fontsize=11.5, fontweight='bold')
ax.grid(linestyle=':', alpha=0.30)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# Single combined legend in upper-left — curves + marker meanings
curve_handles, curve_labels = ax.get_legend_handles_labels()
marker_handles = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='gold',
           markeredgecolor='black', markersize=11, label='★ A maximum (ν < 0.5)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=NEUTRAL,
           markeredgecolor='black', markersize=8, label='■ Full self-pledge (π = ν)'),
]
ax.legend(handles=curve_handles + marker_handles,
          loc='upper left', fontsize=8.8, framealpha=0.93,
          title='Pool size  ν   (and markers)', title_fontsize=9.5, ncol=2)

# (Long explanation moved to figure footer)

plt.suptitle('Structural anatomy of A(π, ν) — what the formula says before any numbers',
             fontsize=13, fontweight='bold', y=0.97)

# Footer: explanation boxes BELOW the panels, no overlap with chart elements
fig.text(0.265, 0.03,
         '(a)  Half the (π, ν) plane is unreachable.  A function whose two inputs are coupled by an\n'
         '       external constraint (π ≤ ν) is parametrised in the wrong basis — the natural\n'
         '       independent inputs would be (ν, ρ) with ρ = π/ν the pledge ratio.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
fig.text(0.755, 0.03,
         '(b)  For ν < 0.5: the parabola peaks INSIDE the valid domain.  The optimal pledge for\n'
         '       an operator running a sub-half-saturated pool is NOT to fully self-pledge — it is\n'
         '       to withhold some pledge.  A "skin-in-the-game" formula pays you LESS for more skin.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
out_path = os.path.join(OUT, 'cip_levers_04_A_structural_anatomy.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')

# Console verification
print('---')
print('Verification of non-monotonicity at ν = 0.3:')
for pi in [0.1, 0.15, 0.2, 0.214, 0.25, 0.3]:
    print(f'  π = {pi:.3f}  →  A = {A_func(pi, 0.3):.5f}')
print('  (max at π* = 0.3/(2·0.7) = 0.214, A_max = 0.03214)')
print('  (full self-pledge at π = ν = 0.3, A = 0.027)')
print('  → full self-pledge is 16 % BELOW the optimal interior pledge')
