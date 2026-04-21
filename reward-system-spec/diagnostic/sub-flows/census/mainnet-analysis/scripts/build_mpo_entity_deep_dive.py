#!/usr/bin/env python3
"""
Build a deep-dive MPO entity attribution document from raw Koios data.

Outputs:
- scenarii-evaluation/figures/mpo_entity_current_distribution_mainnet.png
- scenarii-evaluation/outputs/mpo_entity_deep_dive_mainnet.md
- scenarii-evaluation/outputs/mpo_entity_summary_mainnet.csv
- scenarii-evaluation/outputs/mpo_entity_pool_mapping_mainnet.csv
- scenarii-evaluation/outputs/mpo_unresolved_group_labels_mainnet.csv
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.parse import urlparse

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class EntityProfile:
    entity_id: str
    display_name: str
    category: str
    visibility: str
    confidence: str
    claim_type: str
    rationale: str
    caution: str
    patterns: Tuple[str, ...]


@dataclass
class EntityStats:
    profile: EntityProfile
    matched_pool_ids: set[str] = field(default_factory=set)
    active_pool_ids: set[str] = field(default_factory=set)
    current_stake_ada: float = 0.0
    epoch_400_stake_ada: float = 0.0
    epoch_410_stake_ada: float = 0.0
    epoch_584_stake_ada: float = 0.0
    tickers: Counter[str] = field(default_factory=Counter)
    meta_domains: Counter[str] = field(default_factory=Counter)
    pool_groups: Counter[str] = field(default_factory=Counter)
    adastat_groups: Counter[str] = field(default_factory=Counter)
    balance_groups: Counter[str] = field(default_factory=Counter)
    reward_addrs: Counter[str] = field(default_factory=Counter)
    relay_hints: Counter[str] = field(default_factory=Counter)
    pool_samples: List[Tuple[str, float]] = field(default_factory=list)


ENTITY_PROFILES: List[EntityProfile] = [
    EntityProfile(
        entity_id="BINANCE",
        display_name="Binance",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="BNP ticker family and Binance-branded metadata paths are first-party signals; Koios, AdaStat, and BalanceAnalytics all label the cluster as Binance.",
        caution="Some historical pools are only weakly labeled in current snapshots, but the branded metadata paths keep the attribution stable.",
        patterns=(
            r"\bBINANCE\b",
            r"\bBNP\d*\b",
            r"binancepool\.bnp",
            r"binance\.cardano",
            r"binance-ada",
            r"binance\.com",
        ),
    ),
    EntityProfile(
        entity_id="COINBASE_BISON",
        display_name="Coinbase / bison.run",
        category="opaque_operational",
        visibility="Hidden behind hosted metadata / relay infrastructure",
        confidence="Medium-High",
        claim_type="Same operational cluster",
        rationale="The pools are tied together by hashed bison.run and herd.run metadata / relay hosts, while Koios and BalanceAnalytics surface the operator label as Coinbase.",
        caution="This is strong evidence of common operational control, but the legal attribution to Coinbase comes from third-party group labels rather than first-party pool metadata.",
        patterns=(
            r"\bCOINBASE\b",
            r"bison\.run",
            r"herd\.run",
        ),
    ),
    EntityProfile(
        entity_id="IOG",
        display_name="IOG",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="IOG pools publicly identify through IOG tickers, iohk.io / iog.io domains, and branded relay hostnames.",
        caution="None beyond normal snapshot limitations.",
        patterns=(
            r"\bIOG\b",
            r"\bIOGP?\d*\b",
            r"iog\.io",
            r"iohk\.io",
            r"pools\.iohk\.io",
        ),
    ),
    EntityProfile(
        entity_id="EMURGO",
        display_name="Emurgo",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="EMUR* tickers, pools.emurgo.io metadata, and third-party group labels all point to the same public brand.",
        caution="Some BalanceAnalytics rows are sparse, but the branded metadata is enough on its own.",
        patterns=(
            r"\bEMURGO\b",
            r"\bEMUR\d*\b",
            r"emurgo\.io",
            r"pools\.emurgo\.io",
        ),
    ),
    EntityProfile(
        entity_id="UPBIT",
        display_name="Upbit",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="The cluster is directly branded by UPBIT tickers and upbit.com metadata endpoints, with Koios / AdaStat corroboration.",
        caution="None beyond normal snapshot limitations.",
        patterns=(
            r"\bUPBIT\b",
            r"upbit\.com",
        ),
    ),
    EntityProfile(
        entity_id="EVERSTAKE",
        display_name="Everstake",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="everstake.one metadata plus EVRST / EVERS / ESTK ticker family provide direct brand continuity across pools.",
        caution="Some pools only keep the brand in metadata rather than in the group label.",
        patterns=(
            r"everstake\.one",
            r"\bEVRST\b",
            r"\bEVERS\b",
            r"\bESTK\b",
            r"\bEVE\b",
        ),
    ),
    EntityProfile(
        entity_id="AUTOSTAKE",
        display_name="AutoStake",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="AutoStake pools expose autostake.com metadata and autostake-branded relays across the fleet, with a consistent AUTO ticker surface on the current live rows.",
        caution="The Koios pool_group labels vary across the fleet, so the brand is clearer in metadata and relays than in third-party grouping fields.",
        patterns=(
            r"\bAUTO\b",
            r"autostake\.com",
            r"cardano-relays\.autostake\.com",
        ),
    ),
    EntityProfile(
        entity_id="WAVE",
        display_name="Wave / Wavepool",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="The operator is visible through wavepool.digital / wavemkr metadata, WAVE labels, and consistent third-party groupings.",
        caution="A few pool tickers differ from the WAV* family, so the group label matters more than ticker uniformity.",
        patterns=(
            r"\bWAVE\b",
            r"wavepool\.digital",
            r"wavemkr\.github\.io",
            r"\bWAV\d*\b",
        ),
    ),
    EntityProfile(
        entity_id="BLOCKDAEMON",
        display_name="Blockdaemon",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="The cluster exposes cardano.blockdaemon.com metadata together with BD tickers and matching third-party labels.",
        caution="Some current rows no longer expose metadata, but the branding is consistent on the rest.",
        patterns=(
            r"\bBD\b",
            r"\bBD\d+\b",
            r"blockdaemon\.com",
        ),
    ),
    EntityProfile(
        entity_id="ETORO",
        display_name="eToro",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="ETO* tickers, etoro-branded metadata, and matching Koios / AdaStat / BalanceAnalytics labels make this a straightforward attribution.",
        caution="Some older rows are partially unlabeled, but the branded pools anchor the cluster.",
        patterns=(
            r"\bETORO\b",
            r"\bETO\d+\b",
            r"etoro\.com",
            r"etoro-spo",
        ),
    ),
    EntityProfile(
        entity_id="ONE_PERCENT",
        display_name="1PCT",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="1PCT ticker family, 1percentpool.eu metadata, and convergence across all group-label sources make the cluster explicit.",
        caution="None beyond normal snapshot limitations.",
        patterns=(
            r"\b1PCT\d*\b",
            r"1percentpool\.eu",
            r"\b1PCT\b",
        ),
    ),
    EntityProfile(
        entity_id="CARDANO_FOUNDATION",
        display_name="Cardano Foundation",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="CF tickers, cardanofoundation.org metadata, and a shared reward address make the attribution explicit.",
        caution="This is a governance / institutional cluster rather than a hidden operator cluster.",
        patterns=(
            r"cardanofoundation\.org",
        ),
    ),
    EntityProfile(
        entity_id="FIGMENT",
        display_name="Figment",
        category="provider_cluster",
        visibility="Provider-mediated cluster",
        confidence="Medium-High",
        claim_type="Same provider cluster",
        rationale="Koios and BalanceAnalytics identify the cluster as Figment, while some external views surface Ledger as the client-facing brand on top of the same provider layer.",
        caution="This looks like a common managed-staking provider cluster; the end-client retail brand is not always the same as the operator brand.",
        patterns=(
            r"\bFIGMENT\b",
            r"\bFGMT\d*\b",
            r"\bBTV\d*\b",
        ),
    ),
    EntityProfile(
        entity_id="YUTA",
        display_name="YUTA",
        category="opaque_operational",
        visibility="Multi-brand operator cluster",
        confidence="Medium",
        claim_type="Same managed cluster",
        rationale="The YUTA label links multiple domains and brands together across Koios / BalanceAnalytics, suggesting one managed umbrella rather than one public-facing brand.",
        caution="This is not a first-party self-declared umbrella. The attribution relies on third-party clustering plus repeated multi-brand grouping.",
        patterns=(
            r"\bYUTA\b",
            r"coinzzz\.jp",
            r"tokyostaker\.com",
            r"katanapool\.com",
        ),
    ),
    EntityProfile(
        entity_id="ROCKX",
        display_name="RockX",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="rockx.com metadata and ROCKX labels identify the operator directly.",
        caution="Some tickers are symbolic rather than obviously branded, so metadata domain is the stronger signal.",
        patterns=(
            r"rockx\.com",
            r"\bROCKX\b",
        ),
    ),
    EntityProfile(
        entity_id="P2P",
        display_name="P2P",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="P2P / PPCX tickers and p2p.org / p2p.world metadata make the provider explicit.",
        caution="None beyond normal snapshot limitations.",
        patterns=(
            r"\bP2P\b",
            r"\bPPCX\d*\b",
            r"p2p\.org",
            r"p2p\.world",
        ),
    ),
    EntityProfile(
        entity_id="SPIRE",
        display_name="Spire",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="spirestaking.com / spireblockchain.com metadata and SPIRE labels show direct public continuity.",
        caution="The cluster spans two closely related branded domains, but both are clearly operator-controlled.",
        patterns=(
            r"\bSPIRE\b",
            r"\bSPIR\d*\b",
            r"spirestaking\.com",
            r"spireblockchain\.com",
        ),
    ),
    EntityProfile(
        entity_id="BLOOM",
        display_name="Bloom",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="Bloompool metadata and BLOOM labels provide first-party continuity.",
        caution="The public brand is smaller than the largest custodial clusters, but the identity evidence is clean.",
        patterns=(
            r"\bBLOOM\b",
            r"bloompool\.io",
        ),
    ),
    EntityProfile(
        entity_id="BIGLAZYCAT",
        display_name="BigLazyCat",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="The BLC family is tied together by biglazycat.com metadata and relay hostnames, with consistent BigLazyCat branding across current and historical registration metadata.",
        caution="One current pool drops the visible ticker, so the metadata domains and relay naming are stronger than ticker continuity alone.",
        patterns=(
            r"\bBLC\d*\b",
            r"biglazycat\.com",
        ),
    ),
    EntityProfile(
        entity_id="OCEAN",
        display_name="AdaOcean",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="OCEAN / OCEA ticker family and adaocean.com metadata align across the cluster.",
        caution="Some pools use OCEA* suffixes instead of a single ticker family root.",
        patterns=(
            r"\bOCEAN\b",
            r"\bOCEA\d*\b",
            r"adaocean\.com",
        ),
    ),
    EntityProfile(
        entity_id="RAID",
        display_name="RAID",
        category="declared_brand",
        visibility="Open public brand",
        confidence="High",
        claim_type="Same operator cluster",
        rationale="RAID ticker family is consistent across the cluster and is reinforced by the Koios group label.",
        caution="Many rows use URL shorteners, so the ticker / group label is more informative than the metadata host.",
        patterns=(
            r"\bRAID\d*\b",
            r"\bRAID\b",
        ),
    ),
    EntityProfile(
        entity_id="KILN",
        display_name="Kiln",
        category="provider_cluster",
        visibility="Open provider brand",
        confidence="High",
        claim_type="Same provider cluster",
        rationale="kiln.fi metadata and KILN tickers provide direct branding even where Koios groups them under an Adalite surface.",
        caution="Some third-party sources place these pools under ADALITE, so the provider brand and platform surface should not be conflated.",
        patterns=(
            r"kiln\.fi",
            r"\bKILN\d*\b",
        ),
    ),
    EntityProfile(
        entity_id="NUFI",
        display_name="NuFi",
        category="provider_cluster",
        visibility="Open provider brand",
        confidence="High",
        claim_type="Same provider cluster",
        rationale="NuFi metadata and NUFI ticker family make the provider explicit.",
        caution="Some Koios labels group these pools under ADALITE, which appears to be a platform-level surface rather than a legal-entity claim.",
        patterns=(
            r"nu\.fi",
            r"\bNUFI\d*\b",
        ),
    ),
    EntityProfile(
        entity_id="ADALITE_PLATFORM",
        display_name="Adalite platform cluster",
        category="platform_cluster",
        visibility="Platform-mediated cluster",
        confidence="Low-Medium",
        claim_type="Not asserted as same legal entity",
        rationale="The ADALITE label appears to aggregate pools exposed through a wallet / platform surface, including pools that are better attributed to brands like Kiln or NuFi.",
        caution="This profile is shown to document ambiguity, not to claim one underlying legal entity.",
        patterns=(
            r"\bADALITE\b",
        ),
    ),
    EntityProfile(
        entity_id="CHUCK_BUX",
        display_name="CHUCK BUX",
        category="unresolved_label",
        visibility="External label only",
        confidence="Low",
        claim_type="Unresolved cluster label",
        rationale="The cluster is visible in BalanceAnalytics / Koios labels, but public first-party branding is weak or absent across most pools.",
        caution="This cluster is important economically but should not be overclaimed as a proved single legal entity from the raw data alone.",
        patterns=(
            r"CHUCK BUX",
        ),
    ),
    EntityProfile(
        entity_id="STAKEBOWL",
        display_name="StakeBowl",
        category="opaque_operational",
        visibility="Muted public brand",
        confidence="Medium",
        claim_type="Same operator cluster",
        rationale="SBP1 and SBP2 share the same reward address, relay endpoint, paired neoply.io metadata paths, and a stable STBL grouping, which together indicate one operator cluster historically surfaced as StakeBowl.",
        caution="The current live metadata is not explicitly stakebowl.io-branded, so the public brand continuity relies partly on historical registration metadata rather than on the current metadata host alone.",
        patterns=(
            r"\bSBP1\b",
            r"\bSBP2\b",
            r"\bSTBL\b",
            r"neoply\.io/ada_sbp[12]\.json",
            r"stake1uylsrplhl3ryx02rtehygp2v0uxxanh2hw32txfajm7uykqxxfusy",
        ),
    ),
]


CATEGORY_LABELS = {
    "declared_brand": "Declared MPO",
    "opaque_operational": "Opaque operational cluster",
    "provider_cluster": "Provider cluster",
    "platform_cluster": "Platform-mediated cluster",
    "unresolved_label": "Unresolved external label",
}

CATEGORY_COLORS = {
    "declared_brand": "#0b4f6c",
    "opaque_operational": "#9c6644",
    "provider_cluster": "#4c956c",
    "platform_cluster": "#8d99ae",
    "unresolved_label": "#c1121f",
}

EPOCH_MARKERS = [400, 410, 584]
NOISY_VALUES = {"", "None", "null", "n"}


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def load_live_rows() -> Tuple[List[dict], int, float]:
    pool_rows: List[dict] = []
    offset = 0
    limit = 1000
    while True:
        page = fetch_json(f"https://api.koios.rest/api/v1/pool_list?offset={offset}&limit={limit}")
        if not isinstance(page, list):
            raise RuntimeError("Unexpected pool_list response")
        pool_rows.extend(page)
        if len(page) < limit:
            break
        offset += len(page)

    group_rows: List[dict] = []
    offset = 0
    while True:
        page = fetch_json(f"https://api.koios.rest/api/v1/pool_groups?offset={offset}&limit={limit}")
        if not isinstance(page, list):
            raise RuntimeError("Unexpected pool_groups response")
        group_rows.extend(page)
        if len(page) < limit:
            break
        offset += len(page)
    groups_by_pool = {row["pool_id_bech32"]: row for row in group_rows}

    merged: List[dict] = []
    for row in pool_rows:
        merged_row = dict(row)
        groups = groups_by_pool.get(row["pool_id_bech32"], {})
        merged_row["adastat_group"] = groups.get("adastat_group")
        merged_row["balanceanalytics_group"] = groups.get("balanceanalytics_group")
        merged.append(merged_row)

    tip = fetch_json("https://api.koios.rest/api/v1/tip")
    if not isinstance(tip, list) or not tip:
        raise RuntimeError("Unexpected tip response")
    live_epoch = int(tip[0]["epoch_no"])
    totals = fetch_json(f"https://api.koios.rest/api/v1/totals?_epoch_no={live_epoch}")
    if not isinstance(totals, list) or not totals:
        raise RuntimeError("Unexpected totals response")
    supply_ada = int(totals[0]["supply"]) / 1_000_000.0
    return merged, live_epoch, supply_ada


def load_supply_by_epoch() -> Dict[int, float]:
    totals = fetch_json("https://api.koios.rest/api/v1/totals")
    if not isinstance(totals, list):
        raise RuntimeError("Unexpected totals history response")
    return {int(row["epoch_no"]): int(row["supply"]) / 1_000_000.0 for row in totals}


def build_haystack(row: dict) -> str:
    relay_text_parts: List[str] = []
    for relay in row.get("relays") or []:
        relay_text_parts.extend(
            [
                str(relay.get("dns") or ""),
                str(relay.get("ipv4") or ""),
                str(relay.get("ipv6") or ""),
            ]
        )
    return " | ".join(
        [
            str(row.get("ticker") or ""),
            str(row.get("pool_group") or ""),
            str(row.get("adastat_group") or ""),
            str(row.get("balanceanalytics_group") or ""),
            str(row.get("meta_url") or ""),
            str(row.get("reward_addr") or ""),
            json.dumps(row.get("owners") or []),
            " ".join(relay_text_parts),
        ]
    )


def meta_domain(url: str | None) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.lower()


def relay_hints(relays: Iterable[dict]) -> Iterable[str]:
    for relay in relays or []:
        if relay.get("dns"):
            yield str(relay["dns"]).lower()
        elif relay.get("ipv4"):
            yield str(relay["ipv4"])
        elif relay.get("ipv6"):
            yield str(relay["ipv6"])


def active_stake_ada(row: dict) -> float:
    raw = row.get("active_stake")
    if raw in (None, "", 0, "0"):
        return 0.0
    return int(raw) / 1_000_000.0


def match_profile(row: dict, compiled_profiles: List[Tuple[EntityProfile, List[re.Pattern[str]]]]) -> str | None:
    haystack = build_haystack(row)
    for profile, patterns in compiled_profiles:
        if any(pattern.search(haystack) for pattern in patterns):
            return profile.entity_id
    return None


def build_entity_stats(
    live_rows: List[dict],
    summary_path: Path,
) -> Tuple[Dict[str, EntityStats], Dict[str, str], List[dict]]:
    profiles_by_id = {profile.entity_id: profile for profile in ENTITY_PROFILES}
    compiled_profiles = [(profile, [re.compile(pattern, re.I) for pattern in profile.patterns]) for profile in ENTITY_PROFILES]
    entity_stats = {profile.entity_id: EntityStats(profile=profile) for profile in ENTITY_PROFILES}
    pool_to_entity: Dict[str, str] = {}
    mapping_rows: List[dict] = []

    for row in live_rows:
        entity_id = match_profile(row, compiled_profiles)
        if entity_id is None:
            continue
        pool_id = row["pool_id_bech32"]
        pool_to_entity[pool_id] = entity_id
        stats = entity_stats[entity_id]
        stats.matched_pool_ids.add(pool_id)

        stake_ada = active_stake_ada(row)
        if stake_ada > 0:
            stats.active_pool_ids.add(pool_id)
            stats.current_stake_ada += stake_ada

        ticker = str(row.get("ticker") or "").strip()
        if ticker:
            stats.tickers[ticker] += 1

        domain = meta_domain(row.get("meta_url"))
        if domain:
            stats.meta_domains[domain] += 1

        if row.get("pool_group"):
            stats.pool_groups[str(row["pool_group"])] += 1
        if row.get("adastat_group"):
            stats.adastat_groups[str(row["adastat_group"])] += 1
        if row.get("balanceanalytics_group"):
            stats.balance_groups[str(row["balanceanalytics_group"])] += 1
        if row.get("reward_addr"):
            stats.reward_addrs[str(row["reward_addr"])] += 1

        for hint in relay_hints(row.get("relays") or []):
            stats.relay_hints[hint] += 1

        stats.pool_samples.append((pool_id, stake_ada))

        mapping_rows.append(
            {
                "entity_id": entity_id,
                "display_name": stats.profile.display_name,
                "category": stats.profile.category,
                "confidence": stats.profile.confidence,
                "claim_type": stats.profile.claim_type,
                "pool_id_bech32": pool_id,
                "ticker": ticker,
                "pool_status": str(row.get("pool_status") or ""),
                "current_active_stake_ada": f"{stake_ada:.3f}",
                "meta_domain": domain,
                "meta_url": str(row.get("meta_url") or ""),
                "pool_group": str(row.get("pool_group") or ""),
                "adastat_group": str(row.get("adastat_group") or ""),
                "balanceanalytics_group": str(row.get("balanceanalytics_group") or ""),
                "reward_addr": str(row.get("reward_addr") or ""),
                "relay_hints": "; ".join(sorted(set(relay_hints(row.get("relays") or [])))),
            }
        )

    for stats in entity_stats.values():
        stats.pool_samples.sort(key=lambda item: item[1], reverse=True)

    write_pool_mapping(mapping_rows, summary_path)
    return entity_stats, pool_to_entity, mapping_rows


def write_pool_mapping(rows: List[dict], out_path: Path) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_history_markers(history_path: Path, pool_to_entity: Dict[str, str], entity_stats: Dict[str, EntityStats]) -> None:
    with history_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity_id = pool_to_entity.get(row["pool_id_bech32"])
            if entity_id is None:
                continue
            active_stake = row.get("active_stake_ada") or ""
            if not active_stake:
                continue
            stake_ada = float(active_stake)
            epoch_no = int(row["epoch_no"])
            stats = entity_stats[entity_id]
            if epoch_no == 400:
                stats.epoch_400_stake_ada += stake_ada
            elif epoch_no == 410:
                stats.epoch_410_stake_ada += stake_ada
            elif epoch_no == 584:
                stats.epoch_584_stake_ada += stake_ada


def top_items(counter: Counter[str], limit: int = 4) -> str:
    items = [(key, count) for key, count in counter.items() if key and key not in NOISY_VALUES]
    items.sort(key=lambda item: item[1], reverse=True)
    items = items[:limit]
    if not items:
        return "n/a"
    return ", ".join(f"{key} ({count})" for key, count in items)


def top_samples(stats: EntityStats, limit: int = 3) -> str:
    samples = [pool_id for pool_id, _ in stats.pool_samples[:limit]]
    return ", ".join(samples) if samples else "n/a"


def short_basis(stats: EntityStats) -> str:
    parts: List[str] = []
    if stats.tickers:
        parts.append(f"tickers {top_items(stats.tickers, 3)}")
    if stats.meta_domains:
        parts.append(f"domains {top_items(stats.meta_domains, 2)}")
    label_parts: List[str] = []
    if stats.pool_groups:
        label_parts.append(f"Koios {top_items(stats.pool_groups, 1)}")
    if stats.adastat_groups:
        label_parts.append(f"AdaStat {top_items(stats.adastat_groups, 1)}")
    if stats.balance_groups:
        label_parts.append(f"BalanceAnalytics {top_items(stats.balance_groups, 1)}")
    if label_parts:
        parts.append("; ".join(label_parts))
    return " | ".join(parts) if parts else "n/a"


def summary_basis_text(stats: EntityStats) -> str:
    return stats.profile.rationale.replace("|", "/")


def render_current_distribution(
    out_path: Path,
    rows: List[Tuple[EntityStats, float]],
) -> None:
    top_rows = rows[:12]
    labels = [stats.profile.display_name for stats, _ in top_rows]
    values = [share for _, share in top_rows]
    colors = [CATEGORY_COLORS[stats.profile.category] for stats, _ in top_rows]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.set_xlabel("Share of Koios supply (%)")
    ax.set_ylabel("Entity / cluster")

    for bar, value in zip(bars, values[::-1]):
        ax.text(
            bar.get_width() + 0.08,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}%",
            va="center",
            fontsize=9,
        )

    legend_handles = []
    for category, color in CATEGORY_COLORS.items():
        legend_handles.append(plt.Line2D([0], [0], color=color, lw=8, label=CATEGORY_LABELS[category]))
    ax.legend(handles=legend_handles, loc="lower right")
    ax.set_xlim(0, max(values) + 1.5 if values else 1.0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def write_entity_summary_csv(
    out_path: Path,
    rows: List[Tuple[EntityStats, float, float, float, float]],
) -> None:
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "entity_id",
                "display_name",
                "category",
                "visibility",
                "confidence",
                "claim_type",
                "matched_pools",
                "active_pools",
                "current_stake_b_ada",
                "current_pct_supply",
                "epoch_400_pct_supply",
                "epoch_410_pct_supply",
                "epoch_584_pct_supply",
                "evidence_basis",
            ]
        )
        for stats, current_pct, pct_400, pct_410, pct_584 in rows:
            writer.writerow(
                [
                    stats.profile.entity_id,
                    stats.profile.display_name,
                    stats.profile.category,
                    stats.profile.visibility,
                    stats.profile.confidence,
                    stats.profile.claim_type,
                    len(stats.matched_pool_ids),
                    len(stats.active_pool_ids),
                    f"{stats.current_stake_ada / 1_000_000_000.0:.3f}",
                    f"{current_pct:.2f}",
                    f"{pct_400:.2f}",
                    f"{pct_410:.2f}",
                    f"{pct_584:.2f}",
                    short_basis(stats),
                ]
            )


def unresolved_group_rows(live_rows: List[dict], matched_pool_ids: set[str], supply_ada: float) -> List[dict]:
    grouped: Dict[str, dict] = defaultdict(lambda: {"count": 0, "stake_ada": 0.0, "sample_domains": Counter(), "sample_balance": Counter(), "sample_adastat": Counter()})
    for row in live_rows:
        if row["pool_id_bech32"] in matched_pool_ids:
            continue
        group_label = str(row.get("pool_group") or "").strip()
        if not group_label:
            continue
        grouped[group_label]["count"] += 1
        grouped[group_label]["stake_ada"] += active_stake_ada(row)
        domain = meta_domain(row.get("meta_url"))
        if domain:
            grouped[group_label]["sample_domains"][domain] += 1
        if row.get("balanceanalytics_group"):
            grouped[group_label]["sample_balance"][str(row["balanceanalytics_group"])] += 1
        if row.get("adastat_group"):
            grouped[group_label]["sample_adastat"][str(row["adastat_group"])] += 1

    rows: List[dict] = []
    for label, payload in grouped.items():
        if payload["count"] <= 5 and payload["stake_ada"] < 100_000_000:
            continue
        rows.append(
            {
                "group_label": label,
                "active_pools": payload["count"],
                "current_stake_b_ada": round(payload["stake_ada"] / 1_000_000_000.0, 3),
                "current_pct_supply": round(payload["stake_ada"] / supply_ada * 100.0, 2),
                "sample_domains": top_items(payload["sample_domains"], 3),
                "adastat_labels": top_items(payload["sample_adastat"], 2),
                "balanceanalytics_labels": top_items(payload["sample_balance"], 2),
            }
        )
    rows.sort(key=lambda row: row["current_stake_b_ada"], reverse=True)
    return rows


def write_unresolved_csv(out_path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def should_include_in_summary(stats: EntityStats) -> bool:
    headline_stake = max(
        stats.current_stake_ada,
        stats.epoch_400_stake_ada,
        stats.epoch_410_stake_ada,
        stats.epoch_584_stake_ada,
    )
    has_scale = len(stats.matched_pool_ids) >= 6 or stats.current_stake_ada >= 150_000_000.0
    return has_scale and headline_stake >= 50_000_000.0


def category_totals(rows: List[Tuple[EntityStats, float]]) -> Dict[str, float]:
    out: Dict[str, float] = defaultdict(float)
    for stats, pct in rows:
        out[stats.profile.category] += pct
    return out


def write_markdown(
    out_path: Path,
    figure_name: str,
    progression_figure_name: str,
    live_epoch: int,
    live_supply_ada: float,
    summary_rows: List[Tuple[EntityStats, float, float, float, float]],
    unresolved_rows: List[dict],
) -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    category_pct = category_totals([(stats, current_pct) for stats, current_pct, _, _, _ in summary_rows])

    lines: List[str] = [
        "# MPO Entity Attribution Deep Dive (Mainnet)",
        "",
        f"_Snapshot built from live Koios data at epoch `{live_epoch}` on `{now_utc}` plus local historical pool history._",
        "",
        "## Objective",
        "",
        "Move from pool-level concentration toward entity-level concentration, while being explicit about what is proved, what is inferred, and what remains unresolved.",
        "",
        "## Why this is hard",
        "",
        "Cardano pool registration data does not contain a canonical `legal_entity_id` field. Multi-pool operator (MPO) analysis therefore has to reconstruct operator clusters from observable signals.",
        "",
        "The document distinguishes four different outcomes:",
        "",
        "| Outcome | Meaning | Example |",
        "| --- | --- | --- |",
        "| Declared MPO | Public brand appears directly in metadata, ticker families, and cross-source labels. | Binance, IOG, 1PCT |",
        "| Opaque operational cluster | Pools are clearly linked operationally, but the public brand is muted or hidden. | Coinbase / bison.run |",
        "| Provider / platform cluster | Common staking provider or wallet surface is visible, but not always one legal operator. | Figment, Kiln, NuFi, Adalite surface |",
        "| Unresolved label | Third-party clustering says the pools belong together, but first-party evidence is weak. | CHUCK BUX |",
        "",
        "## Evidence hierarchy used here",
        "",
        "| Strength | What counts as evidence | How it is used |",
        "| --- | --- | --- |",
        "| Strong | First-party metadata domains, branded ticker family, branded relay DNS, shared reward address where public branding also exists | Enough to attribute a declared MPO |",
        "| Medium | Convergent third-party labels across Koios, AdaStat, and BalanceAnalytics | Supports attribution or upgrades confidence |",
        "| Medium | Shared hosted metadata / relay infrastructure with repeated hashed subdomains | Supports an operational cluster, not necessarily a legal-entity claim |",
        "| Weak / excluded alone | Generic shorteners, generic code hosting, generic cloud buckets, common hosting platforms | Not used on their own to claim same entity |",
        "",
        "## What I deliberately do not use alone",
        "",
        "- `tinyurl.com`, `git.io`, `raw.githubusercontent.com`, and similar generic shorteners / code hosting.",
        "- Shared hosting surfaces such as generic metadata platforms, unless a branded domain or cross-source group labels also exist.",
        "- A single external group label with no supporting metadata, unless the cluster is kept explicitly in an unresolved bucket.",
        "",
        "## Current distribution",
        "",
        f"- Koios supply used for percentages: **{live_supply_ada / 1_000_000_000.0:.3f}B ADA**",
        f"- Declared MPO share captured in this document: **{category_pct['declared_brand']:.2f}%**",
        f"- Opaque operational clusters captured here: **{category_pct['opaque_operational']:.2f}%**",
        f"- Provider / platform clusters captured here: **{category_pct['provider_cluster'] + category_pct['platform_cluster']:.2f}%**",
        f"- Unresolved external-label clusters captured here: **{category_pct['unresolved_label']:.2f}%**",
        "",
        f"![Current MPO entity distribution](../figures/{figure_name})",
        "",
        "## Summary table",
        "",
        "| Entity / cluster | Type | Active pools | Current stake (B ADA) | Current % supply | Epoch 400 % | Epoch 410 % | Epoch 584 % | Confidence | Why linked |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    for stats, current_pct, pct_400, pct_410, pct_584 in summary_rows:
        lines.append(
            f"| {stats.profile.display_name} | {CATEGORY_LABELS[stats.profile.category]} | {len(stats.active_pool_ids)} | "
            f"{stats.current_stake_ada / 1_000_000_000.0:.3f} | {current_pct:.2f}% | {pct_400:.2f}% | {pct_410:.2f}% | {pct_584:.2f}% | "
            f"{stats.profile.confidence} | {summary_basis_text(stats)} |"
        )

    lines.extend(
        [
            "",
            "## Detailed profiles",
            "",
        ]
    )

    for stats, current_pct, pct_400, pct_410, pct_584 in summary_rows:
        lines.extend(
            [
                f"### {stats.profile.display_name}",
                "",
                f"- Type: **{CATEGORY_LABELS[stats.profile.category]}**",
                f"- Visibility: **{stats.profile.visibility}**",
                f"- Claim level: **{stats.profile.claim_type}**",
                f"- Confidence: **{stats.profile.confidence}**",
                f"- Live active pools: **{len(stats.active_pool_ids)}** out of **{len(stats.matched_pool_ids)}** matched pool ids",
                f"- Live active stake: **{stats.current_stake_ada / 1_000_000_000.0:.3f}B ADA** (**{current_pct:.2f}%** of Koios supply)",
                f"- Historical markers: epoch 400 = **{pct_400:.2f}%**, epoch 410 = **{pct_410:.2f}%**, epoch 584 = **{pct_584:.2f}%** of supply",
                f"- Deduction: {stats.profile.rationale}",
                f"- Caution: {stats.profile.caution}",
                f"- Tickers seen: {top_items(stats.tickers, 6)}",
                f"- Metadata domains: {top_items(stats.meta_domains, 4)}",
                f"- Koios `pool_group`: {top_items(stats.pool_groups, 3)}",
                f"- AdaStat group: {top_items(stats.adastat_groups, 3)}",
                f"- BalanceAnalytics group: {top_items(stats.balance_groups, 3)}",
                f"- Repeated reward addresses: {sum(1 for _, count in stats.reward_addrs.items() if count > 1)} repeated addresses across the cluster",
                f"- Relay hints: {top_items(stats.relay_hints, 4)}",
                f"- Example pools: {top_samples(stats, 3)}",
                "",
            ]
        )

    lines.extend(
        [
            "## Hidden / unresolved side of the MPO problem",
            "",
            "Not every economically significant cluster is self-declared. That is precisely why a Sybil / MPO lens matters: pool count alone can overstate decentralization if multiple pools are under one operational umbrella.",
            "",
            "The unresolved list below keeps large third-party group labels separate when the public branding is too weak for a stronger same-entity claim.",
            "",
            "| Unresolved label | Active pools | Current stake (B ADA) | Current % supply | Sample domains | AdaStat labels | BalanceAnalytics labels |",
            "| --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )

    for row in unresolved_rows[:10]:
        lines.append(
            f"| {row['group_label']} | {row['active_pools']} | {row['current_stake_b_ada']:.3f} | {row['current_pct_supply']:.2f}% | "
            f"{row['sample_domains']} | {row['adastat_labels']} | {row['balanceanalytics_labels']} |"
        )

    lines.extend(
        [
            "",
            "## Sybil / decentralization interpretation",
            "",
            "- MPO concentration is not automatically a malicious Sybil attack. Exchanges, foundations, and providers can operate many pools for legitimate reasons.",
            "- The decentralization problem appears when pool-level diversity is mistaken for operator-level diversity.",
            "- Hidden or weakly branded clusters are the most concerning for measurement because delegators and researchers cannot audit unique control as easily.",
            "- Platform clusters need extra care: a common wallet or staking surface can make several pools look like one entity even when they are not.",
            "",
            "## Relationship to the progression chart",
            "",
            f"The historical concentration trend is covered separately in `../figures/{progression_figure_name}`. The stacked view keeps the attribution layer visible over time, while this document focuses on **who** the clusters appear to be and **why** the linkage is credible or not.",
            "",
            f"![Historical MPO composition](../figures/{progression_figure_name})",
            "",
            "## Bottom line",
            "",
            "The strongest same-entity attributions are the openly branded MPOs where metadata domains, ticker families, and external group labels all converge. The next tier is opaque but operationally coherent clusters such as Coinbase / bison.run. Everything else should be kept explicitly qualified as provider-mediated, platform-mediated, or unresolved rather than folded into a single hard number without explanation.",
            "",
        ]
    )

    out_path.write_text("\n".join(lines))


def main() -> None:
    entity_dir  = Path(__file__).resolve().parent.parent   # census/mainnet-analysis/
    data_dir    = entity_dir / "data"                     # entity data (local)
    figures_dir = entity_dir / "figures"
    outputs_dir = entity_dir / "data"                     # CSVs live alongside other entity data
    pool_data   = (entity_dir.parent.parent / "pools-distribution"
                   / "mainnet-analysis" / "data")         # shared pool data
    figures_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    figure_path = figures_dir / "mpo_entity_current_distribution_mainnet.png"
    mapping_csv_path = outputs_dir / "mpo_entity_pool_mapping_mainnet.csv"
    summary_csv_path = outputs_dir / "mpo_entity_summary_mainnet.csv"
    unresolved_csv_path = outputs_dir / "mpo_unresolved_group_labels_mainnet.csv"
    markdown_path = outputs_dir / "mpo_entity_deep_dive_mainnet.md"

    live_rows, live_epoch, live_supply_ada = load_live_rows()
    supply_by_epoch = load_supply_by_epoch()
    entity_stats, pool_to_entity, _ = build_entity_stats(live_rows, mapping_csv_path)
    load_history_markers(pool_data / "koios_pool_history_mainnet.csv", pool_to_entity, entity_stats)

    summary_rows: List[Tuple[EntityStats, float, float, float, float]] = []
    for stats in entity_stats.values():
        if not should_include_in_summary(stats):
            continue
        current_pct = stats.current_stake_ada / live_supply_ada * 100.0 if live_supply_ada else 0.0
        pct_400 = stats.epoch_400_stake_ada / supply_by_epoch[400] * 100.0 if 400 in supply_by_epoch else 0.0
        pct_410 = stats.epoch_410_stake_ada / supply_by_epoch[410] * 100.0 if 410 in supply_by_epoch else 0.0
        pct_584 = stats.epoch_584_stake_ada / supply_by_epoch[584] * 100.0 if 584 in supply_by_epoch else 0.0
        summary_rows.append((stats, current_pct, pct_400, pct_410, pct_584))

    summary_rows.sort(key=lambda row: row[1], reverse=True)

    render_current_distribution(figure_path, [(stats, current_pct) for stats, current_pct, _, _, _ in summary_rows])
    write_entity_summary_csv(summary_csv_path, summary_rows)

    unresolved_rows = unresolved_group_rows(live_rows, set(pool_to_entity), live_supply_ada)
    write_unresolved_csv(unresolved_csv_path, unresolved_rows)

    write_markdown(
        markdown_path,
        figure_path.name,
        "mpo_entity_progression_stacked_mainnet.png",
        live_epoch,
        live_supply_ada,
        summary_rows,
        unresolved_rows,
    )

    print(figure_path)
    print(markdown_path)
    print(summary_csv_path)
    print(mapping_csv_path)
    print(unresolved_csv_path)


if __name__ == "__main__":
    main()
