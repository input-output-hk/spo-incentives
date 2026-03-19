# General Reward Pot Proxy (Mainnet)

## Proxy definition from current inputs
- Gross reward-pot proxy: $Fee^{epoch}_{tx} + g(d)\min(\eta,1)\rho \cdot Reserve$.
- Treasury cut proxy: $\tau \cdot GrossRewardPot_{proxy}$.
- Pool-side reward-pot proxy: $(1-\tau)\cdot GrossRewardPot_{proxy}$.
- Deposit^{epoch}_{nonRefundable} is missing from current Koios inputs and therefore omitted.

## Current partial epoch
- Epoch **616** (2026-02-28):
  - fees = **36,977.68 ADA**
  - reserve term = **19,380,240.41 ADA**
  - gross reward-pot proxy = **19,417,218.09 ADA**
  - treasury cut proxy = **3,883,443.62 ADA**
  - pool-side reward-pot proxy = **15,533,774.47 ADA**

## Comparison to observed paid rewards
- The pool-side proxy is expected to sit above observed paid rewards because it is still upstream of several loss / return-to-reserve mechanisms.
- On epochs **211..616**, the median absolute gap between the pool-side proxy and observed paid rewards is **10,321,008.56 ADA**.
