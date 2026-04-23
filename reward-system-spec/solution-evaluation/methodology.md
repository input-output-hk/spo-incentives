# Methodology — Phased evaluation of reward-scheme CIPs

> **Status:** Active 2026/04/23. Methodology for evaluating candidate CIPs against V2. Referenced by every per-CIP file in this folder. Sources in §4.

## TL;DR

- **Phases, not gates.** CIP evaluation is an inquiry in five ordered phases — what is claimed, whether the claim can structurally hold, how much the mechanism actually moves, what else it disturbs, and how to deploy safely. Each phase gates the next.
- **V2 is the problem catalog.** V2 §3/§4 functions as the space's CPS catalog. Each sub-section carries its own *Problem statement*, *Evidence base*, and *Specification*. A CIP is evaluated against claims drawn from this catalog.
- **Evidence has a trust hierarchy.** Analytical theorems and snapshot arithmetic are high-trust. Best-response reasoning and historical analogies are medium. Exploratory simulation is low and supplementary.
- **Side effects can overturn a positive verdict.** A gain on one milestone does not compensate a degradation on another. Phase 4 is the necessary brake on Phase 3.

## 1. Why a phased inquiry

A CIP evaluation mixes claims of different kinds — what the author says the instrument solves, whether the formula can structurally solve it, how much it moves on real data, what else it perturbs, and how to roll it out safely. Treating these as one "does it work?" question collapses the distinctions that matter.

The phased structure separates:

- *What is claimed* from *whether the claim can structurally hold*
- *Whether it can hold* from *how much it actually moves*
- *What it moves on the claimed axis* from *what it moves elsewhere*
- *What it does* from *what is needed to deploy it*

Each phase produces an intermediate verdict that gates the next. A CIP that fails validity on its headline claim does not need quantification work. A CIP that passes validity and quantification but introduces a severe unmitigated side effect is still rejected.

## 2. The five phases

### 2.1 Phase 1 — Which problems does the CIP claim to address?

The V2 specification §3/§4 acts as the space's problem catalog. Each sub-section (§3.1 operator viability, §3.2 pledge as signal, §3.3 delegator yield, §3.4 concentration, §4.1 pot survival, §4.2 fee-gen population, §4.3 price robustness, §4.4 governability) carries its own *Problem statement*, *Evidence base*, and *Specification*.

Phase 1 collects, from the CIP text alone, which of these problems the author claims the instrument addresses.

| Case | Meaning | Evaluator action |
| --- | --- | --- |
| Explicit claim | The CIP names the V2 problem (or an equivalent problem statement) | Cite the passage |
| Implicit claim | The CIP describes a problem without mapping it to the catalog | Reconstruct the mapping; flag as *reconstructed framing* |
| No claim | The CIP proposes a solution without stating the problem | Structural red flag — document before any further work |

Output of Phase 1: a sourced table *CIP ↔ V2 problems claimed*. Phase 1 records the claim; it does not test it.

**Operational note.** Most of the CIPs in this evaluation do not cite a CPS or a V2 sub-section explicitly — the V2 specification post-dates them. The evaluator reconstructs the mapping and flags it. A CIP with *no* stated problem at all is a distinct and more serious case.

### 2.2 Phase 2 — Validity of the proposal

For each claim collected in Phase 1, can the mechanism structurally satisfy the problem's *Specification*? This is a question about the *form* of the instrument, independent of parameter values.

| Verdict | Meaning | Downstream |
| --- | --- | --- |
| **Valid** | Mechanism form fits the problem's acceptance criteria | Phase 3 quantifies magnitude |
| **Contingent** | Validity conditional on another instrument delivering a prerequisite | Phase 3 proceeds under that condition; dependency-chain recorded |
| **Invalid** | Mechanism form cannot satisfy the problem's criteria | Claim rejected — drop it, or reject the CIP on this milestone |
| **Out of reach** | Problem outside the mechanism's structural perimeter | Claim rejected as misplaced |

A CIP whose headline claim is *invalid* is rejected on that milestone regardless of downstream phases.

**Worked example (CIP-0050).** Claims §3.2 (pledge as signal) and §3.4 (concentration). §3.2 is valid — the $L\cdot p$ term couples reward-eligible stake to pledge, exactly the binding signal §3.2 requires. §3.4 is valid at the pool level (pool-splitting revenue-neutral, by theorem) and contingent at the entity level (custodial operators with large native pledge bypass any reasonable $L$). §3.1 is out of reach — the formula does not touch the fee split. Dependency: the §3.2 claim is contingent on §3.1 being delivered first by a fee-layer instrument, otherwise the sub-threshold tail is pushed into the structural floor.

### 2.3 Phase 3 — Quantification of claimed effects

For each claim that survives Phase 2, Phase 3 asks *how much* the mechanism moves on real data, using a stack of evidence tools with explicit trust levels.

| Tool | What it quantifies | Trust |
| --- | --- | --- |
| Analytical properties | Monotonicity, bounds, thresholds, invariances — theorems on the formula alone | High |
| Mainnet-snapshot counterfactual | Immediate redistribution on observed populations, before any behavioural response | High |
| Population best-response reasoning | Plausible effect once each population adapts — assumption set labelled | Medium |
| Historical analogies | Base rates from comparable past parameter changes | Medium-low |
| Exploratory simulation | Sensitivity analysis, ablation, qualitative joint direction — assumptions explicit | Low |

**Composition rule inside Phase 3.** A claim cannot rest on simulation alone. At least one high-trust tool (analytical property or snapshot counterfactual) must carry the claim. Simulation is supplementary, never primary.

Output of Phase 3: per claim, a table *tool × estimated magnitude × trust*. A claim is strongly supported when multiple high-trust tools converge, fragile when only low-trust tools carry it.

### 2.4 Phase 4 — Side-effect scan

A mechanism that delivers on its claimed problem can still introduce or amplify others. Phase 4 is a systematic scan of effects the CIP did *not* claim. Three sweeps, each with its own logic.

**Off-target V2 effects.** Walk the V2 sub-sections the CIP does *not* claim. Does the mechanism touch them? In which direction? Example: CIP-0050 does not claim §3.1, but a low $L$ deployed without prior fee-layer reform pushes the weak-pledge sub-threshold tail against the structural floor — an amplification of §3.1.

**Amplification of existing V2 problems.** For each V2 problem already on record as unresolved or partially addressed by the current system, does the CIP make it worse? This differs from the off-target sweep — it concerns pre-existing ground that V2 already acknowledges.

**New problems outside the V2 catalog.** Expansion of governance surface, calibration fragility, new attack vectors, incompatibility with other in-flight CIPs, Conway-era compatibility regressions, operational burden on SPOs or wallet implementers — any problem the CIP introduces that neither V2 nor the current state records.

Output of Phase 4: a table *effect type × axis affected × direction × severity*, each with a downstream consequence — *rejection / mitigation obligation in Phase 5 / dependency-chain flag*.

**Composition with Phase 3.** A severe Phase 4 negative can overturn a positive Phase 3 verdict. The recommendation cannot claim a net gain when a material collateral loss is unmitigated.

### 2.5 Phase 5 — Deployment contract

Phases 1–4 evaluate the instrument. Phase 5 specifies the production contract — what is measured, when, with what rollback path.

| Element | Content |
| --- | --- |
| Ramp schedule | Sequence of parameter values and epochs between steps |
| Measurement cadence | Which KPIs, at what frequency, with what rolling window |
| Rollback triggers | Explicit conditions that require pausing or reversing a step |
| Pause mechanism | Standard Parameter Change, emergency halt, or none |
| Decision authority | CC / SPO vote / dRep vote / HFC |

Phase 5 replaces "will it work?" with "what do we measure, and when do we stop?". Every Phase 4 risk that was not grounds for rejection must be addressed here as a named mitigation.

## 3. How verdicts compose

A V2-compatible recommendation must:

1. **Pass Phase 2** on every claim it intends to carry. A claim that fails validity cannot be carried; drop it, or reject the CIP on that milestone.
2. **Pass Phase 3** on each surviving claim with at least one high-trust tool supporting the effect magnitude.
3. **Pass Phase 4** — no unmitigated severe side effect. A positive Phase 3 verdict that a severe Phase 4 finding overturns does not stand.
4. **Specify Phase 5** — every surviving Phase 4 risk has a named mitigation in the deployment contract.

A CIP that passes Phases 2 + 3 but carries an unmitigated severe Phase 4 finding is *not recommendable*. A CIP that needs exploratory simulation to carry its main claim is *not yet ready*. A CIP that fails Phase 2 on its headline claim is rejected regardless of everything downstream.

## 4. References

- **V2 specification (the problem catalog):** [`../README.md`](../README.md) §2 grid, §3–§4 per-problem pages, §5 evaluation framework.
- **Diagnostic snapshots:** [`../diagnostic/README.md`](../diagnostic/README.md), [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md), [`../diagnostic/sub-flows/pools-distribution/mainnet-analysis/`](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md).
- **Simulator (Phase 3 supplementary tool):** [`../../../simulator/`](../../../simulator/).
- **Per-CIP evaluations applying this methodology:** [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md), [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`k-parameter.md`](k-parameter.md).
- **Synthesis:** [`synthesis.md`](synthesis.md).
