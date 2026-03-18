# Scenarii Evaluation

Workspace for CIP scenario comparisons (CIP-0023, CIP-0037, CIP-0050, CIP-0082, Status Quo).

## Structure
- data/: input datasets
- config/: canonical scenario axes and assumptions
- notebooks/: exploration notebooks
- scripts/: reproducible analysis scripts
- figures/: generated charts
- outputs/: tables and result exports
- docs/: assumptions and notes

## Scenario matrix
- `config/cip_scenario_axes.json`: canonical fee-rule x stake-cap-rule x `K` scenario axes.
- `scripts/build_cip_scenario_matrix.py`: expands the canonical matrix and writes machine-readable plus Markdown outputs.
- `scripts/run_rewards_engine_scenarios.py`: executes the subset already supported by `Rewards-Sharing-Simulation-Engine`.

## Formula comparison
- `scripts/build_cip_formula_comparison.py`: deterministic formula-layer comparison of `CIP-0023`, `CIP-0037`, `CIP-0050`, `CIP-0082` vs status quo.
- `docs/cip-formula-comparison.md`: generated comparison document with table of contents.
