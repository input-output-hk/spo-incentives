# Monetary Expansion Reserve History (Mainnet)

This output separates three different quantities that are often conflated:

- Reserve stock: $Reserve = T_{\infty} - T$.
- Nominal reserve draw: $\rho \cdot Reserve$.
- Pool-side reserve contribution: $(1-\tau)\,g(d)\,\min(\eta,1)\rho \cdot Reserve$.

- Dataset coverage: epochs **208..618**.
- Complete-history window used for stock comparisons: **209..617**.
- `rho` is constant at **0.003** in this dataset.
- `tau` is constant at **0.2** in this dataset.

## Reserve stock
- First complete reserve point: epoch **209** (2020-08-03) = **13,286,160,713 ADA**.
- Last complete reserve point: epoch **617** (2026-03-05) = **6,516,240,756 ADA**.
- Change over the complete window: **-6,769,919,957 ADA** (-50.95%).

## Reserve-sourced monetary expansion
- Nominal `rho * reserve` fell from **39,858,482 ADA/epoch** to **19,548,722 ADA/epoch** over the complete window.
- Pool-side reserve term fell from **0 ADA/epoch** at epoch **209** to **15,183,565 ADA/epoch** at epoch **617**.

## Extremes on complete epochs for the pool-side reserve term
- Lowest complete epoch: **209** (2020-08-03) = **0 ADA/epoch**.
- Highest complete epoch: **215** (2020-09-02) = **31,670,060 ADA/epoch**.

## Current partial epoch
- Epoch **618** (2026-03-10) currently shows:
  - reserve stock = **6,505,611,847 ADA**
  - nominal `rho * reserve` = **19,516,836 ADA/epoch**
  - pool-side reserve term so far = **7,982,386 ADA/epoch**

The focused table is available in the CSV output next to this note.
