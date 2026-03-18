# Reward^epoch_pools Near-zero Divergence Notes

## Target
- Reconstruct `epoch_info.total_rewards` with near-zero divergence using SL-D1 as base.

## Reconstruction model
- Transition gross pot: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{gross,transition}}=(1-\tau)\cdot(\mathrm{Fee}+g^{\mathrm{transition}}\rho\cdot\mathrm{Reserve})$
- Transition gate: $g^{\mathrm{transition}}=\begin{cases}0,& d\ge 1\\1,& d<1\end{cases}$ where $d$ is the decentralisation parameter
- Active-factor correction: $\phi^{\mathrm{active}}_{\mathrm{transition}}=\begin{cases}1,& d\ge 1\\\frac{\mathrm{activeStake}}{\mathrm{supply}},& d<1\end{cases}$
- Calibrated payout efficiency: $\kappa$
- Final: $\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{paid,recon}}=\mathrm{Reward}^{\mathrm{epoch}}_{\mathrm{gross,transition}}\cdot\phi^{\mathrm{active}}_{\mathrm{transition}}\cdot\kappa$
- Overlay on figure (same axis): $\mathrm{Fee}^{\mathrm{epoch}}_{\mathrm{tx}}$ in Million ADA

## Calibration
- Window: epochs **211..614** (bootstrap epochs 209-210 excluded)
- Calibrated `kappa`: **0.754418**

## Fit quality (same calibration window)
- Gross-only MAPE: **109.35%**
- Transition-base MAPE (gross + active factor): **32.22%**
- Final reconstruction MAPE: **1.49%**
- Final reconstruction MAE: **168,211 ADA/epoch**

## Full-window quality (includes bootstrap)
- Final reconstruction MAPE on epochs 209+: **1.53%**
- Final reconstruction MAE on epochs 209+: **167,797 ADA/epoch**

## Gap diagnostics (theoretical vs observed)
- Gap median (stable window): **10.91M ADA** (p5=9.19M, p95=17.32M)
- Paid share median (stable window): **47.68%** (p5=41.78%, p95=54.33%)

## Calibration diagnostic
- Implied payout efficiency percentiles: p5=**0.732**, p50=**0.759**, p95=**0.775**
- Epochs with formula inputs but missing observed target: **[615, 616]**

## Interpretation
- This is a calibrated reconstruction for analysis, not a pure forward protocol simulation.
- Remaining gap is small and mainly concentrated in early/transition epochs.

## Output figure
- `reward_epoch_pools_near_zero_mainnet.png`
