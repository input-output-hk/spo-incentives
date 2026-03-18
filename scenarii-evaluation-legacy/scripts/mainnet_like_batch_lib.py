#!/usr/bin/env python3
"""
Shared helpers for running and reporting the mainnet-like base-CIP comparison batch.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


BASELINE_K = 500
BASELINE_A0 = 0.3
SEED = 42
MAX_ITERATIONS = 150
ITERATIONS_AFTER_CONVERGENCE = 10
METRICS = [1, 2, 6, 17, 18, 24, 25, 30]
CIP23_MIN_MARGIN = 0.05
CIP82_MIN_RATE = 0.03
CIP50_L = 100
CIP37_PLEDGE_REFERENCE_ADA = 500_000.0
CIP37_SATURATION_FLOOR = 0.10
STAKE_DISTRIBUTION_FILENAME = "synthetic-stake-distribution-2718-agents.csv"


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    label: str
    reward_scheme: int
    extra_args: tuple[str, ...]
    notes: str


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def spo_incentives_root() -> Path:
    return Path(__file__).resolve().parents[2]


def engine_root() -> Path:
    return workspace_root() / "Rewards-Sharing-Simulation-Engine"


def koios_pool_list_path() -> Path:
    return spo_incentives_root() / "scenarii-evaluation" / "data" / "koios_pool_list_mainnet.csv"


def tracker_path() -> Path:
    return engine_root() / "output" / "experiment-tracker.csv"


def stake_distribution_path() -> Path:
    return engine_root() / STAKE_DISTRIBUTION_FILENAME


def load_registered_positive_pools() -> list[dict[str, str]]:
    with koios_pool_list_path().open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row
        for row in rows
        if row["pool_status"] == "registered" and float(row["active_stake"] or 0) > 0
    ]


def write_stake_distribution_file() -> dict[str, float | int | str]:
    rows = load_registered_positive_pools()
    stakes = [float(row["active_stake"]) for row in rows]
    output_path = stake_distribution_path()
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for stake in stakes:
            writer.writerow([f"{stake:.0f}"])
    return {
        "pool_count": len(stakes),
        "active_stake_lovelace": sum(stakes),
        "active_stake_ada": sum(stakes) / 1_000_000,
        "output_path": str(output_path),
    }


def cip37_pledge_reference_share(active_stake_ada: float) -> float:
    return CIP37_PLEDGE_REFERENCE_ADA / active_stake_ada


def scenario_definitions(active_stake_ada: float) -> list[Scenario]:
    pledge_reference_share = cip37_pledge_reference_share(active_stake_ada)
    return [
        Scenario(
            scenario_id="mainnet-like-status-quo",
            label="Status Quo",
            reward_scheme=0,
            extra_args=(),
            notes="Baseline Cardano reward scheme with the current mainnet-like pool-level stake distribution.",
        ),
        Scenario(
            scenario_id="mainnet-like-cip23-minmargin5",
            label="CIP-0023",
            reward_scheme=5,
            extra_args=("--min_margin", str(CIP23_MIN_MARGIN)),
            notes="Minimum margin floor at 5% while keeping the rest of the baseline structure.",
        ),
        Scenario(
            scenario_id="mainnet-like-cip37-currentref",
            label="CIP-0037",
            reward_scheme=6,
            extra_args=(
                "--pledge_reference",
                str(pledge_reference_share),
                "--saturation_floor",
                str(CIP37_SATURATION_FLOOR),
            ),
            notes="Dynamic saturation with a 500k ADA pledge reference rebased on the live active-stake distribution used in this run set.",
        ),
        Scenario(
            scenario_id="mainnet-like-cip50-L100",
            label="CIP-0050",
            reward_scheme=4,
            extra_args=("--L", str(CIP50_L)),
            notes="Pledge leverage cap with L=100, matching the main scenario-matrix assumption.",
        ),
        Scenario(
            scenario_id="mainnet-like-cip82-minrate3",
            label="CIP-0082",
            reward_scheme=7,
            extra_args=("--min_rate", str(CIP82_MIN_RATE)),
            notes="Current engine approximation of the Stage-2 fee reform with minPoolRate=3% while preserving operator cost inputs.",
        ),
    ]


def latest_output_dir_for_execution_id(execution_id: str) -> Path | None:
    path = tracker_path()
    engine_output_root = engine_root() / "output"
    if not path.exists():
        matches = sorted(engine_output_root.glob(f"*-{execution_id}"))
        return matches[-1] if matches else None

    latest_seq = None
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) < 8 or row[7] != execution_id:
                continue
            try:
                seq_id = int(row[0])
            except ValueError:
                continue
            latest_seq = seq_id if latest_seq is None else max(latest_seq, seq_id)
    if latest_seq is None:
        matches = sorted(engine_output_root.glob(f"*-{execution_id}"))
        return matches[-1] if matches else None
    return engine_output_root / f"{latest_seq}-{execution_id}"


def load_final_descriptors(output_dir: Path) -> dict[str, object]:
    return json.loads((output_dir / "final-state-descriptors.json").read_text(encoding="utf-8"))


def load_metrics_rows(output_dir: Path) -> list[dict[str, str]]:
    with (output_dir / "metrics.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
