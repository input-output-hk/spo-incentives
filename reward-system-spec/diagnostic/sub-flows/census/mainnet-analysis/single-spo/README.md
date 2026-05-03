# Single-Pool Operators — The Independent Operator Segment

This sub-document of [*The Staking Census*](../README.md) zooms into the **single-pool operator segment** — the population that remains once attributed multi-pool entities are extracted from the productive pool set. The mechanism's intended growth path runs through this population: small operators who enter, build reputation, attract delegation, and eventually graduate into established entities. *This document audits whether the segment shows any of that designed trajectory, and quantifies what is actually there.*

After extracting the **83 attributed multi-pool entities** (449 productive pools, **76.7% of productive stake**), **284 unattributed single-pool operators** remain in the productive set. They hold **5.28B ADA — 24.5% of productive stake**, and their share is in slow structural decline (from **28.0%** at epoch 583).

**The competitive field is three times smaller than the headline suggests.** The *Incentive Mechanism Analysis*'s headline of **741 "healthy pools"** collapses to **284 productive single-pool operators** once MPO fleet members are removed. The remaining **561 are marginal operators** who partially pledge and sit at the decision boundary — *the narrow policy-sensitive population that any parameter reform must target*.

**Pledge is rationally ignored at this scale.** **80.6%** of single-pool productive stake is zero-pledge (pledge ratio < 2%). At single-pool scale, the pledge bonus is economically *negligible* — the rational operator deploys capital elsewhere. The mechanism's intended pledge-as-commitment signal therefore reaches almost none of the segment it was designed to grow.

**By tier (after MPO removal):**

| Tier | Pools | Stake | Characteristic |
| --- | --- | --- | --- |
| Oversaturated | 0 | — | No independent pool reaches saturation |
| Healthy (viable+) | 283 | ~4.3B ADA | Regular block production, economically viable |
| Marginal | 561 | ~0.9B ADA | The policy-sensitive population — partially pledge, sit at decision boundary |
| Below viability | ~1,253 | ~0.2B ADA | Economic loss zone; fixed cost exceeds reward |

## Data

Single-pool-operator data is currently produced by scripts in
`sub-flows/pools-distribution/mainnet-analysis/` as a by-product of the
landscape analysis (§4.3):

| File | Location | Description |
| --- | --- | --- |
| `filtered_landscape_spo_only_summary.csv` | `sub-flows/pools-distribution/mainnet-analysis/data/` | Tier × pledge-stance summary for single-pool operators |
| `koios_pool_list_mainnet.csv` | `sub-flows/pools-distribution/mainnet-analysis/data/` | Full pool list — filter by excluding pools in `entities/data/mpo_entity_pool_mapping_mainnet.csv` to obtain the single-pool-operator set |

## Figures

| Figure | Location | Description |
| --- | --- | --- |
| `filtered_landscape_spo_only_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Current single-pool-operator tier distribution by pledge stance |
| `spo_only_history_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Historical single-pool-operator composition (epochs 250–618) |
| `mpo_extraction_by_tier_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Tier-by-tier effect of MPO removal |

## Scripts

| Script | Location | What it does |
| --- | --- | --- |
| `build_filtered_landscape_visual.py` | `sub-flows/pools-distribution/mainnet-analysis/scripts/` | Produces the single-pool-operator butterfly chart and history evolution; writes `filtered_landscape_spo_only_summary.csv` |
| `build_mpo_extraction_visual.py` | `sub-flows/pools-distribution/mainnet-analysis/scripts/` | Shows what the pool landscape looks like before and after MPO extraction |

## Deriving the single-pool-operator pool list

There is no dedicated single-pool-operator listing file. The single-pool
operator set is **defined by exclusion**: any pool in
`koios_pool_list_mainnet.csv` that does **not** appear in
`entities/data/mpo_entity_pool_mapping_mainnet.csv` is a single-pool operator.

This keeps the definition consistent and avoids duplication.

```python
import csv

mpo_pools = set()
with open("entities/data/mpo_entity_pool_mapping_mainnet.csv") as f:
    for r in csv.DictReader(f):
        mpo_pools.add(r["pool_id_bech32"])

spo_pools = []
with open("sub-flows/pools-distribution/mainnet-analysis/data/koios_pool_list_mainnet.csv") as f:
    for r in csv.DictReader(f):
        if r["pool_id_bech32"] not in mpo_pools:
            spo_pools.append(r)

print(f"Single-pool operators: {len(spo_pools)}")
```

## Relationship to the MPO entities

The MPO entity analysis and the single-pool-operator segment are **two sides of the same coin**.
Together they partition the full pool landscape.

The split is operationally clean: MPO pools are **attributed** (matched to
named entities by the attribution engine), and the remainder is the
**independent base**.

The key analytical contrast: MPO entities operate in a **multi-game environment**
where the pledge signal is one sub-game among many. Single-pool operators face
the mechanism **directly** — but **78% still do not pledge**, because the
bonus is too small at their scale to matter.

*The 51 marginal operators who partially pledge constitute the narrow
population where parameter reform could actually shift behaviour.*

## Next steps

As the entity workstream matures, this directory can host:

- A generated `spo_pool_list_mainnet.csv` with tier/stance classification per
  pool, extracted by a dedicated script.
- Individual single-pool-operator profiles for operators of analytical interest (e.g. the
  marginal-to-compliant boundary population).
- Comparative analysis: single-pool-operator vs MPO yield, fee structure, pledge behaviour.

> **Status** — Sub-document of [The Staking Census](../README.md). Snapshot epoch: 618. Last updated 2026/04/08.
