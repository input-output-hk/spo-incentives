# Solution Evaluation — Candidate CIPs Against V2

> **Status:** Active 2026/04/22. Working area for evaluating active CIPs and parameter-level proposals against the V2 specification. Sources in §6.

## TL;DR

- **Purpose.** Evaluate each candidate CIP against the V2 milestones on its own merits, then check how candidates combine: two CIPs on the *same* layer (fee or stake-cap) compete — pick one; a fee-layer CIP plus a stake-cap CIP compose cleanly.
- **Core question.** *Given the V2 milestones and their dependency chain, what does this proposal actually deliver, and what does it leave unresolved or worsen?*
- **Validation framework.** Each per-CIP §3 rests on a six-gate framework separating analytical facts from predictive claims. Verdicts require G1 (analytical properties) + G2 (mainnet counterfactual arithmetic); simulation is G6 — supplementary, never load-bearing. Full specification in [`methodology.md`](methodology.md).
- **Folder layout.** Two independent layers of the reward pipeline — fee layer in [`operator-delegator/`](operator-delegator/README.md), stake-cap layer in [`pools-distribution/`](pools-distribution/README.md) — plus transversal protocol parameters at root.
- **Synthesis.** Cross-CIP comparison and recommended package: [`synthesis.md`](synthesis.md).

## 1. Evaluation grid

Every candidate is assessed along five axes. The first four are lifted from V2 §5; the fifth is a pre-step aligning the candidate's stated intent with the V2 problem map.

### 1.1 Milestone coverage

| V2 milestone | Design instrument | Diagnostic anchor |
| --- | --- | --- |
| §3.1 Operator viability | Production threshold, per-pool profitability | [§1.2 O5, §1.3 O1](../diagnostic/README.md) |
| §3.2 Pledge as signal | Skin-in-the-game curve, pledge-linked saturation | [§1.2 O6](../diagnostic/README.md#122-mainnet-observations) |
| §3.3 Delegator yield | Fee structure, delegator differentiation | [§1.3](../diagnostic/README.md#13-operator-delegator-distribution) |
| §3.4 Concentration | Entity-level accounting, anti-Sybil mechanics | [§1.2 O4, §1.2.4.4.3](../diagnostic/README.md) |
| §4.1 Pot survival | Reserve independence, pot composition | — |
| §4.2 Fee-gen population | Transaction-submitter economics | — |
| §4.3 Price robustness | Parameter stability across price scenarios | — |
| §4.4 Governability | On-chain parameter surface, review triggers | — |

**Dependency order is enforced.** A candidate targeting §3.4 without first satisfying §3.1, §3.2, §3.3 is flagged as *building on a foundation that does not exist*.

### 1.2 Validation

The validation of each candidate follows the six-gate framework defined in [`methodology.md`](methodology.md). Summary of gate purposes and trust levels:

| Gate | Purpose | Trust | Role in verdict |
| --- | --- | --- | --- |
| G1 — Analytical properties | Theorems derived from the formula itself | High | Required |
| G2 — Mainnet snapshot counterfactual | Arithmetic on a recent-epoch snapshot at fixed behaviour | High | Required |
| G3 — Historical analogies | Prior parameter moves (e.g., `k: 150 → 500`) | Medium | Supporting |
| G4 — Game-theoretic best responses | Per-population reasoning, assumptions labelled as such | Medium-low | Supporting |
| G5 — Governance ramp and rollback | Production contract: stages, triggers, reversibility | — | Required for deployment |
| G6 — Exploratory simulation | Scenario ablations | Low | Never load-bearing |

**Inputs to G2.** Actual population structure at a recent epoch (not a clean-slate $k$-pool equilibrium), from [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md) and [`../diagnostic/sub-flows/pools-distribution/mainnet-analysis/`](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md). Price-scenario coverage (stress, stable, appreciating) per V2 §4.3.

**G6 simulator.** [`../../../simulator/`](../../../simulator/) — under active improvement 2026. Supplementary only.

### 1.3 Transition path from V1

Migration mechanics: which parameters change, in what sequence, with what governance approvals, over what time horizon. A mechanism optimal in steady state but unreachable from the current state is not a solution.

### 1.4 Interaction audit — two-layer decomposition

| Layer | What it modifies | Where | Instruments |
| --- | --- | --- | --- |
| **Fee layer** | Operator/member split after per-pool allocation | [`operator-delegator/`](operator-delegator/README.md) | CIP-0023 (`minPoolMargin`), CIP-0082 stages 1–2 (`minPoolCost` → `minPoolRate`) |
| **Stake-cap layer** | Reward-eligible stake $\sigma'$ entering the reward curve | [`pools-distribution/`](pools-distribution/README.md) | CIP-0050 (`L`), CIP-0037 (dynamic saturation) |
| **Transversal** | Underlying reward curve both layers compose with | [`k-parameter.md`](k-parameter.md) | `k` (`stakePoolTargetNum`) — embedded in CIP-0082 stages 3–4 |

| Composition | Status |
| --- | --- |
| Cross-layer (fee + stake-cap) | **Clean** — no precedence rule required |
| Same-layer fee (CIP-0023 ⊕ CIP-0082) | **Not canonical** — pick one |
| Same-layer stake-cap (CIP-0050 ⊕ CIP-0037) | **Not canonical** — pick one |

### 1.5 Conway-era governance compatibility

Parameter changes must map to existing governance actions; structural changes must specify the CIP path. A design requiring off-chain coordination without on-chain enforcement is not a protocol-level solution. The proposed mechanism must embed its own review and recalibration triggers (V2 §4.4). Constitutional-tenet mapping follows V2 §2.

## 2. Candidate index

Initial scope: the bundle at the centre of the current governance discussion.

### 2.1 Fee layer — [`operator-delegator/`](operator-delegator/README.md)

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0023** — Fair Min Fees | `minPoolMargin` floor | §3.1, §3.3 | [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md) | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| **CIP-0082** — Improved Rewards Scheme Parameters | 4-stage: `minPoolCost` → `minPoolRate` + `k` increases | §3.1, §3.3, §3.4 | [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md) | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |

### 2.2 Stake-cap layer — [`pools-distribution/`](pools-distribution/README.md)

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0050** — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` | §3.2, §3.4 | [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md) | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| **CIP-0037** — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve | §3.2, §3.4 | [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md) | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

### 2.3 Transversal — global protocol parameter

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **`k` parameter** — target-pool count (standalone) | `stakePoolTargetNum` | §3.1, §3.4 | [`k-parameter.md`](k-parameter.md) | Protocol parameter — no dedicated CIP. [Pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards) |

### 2.4 Out of initial scope

Candidates that extend the design space beyond parameter changes (e.g., pooling/CPD paths along the lines of [`../../../Context/CIPs-repo/CIP-0161/`](../../../Context/CIPs-repo/CIP-0161/) or [`../../../Context/CIPs-repo/CPS-0021/CPD/`](../../../Context/CIPs-repo/CPS-0021/CPD/)) sit naturally under the same framework, to be evaluated in a later iteration.

## 3. Method

Each per-CIP file follows a five-section structure mirroring §1:

| § | Section | Content |
| --- | --- | --- |
| 1 | Mechanism | Canonical formulation, author's stated objective, exact parameter surface |
| 2 | Milestone coverage | V2 milestones addressed, with diagnostic evidence where the instrument bites |
| 3 | Validation plan | Six-gate structure (G1–G6) — see [`methodology.md`](methodology.md). Subsections 3.1–3.6 map one-to-one to gates |
| 4 | Transition and governance | Parameter path, CIP approval route, risk of off-chain dependencies |
| 5 | Interaction audit | Same-layer precedence questions, cross-layer composition, dependency-chain ordering |

Cross-CIP comparison and mapping onto governance philosophies: [`synthesis.md`](synthesis.md).

## 4. Visual layout convention

Per-CIP and synthesis docs follow a **visual-first** pattern: TL;DR block at top, tables over prose, cross-references consolidated at the end of each file. Inline markdown link references are avoided in body prose; links live in the final *References* section.

## 5. Constraints

- All recommendations respect the [Cardano Constitution](https://github.com/IntersectMBO/cardano-constitution/tree/main/cardano-constitution-2). Constitutional-tenet mapping follows V2 §2.
- Python 3.9 compatibility preserved for simulation work against the simulator.
- Dates in generated outputs follow `YYYY/MM/DD` per the workspace date-formatting rule.

## 6. References

- **V2 specification:** [`../README.md`](../README.md) §2 grid, §5 evaluation framework, §4.4 governability criteria, §2 constitutional framework.
- **Diagnostic evidence:** [`../diagnostic/README.md`](../diagnostic/README.md).
- **Mechanism-intent narrative:** [`../the-intended-game/README.md`](../the-intended-game/README.md).
- **Simulator:** [`../../../simulator/`](../../../simulator/).
- **Governance recommendation context:** [`../../../Context/cip-analysis/governance-cip-recommendation-package.md`](../../../Context/cip-analysis/governance-cip-recommendation-package.md).
- **CIP local copies:** [`../../../Context/CIPs-repo/`](../../../Context/CIPs-repo/).
- **Subfolders:** [`operator-delegator/README.md`](operator-delegator/README.md), [`pools-distribution/README.md`](pools-distribution/README.md).
- **Synthesis:** [`synthesis.md`](synthesis.md).
