#!/usr/bin/env python3
"""
Operator / Delegator Reward Distribution — Profiling & Snapshot Export.

Analyses the THIRD stage of the reward pipeline: how each pool's total
reward (hat_f) is split between operator and delegators via the intra-pool
reward-sharing formula:

    operator_take  = min(c, ĥ) + m · max(ĥ − c, 0)   [fixed cost + margin]
    delegator_pot  = (1 − m) · max(ĥ − c, 0)          [pro-rata by stake]

Key design choices:
  - Three strategies along the Hollow–Private pledge spectrum
    (upstream §2.4.2):
      HOLLOW   — owner_stake / active_stake <  10 %  (delegation-dependent)
      BALANCED — 10 % ≤ ratio < 95 %                (genuine skin-in-the-game)
      PRIVATE  — ratio ≥ 95 %                       (operator-funded)
    Each pool is assigned a strategy by owner-stake ratio.
    Each entity is assigned a DOMINANT strategy (by stake weight).
    98.7% of entities apply a single pure strategy across all their pools.
  - Fee-policy analysis uses ENTITY-level grouping: an entity that runs
    41 pools at 3% margin is one policy decision, not 41.
  - On-chain pool_fees_ada is used as ground-truth for operator take.
  - The snapshot epoch is second-to-last (guaranteed settled).

Produces:
  1. reward_split_snapshot.csv          — per-pool reward decomposition
  2. reward_split_timeseries.csv        — epoch-level aggregates (all / hollow / balanced / private)
  3. reward_split_summary.json          — headline statistics + entity strategy consistency
  4. margin_fixed_cost_history.csv      — fee-parameter evolution
  5. entity_fee_policies.csv            — entity-level fee-policy summary (non-private)
  6. entity_strategy_summary.csv        — entity-level strategy assignment with consistency

Data source (read from the pools-distribution sister flow):
  - koios_pool_history_mainnet.csv
  - koios_pool_list_mainnet.csv
  - koios_pool_owner_history_mainnet.csv
  - mpo_entity_pool_mapping_mainnet.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
POOLS_DATA = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "pools-distribution" / "mainnet-analysis" / "data"
)
REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"

HOLLOW_OWNER_THRESHOLD  = 0.10   # owner_stake / active_stake <  10% → hollow strategy
PRIVATE_OWNER_THRESHOLD = 0.95   # owner_stake / active_stake >= 95% → private strategy
# Between 10% and 95% → balanced strategy

PRODUCTION_THRESHOLD_ADA = 3_000_000  # 3M ADA — 95% probability of ≥1 block per
                                       # epoch (λ=3 — see POL.O3.F1 in pools-distribution).


def load_pool_history():
    """Load full pool history with reward-split columns."""
    cols = [
        "pool_id_bech32", "epoch_no", "active_stake_ada",
        "saturation_pct", "block_cnt", "delegator_cnt",
        "margin_rate", "fixed_cost_ada",
        "pool_fees_ada", "deleg_rewards_ada",
        "member_rewards_ada", "owner_member_rewards_ada",
        "total_pool_rewards_ada", "epoch_ros",
    ]
    df = pd.read_csv(
        POOLS_DATA / "koios_pool_history_mainnet.csv",
        usecols=cols, dtype={"pool_id_bech32": str},
    )
    all_epochs = sorted(df["epoch_no"].unique())
    snapshot_epoch = all_epochs[-2]
    print(f"  pool_history: {len(df):,} rows, snapshot epoch {snapshot_epoch} "
          f"(latest in data: {all_epochs[-1]})")
    return df, snapshot_epoch


def load_owner_history_full():
    """Load full owner history — grouped by (pool, epoch)."""
    df = pd.read_csv(
        POOLS_DATA / "koios_pool_owner_history_mainnet.csv",
        usecols=["pool_id_bech32", "epoch_no", "owner_active_stake_ada"],
        dtype={"pool_id_bech32": str},
    )
    grouped = (
        df.groupby(["pool_id_bech32", "epoch_no"])["owner_active_stake_ada"]
        .sum()
        .reset_index()
        .rename(columns={"owner_active_stake_ada": "owner_stake_ada"})
    )
    print(f"  owner_history: {len(grouped):,} pool-epochs "
          f"({df['epoch_no'].nunique()} epochs)")
    return grouped


def load_owner_snapshot(owner_full, epoch):
    """Extract single-epoch snapshot from the full owner history."""
    snap = (
        owner_full[owner_full["epoch_no"] == epoch]
        .drop(columns=["epoch_no"])
        .copy()
    )
    print(f"  owner_snapshot: {len(snap):,} pools at epoch {epoch}")
    return snap


def load_upstream_health():
    """Load pool health metadata from the upstream pools-distribution flow."""
    path = POOLS_DATA / "mpo_entity_pool_health_mainnet.csv"
    if not path.exists():
        print("  upstream_health: not found, skipping")
        return pd.DataFrame()
    cols = ["pool_id_bech32", "pledge_tag", "category",
            "declared_pledge_ada", "health_tag_current"]
    df = pd.read_csv(path, usecols=cols, dtype={"pool_id_bech32": str})
    df = df.drop_duplicates("pool_id_bech32")
    print(f"  upstream_health: {len(df):,} pools")
    return df


def load_pool_list():
    df = pd.read_csv(
        POOLS_DATA / "koios_pool_list_mainnet.csv",
        usecols=["pool_id_bech32", "ticker", "pool_status", "pool_group"],
        dtype=str,
    )
    print(f"  pool_list: {len(df):,} pools")
    return df


def load_entity_mapping():
    path = POOLS_DATA / "mpo_entity_pool_mapping_mainnet.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str)
    print(f"  entity_mapping: {len(df):,} entity-pool pairs")
    return df


# ── Snapshot (latest epoch) ──────────────────────────────────────────────

def build_snapshot(hist, latest, owner_snap, pool_list, entity_map,
                   upstream_health=None):
    """Per-pool reward-split decomposition at latest epoch."""
    snap = hist[hist["epoch_no"] == latest].copy()
    snap = snap[snap["total_pool_rewards_ada"] > 0].copy()
    # Filter out sub-block-threshold pools (main report §2.4.1.5)
    n_before = len(snap)
    snap = snap[snap["active_stake_ada"] >= PRODUCTION_THRESHOLD_ADA].copy()
    n_after = len(snap)
    if n_before != n_after:
        print(f"  production-threshold filter: {n_before} → {n_after} pools "
              f"(dropped {n_before - n_after} below {PRODUCTION_THRESHOLD_ADA/1e6:.0f}M ADA)")

    # Merge owner stake
    snap = snap.merge(owner_snap, on="pool_id_bech32", how="left")
    snap["owner_stake_ada"] = snap["owner_stake_ada"].fillna(0)

    # Merge pool metadata
    snap = snap.merge(
        pool_list[["pool_id_bech32", "ticker", "pool_group"]],
        on="pool_id_bech32", how="left",
    )

    # Entity mapping
    if not entity_map.empty and "entity_id" in entity_map.columns:
        ent = entity_map[["pool_id_bech32", "entity_id", "display_name"]].drop_duplicates("pool_id_bech32")
        snap = snap.merge(ent, on="pool_id_bech32", how="left")
    else:
        snap["entity_id"] = pd.NA
        snap["display_name"] = pd.NA

    snap["is_mpo"] = snap["entity_id"].notna()

    # Merge upstream health metadata (pledge_tag, category)
    if upstream_health is not None and not upstream_health.empty:
        snap = snap.merge(
            upstream_health[["pool_id_bech32", "pledge_tag", "category",
                             "declared_pledge_ada", "health_tag_current"]],
            on="pool_id_bech32", how="left",
        )
    else:
        for col in ["pledge_tag", "category", "declared_pledge_ada",
                     "health_tag_current"]:
            snap[col] = pd.NA

    # ── Three-way classification (per-pool, owner-stake ratio) ──
    snap["owner_stake_ratio"] = np.where(
        snap["active_stake_ada"] > 0,
        snap["owner_stake_ada"] / snap["active_stake_ada"],
        0,
    )
    snap["pool_class"] = np.where(
        snap["owner_stake_ratio"] >= PRIVATE_OWNER_THRESHOLD, "private",
        np.where(snap["owner_stake_ratio"] < HOLLOW_OWNER_THRESHOLD,
                 "hollow", "balanced"),
    )
    # Backward compat
    snap["is_private"] = snap["pool_class"] == "private"

    # ── Derived reward-split columns ──
    hat_f = snap["total_pool_rewards_ada"]
    c     = snap["fixed_cost_ada"]
    m     = snap["margin_rate"]

    snap["operator_take_ada"] = snap["pool_fees_ada"]
    snap["effective_fixed_cost_ada"] = np.minimum(c, hat_f)
    snap["margin_take_ada"] = m * np.maximum(hat_f - c, 0)
    snap["delegator_pot_ada"] = hat_f - snap["operator_take_ada"]

    snap["operator_take_pct"] = np.where(
        hat_f > 0, snap["operator_take_ada"] / hat_f * 100, 0
    )
    snap["fixed_cost_pct_of_reward"] = np.where(
        hat_f > 0, snap["effective_fixed_cost_ada"] / hat_f * 100, 0
    )
    snap["margin_pct_of_reward"] = np.where(
        hat_f > 0, snap["margin_take_ada"] / hat_f * 100, 0
    )

    delegated = (snap["active_stake_ada"] - snap["owner_stake_ada"]).clip(lower=0)
    snap["delegated_stake_ada"] = delegated
    snap["deleg_yield_per_epoch_pct"] = np.where(
        delegated > 0, snap["delegator_pot_ada"] / delegated * 100, 0,
    )

    snap["operator_total_income_ada"] = (
        snap["operator_take_ada"] + snap["owner_member_rewards_ada"]
    )
    snap["effective_tax_pct"] = snap["operator_take_pct"]

    # Effective entity id (for entity-level grouping)
    snap["eff_entity_id"] = snap["entity_id"].fillna(snap["pool_id_bech32"])

    return snap


# ── Entity-level fee policies (public pools only) ───────────────────────

def build_entity_policies(snap):
    """Compute entity-level fee-policy summary for non-private pools."""
    pub = snap[snap["pool_class"] != "private"].copy()

    def _agg(grp):
        margins = sorted(grp["margin_rate"].unique())
        costs = sorted(grp["fixed_cost_ada"].unique())
        stake = grp["active_stake_ada"].sum()
        sw_margin = (
            np.average(grp["margin_rate"], weights=grp["active_stake_ada"])
            if stake > 0 else 0
        )
        return pd.Series({
            "display_name": grp["display_name"].iloc[0],
            "pool_count": len(grp),
            "is_mpo": grp["is_mpo"].iloc[0],
            "margin_values": "|".join(f"{m:.4f}" for m in margins),
            "n_distinct_margins": len(margins),
            "fixed_cost_values": "|".join(f"{c:.0f}" for c in costs),
            "n_distinct_costs": len(costs),
            "stake_weighted_margin": round(sw_margin, 6),
            "total_active_stake_ada": round(stake, 2),
            "total_rewards_ada": round(grp["total_pool_rewards_ada"].sum(), 2),
            "total_operator_take_ada": round(grp["operator_take_ada"].sum(), 2),
            "total_margin_take_ada": round(grp["margin_take_ada"].sum(), 2),
            "total_fixed_cost_ada": round(grp["effective_fixed_cost_ada"].sum(), 2),
            "total_delegator_pot_ada": round(grp["delegator_pot_ada"].sum(), 2),
        })

    ent = pub.groupby("eff_entity_id").apply(_agg).reset_index()
    ent.rename(columns={"eff_entity_id": "entity_id"}, inplace=True)
    ent.sort_values("total_active_stake_ada", ascending=False, inplace=True)
    return ent


# ── Timeseries (epoch-level aggregates) ──────────────────────────────────

def build_timeseries(hist, owner_full):
    """Epoch-level aggregates — total, hollow, mixed, and private."""
    active = hist[hist["total_pool_rewards_ada"] > 0].copy()
    # Apply production-threshold filter (main report §2.4.1.5)
    active = active[active["active_stake_ada"] >= PRODUCTION_THRESHOLD_ADA].copy()

    hat_f = active["total_pool_rewards_ada"]
    c     = active["fixed_cost_ada"]
    m     = active["margin_rate"]

    active["operator_take_ada"] = active["pool_fees_ada"]
    active["effective_fixed_cost_ada"] = np.minimum(c, hat_f)
    active["margin_take_ada"] = m * np.maximum(hat_f - c, 0)
    active["delegator_pot_ada"] = hat_f - active["operator_take_ada"]

    # Owner-ratio classification per pool per epoch
    active = active.merge(
        owner_full, on=["pool_id_bech32", "epoch_no"], how="left",
    )
    active["owner_stake_ada"] = active["owner_stake_ada"].fillna(0)
    active["owner_stake_ratio"] = np.where(
        active["active_stake_ada"] > 0,
        active["owner_stake_ada"] / active["active_stake_ada"],
        0,
    )
    active["pool_class"] = np.where(
        active["owner_stake_ratio"] >= PRIVATE_OWNER_THRESHOLD, "private",
        np.where(active["owner_stake_ratio"] < HOLLOW_OWNER_THRESHOLD,
                 "hollow", "balanced"),
    )

    def _epoch_agg(sub, prefix=""):
        agg = (
            sub.groupby("epoch_no")
            .agg(
                pool_count=("pool_id_bech32", "nunique"),
                total_rewards_ada=("total_pool_rewards_ada", "sum"),
                total_operator_take_ada=("operator_take_ada", "sum"),
                total_fixed_cost_ada=("effective_fixed_cost_ada", "sum"),
                total_margin_take_ada=("margin_take_ada", "sum"),
                total_delegator_pot_ada=("delegator_pot_ada", "sum"),
                total_active_stake_ada=("active_stake_ada", "sum"),
                mean_margin_rate=("margin_rate", "mean"),
                median_margin_rate=("margin_rate", "median"),
                stake_weighted_margin=("margin_rate", lambda x: np.average(
                    x, weights=sub.loc[x.index, "active_stake_ada"].clip(lower=1)
                )),
            )
            .reset_index()
        )
        agg["operator_take_pct"] = (
            agg["total_operator_take_ada"] / agg["total_rewards_ada"] * 100
        )
        agg["fixed_cost_share_pct"] = (
            agg["total_fixed_cost_ada"] / agg["total_rewards_ada"] * 100
        )
        agg["margin_share_pct"] = (
            agg["total_margin_take_ada"] / agg["total_rewards_ada"] * 100
        )
        agg["delegator_pot_pct"] = (
            agg["total_delegator_pot_ada"] / agg["total_rewards_ada"] * 100
        )
        if prefix:
            rename = {col: f"{prefix}_{col}" for col in agg.columns if col != "epoch_no"}
            agg.rename(columns=rename, inplace=True)
        return agg

    ts_all    = _epoch_agg(active)
    ts_hollow = _epoch_agg(active[active["pool_class"] == "hollow"], prefix="hollow")
    ts_mixed  = _epoch_agg(active[active["pool_class"] == "balanced"],  prefix="balanced")
    ts_priv   = _epoch_agg(active[active["pool_class"] == "private"], prefix="priv")

    ts = ts_all.merge(ts_hollow, on="epoch_no", how="left")
    ts = ts.merge(ts_mixed, on="epoch_no", how="left")   # prefix="balanced"
    ts = ts.merge(ts_priv, on="epoch_no", how="left")
    ts.fillna(0, inplace=True)

    return ts


# ── Margin & fixed-cost parameter history ────────────────────────────────

def build_fee_param_history(hist, owner_full):
    """Track evolution of margin and fixed-cost declarations (non-private)."""
    active = hist[hist["total_pool_rewards_ada"] > 0].copy()
    # Apply production-threshold filter (main report §2.4.1.5)
    active = active[active["active_stake_ada"] >= PRODUCTION_THRESHOLD_ADA].copy()

    # Join owner history and classify
    active = active.merge(
        owner_full, on=["pool_id_bech32", "epoch_no"], how="left",
    )
    active["owner_stake_ada"] = active["owner_stake_ada"].fillna(0)
    active["owner_stake_ratio"] = np.where(
        active["active_stake_ada"] > 0,
        active["owner_stake_ada"] / active["active_stake_ada"],
        0,
    )
    # Exclude private pools
    active = active[active["owner_stake_ratio"] < PRIVATE_OWNER_THRESHOLD].copy()

    fee_hist = (
        active.groupby("epoch_no")
        .agg(
            pools_with_min_cost=("fixed_cost_ada", lambda x: (x <= 340).sum()),
            pools_with_zero_margin=("margin_rate", lambda x: (x == 0).sum()),
            pools_total=("pool_id_bech32", "nunique"),
            p10_margin=("margin_rate", lambda x: x.quantile(0.10)),
            p25_margin=("margin_rate", lambda x: x.quantile(0.25)),
            p50_margin=("margin_rate", lambda x: x.quantile(0.50)),
            p75_margin=("margin_rate", lambda x: x.quantile(0.75)),
            p90_margin=("margin_rate", lambda x: x.quantile(0.90)),
            mean_margin=("margin_rate", "mean"),
            p50_fixed_cost=("fixed_cost_ada", lambda x: x.quantile(0.50)),
            mean_fixed_cost=("fixed_cost_ada", "mean"),
            stake_weighted_margin=("margin_rate", lambda x: np.average(
                x, weights=active.loc[x.index, "active_stake_ada"].clip(lower=1)
            )),
        )
        .reset_index()
    )
    fee_hist["pct_min_cost"] = fee_hist["pools_with_min_cost"] / fee_hist["pools_total"] * 100
    fee_hist["pct_zero_margin"] = fee_hist["pools_with_zero_margin"] / fee_hist["pools_total"] * 100

    return fee_hist


# ── Summary statistics ───────────────────────────────────────────────────

def _segment_summary(sub, label):
    """Compute summary stats for a pool segment."""
    if len(sub) == 0:
        return {}
    total_rewards = float(sub["total_pool_rewards_ada"].sum())
    total_op      = float(sub["operator_take_ada"].sum())
    total_fc      = float(sub["effective_fixed_cost_ada"].sum())
    total_margin  = float(sub["margin_take_ada"].sum())
    total_deleg   = float(sub["delegator_pot_ada"].sum())
    total_stake   = float(sub["active_stake_ada"].sum())

    margin_dist = {
        "mean": round(float(sub["margin_rate"].mean()), 6),
        "median": round(float(sub["margin_rate"].median()), 6),
        "stake_weighted": round(float(
            np.average(sub["margin_rate"],
                       weights=sub["active_stake_ada"].clip(lower=1))
        ), 6),
        "pct_zero_margin": round(float((sub["margin_rate"] == 0).mean() * 100), 1),
        "pct_below_2pct": round(float((sub["margin_rate"] < 0.02).mean() * 100), 1),
        "pct_above_5pct": round(float((sub["margin_rate"] > 0.05).mean() * 100), 1),
    }

    fc_dist = {
        "mean_ada": round(float(sub["fixed_cost_ada"].mean()), 1),
        "median_ada": round(float(sub["fixed_cost_ada"].median()), 1),
        "pct_at_minimum_340": round(float(
            (sub["fixed_cost_ada"] <= 340).mean() * 100
        ), 1),
    }

    tax_dist = {
        "mean_pct": round(float(sub["effective_tax_pct"].mean()), 2),
        "median_pct": round(float(sub["effective_tax_pct"].median()), 2),
        "stake_weighted_pct": round(float(
            np.average(sub["effective_tax_pct"],
                       weights=sub["active_stake_ada"].clip(lower=1))
        ), 2),
        "p10_pct": round(float(sub["effective_tax_pct"].quantile(0.10)), 2),
        "p90_pct": round(float(sub["effective_tax_pct"].quantile(0.90)), 2),
    }

    return {
        "label": label,
        "pools": len(sub),
        "total_active_stake_ada": round(total_stake, 2),
        "total_rewards_ada": round(total_rewards, 2),
        "operator_take_ada": round(total_op, 2),
        "operator_take_pct": round(total_op / total_rewards * 100, 2),
        "fixed_cost_total_ada": round(total_fc, 2),
        "fixed_cost_pct": round(total_fc / total_rewards * 100, 2),
        "margin_total_ada": round(total_margin, 2),
        "margin_pct": round(total_margin / total_rewards * 100, 2),
        "delegator_pot_ada": round(total_deleg, 2),
        "delegator_pot_pct": round(total_deleg / total_rewards * 100, 2),
        "margin_distribution": margin_dist,
        "fixed_cost_distribution": fc_dist,
        "effective_tax": tax_dist,
    }


def compute_summary(snap, ent_policies):
    """Headline stats for the README — all, hollow, mixed, and private."""
    epoch = int(snap["epoch_no"].iloc[0])

    hollow   = snap[snap["pool_class"] == "hollow"]
    balanced = snap[snap["pool_class"] == "balanced"]
    priv     = snap[snap["pool_class"] == "private"]
    non_priv = snap[snap["pool_class"] != "private"]

    s_all      = _segment_summary(snap, "all")
    s_hollow   = _segment_summary(hollow, "hollow")
    s_balanced = _segment_summary(balanced, "balanced")
    s_priv     = _segment_summary(priv, "private")

    # MPO / SPO within non-private pools
    mpo = non_priv[non_priv["is_mpo"]]
    spo = non_priv[~non_priv["is_mpo"]]

    # Hollow captive sub-segment (margin >= 99.9% within hollow strategy)
    hollow_captive = hollow[hollow["margin_rate"] >= 0.999]

    # Entity-level stats (non-private only)
    n_entities = len(ent_policies)
    n_mpo_entities = int(ent_policies["is_mpo"].sum())
    n_spo_entities = n_entities - n_mpo_entities
    ent_sw_margins = ent_policies["stake_weighted_margin"].values
    ent_stakes     = ent_policies["total_active_stake_ada"].values

    entity_margin = {
        "n_entities": n_entities,
        "n_mpo_entities": n_mpo_entities,
        "n_spo_entities": n_spo_entities,
        "mean_entity_margin": round(float(ent_sw_margins.mean()), 6),
        "median_entity_margin": round(float(np.median(ent_sw_margins)), 6),
        "stake_weighted_entity_margin": round(float(
            np.average(ent_sw_margins, weights=np.maximum(ent_stakes, 1))
        ), 6),
        "entities_at_zero": int((ent_sw_margins == 0).sum()),
        "entities_below_2pct": int((ent_sw_margins < 0.02).sum()),
        "entities_2_to_5pct": int(
            ((ent_sw_margins >= 0.02) & (ent_sw_margins <= 0.05)).sum()
        ),
        "entities_above_5pct": int((ent_sw_margins > 0.05).sum()),
        "entities_with_mixed_policy": int(
            (ent_policies["n_distinct_margins"] > 1).sum()
        ),
    }

    def _mpo_spo_block(sub, label):
        if len(sub) == 0:
            return {"pools": 0, "total_rewards_ada": 0,
                    "operator_take_ada": 0, "operator_take_pct": 0}
        return {
            "pools": int(len(sub)),
            "total_rewards_ada": round(float(sub["total_pool_rewards_ada"].sum()), 2),
            "operator_take_ada": round(float(sub["operator_take_ada"].sum()), 2),
            "operator_take_pct": round(float(
                sub["operator_take_ada"].sum() / sub["total_pool_rewards_ada"].sum() * 100
            ), 2),
        }

    # ── Entity-level strategy assignment ──
    ent_strat = (
        snap.groupby(["eff_entity_id", "pool_class"])["active_stake_ada"]
        .sum().reset_index()
    )
    dominant = (
        ent_strat.sort_values("active_stake_ada", ascending=False)
        .drop_duplicates("eff_entity_id")[["eff_entity_id", "pool_class"]]
        .rename(columns={"pool_class": "dominant_strategy"})
    )
    # Consistency: how many distinct strategies per entity
    n_strats = (
        snap.groupby("eff_entity_id")["pool_class"]
        .nunique().reset_index()
        .rename(columns={"pool_class": "n_strategies"})
    )
    dominant = dominant.merge(n_strats, on="eff_entity_id")

    n_total_ent = len(dominant)
    n_pure      = int((dominant["n_strategies"] == 1).sum())
    n_hybrid    = n_total_ent - n_pure

    # Entity counts per dominant strategy
    ent_by_strat = {}
    for strat in ["hollow", "balanced", "private"]:
        sub = dominant[dominant["dominant_strategy"] == strat]
        pools_in = snap[snap["eff_entity_id"].isin(sub["eff_entity_id"])]
        ent_by_strat[strat] = {
            "entities": int(len(sub)),
            "pools": int(pools_in["pool_id_bech32"].nunique()),
            "total_active_stake_ada": round(float(pools_in["active_stake_ada"].sum()), 2),
            "total_rewards_ada": round(float(pools_in["total_pool_rewards_ada"].sum()), 2),
            "operator_take_ada": round(float(pools_in["operator_take_ada"].sum()), 2),
            "operator_take_pct": round(float(
                pools_in["operator_take_ada"].sum()
                / pools_in["total_pool_rewards_ada"].sum() * 100
            ), 2) if len(pools_in) > 0 else 0,
            "owner_stake_ada": round(float(pools_in["owner_stake_ada"].sum()), 2),
        }

    strategy_consistency = {
        "total_entities": n_total_ent,
        "pure_strategy_entities": n_pure,
        "pure_strategy_pct": round(n_pure / n_total_ent * 100, 1),
        "hybrid_entities": n_hybrid,
        "by_dominant_strategy": ent_by_strat,
    }

    summary = {
        "epoch": epoch,
        "all": s_all,
        "hollow": s_hollow,
        "balanced": s_balanced,
        "private": s_priv,
        "hollow_captive": {
            "pools": int(len(hollow_captive)),
            "total_active_stake_ada": round(float(hollow_captive["active_stake_ada"].sum()), 2),
            "total_rewards_ada": round(float(hollow_captive["total_pool_rewards_ada"].sum()), 2),
            "operator_take_ada": round(float(hollow_captive["operator_take_ada"].sum()), 2),
            "operator_take_pct": round(float(
                hollow_captive["operator_take_ada"].sum()
                / hollow_captive["total_pool_rewards_ada"].sum() * 100
            ), 2) if len(hollow_captive) > 0 else 0,
        },
        "nonpriv_mpo": _mpo_spo_block(mpo, "nonpriv_mpo"),
        "nonpriv_spo": _mpo_spo_block(spo, "nonpriv_spo"),
        "entity_level_margin": entity_margin,
        "strategy_consistency": strategy_consistency,
    }
    return summary, dominant


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data …")
    hist, latest = load_pool_history()
    owner_full = load_owner_history_full()
    owner_snap = load_owner_snapshot(owner_full, latest)
    pool_list  = load_pool_list()
    entity_map = load_entity_mapping()
    upstream_health = load_upstream_health()

    print("\nBuilding snapshot …")
    snap = build_snapshot(hist, latest, owner_snap, pool_list, entity_map,
                          upstream_health)
    snap.to_csv(DATA_DIR / "reward_split_snapshot.csv", index=False)
    print(f"  → reward_split_snapshot.csv ({len(snap):,} pools)")

    hollow   = snap[snap["pool_class"] == "hollow"]
    balanced = snap[snap["pool_class"] == "balanced"]
    priv     = snap[snap["pool_class"] == "private"]
    print(f"    Hollow: {len(hollow):,}  |  Balanced: {len(balanced):,}  |  Private: {len(priv):,}")

    print("\nBuilding entity-level fee policies (non-private) …")
    ent_policies = build_entity_policies(snap)
    ent_policies.to_csv(DATA_DIR / "entity_fee_policies.csv", index=False)
    print(f"  → entity_fee_policies.csv ({len(ent_policies):,} entities)")

    print("\nBuilding timeseries …")
    ts = build_timeseries(hist, owner_full)
    ts.to_csv(DATA_DIR / "reward_split_timeseries.csv", index=False)
    print(f"  → reward_split_timeseries.csv ({len(ts)} epochs)")

    print("\nBuilding fee parameter history (non-private) …")
    fee_hist = build_fee_param_history(hist, owner_full)
    fee_hist.to_csv(DATA_DIR / "margin_fixed_cost_history.csv", index=False)
    print(f"  → margin_fixed_cost_history.csv ({len(fee_hist)} epochs)")

    print("\nComputing summary …")
    summary, ent_dominant = compute_summary(snap, ent_policies)
    with (DATA_DIR / "reward_split_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"  → reward_split_summary.json")

    # Export entity strategy assignment
    ent_strat_df = snap.groupby("eff_entity_id").agg(
        display_name=("display_name", "first"),
        n_pools=("pool_id_bech32", "nunique"),
        total_stake=("active_stake_ada", "sum"),
        total_owner_stake=("owner_stake_ada", "sum"),
        total_rewards=("total_pool_rewards_ada", "sum"),
        total_op_take=("operator_take_ada", "sum"),
        total_deleg_pot=("delegator_pot_ada", "sum"),
    ).reset_index()
    ent_strat_df = ent_strat_df.merge(ent_dominant, on="eff_entity_id")
    ent_strat_df["owner_ratio"] = (
        ent_strat_df["total_owner_stake"] / ent_strat_df["total_stake"]
    )
    ent_strat_df["op_take_pct"] = (
        ent_strat_df["total_op_take"] / ent_strat_df["total_rewards"] * 100
    )
    ent_strat_df.sort_values("total_stake", ascending=False, inplace=True)
    ent_strat_df.to_csv(DATA_DIR / "entity_strategy_summary.csv", index=False)
    print(f"  → entity_strategy_summary.csv ({len(ent_strat_df):,} entities)")

    # Print key stats
    s = summary
    for seg_key, seg_label in [("all", "ALL POOLS"), ("hollow", "HOLLOW"),
                                ("balanced", "BALANCED"), ("private", "PRIVATE")]:
        seg = s[seg_key]
        print(f"\n{'='*65}")
        print(f"  {seg_label}  |  Epoch {s['epoch']}  |  {seg['pools']:,} pools")
        print(f"  Total distributed rewards: {seg['total_rewards_ada']:,.0f} ADA")
        print(f"  ── Operator take: {seg['operator_take_ada']:,.0f} ADA "
              f"({seg['operator_take_pct']}%)")
        print(f"     · Fixed cost:  {seg['fixed_cost_total_ada']:,.0f} ADA "
              f"({seg['fixed_cost_pct']}%)")
        print(f"     · Margin:      {seg['margin_total_ada']:,.0f} ADA "
              f"({seg['margin_pct']}%)")
        print(f"  ── Delegator pot: {seg['delegator_pot_ada']:,.0f} ADA "
              f"({seg['delegator_pot_pct']}%)")
        md = seg["margin_distribution"]
        print(f"  Margin: mean={md['mean']:.3%}, median={md['median']:.3%}, "
              f"stake-wtd={md['stake_weighted']:.3%}")
    hc = s["hollow_captive"]
    print(f"\n  Hollow-captive (margin ≥ 99.9%): {hc['pools']} pools, "
          f"{hc['total_active_stake_ada']:,.0f} ADA stake, "
          f"op_take={hc['operator_take_pct']}%")
    sc = s["strategy_consistency"]
    print(f"\n{'='*65}")
    print(f"  ENTITY STRATEGY CONSISTENCY")
    print(f"  Total entities: {sc['total_entities']}")
    print(f"  Pure-strategy: {sc['pure_strategy_entities']} ({sc['pure_strategy_pct']}%)")
    print(f"  Hybrid: {sc['hybrid_entities']}")
    for strat in ["hollow", "balanced", "private"]:
        bs = sc["by_dominant_strategy"][strat]
        print(f"  {strat:10s}: {bs['entities']:4d} entities, "
              f"{bs['pools']:5d} pools, {bs['total_active_stake_ada']/1e9:.2f}B ADA, "
              f"op_take={bs['operator_take_pct']}%")
    print(f"\n{'='*65}")
    em = s["entity_level_margin"]
    print(f"  Entity-level margin (non-private): {em['n_entities']} entities "
          f"({em['n_mpo_entities']} MPO, {em['n_spo_entities']} SPO)")
    print(f"  Entity margin: mean={em['mean_entity_margin']:.3%}, "
          f"median={em['median_entity_margin']:.3%}, "
          f"stake-wtd={em['stake_weighted_entity_margin']:.3%}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
