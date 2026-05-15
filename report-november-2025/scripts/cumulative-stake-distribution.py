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

K_PARAMETER = 500
EPOCH_NUMBER = 583 # Set the specific epoch for analysis
MAX_SUPPLY_ADA = 45_000_000_000

# --- SQL Queries ---
# **OPTIMIZED QUERY:** This version is much faster. It starts from epoch_stake
# for the target epoch and then filters out any pools that were retired.
GET_POOL_STAKE_QUERY = """
SELECT
    SUM(es.amount) as total_delegated_lovelace
FROM
    epoch_stake es
WHERE
    es.epoch_no = %s
    AND NOT EXISTS (
        SELECT 1
        FROM pool_retire pr
        WHERE pr.hash_id = es.pool_id AND pr.retiring_epoch <= %s
    )
GROUP BY
    es.pool_id;
"""

# Query to get both reserves and treasury for the epoch
GET_ADA_POTS_QUERY = "SELECT reserves, treasury FROM ada_pots WHERE epoch_no = %s;"

def create_cumulative_stake_chart(df, epoch_no, total_stake_ada, active_stake_ada, total_stake_minus_treasury_ada):
    """Generates a chart of the cumulative stake distribution for a specific epoch."""
    print(f"\nGenerating cumulative stake distribution chart for epoch {epoch_no}...")

    # --- Data Preparation ---
    df['total_delegated_ada'] = (df['total_delegated_lovelace'] / 1000000).astype(float)
    
    # Sort by stake, descending
    df_sorted = df.sort_values(by='total_delegated_ada', ascending=False).reset_index(drop=True)
    
    # Calculate cumulative stake
    df_sorted['cumulative_stake'] = df_sorted['total_delegated_ada'].cumsum()
    
    # --- Correctly Prepare "Ideal" Line based on Circulating Supply ---
    # The ideal line represents k pools reaching saturation based on total stake (circulating supply)
    ideal_stake_curve = np.linspace(0, total_stake_ada, K_PARAMETER + 1)
    
    # --- Plotting ---
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(18, 12))

    # Add horizontal lines for context using spec terminology
    ax.axhline(y=MAX_SUPPLY_ADA, color='navy', linestyle=':', linewidth=2.5, label='Max Supply')
    ax.axhline(y=total_stake_ada, color='green', linestyle='-.', linewidth=2, label='Total Stake (Circulating Supply)')
    ax.axhline(y=total_stake_minus_treasury_ada, color='cyan', linestyle='-.', linewidth=2, label='Total Stake - Treasury')
    ax.axhline(y=active_stake_ada, color='orange', linestyle='--', linewidth=2, label='Total Active Stake')

    # Plot Actual Distribution
    ax.plot(df_sorted.index + 1, df_sorted['cumulative_stake'], label='Actual Active Stake Distribution', color='royalblue', linewidth=3)
    
    # Plot Ideal Distribution
    ax.plot(range(K_PARAMETER + 1), ideal_stake_curve, label=f'Ideal Distribution (Saturation at k={K_PARAMETER})', color='red', linestyle='--', linewidth=2)

    # Shade the area but stop at the k=500 line.
    ideal_line_for_shading = (total_stake_ada / K_PARAMETER) * (df_sorted.index + 1)
    ax.fill_between(
        df_sorted.index + 1, 
        df_sorted['cumulative_stake'], 
        ideal_line_for_shading, 
        # The condition now stops the shading at the K_PARAMETER line.
        where=((ideal_line_for_shading > df_sorted['cumulative_stake']) & (df_sorted.index + 1 <= K_PARAMETER)),
        interpolate=True, color='skyblue', alpha=0.5, label='Untapped Saturation Capacity'
    )

    # Add vertical line for k parameter
    ax.axvline(x=K_PARAMETER, color='gray', linestyle=':', linewidth=2.5, label=f'k = {K_PARAMETER}')

    # --- Formatting ---
    ax.set_title(f'Cumulative Stake Distribution vs. Ideal Saturation (All Active Pools, Epoch {epoch_no})', fontsize=22)
    ax.set_xlabel('Pool Count (Sorted by Stake)', fontsize=14)
    ax.set_ylabel('Cumulative Stake (ADA)', fontsize=14)
    # Move legend to the lower right corner
    ax.legend(fontsize=12, loc='lower right')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, pos: f'{y/1_000_000_000:.2f}B'))

    ax.set_xlim(0, len(df_sorted) + 1)
    # Set the y-axis limit to the max supply for an accurate scale
    ax.set_ylim(0, MAX_SUPPLY_ADA * 1.05)
    
    # **FIX:** Manually add the 45B tick and remove any ticks greater than it.
    yticks = list(ax.get_yticks())
    if MAX_SUPPLY_ADA not in yticks:
        yticks.append(MAX_SUPPLY_ADA)
    # Remove any ticks that are above the max supply
    yticks = [tick for tick in yticks if tick <= MAX_SUPPLY_ADA]
    ax.set_yticks(sorted(yticks))


    plt.tight_layout()
    
    filename = f"cumulative_stake_distribution_epoch_{epoch_no}_annotated.png"
    plt.savefig(filename)
    print(f"Chart saved to '{filename}'")


def analyze_stake_distribution():
    """Main function to connect, query, and plot."""
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected.")

        print(f"Fetching ADA pot values for epoch {EPOCH_NUMBER}...")
        cur.execute(GET_ADA_POTS_QUERY, (EPOCH_NUMBER,))
        reserves_lovelace, treasury_lovelace = cur.fetchone()
        
        # Convert Decimal types to float for calculations
        reserves_lovelace = float(reserves_lovelace)
        treasury_lovelace = float(treasury_lovelace)
        
        total_stake_ada = (MAX_SUPPLY_ADA * 1_000_000 - reserves_lovelace) / 1_000_000
        total_stake_minus_treasury_ada = total_stake_ada - (treasury_lovelace / 1_000_000)
        
        print(f"Calculated Total Stake (Circulating Supply): {total_stake_ada:,.0f} ADA")
        print(f"Calculated Total Stake - Treasury: {total_stake_minus_treasury_ada:,.0f} ADA")

        print(f"Fetching all active pool data for epoch {EPOCH_NUMBER}...")
        cur.execute(GET_POOL_STAKE_QUERY, (EPOCH_NUMBER, EPOCH_NUMBER))
        
        results = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        cur.close()

        df_all_pools = pd.DataFrame(results, columns=headers)
        active_stake_ada = (df_all_pools['total_delegated_lovelace'].sum()) / 1_000_000
        print(f"Found data for {len(df_all_pools)} active pools in epoch {EPOCH_NUMBER}.")
        print(f"Total Active Stake: {active_stake_ada:,.0f} ADA")
        
        # --- Chart Generation ---
        create_cumulative_stake_chart(df_all_pools, EPOCH_NUMBER, total_stake_ada, active_stake_ada, total_stake_minus_treasury_ada)

    except (psycopg2.Error, TypeError) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    # Make sure you have the required libraries installed:
    # pip install psycopg2-binary pandas matplotlib numpy
    analyze_stake_distribution()

