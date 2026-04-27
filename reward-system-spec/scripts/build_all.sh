#!/usr/bin/env bash
# Regenerate all conceptual diagrams for the V2 Specification README.
#
# Run from anywhere:  bash spo-incentives/reward-system-spec/scripts/build_all.sh
# Or from scripts/:   bash build_all.sh
#
# Outputs land in ../figures/ relative to this script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "→ regenerating V2 Specification figures"
python3 build_foundations_overview.py
python3 build_macro_dashboard_loop.py
echo "✓ done — see ../figures/"
