#!/usr/bin/env python3
"""
Build the dedicated report for the mainnet-like comparison batch.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from mainnet_like_batch_lib import (
    BASELINE_A0,
    BASELINE_K,
    CIP23_MIN_MARGIN,
    CIP37_PLEDGE_REFERENCE_ADA,
    CIP37_SATURATION_FLOOR,
    CIP50_L,
    CIP82_MIN_RATE,
    ITERATIONS_AFTER_CONVERGENCE,
    MAX_ITERATIONS,
    METRICS,
    SEED,
    latest_output_dir_for_execution_id,
    load_final_descriptors,
    load_metrics_rows,
    scenario_definitions,
    spo_incentives_root,
    write_stake_distribution_file,
)

PARTIAL_RUNS = {}


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(row[column] for column in columns) + " |" for row in rows]
    return "\n".join([header, separator] + body)


def build_rows() -> tuple[list[dict[str, str]], dict[str, str], float, int]:
    snapshot = write_stake_distribution_file()
    active_stake_ada = float(snapshot["active_stake_ada"])
    rows: list[dict[str, str]] = []

    for scenario in scenario_definitions(active_stake_ada=active_stake_ada):
        output_dir = latest_output_dir_for_execution_id(scenario.scenario_id)
        if output_dir is None:
            raise FileNotFoundError(f"No output folder found for {scenario.scenario_id}")
        final_descriptor_path = output_dir / "final-state-descriptors.json"
        metrics_path = output_dir / "metrics.csv"
        if final_descriptor_path.exists() and metrics_path.exists():
            descriptors = load_final_descriptors(output_dir)
            metrics = load_metrics_rows(output_dir)
            final_metrics = metrics[-1]
            rows.append(
                {
                    "Scenario": scenario.label,
                    "Status": "completed",
                    "Step 1 pools": metrics[1]["Pool count"] if len(metrics) > 1 else "n/a",
                    "Pools": str(descriptors["Pool count"]),
                    "Operators": str(descriptors["Operator count"]),
                    "Nakamoto": str(descriptors["Nakamoto coefficient"]),
                    "Pledge fraction": str(descriptors["Total pledge fraction"]),
                    "Rounds": final_metrics["Round"],
                    "Max pools/op": final_metrics["Max pools per operator"],
                    "Mean margin": f"{float(final_metrics['Mean margin']):.4f}",
                    "Median margin": f"{float(final_metrics['Median margin']):.4f}",
                    "Output folder": output_dir.name,
                    "Notes": "",
                }
            )
            continue

        partial = PARTIAL_RUNS.get(scenario.scenario_id)
        if partial is None:
            raise FileNotFoundError(f"Incomplete run with no partial override for {scenario.scenario_id}")
        rows.append(
            {
                "Scenario": scenario.label,
                "Status": "partial",
                "Step 1 pools": partial["step1_pools"],
                "Pools": "n/a",
                "Operators": "n/a",
                "Nakamoto": "n/a",
                "Pledge fraction": "n/a",
                "Rounds": partial["rounds"],
                "Max pools/op": "n/a",
                "Mean margin": "n/a",
                "Median margin": "n/a",
                "Output folder": output_dir.name,
                "Notes": partial["note"],
            }
        )

    baseline = next(row for row in rows if row["Scenario"] == "Status Quo")
    return rows, baseline, active_stake_ada, int(snapshot["pool_count"])


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_doc(
    rows: list[dict[str, str]],
    baseline: dict[str, str],
    active_stake_ada: float,
    positive_pool_count: int,
) -> str:
    pool_rows = []
    for row in rows:
        delta = "n/a"
        if row["Status"] == "completed" and baseline["Status"] == "completed":
            delta = str(int(row["Pools"]) - int(baseline["Pools"]))
        pool_rows.append(
            {
                "Scenario": row["Scenario"],
                "Status": row["Status"],
                "Pools": row["Pools"],
                "Delta vs SQ": delta,
                "Operators": row["Operators"],
                "Nakamoto": row["Nakamoto"],
                "Rounds": row["Rounds"],
                "Max pools/op": row["Max pools/op"],
            }
        )

    margin_rows = [
        {
            "Scenario": row["Scenario"],
            "Status": row["Status"],
            "Step 1 pools": row["Step 1 pools"],
            "Mean margin": row["Mean margin"],
            "Median margin": row["Median margin"],
            "Pledge fraction": row["Pledge fraction"],
            "Output folder": row["Output folder"],
            "Notes": row["Notes"] or "completed run",
        }
        for row in rows
    ]

    toc = "\n".join(
        [
            "- [Scope](#scope)",
            "- [Mainnet-like Input](#mainnet-like-input)",
            "- [Run Parameters](#run-parameters)",
            "- [Scenario Set](#scenario-set)",
            "- [Headline Results](#headline-results)",
            "- [Early-Path Shock](#early-path-shock)",
            "- [Margin and Pledge Read](#margin-and-pledge-read)",
            "- [Interpretation](#interpretation)",
            "- [Raw Outputs](#raw-outputs)",
            "- [Caveats](#caveats)",
        ]
    )

    raw_outputs = "\n".join(
        f"- `{row['Scenario']}`: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/{row['Output folder']}`"
        for row in rows
    )

    return "\n".join(
        [
            "# Mainnet-like Base CIP Comparison",
            "",
            "## Table of Contents",
            toc,
            "",
            "## Scope",
            "",
            "This report compares `Status Quo`, `CIP-0023`, `CIP-0037`, `CIP-0050`, and `CIP-0082`",
            "inside the strategic simulation engine using a current mainnet-like pool-level stake distribution rather than the tiny smoke setup.",
            "",
            "## Mainnet-like Input",
            "",
            "The stake distribution is built from the current local mainnet snapshot already present in this workspace:",
            "- source file: `scenarii-evaluation/data/koios_pool_list_mainnet.csv`",
            f"- currently registered pools with positive stake: `{positive_pool_count}`",
            f"- active stake represented in this run set: `{active_stake_ada:,.3f}` ADA",
            "- each positive-stake registered pool contributes one stake value into the engine file-based distribution",
            "",
            "This is a **pool-level active-stake distribution**, not a wallet-level delegation snapshot.",
            "It is still much closer to current mainnet structure than the earlier Pareto smoke test.",
            "",
            "## Run Parameters",
            "",
            f"- `k = {BASELINE_K}`",
            f"- `a0 = {BASELINE_A0}`",
            f"- `seed = {SEED}`",
            f"- `max_iterations = {MAX_ITERATIONS}`",
            f"- `iterations_after_convergence = {ITERATIONS_AFTER_CONVERGENCE}`",
            f"- metrics tracked: `{METRICS}`",
            f"- `CIP-0023` floor: `{CIP23_MIN_MARGIN:.0%}`",
            f"- `CIP-0050` leverage: `L = {CIP50_L}`",
            f"- `CIP-0037` reference: `{CIP37_PLEDGE_REFERENCE_ADA:,.0f}` ADA with floor `{CIP37_SATURATION_FLOOR:.0%}`",
            f"- `CIP-0082` min rate: `{CIP82_MIN_RATE:.0%}`",
            "",
            "## Scenario Set",
            "",
            "- `Status Quo`: baseline Cardano reward scheme.",
            "- `CIP-0023`: minimum margin floor only.",
            "- `CIP-0037`: pledge-linked saturation, rebased to the active stake represented by this snapshot.",
            "- `CIP-0050`: pledge leverage cap with `L=100`.",
            "- `CIP-0082`: current engine approximation of Stage 2 with `minPoolRate=3%` while preserving operator cost inputs.",
            "",
            "## Headline Results",
            "",
            markdown_table(
                pool_rows,
                [
                    "Scenario",
                    "Status",
                    "Pools",
                    "Delta vs SQ",
                    "Operators",
                    "Nakamoto",
                    "Rounds",
                    "Max pools/op",
                ],
            ),
            "",
            "## Early-Path Shock",
            "",
            markdown_table(
                [
                    {
                        "Scenario": row["Scenario"],
                        "Status": row["Status"],
                        "Step 1 pools": row["Step 1 pools"],
                        "Notes": row["Notes"] or "completed run",
                    }
                    for row in rows
                ],
                [
                    "Scenario",
                    "Status",
                    "Step 1 pools",
                    "Notes",
                ],
            ),
            "",
            "## Margin and Pledge Read",
            "",
            markdown_table(
                margin_rows,
                [
                    "Scenario",
                    "Status",
                    "Step 1 pools",
                    "Mean margin",
                    "Median margin",
                    "Pledge fraction",
                    "Output folder",
                    "Notes",
                ],
            ),
            "",
            "## Interpretation",
            "",
            "- The mainnet-like setup breaks the artificial smoke-run symmetry immediately.",
            "- `CIP-0023` materially raises the final margin regime and converges much faster than the status quo in this run set.",
            "- `CIP-0037` changes the early trajectory strongly, but lands near the baseline final structure in this first pass.",
            "- `CIP-0050` with `L=100` slightly reduces pools/operators and ends with the lowest margin regime among the completed runs.",
            "- `CIP-0082` should now be read as a margin-floor-only engine approximation until the fee layer is modeled more faithfully.",
            "- The comparison should be read as a first current-mainnet run set, not as a final ledger-faithful economic forecast.",
            "",
            "## Raw Outputs",
            "",
            raw_outputs,
            "",
            "## Caveats",
            "",
            "- The engine still uses an approximation for fee-layer economics; `CIP-0023` and `CIP-0082` are not fully ledger-faithful.",
            "- The input distribution is pool-level active stake, not wallet-level stake-holder distribution.",
            "- This batch keeps `k=500`; the separate `k=1000` policy axis still needs its own run set.",
            "",
        ]
    )


def main() -> None:
    rows, baseline, active_stake_ada, positive_pool_count = build_rows()
    root = spo_incentives_root() / "scenarii-evaluation"
    csv_path = root / "data" / "mainnet_like_base_cip_results.csv"
    doc_path = root / "docs" / "mainnet-like-base-cip-comparison.md"

    write_csv(rows, csv_path)
    doc_path.write_text(
        build_doc(rows, baseline, active_stake_ada, positive_pool_count),
        encoding="utf-8",
    )
    print(doc_path)
    print(csv_path)


if __name__ == "__main__":
    main()
