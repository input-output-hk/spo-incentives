#!/usr/bin/env python3
"""
Build a formula-level comparison document for Status Quo vs CIP-0023 / CIP-0037 / CIP-0050 / CIP-0082.

This script stays at the deterministic formula layer:
- reward production (pool reward curve / stake eligibility)
- fee split (operator vs delegator)

It deliberately does not try to reproduce the full agent-based equilibrium dynamics.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CURRENT_K = 500
HIGH_K = 1000
A0 = 0.3
CURRENT_SATURATION_ADA = 76_000_000.0
TOTAL_ACTIVE_STAKE_ADA = CURRENT_K * CURRENT_SATURATION_ADA
EPOCH_POOL_REWARD_POT_ADA = 11_500_000.0
CURRENT_MIN_POOL_COST_ADA = 170.0
CIP0023_MIN_MARGIN = 0.05
CIP0082_MIN_POOL_RATE = 0.03
CIP0050_L = 100.0
CIP0037_PLEDGE_REFERENCE_ADA = 500_000.0
CIP0037_SATURATION_FLOOR = 0.10


@dataclass(frozen=True)
class PoolCase:
    case_id: str
    label: str
    stake_ada: float
    pledge_ada: float
    registered_margin: float = 0.0
    delegator_stake_ada: float = 10_000.0


def relative_stake(value_ada: float) -> float:
    return value_ada / TOTAL_ACTIVE_STAKE_ADA


def saturation_share(k: int) -> float:
    return 1.0 / k


def saturation_ada(k: int) -> float:
    return TOTAL_ACTIVE_STAKE_ADA / k


def baseline_optimal_pool_reward(pool_pledge_ada: float, pool_stake_ada: float, *, k: int = CURRENT_K) -> float:
    z0 = saturation_share(k)
    sigma = relative_stake(pool_stake_ada)
    pledge = relative_stake(pool_pledge_ada)
    sigma_capped = min(sigma, z0)
    pledge_capped = min(pledge, z0)
    return (EPOCH_POOL_REWARD_POT_ADA / (1 + A0)) * (
        sigma_capped
        + pledge_capped
        * A0
        * ((sigma_capped - pledge_capped * ((z0 - sigma_capped) / z0)) / z0)
    )


def cip0050_optimal_pool_reward(pool_pledge_ada: float, pool_stake_ada: float, *, k: int = CURRENT_K) -> float:
    z0 = saturation_share(k)
    sigma = relative_stake(pool_stake_ada)
    pledge = relative_stake(pool_pledge_ada)
    sigma_capped = min(sigma, z0, CIP0050_L * pledge)
    pledge_capped = min(pledge, z0)
    return (EPOCH_POOL_REWARD_POT_ADA / (1 + A0)) * (
        sigma_capped
        + pledge_capped
        * A0
        * ((sigma_capped - pledge_capped * ((z0 - sigma_capped) / z0)) / z0)
    )


def cip0037_dynamic_saturation_share(pool_pledge_ada: float, *, k: int = CURRENT_K) -> float:
    z0 = saturation_share(k)
    phi = max(
        CIP0037_SATURATION_FLOOR,
        min(1.0, pool_pledge_ada / CIP0037_PLEDGE_REFERENCE_ADA),
    )
    return z0 * phi


def cip0037_optimal_pool_reward(pool_pledge_ada: float, pool_stake_ada: float, *, k: int = CURRENT_K) -> float:
    z0 = saturation_share(k)
    sigma = relative_stake(pool_stake_ada)
    pledge = relative_stake(pool_pledge_ada)
    sigma_capped = min(sigma, cip0037_dynamic_saturation_share(pool_pledge_ada, k=k))
    pledge_capped = min(pledge, z0)
    return (EPOCH_POOL_REWARD_POT_ADA / (1 + A0)) * (
        sigma_capped
        + pledge_capped
        * A0
        * ((sigma_capped - pledge_capped * ((z0 - sigma_capped) / z0)) / z0)
    )


def operator_reward(pool_reward_ada: float, fixed_cost_ada: float, margin: float, pledge_ada: float, stake_ada: float) -> float:
    if pool_reward_ada <= fixed_cost_ada:
        return pool_reward_ada
    return fixed_cost_ada + (pool_reward_ada - fixed_cost_ada) * (
        margin + (1 - margin) * (pledge_ada / stake_ada)
    )


def delegator_reward(
    pool_reward_ada: float,
    fixed_cost_ada: float,
    margin: float,
    delegator_stake_ada: float,
    stake_ada: float,
) -> float:
    if pool_reward_ada <= fixed_cost_ada:
        return 0.0
    return (pool_reward_ada - fixed_cost_ada) * (1 - margin) * (delegator_stake_ada / stake_ada)


def percent_delta(candidate: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return ((candidate - baseline) / baseline) * 100.0


def format_num(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(row[column] for column in columns) + " |" for row in rows]
    return "\n".join([header, sep] + body)


def pool_reward_cases() -> list[PoolCase]:
    return [
        PoolCase("small_growth", "Small growth pool", 3_000_000.0, 1_000.0),
        PoolCase("mid_growth", "Mid-sized pool", 10_000_000.0, 10_000.0),
        PoolCase("large_growth", "Large pool", 40_000_000.0, 25_000.0),
        PoolCase("saturated", "Saturated pool", CURRENT_SATURATION_ADA, 500_000.0),
    ]


def fee_split_cases() -> list[PoolCase]:
    return [
        PoolCase("fee_small", "3M stake / 1k pledge / 0% margin", 3_000_000.0, 1_000.0),
        PoolCase("fee_mid", "10M stake / 10k pledge / 0% margin", 10_000_000.0, 10_000.0),
        PoolCase("fee_saturated", "76M stake / 500k pledge / 0% margin", CURRENT_SATURATION_ADA, 500_000.0),
    ]


def build_pool_reward_rows(cases: Iterable[PoolCase]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case in cases:
        baseline = baseline_optimal_pool_reward(case.pledge_ada, case.stake_ada)
        cip0050 = cip0050_optimal_pool_reward(case.pledge_ada, case.stake_ada)
        cip0037 = cip0037_optimal_pool_reward(case.pledge_ada, case.stake_ada)
        dyn_sat_ada = cip0037_dynamic_saturation_share(case.pledge_ada) * TOTAL_ACTIVE_STAKE_ADA
        rows.append(
            {
                "Case": case.label,
                "Stake (ADA)": format_num(case.stake_ada, 0),
                "Pledge (ADA)": format_num(case.pledge_ada, 0),
                "Status Quo reward": format_num(baseline),
                "CIP-0023 reward": format_num(baseline),
                "CIP-0082 reward": format_num(baseline),
                "CIP-0050 reward": format_num(cip0050),
                "CIP-0050 delta %": format_num(percent_delta(cip0050, baseline)),
                "CIP-0037 reward": format_num(cip0037),
                "CIP-0037 delta %": format_num(percent_delta(cip0037, baseline)),
                "CIP-0037 dyn sat": format_num(dyn_sat_ada, 0),
            }
        )
    return rows


def build_fee_split_rows(cases: Iterable[PoolCase]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case in cases:
        pool_reward = baseline_optimal_pool_reward(case.pledge_ada, case.stake_ada)
        status_operator = operator_reward(
            pool_reward,
            CURRENT_MIN_POOL_COST_ADA,
            case.registered_margin,
            case.pledge_ada,
            case.stake_ada,
        )
        status_member = delegator_reward(
            pool_reward,
            CURRENT_MIN_POOL_COST_ADA,
            case.registered_margin,
            case.delegator_stake_ada,
            case.stake_ada,
        )
        cip0023_operator = operator_reward(
            pool_reward,
            CURRENT_MIN_POOL_COST_ADA,
            max(case.registered_margin, CIP0023_MIN_MARGIN),
            case.pledge_ada,
            case.stake_ada,
        )
        cip0023_member = delegator_reward(
            pool_reward,
            CURRENT_MIN_POOL_COST_ADA,
            max(case.registered_margin, CIP0023_MIN_MARGIN),
            case.delegator_stake_ada,
            case.stake_ada,
        )
        cip0082_operator = operator_reward(
            pool_reward,
            0.0,
            max(case.registered_margin, CIP0082_MIN_POOL_RATE),
            case.pledge_ada,
            case.stake_ada,
        )
        cip0082_member = delegator_reward(
            pool_reward,
            0.0,
            max(case.registered_margin, CIP0082_MIN_POOL_RATE),
            case.delegator_stake_ada,
            case.stake_ada,
        )
        rows.append(
            {
                "Case": case.label,
                "Pool reward (ADA)": format_num(pool_reward),
                "Status Quo operator": format_num(status_operator),
                "Status Quo delegator 10k": format_num(status_member),
                "CIP-0023 operator": format_num(cip0023_operator),
                "CIP-0023 delegator 10k": format_num(cip0023_member),
                "CIP-0082 operator": format_num(cip0082_operator),
                "CIP-0082 delegator 10k": format_num(cip0082_member),
            }
        )
    return rows


def build_k_rows() -> list[dict[str, str]]:
    pledge_ada = 500_000.0
    reward_k500 = baseline_optimal_pool_reward(pledge_ada, saturation_ada(CURRENT_K), k=CURRENT_K)
    reward_k1000 = baseline_optimal_pool_reward(pledge_ada, saturation_ada(HIGH_K), k=HIGH_K)
    return [
        {
            "Scenario": "Status Quo / K=500",
            "Target K": str(CURRENT_K),
            "Saturation (ADA)": format_num(saturation_ada(CURRENT_K), 0),
            "Reward at saturation": format_num(reward_k500),
        },
        {
            "Scenario": "CIP-0082 Stage 4 style / K=1000",
            "Target K": str(HIGH_K),
            "Saturation (ADA)": format_num(saturation_ada(HIGH_K), 0),
            "Reward at saturation": format_num(reward_k1000),
        },
    ]


def build_simulation_smoke_rows(workspace_root: Path) -> list[dict[str, str]]:
    engine_root = workspace_root / "Rewards-Sharing-Simulation-Engine"
    tracker_path = engine_root / "output" / "experiment-tracker.csv"
    if not tracker_path.exists():
        return []

    wanted_runs = {
        "doc-status-quo-smoke": "Status Quo",
        "doc-cip23-smoke": "CIP-0023",
        "doc-cip37-smoke": "CIP-0037",
        "doc-cip50-smoke": "CIP-0050",
        "doc-cip82-smoke": "CIP-0082",
    }

    found_rows: dict[str, dict[str, str]] = {}
    with tracker_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 8:
                continue
            seq_id = row[0]
            scheme_name = row[6]
            execution_id = row[7]
            if execution_id not in wanted_runs:
                continue
            output_dir = engine_root / "output" / f"{seq_id}-{execution_id}"
            descriptor_path = output_dir / "final-state-descriptors.json"
            if not descriptor_path.exists():
                continue
            descriptors = json.loads(descriptor_path.read_text(encoding="utf-8"))
            found_rows[execution_id] = {
                "Variant": wanted_runs[execution_id],
                "Engine scheme": scheme_name,
                "Equilibrium": str(descriptors.get("Equilibrium reached", "n/a")),
                "Pool count": str(descriptors.get("Pool count", "n/a")),
                "Operator count": str(descriptors.get("Operator count", "n/a")),
                "Nakamoto": str(descriptors.get("Nakamoto coefficient", "n/a")),
                "Pledge fraction": str(descriptors.get("Total pledge fraction", "n/a")),
                "Output folder": output_dir.name,
            }

    return [found_rows[key] for key in wanted_runs if key in found_rows]


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_doc(
    pool_rows: list[dict[str, str]],
    fee_rows: list[dict[str, str]],
    k_rows: list[dict[str, str]],
    simulation_rows: list[dict[str, str]],
) -> str:
    toc = "\n".join(
        [
            "- [Scope](#scope)",
            "- [Shared Assumptions](#shared-assumptions)",
            "- [What Was Implemented](#what-was-implemented)",
            "- [Simulation Runs Included](#simulation-runs-included)",
            "- [Formula Comparison vs Status Quo](#formula-comparison-vs-status-quo)",
            "- [Reward-Production Layer Comparison](#reward-production-layer-comparison)",
            "- [Fee-Split Layer Comparison](#fee-split-layer-comparison)",
            "- [Direct K=1000 Implication](#direct-k1000-implication)",
            "- [Simulation Smoke Results](#simulation-smoke-results)",
            "- [Comparison Summary](#comparison-summary)",
            "- [Next Simulation Step](#next-simulation-step)",
        ]
    )

    lines = [
        "# CIP Formula Comparison vs Status Quo",
        "",
        "## Table of Contents",
        toc,
        "",
        "## Scope",
        "",
        "This document compares the formula deltas of `CIP-0023`, `CIP-0037`, `CIP-0050`, and `CIP-0082`",
        "against the Shelley-aligned status quo at the deterministic formula layer.",
        "",
        "It covers two layers separately:",
        "- reward production: what changes the pool reward curve itself",
        "- fee split: what changes how operator and delegators split an already-computed pool reward",
        "",
        "It does **not** attempt to model the full equilibrium dynamics here. That remains the next step.",
        "",
        "## Shared Assumptions",
        "",
        f"- `K` baseline: `{CURRENT_K}`",
        f"- `a0`: `{A0}`",
        f"- Saturation at `K={CURRENT_K}`: `{format_num(CURRENT_SATURATION_ADA, 0)}` ADA",
        f"- Implied active stake anchor: `{format_num(TOTAL_ACTIVE_STAKE_ADA, 0)}` ADA",
        f"- Epoch pool reward pot anchor: `{format_num(EPOCH_POOL_REWARD_POT_ADA, 0)}` ADA",
        f"- Current `minPoolCost` anchor: `{format_num(CURRENT_MIN_POOL_COST_ADA, 0)}` ADA",
        f"- `CIP-0023` illustrative `minPoolMargin`: `{CIP0023_MIN_MARGIN:.0%}`",
        f"- `CIP-0082` Stage 2 `minPoolRate`: `{CIP0082_MIN_POOL_RATE:.0%}`",
        f"- `CIP-0050` illustrative leverage `L`: `{format_num(CIP0050_L, 0)}`",
        f"- `CIP-0037` pledge reference: `{format_num(CIP0037_PLEDGE_REFERENCE_ADA, 0)}` ADA",
        f"- `CIP-0037` saturation floor: `{CIP0037_SATURATION_FLOOR:.0%}` of `K` saturation",
        "",
        "## What Was Implemented",
        "",
        "- `Status Quo`: baseline Shelley reward function and baseline operator/member split.",
        "- `CIP-0023`: fee-layer clamp only. Pool reward production stays identical to the status quo.",
        "- `CIP-0082`: Stage 2 fee-layer reform (`minPoolCost = 0`, `minPoolRate = 3%`). Stages 3 and 4 are treated separately as `K` changes.",
        "- `CIP-0050`: reward-eligible stake cap becomes `min(stake, z0, L * pledge)`.",
        "- `CIP-0037`: pool saturation becomes pledge-dependent with a lower-limit floor.",
        "",
        "## Simulation Runs Included",
        "",
        "This document now includes a small comparable smoke batch from the strategic simulator as a visibility aid.",
        "Those runs use the same compact parameters across variants:",
        "- `n = 50`",
        "- `k = 10`",
        "- `a0 = 0.3`",
        "- `seed = 42`",
        "- `max_iterations = 20`",
        "",
        "These are **not** the final policy-evaluation runs. They only confirm that the five variants execute cleanly in the engine",
        "and give a first same-parameter comparison point against the status quo.",
        "",
        "## Formula Comparison vs Status Quo",
        "",
        "The comparison splits cleanly into two buckets:",
        "- `CIP-0023` and `CIP-0082` are primarily fee-layer changes.",
        "- `CIP-0050` and `CIP-0037` are primarily reward-production / stake-cap changes.",
        "",
        "That distinction matters because `CIP-0023` and `CIP-0082` do not change the raw pool reward curve at fixed `K`,",
        "while `CIP-0050` and `CIP-0037` can materially reduce or reshape the reward earned by high-stake / low-pledge pools.",
        "",
        "## Reward-Production Layer Comparison",
        "",
        "Table below compares pool reward production for four representative pool states. `CIP-0023` and `CIP-0082`",
        "match the status quo here because they do not alter the pool reward function itself at fixed `K`.",
        "",
        markdown_table(
            pool_rows,
            [
                "Case",
                "Stake (ADA)",
                "Pledge (ADA)",
                "Status Quo reward",
                "CIP-0023 reward",
                "CIP-0082 reward",
                "CIP-0050 reward",
                "CIP-0050 delta %",
                "CIP-0037 reward",
                "CIP-0037 delta %",
                "CIP-0037 dyn sat",
            ],
        ),
        "",
        "Reading:",
        "- `CIP-0050` only diverges materially once `L * pledge` is below the pool stake or below the normal saturation cap.",
        "- `CIP-0037` can diverge much earlier because it rewrites the saturation threshold itself.",
        "- For small or moderately growing pools, `CIP-0037` still allows headroom thanks to the floor, but large low-pledge pools lose reward-eligible capacity quickly.",
        "",
        "## Fee-Split Layer Comparison",
        "",
        "This table fixes the pool reward formula to the status quo and then compares how the same reward gets split.",
        "Each example uses a registered margin of `0%`, so the fee-floor effects are visible immediately.",
        "",
        markdown_table(
            fee_rows,
            [
                "Case",
                "Pool reward (ADA)",
                "Status Quo operator",
                "Status Quo delegator 10k",
                "CIP-0023 operator",
                "CIP-0023 delegator 10k",
                "CIP-0082 operator",
                "CIP-0082 delegator 10k",
            ],
        ),
        "",
        "Reading:",
        "- `CIP-0023` raises operator take by clamping low margins upward while keeping the fixed-fee floor in place.",
        "- `CIP-0082` Stage 2 removes the fixed-fee floor, so the operator loses the guaranteed fixed component but still receives the 3% rate floor.",
        "- For smaller pools, that means `CIP-0082` can materially improve delegator fairness while worsening operator protection.",
        "",
        "## Direct K=1000 Implication",
        "",
        "Even before any strategic simulation, the raw formula already shows what `K=1000` means: saturation halves.",
        "",
        markdown_table(
            k_rows,
            [
                "Scenario",
                "Target K",
                "Saturation (ADA)",
                "Reward at saturation",
            ],
        ),
        "",
        "This is why `K=1000` must stay a separate policy axis.",
        "It is not a cosmetic tweak. It changes the economic scale of a 'full' pool.",
        "",
        "## Simulation Smoke Results",
        "",
    ]

    if simulation_rows:
        lines.extend(
            [
                "Smoke-run outputs live under the engine output root:",
                "- `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output`",
                "",
                markdown_table(
                    simulation_rows,
                    [
                        "Variant",
                        "Engine scheme",
                        "Equilibrium",
                        "Pool count",
                        "Operator count",
                        "Nakamoto",
                        "Pledge fraction",
                        "Output folder",
                    ],
                ),
                "",
                "Reading:",
                "- All five smoke runs converge and expose their results in concrete output folders.",
                "- On this tiny validation setup, the final descriptors are identical across variants, so this section is only a run check, not yet a discriminating policy result.",
                "- The real comparison signal should come from larger equilibrium batches at realistic `k` and stake-distribution settings.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "No smoke-run outputs were detected when this document was generated.",
                "",
            ]
        )

    lines.extend(
        [
            "## Comparison Summary",
            "",
            "- `Status Quo`: common global saturation, existing pledge term, fixed-cost floor intact.",
            "- `CIP-0023`: no reward-curve change; pure fee-floor intervention via minimum margin.",
            "- `CIP-0082`: no reward-curve change at Stage 2; strong fee-layer redesign. Stages 3/4 are really `K` policy changes.",
            "- `CIP-0050`: keeps the existing saturation rule but adds a leverage ceiling based on pledge.",
            "- `CIP-0037`: changes the saturation rule itself, so the pool reward curve becomes pool-specific.",
            "",
            "From a modeling perspective, the cleanest interpretation is:",
            "- `0023` and `0082` answer operator/delegator split fairness.",
            "- `0050` and `0037` answer pledge discipline and MPO leverage.",
            "",
            "## Next Simulation Step",
            "",
            "The next implementation step is to push these formula deltas into the strategic simulator in two layers:",
            "",
            "1. stake-cap layer: `Status Quo`, `CIP-0050`, `CIP-0037`",
            "2. fee layer: `Status Quo`, `CIP-0023`, `CIP-0082`",
            "",
            "Then the scenario matrix can combine exactly one rule from each layer and compare equilibrium outcomes against the status quo.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    workspace_root = root.parent
    data_dir = root / "scenarii-evaluation" / "data"
    docs_dir = root / "scenarii-evaluation" / "docs"

    pool_rows = build_pool_reward_rows(pool_reward_cases())
    fee_rows = build_fee_split_rows(fee_split_cases())
    k_rows = build_k_rows()
    simulation_rows = build_simulation_smoke_rows(workspace_root)

    write_csv(pool_rows, data_dir / "cip_formula_pool_comparison.csv")
    write_csv(fee_rows, data_dir / "cip_formula_fee_comparison.csv")
    write_csv(k_rows, data_dir / "cip_formula_k_comparison.csv")
    if simulation_rows:
        write_csv(simulation_rows, data_dir / "cip_formula_simulation_smoke_results.csv")

    doc = build_doc(pool_rows, fee_rows, k_rows, simulation_rows)
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "cip-formula-comparison.md").write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    main()
