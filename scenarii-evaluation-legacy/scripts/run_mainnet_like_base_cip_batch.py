#!/usr/bin/env python3
"""
Run the mainnet-like comparison batch for Status Quo vs the 4 base CIPs.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from mainnet_like_batch_lib import (
    BASELINE_A0,
    BASELINE_K,
    ITERATIONS_AFTER_CONVERGENCE,
    MAX_ITERATIONS,
    METRICS,
    SEED,
    engine_root,
    scenario_definitions,
    spo_incentives_root,
    write_stake_distribution_file,
)


def main() -> None:
    snapshot = write_stake_distribution_file()
    scenarios = scenario_definitions(active_stake_ada=float(snapshot["active_stake_ada"]))

    manifest = {
        "batch": "mainnet-like-base-cip-comparison",
        "engine_root": str(engine_root()),
        "stake_distribution_file": snapshot["output_path"],
        "positive_registered_pools": snapshot["pool_count"],
        "active_stake_ada": snapshot["active_stake_ada"],
        "k": BASELINE_K,
        "a0": BASELINE_A0,
        "seed": SEED,
        "max_iterations": MAX_ITERATIONS,
        "iterations_after_convergence": ITERATIONS_AFTER_CONVERGENCE,
        "metrics": METRICS,
        "scenarios": [],
    }

    python_bin = engine_root() / ".venv" / "bin" / "python"
    if not python_bin.exists():
        raise FileNotFoundError(f"Python venv not found: {python_bin}")

    for scenario in scenarios:
        cmd = [
            str(python_bin),
            "main.py",
            "--n",
            str(snapshot["pool_count"]),
            "--k",
            str(BASELINE_K),
            "--a0",
            str(BASELINE_A0),
            "--stake_distr_source",
            "file",
            "--reward_scheme",
            str(scenario.reward_scheme),
            "--max_iterations",
            str(MAX_ITERATIONS),
            "--iterations_after_convergence",
            str(ITERATIONS_AFTER_CONVERGENCE),
            "--seed",
            str(SEED),
            "--execution_id",
            scenario.scenario_id,
            "--no-generate_graphs",
            "--metrics",
            *[str(metric) for metric in METRICS],
            *scenario.extra_args,
        ]
        print(f"\n== Running {scenario.label} ==")
        print(" ".join(cmd))
        subprocess.run(cmd, cwd=engine_root(), check=True)
        manifest["scenarios"].append(
            {
                "scenario_id": scenario.scenario_id,
                "label": scenario.label,
                "reward_scheme": scenario.reward_scheme,
                "extra_args": list(scenario.extra_args),
                "notes": scenario.notes,
            }
        )

    output_path = (
        spo_incentives_root()
        / "scenarii-evaluation"
        / "outputs"
        / "mainnet_like_base_cip_batch_manifest.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest written to {output_path}")


if __name__ == "__main__":
    main()
