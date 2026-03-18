# Reward^epoch_pools Formula Reconstruction Notes

- Input data: `reward_epoch_pools_mainnet.csv`
- Epoch span in dataset: **208..616**
- Overlap (observed + formula): **209..614**
- Epochs with formula value but missing observed reward: **[615, 616]**

## Formula used
- $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{pools}} = (1-\tau)\cdot(\mathrm{Fee} + \mathrm{Deposit} + \min(\eta,1)\rho\cdot(T_{\infty}-T))$

## Assumptions
- `eta = 1.0`
- `Deposit = 0.0` because an epoch-level non-refundable deposit flow is not present in current inputs
- `T∞ = 45,000,000,000 ADA` and `T` is taken from `totals.supply`

## Fit quality on overlap window
- MAE: **11,853,174 ADA/epoch**
- MAPE: **2583.11%**
- Stable window (epoch >= 211): MAE **11,754,047 ADA/epoch**, MAPE **109.35%**
- Observed/Gross ratio median: **0.477** (p5=0.401, p95=0.543)

## Interpretation
- The formula line is the **gross reward pot** from SL-D1 (pre pool-level performance and pre return-to-reserves).
- The observed line is on-chain **paid rewards** (`epoch_info.total_rewards`).
- These are not strictly the same quantity, so a persistent gap is expected.

## Output figure
- `reward_epoch_pools_formula_mainnet.png`
