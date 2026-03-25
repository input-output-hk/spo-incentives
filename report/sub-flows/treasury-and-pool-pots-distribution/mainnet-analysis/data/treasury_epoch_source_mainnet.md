# Treasury Per-Epoch Source Decomposition (Mainnet)

## What is directly decomposed from current inputs
- Treasury from fees: $\tau \cdot Fee^{epoch}_{tx}$.
- Treasury from monetary expansion: $\tau g(d)\min(\eta,1)\rho \cdot Reserve$.
- Treasury from deposits: not directly available because `Deposit^{epoch}_{nonRefundable}` is not present as an epoch flow in the current Koios dataset.

## Current partial epoch
- Epoch **616** (2026-02-28):
  - fee-side treasury cut = **7,395.54 ADA**
  - reserve-side treasury cut = **3,876,048.08 ADA**
  - total treasury inflow proxy = **3,883,443.62 ADA**

## Verification against treasury stock data
- Observed stock data used for the check: `Treasury_ada` from the timeseries.
- Verification compares the source-based inflow proxy to the net stock delta between epochs.
- They do not match exactly when treasury outflows happen and when the deposit flow is missing from inputs.
- Window used: epochs **211..616**.
- Median absolute gap between proxy inflow and treasury stock delta: **48,791.98 ADA**.
- Epochs within **100k ADA** of the stock delta: **325/406**.
- Epochs with negative treasury stock delta in that window: **13**.
