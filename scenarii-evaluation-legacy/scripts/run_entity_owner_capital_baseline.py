#!/usr/bin/env python3
"""
Build and run a status-quo simulation on a mainnet-derived input that:
- groups operator-side capital by attributed entity when available
- fills the rest of active stake with synthetic delegator cohorts
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

from entity_owner_capital_input_lib import DELEGATOR_COHORT_SIZE_ADA, write_input_files
from mainnet_like_batch_lib import (
    BASELINE_A0,
    BASELINE_K,
    ITERATIONS_AFTER_CONVERGENCE,
    MAX_ITERATIONS,
    METRICS,
    SEED,
    engine_root,
    latest_output_dir_for_execution_id,
    load_final_descriptors,
    load_metrics_rows,
    spo_incentives_root,
)

EXECUTION_ID = "mainnet-entity-owner-capital-status-quo"
RUN_DELEGATOR_COHORT_SIZE_ADA = 30_000_000.0


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(row[column] for column in columns) + " |" for row in rows]
    return "\n".join([header, separator] + body)


def outputs_dir() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "outputs"


def docs_dir() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "docs"


def data_dir() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "data"


def run_simulation(snapshot: dict[str, object]) -> Path:
    python_bin = engine_root() / ".venv" / "bin" / "python"
    if not python_bin.exists():
        raise FileNotFoundError(f"Python venv not found: {python_bin}")

    cmd = [
        str(python_bin),
        "main.py",
        "--n",
        str(snapshot["agent_count"]),
        "--k",
        str(BASELINE_K),
        "--a0",
        str(BASELINE_A0),
        "--stake_distr_source",
        "file",
        "--reward_scheme",
        "0",
        "--max_iterations",
        str(MAX_ITERATIONS),
        "--iterations_after_convergence",
        str(ITERATIONS_AFTER_CONVERGENCE),
        "--seed",
        str(SEED),
        "--execution_id",
        EXECUTION_ID,
        "--no-generate_graphs",
        "--metrics",
        *[str(metric) for metric in METRICS],
    ]

    print("\n== Running status quo on entity-owner-capital input ==")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=engine_root(), check=True)

    output_dir = latest_output_dir_for_execution_id(EXECUTION_ID)
    if output_dir is None:
        raise FileNotFoundError(f"No output folder found for {EXECUTION_ID}")
    return output_dir


def build_result_row(output_dir: Path) -> dict[str, str]:
    descriptors = load_final_descriptors(output_dir)
    metrics = load_metrics_rows(output_dir)
    final_metrics = metrics[-1]
    return {
        "Scenario": "Status Quo",
        "Pools": str(descriptors["Pool count"]),
        "Operators": str(descriptors["Operator count"]),
        "Nakamoto": str(descriptors["Nakamoto coefficient"]),
        "Pledge fraction": str(descriptors["Total pledge fraction"]),
        "Rounds": final_metrics["Round"],
        "Step 1 pools": metrics[1]["Pool count"] if len(metrics) > 1 else "n/a",
        "Max pools/op": final_metrics["Max pools per operator"],
        "Mean margin": f"{float(final_metrics['Mean margin']):.4f}",
        "Median margin": f"{float(final_metrics['Median margin']):.4f}",
        "Output folder": output_dir.name,
    }


def write_csv(row: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def build_doc(snapshot: dict[str, object], result_row: dict[str, str]) -> str:
    toc = "\n".join(
        [
            "- [Scope](#scope)",
            "- [Input Construction](#input-construction)",
            "- [Run Parameters](#run-parameters)",
            "- [Result](#result)",
            "- [Read](#read)",
            "- [Artifacts](#artifacts)",
            "- [Limits](#limits)",
        ]
    )

    return "\n".join(
        [
            "# Mainnet Entity-Owner-Capital Status Quo",
            "",
            "## Table of Contents",
            toc,
            "",
            "## Scope",
            "",
            "This run tries to correct the main weakness of the earlier mainnet-like batch:",
            "large pool active stake was being treated as if it were operator-controlled capital.",
            "",
            "## Input Construction",
            "",
            "The engine input is rebuilt in two layers:",
            "- operator layer: current positive pools are grouped by attributed MPO entity where available, otherwise by repeated reward address when it clearly repeats, otherwise left standalone",
            "- capital basis: each operator group gets `min(current active stake, max(observed owner stake, declared pledge))`",
            f"- delegator layer: the remaining active stake is split into synthetic delegator cohorts of `{float(snapshot['delegator_cohort_size_ada']):,.0f}` ADA each",
            "",
            markdown_table(
                [
                    {
                        "Positive pools": str(snapshot["positive_registered_pools"]),
                        "Mapped entity pools": str(snapshot["mapped_entity_pools"]),
                        "Entity groups": str(snapshot["entity_group_count"]),
                        "Reward-grouped pools": str(snapshot["reward_grouped_pools"]),
                        "Operator groups": str(snapshot["operator_group_count"]),
                        "Pools with owner snapshot": str(snapshot["owner_snapshot_pool_count"]),
                        "Delegator cohorts": str(snapshot["delegator_cohort_count"]),
                        "Agent count": str(snapshot["agent_count"]),
                    }
                ],
                [
                    "Positive pools",
                    "Mapped entity pools",
                    "Entity groups",
                    "Reward-grouped pools",
                    "Operator groups",
                    "Pools with owner snapshot",
                    "Delegator cohorts",
                    "Agent count",
                ],
            ),
            "",
            markdown_table(
                [
                    {
                        "Active stake (ADA)": f"{float(snapshot['active_stake_ada']):,.3f}",
                        "Operator capital (ADA)": f"{float(snapshot['operator_capital_ada']):,.3f}",
                        "Public delegation (ADA)": f"{float(snapshot['public_delegation_ada']):,.3f}",
                        "Operator share": f"{float(snapshot['operator_capital_ada']) / float(snapshot['active_stake_ada']):.2%}",
                    }
                ],
                [
                    "Active stake (ADA)",
                    "Operator capital (ADA)",
                    "Public delegation (ADA)",
                    "Operator share",
                ],
            ),
            "",
            "## Run Parameters",
            "",
            f"- `k = {BASELINE_K}`",
            f"- `a0 = {BASELINE_A0}`",
            f"- `seed = {SEED}`",
            f"- `max_iterations = {MAX_ITERATIONS}`",
            f"- `iterations_after_convergence = {ITERATIONS_AFTER_CONVERGENCE}`",
            f"- metrics tracked: `{METRICS}`",
            "",
            "## Result",
            "",
            markdown_table(
                [result_row],
                [
                    "Scenario",
                    "Pools",
                    "Operators",
                    "Nakamoto",
                    "Rounds",
                    "Step 1 pools",
                    "Max pools/op",
                    "Mean margin",
                    "Median margin",
                    "Pledge fraction",
                ],
            ),
            "",
            "## Read",
            "",
            "This run is still an approximation, but it is a better one for the operator-count question:",
            "- operator-side stake is no longer seeded from full pool active stake",
            "- large multi-pool clusters no longer start with all delegated stake as if it were their own",
            "- the residual active stake remains in the system as delegator cohorts instead of disappearing",
            "",
            "## Artifacts",
            "",
            f"- stake distribution: `{snapshot['output_path']}`",
            f"- operator groups CSV: `{snapshot['operator_csv_path']}`",
            f"- input summary JSON: `{outputs_dir() / 'mainnet_entity_owner_capital_input_summary.json'}`",
            f"- engine output: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/{result_row['Output folder']}`",
            "",
            "## Limits",
            "",
            "- MPO attribution still depends on local clustering, not a canonical on-chain entity id.",
            "- Delegator cohorts are synthetic tranches, not real wallet-level delegates.",
            "- The engine still lets any agent become an operator if economics justify it.",
        ]
    )


def main() -> None:
    snapshot = write_input_files(cohort_size_ada=RUN_DELEGATOR_COHORT_SIZE_ADA)
    output_dir = run_simulation(snapshot)
    result_row = build_result_row(output_dir)

    manifest = {
        "batch": EXECUTION_ID,
        "input_summary": snapshot,
        "result": result_row,
    }

    manifest_path = outputs_dir() / "mainnet_entity_owner_capital_status_quo_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    csv_path = data_dir() / "mainnet_entity_owner_capital_status_quo.csv"
    write_csv(result_row, csv_path)

    doc_path = docs_dir() / "mainnet-entity-owner-capital-status-quo.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(build_doc(snapshot, result_row), encoding="utf-8")

    print(f"\nManifest written to {manifest_path}")
    print(f"CSV written to {csv_path}")
    print(f"Doc written to {doc_path}")


if __name__ == "__main__":
    main()
