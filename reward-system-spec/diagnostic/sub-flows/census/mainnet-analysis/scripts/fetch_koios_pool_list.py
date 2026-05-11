"""Fresh full-network pool snapshot from Koios.

Pulls /pool_list (paginated) — every pool, with active_stake, status, ticker,
pool_group, meta_url, and the structured `relays` array. Saves to
data/koios_pool_list.json so downstream pipeline steps can run against
network truth rather than the curated MPO mapping CSV.

This single endpoint gives us:
  - Figment + small MPOs missing from the curated CSV
  - The full long tail of single-pool operators (~3000 pools total)
  - Fresh relay data (the curated CSV is a few months old)

Run: python3 scripts/fetch_koios_pool_list.py
"""
from __future__ import annotations
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "koios_pool_list.json"

API = "https://api.koios.rest/api/v1/pool_list"
PAGE = 1000  # Koios default max
TIMEOUT = 30


def fetch_page(offset: int) -> list:
    url = f"{API}?limit={PAGE}&offset={offset}"
    req = urllib.request.Request(url, headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def main() -> None:
    all_pools = []
    offset = 0
    while True:
        page = fetch_page(offset)
        if not page:
            break
        all_pools.extend(page)
        print(f"  ... fetched {len(all_pools)} (offset={offset})")
        if len(page) < PAGE:
            break
        offset += PAGE
        time.sleep(0.2)  # be polite
    print(f"total pools: {len(all_pools)}")
    # quick stats
    active = [p for p in all_pools if p.get("pool_status") == "registered"]
    with_relays = [p for p in active if p.get("relays")]
    total_stake = sum(int(p.get("active_stake") or 0) for p in active)
    print(f"  active: {len(active)}")
    print(f"  active w/ relays: {len(with_relays)}")
    print(f"  total active stake: {total_stake/1e12:.2f}B ADA")
    OUT.write_text(json.dumps(all_pools, indent=0))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
