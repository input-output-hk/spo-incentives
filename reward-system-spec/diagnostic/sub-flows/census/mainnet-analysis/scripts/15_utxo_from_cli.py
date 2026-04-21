#!/usr/bin/env python3
"""15_utxo_from_cli.py
Fast-path UTxO decomposition using cardano-cli instead of db-sync tx_out.

Zero external dependencies — uses only Python stdlib. Bech32 decoding is
inlined; postgres queries use docker exec + psql.

Classifies each UTxO by address type (CIP-19 header byte) and delegation
status (cross-referenced against Instance A postgres), producing:
  - data/utxo_address_type_decomposition.csv   (§5.2)
  - data/non_participant_by_address_type.csv    (summary for visuals)

Usage:
  # 1. Dump UTxO to JSON (run via the shell wrapper)
  bash scripts/15_run_utxo_dump.sh

  # 2. Run classification
  python3 15_utxo_from_cli.py /tmp/utxo_whole.json

  # Or in one shot:
  python3 15_utxo_from_cli.py --dump-and-classify
"""

import csv, json, os, sys, subprocess
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, '..', 'data')

# ═══════════════════════════════════════════════════════════════
# Inline bech32 decoder (from BIP-173 / CIP-19)
# ═══════════════════════════════════════════════════════════════

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def _bech32_polymod(values):
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk

def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_decode(bech):
    """Decode a bech32/bech32m string. Returns (hrp, data_bytes) or (None, None).

    Skips checksum verification — addresses from cardano-cli are pre-validated.
    """
    bech = bech.strip().lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech):
        return None, None
    hrp = bech[:pos]
    data_part = bech[pos+1:]
    try:
        data = [BECH32_CHARSET.index(c) for c in data_part]
    except ValueError:
        return None, None

    # Convert from 5-bit groups to 8-bit bytes (drop 6-char checksum)
    five_bit = data[:-6]
    acc = 0
    bits = 0
    result = []
    for v in five_bit:
        acc = (acc << 5) | v
        bits += 5
        while bits >= 8:
            bits -= 8
            result.append((acc >> bits) & 0xff)
    return hrp, result


# ═══════════════════════════════════════════════════════════════
# Address classification (CIP-19)
# ═══════════════════════════════════════════════════════════════

def classify_address(addr_str):
    """Classify a Cardano address. Returns (addr_type, staking_cred_hex_or_None).

    addr_type: 'base', 'script_base', 'enterprise', 'script_enterprise',
               'pointer', 'bootstrap', 'reward', 'unknown'
    """
    if addr_str.startswith('addr1') or addr_str.startswith('addr_test1'):
        hrp, decoded = bech32_decode(addr_str)
        if decoded and len(decoded) > 0:
            header = decoded[0]
            top4 = (header >> 4) & 0x0F

            # Extract staking credential (28 bytes at offset 29) for base addresses
            staking_cred = None
            if top4 in (0, 1, 2, 3) and len(decoded) >= 57:
                staking_cred = bytes(decoded[29:57]).hex()

            if top4 == 0: return ('base', staking_cred)
            elif top4 == 1: return ('script_base', staking_cred)
            elif top4 == 2: return ('base', staking_cred)        # key pay, script stake
            elif top4 == 3: return ('script_base', staking_cred) # script pay, script stake
            elif top4 == 4: return ('pointer', None)
            elif top4 == 5: return ('pointer', None)
            elif top4 == 6: return ('enterprise', None)
            elif top4 == 7: return ('script_enterprise', None)
            elif top4 == 8: return ('bootstrap', None)
            elif top4 in (14, 15): return ('reward', None)
            else: return ('unknown', None)
        return ('base', None)  # conservative fallback

    elif addr_str.startswith('Ae2') or addr_str.startswith('DdzFF'):
        return ('bootstrap', None)
    elif addr_str.startswith('stake1'):
        return ('reward', None)
    else:
        return ('unknown', None)


# ═══════════════════════════════════════════════════════════════
# Delegation status from postgres (via docker exec + psql)
# ═══════════════════════════════════════════════════════════════

def get_delegated_stake_creds():
    """Query Instance A postgres for currently delegated staking credential hashes."""
    print("Querying delegated stake credentials from postgres (via docker exec)...")

    # hash_raw is 29 bytes: 1 header (0xe0/0xe1/0xf0/0xf1) + 28 credential.
    # We extract only the 28-byte credential to match against address-extracted creds.
    sql = """
    COPY (
        SELECT encode(substring(sa.hash_raw from 2), 'hex')
        FROM stake_address sa
        WHERE EXISTS (
            SELECT 1 FROM delegation d
            WHERE d.addr_id = sa.id
            AND NOT EXISTS (
                SELECT 1 FROM stake_deregistration sd
                WHERE sd.addr_id = sa.id
                AND sd.tx_id > d.tx_id
            )
        )
    ) TO STDOUT;
    """

    result = subprocess.run(
        ['docker', 'exec', 'dbsync-postgres-1',
         'psql', '-U', 'postgres', '-d', 'cexplorer',
         '-t', '-A', '-c', sql],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        print(f"WARNING: postgres query failed: {result.stderr[:200]}")
        print("  Falling back to classification without delegation status.")
        return set()

    delegated = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
    delegated.discard('')  # remove empty strings
    print(f"  Found {len(delegated):,} delegated stake credentials")
    return delegated


# ═══════════════════════════════════════════════════════════════
# UTxO dump via cardano-cli (inside Docker)
# ═══════════════════════════════════════════════════════════════

def dump_utxo(output_path='/tmp/utxo_whole.json'):
    """Dump the full UTxO set using cardano-cli inside the node container."""
    container = 'dbsync-cardano-node-1'
    socket = '/ipc/node.socket'
    container_path = '/data/utxo_whole.json'

    # Check socket exists
    check = subprocess.run(
        ['docker', 'exec', container, 'test', '-S', socket],
        capture_output=True
    )
    if check.returncode != 0:
        print("ERROR: Node socket not found. Node is still validating.")
        sys.exit(1)

    print(f"Dumping UTxO set (this takes 5-15 minutes on mainnet)...")
    result = subprocess.run(
        ['docker', 'exec', '-e', f'CARDANO_NODE_SOCKET_PATH={socket}',
         container, 'cardano-cli', 'query', 'utxo',
         '--whole-utxo', '--mainnet', '--out-file', container_path],
        capture_output=True, text=True, timeout=1200  # 20 min timeout
    )
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[:500]}")
        sys.exit(1)

    # Copy out
    print(f"Copying to {output_path}...")
    subprocess.run(['docker', 'cp', f'{container}:{container_path}', output_path],
                   check=True)
    subprocess.run(['docker', 'exec', container, 'rm', '-f', container_path])

    size_gb = os.path.getsize(output_path) / 1e9
    print(f"  Done. File size: {size_gb:.1f} GB")
    return output_path


# ═══════════════════════════════════════════════════════════════
# Classification engine
# ═══════════════════════════════════════════════════════════════

def classify_utxo(json_path, delegated_creds):
    """Stream-parse the UTxO JSON and classify each output."""
    print(f"Loading UTxOs from {json_path}...")
    with open(json_path) as f:
        utxo = json.load(f)

    total = len(utxo)
    print(f"  {total:,} UTxOs to classify")

    totals = defaultdict(lambda: {'utxo_count': 0, 'total_lovelace': 0})
    processed = 0

    for txref, entry in utxo.items():
        addr = entry.get('address', '')
        value = entry.get('value', {})
        if isinstance(value, dict):
            lovelace = int(value.get('lovelace', 0))
        elif isinstance(value, (int, str)):
            lovelace = int(value)
        else:
            lovelace = 0

        addr_type, staking_cred = classify_address(addr)

        # Map to 6-category classification
        if addr_type == 'bootstrap':
            classification = 'enterprise'  # Byron can't delegate
        elif addr_type == 'script_enterprise':
            classification = 'script_no_staking_cred'
        elif addr_type == 'enterprise':
            classification = 'enterprise'
        elif addr_type in ('base', 'script_base'):
            is_script = addr_type == 'script_base'
            is_delegated = staking_cred in delegated_creds if staking_cred else False
            if is_script:
                classification = 'script_delegated' if is_delegated else 'script_not_delegated'
            else:
                classification = 'base_delegated' if is_delegated else 'base_not_delegated'
        elif addr_type == 'pointer':
            classification = 'base_not_delegated'
        else:
            classification = 'enterprise'

        totals[classification]['utxo_count'] += 1
        totals[classification]['total_lovelace'] += lovelace

        processed += 1
        if processed % 2_000_000 == 0:
            print(f"  Processed {processed:,}/{total:,} ({100*processed/total:.1f}%)")

    return dict(totals)


# ═══════════════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════════════

def save_results(totals):
    """Save classification results to CSV files."""
    os.makedirs(DATA, exist_ok=True)

    # (A) Full decomposition
    out_a = os.path.join(DATA, 'utxo_address_type_decomposition.csv')
    rows = sorted(totals.items(), key=lambda x: -x[1]['total_lovelace'])
    with open(out_a, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['classification', 'utxo_count', 'total_lovelace'])
        for cls, vals in rows:
            w.writerow([cls, vals['utxo_count'], vals['total_lovelace']])
    print(f"\nSaved {out_a}")

    # Print summary
    total_ada = sum(v['total_lovelace'] for v in totals.values()) / 1e6
    total_utxo = sum(v['utxo_count'] for v in totals.values())
    print(f"\n{'Classification':<28} {'UTxOs':>12} {'ADA':>16} {'Share':>8}")
    print('-' * 68)
    for cls, vals in rows:
        ada = vals['total_lovelace'] / 1e6
        share = 100 * ada / total_ada if total_ada > 0 else 0
        print(f"{cls:<28} {vals['utxo_count']:>12,} {ada:>14,.0f} {share:>7.1f}%")
    print('-' * 68)
    print(f"{'TOTAL':<28} {total_utxo:>12,} {total_ada:>14,.0f} {'100.0':>7}%")

    # (B) Summary
    staked = totals.get('base_delegated', {}).get('total_lovelace', 0) + \
             totals.get('script_delegated', {}).get('total_lovelace', 0)
    can_stake = totals.get('base_not_delegated', {}).get('total_lovelace', 0) + \
                totals.get('script_not_delegated', {}).get('total_lovelace', 0)
    cannot_stake = totals.get('enterprise', {}).get('total_lovelace', 0) + \
                   totals.get('script_no_staking_cred', {}).get('total_lovelace', 0)
    total_utxo_ada = staked + can_stake + cannot_stake

    out_b = os.path.join(DATA, 'non_participant_by_address_type.csv')
    with open(out_b, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['category', 'total_lovelace', 'total_ada'])
        w.writerow(['staked', staked, staked / 1e6])
        w.writerow(['can_stake_not_delegated', can_stake, can_stake / 1e6])
        w.writerow(['cannot_stake', cannot_stake, cannot_stake / 1e6])
    print(f"Saved {out_b}")

    print(f"\nSummary:")
    print(f"  Staked:                 {staked/1e6:>14,.0f} ADA"
          f" ({100*staked/total_utxo_ada:.1f}%)" if total_utxo_ada else "")
    print(f"  Can stake, not doing:   {can_stake/1e6:>14,.0f} ADA"
          f" ({100*can_stake/total_utxo_ada:.1f}%)" if total_utxo_ada else "")
    print(f"  Cannot stake (struct.): {cannot_stake/1e6:>14,.0f} ADA"
          f" ({100*cannot_stake/total_utxo_ada:.1f}%)" if total_utxo_ada else "")


def main():
    if '--dump-and-classify' in sys.argv:
        json_path = dump_utxo()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        json_path = sys.argv[1]
    else:
        print("Usage:")
        print("  python3 15_utxo_from_cli.py /tmp/utxo_whole.json")
        print("  python3 15_utxo_from_cli.py --dump-and-classify")
        sys.exit(1)

    if not os.path.exists(json_path):
        print(f"ERROR: {json_path} not found")
        sys.exit(1)

    delegated_creds = get_delegated_stake_creds()
    totals = classify_utxo(json_path, delegated_creds)
    save_results(totals)


if __name__ == '__main__':
    main()
