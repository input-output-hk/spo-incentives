#!/usr/bin/env bash
# Build all outputs for the Treasury & Pool Pots Distribution sub-report.
# Run from this directory: cd scripts && bash build_all.sh
#
# Prerequisites: Python 3.9+, matplotlib, numpy
# Input data:    ../data/reward_epoch_pools_mainnet.csv  (Koios epoch-level export)

set -euo pipefail
cd "$(dirname "$0")"

echo "=== Treasury & Pool Pots Distribution — Build All ==="
echo ""

echo "[1/7] Building epoch pot composition visual..."
python3 build_general_reward_pot_visual.py

echo "[2/7] Building reserve stock & monetary expansion visual..."
python3 build_monetary_expansion_reserve_history.py

echo "[3/7] Building transaction fee history visual..."
python3 build_fee_epoch_tx_history_visual.py

echo "[4/7] Building treasury inflow decomposition visual..."
python3 build_treasury_epoch_source_visual.py

echo "[5/7] Building deposit obligation history visual..."
python3 build_deposit_obligation_history_visual.py

echo "[6/7] Building return-to-reserve impact visual..."
python3 build_return_to_reserve_impact_visual.py

echo "[7/7] Building block-production ratio (η) visual..."
python3 build_eta_history_visual.py

echo ""
echo "=== Done ==="
echo "Outputs:"
echo "  data/general_reward_pot_mainnet.md"
echo "  data/monetary_expansion_reserve_history_mainnet.md"
echo "  data/monetary_expansion_reserve_history_mainnet.csv"
echo "  data/fee_epoch_tx_history_mainnet.md"
echo "  data/treasury_epoch_source_mainnet.md"
echo "  data/deposit_obligation_history_mainnet.md"
echo "  data/return_to_reserve_impact_mainnet.md"
echo "  data/eta_history_mainnet.md"
echo "  figures/general_reward_pot_mainnet.png"
echo "  figures/monetary_expansion_reserve_history_mainnet.png"
echo "  figures/fee_epoch_tx_history_mainnet.png"
echo "  figures/treasury_epoch_source_mainnet.png"
echo "  figures/deposit_obligation_history_mainnet.png"
echo "  figures/return_to_reserve_impact_mainnet.png"
echo "  figures/eta_history_mainnet.png"
