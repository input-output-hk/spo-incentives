#!/usr/bin/env python3
"""build_switch_motivation_visual.py
Three-panel figure for switch motivation analysis:
  Panel A – Margin direction × Size direction heatmap
  Panel B – Margin-band transition matrix (Sankey-style grouped bar)
  Panel C – Loyal vs Volatile margin-band distribution (grouped bar)
"""

import csv, os, sys
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
ULTRAVIOLET = '#A700FF'
VOLT      = '#F2FF58'
SOLAR     = '#FFBA36'
EMBER     = '#FF532C'
COBALT    = '#2C4FFA'

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')

# ── Panel A: Switch motivation (margin_direction × size_direction) ──────────

def load_motivation():
    rows = []
    with open(os.path.join(DATA, 'switch_motivation.csv')) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def load_transition():
    rows = []
    with open(os.path.join(DATA, 'margin_transition_matrix.csv')) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def load_aggregate():
    rows = []
    with open(os.path.join(DATA, 'loyal_pool_aggregate.csv')) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def build_figure():
    motivation = load_motivation()
    transition = load_transition()
    aggregate  = load_aggregate()

    fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.32, left=0.05, right=0.97, top=0.88, bottom=0.15)

    # ── Panel A: Heatmap ────────────────────────────────────────────────
    ax = axes[0]
    margin_labels = ['lower_margin', 'same_margin', 'higher_margin']
    margin_display = ['Lower\nmargin', 'Same\nmargin', 'Higher\nmargin']
    size_labels   = ['to_smaller', 'similar_size', 'to_larger']
    size_display  = ['To smaller\npool', 'Similar\nsize', 'To larger\npool']

    grid = np.zeros((3, 3))
    for r in motivation:
        mi = margin_labels.index(r['margin_direction']) if r['margin_direction'] in margin_labels else None
        si = size_labels.index(r['size_direction']) if r['size_direction'] in size_labels else None
        if mi is not None and si is not None:
            grid[mi, si] = float(r['pct'])

    im = ax.imshow(grid, cmap='YlOrRd', aspect='auto', vmin=0, vmax=16)
    for i in range(3):
        for j in range(3):
            val = grid[i, j]
            colour = WHITE if val > 12 else BLACK
            ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                    fontsize=11, fontweight='bold', color=colour)

    ax.set_xticks(range(3))
    ax.set_xticklabels(size_display, fontsize=9)
    ax.set_yticks(range(3))
    ax.set_yticklabels(margin_display, fontsize=9)
    ax.set_xlabel('Pool size direction', fontsize=10, fontweight='bold')
    ax.set_ylabel('Margin direction', fontsize=10, fontweight='bold')
    ax.set_title('A. Switch motivation profile', fontsize=12, fontweight='bold',
                 color=INFARED, loc='left')

    # ── Panel B: Margin band transition (top flows) ─────────────────────
    ax = axes[1]
    # Build a grouped view: for each from_band, show top to_band flows
    bands_order = ['0-2%', '2-5%', '5-10%', '10-99%', '100%']
    band_colours = {
        '0-2%': ELECTRIC, '2-5%': COBALT, '5-10%': SOLAR,
        '10-99%': DAWN, '100%': INFARED
    }

    # Build from→to matrix
    matrix = {}
    for r in transition:
        fb, tb = r['from_band'], r['to_band']
        if fb in bands_order and tb in bands_order:
            matrix.setdefault(fb, {})[tb] = float(r['pct'])

    x = np.arange(len(bands_order))
    width = 0.15
    for i, tb in enumerate(bands_order):
        vals = [matrix.get(fb, {}).get(tb, 0) for fb in bands_order]
        offset = (i - 2) * width
        bars = ax.bar(x + offset, vals, width, label=f'→ {tb}',
                      color=band_colours[tb], alpha=0.85, edgecolor=WHITE, linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(bands_order, fontsize=9)
    ax.set_xlabel('Origin margin band', fontsize=10, fontweight='bold')
    ax.set_ylabel('Share of all switches (%)', fontsize=10, fontweight='bold')
    ax.legend(title='Destination', fontsize=7, title_fontsize=8,
              loc='upper right', ncol=1, framealpha=0.9)
    ax.set_title('B. Margin-band transition flows', fontsize=12, fontweight='bold',
                 color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel C: Loyal vs Volatile margin distribution ──────────────────
    ax = axes[2]
    types_order = ['loyal', 'moderate', 'volatile']
    type_display = ['Loyal\n(201+ ep)', 'Moderate\n(6-200 ep)', 'Volatile\n(≤5 ep)']
    type_colours = [ACID, SOLAR, INFARED]

    # Build type→band data
    type_data = {}
    for r in aggregate:
        dt = r['delegator_type']
        mb = r['margin_band']
        if dt in types_order and mb in bands_order:
            type_data.setdefault(dt, {})[mb] = float(r['pct_within_type'])

    x = np.arange(len(bands_order))
    width = 0.25
    for i, dt in enumerate(types_order):
        vals = [type_data.get(dt, {}).get(b, 0) for b in bands_order]
        offset = (i - 1) * width
        ax.bar(x + offset, vals, width, label=type_display[i].replace('\n', ' '),
               color=type_colours[i], alpha=0.85, edgecolor=WHITE, linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(bands_order, fontsize=9)
    ax.set_xlabel('Pool margin band', fontsize=10, fontweight='bold')
    ax.set_ylabel('% of delegations within type', fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
    ax.set_title('C. Margin preference by delegator loyalty', fontsize=12,
                 fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'switch_motivation.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
