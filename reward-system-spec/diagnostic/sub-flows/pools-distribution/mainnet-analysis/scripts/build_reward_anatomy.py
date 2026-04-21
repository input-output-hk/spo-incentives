#!/usr/bin/env python3
"""
Compute per-pool reward envelope efficiency and aggregate waste decomposition.

For each pool with stake, computes:
  - ν (saturation level)
  - π (pledge normalised)
  - A(π,ν) (pledge activation)
  - E(π,ν) = λ_min·ν + λ_max·A  (proportioning envelope)
  - Contribution to aggregate efficiency

Outputs:
  - data/reward_anatomy.json      (aggregate decomposition)
  - data/reward_anatomy.md        (human-readable summary)
  - data/pool_envelope_detail.csv (per-pool values for top pools)

Data sources:
  - data/koios_pool_list_mainnet.csv
  - data/reward_epoch_pools_mainnet.csv
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPORT_DIR / "data"
OUT_DIR = REPORT_DIR / "data"


# ---------------------------------------------------------------------------
# Pool record
# ---------------------------------------------------------------------------

@dataclass
class Pool:
    pool_id: str
    ticker: str
    active_stake: float   # ADA
    pledge: float         # ADA
    fixed_cost: float     # ADA
    margin: float


def parse_float(v, default=0.0):
    if v is None:
        return default
    v = str(v).strip()
    return float(v) if v else default


def load_pools(path):
    pools = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("pool_status", "") != "registered":
                continue
            stake = parse_float(r.get("active_stake")) / 1e6  # lovelace->ADA
            if stake <= 0:
                continue
            pools.append(Pool(
                pool_id=r["pool_id_bech32"],
                ticker=r.get("ticker", ""),
                active_stake=stake,
                pledge=parse_float(r.get("pledge")) / 1e6,
                fixed_cost=parse_float(r.get("fixed_cost", "0")) / 1e6,
                margin=parse_float(r.get("margin", "0")),
            ))
    return pools


def load_protocol_params(path):
    last = None
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            last = r
    if last is None:
        raise RuntimeError("Empty epoch file")
    return {
        "k": int(parse_float(last.get("k_optimal_pool_count"))),
        "a0": parse_float(last.get("a0_influence")),
        "supply": parse_float(last.get("Supply_ada")),
        "epoch": int(parse_float(last.get("epoch_no"))),
    }


def load_pools_pot(path):
    """Return the latest epoch's pools pot (ADA) where data is complete."""
    last_with_data = None
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rw = r.get("Reward_epoch_pools_ada", "").strip()
            if rw:
                last_with_data = r
    if last_with_data is None:
        raise RuntimeError("No epoch with reward data")
    return {
        "epoch": int(parse_float(last_with_data["epoch_no"])),
        "pools_pot_ada": parse_float(last_with_data["Reward_epoch_pools_ada"]),
        "reserve_ada": parse_float(last_with_data.get("Reserve_ada")),
        "supply_ada": parse_float(last_with_data.get("Supply_ada")),
        "rho": parse_float(last_with_data.get("rho_monetary_expand_rate")),
        "tau": parse_float(last_with_data.get("tau_treasury_growth_rate")),
        "fee_ada": parse_float(last_with_data.get("Fee_epoch_ada")),
        "active_stake_ada": parse_float(last_with_data.get("active_stake_ada")),
        "blk_count": int(parse_float(last_with_data.get("blk_count_epoch"))),
    }


# ---------------------------------------------------------------------------
# Envelope computation
# ---------------------------------------------------------------------------

def pledge_activation(pi, nu):
    """A(π, ν) = πν - π²(1-ν)"""
    return pi * nu - pi**2 * (1 - nu)


def envelope(pi, nu, lam_min, lam_max):
    """E(π,ν) = λ_min·min(ν,1) + λ_max·A(min(π,1), min(ν,1))"""
    nu_c = min(nu, 1.0)
    pi_c = min(pi, nu_c)  # physical constraint π ≤ ν
    A = pledge_activation(pi_c, nu_c)
    base = lam_min * nu_c
    bonus = lam_max * A
    return base, bonus, base + bonus


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pools = load_pools(DATA_DIR / "koios_pool_list_mainnet.csv")
    params = load_protocol_params(DATA_DIR / "reward_epoch_pools_mainnet.csv")
    pot_data = load_pools_pot(DATA_DIR / "reward_epoch_pools_mainnet.csv")

    k = params["k"]
    a0 = params["a0"]
    supply = params["supply"]
    z0 = supply / k

    lam_min = 1.0 / (1.0 + a0)
    lam_max = a0 / (1.0 + a0)

    # Compute the theoretical pools pot (before per-pool distribution)
    # R_theoretical = (1-τ)(ρ×Reserve + fees)
    rho = pot_data["rho"]
    tau = pot_data["tau"]
    reserve = pot_data["reserve_ada"]
    fees = pot_data["fee_ada"]
    expansion = reserve * rho
    total_pot = expansion + fees
    treasury_cut = total_pot * tau
    R_theoretical = total_pot - treasury_cut

    # η network-level = blk_count / expected_blocks
    blk_count = pot_data["blk_count"]
    expected_blocks = 21600  # L × f for mainnet
    eta_network = blk_count / expected_blocks

    # The actual pools pot input to the formula
    R = R_theoretical * eta_network
    P_max = R / k

    # The actual distributed amount (from CSV)
    distributed = pot_data["pools_pot_ada"]

    print(f"Epoch: {pot_data['epoch']}")
    print(f"R_theoretical (pre-η): {R_theoretical:,.0f} ADA")
    print(f"η_network: {eta_network:.4f} ({blk_count}/{expected_blocks})")
    print(f"R (pools pot, post-η): {R:,.0f} ADA")
    print(f"P_max = R/k: {P_max:,.0f} ADA")
    print(f"Distributed (from CSV): {distributed:,.0f} ADA")
    print(f"Distribution efficiency: {distributed/R*100:.1f}%")
    print()

    # Per-pool envelope computation
    total_stake = sum(p.active_stake for p in pools)
    sum_nu = total_stake / z0
    sum_base = 0.0
    sum_bonus = 0.0
    sum_E = 0.0

    pool_details = []
    for p in pools:
        nu = p.active_stake / z0
        pi = p.pledge / z0
        base_i, bonus_i, E_i = envelope(pi, nu, lam_min, lam_max)
        sum_base += base_i
        sum_bonus += bonus_i
        sum_E += E_i
        pool_details.append({
            "pool_id": p.pool_id,
            "ticker": p.ticker,
            "stake_ada": p.active_stake,
            "pledge_ada": p.pledge,
            "nu": nu,
            "pi": pi,
            "A": pledge_activation(min(pi, min(nu, 1.0)), min(nu, 1.0)),
            "base": base_i,
            "bonus": bonus_i,
            "E": E_i,
            "reward_at_pbar1": P_max * E_i,
        })

    # Sort by E descending
    pool_details.sort(key=lambda x: x["E"], reverse=True)

    # Aggregate decomposition
    agg_base_pct = sum_base / k * 100
    agg_bonus_pct = sum_bonus / k * 100
    agg_E_pct = sum_E / k * 100
    eff_with_perf = distributed / R * 100

    # Theoretical max with same stake but optimal distribution
    # If all stake were in ceil(total_stake/z0) pools, each at z0 (last one partial)
    n_full = int(total_stake // z0)
    remainder = (total_stake % z0) / z0
    optimal_base = lam_min * (n_full * 1.0 + remainder)
    optimal_bonus_zero_pledge = 0  # no pledge assumed
    optimal_E_zero_pledge = optimal_base / k * 100

    print(f"Aggregate envelope analysis:")
    print(f"  Σν = {sum_nu:.1f} (saturation units)")
    print(f"  Σ base / k = {agg_base_pct:.2f}%")
    print(f"  Σ bonus / k = {agg_bonus_pct:.2f}%")
    print(f"  Σ E / k = {agg_E_pct:.2f}% (envelope efficiency)")
    print(f"  With performance: {eff_with_perf:.1f}% (actual distributed / R)")
    print(f"  Performance waste: {agg_E_pct - eff_with_perf:.2f}%")
    print()
    print(f"  Optimal (same stake, perfect redistribution, zero pledge):")
    print(f"    {n_full} full pools + 1 at {remainder:.2f}ν")
    print(f"    Base efficiency = {optimal_E_zero_pledge:.2f}%")
    print()

    # Decompose the waste
    total_waste_pct = 100.0 - eff_with_perf
    # Participation waste: what's lost because Σν < k
    participation_waste = (1.0 - sum_nu / k) * lam_min * 100
    # Proportioning waste within staked: suboptimal pool structure
    # = (optimal base at this participation) - (actual base)
    # Optimal base at this participation = lam_min * min(sum_nu, k) / k
    # But sum_nu < k, so = lam_min * sum_nu / k = agg_base_pct
    # The base is already "optimal" for the current participation given that
    # Σ lam_min * νi = lam_min * Σνi regardless of how pools are distributed.
    # The waste within staked comes from:
    #   a) Pools above saturation (ν capped at 1) losing excess stake
    #   b) The bonus being near zero
    #   c) Performance < 1

    # More precisely:
    # If all stake were in perfectly sized pools (each at ν=1):
    # sum_base_optimal = lam_min * sum_nu (same as actual, since base is linear in ν)
    # sum_bonus_optimal = lam_max * sum(A(ν,ν)) for each pool
    # With zero pledge: bonus = 0
    # With max pledge (π=ν=1 for n_full pools): bonus = lam_max * n_full

    # The base is linear in ν → pool structure doesn't matter for base!
    # Only capping at ν=1 matters (oversaturated pools lose)
    oversaturated = [d for d in pool_details if d["nu"] > 1.0]
    excess_stake = sum(d["nu"] - 1.0 for d in oversaturated) * z0
    base_lost_to_cap = lam_min * sum(d["nu"] - 1.0 for d in oversaturated) / k * 100

    print(f"Waste decomposition:")
    print(f"  Total waste: {total_waste_pct:.1f}%")
    print(f"  Participation gap (Σν < k): {participation_waste:.1f}%")
    print(f"  Saturation cap loss ({len(oversaturated)} oversaturated pools): {base_lost_to_cap:.2f}%")
    print(f"  Pledge shortfall (bonus actual vs theoretical): {agg_bonus_pct:.2f}% captured")
    print(f"    Max possible bonus at this participation: {lam_max * sum_nu / k * 100:.2f}% (if all π=ν)")
    print(f"    Bonus gap: {(lam_max * sum_nu / k * 100) - agg_bonus_pct:.2f}%")
    perf_waste = agg_E_pct - eff_with_perf
    print(f"  Performance loss: {perf_waste:.2f}%")

    # Write JSON
    anatomy = {
        "epoch": pot_data["epoch"],
        "R_theoretical_ada": R_theoretical,
        "eta_network": eta_network,
        "R_pools_pot_ada": R,
        "P_max_ada": P_max,
        "distributed_ada": distributed,
        "distribution_efficiency_pct": eff_with_perf,
        "k": k,
        "a0": a0,
        "z0_ada": z0,
        "lambda_min": lam_min,
        "lambda_max": lam_max,
        "sum_nu": sum_nu,
        "sum_base_over_k_pct": agg_base_pct,
        "sum_bonus_over_k_pct": agg_bonus_pct,
        "sum_E_over_k_pct": agg_E_pct,
        "participation_waste_pct": participation_waste,
        "base_lost_to_cap_pct": base_lost_to_cap,
        "oversaturated_pools": len(oversaturated),
        "performance_waste_pct": perf_waste,
        "n_pools_with_stake": len(pools),
        "total_active_stake_ada": total_stake,
    }
    with (OUT_DIR / "reward_anatomy.json").open("w") as f:
        json.dump(anatomy, f, indent=2)
    print(f"\n[OK] {OUT_DIR / 'reward_anatomy.json'}")

    # Write human-readable MD
    with (OUT_DIR / "reward_anatomy.md").open("w") as f:
        f.write(f"# Reward Formula Anatomy — Epoch {pot_data['epoch']}\n\n")
        f.write(f"| Metric | Value |\n| --- | --- |\n")
        f.write(f"| Pools pot R (post-η) | **{R:,.0f} ADA** |\n")
        f.write(f"| P_max = R/{k} | **{P_max:,.0f} ADA** |\n")
        f.write(f"| Distributed | **{distributed:,.0f} ADA** ({eff_with_perf:.1f}%) |\n")
        f.write(f"| η_network | {eta_network:.4f} |\n")
        f.write(f"| Σν (saturation units) | {sum_nu:.1f} / {k} |\n")
        f.write(f"| Σ base / k | {agg_base_pct:.2f}% |\n")
        f.write(f"| Σ bonus / k | {agg_bonus_pct:.3f}% |\n")
        f.write(f"| Envelope efficiency Σ E / k | {agg_E_pct:.2f}% |\n")
        f.write(f"\n### Waste decomposition\n\n")
        f.write(f"| Source | Waste (% of pot) |\n| --- | --- |\n")
        f.write(f"| Participation gap | {participation_waste:.1f}% |\n")
        f.write(f"| Saturation cap loss | {base_lost_to_cap:.2f}% |\n")
        f.write(f"| Pledge shortfall | {(lam_max * sum_nu / k * 100) - agg_bonus_pct:.2f}% |\n")
        f.write(f"| Performance loss | {perf_waste:.2f}% |\n")
        f.write(f"| **Total waste** | **{total_waste_pct:.1f}%** |\n")
    print(f"[OK] {OUT_DIR / 'reward_anatomy.md'}")

    # Write per-pool CSV (top 100 by E)
    csv_path = OUT_DIR / "pool_envelope_detail.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pool_id", "ticker", "stake_ada", "pledge_ada",
                         "nu", "pi", "A", "base", "bonus", "E",
                         "reward_at_pbar1_ada"])
        for d in pool_details[:200]:
            writer.writerow([
                d["pool_id"], d["ticker"],
                f"{d['stake_ada']:.0f}", f"{d['pledge_ada']:.0f}",
                f"{d['nu']:.6f}", f"{d['pi']:.6f}",
                f"{d['A']:.6f}", f"{d['base']:.6f}",
                f"{d['bonus']:.6f}", f"{d['E']:.6f}",
                f"{d['reward_at_pbar1']:.0f}",
            ])
    print(f"[OK] {csv_path}")


if __name__ == "__main__":
    main()
