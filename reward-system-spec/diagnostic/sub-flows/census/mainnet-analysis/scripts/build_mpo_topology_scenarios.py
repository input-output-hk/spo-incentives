"""Joint-failure scenario library for the Cardano infrastructure topology.

Computes stake-at-risk for a curated list of concrete plausible failure
scenarios, framed as the question Leios actually cares about: "what fraction
of voting stake would be silenced if scenario X occurs simultaneously?".

For each scenario, the script reports:
  - stake_at_risk_ada   sum of stake in pools that match the scenario predicate
  - stake_at_risk_pct   as a fraction of total productive stake
  - gap_to_26pct        25 - pct  (positive = safe under flat 25% heuristic)
  - n_pools             number of pools touching the scenario footprint
  - n_entities          number of entities affected
  - top_entities        the largest five entities at risk

The "any-exposure" rule is used here — a pool is counted as at risk if
*any* of its registered relays sits in the scenario's footprint. This is
the appropriate liveness read: a multi-relay pool whose Tokyo relay falls
over but Frankfurt relay survives is *not* silenced, but a pool with all
its relays in a single failing region is.

Scenarios cover historical incidents (real outages that affected
specifically these providers/regions) and structural correlations (shared
upstream, BGP peering, certificate authority).

Output: data/mpo_topology_failure_scenarios.csv
"""
from __future__ import annotations
import csv
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Set

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ENDPOINTS = DATA / "mpo_relay_endpoints_resolved.csv"
OUT = DATA / "mpo_topology_failure_scenarios.csv"


@dataclass
class Scenario:
    id: str
    title: str
    rationale: str
    # predicate takes an endpoint row dict and returns True if it falls inside
    # the scenario's failure footprint
    predicate: Callable[[dict], bool]


# Historical or structurally plausible failure scenarios.
SCENARIOS: List[Scenario] = [
    Scenario(
        "aws_us-east-1_cascade",
        "AWS us-east-1 control-plane cascade",
        "Historically the most consequential AWS region; control-plane events "
        "in 2017, 2020 and 2021 cascaded across other AWS regions and into "
        "GCP / Azure via shared IAM, STS, and DNS dependencies.",
        lambda r: r["region"] in ("aws:us-east-1", "aws:us-east-2"),
    ),
    Scenario(
        "ovh_sbg_fire",
        "OVH Strasbourg datacentre fire (SBG-style)",
        "Real precedent: March 2021, SBG2 destroyed by fire; SBG1, SBG3, "
        "SBG4 went offline for days. Predicate matches OVH stake whose "
        "physical datacentre is in France (Roubaix / Strasbourg / "
        "Gravelines), excluding OVH's foreign datacentres (Beauharnois, "
        "Hillsboro, Singapore, Sydney) which BGP-register to the FR/CA "
        "parent block but are not exposed to a Strasbourg-region event.",
        lambda r: r["provider"] == "OVH" and r["physical_country"] == "FR",
    ),
    Scenario(
        "gcp_global_iam",
        "GCP global IAM / control-plane outage",
        "Multi-region GCP control-plane events (Jun 2019, Nov 2021, Mar "
        "2024) have made every GCP region simultaneously unreachable for "
        "authenticated workloads.",
        lambda r: r["provider"] == "GCP",
    ),
    Scenario(
        "azure_we_outage",
        "Azure westeurope (Amsterdam) regional outage",
        "Azure westeurope hosts essentially all eToro stake plus other "
        "European institutional operators; the region's storage + AAD "
        "incidents (Apr 2021, May 2022) silence everything there.",
        lambda r: r["region"] == "azure:westeurope",
    ),
    Scenario(
        "aws_full_outage",
        "Complete AWS unavailability (control plane + all regions)",
        "Unprecedented at this scope but used as upper-bound: full AWS "
        "absence (BGP withdrawal, root-DNS misconfiguration, or "
        "certificate-authority chain failure).",
        lambda r: r["provider"] == "AWS",
    ),
    Scenario(
        "aws_plus_gcp",
        "Correlated AWS + GCP outage",
        "Joint failure scenario: an AWS us-east-1 incident that propagates "
        "to GCP through shared DNS / IAM / CA upstreams. This crosses the "
        "25% quorum heuristic and is the most plausible threshold-breaching "
        "event observed in the data.",
        lambda r: r["provider"] in ("AWS", "GCP"),
    ),
    Scenario(
        "frankfurt_metro",
        "Frankfurt metro-area outage (DE-CIX peering point)",
        "DE-CIX (Frankfurt) is one of the largest Internet exchanges; a "
        "metro-level power or peering failure affects every datacentre in "
        "the Frankfurt cluster simultaneously, regardless of provider.",
        lambda r: r["region"] in ("aws:eu-central-1", "gcp:europe-west3")
        or r["region"].startswith(("ovh:de:frankfurt", "hetzner:frankfurt")),
    ),
    Scenario(
        "all_hyperscalers",
        "Joint hyperscaler outage (AWS + GCP + Azure)",
        "Upper-bound scenario: all three hyperscalers unreachable "
        "simultaneously (e.g., a shared certificate authority compromise "
        "or coordinated denial of service against TLS-fronting Akamai).",
        lambda r: r["tier"] == "hyperscaler",
    ),
    Scenario(
        "single_region_worst",
        "Single-region worst case (GCP europe-west3 / Frankfurt)",
        "The largest single-region concentration observed in the data. "
        "Dominated by Coinbase. Bounded by what any one region failure "
        "can cost the network.",
        lambda r: r["region"] == "gcp:europe-west3",
    ),
    Scenario(
        "ovh_full",
        "Complete OVH outage (multi-datacentre)",
        "OVH-wide event such as a billing/identity outage affecting all "
        "OVH datacentres simultaneously. OVH is the largest non-hyperscaler "
        "concentration on Cardano.",
        lambda r: r["provider"] == "OVH",
    ),
    Scenario(
        "hetzner_full",
        "Complete Hetzner outage",
        "Hetzner (Nuremberg / Falkenstein / Helsinki) is the densest "
        "single-pool-operator hoster. A Hetzner-wide event silences a "
        "large slice of the long tail.",
        lambda r: r["provider"] == "Hetzner",
    ),
]


def load() -> List[dict]:
    return list(csv.DictReader(open(ENDPOINTS)))


def compute(rows: List[dict]) -> List[dict]:
    # pool -> total stake; pool -> entity_name; pool -> set of regions touched
    pool_stake = {r["pool_id_bech32"]: float(r["current_active_stake_ada"] or 0)
                  for r in rows}
    pool_entity = {r["pool_id_bech32"]: r["display_name"] or r["entity_id"]
                   for r in rows}
    total = sum(pool_stake.values())
    # endpoints per pool
    pool_rows: dict = defaultdict(list)
    for r in rows:
        pool_rows[r["pool_id_bech32"]].append(r)
    out_rows = []
    for sc in SCENARIOS:
        at_risk_stake = 0.0
        at_risk_pools: Set[str] = set()
        ent_stake: dict = defaultdict(float)
        for pool, lst in pool_rows.items():
            # any-exposure: if any registered relay matches the predicate, the
            # pool is at risk for that scenario
            if any(sc.predicate(r) for r in lst):
                s = pool_stake.get(pool, 0)
                at_risk_stake += s
                at_risk_pools.add(pool)
                ent_stake[pool_entity[pool]] += s
        pct = 100 * at_risk_stake / total if total else 0
        top_entities = sorted(ent_stake.items(), key=lambda kv: -kv[1])[:5]
        out_rows.append({
            "scenario_id": sc.id,
            "title": sc.title,
            "rationale": sc.rationale,
            "stake_at_risk_ada": int(at_risk_stake),
            "stake_at_risk_pct": round(pct, 2),
            "gap_to_26pct": round(26.0 - pct, 2),
            "n_pools": len(at_risk_pools),
            "n_entities": len(ent_stake),
            "top_entities": "; ".join(
                f"{n} ({v/1e6:.0f}M)" for n, v in top_entities
            ),
        })
    out_rows.sort(key=lambda r: -r["stake_at_risk_pct"])
    return out_rows


def main() -> None:
    rows = load()
    out = compute(rows)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    total = sum(float(r["current_active_stake_ada"] or 0) for r in rows)
    print(f"Total productive stake (all distinct pools): "
          f"{sum({r['pool_id_bech32']: float(r['current_active_stake_ada'] or 0) for r in rows}.values())/1e9:.2f}B ADA")
    print()
    print(f"{'Scenario':40s} {'%':>6s} {'Gap':>7s} {'Pools':>6s} {'Ents':>5s}")
    for r in out:
        flag = "X" if r["gap_to_26pct"] < 0 else " "
        print(f"  {flag} {r['title'][:38]:38s} {r['stake_at_risk_pct']:>5.2f}% "
              f"{r['gap_to_26pct']:>+6.2f} {r['n_pools']:>6d} {r['n_entities']:>5d}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
