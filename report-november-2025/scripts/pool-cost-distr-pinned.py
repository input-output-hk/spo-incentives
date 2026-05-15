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
# This query gets the fixed cost and total delegated stake for all active,
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
        pu.fixed_cost
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
-- Final query to join costs with stake
SELECT
    ap.fixed_cost,
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
        # Read each line, strip whitespace, and filter out any empty lines
        pool_ids = [line.strip() for line in f if line.strip()]
        return tuple(pool_ids)

def create_grouped_bar_chart(df):
    """Generates a grouped bar chart of common fixed costs by pool size with data labels."""
    print("\nGenerating grouped bar chart...")

    # --- Data Preparation ---
    df['fixed_cost_ada'] = (df['fixed_cost'] / 1000000).astype(float)
    df['total_delegated_ada'] = (df['total_delegated_lovelace'] / 1000000).astype(float)

    # Define the size buckets in millions of ADA to match the example chart
    bins = [0, 1, 5, 10, 20, 30, 40, 50, 60, 70, np.inf]
    labels = ['< 1M', '1M - 5M', '5M - 10M', '10M - 20M', '20M - 30M', '30M - 40M', '40M - 50M', '50M - 60M', '60M - 70M', '> 70M']
    
    # **FIX:** The logic for bucketing was incorrect. This version scales the data correctly.
    # We compare the 'total_delegated_ada' (which is in absolute ADA) against bins
    # that are also scaled up to absolute ADA values.
    bins_in_ada = [b * 1_000_000 for b in bins]
    df['size_bucket'] = pd.cut(df['total_delegated_ada'], bins=bins_in_ada, labels=labels, right=False)


    # Identify common costs and group the rest
    common_costs = [170.0, 340.0, 345.0, 500.0, 1000.0]
    df['cost_category'] = df['fixed_cost_ada'].apply(lambda x: str(x) if x in common_costs else 'Other')

    # Create a pivot table for plotting
    pivot_df = df.groupby(['size_bucket', 'cost_category'], observed=False).size().unstack(fill_value=0)
    
    common_costs_str = [str(c) for c in common_costs]
    for cost in common_costs_str:
        if cost not in pivot_df.columns:
            pivot_df[cost] = 0
    if 'Other' not in pivot_df.columns:
        pivot_df['Other'] = 0

    # Order the columns logically
    plot_order = common_costs_str + ['Other']
    pivot_df = pivot_df[[col for col in plot_order if col in pivot_df.columns]]

    # --- Plotting ---
    plt.style.use('seaborn-v0_8-darkgrid')
    ax = pivot_df.plot(kind='bar', figsize=(20, 12), width=0.8)

    # --- Add Data Labels (Annotations) ---
    for container in ax.containers:
        ax.bar_label(container, label_type='edge', fontsize=9, padding=3)

    # --- Formatting ---
    ax.set_title('Distribution of Common Fixed Costs by Pool Size (Excluding Inactive pools)', fontsize=20)
    ax.set_xlabel('Pool Size (M ADA)', fontsize=14)
    ax.set_ylabel('Number of Pools', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    ax.legend(title='Fixed Cost (ADA)', loc='upper right', fontsize='12', title_fontsize='14')

    # Adjust y-axis limit to make space for labels on top of the bars
    ax.set_ylim(0, ax.get_ylim()[1] * 1.1)

    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make room for legend
    
    filename = "pool-cost-distr-pinned.png"
    plt.savefig(filename)
    print(f"Chart saved to '{filename}'")


def analyze_pool_costs_by_size():
    """Main function to connect, query, and plot."""
    conn = None
    try:
        # --- Database Connection and Query ---
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
        
        # --- Chart Generation ---
        create_grouped_bar_chart(df_all_pools)

    except (psycopg2.Error, FileNotFoundError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas matplotlib numpy
    analyze_pool_costs_by_size()

