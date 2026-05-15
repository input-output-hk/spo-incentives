import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from multiprocessing import Pool, cpu_count

# --- Display Options ---
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# ==============================================================================
#                              -- CONFIGURATION --
# ==============================================================================
INPUT_CSV_FILE = '../appendixB.csv'
# The case-study section of the report is also written to OUTPUT_FILE so the
# report can be diffed against the published ../appendixC.txt without having to
# hand-trim the script's stdout (which also includes the data-overview and
# longitudinal-performance sections).
OUTPUT_FILE = 'appendixC-pinned.txt'

# --- Use all available CPU cores for parallel processing ---
NUM_WORKERS = cpu_count()

# --- Dynamic Stake Proximity Configuration ---
MIN_STAKE_TOLERANCE = 1.30  # 30% tolerance for the smallest pools
MAX_STAKE_TOLERANCE = 1.05  # 5% tolerance for saturated pools
SATURATION_POINT_ADA = 74_000_000

# ==============================================================================
#                       -- PARALLEL WORKER FUNCTION --
# ==============================================================================

def find_valid_subgroups(group_tuple):
    """
    This function runs in a separate process. It takes one large "luck-equal" 
    group and finds all valid "cliques" (subgroups with similar stake) within it.
    """
    (epoch, blocks), group_df = group_tuple
    
    # Skip groups that didn't produce blocks
    if blocks == 0:
        return []
    
    if len(group_df) < 2:
        return []

    # Heartbeat for this specific worker
    print(f"  -> Worker processing: Epoch {epoch}, Blocks {blocks} ({len(group_df)} pools)")

    sorted_group = group_df.sort_values('total_stake_ada').reset_index(drop=True)
    found_subgroups = []

    for i in range(len(sorted_group)):
        for j in range(i + 1, len(sorted_group)):
            subgroup = sorted_group.iloc[i:j+1]
            if len(subgroup) < 2: continue

            min_stake = subgroup['total_stake_ada'].min()
            max_stake = subgroup['total_stake_ada'].max()
            mean_stake = subgroup['total_stake_ada'].mean()
            
            stake_ratio = min(mean_stake / SATURATION_POINT_ADA, 1.0)
            tolerance_range = MIN_STAKE_TOLERANCE - MAX_STAKE_TOLERANCE
            dynamic_threshold = MIN_STAKE_TOLERANCE - (tolerance_range * stake_ratio)
            
            if max_stake <= min_stake * dynamic_threshold:
                found_subgroups.append({
                    'epoch': epoch, 'blocks': blocks,
                    'num_pools': len(subgroup), 'df': subgroup
                })
    
    # Filter out redundant subgroups (e.g., if we found [A,B,C], remove [A,B])
    maximal_studies = []
    for study in sorted(found_subgroups, key=lambda x: len(x['df']), reverse=True):
        is_subset = False
        for max_study in maximal_studies:
            if set(study['df']['pool_id']).issubset(set(max_study['df']['pool_id'])):
                is_subset = True
                break
        if not is_subset:
            maximal_studies.append(study)
            
    return maximal_studies

# ==============================================================================
#                                -- MAIN SCRIPT --
# ==============================================================================

def analyze_data(file_path):
    df = pd.read_csv(file_path)

    # --- Data Preparation ---
    for col in ['total_delegated_stake', 'rewards_earned_in_epoch', 'pool_owners_cumulative_stake']:
        df[col] = df[col] / 1_000_000
    df.rename(columns={
        'total_delegated_stake': 'total_stake_ada', 'rewards_earned_in_epoch': 'rewards_ada',
        'pool_owners_cumulative_stake': 'pledge_ada', 'total_block_count_for_epoch': 'blocks'
    }, inplace=True)
    
    unique_epochs = sorted(df['epoch_no'].unique(), reverse=True)

    # --- Analysis Part 1: General Overview ---
    print("--- 1. Data Overview ---")
    print(f"The dataset contains {len(df)} records from {df['epoch_no'].nunique()} unique epochs.")
    print("\nStatistical Summary (in ADA):")
    print(df[['total_stake_ada', 'blocks', 'rewards_ada', 'pledge_ada']].describe().round(2))
    print("\n" + "="*80 + "\n")

    # --- Analysis Part 2: Parallel Pledge Impact Analysis ---
    print("--- 2. Pledge Impact Analysis (Holding Blocks & Stake Constant) ---")
    
    print("Grouping data by epoch and block count...")
    grouped = df.groupby(['epoch_no', 'blocks'])
    tasks = list(grouped)
    
    print(f"Found {len(tasks)} groups to check. Searching for valid comparison cliques using {NUM_WORKERS} parallel workers...")
    
    with Pool(processes=NUM_WORKERS) as pool:
        list_of_clique_lists = pool.map(find_valid_subgroups, tasks)

    all_valid_case_studies = [clique for clique_list in list_of_clique_lists for clique in clique_list]
    
    if not all_valid_case_studies:
        print("\nCould not find any valid comparison groups.")
    else:
        all_valid_case_studies.sort(key=lambda x: (x['blocks'], x['epoch']))

        # Print the case-study section to both stdout (original behavior) AND
        # to OUTPUT_FILE so the file matches the published Appendix C without
        # any stdout post-processing.
        with open(OUTPUT_FILE, 'w') as out_f:
            def emit(line=""):
                print(line)
                print(line, file=out_f)

            emit(f"Found and displaying all {len(all_valid_case_studies)} valid comparison groups across all epochs:\n")

            for study in all_valid_case_studies:
                emit(f"--- Case Study: {study['num_pools']} pools produced {study['blocks']} blocks in Epoch {study['epoch']} ---")
                sorted_case_study = study['df'].sort_values(by='pledge_ada', ascending=False)
                display_df = sorted_case_study[['pool_id', 'total_stake_ada', 'pledge_ada', 'rewards_ada']].copy()
                emit(display_df.round(2).to_string())

                high_pledge_pool = sorted_case_study.iloc[0]
                low_pledge_pool = sorted_case_study.iloc[-1]
                reward_diff = high_pledge_pool['rewards_ada'] - low_pledge_pool['rewards_ada']

                emit(f"  -> Analysis: The highest pledge pool earned {reward_diff:,.2f} ADA more than the lowest pledge pool.")
                emit("-" * 40 + "\n")
        print(f"\nCase-study section also saved to {OUTPUT_FILE}")

    print("\n" + "="*80 + "\n")

    # --- Analysis Part 3: Longitudinal Performance (Full Spectrum) ---
    print("--- 3. Multi-Epoch Performance Analysis (Full Spectrum) ---")
    pool_performance = df.groupby('pool_id').agg(
        avg_blocks=('blocks', 'mean'),
        total_blocks=('blocks', 'sum'),
        avg_pledge_ada=('pledge_ada', 'mean'),
        epochs_present=('epoch_no', 'count')
    ).sort_values(by='avg_blocks', ascending=False)

    min_epochs_present = df['epoch_no'].nunique() // 2 if df['epoch_no'].nunique() > 1 else 1
    consistent_performers = pool_performance[pool_performance['epochs_present'] >= min_epochs_present]
    num_consistent_pools = len(consistent_performers)

    if num_consistent_pools > 0:
        print(f"Found {num_consistent_pools} consistent performers (present in at least {int(min_epochs_present)} of the {df['epoch_no'].nunique()} epochs analyzed).")
        print("\n--- Top 10 Performing Pools (by Average Blocks) ---")
        print(consistent_performers.head(10).round(2))
        if num_consistent_pools > 20:
            print("\n--- 10 Middle Performing Pools (by Average Blocks) ---")
            midpoint = num_consistent_pools // 2
            print(consistent_performers.iloc[midpoint-5:midpoint+5].round(2))
            print("\n--- Bottom 10 Performing Pools (by Average Blocks) ---")
            print(consistent_performers.tail(10).round(2))
    else:
        print("No pools were present for the minimum number of epochs to analyze.")
    print("\n" + "="*80 + "\n")

    # --- Analysis Part 4: Visualization ---
    print("--- 4. Generating Visualization ---")
    plot_epoch = unique_epochs[0] if unique_epochs else None
    if plot_epoch:
        plot_epoch_df = df[(df['epoch_no'] == plot_epoch) & (df['blocks'] > 0)]
        plt.figure(figsize=(12, 7))
        pledge_bins = np.log10(plot_epoch_df['pledge_ada'] + 1)
        scatter = plt.scatter(
            plot_epoch_df['total_stake_ada'] / 1_000_000,
            plot_epoch_df['blocks'],
            c=pledge_bins, cmap='viridis', alpha=0.7, s=50
        )
        cbar = plt.colorbar(scatter)
        cbar.set_label('Pledge (log10 ADA)')
        plt.title(f'Stake vs. Block Production for Epoch {plot_epoch} (Block-Producing Pools Only)', fontsize=16)
        plt.xlabel('Total Delegated Stake (Million ADA)', fontsize=12)
        plt.ylabel('Blocks Produced', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plot_filename = 'stake_vs_blocks.png'
        plt.savefig(plot_filename)
        print(f"Scatter plot saved as '{plot_filename}'.")
    else:
        print("Skipping plot generation as no epochs were found in the data.")
    print("\nAnalysis complete.")

if __name__ == "__main__":
    if not os.path.exists(INPUT_CSV_FILE):
         print(f"FATAL ERROR: The file '{INPUT_CSV_FILE}' was not found.")
         sys.exit(1)
    analyze_data(INPUT_CSV_FILE)