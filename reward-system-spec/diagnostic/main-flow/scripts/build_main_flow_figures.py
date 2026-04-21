#!/usr/bin/env python3
"""
Main-Flow Figures — generates figures referenced directly in
cardano-reward-analysis.md.

This script reads intermediate artefacts produced by the sub-flow
pipelines and generates the figures that the main document embeds
directly (as opposed to referencing via relative paths into sub-flows).

Current figures:
  - three_strategies.png — entity count, stake, and owner-stake breakdown
    across hollow / balanced / private strategies (sourced from
    operator-delegator-distribution profiling data).

Data dependencies (read-only):
  - operator-delegator-distribution/mainnet-analysis/data/
      entity_strategy_summary.csv
      reward_split_summary.json

Output:
  - main-flow/figures/three_strategies.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ── paths ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
MAIN_FLOW  = SCRIPT_DIR.parent
FIG_DIR    = MAIN_FLOW / "figures"

OD_DATA = (
    MAIN_FLOW.parent / "sub-flows"
    / "operator-delegator-distribution" / "mainnet-analysis" / "data"
)

STRATEGY_ORDER = ["hollow", "balanced", "private"]
STRATEGY_COLORS = {
    "hollow":   "#E52321",   # IOG Infared
    "balanced": "#16E9D8",   # IOG Electric Blue (Research)
    "private":  "#A700FF",   # IOG Ultraviolet (Venture Studios)
}


def load_entity_strategy_summary() -> pd.DataFrame:
    """Load entity-level strategy summary from operator-delegator sub-flow."""
    path = OD_DATA / "entity_strategy_summary.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Entity strategy summary not found at {path}.\n"
            "Run the operator-delegator profiling script first:\n"
            "  python3 sub-flows/operator-delegator-distribution/"
            "mainnet-analysis/scripts/build_operator_delegator_profile.py"
        )
    return pd.read_csv(path)


def load_summary_json() -> dict:
    """Load headline statistics from operator-delegator sub-flow."""
    path = OD_DATA / "reward_split_summary.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Reward split summary not found at {path}.\n"
            "Run the operator-delegator profiling script first."
        )
    with open(path) as f:
        return json.load(f)


def build_three_strategies_figure(df: pd.DataFrame) -> None:
    """
    Triptych: entity count, active stake, and owner-stake ratio
    for hollow / balanced / private strategies.

    This is the main-flow version of the figure — focused on the
    structural breakdown (population + capital) rather than the
    intra-pool split (which stays in the sub-report).
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle(
        "Three Strategies — Entity-Level View",
        fontsize=14, fontweight="bold", y=1.02,
    )

    # --- Panel 1: Entity count ---
    counts = df.groupby("dominant_strategy").size().reindex(STRATEGY_ORDER)
    colors = [STRATEGY_COLORS[s] for s in STRATEGY_ORDER]
    axes[0].bar(STRATEGY_ORDER, counts.values, color=colors, edgecolor="black",
                linewidth=0.5)
    axes[0].set_title("Entities")
    axes[0].set_ylabel("Count")
    for i, v in enumerate(counts.values):
        axes[0].text(i, v + 5, str(int(v)), ha="center", fontsize=10)

    # --- Panel 2: Active stake ---
    stakes = (
        df.groupby("dominant_strategy")["total_stake"]
        .sum()
        .reindex(STRATEGY_ORDER) / 1e9
    )
    axes[1].bar(STRATEGY_ORDER, stakes.values, color=colors,
                edgecolor="black", linewidth=0.5)
    axes[1].set_title("Active Stake")
    axes[1].set_ylabel("Billion ADA")
    for i, v in enumerate(stakes.values):
        axes[1].text(i, v + 0.1, f"{v:.2f}B", ha="center", fontsize=10)

    # --- Panel 3: Owner-stake ratio ---
    owner_ratios = (
        df.groupby("dominant_strategy")
        .apply(lambda g: g["total_owner_stake"].sum() / g["total_stake"].sum() * 100)
        .reindex(STRATEGY_ORDER)
    )
    axes[2].bar(STRATEGY_ORDER, owner_ratios.values, color=colors,
                edgecolor="black", linewidth=0.5)
    axes[2].set_title("Owner-Stake Ratio")
    axes[2].set_ylabel("% of active stake")
    axes[2].set_ylim(0, 105)
    for i, v in enumerate(owner_ratios.values):
        axes[2].text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=10)

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.tight_layout()
    out_path = FIG_DIR / "strategy_landscape.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out_path.relative_to(MAIN_FLOW)}")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Note: main-flow figures use distinct filenames from sub-report figures.

    print("Loading entity strategy data...")
    df = load_entity_strategy_summary()
    print(f"  {len(df)} entities loaded.")

    print("Building figures...")
    build_three_strategies_figure(df)

    print("Done.")


if __name__ == "__main__":
    main()
