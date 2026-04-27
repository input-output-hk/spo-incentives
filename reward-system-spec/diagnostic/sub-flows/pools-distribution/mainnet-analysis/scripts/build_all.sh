#!/usr/bin/env bash
# Build all outputs for the Pools Distribution sub-report.
# Run from this directory: cd scripts && bash build_all.sh
#
# Prerequisites: Python 3.9+, matplotlib, numpy
# Input data:    ../data/*.csv  (pool list + history from Koios)
#
# Two scripts fetch live data from Koios and should be run first when
# refreshing for a new epoch (see §8.2 of README.md):
#   build_mpo_entity_deep_dive.py    — refreshes MPO entity CSVs + figure
#   build_mpo_progression_analysis.py — refreshes MPO historical figure

set -euo pipefail
cd "$(dirname "$0")"

echo "=== Pools Distribution — Build All ==="
echo ""

echo "[1/10] Computing snapshot metrics..."
python3 build_pool_distribution_snapshot.py

echo "[2/10] Computing reward formula anatomy..."
python3 build_reward_anatomy.py

echo "[3/10] Building reward anatomy visual..."
python3 build_reward_anatomy_visual.py

echo "[4/10] Building playing field visual..."
python3 build_playing_field_visual.py

echo "[5/10] Building pledge bonus activation visual..."
python3 build_pledge_bonus_activation_visual.py

echo "[6/10] Building saturation utilisation visual..."
python3 build_saturation_utilisation_visual.py

echo "[7/10] Building pool landscape by size visual..."
python3 build_pool_landscape_by_size_visual.py

echo "[8/10] Building three thresholds visual..."
python3 build_three_thresholds_visual.py

echo "[9/10] Building MPO entity deep-dive (fetches Koios live data)..."
python3 build_mpo_entity_deep_dive.py

echo "[10/10] Building MPO progression analysis..."
python3 build_mpo_progression_analysis.py

echo ""
echo "=== Done ==="
echo "Outputs:"
echo "  data/pool_distribution_snapshot.json"
echo "  data/pool_distribution_snapshot.md"
echo "  data/reward_anatomy.json"
echo "  data/reward_anatomy.md"
echo "  data/pool_envelope_detail.csv"
echo "  data/mpo_entity_summary_mainnet.csv"
echo "  data/mpo_entity_pool_mapping_mainnet.csv"
echo "  data/mpo_entity_health_overview_mainnet.csv"
echo "  data/mpo_unresolved_group_labels_mainnet.csv"
echo "  data/mpo_progression_proxy_key_epochs_mainnet.csv"
echo "  figures/reward_anatomy_mainnet.png"
echo "  figures/playing_field_mainnet.png"
echo "  figures/pledge_bonus_activation_mainnet.png"
echo "  figures/saturation_utilisation_mainnet.png"
echo "  figures/pool_landscape_by_size_mainnet.png"
echo "  figures/three_thresholds_mainnet.png"
echo "  figures/mpo_entity_current_distribution_mainnet.png"
echo "  figures/mpo_entity_progression_stacked_mainnet.png"
