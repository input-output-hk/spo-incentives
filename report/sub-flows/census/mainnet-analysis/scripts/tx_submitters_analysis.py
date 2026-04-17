#!/usr/bin/env python3
"""Transaction submitters analysis for Census §6.
Reads query results, computes findings F6.1/F6.3, generates figures."""

import csv
import io
import subprocess
import json

# ── Query 1 results: already have tx_epoch_summary from osascript
# Let's re-query via docker exec and parse in Python

def run_query(sql, label=""):
    """Run a SQL query against db-sync Instance A and return rows as list of dicts."""
    cmd = [
        "docker", "exec", "dbsync-postgres-1",
        "psql", "-U", "postgres", "-d", "cexplorer", "--csv", "-c", sql
    ]
    env = {"PGPASSWORD": "delegator-analysis-2026", "PATH": "/usr/local/bin:/usr/bin:/bin"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
    if result.returncode != 0:
        print(f"ERROR [{label}]: {result.stderr}")
        return []
    reader = csv.DictReader(io.StringIO(result.stdout))
    return list(reader)

# ── F6.1: tx count per epoch (already have data, but let's get summary stats)
print("=" * 60)
print("F6.1: Transaction volume and fee summary")
print("=" * 60)

rows = run_query("""
SELECT b.epoch_no::int,
       COUNT(*)::bigint AS tx_count,
       SUM(t.fee)/1e6 AS total_fee_ada
FROM tx t JOIN block b ON b.id = t.block_id
WHERE b.epoch_no >= 208 AND b.epoch_no < 623
GROUP BY b.epoch_no ORDER BY b.epoch_no;
""", "F6.1")

epochs = [int(r['epoch_no']) for r in rows]
tx_counts = [int(r['tx_count']) for r in rows]
fees = [float(r['total_fee_ada']) for r in rows]

# Recent baseline (last 20 full epochs)
recent = rows[-20:]
recent_tx = [int(r['tx_count']) for r in recent]
recent_fee = [float(r['total_fee_ada']) for r in recent]

print(f"Total epochs: {len(rows)} (208–622)")
print(f"Total transactions: {sum(tx_counts):,}")
print(f"Total fees: {sum(fees):,.0f} ADA")
print(f"Recent 20-epoch avg tx/epoch: {sum(recent_tx)/len(recent_tx):,.0f}")
print(f"Recent 20-epoch avg fee/epoch: {sum(recent_fee)/len(recent_fee):,.0f} ADA")
print(f"All-time peak tx: epoch {epochs[tx_counts.index(max(tx_counts))]}, {max(tx_counts):,} tx")
print(f"All-time peak fee: epoch {epochs[fees.index(max(fees))]}, {max(fees):,.0f} ADA")

# ── F6.3: Script vs key composition
print("\n" + "=" * 60)
print("F6.3: Script vs key transaction composition")
print("=" * 60)

rows_comp = run_query("""
SELECT b.epoch_no::int,
       COUNT(*) FILTER (WHERE t.script_size > 0)::bigint AS script_tx,
       COUNT(*) FILTER (WHERE t.script_size = 0)::bigint AS key_tx,
       COALESCE(SUM(t.fee) FILTER (WHERE t.script_size > 0)/1e6, 0) AS script_fee,
       COALESCE(SUM(t.fee) FILTER (WHERE t.script_size = 0)/1e6, 0) AS key_fee
FROM tx t JOIN block b ON b.id = t.block_id
WHERE b.epoch_no >= 208 AND b.epoch_no < 623
GROUP BY b.epoch_no ORDER BY b.epoch_no;
""", "F6.3")

# Post-Alonzo only (epoch >= 290)
alonzo = [r for r in rows_comp if int(r['epoch_no']) >= 290]
recent_comp = alonzo[-20:]

for label, data in [("Post-Alonzo (290–622)", alonzo), ("Recent 20 epochs", recent_comp)]:
    total_script_fee = sum(float(r['script_fee']) for r in data)
    total_key_fee = sum(float(r['key_fee']) for r in data)
    total_fee = total_script_fee + total_key_fee
    total_script_tx = sum(int(r['script_tx']) for r in data)
    total_key_tx = sum(int(r['key_tx']) for r in data)
    total_tx = total_script_tx + total_key_tx
    print(f"\n{label}:")
    print(f"  Script tx: {total_script_tx:,} ({100*total_script_tx/total_tx:.1f}%)")
    print(f"  Key tx:    {total_key_tx:,} ({100*total_key_tx/total_tx:.1f}%)")
    print(f"  Script fee: {total_script_fee:,.0f} ADA ({100*total_script_fee/total_fee:.1f}%)")
    print(f"  Key fee:    {total_key_fee:,.0f} ADA ({100*total_key_fee/total_fee:.1f}%)")

print("\nDone.")
