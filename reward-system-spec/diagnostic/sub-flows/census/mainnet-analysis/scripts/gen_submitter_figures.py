#!/usr/bin/env python3
"""Generate §6 Transaction Submitter figures for the Census.

Produces 4 figures following the analytical decomposition:
  1. submitter_volume.png        — Tx volume + fee (Instance A, full) with unique-addr overlay (Instance B, partial)
  2. submitter_population.png    — Stacked bar: address-type decomposition by epoch
  3. submitter_fee_decomposition.png — Who pays: fee share by address type across epochs
  4. submitter_concentration.png — Cumulative fee share + Lorenz-style at epoch 384

Data sources:
  - Instance A (epoch 623): tx_epoch_summary, tx_composition (full 208–622)
  - Instance B (epoch 384): unique submitters, address-type decomposition, fee attribution, concentration
"""

import csv
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ── Paths ──
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
FIG  = os.path.join(BASE, 'figures')
os.makedirs(FIG, exist_ok=True)

# ── Style (match existing Census figures — light background, clean) ──
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.labelsize': 10,
})

# Colour palette — IOG brand (primary + secondary)
C_RED    = '#E52321'
C_DAWN   = '#EC641D'
C_GREEN  = '#06FF89'
C_BLUE   = '#16E9D8'
C_VIOLET = '#A700FF'
C_YELLOW = '#F2FF58'
C_AMBER  = '#FFBA36'
C_COBALT = '#2C4FFA'
C_PINK   = '#FF79FC'

# Category colours for address types
ADDR_COLOURS = {
    'base_key':           '#2C4FFA',   # Cobalt Pulse — stakeable key
    'base_script':        '#16E9D8',   # Electric Blue — stakeable script
    'enterprise_key':     '#EC641D',   # Dawn — non-stakeable key
    'enterprise_script':  '#E52321',   # Infared — non-stakeable script
    'other':              '#999999',   # Grey — Byron / legacy
}
ADDR_LABELS = {
    'base_key':           'Base key (addr1q) — stakeable',
    'base_script':        'Base script (addr1z) — stakeable',
    'enterprise_key':     'Enterprise key (addr1v) — non-stakeable',
    'enterprise_script':  'Enterprise script (addr1w) — non-stakeable',
    'other':              'Other (Byron / legacy)',
}

def thousands(x, pos): return f'{x/1e3:.0f}K' if x >= 1e3 else f'{x:.0f}'
def millions(x, pos):  return f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'

# ══════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════

def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

# Instance A full series
summary_a = load_csv(os.path.join(DATA, 'tx_epoch_summary_a.csv'))   # will create below
comp_a    = load_csv(os.path.join(DATA, 'tx_composition_a.csv'))

# Instance B sampled
unique_b  = load_csv(os.path.join(DATA, 'submitter_unique_by_epoch.csv'))
addrtype  = load_csv(os.path.join(DATA, 'submitter_addr_type_by_epoch.csv'))
feetype   = load_csv(os.path.join(DATA, 'submitter_fee_by_addr_type.csv'))
conc      = load_csv(os.path.join(DATA, 'submitter_concentration_384.csv'))

# Parse Instance A
epochs_a   = [int(r['epoch_no']) for r in summary_a]
tx_a       = [int(r['tx_count']) for r in summary_a]
fee_a      = [float(r['total_fee_ada']) for r in summary_a]

# Parse composition
comp_epochs = [int(r['epoch_no']) for r in comp_a]
script_tx   = [int(r['script_tx']) for r in comp_a]
key_tx      = [int(r['key_tx']) for r in comp_a]
script_fee  = [float(r['script_fee']) for r in comp_a]
key_fee     = [float(r['key_fee']) for r in comp_a]

# Parse unique submitters (Instance B)
ub_epochs = [int(r['epoch_no']) for r in unique_b]
ub_addrs  = [int(r['unique_addrs']) for r in unique_b]
ub_tx     = [int(r['tx_count']) for r in unique_b]

# ══════════════════════════════════════════════════════════════════
# Figure 1: Volume + unique submitters overlay
# ══════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                                gridspec_kw={'height_ratios': [2, 1]})
fig.suptitle('Transaction Submitters — Volume and Population', fontsize=14, fontweight='bold', y=0.98)

# Top panel: tx count + unique addrs
ax1.fill_between(epochs_a, tx_a, alpha=0.25, color=C_COBALT, label='Tx count (Instance A, 208–622)')
ax1.plot(epochs_a, tx_a, color=C_COBALT, linewidth=0.8, alpha=0.6)
ax1b = ax1.twinx()
ax1b.plot(ub_epochs, ub_addrs, 'o-', color=C_RED, markersize=4, linewidth=2,
          label='Unique input addresses (Instance B, 208–384)')
ax1b.axvline(x=384, color='grey', linestyle='--', alpha=0.5, linewidth=0.8)
ax1b.annotate('Instance B\nboundary (ep 384)', xy=(384, max(ub_addrs)*0.9),
              fontsize=8, color='grey', ha='right')

ax1.set_ylabel('Transactions per epoch', color=C_COBALT)
ax1b.set_ylabel('Unique input addresses', color=C_RED)
ax1.yaxis.set_major_formatter(FuncFormatter(thousands))
ax1b.yaxis.set_major_formatter(FuncFormatter(thousands))
ax1.set_title('Transaction count vs distinct submitter addresses')

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8, framealpha=0.9)

# Bottom panel: fee per epoch
ax2.fill_between(epochs_a, fee_a, alpha=0.3, color=C_DAWN)
ax2.plot(epochs_a, fee_a, color=C_DAWN, linewidth=1)
ax2.axvline(x=384, color='grey', linestyle='--', alpha=0.5, linewidth=0.8)
ax2.set_ylabel('Fee per epoch (ADA)')
ax2.set_xlabel('Epoch')
ax2.yaxis.set_major_formatter(FuncFormatter(thousands))
ax2.set_title('Fee revenue per epoch')

# Alonzo marker
for ax in [ax1, ax2]:
    ax.axvline(x=290, color=C_GREEN, linestyle=':', alpha=0.4, linewidth=1)
ax1.annotate('Alonzo\n(ep 290)', xy=(290, max(tx_a)*0.85), fontsize=7, color=C_GREEN, ha='left')

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(FIG, 'submitter_volume.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print('✓ submitter_volume.png')

# ══════════════════════════════════════════════════════════════════
# Figure 2: Population decomposition by address type (stacked bar)
# ══════════════════════════════════════════════════════════════════
# Group addrtype data by epoch
at_epochs = sorted(set(int(r['epoch_no']) for r in addrtype))
categories = ['base_key', 'enterprise_key', 'enterprise_script', 'base_script', 'other']

fig, (ax_count, ax_pct) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Submitter Population Decomposition by Address Type', fontsize=14, fontweight='bold')

bar_width = 6
for panel_idx, (ax, mode) in enumerate([(ax_count, 'abs'), (ax_pct, 'pct')]):
    for i, ep in enumerate(at_epochs):
        ep_data = {r['addr_type']: int(r['n_addrs']) for r in addrtype if int(r['epoch_no']) == ep}
        total = sum(ep_data.get(c, 0) for c in categories)
        bottom = 0
        for cat in categories:
            val = ep_data.get(cat, 0)
            if mode == 'pct' and total > 0:
                val = 100.0 * val / total
            ax.bar(ep, val, bottom=bottom, width=bar_width, color=ADDR_COLOURS[cat],
                   label=ADDR_LABELS[cat] if i == 0 else None, edgecolor='white', linewidth=0.3)
            bottom += val

    ax.set_xlabel('Epoch')
    if mode == 'abs':
        ax.set_title('Address count by type')
        ax.set_ylabel('Unique addresses')
        ax.yaxis.set_major_formatter(FuncFormatter(thousands))
    else:
        ax.set_title('Share by type (%)')
        ax.set_ylabel('% of addresses')
        ax.set_ylim(0, 100)

ax_count.legend(fontsize=7, loc='upper left', framealpha=0.9)
plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIG, 'submitter_population.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print('✓ submitter_population.png')

# ══════════════════════════════════════════════════════════════════
# Figure 3: Fee decomposition — who pays (stacked bar + % panel)
# ══════════════════════════════════════════════════════════════════
ft_epochs = sorted(set(int(r['epoch_no']) for r in feetype))

fig, (ax_abs, ax_pct) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Fee Revenue Decomposition by Submitter Address Type', fontsize=14, fontweight='bold')

for panel_idx, (ax, mode) in enumerate([(ax_abs, 'abs'), (ax_pct, 'pct')]):
    for i, ep in enumerate(ft_epochs):
        ep_data = {r['addr_type']: float(r['fee_ada']) for r in feetype if int(r['epoch_no']) == ep}
        total = sum(ep_data.get(c, 0) for c in categories)
        bottom = 0
        for cat in categories:
            val = ep_data.get(cat, 0)
            if mode == 'pct' and total > 0:
                val = 100.0 * val / total
            ax.bar(ep, val, bottom=bottom, width=bar_width, color=ADDR_COLOURS[cat],
                   label=ADDR_LABELS[cat] if i == 0 else None, edgecolor='white', linewidth=0.3)
            bottom += val

    ax.set_xlabel('Epoch')
    if mode == 'abs':
        ax.set_title('Fee (ADA) by address type')
        ax.set_ylabel('Fee (ADA)')
        ax.yaxis.set_major_formatter(FuncFormatter(thousands))
    else:
        ax.set_title('Fee share by type (%)')
        ax.set_ylabel('% of epoch fees')
        ax.set_ylim(0, 100)
        # Add horizontal lines at key thresholds
        ax.axhline(y=50, color='grey', linestyle=':', alpha=0.3)

ax_abs.legend(fontsize=7, loc='upper left', framealpha=0.9)
plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIG, 'submitter_fee_decomposition.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print('✓ submitter_fee_decomposition.png')

# ══════════════════════════════════════════════════════════════════
# Figure 4: Fee concentration at epoch 384 + script vs key composition
# ══════════════════════════════════════════════════════════════════
fig, (ax_conc, ax_comp) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Fee Concentration and Script/Key Composition', fontsize=14, fontweight='bold')

# Left: concentration waterfall / cumulative
buckets = [r['bucket'] for r in conc]
fees_c  = [float(r['fee_ada']) for r in conc]
pcts    = [float(r['fee_pct']) for r in conc]
n_addr  = [int(r['n_addresses']) for r in conc]

bucket_labels = ['Top 10', 'Top 11–50', 'Top 51–100', 'Top 101–500', 'Rest (~100K)']
cumulative_pct = np.cumsum(pcts)
colors_conc = [C_RED, C_DAWN, C_AMBER, C_COBALT, '#cccccc']

bars = ax_conc.bar(range(len(buckets)), pcts, color=colors_conc, edgecolor='white', linewidth=0.5)
ax_conc.set_xticks(range(len(buckets)))
ax_conc.set_xticklabels(bucket_labels, fontsize=8, rotation=15)
ax_conc.set_ylabel('Fee share (%)')
ax_conc.set_title('Fee Concentration — Epoch 384')

# Annotate with cumulative
for i, (bar, cp) in enumerate(zip(bars, cumulative_pct)):
    ax_conc.annotate(f'{pcts[i]:.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9, fontweight='bold')
    if i < len(buckets) - 1:
        ax_conc.annotate(f'cum: {cp:.0f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height() + 2),
                         ha='center', va='bottom', fontsize=7, color='grey')

# Right: script vs key composition over time (from Instance A)
# Compute script % of tx and script % of fee per epoch
script_pct_tx  = [100.0 * s / (s + k) if (s + k) > 0 else 0 for s, k in zip(script_tx, key_tx)]
script_pct_fee = [100.0 * s / (s + k) if (s + k) > 0 else 0 for s, k in zip(script_fee, key_fee)]

ax_comp.fill_between(comp_epochs, script_pct_fee, alpha=0.3, color=C_RED, label='Script share of fees')
ax_comp.plot(comp_epochs, script_pct_fee, color=C_RED, linewidth=1.5)
ax_comp.fill_between(comp_epochs, script_pct_tx, alpha=0.2, color=C_COBALT, label='Script share of tx count')
ax_comp.plot(comp_epochs, script_pct_tx, color=C_COBALT, linewidth=1.5)
ax_comp.axvline(x=290, color=C_GREEN, linestyle=':', alpha=0.5)
ax_comp.annotate('Alonzo', xy=(292, 5), fontsize=8, color=C_GREEN)
ax_comp.axvline(x=384, color='grey', linestyle='--', alpha=0.3)
ax_comp.set_xlabel('Epoch')
ax_comp.set_ylabel('Script share (%)')
ax_comp.set_title('Script Transaction Share (Instance A, 208–622)')
ax_comp.legend(fontsize=8, loc='upper left')
ax_comp.set_ylim(0, 55)

plt.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(FIG, 'submitter_concentration.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
print('✓ submitter_concentration.png')

print('\nAll figures generated.')
