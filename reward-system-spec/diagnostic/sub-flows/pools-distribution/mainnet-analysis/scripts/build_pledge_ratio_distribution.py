#!/usr/bin/env python3
"""
Pledge ratio distribution — pool count vs stake share.

Shows how pledge/active_stake is distributed across pools,
with a dual view: pool count and stake weight.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import csv

DATA = '/sessions/tender-great-allen/mnt/stream-SPO/spo-incentives/report/mainnet/pools-distribution/data'

with open(f'{DATA}/koios_pool_list_mainnet.csv') as f:
    pools = list(csv.DictReader(f))

# Filter: registered pools with meaningful stake (>10K ADA = 10B lovelace)
# This excludes dormant/zombie pools that distort the ratio distribution.
active_pools = []
for p in pools:
    stake = float(p['active_stake'] or 0)
    pledge = float(p['pledge'] or 0)
    if stake > 10_000e6 and p.get('pool_status', '') == 'registered':
        active_pools.append({
            'stake_ada': stake / 1e6,
            'pledge_ada': pledge / 1e6,
            'ratio_pct': (pledge / stake * 100) if stake > 0 else 0,
        })

total_stake = sum(p['stake_ada'] for p in active_pools)
total_pools = len(active_pools)

# Define bands by pledge ratio
bands = [
    ("0%\n(zero pledge)",      0,    0.0001, '#1a1a1a'),
    ("<0.1%",                  0.0001, 0.1,  '#c0392b'),
    ("0.1–1%",                 0.1,    1,    '#e74c3c'),
    ("1–10%",                  1,      10,   '#f39c12'),
    ("10–50%",                 10,     50,   '#f1c40f'),
    ("50–100%",                50,     100,  '#2ecc71'),
    (">100%\n(over-declared)", 100,    1e10, '#95a5a6'),
]

pool_counts = []
stake_shares = []
labels = []
colors = []

for label, lo, hi, color in bands:
    if lo == 0:
        count = sum(1 for p in active_pools if p['ratio_pct'] < hi)
        stake = sum(p['stake_ada'] for p in active_pools if p['ratio_pct'] < hi)
    else:
        count = sum(1 for p in active_pools if lo <= p['ratio_pct'] < hi)
        stake = sum(p['stake_ada'] for p in active_pools if lo <= p['ratio_pct'] < hi)
    pool_counts.append(count)
    stake_shares.append(stake / total_stake * 100)
    labels.append(label)
    colors.append(color)

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

x = np.arange(len(labels))
bar_w = 0.7

# Left: pool count
bars1 = ax1.barh(x, [c / total_pools * 100 for c in pool_counts], bar_w,
                 color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
ax1.set_xlabel('% of pools', fontsize=11, fontfamily='sans-serif')
ax1.set_title('By pool count', fontsize=12, fontweight='bold', fontfamily='sans-serif')
ax1.set_xlim(0, 25)
ax1.invert_xaxis()
ax1.set_yticks(x)
ax1.set_yticklabels(labels, fontsize=9, fontfamily='sans-serif')

# Add count labels
for i, (c, pct) in enumerate(zip(pool_counts, [c/total_pools*100 for c in pool_counts])):
    ax1.text(pct + 0.5, i, f'{c} ({pct:.1f}%)', va='center', ha='left',
             fontsize=8, fontfamily='sans-serif', color='#333')

# Right: stake share
bars2 = ax2.barh(x, stake_shares, bar_w,
                 color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
ax2.set_xlabel('% of active stake', fontsize=11, fontfamily='sans-serif')
ax2.set_title('By stake weight', fontsize=12, fontweight='bold', fontfamily='sans-serif')
ax2.set_xlim(0, 45)

# Add stake labels
for i, pct in enumerate(stake_shares):
    lo, hi = bands[i][1], bands[i][2]
    if lo == 0:
        stake_b = sum(p['stake_ada'] for p in active_pools if p['ratio_pct'] < hi)
    else:
        stake_b = sum(p['stake_ada'] for p in active_pools if lo <= p['ratio_pct'] < hi)
    ax2.text(pct + 0.5, i, f'{pct:.1f}% ({stake_b/1e9:.1f}B)',
             va='center', ha='left', fontsize=8, fontfamily='sans-serif', color='#333')

# Highlight the "broken zone" — ratio < 1%
for ax in [ax1, ax2]:
    ax.axhspan(-0.5, 2.5, color='#ffcccc', alpha=0.15, zorder=0)
    ax.grid(axis='x', alpha=0.2, linewidth=0.5)
    ax.set_facecolor('white')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

# Annotation
fig.text(0.5, -0.02,
         f'Pledge ratio = declared_pledge / active_stake  •  {total_pools:,} pools  •  {total_stake/1e9:.1f}B ADA  •  epoch 618',
         ha='center', fontsize=8.5, fontfamily='sans-serif', color='#666')

plt.tight_layout()
outpath = '/sessions/tender-great-allen/mnt/stream-SPO/spo-incentives/report/mainnet/pools-distribution/figures/pledge_ratio_distribution_mainnet.png'
fig.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='white')
print(f'Saved: {outpath}')

# Print summary
print(f'\nSummary:')
print(f'  Pools with ratio < 1%: {sum(pool_counts[:3])} ({sum(pool_counts[:3])/total_pools*100:.1f}%)')
print(f'  Stake with ratio < 1%: {sum(stake_shares[:3]):.1f}% ({sum(stake_shares[:3])*total_stake/100/1e9:.1f}B ADA)')
print(f'  Pools with ratio < 0.1%: {sum(pool_counts[:2])} ({sum(pool_counts[:2])/total_pools*100:.1f}%)')
print(f'  Stake with ratio < 0.1%: {sum(stake_shares[:2]):.1f}% ({sum(stake_shares[:2])*total_stake/100/1e9:.1f}B ADA)')
