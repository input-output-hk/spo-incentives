import pandas as pd
from sqlalchemy import create_engine
from tabulate import tabulate
import numpy as np
import os

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"  # Replace with your local username if different
}
ABANDONED_POOLS_FILE = 'abandoned-only.txt'
EPOCH_START = 548
EPOCH_END = 583
OUTPUT_DIR = 'results' # Directory to save CSV files

# --- Stake Brackets Definition ---
BINS = [0, 3e6, 10e6, 20e6, 30e6, 40e6, 50e6, 60e6, 70e6, np.inf]
LABELS = [
    '< 3M', '3M - 10M', '10M - 20M', '20M - 30M',
    '30M - 40M', '40M - 50M', '50M - 60M', '60M - 70M', '> 70M'
]


def get_pool_data_query(epoch):
    """Generates the SQL query for a specific epoch."""
    return f"""
    WITH pool_total_stake AS (
        SELECT pool_id, SUM(amount) as total_stake_lovelace
        FROM epoch_stake WHERE epoch_no = {epoch} GROUP BY pool_id
    ),
    latest_pool_update AS (
        SELECT DISTINCT ON (pu.hash_id) pu.hash_id, pu.margin, pu.fixed_cost
        FROM pool_update pu WHERE pu.active_epoch_no <= {epoch}
        ORDER BY pu.hash_id, pu.active_epoch_no DESC
    ),
    epoch_blocks AS (
        SELECT sl.pool_hash_id, COUNT(b.id) AS block_count
        FROM block b JOIN slot_leader sl ON b.slot_leader_id = sl.id
        WHERE b.epoch_no = {epoch} GROUP BY sl.pool_hash_id
    ),
    epoch_leader_rewards AS (
        SELECT r.pool_id, r.amount AS total_reward_lovelace
        FROM reward r WHERE r.earned_epoch = {epoch} AND r.type = 'leader'
    ),
    epoch_member_rewards AS (
        SELECT r.pool_id, SUM(r.amount) AS member_rewards_lovelace
        FROM reward r WHERE r.earned_epoch = {epoch} AND r.type = 'member'
        GROUP BY r.pool_id
    )
    SELECT
        ph.view AS pool_id,
        pts.total_stake_lovelace / 1000000 AS total_stake_ada,
        COALESCE(eb.block_count, 0) AS block_count,
        COALESCE(
            CASE
                WHEN elr.total_reward_lovelace < lpu.fixed_cost THEN elr.total_reward_lovelace / 1000000
                ELSE (lpu.fixed_cost / 1000000) + (lpu.margin * (elr.total_reward_lovelace - lpu.fixed_cost) / 1000000)
            END, 0
        ) AS operator_rewards_ada,
        COALESCE(emr.member_rewards_lovelace / 1000000, 0) AS member_rewards_ada
    FROM
        pool_total_stake pts
    JOIN pool_hash ph ON pts.pool_id = ph.id
    LEFT JOIN latest_pool_update lpu ON ph.id = lpu.hash_id
    LEFT JOIN epoch_blocks eb ON ph.id = eb.pool_hash_id -- <<< THIS IS THE CORRECTED LINE
    LEFT JOIN epoch_leader_rewards elr ON ph.id = elr.pool_id
    LEFT JOIN epoch_member_rewards emr ON ph.id = emr.pool_id;
    """


def load_abandoned_pools(filepath):
    """Loads the list of abandoned pool IDs from a text file."""
    try:
        with open(filepath, 'r') as f:
            abandoned_ids = {line.strip() for line in f if line.strip()}
        print(f"Successfully loaded {len(abandoned_ids)} abandoned pool IDs.")
        return abandoned_ids
    except FileNotFoundError:
        print(f"Warning: The file '{filepath}' was not found. The 'Abandoned Pools' summary row will not be generated.")
        return set()


def generate_summary_table(dataframe, abandoned_ids):
    """
    Calculates aggregated statistics, separating abandoned pools from stake tiers.
    """
    dataframe['stake_range'] = pd.Categorical(dataframe['stake_range'], categories=LABELS, ordered=True)

    # --- Create separate dataframes for active and abandoned pools ---
    df_active = dataframe[~dataframe['pool_id'].isin(abandoned_ids)]
    df_abandoned = dataframe[dataframe['pool_id'].isin(abandoned_ids)]

    # --- 1. Aggregation for ACTIVE pools by stake range ---
    summary_active = df_active.groupby('stake_range', observed=False).agg(
        pool_count=('pool_id', 'size'),
        pools_with_blocks=('block_count', lambda x: (x > 0).sum()),
        controlled_stake_ada=('total_stake_ada', 'sum'),
        blocks_produced=('block_count', 'sum'),
        operator_rewards_ada=('operator_rewards_ada', 'sum'),
        member_rewards_ada=('member_rewards_ada', 'sum')
    ).reset_index()

    # --- 2. Create the summary row for all ABANDONED pools ---
    abandoned_df_row = pd.DataFrame()
    if not df_abandoned.empty:
        abandoned_summary = {
            'stake_range': 'Inactive',
            'pool_count': len(df_abandoned),
            'pools_with_blocks': (df_abandoned['block_count'] > 0).sum(),
            'controlled_stake_ada': df_abandoned['total_stake_ada'].sum(),
            'blocks_produced': df_abandoned['block_count'].sum(),
            'operator_rewards_ada': df_abandoned['operator_rewards_ada'].sum(),
            'member_rewards_ada': df_abandoned['member_rewards_ada'].sum()
        }
        abandoned_df_row = pd.DataFrame([abandoned_summary])

    # --- 3. Create the TOTALS row from the original, complete dataframe ---
    total_row_data = {
        'stake_range': '--- TOTALS ---',
        'pool_count': len(dataframe),
        'pools_with_blocks': (dataframe['block_count'] > 0).sum(),
        'controlled_stake_ada': dataframe['total_stake_ada'].sum(),
        'blocks_produced': dataframe['block_count'].sum(),
        'operator_rewards_ada': dataframe['operator_rewards_ada'].sum(),
        'member_rewards_ada': dataframe['member_rewards_ada'].sum()
    }
    total_row = pd.DataFrame([total_row_data])
    
    # --- Combine all parts in the correct order ---
    final_summary = pd.concat([abandoned_df_row, summary_active, total_row], ignore_index=True)

    # --- Calculate derived columns on the complete, assembled table ---
    final_summary['pool_rewards_ada'] = final_summary['operator_rewards_ada'] + final_summary['member_rewards_ada']
    
    # Use the pre-calculated totals for percentage calculations
    total_stake = total_row_data['controlled_stake_ada']
    total_blocks = total_row_data['blocks_produced']
    total_pool_rewards = total_row_data['operator_rewards_ada'] + total_row_data['member_rewards_ada']
    
    final_summary['% of Total Stake'] = (final_summary['controlled_stake_ada'] / total_stake * 100) if total_stake > 0 else 0
    final_summary['% of Blocks'] = (final_summary['blocks_produced'] / total_blocks * 100) if total_blocks > 0 else 0
    final_summary['% of Pool Rewards'] = (final_summary['pool_rewards_ada'] / total_pool_rewards * 100) if total_pool_rewards > 0 else 0
    
    return final_summary


def process_and_output_table(summary_df, title, csv_filename):
    """Formats, prints, and saves the consolidated summary table."""
    summary_df_display = summary_df.copy()

    for col in ['% of Total Stake', '% of Blocks', '% of Pool Rewards']:
        summary_df_display[col] = summary_df_display[col].apply(lambda x: f"{x:.2f}%")
        
    for col in ['controlled_stake_ada', 'operator_rewards_ada', 'member_rewards_ada', 'pool_rewards_ada']:
        summary_df_display[col] = summary_df_display[col].apply(lambda x: f"{x:,.2f}")

    summary_df_display = summary_df_display[[
        'stake_range', 'pool_count', 'pools_with_blocks',
        'controlled_stake_ada', '% of Total Stake', 'blocks_produced', '% of Blocks',
        'operator_rewards_ada', 'member_rewards_ada', 'pool_rewards_ada', '% of Pool Rewards'
    ]]

    summary_df_display.columns = [
        'Stake Range (ADA)', 'Pool Count', 'Pools w/ Blocks',
        'Controlled Stake (ADA)', '% of Total Stake', 'Blocks Produced', '% of Blocks',
        'Operator Rewards (ADA)', 'Member Rewards (ADA)', 'Total Pool Rewards (ADA)', '% of Pool Rewards'
    ]

    print("\n" + "=" * 180)
    print(title.center(180))
    print("=" * 180)
    print(tabulate(summary_df_display, headers='keys', tablefmt='psql', showindex=False))
    print("=" * 180)

    try:
        summary_df.to_csv(csv_filename, index=False, float_format='%.2f')
        print(f"✅ Table successfully saved to: {csv_filename}")
    except Exception as e:
        print(f"❌ Error saving file to {csv_filename}: {e}")


def main():
    """Main function to run the analysis and generate outputs."""
    engine = None
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"CSV output will be saved to the '{OUTPUT_DIR}/' directory.")
        
        print("Connecting to the database...")
        db_url = f"postgresql:///{DB_CONFIG['dbname']}?user={DB_CONFIG['user']}"
        engine = create_engine(db_url)

        abandoned_pool_ids = load_abandoned_pools(ABANDONED_POOLS_FILE)

        for epoch in range(EPOCH_START, EPOCH_END + 1):
            print(f"\n\n--- Processing data for Epoch {epoch} ---")
            query = get_pool_data_query(epoch)
            df = pd.read_sql_query(query, engine)

            df['block_count'] = df['block_count'].fillna(0).astype(int)
            df['operator_rewards_ada'] = df['operator_rewards_ada'].fillna(0)
            df['member_rewards_ada'] = df['member_rewards_ada'].fillna(0)
            df['stake_range'] = pd.cut(df['total_stake_ada'], bins=BINS, labels=LABELS, right=False)

            summary_table = generate_summary_table(df, abandoned_pool_ids)

            csv_path = os.path.join(OUTPUT_DIR, f"epoch_{epoch}_summary.csv")
            title = f"Consolidated Pool Snapshot - Epoch {epoch}"
            process_and_output_table(summary_table, title, csv_path)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if engine is not None:
            engine.dispose()
            print("\nDatabase connection closed.")


if __name__ == '__main__':
    main()