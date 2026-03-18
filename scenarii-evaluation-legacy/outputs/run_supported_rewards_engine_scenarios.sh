#!/usr/bin/env bash
set -euo pipefail

cd /Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine

# baseline__baseline__k500
.venv/bin/python main.py --n=1000 --k=500 --a0=0.3 --reward_scheme=0 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__baseline__k500 --no-generate_graphs

# baseline__baseline__k1000
.venv/bin/python main.py --n=1000 --k=1000 --a0=0.3 --reward_scheme=0 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__baseline__k1000 --no-generate_graphs

# baseline__cip0050__k500
.venv/bin/python main.py --n=1000 --k=500 --a0=0.3 --reward_scheme=4 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__cip0050__k500 --no-generate_graphs --L=100

# baseline__cip0050__k1000
.venv/bin/python main.py --n=1000 --k=1000 --a0=0.3 --reward_scheme=4 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__cip0050__k1000 --no-generate_graphs --L=100
