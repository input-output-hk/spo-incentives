#!/usr/bin/env python3
"""
Fetch Cardano mainnet pool owner history from Koios.

The fetch is resumable:
- `koios_pool_owner_history_mainnet.csv` stores the raw owner history rows.
- `koios_pool_owner_history_fetched_ids.txt` records pool ids whose owner history was fetched.

Outputs:
- scenarii-evaluation/data/koios_pool_owner_history_mainnet.csv
- scenarii-evaluation/data/koios_pool_owner_history_fetched_ids.txt
- scenarii-evaluation/outputs/koios_pool_owner_history_fetch_audit.md
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any, Iterable, List, Optional


def getenv_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def getenv_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


KOIOS_BASE = "https://api.koios.rest/api/v1"
SHELLEY_START_EPOCH = 208
PAGE_SIZE = 1000
REQUEST_DELAY_S = getenv_float("KOIOS_REQUEST_DELAY_S", 0.0)
MAX_WORKERS = max(1, getenv_int("KOIOS_MAX_WORKERS", 4))
BATCH_SIZE = max(1, getenv_int("KOIOS_OWNER_HISTORY_BATCH_SIZE", 50))

OWNER_HISTORY_FIELDS = [
    "pool_id_bech32",
    "stake_address",
    "epoch_no",
    "declared_pledge_lovelace",
    "declared_pledge_ada",
    "owner_active_stake_lovelace",
    "owner_active_stake_ada",
]


def fetch_json(url: str, *, method: str = "GET", body: bytes | None = None, retries: int = 20) -> Any:
    for attempt in range(retries):
        try:
            headers = {"accept": "application/json", "content-type": "application/json"}
            token = os.getenv("KOIOS_BEARER_TOKEN") or os.getenv("KOIOS_API_TOKEN")
            if token:
                headers["authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=180) as resp:
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


def read_pool_ids(path: Path) -> List[str]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return [row["pool_id_bech32"] for row in reader]


def read_completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {line.strip() for line in f if line.strip()}


def fetch_owner_history_rows(pool_ids: List[str]) -> tuple[List[str], List[dict], Optional[int], Optional[int]]:
    body = json.dumps({"_pool_bech32_ids": pool_ids}).encode()
    output_rows: List[dict] = []
    min_epoch = None
    max_epoch = None
    offset = 0
    while True:
        try:
            rows = fetch_json(
                f"{KOIOS_BASE}/pool_owner_history?offset={offset}&limit={PAGE_SIZE}",
                method="POST",
                body=body,
            )
        except urllib.error.HTTPError as exc:
            if exc.code == 413 and len(pool_ids) > 1:
                mid = len(pool_ids) // 2
                left_ids, left_rows, left_min_epoch, left_max_epoch = fetch_owner_history_rows(pool_ids[:mid])
                right_ids, right_rows, right_min_epoch, right_max_epoch = fetch_owner_history_rows(pool_ids[mid:])
                min_epoch = left_min_epoch if right_min_epoch is None else right_min_epoch if left_min_epoch is None else min(left_min_epoch, right_min_epoch)
                max_epoch = left_max_epoch if right_max_epoch is None else right_max_epoch if left_max_epoch is None else max(left_max_epoch, right_max_epoch)
                return left_ids + right_ids, left_rows + right_rows, min_epoch, max_epoch
            raise

        if not rows:
            break
        for row in rows:
            epoch_no = int(row["epoch_no"])
            if epoch_no < SHELLEY_START_EPOCH:
                continue
            min_epoch = epoch_no if min_epoch is None else min(min_epoch, epoch_no)
            max_epoch = epoch_no if max_epoch is None else max(max_epoch, epoch_no)
            output_rows.append(
                {
                    "pool_id_bech32": row.get("pool_id_bech32"),
                    "stake_address": row.get("stake_address"),
                    "epoch_no": epoch_no,
                    "declared_pledge_lovelace": row.get("declared_pledge"),
                    "declared_pledge_ada": lovelace_to_ada(row.get("declared_pledge")),
                    "owner_active_stake_lovelace": row.get("active_stake"),
                    "owner_active_stake_ada": lovelace_to_ada(row.get("active_stake")),
                }
            )
        offset += len(rows)
        if REQUEST_DELAY_S > 0:
            time.sleep(REQUEST_DELAY_S)
        if len(rows) < PAGE_SIZE:
            break
    return pool_ids, output_rows, min_epoch, max_epoch


def iter_batches(pool_ids: List[str], completed_ids: set[str]) -> Iterable[tuple[int, List[str], List[dict], Optional[int], Optional[int]]]:
    remaining_pool_ids = [pool_id for pool_id in pool_ids if pool_id not in completed_ids]
    batches = [remaining_pool_ids[idx : idx + BATCH_SIZE] for idx in range(0, len(remaining_pool_ids), BATCH_SIZE)]
    if MAX_WORKERS == 1 or len(batches) <= 1:
        for done_count, batch_pool_ids in enumerate(batches, start=1):
            pool_ids_done, rows, min_epoch, max_epoch = fetch_owner_history_rows(batch_pool_ids)
            yield done_count, pool_ids_done, rows, min_epoch, max_epoch
        return

    worker_count = min(MAX_WORKERS, len(batches))
    batch_iter = iter(batches)
    done_count = 0

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_batch = {}

        def submit_next() -> bool:
            try:
                batch_pool_ids = next(batch_iter)
            except StopIteration:
                return False
            future = executor.submit(fetch_owner_history_rows, batch_pool_ids)
            future_to_batch[future] = batch_pool_ids
            return True

        for _ in range(worker_count):
            if not submit_next():
                break

        while future_to_batch:
            done_futures, _ = wait(future_to_batch, return_when=FIRST_COMPLETED)
            for future in done_futures:
                future_to_batch.pop(future)
                pool_ids_done, rows, min_epoch, max_epoch = future.result()
                done_count += 1
                yield done_count, pool_ids_done, rows, min_epoch, max_epoch
                submit_next()


def write_audit(
    *,
    total_pools: int,
    completed_pools: int,
    row_count: int,
    min_epoch: Optional[int],
    max_epoch: Optional[int],
    out_path: Path,
) -> None:
    lines = [
        "# Koios Pool Owner History Fetch Audit",
        "",
        f"- Source: `{KOIOS_BASE}`",
        f"- Pools discovered: **{total_pools}**",
        f"- Pools completed: **{completed_pools}**",
        f"- Rows written: **{row_count:,}**",
        f"- Epoch range written: **{min_epoch}..{max_epoch}**",
        "",
        "## Notes",
        "- `pool_owner_history` is fetched in POST batches of pool ids.",
        "- Oversized batches are split recursively on HTTP 413.",
        "- The job is resumable through `koios_pool_owner_history_fetched_ids.txt`.",
        "",
    ]
    out_path.write_text("\n".join(lines))


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "scenarii-evaluation" / "data"
    outputs_dir = root / "scenarii-evaluation" / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pool_list_path = data_dir / "koios_pool_list_mainnet.csv"
    out_path = data_dir / "koios_pool_owner_history_mainnet.csv"
    fetched_ids_path = data_dir / "koios_pool_owner_history_fetched_ids.txt"
    audit_path = outputs_dir / "koios_pool_owner_history_fetch_audit.md"

    pool_ids = read_pool_ids(pool_list_path)
    completed_ids = read_completed_ids(fetched_ids_path)
    needs_header = not out_path.exists() or out_path.stat().st_size == 0

    with out_path.open("a", newline="") as csv_file, fetched_ids_path.open("a") as fetched_file:
        writer = csv.DictWriter(csv_file, fieldnames=OWNER_HISTORY_FIELDS)
        if needs_header:
            writer.writeheader()

        completed_pool_count = len(completed_ids)
        new_rows_written = 0
        for batch_count, batch_pool_ids, rows, _, _ in iter_batches(pool_ids, completed_ids):
            for row in rows:
                writer.writerow(row)
            csv_file.flush()
            for pool_id in batch_pool_ids:
                if pool_id not in completed_ids:
                    fetched_file.write(pool_id + "\n")
                    completed_ids.add(pool_id)
                    completed_pool_count += 1
            fetched_file.flush()
            new_rows_written += len(rows)
            if batch_count % 5 == 0 or completed_pool_count == len(pool_ids):
                print(
                    f"pool_owner_history progress: pools={completed_pool_count}/{len(pool_ids)} "
                    f"| new_rows={new_rows_written:,} | workers={MAX_WORKERS} | batch_size={BATCH_SIZE}"
                )

    row_count = 0
    min_epoch = None
    max_epoch = None
    with out_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            epoch_no = int(row["epoch_no"])
            min_epoch = epoch_no if min_epoch is None else min(min_epoch, epoch_no)
            max_epoch = epoch_no if max_epoch is None else max(max_epoch, epoch_no)

    write_audit(
        total_pools=len(pool_ids),
        completed_pools=len(completed_ids),
        row_count=row_count,
        min_epoch=min_epoch,
        max_epoch=max_epoch,
        out_path=audit_path,
    )

    print(f"Wrote: {out_path}")
    print(f"Wrote: {fetched_ids_path}")
    print(f"Wrote: {audit_path}")


if __name__ == "__main__":
    main()
