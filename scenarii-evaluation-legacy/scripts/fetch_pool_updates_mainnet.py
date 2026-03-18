#!/usr/bin/env python3
"""
Fetch Cardano mainnet pool update history from Koios.

Outputs:
- scenarii-evaluation/data/koios_pool_updates_mainnet.csv
- scenarii-evaluation/outputs/koios_pool_updates_fetch_audit.md
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional


KOIOS_BASE = "https://api.koios.rest/api/v1"
PAGE_SIZE = 1000
REQUEST_DELAY_S = float(os.getenv("KOIOS_REQUEST_DELAY_S", "0.0"))

POOL_UPDATE_FIELDS = [
    "tx_hash",
    "block_time",
    "pool_id_bech32",
    "pool_id_hex",
    "active_epoch_no",
    "vrf_key_hash",
    "margin",
    "fixed_cost_lovelace",
    "fixed_cost_ada",
    "pledge_lovelace",
    "pledge_ada",
    "reward_addr",
    "owners",
    "relays",
    "meta_url",
    "meta_hash",
    "meta_json",
    "update_type",
    "retiring_epoch",
]


def fetch_json(url: str, retries: int = 20) -> Any:
    for attempt in range(retries):
        try:
            headers = {"accept": "application/json", "content-type": "application/json"}
            token = os.getenv("KOIOS_BEARER_TOKEN") or os.getenv("KOIOS_API_TOKEN")
            if token:
                headers["authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                sleep_s = 75 if exc.code == 429 else min(2**attempt, 30)
                print(f"Retrying {url} after HTTP {exc.code}; sleep {sleep_s}s", file=sys.stderr)
                time.sleep(sleep_s)
                continue
            raise
        except urllib.error.URLError:
            if attempt + 1 < retries:
                time.sleep(min(2**attempt, 30))
                continue
            raise


def lovelace_to_ada(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    return int(value) / 1_000_000.0


def flatten_row(row: dict) -> dict:
    return {
        "tx_hash": row.get("tx_hash"),
        "block_time": row.get("block_time"),
        "pool_id_bech32": row.get("pool_id_bech32"),
        "pool_id_hex": row.get("pool_id_hex"),
        "active_epoch_no": row.get("active_epoch_no"),
        "vrf_key_hash": row.get("vrf_key_hash"),
        "margin": row.get("margin"),
        "fixed_cost_lovelace": row.get("fixed_cost"),
        "fixed_cost_ada": lovelace_to_ada(row.get("fixed_cost")),
        "pledge_lovelace": row.get("pledge"),
        "pledge_ada": lovelace_to_ada(row.get("pledge")),
        "reward_addr": row.get("reward_addr"),
        "owners": json.dumps(row.get("owners"), separators=(",", ":")) if row.get("owners") is not None else "",
        "relays": json.dumps(row.get("relays"), separators=(",", ":")) if row.get("relays") is not None else "",
        "meta_url": row.get("meta_url"),
        "meta_hash": row.get("meta_hash"),
        "meta_json": json.dumps(row.get("meta_json"), separators=(",", ":")) if row.get("meta_json") is not None else "",
        "update_type": row.get("update_type"),
        "retiring_epoch": row.get("retiring_epoch"),
    }


def write_audit(
    *,
    row_count: int,
    min_active_epoch: Optional[int],
    max_active_epoch: Optional[int],
    out_path: Path,
) -> None:
    lines = [
        "# Koios Pool Updates Fetch Audit",
        "",
        f"- Source: `{KOIOS_BASE}`",
        f"- Rows written: **{row_count:,}**",
        f"- Active epoch range: **{min_active_epoch}..{max_active_epoch}**",
        "",
        "## Notes",
        "- `pool_updates` is fetched page by page with `offset` and `limit`.",
        "- JSON-valued columns such as `owners`, `relays`, and `meta_json` are serialized into CSV cells.",
        "",
    ]
    out_path.write_text("\n".join(lines))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "scenarii-evaluation" / "data"
    outputs_dir = root / "scenarii-evaluation" / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    out_path = data_dir / "koios_pool_updates_mainnet.csv"
    audit_path = outputs_dir / "koios_pool_updates_fetch_audit.md"
    state_path = data_dir / "koios_pool_updates_next_offset.txt"

    start_offset = int(state_path.read_text().strip()) if state_path.exists() else 0
    needs_header = not out_path.exists() or out_path.stat().st_size == 0

    with out_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=POOL_UPDATE_FIELDS)
        if needs_header:
            writer.writeheader()

        offset = start_offset
        total_new_rows = 0
        while True:
            url = f"{KOIOS_BASE}/pool_updates?offset={offset}&limit={PAGE_SIZE}"
            rows = fetch_json(url)
            if not rows:
                break
            for row in rows:
                writer.writerow(flatten_row(row))
            f.flush()
            total_new_rows += len(rows)
            offset += len(rows)
            state_path.write_text(str(offset))
            print(f"pool_updates progress: offset={offset} new_rows={total_new_rows:,}")
            if len(rows) < PAGE_SIZE:
                break
            if REQUEST_DELAY_S > 0:
                time.sleep(REQUEST_DELAY_S)

    row_count = 0
    min_active_epoch = None
    max_active_epoch = None
    with out_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            active_epoch_text = str(row.get("active_epoch_no") or "").strip()
            if active_epoch_text == "":
                continue
            active_epoch = int(active_epoch_text)
            min_active_epoch = active_epoch if min_active_epoch is None else min(min_active_epoch, active_epoch)
            max_active_epoch = active_epoch if max_active_epoch is None else max(max_active_epoch, active_epoch)

    write_audit(
        row_count=row_count,
        min_active_epoch=min_active_epoch,
        max_active_epoch=max_active_epoch,
        out_path=audit_path,
    )

    if state_path.exists():
        state_path.unlink()

    print(f"Wrote: {out_path}")
    print(f"Wrote: {audit_path}")


if __name__ == "__main__":
    main()
