# Methodology — Gated evaluation of reward-scheme CIPs

> **Status:** Active 2026/04/22. Methodology for evaluating candidate CIPs against V2. Referenced by every per-CIP file in this folder. Sources in §5.

## TL;DR

- **Why.** A single "does it work?" verdict is not actionable. Each CIP mixes claims of very different kinds — formula properties (provable), mainnet-snapshot counterfactuals (provable), historical analogies (base rates), game-theoretic arguments (plausible), and simulator outputs (dependent on assumptions).
- **Gates.** Six validation gates, each with its own trust level. A verdict is built by checking which gates the candidate clears, not by running one simulation.
- **Simulator.** Demoted to G6 — *exploratory*, not primary. A recommendation does not depend on G6.
- **Actionable spine.** G1 + G2 (high-trust) as the backbone; G3 + G4 as directional evidence; G5 as the production-side safety net that replaces prediction with measurement.

## 1. Why gates

A CIP evaluation mixes claims of very different epistemic status:

| Claim kind | Example | How it is known |
| --- | --- | --- |
| Formula property | $L\cdot 0 = 0$ — zero pledge yields zero reward-eligible stake | Theorem — provable from the formula |
| Mainnet-snapshot arithmetic | 473 zero-pledge pools, 2.74 B ADA → zero rewards under CIP-0050 at any $L$ | Direct substitution — provable from snapshot + formula |
| Base-rate response | A `k` raise in weak-pledge regime elicits MPO fleet expansion | Historical — one prior instance (`k: 150 → 500`) |
| Equilibrium argument | Under flat-yield stage-2 CIP-0082, delegators steer by brand / convenience | Qualitative game theory — plausible, not demonstrated |
| Prediction | Nakamoto coefficient will reach ~160 at $L = 100$ under steady state | Simulation — depends on engine + behavioural assumptions |

Treating all of these as evidence of equal weight is the failure mode. Separating them into **gates** lets a recommendation rest on the high-confidence gates and carry its residual uncertainty explicitly.

## 2. The six gates

| Gate | Question | Trust | What it can show | What it cannot show |
| --- | --- | --- | --- | --- |
| **G1** | Analytical properties | High | Hard breaks, monotonicity, price invariance, governance surface | Behavioural response, equilibria |
| **G2** | Mainnet-snapshot counterfactual | High | Immediate impact on observed populations (zero-pledge, subthreshold, MPO fleet, CEX / IVaaS) | Dynamic response, second-order effects |
| **G3** | Historical analogies | Medium | Base rates for MPO / delegator response | Anything outside the reference class |
| **G4** | Game-theoretic reasoning | Medium–low | Plausible equilibria, dominant strategies, Sybil incentives | Point predictions |
| **G5** | Governance ramp & rollback | N/A (production) | Measurement cadence, triggers, safe rollback paths | — (not a verdict; a production contract) |
| **G6** | Exploratory simulation | Low | Ablation studies, parameter sensitivity, qualitative direction | Primary verdict |

### 2.1 G1 — Analytical properties

Things provable from the formula alone, without data.

**What to check.**

- Monotonicity in pledge — more pledge → weakly more capacity?
- Hard breaks (e.g., $L\cdot 0 = 0$) or soft floors (e.g., CIP-0037's $e$)?
- Price invariance — is the mechanism a ratio (invariant) or absolute ADA (price-coupled)?
- Governance surface — how many governable knobs?
- Pool-splitting response — revenue-neutral, revenue-decreasing, or revenue-increasing?

**Worked example (CIP-0050).** $L\cdot 0 = 0$ — zero-pledge hard break is a theorem. Revenue-neutrality of pool splitting: $L\cdot p$ summed across $N$ pools sharing pledge $p/N$ each equals $L\cdot p$, identical to the single-pool cap. No simulation needed.

### 2.2 G2 — Mainnet-snapshot counterfactual

Apply the CIP formula to the current mainnet state. Which populations immediately cross a threshold?

**What to check.**

- Which pools lose eligible stake, and how much?
- Which pools gain capacity?
- Which populations (zero-pledge, subthreshold, MPO fleet, CEX / IVaaS) are structurally affected?
- Quantify the *immediate* redistribution, before any behavioural response.

**Worked example (CIP-0050 at $L = 100$, epoch 560).** 473 zero-pledge pools × 2.74 B ADA → zero reward-eligible stake. Subthreshold pools with pledge-to-stake ratio below 1 % → capped. Custodial pools with native ADA pledge ≫ 1 % of stake → unaffected. These are counterfactuals on snapshot data, not predictions.

**Data sources.** Mainnet analysis at the V2 diagnostic anchor epoch, stratified by pledge ratio, MPO entity, custodial classification.

### 2.3 G3 — Historical analogies

Past parameter changes as a reference class.

**Usable anchors.**

| Anchor | Used for | Caveat |
| --- | --- | --- |
| `k: 150 → 500` (2020) | Weak-pledge `k` raises → MPO fleet expansion | One observation |
| Fee-schedule updates 2020–2021 | Fee-layer response | Small sample |
| `minPoolCost` era shifts | Subthreshold viability response | Small sample |
| Pool-saturation events | Delegator response | Small sample |

**Limits.** One observation per anchor. The reference class is small. Use as a base rate, not a point prediction.

### 2.4 G4 — Population best-response reasoning

Qualitative analysis of how each population's best response shifts under the CIP. Not a prediction — an explicit *assumption set*, labelled as such.

| Population | Key variables | Typical response lever |
| --- | --- | --- |
| Independent single-pool SPO | Viability, pledge capacity | Margin, pledge top-up, exit |
| MPO fleet | Per-pool capacity, pledge budget | Split further, consolidate, exit |
| CEX / IVaaS | Native ADA balance, brand pull | Adjust fees, create / retire pools |
| Delegator | Yield, brand, convenience | Switch pool, switch CEX, unstake |

**How to use.** Sketch the plausible best response per population. Flag which milestone it threatens if the response realises. Label conclusions *assumptions*, not predictions.

### 2.5 G5 — Governance ramp and rollback

Since G1–G4 cannot predict dynamic outcomes with certainty, a responsible package encodes **measurement and rollback** in the governance path itself.

**What to specify per CIP.**

| Element | Content |
| --- | --- |
| Ramp schedule | Sequence of parameter values and epochs between steps |
| Measurement cadence | Which KPIs are checked, at what frequency, with what rolling window |
| Rollback triggers | Explicit conditions that require pausing or reversing a step |
| Pause mechanism | Standard Parameter Change, emergency halt, or none |
| Decision authority | CC / SPO vote / dRep vote / HFC |

G5 is not a verdict — it is a **production contract**. It replaces "will it work?" with "what do we measure, and when do we stop?".

### 2.6 G6 — Exploratory simulation (optional)

Explicitly demoted.

**Useful for.**

- Ablation studies across parameter ranges.
- Sensitivity of a G1 / G2 result to assumption perturbations.
- Qualitative direction of joint movements (e.g., `k` + $L$ interaction).

**Must not.**

- Produce a headline number quoted without caveats.
- Be the primary justification for a recommendation.
- Hide its modelling assumptions (agent behaviour, convergence criterion, starting state).

**Engine.** [`../../../simulator/`](../../../simulator/). Under active improvement 2026. Any G6 output is provisional until the engine's behavioural assumptions are independently cross-checked.

## 3. How to read a §3 block

Each per-CIP file's §3 *Validation plan* maps directly to the six gates:

| Subsection | Gate | Produces |
| --- | --- | --- |
| 3.1 | G1 | Formula-property table |
| 3.2 | G2 | Snapshot counterfactual table |
| 3.3 | G3 | Historical anchor table |
| 3.4 | G4 | Per-population best-response table |
| 3.5 | G5 | Ramp + rollback table |
| 3.6 | G6 | Ablation questions (optional) |

## 4. How verdicts compose

A V2-compatible recommendation should:

1. **Pass G1 + G2** on the core milestones it claims to address (§3.1, §3.2, §3.3, §3.4 as relevant).
2. **Have at least one G3 analogy** that does not actively contradict the verdict.
3. **Have a coherent G4 story** per affected population, with labelled assumptions.
4. **Specify G5** — ramp, measurement, rollback triggers.
5. G6 is *supplementary*, not load-bearing.

A CIP that clears G1 + G2 but has a weak G4 can still be deployed — with a tight G5. A CIP that needs G6 to justify its main verdict is **not yet ready**.

## 5. References

- **V2 specification:** [`../README.md`](../README.md) §2 grid, §5 evaluation framework.
- **Diagnostic snapshots:** [`../diagnostic/README.md`](../diagnostic/README.md), [`../diagnostic/sub-flows/census/mainnet-analysis/`](../diagnostic/sub-flows/census/mainnet-analysis/README.md), [`../diagnostic/sub-flows/pools-distribution/mainnet-analysis/`](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md).
- **Simulator (G6, exploratory):** [`../../../simulator/`](../../../simulator/).
- **Per-CIP evaluations applying this methodology:** [`operator-delegator/cip-0023.md`](operator-delegator/cip-0023.md), [`operator-delegator/cip-0082.md`](operator-delegator/cip-0082.md), [`pools-distribution/cip-0050.md`](pools-distribution/cip-0050.md), [`pools-distribution/cip-0037.md`](pools-distribution/cip-0037.md), [`k-parameter.md`](k-parameter.md).
- **Synthesis:** [`synthesis.md`](synthesis.md).
