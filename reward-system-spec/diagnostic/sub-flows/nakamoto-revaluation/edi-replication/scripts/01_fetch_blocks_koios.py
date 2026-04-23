"""
Fetch Cardano blocks from Koios for a 6-epoch (30-day) window ending at the
end of epoch 584, decode pool bech32 → hex pool_hash, and write the NDJSON
file expected by the EDI consensus_decentralization tool.
"""

import json
import sys
import time
from pathlib import Path

import bech32
import requests

KOIOS = "https://api.koios.rest/api/v1"
EPOCHS = list(range(579, 585))  # 579..584 inclusive (6 epochs ≈ 30 days)
PAGE = 1000
OUT = Path("raw_block_data/cardano_raw_data.json")


def bech32_to_hex(addr: str) -> str:
    hrp, data = bech32.bech32_decode(addr)
    if data is None:
        raise ValueError(f"bech32 decode failed for {addr}")
    decoded = bech32.convertbits(data, 5, 8, False)
    return bytes(decoded).hex()


def fetch_epoch(epoch: int) -> list[dict]:
    rows = []
    offset = 0
    while True:
        url = (
            f"{KOIOS}/blocks?epoch_no=eq.{epoch}"
            f"&select=hash,epoch_no,block_time,pool"
            f"&order=block_time.asc"
            f"&limit={PAGE}&offset={offset}"
        )
        for attempt in range(5):
            try:
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                batch = r.json()
                break
            except Exception as exc:
                wait = 2 ** attempt
                print(f"  retry {attempt+1} after {wait}s: {exc}", file=sys.stderr)
                time.sleep(wait)
        else:
            raise RuntimeError(f"failed page offset={offset} epoch={epoch}")
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < PAGE:
            break
        offset += PAGE
        time.sleep(0.05)
    print(f"epoch {epoch}: {len(rows)} blocks", flush=True)
    return rows


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen_pools: set[str] = set()
    n_blocks = 0
    n_no_pool = 0
    with OUT.open("w") as f:
        for ep in EPOCHS:
            rows = fetch_epoch(ep)
            for r in rows:
                pool_bech32 = r.get("pool")
                if not pool_bech32:
                    n_no_pool += 1
                    rec = {
                        "number": str(r["hash"]),
                        "timestamp": time.strftime(
                            "%Y-%m-%dT%H:%M:%S", time.gmtime(r["block_time"])
                        ),
                    }
                else:
                    pool_hex = bech32_to_hex(pool_bech32)
                    seen_pools.add(pool_hex)
                    rec = {
                        "number": str(r["hash"]),
                        "timestamp": time.strftime(
                            "%Y-%m-%dT%H:%M:%S", time.gmtime(r["block_time"])
                        ),
                        "reward_addresses": pool_hex,
                    }
                f.write(json.dumps(rec) + "\n")
                n_blocks += 1
    print(
        f"\nTotal blocks: {n_blocks}\n"
        f"Unique pool hashes: {len(seen_pools)}\n"
        f"Blocks with no pool (pre-decentralization / OBFT): {n_no_pool}\n"
        f"Output: {OUT}"
    )


if __name__ == "__main__":
    main()
