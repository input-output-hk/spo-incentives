# `k` parameter — Target-pool count as a standalone lever

> **Status:** Active 2026/04/22. Transversal parameter (no dedicated CIP). Evaluation against V2 §2 grid. Sources in §7.

## Executive summary

- **Verdict.** Wrong first lever. A standalone `k` raise addresses *no* V2 milestone directly and actively regresses on §3.1 and potentially §3.4.
- **Ordering rule.** Belongs at **step 3** of a three-step sequence: fee-layer reform → stake-cap reform → `k` recalibration. Its embedding in CIP-0082 stages 3–4 respects this.
- **Historical warning.** CIP-0050 simulation shows Nakamoto coefficient *falls* 142 → 116 when sweeping `k` 1 000 → 2 000 in the current weak-pledge regime — fleet-splitting response dominates the gain.
- **Technical triviality.** Single-integer update via standard Parameter Change — maximum governability, but that does not make it a reform.

## 1. Mechanism

**Definition.** `k` is a scalar protocol parameter that sets two linked quantities:

$$\sigma_{\text{sat}} = \frac{1}{k} \qquad\text{and}\qquad \text{per-pool-at-sat revenue} \propto \frac{1}{k}$$

| Property | Value |
| --- | --- |
| Current value | `k = 500` |
| Current saturation | ≈ 67.44 M ADA per pool (supply ≈ 33.72 B ADA) |
| Layer | **Neither fee nor stake-cap** — reparameterises the underlying reward curve |
| Governance path | Standard Parameter Change action (Conway-era) |
| Structural reform | **No** — a reparameterisation, not a mechanism change |

**Intent (nominal).** Increase decentralisation by targeting a larger pool population.

**Why evaluated standalone.** Under active governance discussion *outside* the CIP-0082 package, even though V2 dependency-chain reasoning places it at the end of any coherent sequence. Its embedding inside CIP-0082 stages 3–4 is covered in [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md).

### 1.1 Historical and simulation record

From CIP-0050 motivation section, on sweeping `k` 250 → 2 000 at low $a_0 = 0.1$:

> *"The headline 'target pool' count grows, but the Nakamoto coefficient actually falls from about 142 at `k = 1 000` to just 116 at `k = 2 000`. The hypothesis is that pledge is too insignificant, which leads big operators to simply split their stake into even more zero-pledge pools."*

**Effect of a `k`-only move with current pledge mechanics:**

| Effect | Direction |
| --- | --- |
| Pool count (nominal decentralisation metric) | ↑ |
| Nakamoto coefficient (at weak $a_0$) | ↓ |
| Per-pool revenue at saturation | ↓ |
| Subscale-operator viability | ↓ |

This is the **exact pathology CIP-0050 (via $L$) and CIP-0037 (via dynamic saturation) are designed to foreclose before `k` is raised.**

## 2. Milestone coverage

| V2 milestone | Verdict | Why |
| --- | --- | --- |
| §3.1 Operator viability | **Negative** | Lower saturation → lower per-pool revenue → viability worsens, especially for subscale independent operators |
| §3.2 Pledge as signal | No effect | Pledge mechanics unchanged |
| §3.3 Delegator yield | Weakly negative | Per-pool yield dispersion widens; average delegator yield unchanged absent other reforms |
| §3.4 Concentration | **Pool-level yes, entity-level no** | Fragments saturated pools but does not constrain a single entity from operating more at ~500 ADA certificate cost each; empirically *reduces* Nakamoto in weak-pledge regimes |
| §4.1 Pot survival | No effect | Pot composition / reserve schedule unchanged |
| §4.2 Fee-gen population | No effect | — |
| §4.3 Price robustness | **Compounds sensitivity** | Lower per-pool budget interacts non-linearly with the fixed-fee floor; viability line shifts sharply with ADA price |
| §4.4 Governability | Trivial | Existing parameter; single-integer update |

**Dependency-chain note.** A `k` increase in isolation is a §3.4 move applied *before* §3.1 and §3.2 have been secured — exactly what V2 §5 flags as *building on a foundation that does not exist*.

## 3. Validation plan

The evaluation rests on the gate framework defined in [`methodology.md`](methodology.md). G1 (analytical properties) and G2 (mainnet counterfactual arithmetic) carry the verdict; G3 carries heavy weight here because the k:150→500 and k-sweep simulation records are the most informative evidence available.

### 3.1 G1 — Analytical properties (high trust)

Proved directly from the saturation-size identity $\sigma_{\text{sat}} = 1/k$:

| Property | Statement | Consequence |
| --- | --- | --- |
| Per-pool revenue at saturation | $\propto 1/k$ | A `k` raise lowers the viability line |
| Pool-count headline | Nominal target = $k$ | §3.4 pool-level metric rises mechanically |
| Entity-level decoupling | Pool count is not a function of entity count | §3.4 entity-level not addressed |
| Pledge-mechanics coupling | `k` does not change pledge-influence parameters | §3.1, §3.2 untouched structurally |
| Layer | Neither fee nor stake-cap | Composes with all other CIPs; never precedes them in a dependency chain |
| Governance surface | 1 integer parameter | Technically trivial — governance cost is not the same as mechanism quality |

G1 alone rules out a `k` raise as a standalone reform instrument: the parameter moves no V2 milestone structurally and lowers the viability line mechanically.

### 3.2 G2 — Mainnet snapshot counterfactual (high trust)

Arithmetic on the recent-epoch snapshot for an isolated `k: 500 → 1000` move, holding all other parameters fixed.

| Quantity | Pre (`k=500`) | Post (`k=1000`) | Immediate effect |
| --- | --- | --- | --- |
| Saturation per pool | ≈ 67.44 M ADA | ≈ 33.72 M ADA | Halved |
| Per-pool revenue at saturation | baseline | ≈ baseline / 2 | Viability line rises by ≈ 2× in pledge-at-sat |
| Sub-threshold pools | 116 | Strictly ≥ 116 | More pools cross the fixed-cost floor |
| Viable independent 1-pool operators | 283 | Strictly ≤ 283 | Bottom of the viable band pinched out |
| Fixed-fee regressivity | baseline | Worse | `minPoolCost` becomes a larger share of each pool's actual pot |
| MPO fleet-expansion headroom | current | +500 pool slots | New capacity fillable by fleet expansion at ~500 ADA registration cost per pool |

### 3.3 G3 — Historical analogies (medium–high trust, load-bearing here)

Unlike other CIPs, `k` has direct precedents:

| Analogue | Information content | Confidence |
| --- | --- | --- |
| `k: 150 → 500` (Cardano, Aug 2020) | Demonstrated that a `k` raise succeeds on the pool-count metric; did not address the emergent MPO fleet-splitting pattern that followed | High |
| CIP-0050 motivation's `k: 1 000 → 2 000` simulation | Reported Nakamoto coefficient **142 → 116** under low $a_0$; isolates the pathology to weak-pledge regimes | Medium — cited in CIP-0050, tagged G3 here rather than G6 because it establishes a qualitative sign |

The weak-pledge-regime sign is the load-bearing G3 claim: in the current regime, a standalone `k` raise regresses on the entity-level §3.4 metric it nominally serves.

### 3.4 G4 — Game-theoretic best responses (assumptions, not predictions)

Conditional on behaviour staying within the rational-yield assumption:

| Population | Assumed response to isolated `k` raise | Confidence |
| --- | --- | --- |
| MPO fleets with fixed pledge budget | Expand pool count to absorb the new reward slots; pledge per pool dilutes further | Medium-high — ~500 ADA registration cost is negligible vs delegation revenue |
| CEX / IVaaS with native pledge | Neutral — already at or above ceiling; entity-level share grows passively | Medium |
| Viable independent 1-pool operators | Per-pool revenue compression; attrition at the bottom of the viable band | Medium — depends on delegator response |
| Subthreshold pools | Pushed further below the fixed-cost floor | High — arithmetic from G2 |

### 3.5 G5 — Governance ramp and rollback

Production contract when `k` moves as a standalone action (outside the CIP-0082 embedding):

| Stage | `k` | Duration | Rollback trigger |
| --- | --- | --- | --- |
| 0 | 500 (status quo) | — | — |
| 1 | 750 | 10–20 epochs | Sub-threshold pool count grows, or MAV trends down |
| 2 | 1000 | 10–20 epochs | Independent-SPO share of productive stake falls |

**Ordering precondition.** Stages above are *only* coherent if a fee-layer instrument and a stake-cap instrument are active first. A standalone `k` raise without the preceding layers should not pass G5 — it is the pattern CIP-0050's motivation section documented as harmful.

### 3.6 G6 — Exploratory simulation (low trust, supplementary)

Simulator: Rewards-Sharing-Simulation-Engine (separate repository) — under active improvement 2026. Ablations to characterise — not to certify — are:

- `k ∈ {500, 650, 750, 1 000, 1 500, 2 000}` — recovery of the CIP-0050 motivation curve on the current snapshot.
- Joint `(k, L)` sweep — CIP-0050's claim that $L$ converts a `k` raise into a decentralisation lever.
- Joint `(k, e, \ell, p_{100\%})` sweep — CIP-0037's dependence on `orig_sat = supply / k`.
- Price interaction — viability-line shift at low, stable, appreciating ADA price.

None of these runs can by themselves reverse the G1 + G3 finding that a standalone `k` raise is the wrong first lever.

## 4. Transition and governance

| Aspect | Path / Risk |
| --- | --- |
| On-chain path | Standard Parameter Change governance action. Technically trivial |
| Social transition | Shocks existing pool revenue on day one, no compensating mechanism absent other reforms |
| Historical reference | The 150 → 500 move is the canonical case for `k` moving faster than pledge discipline |
| Staging (if outside CIP-0082) | Phased path `500 → 750 → 1 000`, not a single jump — allows epoch-level observation + governance checkpoint if Nakamoto trends down rather than up |

## 5. Interaction audit

### 5.1 Layer independence

`k` lives on **neither the fee layer nor the stake-cap layer** — it parameterises the underlying reward curve that both layers compose with. Every CIP in this folder composes with any `k` value.

### 5.2 Interaction with the fee layer

| Force | Direction |
| --- | --- |
| `k` increase → per-pool revenue at sat drops by ≈ $k_{\text{new}} / k_{\text{old}}$ | Viability line **falls** |
| Fee-layer reform (CIP-0023 margin floor, CIP-0082 fee-structure reform) | Viability line **rises** |

**Opposing forces.** Net effect must be simulated jointly. Correct order: secure the fee-layer instrument first, measure the resulting viability band, *then* apply a `k` move into it.

### 5.3 Interaction with the stake-cap layer

| Force | Direction |
| --- | --- |
| Pledge-linked saturation / leverage caps → raise Sybil cost per pool | ↑ |
| `k` increase → raises number of *reward slots* per unit of pledge | ↑ reward-slot inventory |

Joint behaviour depends on whether the stake-cap constraint binds before or after the new saturation threshold on the marginal MPO pool.

**CIP-0050 synergy argument:** once pledge discipline binds (via $L$), a `k` raise translates to *new operators* filling the new slots — existing MPOs cannot spread pledge thinner without losing revenue. Without $L$, the same `k` raise invites MPO fleet expansion.

### 5.4 Specific interaction with CIP-0037

CIP-0037's saturation formula uses `orig_sat = total_supply / k` as its reference scale. A `k` change *directly reshapes* the CIP-0037 saturation curve.

**Simultaneous `k` and CIP-0037 activation requires joint recalibration of $(e, \ell, p_{100\%})$** — the two parameters are not independent from a governance standpoint.

### 5.5 Ordering verdict

`k` is the wrong first lever when pledge discipline is weak and the viability line is unresolved. It belongs at the **end of the sequence** — revisited *after* §3.1 and §3.2 are secured, as a calibration tool once the pledge-response mechanism is working.

This matches:

- CIP-0082's embedding of `k` at stages 3–4, after the `minPoolCost` → `minPoolRate` fee reform at stages 1–2.
- CIP-0050's argument that $L$ converts a `k` raise from a concentration risk into a decentralisation lever.
- The consistent positioning of `k` across the active governance discussion as a late-stage calibration parameter, not a first-order reform instrument.

## 6. Gaps against V2

Standalone `k` movement addresses **no V2 milestone directly** and actively regresses on several.

**Role in a V2 package.** Calibration tool at **step 3** of a three-step sequence:

1. Fee-layer reform (CIP-0082 stages 1–2).
2. Stake-cap reform (CIP-0050 or CIP-0037).
3. `k` recalibration (CIP-0082 stages 3–4).

Not a standalone reform.

## 7. References

- **Reference doc:** <https://docs.cardano.org/about-cardano/learn/pledging-rewards>.
- **V2 grid:** [`README.md`](README.md) §2. **Diagnostic anchors:** [`../diagnostic/README.md`](../diagnostic/README.md) §1.2 O4/O5/O8, §1.2.4.1.1, §1.2.4.4.3.
- **Companion evaluations:** [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md), [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md).
- **Simulator:** Rewards-Sharing-Simulation-Engine (separate repository). **Mainnet inputs:** [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md), [`../diagnostic/sub-flows/pools-distribution/mainnet-analysis/`](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md).
