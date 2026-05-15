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

def plot_reg_vs_retire_chart_linear_broken_fixed():
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
        print("Merging datasets...")
        start_epoch = min(df_regs['epoch_no'].min(), df_rets['epoch_no'].min())
        end_epoch = max(df_regs['epoch_no'].max(), df_rets['epoch_no'].max())
        df = pd.DataFrame({'epoch_no': range(start_epoch, end_epoch + 1)})

        df = pd.merge(df, df_regs, on='epoch_no', how='left')
        df = pd.merge(df, df_rets, on='epoch_no', how='left')

        df.fillna(0, inplace=True)
        df.set_index('epoch_no', inplace=True)
        
        # 3. Setup and create the plot
        print("Generating plot...")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(14, 8),
                                     gridspec_kw={'height_ratios': [1, 3]})
        fig.subplots_adjust(hspace=0.05)

        # Plot the same data on both axes using more descriptive labels
        ax1.plot(df.index, df['retired_count'], color='red', marker='x', markersize=3, label='Retired Pools')
        ax2.plot(df.index, df['retired_count'], color='red', marker='x', markersize=3)
        ax1.plot(df.index, df['registered_count'], color='green', marker='o', markersize=2, label='Newly Registered Pools')
        ax2.plot(df.index, df['registered_count'], color='green', marker='o', markersize=2)


        # Set y-axis limits and ticks
        ax1.set_ylim(650, 900)
        ax2.set_ylim(0, 125)
        ax2.yaxis.set_major_locator(mticker.MultipleLocator(25))

        # Hide the spines between ax1 and ax2
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.xaxis.tick_top()
        ax1.tick_params(labeltop=False)
        ax2.xaxis.tick_bottom()

        # Add the diagonal lines to indicate the break
        d = .015
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
        
        # 4. Format the plot for clarity
        ax1.set_title('New Pool Registrations vs. Retirements per Epoch', fontsize=16)
        ax2.set_xlabel('Epoch Number', fontsize=12)
        fig.text(0.06, 0.5, 'Number of Pools', va='center', rotation='vertical', fontsize=12)

        # --- PRIMARY FIX: Moved legend to the more detailed bottom plot ---
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, labels)
        
        ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
        ax2.grid(True, which='both', linestyle=':', linewidth=0.5)

        # 5. Save the final chart
        output_filename = 'pool_registrations_vs_retirements_linear_broken_fixed.png'
        plt.savefig(output_filename, dpi=300) # 300 dpi is standard for high quality
        print(f"\nSuccess! Plot saved as '{output_filename}'")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if engine is not None:
            engine.dispose()
            print("Database engine disposed.")

if __name__ == '__main__':
    plot_reg_vs_retire_chart_linear_broken_fixed()