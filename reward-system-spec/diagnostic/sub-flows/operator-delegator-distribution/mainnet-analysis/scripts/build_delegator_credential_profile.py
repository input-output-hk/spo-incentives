#!/usr/bin/env python3
"""
Delegator Credential Profile — Key vs Script stake address classification.

For each rewarded pool at a given epoch, queries Koios `pool_delegators`
to retrieve every stake_address and its delegated amount, then classifies
the address as KEY-based (stake1u… / header e0/e1) or SCRIPT-based
(stake17… / header f0/f1) using the Bech32 prefix.

Produces:
  1. data/delegator_credential_by_pool.csv
       pool_id_bech32, key_deleg, script_deleg, key_stake, script_stake
  2. data/delegator_credential_summary.csv
       Aggregate: total key vs script delegations and stake, by strategy
  3. data/delegator_credential_by_entity.csv
       Entity-level: key vs script delegations and stake

Data source:
  - data/reward_split_snapshot.csv  (pool list + entity mapping)
  - Koios API: pool_delegators      (live query, paginated)

Usage:
    python3 scripts/build_delegator_credential_profile.py

Concurrency: uses ThreadPoolExecutor with 10 workers. Resume-safe.
Total runtime: ~10-20 min for 875 pools depending on Koios load.
"""

import csv
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SNAPSHOT_PATH = DATA_DIR / "reward_split_snapshot.csv"

OUT_BY_POOL = DATA_DIR / "delegator_credential_by_pool.csv"
OUT_SUMMARY = DATA_DIR / "delegator_credential_summary.csv"
OUT_BY_ENTITY = DATA_DIR / "delegator_credential_by_entity.csv"

KOIOS_BASE = "https://api.koios.rest/api/v1"
PAGE_LIMIT = 1000
MAX_RETRIES = 4
RETRY_BACKOFF = 3
WORKERS = 10

# Thread-safe writer
write_lock = threading.Lock()


def classify_stake_address(addr: str) -> str:
    """Return 'key' or 'script' based on the Bech32 prefix."""
    if addr.startswith("stake_test1"):
        discriminant = addr[11] if len(addr) > 11 else "?"
    elif addr.startswith("stake1"):
        discriminant = addr[6] if len(addr) > 6 else "?"
    else:
        return "unknown"

    if discriminant in ("u", "q"):
        return "key"
    elif discriminant in ("7", "z"):
        return "script"
    return "unknown"


def fetch_pool_delegators(pool_bech32: str) -> list[dict]:
    """Fetch all delegators for a pool from Koios, handling pagination."""
    all_delegators = []
    offset = 0
    session = requests.Session()

    while True:
        url = f"{KOIOS_BASE}/pool_delegators"
        params = {
            "_pool_bech32": pool_bech32,
            "limit": PAGE_LIMIT,
            "offset": offset,
        }

        for attempt in range(MAX_RETRIES):
            try:
                r = session.get(url, params=params, timeout=120)
                if r.status_code == 200:
                    break
                if r.status_code in (429, 500, 502, 503, 504):
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    time.sleep(wait)
                    continue
                return all_delegators
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError):
                wait = RETRY_BACKOFF * (2 ** attempt)
                time.sleep(wait)
        else:
            return all_delegators

        page = r.json()
        if not page:
            break
        all_delegators.extend(page)
        if len(page) < PAGE_LIMIT:
            break
        offset += PAGE_LIMIT

    return all_delegators


def process_pool(pool: dict, writer, counter: dict):
    """Fetch delegators for one pool, classify, and write result."""
    pid = pool["pool_id_bech32"]
    delegators = fetch_pool_delegators(pid)

    counts = {"key": 0, "script": 0, "unknown": 0}
    stakes = {"key": 0.0, "script": 0.0, "unknown": 0.0}

    for d in delegators:
        addr = d.get("stake_address", "")
        ctype = classify_stake_address(addr)
        amount = float(d.get("amount", 0)) / 1e6
        counts[ctype] += 1
        stakes[ctype] += amount

    row = [
        pid, pool["pool_class"], pool["eff_entity_id"],
        pool["display_name"],
        counts["key"], counts["script"], counts["unknown"],
        f"{stakes['key']:.2f}", f"{stakes['script']:.2f}",
        f"{stakes['unknown']:.2f}",
    ]

    with write_lock:
        writer.writerow(row)
        counter["done"] += 1
        n = counter["done"]
        total = counter["total"]
        if n % 25 == 0 or n == total:
            print(f"  [{n}/{total}] latest: {pool['display_name'] or pid[:16]}… "
                  f"key={counts['key']} script={counts['script']}", flush=True)


def main():
    # ------------------------------------------------------------------
    # 1. Load pool snapshot
    # ------------------------------------------------------------------
    if not SNAPSHOT_PATH.exists():
        print(f"ERROR: {SNAPSHOT_PATH} not found.")
        sys.exit(1)

    pools = []
    with open(SNAPSHOT_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            pools.append({
                "pool_id_bech32": row["pool_id_bech32"],
                "pool_class": row["pool_class"],
                "eff_entity_id": row["eff_entity_id"],
                "display_name": row.get("display_name", ""),
                "active_stake_ada": float(row["active_stake_ada"]),
                "delegator_cnt": int(row["delegator_cnt"]),
            })

    print(f"Loaded {len(pools)} pools")

    # ------------------------------------------------------------------
    # 2. Resume support
    # ------------------------------------------------------------------
    done_pools = set()
    if OUT_BY_POOL.exists():
        with open(OUT_BY_POOL) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_pools.add(row["pool_id_bech32"])
        print(f"Resuming: {len(done_pools)} pools already done")

    todo = [p for p in pools if p["pool_id_bech32"] not in done_pools]
    if not todo:
        print("All pools already done, skipping to aggregation")
    else:
        print(f"Querying {len(todo)} pools with {WORKERS} threads …")

        write_header = len(done_pools) == 0
        out_f = open(OUT_BY_POOL, "a", newline="")
        writer = csv.writer(out_f)
        if write_header:
            writer.writerow([
                "pool_id_bech32", "pool_class", "eff_entity_id", "display_name",
                "key_deleg", "script_deleg", "unknown_deleg",
                "key_stake_ada", "script_stake_ada", "unknown_stake_ada",
            ])
            out_f.flush()

        counter = {"done": len(done_pools), "total": len(pools)}
        t0 = time.time()

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(process_pool, p, writer, counter): p
                for p in todo
            }
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pool = futures[future]
                    print(f"  ERROR on {pool['pool_id_bech32'][:16]}: {e}")
                # Flush periodically
                out_f.flush()

        out_f.close()
        elapsed = time.time() - t0
        print(f"\nDone in {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # ------------------------------------------------------------------
    # 3. Build summaries
    # ------------------------------------------------------------------
    import pandas as pd
    df = pd.read_csv(OUT_BY_POOL)
    print(f"\nAggregating {len(df)} pools …")

    strat_map = {"hollow": "hollow", "balanced": "balanced", "private": "private"}
    df["strategy"] = df["pool_class"].str.lower().map(
        lambda x: next((v for k, v in strat_map.items() if k in x), "other")
    )

    # Strategy summary
    summary = df.groupby("strategy").agg(
        pools=("pool_id_bech32", "count"),
        key_deleg=("key_deleg", "sum"),
        script_deleg=("script_deleg", "sum"),
        key_stake_ada=("key_stake_ada", "sum"),
        script_stake_ada=("script_stake_ada", "sum"),
    ).reset_index()
    summary["total_deleg"] = summary["key_deleg"] + summary["script_deleg"]
    summary["script_deleg_pct"] = (
        summary["script_deleg"] / summary["total_deleg"] * 100
    ).round(2)
    summary["script_stake_pct"] = (
        summary["script_stake_ada"]
        / (summary["key_stake_ada"] + summary["script_stake_ada"])
        * 100
    ).round(2)

    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"\n=== Strategy summary → {OUT_SUMMARY} ===")
    print(summary.to_string(index=False))

    # Grand totals
    print(f"\n=== Grand totals ===")
    for col in ["key_deleg", "script_deleg", "key_stake_ada", "script_stake_ada"]:
        print(f"  {col}: {df[col].sum():,.0f}")

    # Entity summary
    ent = df.groupby(["eff_entity_id", "display_name", "strategy"]).agg(
        pools=("pool_id_bech32", "count"),
        key_deleg=("key_deleg", "sum"),
        script_deleg=("script_deleg", "sum"),
        key_stake_ada=("key_stake_ada", "sum"),
        script_stake_ada=("script_stake_ada", "sum"),
    ).reset_index()
    ent["total_deleg"] = ent["key_deleg"] + ent["script_deleg"]
    ent["script_deleg_pct"] = (
        ent["script_deleg"] / ent["total_deleg"].replace(0, 1) * 100
    ).round(2)
    ent.sort_values("script_stake_ada", ascending=False, inplace=True)
    ent.to_csv(OUT_BY_ENTITY, index=False)
    print(f"\nEntity-level output → {OUT_BY_ENTITY}")

    top = ent[ent["script_deleg"] > 0].head(20)
    if not top.empty:
        print("\nTop 20 entities by script-based stake:")
        print(top[["display_name", "strategy", "pools",
                    "key_deleg", "script_deleg", "script_deleg_pct",
                    "script_stake_ada"]].to_string(index=False))

    print("\nDone.")


if __name__ == "__main__":
    main()
