#!/usr/bin/env python3
"""
Figure 2 (cip_levers) — vulgarised anatomy of the pledge-bonus A(π, ν).

Concrete scenario: three operators who give the MAXIMUM possible commitment
signal (100 % self-pledge) earn radically different bonuses because A
favours pool size over commitment.

Panel (a): bar chart — yearly pledge bonus for three fully self-pledged pools
           (Sub-reliable 2 M, Healthy 15 M, Saturated 67 M).  Log scale.

Panel (b): bonus per ADA of pledge, by pool size, at 100 % self-pledge —
           shows the bonus YIELD scales as ν², so a small operator's
           pledged ADA earns ~1000× less than a big operator's pledged ADA.
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
GREY = '#7a7a7a'
PURPLE = '#A700FF'

# Mainnet protocol params + reward scale
SUPPLY = 33_719_282_563
K = 500
ORIG_SAT = SUPPLY / K
A0 = 0.3
LAM_SIZE = 1.0 / (1.0 + A0)
LAM_PLEDGE = A0 / (1.0 + A0)
P_MAX_ADA_PER_EPOCH = 31_082          # calibrated from pool_envelope_detail.csv
EPOCHS_PER_YEAR = 73

def A_func(pi, nu):
    return pi * nu - pi**2 * (1 - nu)

# Three operators, ALL fully self-pledged (π = ν)
operators = [
    ('Bob\nSub-reliable',  2_000_000,  '#909090'),
    ('Charles\nHealthy', 15_000_000, DAWN),
    ('Alice\nSaturated', 67_000_000, RED),
]

fig = plt.figure(figsize=(16, 8.2), dpi=150)
gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.30,
                      bottom=0.20, top=0.92)
ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])

# ====================================================================
# Panel (a) — yearly bonus bar chart for three fully self-pledged pools
# ====================================================================
ax = ax_left

names, sigmas, colors = zip(*operators)
nus = np.array([s / ORIG_SAT for s in sigmas])
A_vals = nus ** 3                              # A(ν, ν) = ν³ at full self-pledge
bonus_per_ep = LAM_PLEDGE * A_vals * P_MAX_ADA_PER_EPOCH
bonus_per_year = bonus_per_ep * EPOCHS_PER_YEAR

# Compose richer x-axis labels including pool size + commitment level — keeps
# σ info on screen without floating boxes that could overlap bar value labels
xlabels = [f'{n}\nσ = p = {s/1e6:.0f} M ₳\n100 % self-pledged'
           for n, s in zip(names, sigmas)]
bars = ax.bar(xlabels, bonus_per_year, color=colors,
              edgecolor='black', linewidth=0.7, width=0.6)

# Bar labels — show the absolute yearly bonus value above the bar,
# and the per-million yield in a compact form INSIDE the bar
for bar, v, sigma in zip(bars, bonus_per_year, sigmas):
    text = f'{v:,.0f} ₳ /yr'
    ax.text(bar.get_x() + bar.get_width() / 2, v * 1.4,
            text, ha='center', va='bottom',
            fontsize=10.5, fontweight='bold',
            color='black' if v > 100 else RED)

# (σ + pledge info now embedded in the x-axis tick labels above)

ax.set_yscale('log')
ax.set_ylim(1, 5e6)
ax.set_ylabel('Yearly pledge bonus  λmax · A · P_max · 73 epochs   (ADA / year)',
              fontsize=10.5)
ax.set_title('(a) Three operators, all fully self-pledged — same commitment, very different reward',
             fontsize=11, fontweight='bold')
ax.grid(axis='y', linestyle=':', alpha=0.4, which='both')
ax.set_axisbelow(True)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Big-takeaway box removed — the bars already convey the disparity, and the
#  footer caption restates it.  Avoids overlapping with bar value labels.)
ratio = bonus_per_year[2] / bonus_per_year[0]
print(f'  Alice/Bob ratio (for footer reference): {ratio:,.0f}×')

# ====================================================================
# Panel (b) — bonus per ADA of pledge, by pool size, at 100% self-pledge
# ====================================================================
ax = ax_right

sigma_axis = np.logspace(5, 8, 500)        # 100k → 100M ADA
nu_axis = sigma_axis / ORIG_SAT

# Bonus per ADA of pledge per year, at full self-pledge
# yearly bonus = LAM_PLEDGE · ν³ · P_MAX · 73
# pledge = σ = ν · z0
# yield = (LAM_PLEDGE · ν³ · P_MAX · 73) / (ν · z0) = LAM_PLEDGE · ν² · P_MAX · 73 / z0
yield_per_ada_year = (LAM_PLEDGE * nu_axis**2 * P_MAX_ADA_PER_EPOCH * EPOCHS_PER_YEAR) / ORIG_SAT
# As a percentage yield per year
yield_pct = yield_per_ada_year * 100        # ADA per ADA per year, ×100 for %

ax.plot(sigma_axis / 1e6, yield_pct, color=NEUTRAL, lw=2.6, zorder=5)

# Mark the three operators
op_yields = []
for name, sigma, color in operators:
    nu = sigma / ORIG_SAT
    y_pct = LAM_PLEDGE * nu**2 * P_MAX_ADA_PER_EPOCH * EPOCHS_PER_YEAR / ORIG_SAT * 100
    op_yields.append(y_pct)
    ax.plot(sigma / 1e6, y_pct, 'o', markersize=10,
            markerfacecolor=color, markeredgecolor='black', markeredgewidth=0.8,
            zorder=10)
    ax.annotate(f'{name.split(chr(10))[0]}\n{y_pct:.4f} %/yr',
                xy=(sigma/1e6, y_pct),
                xytext=(sigma/1e6 * 1.5, y_pct * 0.3 if y_pct > 0.01 else y_pct * 5),
                fontsize=9, color=color, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=color, lw=1.0),
                bbox=dict(facecolor='white', edgecolor=color, pad=3, boxstyle='round,pad=0.25'))

# Reference line: passive delegation yield (~2.3 %/yr) — the "opportunity cost"
ax.axhline(2.3, color=BLUE, ls='--', lw=1.4, alpha=0.85)
ax.text(80, 2.6,
        'passive-delegation yield ≈ 2.3 %/yr\n(POL.O2.F2 — what the operator gives up by locking pledge)',
        ha='right', va='bottom', fontsize=9, color=BLUE, fontweight='bold')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(0.1, 100)
ax.set_ylim(1e-5, 10)
ax.set_xlabel('Pool size  σ   (M ADA, log scale)', fontsize=10.5)
ax.set_ylabel('Bonus YIELD per ADA of pledge   (% per year, log scale)',
              fontsize=10.5)
ax.set_title('(b) Bonus yield per ADA of pledge, at 100 % self-pledge — grows as σ²',
             fontsize=11, fontweight='bold')
ax.grid(True, which='both', linestyle=':', alpha=0.30)
for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)

# (Long explanation moved to figure footer)

plt.suptitle('What A(ν, π) actually pays — the pledge bonus paradox  (full self-pledge, π = 1)',
             fontsize=13, fontweight='bold', y=0.97)

# Footer explanation boxes — placed BELOW the panels
fig.text(0.27, 0.03,
         '(a)  Same commitment signal (100 % self-pledge), three pool sizes — bonus disparity\n'
         '       grows ~37 595× across the population.  The bonus YIELD per pledged ADA is shown\n'
         '       as a small overlay inside each bar.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
fig.text(0.755, 0.03,
         '(b)  Same act (100 % self-pledge), 1000× different yield by pool size.  For Bob, pledging\n'
         '       1 M ₳ buys 7 ₳/yr of bonus — vs 23 000 ₳/yr he\'d earn delegating that same 1 M\n'
         '       passively.  The bonus is a LOSS for small operators — what 78 % of mainnet tells you.',
         ha='center', va='bottom', fontsize=9.0, color=NEUTRAL,
         bbox=dict(facecolor='#f7f7f7', edgecolor=NEUTRAL, pad=6, boxstyle='round,pad=0.4'))
out_path = os.path.join(OUT, 'cip_levers_02_A_anatomy.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f'Wrote {out_path}')
print('---')
for (name, sigma, _), y, by in zip(operators, op_yields, bonus_per_year):
    print(f'  {name.replace(chr(10), " "):20s}  σ={sigma/1e6:5.1f} M  '
          f'yearly bonus = {by:>10,.0f} ADA/yr   '
          f'yield = {y:.5f} %/yr')
