#!/usr/bin/env python3
"""build_operator_landscape_visual.py
Three-panel figure for the operator landscape:
  Panel A – Fleet size (n-MPO) distribution: entities vs pools vs stake
  Panel B – Archetype composition (treemap-style horizontal stacked bar)
  Panel C – Top 15 entities by stake
"""

import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

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
EMBER     = '#FF532C'
HYPER     = '#FF79FC'

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')


def load_csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def build_figure():
    fleet = load_csv('mpo_fleet_distribution.csv')
    arch = load_csv('entity_archetype_summary.csv')
    entities = load_csv('entity_stake_summary_623.csv')

    fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.30, left=0.05, right=0.97, top=0.88, bottom=0.18)

    # ── Panel A: Fleet size distribution ────────────────────────────────
    ax = axes[0]
    labels = [r['fleet_size'].replace(' (attributed SPO)', '\n(attr. SPO)') for r in fleet]
    ent_counts = [int(r['entities']) for r in fleet]
    pool_counts = [int(r['pools']) for r in fleet]
    stakes = [float(r['total_stake_ada']) / 1e9 for r in fleet]

    x = np.arange(len(labels))
    width = 0.27

    bars1 = ax.bar(x - width, ent_counts, width, color=ELECTRIC, alpha=0.85,
                   label='Entities', edgecolor=WHITE)
    bars2 = ax.bar(x, pool_counts, width, color=COBALT, alpha=0.85,
                   label='Pools', edgecolor=WHITE)

    ax2 = ax.twinx()
    bars3 = ax2.bar(x + width, stakes, width, color=DAWN, alpha=0.85,
                    label='Stake (B)', edgecolor=WHITE)
    ax2.set_ylabel('Stake (B ADA)', fontsize=10, fontweight='bold', color=DAWN)
    ax2.tick_params(axis='y', labelcolor=DAWN)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_xlabel('Fleet size (n-MPO)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Count', fontsize=10, fontweight='bold')

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper left')

    ax.set_title('A. Operator fleet size distribution',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)

    # ── Panel B: Archetype composition ──────────────────────────────────
    ax = axes[1]
    arch_labels_map = {
        'cex': 'Exchange',
        'ivaas': 'IVaaS',
        'community_branded_fleet': 'Community fleet',
        'independent_mpo': 'Independent MPO',
        'multi_brand_fleet': 'Multi-brand',
        'opaque': 'Opaque',
        'opaque_fleet': 'Opaque fleet',
        'ecosystem': 'Ecosystem',
        'platform': 'Platform',
        'protocol_project': 'Protocol project',
        'unknown': 'Unknown',
    }
    arch_colours = {
        'cex': INFARED, 'ivaas': DAWN, 'community_branded_fleet': ACID,
        'independent_mpo': COBALT, 'multi_brand_fleet': SOLAR,
        'opaque': ULTRAVIOLET, 'opaque_fleet': HYPER,
        'ecosystem': ELECTRIC, 'platform': EMBER,
        'protocol_project': '#8421A2', 'unknown': '#888888',
    }

    # Horizontal stacked bar: entities, pools, stake
    metrics = ['entities', 'pools', 'total_stake_ada']
    metric_labels = ['Entities', 'Pools', 'Stake']
    y_pos = np.arange(3)

    # Compute totals for percentages
    totals = {m: sum(float(r[m]) for r in arch) for m in metrics}

    lefts = [0.0, 0.0, 0.0]
    for r in arch:
        a = r['archetype']
        label = arch_labels_map.get(a, a)
        col = arch_colours.get(a, '#888888')
        widths = []
        for i, m in enumerate(metrics):
            val = float(r[m])
            pct = 100 * val / totals[m] if totals[m] > 0 else 0
            widths.append(pct)

        ax.barh(y_pos, widths, left=lefts, height=0.5, color=col, alpha=0.85,
                label=label if float(r['total_stake_ada']) > 0.3e9 else None,
                edgecolor=WHITE, linewidth=0.5)
        lefts = [l + w for l, w in zip(lefts, widths)]

    ax.set_yticks(y_pos)
    ax.set_yticklabels(metric_labels, fontsize=10)
    ax.set_xlabel('% of attributed total', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 100)

    # Legend — only top archetypes
    handles, labs = ax.get_legend_handles_labels()
    ax.legend(handles, labs, fontsize=7, loc='lower right',
              ncol=2, framealpha=0.9)

    ax.set_title('B. Entity archetype composition',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel C: Top 15 entities by stake ───────────────────────────────
    ax = axes[2]
    top15 = sorted(entities, key=lambda r: -float(r['total_ada']))[:15]
    names = [r['display_name'][:18] for r in top15]
    stakes_top = [float(r['total_ada']) / 1e9 for r in top15]
    pools_top = [int(r['active_pools']) for r in top15]
    arch_top = [r['archetype'] for r in top15]
    colours_top = [arch_colours.get(a, '#888888') for a in arch_top]

    y = np.arange(len(names))
    bars = ax.barh(y, stakes_top, color=colours_top, alpha=0.85, edgecolor=WHITE)

    for bar, n_pools in zip(bars, pools_top):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f'{n_pools}p', va='center', fontsize=8, color='grey')

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Stake (B ADA)', fontsize=10, fontweight='bold')
    ax.set_title('C. Top 15 entities (pool count annotated)',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'operator_landscape.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
