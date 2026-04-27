#!/usr/bin/env python3
"""
Discovers hidden MPO entities by clustering non-mapped pools.

Clustering logic:
1. Primary signal: shared pool_group field
2. Secondary signal: shared reward_addr (merges into pool_group clusters)
3. Filter: clusters with >= 2 pools AND total stake >= 30M ADA

For each discovered entity:
- Classifies as independent_mpo (community multi-pool operators)
- Sets incentive_alignment = "full"
- Sets exclude_from_baseline = "false"
- Confidence = "Medium"
- claim_type = "Pool group / reward address clustering"

Appends rows to both mapping and archetype CSVs.
"""

import pandas as pd
import csv
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse


def sanitize_entity_id(text):
    """Convert pool_group to valid entity_id: uppercase, replace spaces/dots with _."""
    if not text or pd.isna(text):
        return ""
    text = str(text).strip().upper()
    # Replace spaces, dots, hyphens with underscores
    text = re.sub(r'[\s\.\-]+', '_', text)
    # Remove any other non-alphanumeric characters except underscore
    text = re.sub(r'[^A-Z0-9_]', '', text)
    return text


def extract_meta_domain(url):
    """Extract domain from meta_url."""
    if not url or pd.isna(url):
        return ""
    try:
        parsed = urlparse(str(url))
        domain = parsed.netloc or parsed.path
        # Clean up: remove 'www.' prefix if present
        domain = domain.replace('www.', '')
        return domain if domain else ""
    except:
        return ""


def truncate_relays(relays, max_length=100):
    """Truncate relay hints to max_length."""
    if not relays or pd.isna(relays):
        return ""
    text = str(relays).strip()
    if len(text) > max_length:
        return text[:max_length]
    return text


def load_existing_mappings(csv_path):
    """Load existing pool mappings; return set of already-mapped pool IDs."""
    try:
        df = pd.read_csv(csv_path)
        return set(df['pool_id_bech32'].unique())
    except FileNotFoundError:
        return set()


def load_pool_list(csv_path):
    """Load koios pool list, filter for pools with stake > 0."""
    df = pd.read_csv(csv_path)
    # Filter for registered pools with active stake > 0
    df = df[df['pool_status'] == 'registered']
    df = df[df['active_stake'] > 0]
    return df


def cluster_pools_by_group(pools_df, mapped_pool_ids):
    """
    Cluster unmapped pools by pool_group.

    Returns dict: {pool_group -> list of pool records}
    """
    # Filter out already-mapped pools
    unmapped = pools_df[~pools_df['pool_id_bech32'].isin(mapped_pool_ids)].copy()

    # Only consider pools with non-empty pool_group
    unmapped = unmapped[unmapped['pool_group'].notna() & (unmapped['pool_group'] != '')]

    clusters = {}
    for _, row in unmapped.iterrows():
        group = str(row['pool_group']).strip()
        if group:
            if group not in clusters:
                clusters[group] = []
            clusters[group].append(row)

    return clusters


def merge_by_reward_address(clusters):
    """
    For clusters with only 1 pool, try to merge with other clusters
    sharing the same reward_addr.

    Returns refined dict.
    """
    # Build reward_addr -> clusters mapping
    addr_to_clusters = {}
    single_pool_clusters = {}

    for group_name, pools in clusters.items():
        if len(pools) == 1:
            single_pool_clusters[group_name] = pools
        if pools:  # Only process non-empty clusters
            # Get reward addresses from pools in cluster
            addrs = set()
            for pool in pools:
                addr = str(pool.get('reward_addr', '')).strip()
                if addr and addr != '':
                    addrs.add(addr)

            for addr in addrs:
                if addr not in addr_to_clusters:
                    addr_to_clusters[addr] = []
                addr_to_clusters[addr].append(group_name)

    # Merge single-pool clusters that share reward_addr with other clusters
    merged_clusters = clusters.copy()
    merged_into = {}

    for group_name, pools in single_pool_clusters.items():
        addr = str(pools[0].get('reward_addr', '')).strip()
        if addr and addr in addr_to_clusters and len(addr_to_clusters[addr]) > 1:
            # This single-pool cluster shares reward_addr with others
            # Find the first non-single-pool cluster or largest cluster with this addr
            target = None
            for other_group in addr_to_clusters[addr]:
                if other_group != group_name and len(clusters[other_group]) > 1:
                    target = other_group
                    break

            if target:
                # Merge this pool into target
                merged_clusters[target].extend(pools)
                del merged_clusters[group_name]
                merged_into[group_name] = target

    return merged_clusters


def filter_by_size(clusters):
    """Filter clusters: keep only >= 2 pools AND total stake >= 30M ADA."""
    filtered = {}

    for group_name, pools in clusters.items():
        if len(pools) < 2:
            continue

        # Sum active_stake (in lovelace), convert to ADA
        total_stake_lovelace = sum(
            float(pool.get('active_stake', 0)) for pool in pools
        )
        total_stake_ada = total_stake_lovelace / 1e6

        if total_stake_ada >= 30_000_000:  # 30M ADA
            filtered[group_name] = pools

    return filtered


def get_display_name(pools, pool_group):
    """
    Generate display_name: prefer dominant ticker, fallback to pool_group.
    """
    tickers = []
    for pool in pools:
        ticker = str(pool.get('ticker', '')).strip()
        if ticker and ticker != '':
            tickers.append(ticker)

    if tickers:
        # Most common ticker
        from collections import Counter
        ticker_counts = Counter(tickers)
        dominant = ticker_counts.most_common(1)[0][0]
        return dominant

    return pool_group


def build_new_mapping_rows(discovered_clusters, pools_df):
    """
    Build new rows for mpo_entity_pool_mapping_mainnet.csv.

    Returns list of dicts matching columns:
    entity_id, display_name, category, confidence, claim_type, pool_id_bech32, ticker,
    pool_status, current_active_stake_ada, meta_domain, meta_url, pool_group,
    adastat_group, balanceanalytics_group, reward_addr, relay_hints
    """
    new_rows = []

    for pool_group, pools in discovered_clusters.items():
        entity_id = sanitize_entity_id(pool_group)
        if not entity_id:
            entity_id = f"CLUSTER_{len(new_rows)}"

        display_name = get_display_name(pools, pool_group)

        for pool in pools:
            active_stake_lovelace = float(pool.get('active_stake', 0))
            active_stake_ada = active_stake_lovelace / 1e6

            meta_url = str(pool.get('meta_url', '')).strip() if pool.get('meta_url') else ""
            meta_domain = extract_meta_domain(meta_url)

            relays = pool.get('relays', '')
            relay_hints = truncate_relays(relays, 100)

            row = {
                'entity_id': entity_id,
                'display_name': display_name,
                'category': 'discovered_mpo',
                'confidence': 'Medium',
                'claim_type': 'Pool group / reward address clustering',
                'pool_id_bech32': str(pool.get('pool_id_bech32', '')),
                'ticker': str(pool.get('ticker', '')).strip() if pool.get('ticker') else '',
                'pool_status': str(pool.get('pool_status', '')),
                'current_active_stake_ada': f"{active_stake_ada:.6f}",
                'meta_domain': meta_domain,
                'meta_url': meta_url,
                'pool_group': str(pool.get('pool_group', '')).strip() if pool.get('pool_group') else '',
                'adastat_group': '',
                'balanceanalytics_group': '',
                'reward_addr': str(pool.get('reward_addr', '')).strip() if pool.get('reward_addr') else '',
                'relay_hints': relay_hints,
            }
            new_rows.append(row)

    return new_rows


def build_new_archetype_rows(discovered_clusters):
    """
    Build new rows for mpo_entity_archetypes.csv.

    Returns list of dicts matching columns:
    entity_id, display_name, archetype, archetype_label, delegation_source,
    incentive_alignment, exclude_from_baseline, confidence, reasoning
    """
    new_rows = []

    for pool_group, pools in discovered_clusters.items():
        entity_id = sanitize_entity_id(pool_group)
        if not entity_id:
            entity_id = f"CLUSTER_{len(new_rows)}"

        display_name = get_display_name(pools, pool_group)

        # Total stake
        total_stake_lovelace = sum(
            float(pool.get('active_stake', 0)) for pool in pools
        )
        total_stake_ada = total_stake_lovelace / 1e6

        reasoning = (
            f"Automated discovery via pool group and reward address clustering. "
            f"{len(pools)} pools identified, total stake {total_stake_ada:,.0f} ADA. "
            f"Community multi-pool operator pattern detected."
        )

        row = {
            'entity_id': entity_id,
            'display_name': display_name,
            'archetype': 'independent_mpo',
            'archetype_label': 'Independent Multi-Pool Operator',
            'delegation_source': 'Community delegators',
            'incentive_alignment': 'full',
            'exclude_from_baseline': 'false',
            'confidence': 'Medium',
            'reasoning': reasoning,
        }
        new_rows.append(row)

    return new_rows


def append_to_csv(csv_path, new_rows, expected_columns):
    """
    Append new_rows (list of dicts) to CSV, preserving column order.
    Creates file if missing.
    """
    existing_rows = []
    if Path(csv_path).exists():
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_rows = list(reader)
        except Exception as e:
            print(f"Warning: Could not read {csv_path}: {e}")

    # Combine and write
    all_rows = existing_rows + new_rows

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=expected_columns)
        writer.writeheader()
        writer.writerows(all_rows)


def main():
    base_path = Path(__file__).parent.parent
    pool_list_path = base_path / 'data' / 'koios_pool_list_mainnet.csv'
    entity_data_path = base_path.parent.parent.parent / 'entities' / 'data'
    mapping_path = entity_data_path / 'mpo_entity_pool_mapping_mainnet.csv'
    archetype_path = entity_data_path / 'mpo_entity_archetypes.csv'

    print("=" * 80)
    print("Hidden MPO Discovery")
    print("=" * 80)

    # Load existing mappings
    print("\n[1] Loading existing mappings...")
    mapped_pool_ids = load_existing_mappings(mapping_path)
    print(f"    Found {len(mapped_pool_ids)} already-mapped pools")

    # Load pool list
    print("\n[2] Loading pool list...")
    pools_df = load_pool_list(pool_list_path)
    print(f"    Loaded {len(pools_df)} registered pools with active stake > 0")

    # Cluster by pool_group
    print("\n[3] Clustering by pool_group...")
    pool_group_clusters = cluster_pools_by_group(pools_df, mapped_pool_ids)
    total_pool_group_clusters = len(pool_group_clusters)
    total_pools_in_groups = sum(len(p) for p in pool_group_clusters.values())
    print(f"    Found {total_pool_group_clusters} pool groups with {total_pools_in_groups} unmapped pools")

    # Merge by reward_addr (secondary signal)
    print("\n[4] Merging clusters by shared reward_addr...")
    merged_clusters = merge_by_reward_address(pool_group_clusters)
    print(f"    After reward_addr merge: {len(merged_clusters)} clusters")

    # Filter by size threshold
    print("\n[5] Filtering by size (>= 2 pools AND >= 30M ADA)...")
    discovered = filter_by_size(merged_clusters)
    print(f"    Discovered {len(discovered)} qualifying clusters")

    if len(discovered) == 0:
        print("\n    No new MPO entities to add.")
        return

    # Summary of discovered clusters
    print("\n[6] Discovered clusters:")
    for group_name, pools in discovered.items():
        total_stake_lovelace = sum(
            float(pool.get('active_stake', 0)) for pool in pools
        )
        total_stake_ada = total_stake_lovelace / 1e6
        entity_id = sanitize_entity_id(group_name)
        print(f"    {entity_id:<30} {len(pools):3d} pools, {total_stake_ada:>15,.0f} ADA")

    # Build new rows
    print("\n[7] Building new mapping rows...")
    new_mapping_rows = build_new_mapping_rows(discovered, pools_df)
    print(f"    Generated {len(new_mapping_rows)} new pool mappings")

    print("\n[8] Building new archetype rows...")
    new_archetype_rows = build_new_archetype_rows(discovered)
    print(f"    Generated {len(new_archetype_rows)} new archetypes")

    # Append to CSVs
    print("\n[9] Appending to CSVs...")
    mapping_columns = [
        'entity_id', 'display_name', 'category', 'confidence', 'claim_type',
        'pool_id_bech32', 'ticker', 'pool_status', 'current_active_stake_ada',
        'meta_domain', 'meta_url', 'pool_group', 'adastat_group',
        'balanceanalytics_group', 'reward_addr', 'relay_hints'
    ]
    append_to_csv(mapping_path, new_mapping_rows, mapping_columns)
    print(f"    Updated {mapping_path}")

    archetype_columns = [
        'entity_id', 'display_name', 'archetype', 'archetype_label',
        'delegation_source', 'incentive_alignment', 'exclude_from_baseline',
        'confidence', 'reasoning'
    ]
    append_to_csv(archetype_path, new_archetype_rows, archetype_columns)
    print(f"    Updated {archetype_path}")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Added {len(discovered)} new MPO entities with {len(new_mapping_rows)} total pools")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)


if __name__ == '__main__':
    main()
