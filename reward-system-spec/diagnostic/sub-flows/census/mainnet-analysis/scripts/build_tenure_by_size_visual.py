#!/usr/bin/env python3
"""build_tenure_by_size_visual.py
Three-panel figure profiling delegator behaviour by stake size:
  Panel A – Tenure distribution heatmap (tenure bucket × size bucket, % of size cohort)
  Panel B – Switch rate by size (avg switches + % never switched)
  Panel C – Stake concentration by tenure (where is the ADA?)
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
    tenure_size = load_csv('tenure_by_stake_size.csv')
    switch_rate = load_csv('switch_rate_by_size.csv')

    # ── Parse tenure × size data ────────────────────────────────────────
    tenure_order = ['0-5 ep (volatile)', '6-25 ep', '26-100 ep',
                    '101-200 ep', '201+ ep (loyal)']
    tenure_display = ['0–5 ep\n(≤25 d)', '6–25 ep\n(1–4 mo)', '26–100 ep\n(4–17 mo)',
                      '101–200 ep\n(1.4–2.7 yr)', '201+ ep\n(>2.7 yr)']
    size_order = ['<1K', '1K-10K', '10K-100K', '100K-1M', '1M+']
    size_display = ['<1K', '1K–10K', '10K–100K', '100K–1M', '1M+']

    # Build count grid [tenure × size]
    count_grid = np.zeros((len(tenure_order), len(size_order)))
    stake_grid = np.zeros((len(tenure_order), len(size_order)))
    for r in tenure_size:
        ti = tenure_order.index(r['tenure_bucket']) if r['tenure_bucket'] in tenure_order else None
        si = size_order.index(r['size_bucket']) if r['size_bucket'] in size_order else None
        if ti is not None and si is not None:
            count_grid[ti, si] = int(r['delegation_count'])
            stake_grid[ti, si] = float(r['total_stake_ada'])

    # Normalise: % of each SIZE cohort (column-wise)
    col_totals = count_grid.sum(axis=0)
    pct_grid = 100.0 * count_grid / np.where(col_totals > 0, col_totals, 1)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.30, left=0.06, right=0.97, top=0.88, bottom=0.18)

    # ── Panel A: Heatmap — tenure distribution by size cohort ───────────
    ax = axes[0]
    im = ax.imshow(pct_grid, cmap='YlOrRd', aspect='auto', vmin=0)
    for i in range(len(tenure_order)):
        for j in range(len(size_order)):
            val = pct_grid[i, j]
            cnt = int(count_grid[i, j])
            colour = WHITE if val > 50 else BLACK
            # Show percentage and count
            if cnt >= 1000:
                label = f'{val:.0f}%\n({cnt/1000:.0f}K)'
            else:
                label = f'{val:.1f}%\n({cnt})'
            ax.text(j, i, label, ha='center', va='center',
                    fontsize=8, fontweight='bold', color=colour)

    ax.set_xticks(range(len(size_order)))
    ax.set_xticklabels(size_display, fontsize=9)
    ax.set_yticks(range(len(tenure_order)))
    ax.set_yticklabels(tenure_display, fontsize=8)
    ax.set_xlabel('Delegation size (ADA)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Current tenure', fontsize=10, fontweight='bold')
    ax.set_title('A. Tenure profile by delegation size',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')

    # ── Panel B: Switch rate by size ────────────────────────────────────
    ax = axes[1]
    sizes = [r['size_bucket'] for r in switch_rate]
    avg_sw = [float(r['avg_switches']) for r in switch_rate]
    pct_never = [float(r['pct_never_switched']) for r in switch_rate]
    pct_freq = [float(r['pct_frequent_switcher']) for r in switch_rate]

    x = np.arange(len(sizes))
    width = 0.30

    bars1 = ax.bar(x - width, avg_sw, width, color=DAWN, alpha=0.85,
                   label='Avg switches', edgecolor=WHITE)
    ax.set_ylabel('Average lifetime switches', fontsize=10, fontweight='bold',
                  color=DAWN)

    ax2 = ax.twinx()
    ax2.bar(x, pct_never, width, color=ACID, alpha=0.85,
            label='% never switched', edgecolor=WHITE)
    ax2.bar(x + width, pct_freq, width, color=INFARED, alpha=0.85,
            label='% frequent (≥3)', edgecolor=WHITE)
    ax2.set_ylabel('% of delegators', fontsize=10, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(size_display, fontsize=9)
    ax.set_xlabel('Delegation size (ADA)', fontsize=10, fontweight='bold')
    ax.set_title('B. Switching activity by delegation size',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8,
              loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)

    # ── Panel C: Stake by tenure (stacked bar per size bucket) ──────────
    ax = axes[2]
    # Normalise stake: % within each size bucket (column)
    stake_col_totals = stake_grid.sum(axis=0)
    stake_pct = 100.0 * stake_grid / np.where(stake_col_totals > 0, stake_col_totals, 1)

    tenure_colours = [INFARED, DAWN, SOLAR, COBALT, ACID]
    x = np.arange(len(size_order))
    bottoms = np.zeros(len(size_order))
    for i, (tenure_label, col) in enumerate(zip(tenure_display, tenure_colours)):
        vals = stake_pct[i, :]
        short_label = tenure_label.split('\n')[0]
        ax.bar(x, vals, 0.55, bottom=bottoms, label=short_label, color=col,
               alpha=0.85, edgecolor=WHITE, linewidth=0.5)
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels(size_display, fontsize=9)
    ax.set_xlabel('Delegation size (ADA)', fontsize=10, fontweight='bold')
    ax.set_ylabel('% of stake in size cohort', fontsize=10, fontweight='bold')
    ax.set_title('C. Where is the stake? Tenure × size',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.legend(fontsize=7, loc='upper right', framealpha=0.9, title='Tenure',
              title_fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'tenure_by_stake_size.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
