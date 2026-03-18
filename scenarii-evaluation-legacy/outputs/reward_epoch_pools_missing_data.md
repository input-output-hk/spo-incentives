# Reward^epoch_pools Missing Data Audit (Mainnet)

- Source: Koios API (`https://api.koios.rest/api/v1`)
- Tip epoch at fetch time: **618**
- Target range: epochs **208..618**

## Coverage
- Genesis constants: active slot coeff **0.05**, epoch length **432000** slots
- Derived expected blocks/epoch: **21600**
- `epoch_info` rows in range: **411**
- `totals` rows in range: **410**
- `epoch_params` rows in range: **411**

## Missing fields for direct `Reward^epoch_pools` line
- Epochs with missing `total_rewards` in `epoch_info`: **[208, 617, 618]**
- Epochs with missing `totals` row: **[208]**
- Epochs with missing `epoch_params` row: **[]**

## Practically plottable contiguous window
- Fully populated epochs (all three sources): **209..616**

## Notes
- If the objective is only plotting `Reward^epoch_pools`, `epoch_info.total_rewards` is sufficient.
- If the objective is decomposition (fees / reserves / treasury / parameter overlays), all three sources are needed.
