import pandas as pd
import psycopg2
import sqlalchemy
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np # Ensure numpy is imported
import concurrent.futures
import os
import time

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
    # No password needed if using peer authentication
}

START_EPOCH = 208
END_EPOCH = 584
MIN_POOL_COUNT = 5 # Filter for MPOs with > 5 pools

# Use all available logical cores (16 on your system)
N_CORES = os.cpu_count() or 16

# --- SQL Queries ---
# (Unchanged)
STAKE_HISTORY_QUERY = f"""
SELECT
    es.epoch_no,
    es.pool_id,
    SUM(es.amount) as total_stake_lovelace
FROM epoch_stake es
WHERE es.epoch_no BETWEEN {START_EPOCH} AND {END_EPOCH}
GROUP BY es.epoch_no, es.pool_id;
"""

METADATA_QUERY = f"""
WITH all_pools_in_range AS (
    SELECT DISTINCT pool_id FROM epoch_stake WHERE epoch_no BETWEEN {START_EPOCH} AND {END_EPOCH}
),
latest_pool_update AS (
    SELECT DISTINCT ON (pu.hash_id)
        pu.hash_id as pool_id,
        pu.meta_id,
        pu.reward_addr_id,
        pu.id as update_id
    FROM pool_update pu
    WHERE pu.hash_id IN (SELECT pool_id FROM all_pools_in_range)
    ORDER BY pu.hash_id, pu.id DESC
),
pool_tickers AS (
    SELECT
        lpu.pool_id,
        opd.ticker_name as ticker
    FROM latest_pool_update lpu
    LEFT JOIN off_chain_pool_data opd ON lpu.meta_id = opd.pmr_id
),
pool_domains AS (
    SELECT DISTINCT ON (lpu.pool_id)
        lpu.pool_id,
        pr.dns_name as dns
    FROM latest_pool_update lpu
    JOIN pool_relay pr ON lpu.update_id = pr.update_id
    WHERE pr.dns_name IS NOT NULL
    ORDER BY lpu.pool_id, pr.id DESC
)
SELECT
    ap.pool_id,
    ph.view as pool_bech32,
    lpu.reward_addr_id,
    pt.ticker,
    pd.dns
FROM all_pools_in_range ap
JOIN pool_hash ph ON ap.pool_id = ph.id
LEFT JOIN latest_pool_update lpu ON ap.pool_id = lpu.pool_id
LEFT JOIN pool_tickers pt ON ap.pool_id = pt.pool_id
LEFT JOIN pool_domains pd ON ap.pool_id = pd.pool_id;
"""

SUPPLY_HISTORY_QUERY = f"""
SELECT
    epoch_no,
    (45000000000000000 - reserves) as circulating_supply_lovelace
FROM ada_pots
WHERE epoch_no BETWEEN {START_EPOCH} AND {END_EPOCH}
ORDER BY epoch_no;
"""

TOTAL_DELEGATED_QUERY = f"""
SELECT
    epoch_no,
    SUM(amount) as total_delegated_lovelace
FROM epoch_stake
WHERE epoch_no BETWEEN {START_EPOCH} AND {END_EPOCH}
GROUP BY epoch_no;
"""


# --- Parallel Helper Functions (TOP LEVEL) ---
# (Unchanged)
def _apply_chunk_wrapper(args):
    chunk, apply_func = args
    return chunk.apply(apply_func, axis=1)

def _merge_chunk_wrapper(args):
    df_left_chunk, df_right, on, how = args
    return pd.merge(df_left_chunk, df_right, on=on, how=how)

def parallel_apply(df, func, n_cores=N_CORES):
    if df.empty:
        return pd.Series(dtype=df.dtypes.iloc[0] if len(df.dtypes) > 0 else 'object')
    print(f"Applying function in parallel across {n_cores} cores...")
    chunk_size = int(np.ceil(len(df) / n_cores))
    df_split = [df[i*chunk_size:(i+1)*chunk_size] for i in range(n_cores)]
    tasks = [(chunk, func) for chunk in df_split if not chunk.empty]
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cores) as executor:
        results = executor.map(_apply_chunk_wrapper, tasks)
    return pd.concat(results)

def parallel_merge(df_left, df_right, on, how, n_cores=N_CORES):
    print(f"Merging DataFrames in parallel across {n_cores} cores...")
    chunk_size = int(np.ceil(len(df_left) / n_cores))
    df_left_split = [df_left[i*chunk_size:(i+1)*chunk_size] for i in range(n_cores)]
    tasks = [(chunk, df_right, on, how) for chunk in df_left_split if not chunk.empty]
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cores) as executor:
        results = executor.map(_merge_chunk_wrapper, tasks)
    return pd.concat(results)

# --- Core Logic Functions ---
# (Unchanged)
GENERIC_DOMAINS = {
    'cloud.com', 'amazonaws.com', 'digitalocean.com', 'vultr.com',
    'cloud.google.com', 'azure.com', 'ovh.com', 'linode.com', 'hetzner.com',
    'googleusercontent.com'
}

def get_base_domain(dns):
    if pd.isna(dns): return None
    dns = str(dns).lower().strip()
    parts = dns.split('.')
    domain = None
    if len(parts) > 2:
        if parts[-2] in ('co', 'com', 'org', 'net', 'gov', 'edu') and len(parts) > 2:
            domain = '.'.join(parts[-3:])
        else: domain = '.'.join(parts[-2:])
    elif len(parts) == 2: domain = dns
    if domain and domain not in GENERIC_DOMAINS: return domain
    return None

def get_base_ticker(ticker):
    if pd.isna(ticker): return None
    ticker = str(ticker).upper().strip()
    match = re.match(r'^([A-Z]{3,6})([\d\w]{1,2})$', ticker)
    if match: return match.group(1)
    if 3 <= len(ticker) <= 6: return ticker
    return None

def group_pools(metadata_df):
    print("Discovering MPOs using hierarchical method (v19)...")
    print("Pre-processing heuristics...")
    metadata_df['base_domain'] = metadata_df['dns'].apply(get_base_domain)
    metadata_df['base_ticker'] = metadata_df['ticker'].apply(get_base_ticker)
    metadata_df['group'] = None
    assigned_pool_ids = set()

    print(f"Pass 1: Discovering MPOs by Reward Address (>{MIN_POOL_COUNT} pools)...")
    reward_groups = metadata_df.groupby('reward_addr_id')['pool_id'].unique()
    reward_addr_map = {}
    pools_in_reward_groups = set()
    for reward_addr_id, pool_ids in reward_groups.items():
        if pd.isna(reward_addr_id): continue
        if len(pool_ids) > MIN_POOL_COUNT:
            group_label = None
            pools_in_group_df = metadata_df[metadata_df['pool_id'].isin(pool_ids)]
            first_ticker = pools_in_group_df['base_ticker'].dropna().iloc[0] if not pools_in_group_df['base_ticker'].dropna().empty else None
            if first_ticker: group_label = f"{first_ticker}_Group"
            else:
                first_dns = pools_in_group_df['base_domain'].dropna().iloc[0] if not pools_in_group_df['base_domain'].dropna().empty else None
                if first_dns: group_label = f"{first_dns}_Group"
                else: group_label = f"RewardGroup_{int(reward_addr_id)}"
            reward_addr_map[reward_addr_id] = group_label
            pools_in_reward_groups.update(pool_ids)
    metadata_df['group'] = metadata_df['reward_addr_id'].map(reward_addr_map)
    assigned_pool_ids.update(pools_in_reward_groups)
    print(f"  Assigned {len(pools_in_reward_groups)} pools to {len(reward_addr_map)} reward address groups.")

    print(f"Pass 2: Discovering MPOs by DNS (>{MIN_POOL_COUNT} pools)...")
    remaining_pools_df = metadata_df[~metadata_df['pool_id'].isin(assigned_pool_ids)]
    dns_groups = remaining_pools_df.groupby('base_domain')['pool_id'].unique()
    dns_map = {}
    pools_in_dns_groups = set()
    for base_domain, pool_ids in dns_groups.items():
         if pd.isna(base_domain): continue
         if len(pool_ids) > MIN_POOL_COUNT:
             group_label = f"{base_domain}"
             dns_map[base_domain] = group_label
             pools_in_dns_groups.update(pool_ids)
    mask_pass2 = metadata_df['group'].isna() & metadata_df['base_domain'].isin(dns_map)
    metadata_df.loc[mask_pass2, 'group'] = metadata_df.loc[mask_pass2, 'base_domain'].map(dns_map)
    assigned_pool_ids.update(pools_in_dns_groups)
    print(f"  Assigned {len(pools_in_dns_groups)} pools to {len(dns_map)} DNS groups.")

    print(f"Pass 3: Discovering MPOs by Ticker (>{MIN_POOL_COUNT} pools)...")
    remaining_pools_df = metadata_df[~metadata_df['pool_id'].isin(assigned_pool_ids)]
    ticker_groups = remaining_pools_df.groupby('base_ticker')['pool_id'].unique()
    ticker_map = {}
    pools_in_ticker_groups = set()
    for base_ticker, pool_ids in ticker_groups.items():
        if pd.isna(base_ticker): continue
        if len(pool_ids) > MIN_POOL_COUNT:
            group_label = f"{base_ticker}"
            ticker_map[base_ticker] = group_label
            pools_in_ticker_groups.update(pool_ids)
    mask_pass3 = metadata_df['group'].isna() & metadata_df['base_ticker'].isin(ticker_map)
    metadata_df.loc[mask_pass3, 'group'] = metadata_df.loc[mask_pass3, 'base_ticker'].map(ticker_map)
    assigned_pool_ids.update(pools_in_ticker_groups)
    print(f"  Assigned {len(pools_in_ticker_groups)} pools to {len(ticker_map)} Ticker groups.")

    print("Pass 4: Cleaning up...")
    metadata_df['group'] = metadata_df['group'].fillna('single_pools')
    num_mpos = len(metadata_df[metadata_df['group'] != 'single_pools']['group'].unique())
    print(f"Discovery complete. Identified {num_mpos} MPO groups with > {MIN_POOL_COUNT} pools.")
    return metadata_df

def fetch_data(engine, query, name):
    # (Unchanged)
    print(f"Starting fetch: {name}...")
    start_time = time.time()
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sqlalchemy.text(query), conn)
        end_time = time.time()
        print(f"Finished fetch: {name} ({len(df)} rows) in {end_time - start_time:.2f} seconds.")
        return df
    except Exception as e:
        print(f"Error fetching {name} data: {e}")
        return pd.DataFrame()

def plot_evolution_data(pivot_df, title, ylabel, filename):
    """
    Generates and saves a stacked area chart for stake evolution.
    *** MODIFIED to explicitly convert data to NumPy float array. ***
    """
    print(f"Generating plot: {title}...")

    # Sort columns by mean value (descending) for better stacking order
    sorted_columns = pivot_df.mean().sort_values(ascending=False).index
    pivot_df = pivot_df[sorted_columns]

    labels = pivot_df.columns
    num_groups = len(labels)

    # Get colors
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i % 20) for i in range(num_groups)]

    plt.figure(figsize=(20, 12))
    ax = plt.gca()

    # *** NEW: Explicitly convert data to a NumPy float array ***
    try:
        # Get the index (epochs) and the values
        x = pivot_df.index
        # Transpose values so shape is (num_groups, num_epochs)
        y = pivot_df.values.T 
        # Ensure the data is float type
        y = y.astype(np.float64) 

        # Check for non-finite values one last time (debugging)
        if not np.all(np.isfinite(y)):
            print(f"WARNING: Non-finite values detected in data for {filename} even after conversion!")
            # Option: Replace non-finite with 0 directly in numpy array
            y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)

        plt.stackplot(x, y, labels=labels, colors=colors, alpha=0.8)

    except Exception as e:
        print(f"ERROR during stackplot for {filename}: {e}")
        # Print some debug info about the data
        print("Data shape:", y.shape if 'y' in locals() else 'N/A')
        print("Data dtype:", y.dtype if 'y' in locals() else 'N/A')
        # You might add more checks here if needed
        plt.close() # Close the potentially broken plot figure
        raise # Re-raise the exception to stop the script

    # --- Formatting (unchanged) ---
    if "Percentage" in ylabel:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    else:
        ax.get_yaxis().set_major_formatter(
            mticker.FuncFormatter(lambda x, p: f'{x/1_000_000:.0f}M'))

    plt.title(title, fontsize=18)
    plt.xlabel("Epoch Number", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(x.min(), x.max()) # Use x variable defined above
    plt.ylim(0)

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=6,
               fancybox=True, shadow=True, title="Groups")
    plt.subplots_adjust(bottom=0.25)

    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Plot saved to {filename}")
    plt.close()

# --- Main Execution ---
def main():
    engine = None
    try:
        print(f"Using {N_CORES} cores for parallel operations.")
        db_url = f"postgresql+psycopg2://{DB_CONFIG['user']}@/{DB_CONFIG['dbname']}"
        engine = sqlalchemy.create_engine(db_url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_stake = executor.submit(fetch_data, engine, STAKE_HISTORY_QUERY, "stake history")
            future_meta = executor.submit(fetch_data, engine, METADATA_QUERY, "pool metadata")
            future_supply = executor.submit(fetch_data, engine, SUPPLY_HISTORY_QUERY, "circulating supply (45B-R)")
            future_delegated = executor.submit(fetch_data, engine, TOTAL_DELEGATED_QUERY, "total delegated stake")
            stake_df = future_stake.result()
            metadata_df = future_meta.result()
            supply_df = future_supply.result()
            delegated_df = future_delegated.result()

        if stake_df.empty or metadata_df.empty or supply_df.empty or delegated_df.empty:
            print("One or more data queries returned empty. Exiting.")
            return

        metadata_with_groups_df = group_pools(metadata_df)
        group_mapping_df = metadata_with_groups_df[['pool_id', 'group']]

        print("Merging datasets...")
        main_df = parallel_merge(stake_df, group_mapping_df, on='pool_id', how='left', n_cores=N_CORES)
        print("Merging with supply data...")
        main_df = pd.merge(main_df, supply_df, on='epoch_no', how='left')
        print("Merging with total delegated stake data...")
        main_df = pd.merge(main_df, delegated_df, on='epoch_no', how='left')
        main_df['group'] = main_df['group'].fillna('single_pools')
        main_df = main_df.dropna(subset=['circulating_supply_lovelace', 'total_delegated_lovelace'])

        print("Aggregating data by epoch and group...")
        agg_df = main_df.groupby(['epoch_no', 'group', 'circulating_supply_lovelace', 'total_delegated_lovelace']).agg(
            total_stake_lovelace=('total_stake_lovelace', 'sum'),
            pool_count=('pool_id', 'nunique')
        ).reset_index()

        agg_df['total_stake_ada'] = agg_df['total_stake_lovelace'] / 1_000_000
        agg_df['percentage_circulating'] = (agg_df['total_stake_lovelace'] / agg_df['circulating_supply_lovelace']) * 100
        agg_df['percentage_delegated'] = (agg_df['total_stake_lovelace'] / agg_df['total_delegated_lovelace']) * 100

        agg_df.to_csv('mpo_evolution_report.csv', index=False, float_format='%.6f')
        print("Full aggregated report saved to mpo_evolution_report.csv")

        print("Preparing data for plotting...")
        def categorize_group(group_name):
            if group_name == 'single_pools': return None
            return group_name
        agg_df['plot_group'] = agg_df['group'].apply(categorize_group)
        plot_agg_df = agg_df[agg_df['plot_group'].notna()].copy()
        plot_agg_df = plot_agg_df.groupby(['epoch_no', 'plot_group']).agg(
            percentage_circulating=('percentage_circulating', 'sum'),
            percentage_delegated=('percentage_delegated', 'sum')
        ).reset_index()

        # --- Chart 1: Percentage of Circulating Supply ---
        pivot_circ_df = plot_agg_df.pivot(
            index='epoch_no',
            columns='plot_group',
            values='percentage_circulating'
        )
        # *** FIX IS HERE ***
        pivot_circ_df = pivot_circ_df.replace([np.inf, -np.inf], np.nan).fillna(0).astype(float) # Ensure float

        plot_evolution_data(
            pivot_circ_df,
            f"MPO Stake as % of Circulating Supply (Discovered MPOs with > {MIN_POOL_COUNT} pools)",
            f"Percentage of Circulating Supply",
            "mpo_evolution_pct_circulating.png"
        )

        # --- Chart 2: Percentage of Total Delegated Stake ---
        pivot_del_df = plot_agg_df.pivot(
            index='epoch_no',
            columns='plot_group',
            values='percentage_delegated'
        )
        # *** FIX IS HERE ***
        pivot_del_df = pivot_del_df.replace([np.inf, -np.inf], np.nan).fillna(0).astype(float) # Ensure float

        plot_evolution_data(
            pivot_del_df,
            f"MPO Stake as % of Total Delegated Stake (Discovered MPOs with > {MIN_POOL_COUNT} pools)",
            f"Percentage of Total Delegated Stake (Market Share)",
            "mpo_evolution_pct_delegated.png"
        )

        print(f"\nAnalysis complete. Generated two new charts for ALL discovered MPOs with > {MIN_POOL_COUNT} pools.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"An error occurred: {error}")
    finally:
        if engine is not None:
            engine.dispose()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()