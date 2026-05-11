"""Visualise MPO infrastructure-topology concentration.

Two figures, IOG-brand palette:
  figures/mpo_topology_provider_tier.png  -- stacked horizontal bar: tier x provider
  figures/mpo_topology_aws_region.png     -- AWS region stake-bar with entity callouts

Run: python3 scripts/build_mpo_topology_figure.py
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# IOG brand palette
IOG = {
    "infared":      "#E52321",
    "dawn":         "#EC641D",
    "black":        "#000000",
    "white":        "#FFFFFF",
    "ultraviolet":  "#A700FF",
    "acid_green":   "#06FF89",
    "electric":     "#16E9D8",
    "volt":         "#F2FF58",
    "amber":        "#FFBA36",
    "ember":        "#FF532C",
    "cobalt":       "#2C4FFA",
    "pink":         "#FF79FC",
}

PROVIDER_COLOR = {
    "AWS":           IOG["infared"],
    "GCP":           IOG["dawn"],
    "Azure":         IOG["cobalt"],
    "Oracle Cloud":  IOG["amber"],
    "Huawei Cloud":  IOG["ember"],
    "Alibaba Cloud": IOG["pink"],
    "OVH":           IOG["electric"],
    "Hetzner":       IOG["acid_green"],
    "DigitalOcean":  IOG["volt"],
    "Vultr / Choopa":IOG["ultraviolet"],
    "Contabo":       "#8421A2",
    "Akamai/Linode": "#1f9d55",
    "IONOS":         "#888888",
    "Leaseweb":      "#6699CC",
    "WorldStream":   "#A0CFB7",
    "Cherry Servers":"#F2B5A7",
    "MEVspace":      "#C3B7F2",
    "HostHatch":     "#88AABB",
    "Hostinger":     "#AA88BB",
    "Servers.com":   "#998866",
    "Clouvider":     "#BBAA77",
    "Green.ch":      "#7FBF7F",
    "Cogeco (CA cable ISP)": "#A0826D",
    "Sunrise (CH residential ISP)": "#B0A090",
    "Starlink":      "#222222",
    "Other / on-prem": "#666666",
    "Unresolved":    "#CCCCCC",
}


def load_concentration_by_provider() -> list:
    rows = list(csv.DictReader(open(DATA / "mpo_topology_concentration_by_provider.csv")))
    return [
        (r["provider"], float(r["stake_split_ada"]), float(r["stake_split_pct"]), int(r["entities"]))
        for r in rows
    ]


def load_concentration_by_region() -> list:
    rows = list(csv.DictReader(open(DATA / "mpo_topology_concentration_by_region.csv")))
    return [
        (r["region"], float(r["stake_split_ada"]), float(r["stake_split_pct"]), int(r["entities"]))
        for r in rows
    ]


def load_endpoints() -> list:
    return list(csv.DictReader(open(DATA / "mpo_relay_endpoints_resolved.csv")))


def fig_provider() -> None:
    data = load_concentration_by_provider()
    # drop unresolved + very small
    data = [d for d in data if d[2] >= 0.5]
    data.sort(key=lambda d: -d[2])
    fig, ax = plt.subplots(figsize=(11, 7), dpi=140)
    fig.patch.set_facecolor(IOG["white"])
    labels = [f"{p}\n({n} entities)" for p, _, _, n in data]
    pcts = [d[2] for d in data]
    colors = [PROVIDER_COLOR.get(d[0], "#888") for d in data]
    bars = ax.barh(range(len(data))[::-1], pcts, color=colors, edgecolor=IOG["black"], linewidth=0.6)
    ax.set_yticks(range(len(data))[::-1])
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Stake share of attributable MPO base (%)", fontsize=10)
    ax.set_title(
        "Cardano MPO infrastructure providers, stake-weighted\n"
        "11.23B ADA across 475 registered pools and 46 entities",
        fontsize=12, fontweight="bold", color=IOG["black"], loc="left",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    # annotate bar tips
    for i, (p, ada, pct, n) in enumerate(data):
        y = len(data) - 1 - i
        ax.text(pct + 0.4, y, f"{pct:.1f}%  ({ada/1e9:.2f}B ADA)", va="center", fontsize=8.5)
    # tier guide on the right
    tier_text = (
        "TIERS\n"
        "Hyperscaler  63.9%  AWS / GCP / Azure / Oracle\n"
        "Commodity VPS  27.6%  OVH / Hetzner / DO / Contabo / ...\n"
        "Residential  5.2%  Green.ch / Cogeco / Sunrise / Starlink\n"
        "Other / on-prem  2.2%\n"
        "Unresolved  1.1%"
    )
    ax.text(
        0.98, -0.18, tier_text, transform=ax.transAxes, fontsize=8.2,
        va="top", ha="right",
        bbox=dict(facecolor="#F4F4F4", edgecolor="#888", boxstyle="round,pad=0.4"),
    )
    plt.subplots_adjust(left=0.22, right=0.98, top=0.91, bottom=0.20)
    out = FIG / "mpo_topology_provider_tier.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor=IOG["white"])
    print(f"wrote {out.relative_to(ROOT)}")


def fig_hyperscaler_region() -> None:
    """All hyperscaler regions (AWS / GCP / Azure), top 18 by share."""
    rows = [
        r for r in load_concentration_by_region()
        if r[0].startswith(("aws:", "gcp:", "azure:"))
    ]
    rows.sort(key=lambda r: -r[2])
    rows = rows[:18]
    # entity callouts
    endpoints = load_endpoints()
    reg_ent: dict = defaultdict(lambda: defaultdict(float))
    pool_regs: dict = defaultdict(set)
    pool_stake: dict = {}
    pool_ent: dict = {}
    for r in endpoints:
        pool_regs[r["pool_id_bech32"]].add(r["region"])
        pool_stake[r["pool_id_bech32"]] = float(r["current_active_stake_ada"] or 0)
        pool_ent[r["pool_id_bech32"]] = r["display_name"] or r["entity_id"]
    for pool, regs in pool_regs.items():
        per = pool_stake.get(pool, 0) / max(len(regs), 1)
        for rg in regs:
            reg_ent[rg][pool_ent[pool]] += per

    region_colors = {"aws": IOG["infared"], "gcp": IOG["dawn"], "azure": IOG["cobalt"]}
    fig, ax = plt.subplots(figsize=(11, 8), dpi=140)
    fig.patch.set_facecolor(IOG["white"])
    labels = [r[0] for r in rows]
    pcts = [r[2] for r in rows]
    bar_colors = [region_colors[r[0].split(":")[0]] for r in rows]
    ax.barh(range(len(rows))[::-1], pcts, color=bar_colors,
            edgecolor=IOG["black"], linewidth=0.5)
    ax.set_yticks(range(len(rows))[::-1])
    ax.set_yticklabels(labels, fontsize=9, fontweight="bold")
    ax.set_xlabel("Stake share of total productive stake (%)", fontsize=10)
    ax.set_title(
        "Hyperscaler regional concentration — stake-weighted, full Cardano pool population\n"
        "21.15B ADA, 2915 active pools (MPO + single-pool operators combined)",
        fontsize=12, fontweight="bold", color=IOG["black"], loc="left",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    for i, (rg, ada, pct, n_ents) in enumerate(rows):
        y = len(rows) - 1 - i
        ents = reg_ent.get(rg, {})
        top_ents = sorted(ents.items(), key=lambda kv: -kv[1])[:2]
        callout = ", ".join(f"{e} ({v/1e6:.0f}M)" for e, v in top_ents)
        ax.text(pct + 0.05, y, f"{pct:.2f}%  ·  {callout}", va="center", fontsize=8)
    ax.axvline(25, color="#888", linestyle="--", lw=1.2, alpha=0.6)
    ax.text(25.1, len(rows) - 0.5, "25% Leios-vote threshold",
            color="#666", fontsize=8.5, fontweight="bold")
    handles = [
        mpatches.Patch(color=region_colors["aws"], label="AWS region"),
        mpatches.Patch(color=region_colors["gcp"], label="GCP region"),
        mpatches.Patch(color=region_colors["azure"], label="Azure region"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    ax.set_xlim(0, max(28, max(pcts) + 2))
    plt.subplots_adjust(left=0.18, right=0.98, top=0.91, bottom=0.10)
    out = FIG / "mpo_topology_hyperscaler_region.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor=IOG["white"])
    print(f"wrote {out.relative_to(ROOT)}")


def fig_aws_region() -> None:
    region_rows = [r for r in load_concentration_by_region() if r[0].startswith("aws:")]
    region_rows.sort(key=lambda r: -r[2])
    # entity callouts per region
    endpoints = load_endpoints()
    region_entities: dict = defaultdict(lambda: defaultdict(float))
    pool_regions: dict = defaultdict(set)
    pool_stake: dict = {}
    pool_entity: dict = {}
    for r in endpoints:
        pool_regions[r["pool_id_bech32"]].add(r["region"])
        pool_stake[r["pool_id_bech32"]] = float(r["current_active_stake_ada"] or 0)
        pool_entity[r["pool_id_bech32"]] = r["display_name"]
    for pool, regs in pool_regions.items():
        per = pool_stake.get(pool, 0) / len(regs)
        for rg in regs:
            region_entities[rg][pool_entity[pool]] += per
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=140)
    fig.patch.set_facecolor(IOG["white"])
    labels = [r[0].replace("aws:", "") for r in region_rows]
    pcts = [r[2] for r in region_rows]
    bars = ax.barh(range(len(region_rows))[::-1], pcts, color=IOG["infared"],
                   edgecolor=IOG["black"], linewidth=0.6)
    ax.set_yticks(range(len(region_rows))[::-1])
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_xlabel("Stake share of attributable MPO base (%)", fontsize=10)
    ax.set_title(
        "AWS region exposure — stake-weighted\n"
        "No single region exceeds 7% of attributable stake; "
        "concentration is single-entity-dominated",
        fontsize=12, fontweight="bold", color=IOG["black"], loc="left",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    # entity callout
    for i, (rg, ada, pct, n_ents) in enumerate(region_rows):
        y = len(region_rows) - 1 - i
        ents = region_entities.get(rg, {})
        top_ents = sorted(ents.items(), key=lambda kv: -kv[1])[:3]
        callout = ", ".join(f"{e} ({v/1e6:.0f}M)" for e, v in top_ents)
        ax.text(pct + 0.15, y, f"{pct:.1f}%  ·  {callout}", va="center", fontsize=8.5)
    # threshold annotation
    ax.axvline(25, color=IOG["dawn"], linestyle="--", lw=1.5, alpha=0.7)
    ax.text(25.2, len(region_rows) - 0.5, "25% Leios-vote threshold (illustrative)",
            color=IOG["dawn"], fontsize=8.5, fontweight="bold")
    ax.set_xlim(0, 28)
    plt.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.10)
    out = FIG / "mpo_topology_aws_region.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor=IOG["white"])
    print(f"wrote {out.relative_to(ROOT)}")


def main() -> None:
    fig_provider()
    fig_aws_region()
    fig_hyperscaler_region()


if __name__ == "__main__":
    main()
