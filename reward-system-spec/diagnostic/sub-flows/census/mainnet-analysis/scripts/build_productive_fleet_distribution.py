#!/usr/bin/env python3
"""build_productive_fleet_distribution.py

Recompute mpo_fleet_distribution.csv using ONLY productive pools
(stake >= 3M ADA at epoch 623, the 95%-block-probability threshold from
POL.O3.F1).

Definitions
-----------
n-MPO              count of *productive* (>=3M ADA) pools an entity controls.
strict multi-pool  entity with n-MPO >= 2 (i.e., 2 or more productive pools).
attributed
single-pool        entity attributed by off-chain signals that has only ONE
                   productive pool — even if it owns additional sub-threshold
                   pools. The fleet may be larger on paper, but only one pool
                   is economically active, so the entity is *not* a strict
                   multi-pool operator.

Inputs:
- data/mpo_entity_pool_mapping_mainnet.csv  (pool -> entity)
- data/pool_stake_623.csv                   (pool -> stake at epoch 623)

Outputs:
- data/mpo_fleet_distribution.csv           (productive-only fleet buckets)
- data/mpo_attributed_single_pool_detail.csv (12 attributed single-pool
                                              entities, with sub-threshold
                                              pool counts so the 71 vs 12
                                              boundary is auditable)

The fleet-size buckets follow §3.4.2 convention:
  1 (attributed single-pool operator): exactly 1 productive pool
  2-3, 4-5, 6-10, 11-20, 21+: count of productive pools per entity
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

DATA = Path(__file__).resolve().parent.parent / "data"

PRODUCTION_THRESHOLD_ADA = 3_000_000  # POL.O3.F1 — 95% block probability


def load_pool_stake() -> dict[str, float]:
    out: dict[str, float] = {}
    with open(DATA / "pool_stake_623.csv") as f:
        for r in csv.DictReader(f):
            out[r["pool_id"]] = float(r["total_ada"])
    return out


def load_pool_to_entity() -> dict[str, str]:
    out: dict[str, str] = {}
    with open(DATA / "mpo_entity_pool_mapping_mainnet.csv") as f:
        for r in csv.DictReader(f):
            pool = r["pool_id_bech32"]
            ent = r["entity_id"]
            if pool and ent:
                out[pool] = ent
    return out


def load_pool_delegations() -> dict[str, int]:
    out: dict[str, int] = {}
    with open(DATA / "pool_stake_623.csv") as f:
        for r in csv.DictReader(f):
            out[r["pool_id"]] = int(r["delegation_count"])
    return out


def bucket_for(n: int) -> str:
    if n == 1:
        return "1 (attributed SPO)"
    if n <= 3:
        return "2-3"
    if n <= 5:
        return "4-5"
    if n <= 10:
        return "6-10"
    if n <= 20:
        return "11-20"
    return "21+"


def main() -> None:
    pool_stake = load_pool_stake()
    pool_to_entity = load_pool_to_entity()
    pool_delegations = load_pool_delegations()

    # ── Step 1 — total fleet (every named pool, productive or not) ──────
    entity_all_pools: dict[str, list[str]] = defaultdict(list)
    for pool, ent in pool_to_entity.items():
        if pool in pool_stake:  # only pools observed at epoch 623
            entity_all_pools[ent].append(pool)

    # ── Step 2 — productive-only fleet ──────────────────────────────────
    productive_pools = {
        p: s for p, s in pool_stake.items() if s >= PRODUCTION_THRESHOLD_ADA
    }
    print(f"Productive pools (>= 3M): {len(productive_pools)}")

    entity_productive_pools: dict[str, list[str]] = defaultdict(list)
    for pool, ent in pool_to_entity.items():
        if pool in productive_pools:
            entity_productive_pools[ent].append(pool)

    # Drop entities with zero productive pools (they leave the productive set)
    entity_productive_pools = {e: ps for e, ps in entity_productive_pools.items() if ps}
    print(f"Entities with >= 1 productive pool: {len(entity_productive_pools)}")

    # ── Step 3 — per-entity counts + stakes ─────────────────────────────
    per_entity = {
        e: {
            "n_mpo": len(ps),  # productive pool count → drives the bucket
            "n_total_owned": len(entity_all_pools.get(e, [])),
            "stake_productive": sum(pool_stake[p] for p in ps),
            "delegations_productive": sum(pool_delegations[p] for p in ps),
        }
        for e, ps in entity_productive_pools.items()
    }

    # ── Step 4 — strict-multi-pool vs attributed-single-pool split ──────
    # An entity is **strict multi-pool** iff n-MPO >= 2 (i.e. 2+ productive
    # pools). An entity with several owned pools but only 1 productive pool
    # is classified as **attributed single-pool** — it does NOT count as
    # multi-pool because the rest of the fleet is sub-threshold and
    # economically inactive.
    strict_mp = {e: i for e, i in per_entity.items() if i["n_mpo"] >= 2}
    attr_sp = {e: i for e, i in per_entity.items() if i["n_mpo"] == 1}

    print(f"\n  Strict multi-pool (n-MPO >= 2): {len(strict_mp)}")
    print(f"  Attributed single-pool (n-MPO = 1): {len(attr_sp)}")
    print(f"  Total attributed: {len(strict_mp) + len(attr_sp)}")

    # ── Step 5 — bucket aggregation ─────────────────────────────────────
    buckets: dict[str, dict[str, float]] = defaultdict(
        lambda: {"entities": 0, "pools": 0, "total_stake_ada": 0.0, "delegations": 0}
    )
    for e, info in per_entity.items():
        b = bucket_for(info["n_mpo"])
        buckets[b]["entities"] += 1
        buckets[b]["pools"] += info["n_mpo"]
        buckets[b]["total_stake_ada"] += info["stake_productive"]
        buckets[b]["delegations"] += info["delegations_productive"]

    bucket_order = ["1 (attributed SPO)", "2-3", "4-5", "6-10", "11-20", "21+"]

    # ── Step 6 — write fleet distribution ───────────────────────────────
    out_path = DATA / "mpo_fleet_distribution.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fleet_size", "entities", "pools", "total_stake_ada", "delegations"])
        for b in bucket_order:
            row = buckets.get(b)
            if not row:
                continue
            w.writerow([
                b,
                int(row["entities"]),
                int(row["pools"]),
                f"{row['total_stake_ada']:.0f}",
                int(row["delegations"]),
            ])
    print(f"\nWrote {out_path}")

    # ── Step 7 — write attributed-single-pool detail (auditable) ────────
    detail_path = DATA / "mpo_attributed_single_pool_detail.csv"
    with open(detail_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "entity_id",
            "n_productive_pools",
            "n_total_owned_pools",
            "n_sub_threshold_pools",
            "productive_stake_ada",
        ])
        for e, info in sorted(attr_sp.items(), key=lambda x: -x[1]["stake_productive"]):
            sub = info["n_total_owned"] - info["n_mpo"]
            w.writerow([
                e,
                info["n_mpo"],
                info["n_total_owned"],
                sub,
                f"{info['stake_productive']:.0f}",
            ])
    print(f"Wrote {detail_path}")

    # ── Print summary ───────────────────────────────────────────────────
    total_entities = sum(b["entities"] for b in buckets.values())
    total_pools = sum(b["pools"] for b in buckets.values())
    total_stake = sum(b["total_stake_ada"] for b in buckets.values())
    print(f"\nSummary:")
    print(f"  Total attributed entities (productive set): {total_entities}")
    print(f"  Total productive pools attributed: {total_pools}")
    print(f"  Total stake: {total_stake / 1e9:.2f}B ADA")
    for b in bucket_order:
        row = buckets.get(b)
        if row:
            print(
                f"  {b:<22} entities={int(row['entities']):>3} "
                f"pools={int(row['pools']):>4} stake={row['total_stake_ada']/1e9:>5.2f}B"
            )

    # Sanity: how many sub-threshold pools do the 12 attributed-SP entities
    # collectively own? This is the population that *looks* like multi-pool
    # on paper but only has 1 productive pool.
    extra_sub_pools = sum(
        info["n_total_owned"] - info["n_mpo"] for info in attr_sp.values()
    )
    print(f"\n  Of the {len(attr_sp)} attributed single-pool entities:")
    print(f"    They own {sum(i['n_total_owned'] for i in attr_sp.values())} pools total")
    print(f"    but only {sum(i['n_mpo'] for i in attr_sp.values())} are productive")
    print(f"    The remaining {extra_sub_pools} are sub-threshold (< 3M ADA)")


if __name__ == "__main__":
    main()
