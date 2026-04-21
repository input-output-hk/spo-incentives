#!/usr/bin/env python3
"""13_switch_motivation_ros.py
Re-analyse switch motivation using operator take and net ROS from the
reward_split_snapshot (epoch 614) rather than raw margin.

Approach:
1. Load switches from delegation_flow_matrix.csv (pool-to-pool)
   OR reconstruct from the delegation churn data.
   Better: use the raw switch_motivation.csv (margin_direction × size_direction)
   as baseline, but re-compute using operator_take_pct and deleg_yield_per_epoch_pct.

2. For each switch (from pool → to pool), look up:
   - operator_take_pct for origin and destination
   - deleg_yield_per_epoch_pct (net ROS) for origin and destination
   - active_stake_ada (pool size)

3. Classify:
   - take_direction: lower_take / higher_take / similar_take (±1pp)
   - ros_direction: better_ros / worse_ros / similar_ros (±5 bps)
   - size_direction: to_larger / to_smaller / similar_size (±10%)

Output: motivation profile CSVs + summary stats.
"""

import csv, os, sys
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
CENSUS_DATA = os.path.join(BASE, '..', 'data')
OPCUT_DATA  = os.path.join(BASE, '..', '..', '..', 'operator-delegator-distribution',
                           'mainnet-analysis', 'data')


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    # ── Load pool characteristics from reward_split_snapshot ────────────
    snapshot = load_csv(os.path.join(OPCUT_DATA, 'reward_split_snapshot.csv'))
    pool_data = {}
    for p in snapshot:
        pid = p['pool_id_bech32']
        try:
            pool_data[pid] = {
                'operator_take_pct': float(p['operator_take_pct']),
                'net_ros': float(p['deleg_yield_per_epoch_pct']),
                'gross_ros': float(p['epoch_ros']),
                'stake': float(p['active_stake_ada']),
                'margin': float(p['margin_rate']),
                'fixed_cost': float(p['fixed_cost_ada']),
                'pool_class': p['pool_class'],
            }
        except (ValueError, KeyError):
            continue

    print(f'Loaded {len(pool_data)} pools from reward_split_snapshot')

    # ── Reconstruct switches from delegation table via SQL output ───────
    # We need per-switch from_pool → to_pool. The flow_matrix has this but
    # aggregated. Let's use a SQL query instead.
    # For now: run SQL from Python via the existing CSVs won't work.
    # Alternative: use the flow matrix which has from_pool, to_pool, flow_count
    flow_matrix = load_csv(os.path.join(CENSUS_DATA, 'delegation_flow_matrix.csv'))
    print(f'Loaded {len(flow_matrix)} flow corridors')

    # Check columns
    if flow_matrix:
        print(f'Columns: {list(flow_matrix[0].keys())}')

    # ── Classify each flow corridor ─────────────────────────────────────
    results = []
    matched = 0
    unmatched = 0

    for row in flow_matrix:
        from_pool = row.get('from_pool_id', '')
        to_pool = row.get('to_pool_id', '')
        count = int(row.get('flow_count', 0))

        if from_pool not in pool_data or to_pool not in pool_data:
            unmatched += count
            continue

        fp = pool_data[from_pool]
        tp = pool_data[to_pool]
        matched += count

        # Operator take direction (threshold: 1pp)
        take_diff = tp['operator_take_pct'] - fp['operator_take_pct']
        if take_diff < -1.0:
            take_dir = 'lower_take'
        elif take_diff > 1.0:
            take_dir = 'higher_take'
        else:
            take_dir = 'similar_take'

        # Net ROS direction (threshold: 5 bps = 0.005%)
        ros_diff = tp['net_ros'] - fp['net_ros']
        if ros_diff > 0.005:
            ros_dir = 'better_ros'
        elif ros_diff < -0.005:
            ros_dir = 'worse_ros'
        else:
            ros_dir = 'similar_ros'

        # Size direction (threshold: 10%)
        if tp['stake'] > fp['stake'] * 1.1:
            size_dir = 'to_larger'
        elif tp['stake'] < fp['stake'] * 0.9:
            size_dir = 'to_smaller'
        else:
            size_dir = 'similar_size'

        results.append({
            'from_pool': from_pool,
            'to_pool': to_pool,
            'flow_count': count,
            'take_direction': take_dir,
            'ros_direction': ros_dir,
            'size_direction': size_dir,
            'from_take': fp['operator_take_pct'],
            'to_take': tp['operator_take_pct'],
            'from_ros': fp['net_ros'],
            'to_ros': tp['net_ros'],
            'from_stake': fp['stake'],
            'to_stake': tp['stake'],
        })

    total = matched + unmatched
    print(f'\nMatched: {matched} switches ({100*matched/max(total,1):.1f}%)')
    print(f'Unmatched: {unmatched} switches ({100*unmatched/max(total,1):.1f}%)')

    # ── Aggregate: take_direction × ros_direction ───────────────────────
    from collections import Counter
    take_ros = Counter()
    take_size = Counter()
    take_only = Counter()
    ros_only = Counter()

    for r in results:
        c = r['flow_count']
        take_ros[(r['take_direction'], r['ros_direction'])] += c
        take_size[(r['take_direction'], r['size_direction'])] += c
        take_only[r['take_direction']] += c
        ros_only[r['ros_direction']] += c

    total_matched = sum(take_only.values())

    print(f'\n=== OPERATOR TAKE DIRECTION ===')
    for k in ['lower_take', 'similar_take', 'higher_take']:
        n = take_only[k]
        print(f'  {k:20s}: {n:>8,} ({100*n/total_matched:.1f}%)')

    print(f'\n=== NET ROS DIRECTION ===')
    for k in ['better_ros', 'similar_ros', 'worse_ros']:
        n = ros_only[k]
        print(f'  {k:20s}: {n:>8,} ({100*n/total_matched:.1f}%)')

    print(f'\n=== TAKE × ROS MATRIX ===')
    take_labels = ['lower_take', 'similar_take', 'higher_take']
    ros_labels = ['better_ros', 'similar_ros', 'worse_ros']
    print(f'{"":>20s}', end='')
    for rl in ros_labels:
        print(f'  {rl:>14s}', end='')
    print()
    for tl in take_labels:
        print(f'{tl:>20s}', end='')
        for rl in ros_labels:
            n = take_ros[(tl, rl)]
            print(f'  {100*n/total_matched:>13.1f}%', end='')
        print()

    # ── Save take × ros matrix CSV ──────────────────────────────────────
    out_csv = os.path.join(CENSUS_DATA, 'switch_motivation_ros.csv')
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['take_direction', 'ros_direction', 'switch_count', 'pct'])
        for tl in take_labels:
            for rl in ros_labels:
                n = take_ros[(tl, rl)]
                w.writerow([tl, rl, n, round(100*n/total_matched, 2)])
    print(f'\nSaved {out_csv}')

    # ── Save take × size matrix CSV ─────────────────────────────────────
    out_csv2 = os.path.join(CENSUS_DATA, 'switch_motivation_take_size.csv')
    size_labels = ['to_smaller', 'similar_size', 'to_larger']
    with open(out_csv2, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['take_direction', 'size_direction', 'switch_count', 'pct'])
        for tl in take_labels:
            for sl in size_labels:
                n = take_size[(tl, sl)]
                w.writerow([tl, sl, n, round(100*n/total_matched, 2)])
    print(f'Saved {out_csv2}')

    # ── Summary stats on ROS differentials ──────────────────────────────
    ros_diffs = []
    take_diffs = []
    for r in results:
        c = r['flow_count']
        ros_diffs.extend([r['to_ros'] - r['from_ros']] * c)
        take_diffs.extend([r['to_take'] - r['from_take']] * c)

    ros_arr = np.array(ros_diffs)
    take_arr = np.array(take_diffs)

    print(f'\n=== ROS DIFFERENTIAL (to - from) ===')
    print(f'  Mean:   {np.mean(ros_arr)*100:.3f} bps')
    print(f'  Median: {np.median(ros_arr)*100:.3f} bps')
    print(f'  Std:    {np.std(ros_arr)*100:.3f} bps')
    print(f'  P25:    {np.percentile(ros_arr, 25)*100:.3f} bps')
    print(f'  P75:    {np.percentile(ros_arr, 75)*100:.3f} bps')

    print(f'\n=== OPERATOR TAKE DIFFERENTIAL (to - from) ===')
    print(f'  Mean:   {np.mean(take_arr):.2f} pp')
    print(f'  Median: {np.median(take_arr):.2f} pp')
    print(f'  Std:    {np.std(take_arr):.2f} pp')

    # ── Save summary CSV ────────────────────────────────────────────────
    out_csv3 = os.path.join(CENSUS_DATA, 'switch_motivation_ros_summary.csv')
    with open(out_csv3, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'ros_diff_bps', 'take_diff_pp'])
        w.writerow(['mean', round(np.mean(ros_arr)*100, 3), round(np.mean(take_arr), 3)])
        w.writerow(['median', round(np.median(ros_arr)*100, 3), round(np.median(take_arr), 3)])
        w.writerow(['std', round(np.std(ros_arr)*100, 3), round(np.std(take_arr), 3)])
        w.writerow(['p25', round(np.percentile(ros_arr, 25)*100, 3), round(np.percentile(take_arr, 25), 3)])
        w.writerow(['p75', round(np.percentile(ros_arr, 75)*100, 3), round(np.percentile(take_arr, 75), 3)])
    print(f'Saved {out_csv3}')


if __name__ == '__main__':
    main()
