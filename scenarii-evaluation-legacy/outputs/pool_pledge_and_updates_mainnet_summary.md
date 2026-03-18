# Pool Pledge and Updates Summary (Mainnet)

- Reward-history epochs covered: **210..615**
- Pools with reward history: **6,056**
- Raw `pool_owner_history` rows: **1,360,003**
- Raw `pool_updates` rows: **39,982**

## Pledge compliance proxy
- Median epoch pledge-met share: **80.8%** of pools with observed owner history.
- Latest epoch pledge-met share: **74.5%**.
- Max epoch reward share from pledge-unmet pools: **5.98%**.
- Latest epoch reward share from pledge-unmet pools: **4.75%**.
- Full-window realized rewards linked to pledge-unmet pool-epochs: **182.11M ADA** (4.03% of realized pool rewards).

## Fee/update regime
- Median of epoch-median active margin: **2.00%**.
- Latest median active margin: **2.00%**.
- Latest share of pools at 340 ADA fixed cost: **66.5%**.
- Total pool updates observed: **36,480**.

## Pool distribution
- Pools with perfect observed compliance: **3,099**.
- Pools below 90% observed compliance: **1,469**.
- Pools with no owner-history observations in the reward window: **160**.

## Reading caveat
- This is a same-epoch operational proxy built from Koios `pool_history`, `pool_owner_history`, and `pool_updates` labels.
- It is useful for incentive analysis and anomaly hunting, but it is not a direct proof that a ledger reward should or should not have been zeroed.

## Latest epoch snapshot
- Epoch: **615**
- Pools with observed owner history: **2714**
- Pools below declared pledge: **692**
- Median pledge coverage ratio: **1.060x**
