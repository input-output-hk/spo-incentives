#!/usr/bin/env python3
"""
Write a redirect note for the retired standalone MPO landscape report.

The canonical merged document is now:
- docs/pool-landscape-mainnet.md

Output:
- docs/mpo-landscape-mainnet.md
"""

from __future__ import annotations

import csv
import json
import statistics
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUTPUTS_DIR = ROOT / "outputs"
DATA_DIR = ROOT / "data"

OVERVIEW_CSV = OUTPUTS_DIR / "mpo_entity_health_overview_mainnet.csv"
POOL_HEALTH_CSV = OUTPUTS_DIR / "mpo_entity_pool_health_mainnet.csv"
POOL_MAPPING_CSV = OUTPUTS_DIR / "mpo_entity_pool_mapping_mainnet.csv"
LOW_PLEDGE_HISTORY_CSV = OUTPUTS_DIR / "zero_pledge_large_pool_history_mainnet.csv"
POOL_HISTORY_CSV = DATA_DIR / "koios_pool_history_mainnet.csv"
OUT_DOC = DOCS_DIR / "mpo-landscape-mainnet.md"

MARKER_EPOCHS = [400, 410, 584]
KEY_HISTORY_EPOCHS = [400, 410, 441, 448, 583, 615, 617]

CATEGORY_LABELS = {
    "declared_brand": "Declared MPO",
    "opaque_operational": "Opaque operational cluster",
    "provider_cluster": "Provider cluster",
    "platform_cluster": "Platform cluster",
    "unresolved_label": "Unresolved external label",
}

PRESSURE_LABELS = {
    "Very high": "Very high",
    "High": "High",
    "Moderate": "Moderate",
    "Limited": "Limited",
}


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def fetch_live_pool_rows() -> tuple[dict[str, dict], int, float, int]:
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


def load_supply_by_epoch() -> Dict[int, float]:
    totals = fetch_json("https://api.koios.rest/api/v1/totals")
    if not isinstance(totals, list):
        raise RuntimeError("Unexpected totals history response")
    return {int(row["epoch_no"]): int(row["supply"]) / 1_000_000.0 for row in totals}


def load_csv(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def stake_ada_live(row: dict) -> float:
    return int(row.get("active_stake") or 0) / 1_000_000.0


def pledge_ada_live(row: dict) -> float:
    return int(row.get("pledge") or 0) / 1_000_000.0


def pool_status_live(row: dict) -> str:
    return str(row.get("pool_status") or "")


def registered_only(rows: Iterable[dict]) -> List[dict]:
    return [row for row in rows if pool_status_live(row) == "registered"]


def positive_stake_only(rows: Iterable[dict]) -> List[dict]:
    return [row for row in registered_only(rows) if stake_ada_live(row) > 0.0]


def healthy_only(rows: Iterable[dict]) -> List[dict]:
    return [row for row in registered_only(rows) if stake_ada_live(row) >= 3_000_000.0]


def near_saturation_only(rows: Iterable[dict], saturation_point_ada: float) -> List[dict]:
    out: List[dict] = []
    for row in registered_only(rows):
        if saturation_point_ada <= 0.0:
            continue
        if stake_ada_live(row) / saturation_point_ada * 100.0 >= 80.0:
            out.append(row)
    return out


def median_or_zero(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def format_count(value: int) -> str:
    return f"{value:,}"


def format_pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}%"


def format_b_ada(value: float) -> str:
    return f"{value / 1_000_000_000.0:.3f}"


def format_m_ada(value: float) -> str:
    return f"{value / 1_000_000.0:.2f}"


def format_ada_value(value: float) -> str:
    if value == 0.0:
        return "0"
    if value < 0.001:
        return "<0.001"
    if value >= 1.0 and float(value).is_integer():
        return f"{value:,.0f}"
    if value >= 1_000_000.0:
        return f"{value:,.0f}"
    if value >= 10_000.0:
        return f"{value:,.0f}"
    if value >= 1.0:
        return f"{value:,.3f}"
    return f"{value:.6f}"


def format_pledge_from_lovelace(raw_lovelace: int) -> str:
    if raw_lovelace == 0:
        return "0"
    ada = raw_lovelace / 1_000_000.0
    return format_ada_value(ada)


def short_pool_id(pool_id: str) -> str:
    if len(pool_id) <= 18:
        return pool_id
    return f"{pool_id[:12]}...{pool_id[-6:]}"


def markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def network_snapshot(rows: List[dict], supply_ada: float, saturation_point_ada: float) -> dict:
    registered = registered_only(rows)
    positive = positive_stake_only(rows)
    healthy = healthy_only(rows)
    subscale = [row for row in registered if 100_000.0 <= stake_ada_live(row) < 3_000_000.0]
    dormant = [row for row in registered if 0.0 < stake_ada_live(row) < 100_000.0]
    zero_stake = [row for row in registered if stake_ada_live(row) == 0.0]
    near = near_saturation_only(rows, saturation_point_ada)
    zero_pledge = [row for row in registered if int(row.get("pledge") or 0) == 0]
    very_low_pledge = [row for row in registered if pledge_ada_live(row) < 10_000.0]
    margins = [float(row.get("margin") or 0.0) * 100.0 for row in registered]
    fixed_costs = [int(row.get("fixed_cost") or 0) / 1_000_000.0 for row in registered]
    pledges = [pledge_ada_live(row) for row in registered]
    return {
        "registered": len(registered),
        "positive": len(positive),
        "healthy": len(healthy),
        "subscale": len(subscale),
        "dormant": len(dormant),
        "zero_stake": len(zero_stake),
        "near": len(near),
        "zero_pledge": len(zero_pledge),
        "very_low_pledge": len(very_low_pledge),
        "stake_ada": sum(stake_ada_live(row) for row in registered),
        "pledge_ada": sum(pledge_ada_live(row) for row in registered),
        "median_pledge_ada": median_or_zero(pledges),
        "median_margin_pct": median_or_zero(margins),
        "avg_margin_pct": sum(margins) / len(margins) if margins else 0.0,
        "median_fixed_cost_ada": median_or_zero(fixed_costs),
        "avg_fixed_cost_ada": sum(fixed_costs) / len(fixed_costs) if fixed_costs else 0.0,
        "pct_supply": (sum(stake_ada_live(row) for row in registered) / supply_ada * 100.0) if supply_ada else 0.0,
    }


def attributed_snapshot(
    current_pool_rows: List[dict],
    live_rows_by_id: Dict[str, dict],
    supply_ada: float,
    saturation_point_ada: float,
) -> dict:
    live_rows = [live_rows_by_id[row["pool_id_bech32"]] for row in current_pool_rows]
    registered = registered_only(live_rows)
    positive = positive_stake_only(live_rows)
    healthy = healthy_only(live_rows)
    near = near_saturation_only(live_rows, saturation_point_ada)
    zero_pledge = [row for row in registered if int(row.get("pledge") or 0) == 0]
    very_low_pledge = [row for row in registered if pledge_ada_live(row) < 10_000.0]
    zero_near = [row for row in near if int(row.get("pledge") or 0) == 0]
    very_low_near = [row for row in near if pledge_ada_live(row) < 10_000.0]
    return {
        "registered": len(registered),
        "positive": len(positive),
        "healthy": len(healthy),
        "near": len(near),
        "stake_ada": sum(stake_ada_live(row) for row in registered),
        "pct_supply": (sum(stake_ada_live(row) for row in registered) / supply_ada * 100.0) if supply_ada else 0.0,
        "zero_pledge": len(zero_pledge),
        "zero_pledge_stake_ada": sum(stake_ada_live(row) for row in zero_pledge),
        "very_low_pledge": len(very_low_pledge),
        "very_low_pledge_stake_ada": sum(stake_ada_live(row) for row in very_low_pledge),
        "zero_near": len(zero_near),
        "zero_near_stake_ada": sum(stake_ada_live(row) for row in zero_near),
        "very_low_near": len(very_low_near),
        "very_low_near_stake_ada": sum(stake_ada_live(row) for row in very_low_near),
    }


def stacked_graph_snapshot(
    overview_rows: List[dict],
    current_pool_rows: List[dict],
    live_rows_by_id: Dict[str, dict],
    supply_ada: float,
    network: dict,
) -> dict:
    selected_entities = {
        row["display_name"]
        for row in overview_rows
        if int(row["current_registered_pool_count"]) >= 2
    }
    selected_rows: List[dict] = []
    seen_pool_ids: set[str] = set()
    for row in current_pool_rows:
        if row["display_name"] not in selected_entities:
            continue
        pool_id = row["pool_id_bech32"]
        if pool_id in seen_pool_ids:
            continue
        seen_pool_ids.add(pool_id)
        live = live_rows_by_id[pool_id]
        if pool_status_live(live) != "registered":
            continue
        selected_rows.append(live)

    stake_ada = sum(stake_ada_live(row) for row in selected_rows)
    pledge_ada = sum(pledge_ada_live(row) for row in selected_rows)
    return {
        "entities": len(selected_entities),
        "registered_pools": len(selected_rows),
        "stake_ada": stake_ada,
        "stake_pct_consensus": (stake_ada / network["stake_ada"] * 100.0) if network["stake_ada"] else 0.0,
        "stake_pct_supply": (stake_ada / supply_ada * 100.0) if supply_ada else 0.0,
        "pledge_ada": pledge_ada,
        "pledge_pct_network": (pledge_ada / network["pledge_ada"] * 100.0) if network["pledge_ada"] else 0.0,
        "pledge_pct_supply": (pledge_ada / supply_ada * 100.0) if supply_ada else 0.0,
        "active_over_pledge": (stake_ada / pledge_ada) if pledge_ada else 0.0,
    }


def entity_context_from_pools(current_pool_rows: List[dict]) -> Dict[str, dict]:
    context: Dict[str, dict] = {}
    for row in current_pool_rows:
        context.setdefault(
            row["display_name"],
            {
                "entity_id": row["entity_id"],
                "category": row["category"],
                "confidence": row["confidence"],
                "claim_type": row["claim_type"],
            },
        )
    return context


def build_history_markers(mapping_rows: List[dict], supply_by_epoch: Dict[int, float]) -> tuple[dict[str, dict[int, float]], dict[int, float]]:
    pool_to_entity = {row["pool_id_bech32"]: row["display_name"] for row in mapping_rows}
    entity_epoch_stake: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    total_by_epoch: dict[int, float] = defaultdict(float)

    with POOL_HISTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pool_id = row["pool_id_bech32"]
            entity_name = pool_to_entity.get(pool_id)
            if entity_name is None:
                continue
            epoch_no = int(row["epoch_no"])
            if epoch_no not in MARKER_EPOCHS:
                continue
            active_stake_ada = float(row["active_stake_ada"])
            entity_epoch_stake[entity_name][epoch_no] += active_stake_ada
            total_by_epoch[epoch_no] += active_stake_ada

    entity_markers: dict[str, dict[int, float]] = defaultdict(dict)
    pct_totals: dict[int, float] = {}
    for epoch_no in MARKER_EPOCHS:
        supply_ada = supply_by_epoch[epoch_no]
        pct_totals[epoch_no] = total_by_epoch[epoch_no] / supply_ada * 100.0 if supply_ada else 0.0
        for entity_name in {row["display_name"] for row in mapping_rows}:
            stake_ada = entity_epoch_stake[entity_name].get(epoch_no, 0.0)
            entity_markers[entity_name][epoch_no] = stake_ada / supply_ada * 100.0 if supply_ada else 0.0
    return entity_markers, pct_totals


def load_low_pledge_history() -> Dict[int, dict]:
    rows = load_csv(LOW_PLEDGE_HISTORY_CSV)
    return {int(row["epoch_no"]): row for row in rows}


def current_entity_table_rows(overview_rows: List[dict], context_by_entity: Dict[str, dict]) -> List[List[str]]:
    rows: List[List[str]] = []
    sorted_rows = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    for row in sorted_rows:
        context = context_by_entity[row["display_name"]]
        rows.append(
            [
                row["display_name"],
                CATEGORY_LABELS.get(context["category"], context["category"]),
                row["current_registered_pool_count"],
                row["current_live_positive_pool_count"],
                format_b_ada(float(row["current_stake_ada"])),
                format_pct(float(row["current_pct_supply"])),
                row["healthy_core_pool_count"],
                row["near_saturation_pool_count"],
                format_ada_value(float(row["median_live_pledge_ada"])),
                format_pct(float(row["avg_live_margin_pct"])),
                PRESSURE_LABELS.get(row["decentralization_pressure_tag"], row["decentralization_pressure_tag"]),
            ]
        )
    return rows


def low_pledge_entity_rows(
    current_pool_rows: List[dict],
    live_rows_by_id: Dict[str, dict],
    saturation_point_ada: float,
) -> List[List[str]]:
    per_entity: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in current_pool_rows:
        entity = row["display_name"]
        live = live_rows_by_id[row["pool_id_bech32"]]
        pledge_ada = pledge_ada_live(live)
        stake_ada = stake_ada_live(live)
        near = (stake_ada / saturation_point_ada * 100.0) >= 80.0 if saturation_point_ada else False
        per_entity[entity]["registered"] += 1
        if pledge_ada < 10_000.0:
            per_entity[entity]["very_low_count"] += 1
            per_entity[entity]["very_low_stake_ada"] += stake_ada
            if near:
                per_entity[entity]["very_low_near_count"] += 1
                per_entity[entity]["very_low_near_stake_ada"] += stake_ada
        if pledge_ada == 0.0:
            per_entity[entity]["zero_count"] += 1

    ranked = sorted(per_entity.items(), key=lambda item: item[1].get("very_low_near_stake_ada", 0.0), reverse=True)
    rows: List[List[str]] = []
    for entity, stats in ranked[:12]:
        if stats.get("very_low_count", 0.0) == 0.0:
            continue
        rows.append(
            [
                entity,
                format_count(int(stats["registered"])),
                format_count(int(stats["zero_count"])),
                format_count(int(stats["very_low_count"])),
                format_b_ada(stats["very_low_stake_ada"]),
                format_count(int(stats.get("very_low_near_count", 0.0))),
                format_b_ada(stats.get("very_low_near_stake_ada", 0.0)),
            ]
        )
    return rows


def largest_pool_rows(current_pool_rows: List[dict], live_rows_by_id: Dict[str, dict]) -> List[List[str]]:
    ranked = sorted(current_pool_rows, key=lambda row: float(row["current_active_stake_ada"]), reverse=True)
    rows: List[List[str]] = []
    for row in ranked[:20]:
        live = live_rows_by_id[row["pool_id_bech32"]]
        rows.append(
            [
                row["display_name"],
                row["ticker"] or "N/A",
                short_pool_id(row["pool_id_bech32"]),
                format_m_ada(float(row["current_active_stake_ada"])),
                format_pct(float(row["current_pct_saturation"])),
                format_pledge_from_lovelace(int(live.get("pledge") or 0)),
                format_pct(float(row["margin_pct"])),
                format_ada_value(float(row["fixed_cost_ada"])),
            ]
        )
    return rows


def current_pressure_bullets(overview_rows: List[dict]) -> List[str]:
    rows = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    bullets: List[str] = []
    if rows:
        first = rows[0]
        bullets.append(
            f"{first['display_name']} remains the largest cluster with {format_pct(float(first['current_pct_supply']))} of supply "
            f"and {first['current_registered_pool_count']} registered pools."
        )
    high_margin = [row for row in overview_rows if float(row["avg_live_margin_pct"]) >= 90.0]
    high_margin = sorted(high_margin, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    if high_margin:
        bullets.append(
            "The clusters with very high average margin are "
            + ", ".join(
                f"{row['display_name']} ({format_pct(float(row['avg_live_margin_pct']))}, {format_pct(float(row['current_pct_supply']))} of supply)"
                for row in high_margin[:5]
            )
            + "."
        )
    thin = [row for row in rows if int(row["current_live_positive_pool_count"]) < int(row["current_registered_pool_count"])]
    if thin:
        bullets.append(
            "The landscape is not homogeneous: "
            + ", ".join(f"{row['display_name']} ({row['current_live_positive_pool_count']}/{row['current_registered_pool_count']} with stake)" for row in thin[:4])
            + "."
        )
    return bullets


def history_leader_rows(overview_rows: List[dict], entity_markers: dict[str, dict[int, float]]) -> List[List[str]]:
    sorted_rows = sorted(overview_rows, key=lambda row: float(row["current_pct_supply"]), reverse=True)
    rows: List[List[str]] = []
    for row in sorted_rows[:15]:
        current_pct = float(row["current_pct_supply"])
        epoch_400 = entity_markers[row["display_name"]].get(400, 0.0)
        epoch_410 = entity_markers[row["display_name"]].get(410, 0.0)
        epoch_584 = entity_markers[row["display_name"]].get(584, 0.0)
        rows.append(
            [
                row["display_name"],
                format_pct(epoch_400),
                format_pct(epoch_410),
                format_pct(epoch_584),
                format_pct(current_pct),
                f"{current_pct - epoch_400:+.2f} pts",
            ]
        )
    return rows


def history_shift_bullets(overview_rows: List[dict], entity_markers: dict[str, dict[int, float]]) -> List[str]:
    diffs_400 = []
    diffs_584 = []
    for row in overview_rows:
        name = row["display_name"]
        current_pct = float(row["current_pct_supply"])
        diffs_400.append((current_pct - entity_markers[name].get(400, 0.0), name))
        diffs_584.append((current_pct - entity_markers[name].get(584, 0.0), name))

    down_400 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_400)[:5])
    up_400 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_400, reverse=True)[:5])
    down_584 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_584)[:5])
    up_584 = ", ".join(f"{name} ({delta:+.2f} pts)" for delta, name in sorted(diffs_584, reverse=True)[:5])
    return [
        f"Since epoch 400, the largest declines are {down_400}.",
        f"Since epoch 400, the largest increases are {up_400}.",
        f"Since epoch 584, the declines are more limited: {down_584}.",
        f"Since epoch 584, the most visible increases are {up_584}.",
    ]


def key_history_rows(low_pledge_history: Dict[int, dict]) -> List[List[str]]:
    rows: List[List[str]] = []
    for epoch_no in KEY_HISTORY_EPOCHS:
        row = low_pledge_history.get(epoch_no)
        if row is None:
            continue
        rows.append(
            [
                str(epoch_no),
                row["source"],
                row["gt70_pool_count"],
                row["very_low_pledge_gt70_pool_count"],
                row["zero_pledge_gt70_pool_count"],
                row["very_low_pledge_ge80sat_pool_count"],
                row["zero_pledge_ge80sat_pool_count"],
            ]
        )
    return rows


def write_report() -> Path:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    doc = f"""# MPO Landscape Report (Mainnet)

_Built on {now_utc}._

This standalone MPO report has been merged into the canonical [Pool Landscape Report (Mainnet)](./pool-landscape-mainnet.md).

Use that document for:

- current network snapshot
- current entity / MPO concentration layer
- low-pledge MPO pattern
- historical MPO composition and low-pledge regime analysis

Supporting MPO-specific outputs remain available here:

- `../outputs/mpo_entity_deep_dive_mainnet.md`
- `../outputs/mpo_entity_pool_health_summary_mainnet.md`
- `../outputs/zero_pledge_large_pool_history_mainnet_summary.md`
"""

    OUT_DOC.write_text(doc)
    return OUT_DOC


def main() -> None:
    out_path = write_report()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
