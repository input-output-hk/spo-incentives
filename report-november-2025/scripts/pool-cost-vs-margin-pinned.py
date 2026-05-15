import psycopg2
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
    # Assumes local connection with peer authentication
}

ABANDONED_LIST_FILE = "inactive-pools.txt"

# --- SQL Query ---
# This query gets the fixed cost and margin for all active, non-abandoned pools.
GET_POOL_FEES_QUERY = """
WITH active_pools AS (
    -- Get the latest update for all non-retired, non-abandoned pools
    SELECT
        pu.fixed_cost,
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
)
-- Final select
SELECT
    fixed_cost,
    margin
FROM
    active_pools;
"""

def get_abandoned_pools(filename):
    """Reads the abandoned list file (one pool ID per line) and returns a tuple."""
    if not os.path.exists(filename):
        print(f"Warning: '{filename}' not found. No pools will be excluded.")
        return tuple()
    
    with open(filename, 'r') as f:
        pool_ids = [line.strip() for line in f if line.strip()]
        return tuple(pool_ids)

def create_cost_vs_margin_plot(df):
    """Generates a filtered scatter plot to show the main data cluster."""
    print("\nGenerating filtered cost vs. margin scatter plot...")

    # --- Data Preparation ---
    df['margin_percent'] = df['margin'] * 100
    df['fixed_cost_ada'] = (df['fixed_cost'] / 1000000).astype(float)

    # Filter out outliers to focus the chart
    df_filtered = df[df['fixed_cost_ada'] <= 1000].copy()

    # --- Plotting ---
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(18, 12))

    # Plot the filtered data points
    ax.scatter(
        x=df_filtered['fixed_cost_ada'],
        y=df_filtered['margin_percent'],
        alpha=0.5,
        edgecolors='w',
        linewidth=0.5
    )

    # --- Formatting ---
    ax.set_title('Pool Margin vs. Fixed Cost (Excluding Inactive pools)', fontsize=22)
    ax.set_xlabel('Pool Fixed Cost (ADA)', fontsize=14)
    ax.set_ylabel('Pool Margin (%)', fontsize=14)
    
    # Set the x-axis limit to focus on the 0-1000 ADA range
    ax.set_xlim(0, 1000)

    plt.tight_layout()
    
    filename = "pool_cost_vs_margin-pinned.png"
    plt.savefig(filename)
    print(f"Chart saved to '{filename}'")


def analyze_cost_vs_margin():
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
        cur.execute(GET_POOL_FEES_QUERY, (abandoned_list,))
        
        results = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        cur.close()

        df_all_pools = pd.DataFrame(results, columns=headers)
        print(f"Found data for {len(df_all_pools)} active, non-abandoned pools.")
        
        create_cost_vs_margin_plot(df_all_pools)

    except (psycopg2.Error, FileNotFoundError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas matplotlib numpy
    analyze_cost_vs_margin()

