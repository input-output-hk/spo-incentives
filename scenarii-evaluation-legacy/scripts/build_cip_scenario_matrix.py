from __future__ import annotations

import json
import shlex
from pathlib import Path

from scenario_matrix_lib import (
    build_engine_command,
    expand_scenarios,
    load_axes_config,
    rewards_engine_root,
    scenario_eval_root,
)


def render_markdown(config: dict, scenarios: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# CIP Scenario Matrix")
    lines.append("")
    lines.append("Canonical first-pass scenario matrix for SPO incentive evaluation.")
    lines.append("")
    lines.append("Scope:")
    lines.append(f"- Baseline `K`: `{config['metadata']['baseline_k']}`")
    lines.append(f"- High `K`: `{config['metadata']['high_k']}`")
    lines.append(f"- Baseline `a0`: `{config['metadata']['baseline_a0']}`")
    lines.append(f"- Note: {config['metadata']['scope_note']}")
    lines.append("")
    lines.append("## Canonical matrix")
    lines.append("")
    lines.append("| Scenario ID | Fee rule | Stake-cap rule | K | Support in current reward engine | Notes |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for scenario in scenarios:
        support = scenario["simulator_support"]
        note = support["reason"].replace("|", "/")
        lines.append(
            "| {id} | {fee} | {stake} | {k} | {status} | {note} |".format(
                id=scenario["id"],
                fee=scenario["fee_rule"],
                stake=scenario["stake_cap_rule"],
                k=scenario["assumptions"]["k_target_pools"],
                status=support["status"],
                note=note,
            )
        )

    lines.append("")
    lines.append("## Governance bundles")
    lines.append("")
    lines.append("| Bundle | Preferred scenario(s) | Stress-test scenario(s) | Notes |")
    lines.append("| --- | --- | --- | --- |")
    for bundle in config["governance_bundles"]:
        preferred = ", ".join(f"`{item}`" for item in bundle["preferred"])
        stress = ", ".join(f"`{item}`" for item in bundle["stress_test"])
        lines.append(f"| {bundle['label']} | {preferred} | {stress} | {bundle['notes']} |")

    supported = [scenario for scenario in scenarios if scenario["simulator_support"]["status"] == "supported"]
    lines.append("")
    lines.append("## Supported reward-engine commands")
    lines.append("")
    lines.append(
        f"Target engine path: `{rewards_engine_root()}`"
    )
    lines.append("")
    for scenario in supported:
        command = shlex.join(build_engine_command(scenario))
        lines.append(f"### `{scenario['id']}`")
        lines.append("")
        lines.append("```bash")
        lines.append(f"cd {rewards_engine_root()}")
        lines.append(command)
        lines.append("```")
        lines.append("")

    unsupported = [scenario for scenario in scenarios if scenario["simulator_support"]["status"] != "supported"]
    lines.append("## Unsupported scenarios")
    lines.append("")
    for scenario in unsupported:
        lines.append(f"- `{scenario['id']}`: {scenario['simulator_support']['reason']}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(config: dict, scenarios: list[dict]) -> None:
    outputs_dir = scenario_eval_root() / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    matrix_path = outputs_dir / "cip_scenario_matrix.json"
    matrix_path.write_text(
        json.dumps({"metadata": config["metadata"], "scenarios": scenarios}, indent=2) + "\n",
        encoding="utf-8",
    )

    markdown_path = outputs_dir / "cip_scenario_matrix.md"
    markdown_path.write_text(render_markdown(config, scenarios) + "\n", encoding="utf-8")

    shell_path = outputs_dir / "run_supported_rewards_engine_scenarios.sh"
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", "", f"cd {shlex.quote(str(rewards_engine_root()))}"]
    for scenario in scenarios:
        if scenario["simulator_support"]["status"] != "supported":
            continue
        lines.append("")
        lines.append(f"# {scenario['id']}")
        lines.append(shlex.join(build_engine_command(scenario)))
    shell_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    shell_path.chmod(0o755)


def main() -> None:
    config = load_axes_config()
    scenarios = expand_scenarios(config)
    write_outputs(config, scenarios)


if __name__ == "__main__":
    main()
