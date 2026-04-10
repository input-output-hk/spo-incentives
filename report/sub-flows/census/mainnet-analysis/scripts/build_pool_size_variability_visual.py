#!/usr/bin/env python3
"""build_pool_size_variability_visual.py
Three-panel figure for pool size variability:
  Panel A – CV distribution histogram (productive pools, last year)
  Panel B – Per-epoch size dispersion time series (mean ± stddev envelope)
  Panel C – Per-epoch CV trend with 20-epoch moving average
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
COBALT    = '#2C4FFA'
SOLAR     = '#FFBA36'
ACID      = '#06FF89'

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')
FIG  = os.path.join(os.path.dirname(__file__), '..', 'figures')


def load_csv(name):
    rows = []
    with open(os.path.join(DATA, name)) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def moving_avg(arr, window=20):
    out = np.full_like(arr, np.nan, dtype=float)
    for i in range(len(arr)):
        lo = max(0, i - window + 1)
        out[i] = np.nanmean(arr[lo:i+1])
    return out


def build_figure():
    cv_dist = load_csv('pool_size_cv_distribution.csv')
    ts = load_csv('pool_size_dispersion_timeseries.csv')

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.30, left=0.05, right=0.97, top=0.88, bottom=0.15)

    # ── Panel A: CV distribution histogram ──────────────────────────────
    ax = axes[0]
    buckets = [r['cv_bucket'] for r in cv_dist]
    counts  = [int(r['pool_count']) for r in cv_dist]
    pcts    = [float(r['pct']) for r in cv_dist]
    colours = [ACID, ELECTRIC, COBALT, SOLAR, DAWN, INFARED]

    bars = ax.bar(range(len(buckets)), counts, color=colours[:len(buckets)],
                  edgecolor=WHITE, linewidth=0.5)
    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(buckets)))
    ax.set_xticklabels(buckets, fontsize=9)
    ax.set_xlabel('Coefficient of variation (CV)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Number of productive pools', fontsize=10, fontweight='bold')
    ax.set_title('A. Stake variability over 1 year (epochs 551–623)',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel B: Size dispersion time series ────────────────────────────
    ax = axes[1]
    epochs = np.array([int(r['epoch_no']) for r in ts])
    means  = np.array([float(r['mean_ada']) for r in ts]) / 1e6  # in M ADA
    stds   = np.array([float(r['stddev_ada']) for r in ts]) / 1e6
    mins   = np.array([float(r['min_ada']) for r in ts]) / 1e6
    maxs   = np.array([float(r['max_ada']) for r in ts]) / 1e6

    ax.fill_between(epochs, means - stds, means + stds, alpha=0.25, color=ELECTRIC,
                    label='Mean ± 1 SD')
    ax.plot(epochs, means, color=COBALT, linewidth=1.2, label='Mean pool stake')
    ax.plot(epochs, maxs, color=INFARED, linewidth=0.7, alpha=0.6, label='Max pool')
    ax.plot(epochs, mins, color=ACID, linewidth=0.7, alpha=0.6, label='Min productive')

    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylabel('Pool stake (M ADA)', fontsize=10, fontweight='bold')
    ax.set_title('B. Pool size distribution over time',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')
    ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Panel C: CV time series ─────────────────────────────────────────
    ax = axes[2]
    cvs = np.array([float(r['cv_pct']) for r in ts])
    pool_counts = np.array([int(r['pool_count']) for r in ts])
    ma = moving_avg(cvs)

    ax.bar(epochs, cvs, width=1.0, color=DAWN, alpha=0.4, label='Per-epoch CV (%)')
    ax.plot(epochs, ma, color=INFARED, linewidth=2, label='20-epoch MA')

    ax2 = ax.twinx()
    ax2.plot(epochs, pool_counts, color=COBALT, linewidth=1, alpha=0.7, linestyle='--',
             label='Pool count')
    ax2.set_ylabel('Productive pool count', fontsize=9, color=COBALT)
    ax2.tick_params(axis='y', labelcolor=COBALT)
    ax2.spines['top'].set_visible(False)

    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylabel('Coefficient of variation (%)', fontsize=10, fontweight='bold')
    ax.set_title('C. System-wide size dispersion trend',
                 fontsize=11, fontweight='bold', color=INFARED, loc='left')

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper right',
              framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ── Save ────────────────────────────────────────────────────────────
    os.makedirs(FIG, exist_ok=True)
    out = os.path.join(FIG, 'pool_size_variability.png')
    fig.savefig(out, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out}')


if __name__ == '__main__':
    build_figure()
