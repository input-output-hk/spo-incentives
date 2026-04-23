"""
Render the central comparison figure: Nakamoto coefficient under each of
the eleven definitions in this sub-flow — D1..D7 (project's stake-based
recompute) plus D8a/D8b (EDI methodology, on-chain-metadata clustering)
and D9a/D9b (EDI methodology, no clustering), grouped to make the
methodological provenance of each bar explicit.

Reads:
  outputs/nakamoto_definitions.csv      (D1..D7, project recompute)
  edi-replication/outputs/edi_output_clustered.csv          (D8a)
  edi-replication/outputs/edi_output_pool_only.csv          (D9a)
  edi-replication/outputs_e618_e623/edi_output_clustered.csv (D8b)
  edi-replication/outputs_e618_e623/edi_output_pool_only.csv (D9b)

Writes:
  figures/definitions_comparison.png
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DEFS = ROOT / "outputs" / "nakamoto_definitions.csv"
EDI_E584_CLUSTERED = ROOT / "edi-replication" / "outputs" / "edi_output_clustered.csv"
EDI_E584_POOL = ROOT / "edi-replication" / "outputs" / "edi_output_pool_only.csv"
EDI_E623_CLUSTERED = ROOT / "edi-replication" / "outputs_e618_e623" / "edi_output_clustered.csv"
EDI_E623_POOL = ROOT / "edi-replication" / "outputs_e618_e623" / "edi_output_pool_only.csv"
OUT = ROOT / "figures" / "definitions_comparison.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# IOG palette (from .claude/rules/IOG_BRAND_GUIDELINES.md)
INFARED = "#E52321"      # primary, pool-level stake
DAWN = "#EC641D"         # warm accent, pool-level stake
ELECTRIC_BLUE = "#16E9D8"  # Research, entity-clustered stake
ULTRAVIOLET = "#A700FF"  # Venture Studios, custody-removed
ACID_GREEN = "#06FF89"   # Engineering, sub-threshold variants
SOLAR_AMBER = "#FFBA36"  # tertiary, EDI pool-only blocks
COBALT_PULSE = "#2C4FFA"  # tertiary, EDI clustered blocks
BLACK = "#000000"
GRAY = "#6A6A6A"


def read_nakamoto_at(csv_path: Path, target_date: str) -> int:
    """Return the nakamoto_coefficient field of the row whose ``date``
    column matches ``target_date``.

    EDI emits two adjacent 30-day windows per batch; the relevant one for
    each reference epoch is the window whose 30 days contain the last slot
    of that epoch (see edi-replication/README.md).
    """
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] == target_date:
                return int(row["nakamoto_coefficient"])
    raise KeyError(f"No row for date {target_date} in {csv_path}")


# Project recompute (D1..D7)
defs: list[tuple[str, str, int]] = []
with DEFS.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        defs.append((row["definition"], row["description"], int(row["nakamoto"])))

# EDI methodology in-house run (D8a/D8b/D9a/D9b) — windows pinned to the
# 30-day window containing the last slot of each reference epoch
d8a = read_nakamoto_at(EDI_E584_CLUSTERED, "2025-09-05")
d8b = read_nakamoto_at(EDI_E623_CLUSTERED, "2026-04-03")
d9a = read_nakamoto_at(EDI_E584_POOL, "2025-09-05")
d9b = read_nakamoto_at(EDI_E623_POOL, "2026-04-03")

# Display order: pool stake | entity stake | EDI pool-only | EDI clustered
short_labels = [
    "D1\nPool, raw\nstake",
    "D2\nPool,\nproductive",
    "D3\nEntity,\nall pools",
    "D4\nEntity, productive\n(status-quo)",
    "D5\nEntity, prod.\nno custody",
    "D6\nEntity + sub-thr.\ncoalition",
    "D7\nEntity, all pools\nno custody",
    "D9a\nEDI, pool\nblocks · e584",
    "D9b\nEDI, pool\nblocks · e623",
    "D8a\nEDI, clustered\nblocks · e584",
    "D8b\nEDI, clustered\nblocks · e623",
]

stake_values = [d[2] for d in defs]
edi_values = [d9a, d9b, d8a, d8b]
values = stake_values + edi_values

colors = [
    DAWN, INFARED,                                           # D1, D2 — pool stake
    ELECTRIC_BLUE, ELECTRIC_BLUE, ULTRAVIOLET, ACID_GREEN, ULTRAVIOLET,  # D3..D7 — entity stake
    SOLAR_AMBER, SOLAR_AMBER,                                # D9a, D9b — EDI pool blocks
    COBALT_PULSE, COBALT_PULSE,                              # D8a, D8b — EDI clustered blocks
]

# Insert visual gap between methodological groups by shifting bar x-positions
group_breaks = {7}  # gap before D9a (start of EDI methodology block)
positions: list[float] = []
x = 0.0
for i in range(len(values)):
    if i in group_breaks:
        x += 0.6
    positions.append(x)
    x += 1.0

fig, ax = plt.subplots(figsize=(13, 5.8))
bars = ax.bar(positions, values, color=colors, alpha=0.88,
              edgecolor=BLACK, linewidth=0.7, width=0.78)

# Highlight D4 (canonical status-quo) with a thicker edge
bars[3].set_edgecolor(INFARED)
bars[3].set_linewidth(2.0)

# Annotate bars with their value
for bar, val in zip(bars, values):
    ax.annotate(str(val),
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                textcoords="offset points", xytext=(0, 5),
                ha="center", fontsize=10.5, color=BLACK, fontweight="bold")

ax.set_xticks(positions)
ax.set_xticklabels(short_labels, fontsize=8.3)

# Group labels under the x-axis
y_group = -max(values) * 0.18
ax.annotate("Project recompute · stake-based · snapshot e623",
            (sum(positions[:7]) / 7, y_group),
            ha="center", fontsize=9.5, color=GRAY, style="italic",
            annotation_clip=False)
ax.annotate("EDI methodology · in-house run · 30-day block windows",
            (sum(positions[7:]) / 4, y_group),
            ha="center", fontsize=9.5, color=GRAY, style="italic",
            annotation_clip=False)

ax.set_ylabel("Nakamoto coefficient", fontsize=11)
ax.set_title("Nakamoto coefficient under eleven definitions — Cardano mainnet\n"
             "Cascade 162 → 90 → 18 reads as a clustering-only effect",
             fontsize=12.5, loc="left", color=BLACK)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, max(values) * 1.18)

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Wrote {OUT} — D1..D7 + D8a/D8b/D9a/D9b")
