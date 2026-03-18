#!/usr/bin/env python3
"""
Helpers for building a mainnet-derived engine input that separates:
- operator-side capital, grouped by attributed entity when available
- synthetic delegator cohorts for the remaining active stake
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


DELEGATOR_COHORT_SIZE_ADA = 10_000_000.0


@dataclass(frozen=True)
class PoolRow:
    pool_id: str
    active_stake_ada: float
    pledge_ada: float
    reward_addr: str
    owners: tuple[str, ...]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def spo_incentives_root() -> Path:
    return Path(__file__).resolve().parents[2]


def engine_root() -> Path:
    return workspace_root() / "Rewards-Sharing-Simulation-Engine"


def koios_pool_list_path() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "data" / "koios_pool_list_mainnet.csv"


def mpo_pool_mapping_path() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "outputs" / "mpo_entity_pool_mapping_mainnet.csv"


def owner_history_path() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "data" / "koios_pool_owner_history_mainnet.csv"


def stake_distribution_path(agent_count: int) -> Path:
    return engine_root() / f"synthetic-stake-distribution-{agent_count}-agents.csv"


def input_summary_json_path() -> Path:
    return (
        spo_incentives_root()
        / "scenarii-evaluation"
        / "outputs"
        / "mainnet_entity_owner_capital_input_summary.json"
    )


def input_operator_csv_path() -> Path:
    return (
        spo_incentives_root()
        / "scenarii-evaluation"
        / "outputs"
        / "mainnet_entity_owner_capital_operator_groups.csv"
    )


def load_registered_positive_pools() -> dict[str, PoolRow]:
    pools: dict[str, PoolRow] = {}
    with koios_pool_list_path().open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["pool_status"] != "registered" or float(row["active_stake"] or 0) <= 0:
                continue
            owners = tuple(sorted(set(json.loads(row["owners"]) if row["owners"] else [])))
            pools[row["pool_id_bech32"]] = PoolRow(
                pool_id=row["pool_id_bech32"],
                active_stake_ada=float(row["active_stake"]) / 1_000_000.0,
                pledge_ada=float(row["pledge"] or 0) / 1_000_000.0,
                reward_addr=str(row["reward_addr"] or ""),
                owners=owners,
            )
    return pools


def load_entity_ids_for_current_pools(current_pool_ids: set[str]) -> dict[str, str]:
    entity_by_pool: dict[str, str] = {}
    with mpo_pool_mapping_path().open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            pool_id = row["pool_id_bech32"]
            if pool_id in current_pool_ids:
                entity_by_pool[pool_id] = row["entity_id"]
    return entity_by_pool


def load_latest_owner_rows(current_pool_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    latest_epoch_by_pool: dict[str, int] = {}
    latest_rows_by_pool: dict[str, list[dict[str, str]]] = defaultdict(list)
    with owner_history_path().open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            pool_id = row["pool_id_bech32"]
            if pool_id not in current_pool_ids:
                continue
            epoch_no = int(row["epoch_no"])
            latest_epoch = latest_epoch_by_pool.get(pool_id)
            if latest_epoch is None or epoch_no > latest_epoch:
                latest_epoch_by_pool[pool_id] = epoch_no
                latest_rows_by_pool[pool_id] = [row]
            elif epoch_no == latest_epoch:
                latest_rows_by_pool[pool_id].append(row)
    return latest_rows_by_pool


def build_group_keys(
    pools: dict[str, PoolRow], entity_by_pool: dict[str, str]
) -> tuple[dict[str, tuple[str, str]], int]:
    keys: dict[str, tuple[str, str]] = {}
    for pool_id, pool in pools.items():
        if pool_id in entity_by_pool:
            keys[pool_id] = ("entity", entity_by_pool[pool_id])
        elif pool.reward_addr:
            keys[pool_id] = ("reward", pool.reward_addr)
        else:
            keys[pool_id] = ("pool", pool_id)

    grouped_by_reward = Counter(keys.values())
    reward_grouped_pools = 0
    for pool_id, group_key in list(keys.items()):
        if group_key[0] == "reward" and grouped_by_reward[group_key] == 1:
            keys[pool_id] = ("pool", pool_id)
        elif group_key[0] == "reward":
            reward_grouped_pools += 1

    return keys, reward_grouped_pools


def pool_owner_capital_ada(latest_owner_rows: list[dict[str, str]], pledge_ada: float) -> float:
    owner_capital = sum(float(row["owner_active_stake_ada"] or 0) for row in latest_owner_rows)
    return max(owner_capital, pledge_ada)


def build_input_snapshot(cohort_size_ada: float = DELEGATOR_COHORT_SIZE_ADA) -> dict[str, object]:
    pools = load_registered_positive_pools()
    entity_by_pool = load_entity_ids_for_current_pools(set(pools))
    latest_owner_rows = load_latest_owner_rows(set(pools))
    group_key_by_pool, reward_grouped_pools = build_group_keys(pools, entity_by_pool)

    pools_by_group: dict[tuple[str, str], list[str]] = defaultdict(list)
    for pool_id, group_key in group_key_by_pool.items():
        pools_by_group[group_key].append(pool_id)

    operator_rows: list[dict[str, object]] = []
    operator_stakes_ada: list[float] = []
    total_active_stake_ada = sum(pool.active_stake_ada for pool in pools.values())
    owner_snapshot_pool_count = 0

    for group_key, pool_ids in sorted(pools_by_group.items()):
        unique_owner_stakes: dict[str, float] = {}
        declared_pledge_ada = 0.0
        group_active_stake_ada = 0.0
        owner_snapshot_rows = 0

        for pool_id in pool_ids:
            pool = pools[pool_id]
            declared_pledge_ada += pool.pledge_ada
            group_active_stake_ada += pool.active_stake_ada
            rows = latest_owner_rows.get(pool_id, [])
            if rows:
                owner_snapshot_pool_count += 1
                owner_snapshot_rows += 1
            for row in rows:
                stake_address = row["stake_address"]
                owner_stake_ada = float(row["owner_active_stake_ada"] or 0)
                if owner_stake_ada > unique_owner_stakes.get(stake_address, 0.0):
                    unique_owner_stakes[stake_address] = owner_stake_ada

        observed_owner_capital_ada = sum(unique_owner_stakes.values())
        operator_capital_ada = min(
            group_active_stake_ada,
            max(observed_owner_capital_ada, declared_pledge_ada),
        )

        if operator_capital_ada > 0:
            operator_rows.append(
                {
                    "group_kind": group_key[0],
                    "group_id": group_key[1],
                    "pool_count": len(pool_ids),
                    "group_active_stake_ada": round(group_active_stake_ada, 6),
                    "observed_owner_capital_ada": round(observed_owner_capital_ada, 6),
                    "declared_pledge_ada": round(declared_pledge_ada, 6),
                    "operator_capital_ada": round(operator_capital_ada, 6),
                    "owner_snapshot_pool_count": owner_snapshot_rows,
                }
            )
            operator_stakes_ada.append(operator_capital_ada)

    total_operator_capital_ada = sum(operator_stakes_ada)
    public_delegation_ada = max(0.0, total_active_stake_ada - total_operator_capital_ada)

    delegator_cohort_stakes_ada: list[float] = []
    remaining = public_delegation_ada
    while remaining > 1e-9:
        cohort = min(cohort_size_ada, remaining)
        delegator_cohort_stakes_ada.append(cohort)
        remaining -= cohort

    stake_values_ada = sorted(operator_stakes_ada + delegator_cohort_stakes_ada, reverse=True)

    return {
        "stake_values_ada": stake_values_ada,
        "operator_rows": sorted(
            operator_rows,
            key=lambda row: (-float(row["operator_capital_ada"]), -int(row["pool_count"]), str(row["group_id"])),
        ),
        "positive_registered_pools": len(pools),
        "mapped_entity_pools": len(entity_by_pool),
        "entity_group_count": len({group_id for kind, group_id in pools_by_group if kind == "entity"}),
        "reward_grouped_pools": reward_grouped_pools,
        "operator_group_count": len(operator_stakes_ada),
        "owner_snapshot_pool_count": owner_snapshot_pool_count,
        "delegator_cohort_count": len(delegator_cohort_stakes_ada),
        "delegator_cohort_size_ada": cohort_size_ada,
        "operator_capital_ada": total_operator_capital_ada,
        "public_delegation_ada": public_delegation_ada,
        "active_stake_ada": total_active_stake_ada,
    }


def write_input_files(cohort_size_ada: float = DELEGATOR_COHORT_SIZE_ADA) -> dict[str, object]:
    snapshot = build_input_snapshot(cohort_size_ada=cohort_size_ada)

    agent_count = len(snapshot["stake_values_ada"])
    stake_path = stake_distribution_path(agent_count)
    with stake_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for stake_ada in snapshot["stake_values_ada"]:
            writer.writerow([f"{stake_ada * 1_000_000:.0f}"])

    operator_path = input_operator_csv_path()
    operator_path.parent.mkdir(parents=True, exist_ok=True)
    operator_rows = snapshot["operator_rows"]
    with operator_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(operator_rows[0].keys()))
        writer.writeheader()
        writer.writerows(operator_rows)

    summary = dict(snapshot)
    summary.pop("stake_values_ada")
    summary.pop("operator_rows")
    summary["agent_count"] = agent_count
    summary["output_path"] = str(stake_path)
    summary["operator_csv_path"] = str(operator_path)
    summary_path = input_summary_json_path()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
