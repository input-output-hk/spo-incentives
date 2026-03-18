from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def scenario_eval_root() -> Path:
    return Path(__file__).resolve().parents[1]


def workspace_root() -> Path:
    return scenario_eval_root().parents[1]


def rewards_engine_root() -> Path:
    return workspace_root() / "Rewards-Sharing-Simulation-Engine"


def load_axes_config() -> dict[str, Any]:
    config_path = scenario_eval_root() / "config" / "cip_scenario_axes.json"
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expand_scenarios(config: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    defaults = config["defaults"]
    for fee_rule in config["fee_rules"]:
        for stake_cap_rule in config["stake_cap_rules"]:
            for k_variant in config["k_variants"]:
                assumptions = dict(defaults)
                assumptions.update(fee_rule.get("params", {}))
                assumptions.update(stake_cap_rule.get("params", {}))
                assumptions["k_target_pools"] = k_variant["k"]

                scenario = {
                    "id": f"{fee_rule['id']}__{stake_cap_rule['id']}__{k_variant['id']}",
                    "fee_rule": fee_rule["id"],
                    "stake_cap_rule": stake_cap_rule["id"],
                    "k_variant": k_variant["id"],
                    "label": (
                        f"{fee_rule['label']} + {stake_cap_rule['label']} / {k_variant['label']}"
                    ),
                    "canonical": True,
                    "descriptions": {
                        "fee_rule": fee_rule["description"],
                        "stake_cap_rule": stake_cap_rule["description"],
                        "k_variant": k_variant["description"],
                    },
                    "assumptions": assumptions,
                }
                scenario["simulator_support"] = derive_simulator_support(scenario)
                scenarios.append(scenario)
    return scenarios


def derive_simulator_support(scenario: dict[str, Any]) -> dict[str, Any]:
    fee_rule = scenario["fee_rule"]
    stake_cap_rule = scenario["stake_cap_rule"]
    assumptions = scenario["assumptions"]

    if fee_rule != "baseline":
        return {
            "status": "unsupported",
            "reason": (
                "The current rewards-sharing engine does not model the Cardano ledger fee-layer "
                "changes behind minPoolMargin/minPoolRate/minPoolCost."
            ),
        }

    if stake_cap_rule == "baseline":
        engine_args = {
            "reward_scheme": 0,
            "k": assumptions["k_target_pools"],
            "a0": assumptions["a0"],
        }
        return {"status": "supported", "reason": "Direct status-quo mapping.", "engine_args": engine_args}

    if stake_cap_rule == "cip0050":
        engine_args = {
            "reward_scheme": 4,
            "k": assumptions["k_target_pools"],
            "a0": assumptions["a0"],
            "L": assumptions["cip0050_L"],
        }
        return {
            "status": "supported",
            "reason": "Mapped to CIP50RSS in the current rewards-sharing engine.",
            "engine_args": engine_args,
        }

    if stake_cap_rule == "cip0037":
        return {
            "status": "unsupported",
            "reason": "Dynamic pledge-linked saturation is not implemented in the current rewards-sharing engine.",
        }

    return {"status": "unsupported", "reason": "Unknown simulator mapping."}


def build_engine_command(
    scenario: dict[str, Any],
    *,
    n: int = 1000,
    seed: int = 42,
    max_iterations: int = 200,
    iterations_after_convergence: int = 10,
    execution_prefix: str = "matrix",
) -> list[str]:
    support = scenario["simulator_support"]
    if support["status"] != "supported":
        raise ValueError(f"Scenario {scenario['id']} is not supported by the current rewards-sharing engine.")

    engine_args = support["engine_args"]
    command = [
        ".venv/bin/python",
        "main.py",
        f"--n={n}",
        f"--k={engine_args['k']}",
        f"--a0={engine_args['a0']}",
        f"--reward_scheme={engine_args['reward_scheme']}",
        f"--max_iterations={max_iterations}",
        f"--iterations_after_convergence={iterations_after_convergence}",
        f"--seed={seed}",
        f"--execution_id={execution_prefix}-{scenario['id']}",
        "--no-generate_graphs",
    ]
    if "L" in engine_args and engine_args["L"] is not None:
        command.append(f"--L={engine_args['L']}")
    return command


def scenario_index(scenarios: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {scenario["id"]: scenario for scenario in scenarios}
