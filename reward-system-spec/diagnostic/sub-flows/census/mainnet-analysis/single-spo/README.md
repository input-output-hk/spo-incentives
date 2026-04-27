# Single-Pool Operators

> The independent operator segment — what remains after MPO extraction.
>
> Last updated: 2026/04/08. Snapshot epoch: 618.

## The segment at a glance

After extracting the **85 MPO entities** (901 pools, **75.4% of stake**),
**2,097 single-pool operators** remain.

They hold **5.44B ADA** — **25.0% of active stake** — and their share is
declining (from **28.0% at epoch 583**).

The headline figure of **741 "healthy pools"** from the *Incentive Mechanism
Analysis* collapses to **283 viable independents** once fleet members are
removed.

*The competitive field is three times smaller than the headline suggests.*

**By tier (after MPO removal):**

| Tier | Pools | Stake | Characteristic |
| --- | --- | --- | --- |
| Oversaturated | 0 | — | No independent pool reaches saturation |
| Healthy (viable+) | 283 | ~4.3B ADA | Regular block production, economically viable |
| Marginal | 561 | ~0.9B ADA | The policy-sensitive population — partially pledge, sit at decision boundary |
| Below viability | ~1,253 | ~0.2B ADA | Economic loss zone; fixed cost exceeds reward |

**By pledge compliance:**

**78% of independent stake is non-compliant** (pledge ratio < 2%). This is
rational: at single-pool scale, the pledge bonus is economically
**negligible**.

The **561 marginal operators** who partially pledge are the narrowest and
highest-return target for any incentive reform.

## Data

SPO-specific data is currently produced by scripts in
`sub-flows/pools-distribution/mainnet-analysis/` as a by-product of the
landscape analysis (§4.3):

| File | Location | Description |
| --- | --- | --- |
| `filtered_landscape_spo_only_summary.csv` | `sub-flows/pools-distribution/mainnet-analysis/data/` | Tier × pledge-stance summary for single-pool operators |
| `koios_pool_list_mainnet.csv` | `sub-flows/pools-distribution/mainnet-analysis/data/` | Full pool list — filter by excluding pools in `entities/data/mpo_entity_pool_mapping_mainnet.csv` to obtain the SPO set |

## Figures

| Figure | Location | Description |
| --- | --- | --- |
| `filtered_landscape_spo_only_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Current SPO tier distribution by pledge stance |
| `spo_only_history_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Historical SPO composition (epochs 250–618) |
| `mpo_extraction_by_tier_mainnet.png` | `sub-flows/pools-distribution/mainnet-analysis/figures/` | Tier-by-tier effect of MPO removal |

## Scripts

| Script | Location | What it does |
| --- | --- | --- |
| `build_filtered_landscape_visual.py` | `sub-flows/pools-distribution/mainnet-analysis/scripts/` | Produces the SPO-only butterfly chart and history evolution; writes `filtered_landscape_spo_only_summary.csv` |
| `build_mpo_extraction_visual.py` | `sub-flows/pools-distribution/mainnet-analysis/scripts/` | Shows what the pool landscape looks like before and after MPO extraction |

## Deriving the SPO pool list

There is no dedicated SPO listing file. The single-pool operator set is
**defined by exclusion**: any pool in `koios_pool_list_mainnet.csv` that does
**not** appear in `entities/data/mpo_entity_pool_mapping_mainnet.csv` is a
single-pool operator.

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

The MPO entity analysis and the single-SPO segment are **two sides of the same coin**.
Together they partition the full pool landscape.

The split is operationally clean: MPO pools are **attributed** (matched to
named entities by the attribution engine), and the remainder is the
**independent base**.

The key analytical contrast: MPO entities operate in a **multi-game environment**
where the pledge signal is one sub-game among many. Single-pool operators face
the mechanism **directly** — but **78% still do not pledge**, because the
bonus is too small at their scale to matter.

*The 561 marginal operators who partially pledge constitute the narrow
population where parameter reform could actually shift behaviour.*

## Next steps

As the entity workstream matures, this directory can host:

- A generated `spo_pool_list_mainnet.csv` with tier/stance classification per
  pool, extracted by a dedicated script.
- Individual SPO profiles for operators of analytical interest (e.g. the
  marginal-to-compliant boundary population).
- Comparative analysis: SPO vs MPO yield, fee structure, pledge behaviour.
