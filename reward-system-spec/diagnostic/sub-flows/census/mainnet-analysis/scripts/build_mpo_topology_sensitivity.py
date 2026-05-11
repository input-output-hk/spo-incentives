"""Sensitivity analysis + entity profile diff for the MPO topology pass.

Outputs (under data/):
  mpo_topology_sensitivity.csv         — same headline metrics under three
                                         stake-attribution rules so the
                                         reader can see if conclusions move
  mpo_topology_entity_profile_diff.csv — for every MPO entity, the observed
                                         provider mix + dominant-provider
                                         share + diversity index

Rules compared:
  even-split   (current default) — pool stake split evenly across distinct
                                   (provider, region) labels its relays expose
  majority     — entire pool stake assigned to the most frequent
                 (provider, region) label among its relays (ties broken
                 alphabetically); each pool counts once
  any-exposure — pool stake counted for *every* distinct label it touches;
                 totals can sum >100% — useful for "how much stake is at
                 risk if X goes down"
"""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ENDPOINTS = DATA / "mpo_relay_endpoints_resolved.csv"
OUT_SENSITIVITY = DATA / "mpo_topology_sensitivity.csv"
OUT_PROFILE_DIFF = DATA / "mpo_topology_entity_profile_diff.csv"


def load() -> list:
    return list(csv.DictReader(open(ENDPOINTS)))


def stake_per_pool(rows: list) -> dict:
    return {r["pool_id_bech32"]: float(r["current_active_stake_ada"] or 0) for r in rows}


def pool_keys(rows: list, key: str) -> dict:
    out = defaultdict(list)  # pool -> list of labels (with repetition for majority)
    for r in rows:
        out[r["pool_id_bech32"]].append(r[key])
    return out


def aggregate(rows: list, key: str, rule: str) -> Counter:
    stake = stake_per_pool(rows)
    keys = pool_keys(rows, key)
    out: Counter = Counter()
    for pool, lab_list in keys.items():
        s = stake.get(pool, 0)
        if not lab_list:
            continue
        if rule == "even-split":
            distinct = set(lab_list)
            per = s / len(distinct)
            for k in distinct:
                out[k] += per
        elif rule == "majority":
            c = Counter(lab_list)
            top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            out[top] += s
        elif rule == "any-exposure":
            for k in set(lab_list):
                out[k] += s
    return out


def write_sensitivity(rows: list) -> None:
    total = sum(stake_per_pool(rows).values())
    # focus on headline categories: tier, provider, top regions
    keys_to_compare = [
        ("tier", "Hyperscaler vs commodity vs residential"),
        ("provider", "Single-provider exposure"),
        ("region", "Region exposure (AWS / GCP / Azure / OVH cities)"),
    ]
    with OUT_SENSITIVITY.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "key", "even_split_pct", "majority_pct", "any_exposure_pct"])
        for dim, _label in keys_to_compare:
            agg = {
                rule: aggregate(rows, dim, rule)
                for rule in ("even-split", "majority", "any-exposure")
            }
            # universe of keys to compare = union, sorted by even-split desc
            keys = sorted(agg["even-split"].keys(), key=lambda k: -agg["even-split"][k])
            keys = [k for k in keys if agg["even-split"][k] / total >= 0.005]
            for k in keys:
                w.writerow([
                    dim, k,
                    f"{100 * agg['even-split'][k]/total:.3f}",
                    f"{100 * agg['majority'][k]/total:.3f}",
                    f"{100 * agg['any-exposure'][k]/total:.3f}",
                ])
    print(f"wrote {OUT_SENSITIVITY.relative_to(ROOT)}")


def shannon_diversity(counter: Counter) -> float:
    import math
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for v in counter.values():
        if v <= 0:
            continue
        p = v / total
        h -= p * math.log(p)
    return h


def write_profile_diff(rows: list) -> None:
    """Per-entity provider mix, dominant share, diversity (Shannon H, in nats)."""
    # entity -> { pool -> {providers} }
    ent_pools: dict = defaultdict(lambda: defaultdict(set))
    ent_meta: dict = {}
    ent_regions: dict = defaultdict(lambda: defaultdict(set))
    stake = stake_per_pool(rows)
    for r in rows:
        ent_pools[r["entity_id"]][r["pool_id_bech32"]].add(r["provider"])
        ent_regions[r["entity_id"]][r["pool_id_bech32"]].add(r["region"])
        ent_meta[r["entity_id"]] = {
            "display_name": r["display_name"], "category": r["category"],
        }
    out = []
    for eid, pools in ent_pools.items():
        prov_share: Counter = Counter()
        reg_share: Counter = Counter()
        total = 0.0
        for pool, provs in pools.items():
            s = stake.get(pool, 0)
            total += s
            if not provs:
                continue
            per = s / len(provs)
            for p in provs:
                prov_share[p] += per
        for pool, regs in ent_regions[eid].items():
            s = stake.get(pool, 0)
            if not regs:
                continue
            per = s / len(regs)
            for rg in regs:
                reg_share[rg] += per
        if not prov_share or total <= 0:
            continue
        top_prov, top_prov_s = prov_share.most_common(1)[0]
        top_reg, top_reg_s = reg_share.most_common(1)[0]
        h_prov = shannon_diversity(prov_share)
        h_reg = shannon_diversity(reg_share)
        out.append({
            "entity_id": eid,
            "display_name": ent_meta[eid]["display_name"],
            "category": ent_meta[eid]["category"],
            "pools": len(pools),
            "stake_ada": round(total),
            "dominant_provider": top_prov,
            "dominant_provider_share": f"{100*top_prov_s/total:.1f}" if total else "0.0",
            "dominant_region": top_reg,
            "dominant_region_share": f"{100*top_reg_s/total:.1f}" if total else "0.0",
            "n_providers": len(prov_share),
            "n_regions": len(reg_share),
            "provider_diversity_H": f"{h_prov:.3f}",
            "region_diversity_H": f"{h_reg:.3f}",
            "provider_mix": "; ".join(
                f"{p}={100*v/total:.0f}%" for p, v in prov_share.most_common(5)
            ),
        })
    # sort by stake desc
    out.sort(key=lambda r: -r["stake_ada"])
    with OUT_PROFILE_DIFF.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {OUT_PROFILE_DIFF.relative_to(ROOT)}  ({len(out)} entities)")


def main() -> None:
    rows = load()
    write_sensitivity(rows)
    write_profile_diff(rows)


if __name__ == "__main__":
    main()
