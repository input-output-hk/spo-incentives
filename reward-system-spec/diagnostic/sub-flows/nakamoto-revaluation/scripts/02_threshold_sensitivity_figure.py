"""
Render the threshold-sensitivity figure: Nakamoto coefficient as a function
of the production-threshold cut, on the entity-clustered population.

Reads:
  outputs/sensitivity_threshold.csv

Writes:
  figures/threshold_sensitivity.png
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SENS = ROOT / "outputs" / "sensitivity_threshold.csv"
OUT = ROOT / "figures" / "threshold_sensitivity.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# IOG palette (from .claude/rules/IOG_BRAND_GUIDELINES.md)
INFARED = "#E52321"
DAWN = "#EC641D"
ELECTRIC_BLUE = "#16E9D8"
BLACK = "#000000"

thresholds: list[float] = []
n_entities: list[int] = []
nakamoto: list[int] = []
n_pools: list[int] = []

with SENS.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        thresholds.append(float(row["threshold_ada"]))
        n_pools.append(int(row["n_pools"]))
        n_entities.append(int(row["n_entities"]))
        nakamoto.append(int(row["nakamoto"]))

xticks = [f"{int(t/1e3)}k" if t < 1e6 else f"{int(t/1e6)}M" if t > 0 else "0" for t in thresholds]

fig, ax1 = plt.subplots(figsize=(8.5, 4.6))
ax2 = ax1.twinx()

ax1.bar(range(len(thresholds)), n_entities, color=ELECTRIC_BLUE, alpha=0.55, width=0.6,
        label="Entities after clustering (left axis)")
ax1.set_xticks(range(len(thresholds)))
ax1.set_xticklabels(xticks)
ax1.set_xlabel("Production threshold (ADA per pool)")
ax1.set_ylabel("Number of entities", color=BLACK)
ax1.tick_params(axis="y", colors=BLACK)
ax1.spines["top"].set_visible(False)

line, = ax2.plot(range(len(thresholds)), nakamoto, color=INFARED, marker="o",
                 linewidth=2.4, markersize=7, label="Nakamoto coefficient (right axis)")
for i, nc in enumerate(nakamoto):
    ax2.annotate(str(nc), (i, nc), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontsize=9, color=INFARED, fontweight="bold")
ax2.set_ylabel("Nakamoto coefficient", color=INFARED)
ax2.tick_params(axis="y", colors=INFARED)
ax2.set_ylim(0, max(nakamoto) * 1.6)
ax2.spines["top"].set_visible(False)

ax1.set_title("Entity-clustered Nakamoto coefficient is robust to the\n"
              "production-threshold cut — mainnet, epoch 623",
              fontsize=11, color=BLACK, loc="left")

# combined legend
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=9)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Wrote {OUT}")
