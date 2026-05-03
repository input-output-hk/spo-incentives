#!/usr/bin/env python3
"""
Compute all key metrics for the Pools Distribution sub-report.

Reads the canonical scenarii-evaluation data and outputs:
  - data/pool_distribution_snapshot.md   (human-readable summary)
  - data/pool_distribution_snapshot.json (machine-readable, for README regeneration)

Data sources (relative to scenarii-evaluation/data/):
  - koios_pool_list_mainnet.csv          (current pool snapshot)
  - pool_reward_pool_summary_mainnet.csv (reward distribution)
  - reward_epoch_pools_mainnet.csv       (protocol parameters)
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import median
from typing import List, Optional


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
OUT_DIR = REPORT_DIR / "data"


# ---------------------------------------------------------------------------
# Pool record
# ---------------------------------------------------------------------------

@dataclass
class Pool:
    pool_id: str
    status: str
    active_stake: float  # ADA
    pledge: float  # ADA
    margin: float
    fixed_cost: float  # ADA


def parse_float(v: str | None, default: float = 0.0) -> float:
    if v is None:
        return default
    v = v.strip()
    return float(v) if v else default


def load_pools(path: Path) -> List[Pool]:
    pools: List[Pool] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            pools.append(Pool(
                pool_id=r["pool_id_bech32"],
                status=r.get("pool_status", ""),
                active_stake=parse_float(r.get("active_stake")) / 1e6,  # lovelace -> ADA
                pledge=parse_float(r.get("pledge")) / 1e6,
                margin=parse_float(r.get("margin", "0")),
                fixed_cost=parse_float(r.get("fixed_cost", "0")) / 1e6,
            ))
    return pools


# ---------------------------------------------------------------------------
# Protocol parameters from latest epoch
# ---------------------------------------------------------------------------

def load_protocol_params(path: Path) -> dict:
    """Return k, a0, supply from the latest epoch row."""
    last = None
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            last = r
    if last is None:
        raise RuntimeError("Empty epoch file")
    return {
        "k": int(parse_float(last.get("k_optimal_pool_count"))),
        "a0": parse_float(last.get("a0_influence")),
        "supply": parse_float(last.get("Supply_ada")),
        "epoch": int(parse_float(last.get("epoch_no"))),
    }


# ---------------------------------------------------------------------------
# Pledge bonus computation
# ---------------------------------------------------------------------------

def pledge_bonus_pct(pledge: float, stake: float, z0: float, a0: float) -> float:
    """Return the pledge bonus as a % over base reward."""
    if stake <= 0 or z0 <= 0:
        return 0.0
    nu = min(stake / z0, 1.0)
    pi = min(pledge / z0, 1.0)
    lam_min = 1.0 / (1.0 + a0)
    lam_max = a0 / (1.0 + a0)
    base = lam_min * nu
    if base <= 0:
        return 0.0
    A = pi * nu - pi ** 2 * (1.0 - nu)
    bonus = lam_max * A
    return bonus / base * 100.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    pools = load_pools(DATA_DIR / "koios_pool_list_mainnet.csv")
    params = load_protocol_params(DATA_DIR / "reward_epoch_pools_mainnet.csv")

    k = params["k"]
    a0 = params["a0"]
    supply = params["supply"]
    epoch = params["epoch"]
    z0 = supply / k

    # Filter
    registered = [p for p in pools if p.status == "registered"]
    with_stake = [p for p in registered if p.active_stake > 0]
    viability = 3_000_000  # 3M ADA
    healthy = [p for p in with_stake if p.active_stake >= viability]
    below_healthy_floor = [p for p in with_stake if p.active_stake < viability]

    # Saturation stats
    near_sat_80 = [p for p in with_stake if p.active_stake >= z0 * 0.80]
    saturated = [p for p in with_stake if p.active_stake >= z0]
    over_sat = [p for p in with_stake if p.active_stake > z0]

    total_stake = sum(p.active_stake for p in with_stake)
    healthy_stake = sum(p.active_stake for p in healthy)
    theoretical_capacity = k * z0
    utilisation = total_stake / theoretical_capacity if theoretical_capacity > 0 else 0
    max_sat = int(total_stake / z0) if z0 > 0 else 0
    inactive = supply - total_stake

    # Pledge bands
    pledge_bands = {
        "zero": 0,
        "micro_lt10k": 0,
        "low_10k_100k": 0,
        "modest_100k_1M": 0,
        "material_1M_10M": 0,
        "high_gte10M": 0,
    }
    for p in with_stake:
        if p.pledge == 0:
            pledge_bands["zero"] += 1
        elif p.pledge < 10_000:
            pledge_bands["micro_lt10k"] += 1
        elif p.pledge < 100_000:
            pledge_bands["low_10k_100k"] += 1
        elif p.pledge < 1_000_000:
            pledge_bands["modest_100k_1M"] += 1
        elif p.pledge < 10_000_000:
            pledge_bands["material_1M_10M"] += 1
        else:
            pledge_bands["high_gte10M"] += 1

    below_100k = pledge_bands["zero"] + pledge_bands["micro_lt10k"] + pledge_bands["low_10k_100k"]

    # Pledge bonus distribution for healthy pools
    bonuses = []
    for p in healthy:
        b = pledge_bonus_pct(p.pledge, p.active_stake, z0, a0)
        bonuses.append(b)
    bonuses.sort()
    n = len(bonuses)

    bonus_stats = {
        "median": bonuses[n // 2] if n else 0,
        "p25": bonuses[n // 4] if n else 0,
        "p75": bonuses[3 * n // 4] if n else 0,
        "p90": bonuses[int(n * 0.9)] if n else 0,
        "p99": bonuses[int(n * 0.99)] if n else 0,
        "max": bonuses[-1] if n else 0,
        "gt_0_1_pct": sum(1 for b in bonuses if b > 0.1),
        "gt_1_pct": sum(1 for b in bonuses if b > 1),
        "gt_5_pct": sum(1 for b in bonuses if b > 5),
        "gt_10_pct": sum(1 for b in bonuses if b > 10),
    }

    # Pledge/stake ratio for healthy pools
    ratios = [p.pledge / p.active_stake * 100 for p in healthy if p.active_stake > 0]
    ratios.sort()
    median_ratio = ratios[len(ratios) // 2] if ratios else 0

    # Assemble snapshot
    snapshot = {
        "epoch": epoch,
        "supply_ada": supply,
        "k": k,
        "a0": a0,
        "z0_ada": z0,
        "registered_pools": len(registered),
        "pools_with_stake": len(with_stake),
        "healthy_pools": len(healthy),
        "healthy_stake_ada": healthy_stake,
        "healthy_stake_pct": healthy_stake / total_stake * 100 if total_stake > 0 else 0,
        "below_healthy_floor_pools": len(below_healthy_floor),
        "below_healthy_floor_stake_pct": (total_stake - healthy_stake) / total_stake * 100 if total_stake > 0 else 0,
        "near_sat_80_pools": len(near_sat_80),
        "saturated_pools": len(saturated),
        "oversaturated_pools": len(over_sat),
        "total_active_stake_ada": total_stake,
        "theoretical_capacity_ada": theoretical_capacity,
        "utilisation_pct": utilisation * 100,
        "max_saturable_pools": max_sat,
        "inactive_stake_ada": inactive,
        "inactive_stake_pct": inactive / supply * 100 if supply > 0 else 0,
        "pledge_bands": pledge_bands,
        "pools_below_100k_pledge": below_100k,
        "pools_below_100k_pledge_pct": below_100k / len(with_stake) * 100 if with_stake else 0,
        "median_pledge_stake_ratio_pct": median_ratio,
        "pledge_bonus_stats_healthy": bonus_stats,
    }

    # Write JSON
    json_path = OUT_DIR / "pool_distribution_snapshot.json"
    with json_path.open("w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"[OK] {json_path}")

    # Write human-readable summary
    md_path = OUT_DIR / "pool_distribution_snapshot.md"
    with md_path.open("w") as f:
        f.write(f"# Pool Distribution Snapshot — Epoch {epoch}\n\n")
        f.write(f"| Metric | Value |\n| --- | --- |\n")
        f.write(f"| Circulating supply | **{supply / 1e9:.2f}B ADA** |\n")
        f.write(f"| Active stake | **{total_stake / 1e9:.2f}B ADA** ({utilisation * 100:.1f}% of capacity) |\n")
        f.write(f"| Protocol k | **{k}** |\n")
        f.write(f"| Saturation point z₀ | **{z0 / 1e6:.2f}M ADA** |\n")
        f.write(f"| Pledge influence a₀ | **{a0}** |\n")
        f.write(f"| Registered pools | **{len(registered):,}** |\n")
        f.write(f"| Pools with stake | **{len(with_stake):,}** |\n")
        f.write(f"| Healthy pools (≥3M) | **{len(healthy)}** (carry {healthy_stake / total_stake * 100:.1f}% of stake) |\n")
        f.write(f"| Below healthy floor (<3M) | **{len(below_healthy_floor):,}** |\n")
        f.write(f"| Near-saturation (≥80% z₀) | **{len(near_sat_80)}** |\n")
        f.write(f"| At/above saturation | **{len(saturated)}** |\n")
        f.write(f"| Max saturable pools | **{max_sat}** |\n")
        f.write(f"| Inactive stake | **{inactive / 1e9:.2f}B ADA** ({inactive / supply * 100:.1f}% of supply) |\n")
        f.write(f"\n### Pledge bands (pools with stake)\n\n")
        f.write(f"| Band | Pools | % |\n| --- | --- | --- |\n")
        band_labels = [
            ("Zero (0 ADA)", "zero"),
            ("Micro (<10K)", "micro_lt10k"),
            ("Low (10K–100K)", "low_10k_100k"),
            ("Modest (100K–1M)", "modest_100k_1M"),
            ("Material (1M–10M)", "material_1M_10M"),
            ("High (≥10M)", "high_gte10M"),
        ]
        for label, key in band_labels:
            cnt = pledge_bands[key]
            pct = cnt / len(with_stake) * 100 if with_stake else 0
            f.write(f"| {label} | {cnt} | {pct:.1f}% |\n")
        f.write(f"\n### Pledge bonus (healthy pools)\n\n")
        f.write(f"| Stat | Value |\n| --- | --- |\n")
        f.write(f"| Median bonus | {bonus_stats['median']:.4f}% |\n")
        f.write(f"| P75 | {bonus_stats['p75']:.4f}% |\n")
        f.write(f"| P90 | {bonus_stats['p90']:.4f}% |\n")
        f.write(f"| Pools with bonus > 1% | {bonus_stats['gt_1_pct']} / {n} |\n")
        f.write(f"| Pools with bonus > 5% | {bonus_stats['gt_5_pct']} / {n} |\n")
        f.write(f"| Median pledge/stake ratio | {median_ratio:.2f}% |\n")
    print(f"[OK] {md_path}")


if __name__ == "__main__":
    main()
