# `k` parameter — Target-pool count as a standalone lever

> **Status:** Active 2026/04/22. Transversal parameter (no dedicated CIP). Evaluation against V2 §2 grid. Sources in §7.

## TL;DR

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

## 3. Simulation plan

| Axis | Setting |
| --- | --- |
| Initial state | Recent-epoch population snapshot — initialise with full MPO-fleet structure. Mechanism of interest is MPO response, not equilibrium pool count |
| Parameter sweep | `k ∈ {500, 650, 750, 1 000, 1 500, 2 000}` — 750/1 000 align with CIP-0082 stages 3–4; 2 000 stress-tests fleet-splitting |
| Scenarios | Stress / stable / appreciating ADA price (V2 §4.3) — sharpest interaction with fixed-fee floor at low ADA price |

**KPI focus.**

- **Viability rate across operator tiers** — binding constraint at high `k`.
- **HHI on entities** (not just pools) — catches the fleet-splitting response.
- **Independent-SPO share of productive stake** — core §3.1 cross-check.
- **Sub-threshold pool share** — does `k` expand or shrink the 116-pool subthreshold population?

**Populations to watch.**

| Population | Size | Why it matters |
| --- | --- | --- |
| Sub-threshold pools | 116 | Likely further suppressed by `k` rise |
| Viable independent single-pool operators | 283 | Tail at risk from per-pool revenue drop |
| MPO fleet entities | 85 | `k` raise expands delegation surface faster than current pledge mechanics tighten Sybil economics |

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
- **Simulator:** [`../../../Rewards-Sharing-Simulation-Engine/`](../../../Rewards-Sharing-Simulation-Engine/). **Mainnet inputs:** [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md), [`../diagnostic/sub-flows/pools-distribution/mainnet-analysis/`](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md).
