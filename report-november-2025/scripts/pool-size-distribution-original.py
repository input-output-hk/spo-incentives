import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sqlalchemy import create_engine, text
import re
import multiprocessing

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
}
ANALYSIS_START_EPOCH = 257
ABANDONED_POOLS_SOURCE_FILE = 'appendixA.txt'
NUM_CORES = 10
TEMP_TABLE_NAME = 'temp_inactive_pools'

# --- Global variable for worker processes ---
global_db_url = None

def init_worker(db_url):
    """Initializes the database URL for each worker in the pool."""
    global global_db_url
    global_db_url = db_url

def get_abandoned_pools_from_file(filename):
    """
    Parses the comprehensive report file to extract a list of all pool IDs
    that have the status "Inactive".
    """
    print(f"Parsing '{filename}' to find 'Inactive' pools to exclude...")
    abandoned_pools = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if 'Inactive' in line and line.strip().startswith('|'):
                    columns = [col.strip() for col in line.split('|')]
                    if len(columns) > 5 and columns[5] == 'Inactive':
                        pool_id = columns[3]
                        if pool_id.startswith('pool1'):
                            abandoned_pools.append(pool_id)
        
        unique_pools = list(set(abandoned_pools))
        print(f"Found {len(unique_pools)} unique 'Inactive' pools in '{filename}'.")
        return unique_pools
        
    except FileNotFoundError:
        print(f"Error: The source file '{filename}' was not found.")
        return []

def process_epoch(epoch_no):
    """
    Connects to the DB and processes a single epoch, filtering via a LEFT JOIN.
    """
    engine = None
    # --- SQL QUERY MODIFIED for a single epoch ---
    # The final line "FROM active_pools_this_epoch" has been added to fix the error.
    SINGLE_EPOCH_QUERY = f"""
    WITH pool_total_stake_per_epoch AS (
      SELECT pool_id, SUM(amount) AS total_stake
      FROM epoch_stake
      WHERE epoch_no = {epoch_no}
      GROUP BY pool_id
    ),
    active_pools_this_epoch AS (
        SELECT ptspe.total_stake
        FROM pool_total_stake_per_epoch ptspe
        JOIN pool_hash ph ON ptspe.pool_id = ph.id
        LEFT JOIN pool_retire pr ON ptspe.pool_id = pr.hash_id AND {epoch_no} >= pr.retiring_epoch
        LEFT JOIN {TEMP_TABLE_NAME} ap ON ph.view = ap.pool_id
        WHERE 
            pr.hash_id IS NULL
            AND ap.pool_id IS NULL
    )
    SELECT
      {epoch_no} AS epoch_no,
      COUNT(*) FILTER (WHERE total_stake < 3000000::numeric * 1000000) AS "< 3M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 3000000::numeric * 1000000 AND total_stake < 10000000::numeric * 1000000) AS "3M - 10M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 10000000::numeric * 1000000 AND total_stake < 20000000::numeric * 1000000) AS "10M - 20M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 20000000::numeric * 1000000 AND total_stake < 30000000::numeric * 1000000) AS "20M - 30M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 30000000::numeric * 1000000 AND total_stake < 40000000::numeric * 1000000) AS "30M - 40M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 40000000::numeric * 1000000 AND total_stake < 50000000::numeric * 1000000) AS "40M - 50M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 50000000::numeric * 1000000 AND total_stake < 60000000::numeric * 1000000) AS "50M - 60M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 60000000::numeric * 1000000 AND total_stake < 70000000::numeric * 1000000) AS "60M - 70M ADA",
      COUNT(*) FILTER (WHERE total_stake >= 70000000::numeric * 1000000) AS "> 70M ADA"
    FROM active_pools_this_epoch; -- <<< THIS LINE WAS MISSING
    """
    try:
        engine = create_engine(global_db_url)
        result_df = pd.read_sql_query(text(SINGLE_EPOCH_QUERY), engine)
        return result_df.to_dict('records')[0]
    except Exception as e:
        print(f"Error processing epoch {epoch_no}: {e}")
        return None
    finally:
        if engine:
            engine.dispose()

def plot_pool_size_distribution():
    engine = None
    db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
    
    try:
        abandoned_pool_list = get_abandoned_pools_from_file(ABANDONED_POOLS_SOURCE_FILE)
        
        if not abandoned_pool_list:
            print("No abandoned pools to filter. Aborting.")
            return

        engine = create_engine(db_url)
        
        print(f"\nUploading {len(abandoned_pool_list)} inactive pool IDs to a temporary table...")
        df_abandoned = pd.DataFrame(abandoned_pool_list, columns=['pool_id'])
        with engine.connect() as conn:
             df_abandoned.to_sql(TEMP_TABLE_NAME, conn, if_exists='replace', index=False)
        print("Upload complete.")

        print("Connecting to DB to find the latest epoch...")
        latest_epoch = pd.read_sql_query("SELECT MAX(no) FROM epoch;", engine).iloc[0,0]
        
        epochs_to_process = list(range(ANALYSIS_START_EPOCH, latest_epoch + 1))
        print(f"Preparing to process {len(epochs_to_process)} epochs (from {ANALYSIS_START_EPOCH} to {latest_epoch}) using {NUM_CORES} cores.")

        with multiprocessing.Pool(processes=NUM_CORES, initializer=init_worker, initargs=(db_url,)) as pool:
            results = pool.map(process_epoch, epochs_to_process)

        results = [r for r in results if r is not None]
        if not results:
            print("No data was processed. Aborting plot generation.")
            return
            
        print(f"\nAll epochs processed. Combining {len(results)} results.")
        df = pd.DataFrame(results)
        df.set_index('epoch_no', inplace=True)
        df.sort_index(inplace=True)

        print("Generating plot...")
        fig, ax = plt.subplots(figsize=(14, 8))

        tab10_colors = plt.get_cmap('tab10').colors
        color_map = {
            "< 3M ADA": tab10_colors[0],
            "3M - 10M ADA": tab10_colors[1],
            "10M - 20M ADA": tab10_colors[2],
            "20M - 30M ADA": tab10_colors[3],
            "30M - 40M ADA": tab10_colors[4],
            "40M - 50M ADA": tab10_colors[5],
            "50M - 60M ADA": tab10_colors[6],
            "60M - 70M ADA": tab10_colors[7],
            "> 70M ADA": tab10_colors[9]
        }
        
        for column in df.columns:
            df[column].plot(ax=ax, color=color_map.get(column), label=column, marker='o', linestyle='-', markersize=3, linewidth=1.5)

        ax.set_title(f'Cardano Stake Pool Size Distribution (Excluding {len(abandoned_pool_list)} Inactive Pools)', fontsize=16)
        ax.set_xlabel('Epoch Number', fontsize=12)
        ax.set_ylabel('Number of Pools', fontsize=12)
        
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        
        ax.legend(title='Pool Size Category', loc='upper left')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        fig.tight_layout()
        output_filename = 'pool_size_distribution_abandoned_filtered_full.png'
        plt.savefig(output_filename, dpi=300)
        print(f"\nSuccess! Plot saved as '{output_filename}'")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if engine is not None:
            try:
                with engine.connect() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS {TEMP_TABLE_NAME};"))
                    conn.commit()
                print(f"Temporary table '{TEMP_TABLE_NAME}' dropped.")
            except Exception as e:
                print(f"Error dropping temporary table: {e}")
            finally:
                engine.dispose()
                print("Database engine disposed.")

if __name__ == '__main__':
    plot_pool_size_distribution()