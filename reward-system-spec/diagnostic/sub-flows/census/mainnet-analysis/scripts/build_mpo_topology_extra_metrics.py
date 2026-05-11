"""Additional analytical layers on top of the topology pipeline.

  1. tau_sensitivity  -- adversarial-stake threshold (1 - tau) for tau in
                         {60, 70, 75, 80, 90}; for each tau, which scenarios
                         breach.
  2. mpo_vs_spo       -- per-provider concentration split into MPO-only and
                         single-pool-operator-only views.
  3. hhi              -- Herfindahl-Hirschman Index for provider, region,
                         physical-country distributions, plus the
                         effective-number-of-domains (exp of Shannon entropy).

Outputs (under data/):
  mpo_topology_tau_sensitivity.csv
  mpo_topology_mpo_vs_spo.csv
  mpo_topology_concentration_index.csv
"""
from __future__ import annotations
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ENDPOINTS = DATA / "mpo_relay_endpoints_resolved.csv"
SCENARIOS = DATA / "mpo_topology_failure_scenarios.csv"

OUT_TAU = DATA / "mpo_topology_tau_sensitivity.csv"
OUT_MPO_SPO = DATA / "mpo_topology_mpo_vs_spo.csv"
OUT_HHI = DATA / "mpo_topology_concentration_index.csv"


def load_endpoints() -> list:
    return list(csv.DictReader(open(ENDPOINTS)))


def load_scenarios() -> list:
    return list(csv.DictReader(open(SCENARIOS)))


# 1. tau-sensitivity ---------------------------------------------------------

def tau_sensitivity() -> None:
    """For each tau, derive the adversarial-stake threshold and flag which
    scenarios breach. Per CIP-0164 security note, a 26% stake attacker
    "trivially" attacks a 75% tau, i.e. the adversarial threshold is 1 - tau
    plus a one-vote margin. We use (1 - tau) * 100 + 1 as a defensible
    rounded threshold, capped at 0."""
    scenarios = load_scenarios()
    tau_values = [60, 70, 75, 80, 90]
    with OUT_TAU.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["tau_pct", "adversarial_threshold_pct"]
            + [s["scenario_id"] for s in scenarios]
        )
        for tau in tau_values:
            # adversarial threshold: smallest stake fraction that prevents tau
            # from being reached. With a perfectly stake-weighted committee
            # and binary participation, this is simply 100 - tau.
            adv = 100 - tau
            row = [tau, adv]
            for sc in scenarios:
                pct = float(sc["stake_at_risk_pct"])
                breach = "BREACH" if pct >= adv else f"+{adv - pct:.2f}"
                row.append(breach)
            w.writerow(row)
    print(f"wrote {OUT_TAU.relative_to(ROOT)}")
    # also print compact summary
    print(f"\n{'scenario':40s}  " + "  ".join(f"tau={t}" for t in tau_values))
    for sc in scenarios:
        pct = float(sc["stake_at_risk_pct"])
        cells = []
        for tau in tau_values:
            adv = 100 - tau
            cells.append("X    " if pct >= adv else f"+{adv-pct:5.1f}")
        print(f"  {sc['title'][:38]:38s}  " + "  ".join(cells))


# 2. mpo vs spo --------------------------------------------------------------

def mpo_vs_spo() -> None:
    rows = load_endpoints()
    # pool -> {category, providers, regions, stake}
    pool_stake = {}
    pool_cat = {}
    pool_provs = defaultdict(set)
    pool_regs = defaultdict(set)
    for r in rows:
        p = r["pool_id_bech32"]
        pool_stake[p] = float(r["current_active_stake_ada"] or 0)
        pool_cat[p] = "single_pool" if r["category"] == "single_pool" else "mpo"
        pool_provs[p].add(r["provider"])
        pool_regs[p].add(r["region"])

    def by_provider(cohort: str) -> tuple:
        agg = Counter()
        n_pools = Counter()
        ents_per: dict = defaultdict(set)
        total = 0.0
        for p, cat in pool_cat.items():
            if cat != cohort:
                continue
            s = pool_stake[p]
            total += s
            provs = pool_provs[p]
            if not provs:
                continue
            per = s / len(provs)
            for pr in provs:
                agg[pr] += per
                n_pools[pr] += 1
        return agg, n_pools, total

    mpo_agg, mpo_pools, mpo_total = by_provider("mpo")
    spo_agg, spo_pools, spo_total = by_provider("single_pool")
    all_providers = sorted(
        set(mpo_agg.keys()) | set(spo_agg.keys()),
        key=lambda k: -(mpo_agg.get(k, 0) + spo_agg.get(k, 0)),
    )
    with OUT_MPO_SPO.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "provider",
            "mpo_stake_ada", "mpo_pct_of_total", "mpo_pct_of_mpo_cohort",
            "spo_stake_ada", "spo_pct_of_total", "spo_pct_of_spo_cohort",
        ])
        grand = mpo_total + spo_total
        for prov in all_providers:
            m = mpo_agg.get(prov, 0)
            s = spo_agg.get(prov, 0)
            w.writerow([
                prov,
                int(m),
                f"{100*m/grand:.2f}" if grand else "0",
                f"{100*m/mpo_total:.2f}" if mpo_total else "0",
                int(s),
                f"{100*s/grand:.2f}" if grand else "0",
                f"{100*s/spo_total:.2f}" if spo_total else "0",
            ])
    print(f"wrote {OUT_MPO_SPO.relative_to(ROOT)}")
    print(f"\nMPO cohort:  {mpo_total/1e9:.2f}B ADA")
    print(f"SPO cohort:  {spo_total/1e9:.2f}B ADA")
    print(f"\n{'provider':25s} {'MPO %coh':>9s} {'SPO %coh':>9s}")
    for prov in all_providers[:12]:
        m_pct = 100 * mpo_agg.get(prov, 0) / mpo_total if mpo_total else 0
        s_pct = 100 * spo_agg.get(prov, 0) / spo_total if spo_total else 0
        print(f"  {prov:25s} {m_pct:>8.1f}% {s_pct:>8.1f}%")


# 3. HHI + effective-number-of-domains ---------------------------------------

def hhi_and_endn(values: list) -> tuple:
    """Returns (hhi, endn) where values is a list of stake shares (need not
    sum to 1). HHI is sum of squared shares times 10_000 (industrial standard
    scaling); ENDN = exp(Shannon entropy in nats) — the equivalent number of
    equally-weighted categories.
    """
    total = sum(values)
    if total <= 0:
        return (0.0, 0.0)
    shares = [v / total for v in values if v > 0]
    hhi = 10_000 * sum(s * s for s in shares)
    h = -sum(s * math.log(s) for s in shares)
    endn = math.exp(h)
    return (hhi, endn)


def hhi() -> None:
    rows = load_endpoints()
    stake = {r["pool_id_bech32"]: float(r["current_active_stake_ada"] or 0) for r in rows}
    # for each dimension, pool stake split across its distinct labels
    pool_keys: dict = {"provider": defaultdict(set),
                       "region": defaultdict(set),
                       "physical_country": defaultdict(set),
                       "tier": defaultdict(set)}
    for r in rows:
        for k in pool_keys:
            pool_keys[k][r["pool_id_bech32"]].add(r[k])
    out_rows = []
    for dim, mp in pool_keys.items():
        agg: dict = defaultdict(float)
        for p, keys in mp.items():
            if not keys:
                continue
            per = stake.get(p, 0) / len(keys)
            for k in keys:
                agg[k] += per
        hhi_v, endn = hhi_and_endn(list(agg.values()))
        # classification helpers
        if hhi_v < 1500:
            grade = "low concentration"
        elif hhi_v < 2500:
            grade = "moderate concentration"
        else:
            grade = "high concentration"
        out_rows.append({
            "dimension": dim,
            "n_distinct_labels": len(agg),
            "HHI": round(hhi_v, 1),
            "effective_n_domains": round(endn, 2),
            "concentration_grade": grade,
            "top1_share_pct": round(100 * max(agg.values()) / sum(agg.values()), 2)
            if agg else 0,
        })
    with OUT_HHI.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {OUT_HHI.relative_to(ROOT)}")
    print()
    for r in out_rows:
        print(f"  {r['dimension']:18s}  HHI={r['HHI']:>7.1f}  "
              f"endn={r['effective_n_domains']:>5.2f}  "
              f"top1={r['top1_share_pct']:>5.2f}%  ({r['concentration_grade']})")


def main() -> None:
    tau_sensitivity()
    print()
    mpo_vs_spo()
    print()
    hhi()


if __name__ == "__main__":
    main()
