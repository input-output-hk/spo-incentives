from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from scenario_matrix_lib import (
    build_engine_command,
    expand_scenarios,
    load_axes_config,
    rewards_engine_root,
    scenario_index,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run supported SPO incentive scenarios in Rewards-Sharing-Simulation-Engine.")
    parser.add_argument("--list", action="store_true", help="List all canonical scenarios and exit.")
    parser.add_argument("--supported-only", action="store_true", help="Only show supported scenarios when used with --list.")
    parser.add_argument("--scenario-id", type=str, help="Run one scenario by its canonical ID.")
    parser.add_argument("--all-supported", action="store_true", help="Run all currently supported scenarios.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument("--n", type=int, default=1000, help="Number of agents for reward-engine runs.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for reward-engine runs.")
    parser.add_argument("--max-iterations", type=int, default=200, help="Maximum iterations for reward-engine runs.")
    parser.add_argument(
        "--iterations-after-convergence",
        type=int,
        default=10,
        help="Consecutive idle iterations required for convergence.",
    )
    parser.add_argument(
        "--execution-prefix",
        type=str,
        default="matrix",
        help="Execution ID prefix passed to the reward engine.",
    )
    parser.add_argument(
        "--engine-root",
        type=Path,
        default=rewards_engine_root(),
        help="Path to the Rewards-Sharing-Simulation-Engine checkout.",
    )
    return parser.parse_args()


def print_scenarios(scenarios: list[dict], supported_only: bool) -> None:
    for scenario in scenarios:
        support = scenario["simulator_support"]
        if supported_only and support["status"] != "supported":
            continue
        print(
            "{id}: fee={fee} stake_cap={stake} k={k} support={support}".format(
                id=scenario["id"],
                fee=scenario["fee_rule"],
                stake=scenario["stake_cap_rule"],
                k=scenario["assumptions"]["k_target_pools"],
                support=support["status"],
            )
        )
        print(f"  {support['reason']}")


def run_command(command: list[str], engine_root: Path, dry_run: bool) -> int:
    printable = shlex.join(command)
    print(f"cd {engine_root}")
    print(printable)
    if dry_run:
        return 0
    result = subprocess.run(command, cwd=engine_root, check=False)
    return result.returncode


def main() -> int:
    args = parse_args()
    scenarios = expand_scenarios(load_axes_config())
    scenarios_by_id = scenario_index(scenarios)

    if args.list:
        print_scenarios(scenarios, args.supported_only)
        return 0

    targets: list[dict] = []
    if args.scenario_id:
        scenario = scenarios_by_id.get(args.scenario_id)
        if scenario is None:
            print(f"Unknown scenario ID: {args.scenario_id}", file=sys.stderr)
            return 2
        targets = [scenario]
    elif args.all_supported:
        targets = [scenario for scenario in scenarios if scenario["simulator_support"]["status"] == "supported"]
    else:
        print("Specify --list, --scenario-id, or --all-supported.", file=sys.stderr)
        return 2

    engine_root = args.engine_root
    if not engine_root.exists():
        print(f"Rewards engine checkout not found: {engine_root}", file=sys.stderr)
        return 2

    for scenario in targets:
        support = scenario["simulator_support"]
        if support["status"] != "supported":
            print(
                f"Scenario {scenario['id']} is not supported by the current rewards-sharing engine: {support['reason']}",
                file=sys.stderr,
            )
            return 2

        command = build_engine_command(
            scenario,
            n=args.n,
            seed=args.seed,
            max_iterations=args.max_iterations,
            iterations_after_convergence=args.iterations_after_convergence,
            execution_prefix=args.execution_prefix,
        )
        exit_code = run_command(command, engine_root, args.dry_run)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
