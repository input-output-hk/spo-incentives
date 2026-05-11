"""TCP-liveness probe over every registered relay endpoint.

Reads the Koios snapshot, extracts every (ip, port) tuple, attempts a 3-second
TCP connect against each in parallel. Result cached so re-runs only probe
endpoints not yet seen. The output flags which registered relays actually
respond on their advertised port — the difference between "registered" and
"operational" is part of the Leios liveness picture.

NOTE — this script must be run from a host with unrestricted outbound TCP
access to arbitrary IP:port. The default Cowork sandbox blocks outbound TCP
except to a small allowlist; running this from a workstation or CI runner
without that restriction is the intended environment.

Output: data/cache/relay_liveness.json
        {ip:port: {"alive": bool, "rtt_ms": int|null, "error": str|null,
                   "ts": iso}}

Run: python3 scripts/probe_relay_liveness.py [--workers 100] [--timeout 3]
"""
from __future__ import annotations
import argparse
import ipaddress
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "cache"
KOIOS = DATA / "koios_pool_list.json"
DNS_CACHE = CACHE / "dns_forward.json"
OUT = CACHE / "relay_liveness.json"


def is_ip(v: str) -> bool:
    try:
        ipaddress.ip_address(v)
        return True
    except ValueError:
        return False


def gather_endpoints() -> list:
    """Return [(ip, port)] pairs from Koios relays. DNS targets are resolved
    against the existing forward-DNS cache so we don't re-resolve here."""
    pools = json.loads(KOIOS.read_text())
    dns_cache = json.loads(DNS_CACHE.read_text()) if DNS_CACHE.exists() else {}
    seen: set = set()
    out: list = []
    for p in pools:
        if p.get("pool_status") != "registered":
            continue
        for r in p.get("relays") or []:
            if not isinstance(r, dict):
                continue
            port = r.get("port") or 3001  # 3001 is Cardano default
            try:
                port = int(port)
            except (ValueError, TypeError):
                port = 3001
            if not (1 <= port <= 65535):
                continue
            for f in ("ipv4", "ipv6", "dns"):
                v = (r.get(f) or "")
                if not isinstance(v, str) or not v.strip():
                    continue
                v = v.strip()
                if is_ip(v):
                    ips = [v]
                else:
                    ips = dns_cache.get(v.lower(), []) or []
                for ip in ips:
                    key = (ip, port)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(key)
    return out


def probe_one(ip: str, port: int, timeout: float = 3.0) -> dict:
    t0 = time.monotonic()
    try:
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
        rtt = int((time.monotonic() - t0) * 1000)
        return {"alive": True, "rtt_ms": rtt, "error": None}
    except (socket.timeout, TimeoutError):
        return {"alive": False, "rtt_ms": None, "error": "timeout"}
    except OSError as e:
        return {"alive": False, "rtt_ms": None, "error": e.strerror or str(e)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=100)
    ap.add_argument("--timeout", type=float, default=3.0)
    ap.add_argument("--limit", type=int, default=0, help="probe at most N new endpoints (0 = all)")
    args = ap.parse_args()

    cache = json.loads(OUT.read_text()) if OUT.exists() else {}
    endpoints = gather_endpoints()
    todo = [(ip, port) for ip, port in endpoints if f"{ip}:{port}" not in cache]
    if args.limit:
        todo = todo[: args.limit]
    print(f"[probe] {len(endpoints)} total endpoints, {len(cache)} cached, {len(todo)} to probe")
    if not todo:
        return
    done = 0
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe_one, ip, port, args.timeout): (ip, port) for ip, port in todo}
        for fut in as_completed(futs):
            ip, port = futs[fut]
            res = fut.result()
            res["ts"] = ts
            cache[f"{ip}:{port}"] = res
            done += 1
            if done % 200 == 0:
                print(f"  ... {done}/{len(todo)}")
                OUT.write_text(json.dumps(cache, indent=0, sort_keys=True))
    OUT.write_text(json.dumps(cache, indent=0, sort_keys=True))
    alive = sum(1 for v in cache.values() if v.get("alive"))
    print(f"[probe] done. alive={alive}/{len(cache)} ({100*alive/len(cache):.1f}%)")


if __name__ == "__main__":
    main()
