# Whiteboard — A coupled viability/pledge reward architecture

> **Status:** Exploratory draft 2026/04/26. Not a candidate specification; a working sketch for the V2 reward formula. To be challenged, rewritten, or discarded.
> **Scope:** Re-architect the per-pool reward distribution function — break with the (ceiling × performance × envelope) decomposition inherited from SL-D1 and propose a structure that treats operator viability ([§3.1](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) and pledge as Sybil instrument ([§3.2](../README.md#32-restore-the-notion-of-pledge-among-operators)) as **one coupled problem**, not two layers in a dependency chain.

## Executive summary

The current Shelley reward function decomposes into a *ceiling* ($P_{\max} = z_0 \cdot R$), a *performance* multiplier ($\bar p$), and an *envelope* ($E(\nu, \pi)$ blending a stake-linear base term with a pledge-leveraged bonus). The four evaluated CIPs (CIP-0023, CIP-0082, CIP-0050, CIP-0037) intervene either on the **fee layer** (viability) or on the **stake-cap layer** (pledge signal) — never on both at once — and the synthesis explicitly frames them as alternatives, not stacks.

This whiteboard takes a different bet:

- **Wager 1 — the two problems are one.** Operator viability and pledge meaning collapse together: a pledge-leveraged bonus that requires capital is a regressive viability shock; a fee floor that ignores commitment hollows the Sybil tax. They must be designed jointly.
- **Wager 2 — the architecture is three populations, not two layers.** The three structural populations identified in the Diagnostic (custodial, multi-pool-entity, independent) each impose a distinct structural constraint. Any successor must produce a function whose *response* to each population is engineered, not incidental.
- **Wager 3 — the formula must answer security properties, not assume them.** The role of pledge is derived downstream from the four security properties (liveness, safety, Sybil resistance, non-triviality) of *The Intended Game*, not posited a priori as in CIP-0050/0037.

The shape this points to: a three-component reward function — **admission**, **wage**, **commitment signal** — that are *coupled by construction* (each component constrains the others) rather than chained sequentially.

## 1. The coupling thesis

### 1.1 Why the dependency-chained reading fails

The current V2 reading orders the milestones as a chain: viability ([§3.1](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) precedes pledge ([§3.2](../README.md#32-restore-the-notion-of-pledge-among-operators)) precedes delegator yield ([§3.3](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield)) precedes concentration ([§3.4](../README.md#34-reduce-the-concentration-effects-that-distort-both-populations)). The synthesis composes the candidate package the same way: *fee-layer first*, *stake-cap second*, *k raises last*.

Two structural objections emerge from re-reading the Diagnostic against the four CIP evaluations.

**Objection A — fee reform is not pledge-neutral.** A flat percentage floor (CIP-0082 stage 2 `minPoolRate`, or any ledger-level proportional cost) collapses the delegator fee-rate dispersion from 38× to 1.00× and reshapes the per-pool revenue gradient. That gradient is the same surface on which pledge-as-signal must live. Rewriting it without simultaneously rewriting the pledge component leaves the pledge instrument designed for a fee structure that no longer exists.

**Objection B — pledge reform is not viability-neutral.** CIP-0050 ($\sigma' = \min(\sigma, 1/k, L\cdot p)$) and CIP-0037 ($\text{sat}(p) = \text{orig\_sat} \cdot \max(e, \min(1/k, p/\text{orig\_sat}\cdot \ell))$) both gate eligible-stake on pledge. The retail single-pool operator (median pledge ratio ≈ 0.07%) is clipped to ~7% of the saturation ceiling at $L = 100$, or to the 20% floor at $e = 0.2$. In either case, **the viability gap that [§3.1](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population) seeks to close is mechanically widened by the very instrument that [§3.2](../README.md#32-restore-the-notion-of-pledge-among-operators) is supposed to introduce**. The chain assumes the layers don't interact; the algebra says they do.

The conclusion is not that the V2 milestone ordering is wrong — it is that **the candidate reward function cannot be a stack**: the fee structure and the pledge structure are two cuts of the same surface and must be co-designed.

### 1.2 The unified problem statement

A reward function $f$ over a per-pool tuple $(\sigma, p, \pi)$ — with entity-level state acknowledged but its incorporation deferred (§4.4) — is a **coupled solution** if and only if:

> **C1 — Universal viability.** For every pool above the production threshold $\sigma_{\min}$, the operator share of $f$ exceeds a fiat-denominated viability cost across a stated ADA price range, *regardless of pledge level*. Custodial inability to pledge does not cross the viability boundary.
>
> **C2 — Material commitment signal.** The yield differential between meaningfully-committed and uncommitted operators is large enough to be visible to delegators (>0.5pp, per [§3.2.2](../README.md#322-specification)) and *increases with entity-level fleet size*, not pool-level pledge ratio.
>
> **C3 — Architectural recognition of the three populations.** Custodial operators (cannot commit own capital) and independent operators (commit capital out of conviction) are *not* mapped to the same reward branch. The function must distinguish *architectural inability* from *strategic choice* through a means other than pledge ratio alone.

A solution that satisfies C1 but not C2 collapses to CIP-0023/0082 — viable but Sybil-permissive. A solution that satisfies C2 but not C1 collapses to CIP-0050/0037 — anti-Sybil but capital-capability-biased. A solution satisfying C2 without C3 collapses custodial to "uncommitted" and reproduces the CIP-0050 zero-pledge break.

The whiteboard takes C1 ∧ C2 ∧ C3 as the **joint admissibility predicate** and asks: *what shape must $f$ take?*

## 2. Constraints inherited from V2

The proposal must satisfy a fixed set of constraints that come from the V2 specification, the Cardano Constitution, and the *Intended Game* security properties. They are not negotiable; they are the boundary conditions of the design space.

### 2.1 Hard constraints from the V2 specification

| Origin | Constraint | Quantitative target |
|---|---|---|
| [§3.1.2](../README.md#312-structural-enforce-the-production-threshold) — production threshold | A minimum active-stake threshold $\sigma_{\min}$ must be defined and enforced; a sub-threshold pooling-service path must exist | $\sigma_{\min} \approx 1\text{M ADA}$ at current parameters; sub-threshold pool count → 0 |
| [§3.1.3](../README.md#313-economic-every-productive-pool-must-be-profitable) — economic viability | Every pool at or above $\sigma_{\min}$ must generate operator revenue exceeding fiat operating cost; the floor must be proportional, not fixed | Operator viability rate >90% across the productive set; >50% at ADA = $0.10 |
| [§3.2.2 R1](../README.md#322-specification) — material pledge differential | Yield differential between pledged and unpledged pools must be visible to delegators | >0.5pp |
| [§3.2.2 R2](../README.md#322-specification) — entity-level pledge | Pledge must be evaluated at the entity level; an entity splitting capital across $n$ pools must not receive the aggregate benefit of $n$ independent pledges | Marginal pledge cost positive and increasing with $n$ |
| [§3.2.2 R3](../README.md#322-specification) — custodial recognition | The mechanism must distinguish architectural inability to pledge from strategic choice | Custodial population (CEX + IVaaS) must remain viable without pledging delegated capital |
| [§3.2.2 R4](../README.md#322-specification) — governable pledge | Pledge parameters must be reviewable through Conway-era governance, with awareness of fiat/ADA asymmetry | Parameter review cadence; oracle-informed adjustment instrument |

### 2.2 Hard constraints from the Cardano Constitution

| Parameter | Constitutional bound | Implication |
|---|---|---|
| $a_0$ (poolPledgeInfluence) | [0.1, 1.0] (PPI-01–04) | Any pledge-leveraged bonus must remain expressible within this range — or the bound itself must be widened by constitutional amendment |
| $k$ (saturation target) | [250, 2000] (SPTN-01–04) | The saturation surface remains a parameter, not a design variable |
| $minPoolCost$ | [0, 500] (MPC-01–03) | A residual fixed-floor instrument remains available; not all viability mechanisms require ledger-level rewrites |
| $\rho$ (monetary expansion) | [0.001, 0.005] (ME-01–05) | The funding envelope is bounded; the proposal must operate within the existing $R$ |
| $\tau$ (treasury cut) | [0.1, 0.3] (TC-01–05) | Treasury share is bounded; the proposal cannot fund itself by taking from the treasury without governance approval |

### 2.3 Security properties from *The Intended Game*

The four security properties of [*The Intended Game* §3.4](../the-intended-game/README.md) are **derivation premises**, not design choices. The pledge component of the formula must answer to them — its presence, shape, and weight are downstream of these properties.

| Property | What the formula must guarantee |
|---|---|
| Liveness | Block production at the $k$-target requires $\geq k$ entities reaching the production threshold profitably |
| Safety | The reward gradient must not incentivise withholding or strategic absence |
| Sybil resistance | The marginal reward of the $n$-th pool registered by a single entity must, beyond a calibrated $n$, fall below the marginal cost — *through the designed reward structure*, not through wealth alone |
| Non-triviality | The mechanism must produce more than one viable strategy; if pledge is the only path, custodial and independent populations face identical economics, which contradicts [§3.2.2 R3](../README.md#322-specification) |

## 3. Anti-patterns inherited from the four CIP evaluations

The whiteboard treats the following pathologies as **pre-conditions to forbid**. A candidate function is rejected if it reproduces any of them.

| Anti-pattern | Source CIP(s) | What the formula must not do |
|---|---|---|
| Per-pool revenue regressive uplift | CIP-0023, CIP-0082 stage 2 | The marginal change in operator revenue between sub-viable and saturated tiers must not exceed the change at the lower tier (no 50× tier amplification) |
| MPO fleet amplification | CIP-0023, CIP-0082 | The marginal benefit of the $(n+1)$-th pool to an $n$-pool entity must not be larger than the benefit to the 1st pool of an independent operator (current bundle: ~500× gap) |
| Capital-capability bias | CIP-0050, CIP-0037 | The activation threshold of any pledge-conditioned bonus must scale with pool size, not with absolute pledge — otherwise floor-exit is mechanically regressive |
| Zero-pledge discontinuity | CIP-0050 | The reward at $\pi = 0$ must be continuous and non-zero for pools that pass the production gate; custodial populations must not collapse |
| Custodial / strategic conflation | CIP-0050, CIP-0037 | The function must not treat custodial inability and MPO strategic non-pledging through the same reward branch |
| Pledge-bonus dormancy | Current Shelley | The bonus budget actually distributed must exceed a stated fraction of the budget allocated (current: <5% utilisation) |
| Fixed-cost fiat asymmetry | Current Shelley, persists in CIP-0023 | An ADA-denominated fixed floor that has no protocol-level awareness of ADA price drift is rejected (cost has fluctuated 10× since launch) |
| Parameter dormancy | Current Shelley ($a_0$) | A pledge parameter that is never adjusted post-deployment defeats the [§3.2.2 R4](../README.md#322-specification) governability requirement |

## 4. Architecture sketch — three-term envelope, retained outer multiplier

The whiteboard retains the global shape inherited from SL-D1 — $\bar p \cdot P_{\max} \cdot E$ — and re-engineers the envelope $E$ from a two-term to a three-term convex decomposition. The performance multiplier $\bar p$ is preserved as the outer gate: a pool that fails to deliver blocks earns nothing, regardless of how the envelope is shaped.

### 4.1 The retained outer structure

$$
\hat f'(\nu,\, \pi,\, \bar p,\, n^{\text{cum}}) \;=\; \bar p \cdot P_{\max} \cdot E(\nu,\, \pi,\, n^{\text{cum}})
$$

with $P_{\max} = z_0 \cdot R$ retained from current Shelley.

Why $\bar p$ stays. The performance multiplier is the protocol's only on-chain signal of *delivered* work in the current epoch, and conditioning the entire envelope on it collapses three concerns into one structural property: sub-threshold pools cannot earn (Poisson-sparse production drives $\bar p \to 0$), absentee operators cannot earn, and viability subsidies do not reach pools that fail to perform. The performance gate sits *outside* the redesign — a precondition, not a parameter.

Why $n^{\text{cum}}$ enters. The viability term defined in §4.3 below conditions on a *lifetime* qualification (has the pool ever produced a block?). SL-D1 [§5.5.1](../references/design-specs/delegation-incentives-design-spec_kant-brunjes-coutts_2019.pdf) only exposes the per-epoch block count $n$ through its derivation of $\bar p$; it does not expose a stateful lifetime counter. Introducing $n^{\text{cum}}$ as an explicit input makes the lifetime gate computable and makes the dependency surface auditable.

**Notation against SL-D1.** The proposed signature extends SL-D1 §5.5.1 Eq.(1) without breaking it.

| Symbol | Meaning | SL-D1 origin |
|---|---|---|
| $\sigma$ | Pool's relative stake (fraction of total stake) | SL-D1 §5.5.1 |
| $\nu = \sigma / z_0$ | Pool's stake normalised to the saturation cap $z_0 = 1/k$ | Diagnostic §2.3 (normalised coordinate) |
| $\pi = s' / \sigma'$ | Within-pool pledge ratio (capped pledge over capped stake) | Derived from SL-D1 $s', \sigma'$ |
| $n$ | Blocks produced *by the pool, in the current epoch* | SL-D1 §5.5.1 |
| $\overline{N}$ | Total blocks added to the chain in the current epoch | SL-D1 §5.5.1 |
| $\beta = n / \max(1, \overline{N})$ | Pool's per-epoch block share | SL-D1 §5.5.1 Eq.(1) |
| $\bar p = \beta / \sigma$ | Apparent performance (per-epoch block share, stake-normalised) | SL-D1 §5.5.1 |
| $n^{\text{cum}}$ | **Cumulative blocks produced by the pool over its lifetime** (new) | Extension — not in SL-D1; required by the first-block gate of §4.3 |

The relationship between the new and existing variables is purely additive: $n^{\text{cum}}_p(t) = \sum_{e \leq t} n_p(e)$, where $n_p(e)$ is SL-D1's per-epoch block count for pool $p$ at epoch $e$. The protocol already records $n_p(e)$ to compute $\bar p$; persisting its cumulative sum across epochs adds one $\mathbb{N}$-valued field per pool to the ledger state.

### 4.2 The three-term envelope

The variables in scope are summarised in the §4.1 table. The size and pledge terms are pool-local in the same shape as current Shelley; the viability term consumes the new lifetime block-count input $n^{\text{cum}}$. The entity-level evaluation that [§3.2.2 R2](../README.md#322-specification) requires for the pledge term is **deferred** (see §4.4).

The envelope is rewritten as a convex combination of three terms:

$$
E(\nu,\, \pi,\, n^{\text{cum}}) \;=\; \lambda_{\text{viability}} \cdot V(\nu,\, n^{\text{cum}}) \;+\; \lambda_{\text{size}} \cdot \nu \;+\; \lambda_{\text{pledge}} \cdot A(\nu,\, \pi)
$$

with the convex constraint

$$
\lambda_{\text{viability}} + \lambda_{\text{size}} + \lambda_{\text{pledge}} = 1, \qquad \lambda_{\text{viability}}, \lambda_{\text{size}}, \lambda_{\text{pledge}} \geq 0.
$$

| Term | Role | Maps to | Status vs. current Shelley |
|---|---|---|---|
| $\lambda_{\text{viability}} \cdot V$ | **Viability mass** — operator floor for productive pools | [§3.1.3](../README.md#313-economic-every-productive-pool-must-be-profitable) | New term — no in-envelope Shelley analogue (the current $minPoolCost$ floor sits *outside* $E$, after the envelope is computed) |
| $\lambda_{\text{size}} \cdot \nu$ | **Size mass** — stake-accessible component | [§3.3](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield) | Retained from current Shelley ($\lambda_{\text{size}} = 1/(1+a_0)$ at present) |
| $\lambda_{\text{pledge}} \cdot A$ | **Pledge mass** — entity-level commitment instrument | [§3.2](../README.md#32-restore-the-notion-of-pledge-among-operators) | Retained shape but $A$ must be redesigned (see §4.4); current $\lambda_{\text{pledge}} = a_0/(1+a_0)$ |

The substantive change is twofold: (i) introducing $V$ as a *first-class envelope citizen* — viability becomes a property of the reward function itself, not of an external floor; and (ii) coupling the three terms through the convex sum, so that raising any one term mechanically compresses the others. The trade-off becomes explicit and governable.

### 4.3 The viability term $V$ — a viability pack triggered by demonstrated production

**Working hypothesis.** The viability injection takes the form of a **viability pack**: a fixed quantity $X$ ADA per epoch granted to every pool that has crossed an *initiation gate*, defined as **producing its first block**. The pack reframes $V$ from a continuous function of stake to a binary eligibility flag with an absolute injection size:

$$
V(\nu,\, n^{\text{cum}}) \;=\; \frac{X}{\lambda_{\text{viability}} \cdot P_{\max}} \cdot \mathbb{1}[\nu \geq \nu_{\min}] \cdot \mathbb{1}[n^{\text{cum}} \geq 1]
$$

Per-pool injection: $\lambda_{\text{viability}} \cdot V \cdot P_{\max} = X$ for any qualified pool — by construction, the absolute floor target.

The two indicator functions encode the two-layer admission gate of §4.3.1: $\mathbb{1}[\nu \geq \nu_{\min}]$ is the structural production gate ([§3.1.2 R1](../README.md#312-structural-enforce-the-production-threshold)), and $\mathbb{1}[n^{\text{cum}} \geq 1]$ is the empirical first-block gate. Both must fire for the pack to activate.

The pack defines $X$ as **the minimum operator profit per epoch required to keep a pool producing** — the epoch-granular analog of the [§3.1.3](../README.md#313-economic-every-productive-pool-must-be-profitable) fiat operating cost. The injection is granted in full to every qualified pool, regardless of size.

#### 4.3.1 Why "first block" as the eligibility gate

The first-block gate composes with $\sigma_{\min}$ ([§3.1.2 R1](../README.md#312-structural-enforce-the-production-threshold)) to form a two-layer admission system:

- $\sigma_{\min}$ — *can produce* (Poisson-feasibility, structural threshold derived from block-production statistics).
- First block — *has produced* (empirical confirmation that the pool is operationally functional, not certificate-only).

Three properties follow:

- **Demonstrated, not declared.** Registering a pool costs ~500 ADA and a configuration file; producing a block requires sustained operational capability over multiple epochs. The gate filters the productive cohort that should actually receive viability subsidy.
- **Sybil-resistant by construction.** An entity registering a Sybil pool to harvest $X$ must first run the pool long enough to produce a block — which carries operational cost and exposes the pool to the same delegation, performance, and reward dynamics as any other. The gate is not a paper credential.
- **Composable with the production-threshold reform.** The whiteboard already adopts [§3.1.2](../README.md#312-structural-enforce-the-production-threshold)'s requirement that $\sigma_{\min}$ become explicit and enforced. The first-block gate sits *downstream* of $\sigma_{\min}$: a pool above $\sigma_{\min}$ is structurally *capable* of producing; the first-block event is the empirical *witness* that it actually does. Sub-$\sigma_{\min}$ pools are excluded earlier, by registration; the first-block gate adds the next filter.

#### 4.3.2 Budget closure and target $X$

With $N_q$ qualified pools (those past the first-block gate) and $P_{\max} = R / k$:

$$
\lambda_{\text{viability}} \;=\; \frac{N_q \cdot X}{R}
$$

For the working partition $(\lambda_{\text{size}},\, \lambda_{\text{viability}},\, \lambda_{\text{pledge}}) = (0.5,\; 0.1,\; 0.4)$, with $R \approx 15.5$M ADA/epoch:

| Quantity | Value |
|---|---|
| Viability budget per epoch | $0.1 \cdot R \approx 1.55$M ADA |
| Estimated $N_q$ (productive subset post-gate) | $\sim 900$ |
| Implied $X$ per qualified pool | $\sim 1.72$K ADA/epoch |
| Annualised (73 epochs/year) | $\sim 125$K ADA/year |

This lands directly in the [§3.1.3](../README.md#313-economic-every-productive-pool-must-be-profitable) viability-target zone (>50K ADA/year at ADA = $0.10$, comfortably so at higher prices). The current Shelley sub-viable single-pool operator earns ~25K ADA/year; the pack would multiply that floor by $\sim 5\times$ for the *median single-pool operator*, while adding only $\sim 5\%$ to a saturated pool's reward (the pack is anti-regressive in proportional terms by construction — every qualified pool receives the *same absolute amount* $X$, which is a much larger fraction of small-pool rewards).

#### 4.3.3 Edge cases and parameters to resolve

The pack framing leaves four sub-questions for the next iteration. They do not gate the architecture's feasibility but they shape its calibration.

- **Persistence of qualification.** The variable that enters the indicator function depends on the persistence rule. *Lifetime-permanent*: $\mathbb{1}[n^{\text{cum}} \geq 1]$ — one block ever, eligible forever. Simplest but admits zombie pools that produced once and went silent. *Recency-conditioned*: $\mathbb{1}\!\left[\sum_{e=t-N+1}^{t} n_p(e) \geq 1\right]$ over the last $N$ epochs — aligns better with the *productive cohort* concept but penalises stake-volatile small pools that legitimately oscillate around the production threshold. *Cohort-graded*: the pack scales monotonically with sustained production count, replacing the indicator with a saturating function. The choice determines whether the new state variable in §4.1 is $n^{\text{cum}}$ (lifetime, monotone) or $n^{\text{recent}}_{N}$ (windowed sum).
- **Re-entry behaviour.** If a pool deregisters and re-registers, does the first-block credential carry over (under the same operator key, the same VRF, etc.) or does the gate reapply? Affects Sybil resistance: a permissive carry-over rule lets an entity migrate the credential across pools; a strict reapplication forces re-demonstration.
- **Denomination of $X$.** Three options. *(a)* ADA-fixed: governable but drifts with price (same pathology as current $minPoolCost$). *(b)* Fiat-anchored via oracle: addresses [§3.1.3 R3](../README.md#313-economic-every-productive-pool-must-be-profitable) directly but introduces an oracle dependency. *(c)* Hybrid: ADA-fixed with periodic governance review against a fiat reference. Inherits OQ4.
- **Variance smoothing.** Small pools produce blocks irregularly (Poisson sparsity). If qualification depends on $\bar p > 0$ in the current epoch, a small productive pool with a single bad epoch loses the pack — exactly the variance pathology OQ5 flags. Likely answer: the first-block gate is a *qualifier*, evaluated once per pool lifecycle (or on a multi-epoch window for "active" status), and is *not* re-evaluated each epoch on $\bar p$. The outer multiplier $\bar p$ still scales the entire envelope, so a non-producing epoch yields zero — but the qualification status persists.

#### 4.3.4 Fallback alternatives if the pack does not pan out

If the viability pack design hits a blocker on one of the sub-questions above (e.g., the persistence-of-qualification debate cannot be resolved without an entity-identity primitive that does not exist), four continuous-form alternatives remain on the table as fallbacks:

| Form | Functional shape | Behaviour |
|---|---|---|
| V1 — Equal-share | $V = \mathbb{1}[\nu \geq \nu_{\min}] / N_{\text{prod}}$ | Equipartition over the structural productive set (without first-block filter) |
| V2 — Threshold ramp | $V = \mathbb{1}[\nu \geq \nu_{\min}] \cdot \max(0, 1 - (\nu - \nu_{\min})/\nu_{\text{ref}})$ | Maximal at $\sigma_{\min}$, decays toward $\nu_{\text{ref}}$ |
| V3 — Fiat-anchored continuous | $V = \mathbb{1}[\nu \geq \nu_{\min}] \cdot c_{\text{fiat}} / (P_{\max} \cdot \bar p_{\text{ref}})$ | Continuous fiat-indexed, applied to all productive pools |
| V4 — Saturation-decreasing | $V = \mathbb{1}[\nu \geq \nu_{\min}] \cdot (1 - \nu / \nu_{\text{sat}})$ | Smooth, larger for small pools, zero at saturation |

The viability pack is effectively *V1 with an additional first-block filter and a fiat-anchorable injection size*. The fallbacks differ in two dimensions: (i) whether the productive set is filtered by structural threshold alone or by structural-plus-empirical (first-block), and (ii) whether the injection per pool is uniform (V1, pack), declining with size (V2, V4), or fiat-anchored (V3).

### 4.4 The pledge term $A$ — entity-level redesign deferred

The current $A(\nu, \pi) = \nu^2 \pi [1 - \pi(1 - \nu)]$ exhibits three pathologies (cf. §3): quadratic-in-$\nu$ penalisation of small pools (capital-capability bias), discontinuity at $\pi = 0$ (zero-pledge break), and per-pool evaluation (no Sybil tax on the entity axis).

The whiteboard **defers** the third concern — entity-level evaluation — to a later iteration. Addressing it requires an entity-identity primitive in the protocol (a CIP-0161 / CPS-0021 CPD-class instrument), which is out of scope here. For the present iteration, $A$ retains its pool-local signature, and the [§3.2.2 R2](../README.md#322-specification) entity requirement is acknowledged as an unresolved obligation.

This deferral is conditional, not abandonment. Without entity-level evaluation, the Sybil-resistance property that [§3.2.2 R2](../README.md#322-specification) mandates is not met by the formula alone — it remains satisfied incidentally through wealth constraints, exactly the failure mode the V2 spec calls out. The next iteration must either (i) propose a pool-level approximation that captures most of the entity-axis Sybil tax, or (ii) state the entity primitive as a hard prerequisite for the proposal to ship.

For the *first-block viability pack* design hypothesis, this deferral is structurally compatible: the pack lives entirely in $V$, which is already pool-local. The entity dimension only matters once $A$ is reformed.

### 4.5 The coupling — what $(\lambda_{\text{viability}}, \lambda_{\text{size}}, \lambda_{\text{pledge}})$ encodes

The convex constraint $\lambda_{\text{viability}} + \lambda_{\text{size}} + \lambda_{\text{pledge}} = 1$ is the explicit coupling between the three V2 milestones:

| Lever | Direct effect | Trade-off cost |
|---|---|---|
| Raising $\lambda_{\text{viability}}$ | Enlarges retail operator viability ([§3.1](../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) | Compresses delegator base yield ($\lambda_{\text{size}}$) or commitment incentive ($\lambda_{\text{pledge}}$) |
| Raising $\lambda_{\text{pledge}}$ | Steepens the Sybil tax ([§3.2](../README.md#32-restore-the-notion-of-pledge-among-operators)) | Compresses viability injection ($\lambda_{\text{viability}}$) or delegator base yield ($\lambda_{\text{size}}$) |
| Raising $\lambda_{\text{size}}$ | Maintains competitive delegator yield ([§3.3](../README.md#33-maintain-and-diversify-a-competitive-delegator-yield)) | Compresses viability injection or commitment incentive |

The current Shelley calibration is the limiting case $\lambda_{\text{viability}} = 0$ — viability is left to a separate $minPoolCost$ instrument outside the envelope, which generates the regressive $1/\sigma$ surface. The proposal makes viability a first-class envelope citizen and forces the trade-off to be expressed in a single governable triple.

The constitutional handle. The current $a_0 \in [0.1, 1.0]$ encodes a one-dimensional projection of this trade-off via $\lambda_{\max} = a_0 / (1 + a_0)$, $\lambda_{\min} = 1 / (1 + a_0)$. A three-term envelope requires either (i) a re-expression of the constitutional parameter as a tuple — e.g. $(a_0, b_0)$ with $\lambda_{\text{viability}} = b_0 / (1 + a_0 + b_0)$, $\lambda_{\text{size}} = 1 / (1 + a_0 + b_0)$, $\lambda_{\text{pledge}} = a_0 / (1 + a_0 + b_0)$ — or (ii) a constitutional amendment introducing a viability-influence parameter alongside $a_0$. The first option is parameter-update-grade and stays within the current Constitution; the second is amendment-grade and has higher governance cost. Both routes must be stated explicitly when the proposal is finalised.

## 5. Open questions to converge on next

Five design choices must be resolved before the formula's parameters can be calibrated. Each one materially shapes the final functional form.

- **OQ1 — Functional form of $V$.** Pick among V1 (equal-share), V2 (threshold ramp), V3 (fiat-anchored), V4 (saturation-decreasing), or a hybrid. The choice determines whether viability is fiat-aware (V1, V3) or stake-anchored (V2, V4), and whether all productive pools are treated equally (V1) or graduated (V2, V4).
- **OQ2 — Entity-identity primitive.** *Deferred.* Self-attested pool grouping, on-chain entity certificate, inferred clustering, or no primitive. Without it, the entity-level Sybil tax that [§3.2.2 R2](../README.md#322-specification) mandates cannot be collected, and $A$ remains in its current pool-local pathological form. The whiteboard parks this question for a later iteration; the present design does not solve it.
- **OQ3 — Custodial branch — express in $V$ alone, or also in $A$?** *Deferred jointly with OQ2.* With $V$ pledge-blind, custodial pools reach viability without entering $A$. The question of whether custodial registration should also appear as a transparency signal in $A$ depends on the entity-identity primitive of OQ2 and is parked alongside it.
- **OQ4 — Constitutional encoding of $(\lambda_{\text{viability}}, \lambda_{\text{size}}, \lambda_{\text{pledge}})$.** Re-express the existing $a_0$ as a two-dimensional parameter (parameter-update-grade), or introduce a new viability-influence parameter through constitutional amendment (amendment-grade). The first option preserves the existing PPI guardrails; the second widens them.
- **OQ5 — Smoothing of $\bar p$ on the viability term.** $\bar p$ is high-variance for small pools (Poisson sparsity); a small productive pool with a single bad epoch loses its viability injection. Three options: (a) accept the variance as a feature of the production gate; (b) apply a smoothed $\bar p^* = \text{EMA}(\bar p, \text{horizon})$ to the entire envelope; (c) apply $\bar p$ to $\lambda_{\text{size}}$ and $\lambda_{\text{pledge}}$ but $\bar p^*$ to $\lambda_{\text{viability}} \cdot V$ — partial decoupling that breaks the clean outer-multiplier structure but stabilises the viability signal.

## 6. Next steps

Three iterations are anticipated before this whiteboard becomes a candidate spec.

- **Iteration 1 — Resolve OQ1 (form of $V$).** This is the immediate scope: pin down the viability term and its parameters. OQ2 (entity primitive) and OQ3 (custodial branch in $A$) are *deferred* — the present iteration leaves $A$ pool-local and the [§3.2.2 R2](../README.md#322-specification) entity requirement unresolved.
- **Iteration 2 — Specify $V$ and $A$ and verify coupling.** Write the candidate functional forms (the size term needs no functional form beyond $\nu$ itself); verify that the convex constraint $\lambda_{\text{viability}} + \lambda_{\text{size}} + \lambda_{\text{pledge}} = 1$ and the budget closure $\mathbb{E}_{\text{pop}}[\bar p \cdot E] \cdot k = 1$ hold by construction; check that no anti-pattern from §3 is reproduced.
- **Iteration 3 — Quantify against the 9-tier × n-MPO grid.** Apply the per-CIP evaluation template (Exec summary / Evaluation findings / §1 Intro / §2 Mechanism / §3 Limits) to the candidate, mirroring the CIP-0023 / CIP-0082 / CIP-0050 / CIP-0037 evaluations. The candidate is admissible only if it improves on every cell where the four CIPs regress.

## References

- Current Shelley reward formula: [diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md §2.3](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md)
- V2 specification: [reward-system-spec/README.md §3.1, §3.2, §3.4, §4.4](../README.md)
- *The Intended Game* security properties: [the-intended-game/README.md §3.4](../the-intended-game/README.md)
- Cross-CIP synthesis: [solution-evaluation/synthesis.md](../solution-evaluation/synthesis.md)
- CIP evaluations: [cip-0023](../solution-evaluation/operator-delegator/cip-0023.md), [cip-0082](../solution-evaluation/operator-delegator/cip-0082.md), [cip-0050](../solution-evaluation/pools-distribution/cip-0050.md), [cip-0037](../solution-evaluation/pools-distribution/cip-0037.md)
- Cardano Constitution: <https://github.com/IntersectMBO/cardano-constitution/tree/main/cardano-constitution-2>
