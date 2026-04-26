#!/usr/bin/env python3
"""
Figure 4 (cip_levers) — STRUCTURAL anatomy of A(ν, π).

In the (ν, π) basis with ν = σ/z₀ ∈ [0,1] and π = s/σ ∈ [0,1] independent,
the bonus activation factorises as

    A(ν, π) = ν² · π · [1 − π(1−ν)]

Two structural pathologies surfaced BEFORE the Bob/Charles/Alice scenarios:

Panel (a) — heatmap of A on the unit square [0,1]² with contour lines.
            Mainnet's operating zone is a thin strip near π = 0; the
            full-self-pledge boundary is π = 1 (where A collapses to ν³).

Panel (b) — A is NON-MONOTONE in π for any ν < 0.5.  At fixed ν, A is a
            concave parabola in π over [0,1], with maximum at
            π* = 1 / [2(1−ν)].  For ν < 0.5, π* < 1, so increasing pledge
            ratio beyond π* DECREASES the bonus.  The formula punishes
            full self-pledge for any pool below half-saturation.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors

OUT = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(OUT, exist_ok=True)

RED = '#E52321'
DAWN = '#EC641D'
BLUE = '#2C4FFA'
GREEN = '#1e6b1e'
NEUTRAL = '#4a4a4a'
GREY = '#808080'

def A_func(nu, pi):
    return nu**2 * pi * (1.0 - pi * (1.0 - nu))

# Layout: more whitespace between panels, room above and below
fig = plt.figure(figsize=(15.5, 8.0), dpi=150)
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.05],
                      left=0.06, right=0.97, bottom=0.21, top=0.88,
                      wspace=0.35)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])

# ====================================================================
# Panel (a) — heatmap of A on the unit square [0,1]²
# ====================================================================
ax = ax_a

nu_grid = np.linspace(0.001, 1.0, 300)
pi_grid = np.linspace(0.0, 1.0, 300)
NU, PI = np.meshgrid(nu_grid, pi_grid)
A_grid = A_func(NU, PI)
A_grid = np.where(A_grid > 1e-6, A_grid, 1e-6)

norm = mcolors.LogNorm(vmin=1e-4, vmax=1.0)
mesh = ax.pcolormesh(NU, PI, A_grid, norm=norm, cmap='viridis', shading='auto')

# Contour lines at meaningful A values
contour_levels = [1e-3, 1e-2, 0.05, 0.2, 0.5]
cs = ax.contour(NU, PI, A_grid, levels=contour_levels,
                colors='white', linewidths=0.8, alpha=0.55)
ax.clabel(cs, inline=True, fontsize=8.5,
          fmt={lv: f'A={lv}' for lv in contour_levels})

# Mainnet operating zone — thin band near π = 0
ax.add_patch(Rectangle((0, 0), 1.0, 0.012, facecolor=DAWN, edgecolor='none',
                        alpha=0.75, zorder=4))
ax.text(0.5, 0.04, 'mainnet operating zone   (median π = 0.07 %)',
        ha='center', va='bottom', fontsize=9.0, color=DAWN, fontweight='bold',
        bbox=dict(facecolor='white', edgecolor='none', pad=2, alpha=0.85))

# Mark full-self-pledge boundary π = 1 as a clean dashed line, label inside
ax.axhline(1.0, color='white', lw=1.8, linestyle='--', alpha=0.7, zorder=5)
ax.text(0.50, 0.96, 'π = 1   →   A = ν³  (cubic collapse)',
        ha='center', va='top', fontsize=9.5, color='white', fontweight='bold',
        bbox=dict(facecolor=RED, edgecolor='none', pad=3, alpha=0.85),
        zorder=6)

# Compact colorbar BELOW the panel (avoids overlap with panel b's y-axis)
cbar = fig.colorbar(mesh, ax=ax, orientation='horizontal',
                    fraction=0.046, pad=0.13, aspect=35)
cbar.set_label('A(ν, π)   pledge-bonus value   (log scale)', fontsize=9.5)

ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.0)
ax.set_xlabel('Stake saturation level   ν = σ / z₀', fontsize=10.5)
ax.set_ylabel('Within-pool pledge ratio   π = s / σ', fontsize=10.5)
ax.set_title('(a) A on the unit square — mainnet sits at π ≈ 0',
             fontsize=11.5, fontweight='bold', pad=10)
ax.set_aspect('equal')

# ====================================================================
# Panel (b) — A is NON-MONOTONE in π for ν < 0.5
# ====================================================================
ax = ax_b

# Drop ν = 1.0 (linear case, range incompatible with the rest);
# keep five informative ν values
nu_levels = [
    (0.10, '#a5a5a5'),
    (0.20, GREY),
    (0.30, DAWN),
    (0.50, '#2ecc71'),
    (0.70, BLUE),
]

pi_axis = np.linspace(0, 1.0, 400)
for nu, color in nu_levels:
    A_vals = A_func(nu, pi_axis)
    ax.plot(pi_axis, A_vals, color=color, lw=2.6, label=f'ν = {nu:.2f}')
    # Endpoint at π = 1 (cubic collapse): A = ν³
    ax.plot(1.0, nu**3, 's', markersize=10,
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.8,
            zorder=10)
    # Interior maximum if it exists (ν < 0.5 strictly)
    if nu < 0.5:
        pi_star = 1.0 / (2.0 * (1.0 - nu))
        if pi_star < 1.0:
            A_star = A_func(nu, pi_star)
            ax.plot(pi_star, A_star, '*', markersize=15,
                    markerfacecolor='gold', markeredgecolor='black', markeredgewidth=0.8,
                    zorder=11)

# Annotate the pathology for ν = 0.3 — placed in the upper-right empty zone
nu_demo = 0.3
pi_star_demo = 1.0 / (2.0 * (1.0 - nu_demo))
A_star_demo = A_func(nu_demo, pi_star_demo)
A_full_demo = nu_demo**3

ax.annotate(f'★ MAX at π* = {pi_star_demo:.3f}\n     A(0.3, π*) = {A_star_demo:.4f}',
            xy=(pi_star_demo, A_star_demo),
            xytext=(0.35, 0.27),
            fontsize=9.5, color='black', fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='black', pad=4, boxstyle='round,pad=0.3'),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.0))
ax.annotate(f'■ full self-pledge  π = 1\n     A(0.3, 1) = {A_full_demo:.4f}\n     (16 % BELOW the max!)',
            xy=(1.0, A_full_demo),
            xytext=(0.62, 0.10),
            fontsize=9.5, color=DAWN, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor=DAWN, pad=4, boxstyle='round,pad=0.3'),
            arrowprops=dict(arrowstyle='->', color=DAWN, lw=1.0))

ax.set_xlim(0, 1.05)
ax.set_ylim(0, 0.42)
ax.set_xlabel('Within-pool pledge ratio   π = s / σ', fontsize=10.5)
ax.set_ylabel('A(ν, π)   pledge-bonus value', fontsize=10.5)
ax.set_title('(b) Non-monotone in π for ν < 0.5 — pledging more can pay LESS',
             fontsize=11.5, fontweight='bold', pad=10)
ax.grid(linestyle=':', alpha=0.30)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# Combined legend — curves + marker meanings, top-left where it doesn't intersect curves
curve_handles, curve_labels = ax.get_legend_handles_labels()
marker_handles = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='gold',
           markeredgecolor='black', markersize=12,
           label='★ A maximum (ν < 0.5)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor=NEUTRAL,
           markeredgecolor='black', markersize=9,
           label='■ Full self-pledge (π = 1)'),
]
ax.legend(handles=curve_handles + marker_handles,
          loc='upper left', fontsize=9.0, framealpha=0.95,
          title='Pool size  ν', title_fontsize=10, ncol=2)

# Note about ν = 1 omission
ax.text(0.98, 0.02,
        'ν = 1.0 omitted — the saturated case A(1, π) = π is linear over [0, 1],\n'
        'the only regime where the formula is fully monotone in π.',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=8.2, color=NEUTRAL, fontstyle='italic')

# Suptitle anchored above panels with extra padding
plt.suptitle('Structural anatomy of A(ν, π) — what the formula says before any numbers',
             fontsize=13.5, fontweight='bold', y=0.96)

# Footer explanation boxes BELOW the panels
fig.text(0.27, 0.04,
         '(a)  A on the unit square [0,1]².  Contour lines mark constant-A levels.\n'
         '       Almost the entire mainnet population sits in the orange band near π = 0,\n'
         '       where A < 10⁻³ — the bonus signal is structurally near-zero in the operating zone.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
fig.text(0.755, 0.04,
         '(b)  For ν < 0.5: the parabola peaks INSIDE the domain at π* = 1 / [2(1−ν)].\n'
         '       The optimal pledge ratio for a sub-half-saturated pool is NOT 100 % — it is\n'
         '       to withhold some pledge.  A "skin-in-the-game" formula pays you LESS for more skin.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))

out_path = os.path.join(OUT, 'cip_levers_04_A_structural_anatomy.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')

# Verification
print('---')
print('Verification of non-monotonicity at ν = 0.3 (new framework):')
for pi in [0.30, 0.50, 0.65, 0.714, 0.80, 1.00]:
    print(f'  π = {pi:.3f}  →  A(0.3, π) = {A_func(0.3, pi):.5f}')
print('  (max at π* = 1/[2·0.7] = 0.714, A_max = 0.0321)')
print('  (full self-pledge at π = 1, A = 0.0270 → 16 % below max)')
