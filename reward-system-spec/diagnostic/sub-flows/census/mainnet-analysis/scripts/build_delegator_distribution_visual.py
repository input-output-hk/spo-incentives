#!/usr/bin/env python3
"""build_delegator_distribution_visual.py
Four-panel figure for delegator stake distribution:
  Panel A – Size bucket histogram (count + stake share)
  Panel B – Lorenz curve with Gini
  Panel C – Concentration: top-N share
  Panel D – Evolution of top-1% share over time
"""

import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')


def load_csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def build_figure():
    dist = load_csv('delegator_stake_distribution.csv')
    conc = load_csv('delegator_concentration_metrics.csv')

    # Try loading optional files
    try:
        lorenz = load_csv('delegator_lorenz_curve.csv')
    except Exception:
        lorenz = None
    try:
        evo = load_csv('delegator_distribution_evolution.csv')
    except Exception:
        evo = None

    n_panels = 2 + (1 if lorenz else 0) + (1 if evo else 0)
    fig, axes = plt.subplots(1, n_panels, figsize=(6 * n_panels, 6.5))
    if n_panels == 1:
        axes = [axes]
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.30, left=0.05, right=0.97, top=0.88, bottom=0.18)

    panel_idx = 0

    # ── Panel A: Size bucket histogram ──────────────────────────────────
    ax = axes[panel_idx]; panel_idx += 1
    buckets = [r['size_bucket'] for r in dist]
    counts = [int(r['delegator_count']) for r in dist]
    stakes = [float(r['total_stake_ada']) for r in dist]
    total_stake = sum(stakes)
    stake_pcts = [100 * s / total_stake for s in stakes]

    x = np.arange(len(buckets))
    width = 0.38

    # Count bars (left axis)
    bars1 = ax.bar(x - width/2, counts, width, color=ELECTRIC, alpha=0.85,
                   label='Delegators', edgecolor=WHITE)
    ax.set_ylabel('Number of delegators', fontsize=10, fontweight='bold', color=ELECTRIC)
    ax.set_yscale('log')
    ax.tick_params(axis='y', labelcolor=ELECTRIC)

    # Stake share bars (right axis)
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + width/2, stake_pcts, width, color=DAWN, alpha=0.85,
                    label='Stake share', edgecolor=WHITE)
    ax2.set_ylabel('% of total stake', fontsize=10, fontweight='bold', color=DAWN)
    ax2.tick_params(axis='y', labelcolor=DAWN)

    ax.set_xticks(x)
    ax.set_xticklabels(buckets, fontsize=8, rotation=30)
    ax.set_xlabel('Delegation size (ADA)', fontsize=10, fontweight='bold')
    ax.set_title('A. Delegator count vs stake by size',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper center')
    ax.spines['top'].set_visible(False)

    # ── Panel B: Lorenz curve ───────────────────────────────────────────
    if lorenz:
        ax = axes[panel_idx]; panel_idx += 1
        pct_del = np.array([float(r['pct_delegators']) for r in lorenz])
        cum_stake = np.array([float(r['cum_pct_stake']) for r in lorenz])

        ax.fill_between(pct_del, cum_stake, pct_del, alpha=0.25, color=INFARED,
                        label='Inequality area')
        ax.plot(pct_del, cum_stake, color=INFARED, linewidth=2, label='Lorenz curve')
        ax.plot([0, 100], [0, 100], color=BLACK, linewidth=1, linestyle='--',
                alpha=0.5, label='Perfect equality')

        # Compute Gini from Lorenz data
        gini = 1 - 2 * np.trapz(cum_stake / 100, pct_del / 100)
        ax.text(20, 80, f'Gini = {gini:.3f}', fontsize=14, fontweight='bold',
                color=INFARED)

        ax.set_xlabel('Cumulative % of delegators (sorted by stake)', fontsize=10,
                      fontweight='bold')
        ax.set_ylabel('Cumulative % of stake', fontsize=10, fontweight='bold')
        ax.set_title('B. Lorenz curve — stake inequality',
                     fontsize=11, fontweight='bold', color=INFARED, loc='left')
        ax.legend(fontsize=8, loc='upper left')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # ── Panel C: Top-N concentration ────────────────────────────────────
    ax = axes[panel_idx]; panel_idx += 1
    if conc:
        c = conc[0]
        labels_c = ['Top 100', 'Top 1,000', 'Top 10,000']
        vals_c = [float(c['top100_pct']), float(c['top1000_pct']), float(c['top10000_pct'])]
        colours_c = [INFARED, DAWN, SOLAR]

        bars = ax.barh(range(len(labels_c)), vals_c, color=colours_c, alpha=0.85,
                       edgecolor=WHITE)
        for bar, val in zip(bars, vals_c):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')

        ax.set_yticks(range(len(labels_c)))
        ax.set_yticklabels(labels_c, fontsize=10)
        ax.set_xlabel('% of total stake', fontsize=10, fontweight='bold')

        # Add delegator context
        total_n = int(c['delegator_count'])
        ax.text(0.95, 0.05, f'of {total_n:,} delegators',
                transform=ax.transAxes, ha='right', fontsize=9, color='grey')

    pnl_label = chr(ord('A') + panel_idx - 1)
    ax.set_title(f'{pnl_label}. Top-N concentration',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel D: Evolution ──────────────────────────────────────────────
    if evo:
        ax = axes[panel_idx]; panel_idx += 1
        epochs = [int(r['epoch_no']) for r in evo]
        top1 = [float(r['top1pct_share']) for r in evo]
        top01 = [float(r['top01pct_share']) for r in evo]
        deleg_counts = [int(r['delegator_count']) for r in evo]

        ax.plot(epochs, top1, color=INFARED, linewidth=2, label='Top 1% share')
        ax.plot(epochs, top01, color=DAWN, linewidth=2, label='Top 0.1% share')
        ax.set_ylabel('% of total stake', fontsize=10, fontweight='bold')
        ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')

        ax2 = ax.twinx()
        ax2.plot(epochs, [n/1000 for n in deleg_counts], color=COBALT, linewidth=1,
                 linestyle='--', alpha=0.6, label='Delegators (K)')
        ax2.set_ylabel('Delegators (thousands)', fontsize=9, color=COBALT)
        ax2.tick_params(axis='y', labelcolor=COBALT)

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='center right')

        pnl_label = chr(ord('A') + panel_idx - 1)
        ax.set_title(f'{pnl_label}. Concentration evolution',
                     fontsize=11, fontweight='bold', color=INFARED, loc='left')
        ax.spines['top'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'delegator_stake_distribution.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
