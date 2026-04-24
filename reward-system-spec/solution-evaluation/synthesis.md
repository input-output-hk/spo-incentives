# Synthesis — Cross-CIP comparison and recommended package

> **Status:** Active 2026/04/22. Orthogonal read across the four active CIPs and the `k` parameter lever. Anchored on V2 §2 grid and the house recommendation package (links in §8).

## Executive summary

- **Do.** Activate fee-layer reform first (CIP-0082 stages 1–2, or CIP-0023 as conservative fallback), then the stake-cap layer (CIP-0050 default; CIP-0037 as the calibrated-curve alternative), then `k` raises under observation gates.
- **Don't.** Run `k` as a first lever; stack CIP-0050 and CIP-0037; stack CIP-0023 and CIP-0082 stage 2; or expect this bundle to close V2 §4.1 and §4.2 — it doesn't.
- **Open design choices.** (a) Fee layer — margin floor (CIP-0023) vs rate floor (CIP-0082 stage 2). (b) Stake-cap layer — hard cap (CIP-0050) vs smooth curve (CIP-0037).
- **Blind spots in the current bundle.** Staking-pot survival after reserve depletion (§4.1), transaction-submitter economics (§4.2), and custodial-operator concentration (§3.4 at entity level).

## 1. Coverage matrix

Rows = V2 milestones (dependency order §3.1 → §3.2 → §3.3 → §3.4 → transversal §4). Columns = active candidates. Symbols: **●** directly addressed, **○** partial / indirect, **·** neutral, **▼** regresses in the weak-pledge regime.

| V2 milestone | CIP-0023 | CIP-0082 | CIP-0050 | CIP-0037 | `k` alone |
| --- | :---: | :---: | :---: | :---: | :---: |
| §3.1 Operator viability | ● | ● | ○ | ○ | ▼ |
| §3.2 Pledge as signal | · | · | ● | ● | · |
| §3.3 Delegator yield | ● | ● | ○ | ○ | ○ |
| §3.4 Concentration | · | ○ | ● | ● | ▼ |
| §4.1 Pot survival | · | · | · | · | · |
| §4.2 Fee-gen population | · | · | · | · | · |
| §4.3 Price robustness | ● (stage 2) | ● (stage 2) | ○ | ○ | ▼ |
| §4.4 Governability | ● | ○ | ● | ● | ● |

**Headline.** Every row under §4.1–§4.2 is a blank column — the bundle does not touch pot composition or transaction-submitter economics. Fee-layer CIPs carry §3.1 / §3.3; stake-cap CIPs carry §3.2 / §3.4; `k` alone only regresses.

### 1.1 Gaps the bundle does not close

| Gap | Why the bundle misses it | Where the instrument lives |
| --- | --- | --- |
| §4.1 Staking-pot survival | All four CIPs are reparameterisations of the *pre*-depletion pipeline; none alters pot composition or reserve draw | Out of scope — requires a separate pot-redesign workstream |
| §4.2 Fee-generating population | No candidate addresses transaction-submitter economics (V2 §2.2) | Out of scope — long-run replacement for reserve draw |
| Custodial concentration (§3.4, entity level) | Levers act through pool-level economics; custodial stake aggregation is off-protocol | Pooling / CPD primitives (CIP-0161, CPS-0021 CPD) or governance disclosure |

## 2. Two open design choices

Both pairs of CIPs rewrite the same equation. Each pair requires an explicit precedence rule — **alternatives, not a stack.**

### 2.1 Fee layer — margin floor (CIP-0023) vs rate floor (CIP-0082 stage 2)

| Property | CIP-0023 (`minPoolMargin`) | CIP-0082 stage 2 (`minPoolRate`) |
| --- | --- | --- |
| Instrument type | Additive floor on the variable fee | Proportional floor replacing `minPoolCost` |
| `minPoolCost` status | Untouched | Removed |
| Governance path | Parameter change, no hard fork | Hard fork + ledger-rule change |
| Initial shock | Zero (initial value 0) | Viability point collapses to 1 ADA |
| Coordination cost | Low | High |
| Standalone completeness | Needs separate `minPoolCost` reduction to bite | Complete in one step |

**Composition rule.** CIP-0023 is a *safe first step* toward CIP-0082 stage 2, not a terminal design. If CIP-0082 stage 2 ships, CIP-0023 is redundant. If only CIP-0023 ships, a separate `minPoolCost` parameter-change action is needed to obtain the same viability effect.

### 2.2 Stake-cap layer — hard cap (CIP-0050) vs smooth curve (CIP-0037)

| Property | CIP-0050 (`L`) | CIP-0037 (dynamic saturation) |
| --- | --- | --- |
| Formula | $\sigma' = \min(\sigma,\ 1/k,\ L\cdot p)$ | $\text{sat}(p) = \text{orig\_sat} \cdot \max(e,\ \min(1/k,\ p/\text{orig\_sat}\cdot \ell))$ |
| Zero-pledge rewards | 0 (hard break) | $e \cdot \text{orig\_sat}$ (20 % of K at reference params) |
| Pool-splitting economics | Neutralised (summed cap = single-pool cap) | Partially neutralised at low pledge, fully at high pledge |
| New parameters | 1 ($L$) | 3 ($e$, $\ell$, $p_{100\%}$) |
| Governance surface | Narrow, low calibration error | Wide, more calibration error |
| Simulation headline | Nakamoto ≈ 160 at $L = 100$ | Anchor-calibration-dependent |

**Composition rule.** Joint activation double-caps $\sigma'$; there is no meaningful stack. Pick one. CIP-0050 maximises sharpness and anti-Sybil pressure; CIP-0037 preserves a reward floor and adds three governance knobs for future calibration. A detailed joint-composition analysis is maintained as a separate working document.

## 3. Cross-layer composition

Cross-layer pairings (one fee-layer + one stake-cap-layer) compose cleanly. Four options:

| Fee layer | Stake-cap layer | Profile |
| --- | --- | --- |
| CIP-0023 | CIP-0050 | Conservative pair: single new parameter on each layer. Lowest coordination cost. |
| CIP-0023 | CIP-0037 | Conservative fee + calibrated saturation. Three knobs retained on the stake-cap. |
| CIP-0082 | CIP-0050 | **House recommendation.** Strong fee reform + hard leverage cap. |
| CIP-0082 | CIP-0037 | Strong fee reform + calibrated saturation. Requires joint recalibration if `k` stages 3–4 activate. |

### 3.1 Interaction edges

- **Viability ↔ eligibility.** Fee reform *raises* the viability line; stake-cap reform *lowers* reward-eligible stake for under-pledged pools. Order: fee first (widen the band), stake-cap second (filter within the widened band).
- **`k` interaction.** Both stake-cap CIPs reference $1/k$ inside their formula. A `k` raise applied *before* the stake-cap reform invites MPO fleet expansion (the documented 2020 `k: 150 → 500` pattern; CIP-0050's motivation cites a weak-pledge `k: 1000 → 2000` sweep showing a notable Nakamoto-coefficient regression). Applied *after*, the same raise translates into new-operator entry. Sequencing `k` last is the headline argument.

## 4. Recommended package

### 4.1 Sequencing principle (V2 dependency chain)

1. **§3.1 Viability** — fee layer first. Acts without altering the pool-count landscape.
2. **§3.2 Pledge as signal** — stake-cap layer second. Pledge discipline is a property of eligible stake, not fee split.
3. **§3.4 Concentration recalibration** — `k` last. Calibration tool once pledge discipline binds, not a first-order reform.

### 4.2 Step-by-step plan

| Step | Action | Technical path | Targets |
| :---: | --- | --- | --- |
| 1 | CIP-0082 stage 1 — halve `minPoolCost` to 170 ADA | Parameter update | §3.1, §3.3 |
| 2 | CIP-0082 stage 2 — replace `minPoolCost` with `minPoolRate = 3 %` | Hard fork + ledger rule | §3.1, §3.3 |
| 3 | CIP-0050 — activate `L` (recommended band: $L \in [10, 100]$) | Parameter update + ledger rule | §3.2, §3.4 |
| 4 | Observation window ≥ 6 months | Measure Nakamoto trend, sub-threshold share, MPO response | — |
| 5 | `k` raise — CIP-0082 stage 3 (`k = 750`) | Parameter update, gated | §3.4 |
| 6 | `k` raise — CIP-0082 stage 4 (`k = 1000`) | Parameter update, gated | §3.4 |

**Alternatives inside the sequence.**

| Substitution | When | Effect |
| --- | --- | --- |
| CIP-0023 in place of CIP-0082 stages 1–2 | Governance declines the hard fork | Weaker viability effect; need separate `minPoolCost` reduction to approximate stage 2 |
| CIP-0037 in place of CIP-0050 at step 3 | Governance prefers calibrated curve over hard cap | Retains 20 % reward floor at zero pledge; three post-activation knobs |

**Preconditions for `k` raises (steps 5–6).**

- No deterioration in entity-level decentralisation metrics.
- Improvement in struggling-pool viability metrics.
- No new pool-splitting pathology bypassing `L` / pledge discipline.

## 5. Mapping to the three governance philosophies

| Philosophy | Compatible subsequence | V2 dependency chain |
| --- | --- | --- |
| Stability-first incrementalism | Step 1 only (CIP-0023) | Respected — defers §3.2 |
| Viability-first egalitarianism (**house position**) | Steps 1–3, CIP-0050 at step 3 | Respected |
| Security-first skin-in-the-game | Step 3 first, then 1–2 | Violated — collapses the viability band before widening it |

## 6. Validation cross-checks

Non-optional before any go/no-go at any step. Each step must be re-quantified on the canonical anchors before it ships.

| Check | Minimum readout |
| --- | --- |
| Analytical property holds at new parameters | Monotonicity / price-coupling / governance-surface count re-derived from the formula |
| Mainnet counterfactual on canonical taxonomy | Pool-axis effect across the 9-tier taxonomy ([pools-distribution §4.1.3](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions)); operator-axis effect across n-MPO brackets ([operator-delegator §4.4](../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#44-operator-profitability-versus-delegator-return)); entity-level HHI, sub-threshold pool share, independent-SPO share vs initial state |
| Historical reference check | `k: 150→500` or CIP-0050 k-sweep record contradicts the step? If so, treat as rollback trigger |
| Per-population response assumptions made explicit | Best-response table for MPO / CEX / small-op / delegator populations, labelled assumption-not-prediction |
| Production ramp | ≥ 10 epochs observation between stages; rollback triggers active; ≥ 6 months between stake-cap activation and first `k` raise; ≥ 3 months between `k` raises |
| Gap readout | §4.1 (pot survival) and §4.2 (fee-gen) not closed by any step — separate workstream required |

## 7. Bottom line

The active bundle is a **partial but coherent redesign of the pre-depletion reward pipeline**. It fixes the fee-layer regressivity (CIP-0023 / CIP-0082) and re-weaponises pledge (CIP-0050 / CIP-0037). It does not close the long-run gaps under V2 §4. Within its scope, the V2 dependency chain pins a single canonical ordering: fee → stake-cap → `k`. Every alternative sequence is either a conservative subsequence of this path or an explicit philosophy choice that accepts a documented dependency-chain violation.

## 8. References

**Per-candidate evaluations (this folder).**

- Fee layer — [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md).
- Stake-cap layer — [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md).
- Transversal `k` lever (filed under fee layer since the standalone analysis holds the pool-distribution formula fixed) — [`operator-delegator/k-parameter.md`](operator-delegator/k-parameter.md).
- Candidate index and method — [`README.md`](README.md).

**Canonical CIP sources.**

| CIP | Official | PRs |
| --- | --- | --- |
| CIP-0023 | [cips.cardano.org/cip/CIP-0023](https://cips.cardano.org/cip/CIP-0023) | [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| CIP-0037 | [cips.cardano.org/cip/CIP-0037](https://cips.cardano.org/cip/CIP-0037) | [#163](https://github.com/cardano-foundation/CIPs/pull/163) |
| CIP-0050 | [cips.cardano.org/cip/CIP-0050](https://cips.cardano.org/cip/CIP-0050) | [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| CIP-0082 | [cips.cardano.org/cip/CIP-0082](https://cips.cardano.org/cip/CIP-0082) | — |
| `k` / `stakePoolTargetNum` | [pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards) | — |

**Workspace references.**

- V2 spec — [`../README.md`](../README.md). Diagnostic — [`../diagnostic/README.md`](../diagnostic/README.md). Mainnet census — [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md).
- Governance package — referenced from a companion repository.
- Simulator — Rewards-Sharing-Simulation-Engine (separate repository).
- Joint-composition analysis (CIP-0050 vs CIP-0037) — maintained as a separate working document.

**Constraints.** All recommendations respect the [Cardano Constitution](https://github.com/IntersectMBO/cardano-constitution/tree/main/cardano-constitution-2). Python 3.9 compatibility is preserved in simulation work. Dates use `YYYY/MM/DD`.
