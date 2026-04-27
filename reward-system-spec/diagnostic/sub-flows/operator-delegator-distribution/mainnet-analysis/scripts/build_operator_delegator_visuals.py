#!/usr/bin/env python3
"""
Operator / Delegator Reward Distribution — Visual Suite.

Three strategies along the Hollow–Private pledge spectrum:
  HOLLOW   — owner_stake / active_stake <  10 %
  BALANCED — 10 % ≤ ratio < 95 %
  PRIVATE  — ratio ≥ 95 %

Pool-level figures focus on HOLLOW pools (the delegation market) unless
noted otherwise.  Entity-level figures aggregate by operator identity.

Figures:
  1.  Waterfall: hollow-pool reward split (hat_f → c → m → delegator)
  2.  Stacked area: hollow operator take vs delegator pot over time
  3.  Operator-take share (%) over time — hollow / mixed / all
  4.  Effective-tax distribution (hollow pools, histogram)
  5.  Margin-rate distribution — pool-count vs entity-count
  6.  Fixed-cost dominance vs pool size (hollow pools)
  7.  Fee-parameter evolution (non-private pools)
  8.  MPO vs SPO operator take (non-private pools)
  9.  Top-20 entities by operator take (non-private pools)
  10. Three-population comparison (bar chart)

Outputs: figures/*.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

REPORT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR   = REPORT_DIR / "data"
FIG_DIR    = REPORT_DIR / "figures"

# ── IOG Brand colours ──────────────────────────────────────────────────
BG             = "#FFFFFF"
INK            = "#1A1A1A"
DIM            = "#666666"
GRID           = "#EBEBEB"
INFARED        = "#E52321"
DAWN           = "#EC641D"
ELECTRIC_BLUE  = "#16E9D8"
ACID_GREEN     = "#06FF89"
ULTRAVIOLET    = "#A700FF"
SOLAR_AMBER    = "#FFBA36"
COBALT_PULSE   = "#2C4FFA"
EMBER_ORANGE   = "#FF532C"
HYPER_PINK     = "#FF79FC"

# Semantic colours
COL_FIXED_COST = INFARED
COL_MARGIN     = DAWN
COL_DELEG      = COBALT_PULSE
COL_OWNER_MBR  = SOLAR_AMBER
COL_HOLLOW     = COBALT_PULSE
COL_BALANCED   = ACID_GREEN
COL_PRIVATE    = ULTRAVIOLET


def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=12)
    ax.set_xlabel(xlabel, fontsize=10, color=DIM)
    ax.set_ylabel(ylabel, fontsize=10, color=DIM)
    ax.tick_params(colors=DIM, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)


# ═══════════════════════════════════════════════════════════════════════
# 1. Waterfall: HOLLOW pool reward split
# ═══════════════════════════════════════════════════════════════════════
def fig_waterfall(summary):
    seg = summary["hollow"]
    epoch = summary["epoch"]
    total  = seg["total_rewards_ada"]
    fc     = seg["fixed_cost_total_ada"]
    margin = seg["margin_total_ada"]
    deleg  = seg["delegator_pot_ada"]

    labels  = ["Total\nrewards", "Fixed\ncost", "Margin", "Delegator\npot"]
    colors  = [DIM, COL_FIXED_COST, COL_MARGIN, COL_DELEG]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(0, total, color=DIM, alpha=0.3, width=0.6, edgecolor=DIM, linewidth=0.8)
    ax.bar(1, fc, bottom=total - fc, color=COL_FIXED_COST, width=0.6, edgecolor="none")
    ax.bar(2, margin, bottom=total - fc - margin, color=COL_MARGIN, width=0.6, edgecolor="none")
    ax.bar(3, deleg, bottom=0, color=COL_DELEG, width=0.6, edgecolor="none")

    for i, (top_from, bot_to) in enumerate([
        (total, total), (total - fc, total - fc), (total - fc - margin, deleg),
    ]):
        ax.plot([i + 0.3, i + 0.7], [top_from, bot_to],
                color=DIM, linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=9)
    style_ax(ax,
             title=f"Intra-Pool Reward Split — Hollow Pools, Epoch {epoch}",
             ylabel="ADA")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))

    for i, (val, pct) in enumerate([
        (total, "100%"),
        (fc, f"{seg['fixed_cost_pct']}%"),
        (margin, f"{seg['margin_pct']}%"),
        (deleg, f"{seg['delegator_pot_pct']}%"),
    ]):
        y_pos = [total/2, total - fc + fc/2, total - fc - margin + margin/2, deleg/2][i]
        ax.text(i, y_pos, f"{val/1e3:,.0f}K\n({pct})",
                ha="center", va="center", fontsize=8, color=INK, fontweight="bold")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "reward_split_waterfall.png", dpi=180)
    plt.close(fig)
    print("  ✓ reward_split_waterfall.png")


# ═══════════════════════════════════════════════════════════════════════
# 2. Stacked area: HOLLOW operator take vs delegator pot over time
# ═══════════════════════════════════════════════════════════════════════
def fig_reward_split_timeseries(ts):
    fig, ax = plt.subplots(figsize=(12, 5))
    ep = ts["epoch_no"]
    fc = ts["hollow_total_fixed_cost_ada"] / 1e3
    mg = ts["hollow_total_margin_take_ada"] / 1e3
    dp = ts["hollow_total_delegator_pot_ada"] / 1e3

    ax.fill_between(ep, 0, fc, color=COL_FIXED_COST, alpha=0.85,
                    label="Fixed cost (operator)")
    ax.fill_between(ep, fc, fc + mg, color=COL_MARGIN, alpha=0.85,
                    label="Margin (operator)")
    ax.fill_between(ep, fc + mg, fc + mg + dp, color=COL_DELEG, alpha=0.65,
                    label="Delegator pot (pro-rata)")

    style_ax(ax,
             title="Intra-Pool Reward Split — Hollow Pools, Historical",
             xlabel="Epoch", ylabel="Distributed rewards (K ADA)")
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "reward_split_area_timeseries.png", dpi=180)
    plt.close(fig)
    print("  ✓ reward_split_area_timeseries.png")


# ═══════════════════════════════════════════════════════════════════════
# 3. Operator-take share (%) — hollow / mixed / all
# ═══════════════════════════════════════════════════════════════════════
def fig_operator_take_pct_timeseries(ts):
    fig, ax = plt.subplots(figsize=(12, 4.5))

    # Hollow lines
    ax.plot(ts["epoch_no"], ts["hollow_fixed_cost_share_pct"], color=COL_FIXED_COST,
            linewidth=1.5, label="Fixed cost (hollow)")
    ax.plot(ts["epoch_no"], ts["hollow_margin_share_pct"], color=COL_MARGIN,
            linewidth=1.5, label="Margin (hollow)")
    ax.plot(ts["epoch_no"], ts["hollow_operator_take_pct"], color=COL_HOLLOW,
            linewidth=2, linestyle="--", label="Total operator take (hollow)")

    # Balanced for reference
    ax.plot(ts["epoch_no"], ts["balanced_operator_take_pct"], color=COL_BALANCED,
            linewidth=1.5, linestyle="-.", alpha=0.8, label="Total operator take (balanced)")

    # All-pools total for reference
    ax.plot(ts["epoch_no"], ts["operator_take_pct"], color=COL_PRIVATE,
            linewidth=1, linestyle=":", alpha=0.7, label="Total operator take (all incl. private)")

    style_ax(ax,
             title="Operator Take as Share of Distributed Rewards — Historical",
             xlabel="Epoch", ylabel="Share of distributed rewards (%)")
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "operator_take_pct_timeseries.png", dpi=180)
    plt.close(fig)
    print("  ✓ operator_take_pct_timeseries.png")


# ═══════════════════════════════════════════════════════════════════════
# 4. Effective tax distribution (HOLLOW pools)
# ═══════════════════════════════════════════════════════════════════════
def fig_effective_tax_hist(snap):
    hollow = snap[snap["pool_class"] == "hollow"]
    fig, ax = plt.subplots(figsize=(10, 5))
    vals = hollow["effective_tax_pct"].dropna()
    bins = np.arange(0, 55, 2)
    ax.hist(vals, bins=bins, color=INFARED, alpha=0.8, edgecolor=BG, linewidth=0.5)

    med = vals.median()
    ax.axvline(med, color=COBALT_PULSE, linestyle="--", linewidth=1.5)
    ax.text(med + 1, ax.get_ylim()[1] * 0.9,
            f"Median: {med:.1f}%", fontsize=9, color=COBALT_PULSE)

    sw = np.average(vals, weights=hollow.loc[vals.index, "active_stake_ada"].clip(lower=1))
    ax.axvline(sw, color="#006644", linestyle="--", linewidth=1.5)
    ax.text(sw + 1, ax.get_ylim()[1] * 0.75,
            f"Stake-wtd: {sw:.1f}%", fontsize=9, color="#006644")

    style_ax(ax,
             title="Effective Tax on Delegators — Hollow Pools",
             xlabel="Operator take as % of pool reward", ylabel="Number of pools")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "effective_tax_distribution.png", dpi=180)
    plt.close(fig)
    print("  ✓ effective_tax_distribution.png")


# ═══════════════════════════════════════════════════════════════════════
# 5. Margin-rate distribution — pool count vs entity count
# ═══════════════════════════════════════════════════════════════════════
def fig_margin_distribution(snap, ent):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    hollow = snap[snap["pool_class"] == "hollow"]

    # (a) Pool-level (hollow)
    ax = axes[0]
    vals = hollow["margin_rate"] * 100
    bins = np.arange(0, 22, 0.5)
    ax.hist(vals, bins=bins, color=DAWN, alpha=0.85, edgecolor=BG, linewidth=0.4)
    med = vals.median()
    ax.axvline(med, color=COBALT_PULSE, linestyle="--", linewidth=1.5)
    ax.text(med + 0.3, ax.get_ylim()[1] * 0.9, f"Median: {med:.1f}%",
            fontsize=9, color=COBALT_PULSE)
    style_ax(ax, title="Margin Rate — By Pool (hollow)", xlabel="Margin (%)",
             ylabel="Number of pools")

    # (b) Entity-level (non-private)
    ax = axes[1]
    ent_margins = ent["stake_weighted_margin"].values * 100
    ax.hist(ent_margins, bins=bins, color=ELECTRIC_BLUE, alpha=0.85, edgecolor=BG, linewidth=0.4)
    med_e = np.median(ent_margins)
    ax.axvline(med_e, color=COBALT_PULSE, linestyle="--", linewidth=1.5)
    ax.text(med_e + 0.3, ax.get_ylim()[1] * 0.9, f"Median: {med_e:.1f}%",
            fontsize=9, color=COBALT_PULSE)
    style_ax(ax, title="Margin Rate — By Entity (non-private)", xlabel="Margin (%)",
             ylabel="Number of entities")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "margin_rate_distribution.png", dpi=180)
    plt.close(fig)
    print("  ✓ margin_rate_distribution.png")


# ═══════════════════════════════════════════════════════════════════════
# 6. Fixed-cost dominance vs pool size (HOLLOW pools)
# ═══════════════════════════════════════════════════════════════════════
def fig_fixed_cost_dominance(snap):
    pub = snap[(snap["pool_class"] == "hollow")
               & (snap["total_pool_rewards_ada"] > 0)].copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    x = pub["active_stake_ada"] / 1e6
    y = pub["fixed_cost_pct_of_reward"]

    ax.scatter(x, y, s=10, alpha=0.5, color=COL_FIXED_COST, edgecolors="none")
    ax.set_xscale("log")

    x_th = np.logspace(-1, 2, 200)
    per_ada = pub["total_pool_rewards_ada"].sum() / pub["active_stake_ada"].sum()
    y_th = 340 / (x_th * 1e6 * per_ada) * 100
    ax.plot(x_th, y_th.clip(max=100), color=INK, linewidth=1.5, linestyle="--",
            label=f"Theoretical (c=340, yield≈{per_ada*100:.4f}%/epoch)")

    style_ax(ax,
             title="Fixed-Cost Dominance — Hollow Pools",
             xlabel="Active stake (M ADA, log)", ylabel="Fixed cost as % of pool reward")
    ax.set_ylim(0, 80)
    ax.legend(fontsize=9, frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fixed_cost_dominance.png", dpi=180)
    plt.close(fig)
    print("  ✓ fixed_cost_dominance.png")


# ═══════════════════════════════════════════════════════════════════════
# 7. Fee-parameter evolution (non-private pools)
# ═══════════════════════════════════════════════════════════════════════
def fig_fee_parameter_evolution(fee_hist):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax = axes[0]
    ax.fill_between(fee_hist["epoch_no"], fee_hist["p10_margin"] * 100,
                    fee_hist["p90_margin"] * 100, alpha=0.15, color=DAWN)
    ax.fill_between(fee_hist["epoch_no"], fee_hist["p25_margin"] * 100,
                    fee_hist["p75_margin"] * 100, alpha=0.30, color=DAWN)
    ax.plot(fee_hist["epoch_no"], fee_hist["p50_margin"] * 100,
            color=DAWN, linewidth=1.5, label="Median")
    ax.plot(fee_hist["epoch_no"], fee_hist["stake_weighted_margin"] * 100,
            color="#006644", linewidth=1.5, linestyle="--", label="Stake-weighted mean")
    style_ax(ax, title="Margin Rate Evolution — Non-Private Pools", ylabel="Margin (%)")
    ax.legend(fontsize=9, frameon=False)

    ax = axes[1]
    ax.plot(fee_hist["epoch_no"], fee_hist["pct_min_cost"],
            color=COL_FIXED_COST, linewidth=1.5, label="Pools at minimum (340 ADA)")
    ax.plot(fee_hist["epoch_no"], fee_hist["pct_zero_margin"],
            color=COBALT_PULSE, linewidth=1.5, label="Pools with 0% margin")
    style_ax(ax, title="Fee Parameter Adoption — Non-Private Pools", xlabel="Epoch",
             ylabel="Share of rewarded pools (%)")
    ax.legend(fontsize=9, frameon=False)
    ax.set_ylim(0, 100)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fee_parameter_evolution.png", dpi=180)
    plt.close(fig)
    print("  ✓ fee_parameter_evolution.png")


# ═══════════════════════════════════════════════════════════════════════
# 8. MPO vs SPO operator take (non-private pools)
# ═══════════════════════════════════════════════════════════════════════
def fig_mpo_vs_spo_take(snap):
    pub = snap[snap["pool_class"] != "private"]
    mpo = pub[pub["is_mpo"]]
    spo = pub[~pub["is_mpo"]]

    labels = ["Rewarded\npools", "Total\nrewards\n(K ADA)", "Operator\ntake\n(K ADA)",
              "Operator\ntake (%)"]
    mpo_vals = [len(mpo), mpo["total_pool_rewards_ada"].sum() / 1e3,
                mpo["operator_take_ada"].sum() / 1e3,
                mpo["operator_take_ada"].sum() / mpo["total_pool_rewards_ada"].sum() * 100
                if len(mpo) > 0 else 0]
    spo_vals = [len(spo), spo["total_pool_rewards_ada"].sum() / 1e3,
                spo["operator_take_ada"].sum() / 1e3,
                spo["operator_take_ada"].sum() / spo["total_pool_rewards_ada"].sum() * 100
                if len(spo) > 0 else 0]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w/2, mpo_vals, w, color=ULTRAVIOLET, label="MPO pools", edgecolor="none")
    ax.bar(x + w/2, spo_vals, w, color=ACID_GREEN, label="SPO pools", edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    style_ax(ax, title="Operator Take — MPO vs SPO (Non-Private Pools)")
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpo_vs_spo_operator_take.png", dpi=180)
    plt.close(fig)
    print("  ✓ mpo_vs_spo_operator_take.png")


# ═══════════════════════════════════════════════════════════════════════
# 9. Top-20 ENTITIES by operator take (PUBLIC pools)
# ═══════════════════════════════════════════════════════════════════════
def fig_top_entities_operator_take(ent):
    top = ent.nlargest(20, "total_operator_take_ada").copy()
    labels = top["display_name"].fillna(top["entity_id"].str[:12]).values
    y = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(12, 7))
    fc_vals = top["total_fixed_cost_ada"].values
    mg_vals = top["total_margin_take_ada"].values

    ax.barh(y, fc_vals, color=COL_FIXED_COST, label="Fixed cost", height=0.7)
    ax.barh(y, mg_vals, left=fc_vals, color=COL_MARGIN, label="Margin", height=0.7)

    # Annotate pool count
    for i, (_, row) in enumerate(top.iterrows()):
        total = row["total_operator_take_ada"]
        ax.text(total + 50, i, f"({int(row['pool_count'])}p)",
                fontsize=7, color=DIM, va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    style_ax(ax, title="Top 20 Entities by Operator Take — Public Pools",
             xlabel="Operator take (ADA)")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "top20_entities_operator_take.png", dpi=180)
    plt.close(fig)
    print("  ✓ top20_entities_operator_take.png")


# ═══════════════════════════════════════════════════════════════════════
# 10. Three strategies comparison — entity-level
# ═══════════════════════════════════════════════════════════════════════
def fig_three_strategies(summary):
    sc = summary["strategy_consistency"]["by_dominant_strategy"]
    h = sc["hollow"]
    b = sc["balanced"]
    p = sc["private"]

    labels = ["Hollow", "Balanced", "Private"]
    colors = [COL_HOLLOW, COL_BALANCED, COL_PRIVATE]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    # (a) Entity count
    ax = axes[0]
    counts = [h["entities"], b["entities"], p["entities"]]
    ax.bar(labels, counts, color=colors, edgecolor="none", width=0.5)
    for i, v in enumerate(counts):
        ax.text(i, v + max(counts) * 0.02, str(v),
                ha="center", fontsize=10, color=INK, fontweight="bold")
    style_ax(ax, title="Entity Count", ylabel="Entities")

    # (b) Stake
    ax = axes[1]
    stakes = [h["total_active_stake_ada"] / 1e9,
              b["total_active_stake_ada"] / 1e9,
              p["total_active_stake_ada"] / 1e9]
    ax.bar(labels, stakes, color=colors, edgecolor="none", width=0.5)
    for i, v in enumerate(stakes):
        ax.text(i, v + max(stakes) * 0.02, f"{v:.1f}B",
                ha="center", fontsize=10, color=INK, fontweight="bold")
    style_ax(ax, title="Active Stake", ylabel="Stake (B ADA)")

    # (c) Operator take %
    ax = axes[2]
    op_pcts = [h["operator_take_pct"], b["operator_take_pct"], p["operator_take_pct"]]
    ax.bar(labels, op_pcts, color=colors, edgecolor="none", width=0.5)
    for i, v in enumerate(op_pcts):
        ax.text(i, v + 1.5, f"{v:.1f}%",
                ha="center", fontsize=10, color=INK, fontweight="bold")
    style_ax(ax, title="Operator Take", ylabel="Share of rewards (%)")
    ax.set_ylim(0, 110)

    n_ent = summary["strategy_consistency"]["total_entities"]
    pure_pct = summary["strategy_consistency"]["pure_strategy_pct"]
    fig.suptitle(f"Three Strategies — {n_ent} Entities, Epoch {summary['epoch']}\n"
                 f"({pure_pct}% apply a single pure strategy)",
                 fontsize=13, fontweight="bold", color=INK, y=1.05)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "three_strategies.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ three_strategies.png")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════
def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data …")
    snap = pd.read_csv(DATA_DIR / "reward_split_snapshot.csv",
                       dtype={"pool_id_bech32": str, "entity_id": str,
                              "display_name": str, "ticker": str,
                              "eff_entity_id": str})
    ts = pd.read_csv(DATA_DIR / "reward_split_timeseries.csv")
    fee_hist = pd.read_csv(DATA_DIR / "margin_fixed_cost_history.csv")
    ent = pd.read_csv(DATA_DIR / "entity_fee_policies.csv",
                      dtype={"entity_id": str, "display_name": str})
    with (DATA_DIR / "reward_split_summary.json").open() as f:
        summary = json.load(f)
    print(f"  snapshot: {len(snap):,} pools | entities: {len(ent):,} | "
          f"timeseries: {len(ts)} epochs")

    print("\nGenerating figures …")
    fig_waterfall(summary)
    fig_reward_split_timeseries(ts)
    fig_operator_take_pct_timeseries(ts)
    fig_effective_tax_hist(snap)
    fig_margin_distribution(snap, ent)
    fig_fixed_cost_dominance(snap)
    fig_fee_parameter_evolution(fee_hist)
    fig_mpo_vs_spo_take(snap)
    fig_top_entities_operator_take(ent)
    fig_three_strategies(summary)
    print(f"\nDone — {10} figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
