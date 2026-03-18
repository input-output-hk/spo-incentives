#!/usr/bin/env python3
"""
Build pool-level detail for attributed MPO entities / clusters.

Outputs:
- scenarii-evaluation/outputs/mpo_entity_pool_health_mainnet.csv
- scenarii-evaluation/outputs/mpo_entity_health_overview_mainnet.csv
- scenarii-evaluation/outputs/mpo_entity_pool_health_summary_mainnet.md
- scenarii-evaluation/outputs/mpo_entity_pool_table_mainnet.md

All canonical outputs in this script are current-only:
- registered pools only
- live stake from the current Koios snapshot

Historical / retired membership remains available in
`mpo_entity_pool_mapping_mainnet.csv`.
"""

from __future__ import annotations

import csv
import json
import statistics
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def load_live_pool_rows() -> tuple[Dict[str, dict], int, float, int]:
    rows: List[dict] = []
    offset = 0
    limit = 1000
    while True:
        page = fetch_json(f"https://api.koios.rest/api/v1/pool_list?offset={offset}&limit={limit}")
        if not isinstance(page, list):
            raise RuntimeError("Unexpected pool_list response")
        rows.extend(page)
        if len(page) < limit:
            break
        offset += len(page)

    tip = fetch_json("https://api.koios.rest/api/v1/tip")
    if not isinstance(tip, list) or not tip:
        raise RuntimeError("Unexpected tip response")
    live_epoch = int(tip[0]["epoch_no"])

    totals = fetch_json(f"https://api.koios.rest/api/v1/totals?_epoch_no={live_epoch}")
    if not isinstance(totals, list) or not totals:
        raise RuntimeError("Unexpected totals response")
    supply_ada = int(totals[0]["supply"]) / 1_000_000.0

    params = fetch_json(f"https://api.koios.rest/api/v1/epoch_params?_epoch_no={live_epoch}")
    if not isinstance(params, list) or not params:
        raise RuntimeError("Unexpected epoch_params response")
    optimal_pool_count = int(params[0]["optimal_pool_count"])

    return {row["pool_id_bech32"]: row for row in rows}, live_epoch, supply_ada, optimal_pool_count


def load_entity_mapping(path: Path) -> Dict[str, dict]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return {row["pool_id_bech32"]: row for row in reader}


def load_latest_owner_snapshot(path: Path) -> Dict[str, dict]:
    by_pool_epoch: Dict[str, int] = {}
    per_pool_epoch_rows: Dict[tuple[str, int], list[dict]] = defaultdict(list)

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id_bech32"]
            epoch_no = int(row["epoch_no"])
            if epoch_no > by_pool_epoch.get(pool_id, -1):
                by_pool_epoch[pool_id] = epoch_no
            per_pool_epoch_rows[(pool_id, epoch_no)].append(row)

    snapshots: Dict[str, dict] = {}
    for pool_id, epoch_no in by_pool_epoch.items():
        rows = per_pool_epoch_rows[(pool_id, epoch_no)]
        declared_pledge_ada = max(float(row["declared_pledge_ada"]) for row in rows)
        owner_active_stake_ada = sum(float(row["owner_active_stake_ada"]) for row in rows)
        snapshots[pool_id] = {
            "snapshot_epoch_no": epoch_no,
            "snapshot_declared_pledge_ada": declared_pledge_ada,
            "snapshot_owner_active_stake_ada": owner_active_stake_ada,
        }
    return snapshots


def current_stake_ada(row: dict) -> float:
    raw = row.get("active_stake")
    if raw in (None, "", "0", 0):
        return 0.0
    return int(raw) / 1_000_000.0


def pledge_ada(row: dict) -> float:
    raw = row.get("pledge")
    if raw in (None, "", "0", 0):
        return 0.0
    return int(raw) / 1_000_000.0


def fixed_cost_ada(row: dict) -> float:
    raw = row.get("fixed_cost")
    if raw in (None, "", "0", 0):
        return 0.0
    return int(raw) / 1_000_000.0


def health_tag(pool_status: str, stake_ada: float) -> str:
    if pool_status == "retired":
        return "Retired"
    if stake_ada >= 3_000_000.0:
        return "Healthy core"
    if stake_ada >= 100_000.0:
        return "Subscale active"
    if stake_ada > 0.0:
        return "Dormant"
    return "Zero-stake registered"


def saturation_tag(util_pct: float, stake_ada: float, pool_status: str) -> str:
    if pool_status == "retired":
        return "Retired"
    if stake_ada <= 0.0:
        return "No live stake"
    if util_pct >= 80.0:
        return "Near saturation"
    if util_pct >= 20.0:
        return "Mid-scale"
    return "Underfilled"


def pledge_tag(pledge_ada_value: float) -> str:
    if pledge_ada_value == 0.0:
        return "Zero pledge"
    if pledge_ada_value < 10_000.0:
        return "Minimal pledge"
    if pledge_ada_value < 1_000_000.0:
        return "Low pledge"
    if pledge_ada_value < 10_000_000.0:
        return "Material pledge"
    return "High pledge"


def snapshot_pledge_tag(snapshot: dict | None) -> str:
    if snapshot is None:
        return "No local owner snapshot"
    if snapshot["snapshot_declared_pledge_ada"] <= 0:
        return "No pledge declared in snapshot"
    ratio = snapshot["snapshot_owner_active_stake_ada"] / snapshot["snapshot_declared_pledge_ada"]
    if ratio >= 1.0:
        return "Meets pledge in latest local snapshot"
    if ratio >= 0.9:
        return "Near pledge in latest local snapshot"
    return "Below pledge in latest local snapshot"


def build_rows(
    live_rows_by_id: Dict[str, dict],
    entity_mapping: Dict[str, dict],
    owner_snapshots: Dict[str, dict],
    supply_ada: float,
    optimal_pool_count: int,
) -> List[dict]:
    saturation_point_ada = supply_ada / optimal_pool_count
    rows: List[dict] = []
    for pool_id, mapping in entity_mapping.items():
        live = live_rows_by_id.get(pool_id)
        if live is None:
            continue
        stake = current_stake_ada(live)
        pledge = pledge_ada(live)
        margin_pct = float(live.get("margin") or 0.0) * 100.0
        fixed_cost = fixed_cost_ada(live)
        status = str(live.get("pool_status") or "")
        saturation_util_pct = stake / saturation_point_ada * 100.0 if saturation_point_ada else 0.0
        snapshot = owner_snapshots.get(pool_id)
        owner_stake_snapshot = snapshot["snapshot_owner_active_stake_ada"] if snapshot else None
        snapshot_pledge = snapshot["snapshot_declared_pledge_ada"] if snapshot else None
        pledge_ratio = None
        if snapshot and snapshot_pledge and snapshot_pledge > 0:
            pledge_ratio = owner_stake_snapshot / snapshot_pledge

        rows.append(
            {
                "entity_id": mapping["entity_id"],
                "display_name": mapping["display_name"],
                "category": mapping["category"],
                "confidence": mapping["confidence"],
                "claim_type": mapping["claim_type"],
                "pool_id_bech32": pool_id,
                "ticker": str(live.get("ticker") or ""),
                "pool_status": status,
                "current_active_stake_ada": f"{stake:.3f}",
                "current_pct_supply": f"{stake / supply_ada * 100.0:.4f}" if supply_ada else "0.0000",
                "current_pct_saturation": f"{saturation_util_pct:.2f}",
                "declared_pledge_ada": f"{pledge:.3f}",
                "pledge_tag": pledge_tag(pledge),
                "margin_pct": f"{margin_pct:.2f}",
                "fixed_cost_ada": f"{fixed_cost:.3f}",
                "health_tag_current": health_tag(status, stake),
                "saturation_tag_current": saturation_tag(saturation_util_pct, stake, status),
                "snapshot_epoch_no": "" if snapshot is None else str(snapshot["snapshot_epoch_no"]),
                "snapshot_owner_active_stake_ada": "" if owner_stake_snapshot is None else f"{owner_stake_snapshot:.3f}",
                "snapshot_declared_pledge_ada": "" if snapshot_pledge is None else f"{snapshot_pledge:.3f}",
                "snapshot_owner_vs_pledge_ratio": "" if pledge_ratio is None else f"{pledge_ratio:.3f}",
                "snapshot_pledge_tag": snapshot_pledge_tag(snapshot),
                "meta_domain": mapping["meta_domain"],
                "meta_url": mapping["meta_url"],
                "pool_group": mapping["pool_group"],
                "adastat_group": mapping["adastat_group"],
                "balanceanalytics_group": mapping["balanceanalytics_group"],
                "reward_addr": mapping["reward_addr"],
                "relay_hints": mapping["relay_hints"],
            }
        )
    rows.sort(key=lambda row: (row["display_name"], -float(row["current_active_stake_ada"]), row["pool_id_bech32"]))
    return rows


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def group_rows(rows: List[dict]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        out[row["display_name"]].append(row)
    return out


def registered_rows(rows: List[dict]) -> List[dict]:
    return [row for row in rows if row["pool_status"] == "registered"]


def positive_stake_rows(rows: List[dict]) -> List[dict]:
    return [row for row in registered_rows(rows) if float(row["current_active_stake_ada"]) > 0.0]


def median_or_zero(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def pool_label(row: dict) -> str:
    ticker = str(row["ticker"] or "").strip()
    if ticker:
        return ticker
    pool_id = row["pool_id_bech32"]
    return f"{pool_id[:12]}...{pool_id[-6:]}"


def format_pledge_display(pledge_ada: float) -> str:
    if pledge_ada == 0.0:
        return "0"
    if pledge_ada < 0.001:
        return "<0.001"
    if pledge_ada < 1.0:
        return f"{pledge_ada:.6f}"
    return f"{pledge_ada:,.0f}"


def top_pool_lines(rows: List[dict], limit: int = 5) -> List[str]:
    ranked = sorted(
        positive_stake_rows(rows),
        key=lambda row: float(row["current_active_stake_ada"]),
        reverse=True,
    )[:limit]
    lines: List[str] = []
    for row in ranked:
        lines.append(
            f"`{pool_label(row)}` {float(row['current_active_stake_ada'])/1_000_000:.2f}M ADA, "
            f"pledge {float(row['declared_pledge_ada']):,.0f} ADA, "
            f"margin {float(row['margin_pct']):.2f}%, "
            f"fixed cost {float(row['fixed_cost_ada']):.0f} ADA, "
            f"{row['health_tag_current']}, {row['saturation_tag_current']}"
        )
    return lines


def should_include_entity(rows: List[dict]) -> bool:
    current_stake = sum(float(row["current_active_stake_ada"]) for row in rows)
    return current_stake >= 50_000_000.0 or len(rows) >= 6


def top_values(rows: List[dict], key: str, limit: int = 3) -> List[tuple[str, int]]:
    counter: Counter[str] = Counter()
    ignored = {"n", "n/a", "na", "singlepool"}
    for row in rows:
        value = str(row.get(key) or "").strip()
        if not value:
            continue
        if value.lower() in ignored:
            continue
        counter[value] += 1
    return counter.most_common(limit)


def top_relay_hints(rows: List[dict], limit: int = 3) -> List[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for row in rows:
        relay_hints = str(row.get("relay_hints") or "").strip()
        if not relay_hints:
            continue
        for hint in relay_hints.split(";"):
            value = hint.strip()
            if value:
                counter[value] += 1
    return counter.most_common(limit)


def format_samples(values: List[tuple[str, int]]) -> str:
    if not values:
        return "n/a"
    return ", ".join(f"`{value}` ({count})" for value, count in values)


def operational_health_tag(rows: List[dict]) -> str:
    registered = registered_rows(rows)
    if not registered:
        return "Historical only"

    live_positive = positive_stake_rows(rows)
    healthy = [row for row in live_positive if row["health_tag_current"] == "Healthy core"]

    if len(live_positive) >= 10 and len(healthy) / len(registered) >= 0.75:
        return "Dense live fleet"
    if len(live_positive) >= 5 and len(healthy) / len(registered) >= 0.50:
        return "Mostly healthy live fleet"
    if len(live_positive) >= 5:
        return "Mixed live fleet"
    if live_positive:
        return "Thin live fleet"
    return "Legacy-only footprint"


def decentralization_pressure_tag(total_stake_ada: float, supply_ada: float, healthy_count: int) -> str:
    share_pct = total_stake_ada / supply_ada * 100.0 if supply_ada else 0.0
    if share_pct >= 5.0 or healthy_count >= 30:
        return "Very high"
    if share_pct >= 2.0 or healthy_count >= 15:
        return "High"
    if share_pct >= 1.0 or healthy_count >= 5:
        return "Moderate"
    return "Limited"


def summarize_entity(entity_name: str, rows: List[dict], supply_ada: float) -> dict:
    registered = registered_rows(rows)
    live_positive = positive_stake_rows(rows)
    live_stakes = [float(row["current_active_stake_ada"]) for row in live_positive]
    live_pledges = [float(row["declared_pledge_ada"]) for row in live_positive]
    live_margins = [float(row["margin_pct"]) for row in live_positive]
    live_fixed_costs = [float(row["fixed_cost_ada"]) for row in live_positive]
    total_stake = sum(float(row["current_active_stake_ada"]) for row in rows)
    healthy_count = sum(row["health_tag_current"] == "Healthy core" for row in rows)
    subscale_count = sum(row["health_tag_current"] == "Subscale active" for row in rows)
    dormant_count = sum(row["health_tag_current"] == "Dormant" for row in rows)
    zero_count = sum(row["health_tag_current"] == "Zero-stake registered" for row in rows)
    retired_count = sum(row["health_tag_current"] == "Retired" for row in rows)
    near_sat = sum(row["saturation_tag_current"] == "Near saturation" for row in rows)
    zero_pledge = sum(row["pledge_tag"] == "Zero pledge" for row in rows)
    minimal_pledge = sum(row["pledge_tag"] == "Minimal pledge" for row in rows)

    return {
        "display_name": entity_name,
        "claim_type": rows[0]["claim_type"],
        "confidence": rows[0]["confidence"],
        "current_registered_pool_count": len(registered),
        "current_live_positive_pool_count": len(live_positive),
        "healthy_core_pool_count": healthy_count,
        "subscale_active_pool_count": subscale_count,
        "dormant_pool_count": dormant_count,
        "zero_stake_registered_pool_count": zero_count,
        "near_saturation_pool_count": near_sat,
        "zero_pledge_pool_count": zero_pledge,
        "minimal_pledge_pool_count": minimal_pledge,
        "current_stake_ada": total_stake,
        "current_pct_supply": total_stake / supply_ada * 100.0 if supply_ada else 0.0,
        "median_live_stake_ada": median_or_zero(live_stakes),
        "largest_live_stake_ada": max(live_stakes) if live_stakes else 0.0,
        "median_live_pledge_ada": median_or_zero(live_pledges),
        "avg_live_pledge_ada": statistics.mean(live_pledges) if live_pledges else 0.0,
        "avg_live_margin_pct": statistics.mean(live_margins) if live_margins else 0.0,
        "avg_live_fixed_cost_ada": statistics.mean(live_fixed_costs) if live_fixed_costs else 0.0,
        "operational_health_tag": operational_health_tag(rows),
        "decentralization_pressure_tag": decentralization_pressure_tag(total_stake, supply_ada, healthy_count),
        "dominant_meta_domains": format_samples(top_values(rows, "meta_domain")),
        "koios_pool_groups": format_samples(top_values(rows, "pool_group")),
        "adastat_groups": format_samples(top_values(rows, "adastat_group")),
        "balanceanalytics_groups": format_samples(top_values(rows, "balanceanalytics_group")),
        "relay_hints": format_samples(top_relay_hints(rows)),
    }


def write_entity_summary_csv(path: Path, grouped: Dict[str, List[dict]], supply_ada: float) -> None:
    entity_rows: List[dict] = []
    for entity_name, rows in grouped.items():
        if not should_include_entity(rows):
            continue
        summary = summarize_entity(entity_name, rows, supply_ada)
        entity_rows.append(
            {
                "display_name": summary["display_name"],
                "claim_type": summary["claim_type"],
                "confidence": summary["confidence"],
                "operational_health_tag": summary["operational_health_tag"],
                "decentralization_pressure_tag": summary["decentralization_pressure_tag"],
                "current_registered_pool_count": str(summary["current_registered_pool_count"]),
                "current_live_positive_pool_count": str(summary["current_live_positive_pool_count"]),
                "healthy_core_pool_count": str(summary["healthy_core_pool_count"]),
                "subscale_active_pool_count": str(summary["subscale_active_pool_count"]),
                "dormant_pool_count": str(summary["dormant_pool_count"]),
                "zero_stake_registered_pool_count": str(summary["zero_stake_registered_pool_count"]),
                "near_saturation_pool_count": str(summary["near_saturation_pool_count"]),
                "current_stake_ada": f"{summary['current_stake_ada']:.3f}",
                "current_pct_supply": f"{summary['current_pct_supply']:.4f}",
                "median_live_stake_ada": f"{summary['median_live_stake_ada']:.3f}",
                "largest_live_stake_ada": f"{summary['largest_live_stake_ada']:.3f}",
                "median_live_pledge_ada": f"{summary['median_live_pledge_ada']:.3f}",
                "avg_live_pledge_ada": f"{summary['avg_live_pledge_ada']:.3f}",
                "avg_live_margin_pct": f"{summary['avg_live_margin_pct']:.2f}",
                "avg_live_fixed_cost_ada": f"{summary['avg_live_fixed_cost_ada']:.3f}",
                "dominant_meta_domains": summary["dominant_meta_domains"],
                "koios_pool_groups": summary["koios_pool_groups"],
                "adastat_groups": summary["adastat_groups"],
                "balanceanalytics_groups": summary["balanceanalytics_groups"],
                "relay_hints": summary["relay_hints"],
            }
        )

    entity_rows.sort(key=lambda row: float(row["current_stake_ada"]), reverse=True)
    if not entity_rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(entity_rows[0].keys()))
        writer.writeheader()
        writer.writerows(entity_rows)


def write_markdown(
    path: Path,
    grouped: Dict[str, List[dict]],
    live_epoch: int,
    supply_ada: float,
    optimal_pool_count: int,
) -> None:
    saturation_point_ada = supply_ada / optimal_pool_count
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entity_order = sorted(
        (name for name, rows in grouped.items() if should_include_entity(rows)),
        key=lambda name: sum(float(row["current_active_stake_ada"]) for row in grouped[name]),
        reverse=True,
    )

    lines: List[str] = [
        "# MPO Entity Pool Health Summary (Mainnet)",
        "",
        f"_Snapshot built from live Koios data at epoch `{live_epoch}` on `{now_utc}`._",
        "",
        "## What the health tags mean",
        "",
        f"- `Healthy core`: live registered pool with at least **3M ADA** active stake. This reuses the report's core viability threshold for consistent block production.",
        "- `Subscale active`: live registered pool with **100k to <3M ADA** active stake.",
        "- `Dormant`: live registered pool with **>0 and <100k ADA** active stake.",
        "- `Zero-stake registered`: still registered, but no live active stake right now.",
        "",
        "These are **current-size tags**, not a full 36-epoch profitability verdict.",
        "All counts below refer to **currently registered pools only**.",
        "",
        "## Two different questions",
        "",
        "- `Operational health` asks whether the current live fleet is materially staked or mostly thin / dormant.",
        "- `Decentralization pressure` asks whether one cluster still controls enough live stake and enough healthy pools to matter for network concentration.",
        "- A cluster can be operationally strong and still be bad news for decentralization. Coinbase is the clearest example.",
        "",
        "## Context",
        "",
        f"- Koios supply: **{supply_ada / 1_000_000_000.0:.3f}B ADA**",
        f"- Protocol `k`: **{optimal_pool_count}**",
        f"- Approximate saturation point: **{saturation_point_ada / 1_000_000.0:.2f}M ADA per pool**",
        "",
        "## Entity summaries",
        "",
    ]

    for entity_name in entity_order:
        rows = grouped[entity_name]
        summary = summarize_entity(entity_name, rows, supply_ada)

        lines.extend(
            [
                f"### {entity_name}",
                "",
                f"- Claim type: **{summary['claim_type']}**",
                f"- Confidence: **{summary['confidence']}**",
                f"- Operational health: **{summary['operational_health_tag']}**",
                f"- Decentralization pressure: **{summary['decentralization_pressure_tag']}**",
                f"- Attribution basis: metadata domains {summary['dominant_meta_domains']}; Koios `pool_group` {summary['koios_pool_groups']}; AdaStat {summary['adastat_groups']}; BalanceAnalytics {summary['balanceanalytics_groups']}; relay hints {summary['relay_hints']}",
                f"- Current fleet: **{summary['current_registered_pool_count']} currently registered pools**, **{summary['current_live_positive_pool_count']} with positive live stake**",
                f"- Live stake under this entity / cluster: **{summary['current_stake_ada'] / 1_000_000_000.0:.3f}B ADA** (**{summary['current_pct_supply']:.2f}%** of supply)",
                f"- Current live health mix: **{summary['healthy_core_pool_count']} Healthy core**, **{summary['subscale_active_pool_count']} Subscale active**, **{summary['dormant_pool_count']} Dormant**, **{summary['zero_stake_registered_pool_count']} Zero-stake registered**",
                f"- Saturation mix: **{summary['near_saturation_pool_count']} Near saturation** pools; median live stake = **{summary['median_live_stake_ada'] / 1_000_000.0:.2f}M ADA**; largest live pool = **{summary['largest_live_stake_ada'] / 1_000_000.0:.2f}M ADA**",
                f"- Current live parameters: median pledge = **{summary['median_live_pledge_ada']:,.0f} ADA**, average live pledge = **{summary['avg_live_pledge_ada']:,.0f} ADA**, average margin = **{summary['avg_live_margin_pct']:.2f}%**, average fixed cost = **{summary['avg_live_fixed_cost_ada']:.0f} ADA**",
                f"- Pledge posture across matched set: **{summary['zero_pledge_pool_count']} Zero pledge** pools and **{summary['minimal_pledge_pool_count']} Minimal pledge** pools",
                "- Largest pools:",
            ]
        )
        for line in top_pool_lines(rows):
            lines.append(f"  - {line}")
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- A large pool count is not automatically the same thing as 47 equally large pools. The summary above uses currently registered pools only, then separates those with positive live stake from zero-stake registrations.",
            "- For custodial or provider clusters, the more important question is not just count, but how many pools are actually carrying material live stake and how thin the pledge is relative to that stake.",
            "- Coinbase / bison.run is still the biggest concentration issue in this cut: **47 live positive-stake pools**, **41 healthy-core pools**, and **6.37% of supply**, with near-zero pledge on almost the entire fleet.",
            "- The detailed pool sheet is in `mpo_entity_pool_health_mainnet.csv`; the one-row-per-entity overview is in `mpo_entity_health_overview_mainnet.csv`.",
            "- If you need the historical / retired attribution set later, use `mpo_entity_pool_mapping_mainnet.csv` instead of the current-only health outputs.",
            "",
        ]
    )

    path.write_text("\n".join(lines))


def write_pool_table_markdown(
    path: Path,
    grouped: Dict[str, List[dict]],
    live_epoch: int,
    supply_ada: float,
) -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entity_order = sorted(
        (name for name, rows in grouped.items() if should_include_entity(rows)),
        key=lambda name: sum(float(row["current_active_stake_ada"]) for row in grouped[name]),
        reverse=True,
    )

    lines: List[str] = [
        "# MPO Entity Pool Table (Mainnet)",
        "",
        f"_Snapshot built from live Koios data at epoch `{live_epoch}` on `{now_utc}`._",
        "",
        "This file lists **currently registered pools only**.",
        "",
        "Column notes:",
        "",
        "- `Stake (M)`: current active stake in millions of ADA.",
        "- `Sat %`: current percentage of the live saturation point.",
        "- `Snapshot pledge`: latest local owner-history comparison against declared pledge, where available.",
        "- `Koios`, `AdaStat`, and `Balance` are attribution fields used to group pools under the same suspected entity / cluster.",
        "",
    ]

    for entity_name in entity_order:
        rows = grouped[entity_name]
        summary = summarize_entity(entity_name, rows, supply_ada)
        ranked = sorted(rows, key=lambda row: float(row["current_active_stake_ada"]), reverse=True)

        lines.extend(
            [
                f"## {entity_name}",
                "",
                f"- Claim type: **{summary['claim_type']}**",
                f"- Confidence: **{summary['confidence']}**",
                f"- Registered pools: **{summary['current_registered_pool_count']}**",
                f"- Positive-stake pools: **{summary['current_live_positive_pool_count']}**",
                f"- Current stake: **{summary['current_stake_ada'] / 1_000_000_000.0:.3f}B ADA** (**{summary['current_pct_supply']:.2f}%** of supply)",
                "",
                "| Pool ID | Ticker | Stake (M) | Sat % | Pledge ADA | Margin % | Fixed ADA | Health | Sat tag | Snapshot pledge | Meta domain | Koios | AdaStat | Balance |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )

        for row in ranked:
            pool_id = row["pool_id_bech32"]
            ticker = row["ticker"] or "n/a"
            stake_m = float(row["current_active_stake_ada"]) / 1_000_000.0
            sat_pct = float(row["current_pct_saturation"])
            pledge = float(row["declared_pledge_ada"])
            margin = float(row["margin_pct"])
            fixed_cost = float(row["fixed_cost_ada"])
            health = row["health_tag_current"]
            sat_tag = row["saturation_tag_current"]
            snapshot = row["snapshot_pledge_tag"]
            meta_domain = row["meta_domain"] or "n/a"
            koios_group = row["pool_group"] or "n/a"
            adastat_group = row["adastat_group"] or "n/a"
            balance_group = row["balanceanalytics_group"] or "n/a"
            lines.append(
                f"| `{pool_id}` | `{ticker}` | {stake_m:.2f} | {sat_pct:.2f} | {format_pledge_display(pledge)} | {margin:.2f} | {fixed_cost:,.0f} | {health} | {sat_tag} | {snapshot} | `{meta_domain}` | `{koios_group}` | `{adastat_group}` | `{balance_group}` |"
            )
        lines.append("")

    path.write_text("\n".join(lines))


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    outputs_dir = repo_root / "scenarii-evaluation" / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    mapping_path = outputs_dir / "mpo_entity_pool_mapping_mainnet.csv"
    if not mapping_path.exists():
        raise RuntimeError(f"Missing entity mapping: {mapping_path}")

    live_rows_by_id, live_epoch, supply_ada, optimal_pool_count = load_live_pool_rows()
    entity_mapping = load_entity_mapping(mapping_path)
    owner_snapshots = load_latest_owner_snapshot(repo_root / "scenarii-evaluation" / "data" / "koios_pool_owner_history_mainnet.csv")

    rows = build_rows(live_rows_by_id, entity_mapping, owner_snapshots, supply_ada, optimal_pool_count)
    current_rows = registered_rows(rows)
    csv_path = outputs_dir / "mpo_entity_pool_health_mainnet.csv"
    entity_csv_path = outputs_dir / "mpo_entity_health_overview_mainnet.csv"
    md_path = outputs_dir / "mpo_entity_pool_health_summary_mainnet.md"
    table_md_path = outputs_dir / "mpo_entity_pool_table_mainnet.md"
    grouped = group_rows(current_rows)
    write_csv(csv_path, current_rows)
    write_entity_summary_csv(entity_csv_path, grouped, supply_ada)
    write_markdown(md_path, grouped, live_epoch, supply_ada, optimal_pool_count)
    write_pool_table_markdown(table_md_path, grouped, live_epoch, supply_ada)

    print(csv_path)
    print(entity_csv_path)
    print(md_path)
    print(table_md_path)


if __name__ == "__main__":
    main()
