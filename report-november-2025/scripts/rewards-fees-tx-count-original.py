import psycopg2
import os
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
    # Assumes local connection with peer authentication
}

# --- SQL Query ---
# This query calculates total rewards from the 'reward' table and gets total fees
# and tx_count from the 'epoch' table for the last 73 completed epochs.
GET_REWARDS_FEES_QUERY = """
WITH latest_epoch AS (
    -- Find the latest epoch that has fully ended
    SELECT max(no) as max_no FROM epoch
    WHERE end_time <= NOW()
),
epoch_range AS (
    -- Define our epoch range for the last 73 epochs
    SELECT no FROM epoch
    WHERE no BETWEEN (SELECT max_no FROM latest_epoch) - 72 AND (SELECT max_no FROM latest_epoch)
),
epoch_rewards AS (
    -- Calculate the sum of all leader and member rewards for each epoch
    -- This is the slow part of the query
    SELECT
        earned_epoch,
        SUM(amount) as total_rewards_lovelace
    FROM
        reward
    WHERE
        type IN ('leader', 'member')
        AND earned_epoch IN (SELECT no FROM epoch_range)
    GROUP BY
        earned_epoch
)
-- Join with the epoch table to get the pre-aggregated fees and tx_count
SELECT
    e.no as epoch_no,
    er.total_rewards_lovelace,
    e.fees as total_fees_lovelace,
    e.tx_count
FROM
    epoch e
LEFT JOIN
    epoch_rewards er ON e.no = er.earned_epoch
WHERE
    e.no IN (SELECT no FROM epoch_range)
ORDER BY
    e.no ASC;
"""

def create_rewards_fees_chart(df, start_epoch, end_epoch, avg_rewards, avg_fees, avg_tx_count):
    """
    Generates and saves a stacked line chart of total rewards, fees, and tx count,
    including average lines.
    """
    print("\nGenerating rewards vs. fees vs. tx count chart...")

    # --- Plotting ---
    plt.style.use('seaborn-v0_8-darkgrid')
    # **CHANGE:** Create three subplots, stacked vertically, sharing the x-axis
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(18, 16), sharex=True)

    fig.suptitle(f'Total Rewards, Fees, and Transactions per Epoch (Epoch {start_epoch} - {end_epoch})', fontsize=22)

    # --- Axis 1 (Top): Total Rewards ---
    color1 = 'dodgerblue'
    ax1.set_ylabel('Total Rewards (ADA)', fontsize=14, color=color1)
    ax1.plot(df['epoch_no'], df['total_rewards_ada'], color=color1, linestyle='-', linewidth=2, label='Total Rewards (Member+Leader)')
    ax1.axhline(avg_rewards, color=color1, linestyle='--', label=f'Avg. Rewards: {avg_rewards:,.0f} ADA')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(bottom=0)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x/1_000_000:.1f}M'))
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.legend(loc='lower left')

    # --- Axis 2 (Middle): Total Fees ---
    color2 = 'forestgreen'
    ax2.set_ylabel('Total Fees (ADA)', fontsize=14, color=color2)
    ax2.plot(df['epoch_no'], df['total_fees_ada'], color=color2, linestyle='-', linewidth=2, label='Total Fees')
    ax2.axhline(avg_fees, color=color2, linestyle='--', label=f'Avg. Fees: {avg_fees:,.0f} ADA')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(bottom=0)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x:,.0f}'))
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax2.legend(loc='lower left')

    # --- Axis 3 (Bottom): Transaction Count ---
    color3 = 'purple'
    ax3.set_xlabel('Epoch Number', fontsize=14) # X-label only on the bottom plot
    ax3.set_ylabel('Transaction Count', fontsize=14, color=color3)
    ax3.plot(df['epoch_no'], df['tx_count'], color=color3, linestyle='-', linewidth=2, label='Transaction Count')
    ax3.axhline(avg_tx_count, color=color3, linestyle='--', label=f'Avg. Tx Count: {avg_tx_count:,.0f}')
    ax3.tick_params(axis='y', labelcolor=color3)
    ax3.set_ylim(bottom=0)
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x:,.0f}'))
    ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax3.legend(loc='lower left')


    # Remove horizontal space between plots
    plt.subplots_adjust(hspace=0.1)

    output_filename = f"rewards_fees_tx_count_last_73_epochs.png"
    plt.savefig(output_filename)
    print(f"Successfully saved chart to '{output_filename}'")


def analyze_rewards_vs_fees():
    """
    Fetches total rewards, fees, and tx count per epoch for the last 73 epochs,
    prints tables, and generates a stacked chart.
    """
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected.")

        print("Fetching rewards, fees, and tx count data for the last 73 completed epochs (this may take a moment)...")
        cur.execute(GET_REWARDS_FEES_QUERY)

        results = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        cur.close()

        if not results:
            print("No data found for the specified epoch range.")
            return

        df = pd.DataFrame(results, columns=headers)
        print(f"Found data for {len(df)} epochs.")

        # --- Data Preparation ---
        print("Processing data...")
        df['total_rewards_lovelace'] = pd.to_numeric(df['total_rewards_lovelace']).fillna(0)
        df['total_fees_lovelace'] = pd.to_numeric(df['total_fees_lovelace']).fillna(0)
        df['tx_count'] = pd.to_numeric(df['tx_count']).fillna(0)

        df['total_rewards_ada'] = df['total_rewards_lovelace'] / 1_000_000
        df['total_fees_ada'] = df['total_fees_lovelace'] / 1_000_000

        # Calculate averages for the whole period
        avg_rewards = df['total_rewards_ada'].mean()
        avg_fees = df['total_fees_ada'].mean()
        avg_tx_count = df['tx_count'].mean()

        # Get the actual epoch range for titling
        start_epoch = df['epoch_no'].min()
        end_epoch = df['epoch_no'].max()

        # --- Output CSV ---
        output_filename = f"rewards_fees_tx_count_epoch_{start_epoch}-{end_epoch}.csv"
        df.to_csv(output_filename, index=False)
        print(f"\nSuccessfully saved data to '{output_filename}'")

        # --- Console Table ---
        print(f"\n--- Total Rewards, Fees, & Tx Count per Epoch ({start_epoch}-{end_epoch}) ---")
        df_display = df.copy()
        df_display['total_rewards_ada'] = df_display['total_rewards_ada'].map('{:,.2f}'.format)
        df_display['total_fees_ada'] = df_display['total_fees_ada'].map('{:,.2f}'.format)
        df_display['tx_count'] = df_display['tx_count'].map('{:,.0f}'.format)
        print(tabulate(df_display[['epoch_no', 'total_rewards_ada', 'total_fees_ada', 'tx_count']], headers=['Epoch', 'Total Rewards (ADA)', 'Total Fees (ADA)', 'Tx Count'], tablefmt='psql', showindex=False))

        # --- Summary Table ---
        print(f"\n--- Overall Averages ({start_epoch}-{end_epoch}) ---")
        summary_data = {
            "Metric": ["Average Total Rewards per Epoch", "Average Total Fees per Epoch", "Average Tx Count per Epoch"],
            "Value": [f"{avg_rewards:,.2f} ADA", f"{avg_fees:,.2f} ADA", f"{avg_tx_count:,.0f}"]
        }
        summary_df = pd.DataFrame(summary_data)
        print(tabulate(summary_df, headers='keys', tablefmt='psql', showindex=False))

        # --- Chart Generation ---
        create_rewards_fees_chart(df, start_epoch, end_epoch, avg_rewards, avg_fees, avg_tx_count)

    except (psycopg2.Error, TypeError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas tabulate matplotlib
    analyze_rewards_vs_fees()

