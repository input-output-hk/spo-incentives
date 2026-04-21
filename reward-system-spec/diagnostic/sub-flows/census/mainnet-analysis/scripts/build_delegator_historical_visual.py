#!/usr/bin/env python3
"""build_delegator_historical_visual.py
Three-panel figure for delegator population historical evolution:
  Panel A – Delegator count by size tier (stacked area)
  Panel B – Total stake by size tier (stacked area)
  Panel C – Concentration evolution (top-1%, top-0.1%) + mean/median ratio
"""

import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# --- IOG brand colours ---
INFARED   = '#E52321'
DAWN      = '#EC641D'
BLACK     = '#000000'
WHITE     = '#FFFFFF'
ELECTRIC  = '#16E9D8'
ACID      = '#06FF89'
COBALT    = '#2C4FFA'
SOLAR     = '#FFBA36'
ULTRAVIOLET = '#A700FF'

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')


def load_csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def build_figure():
    tiers = load_csv('delegator_size_tier_evolution.csv')
    evo = load_csv('delegator_distribution_evolution.csv')

    # Parse tier data into {epoch: {tier: (count, stake)}}
    tier_order = ['micro_under_1k', 'small_1k_100k', 'medium_100k_1m', 'large_1m_plus']
    tier_labels = ['< 1K ADA', '1K – 100K', '100K – 1M', '1M+']
    tier_colours = [ELECTRIC, COBALT, SOLAR, INFARED]

    epoch_tier_count = defaultdict(dict)
    epoch_tier_stake = defaultdict(dict)
    for r in tiers:
        ep = int(r['epoch_no'])
        t = r['tier']
        epoch_tier_count[ep][t] = int(r['delegator_count'])
        epoch_tier_stake[ep][t] = float(r['total_stake_ada']) / 1e9  # in B ADA

    epochs_t = sorted(epoch_tier_count.keys())

    # Build arrays
    count_arrays = []
    stake_arrays = []
    for t in tier_order:
        count_arrays.append([epoch_tier_count[ep].get(t, 0) for ep in epochs_t])
        stake_arrays.append([epoch_tier_stake[ep].get(t, 0) for ep in epochs_t])

    # Parse evolution data
    epochs_e = [int(r['epoch_no']) for r in evo]
    top1 = [float(r['top1pct_share']) for r in evo]
    top01 = [float(r['top01pct_share']) for r in evo]
    deleg_counts = [int(r['delegator_count']) for r in evo]
    mean_ada = [float(r['mean_ada']) for r in evo]

    fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.28, left=0.05, right=0.97, top=0.88, bottom=0.12)

    # ── Panel A: Delegator count by tier (stacked area) ─────────────────
    ax = axes[0]
    ax.stackplot(epochs_t, *[np.array(a) / 1000 for a in count_arrays],
                 labels=tier_labels, colors=tier_colours, alpha=0.8)
    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylabel('Delegators (thousands)', fontsize=10, fontweight='bold')
    ax.set_title('A. Delegator population by size tier',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.legend(fontsize=8, loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel B: Stake by tier (stacked area) ───────────────────────────
    ax = axes[1]
    ax.stackplot(epochs_t, *stake_arrays,
                 labels=tier_labels, colors=tier_colours, alpha=0.8)
    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylabel('Staked ADA (billions)', fontsize=10, fontweight='bold')
    ax.set_title('B. Stake composition by size tier',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.legend(fontsize=8, loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel C: Concentration + delegator count ────────────────────────
    ax = axes[2]
    ax.plot(epochs_e, top1, color=INFARED, linewidth=2.5, label='Top 1% stake share')
    ax.plot(epochs_e, top01, color=DAWN, linewidth=2, label='Top 0.1% stake share')
    ax.set_ylabel('% of total stake', fontsize=10, fontweight='bold')
    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 100)

    ax2 = ax.twinx()
    ax2.plot(epochs_e, [n / 1000 for n in deleg_counts], color=COBALT,
             linewidth=1.2, linestyle='--', alpha=0.7, label='Delegators (K)')
    ax2.set_ylabel('Delegators (thousands)', fontsize=9, color=COBALT)
    ax2.tick_params(axis='y', labelcolor=COBALT)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8,
              loc='center right', framealpha=0.9)

    ax.set_title('C. Concentration evolution',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'delegator_historical_evolution.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
