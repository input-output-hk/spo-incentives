#!/usr/bin/env python3
"""
Exploratory script: fetch delegation snapshots per pool over a window of
epochs via Koios, then compute delegation churn metrics.

Strategy
--------
1. For each epoch in [start, end], call ``/pool_delegators`` for a sample of
   active pools. This returns (stake_address, amount_lovelace) per pool per
   epoch.
2. Build a mapping  stake_addr -> [(epoch, pool_id)] across the window.
3. From that mapping, derive:
   - redelegation count per epoch (how many addresses changed pool)
   - flow matrix (origin_pool -> dest_pool counts)
   - tenure distribution (consecutive epochs on same pool)
   - churn rate = redelegations / total_active_delegations per epoch

The script is resumable: completed (pool, epoch) pairs are tracked in a
progress file so interrupted runs can continue.

Environment variables
---------------------
KOIOS_BEARER_TOKEN   Optional bearer token for higher rate limits.
KOIOS_REQUEST_DELAY_S  Delay between requests (default 0.20s).
KOIOS_MAX_WORKERS      Concurrent workers (default 1).

Usage
-----
    python fetch_delegation_churn_mainnet.py --start-epoch 600 --end-epoch 610

    # Narrower pool sample (top N by delegator count):
    python fetch_delegation_churn_mainnet.py --start-epoch 600 --end-epoch 610 --top-pools 50

Outputs land in  scenarii-evaluation-legacy/data/delegation_churn/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KOIOS_BASE = "https://api.koios.rest/api/v1"
PAGE_SIZE = 1000

def _getenv_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw and raw.strip() else default

def _getenv_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw and raw.strip() else default

REQUEST_DELAY_S = _getenv_float("KOIOS_REQUEST_DELAY_S", 0.20)
MAX_WORKERS = max(1, _getenv_int("KOIOS_MAX_WORKERS", 1))

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data" / "delegation_churn"


# ---------------------------------------------------------------------------
# HTTP helper  (mirrors the pattern in fetch_pool_history_mainnet.py)
# ---------------------------------------------------------------------------

def fetch_json(
    url: str,
    *,
    method: str = "GET",
    body: Optional[bytes] = None,
    retries: int = 20,
) -> Any:
    for attempt in range(retries):
        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
            }
            token = os.getenv("KOIOS_BEARER_TOKEN") or os.getenv("KOIOS_API_TOKEN")
            if token:
                headers["authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                sleep_s = 75 if exc.code == 429 else min(2 ** attempt, 30)
                print(f"  retry {url} HTTP {exc.code}; sleep {sleep_s}s", file=sys.stderr)
                time.sleep(sleep_s)
                continue
            raise
        except urllib.error.URLError:
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 30))
                continue
            raise


# ---------------------------------------------------------------------------
# Koios calls
# ---------------------------------------------------------------------------

def fetch_current_epoch() -> int:
    tip = fetch_json(f"{KOIOS_BASE}/tip")
    return int(tip[0]["epoch_no"])


def fetch_pool_list_active() -> List[dict]:
    """Return all registered pools (paginated GET)."""
    rows: List[dict] = []
    offset = 0
    while True:
        url = f"{KOIOS_BASE}/pool_list?offset={offset}&limit={PAGE_SIZE}"
        page = fetch_json(url)
        if not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += len(page)
        time.sleep(REQUEST_DELAY_S)
    return rows


def fetch_pool_delegators_for_epoch(
    pool_bech32: str, epoch_no: int
) -> List[dict]:
    """
    GET /pool_delegators_history?_pool_bech32=...&_epoch_no=...
    Returns list of {stake_address, amount, epoch_no} dicts.
    Handles pagination.
    """
    rows: List[dict] = []
    offset = 0
    while True:
        qs = urllib.parse.urlencode({
            "_pool_bech32": pool_bech32,
            "_epoch_no": epoch_no,
        })
        url = f"{KOIOS_BASE}/pool_delegators_history?{qs}&offset={offset}&limit={PAGE_SIZE}"
        page = fetch_json(url)
        if not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += len(page)
        time.sleep(REQUEST_DELAY_S)
    return rows


# ---------------------------------------------------------------------------
# Progress tracking (resumability)
# ---------------------------------------------------------------------------

def load_progress(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {line.strip() for line in f if line.strip()}


def save_progress_entry(path: Path, entry: str) -> None:
    with path.open("a") as f:
        f.write(entry + "\n")


def progress_key(pool_id: str, epoch: int) -> str:
    return f"{pool_id}|{epoch}"


# ---------------------------------------------------------------------------
# Pool selection heuristic
# ---------------------------------------------------------------------------

def select_pools(
    pool_list: List[dict],
    pool_history_csv: Optional[Path],
    top_n: int,
    ref_epoch: int,
) -> List[str]:
    """
    Pick the top_n pools by delegator count at ref_epoch.
    If pool_history_csv is available, use it; otherwise fall back to
    active_stake from pool_list as a proxy.
    """
    if pool_history_csv and pool_history_csv.exists():
        pool_deleg: Dict[str, int] = {}
        with pool_history_csv.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row.get("epoch_no", 0)) == ref_epoch:
                    pid = row["pool_id_bech32"]
                    cnt = int(row.get("delegator_cnt", 0) or 0)
                    pool_deleg[pid] = cnt
        ranked = sorted(pool_deleg, key=lambda p: pool_deleg[p], reverse=True)
        if ranked:
            return ranked[:top_n]

    # Fallback: sort by active_stake from pool_list
    valid = [p for p in pool_list if p.get("pool_status") == "registered"]
    valid.sort(key=lambda p: int(p.get("active_stake") or 0), reverse=True)
    return [p["pool_id_bech32"] for p in valid[:top_n]]


# ---------------------------------------------------------------------------
# Main fetch loop
# ---------------------------------------------------------------------------

def fetch_snapshots(
    pools: List[str],
    start_epoch: int,
    end_epoch: int,
    snapshot_csv: Path,
    progress_file: Path,
) -> None:
    """
    For each (pool, epoch) pair, fetch delegators and append to snapshot_csv.
    """
    done = load_progress(progress_file)
    write_header = not snapshot_csv.exists() or snapshot_csv.stat().st_size == 0

    total_pairs = len(pools) * (end_epoch - start_epoch + 1)
    already = len(done)
    remaining = total_pairs - already
    print(f"Total (pool x epoch) pairs: {total_pairs}  |  already done: {already}  |  remaining: {remaining}")

    with snapshot_csv.open("a", newline="") as fout:
        writer = csv.writer(fout)
        if write_header:
            writer.writerow(["epoch_no", "pool_id_bech32", "stake_address", "amount_lovelace"])

        for epoch in range(start_epoch, end_epoch + 1):
            for pool_id in pools:
                key = progress_key(pool_id, epoch)
                if key in done:
                    continue

                delegators = fetch_pool_delegators_for_epoch(pool_id, epoch)
                for d in delegators:
                    writer.writerow([
                        epoch,
                        pool_id,
                        d.get("stake_address", ""),
                        d.get("amount", ""),
                    ])
                fout.flush()
                save_progress_entry(progress_file, key)

                n = len(delegators)
                print(f"  epoch {epoch}  pool {pool_id[:20]}…  delegators={n}")
                time.sleep(REQUEST_DELAY_S)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyse_churn(snapshot_csv: Path, output_dir: Path) -> None:
    """
    Read the snapshot CSV and compute churn metrics.
    """
    print("\n=== Analysing delegation churn ===")

    # stake_addr -> sorted list of (epoch, pool_id)
    addr_history: Dict[str, List[Tuple[int, str]]] = defaultdict(list)

    with snapshot_csv.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            addr_history[row["stake_address"]].append(
                (int(row["epoch_no"]), row["pool_id_bech32"])
            )

    # Sort each address's history by epoch
    for addr in addr_history:
        addr_history[addr].sort()

    total_addrs = len(addr_history)
    print(f"Unique stake addresses: {total_addrs}")

    # --- 1. Redelegation events ---
    # An event = address present in epoch N on pool A, epoch N+1 on pool B (A != B)
    redelegations_by_epoch: Dict[int, int] = defaultdict(int)
    active_by_epoch: Dict[int, int] = defaultdict(int)
    flow: Dict[Tuple[str, str], int] = defaultdict(int)  # (from_pool, to_pool) -> count
    tenures: List[int] = []  # consecutive epochs on same pool

    for addr, hist in addr_history.items():
        # Count active per epoch
        for epoch, _ in hist:
            active_by_epoch[epoch] += 1

        # Detect changes
        prev_epoch, prev_pool = hist[0]
        streak = 1
        for epoch, pool in hist[1:]:
            if pool != prev_pool:
                redelegations_by_epoch[epoch] += 1
                flow[(prev_pool, pool)] += 1
                tenures.append(streak)
                streak = 1
            else:
                # Only count consecutive epochs
                if epoch == prev_epoch + 1:
                    streak += 1
                else:
                    tenures.append(streak)
                    streak = 1
            prev_epoch, prev_pool = epoch, pool
        tenures.append(streak)  # final streak

    # --- Write churn_rate_per_epoch.csv ---
    churn_csv = output_dir / "churn_rate_per_epoch.csv"
    epochs_sorted = sorted(set(list(redelegations_by_epoch.keys()) + list(active_by_epoch.keys())))
    with churn_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch_no", "active_delegations", "redelegations", "churn_rate"])
        for e in epochs_sorted:
            active = active_by_epoch.get(e, 0)
            redel = redelegations_by_epoch.get(e, 0)
            rate = redel / active if active else 0.0
            w.writerow([e, active, redel, f"{rate:.6f}"])
    print(f"Wrote {churn_csv}")

    # --- Write flow_matrix.csv ---
    flow_csv = output_dir / "flow_matrix.csv"
    flow_sorted = sorted(flow.items(), key=lambda x: x[1], reverse=True)
    with flow_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["from_pool", "to_pool", "count"])
        for (fp, tp), cnt in flow_sorted:
            w.writerow([fp, tp, cnt])
    print(f"Wrote {flow_csv}  ({len(flow_sorted)} flows)")

    # --- Write tenure_distribution.csv ---
    tenure_csv = output_dir / "tenure_distribution.csv"
    tenure_counts: Dict[int, int] = defaultdict(int)
    for t in tenures:
        tenure_counts[t] += 1
    with tenure_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tenure_epochs", "count"])
        for t in sorted(tenure_counts):
            w.writerow([t, tenure_counts[t]])
    print(f"Wrote {tenure_csv}")

    # --- Summary ---
    total_redel = sum(redelegations_by_epoch.values())
    avg_tenure = sum(tenures) / len(tenures) if tenures else 0
    summary_path = output_dir / "churn_summary.md"
    with summary_path.open("w") as f:
        f.write("# Delegation Churn Summary\n\n")
        f.write(f"- **Window**: epochs {epochs_sorted[0]}–{epochs_sorted[-1]}\n")
        f.write(f"- **Unique stake addresses observed**: {total_addrs:,}\n")
        f.write(f"- **Total redelegation events**: {total_redel:,}\n")
        f.write(f"- **Average tenure** (consecutive epochs on same pool): {avg_tenure:.1f}\n")
        f.write(f"- **Top 10 flows** (origin → destination):\n\n")
        f.write("| From pool | To pool | Count |\n")
        f.write("|---|---|---|\n")
        for (fp, tp), cnt in flow_sorted[:10]:
            f.write(f"| `{fp[:20]}…` | `{tp[:20]}…` | {cnt:,} |\n")
    print(f"Wrote {summary_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch delegation snapshots and compute churn metrics.")
    parser.add_argument("--start-epoch", type=int, default=None,
                        help="First epoch to fetch (default: current - 10)")
    parser.add_argument("--end-epoch", type=int, default=None,
                        help="Last epoch to fetch (default: current - 1)")
    parser.add_argument("--top-pools", type=int, default=30,
                        help="Number of top pools to sample (default: 30)")
    parser.add_argument("--analyse-only", action="store_true",
                        help="Skip fetching, run analysis on existing snapshot CSV")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_dir = DATA_DIR
    snapshot_csv = DATA_DIR / "delegation_snapshots.csv"
    progress_file = DATA_DIR / "delegation_fetch_progress.txt"

    if not args.analyse_only:
        current_epoch = fetch_current_epoch()
        print(f"Current tip epoch: {current_epoch}")

        start = args.start_epoch if args.start_epoch is not None else current_epoch - 10
        end = args.end_epoch if args.end_epoch is not None else current_epoch - 1
        print(f"Epoch window: {start}–{end}")

        # Pool history CSV (from prior fetch) for ranking
        pool_history_csv = SCRIPT_DIR.parent / "data" / "koios_pool_history_mainnet.csv"

        print("Fetching pool list …")
        pool_list = fetch_pool_list_active()
        print(f"Pool universe: {len(pool_list)} pools")

        pools = select_pools(pool_list, pool_history_csv, args.top_pools, end)
        print(f"Selected {len(pools)} pools for delegation snapshot")

        fetch_snapshots(pools, start, end, snapshot_csv, progress_file)

    if snapshot_csv.exists() and snapshot_csv.stat().st_size > 0:
        analyse_churn(snapshot_csv, output_dir)
    else:
        print("No snapshot data to analyse.", file=sys.stderr)


if __name__ == "__main__":
    main()
