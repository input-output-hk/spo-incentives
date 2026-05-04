#!/usr/bin/env python3
"""Build §6 submitter figures from definitive epoch 627 data (Instance B, full).

Reads:
  data/submitter_totals_627.csv        — per-epoch unique submitters, tx count, fee
  data/submitter_decomp_627.csv        — per-epoch × addr_type decomposition
  data/fee_concentration_627.csv       — fee tier buckets (ep 622–627)
  data/tx_type_composition_627.csv     — per-epoch script/simple tx split
  data/submitter_staking_overlap_627.csv — top-500 fee payers x delegation status

Generates:
  figures/submitter_volume_627.png        — tx volume + unique submitters timeline
  figures/submitter_population_627.png    — addr-type decomposition stacked area
  figures/submitter_fee_decomp_627.png    — fee share by addr type over time
  figures/submitter_staking_overlap_627.png — top-500 fee payers staking status
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
    with (DATA / "submitter_totals_627.csv").open(newline="") as f:
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
    ax1.set_title("Transaction Volume and Submitter Population — Epochs 208–627",
                  fontsize=12, fontweight="medium", color=INK, pad=12)
    ax1.legend(fontsize=8, loc="upper left")

    ax2.fill_between(epochs, 0, fee, alpha=0.5, color=DAWN)
    ax2.set_ylabel("Fee (K ADA)", fontsize=9, color=DIM)
    ax2.set_xlabel("Epoch", fontsize=9, color=DIM)

    fig.tight_layout()
    out = FIG / "submitter_volume_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_population_figure():
    """Figure 2: submitter addr-type decomposition stacked area."""
    raw = defaultdict(dict)
    with (DATA / "submitter_decomp_627.csv").open(newline="") as f:
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
    ax.set_title("Submitter Population by Address Type — Epochs 208–627",
                 fontsize=12, fontweight="medium", color=INK, pad=12)
    ax.legend(fontsize=7, loc="upper right", ncol=2)

    fig.tight_layout()
    out = FIG / "submitter_population_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_fee_decomp_figure():
    """Figure 3: fee share by addr type stacked area."""
    raw = defaultdict(dict)
    with (DATA / "submitter_decomp_627.csv").open(newline="") as f:
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
    ax.set_title("Fee Revenue Share by Submitter Address Type — Epochs 208–627",
                 fontsize=12, fontweight="medium", color=INK, pad=12)
    ax.legend(fontsize=7, loc="upper right", ncol=2)

    fig.tight_layout()
    out = FIG / "submitter_fee_decomp_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_tx_type_composition_figure():
    """Figure 5: tx_type composition (script vs simple) over Shelley era."""
    rows = []
    with (DATA / "tx_type_composition_627.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    epochs = [int(r["epoch_no"]) for r in rows]
    total  = [int(r["total_tx"]) / 1e3 for r in rows]
    script = [int(r["script_tx"]) / 1e3 for r in rows]
    simple = [int(r["simple_tx"]) / 1e3 for r in rows]
    script_pct  = [float(r["script_pct"])      for r in rows]
    fee_pct     = [float(r["script_fee_pct"])  for r in rows]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), facecolor=BG,
                                    sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for ax in [ax1, ax2]:
        style_ax(ax)

    ax1.fill_between(epochs, 0, simple, color=COBALT, alpha=0.5, label="Simple tx (K)")
    ax1.fill_between(epochs, simple,
                     [s + sc for s, sc in zip(simple, script)],
                     color=INFARED, alpha=0.6, label="Script tx (K)")
    ax1.set_ylabel("Transactions per epoch (K)", fontsize=9, color=DIM)
    ax1.set_title("Transaction Composition — Script vs Simple — Epochs 208–627",
                  fontsize=12, fontweight="medium", color=INK, pad=12)
    for ep_hf, lbl in [(208, "Shelley"), (290, "Alonzo"), (508, "Conway")]:
        ax1.axvline(x=ep_hf, color=DIM, linestyle=":", linewidth=0.7, alpha=0.6)
        ax1.text(ep_hf, ax1.get_ylim()[1] * 0.92, lbl,
                 fontsize=8, color=DIM, ha="left", rotation=0)
    ax1.legend(fontsize=8, loc="upper left")

    ax2.plot(epochs, script_pct, color=COBALT, lw=1.5, label="Script share of tx count (%)")
    ax2.plot(epochs, fee_pct,    color=INFARED, lw=1.5, label="Script share of fee revenue (%)")
    ax2.set_ylabel("Share (%)", fontsize=9, color=DIM)
    ax2.set_xlabel("Epoch", fontsize=9, color=DIM)
    ax2.legend(fontsize=8, loc="upper right")

    fig.tight_layout()
    out = FIG / "tx_type_composition_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_fee_concentration_figure():
    """Figure 6: fee concentration in the recent window 622-627."""
    rows = []
    with (DATA / "fee_concentration_627.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    BUCKET_LABELS = {
        "top_10":      "Top 10",
        "top_11_50":   "Top 11–50",
        "top_51_100":  "Top 51–100",
        "top_101_500": "Top 101–500",
        "rest":        "Rest",
    }
    BUCKET_ORDER = ["top_10", "top_11_50", "top_51_100", "top_101_500", "rest"]
    BUCKET_COLOURS = [INFARED, DAWN, SOLAR, COBALT, GREY]

    by_bucket = {r["bucket"]: r for r in rows}
    pcts = [float(by_bucket[b]["fee_pct"]) for b in BUCKET_ORDER]
    n_addrs = [int(by_bucket[b]["n_addresses"]) for b in BUCKET_ORDER]
    tx_counts = [int(by_bucket[b]["tx_count"]) for b in BUCKET_ORDER]

    cumulative = []
    s = 0
    for p in pcts:
        s += p
        cumulative.append(s)

    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=BG)
    style_ax(ax)

    bars = ax.bar(range(len(BUCKET_ORDER)), pcts,
                   color=BUCKET_COLOURS, alpha=0.85,
                   edgecolor="white", linewidth=0.6)
    ax.set_xticks(range(len(BUCKET_ORDER)))
    ax.set_xticklabels(
        [f"{BUCKET_LABELS[b]}\n({n_addrs[i]:,} addrs · {tx_counts[i]:,} tx)"
         for i, b in enumerate(BUCKET_ORDER)],
        fontsize=9, color=INK)
    ax.set_ylabel("Share of fee revenue (%)", fontsize=9, color=DIM)
    ax.set_title("Fee Revenue Concentration — Recent Window (Epochs 622–627, Instance B)",
                 fontsize=12, fontweight="medium", color=INK, pad=12)

    for i, (bar, p, c) in enumerate(zip(bars, pcts, cumulative)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6,
                f"{p:.1f}%", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=INK)
        if i < len(BUCKET_ORDER) - 1:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3.2,
                    f"cum {c:.0f}%", ha="center", va="bottom",
                    fontsize=8, color=DIM)

    fig.tight_layout()
    out = FIG / "fee_concentration_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


def build_staking_overlap_figure():
    """Figure 4: top-500 fee payers x staking status (epoch 627).

    Three groups (by staking_status), broken down by addr_type, shown as a
    stacked bar of fee revenue. Highlights the share of fee revenue that comes
    from currently-delegating addresses vs. has-cred-but-not-delegating vs.
    no-stake-credential.
    """
    rows = []
    with (DATA / "submitter_staking_overlap_627.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    STATUS_ORDER = ["delegating", "has_cred_not_delegating", "no_stake_cred"]
    STATUS_LABELS = {
        "delegating":              "Delegating at epoch 627",
        "has_cred_not_delegating": "Has stake credential, NOT delegating",
        "no_stake_cred":           "No stake credential (enterprise / legacy)",
    }
    STATUS_COLOURS = {
        "delegating":              ACID,    # acid green = participating
        "has_cred_not_delegating": SOLAR,   # amber = capable but inactive
        "no_stake_cred":           INFARED, # red = structurally excluded
    }

    # Aggregate top500 fees by status
    by_status = {s: 0.0 for s in STATUS_ORDER}
    by_status_n = {s: 0 for s in STATUS_ORDER}
    for r in rows:
        s = r["staking_status"]
        by_status[s] += float(r["top500_fee_ada"])
        by_status_n[s] += int(r["top500_n"])

    # Also aggregate full population for comparison
    by_status_full = {s: 0.0 for s in STATUS_ORDER}
    by_status_full_n = {s: 0 for s in STATUS_ORDER}
    for r in rows:
        s = r["staking_status"]
        by_status_full[s] += float(r["total_fee_ada"])
        by_status_full_n[s] += int(r["total_n"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), facecolor=BG)
    for ax in [ax1, ax2]:
        style_ax(ax)

    # Left: top-500 share of fees by status
    total_500 = sum(by_status.values())
    bottom = 0
    for s in STATUS_ORDER:
        v = by_status[s]
        pct = 100.0 * v / total_500 if total_500 else 0
        ax1.bar(["Top 500\nfee payers"], [v], bottom=[bottom],
                color=STATUS_COLOURS[s], alpha=0.85,
                label=f"{STATUS_LABELS[s]}  —  {by_status_n[s]} addrs · {pct:.1f}%")
        ax1.text(0, bottom + v / 2, f"{pct:.1f}%",
                 ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
        bottom += v
    ax1.set_ylabel("Cumulative fee revenue (ADA)", fontsize=9, color=DIM)
    ax1.set_title("Top-500 fee payers — staking status (ep 622–627)",
                  fontsize=11, color=INK, pad=10)
    ax1.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.30),
               frameon=False, ncol=1)

    # Right: full population share of fees by status
    total_all = sum(by_status_full.values())
    bottom = 0
    for s in STATUS_ORDER:
        v = by_status_full[s]
        pct = 100.0 * v / total_all if total_all else 0
        ax2.bar(["All submitters"], [v], bottom=[bottom],
                color=STATUS_COLOURS[s], alpha=0.85,
                label=f"{STATUS_LABELS[s]}  —  {by_status_full_n[s]:,} addrs · {pct:.1f}%")
        ax2.text(0, bottom + v / 2, f"{pct:.1f}%",
                 ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
        bottom += v
    ax2.set_ylabel("Cumulative fee revenue (ADA)", fontsize=9, color=DIM)
    ax2.set_title("All fee payers — staking status (ep 622–627)",
                  fontsize=11, color=INK, pad=10)
    ax2.legend(fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.30),
               frameon=False, ncol=1)

    fig.suptitle(
        "Who pays fees, and do they delegate? — Instance B, epoch 627 stake snapshot",
        fontsize=12, fontweight="medium", color=INK, y=1.02)
    fig.tight_layout()
    out = FIG / "submitter_staking_overlap_627.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved -> {out}")


if __name__ == "__main__":
    if (DATA / "submitter_totals_627.csv").exists() and \
       (DATA / "submitter_totals_627.csv").stat().st_size > 0:
        build_volume_figure()
    else:
        print("submitter_totals_627.csv not ready, skipping volume figure")

    if (DATA / "submitter_decomp_627.csv").exists() and \
       (DATA / "submitter_decomp_627.csv").stat().st_size > 0:
        build_population_figure()
        build_fee_decomp_figure()
    else:
        print("submitter_decomp_627.csv not ready, skipping decomposition figures")

    if (DATA / "tx_type_composition_627.csv").exists() and \
       (DATA / "tx_type_composition_627.csv").stat().st_size > 0:
        build_tx_type_composition_figure()
    else:
        print("tx_type_composition_627.csv not ready, skipping tx_type figure")

    if (DATA / "fee_concentration_627.csv").exists() and \
       (DATA / "fee_concentration_627.csv").stat().st_size > 0:
        build_fee_concentration_figure()
    else:
        print("fee_concentration_627.csv not ready, skipping fee_concentration figure")

    if (DATA / "submitter_staking_overlap_627.csv").exists() and \
       (DATA / "submitter_staking_overlap_627.csv").stat().st_size > 0:
        build_staking_overlap_figure()
    else:
        print("submitter_staking_overlap_627.csv not ready, skipping overlap figure")
