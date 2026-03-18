# Epoch Pool Reward Gap Decomposition Notes

Target quantity: $Reward^{epoch}_{pools}$

- Dataset window: **208..617**
- Analysis window for quantification: **epoch >= 211**

## Core formulas
- Theoretical pool pot: $R^{epoch}_{pot}=(1-\tau)\cdot(Fee+\eta\cdot\rho\cdot Reserve\cdot g^{transition})$
- Transition gate: $g^{transition}=0$ if $d\ge 1$, else $1$
- Total gap: $Gap=R^{epoch}_{pot}-R^{epoch}_{paid}$
- Reason 1 proxy: $Gap_{unstaked}=R^{epoch}_{pot}\cdot(1-\phi^{active}_{transition})$
- with $\phi^{active}_{transition}=1$ if $d\ge 1$, else $\frac{activeStake}{supply}$
- Reasons 2-7 residual bucket: $Gap_{residual}=Gap-Gap_{unstaked}$

## Seven reasons why a gap exists
- Reason 1. Inactive / reward-ineligible stake: Byron-era funds, undelegated stake, retired pools, and other stake not participating in the reward mechanism.
- Reason 2. Pool performance losses: $\bar{p}<1$ due to missed blocks, forks, or underperformance, so actual paid rewards are below optimal rewards.
- Reason 3. Unmet pledge: if pledge is not respected, the pool reward collapses to zero for that epoch.
- Reason 4. Saturation / cap effects: $\sigma'=\min(\sigma,z_0)$ and $s'=\min(s,z_0)$ cap the reward-relevant stake and pledge terms.
- Reason 5. Byron -> Shelley transition: early epochs are affected by the decentralisation parameter $d$ and the OBFT/Praos transition.
- Reason 6. Ledger timing and rounding: reward accounting is epoch-shifted and uses integer lovelace arithmetic.
- Reason 7. Incomplete $Deposit_{nonRefund}$ measurement: if the true per-epoch non-refundable deposit flow is unavailable, the theoretical pot is only approximate.

## What is quantified here
- The current dataset supports a direct proxy only for reason 1.
- Reasons 2-7 remain grouped in one residual bucket in the graph.
- Reason 5 is partially reflected through the transition gate based on $d$.
- Reason 7 is explicitly present as a limitation because the analysis sets $Deposit_{nonRefund}=0$.

## Quantification (epoch >= 211)
- Total gap: **4527.86M ADA**
- Reason 1 proxy (inactive / non-eligible stake): **3212.38M ADA** (**70.9%** of gap)
- Reasons 2-7 residual bucket: **1315.48M ADA** (**29.1%** of gap)
- Median per-epoch gap: **10.33M ADA**

## Caveats
- $Deposit_{nonRefund}$ is set to 0 in this approximation (epoch-level direct flow unavailable here).
- If $\eta_{mainnet,capped}$ is missing in any epoch row, the script falls back to 1.0 for that row.
- Reason 1 remains a proxy, not a direct ledger-identity attribution.
- The residual bucket groups reasons 2-7 and therefore is not a full causal attribution.
