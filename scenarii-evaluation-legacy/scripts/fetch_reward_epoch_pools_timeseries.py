#!/usr/bin/env python3
"""
Fetch mainnet epoch-level data needed to graph Reward^{epoch}_{pools}.

Primary source: Koios REST API.
Endpoints used:
- /tip
- /epoch_info
- /totals
- /epoch_params
- /genesis

Outputs:
- scenarii-evaluation/data/reward_epoch_pools_mainnet.csv
- scenarii-evaluation/outputs/reward_epoch_pools_missing_data.md
"""

from __future__ import annotations

import csv
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


KOIOS_BASE = "https://api.koios.rest/api/v1"
SHELLEY_START_EPOCH = 208


def fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def lovelace_to_ada(val: str | int | None) -> float | None:
    if val is None:
        return None
    return int(val) / 1_000_000.0


def unix_to_iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "scenarii-evaluation" / "data"
    out_dir = root / "scenarii-evaluation" / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    tip = fetch_json(f"{KOIOS_BASE}/tip")[0]
    tip_epoch = int(tip["epoch_no"])
    genesis_rows = fetch_json(f"{KOIOS_BASE}/genesis")
    if not genesis_rows:
        raise RuntimeError("Koios /genesis returned no rows.")
    genesis = genesis_rows[0]
    active_slot_coeff = float(genesis["activeslotcoeff"])
    epoch_length_slots = float(genesis["epochlength"])
    expected_blocks_epoch = active_slot_coeff * epoch_length_slots

    epoch_info_rows = fetch_json(f"{KOIOS_BASE}/epoch_info")
    totals_rows = fetch_json(f"{KOIOS_BASE}/totals")
    epoch_params_rows = fetch_json(f"{KOIOS_BASE}/epoch_params")

    epoch_info_by_epoch: Dict[int, Dict[str, Any]] = {
        int(r["epoch_no"]): r for r in epoch_info_rows if int(r["epoch_no"]) >= SHELLEY_START_EPOCH
    }
    totals_by_epoch: Dict[int, Dict[str, Any]] = {
        int(r["epoch_no"]): r for r in totals_rows if int(r["epoch_no"]) >= SHELLEY_START_EPOCH
    }
    params_by_epoch: Dict[int, Dict[str, Any]] = {
        int(r["epoch_no"]): r for r in epoch_params_rows if int(r["epoch_no"]) >= SHELLEY_START_EPOCH
    }

    all_epochs = list(range(SHELLEY_START_EPOCH, tip_epoch + 1))
    rows_out: List[Dict[str, Any]] = []

    missing_total_rewards: List[int] = []
    missing_totals: List[int] = []
    missing_params: List[int] = []

    for epoch in all_epochs:
        ei = epoch_info_by_epoch.get(epoch)
        tt = totals_by_epoch.get(epoch)
        ep = params_by_epoch.get(epoch)

        total_rewards_ll = None if ei is None else ei.get("total_rewards")
        if total_rewards_ll is None:
            missing_total_rewards.append(epoch)
        if tt is None:
            missing_totals.append(epoch)
        if ep is None:
            missing_params.append(epoch)

        fees_ll = None
        if ei is not None and ei.get("fees") is not None:
            fees_ll = ei.get("fees")
        elif tt is not None:
            fees_ll = tt.get("fees")

        rows_out.append(
            {
                "epoch_no": epoch,
                "start_time_unix": None if ei is None else ei.get("start_time"),
                "start_time_utc": None if ei is None else unix_to_iso(ei.get("start_time")),
                "end_time_unix": None if ei is None else ei.get("end_time"),
                "end_time_utc": None if ei is None else unix_to_iso(ei.get("end_time")),
                "blk_count_epoch": None if ei is None else ei.get("blk_count"),
                "active_slot_coeff_mainnet": active_slot_coeff,
                "epoch_length_slots_mainnet": int(epoch_length_slots),
                "expected_blocks_epoch_mainnet": expected_blocks_epoch,
                "eta_mainnet_raw": None
                if ei is None or ei.get("blk_count") is None
                else (float(ei.get("blk_count")) / expected_blocks_epoch),
                "eta_mainnet_capped": None
                if ei is None or ei.get("blk_count") is None
                else min(float(ei.get("blk_count")) / expected_blocks_epoch, 1.0),
                "Reward_epoch_pools_lovelace": total_rewards_ll,
                "Reward_epoch_pools_ada": lovelace_to_ada(total_rewards_ll),
                "Fee_epoch_lovelace": fees_ll,
                "Fee_epoch_ada": lovelace_to_ada(fees_ll),
                "active_stake_lovelace": None if ei is None else ei.get("active_stake"),
                "active_stake_ada": None if ei is None else lovelace_to_ada(ei.get("active_stake")),
                "Reserve_lovelace": None if tt is None else tt.get("reserves"),
                "Reserve_ada": None if tt is None else lovelace_to_ada(tt.get("reserves")),
                "Supply_lovelace": None if tt is None else tt.get("supply"),
                "Supply_ada": None if tt is None else lovelace_to_ada(tt.get("supply")),
                "Treasury_lovelace": None if tt is None else tt.get("treasury"),
                "Treasury_ada": None if tt is None else lovelace_to_ada(tt.get("treasury")),
                "Deposit_stake_lovelace": None if tt is None else tt.get("deposits_stake"),
                "Deposit_drep_lovelace": None if tt is None else tt.get("deposits_drep"),
                "Deposit_proposal_lovelace": None if tt is None else tt.get("deposits_proposal"),
                "rho_monetary_expand_rate": None if ep is None else ep.get("monetary_expand_rate"),
                "tau_treasury_growth_rate": None if ep is None else ep.get("treasury_growth_rate"),
                "d_decentralisation": None if ep is None else ep.get("decentralisation"),
                "k_optimal_pool_count": None if ep is None else ep.get("optimal_pool_count"),
                "a0_influence": None if ep is None else ep.get("influence"),
                "has_total_rewards": total_rewards_ll is not None,
                "has_totals_row": tt is not None,
                "has_epoch_params": ep is not None,
            }
        )

    csv_path = data_dir / "reward_epoch_pools_mainnet.csv"
    fieldnames = list(rows_out[0].keys()) if rows_out else []
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    settled_epochs = [
        e for e in all_epochs if (e not in missing_total_rewards and e not in missing_totals and e not in missing_params)
    ]
    settled_min = min(settled_epochs) if settled_epochs else None
    settled_max = max(settled_epochs) if settled_epochs else None

    md_path = out_dir / "reward_epoch_pools_missing_data.md"
    md_lines = [
        "# Reward^epoch_pools Missing Data Audit (Mainnet)",
        "",
        f"- Source: Koios API (`{KOIOS_BASE}`)",
        f"- Tip epoch at fetch time: **{tip_epoch}**",
        f"- Target range: epochs **{SHELLEY_START_EPOCH}..{tip_epoch}**",
        "",
        "## Coverage",
        f"- Genesis constants: active slot coeff **{active_slot_coeff}**, epoch length **{int(epoch_length_slots)}** slots",
        f"- Derived expected blocks/epoch: **{expected_blocks_epoch:.0f}**",
        f"- `epoch_info` rows in range: **{len(epoch_info_by_epoch)}**",
        f"- `totals` rows in range: **{len(totals_by_epoch)}**",
        f"- `epoch_params` rows in range: **{len(params_by_epoch)}**",
        "",
        "## Missing fields for direct `Reward^epoch_pools` line",
        f"- Epochs with missing `total_rewards` in `epoch_info`: **{missing_total_rewards}**",
        f"- Epochs with missing `totals` row: **{missing_totals}**",
        f"- Epochs with missing `epoch_params` row: **{missing_params}**",
        "",
        "## Practically plottable contiguous window",
        f"- Fully populated epochs (all three sources): **{settled_min}..{settled_max}**",
        "",
        "## Notes",
        "- If the objective is only plotting `Reward^epoch_pools`, `epoch_info.total_rewards` is sufficient.",
        "- If the objective is decomposition (fees / reserves / treasury / parameter overlays), all three sources are needed.",
    ]
    md_path.write_text("\n".join(md_lines) + "\n")

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {md_path}")
    print(f"Missing total_rewards epochs: {missing_total_rewards}")
    print(f"Missing totals epochs: {missing_totals}")
    print(f"Missing epoch_params epochs: {missing_params}")


if __name__ == "__main__":
    main()
