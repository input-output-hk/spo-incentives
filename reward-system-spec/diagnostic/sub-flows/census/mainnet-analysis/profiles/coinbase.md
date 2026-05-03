# Coinbase

> Archetype: **CEX** (Exchange Custody)
> Website: [coinbase.com](https://www.coinbase.com) — Cardano pools hidden behind bison.run / herd.run infrastructure
> Attribution confidence: Medium-High (operational cluster, not first-party metadata)

## Identity

Coinbase Global Inc. (NASDAQ: COIN). US-listed exchange and prime brokerage offering retail and institutional products: custody, execution, staking, and earn. The largest single entity on Cardano by delegated stake.

## Cardano presence

| Metric | Value |
| --- | --- |
| Pools | 41 (in hollow × competitive) |
| Stake | 2,444M ADA (19.2% of cell) |
| Delegators | 403 |
| ADA / delegator | 6.06M |
| Margin | 5.0% |
| Operator take | 6.6% |
| Custodial signal | **Yes** — operator manages the delegation addresses |

Tickers: generic/randomised (RRC, CVM, TIA, FVG, GCN, …). No Coinbase branding on-chain. Metadata and relays under bison.run and herd.run domains. Koios and BalanceAnalytics surface the cluster as COINBASE.

## Profile

Coinbase is the defining custodial entity in the delegation market. 403 delegation addresses for 2.44B ADA means an average of 6.06M ADA per address — these are internal wallets managed by Coinbase, not retail delegators choosing a pool. The capital is Coinbase's customers' ADA, staked through Coinbase's earn product. The customers do not choose the pool; Coinbase routes the delegation.

At 5.0% margin — the ceiling of the competitive band — Coinbase prices at the top of the cell. It can: it controls the routing and the customers have no friction-free exit to a competing pool. This is market power without market discipline.

Coinbase alone holds more stake than the bottom 200 entities in the cell combined.

## Historical trajectory

Broadly stable: 6.60% of supply at epoch 400, 6.38% at epoch 618. The largest single entity throughout the Shelley era. A mid-period dip around epoch 410 reversed fully.

## Pledge

2.45B ADA delegated / ~0 pledged = **∞**. Structurally pledge-zero — custodied funds cannot be pledged.

## Source

Existing profile: `sub-flows/census/mainnet-analysis/docs/mpo_entity_profiles.md` (CEX section). Coinbase.com/earn returned 403 (gated content).
