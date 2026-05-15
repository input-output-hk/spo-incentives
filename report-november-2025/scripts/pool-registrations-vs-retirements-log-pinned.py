import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sqlalchemy import create_engine

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
}

# --- Query 1: To Count First-Time Pool Registrations per Epoch ---
FIRST_REGISTRATION_QUERY = """
WITH first_registrations AS (
  -- First, find the absolute first registration epoch for each unique pool ID.
  SELECT
    MIN(active_epoch_no) as epoch_no
  FROM pool_update
  GROUP BY hash_id
)
-- Now, count how many pools had their first registration in each epoch.
SELECT
  epoch_no,
  COUNT(*) AS registered_count
FROM first_registrations
GROUP BY epoch_no
ORDER BY epoch_no ASC;
"""

# --- Query 2: To Count Pool Retirements per Epoch ---
RETIREMENT_QUERY = """
SELECT
  retiring_epoch AS epoch_no,
  COUNT(*) AS retired_count
FROM pool_retire
GROUP BY retiring_epoch
ORDER BY epoch_no ASC;
"""

def plot_reg_vs_retire_chart_log_scale():
    engine = None
    try:
        print("Creating SQLAlchemy engine...")
        db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
        engine = create_engine(db_url)

        # 1. Execute both queries to get the two datasets
        print("Executing query for first-time registrations...")
        df_regs = pd.read_sql_query(FIRST_REGISTRATION_QUERY, engine)

        print("Executing query for retirements...")
        df_rets = pd.read_sql_query(RETIREMENT_QUERY, engine)
        
        # 2. Merge the datasets into a single DataFrame
        # Pin: cap the upper epoch at 585 (db-sync's MAX(block.epoch_no) at
        # report time) so re-running today doesn't extend the chart with
        # post-report epochs.
        ANALYSIS_END_EPOCH = 585
        print("Merging datasets...")
        start_epoch = min(df_regs['epoch_no'].min(), df_rets['epoch_no'].min())
        end_epoch = min(max(df_regs['epoch_no'].max(), df_rets['epoch_no'].max()), ANALYSIS_END_EPOCH)
        df = pd.DataFrame({'epoch_no': range(start_epoch, end_epoch + 1)})

        df = pd.merge(df, df_regs, on='epoch_no', how='left')
        df = pd.merge(df, df_rets, on='epoch_no', how='left')

        df.fillna(0, inplace=True)
        df.set_index('epoch_no', inplace=True)
        
        # 3. Setup and create the plot (single log-scale subplot)
        print("Generating log-scale plot...")

        fig, ax = plt.subplots(figsize=(14, 7))

        ax.plot(df.index, df['registered_count'], color='green', marker='o', markersize=2, label='Newly Registered Pools')
        ax.plot(df.index, df['retired_count'], color='red', marker='x', markersize=3, label='Retired Pools')

        # 4. Format the plot for clarity
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(mticker.ScalarFormatter())  # 1, 10, 100, 1000 instead of 10^N
        ax.set_title('New Pool Registrations vs. Retirements per Epoch (Log Scale)', fontsize=16)
        ax.set_xlabel('Epoch Number', fontsize=12)
        ax.set_ylabel('Number of Pools (Log Scale)', fontsize=12)
        ax.legend()
        ax.grid(True, which='both', linestyle=':', linewidth=0.5)

        # 5. Save the final chart
        output_filename = 'pool_registrations_vs_retirements_log-pinned.png'
        plt.savefig(output_filename, dpi=300)
        print(f"\nSuccess! Plot saved as '{output_filename}'")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if engine is not None:
            engine.dispose()
            print("Database engine disposed.")

if __name__ == '__main__':
    plot_reg_vs_retire_chart_log_scale()