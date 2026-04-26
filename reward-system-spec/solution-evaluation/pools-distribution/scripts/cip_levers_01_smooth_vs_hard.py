#!/usr/bin/env python3
"""
Figure 1 (cip_levers) — five reward-vs-pledge mechanisms on a Healthy pool
(σ = 15 M ADA, ν ≈ 0.222), two panels with a SHARED y-axis so the
magnitudes compare honestly.

Insight: raising a₀ doesn't just "tilt" the curve — it REBALANCES.  Higher
a₀ ⇒ smaller λmin ⇒ low-pledge pools earn LESS at p = 0, and the bonus
recovers some but not all of it.  This is structurally different from
CIP-0050 / CIP-0037 which clip σ′ instead of touching the (λmin, λmax) split.
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
NEUTRAL = '#4a4a4a'
GREY = '#7a7a7a'
GREEN = '#1e6b1e'

SUPPLY = 33_719_282_563
K = 500
ORIG_SAT = SUPPLY / K
SIGMA = 15_000_000
NU = SIGMA / ORIG_SAT
E37 = 0.2
ELL = 125
SAT_FLOOR = E37 * ORIG_SAT
L50 = 100

def A(pi, nu):
    return pi * nu - pi**2 * (1 - nu)

def envelope(pi, nu, a0):
    """Reward envelope E(ν, π) = λ_size·ν + λ_pledge·A(ν, π)
    where the pledge ratio is taken as π_legacy/ν_legacy under the
    transformation s = π·σ.  Here `pi` is supplied as p/z0 to keep the
    bilinear original SL-D1 expression below; the script then reasons
    in absolute pledge p, so labels are unaffected by the (ν, π=s/σ)
    convention used in the published prose."""
    return (1.0/(1.0+a0)) * nu + (a0/(1.0+a0)) * A(pi, nu)

p_ada = np.linspace(0, 600_000, 2000)
pi_n = p_ada / ORIG_SAT
baseline = envelope(0.0, NU, 0.3)        # V1 a₀=0.3 at p=0

v1_03 = envelope(pi_n, NU, 0.3) / baseline
v1_10 = envelope(pi_n, NU, 1.0) / baseline
v1_30 = envelope(pi_n, NU, 3.0) / baseline

sigma_p_50 = np.minimum(SIGMA, L50 * p_ada)
nu_p_50 = sigma_p_50 / ORIG_SAT
cip50 = envelope(pi_n, nu_p_50, 0.3) / baseline

sat_p = np.clip(ELL * p_ada, SAT_FLOOR, ORIG_SAT)
sigma_p_37 = np.minimum(SIGMA, sat_p)
nu_p_37 = sigma_p_37 / ORIG_SAT
cip37 = envelope(pi_n, nu_p_37, 0.3) / baseline

p_k = p_ada / 1000
median_p_k = 0.0007 * SIGMA / 1000      # 10.5 k
cip50_k = SIGMA / L50 / 1000            # 150 k
cip37_floor_k = SAT_FLOOR / ELL / 1000  # 108 k

YMIN, YMAX = 0.0, 1.18

fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.6), dpi=150, sharey=True,
                          gridspec_kw={'bottom': 0.20, 'top': 0.92})

# ============================================================
# Panel (a) — V1 with three a₀ values: 0.3, 1.0, 3.0
# ============================================================
ax = axes[0]

ax.plot(p_k, v1_03, color=GREY, lw=2.4, label='V1 baseline  (a₀ = 0.3)')
ax.plot(p_k, v1_10, color=NEUTRAL, lw=2.2, ls='--', label='V1 raised  a₀ = 1.0')
ax.plot(p_k, v1_30, color='black', lw=2.2, ls=':', label='V1 raised  a₀ = 3.0')

ax.axhline(1.0, color=NEUTRAL, ls=':', lw=0.8, alpha=0.55)

# Mainnet median pledge marker
ax.axvline(median_p_k, color=DAWN, ls='-', lw=1.1, alpha=0.85)
ax.text(median_p_k + 6, 1.05, 'mainnet median\np = 10.5 k  (ρ = 0.07 %)',
        fontsize=8.8, color=DAWN, fontweight='bold', va='bottom')

# Annotate p=0 starting points (where the rebalancing shows)
ax.annotate(f'a₀=1.0 at p=0:\n{v1_10[0]:.0%} of baseline',
            xy=(0, v1_10[0]), xytext=(80, 0.42),
            fontsize=8.8, color=NEUTRAL, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=NEUTRAL, lw=0.9))
ax.annotate(f'a₀=3.0 at p=0:\n{v1_30[0]:.0%} of baseline',
            xy=(0, v1_30[0]), xytext=(80, 0.18),
            fontsize=8.8, color='black', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black', lw=0.9))

# Annotate p=full saturation
ax.text(p_k[-1] + 4, v1_03[-1], f'  {v1_03[-1]:.0%}',
        ha='left', va='center', fontsize=8.8, color=GREY, fontweight='bold')
ax.text(p_k[-1] + 4, v1_10[-1], f'  {v1_10[-1]:.0%}',
        ha='left', va='center', fontsize=8.8, color=NEUTRAL, fontweight='bold')
ax.text(p_k[-1] + 4, v1_30[-1], f'  {v1_30[-1]:.0%}',
        ha='left', va='center', fontsize=8.8, color='black', fontweight='bold')

ax.set_xlabel('Operator pledge  p  (k ADA)', fontsize=10.5)
ax.set_ylabel('Pool reward  /  V1(a₀=0.3) baseline at p = 0', fontsize=10.5)
ax.set_title('(a) V1 levers — raising a₀ rebalances, not just tilts',
             fontsize=11.5, fontweight='bold')
ax.legend(loc='upper left', fontsize=9.5, framealpha=0.93)
ax.set_xlim(0, 660)
ax.set_ylim(YMIN, YMAX)
ax.grid(axis='both', linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Long explanation moved to figure footer)

# ============================================================
# Panel (b) — V1(a₀=0.3) baseline + CIP-0050 + CIP-0037
# ============================================================
ax = axes[1]

ax.plot(p_k, v1_03, color=GREY, lw=2.0, ls='--', label='V1 baseline  (a₀ = 0.3)')
ax.plot(p_k, cip50, color=RED, lw=2.6, label='CIP-0050  (L = 100, a₀ = 0.3)')
ax.plot(p_k, cip37, color=BLUE, lw=2.6, label='CIP-0037  (ℓ = 125, e = 0.2, a₀ = 0.3)')

ax.axhline(1.0, color=NEUTRAL, ls=':', lw=0.8, alpha=0.55)

ax.axvline(median_p_k, color=DAWN, ls='-', lw=1.1, alpha=0.85)
ax.annotate('mainnet median\np = 10.5 k  (ρ = 0.07 %)',
            xy=(median_p_k, 0.07), xytext=(75, 0.34),
            fontsize=9, color=DAWN, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=DAWN, lw=1.0))

ax.axvline(cip37_floor_k, color=BLUE, ls=':', lw=1.0, alpha=0.7)
ax.axvline(cip50_k, color=RED, ls=':', lw=1.0, alpha=0.7)
ax.text(cip37_floor_k - 4, 1.155, 'CIP-0037\nfloor exit\n108 k',
        fontsize=8.6, color=BLUE, fontweight='bold', ha='right', va='top',
        bbox=dict(facecolor='white', edgecolor=BLUE, pad=2.5, boxstyle='round,pad=0.25'))
ax.text(cip50_k + 4, 1.155, 'CIP-0050\ncompliance\nσ/L = 150 k',
        fontsize=8.6, color=RED, fontweight='bold', ha='left', va='top',
        bbox=dict(facecolor='white', edgecolor=RED, pad=2.5, boxstyle='round,pad=0.25'))

# Floor value annotation for CIP-0037
floor_val = cip37[0]
ax.annotate(f'floor at\n{floor_val*100:.0f} % of V1',
            xy=(2, floor_val), xytext=(45, floor_val - 0.22),
            fontsize=9, color=BLUE, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.0))

ax.set_xlabel('Operator pledge  p  (k ADA)', fontsize=10.5)
ax.set_title('(b) Hard caps — clip σ′, leave a₀ alone',
             fontsize=11.5, fontweight='bold')
ax.legend(loc='lower right', fontsize=9.5, framealpha=0.93)
ax.set_xlim(0, 660)
ax.set_ylim(YMIN, YMAX)
ax.grid(axis='both', linestyle=':', alpha=0.35)
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Long explanation moved to figure footer)

plt.suptitle('Reward-vs-pledge — V1 levers (left) vs CIP-0050 / CIP-0037 (right)   '
             '·   Healthy pool σ = 15 M ADA, ν ≈ 0.222',
             fontsize=13, fontweight='bold', y=0.97)

# Footer explanation boxes — placed BELOW the panels, no overlap risk
fig.text(0.265, 0.03,
         '(a)  Higher a₀ shifts weight from λmin·ν onto λmax·A.  For a Healthy pool the\n'
         '       bonus recovers only a few % — even a₀ = 3.0 leaves the pool below baseline\n'
         '       at any realistic pledge level.  Raising λmax cannot fix what A doesn\'t carry.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
fig.text(0.755, 0.03,
         '(b)  CIP-0050 / CIP-0037 don\'t touch (λmin, λmax) — they clip σ′ BEFORE the\n'
         '       reward formula runs.  Penalty hits the BASE term λmin·ν′, not the bonus.\n'
         '       That is why the cliff is steep where a₀ tweaks barely move the needle.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
out_path = os.path.join(OUT, 'cip_levers_01_smooth_vs_hard.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
