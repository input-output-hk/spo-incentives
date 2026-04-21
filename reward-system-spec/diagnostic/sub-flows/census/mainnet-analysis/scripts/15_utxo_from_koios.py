#!/usr/bin/env python3
"""15_utxo_from_koios.py
Stake-account census and non-participant decomposition via Koios + Instance A postgres.

Since cardano-cli `--whole-utxo` hits a TxIx >16-bit CBOR deserialization bug
(node 10.6.2, confirmed in CLI 10.15/10.16 and ogmios 6.12.0), this script
derives the address-type decomposition from two complementary sources:

  1. Instance A postgres (pruned db-sync): epoch_stake, delegation, stake_address
     tables give the staked split (key vs script) and the list of registered-but-
     not-delegated stake addresses.

  2. Koios public API: supply totals at epoch 623 plus per-account balances for
     the ~24K registered-not-delegated accounts.

The residual (circulation minus all stake-account-controlled ADA) gives the
structurally-excluded portion: enterprise addresses + script addresses without
staking credentials + base addresses whose staking key was never registered.

Produces:
  data/non_participant_decomposition_623.csv   — 5-category decomposition
  data/stake_account_census_623.csv            — per-category account counts

Usage:
  python3 15_utxo_from_koios.py            (runs from sandbox via Koios + docker)
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

EPOCH = 623
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")
KOIOS = "https://api.koios.rest/api/v1"


# ── Koios helpers ───────────────────────────────────────────────
def koios_get(endpoint: str, params: str = "", retries: int = 3):
    url = f"{KOIOS}/{endpoint}{params}"
    for attempt in range(retries):
        try:
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            elif attempt == retries - 1:
                raise
            else:
                time.sleep(1)


def koios_post(endpoint: str, payload: dict, retries: int = 3):
    url = f"{KOIOS}/{endpoint}"
    body = json.dumps(payload).encode()
    for attempt in range(retries):
        try:
            req = Request(url, data=body, headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            })
            with urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  Rate-limited, waiting {wait}s ...")
                time.sleep(wait)
            elif attempt == retries - 1:
                raise
            else:
                time.sleep(1)


# ── Postgres helper (Instance A via docker) ─────────────────────
def pg(sql: str, timeout: int = 300) -> str:
    r = subprocess.run(
        ["docker", "exec", "dbsync-postgres-1",
         "psql", "-U", "postgres", "-d", "cexplorer", "-t", "-A", "-c", sql],
        capture_output=True, text=True, timeout=timeout,
    )
    if r.returncode != 0:
        raise RuntimeError(f"postgres: {r.stderr[:300]}")
    return r.stdout.strip()


# ═════════════════════════════════════════════════════════════════
# 1. Supply totals from Koios at target epoch
# ═════════════════════════════════════════════════════════════════
def get_supply(epoch: int = EPOCH) -> dict:
    print(f"[1/4] Fetching supply totals from Koios (epoch {epoch}) ...")
    rows = koios_get("totals", f"?_epoch_no={epoch}")
    if not rows:
        sys.exit("ERROR: no totals from Koios")
    t = rows[0]
    d = {k: int(t[k]) for k in (
        "circulation", "treasury", "reward", "supply", "reserves",
        "deposits_stake", "deposits_drep", "deposits_proposal",
    )}
    d["deposits_total"] = d["deposits_stake"] + d["deposits_drep"] + d["deposits_proposal"]
    # UTxO ADA = circulation minus reward accounts minus deposits
    d["utxo_total"] = d["circulation"] - d["reward"] - d["deposits_total"]

    print(f"  supply:       {d['supply']/1e12:.4f}T lovelace  ({d['supply']/1e12:.3f}B ADA)")
    print(f"  circulation:  {d['circulation']/1e12:.4f}T lovelace  ({d['circulation']/1e12:.3f}B ADA)")
    print(f"  treasury:     {d['treasury']/1e12:.4f}T lovelace")
    print(f"  reward accts: {d['reward']/1e12:.4f}T lovelace")
    print(f"  deposits:     {d['deposits_total']/1e6:,.0f} ADA")
    print(f"  UTxO total:   {d['utxo_total']/1e12:.4f}T lovelace  ({d['utxo_total']/1e12:.3f}B ADA)")
    return d


# ═════════════════════════════════════════════════════════════════
# 2. Staked split from Instance A epoch_stake
# ═════════════════════════════════════════════════════════════════
def get_staked_split(epoch: int = EPOCH) -> dict:
    print(f"\n[2/4] Querying epoch_stake from Instance A (epoch {epoch}) ...")

    key_sql = f"""
    SELECT COUNT(*), COALESCE(SUM(es.amount),0)
    FROM epoch_stake es
    JOIN stake_address sa ON sa.id = es.addr_id
    WHERE es.epoch_no = {epoch}
      AND get_byte(sa.hash_raw, 0) IN (224, 225);
    """
    script_sql = f"""
    SELECT COUNT(*), COALESCE(SUM(es.amount),0)
    FROM epoch_stake es
    JOIN stake_address sa ON sa.id = es.addr_id
    WHERE es.epoch_no = {epoch}
      AND get_byte(sa.hash_raw, 0) IN (240, 241);
    """

    kc, ka = pg(key_sql).split("|")
    sc, sa_ = pg(script_sql).split("|")

    result = {
        "delegated_key_count": int(kc),
        "delegated_key_lovelace": int(ka),
        "delegated_script_count": int(sc),
        "delegated_script_lovelace": int(sa_),
    }
    result["delegated_total"] = result["delegated_key_lovelace"] + result["delegated_script_lovelace"]

    print(f"  Key-based:    {result['delegated_key_count']:>10,} accounts  "
          f"{result['delegated_key_lovelace']/1e6/1e9:.3f}B ADA")
    print(f"  Script-based: {result['delegated_script_count']:>10,} accounts  "
          f"{result['delegated_script_lovelace']/1e6/1e9:.3f}B ADA")
    print(f"  TOTAL staked: {result['delegated_total']/1e6/1e9:.3f}B ADA")
    return result


# ═════════════════════════════════════════════════════════════════
# 3. Registered-not-delegated: list from Instance A, balances from Koios
# ═════════════════════════════════════════════════════════════════
def get_registered_not_delegated() -> dict:
    print("\n[3/4] Registered-not-delegated accounts ...")

    # Get bech32 addresses + credential type from Instance A
    sql = """
    SELECT sa.view,
           CASE WHEN get_byte(sa.hash_raw, 0) IN (224,225) THEN 'key' ELSE 'script' END
    FROM stake_address sa
    WHERE EXISTS (
        SELECT 1 FROM stake_registration sr WHERE sr.addr_id = sa.id
        AND NOT EXISTS (SELECT 1 FROM stake_deregistration sd WHERE sd.addr_id = sa.id AND sd.tx_id > sr.tx_id)
    )
    AND NOT EXISTS (
        SELECT 1 FROM delegation d WHERE d.addr_id = sa.id
        AND NOT EXISTS (SELECT 1 FROM stake_deregistration sd WHERE sd.addr_id = sa.id AND sd.tx_id > d.tx_id)
    );
    """
    raw = pg(sql)
    if not raw:
        print("  No registered-not-delegated accounts found")
        return {"key_count": 0, "key_lovelace": 0, "script_count": 0, "script_lovelace": 0, "total_lovelace": 0}

    accounts = []
    for line in raw.split("\n"):
        if "|" in line:
            addr, ctype = line.split("|", 1)
            accounts.append((addr.strip(), ctype.strip()))

    key_addrs = [a for a, c in accounts if c == "key"]
    script_addrs = [a for a, c in accounts if c == "script"]
    print(f"  Found {len(key_addrs):,} key + {len(script_addrs):,} script = {len(accounts):,} total")

    # Query Koios for balances in batches
    print("  Querying Koios for balances ...")
    all_addrs = [a for a, _ in accounts]
    balances = {}  # addr -> total_balance (lovelace)
    batch_size = 100
    for i in range(0, len(all_addrs), batch_size):
        batch = all_addrs[i : i + batch_size]
        if i > 0 and i % 1000 == 0:
            print(f"    ... {i:,}/{len(all_addrs):,}")
        try:
            rows = koios_post("account_info", {"_stake_addresses": batch})
            for row in rows:
                bal = int(row.get("total_balance", "0"))
                balances[row["stake_address"]] = bal
        except Exception as e:
            print(f"    WARNING: batch {i}-{i+batch_size} failed: {e}")
        # Rate limiting: ~5 req/s
        time.sleep(0.25)

    key_bal = sum(balances.get(a, 0) for a in key_addrs)
    script_bal = sum(balances.get(a, 0) for a in script_addrs)

    result = {
        "key_count": len(key_addrs),
        "key_lovelace": key_bal,
        "script_count": len(script_addrs),
        "script_lovelace": script_bal,
        "total_lovelace": key_bal + script_bal,
    }
    print(f"  Key not-delegated:    {result['key_count']:>8,} accounts  "
          f"{key_bal/1e6:>14,.0f} ADA")
    print(f"  Script not-delegated: {result['script_count']:>8,} accounts  "
          f"{script_bal/1e6:>14,.0f} ADA")
    return result


# ═════════════════════════════════════════════════════════════════
# 4. Compute final decomposition
# ═════════════════════════════════════════════════════════════════
def compute_and_save(supply: dict, staked: dict, not_del: dict):
    print("\n[4/4] Computing decomposition ...")

    circulation = supply["circulation"]
    delegated_key = staked["delegated_key_lovelace"]
    delegated_script = staked["delegated_script_lovelace"]
    reg_not_del_key = not_del["key_lovelace"]
    reg_not_del_script = not_del["script_lovelace"]

    # ADA controlled by ANY stake address = staked + registered-not-delegated
    stake_controlled = (delegated_key + delegated_script
                        + reg_not_del_key + reg_not_del_script)

    # Residual: ADA NOT controlled by any stake address
    # = enterprise (type 6) + script-without-staking (type 7)
    #   + base addresses whose staking key was never registered
    # circulation includes UTxOs + reward accounts + deposits
    # But stake-controlled already includes reward balances (from Koios total_balance)
    # and epoch_stake includes the UTxO+reward portion for delegated accounts.
    #
    # More precisely:
    #   circulation = sum_over_all_utxos(value) + sum_over_reward_accounts(balance) + deposits
    #   stake_controlled ≈ delegated (from epoch_stake snapshot) + not_del (from Koios current)
    #
    # epoch_stake is the snapshot at epoch boundary: it includes the total controlled
    # stake (UTxOs + rewards) for each delegated account at that point.
    # For not-delegated accounts, Koios total_balance = utxo + rewards_available.
    #
    # The residual includes:
    #   - Enterprise address UTxOs (no staking credential)
    #   - Script addresses without staking credential (Plutus type 7)
    #   - Base address UTxOs whose staking credential is unregistered
    #   - Deposit balances (stake key, DRep, governance deposits)
    #
    # We subtract deposits separately since they're a known category.
    deposits = supply["deposits_total"]
    no_stake_addr = circulation - stake_controlled - deposits

    categories = [
        ("delegated_key", staked["delegated_key_count"],
         delegated_key, "Standard stakers (key-based delegation)"),
        ("delegated_script", staked["delegated_script_count"],
         delegated_script, "Smart-contract staking (script-based delegation)"),
        ("registered_not_delegated_key", not_del["key_count"],
         reg_not_del_key, "Registered key credential, no delegation"),
        ("registered_not_delegated_script", not_del["script_count"],
         reg_not_del_script, "Registered script credential, no delegation"),
        ("no_stake_credential", None,
         no_stake_addr, "Enterprise + unregistered base + script-no-cred"),
        ("deposits", None,
         deposits, "Stake-key, DRep, and governance proposal deposits"),
    ]

    # ── Print table ──
    print()
    print(f"{'Category':<40} {'Accounts':>10} {'ADA':>16} {'Share':>7}")
    print("─" * 77)
    for cat, cnt, lv, desc in categories:
        ada = lv / 1e6
        pct = 100 * lv / circulation
        cnt_s = f"{cnt:,}" if cnt is not None else "—"
        print(f"{cat:<40} {cnt_s:>10} {ada:>14,.0f} {pct:>6.2f}%")
    print("─" * 77)
    print(f"{'CIRCULATION':<40} {'':>10} {circulation/1e6:>14,.0f} {'100.00':>6}%")

    # ── Derived census metrics ──
    addressable = reg_not_del_key + reg_not_del_script
    structurally_excluded = no_stake_addr  # upper bound (includes unregistered base)

    print(f"\n  Addressable non-participants:    {addressable/1e6:>14,.0f} ADA  "
          f"({100*addressable/circulation:.2f}%)")
    print(f"  Structurally excluded (upper):   {structurally_excluded/1e6:>14,.0f} ADA  "
          f"({100*structurally_excluded/circulation:.2f}%)")
    print(f"  Note: 'structurally excluded' is an upper bound — it includes base")
    print(f"        addresses with unregistered staking keys (addressable in principle).")
    print(f"        Separating enterprise from unregistered-base requires a full UTxO dump.")

    # ── Save CSV ──
    os.makedirs(DATA, exist_ok=True)

    out1 = os.path.join(DATA, "non_participant_decomposition_623.csv")
    with open(out1, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "account_count", "total_lovelace", "total_ada", "pct_of_circulation", "description"])
        for cat, cnt, lv, desc in categories:
            w.writerow([cat, cnt or "", lv, f"{lv/1e6:.0f}", f"{100*lv/circulation:.4f}", desc])
    print(f"\n  Saved {out1}")

    out2 = os.path.join(DATA, "stake_account_census_623.csv")
    with open(out2, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "credential_type", "account_count", "total_lovelace", "total_ada"])
        w.writerow(["delegated", "key", staked["delegated_key_count"],
                     delegated_key, f"{delegated_key/1e6:.0f}"])
        w.writerow(["delegated", "script", staked["delegated_script_count"],
                     delegated_script, f"{delegated_script/1e6:.0f}"])
        w.writerow(["registered_not_delegated", "key", not_del["key_count"],
                     reg_not_del_key, f"{reg_not_del_key/1e6:.0f}"])
        w.writerow(["registered_not_delegated", "script", not_del["script_count"],
                     reg_not_del_script, f"{reg_not_del_script/1e6:.0f}"])
    print(f"  Saved {out2}")

    return categories


def main():
    supply = get_supply(EPOCH)
    staked = get_staked_split(EPOCH)
    not_del = get_registered_not_delegated()
    compute_and_save(supply, staked, not_del)


if __name__ == "__main__":
    main()
