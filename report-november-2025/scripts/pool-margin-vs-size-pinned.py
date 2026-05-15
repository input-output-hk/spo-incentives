import psycopg2
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
    # Assumes local connection with peer authentication
}

ABANDONED_LIST_FILE = "inactive-pools.txt"

# --- SQL Query ---
# This query gets the margin and total delegated stake for all active,
# non-abandoned pools in the latest epoch.
GET_POOL_DATA_QUERY = """
WITH latest_epoch AS (
    -- Pin: snapshot epoch fixed to 583 (report's analysis-window end)
    SELECT 583 AS no
),
active_pools AS (
    -- Get the latest update for all non-retired, non-abandoned pools
    SELECT
        pu.hash_id,
        pu.margin
    FROM
        pool_update pu
    INNER JOIN (
        -- Subquery to find the most recent update transaction for each pool hash,
        -- pinned to txs in epochs <= 586 (db-sync state at report time).
        SELECT
            pu2.hash_id,
            max(pu2.registered_tx_id) as max_tx_id
        FROM
            pool_update pu2
        JOIN tx t ON pu2.registered_tx_id = t.id
        JOIN block b ON t.block_id = b.id
        WHERE b.epoch_no <= 586
        GROUP BY
            pu2.hash_id
    ) AS latest ON latest.hash_id = pu.hash_id AND latest.max_tx_id = pu.registered_tx_id
    -- Join to get the bech32 pool ID for filtering
    JOIN
        pool_hash ph ON ph.id = pu.hash_id
    WHERE
        -- Ensure the pool is not retired (as of the analysis-window end)
        NOT EXISTS (
            SELECT 1
            FROM pool_retire pr
            WHERE pr.hash_id = pu.hash_id AND pr.retiring_epoch <= 583
        )
        -- Ensure the pool is NOT in our abandoned list
        AND ph.view NOT IN %s
),
pool_stake AS (
    -- Get the total delegated stake for each pool in the latest epoch
    SELECT
        pool_id,
        SUM(amount) as total_stake_lovelace
    FROM
        epoch_stake
    WHERE
        epoch_no = (SELECT no FROM latest_epoch)
    GROUP BY
        pool_id
)
-- Final query to join margins with stake
SELECT
    ap.margin,
    -- Use COALESCE to ensure pools with 0 stake are included
    COALESCE(ps.total_stake_lovelace, 0) as total_delegated_lovelace
FROM
    active_pools ap
LEFT JOIN
    pool_stake ps ON ps.pool_id = ap.hash_id;
"""

def get_abandoned_pools(filename):
    """Reads the abandoned list file (one pool ID per line) and returns a tuple."""
    if not os.path.exists(filename):
        print(f"Warning: '{filename}' not found. No pools will be excluded.")
        return tuple()
    
    with open(filename, 'r') as f:
        pool_ids = [line.strip() for line in f if line.strip()]
        return tuple(pool_ids)

def create_margin_scatter_plot(df):
    """Generates a scatter plot of pool margin vs. pool size with a broken x-axis."""
    print("\nGenerating margin scatter plot with broken axis...")

    # --- Data Preparation ---
    df['margin_percent'] = df['margin'] * 100
    df['total_delegated_ada'] = (df['total_delegated_lovelace'] / 1000000).astype(float)

    # Define the size buckets in millions of ADA
    bins = [0, 3, 10, 20, 30, 40, 50, 60, 70, np.inf]
    labels = ['0-3M', '3-10M', '10-20M', '20-30M', '30-40M', '40-50M', '50-60M', '60-70M', '>70M']
    df['size_bucket'] = pd.cut(df['total_delegated_ada'] / 1_000_000, bins=bins, labels=labels, right=False)
    
    # --- Plotting ---
    plt.style.use('seaborn-v0_8-darkgrid')
    # Create two subplots that share a y-axis
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(22, 12), gridspec_kw={'width_ratios': [2.5, 1]})
    fig.subplots_adjust(wspace=0.05)

    # Plot data on both axes
    for ax in [ax1, ax2]:
        sns.scatterplot(
            data=df,
            x='margin_percent',
            y='total_delegated_ada',
            hue='size_bucket',
            palette='viridis',
            alpha=0.7,
            s=60,
            ax=ax,
            legend= (ax==ax1) # Only add legend to the first plot
        )

    # Set the x-axis limits for each plot to create the "break"
    ax1.set_xlim(-0.5, 10.5)  # Main distribution
    ax2.set_xlim(80, 110) # High-margin outliers

    # --- Formatting ---
    # Hide the spines between the two plots
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.tick_params(axis='y', which='both', left=False) # remove y-ticks from the right plot

    # Add the diagonal "break" lines
    d = .015  # how big to make the diagonal lines in axes coordinates
    kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
    ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
    ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)
    
    # Set titles and labels
    fig.suptitle('Pool Size vs. Margin (Excluding inactive pools)', fontsize=22)
    ax1.set_ylabel('Total Delegated ADA (Pool Size)', fontsize=14)
    # Use a single, centered x-label
    fig.text(0.5, 0.04, 'Pool Margin (%)', ha='center', va='center', fontsize=14)
    ax1.set_xlabel('')
    ax2.set_xlabel('')

    # Format y-axis to show millions (M)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, pos: f'{y/1_000_000:.0f}M'))
    
    # Get handles and labels, reverse them, and then create the legend.
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles=handles[::-1], labels=labels[::-1], title='Pool Size (ADA)', loc='upper right', fontsize=12, title_fontsize=14)

    filename = "pool_margin_vs_size-pinned.png"
    plt.savefig(filename)
    print(f"Chart saved to '{filename}'")


def analyze_pool_margin_vs_size():
    """Main function to connect, query, and plot."""
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected.")

        print(f"Reading abandoned pools from '{ABANDONED_LIST_FILE}'...")
        abandoned_list = get_abandoned_pools(ABANDONED_LIST_FILE)
        
        if not abandoned_list:
            print("Abandoned pools list is empty. Cannot run query.")
            return

        print(f"Found {len(abandoned_list)} pools to exclude. Fetching pool data...")
        cur.execute(GET_POOL_DATA_QUERY, (abandoned_list,))
        
        results = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        cur.close()

        df_all_pools = pd.DataFrame(results, columns=headers)
        print(f"Found data for {len(df_all_pools)} active, non-abandoned pools.")
        
        create_margin_scatter_plot(df_all_pools)

    except (psycopg2.Error, FileNotFoundError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas matplotlib numpy seaborn
    analyze_pool_margin_vs_size()

