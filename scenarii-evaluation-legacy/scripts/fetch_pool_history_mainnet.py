#!/usr/bin/env python3
"""
Fetch Cardano mainnet pool history from Koios, from Shelley start to current tip.

The fetch is resumable:
- `koios_pool_list_mainnet.csv` stores the discovered pool universe.
- `koios_pool_history_mainnet.csv` is appended pool by pool.
- `koios_pool_history_fetched_ids.txt` records which pool ids were completed.

Outputs:
- scenarii-evaluation/data/koios_pool_list_mainnet.csv
- scenarii-evaluation/data/koios_pool_history_mainnet.csv
- scenarii-evaluation/data/koios_pool_history_fetched_ids.txt
- scenarii-evaluation/outputs/koios_pool_history_fetch_audit.md
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


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
PAGE_SIZE = 1000
SHELLEY_START_EPOCH = 208
REQUEST_DELAY_S = getenv_float("KOIOS_REQUEST_DELAY_S", 0.15)
MAX_WORKERS = max(1, getenv_int("KOIOS_MAX_WORKERS", 1))


POOL_LIST_FIELDS = [
    "pool_id_bech32",
    "pool_id_hex",
    "active_epoch_no",
    "margin",
    "fixed_cost",
    "pledge",
    "deposit",
    "reward_addr",
    "owners",
    "relays",
    "ticker",
    "pool_group",
    "meta_url",
    "meta_hash",
    "pool_status",
    "active_stake",
    "retiring_epoch",
]


POOL_HISTORY_FIELDS = [
    "pool_id_bech32",
    "epoch_no",
    "active_stake_lovelace",
    "active_stake_ada",
    "active_stake_pct",
    "saturation_pct",
    "block_cnt",
    "delegator_cnt",
    "margin_rate",
    "fixed_cost_lovelace",
    "fixed_cost_ada",
    "pool_fees_lovelace",
    "pool_fees_ada",
    "deleg_rewards_lovelace",
    "deleg_rewards_ada",
    "member_rewards_lovelace",
    "member_rewards_ada",
    "owner_member_rewards_lovelace",
    "owner_member_rewards_ada",
    "total_pool_rewards_lovelace",
    "total_pool_rewards_ada",
    "epoch_ros",
]


def fetch_json(url: str, *, method: str = "GET", body: Optional[bytes] = None, retries: int = 20) -> Any:
    for attempt in range(retries):
        try:
            headers = {"accept": "application/json", "content-type": "application/json"}
            token = os.getenv("KOIOS_BEARER_TOKEN") or os.getenv("KOIOS_API_TOKEN")
            if token:
                headers["authorization"] = f"Bearer {token}"
            req = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method=method,
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                sleep_s = 75 if exc.code == 429 else min(2 ** attempt, 30)
                print(f"Retrying {url} after HTTP {exc.code}; sleep {sleep_s}s", file=sys.stderr)
                time.sleep(sleep_s)
                continue
            raise
        except urllib.error.URLError:
            if attempt + 1 < retries:
                sleep_s = min(2 ** attempt, 30)
                time.sleep(sleep_s)
                continue
            raise


def lovelace_to_ada(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    return int(value) / 1_000_000.0


def fetch_pool_list() -> List[dict]:
    rows: List[dict] = []
    offset = 0
    while True:
        url = f"{KOIOS_BASE}/pool_list?offset={offset}&limit={PAGE_SIZE}"
        page = fetch_json(url)
        if not page:
            break
        rows.extend(page)
        print(f"pool_list page offset={offset} rows={len(page)}")
        if len(page) < PAGE_SIZE:
            break
        offset += len(page)
    return rows


def write_pool_list_csv(rows: List[dict], out_path: Path) -> None:
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=POOL_LIST_FIELDS)
        writer.writeheader()
        for row in rows:
            flat = {}
            for field in POOL_LIST_FIELDS:
                value = row.get(field)
                if isinstance(value, (list, dict)):
                    flat[field] = json.dumps(value, separators=(",", ":"))
                else:
                    flat[field] = value
            writer.writerow(flat)


def read_pool_list_csv(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {line.strip() for line in f if line.strip()}


def read_cached_tip_epoch(data_dir: Path) -> int | None:
    reward_epoch_path = data_dir / "reward_epoch_pools_mainnet.csv"
    if not reward_epoch_path.exists():
        return None
    max_epoch = None
    with reward_epoch_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch_no = int(row["epoch_no"])
            max_epoch = epoch_no if max_epoch is None else max(max_epoch, epoch_no)
    return max_epoch


def fetch_pool_history_rows(pool_id: str) -> tuple[List[dict], Optional[int], Optional[int]]:
    qs = urllib.parse.urlencode({"_pool_bech32": pool_id})
    rows = fetch_json(f"{KOIOS_BASE}/pool_history?{qs}")
    time.sleep(REQUEST_DELAY_S)
    min_epoch = None
    max_epoch = None
    output_rows: List[dict] = []
    for row in rows:
        epoch_no = int(row["epoch_no"])
        if epoch_no < SHELLEY_START_EPOCH:
            continue
        min_epoch = epoch_no if min_epoch is None else min(min_epoch, epoch_no)
        max_epoch = epoch_no if max_epoch is None else max(max_epoch, epoch_no)
        pool_fees_lovelace = row.get("pool_fees")
        deleg_rewards_lovelace = row.get("deleg_rewards")
        member_rewards_lovelace = row.get("member_rewards")
        owner_member_rewards_lovelace = None
        if deleg_rewards_lovelace is not None:
            if member_rewards_lovelace is None:
                owner_member_rewards_lovelace = int(deleg_rewards_lovelace)
            else:
                owner_member_rewards_lovelace = int(deleg_rewards_lovelace) - int(member_rewards_lovelace)

        total_pool_rewards_lovelace = None
        if pool_fees_lovelace is not None and deleg_rewards_lovelace is not None:
            total_pool_rewards_lovelace = int(pool_fees_lovelace) + int(deleg_rewards_lovelace)

        output_rows.append(
            {
                "pool_id_bech32": pool_id,
                "epoch_no": epoch_no,
                "active_stake_lovelace": row.get("active_stake"),
                "active_stake_ada": lovelace_to_ada(row.get("active_stake")),
                "active_stake_pct": row.get("active_stake_pct"),
                "saturation_pct": row.get("saturation_pct"),
                "block_cnt": row.get("block_cnt"),
                "delegator_cnt": row.get("delegator_cnt"),
                "margin_rate": row.get("margin"),
                "fixed_cost_lovelace": row.get("fixed_cost"),
                "fixed_cost_ada": lovelace_to_ada(row.get("fixed_cost")),
                "pool_fees_lovelace": pool_fees_lovelace,
                "pool_fees_ada": lovelace_to_ada(pool_fees_lovelace),
                "deleg_rewards_lovelace": deleg_rewards_lovelace,
                "deleg_rewards_ada": lovelace_to_ada(deleg_rewards_lovelace),
                "member_rewards_lovelace": member_rewards_lovelace,
                "member_rewards_ada": lovelace_to_ada(member_rewards_lovelace),
                "owner_member_rewards_lovelace": owner_member_rewards_lovelace,
                "owner_member_rewards_ada": None if owner_member_rewards_lovelace is None else owner_member_rewards_lovelace / 1_000_000.0,
                "total_pool_rewards_lovelace": total_pool_rewards_lovelace,
                "total_pool_rewards_ada": None if total_pool_rewards_lovelace is None else total_pool_rewards_lovelace / 1_000_000.0,
                "epoch_ros": row.get("epoch_ros"),
            }
        )
    return output_rows, min_epoch, max_epoch


def iter_pool_history_results(
    pool_ids: List[str],
    completed_ids: set[str],
) -> Iterable[tuple[int, str, List[dict], Optional[int], Optional[int]]]:
    remaining_pool_ids = [pool_id for pool_id in pool_ids if pool_id not in completed_ids]
    if MAX_WORKERS == 1 or len(remaining_pool_ids) <= 1:
        for done_count, pool_id in enumerate(remaining_pool_ids, start=1):
            pool_rows, min_epoch, max_epoch = fetch_pool_history_rows(pool_id)
            yield done_count, pool_id, pool_rows, min_epoch, max_epoch
        return

    worker_count = min(MAX_WORKERS, len(remaining_pool_ids))
    remaining_iter = iter(remaining_pool_ids)
    done_count = 0

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_pool_id = {}

        def submit_next() -> bool:
            try:
                pool_id = next(remaining_iter)
            except StopIteration:
                return False
            future = executor.submit(fetch_pool_history_rows, pool_id)
            future_to_pool_id[future] = pool_id
            return True

        for _ in range(worker_count):
            if not submit_next():
                break

        while future_to_pool_id:
            done_futures, _ = wait(future_to_pool_id, return_when=FIRST_COMPLETED)
            for future in done_futures:
                pool_id = future_to_pool_id.pop(future)
                pool_rows, min_epoch, max_epoch = future.result()
                done_count += 1
                yield done_count, pool_id, pool_rows, min_epoch, max_epoch
                submit_next()


def write_fetch_audit(
    *,
    tip_epoch: int,
    total_pools: int,
    completed_pools: int,
    history_rows_written: int,
    min_epoch: Optional[int],
    max_epoch: Optional[int],
    out_path: Path,
) -> None:
    lines = [
        "# Koios Pool History Fetch Audit",
        "",
        f"- Source: `{KOIOS_BASE}`",
        f"- Shelley start epoch used in filter: **{SHELLEY_START_EPOCH}**",
        f"- Tip epoch at fetch time: **{tip_epoch}**",
        f"- Pools discovered from `pool_list`: **{total_pools}**",
        f"- Pools completed in history fetch: **{completed_pools}**",
        f"- Pool-history rows written: **{history_rows_written:,}**",
        f"- Epoch range actually written: **{min_epoch}..{max_epoch}**",
        "",
        "## Notes",
        "- `pool_history` is fetched one pool at a time because Koios does not expose a global pool-history table.",
        "- The job is resumable through `koios_pool_history_fetched_ids.txt`.",
        "- `pool_fees + deleg_rewards = total_pool_rewards` in this exported dataset.",
        "- `owner_member_rewards = deleg_rewards - member_rewards` when `member_rewards` is available.",
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
    history_path = data_dir / "koios_pool_history_mainnet.csv"
    fetched_ids_path = data_dir / "koios_pool_history_fetched_ids.txt"
    audit_path = outputs_dir / "koios_pool_history_fetch_audit.md"

    tip_epoch = None
    try:
        tip = fetch_json(f"{KOIOS_BASE}/tip")[0]
        tip_epoch = int(tip["epoch_no"])
    except Exception:
        tip_epoch = read_cached_tip_epoch(data_dir)

    if pool_list_path.exists() and pool_list_path.stat().st_size > 0:
        pool_list_rows = read_pool_list_csv(pool_list_path)
    else:
        pool_list_rows = fetch_pool_list()
        write_pool_list_csv(pool_list_rows, pool_list_path)
    pool_ids = [row["pool_id_bech32"] for row in pool_list_rows]

    completed_ids = read_completed_ids(fetched_ids_path)
    needs_header = not history_path.exists()
    history_rows_written = 0
    min_epoch = None
    max_epoch = None

    with history_path.open("a", newline="") as csv_file, fetched_ids_path.open("a") as fetched_file:
        writer = csv.DictWriter(csv_file, fieldnames=POOL_HISTORY_FIELDS)
        if needs_header:
            writer.writeheader()

        total = len(pool_ids)
        completed_pool_count = len(completed_ids)
        for _, pool_id, pool_rows, pool_min_epoch, pool_max_epoch in iter_pool_history_results(pool_ids, completed_ids):
            for row in pool_rows:
                writer.writerow(row)
            csv_file.flush()
            fetched_file.write(pool_id + "\n")
            fetched_file.flush()
            completed_ids.add(pool_id)
            completed_pool_count += 1
            row_count = len(pool_rows)
            history_rows_written += row_count

            if row_count > 0:
                min_epoch = pool_min_epoch if min_epoch is None else min(min_epoch, pool_min_epoch)
                max_epoch = pool_max_epoch if max_epoch is None else max(max_epoch, pool_max_epoch)

            if completed_pool_count % 25 == 0 or completed_pool_count == total:
                print(
                    f"pool_history progress: {completed_pool_count}/{total} pools "
                    f"| wrote_rows={history_rows_written:,} | workers={MAX_WORKERS}"
                )

    # If the fetch was resumed, infer final row count and epoch range from the CSV.
    final_rows = 0
    final_min_epoch = None
    final_max_epoch = None
    with history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            final_rows += 1
            epoch_no = int(row["epoch_no"])
            final_min_epoch = epoch_no if final_min_epoch is None else min(final_min_epoch, epoch_no)
            final_max_epoch = epoch_no if final_max_epoch is None else max(final_max_epoch, epoch_no)

    write_fetch_audit(
        tip_epoch=-1 if tip_epoch is None else tip_epoch,
        total_pools=len(pool_ids),
        completed_pools=len(completed_ids),
        history_rows_written=final_rows,
        min_epoch=final_min_epoch,
        max_epoch=final_max_epoch,
        out_path=audit_path,
    )

    print(f"Wrote: {pool_list_path}")
    print(f"Wrote: {history_path}")
    print(f"Wrote: {fetched_ids_path}")
    print(f"Wrote: {audit_path}")


if __name__ == "__main__":
    main()
