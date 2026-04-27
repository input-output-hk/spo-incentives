#!/usr/bin/env python3
"""build_cv_by_segment.py
Classify pools into the 4-segment taxonomy (Custodial by pledge, by delegation,
by extraction, Retail) and compute CV distribution per segment.

Classification logic (from Operator's Cut §4.3, median-based):
1. Custodial by pledge: pool_class == 'private'
2. Custodial by extraction: NOT private AND margin >= 0.99
3. Custodial by delegation: NOT private, NOT extraction, median delegation >= 100K ADA
   (median computed from db-sync epoch_stake per pool)
4. Retail: everything else
"""

import csv, os, sys
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
ULTRAVIOLET = '#A700FF'
COBALT    = '#2C4FFA'
SOLAR     = '#FFBA36'

BASE = os.path.dirname(os.path.abspath(__file__))
CENSUS_DATA = os.path.join(BASE, '..', 'data')
OPCUT_DATA  = os.path.join(BASE, '..', '..', '..', 'operator-delegator-distribution',
                           'mainnet-analysis', 'data')
FIG = os.path.join(BASE, '..', 'figures')


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def classify_pools():
    """Return dict: pool_id_bech32 -> segment label."""

    # 1. Load reward_split_snapshot_623 for pool_class + margin
    snapshot_path = os.path.join(OPCUT_DATA, 'reward_split_snapshot_623.csv')
    if not os.path.exists(snapshot_path):
        snapshot_path = os.path.join(OPCUT_DATA, 'reward_split_snapshot.csv')
    snapshot = load_csv(snapshot_path)

    # 2. Load median delegation per pool (from db-sync epoch_stake)
    median_path = os.path.join(OPCUT_DATA, 'pool_median_delegation_623.csv')
    medians = {}
    if os.path.exists(median_path):
        for r in load_csv(median_path):
            medians[r['pool_bech32']] = float(r['median_ada'])

    pool_segment = {}
    for p in snapshot:
        pid = p['pool_id_bech32']
        pool_class = p.get('pool_class', '').strip()
        margin = float(p.get('margin_rate', 0))
        dcnt = int(p.get('delegator_cnt', 0))

        if pool_class == 'private':
            pool_segment[pid] = 'Custodial by pledge'
        elif margin >= 0.99:
            pool_segment[pid] = 'Custodial by extraction'
        elif dcnt > 0 and medians.get(pid, 0) >= 100_000:
            pool_segment[pid] = 'Custodial by delegation'
        else:
            pool_segment[pid] = 'Retail'

    return pool_segment


def main():
    pool_segment = classify_pools()

    # Load CV data
    cv_data = load_csv(os.path.join(CENSUS_DATA, 'pool_size_variability.csv'))

    # Match and classify
    segments = ['Custodial by pledge', 'Custodial by delegation',
                'Custodial by extraction', 'Retail']
    seg_cvs = {s: [] for s in segments}
    unmatched = 0

    for row in cv_data:
        pid = row['pool_id']
        cv_str = row.get('cv_pct', '')
        if not cv_str:
            continue
        cv = float(cv_str)
        seg = pool_segment.get(pid, None)
        if seg is None:
            # Pool not in epoch-614 snapshot — likely appeared after.
            # Default to Retail if margin info unavailable.
            unmatched += 1
            continue
        seg_cvs[seg].append(cv)

    print(f'Matched pools: {sum(len(v) for v in seg_cvs.values())}, unmatched: {unmatched}')

    # ── Print summary table ─────────────────────────────────────────────
    print(f'\n{"Segment":<28} {"Pools":>6} {"Mean CV":>8} {"Median CV":>10} '
          f'{"CV<10%":>7} {"CV>50%":>7}')
    print('-' * 70)
    for s in segments:
        arr = np.array(seg_cvs[s]) if seg_cvs[s] else np.array([0])
        n = len(seg_cvs[s])
        mean = np.mean(arr) if n else 0
        med = np.median(arr) if n else 0
        low = np.sum(arr < 10) if n else 0
        high = np.sum(arr > 50) if n else 0
        print(f'{s:<28} {n:>6} {mean:>8.1f}% {med:>9.1f}% '
              f'{low:>6} ({100*low/max(n,1):.0f}%) {high:>3} ({100*high/max(n,1):.0f}%)')

    # ── Save per-segment CSV ────────────────────────────────────────────
    out_csv = os.path.join(CENSUS_DATA, 'pool_cv_by_segment.csv')
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['segment', 'pool_count', 'mean_cv', 'median_cv', 'p25_cv',
                     'p75_cv', 'pct_below_10', 'pct_above_50'])
        for s in segments:
            arr = np.array(seg_cvs[s]) if seg_cvs[s] else np.array([0])
            n = len(seg_cvs[s])
            w.writerow([
                s, n,
                round(np.mean(arr), 2) if n else 0,
                round(np.median(arr), 2) if n else 0,
                round(np.percentile(arr, 25), 2) if n else 0,
                round(np.percentile(arr, 75), 2) if n else 0,
                round(100 * np.sum(arr < 10) / max(n, 1), 1),
                round(100 * np.sum(arr > 50) / max(n, 1), 1),
            ])
    print(f'\nSaved {out_csv}')

    # ── Build figure ────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(WHITE)
    fig.subplots_adjust(wspace=0.30, left=0.07, right=0.97, top=0.88, bottom=0.18)

    seg_colours = {
        'Custodial by pledge': ULTRAVIOLET,
        'Custodial by delegation': COBALT,
        'Custodial by extraction': DAWN,
        'Retail': ACID,
    }

    # Panel A: Box plot of CV by segment
    ax = axes[0]
    data_for_box = [seg_cvs[s] for s in segments if seg_cvs[s]]
    labels_for_box = [s.replace('Custodial by ', 'C. ') for s in segments if seg_cvs[s]]
    colours_for_box = [seg_colours[s] for s in segments if seg_cvs[s]]

    bp = ax.boxplot(data_for_box, labels=labels_for_box, patch_artist=True,
                    showfliers=False, widths=0.5,
                    medianprops=dict(color=BLACK, linewidth=2))
    for patch, col in zip(bp['boxes'], colours_for_box):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)

    # Add pool counts above each box
    for i, s in enumerate([s for s in segments if seg_cvs[s]]):
        n = len(seg_cvs[s])
        ax.text(i + 1, ax.get_ylim()[1] * 0.95, f'n={n}', ha='center',
                fontsize=9, fontweight='bold', color=seg_colours[s])

    ax.set_ylabel('Coefficient of variation (%)', fontsize=10, fontweight='bold')
    ax.set_title('A. Stake variability by market segment',
                 fontsize=12, fontweight='bold', color=INFARED, loc='left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', rotation=15)

    # Panel B: Stacked bar — % of pools in each CV bucket per segment
    ax = axes[1]
    buckets = ['0-10%', '10-25%', '25-50%', '50-100%', '100%+']
    bucket_colours = [ACID, ELECTRIC, SOLAR, DAWN, INFARED]

    seg_bucket_pcts = {}
    for s in segments:
        arr = np.array(seg_cvs[s]) if seg_cvs[s] else np.array([])
        n = max(len(arr), 1)
        seg_bucket_pcts[s] = [
            100 * np.sum(arr <= 10) / n,
            100 * np.sum((arr > 10) & (arr <= 25)) / n,
            100 * np.sum((arr > 25) & (arr <= 50)) / n,
            100 * np.sum((arr > 50) & (arr <= 100)) / n,
            100 * np.sum(arr > 100) / n,
        ]

    x = np.arange(len(segments))
    width = 0.55
    bottoms = np.zeros(len(segments))
    for i, (bucket, col) in enumerate(zip(buckets, bucket_colours)):
        vals = [seg_bucket_pcts[s][i] for s in segments]
        ax.bar(x, vals, width, bottom=bottoms, label=bucket, color=col,
               alpha=0.85, edgecolor=WHITE, linewidth=0.5)
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('Custodial by ', 'C. ') for s in segments],
                       fontsize=9, rotation=15)
    ax.set_ylabel('% of pools in segment', fontsize=10, fontweight='bold')
    ax.set_title('B. CV bucket distribution by segment',
                 fontsize=12, fontweight='bold', color=INFARED, loc='left')
    ax.legend(title='CV bucket', fontsize=8, title_fontsize=9,
              loc='upper right', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    os.makedirs(FIG, exist_ok=True)
    out_fig = os.path.join(FIG, 'pool_cv_by_segment.png')
    fig.savefig(out_fig, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close(fig)
    print(f'Saved {out_fig}')


if __name__ == '__main__':
    main()
