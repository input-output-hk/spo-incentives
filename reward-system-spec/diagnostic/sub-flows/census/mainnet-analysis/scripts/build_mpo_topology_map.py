"""Interactive Leaflet map of every active Cardano pool's infrastructure footprint.

Aggregates each pool's registered relays into a primary location:
  - hyperscaler endpoints -> curated datacentre lat/lon for AWS / GCP / Azure
  - everything else -> GeoLite2-City lat/lon

Output: outputs/mpo_topology_map.html  (self-contained except Leaflet CDN)

Run: python3 scripts/build_mpo_topology_map.py
"""
from __future__ import annotations
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "cache"
ENDPOINTS = DATA / "mpo_relay_endpoints_resolved.csv"
GEOLITE = CACHE / "ipranges" / "GeoLite2-City.mmdb"
OUT_HTML = ROOT / "outputs" / "mpo_topology_map.html"
OUT_JSON = ROOT / "outputs" / "mpo_topology_map_data.json"


# Curated datacentre coordinates for major hyperscaler regions.
# Sources: each provider's published region documentation (city level).
DC_COORDS: dict = {
    # AWS
    "aws:us-east-1": (38.95, -77.45, "Ashburn, US"),
    "aws:us-east-2": (40.00, -82.95, "Columbus, US"),
    "aws:us-west-1": (37.45, -122.18, "Palo Alto, US"),
    "aws:us-west-2": (45.84, -119.71, "Boardman, US"),
    "aws:ca-central-1": (45.50, -73.57, "Montreal, CA"),
    "aws:eu-west-1": (53.34, -6.27, "Dublin, IE"),
    "aws:eu-west-2": (51.51, -0.13, "London, GB"),
    "aws:eu-west-3": (48.86, 2.35, "Paris, FR"),
    "aws:eu-central-1": (50.11, 8.68, "Frankfurt, DE"),
    "aws:eu-central-2": (47.37, 8.55, "Zurich, CH"),
    "aws:eu-north-1": (59.33, 18.06, "Stockholm, SE"),
    "aws:eu-south-1": (45.46, 9.19, "Milan, IT"),
    "aws:ap-northeast-1": (35.69, 139.69, "Tokyo, JP"),
    "aws:ap-northeast-2": (37.57, 126.98, "Seoul, KR"),
    "aws:ap-northeast-3": (34.69, 135.50, "Osaka, JP"),
    "aws:ap-south-1": (19.08, 72.88, "Mumbai, IN"),
    "aws:ap-southeast-1": (1.35, 103.82, "Singapore, SG"),
    "aws:ap-southeast-2": (-33.87, 151.21, "Sydney, AU"),
    "aws:ap-southeast-3": (-6.21, 106.85, "Jakarta, ID"),
    "aws:ap-east-1": (22.32, 114.17, "Hong Kong, HK"),
    "aws:sa-east-1": (-23.55, -46.63, "Sao Paulo, BR"),
    "aws:af-south-1": (-33.92, 18.42, "Cape Town, ZA"),
    "aws:me-south-1": (26.07, 50.55, "Manama, BH"),
    "aws:me-central-1": (25.20, 55.27, "Dubai, AE"),
    # GCP
    "gcp:us-central1": (41.59, -93.62, "Council Bluffs, US"),
    "gcp:us-east1": (33.84, -81.16, "Moncks Corner, US"),
    "gcp:us-east4": (39.04, -77.49, "Ashburn, US"),
    "gcp:us-east5": (39.96, -83.00, "Columbus, US"),
    "gcp:us-south1": (32.78, -96.80, "Dallas, US"),
    "gcp:us-west1": (45.59, -121.18, "The Dalles, US"),
    "gcp:us-west2": (34.05, -118.24, "Los Angeles, US"),
    "gcp:us-west3": (40.76, -111.89, "Salt Lake City, US"),
    "gcp:us-west4": (36.17, -115.14, "Las Vegas, US"),
    "gcp:northamerica-northeast1": (45.50, -73.57, "Montreal, CA"),
    "gcp:northamerica-northeast2": (43.65, -79.38, "Toronto, CA"),
    "gcp:southamerica-east1": (-23.55, -46.63, "Sao Paulo, BR"),
    "gcp:europe-west1": (50.45, 3.82, "St Ghislain, BE"),
    "gcp:europe-west2": (51.51, -0.13, "London, GB"),
    "gcp:europe-west3": (50.11, 8.68, "Frankfurt, DE"),
    "gcp:europe-west4": (53.42, 6.84, "Eemshaven, NL"),
    "gcp:europe-west6": (47.37, 8.55, "Zurich, CH"),
    "gcp:europe-west8": (45.46, 9.19, "Milan, IT"),
    "gcp:europe-west9": (48.86, 2.35, "Paris, FR"),
    "gcp:europe-west10": (52.52, 13.41, "Berlin, DE"),
    "gcp:europe-west12": (45.07, 7.69, "Turin, IT"),
    "gcp:europe-north1": (60.57, 27.19, "Hamina, FI"),
    "gcp:europe-southwest1": (40.42, -3.70, "Madrid, ES"),
    "gcp:europe-central2": (52.23, 21.01, "Warsaw, PL"),
    "gcp:asia-east1": (24.07, 120.55, "Changhua, TW"),
    "gcp:asia-east2": (22.32, 114.17, "Hong Kong, HK"),
    "gcp:asia-northeast1": (35.69, 139.69, "Tokyo, JP"),
    "gcp:asia-northeast2": (34.69, 135.50, "Osaka, JP"),
    "gcp:asia-northeast3": (37.57, 126.98, "Seoul, KR"),
    "gcp:asia-south1": (19.08, 72.88, "Mumbai, IN"),
    "gcp:asia-south2": (28.61, 77.21, "Delhi, IN"),
    "gcp:asia-southeast1": (1.35, 103.82, "Singapore, SG"),
    "gcp:asia-southeast2": (-6.21, 106.85, "Jakarta, ID"),
    "gcp:australia-southeast1": (-33.87, 151.21, "Sydney, AU"),
    "gcp:australia-southeast2": (-37.81, 144.96, "Melbourne, AU"),
    "gcp:me-central1": (25.30, 51.53, "Doha, QA"),
    "gcp:me-west1": (32.08, 34.78, "Tel Aviv, IL"),
    "gcp:africa-south1": (-26.20, 28.04, "Johannesburg, ZA"),
    # Azure
    "azure:eastus": (37.43, -78.66, "Virginia, US"),
    "azure:eastus2": (37.43, -78.66, "Virginia, US"),
    "azure:eastus3": (32.78, -96.80, "Dallas, US"),
    "azure:centralus": (41.59, -93.62, "Iowa, US"),
    "azure:westus": (37.78, -122.42, "California, US"),
    "azure:westus2": (47.61, -122.33, "Washington, US"),
    "azure:westus3": (33.45, -112.07, "Phoenix, US"),
    "azure:southcentralus": (29.42, -98.50, "San Antonio, US"),
    "azure:northcentralus": (41.88, -87.63, "Chicago, US"),
    "azure:canadacentral": (43.65, -79.38, "Toronto, CA"),
    "azure:canadaeast": (46.81, -71.21, "Quebec City, CA"),
    "azure:brazilsouth": (-23.55, -46.63, "Sao Paulo, BR"),
    "azure:northeurope": (53.34, -6.27, "Dublin, IE"),
    "azure:westeurope": (52.37, 4.89, "Amsterdam, NL"),
    "azure:uksouth": (51.51, -0.13, "London, GB"),
    "azure:ukwest": (53.48, -2.24, "Cardiff, GB"),
    "azure:francecentral": (48.86, 2.35, "Paris, FR"),
    "azure:germanywestcentral": (50.11, 8.68, "Frankfurt, DE"),
    "azure:germanywc": (50.11, 8.68, "Frankfurt, DE"),
    "azure:germanynorth": (52.52, 13.41, "Berlin, DE"),
    "azure:swedencentral": (60.13, 18.64, "Gavle, SE"),
    "azure:norwayeast": (59.91, 10.75, "Oslo, NO"),
    "azure:switzerlandnorth": (47.37, 8.55, "Zurich, CH"),
    "azure:switzerlandn": (47.37, 8.55, "Zurich, CH"),
    "azure:italynorth": (45.46, 9.19, "Milan, IT"),
    "azure:polandcentral": (52.23, 21.01, "Warsaw, PL"),
    "azure:spaincentral": (40.42, -3.70, "Madrid, ES"),
    "azure:austriaeast": (48.21, 16.37, "Vienna, AT"),
    "azure:southeastasia": (1.35, 103.82, "Singapore, SG"),
    "azure:eastasia": (22.32, 114.17, "Hong Kong, HK"),
    "azure:koreacentral": (37.57, 126.98, "Seoul, KR"),
    "azure:japaneast": (35.69, 139.69, "Tokyo, JP"),
    "azure:japanwest": (34.69, 135.50, "Osaka, JP"),
    "azure:australiaeast": (-33.87, 151.21, "Sydney, AU"),
    "azure:australiasoutheast": (-37.81, 144.96, "Melbourne, AU"),
    "azure:centralindia": (18.52, 73.86, "Pune, IN"),
    "azure:southindia": (12.97, 80.21, "Chennai, IN"),
    "azure:southafricanorth": (-26.20, 28.04, "Johannesburg, ZA"),
    "azure:uaenorth": (25.20, 55.27, "Dubai, AE"),
    "azure:qatarcentral": (25.30, 51.53, "Doha, QA"),
    "azure:taiwannorth": (24.07, 120.55, "Taipei, TW"),
    "azure:israelcentral": (32.08, 34.78, "Tel Aviv, IL"),
    "azure:newzealandnorth": (-36.85, 174.76, "Auckland, NZ"),
    "azure:newzealandn": (-36.85, 174.76, "Auckland, NZ"),
    "azure:mexicocentral": (19.43, -99.13, "Mexico City, MX"),
    "azure:chilecentral": (-33.45, -70.67, "Santiago, CL"),
}


# IOG brand colour per provider (matches the bar charts)
PROVIDER_COLOR = {
    "AWS": "#E52321",
    "GCP": "#EC641D",
    "Azure": "#2C4FFA",
    "Oracle Cloud": "#FFBA36",
    "Alibaba Cloud": "#FF79FC",
    "Huawei Cloud": "#FF532C",
    "OVH": "#16E9D8",
    "Hetzner": "#06FF89",
    "DigitalOcean": "#F2FF58",
    "Vultr / Choopa": "#A700FF",
    "Contabo": "#8421A2",
    "Akamai/Linode": "#1f9d55",
    "IONOS": "#888888",
    "Leaseweb": "#6699CC",
    "WorldStream": "#A0CFB7",
    "Cherry Servers": "#F2B5A7",
    "MEVspace": "#C3B7F2",
    "HostHatch": "#88AABB",
    "Hostinger": "#AA88BB",
    "Servers.com": "#998866",
    "Clouvider": "#BBAA77",
    "Green.ch": "#7FBF7F",
    "Cogeco (CA cable ISP)": "#A0826D",
    "Sunrise (CH residential ISP)": "#B0A090",
    "Starlink": "#222222",
    "Cloudflare": "#F38020",
    "Other / on-prem": "#666666",
    "Unresolved": "#CCCCCC",
}


def load_endpoints() -> list:
    return list(csv.DictReader(open(ENDPOINTS)))


def geolite_lookup(ip: str) -> tuple:
    """(lat, lon, city, cc) or all empty."""
    try:
        import maxminddb  # type: ignore
    except ImportError:
        return ("", "", "", "")
    try:
        db = geolite_lookup._db  # type: ignore
    except AttributeError:
        if not GEOLITE.exists():
            geolite_lookup._db = None  # type: ignore
            return ("", "", "", "")
        geolite_lookup._db = maxminddb.open_database(str(GEOLITE))  # type: ignore
        db = geolite_lookup._db
    if not db:
        return ("", "", "", "")
    try:
        r = db.get(ip) or {}
    except (ValueError, OSError):
        return ("", "", "", "")
    loc = r.get("location") or {}
    city = ((r.get("city") or {}).get("names") or {}).get("en", "") or ""
    cc = ((r.get("country") or {}).get("iso_code")) or ""
    return (loc.get("latitude"), loc.get("longitude"), city, cc)


def locate_endpoints(rows: list) -> list:
    """Add lat/lon/loc_label to each endpoint row."""
    out = []
    for r in rows:
        coords = DC_COORDS.get(r["region"])
        if coords:
            lat, lon, label = coords
        else:
            lat, lon, city, cc = geolite_lookup(r["ip"])
            label = f"{city}, {cc}" if city else cc or r.get("country", "") or "?"
        r2 = dict(r)
        r2["lat"], r2["lon"], r2["loc_label"] = lat, lon, label
        out.append(r2)
    return out


TIER_OF_PROVIDER = {
    "AWS": "hyperscaler", "GCP": "hyperscaler", "Azure": "hyperscaler",
    "Oracle Cloud": "hyperscaler", "Alibaba Cloud": "hyperscaler",
    "Tencent Cloud": "hyperscaler", "Huawei Cloud": "hyperscaler",
    "OVH": "commodity-vps", "Hetzner": "commodity-vps",
    "DigitalOcean": "commodity-vps", "Vultr / Choopa": "commodity-vps",
    "Contabo": "commodity-vps", "Akamai/Linode": "commodity-vps",
    "IONOS": "commodity-vps", "Leaseweb": "commodity-vps",
    "WorldStream": "commodity-vps", "Cherry Servers": "commodity-vps",
    "MEVspace": "commodity-vps", "HostHatch": "commodity-vps",
    "Hostinger": "commodity-vps", "Servers.com": "commodity-vps",
    "Clouvider": "commodity-vps", "Cloudflare": "edge/cdn",
    "Starlink": "residential/satellite",
    "Sunrise (CH residential ISP)": "residential/satellite",
    "Green.ch": "residential/satellite",
    "Cogeco (CA cable ISP)": "residential/satellite",
    "Other / on-prem": "other-or-onprem",
    "Unresolved": "unresolved",
}


def aggregate_per_pool(located: list) -> list:
    """Return one record per pool, with the dominant (provider, location) and
    a breakdown of all touched providers/locations."""
    by_pool: dict = defaultdict(list)
    for r in located:
        by_pool[r["pool_id_bech32"]].append(r)
    out = []
    for pool, lst in by_pool.items():
        head = lst[0]
        provs = Counter(r["provider"] for r in lst)
        provider, _ = provs.most_common(1)[0]
        locs = [(r["lat"], r["lon"], r["loc_label"]) for r in lst
                if r["lat"] not in ("", None)]
        if locs:
            loc_counter = Counter((round(float(la), 2), round(float(lo), 2), lab)
                                  for la, lo, lab in locs)
            (lat, lon, label), _ = loc_counter.most_common(1)[0]
        else:
            lat, lon, label = "", "", "?"
        try:
            stake = float(head["current_active_stake_ada"] or 0)
        except (ValueError, TypeError):
            stake = 0.0
        out.append({
            "kind": "pool",
            "id": pool,
            "ticker": head.get("ticker") or "",
            "entity_id": head.get("entity_id") or "",
            "entity": head.get("display_name") or "",
            "category": head.get("category") or "",
            "cohort": "single_pool" if head.get("category") == "single_pool" else "mpo",
            "stake_ada": stake,
            "lat": lat,
            "lon": lon,
            "loc": label,
            "provider": provider,
            "tier": TIER_OF_PROVIDER.get(provider, "other-or-onprem"),
            "providers": "; ".join(f"{p}={n}" for p, n in provs.most_common()),
            "regions": "; ".join(sorted({r["region"] for r in lst})),
        })
    return out


def aggregate_per_entity(located: list) -> list:
    """One record per MPO entity (and single-pool operator). For each entity:
       - pin location = the entity's largest single (lat, lon, city) cluster
         by stake (NOT a centroid, which lands in the sea for globally
         distributed entities like Coinbase)
       - dominant provider
       - sum stake
       - list of all providers/regions touched
       - pool count
    """
    by_entity: dict = defaultdict(list)
    for r in located:
        by_entity[r["entity_id"]].append(r)
    out = []
    for eid, lst in by_entity.items():
        head = lst[0]
        try:
            stakes = {row["pool_id_bech32"]: float(row["current_active_stake_ada"] or 0)
                      for row in lst}
        except (ValueError, TypeError):
            continue
        total_stake = sum(stakes.values())
        if total_stake <= 0:
            continue
        # Find the location with the largest stake share for this entity.
        # Splitting a pool's stake evenly across its distinct relays handles
        # pools that multi-home; rounding lat/lon coalesces equivalent
        # datacentres (e.g., two AWS endpoints in the same region).
        loc_stake: Counter = Counter()
        for row in lst:
            if row["lat"] in ("", None):
                continue
            # pool relays per pool — split stake evenly across this pool's relays
            pool_rows = [r2 for r2 in lst if r2["pool_id_bech32"] == row["pool_id_bech32"]
                         and r2["lat"] not in ("", None)]
            n_rel = max(len(pool_rows), 1)
            s = stakes.get(row["pool_id_bech32"], 0) / n_rel
            key = (round(float(row["lat"]), 2), round(float(row["lon"]), 2),
                   row["loc_label"] or "?")
            loc_stake[key] += s
        if not loc_stake:
            continue
        # pick the location with the largest stake
        (lat, lon, loc_label), _ = loc_stake.most_common(1)[0]
        loc = loc_label
        # dominant provider (stake-weighted)
        prov_stake: Counter = Counter()
        for row in lst:
            s = stakes.get(row["pool_id_bech32"], 0)
            prov_stake[row["provider"]] += s
        provider, _ = prov_stake.most_common(1)[0]
        out.append({
            "kind": "entity",
            "id": eid,
            "ticker": "",
            "entity_id": eid,
            "entity": head.get("display_name") or eid,
            "category": head.get("category") or "",
            "cohort": "single_pool" if head.get("category") == "single_pool" else "mpo",
            "stake_ada": total_stake,
            "lat": round(lat, 3),
            "lon": round(lon, 3),
            "loc": loc,
            "provider": provider,
            "tier": TIER_OF_PROVIDER.get(provider, "other-or-onprem"),
            "providers": "; ".join(
                f"{p}={s/1e6:.0f}M" for p, s in prov_stake.most_common()
            ),
            "regions": "; ".join(sorted({r["region"] for r in lst})),
            "pool_count": len(stakes),
        })
    return out


HTML_TMPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cardano SPO Topology &mdash; Interactive Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<style>
  :root { --infared: #E52321; --dawn: #EC641D; --ink: #1a1a1a; --grey: #888; --line: #e5e5e5;
          --bg-soft: #f7f7f8; --hover: #f0f0f2; }
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden;
               font-family: -apple-system, system-ui, sans-serif; color: var(--ink); }
  #topbar { position: absolute; left: 0; right: 0; top: 0; height: 56px;
            padding: 0 14px 0 0; background: #fff; color: var(--ink);
            box-sizing: border-box; display: flex; align-items: stretch; gap: 16px;
            border-bottom: 1px solid var(--line); z-index: 1000;
            box-shadow: 0 1px 0 rgba(0,0,0,0.03); }
  /* Brand strip — IOG / Research, working for the Cardano community */
  #topbar .iog-strip { background: var(--infared); color: #fff;
                       display: flex; align-items: center; gap: 12px;
                       padding: 0 22px 0 14px; height: 100%;
                       clip-path: polygon(0 0, 100% 0, calc(100% - 14px) 100%, 0 100%); }
  #topbar .iog-strip .butterfly { width: 26px; height: 26px; flex-shrink: 0; }
  #topbar .iog-strip .iog-mark { display: flex; flex-direction: column;
                                 line-height: 1.0; font-weight: 700;
                                 letter-spacing: 0.02em; }
  #topbar .iog-strip .iog-mark .name { font-size: 13.5px; letter-spacing: 0.04em; }
  #topbar .iog-strip .iog-mark .for {
       font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.16em;
       color: rgba(255,255,255,0.85); font-weight: 600; margin-top: 4px;
       display: inline-flex; align-items: center; gap: 5px; }
  #topbar .iog-strip .iog-mark .for .ada {
       width: 10px; height: 10px; background: #fff; border-radius: 50%;
       display: inline-block; position: relative; }
  #topbar .iog-strip .iog-mark .for .ada::after {
       content: ''; position: absolute; top: 50%; left: 50%;
       width: 4px; height: 4px; background: var(--infared); border-radius: 50%;
       transform: translate(-50%, -50%); }
  #topbar .brand { display: flex; flex-direction: column; justify-content: center;
                   gap: 2px; padding-left: 4px; }
  #topbar h1 { font-size: 14px; margin: 0; font-weight: 700; letter-spacing: 0;
               line-height: 1.1; }
  #topbar h1 .accent { color: var(--infared); }
  #topbar .sub { color: #888; font-size: 11px; }
  #topbar .spacer { flex: 1; }
  #topbar .ctrl { display: flex; gap: 6px; align-items: center; }
  #topbar label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em;
                  color: #888; font-weight: 600; }
  #topbar select { background: var(--bg-soft); border: 1px solid var(--line);
                   color: var(--ink); padding: 5px 22px 5px 8px; font-size: 12px;
                   font-family: inherit; border-radius: 4px; cursor: pointer;
                   appearance: none; -webkit-appearance: none;
                   background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6'><path d='M0 0l5 6 5-6z' fill='%23888'/></svg>");
                   background-repeat: no-repeat; background-position: right 7px center; }
  #topbar select:hover { border-color: #bbb; }
  #topbar .chk { display: inline-flex; align-items: center; gap: 5px; font-size: 12px;
                 cursor: pointer; user-select: none; padding: 4px 8px; border-radius: 4px;
                 border: 1px solid var(--line); background: var(--bg-soft); }
  #topbar .chk:hover { border-color: #bbb; }
  #topbar .chk.on { background: var(--infared); color: #fff; border-color: var(--infared); }
  #topbar .chk input { display: none; }
  /* Primary segmented pill — used for Browse mode */
  .seg-pill { display: inline-flex; background: var(--bg-soft); border-radius: 6px;
              border: 1px solid var(--line); overflow: hidden; }
  .seg-pill button { background: none; border: 0; color: var(--ink); padding: 6px 14px;
                     font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit;
                     letter-spacing: 0.02em; }
  .seg-pill button.on { background: var(--infared); color: #fff; }
  .seg-pill button:hover:not(.on) { background: var(--hover); }
  #panel { position: absolute; left: 0; top: 56px; bottom: 0; width: 290px;
           background: var(--bg-soft); border-right: 1px solid var(--line);
           overflow-y: auto; font-size: 12px; box-sizing: border-box;
           display: flex; flex-direction: column; }
  #panel.collapsed { width: 0; overflow: hidden; }
  #panelToggle { position: absolute; left: 290px; top: 64px; width: 22px; height: 36px;
                 background: #fff; border: 1px solid var(--line); border-left: 0;
                 border-radius: 0 4px 4px 0; cursor: pointer; z-index: 999;
                 display: flex; align-items: center; justify-content: center;
                 color: #888; font-size: 14px; transition: left 0.15s; }
  #panelToggle:hover { color: var(--infared); }
  #panel.collapsed ~ #panelToggle { left: 0; }
  #map { position: absolute; left: 290px; right: 0; top: 56px; bottom: 0; transition: left 0.15s; }
  #panel.collapsed ~ #map { left: 0; }
  /* KPI block — visually prominent at top of side panel */
  #kpi { padding: 14px 16px 12px; border-bottom: 1px solid var(--line); background: #fff; }
  #kpi .label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
                color: #888; font-weight: 600; }
  #kpi .big { font-size: 26px; font-weight: 700; color: var(--infared); line-height: 1.0;
              margin-top: 2px; }
  #kpi .stake { font-size: 13px; color: var(--ink); margin-top: 4px; font-variant-numeric: tabular-nums; }
  #kpi .stake .pct { color: #888; }
  #kpi .top { font-size: 11px; color: #555; margin-top: 6px; }
  #kpi .top b { color: var(--ink); }
  /* Section bodies */
  .section { padding: 12px 16px; border-bottom: 1px solid var(--line); }
  .section h2 { font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
                margin: 0 0 8px; color: #888; font-weight: 600;
                display: flex; align-items: center; }
  .section h2 .sublabel { margin-left: auto; font-size: 10px; color: #aaa;
                          text-transform: none; letter-spacing: 0; font-weight: 400; }
  /* Search box */
  #searchBox { width: 100%; padding: 6px 10px; box-sizing: border-box;
               border: 1px solid var(--line); border-radius: 4px;
               font-family: inherit; font-size: 12px; background: #fff; }
  #searchBox:focus { outline: 0; border-color: var(--infared); }
  /* Filter list */
  #filterList { list-style: none; padding: 0; margin: 0; }
  #filterList li { display: flex; align-items: center; padding: 4px 6px; gap: 8px;
                   cursor: pointer; user-select: none; border-radius: 3px; font-size: 11.5px; }
  #filterList li.off { opacity: 0.4; }
  #filterList li .sw { width: 11px; height: 11px; border-radius: 50%;
                       border: 1px solid #00000022; flex-shrink: 0; }
  #filterList li .pct { margin-left: auto; font-variant-numeric: tabular-nums;
                        color: #666; font-size: 10.5px; }
  #filterList li:hover { background: var(--hover); }
  /* Fleet-graph banner — appears when an entity is selected */
  #fleetBanner { position: absolute; top: 60px; left: 50%; transform: translateX(-50%);
                 background: #fff; border: 1px solid var(--line); border-radius: 4px;
                 box-shadow: 0 2px 8px rgba(0,0,0,0.12); padding: 6px 8px 6px 14px;
                 z-index: 998; display: none; align-items: center; gap: 12px;
                 font-size: 12px; }
  #fleetBanner.on { display: flex; }
  #fleetBanner .ent { font-weight: 700; color: var(--infared); }
  #fleetBanner .meta { color: #666; }
  #fleetBanner button { background: var(--bg-soft); border: 1px solid var(--line);
                        color: var(--ink); padding: 3px 8px; border-radius: 3px;
                        font-size: 11px; cursor: pointer; font-family: inherit; }
  #fleetBanner button:hover { background: var(--hover); border-color: #bbb; }
  /* Fleet pool marker — small dot, subtle */
  .fleet-pool { stroke: #fff; stroke-width: 1; }
  .fleet-line { stroke-opacity: 0.55; }
  #entityPanel { margin-top: 8px; }
  #entityPanel .group { margin-bottom: 10px; }
  #entityPanel .grpHead { display: flex; align-items: center; gap: 6px;
                          font-size: 11px; text-transform: uppercase;
                          letter-spacing: 0.05em; color: #555;
                          margin-bottom: 4px; cursor: pointer; }
  #entityPanel .grpHead .arrow { transition: transform 0.15s; font-size: 10px; }
  #entityPanel .grpHead.collapsed .arrow { transform: rotate(-90deg); }
  #entityPanel .grpHead .count { margin-left: auto; color: #999; font-size: 10px;
                                  text-transform: none; letter-spacing: 0; }
  #entityPanel ul { margin: 0; padding: 0; max-height: none; }
  #entityPanel ul.collapsed { display: none; }
  #entityPanel li { display: flex; align-items: center; padding: 3px 4px;
                    gap: 6px; font-size: 11px; border-radius: 3px; }
  #entityPanel li .ent-name { white-space: nowrap; overflow: hidden;
                              text-overflow: ellipsis; max-width: 145px; }
  #entityPanel li .ent-val { margin-left: auto; color: #555;
                             font-variant-numeric: tabular-nums;
                             font-size: 10.5px; }
  #entityPanel li .ent-pools { color: #999; font-size: 9.5px; margin-left: 2px; }
  #entityPanel .more { padding: 4px 6px; color: #888; font-size: 10px;
                       cursor: pointer; }
  #entityPanel .more:hover { color: #E52321; }
  .pin { border-radius: 50%; opacity: 0.85; border: 1px solid #00000033; }
  .leaflet-popup-content { font-size: 12px; line-height: 1.4; max-width: 260px; }
  .leaflet-popup-content .ticker { font-weight: 700; color: var(--infared); }
  .leaflet-popup-content .stk { font-weight: 700; font-size: 13px; }
  /* Cluster-stats hover tooltip — clean white card. */
  .leaflet-tooltip.cluster-stats { background: #fff; border: 1px solid #ddd;
                                   box-shadow: 0 6px 20px rgba(0,0,0,0.18);
                                   border-radius: 6px; padding: 8px 10px;
                                   color: #1a1a1a; min-width: 160px; }
  .leaflet-tooltip.cluster-stats::before { display: none; }
  /* Isolate mode — when an entity is selected via the side list or a
     pin click, dim everything else on the map so only the entity's
     fleet (the star graph) is visually prominent. */
  .leaflet-container.isolated .leaflet-marker-cluster,
  .leaflet-container.isolated .pin:not(.fleet-pool),
  .leaflet-container.isolated .leaflet-heatmap-layer {
    opacity: 0.08 !important;
    pointer-events: none !important;
    transition: opacity 0.2s ease;
  }
</style>
</head>
<body>
<div id="topbar">
  <a class="iog-strip" href="https://iohk.io/" target="_blank" rel="noopener" style="text-decoration:none">
    <svg class="butterfly" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <!-- IOG butterfly mark, simplified — two opposed triangles -->
      <path d="M32 8 L8 32 L32 32 Z" fill="#fff"/>
      <path d="M32 56 L56 32 L32 32 Z" fill="#fff"/>
      <path d="M32 8 L56 32 L32 32 Z" fill="#fff" opacity="0.55"/>
      <path d="M32 56 L8 32 L32 32 Z" fill="#fff" opacity="0.55"/>
    </svg>
    <span class="iog-mark">
      <span class="name">Input | Output &middot; Cardano Business Unit</span>
      <span class="for"><span aria-hidden="true">↳</span> for the <span class="ada" aria-hidden="true"></span> Cardano community</span>
    </span>
  </a>
  <div class="brand">
    <h1>Mainnet Diagnostic <span class="accent">·</span> SPO Topology</h1>
    <div class="sub" id="snapshot"></div>
  </div>
  <div class="spacer"></div>
  <div class="ctrl seg-pill" id="browseSeg">
    <button data-v="entity">Entities</button>
    <button data-v="pool" class="on">Pools</button>
  </div>
  <div class="ctrl">
    <label>Cohort</label>
    <select id="cohortSelect">
      <option value="all">All</option>
      <option value="mpo">MPO only</option>
      <option value="spo">Single-pool only</option>
    </select>
  </div>
  <div class="ctrl">
    <label>Colour by</label>
    <select id="colorSelect">
      <option value="provider">Provider</option>
      <option value="tier">Infrastructure tier</option>
      <option value="saturation">Saturation tier</option>
      <option value="cohort">Cohort (MPO / SPO)</option>
    </select>
  </div>
  <label class="chk" id="prodChk"><input type="checkbox" id="prodInput"/>Productive (≥3M only)</label>
  <label class="chk" id="heatChk"><input type="checkbox" id="heatInput"/>Heatmap</label>
</div>
<div id="panel">
  <div id="kpi">
    <div class="label">Current view</div>
    <div class="big" id="kpiCount">&mdash;</div>
    <div class="stake" id="kpiStake">&mdash;</div>
    <div class="top" id="kpiTop">&mdash;</div>
  </div>
  <div class="section">
    <h2 id="filterHeading">Filter by provider <span class="sublabel">click to toggle</span></h2>
    <ul id="filterList"></ul>
  </div>
  <div class="section" style="flex:1; min-height:0; overflow-y:auto;
                                display:flex; flex-direction:column;">
    <h2 style="flex-shrink:0">Entities in view <span class="sublabel">click to fly to</span></h2>
    <input id="searchBox" type="text" placeholder="Search entity / ticker..."
            autocomplete="off" style="flex-shrink:0"/>
    <div id="entityPanel" style="margin-top:8px; flex:1; overflow-y:auto;
                                  min-height:0;"></div>
  </div>
  <div class="section" style="font-size:10.5px; color:#888;">
    z<sub>0</sub> = <span id="z0Label"></span>M ADA  &middot;  k=<span id="kLabel"></span>  &middot;  supply <span id="supplyLabel"></span>B
    <br/>Tiers per <a href="https://github.com/input-output-hk/spo-incentives/blob/main/reward-system-spec/diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions" target="_blank" style="color:#888;text-decoration:underline">diagnostic 4.1.3</a>.
  </div>
</div>
<button id="panelToggle" title="Toggle side panel">‹</button>
<div id="fleetBanner">
  <span>Fleet: <span class="ent" id="fleetEnt"></span></span>
  <span class="meta" id="fleetMeta"></span>
  <button id="fleetClear">Clear (Esc)</button>
</div>
<div id="map"></div>
<script>
const RAW = __DATA__;
const COLORS = __COLORS__;
const TIER_COLORS = __TIER_COLORS__;
const COHORT_COLORS = __COHORT_COLORS__;
const SAT_COLORS = __SAT_COLORS__;
const SAT_POINT_M = __SAT_POINT_M__;   // z0 in M ADA
const SUPPLY_B = __SUPPLY_B__;         // total supply in B ADA
const TOTAL_STAKE_B = __TOTAL_STAKE_B__;  // total active stake in B ADA (fixed network total)
const EPOCH = __EPOCH__;
const K_PARAM = __K_PARAM__;
const PRODUCTIVE_THRESHOLD_M = __PRODUCTIVE_THRESHOLD_M__;
const SNAPSHOT = __SNAPSHOT__;
const SAT_TIER_ORDER = __TIER_ORDER__;

const POOL_DATA = RAW.filter(r => r.kind === 'pool');
const ENTITY_DATA = RAW.filter(r => r.kind === 'entity');

document.getElementById('snapshot').textContent = SNAPSHOT;
document.getElementById('z0Label').textContent = SAT_POINT_M.toFixed(1);
document.getElementById('kLabel').textContent = K_PARAM;
document.getElementById('supplyLabel').textContent = SUPPLY_B;

const state = {
  cohort: 'all',     // all | mpo | spo (filter — who to include)
  pop: 'all',        // all | productive (filter — size cutoff)
  agg: 'pool',       // pool | entity (browse mode — what to count)
  color: 'provider', // provider | tier | cohort | saturation
  // metric is auto-derived from color: stake by default,
  // saturation% when color=saturation
  layer: 'pins',     // pins | both (when heatmap is enabled)
  search: '',
  enabledKeys: new Set(),
};
// Derive metric from color choice — keeps the API simple
function currentMetric() {
  return state.color === 'saturation' ? 'saturation' : 'stake';
}

const map = L.map('map', {worldCopyJump: true, preferCanvas: true}).setView([35, 10], 3);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap', maxZoom: 18
}).addTo(map);

// Wire the new orthogonal controls
// Browse: Entities | Pools — primary axis (what each map pin represents)
document.querySelectorAll('#browseSeg button').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('#browseSeg button').forEach(x => x.classList.remove('on'));
    b.classList.add('on');
    state.agg = b.dataset.v;
    rebuild();
  };
});
// Cohort: who to include in the view
document.getElementById('cohortSelect').onchange = (e) => {
  state.cohort = e.target.value;
  state.enabledKeys = new Set();
  rebuild();
};
// Colour: visual encoding only
document.getElementById('colorSelect').onchange = (e) => {
  state.color = e.target.value;
  state.enabledKeys = new Set();
  rebuild();
};
document.getElementById('prodInput').onchange = (e) => {
  state.pop = e.target.checked ? 'productive' : 'all';
  document.getElementById('prodChk').classList.toggle('on', e.target.checked);
  state.enabledKeys = new Set();
  rebuild();
};
document.getElementById('heatInput').onchange = (e) => {
  state.layer = e.target.checked ? 'both' : 'pins';
  document.getElementById('heatChk').classList.toggle('on', e.target.checked);
  rebuild();
};
document.getElementById('searchBox').oninput = (e) => {
  state.search = e.target.value.trim().toLowerCase();
  renderEntityPanel(activeData().filter(r => state.enabledKeys.has(colorKey(r))),
                    activeData().reduce((a, r) => a + r.stake_ada, 0));
};
document.getElementById('panelToggle').onclick = () => {
  const p = document.getElementById('panel');
  p.classList.toggle('collapsed');
  const tgl = document.getElementById('panelToggle');
  tgl.textContent = p.classList.contains('collapsed') ? '›' : '‹';
  setTimeout(() => map.invalidateSize(), 200);
};

function activeData() {
  const src = state.agg === 'entity' ? ENTITY_DATA : POOL_DATA;
  return src.filter(r => {
    if (state.cohort === 'mpo' && r.cohort !== 'mpo') return false;
    if (state.cohort === 'spo' && r.cohort !== 'single_pool') return false;
    if (state.pop === 'productive' && !r.productive) return false;
    return r.lat !== '' && r.lat !== null;
  });
}

function colorKey(r) {
  if (state.color === 'tier') return r.tier;
  if (state.color === 'cohort') return r.cohort === 'mpo' ? 'MPO entity' : 'Single-pool operator';
  if (state.color === 'saturation') return r.saturation_tier;
  return r.provider;
}

function colorFor(key) {
  if (state.color === 'tier') return TIER_COLORS[key] || '#666';
  if (state.color === 'cohort') return COHORT_COLORS[key] || '#666';
  if (state.color === 'saturation') return SAT_COLORS[key] || '#666';
  return COLORS[key] || '#666';
}

// Metric value used for size, KPI, and heat weight.
function metricValue(r) {
  if (currentMetric() === 'saturation') return r.saturation_pct;
  if (currentMetric() === 'blocks') return r.expected_blocks_per_epoch;
  return r.stake_ada;
}

function metricLabel(v) {
  if (currentMetric() === 'saturation') return v.toFixed(1) + '%';
  if (currentMetric() === 'blocks') return v.toFixed(2) + ' blk/epoch';
  return (v / 1e6).toFixed(1) + 'M ADA';
}

function radiusFor(r, agg) {
  const m = metricValue(r);
  if (!m) return 4;
  const base = agg === 'entity' ? 6 : 4;
  // mapping is logarithmic but the scale depends on metric
  if (currentMetric() === 'saturation') {
    return Math.max(base, Math.min(34, base + Math.log10(1 + m) * 6.0));
  }
  if (currentMetric() === 'blocks') {
    return Math.max(base, Math.min(34, base + Math.log10(1 + m * 100) * 4.0));
  }
  return Math.max(base, Math.min(30, base + Math.log10(m) * 2.0));
}

function heatWeight(r) {
  const m = metricValue(r);
  if (currentMetric() === 'saturation') return Math.min(20, Math.sqrt(m));
  if (currentMetric() === 'blocks') return Math.min(20, Math.sqrt(m * 100));
  return Math.sqrt(m);
}

let pinLayer = null;
let heatLayer = null;

// Build a {entity_id: {entity, lat, lon, stake_ada, pool_count, providers, regions, cohort,
//                       saturation_pct, saturation_tier, productive}} map keyed by entity_id.
const ENTITY_INDEX = {};
ENTITY_DATA.forEach(e => { ENTITY_INDEX[e.entity_id] = e; });

function entitiesFromCurrentView(filtered) {
  // If aggregation is per entity, just use filtered records directly.
  if (state.agg === 'entity') return filtered;
  // Otherwise, look up entities corresponding to the filtered pool ids and
  // recompute the per-entity stake within the current filter (so that
  // toggling provider filters changes the entity's "stake in view").
  const buckets = {};
  filtered.forEach(p => {
    const eid = p.entity_id;
    if (!eid) return;
    const meta = ENTITY_INDEX[eid];
    if (!meta || meta.lat === '' || meta.lat === null) return;
    if (!buckets[eid]) {
      buckets[eid] = {
        entity_id: eid,
        entity: meta.entity,
        cohort: meta.cohort,
        lat: meta.lat,
        lon: meta.lon,
        loc: meta.loc,
        provider: meta.provider,
        tier: meta.tier,
        saturation_tier: meta.saturation_tier,
        productive: meta.productive,
        pool_count: 0,
        stake_ada: 0,
      };
    }
    buckets[eid].pool_count += 1;
    buckets[eid].stake_ada += p.stake_ada;
  });
  return Object.values(buckets);
}

function renderEntityPanel(filtered, totalAda) {
  const panel = document.getElementById('entityPanel');
  panel.innerHTML = '';
  let ents = entitiesFromCurrentView(filtered)
    .sort((a, b) => b.stake_ada - a.stake_ada);
  if (state.search) {
    const q = state.search;
    ents = ents.filter(e =>
      (e.entity || '').toLowerCase().includes(q)
      || (e.entity_id || '').toLowerCase().includes(q)
    );
  }
  const groups = [
    { key: 'mpo', label: 'MPO entities',
      items: ents.filter(e => e.cohort === 'mpo') },
    { key: 'spo', label: 'Single-pool operators',
      items: ents.filter(e => e.cohort === 'single_pool') },
  ];
  const expanded = window._entityGroupsExpanded || (window._entityGroupsExpanded = {mpo: true, spo: false});
  const limits = window._entityLimits || (window._entityLimits = {mpo: 100, spo: 25});
  groups.forEach(g => {
    if (state.cohort === 'mpo' && g.key !== 'mpo') return;
    if (state.cohort === 'spo' && g.key !== 'spo') return;
    const wrap = document.createElement('div'); wrap.className = 'group';
    const head = document.createElement('div'); head.className = 'grpHead';
    if (!expanded[g.key]) head.classList.add('collapsed');
    const arrow = document.createElement('span'); arrow.className = 'arrow'; arrow.textContent = '▼';
    const label = document.createElement('span'); label.textContent = g.label;
    const count = document.createElement('span'); count.className = 'count';
    const totalStake = g.items.reduce((a, e) => a + e.stake_ada, 0);
    count.textContent = g.items.length + ' (' + (totalStake/1e9).toFixed(2) + 'B ADA)';
    head.appendChild(arrow); head.appendChild(label); head.appendChild(count);
    const ul = document.createElement('ul');
    if (!expanded[g.key]) ul.classList.add('collapsed');
    head.onclick = () => {
      expanded[g.key] = !expanded[g.key];
      head.classList.toggle('collapsed', !expanded[g.key]);
      ul.classList.toggle('collapsed', !expanded[g.key]);
    };
    const limit = limits[g.key];
    g.items.slice(0, limit).forEach(e => {
      const li = document.createElement('li');
      const sw = document.createElement('span');
      sw.className = 'sw'; sw.style.background = colorFor(colorKey(e));
      const nm = document.createElement('span'); nm.className = 'ent-name';
      nm.textContent = e.entity || e.entity_id;
      nm.title = e.entity_id;
      const pc = document.createElement('span'); pc.className = 'ent-pools';
      pc.textContent = e.pool_count > 1 ? '(' + e.pool_count + ')' : '';
      const val = document.createElement('span'); val.className = 'ent-val';
      val.textContent = (e.stake_ada / 1e6).toFixed(1) + 'M ADA · ' +
                        (100 * e.stake_ada / totalAda).toFixed(1) + '%';
      li.appendChild(sw); li.appendChild(nm); li.appendChild(pc); li.appendChild(val);
      li.style.cursor = 'pointer';
      li.onclick = () => flyToEntity(e);
      ul.appendChild(li);
    });
    if (g.items.length > limit) {
      const more = document.createElement('div'); more.className = 'more';
      more.textContent = '+ show ' + Math.min(50, g.items.length - limit) + ' more...';
      more.onclick = () => {
        limits[g.key] = limit + 50;
        rebuild();
      };
      ul.appendChild(more);
    }
    wrap.appendChild(head);
    wrap.appendChild(ul);
    panel.appendChild(wrap);
  });
}

let _activeEntityMarker = null;
let _fleetLayer = null;
let _selectedEntityId = null;
let _hiddenPinLayer = null;
let _hiddenHeatLayer = null;

// Fleet-graph layer — for a given entity, draw every one of its pools as a
// small node and a polyline from each pool to the entity's centroid. The
// star layout makes the operator's geographic spread legible at a glance.
function showFleetGraph(eid) {
  clearFleet();
  _selectedEntityId = eid;
  const ent = ENTITY_INDEX[eid];
  if (!ent || ent.lat === '' || ent.lat === null) return;
  // pick all pools belonging to this entity that have a resolvable location
  const pools = POOL_DATA.filter(p => p.entity_id === eid
    && p.lat !== '' && p.lat !== null);
  if (!pools.length) return;
  const entColor = colorFor(colorKey(ent));
  const layers = [];
  // Draw lines first so pool dots sit on top
  pools.forEach(p => {
    if (p.lat === ent.lat && p.lon === ent.lon) return;  // skip self-loop
    layers.push(L.polyline(
      [[ent.lat, ent.lon], [p.lat, p.lon]],
      {color: entColor, weight: 1.2, opacity: 0.55, className: 'fleet-line',
       dashArray: '3,4'}
    ));
  });
  // Pool nodes — small fixed-radius dots, coloured by the same scheme as the map
  pools.forEach(p => {
    const m = L.circleMarker([p.lat, p.lon], {
      radius: 5, fillColor: colorFor(colorKey(p)),
      color: '#222', weight: 1, fillOpacity: 0.95, className: 'fleet-pool',
    });
    const tier = p.saturation_tier || p.tier || '?';
    m.bindPopup(
      '<span class="ticker">' + (p.ticker || p.id.slice(0, 12)) + '</span>'
      + ' <span style="color:#888;font-size:11px">' + p.entity + '</span>'
      + '<br/><span class="stk">' + (p.stake_ada/1e6).toFixed(1) + 'M ADA</span>'
      + ' &middot; ' + tier
      + '<br/><span style="color:#666">' + p.loc + ' &middot; ' + p.provider + '</span>'
      + '<br/><span style="color:#888;font-size:11px">Region: ' + p.region + '</span>'
    );
    layers.push(m);
  });
  // Centroid pin — large ring on top
  const centroid = L.circleMarker([ent.lat, ent.lon], {
    radius: 18, fillColor: entColor, color: '#000', weight: 2.5, fillOpacity: 0.45,
    className: 'pin',
  });
  centroid.bindPopup(
    '<span class="ticker">' + ent.entity + '</span>'
    + '  <span style="color:#888;font-size:11px">[' + pools.length + ' pools]</span>'
    + '<br/><span class="stk">' + (ent.stake_ada/1e6).toFixed(1) + 'M ADA</span>'
    + ' &middot; centroid: ' + ent.loc
    + '<br/><span style="color:#666">Click any pool dot for its details.</span>'
  );
  layers.push(centroid);
  _fleetLayer = L.layerGroup(layers).addTo(map);
  // Isolate mode — remove the main pin/heat layers so only this fleet
  // shows on the map. We keep references on the closure so clearFleet
  // can put them back without rebuilding from scratch.
  if (pinLayer) { map.removeLayer(pinLayer); _hiddenPinLayer = pinLayer; pinLayer = null; }
  if (heatLayer) { map.removeLayer(heatLayer); _hiddenHeatLayer = heatLayer; heatLayer = null; }
  map.getContainer().classList.add('isolated');
  // Frame map on the fleet bounds
  const all = pools.concat([ent]).map(x => [x.lat, x.lon]);
  map.flyToBounds(L.latLngBounds(all), {padding: [60, 60], maxZoom: 6, duration: 0.6});
  // Banner
  const banner = document.getElementById('fleetBanner');
  document.getElementById('fleetEnt').textContent = ent.entity;
  document.getElementById('fleetMeta').textContent =
    pools.length + ' pools · ' + (ent.stake_ada/1e6).toFixed(1) + 'M ADA · ' +
    'centroid ' + ent.loc;
  banner.classList.add('on');
}

function clearFleet() {
  if (_fleetLayer) { map.removeLayer(_fleetLayer); _fleetLayer = null; }
  // Restore the main layers
  if (_hiddenPinLayer) { map.addLayer(_hiddenPinLayer); pinLayer = _hiddenPinLayer; _hiddenPinLayer = null; }
  if (_hiddenHeatLayer) { map.addLayer(_hiddenHeatLayer); heatLayer = _hiddenHeatLayer; _hiddenHeatLayer = null; }
  _selectedEntityId = null;
  map.getContainer().classList.remove('isolated');
  document.getElementById('fleetBanner').classList.remove('on');
}

function flyToEntity(ent) {
  if (ent.lat === '' || ent.lat === null) return;
  // For multi-pool entities, render the fleet graph automatically.
  if (ent.pool_count && ent.pool_count > 1) {
    showFleetGraph(ent.entity_id);
    return;
  }
  // Single-pool case: just fly + pop the marker
  map.flyTo([ent.lat, ent.lon], Math.max(map.getZoom(), 5), {duration: 0.6});
  if (_activeEntityMarker) map.removeLayer(_activeEntityMarker);
  const m = L.circleMarker([ent.lat, ent.lon], {
    radius: 16, fillColor: colorFor(colorKey(ent)),
    color: '#000', weight: 2, fillOpacity: 0.55, className: 'pin',
  });
  m.bindPopup(
    '<span class="ticker">' + ent.entity + '</span>'
    + '<br/><span class="stk">' + (ent.stake_ada/1e6).toFixed(1) + 'M ADA</span>'
    + ' &middot; ' + (ent.saturation_tier || ent.tier || '?')
    + '<br/><span style="color:#666">' + ent.loc + ' &middot; provider: ' + ent.provider + '</span>'
  ).addTo(map).openPopup();
  _activeEntityMarker = m;
}

// Fleet clear handlers
document.getElementById('fleetClear').onclick = clearFleet;
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') clearFleet();
});

function rebuild() {
  // tally by colour key over the active cohort+agg
  const data = activeData();
  const tally = {};
  data.forEach(r => {
    const k = colorKey(r);
    tally[k] = (tally[k] || 0) + r.stake_ada;
  });
  // ordering: saturation has a natural order, others sort by stake
  let ordered;
  if (state.color === 'saturation') {
    ordered = SAT_TIER_ORDER.filter(k => tally[k]).map(k => [k, tally[k]]);
  } else {
    ordered = Object.entries(tally).sort((a,b) => b[1] - a[1]);
  }
  if (state.enabledKeys.size === 0) {
    state.enabledKeys = new Set(ordered.map(x => x[0]));
  }
  // KPI
  const totalAda = data.reduce((a,r) => a + r.stake_ada, 0);
  const filtered = data.filter(r => state.enabledKeys.has(colorKey(r)));
  const filteredAda = filtered.reduce((a,r) => a + r.stake_ada, 0);
  const label = state.agg === 'entity' ? 'entities' : 'pools';
  document.getElementById('kpiCount').textContent =
    filtered.length.toLocaleString() + ' ' + label;
  // Show stake-in-view + share of TOTAL NETWORK staked (fixed denominator,
  // not "% of view" which is trivially 100% before any filter narrows the
  // colour dimension).
  const totalStakeAda = TOTAL_STAKE_B * 1e9;
  const networkShare = (100 * filteredAda / totalStakeAda).toFixed(1);
  document.getElementById('kpiStake').innerHTML =
    (filteredAda / 1e9).toFixed(2) + 'B ADA &nbsp;'
    + '<span class="pct">' + networkShare + '% of network ('
    + TOTAL_STAKE_B.toFixed(2) + 'B staked)</span>';
  // KPI line 3 changes meaning with the metric
  let kpi3 = '';
  if (currentMetric() === 'saturation' || state.color === 'saturation') {
    const isPool = state.agg !== 'entity';
    const tierFn = (r) => r.saturation_tier;
    const sat = filtered.filter(r => tierFn(r) === 'Saturated' || tierFn(r) === 'Oversaturated').length;
    const hlth = filtered.filter(r => tierFn(r) === 'Healthy' || tierFn(r) === 'Large healthy' || tierFn(r) === 'Near-saturation').length;
    const sub = filtered.filter(r => ['Sub-block','Sub-reliable','Dormant','Zero-stake'].includes(tierFn(r))).length;
    kpi3 = 'z<sub>0</sub> = ' + SAT_POINT_M.toFixed(1) + 'M ADA  (supply ' + SUPPLY_B + 'B / k=' + K_PARAM + ')<br/>'
         + '<b>' + sat + '</b> at/over &middot; <b>' + hlth + '</b> healthy &middot; <b>' + sub + '</b> sub-viable';
  } else if (currentMetric() === 'blocks') {
    const total_blocks = filtered.reduce((a,r) => a + r.expected_blocks_per_epoch, 0);
    const n_active = filtered.filter(r => r.expected_blocks_per_epoch >= 1).length;
    kpi3 = '~' + total_blocks.toFixed(0) + ' blocks / epoch expected<br/>'
         + '<b>' + n_active + '</b> with &ge; 1 block / epoch';
  } else if (ordered.length) {
    const [topK, topS] = ordered[0];
    kpi3 = 'Top: ' + topK + '  (' + (100 * topS / totalAda).toFixed(1) + '%)';
  }
  document.getElementById('kpiTop').innerHTML = kpi3;
  // entity-list panel
  renderEntityPanel(filtered, totalAda);
  // filter list
  const ul = document.getElementById('filterList');
  ul.innerHTML = '';
  const filterTitle = {provider:'Filter by provider', tier:'Filter by tier',
                       cohort:'Filter by cohort',
                       saturation:'Filter by saturation tier'}[state.color];
  document.getElementById('filterHeading').textContent = filterTitle;
  ordered.forEach(([k, st]) => {
    const li = document.createElement('li');
    const sw = document.createElement('span');
    sw.className = 'sw'; sw.style.background = colorFor(k);
    const lbl = document.createElement('span'); lbl.textContent = k;
    const pct = document.createElement('span'); pct.className = 'pct';
    pct.textContent = (100 * st / totalAda).toFixed(1) + '%';
    li.appendChild(sw); li.appendChild(lbl); li.appendChild(pct);
    if (!state.enabledKeys.has(k)) li.classList.add('off');
    li.onclick = () => {
      if (state.enabledKeys.has(k)) state.enabledKeys.delete(k);
      else state.enabledKeys.add(k);
      rebuild();
    };
    ul.appendChild(li);
  });
  // map layers
  if (pinLayer) { map.removeLayer(pinLayer); pinLayer = null; }
  if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
  const drawPins = state.layer === 'pins' || state.layer === 'both';
  const drawHeat = state.layer === 'heat' || state.layer === 'both';
  if (drawPins) {
    const cluster = L.markerClusterGroup({maxClusterRadius: state.agg === 'entity' ? 25 : 35,
                                           chunkedLoading: true});
    // Hover-tooltip on cluster bubbles — summarises what's hidden
    // inside (pool / entity count, total stake, top providers / locations).
    cluster.on('clustermouseover', function(e) {
      const records = e.layer.getAllChildMarkers()
        .map(m => m._record).filter(Boolean);
      if (!records.length) return;
      // Stats are contextual to the current view — Browse mode (entity vs
      // pool), Cohort, Productive filter, AND the colour dimension. The
      // breakdown follows whatever Colour-by mode is active so it always
      // tells the user "what is this cluster made of, IN THE DIMENSION
      // I am looking at right now".
      const totalStake = records.reduce((a, r) => a + r.stake_ada, 0);
      const networkPct = 100 * totalStake / (TOTAL_STAKE_B * 1e9);
      const unitLabel = state.agg === 'entity' ? 'entities' : 'pools';
      // Tally by current colour dimension
      const dimTally = {};
      records.forEach(r => {
        const k = colorKey(r);
        dimTally[k] = (dimTally[k] || 0) + r.stake_ada;
      });
      const topDim = Object.entries(dimTally)
        .sort((a, b) => b[1] - a[1]).slice(0, 4);
      const dimLabel = {provider:'By provider', tier:'By tier',
                        cohort:'By cohort', saturation:'By saturation tier'}[state.color];
      const dimHtml = topDim.map(([k, s]) =>
        `<div style="display:flex;align-items:center;gap:6px;padding:1px 0">` +
          `<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${colorFor(k)};flex-shrink:0"></span>` +
          `<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1">${k}</span>` +
          `<span style="color:#888;font-variant-numeric:tabular-nums">${(100*s/totalStake).toFixed(0)}%</span>` +
        `</div>`
      ).join('');
      // Top locations independent of colour mode
      const locTally = {};
      records.forEach(r => { locTally[r.loc] = (locTally[r.loc] || 0) + r.stake_ada; });
      const topLocs = Object.entries(locTally)
        .sort((a, b) => b[1] - a[1]).slice(0, 2)
        .map(([l]) => l);
      // Cohort split — only meaningful when Cohort filter is "All"
      let cohortLine = '';
      if (state.cohort === 'all') {
        const mpo = records.filter(r => r.cohort === 'mpo')
                           .reduce((a, r) => a + r.stake_ada, 0);
        const spo = totalStake - mpo;
        if (mpo && spo) {
          cohortLine = `<div style="font:400 10.5px/1.4 -apple-system,sans-serif;color:#888;margin-top:4px">` +
            `MPO ${(100*mpo/totalStake).toFixed(0)}%  &middot;  SPO ${(100*spo/totalStake).toFixed(0)}%` +
            `</div>`;
        }
      }
      const html =
        `<div style="font:600 11px/1.2 -apple-system,sans-serif;color:#E52321;text-transform:uppercase;letter-spacing:.06em">` +
          `${records.length} ${unitLabel} in cluster` +
        `</div>` +
        `<div style="font:700 16px/1.1 -apple-system,sans-serif;margin-top:3px">` +
          `${(totalStake/1e9).toFixed(2)}B ADA` +
          `<span style="font-weight:400;color:#888;font-size:11px;margin-left:6px">${networkPct.toFixed(1)}% of network</span>` +
        `</div>` +
        cohortLine +
        `<div style="font:600 9.5px/1 -apple-system,sans-serif;color:#888;text-transform:uppercase;letter-spacing:.08em;margin:8px 0 4px;border-top:1px solid #eee;padding-top:6px">` +
          dimLabel +
        `</div>` +
        `<div style="font:400 11.5px/1.3 -apple-system,sans-serif;color:#333">${dimHtml}</div>` +
        `<div style="font:400 10.5px/1.4 -apple-system,sans-serif;color:#888;margin-top:6px;border-top:1px solid #eee;padding-top:5px">` +
          topLocs.join(' &middot; ') +
        `</div>`;
      e.layer.bindTooltip(html, {sticky:true, direction:'top', offset:[0,-8],
                                  opacity:1, className:'cluster-stats'})
             .openTooltip();
    });
    cluster.on('clustermouseout', function(e) {
      e.layer.unbindTooltip();
    });
    filtered.forEach(r => {
      const c = L.circleMarker([r.lat, r.lon], {
        radius: radiusFor(r, state.agg),
        fillColor: colorFor(colorKey(r)),
        color: '#222', weight: 0.6, fillOpacity: 0.85,
        className: 'pin',
      });
      c._record = r;  // attach for cluster-stats lookup
      // Hover tooltip on the individual pin — same card style as the
      // cluster-stats tooltip but with the single record's details.
      const isEnt = r.kind === 'entity';
      const tierBadgeBg = SAT_COLORS[r.saturation_tier] || '#888';
      const tipHead = isEnt
        ? `<div style="font:600 11px/1.2 -apple-system,sans-serif;color:#E52321;text-transform:uppercase;letter-spacing:.06em">${r.entity}</div>`
        : `<div style="font:600 11px/1.2 -apple-system,sans-serif;color:#E52321;text-transform:uppercase;letter-spacing:.06em">${r.ticker || r.id.slice(0,12)}</div>` +
          `<div style="font:400 10.5px/1.3 -apple-system,sans-serif;color:#888;margin-top:1px">${r.entity}</div>`;
      const tipSub = isEnt
        ? `<span style="color:#888;font-size:10.5px;margin-left:4px">[${r.pool_count} pool${r.pool_count>1?'s':''}]</span>`
        : '';
      const tip =
        tipHead +
        `<div style="font:700 16px/1.1 -apple-system,sans-serif;margin-top:4px">` +
          `${(r.stake_ada/1e6).toFixed(1)}M ADA${tipSub}` +
        `</div>` +
        `<div style="font:400 10.5px/1.4 -apple-system,sans-serif;margin-top:5px;display:flex;align-items:center;gap:6px;flex-wrap:wrap">` +
          `<span style="background:${tierBadgeBg};color:#fff;padding:2px 6px;border-radius:3px;font-weight:600;font-size:10px">${r.saturation_tier}</span>` +
          `<span style="color:#666">~${r.expected_blocks_per_epoch.toFixed(2)} blk/epoch</span>` +
        `</div>` +
        `<div style="font:400 11px/1.4 -apple-system,sans-serif;color:#666;margin-top:6px;border-top:1px solid #eee;padding-top:5px">` +
          `<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${colorFor(r.provider)};margin-right:5px;vertical-align:-1px"></span>` +
          `${r.provider}  &middot;  ${r.tier}` +
        `</div>` +
        `<div style="font:400 10.5px/1.4 -apple-system,sans-serif;color:#888;margin-top:3px">${r.loc}</div>` +
        (isEnt
          ? `<div style="font:400 10.5px/1.4 -apple-system,sans-serif;color:#999;margin-top:5px;border-top:1px solid #eee;padding-top:4px;max-width:240px">${r.providers}</div>`
          : `<div style="font:400 10px/1.4 -apple-system,sans-serif;color:#aaa;margin-top:5px;border-top:1px solid #eee;padding-top:4px;max-width:240px">Region: ${r.regions}</div>`);
      c.bindTooltip(tip, {sticky:true, direction:'top', offset:[0,-4],
                           opacity:1, className:'cluster-stats'});
      const head = r.kind === 'entity'
        ? `<span class="ticker">${r.entity}</span>  <span style="color:#888;font-size:11px">[${r.pool_count} pool${r.pool_count>1?'s':''}]</span>`
        : `<span class="ticker">${r.ticker || r.id.slice(0,12)}</span>  <span style="color:#888">${r.entity}</span>`;
      const tierColor = SAT_COLORS[r.saturation_tier] || '#888';
      const satBadge = `<span style="background:${tierColor};color:#fff;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:700">${r.saturation_tier}</span>`;
      const satMeaning = r.kind === 'entity'
        ? ` &middot; ${r.saturation_slots.toFixed(1)} saturation-slots ` +
          `&middot; avg ${r.saturation_pct.toFixed(0)}% per pool`
        : ` &middot; ${r.saturation_pct.toFixed(0)}% of z₀`;
      const prodBadge = r.productive
        ? `<span style="background:#00B35F;color:#fff;padding:1px 5px;border-radius:3px;font-size:10px">productive</span>`
        : `<span style="background:#888;color:#fff;padding:1px 5px;border-radius:3px;font-size:10px">below 3M</span>`;
      c.bindPopup(`${head}<br/>
        <span class="stk">${(r.stake_ada/1e6).toFixed(1)}M ADA</span>
          &middot; ${satBadge}${satMeaning}<br/>
        ${prodBadge} &middot; ~${r.expected_blocks_per_epoch.toFixed(2)} blk/epoch<br/>
        <span style="color:#666">${r.loc}  &middot;  ${r.tier}  &middot;  ${r.cohort}</span><br/>
        <span style="color:#666">Providers: ${r.providers}</span><br/>
        <span style="color:#888;font-size:11px">Regions: ${r.regions}</span>`);
      cluster.addLayer(c);
    });
    pinLayer = cluster;
    map.addLayer(pinLayer);
  }
  if (drawHeat && L.heatLayer) {
    // weight by sqrt of chosen metric so a single huge pool doesn't drown
    // the long tail entirely
    const pts = filtered.map(r => [r.lat, r.lon, heatWeight(r)]);
    if (pts.length) {
      heatLayer = L.heatLayer(pts, {radius: 25, blur: 18, maxZoom: 6, minOpacity: 0.35});
      map.addLayer(heatLayer);
    }
  }
}
rebuild();
</script>
</body>
</html>
"""


TIER_COLOR = {
    "hyperscaler": "#E52321",            # Infared
    "commodity-vps": "#16E9D8",          # Electric Blue
    "edge/cdn": "#EC641D",               # Dawn
    "residential/satellite": "#06FF89",  # Acid Green
    "other-or-onprem": "#666666",
    "unresolved": "#CCCCCC",
}

COHORT_COLOR = {
    "MPO entity": "#E52321",             # Infared — institutional
    "Single-pool operator": "#A700FF",   # Ultraviolet — long tail
}

# Canonical 9-tier palette per diagnostic build_three_thresholds_visual.py.
# Zero-stake added for completeness; the diagnostic plot omits it.
SAT_TIER_COLOR = {
    "Zero-stake":      "#222222",   # near-black — dead registration
    "Dormant":         "#555555",   # GREY_DARK
    "Sub-block":       "#EC641D",   # DAWN
    "Sub-reliable":    "#E52321",   # INFARED
    "Healthy":         "#00B35F",   # ACID_GREEN
    "Large healthy":   "#00897B",   # TEAL
    "Near-saturation": "#FFBA36",   # SOLAR_AMBER
    "Saturated":       "#2C4FFA",   # COBALT_PULSE
    "Oversaturated":   "#A700FF",   # ULTRAVIOLET
}


K_PARAM = 500  # Cardano k parameter — number of "ideal" stake pools
BLOCKS_PER_EPOCH = 21600  # 5 days × 432 active slots × f
PRODUCTIVE_THRESHOLD_ADA = 3_000_000  # POL.O4.F2 — pools below this are sub-block

# Per the diagnostic's canonical 9-tier taxonomy
# (`pools-distribution/mainnet-analysis/scripts/build_three_thresholds_visual.py`).
# Boundaries are expressed as multiples of z0 (saturation point) and absolute ADA
# floors; z0 = supply / k.
def tier_bounds_ada(z0_ada: float) -> list:
    """Tier boundaries in ADA — closed-open intervals partitioning [0, ∞)."""
    return [
        0,                  # zero-stake floor
        1,                  # > 0 starts Dormant
        100_000,            # 100k starts Sub-block
        1_000_000,          # 1M starts Sub-reliable
        3_000_000,          # 3M starts Healthy (production threshold)
        z0_ada * 0.5,       # 0.5×z0 starts Large healthy
        z0_ada * 0.8,       # 0.8×z0 starts Near-saturation
        z0_ada * 0.95,      # 0.95×z0 starts Saturated
        z0_ada * 1.05,      # 1.05×z0 starts Oversaturated
        float("inf"),
    ]


TIER_NAMES = [
    "Zero-stake",
    "Dormant",
    "Sub-block",
    "Sub-reliable",
    "Healthy",
    "Large healthy",
    "Near-saturation",
    "Saturated",
    "Oversaturated",
]


def saturation_tier_for(stake_ada: float, z0_ada: float) -> str:
    bounds = tier_bounds_ada(z0_ada)
    for i, name in enumerate(TIER_NAMES):
        if bounds[i] <= stake_ada < bounds[i + 1]:
            return name
    return TIER_NAMES[-1]


def annotate_with_saturation(records: list, z0_ada: float, total_active_stake: float) -> None:
    """Add saturation_pct (vs z0), saturation_tier (canonical 9-tier),
    saturation_slots (entity_stake / z0), and expected_blocks_per_epoch.

    For pool records, the tier is the pool's tier per the diagnostic.
    For entity records, the tier is the **mean per-pool** tier — i.e., the
    tier that the entity's average pool falls into — which is the meaningful
    operator-level read. The entity's `stake_ada` (sum across all pools) is
    NOT itself a tier (entities aren't pools).
    """
    for r in records:
        s = float(r.get("stake_ada") or 0)
        n_pools = r.get("pool_count") or 1
        if r.get("kind") == "entity" and n_pools > 0:
            avg_pool_stake = s / n_pools
            r["saturation_pct"] = round(100 * avg_pool_stake / z0_ada, 2) if z0_ada else 0
            r["saturation_slots"] = round(s / z0_ada, 2) if z0_ada else 0
            r["saturation_tier"] = saturation_tier_for(avg_pool_stake, z0_ada)
        else:
            r["saturation_pct"] = round(100 * s / z0_ada, 2) if z0_ada else 0
            r["saturation_slots"] = r["saturation_pct"] / 100
            r["saturation_tier"] = saturation_tier_for(s, z0_ada)
        r["expected_blocks_per_epoch"] = round(
            (s / total_active_stake) * BLOCKS_PER_EPOCH, 3
        ) if total_active_stake else 0
        # Productive flag — POL.O4.F2: stake ≥ 3M ADA per pool.
        # For entities: productive if at least one pool of theirs is ≥ 3M.
        if r.get("kind") == "entity":
            r["productive"] = avg_pool_stake >= PRODUCTIVE_THRESHOLD_ADA \
                or (s >= PRODUCTIVE_THRESHOLD_ADA and n_pools >= 1)
        else:
            r["productive"] = s >= PRODUCTIVE_THRESHOLD_ADA


def fetch_z0_from_koios() -> tuple:
    """Returns (z0_ada, supply_ada, epoch). Falls back to documented values if
    the API call fails."""
    import urllib.request
    try:
        req = urllib.request.Request(
            "https://api.koios.rest/api/v1/totals?limit=1&order=epoch_no.desc",
            headers={"accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        if data:
            row = data[0]
            supply_lovelace = int(row.get("supply") or 0)
            supply_ada = supply_lovelace / 1e6
            epoch = int(row.get("epoch_no") or 0)
            z0_ada = supply_ada / K_PARAM
            print(f"  z0 = supply / k = {supply_ada/1e9:.2f}B / {K_PARAM} = "
                  f"{z0_ada/1e6:.1f}M ADA (epoch {epoch})")
            return z0_ada, supply_ada, epoch
    except Exception as e:
        print(f"  ! Koios totals fetch failed: {e}")
    # documented fallback per diagnostic POL.O3.F3
    return 77_000_000, 38_500_000_000, 0


def main() -> None:
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    rows = load_endpoints()
    located = locate_endpoints(rows)
    pools = aggregate_per_pool(located)
    entities = aggregate_per_entity(located)
    pools_with_loc = [p for p in pools if p["lat"] not in ("", None)]
    entities_with_loc = [e for e in entities if e["lat"] not in ("", None)]
    print(f"{len(pools)} pools ({len(pools_with_loc)} with a resolvable location)")
    print(f"{len(entities)} entities ({len(entities_with_loc)} with a resolvable centroid)")
    total_active = sum(float(p.get("stake_ada") or 0) for p in pools)
    print(f"Total active stake: {total_active/1e9:.2f}B ADA")
    z0_ada, supply_ada, epoch = fetch_z0_from_koios()
    sat_point_m = z0_ada / 1e6
    annotate_with_saturation(pools_with_loc, z0_ada, total_active)
    annotate_with_saturation(entities_with_loc, z0_ada, total_active)
    print("Pool count by canonical tier (z0 = supply / k):")
    from collections import Counter as _C
    pool_tier_counts = _C(p["saturation_tier"] for p in pools_with_loc)
    for t in TIER_NAMES:
        print(f"  {t:18s}  {pool_tier_counts.get(t, 0)}")
    n_productive = sum(1 for p in pools_with_loc if p.get("productive"))
    print(f"Productive pools (≥3M ADA): {n_productive} of {len(pools_with_loc)} "
          f"({100*n_productive/len(pools_with_loc):.1f}%)")
    data = pools_with_loc + entities_with_loc
    OUT_JSON.write_text(json.dumps(data, default=str, indent=0))
    import datetime as _dt
    snapshot = _dt.date.today().strftime("%Y/%m/%d")
    h = HTML_TMPL.replace("__DATA__", json.dumps(data, default=str))
    h = h.replace("__COLORS__", json.dumps(PROVIDER_COLOR))
    h = h.replace("__TIER_COLORS__", json.dumps(TIER_COLOR))
    h = h.replace("__COHORT_COLORS__", json.dumps(COHORT_COLOR))
    h = h.replace("__SAT_COLORS__", json.dumps(SAT_TIER_COLOR))
    h = h.replace("__SAT_POINT_M__", json.dumps(round(sat_point_m, 1)))
    h = h.replace("__SUPPLY_B__", json.dumps(round(supply_ada / 1e9, 2)))
    h = h.replace("__TOTAL_STAKE_B__", json.dumps(round(total_active / 1e9, 2)))
    h = h.replace("__EPOCH__", json.dumps(epoch))
    h = h.replace("__K_PARAM__", json.dumps(K_PARAM))
    h = h.replace("__TIER_ORDER__", json.dumps(TIER_NAMES))
    h = h.replace("__PRODUCTIVE_THRESHOLD_M__", json.dumps(PRODUCTIVE_THRESHOLD_ADA / 1e6))
    h = h.replace("__SNAPSHOT__", json.dumps(snapshot))
    OUT_HTML.write_text(h)
    print(f"wrote {OUT_HTML.relative_to(ROOT)} ({OUT_HTML.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
