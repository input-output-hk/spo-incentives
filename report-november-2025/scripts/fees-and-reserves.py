import psycopg2
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
    # Assumes local connection with peer authentication
}

START_EPOCH = 208
END_EPOCH = 583
RHO = 0.003 # The fixed percentage by which reserves decrease each epoch

# --- SQL Query ---
# This query accurately calculates total rewards paid by summing the reward table,
# and also fetches fees and reserves for the specified epoch range.
GET_EPOCH_DATA_QUERY = """
WITH epoch_rewards AS (
    -- Calculate the sum of all leader and member rewards for each epoch
    SELECT
        earned_epoch,
        SUM(amount) as total_rewards_paid
    FROM
        reward
    WHERE
        type IN ('leader', 'member')
        AND earned_epoch BETWEEN %(start_epoch)s AND %(end_epoch)s
    GROUP BY
        earned_epoch
)
SELECT
    e.no as epoch_no,
    e.fees,
    er.total_rewards_paid,
    ap.reserves
FROM
    epoch e
JOIN
    ada_pots ap ON e.no = ap.epoch_no
JOIN
    epoch_rewards er ON e.no = er.earned_epoch
ORDER BY
    e.no ASC;
"""

def analyze_sustainability_trends():
    """
    Fetches historical data and projects reserve depletion, plotting the results.
    """
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected.")

        print(f"Fetching sustainability data from epoch {START_EPOCH} to {END_EPOCH}...")
        cur.execute(GET_EPOCH_DATA_QUERY, {'start_epoch': START_EPOCH, 'end_epoch': END_EPOCH})
        
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
        df['fees_ada'] = pd.to_numeric(df['fees']) / 1_000_000
        df['total_rewards_paid_ada'] = pd.to_numeric(df['total_rewards_paid']) / 1_000_000
        df['reserves_ada'] = pd.to_numeric(df['reserves']) / 1_000_000
        df['rewards_from_reserves_ada'] = df['total_rewards_paid_ada'] - df['fees_ada']
        
        # --- Projection Calculation ---
        print("Projecting reserve depletion...")
        last_epoch = df['epoch_no'].iloc[-1]
        last_reserves = df['reserves_ada'].iloc[-1]
        
        projection_epochs = [last_epoch]
        projected_reserves = [last_reserves]
        
        current_reserves = last_reserves
        current_epoch = last_epoch
        
        # Project until reserves are effectively zero
        while current_reserves > 1_000_000: # Stop when < 1M ADA
            current_reserves *= (1 - RHO)
            current_epoch += 1
            projection_epochs.append(current_epoch)
            projected_reserves.append(current_reserves)
            
        depletion_epoch = current_epoch
        print(f"Estimated reserve depletion epoch: {depletion_epoch}")

        # --- Plotting ---
        print("Generating chart...")
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 15), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.suptitle(f'Cardano Network Economic Sustainability & Reserve Depletion Projection', fontsize=22)
        
        # --- Top Plot: Stacked Area Chart for Reward Composition ---
        ax1.stackplot(
            df['epoch_no'], df['fees_ada'], df['rewards_from_reserves_ada'],
            labels=['Transaction Fees', 'Monetary Expansion (from Reserves)'],
            colors=['dodgerblue', 'darkorange'], alpha=0.8
        )
        ax1.set_ylabel('Total Rewards Paid per Epoch (ADA)', fontsize=14)
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x/1_000_000:.1f}M'))
        ax1.grid(True)
        ax1.legend(loc='upper left')
        
        # --- Bottom Plot: Reserves Line Chart with Projection ---
        ax2.plot(df['epoch_no'], df['reserves_ada'], color='forestgreen', label='Historical Reserves', linewidth=2.5)
        ax2.plot(projection_epochs, projected_reserves, color='red', linestyle='--', label='Projected Depletion (rho=0.3%)')
        
        # Add annotation for depletion point
        ax2.axvline(x=depletion_epoch, color='crimson', linestyle=':', linewidth=2, label=f'Est. Depletion Epoch: {depletion_epoch}')
        
        ax2.set_xlabel('Epoch Number', fontsize=14)
        ax2.set_ylabel('Total Reserves (ADA)', fontsize=14)
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, pos: f'{y/1_000_000_000:.2f}B'))
        ax2.grid(True)
        ax2.legend(loc='upper right')

        plt.subplots_adjust(hspace=0.05)
        output_filename = f"sustainability_trends_with_projection_{START_EPOCH}-{END_EPOCH}.png"
        plt.savefig(output_filename)
        print(f"Successfully saved chart to '{output_filename}'")

    except (psycopg2.Error, TypeError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas matplotlib
    analyze_sustainability_trends()

