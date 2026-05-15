import pandas as pd
from sqlalchemy import create_engine
from tabulate import tabulate
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import matplotlib.patches as mpatches

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
}
EPOCH_WINDOW = 15  # Using a recent epoch for a current snapshot
# Pin: take the snapshot at epoch 583 (the report's analysis-window end)
# instead of querying dbsync's current MAX(no), which would shift the snapshot
# 7+ months past the published chart.
SNAPSHOT_EPOCH = 583

# --- SQL Query to get delegator stake data ---
# This query gets the total stake for each delegator address at the snapshot epoch.
ANALYSIS_QUERY = f"""
SELECT
    addr_id,
    SUM(amount) AS delegator_total_stake
FROM epoch_stake
WHERE epoch_no = {SNAPSHOT_EPOCH}
GROUP BY addr_id;
"""

def analyze_stake_distribution():
    """
    Analyzes the stake distribution and plots a combined bar chart.
    """
    engine = None
    try:
        print("Creating SQLAlchemy engine...")
        db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
        engine = create_engine(db_url)

        print("Executing main analysis query...")
        df_analysis = pd.read_sql_query(
            ANALYSIS_QUERY,
            engine
        )

        print("Data fetched. Analyzing stake distribution and plotting...")

        # Convert stakes from Lovelace to ADA
        df_analysis['delegator_stake_ada'] = df_analysis['delegator_total_stake'] / 1_000_000

        # --- Define Bins for both charts ---
        bins = [0, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, float('inf')]
        labels = ["<1k", "1k-5k", "5k-10k", "10k-50k", "50k-100k", "100k-500k", "500k-1M", ">1M"]
        df_analysis['stake_category'] = pd.cut(df_analysis['delegator_stake_ada'], bins=bins, labels=labels, right=False)
        
        # --- Generate Combined Bar Chart ---
        print("Generating combined wallet distribution chart...")
        bin_counts = df_analysis['stake_category'].value_counts().reindex(labels)
        # CORRECTED: Removed 'observed=False' for compatibility with older pandas versions
        bin_stake_ada = df_analysis.groupby('stake_category')['delegator_stake_ada'].sum().reindex(labels)
        
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Plot wallet counts on the left y-axis
        sns.barplot(x=bin_counts.index, y=bin_counts.values, ax=ax1, color='lightskyblue')
        ax1.set_title('Wallet Count and Total Staked ADA by Size', fontsize=16, pad=20)
        ax1.set_xlabel('Wallet Size (ADA)', fontsize=12)
        ax1.set_ylabel('Number of Wallets', fontsize=12, color='lightskyblue')
        ax1.tick_params(axis='y', labelcolor='lightskyblue')
        
        # Force the bottom of the y-axis to be 0
        ax1.set_ylim(bottom=0)

        # Custom formatter for the left y-axis (Number of Wallets in Millions)
        def millions_formatter(x, pos):
            return f'{x*1e-6:.1f}M'
        ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
        
        # Create a second y-axis for total stake
        ax2 = ax1.twinx()
        sns.lineplot(x=bin_stake_ada.index, y=bin_stake_ada.values, ax=ax2, color='crimson', marker='o')
        ax2.set_ylabel('Total Staked ADA (Billions)', fontsize=12, color='crimson')
        ax2.tick_params(axis='y', labelcolor='crimson')
        
        # Force the bottom of the second y-axis to be 0
        ax2.set_ylim(bottom=0)
        
        # Custom formatter for the right y-axis (Total Stake in Billions of ADA)
        def billions_formatter(x, pos):
            return f'{x / 1e9:.1f}B'
        ax2.yaxis.set_major_formatter(FuncFormatter(billions_formatter))
        
        # Add wallet count labels after plotting the line to ensure they are on top.
        ax1.bar_label(ax1.containers[0], fmt='{:,.0f}', padding=3, color='black', fontsize=10)

        # Manually create and place legend in the center
        blue_patch = mpatches.Patch(color='lightskyblue', label='Wallet Count')
        red_line = plt.Line2D([], [], color='crimson', marker='o', linestyle='-', label='Total Staked ADA')
        ax1.legend(handles=[blue_patch, red_line], loc='center')
        
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        plt.savefig('wallet_distribution_combined_corrected-pinned.png')
        print("Chart saved as wallet_distribution_combined_corrected.png")
        
        # --- Generate Pie Chart of Total Stake Distribution ---
        print("Generating pie chart for total stake distribution...")
        fig_pie, ax_pie = plt.subplots(figsize=(10, 10))
        
        # Explode the largest slice for emphasis (the '>1M' category)
        explode = [0] * len(labels)
        explode[-1] = 0.1  # Explode the last slice
        
        colors = sns.color_palette('pastel')[0:len(bin_stake_ada)]
        
        ax_pie.pie(
            bin_stake_ada,
            labels=bin_stake_ada.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            explode=explode
        )
        ax_pie.set_title('Proportion of Total Staked ADA by Wallet Size', fontsize=16, pad=20)
        ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.tight_layout()
        plt.savefig('stake_distribution_pie_chart.png')
        print("Chart saved as stake_distribution_pie_chart.png")

        # --- Continue with the percentile report ---
        df_sorted = df_analysis.sort_values(by='delegator_stake_ada', ascending=True).reset_index(drop=True)
        total_stake = df_sorted['delegator_stake_ada'].sum()
        df_sorted['cumulative_stake_percent'] = (df_sorted['delegator_stake_ada'].cumsum() / total_stake) * 100

        stake_10th_percentile = df_sorted.loc[df_sorted[df_sorted['cumulative_stake_percent'] >= 10].index.min(), 'delegator_stake_ada']
        stake_90th_percentile = df_sorted.loc[df_sorted[df_sorted['cumulative_stake_percent'] >= 90].index.min(), 'delegator_stake_ada']

        # --- Print the final report ---
        print("\n" + "="*80)
        print("                 Delegator Stake Distribution Analysis")
        print("="*80)

        report_data = {
            'Metric': [
                'Total Delegators',
                'Total Delegated Stake (ADA)',
                'Stake at 10th Percentile (ADA)',
                'Stake at 90th Percentile (ADA)',
                'Range of the middle 80% of stake'
            ],
            'Value': [
                f"{len(df_analysis):,}",
                f"{total_stake:,.0f}",
                f"{stake_10th_percentile:,.0f}",
                f"{stake_90th_percentile:,.0f}",
                f"{stake_10th_percentile:,.0f} to {stake_90th_percentile:,.0f}"
            ]
        }

        print(tabulate(
            pd.DataFrame(report_data),
            headers='keys',
            tablefmt='psql',
            stralign="left"
        ))
        print("="*80)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if engine is not None:
            engine.dispose()
            print("\nDatabase engine disposed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze delegator stake distribution.')
    args = parser.parse_args()

    analyze_stake_distribution()