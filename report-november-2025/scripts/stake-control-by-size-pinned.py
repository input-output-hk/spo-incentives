import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import re
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
}
ANALYSIS_START_EPOCH = 257
# Pin: read the published Appendix A (1,305 Inactive pools) so the chart's
# "Excluding N Abandoned Pools" title matches the report.
ABANDONED_POOLS_SOURCE_FILE = '../appendixA.txt'
# Pin: hardcode the upper epoch bound to 583 (the report's analysis-window
# end) instead of querying dbsync's current MAX(epoch_no), which would extend
# the chart by 7+ months beyond the published version.
ANALYSIS_END_EPOCH = 583
# Use all available cores, or set a specific number like 10
NUM_CORES = 10

def get_abandoned_pools_from_file(filename):
    """
    Parses the provided text file to extract a list of pool IDs marked as 'Inactive'.
    """
    print(f"Parsing '{filename}' to find abandoned pools...")
    abandoned_pools = []
    pool_id_pattern = re.compile(r'(pool1[a-z0-9]{50,})')

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if 'Inactive' in line:
                    match = pool_id_pattern.search(line)
                    if match:
                        abandoned_pools.append(match.group(1))
        
        print(f"Found {len(abandoned_pools)} Inactive pools in '{filename}'.")
        return tuple(abandoned_pools)
        
    except FileNotFoundError:
        print(f"Error: The source file '{filename}' was not found.")
        return tuple()

# --- MODIFIED: Query is now a template for parallel execution ---
# It includes placeholders for a specific epoch range.
STAKE_CONTROL_QUERY_TEMPLATE = """
WITH pool_total_stake_per_epoch AS (
  SELECT
    es.epoch_no,
    es.pool_id,
    SUM(es.amount) AS total_stake_lovelace
  FROM epoch_stake es
  WHERE es.epoch_no BETWEEN %(start_epoch)s AND %(end_epoch)s
  GROUP BY es.epoch_no, es.pool_id
),
active_pools_per_epoch AS (
    SELECT
        ptspe.epoch_no,
        ptspe.total_stake_lovelace
    FROM pool_total_stake_per_epoch ptspe
    JOIN pool_hash ph ON ptspe.pool_id = ph.id
    WHERE ph.view NOT IN %(abandoned_pools)s
)
SELECT
  epoch_no,
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace < 3000000::numeric * 1000000) AS "< 3M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 3000000::numeric * 1000000 AND total_stake_lovelace < 10000000::numeric * 1000000) AS "3M - 10M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 10000000::numeric * 1000000 AND total_stake_lovelace < 20000000::numeric * 1000000) AS "10M - 20M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 20000000::numeric * 1000000 AND total_stake_lovelace < 30000000::numeric * 1000000) AS "20M - 30M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 30000000::numeric * 1000000 AND total_stake_lovelace < 40000000::numeric * 1000000) AS "30M - 40M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 40000000::numeric * 1000000 AND total_stake_lovelace < 50000000::numeric * 1000000) AS "40M - 50M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 50000000::numeric * 1000000 AND total_stake_lovelace < 60000000::numeric * 1000000) AS "50M - 60M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 60000000::numeric * 1000000 AND total_stake_lovelace < 70000000::numeric * 1000000) AS "60M - 70M ADA",
  SUM(total_stake_lovelace) FILTER (WHERE total_stake_lovelace >= 70000000::numeric * 1000000) AS "> 70M ADA"
FROM active_pools_per_epoch
GROUP BY epoch_no
ORDER BY epoch_no ASC;
"""

# --- NEW: Worker function to be run in parallel ---
def fetch_data_for_range(epoch_range, abandoned_pools_list):
    """Connects to DB and fetches data for a specific range of epochs."""
    start_epoch, end_epoch = epoch_range
    print(f"  [Worker] Fetching data for epochs {start_epoch}-{end_epoch}...")
    engine = None
    try:
        db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
        engine = create_engine(db_url)
        params = {
            'start_epoch': start_epoch,
            'end_epoch': end_epoch,
            'abandoned_pools': abandoned_pools_list
        }
        df = pd.read_sql_query(STAKE_CONTROL_QUERY_TEMPLATE, engine, params=params)
        return df
    except Exception as e:
        print(f"  [Worker] Error in range {start_epoch}-{end_epoch}: {e}")
        return pd.DataFrame() # Return empty dataframe on error
    finally:
        if engine:
            engine.dispose()

def plot_stake_control_chart_filtered():
    abandoned_pool_list = get_abandoned_pools_from_file(ABANDONED_POOLS_SOURCE_FILE)
    if not abandoned_pool_list:
        print("No abandoned pools found. Aborting.")
        return

    # --- NEW: Parallel Data Fetching Logic ---
    engine = None
    try:
        print("\nConnecting to database to get epoch range...")
        db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
        engine = create_engine(db_url)
        
        # 1. Get the total range of epochs to analyze.
        # Pin: use the hardcoded ANALYSIS_END_EPOCH instead of dbsync's current
        # MAX(epoch_no) so re-running reproduces the report's chart domain.
        max_epoch = ANALYSIS_END_EPOCH
        epoch_chunks = np.array_split(range(ANALYSIS_START_EPOCH, max_epoch + 1), NUM_CORES)
        epoch_ranges = [(int(chunk[0]), int(chunk[-1])) for chunk in epoch_chunks if len(chunk) > 0]

        print(f"Splitting analysis from epoch {ANALYSIS_START_EPOCH} to {max_epoch} into {len(epoch_ranges)} parallel jobs.")
        
        # 2. Use ProcessPoolExecutor to run queries concurrently
        all_dfs = []
        with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
            # Submit all jobs to the pool
            futures = [executor.submit(fetch_data_for_range, r, abandoned_pool_list) for r in epoch_ranges]
            
            # Collect results as they complete
            for future in as_completed(futures):
                result_df = future.result()
                if not result_df.empty:
                    all_dfs.append(result_df)
        
        if not all_dfs:
            print("No data was fetched from the database. Aborting.")
            return

        # 3. Combine results from all workers
        print("\nCombining results from all workers...")
        df_lovelace = pd.concat(all_dfs, ignore_index=True).sort_values(by='epoch_no').reset_index(drop=True)

        # --- Proceed with original DataFrame processing and plotting ---
        df_lovelace.set_index('epoch_no', inplace=True)
        df_lovelace.fillna(0, inplace=True)

        df_ada = df_lovelace / 1_000_000
        df_ada['total_active_stake'] = df_ada.sum(axis=1)

        print("Generating filtered stacked area plot...")
        fig, ax = plt.subplots(figsize=(14, 8))
        
        df_ada.drop(columns='total_active_stake').plot(
            kind='area', ax=ax, stacked=True, linewidth=0.5, cmap='Spectral'
        )
        df_ada['total_active_stake'].plot(
            ax=ax, color='black', linestyle='--', linewidth=2, label='Total Active Stake'
        )

        ax.set_title(f'Total Stake of Active Pools by Size (Excluding {len(abandoned_pool_list)} Abandoned Pools)', fontsize=16)
        ax.set_xlabel('Epoch Number', fontsize=12)
        ax.set_ylabel('Total Stake (in ADA)', fontsize=12)
        ax.legend(title='Pool Size Category (3M Threshold)', loc='lower left')

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x / 1_000_000_000:.1f}B'))
        
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_ylim(bottom=0)
        fig.tight_layout()

        output_filename = 'stake_control_by_size-pinned.png'
        plt.savefig(output_filename, dpi=300)
        print(f"\nSuccess! Filtered plot saved as '{output_filename}'")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if engine is not None:
            engine.dispose()
            print("\nDatabase engine disposed.")

if __name__ == '__main__':
    plot_stake_control_chart_filtered()