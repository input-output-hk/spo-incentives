import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_png_plots(csv_path='all_epochs_summary.csv'):
    """
    Loads Cardano epoch summary data, performs an expanded analysis, and saves
    the resulting plots as high-quality, professionally styled PNG files using
    the term "Healthy Pools" for clarity and consistency with the report.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"--- ERROR: The file '{csv_path}' was not found. ---")
        return

    # --- Corrected Data Aggregation ---
    rows_to_exclude = ['Inactive', '--- TOTALS ---']
    analysis_df = df[~df['stake_range'].isin(rows_to_exclude)].copy()

    # --- Metric Calculation ---
    total_pools_by_epoch = analysis_df.groupby('epoch')['pools_with_blocks'].sum()
    total_stake_by_epoch = analysis_df.groupby('epoch')['controlled_stake_ada'].sum()
    total_blocks_by_epoch = analysis_df.groupby('epoch')['blocks_produced'].sum()

    # --- Using "Healthy Pools" Terminology ---
    healthy_pools_df = analysis_df[analysis_df['stake_range'] != '< 3M'].copy()
    healthy_pools_by_epoch = healthy_pools_df.groupby('epoch')['pools_with_blocks'].sum()
    healthy_stake_by_epoch = healthy_pools_df.groupby('epoch')['controlled_stake_ada'].sum()
    
    stake_percentage_in_healthy = (healthy_stake_by_epoch / total_stake_by_epoch) * 100
    epochs = total_pools_by_epoch.index

    MAX_BLOCKS_PER_EPOCH = 21600
    block_production_health = (total_blocks_by_epoch / MAX_BLOCKS_PER_EPOCH) * 100
    
    TOTAL_CIRCULATING_SUPPLY_APPROX = 38_000_000_000
    active_stake_participation = (total_stake_by_epoch / TOTAL_CIRCULATING_SUPPLY_APPROX) * 100

    print("[SUCCESS] Data processed. Applying new styles and generating 5 PNG files...")

    # --- Professional Styling Setup ---
    colors = {
        'primary': '#005f73',
        'secondary': '#0a9396',
        'accent_green': '#2E8B57',
        'accent_purple': '#483D8B',
        'mean_line': '#ae2012',
        'grid': '#d8e2dc'
    }

    sns.set_theme(style="whitegrid", rc={
        'font.family': 'sans-serif', 'font.sans-serif': 'Arial',
        'axes.titlesize': 20, 'axes.titleweight': 'bold', 'axes.labelsize': 16,
        'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 14,
        'grid.color': colors['grid'], 'grid.linestyle': '--',
        'axes.edgecolor': 'black'
    })

    # --- Plot 1: Block-Producing Pools ---
    plt.figure(figsize=(12, 7))
    plt.plot(epochs, total_pools_by_epoch, marker='o', linestyle='-', label='Pools Producing Blocks', color=colors['primary'], linewidth=2.5)
    plt.plot(epochs, healthy_pools_by_epoch, marker='s', linestyle='-', label='Healthy Pools (Stake > 3M)', color=colors['secondary'], linewidth=2)
    plt.axhline(total_pools_by_epoch.mean(), color=colors['mean_line'], linestyle=':', linewidth=2, label=f'Mean Total ({total_pools_by_epoch.mean():.0f})')
    plt.title('Block-Producing Pools per Epoch')
    plt.xlabel('Epoch Number')
    plt.ylabel('Number of Pools')
    plt.ylim(bottom=0)
    plt.legend()
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    sns.despine()
    plt.savefig('pool_count_epoch-pinned.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  - Saved 'pool_count_epoch-pinned.png'")

    # --- Plot 2: Percentage of Stake in Healthy Pools ---
    plt.figure(figsize=(12, 7))
    plt.plot(epochs, stake_percentage_in_healthy, marker='o', linestyle='-', color=colors['accent_green'], linewidth=2.5)
    plt.axhline(stake_percentage_in_healthy.mean(), color=colors['mean_line'], linestyle=':', linewidth=2, label=f'Mean ({stake_percentage_in_healthy.mean():.2f}%)')
    plt.title('Percentage of Active Stake in Healthy Pools')
    plt.xlabel('Epoch Number')
    plt.ylabel('Percentage of Stake (%)')
    plt.ylim(96.5, 98)
    plt.legend()
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}%'))
    sns.despine()
    plt.savefig('stake_percentage_epoch-pinned.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  - Saved 'stake_percentage_epoch-pinned.png'")

    # --- Plot 3: Active Stake Distribution ---
    plt.figure(figsize=(12, 7))
    plt.plot(epochs, total_stake_by_epoch / 1e9, marker='o', linestyle='-', label='Total Active Stake', color=colors['primary'], linewidth=2.5)
    plt.plot(epochs, healthy_stake_by_epoch / 1e9, marker='s', linestyle='-', label='Stake in Healthy Pools (> 3M)', color=colors['secondary'], linewidth=2)
    plt.fill_between(epochs, healthy_stake_by_epoch / 1e9, color=colors['secondary'], alpha=0.2)
    plt.title('Active Stake Distribution per Epoch')
    plt.xlabel('Epoch Number')
    plt.ylabel('Stake (in Billions of ADA)')
    plt.legend()
    sns.despine()
    plt.savefig('stake_distribution_epoch-pinned.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  - Saved 'stake_distribution_epoch-pinned.png'")
    
    # --- Plot 4: Block Production Health ---
    plt.figure(figsize=(12, 7))
    plt.plot(epochs, block_production_health, marker='o', linestyle='-', color=colors['accent_purple'], linewidth=2.5)
    plt.axhline(block_production_health.mean(), color=colors['mean_line'], linestyle=':', linewidth=2, label=f'Mean ({block_production_health.mean():.1f}%)')
    plt.title('Block Production Health per Epoch')
    plt.xlabel('Epoch Number')
    plt.ylabel(f'Block Production (% of {MAX_BLOCKS_PER_EPOCH:,} max)')
    plt.ylim(90, 100)
    plt.legend()
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1f}%'))
    sns.despine()
    plt.savefig('block_production_health-pinned.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  - Saved 'block_production_health-pinned.png'")
    
    # --- Plot 5: Active Stake Participation ---
    plt.figure(figsize=(12, 7))
    plt.plot(epochs, active_stake_participation, marker='o', linestyle='-', color=colors['primary'], linewidth=2.5)
    plt.axhline(active_stake_participation.mean(), color=colors['mean_line'], linestyle=':', linewidth=2, label=f'Mean ({active_stake_participation.mean():.1f}%)')
    plt.title('Active Stake Participation Rate')
    plt.xlabel('Epoch Number')
    plt.ylabel('% of Total Supply in Consensus')
    plt.ylim(55, 60)
    plt.legend()
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1f}%'))
    sns.despine()
    plt.savefig('active_stake_participation-pinned.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("  - Saved 'active_stake_participation-pinned.png'")

    print("\n[COMPLETE] All five plots have been saved as high-resolution PNG files.")

if __name__ == '__main__':
    generate_png_plots()

