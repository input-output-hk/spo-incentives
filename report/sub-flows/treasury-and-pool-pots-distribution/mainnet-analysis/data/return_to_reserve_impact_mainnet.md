# Return-to-Reserve Impact (Mainnet)

## Proxy definition
- Gross reward-pot proxy: $Fee + g(d)\min(\eta,1)\rho \cdot Reserve$.
- Pool-side pot proxy: $(1-\tau)\cdot GrossRewardPot_{proxy}$.
- Returned-to-reserve proxy: $\max(PoolSidePot_{proxy} - ObservedPaidRewards, 0)$.
- Deposit^{epoch}_{nonRefundable} is missing from current inputs and is omitted.

## Analysis window
- Epochs **211..616**.
- Later epochs are not included because observed paid rewards are not yet available there.

## Headline numbers
- Median per-epoch returned-to-reserve proxy: **10,321,008.56 ADA**.
- Cumulative returned-to-reserve proxy by epoch **616**: **4,547,433,498.04 ADA**.
- Largest epoch return proxy: epoch **211** (2020-08-13) = **24,192,069.25 ADA**.

## Reserve impact
- Actual reserve at epoch **616**: **6,526,859,579.65 ADA**.
- Counterfactual reserve without returned-to-reserve proxy: **1,979,426,081.61 ADA**.
- This counterfactual is a simplified accounting illustration, not a full ledger replay.
