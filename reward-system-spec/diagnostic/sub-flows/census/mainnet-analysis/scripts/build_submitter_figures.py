#!/usr/bin/env python3
"""Build §6 submitter figures from definitive epoch 623 data.

Reads:
  data/submitter_totals_623.csv        — per-epoch unique submitters, tx count, fee
  data/submitter_decomp_623.csv        — per-epoch × addr_type decomposition
  data/fee_concentration_623.csv       — fee tier buckets (ep 618–623)
  data/tx_type_composition_623.csv     — per-epoch script/simple tx split

Generates:
  figures/submitter_volume_623.png     — tx volume + unique submitters timeline
  figures/submitter_population_623.png — addr-type decomposition stacked area
  figures/submitter_fee_decomp_623.png — fee share by addr type over time
"""
import csv
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPORT = Path(__file__).resolve().parent.parent
DATA   = REPORT / "data"
FIG    = REPORT / "figures"

BG       = "#FFFFFF"
INK      = "#1A1A1A"
DIM      = "#666666"
GRID     = "#EBEBEB"
INFARED  = "#E52321"
DAWN     = "#EC641D"
SOLAR    = "#FFBA36"
COBALT   = "#2C4FFA"
ELEC     = "#16E9D8"
GREY     = "#B0B0B0"
ACID     = "#06FF89"
ULTRA    = "#A700FF"

ADDR_COLOURS = {
    "base_key":           COBALT,
    "enterprise_key":     DAWN,
    "base_script":        ELEC,
    "enterprise_script":  INFARED,
    "base_other":         ULTRA,
    "legacy":             GREY,
}

ADDR_LABELS = {
    "base_key":           "Base key (addr1q)",
    "enterprise_key":     "Enterprise key (addr1v)",
    "base_script":        "Base script (addr1z)",
    "enterprise_script":  "Enterprise script (addr1w)",
    "base_other":         "Base other (addr1x/y)",
    "legacy":             "Legacy (Byron)",
}

ADDR_ORDER = ["base_key", "enterprise_key", "base_script",
              "enterprise_script", "base_other", "legacy"]


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.grid(axis="y", color=GRID, linewidth=0.5, alpha=0.7)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=8)


def build_volume_figure():
    """Figure 1: tx volume + unique submitters over time."""
    rows = []
    with (DATA / "submitter_totals_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    epochs = [int(r["epoch_no"]) for r in rows]
    tx_k = [int(r["tx_count"]) / 1e3 for r in rows]
    sub_k = [int(r["unique_submitters"]) / 1e3 for r in rows]
    fee = [float(r["total_fee_ada"]) / 1e3 for r in rows]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), facecolor=BG,
                                    sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for ax in [ax1, ax2]:
        style_ax(ax)

    ax1.fill_between(epochs, 0, tx_k, alpha=0.4, color=COBALT, label="Transactions (K)")
    ax1.plot(epochs, sub_k, color=INFARED, lw=1.5, label="Unique submitters (K)")
    ax1.set_ylabel("Count (thousands)", fontsize=9, color=DIM)
    ax1.set_title("Transaction Volume and Submitter Population — Epochs 208–623",
                  fontsize=12, fontweight="medium", color=INK, pad=12)
    ax1.legend(fontsize=8, loc="upper left")

    ax2.fill_between(epochs, 0, fee, alpha=0.5, color=DAWN)
    ax2.set_ylabel("Fee (K ADA)", fontsize=9, color=DIM)
    ax2.set_xlabel("Epoch", fontsize=9, color=DIM)

    fig.tight_layout()
    out = FIG / "submitter_volume_623.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_population_figure():
    """Figure 2: submitter addr-type decomposition stacked area."""
    raw = defaultdict(dict)
    with (DATA / "submitter_decomp_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            ep = int(r["epoch_no"])
            raw[ep][r["addr_type"]] = int(r["unique_submitters"])

    epochs = sorted(raw.keys())
    series = {}
    for at in ADDR_ORDER:
        series[at] = [raw[ep].get(at, 0) / 1e3 for ep in epochs]

    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    style_ax(ax)

    bottom = np.zeros(len(epochs))
    for at in ADDR_ORDER:
        vals = np.array(series[at])
        ax.fill_between(epochs, bottom, bottom + vals, alpha=0.7,
                        color=ADDR_COLOURS[at], label=ADDR_LABELS[at])
        bottom += vals

    ax.set_xlabel("Epoch", fontsize=9, color=DIM)
    ax.set_ylabel("Unique submitters (thousands)", fontsize=9, color=DIM)
    ax.set_title("Submitter Population by Address Type — Epochs 208–623",
                 fontsize=12, fontweight="medium", color=INK, pad=12)
    ax.legend(fontsize=7, loc="upper right", ncol=2)

    fig.tight_layout()
    out = FIG / "submitter_population_623.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_fee_decomp_figure():
    """Figure 3: fee share by addr type stacked area."""
    raw = defaultdict(dict)
    with (DATA / "submitter_decomp_623.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            ep = int(r["epoch_no"])
            raw[ep][r["addr_type"]] = float(r["total_fee_ada"])

    epochs = sorted(raw.keys())

    # Compute shares
    totals = {ep: sum(raw[ep].values()) for ep in epochs}
    series = {}
    for at in ADDR_ORDER:
        series[at] = [100 * raw[ep].get(at, 0) / totals[ep] if totals[ep] > 0 else 0
                      for ep in epochs]

    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
    style_ax(ax)

    bottom = np.zeros(len(epochs))
    for at in ADDR_ORDER:
        vals = np.array(series[at])
        ax.fill_between(epochs, bottom, bottom + vals, alpha=0.7,
                        color=ADDR_COLOURS[at], label=ADDR_LABELS[at])
        bottom += vals

    ax.set_ylim(0, 100)
    ax.set_xlabel("Epoch", fontsize=9, color=DIM)
    ax.set_ylabel("Share of fee revenue (%)", fontsize=9, color=DIM)
    ax.set_title("Fee Revenue Share by Submitter Address Type — Epochs 208–623",
                 fontsize=12, fontweight="medium", color=INK, pad=12)
    ax.legend(fontsize=7, loc="upper right", ncol=2)

    fig.tight_layout()
    out = FIG / "submitter_fee_decomp_623.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    if (DATA / "submitter_totals_623.csv").exists() and \
       (DATA / "submitter_totals_623.csv").stat().st_size > 0:
        build_volume_figure()
    else:
        print("submitter_totals_623.csv not ready, skipping volume figure")

    if (DATA / "submitter_decomp_623.csv").exists() and \
       (DATA / "submitter_decomp_623.csv").stat().st_size > 0:
        build_population_figure()
        build_fee_decomp_figure()
    else:
        print("submitter_decomp_623.csv not ready, skipping decomposition figures")
