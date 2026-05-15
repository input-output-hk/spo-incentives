import psycopg2
import csv
from multiprocessing import Pool, cpu_count

# ==============================================================================
#                              -- CONFIGURATION --
# ==============================================================================

DB_CONFIG = {
    "dbname": "cexplorer",
    "user": "carlos",
}

# Number of parallel worker processes to run.
NUM_WORKERS = cpu_count()

NUM_EPOCHS = 36

POOL_SIZE_RANGES_ADA = [
    "100000-1000000",        # 0.1M - 1M
    "1000000-3000000",      # 1M - 3M
    "3000000-5000000",      # 3M - 5M
    "5000000-7000000",      # 5M - 7M
    "7000000-10000000",     # 7M - 10M
    "10000000-15000000",    # 10M - 15M
    "15000000-20000000",    # 15M - 20M
    "20000000-25000000",    # 20M - 25M
    "25000000-30000000",    # 25M - 30M
    "30000000-40000000",    # 30M - 40M
    "40000000-50000000",    # 40M - 50M
    "50000000-60000000",    # 50M - 60M
    "60000000-74000000",     # 60M - 74M (Up to saturation)
    "74000000-100000000"     # 74M - 100M (Above saturation)
]

OUTPUT_CSV_FILE = "appendixB-pinned.csv"

# ==============================================================================
#                               -- SQL QUERY --
# ==============================================================================

SQL_QUERY = """
WITH target_epoch AS (
  -- Pinned to epoch 586 to reproduce the November 2025 report's Appendix B
  -- (epochs 549..584, i.e. 586 minus offsets 2..37). Replace 586 with
  -- (SELECT MAX(epoch_no) FROM epoch_stake) to use the latest indexed epoch.
  SELECT (586 - %s) AS epoch_no
),
-- NEW: Added a filter to exclude abandoned pools at the database level
eligible_pools AS (
  SELECT es.pool_id, SUM(es.amount) AS total_delegated_stake
  FROM epoch_stake AS es
  JOIN pool_hash AS ph ON es.pool_id = ph.id
  WHERE es.epoch_no = (SELECT epoch_no FROM target_epoch)
    AND ph.view NOT IN (
      -- PASTE YOUR COMMA-SEPARATED LIST OF POOL IDs HERE
      -- For example: 'pool1abc...', 'pool1def...'
      'pool1ddskftmsscw92d7vnj89pldwx5feegkgcmamgt5t0e4lkd7mdp8',
      'pool124lm97s6f4satl7xz0ulzgg6tv30tskry3zcntwrz68n60v5yne'
      -- ... continue pasting the rest of your list here
    )
  GROUP BY es.pool_id
  HAVING SUM(es.amount) BETWEEN %s AND %s
),
epoch_blocks AS (
  SELECT sl.pool_hash_id, COUNT(b.id) AS number_of_blocks
  FROM block AS b JOIN slot_leader AS sl ON b.slot_leader_id = sl.id
  WHERE b.epoch_no = (SELECT epoch_no FROM target_epoch) AND sl.pool_hash_id IS NOT NULL
  GROUP BY sl.pool_hash_id
), epoch_rewards AS (
  SELECT pool_id, SUM(amount) AS total_rewards
  FROM reward
  WHERE earned_epoch = (SELECT epoch_no FROM target_epoch) AND type IN ('leader', 'member')
  GROUP BY pool_id
), latest_pool_updates AS (
  -- Owner-pin (Option B): freeze pool_update state to txs registered on or before
  -- epoch 586 (the same anchor used by target_epoch). Without this filter, the
  -- "latest" pool_update reflects whatever is in dbsync at run time, so pools
  -- that re-registered after the original report was produced would resolve to
  -- different owner addresses, causing pool_owners_cumulative_stake to drift.
  SELECT id, hash_id FROM (
      SELECT pu.id, pu.hash_id, ROW_NUMBER() OVER (PARTITION BY pu.hash_id ORDER BY pu.registered_tx_id DESC) as rn
      FROM pool_update pu
      JOIN tx t ON pu.registered_tx_id = t.id
      JOIN block b ON t.block_id = b.id
      WHERE b.epoch_no <= 586
  ) AS ranked_updates WHERE rn = 1
), owner_stake AS (
  SELECT lpu.hash_id AS pool_id, SUM(es.amount) AS owners_cumulative_stake
  FROM latest_pool_updates AS lpu
  JOIN pool_owner AS po ON po.pool_update_id = lpu.id
  JOIN epoch_stake AS es ON es.addr_id = po.addr_id
  WHERE es.epoch_no = (SELECT epoch_no FROM target_epoch)
  GROUP BY lpu.hash_id
)
SELECT
  (SELECT epoch_no FROM target_epoch) as epoch_no,
  ph.view AS pool_id,
  ep.total_delegated_stake,
  COALESCE(eb.number_of_blocks, 0) AS total_block_count_for_epoch,
  COALESCE(er.total_rewards, 0) AS rewards_earned_in_epoch,
  COALESCE(os.owners_cumulative_stake, 0) AS pool_owners_cumulative_stake
FROM eligible_pools AS ep
JOIN pool_hash AS ph ON ep.pool_id = ph.id
LEFT JOIN epoch_blocks AS eb ON ep.pool_id = eb.pool_hash_id
LEFT JOIN epoch_rewards AS er ON ep.pool_id = er.pool_id
LEFT JOIN owner_stake AS os ON ep.pool_id = os.pool_id;
"""
# Note: The ORDER BY in the SQL has been removed as Python will handle the final sorting.

# ==============================================================================
#                                -- SCRIPT --
# ==============================================================================

def run_query_worker(offset, min_lovelace, max_lovelace, range_str):
    """This function is executed by each worker process."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            variables = (offset, min_lovelace, max_lovelace)
            cur.execute(SQL_QUERY, variables)
            rows = cur.fetchall()
            
            # Logging uses the same pinned anchor (586) as the SQL above.
            target_epoch = 586 - offset

            print(f"  -> Fetched {len(rows)} pools for epoch {target_epoch} in range {range_str}")
            return rows
    except psycopg2.Error as e:
        print(f"Database error in worker: {e}")
        return []
    finally:
        if conn:
            conn.close()


def main():
    """Main function to prepare tasks, run them in parallel, sort, and save results."""
    
    tasks = []
    for size_range in POOL_SIZE_RANGES_ADA:
        min_ada_str, max_ada_str = size_range.split('-')
        min_lovelace = int(min_ada_str) * 1_000_000
        max_lovelace = int(max_ada_str) * 1_000_000
        for offset in range(2, NUM_EPOCHS + 2):
            tasks.append((offset, min_lovelace, max_lovelace, size_range))

    print(f"Prepared {len(tasks)} queries to run using {NUM_WORKERS} parallel workers.\n")

    with Pool(processes=NUM_WORKERS) as pool:
        results = pool.starmap(run_query_worker, tasks)

    print("\nAll queries have completed. Sorting results...")

    all_rows = [row for row_list in results for row in row_list]

    # Sort by epoch (desc), then by block count (desc).
    all_rows.sort(key=lambda row: (row[0], row[3]), reverse=True)
    
    print("Writing sorted results to CSV...")

    with open(OUTPUT_CSV_FILE, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        headers = [
            "epoch_no", "pool_id", "total_delegated_stake",
            "total_block_count_for_epoch", "rewards_earned_in_epoch",
            "pool_owners_cumulative_stake"
        ]
        csv_writer.writerow(headers)
        
        csv_writer.writerows(all_rows)

    print(f"Analysis complete. Saved {len(all_rows)} total rows to '{OUTPUT_CSV_FILE}'.")


if __name__ == "__main__":
    main()