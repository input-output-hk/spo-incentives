import pandas as pd
import psycopg2
from tabulate import tabulate
from datetime import timedelta
from decimal import Decimal

# --- Configuration ---
DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos"
}
OUTPUT_FILENAME = "appendixA-pinned.txt" # File to save the report to

# --- Pin anchors for reproducibility ---
# REPORT_DATE: the date the report's appendices were committed (2025-10-20).
# Used to make the "No Update in >1 Year" (NU) signal time-independent.
REPORT_DATE = pd.Timestamp("2025-10-20", tz="UTC")
# DBSYNC_MAX_EPOCH_AT_REPORT: the dbsync epoch_no max at report time.
# Used to freeze `latest_pool_data` so pools that re-registered after the
# report do not resolve to different owners/pledge/last_update values.
DBSYNC_MAX_EPOCH_AT_REPORT = 586

# --- MODIFIED: Analysis Parameters for Specific Epoch Range ---
# The script now runs for a fixed epoch range instead of a dynamic window.
START_EPOCH = 548
END_EPOCH = 583
EPOCH_WINDOW = END_EPOCH - START_EPOCH + 1  # This is now calculated, equals 36 epochs

REWARD_THRESHOLD_ADA = 5500
STAKE_THRESHOLD_ADA = 3_000_000 # Viability threshold for stake
INACTIVE_FLAG_THRESHOLD = 2
# Thresholds for the improved 'Inactive' classification
EXPECTED_BLOCKS_UNDERPERFORMER_THRESHOLD = 1.0
EXPECTED_BLOCKS_NEGLIGIBLE_THRESHOLD = 0.1

# Protocol parameters for block expectation calculation
SLOTS_PER_EPOCH = 432000
ACTIVE_SLOT_COEFF = 0.05

# --- MODIFIED: SQL Query for Specific Epoch Range ---
# The query has been updated to use specific start and end epochs passed as parameters,
# removing the need to calculate them from the latest epoch in the database.
ALL_POOLS_PERFORMANCE_QUERY = """
WITH epoch_range AS (
    SELECT generate_series(%(start_epoch)s, %(end_epoch)s) AS epoch_no
),
active_pools AS (
    -- Pin: original had no registration-epoch filter, so pools that registered
    -- after the report run slip in as "active" and land in the Inactive tier.
    -- Upper bound 585 matches db-sync's MAX(block.epoch_no) at report time
    -- (derived from the P2P block-count math). Pools whose first pool_update
    -- was in epoch 586+ would not have been in db-sync's pool_hash at report
    -- time, so we exclude them here for parity.
    SELECT ph.id, ph.view
    FROM pool_hash ph
    LEFT JOIN pool_retire pr ON ph.id = pr.hash_id AND pr.retiring_epoch <= (SELECT MAX(epoch_no) FROM epoch_range)
    WHERE pr.hash_id IS NULL
      AND EXISTS (
        SELECT 1 FROM pool_update pu
        JOIN tx t ON pu.registered_tx_id = t.id
        JOIN block b ON t.block_id = b.id
        WHERE pu.hash_id = ph.id AND b.epoch_no <= 585
      )
),
rewards_in_window AS (
    -- Pin: original used `earned_epoch >= MIN(epoch_range)` with no upper
    -- bound, which silently accumulates rewards beyond epoch 583 once db-sync
    -- indexes new epochs. Upper bound set to 584 (not 583) because at report
    -- time db-sync had rewards earned through epoch 584 (distributed at the
    -- start of epoch 586). Using 584 matches what the original `>=` bug
    -- effectively returned at report time.
    SELECT pool_id, SUM(amount) as total_operator_rewards
    FROM reward
    WHERE type = 'leader'
      AND earned_epoch BETWEEN (SELECT MIN(epoch_no) FROM epoch_range) AND 584
    GROUP BY pool_id
),
stake_latest_epoch AS (
    SELECT pool_id, SUM(amount) AS total_stake_lovelace
    FROM epoch_stake
    WHERE epoch_no = (SELECT MAX(epoch_no) FROM epoch_range)
    GROUP BY pool_id
),
total_active_stake AS (
    SELECT SUM(amount) as total_stake
    FROM epoch_stake
    WHERE epoch_no = (SELECT MAX(epoch_no) FROM epoch_range)
),
blocks_in_window AS (
    SELECT sl.pool_hash_id as pool_id, COUNT(b.id) as block_count
    FROM block b
    JOIN slot_leader sl ON b.slot_leader_id = sl.id
    WHERE b.epoch_no BETWEEN (SELECT MIN(epoch_no) FROM epoch_range) AND (SELECT MAX(epoch_no) FROM epoch_range)
    GROUP BY sl.pool_hash_id
),
latest_pool_data AS (
    -- Pin: freeze pool_update snapshot to txs in epochs <= 586 (db-sync state
    -- at report time). Without this, pools that re-registered after the report
    -- resolve to different owners/pledge/ticker/last_update_timestamp.
    SELECT DISTINCT ON (pu.hash_id)
        pu.id as update_id,
        pu.hash_id as pool_id,
        pu.pledge,
        pu.reward_addr_id,
        b.time as last_update_timestamp,
        (SELECT ticker_name FROM off_chain_pool_data ocpd WHERE ocpd.pool_id = pu.hash_id ORDER BY pmr_id DESC LIMIT 1) as ticker_name
    FROM pool_update pu
    JOIN tx t ON pu.registered_tx_id = t.id
    JOIN block b ON t.block_id = b.id
    WHERE pu.hash_id IN (SELECT id FROM active_pools)
      AND b.epoch_no <= 586
    ORDER BY pu.hash_id, pu.registered_tx_id DESC
),
owner_total_stake AS (
    SELECT
        lpd.pool_id,
        SUM(COALESCE(es.amount, 0)) as total_owner_stake
    FROM latest_pool_data lpd
    JOIN pool_owner po ON po.pool_update_id = lpd.update_id
    LEFT JOIN epoch_stake es ON po.addr_id = es.addr_id AND es.epoch_no = (SELECT MAX(epoch_no) FROM epoch_range)
    GROUP BY lpd.pool_id
),
spo_voting_activity AS (
    -- Pin: same `>=` bug as rewards_in_window. Upper bound 584 matches what
    -- the original `>=` bug effectively captured at report time (rewards
    -- distributed by epoch 584 / votes by then in db-sync).
    SELECT DISTINCT vp.pool_voter as pool_id
    FROM voting_procedure vp
    JOIN tx t ON vp.tx_id = t.id
    JOIN block b ON t.block_id = b.id
    WHERE vp.voter_role = 'SPO'
      AND b.epoch_no BETWEEN (SELECT MIN(epoch_no) FROM epoch_range) AND 584
),
reward_addr_delegation AS (
    SELECT DISTINCT lpd.pool_id
    FROM latest_pool_data lpd
    WHERE EXISTS (SELECT 1 FROM delegation_vote dv WHERE dv.addr_id = lpd.reward_addr_id)
),
governance_participation AS (
    SELECT pool_id FROM spo_voting_activity
    UNION
    SELECT pool_id FROM reward_addr_delegation
)
-- Final SELECT to join all pre-aggregated data for ALL active pools
SELECT
    ap.view as pool_bech32_id,
    lpd.ticker_name,
    lpd.pledge,
    COALESCE(ots.total_owner_stake, 0) as total_owner_stake,
    COALESCE(sle.total_stake_lovelace, 0) as total_stake_lovelace,
    COALESCE(biw.block_count, 0) as total_blocks_in_window,
    lpd.last_update_timestamp,
    (CASE WHEN gp.pool_id IS NOT NULL THEN TRUE ELSE FALSE END) as is_participating_in_gov,
    COALESCE(riw.total_operator_rewards, 0) as total_operator_rewards,
    (SELECT total_stake FROM total_active_stake) as total_network_stake
FROM active_pools ap
LEFT JOIN latest_pool_data lpd ON ap.id = lpd.pool_id
LEFT JOIN rewards_in_window riw ON ap.id = riw.pool_id
LEFT JOIN stake_latest_epoch sle ON ap.id = sle.pool_id
LEFT JOIN blocks_in_window biw ON ap.id = biw.pool_id
LEFT JOIN governance_participation gp ON ap.id = gp.pool_id
LEFT JOIN owner_total_stake ots ON ap.id = ots.pool_id;
"""

def classify_pool(row):
    """
    Applies the final, robust classification logic. Unmet Pledge is a strong
    signal that overrides viability.
    """
    is_viable_by_stake = row['stake_ada'] >= STAKE_THRESHOLD_ADA
    is_viable_by_reward = row['operator_rewards_ada'] >= REWARD_THRESHOLD_ADA
    pledge_is_met = not row['unmet_pledge']

    # --- Viability Check (Pledge must be met) ---
    if pledge_is_met:
        if is_viable_by_stake:
            return 'Healthy'
        if is_viable_by_reward:
            return 'Viable but Small'

    # --- Inactivity Check (if not viable or pledge is unmet) ---
    has_zero_blocks = row['total_blocks_in_window'] == 0
    
    # Condition A: Unmet pledge combined with another sign of neglect is Inactive.
    if not pledge_is_met and (row['no_update'] or row['no_gov']):
        return 'Inactive'

    # Condition B: Statistical underperformance or negligible presence.
    is_underperformer = row['expected_blocks'] >= EXPECTED_BLOCKS_UNDERPERFORMER_THRESHOLD
    is_negligible = row['expected_blocks'] < EXPECTED_BLOCKS_NEGLIGIBLE_THRESHOLD
    other_flags = row['no_update'] + row['no_gov']
    
    if has_zero_blocks and other_flags >= (INACTIVE_FLAG_THRESHOLD - 1) and (is_underperformer or is_negligible):
        return 'Inactive'
    
    # --- Default to Struggling ---
    return 'Struggling'


def analyze_and_report_pools():
    """
    Connects to the database, runs a comprehensive query to gather all pool data,
    classifies them, and prints a detailed report and the new summary.
    """
    conn = None
    cursor = None
    output_lines = []
    try:
        print("Connecting directly to the database...")
        conn_string = f"dbname='{DB_CONFIG['dbname']}' user='{DB_CONFIG['user']}'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # --- MODIFIED: Contextual headers are now built from the fixed epoch range ---
        analysis_period_str = f"Analysis based on performance in epochs {START_EPOCH} to {END_EPOCH} ({EPOCH_WINDOW} epochs)."
        latest_stake_str = f"Current stake is measured at the end of epoch {END_EPOCH}."
        
        context_header = "\n" + "="*80
        context_footer = "="*80 + "\n"
        print(context_header)
        print(analysis_period_str)
        print(latest_stake_str)
        print(context_footer)

        # Add this context to the top of the output file
        output_lines.extend([analysis_period_str, latest_stake_str])

        # --- MODIFIED: Parameters for the SQL query now use the fixed epoch values ---
        params = {'start_epoch': START_EPOCH, 'end_epoch': END_EPOCH}

        print("Executing comprehensive query for ALL active pools...")
        cursor.execute(ALL_POOLS_PERFORMANCE_QUERY, params)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=column_names)

        print(f"Processing data for {len(df)} non-retired pools...")

        # --- Data Preparation and Scoring ---
        df['last_update_timestamp'] = pd.to_datetime(df['last_update_timestamp']).dt.tz_localize('UTC')
        # Pin: original used pd.Timestamp.now('UTC'); replaced with REPORT_DATE
        # so the "No Update in >1 Year" (NU) signal is independent of when this
        # script is executed.
        one_year_ago = REPORT_DATE - timedelta(days=365)
        
        # FIX: Ensure correct data types before calculations to prevent TypeErrors
        df['total_operator_rewards'] = df['total_operator_rewards'].astype(float)
        df['total_stake_lovelace'] = df['total_stake_lovelace'].astype(float)
        df['total_owner_stake'] = df['total_owner_stake'].astype(float)
        df['pledge'] = df['pledge'].astype(float)
        df['total_network_stake'] = df['total_network_stake'].astype(float)

        df['operator_rewards_ada'] = df['total_operator_rewards'] / 1_000_000
        df['stake_ada'] = df['total_stake_lovelace'] / 1_000_000
        
        # Calculate expected blocks for the new classification logic
        total_network_stake_ada = df['total_network_stake'].iloc[0] / 1_000_000
        total_slots_in_window = EPOCH_WINDOW * SLOTS_PER_EPOCH * ACTIVE_SLOT_COEFF
        df['expected_blocks'] = (df['stake_ada'] / total_network_stake_ada) * total_slots_in_window
        
        # Create boolean columns for signals
        df['unmet_pledge'] = df['total_owner_stake'] < df['pledge']
        df['no_update'] = df['last_update_timestamp'] < one_year_ago
        df['no_gov'] = ~df['is_participating_in_gov']
        
        # --- Classification ---
        df['status'] = df.apply(classify_pool, axis=1)

        # --- Generate NEW Comprehensive Detailed Report for ALL Pools ---
        df_report = df.copy()
        
        signal_map = {
            'unmet_pledge': 'UP',
            'total_blocks_in_window': 'ZB',
            'no_update': 'NU',
            'no_gov': 'NG'
        }
        
        df_report['flags'] = ''
        df_report.loc[df_report['unmet_pledge'], 'flags'] += signal_map['unmet_pledge'] + ', '
        df_report.loc[df_report['total_blocks_in_window'] == 0, 'flags'] += signal_map['total_blocks_in_window'] + ', '
        df_report.loc[df_report['no_update'], 'flags'] += signal_map['no_update'] + ', '
        df_report.loc[df_report['no_gov'], 'flags'] += signal_map['no_gov'] + ', '
        df_report['flags'] = df_report['flags'].str.strip().str.rstrip(',')
        df_report['flag_count'] = df_report['flags'].str.count(',') + 1
        df_report.loc[df_report['flags'] == '', 'flag_count'] = 0

        # Define a categorical type for sorting
        status_order = ['Healthy', 'Viable but Small', 'Struggling', 'Inactive']
        df_report['status'] = pd.Categorical(df_report['status'], categories=status_order, ordered=True)

        sorted_report_df = df_report[[
            'ticker_name', 'pool_bech32_id', 'stake_ada', 'status', 'flag_count',
            'total_blocks_in_window', 'operator_rewards_ada', 'flags'
        ]].sort_values(['status', 'stake_ada'], ascending=[True, False]).reset_index(drop=True)
        sorted_report_df.index += 1

        
        report_title = "Comprehensive Report on All Non-Retired Pools by Viability Status"
        report_header = "\n" + "="*160 + f"\n{report_title.center(160)}\n" + "="*160
        report_table = tabulate(
            sorted_report_df,
            headers=['#', 'Ticker', 'Pool ID', 'Current Stake (ADA)', 'Status', 'Signal Count', 'Blocks (36 ep)', 'Rewards (36 ep)', 'Signals'],
            tablefmt='psql', stralign="left", floatfmt=",.2f"
        )
        report_footer = "="*160
        
        output_lines.extend([report_header, report_table, report_footer])


        # --- Generate NEW Comprehensive Summary Table ---
        healthy_pools = df[df['status'] == 'Healthy']
        viable_small = df[df['status'] == 'Viable but Small']
        struggling = df[df['status'] == 'Struggling']
        inactive = df[df['status'] == 'Inactive']

        # FIX: Cast sums to float before formatting to prevent TypeError
        inactive_stake_sum = float(inactive['stake_ada'].sum())
        struggling_stake_sum = float(struggling['stake_ada'].sum())
        viable_small_stake_sum = float(viable_small['stake_ada'].sum())
        healthy_stake_sum = float(healthy_pools['stake_ada'].sum())
        
        total_active_pools = len(healthy_pools) + len(viable_small) + len(struggling)
        total_active_stake = healthy_stake_sum + viable_small_stake_sum + struggling_stake_sum

        grand_total_pools = len(df)
        grand_total_stake = total_active_stake + inactive_stake_sum

        summary_data = {
            'Status': ['Inactive', 'Active & Struggling', 'Active & Viable', '', 'Total Active', '', 'Grand Total'],
            'Sub-Category': ['(Pools classified as Inactive)', '(Small & Unsuccessful)', 'Viable but Small (< 3M ADA)', 'Healthy (>= 3M ADA)', '', '', '(All Non-Retired Pools)'],
            'Number of Pools': [len(inactive), len(struggling), len(viable_small), len(healthy_pools), total_active_pools, '', grand_total_pools],
            'Controlled Stake (ADA)': [
                f"{inactive_stake_sum/1e6:.2f} M",
                f"{struggling_stake_sum/1e6:.2f} M",
                f"{viable_small_stake_sum/1e6:.2f} M",
                f"{healthy_stake_sum/1e9:.2f} B",
                f"{total_active_stake/1e9:.2f} B",
                '',
                f"{grand_total_stake/1e9:.2f} B"
            ]
        }
        
        summary_title = "Comprehensive Summary of All Pools by Viability Status"
        summary_header = "\n\n" + "="*100 + f"\n{summary_title.center(100)}\n" + "="*100
        summary_table = tabulate(pd.DataFrame(summary_data), headers='keys', tablefmt='psql', stralign="left", showindex=False)
        summary_footer = "="*100
        
        output_lines.extend([summary_header, summary_table, summary_footer])

        # --- NEW, IMPROVED Definitions and Signal Key ---
        definitions_header = "\n\nCategory Definitions (based on a 36-epoch analysis window):"
        def_h = f"- Healthy: A pool with >= {STAKE_THRESHOLD_ADA/1e6:.0f}M ADA in stake AND its pledge is met."
        def_vs = f"- Viable but Small: A pool with < {STAKE_THRESHOLD_ADA/1e6:.0f}M ADA, has earned >= {REWARD_THRESHOLD_ADA} ADA in rewards, AND its pledge is met."
        def_i = (f"- Inactive: A pool is classified as Inactive if it is not viable and meets EITHER of these conditions:\n"
                 f"    a) It has an Unmet Pledge AND at least one other signal of neglect (No Update or No Governance).\n"
                 f"    b) It has 0 blocks, is a statistical underperformer (or has negligible stake), AND triggers at least one other signal of neglect.")
        def_s = f"- Struggling: An active pool that does not meet the criteria for Healthy, Viable but Small, or Inactive."

        signals_header = "\nSignal Key:"
        signal_key_map = { 'UP': 'Unmet Pledge', 'ZB': 'Zero Blocks in 6 Months', 'NU': 'No Update in >1 Year', 'NG': 'No Governance Participation'}
        signal_lines = [f"- {acronym}: {full}" for acronym, full in signal_key_map.items()]

        output_lines.extend([definitions_header, def_h, def_vs, def_s, def_i, signals_header] + signal_lines)

        # --- Write everything to file and print to console ---
        final_output_string = "\n".join(output_lines)
        print(final_output_string)
        
        with open(OUTPUT_FILENAME, 'w') as f:
            f.write(final_output_string)
        print(f"\nReport successfully saved to {OUTPUT_FILENAME}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    analyze_and_report_pools()