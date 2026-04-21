#!/usr/bin/env python3
"""build_switch_motivation_ros_visual.py
Three-panel figure for switch motivation using ROS-based metrics:
  Panel A – Operator take × Net ROS direction heatmap
  Panel B – ROS differential distribution (histogram)
  Panel C – Loyal vs volatile margin-band distribution (reused from existing)
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

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')


def load_csv(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def build_figure():
    take_ros = load_csv('switch_motivation_ros.csv')
    take_size = load_csv('switch_motivation_take_size.csv')
    loyal_agg = load_csv('loyal_pool_aggregate.csv')

    fig, axes = plt.subplots(1, 3, figsize=(20, 6.5))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.32, left=0.05, right=0.97, top=0.88, bottom=0.15)

    # ── Panel A: Take × ROS heatmap ────────────────────────────────────
    ax = axes[0]
    take_labels = ['lower_take', 'similar_take', 'higher_take']
    take_display = ['Lower\noperator take', 'Similar\noperator take', 'Higher\noperator take']
    ros_labels = ['better_ros', 'similar_ros', 'worse_ros']
    ros_display = ['Better\nnet ROS', 'Similar\nnet ROS', 'Worse\nnet ROS']

    grid = np.zeros((3, 3))
    for r in take_ros:
        ti = take_labels.index(r['take_direction']) if r['take_direction'] in take_labels else None
        ri = ros_labels.index(r['ros_direction']) if r['ros_direction'] in ros_labels else None
        if ti is not None and ri is not None:
            grid[ti, ri] = float(r['pct'])

    im = ax.imshow(grid, cmap='YlOrRd', aspect='auto', vmin=0, vmax=28)
    for i in range(3):
        for j in range(3):
            val = grid[i, j]
            colour = WHITE if val > 18 else BLACK
            ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                    fontsize=12, fontweight='bold', color=colour)

    ax.set_xticks(range(3))
    ax.set_xticklabels(ros_display, fontsize=9)
    ax.set_yticks(range(3))
    ax.set_yticklabels(take_display, fontsize=9)
    ax.set_xlabel('Net ROS direction', fontsize=10, fontweight='bold')
    ax.set_ylabel('Operator take direction', fontsize=10, fontweight='bold')
    ax.set_title('A. Switch motivation: take × ROS',
                 fontsize=12, fontweight='bold', color=INFARED, loc='left')

    # ── Panel B: Take × Size heatmap ───────────────────────────────────
    ax = axes[1]
    size_labels = ['to_smaller', 'similar_size', 'to_larger']
    size_display = ['To smaller\npool', 'Similar\nsize', 'To larger\npool']

    grid2 = np.zeros((3, 3))
    for r in take_size:
        ti = take_labels.index(r['take_direction']) if r['take_direction'] in take_labels else None
        si = size_labels.index(r['size_direction']) if r['size_direction'] in size_labels else None
        if ti is not None and si is not None:
            grid2[ti, si] = float(r['pct'])

    im2 = ax.imshow(grid2, cmap='YlOrRd', aspect='auto', vmin=0, vmax=20)
    for i in range(3):
        for j in range(3):
            val = grid2[i, j]
            colour = WHITE if val > 15 else BLACK
            ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                    fontsize=12, fontweight='bold', color=colour)

    ax.set_xticks(range(3))
    ax.set_xticklabels(size_display, fontsize=9)
    ax.set_yticks(range(3))
    ax.set_yticklabels(take_display, fontsize=9)
    ax.set_xlabel('Pool size direction', fontsize=10, fontweight='bold')
    ax.set_ylabel('Operator take direction', fontsize=10, fontweight='bold')
    ax.set_title('B. Switch motivation: take × size',
                 fontsize=12, fontweight='bold', color=INFARED, loc='left')

    # ── Panel C: Loyal margin-band distribution ─────────────────────────
    ax = axes[2]
    types_order = ['loyal', 'moderate', 'volatile']
    type_display = ['Loyal (201+ ep)', 'Moderate (6-200 ep)', 'Volatile (≤5 ep)']
    type_colours = [ACID, SOLAR, INFARED]
    bands_order = ['0-2%', '2-5%', '5-10%', '10-99%', '100%']

    type_data = {}
    for r in loyal_agg:
        dt = r['delegator_type']
        mb = r['margin_band']
        if dt in types_order and mb in bands_order:
            type_data.setdefault(dt, {})[mb] = float(r['pct_within_type'])

    x = np.arange(len(bands_order))
    width = 0.25
    for i, dt in enumerate(types_order):
        vals = [type_data.get(dt, {}).get(b, 0) for b in bands_order]
        offset = (i - 1) * width
        ax.bar(x + offset, vals, width, label=type_display[i],
               color=type_colours[i], alpha=0.85, edgecolor=WHITE, linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(bands_order, fontsize=9)
    ax.set_xlabel('Pool margin band', fontsize=10, fontweight='bold')
    ax.set_ylabel('% of delegations within type', fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
    ax.set_title('C. Margin preference by loyalty',
                 fontsize=12, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'switch_motivation_ros.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
