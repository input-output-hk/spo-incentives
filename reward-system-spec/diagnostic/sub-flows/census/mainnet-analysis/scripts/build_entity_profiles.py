#!/usr/bin/env python3
"""Build per-entity profile cards from the reward-split snapshot.

Reads:
    ../../sub-flows/operator-delegator-distribution/mainnet-analysis/data/reward_split_snapshot.csv
    ../../sub-flows/pools-distribution/mainnet-analysis/data/mpo_entity_archetypes.csv

Writes:
    ../data/entity_profile_hollow_competitive.csv
    (one row per entity in the hollow × competitive cell)
"""

import pathlib
import pandas as pd
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent          # census/mainnet-analysis/
OD_DATA = ROOT.parent.parent / "operator-delegator-distribution" / "mainnet-analysis" / "data"
ENTITY_DATA = ROOT / "data"                                    # entity data (local)
OUT = ROOT / "data"


def margin_band(m: float) -> str:
    if m == 0:
        return "subsidised"
    elif m <= 0.05:
        return "competitive"
    elif m < 0.99:
        return "additional-services"
    else:
        return "privatisation"


def main():
    df = pd.read_csv(OD_DATA / "reward_split_snapshot.csv")
    df["margin_band"] = df["margin_rate"].apply(margin_band)

    # Load archetypes if available
    arch_path = ENTITY_DATA / "mpo_entity_archetypes.csv"
    if arch_path.exists():
        arch = pd.read_csv(arch_path)
        # Normalise join key
        if "entity_id" in arch.columns:
            arch = arch.rename(columns={"entity_id": "eff_entity_id"})
    else:
        arch = pd.DataFrame()

    # Filter hollow × competitive
    hc = df[(df["pool_class"] == "hollow") & (df["margin_band"] == "competitive")].copy()

    # Entity-level aggregation
    ent = hc.groupby("eff_entity_id").agg(
        display_name=("display_name", "first"),
        pools=("pool_id_bech32", "count"),
        stake_ada=("active_stake_ada", "sum"),
        delegator_cnt=("delegator_cnt", "sum"),
        op_take_ada=("operator_take_ada", "sum"),
        fc_ada=("effective_fixed_cost_ada", "sum"),
        margin_ada=("margin_take_ada", "sum"),
        reward_ada=("total_pool_rewards_ada", "sum"),
        median_margin=("margin_rate", "median"),
        is_mpo=("is_mpo", "first"),
        pledge_tags=("pledge_tag", lambda x: "|".join(sorted(x.dropna().unique().astype(str)))),
    ).reset_index()

    # Derived columns
    ent["ada_per_delegator"] = (ent["stake_ada"] / ent["delegator_cnt"]).round(0)
    ent["op_take_pct"] = (ent["op_take_ada"] / ent["reward_ada"] * 100).round(1)
    ent["fc_share_pct"] = (ent["fc_ada"] / ent["reward_ada"] * 100).round(1)
    ent["margin_share_pct"] = (ent["margin_ada"] / ent["reward_ada"] * 100).round(1)
    ent["cell_stake_share_pct"] = (ent["stake_ada"] / ent["stake_ada"].sum() * 100).round(2)
    ent["custodial_signal"] = ent["ada_per_delegator"] >= 1_000_000

    # Join archetypes
    if not arch.empty and "eff_entity_id" in arch.columns:
        cols = ["eff_entity_id"]
        if "archetype" in arch.columns:
            cols.append("archetype")
        if "sub_type" in arch.columns:
            cols.append("sub_type")
        if "reasoning" in arch.columns:
            cols.append("reasoning")
        ent = ent.merge(arch[cols], on="eff_entity_id", how="left")

    ent = ent.sort_values("stake_ada", ascending=False)

    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / "entity_profile_hollow_competitive.csv"
    ent.to_csv(out_path, index=False)
    print(f"Wrote {len(ent)} entities to {out_path}")

    # Print top 15 summary
    print(f"\n{'Entity':30s} {'Pools':>5} {'Stake(M)':>9} {'Deleg':>8} {'ADA/d':>10} {'Custodial':>9}")
    for _, r in ent.head(15).iterrows():
        name = str(r["display_name"])[:30] if pd.notna(r["display_name"]) else r["eff_entity_id"][:25]
        ad = f"{r['ada_per_delegator']/1e6:.1f}M" if r["ada_per_delegator"] >= 1e6 else f"{r['ada_per_delegator']/1e3:.0f}K"
        print(f"{name:30s} {r['pools']:>5.0f} {r['stake_ada']/1e6:>9.0f} {r['delegator_cnt']:>8,.0f} {ad:>10s} {'YES' if r['custodial_signal'] else '':>9s}")


if __name__ == "__main__":
    main()
