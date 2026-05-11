"""Build a stake-weighted MPO infrastructure-topology view.

Pipeline (phases are idempotent and cache to data/cache/):
    1. extract     parse relay_hints from mpo_entity_pool_mapping_mainnet.csv
    2. resolve-dns forward-resolve every DNS hint to IPv4/IPv6 (socket.getaddrinfo)
    3. resolve-rdns reverse-resolve every unique IP to a PTR (socket.gethostbyaddr)
    4. enrich-asn  bulk-query Team Cymru WHOIS for ASN/country/prefix
    5. classify    combine PTR + ASN heuristics into a (provider, region) label
    6. aggregate   emit stake-weighted CSV summaries + a short findings doc

    all            run 1-6 in sequence

Outputs (under data/):
    mpo_relay_endpoints_resolved.csv         one row per (pool, ip) with full enrichment
    mpo_topology_concentration_by_provider.csv
    mpo_topology_concentration_by_country.csv
    mpo_topology_concentration_by_region.csv
    mpo_topology_entity_provider_matrix.csv
    cache/                                   intermediate caches (re-runnable)

Notes:
    - Only pools with pool_status=='registered' are counted.
    - Pool stake is split evenly across the distinct (provider, region) labels its
      relays resolve to. A separate "any-exposure" view is also emitted.
"""
from __future__ import annotations
import argparse
import csv
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA = ROOT / "data"
CACHE = DATA / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

MAPPING_CSV = DATA / "mpo_entity_pool_mapping_mainnet.csv"
KOIOS_POOL_LIST = DATA / "koios_pool_list.json"

ENDPOINTS_RAW = CACHE / "endpoints_raw.csv"
DNS_CACHE = CACHE / "dns_forward.json"
RDNS_CACHE = CACHE / "dns_reverse.json"
ASN_CACHE = CACHE / "asn_cymru.json"

# IP-range / city databases (downloaded by fetch_ipranges_databases.py)
IPRANGES = CACHE / "ipranges"
GCP_RANGES = IPRANGES / "gcp_cloud.json"
AZURE_RANGES = IPRANGES / "azure_servicetags.json"
GEOLITE_CITY = IPRANGES / "GeoLite2-City.mmdb"

OUT_ENDPOINTS = DATA / "mpo_relay_endpoints_resolved.csv"
OUT_PROVIDER = DATA / "mpo_topology_concentration_by_provider.csv"
OUT_COUNTRY = DATA / "mpo_topology_concentration_by_country.csv"
OUT_REGION = DATA / "mpo_topology_concentration_by_region.csv"
OUT_ENTITY_MATRIX = DATA / "mpo_topology_entity_provider_matrix.csv"
OUT_TIER = DATA / "mpo_topology_concentration_by_tier.csv"
OUT_PHYS_COUNTRY = DATA / "mpo_topology_concentration_by_physical_country.csv"
OUT_FINDINGS = ROOT / "docs" / "mpo_topology_tables_auto.md"

# ----- 1. extract ---------------------------------------------------------

IP_RE = re.compile(r"^[0-9a-fA-F:.]+$")


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def parse_relay_hints(raw: str) -> List[Tuple[str, str]]:
    """Return [(kind, value)] where kind in {'ip','dns'}.

    Supports three formats observed in `mpo_entity_pool_mapping_mainnet.csv`:
      1. JSON-array  -- "[{\"dns\":..,\"ipv4\":..,\"ipv6\":..,\"port\":..}, ..]"
      2. semicolon-list -- "1.2.3.4; relay.example.com; 5.6.7.8"
      3. plain single value -- "1.2.3.4"  or  "relay.example.com"
    """
    if not raw:
        return []
    raw = raw.strip()
    out: List[Tuple[str, str]] = []
    # 1. JSON array (Koios `relays` field passthrough)
    if raw.startswith("["):
        try:
            arr = json.loads(raw)
        except json.JSONDecodeError:
            arr = []
        for entry in arr:
            if not isinstance(entry, dict):
                continue
            for field in ("ipv4", "ipv6"):
                v = entry.get(field)
                if v and isinstance(v, str) and is_ip(v.strip()):
                    out.append(("ip", v.strip()))
            v = entry.get("dns")
            if v and isinstance(v, str):
                v = v.strip().lower()
                # dns may itself be an IP literal
                if is_ip(v):
                    out.append(("ip", v))
                else:
                    out.append(("dns", v))
            v = entry.get("srv")
            if v and isinstance(v, str):
                out.append(("dns", v.strip().lower()))
        return out
    # 2 & 3. semicolon or single
    for tok in raw.split(";"):
        v = tok.strip()
        if not v:
            continue
        if is_ip(v):
            out.append(("ip", v))
        else:
            out.append(("dns", v.lower()))
    return out


def _parse_koios_relays(relays: list) -> List[Tuple[str, str]]:
    """Koios returns relays as [{'dns':..,'srv':..,'ipv4':..,'ipv6':..,'port':..}, ..]."""
    out = []
    for entry in relays or []:
        if not isinstance(entry, dict):
            continue
        for field in ("ipv4", "ipv6"):
            v = entry.get(field)
            if v and isinstance(v, str) and is_ip(v.strip()):
                out.append(("ip", v.strip()))
        v = entry.get("dns")
        if v and isinstance(v, str):
            v = v.strip().lower()
            if is_ip(v):
                out.append(("ip", v))
            else:
                out.append(("dns", v))
        v = entry.get("srv")
        if v and isinstance(v, str):
            out.append(("dns", v.strip().lower()))
    return out


def _load_mpo_mapping() -> Dict[str, dict]:
    """pool_id_bech32 -> mpo entity metadata."""
    out = {}
    if not MAPPING_CSV.exists():
        return out
    with MAPPING_CSV.open() as f:
        for r in csv.DictReader(f):
            out[r["pool_id_bech32"]] = {
                "entity_id": r["entity_id"],
                "display_name": r["display_name"],
                "category": r["category"],
            }
    return out


def phase_extract() -> None:
    """Build endpoints_raw.csv from the Koios snapshot (or MPO mapping if Koios is absent).

    When Koios is available we cover the *entire* active Cardano pool population
    (~2959 pools / ~21.7B ADA), not just the MPO-mapped subset. MPO entity
    attribution is layered on top from the mapping CSV; non-MPO pools are
    self-attributed (one entity per pool, named by ticker).
    """
    mpo = _load_mpo_mapping()
    rows_out = []
    if KOIOS_POOL_LIST.exists():
        print(f"[extract] reading Koios snapshot {KOIOS_POOL_LIST.name}")
        pools = json.loads(KOIOS_POOL_LIST.read_text())
        for p in pools:
            if p.get("pool_status") != "registered":
                continue
            try:
                stake = float(p.get("active_stake") or 0) / 1e6  # lovelace -> ADA
            except (ValueError, TypeError):
                stake = 0.0
            pid = p["pool_id_bech32"]
            ticker = p.get("ticker") or ""
            m = mpo.get(pid)
            if m:
                entity_id = m["entity_id"]
                display_name = m["display_name"]
                category = m["category"]
            else:
                entity_id = f"SPO:{pid[:14]}"
                display_name = ticker or pid[:14]
                category = "single_pool"
            for kind, value in _parse_koios_relays(p.get("relays") or []):
                rows_out.append({
                    "entity_id": entity_id,
                    "display_name": display_name,
                    "category": category,
                    "pool_id_bech32": pid,
                    "ticker": ticker,
                    "current_active_stake_ada": stake,
                    "endpoint_kind": kind,
                    "endpoint_value": value,
                })
    else:
        print(f"[extract] no Koios snapshot; falling back to {MAPPING_CSV.name}")
        with MAPPING_CSV.open() as f:
            for r in csv.DictReader(f):
                if r["pool_status"] != "registered":
                    continue
                try:
                    stake = float(r["current_active_stake_ada"] or 0)
                except ValueError:
                    stake = 0.0
                for kind, value in parse_relay_hints(r.get("relay_hints", "")):
                    rows_out.append({
                        "entity_id": r["entity_id"],
                        "display_name": r["display_name"],
                        "category": r["category"],
                        "pool_id_bech32": r["pool_id_bech32"],
                        "ticker": r["ticker"],
                        "current_active_stake_ada": stake,
                        "endpoint_kind": kind,
                        "endpoint_value": value,
                    })

    with ENDPOINTS_RAW.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    pools_seen = {r["pool_id_bech32"] for r in rows_out}
    ips = {r["endpoint_value"] for r in rows_out if r["endpoint_kind"] == "ip"}
    dnss = {r["endpoint_value"] for r in rows_out if r["endpoint_kind"] == "dns"}
    n_mpo = sum(1 for r in rows_out if r["category"] != "single_pool")
    n_spo = sum(1 for r in rows_out if r["category"] == "single_pool")
    print(
        f"[extract] {len(rows_out)} endpoint rows across {len(pools_seen)} pools "
        f"({len(ips)} unique IPs, {len(dnss)} unique DNS names)"
    )
    print(f"           MPO-attributed rows: {n_mpo}; single-pool rows: {n_spo}")


# ----- 2. resolve-dns -----------------------------------------------------


def _load_cache(path: Path) -> Dict[str, list]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_cache(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, sort_keys=True, indent=0))


def _resolve_dns(host: str, timeout: float = 4.0) -> List[str]:
    socket.setdefaulttimeout(timeout)
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, socket.herror, OSError, UnicodeError):
        return []
    seen, out = set(), []
    for inf in infos:
        ip = inf[4][0]
        if ip not in seen:
            seen.add(ip)
            out.append(ip)
    return out


def phase_resolve_dns(workers: int = 40) -> None:
    cache = _load_cache(DNS_CACHE)
    print(f"[resolve-dns] {len(cache)} cached hosts already resolved")
    with ENDPOINTS_RAW.open() as f:
        hosts = sorted({r["endpoint_value"] for r in csv.DictReader(f) if r["endpoint_kind"] == "dns"})
    todo = [h for h in hosts if h not in cache]
    print(f"[resolve-dns] resolving {len(todo)} new hosts (workers={workers})")
    if todo:
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_resolve_dns, h): h for h in todo}
            for fut in as_completed(futs):
                h = futs[fut]
                cache[h] = fut.result() or []
                done += 1
                if done % 50 == 0:
                    print(f"  ... {done}/{len(todo)}")
                    _save_cache(DNS_CACHE, cache)
        _save_cache(DNS_CACHE, cache)
    resolved = sum(1 for v in cache.values() if v)
    print(f"[resolve-dns] resolved={resolved}/{len(cache)} ({len(cache) - resolved} failures)")


# ----- 3. resolve-rdns ----------------------------------------------------


def _all_ips() -> Set[str]:
    ips: Set[str] = set()
    with ENDPOINTS_RAW.open() as f:
        for r in csv.DictReader(f):
            if r["endpoint_kind"] == "ip":
                ips.add(r["endpoint_value"])
    dns_cache = _load_cache(DNS_CACHE)
    for vs in dns_cache.values():
        for ip in vs:
            ips.add(ip)
    return ips


def _resolve_rdns(ip: str, timeout: float = 4.0) -> str:
    """Shell out to `dig` -- socket.gethostbyaddr is unreliable in some sandboxes."""
    try:
        out = subprocess.run(
            ["dig", "+short", "+time=3", "+tries=1", "-x", ip, "@1.1.1.1"],
            capture_output=True, text=True, timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    line = (out.stdout or "").strip().splitlines()
    if not line:
        return ""
    name = line[0].strip().rstrip(".").lower()
    return name


def phase_resolve_rdns(workers: int = 40) -> None:
    cache = _load_cache(RDNS_CACHE)
    print(f"[resolve-rdns] {len(cache)} cached PTRs")
    ips = sorted(_all_ips())
    todo = [ip for ip in ips if ip not in cache]
    print(f"[resolve-rdns] resolving {len(todo)} new PTRs (workers={workers})")
    if todo:
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_resolve_rdns, ip): ip for ip in todo}
            for fut in as_completed(futs):
                ip = futs[fut]
                cache[ip] = fut.result()
                done += 1
                if done % 100 == 0:
                    print(f"  ... {done}/{len(todo)}")
                    _save_cache(RDNS_CACHE, cache)
        _save_cache(RDNS_CACHE, cache)
    with_ptr = sum(1 for v in cache.values() if v)
    print(f"[resolve-rdns] PTR found for {with_ptr}/{len(cache)} IPs")


# ----- 4. enrich-asn ------------------------------------------------------

CYMRU_HOST = "whois.cymru.com"
CYMRU_PORT = 43


def _cymru_chunk(ips: List[str]) -> List[dict]:
    body = "begin\nverbose\n" + "\n".join(ips) + "\nend\n"
    out_rows = []
    with socket.create_connection((CYMRU_HOST, CYMRU_PORT), timeout=20) as s:
        s.sendall(body.encode())
        chunks = []
        while True:
            data = s.recv(65536)
            if not data:
                break
            chunks.append(data)
    text = b"".join(chunks).decode("utf-8", "replace")
    for line in text.splitlines():
        if "|" not in line or line.startswith("Bulk mode"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        asn, ip, prefix, cc, registry, allocated, asname = parts[:7]
        out_rows.append(
            {
                "ip": ip,
                "asn": asn,
                "prefix": prefix,
                "country": cc,
                "registry": registry,
                "allocated": allocated,
                "as_name": asname,
            }
        )
    return out_rows


def phase_enrich_asn(chunk: int = 400) -> None:
    cache = _load_cache(ASN_CACHE)
    print(f"[enrich-asn] {len(cache)} cached")
    ips = sorted(_all_ips())
    todo = [ip for ip in ips if ip not in cache and not ip.startswith(("10.", "192.168.", "127."))]
    print(f"[enrich-asn] querying {len(todo)} IPs in chunks of {chunk}")
    for i in range(0, len(todo), chunk):
        sub = todo[i : i + chunk]
        try:
            results = _cymru_chunk(sub)
        except Exception as e:
            print(f"  ! chunk {i} failed: {e}")
            continue
        by_ip = {r["ip"]: r for r in results}
        for ip in sub:
            cache[ip] = by_ip.get(ip, {})
        _save_cache(ASN_CACHE, cache)
        print(f"  ... {min(i+chunk,len(todo))}/{len(todo)}")
    with_asn = sum(1 for v in cache.values() if v.get("asn"))
    print(f"[enrich-asn] ASN found for {with_asn}/{len(cache)} IPs")


# ----- 5. classify --------------------------------------------------------

# Curated ASN -> provider table.  Anchored to public ASN-allocations docs.
ASN_PROVIDER = {
    # AWS
    "16509": "AWS", "14618": "AWS", "39111": "AWS", "9059": "AWS",
    "8987": "AWS", "7224": "AWS", "10124": "AWS",
    # Google Cloud
    "15169": "GCP", "396982": "GCP", "139070": "GCP", "36492": "GCP",
    # Azure
    "8075": "Azure", "8068": "Azure", "8069": "Azure", "8070": "Azure",
    "8071": "Azure", "8072": "Azure", "8073": "Azure", "8074": "Azure",
    "12076": "Azure",
    # Cloudflare (some operators terminate behind CF; rare for relays)
    "13335": "Cloudflare",
    # Big bare-metal / VPS clouds favoured by SPOs
    "24940": "Hetzner",
    "16276": "OVH",
    "14061": "DigitalOcean",
    "63949": "Akamai/Linode",
    "20473": "Vultr / Choopa",
    "51167": "Contabo",
    "8560": "IONOS",
    "44788": "PrivateLayer",
    "60068": "Datacamp/CDN77",
    "62240": "Clouvider",
    "42864": "Giganet",
    "29802": "HiVelocity",
    "20546": "AdvancedHosting",
    "31898": "Oracle Cloud",
    "132203": "Tencent Cloud",
    "37963": "Alibaba Cloud",
    "45102": "Alibaba Cloud",
    "135377": "Alibaba Cloud",
    "136907": "Huawei Cloud",
    "55990": "Huawei Cloud",
    # commodity VPS / bare-metal hosters that show up materially in Cardano relays
    "59642": "Cherry Servers",
    "49981": "WorldStream",
    "201814": "MEVspace",
    "28753": "Leaseweb",
    "60781": "Leaseweb",
    "63473": "HostHatch",
    "47583": "Hostinger",
    "210644": "Hostinger",
    "47147": "Hostinger / Hostinger International",
    "14593": "Starlink",
    "6730":  "Sunrise (CH residential ISP)",
    "1836":  "Green.ch",
    "7992":  "Cogeco (CA cable ISP)",
    "7979":  "Servers.com",
}

# "tier" rolls providers up into hyperscaler / commodity-vps / other for higher-level reads
PROVIDER_TIER: Dict[str, str] = {
    "AWS": "hyperscaler",
    "GCP": "hyperscaler",
    "Azure": "hyperscaler",
    "Oracle Cloud": "hyperscaler",
    "Alibaba Cloud": "hyperscaler",
    "Tencent Cloud": "hyperscaler",
    "Huawei Cloud": "hyperscaler",
    "Hetzner": "commodity-vps",
    "OVH": "commodity-vps",
    "DigitalOcean": "commodity-vps",
    "Vultr / Choopa": "commodity-vps",
    "Contabo": "commodity-vps",
    "Akamai/Linode": "commodity-vps",
    "IONOS": "commodity-vps",
    "Leaseweb": "commodity-vps",
    "WorldStream": "commodity-vps",
    "Cherry Servers": "commodity-vps",
    "MEVspace": "commodity-vps",
    "HostHatch": "commodity-vps",
    "Hostinger": "commodity-vps",
    "Hostinger / Hostinger International": "commodity-vps",
    "Servers.com": "commodity-vps",
    "Cloudflare": "edge/cdn",
    "Starlink": "residential/satellite",
    "Sunrise (CH residential ISP)": "residential/satellite",
    "Green.ch": "residential/satellite",
    "Cogeco (CA cable ISP)": "residential/satellite",
    "Other / on-prem": "other-or-onprem",
    "Unresolved": "unresolved",
}

# PTR pattern -> (provider, optional region extractor)
PTR_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\.amazonaws\.com$"), "AWS"),
    (re.compile(r"\.compute\.amazonaws\.com$"), "AWS"),
    (re.compile(r"\.googleusercontent\.com$"), "GCP"),
    (re.compile(r"\.bc\.googleusercontent\.com$"), "GCP"),
    (re.compile(r"\.cloudapp\.net$"), "Azure"),
    (re.compile(r"\.cloudapp\.azure\.com$"), "Azure"),
    (re.compile(r"your-server\.de$"), "Hetzner"),
    (re.compile(r"\.hetzner\.com$"), "Hetzner"),
    (re.compile(r"\.ovh\.net$"), "OVH"),
    (re.compile(r"\.ovh\.ca$"), "OVH"),
    (re.compile(r"\.kimsufi\.com$"), "OVH"),
    (re.compile(r"\.digitalocean\.com$"), "DigitalOcean"),
    (re.compile(r"\.linode\.com$"), "Akamai/Linode"),
    (re.compile(r"\.linodeusercontent\.com$"), "Akamai/Linode"),
    (re.compile(r"\.akamaitechnologies\.com$"), "Akamai/Linode"),
    (re.compile(r"\.vultr\.com$"), "Vultr / Choopa"),
    (re.compile(r"\.choopa\.net$"), "Vultr / Choopa"),
    (re.compile(r"\.contabo\.(net|com)$"), "Contabo"),
    (re.compile(r"\.ionos\.com$"), "IONOS"),
    (re.compile(r"\.oracle(cloud)?\.com$"), "Oracle Cloud"),
    (re.compile(r"\.aliyun(cs)?\.com$"), "Alibaba Cloud"),
    (re.compile(r"\.cloudflare\.com$"), "Cloudflare"),
]

AWS_REGION_RE = re.compile(
    r"\.([a-z]{2}-(?:north|south|east|west|central|northeast|southeast|southwest|northwest)-\d)\."
)

# Cloud region -> physical ISO2 country code.
# Hand-curated from each provider's public regions documentation.
REGION_TO_COUNTRY: Dict[str, str] = {
    # AWS
    "aws:us-east-1": "US", "aws:us-east-2": "US",
    "aws:us-west-1": "US", "aws:us-west-2": "US",
    "aws:us-gov-east-1": "US", "aws:us-gov-west-1": "US",
    "aws:ca-central-1": "CA", "aws:ca-west-1": "CA",
    "aws:eu-west-1": "IE", "aws:eu-west-2": "GB", "aws:eu-west-3": "FR",
    "aws:eu-central-1": "DE", "aws:eu-central-2": "CH",
    "aws:eu-north-1": "SE", "aws:eu-south-1": "IT", "aws:eu-south-2": "ES",
    "aws:ap-northeast-1": "JP", "aws:ap-northeast-2": "KR", "aws:ap-northeast-3": "JP",
    "aws:ap-south-1": "IN", "aws:ap-south-2": "IN",
    "aws:ap-southeast-1": "SG", "aws:ap-southeast-2": "AU",
    "aws:ap-southeast-3": "ID", "aws:ap-southeast-4": "AU",
    "aws:ap-east-1": "HK", "aws:sa-east-1": "BR",
    "aws:af-south-1": "ZA", "aws:me-south-1": "BH", "aws:me-central-1": "AE",
    # GCP
    "gcp:us-central1": "US", "gcp:us-east1": "US", "gcp:us-east4": "US",
    "gcp:us-east5": "US", "gcp:us-south1": "US",
    "gcp:us-west1": "US", "gcp:us-west2": "US", "gcp:us-west3": "US", "gcp:us-west4": "US",
    "gcp:northamerica-northeast1": "CA", "gcp:northamerica-northeast2": "CA",
    "gcp:southamerica-east1": "BR", "gcp:southamerica-west1": "CL",
    "gcp:europe-west1": "BE", "gcp:europe-west2": "GB", "gcp:europe-west3": "DE",
    "gcp:europe-west4": "NL", "gcp:europe-west6": "CH", "gcp:europe-west8": "IT",
    "gcp:europe-west9": "FR", "gcp:europe-west10": "DE", "gcp:europe-west12": "IT",
    "gcp:europe-north1": "FI", "gcp:europe-southwest1": "ES",
    "gcp:europe-central2": "PL",
    "gcp:asia-east1": "TW", "gcp:asia-east2": "HK",
    "gcp:asia-northeast1": "JP", "gcp:asia-northeast2": "JP", "gcp:asia-northeast3": "KR",
    "gcp:asia-south1": "IN", "gcp:asia-south2": "IN",
    "gcp:asia-southeast1": "SG", "gcp:asia-southeast2": "ID",
    "gcp:australia-southeast1": "AU", "gcp:australia-southeast2": "AU",
    "gcp:me-central1": "QA", "gcp:me-central2": "SA", "gcp:me-west1": "IL",
    "gcp:africa-south1": "ZA",
    # Azure (region names as in ServiceTags JSON, lowercased)
    "azure:eastus": "US", "azure:eastus2": "US", "azure:eastusslv": "US",
    "azure:eastus3": "US", "azure:centralus": "US", "azure:centraluseuap": "US",
    "azure:westus": "US", "azure:westus2": "US", "azure:westus3": "US",
    "azure:southcentralus": "US", "azure:northcentralus": "US",
    "azure:westcentralus": "US", "azure:eastus2euap": "US",
    "azure:canadacentral": "CA", "azure:canadaeast": "CA",
    "azure:brazilsouth": "BR", "azure:brazilsoutheast": "BR", "azure:brazilus": "BR",
    "azure:northeurope": "IE", "azure:westeurope": "NL",
    "azure:uksouth": "GB", "azure:ukwest": "GB",
    "azure:francecentral": "FR", "azure:francesouth": "FR",
    "azure:germanywestcentral": "DE", "azure:germanywc": "DE",
    "azure:germanynorth": "DE",
    "azure:swedencentral": "SE", "azure:swedensouth": "SE",
    "azure:norwayeast": "NO", "azure:norwaywest": "NO",
    "azure:switzerlandnorth": "CH", "azure:switzerlandn": "CH",
    "azure:switzerlandwest": "CH",
    "azure:italynorth": "IT", "azure:polandcentral": "PL",
    "azure:spaincentral": "ES", "azure:austriaeast": "AT",
    "azure:southeastasia": "SG", "azure:eastasia": "HK",
    "azure:koreacentral": "KR", "azure:koreasouth": "KR",
    "azure:japaneast": "JP", "azure:japanwest": "JP",
    "azure:australiaeast": "AU", "azure:australiasoutheast": "AU",
    "azure:australiacentral": "AU", "azure:australiacentral2": "AU",
    "azure:centralindia": "IN", "azure:southindia": "IN", "azure:westindia": "IN",
    "azure:southafricanorth": "ZA", "azure:southafricawest": "ZA",
    "azure:uaenorth": "AE", "azure:uaecentral": "AE",
    "azure:qatarcentral": "QA", "azure:israelcentral": "IL",
    "azure:taiwannorth": "TW",
    "azure:newzealandnorth": "NZ", "azure:newzealandn": "NZ",
    "azure:mexicocentral": "MX", "azure:chilecentral": "CL",
    "azure:malaysiawest": "MY", "azure:indonesiacentral": "ID",
}


def physical_country(region: str, ovh_or_geo_country: str = "") -> str:
    """Map a region label to its physical-datacentre country.

    Falls back to (a) the country tag inside an OVH/Hetzner/Contabo region label,
    (b) the supplied BGP/Geo country, (c) empty string.
    """
    if region in REGION_TO_COUNTRY:
        return REGION_TO_COUNTRY[region]
    # OVH labels look like "ovh:fr:roubaix" -> use the country tag
    if region.startswith(("ovh:", "hetzner:", "contabo:", "leaseweb:", "worldstream:")):
        parts = region.split(":")
        if len(parts) >= 3:
            # ovh:cc:city  -- second part is country code if 2-letter
            if len(parts[1]) == 2:
                return parts[1].upper()
    if region.startswith("cc:") and len(region) == 5:
        return region[3:].upper()
    return ovh_or_geo_country


# ---------- GCP / Azure region tries + GeoLite2 city -----------------------

_GCP_RANGES: List[Tuple[ipaddress._BaseNetwork, str]] = []
_AZURE_RANGES: List[Tuple[ipaddress._BaseNetwork, str]] = []
_GEOLITE_DB = None


def _load_gcp_ranges() -> None:
    if _GCP_RANGES or not GCP_RANGES.exists():
        return
    data = json.loads(GCP_RANGES.read_text())
    for p in data.get("prefixes", []):
        net = p.get("ipv4Prefix") or p.get("ipv6Prefix")
        scope = p.get("scope") or ""  # e.g. "europe-west1"
        if not net or not scope:
            continue
        try:
            _GCP_RANGES.append((ipaddress.ip_network(net), scope))
        except ValueError:
            pass


def _load_azure_ranges() -> None:
    if _AZURE_RANGES or not AZURE_RANGES.exists():
        return
    data = json.loads(AZURE_RANGES.read_text())
    # Use only the AzureCloud.<region> service tags (cleanest region attribution)
    for v in data.get("values", []):
        name = v.get("name", "")
        if not name.startswith("AzureCloud."):
            continue
        region = (v.get("properties") or {}).get("region") or ""
        if not region:
            continue
        for px in (v.get("properties") or {}).get("addressPrefixes") or []:
            try:
                _AZURE_RANGES.append((ipaddress.ip_network(px), region))
            except ValueError:
                pass


def _load_geolite() -> None:
    global _GEOLITE_DB
    if _GEOLITE_DB is not None or not GEOLITE_CITY.exists():
        return
    try:
        import maxminddb  # type: ignore
    except ImportError:
        print("[classify] maxminddb not installed; OVH city lookup disabled")
        _GEOLITE_DB = False
        return
    _GEOLITE_DB = maxminddb.open_database(str(GEOLITE_CITY))


def _gcp_region(ip: str) -> str:
    _load_gcp_ranges()
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ""
    # last-match wins for nested ranges; iterate and prefer the most-specific
    best = ""
    best_pref = -1
    for net, scope in _GCP_RANGES:
        if addr in net and net.prefixlen > best_pref:
            best, best_pref = scope, net.prefixlen
    return best


def _azure_region(ip: str) -> str:
    _load_azure_ranges()
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ""
    best = ""
    best_pref = -1
    for net, scope in _AZURE_RANGES:
        if addr in net and net.prefixlen > best_pref:
            best, best_pref = scope, net.prefixlen
    return best


def _geolite_city(ip: str) -> Tuple[str, str, str]:
    """Return (city, subdivision, country_iso2) — all empty if unknown."""
    _load_geolite()
    if not _GEOLITE_DB:
        return ("", "", "")
    try:
        r = _GEOLITE_DB.get(ip) or {}
    except (ValueError, OSError):
        return ("", "", "")
    city = ((r.get("city") or {}).get("names") or {}).get("en", "") or ""
    subs = r.get("subdivisions") or []
    sub = (subs[0].get("names", {}).get("en", "") if subs else "") or ""
    cc = ((r.get("country") or {}).get("iso_code")) or ""
    return (city, sub, cc)


def classify_endpoint(
    ptr: str, asn: str, country: str, as_name: str, ip: str = ""
) -> Tuple[str, str]:
    """Return (provider, region).

    Region precedence:
      1. AWS region from PTR (most specific, contains region code)
      2. GCP region from IP-range trie
      3. Azure region from IP-range trie
      4. OVH city / subdivision from GeoLite2
      5. Hetzner / Contabo etc.: city from GeoLite2 if available
      6. Country code fallback
    """
    provider = ""
    if ptr:
        for rx, name in PTR_RULES:
            if rx.search(ptr):
                provider = name
                break
    if not provider and asn:
        provider = ASN_PROVIDER.get(asn, "")
    if not provider and as_name:
        up = as_name.upper()
        if "AMAZON" in up:
            provider = "AWS"
        elif "GOOGLE" in up:
            provider = "GCP"
        elif "MICROSOFT" in up or "AZURE" in up:
            provider = "Azure"
        elif "HETZNER" in up:
            provider = "Hetzner"
        elif "OVH" in up:
            provider = "OVH"
        elif "DIGITALOCEAN" in up or "DIGITAL OCEAN" in up:
            provider = "DigitalOcean"
        elif "LINODE" in up or "AKAMAI" in up:
            provider = "Akamai/Linode"
        elif "VULTR" in up or "CHOOPA" in up:
            provider = "Vultr / Choopa"
        elif "CONTABO" in up:
            provider = "Contabo"
        elif "ALIBABA" in up:
            provider = "Alibaba Cloud"
        elif "ORACLE" in up:
            provider = "Oracle Cloud"
        elif "CLOUDFLARE" in up:
            provider = "Cloudflare"
    if not provider:
        provider = "Other / on-prem"

    # region attribution
    region = ""
    if provider == "AWS" and ptr:
        m = AWS_REGION_RE.search(ptr)
        if m:
            region = "aws:" + m.group(1)
    elif provider == "GCP" and ip:
        r = _gcp_region(ip)
        if r:
            region = "gcp:" + r
    elif provider == "Azure" and ip:
        r = _azure_region(ip)
        if r:
            region = "azure:" + r
    elif provider == "OVH" and ip:
        city, sub, geo_cc = _geolite_city(ip)
        if city or sub:
            tag = (city or sub).lower().replace(" ", "_")
            # geo_cc is the physical country derived from GeoLite2 city lookup —
            # *not* the BGP country (which for OVH is always FR or CA regardless
            # of where the actual datacentre sits)
            cc_part = geo_cc.lower() if geo_cc else country.lower() if country else ""
            region = f"ovh:{cc_part}:{tag}" if cc_part else f"ovh:{tag}"
    elif provider in ("Hetzner", "Contabo", "Leaseweb", "WorldStream") and ip:
        city, _sub, _cc = _geolite_city(ip)
        if city:
            region = f"{provider.lower()}:{city.lower().replace(' ', '_')}"

    if not region:
        region = f"cc:{country}" if country else "cc:??"
    return provider, region


def phase_classify() -> None:
    dns_cache = _load_cache(DNS_CACHE)
    rdns_cache = _load_cache(RDNS_CACHE)
    asn_cache = _load_cache(ASN_CACHE)
    out_rows = []
    with ENDPOINTS_RAW.open() as f:
        for r in csv.DictReader(f):
            if r["endpoint_kind"] == "ip":
                ips = [r["endpoint_value"]]
            else:
                ips = dns_cache.get(r["endpoint_value"], [])
            if not ips:
                out_rows.append(
                    {
                        **r,
                        "ip": "",
                        "ptr": "",
                        "asn": "",
                        "as_name": "",
                        "country": "",
                        "physical_country": "",
                        "provider": "Unresolved",
                        "tier": "unresolved",
                        "region": "cc:??",
                    }
                )
                continue
            for ip in ips:
                a = asn_cache.get(ip, {}) or {}
                ptr = rdns_cache.get(ip, "")
                provider, region = classify_endpoint(
                    ptr, a.get("asn", ""), a.get("country", ""), a.get("as_name", ""), ip,
                )
                bgp_country = a.get("country", "")
                phys_country = physical_country(region, bgp_country)
                out_rows.append(
                    {
                        **r,
                        "ip": ip,
                        "ptr": ptr,
                        "asn": a.get("asn", ""),
                        "as_name": a.get("as_name", ""),
                        "country": bgp_country,
                        "physical_country": phys_country,
                        "provider": provider,
                        "tier": PROVIDER_TIER.get(provider, "other-or-onprem"),
                        "region": region,
                    }
                )
    with OUT_ENDPOINTS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"[classify] {len(out_rows)} rows -> {OUT_ENDPOINTS.relative_to(ROOT)}")


# ----- 6. aggregate -------------------------------------------------------


def _load_endpoints() -> List[dict]:
    with OUT_ENDPOINTS.open() as f:
        return list(csv.DictReader(f))


def _pool_stake(rows: List[dict]) -> Dict[str, float]:
    out = {}
    for r in rows:
        out[r["pool_id_bech32"]] = float(r["current_active_stake_ada"] or 0)
    return out


def _aggregate_by(rows: List[dict], key: str) -> List[Tuple[str, int, float, float, int]]:
    """Stake-split: each pool's stake is divided evenly across its distinct keys.
    Returns rows of (key, n_pools_exposure, stake_split_ada, stake_split_pct, n_entities).
    """
    # exposure: pool -> set of keys
    pool_keys: Dict[str, Set[str]] = defaultdict(set)
    pool_entity: Dict[str, str] = {}
    for r in rows:
        pool_keys[r["pool_id_bech32"]].add(r[key])
        pool_entity[r["pool_id_bech32"]] = r["entity_id"]
    stake = _pool_stake(rows)
    total_stake = sum(stake.values())
    key_split: Counter = Counter()
    key_pools: Dict[str, Set[str]] = defaultdict(set)
    key_entities: Dict[str, Set[str]] = defaultdict(set)
    for pool, keys in pool_keys.items():
        s = stake.get(pool, 0)
        if not keys:
            continue
        per = s / len(keys)
        for k in keys:
            key_split[k] += per
            key_pools[k].add(pool)
            key_entities[k].add(pool_entity[pool])
    out = []
    for k, s in key_split.most_common():
        out.append(
            (
                k,
                len(key_pools[k]),
                s,
                100 * s / total_stake if total_stake else 0,
                len(key_entities[k]),
            )
        )
    return out


def _write_agg(path: Path, header: str, rows: List[Tuple]) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([header, "pools_exposed", "stake_split_ada", "stake_split_pct", "entities"])
        for r in rows:
            w.writerow([r[0], r[1], f"{r[2]:.0f}", f"{r[3]:.3f}", r[4]])


def phase_aggregate() -> None:
    rows = _load_endpoints()
    # provider
    by_provider = _aggregate_by(rows, "provider")
    _write_agg(OUT_PROVIDER, "provider", by_provider)
    by_country = _aggregate_by(rows, "country")
    _write_agg(OUT_COUNTRY, "country_iso2", by_country)
    by_region = _aggregate_by(rows, "region")
    _write_agg(OUT_REGION, "region", by_region)
    by_tier = _aggregate_by(rows, "tier")
    _write_agg(OUT_TIER, "tier", by_tier)
    by_phys = _aggregate_by(rows, "physical_country")
    _write_agg(OUT_PHYS_COUNTRY, "physical_country", by_phys)
    # entity x provider matrix
    ents = sorted({r["entity_id"] for r in rows})
    providers = sorted({r["provider"] for r in rows})
    cell: Dict[Tuple[str, str], float] = defaultdict(float)
    pool_seen: Dict[str, Set[str]] = defaultdict(set)
    for r in rows:
        pool_seen[r["pool_id_bech32"]].add((r["entity_id"], r["provider"]))
    stake = _pool_stake(rows)
    # For each pool, split stake across distinct (entity, provider)
    for pool, pairs in pool_seen.items():
        s = stake.get(pool, 0)
        if not pairs:
            continue
        per = s / len(pairs)
        for ent, prov in pairs:
            cell[(ent, prov)] += per
    with OUT_ENTITY_MATRIX.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "display_name", "category", "provider", "stake_split_ada"])
        # need entity meta
        meta: Dict[str, dict] = {}
        for r in rows:
            meta.setdefault(r["entity_id"], r)
        for (ent, prov), s in sorted(cell.items(), key=lambda kv: -kv[1]):
            m = meta[ent]
            w.writerow([ent, m["display_name"], m["category"], prov, f"{s:.0f}"])
    print(f"[aggregate] wrote 4 CSVs to {DATA.relative_to(ROOT)}")
    # Findings doc
    OUT_FINDINGS.parent.mkdir(parents=True, exist_ok=True)
    total_stake = sum(stake.values())
    top_provider = by_provider[:8]
    top_country = by_country[:8]
    top_region = [r for r in by_region if r[0].startswith("aws:")][:8]
    lines = [
        "# MPO Infrastructure Topology — Concentration Findings",
        "",
        f"_Snapshot: derived from `mpo_entity_pool_mapping_mainnet.csv` (registered pools only)._",
        "",
        f"- Pools covered: **{len(stake)}**, total active stake **{total_stake/1e9:.2f}B ADA**",
        f"- Endpoint rows (pool, ip): **{len(rows)}**",
        "",
        "## Top providers (stake-split, %)",
        "",
        "| Provider | Pools exposed | Stake (B ADA) | Stake share | Entities |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, n_p, s, pct, n_e in top_provider:
        lines.append(f"| {k} | {n_p} | {s/1e9:.2f} | {pct:.1f}% | {n_e} |")
    lines += [
        "",
        "## Top countries (stake-split, %)",
        "",
        "| ISO2 | Pools exposed | Stake (B ADA) | Stake share | Entities |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, n_p, s, pct, n_e in top_country:
        lines.append(f"| {k} | {n_p} | {s/1e9:.2f} | {pct:.1f}% | {n_e} |")
    if top_region:
        lines += [
            "",
            "## AWS regions (where PTR exposes region code)",
            "",
            "| Region | Pools exposed | Stake (B ADA) | Stake share | Entities |",
            "|---|---:|---:|---:|---:|",
        ]
        for k, n_p, s, pct, n_e in top_region:
            lines.append(f"| {k} | {n_p} | {s/1e9:.2f} | {pct:.1f}% | {n_e} |")
    lines += [
        "",
        "## Method (one-paragraph)",
        "",
        "Each registered pool's `relay_hints` (from the diagnostic mapping CSV) is "
        "parsed into a set of IPv4 / IPv6 / DNS endpoints. DNS names are forward-resolved "
        "via `socket.getaddrinfo`; every unique IP is then reverse-resolved (PTR) and "
        "queried against Team Cymru's bulk WHOIS for ASN, country, and BGP prefix. "
        "Provider attribution combines a PTR-pattern table (most specific) with an "
        "ASN-to-provider lookup (fallback) and AS-name keyword matching (last resort). "
        "AWS region is extracted from the PTR record when present. A pool's stake is "
        "split evenly across the distinct (provider, region) labels its relays resolve "
        "to, so totals sum to ~100%.",
        "",
        "## Caveats",
        "",
        "- Registered relays ≠ block-producing node. Most serious MPOs hide producers "
        "behind public-facing relays, often in different facilities. Numbers below are "
        "a **lower bound** on operator-side concentration.",
        "- Multi-relay pools registering across providers get their stake split, so a "
        "pool that relays at AWS and Hetzner contributes 50/50.",
        "- Cloudflare / generic CDN PTRs mask the real upstream; small fraction.",
        "",
    ]
    OUT_FINDINGS.write_text("\n".join(lines))
    print(f"[aggregate] wrote {OUT_FINDINGS.relative_to(ROOT)}")


# ----- CLI ----------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "phase",
        choices=["extract", "resolve-dns", "resolve-rdns", "enrich-asn", "classify", "aggregate", "all"],
    )
    args = p.parse_args(argv)
    if args.phase in ("extract", "all"):
        phase_extract()
    if args.phase in ("resolve-dns", "all"):
        phase_resolve_dns()
    if args.phase in ("resolve-rdns", "all"):
        phase_resolve_rdns()
    if args.phase in ("enrich-asn", "all"):
        phase_enrich_asn()
    if args.phase in ("classify", "all"):
        phase_classify()
    if args.phase in ("aggregate", "all"):
        phase_aggregate()


if __name__ == "__main__":
    main()
