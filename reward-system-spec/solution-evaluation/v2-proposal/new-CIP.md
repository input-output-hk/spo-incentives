# Whiteboard — V2 reward distribution: ViabilityPackage channel + redesigned envelope

> **Status:** Exploratory draft 2026/04/26. Source material for a future CIP submission. To be challenged, rewritten, or discarded.
> **Scope:** Re-architect the macro epoch-pot split and the per-pool reward formula to address operator viability ([Guarantee operator viability across the entire productive population](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) and pledge as Sybil instrument ([Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators)) jointly, while keeping the two problems on **separate budget channels**.

## Executive summary

The current Shelley reward function distributes the entire $PoolsPot^{\text{epoch}}$ through a single per-pool envelope $E(\nu, \pi) = \lambda_{\text{size}} \cdot \nu + \lambda_{\text{pledge}} \cdot A(\nu, \pi)$. The four evaluated CIPs (CIP-0023, CIP-0082, CIP-0050, CIP-0037) intervene either on the **fee layer** (operator viability) or on the **stake-cap layer** (pledge signal) — never on both at once — and the synthesis explicitly frames them as alternatives, not stacks.

This whiteboard takes a different bet, organised around two architectural decisions:

- **Wager 1 — the two problems are one design, on two budget channels.** Operator viability ([Guarantee operator viability across the entire productive population](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) and pledge as Sybil instrument ([Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators)) must be designed jointly — a viability mechanism that ignores Sybil leaks, or a pledge mechanism that ignores small-operator viability, fails the same way. **But the budgets are separate**: the viability subsidy is a dedicated *channel* alongside the per-pool reward envelope, sized at the macro level by a new governance fraction $\mu$, never competing with delegator yield.
- **Wager 2 — the envelope reverts to Shelley two-term shape, with the pledge term redesigned.** The size mass $\lambda_{\text{size}} \cdot \nu$ is unchanged. The pledge mass $\lambda_{\text{pledge}} \cdot A$ keeps the constitutional encoding ($a_0$, no amendment) but $A$ itself is redesigned to peak at $\pi = 0.5$ with a plateau above — restoring the [delegation-as-counter-power](../the-intended-game/README.md#342-delegation-as-counter-power) accountability that the current Shelley peak-at-$\pi=1$ destroys.

The architecture introduces one new governance parameter ($\mu$, ViabilityPackage share of PoolsPot) and one redesigned pledge function ($A_{\text{new}}(\nu, \pi) = \nu \cdot 4 \bar\pi (1-\bar\pi)$ with $\bar\pi = \min(\pi, 0.5)$). $a_0$, $k$, $\rho$, $\tau$, and the SL-D1 outer structure $\bar p \cdot P_{\max} \cdot E$ are all retained. The whiteboard is the source draft for a forthcoming CIP submission; entity-level Sybil tax ([§3.2.2 R2](../README.md#322-specification)) is scoped out of this iteration's CIP and parked as a follow-up CIP that depends on a separate entity-identity primitive.

## 1. The coupling thesis

### 1.1. Why the dependency-chained reading fails

The current V2 reading orders the milestones as a chain: viability ([Guarantee operator viability across the entire productive population](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population)) precedes pledge ([Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators)) precedes delegator yield ([Maintain and diversify a competitive delegator yield](../../README.md#33-maintain-and-diversify-a-competitive-delegator-yield)) precedes concentration ([Reduce the concentration effects that distort both populations](../../README.md#34-reduce-the-concentration-effects-that-distort-both-populations)). The synthesis composes the candidate package the same way: *fee-layer first*, *stake-cap second*, *k raises last*.

Two structural objections emerge from re-reading the Diagnostic against the four CIP evaluations.

**Objection A — fee reform is not pledge-neutral.** A flat percentage floor (CIP-0082 stage 2 `minPoolRate`, or any ledger-level proportional cost) collapses the delegator fee-rate dispersion from 38× to 1.00× and reshapes the per-pool revenue gradient. That gradient is the same surface on which pledge-as-signal must live. Rewriting it without simultaneously rewriting the pledge component leaves the pledge instrument designed for a fee structure that no longer exists.

**Objection B — pledge reform is not viability-neutral.** CIP-0050 ($\sigma' = \min(\sigma, 1/k, L\cdot p)$) and CIP-0037 ($\text{sat}(p) = \text{orig\_sat} \cdot \max(e, \min(1/k, p/\text{orig\_sat}\cdot \ell))$) both gate eligible-stake on pledge. The retail single-pool operator (median pledge ratio ≈ 0.07%) is clipped to ~7% of the saturation ceiling at $L = 100$, or to the 20% floor at $e = 0.2$. In either case, **the viability gap that [Guarantee operator viability across the entire productive population](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population) seeks to close is mechanically widened by the very instrument that [Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators) is supposed to introduce**. The chain assumes the layers don't interact; the algebra says they do.

The conclusion is not that the V2 milestone ordering is wrong — it is that **the candidate reward function cannot be a stack**: the fee structure and the pledge structure are two cuts of the same surface and must be co-designed.

### 1.2. The unified problem statement

A reward function $f$ over a per-pool tuple $(\sigma, p, \pi)$ — with entity-level state acknowledged but its incorporation deferred (§4.4) — is a **coupled solution** if and only if:

> **C1 — Universal viability.** For every pool above the production threshold $\sigma_{\min}$, the operator share of $f$ exceeds a fiat-denominated viability cost across a stated ADA price range, *regardless of pledge level*. Custodial inability to pledge does not cross the viability boundary.
>
> **C2 — Material commitment signal.** The yield differential between meaningfully-committed and uncommitted operators is large enough to be visible to delegators (>0.5pp, per [Specification](../../README.md#322-specification)) and *increases with entity-level fleet size*, not pool-level pledge ratio.
>
> **C3 — Architectural recognition of the three populations.** Custodial operators (cannot commit own capital) and single-pool operators (commit capital out of conviction) are *not* mapped to the same reward branch. The function must distinguish *architectural inability* from *strategic choice* through a means other than pledge ratio alone.

A solution that satisfies C1 but not C2 collapses to CIP-0023/0082 — viable but Sybil-permissive. A solution that satisfies C2 but not C1 collapses to CIP-0050/0037 — anti-Sybil but capital-capability-biased. A solution satisfying C2 without C3 collapses custodial to "uncommitted" and reproduces the CIP-0050 zero-pledge break.

The whiteboard takes C1 ∧ C2 ∧ C3 as the **joint admissibility predicate** and asks: *what shape must $f$ take?*

## 2. Constraints inherited from V2

The proposal must satisfy a fixed set of constraints that come from the V2 specification, the Cardano Constitution, and the *Intended Game* security properties. They are not negotiable; they are the boundary conditions of the design space.

### 2.1. Hard constraints from the V2 specification

| Origin | Constraint | Quantitative target |
|---|---|---|
| [Structural: enforce the production threshold](../../README.md#312-structural-enforce-the-production-threshold) — production threshold | A minimum active-stake threshold $\sigma_{\min}$ must be defined and enforced; a sub-threshold pooling-service path must exist | $\sigma_{\min} \approx 1\text{M ADA}$ at current parameters; sub-threshold pool count → 0 |
| [Economic: every productive pool must be profitable](../../README.md#313-economic-every-productive-pool-must-be-profitable) — economic viability | Every pool at or above $\sigma_{\min}$ must generate operator revenue exceeding fiat operating cost; the floor must be proportional, not fixed | Operator viability rate >90% across the productive set; >50% at ADA = $0.10 |
| [§3.2.2 R1](../README.md#322-specification) — material pledge differential | Yield differential between pledged and unpledged pools must be visible to delegators | >0.5pp |
| [§3.2.2 R2](../README.md#322-specification) — entity-level pledge | Pledge must be evaluated at the entity level; an entity splitting capital across $n$ pools must not receive the aggregate benefit of $n$ independent pledges | Marginal pledge cost positive and increasing with $n$ |
| [§3.2.2 R3](../README.md#322-specification) — custodial recognition | The mechanism must distinguish architectural inability to pledge from strategic choice | Custodial population (CEX + IVaaS) must remain viable without pledging delegated capital |
| [§3.2.2 R4](../README.md#322-specification) — governable pledge | Pledge parameters must be reviewable through Conway-era governance, with awareness of fiat/ADA asymmetry | Parameter review cadence; oracle-informed adjustment instrument |

### 2.2. Hard constraints from the Cardano Constitution

| Parameter | Constitutional bound | Implication |
|---|---|---|
| $a_0$ (poolPledgeInfluence) | [0.1, 1.0] (PPI-01–04) | Any pledge-leveraged bonus must remain expressible within this range — or the bound itself must be widened by constitutional amendment |
| $k$ (saturation target) | [250, 2000] (SPTN-01–04) | The saturation surface remains a parameter, not a design variable |
| $minPoolCost$ | [0, 500] (MPC-01–03) | A residual fixed-floor instrument remains available; not all viability mechanisms require ledger-level rewrites |
| $\rho$ (monetary expansion) | [0.001, 0.005] (ME-01–05) | The funding envelope is bounded; the proposal must operate within the existing $R$ |
| $\tau$ (treasury cut) | [0.1, 0.3] (TC-01–05) | Treasury share is bounded; the proposal cannot fund itself by taking from the treasury without governance approval |

### 2.3. Security properties from *The Intended Game*

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
| Per-pool revenue regressive uplift | CIP-0023, CIP-0082 stage 2 | The marginal change in operator revenue between sub-reliable and saturated tiers must not exceed the change at the lower tier (no 50× tier amplification) |
| MPO fleet amplification | CIP-0023, CIP-0082 | The marginal benefit of the $(n+1)$-th pool to an $n$-pool entity must not be larger than the benefit to the 1st pool of an single-pool operator (current bundle: ~500× gap) |
| Capital-capability bias | CIP-0050, CIP-0037 | The activation threshold of any pledge-conditioned bonus must scale with pool size, not with absolute pledge — otherwise floor-exit is mechanically regressive |
| Zero-pledge discontinuity | CIP-0050 | The reward at $\pi = 0$ must be continuous and non-zero for pools that pass the production gate; custodial populations must not collapse |
| Custodial / strategic conflation | CIP-0050, CIP-0037 | The function must not treat custodial inability and MPO strategic non-pledging through the same reward branch |
| Pledge-bonus dormancy | Current Shelley | The bonus budget actually distributed must exceed a stated fraction of the budget allocated (current: <5% utilisation) |
| Fixed-cost fiat asymmetry | Current Shelley, persists in CIP-0023 | An ADA-denominated fixed floor that has no protocol-level awareness of ADA price drift is rejected (cost has fluctuated 10× since launch) |
| Parameter dormancy | Current Shelley ($a_0$) | A pledge parameter that is never adjusted post-deployment defeats the [§3.2.2 R4](../README.md#322-specification) governability requirement |

## 4. Architecture sketch — separate viability channel, simplified envelope

The whiteboard restructures the macro split of the epoch pot to take the viability injection out of the per-pool envelope $E$ entirely. The viability package becomes a *channel*, not an envelope component: a dedicated subsidy that flows directly to qualified operators without being subject to fee, margin, or delegator split. The envelope $E$ reverts to its current Shelley two-term form (size + pledge), with the pledge term redesigned per §4.4.

### 4.1. The macro split — viability as a separate channel inside PoolsPot

The current Shelley macro split assembles the epoch pot from three sources and divides it 80/20 between pools and treasury:

$$
Pot^{\text{epoch}} \;=\; Fee^{\text{epoch}}_{\text{tx}} \;+\; Deposit^{\text{epoch}}_{\text{nonRefundable}} \;+\; \min\!\left(\tfrac{Blocks^{\text{epoch}}_{\text{produced}}}{21,600},\, 1\right) \cdot 0.3\% \cdot \big(45\text{B} - Supply^{\text{system}}_{\text{circulating}}\big)
$$

$$
PoolsPot^{\text{epoch}} \;:=\; 80\% \cdot Pot^{\text{epoch}}, \qquad TreasuryPot^{\text{epoch}} \;:=\; 20\% \cdot Pot^{\text{epoch}}
$$

The whiteboard adds a second-tier split *inside* PoolsPot, partitioning it between a viability channel and the per-pool reward pot:

$$
\boxed{\;ViabilityPackage^{\text{epoch}} \;:=\; \mu \cdot PoolsPot^{\text{epoch}}\;}
$$
$$
RewardPot^{\text{epoch}} \;:=\; (1 - \mu) \cdot PoolsPot^{\text{epoch}}
$$

with $\mu \in [0, 1]$ a new governance parameter. Treasury is untouched. The choice $\mu = 0$ recovers current Shelley exactly (status quo). The whiteboard's working value is $\mu = 20\%$.

The constitutional handle is a single new top-level fraction $\mu$ — *not* a new envelope coefficient. The encoding of the per-pool reward stays at the existing Shelley form, with $a_0 \in [0.1, 1.0]$ alone parameterising the pledge influence. No constitutional amendment on the envelope is required; only a parameter-update action introducing $\mu$ as a governable fraction.

#### 4.1.1. Numerical sizing at $\mu = 20\%$

For mainnet at epoch 623 (per [treasury-and-pool-pots-distribution mainnet-analysis](../diagnostic/sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md)):

| Quantity | ADA/epoch | Share of $Pot^{\text{epoch}}$ |
|---|---:|---:|
| $Pot^{\text{epoch}}$ | ~19.2M | 100% |
| $PoolsPot^{\text{epoch}} = 0.80 \cdot Pot$ | ~15.4M | 80% |
| $TreasuryPot^{\text{epoch}} = 0.20 \cdot Pot$ | ~3.84M | 20% |
| $ViabilityPackage^{\text{epoch}} = \mu \cdot PoolsPot$ | ~3.08M | 16% |
| $RewardPot^{\text{epoch}} = (1-\mu) \cdot PoolsPot$ | ~12.3M | 64% |

For $N_q \approx 460$ qualified pools (the §3 [284 productive single-pool operators + ~176 viable MPO-attached pools](../diagnostic/sub-flows/census/mainnet-analysis/single-spo/README.md) baseline): per-pool injection $X_p = ViabilityPackage / N_q \approx 6700$ ADA/epoch ≈ **489K ADA/year**. At ADA = $0.10$ stress price ([§3.1.3 KPI](../README.md#313-economic-every-productive-pool-must-be-profitable) floor), that delivers ≈ $48,900/year per qualified operator — well above the [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour) lower-bound of ~$7,160/year. The pack at $\mu = 20\%$ is *generous*: it covers the cost floor and provides a real operator wage on top.

The implication: $\mu = 20\%$ is a working starting point, not a target. The actual calibration depends on what the design wants the pack to *cover* — bare cost floor, professional wage, or a graduated allocation between the two. See OQ7.

#### 4.1.2. Per-pool reward formula — outer structure

$$
\hat f'(\nu,\, \pi,\, \bar p) \;=\; \bar p \cdot P_{\max} \cdot E(\nu,\, \pi)
$$

with $P_{\max} = z_0 \cdot RewardPot^{\text{epoch}} = z_0 \cdot (1-\mu) \cdot PoolsPot^{\text{epoch}}$. The ceiling per pool is now $1-\mu$ times the current Shelley value — at $\mu = 20\%$, $P_{\max}$ shrinks by 20%. The envelope $E$ is the unchanged-shape Shelley two-term form (see §4.2).

Why $\bar p$ stays. The performance multiplier is the protocol's only on-chain signal of *delivered* work in the current epoch. Conditioning the per-pool envelope on it preserves three structural properties: sub-threshold pools cannot earn (Poisson-sparse production drives $\bar p \to 0$), absentee operators cannot earn, and the per-pool envelope is gated by demonstrated production. $\bar p$ is a precondition, not a parameter — it remains identical to current Shelley.

#### 4.1.3. ViabilityPackage distribution — outline

The package is distributed to pools that satisfy two gates: the structural production threshold ($\nu \geq \nu_{\min}$) and the per-epoch production gate ($n_t \geq 1$ — pool produced at least one block in the current epoch, using SL-D1's existing $n$ variable). The distribution rule is the subject of §4.3 (where pack form, phase-out, and properties are treated). Because the package lives *outside* the per-pool reward formula, its distribution is freely shaped — no convex-coefficient constraint with $\lambda_{\text{size}}$ or $\lambda_{\text{pledge}}$, no impact on delegator yield channels.

#### 4.1.4. Notation against SL-D1

The proposed signature extends SL-D1 §5.5.1 Eq.(1) without breaking it.

| Symbol | Meaning | SL-D1 origin |
|---|---|---|
| $\sigma$ | Pool's relative stake (fraction of total stake) | SL-D1 §5.5.1 |
| $\nu = \sigma / z_0$ | Pool's stake normalised to the saturation cap $z_0 = 1/k$ | Diagnostic §2.3 (normalised coordinate) |
| $\pi = s' / \sigma'$ | Within-pool pledge ratio (capped pledge over capped stake) | Derived from SL-D1 $s', \sigma'$ |
| $n$ | Blocks produced *by the pool, in the current epoch* | SL-D1 §5.5.1 |
| $\overline{N}$ | Total blocks added to the chain in the current epoch | SL-D1 §5.5.1 |
| $\beta = n / \max(1, \overline{N})$ | Pool's per-epoch block share | SL-D1 §5.5.1 Eq.(1) |
| $\bar p = \beta / \sigma$ | Apparent performance | SL-D1 §5.5.1 |
| $\mu$ | ViabilityPackage share of PoolsPot (new governance parameter) | Top-level addition |

**No new ledger state.** The ViabilityPackage channel uses the per-epoch block count $n$ (already exposed by SL-D1 §5.5.1 in the derivation of $\bar p$) for its eligibility gate. No cumulative or lifetime counter is required. The only addition to the protocol parameter set is $\mu$ — a single rational fraction governable through Conway parameter-update actions.

### 4.2. The envelope $E$ — Shelley two-term form retained

With viability promoted to a separate channel (§4.1), the envelope $E$ that distributes $RewardPot^{\text{epoch}}$ across pools reverts to the Shelley two-term shape:

$$
E(\nu, \pi) \;=\; \lambda_{\text{size}} \cdot \nu \;+\; \lambda_{\text{pledge}} \cdot A(\nu, \pi)
$$

with the standard Shelley constitutional encoding:

$$
\lambda_{\text{size}} \;=\; \frac{1}{1 + a_0}, \qquad \lambda_{\text{pledge}} \;=\; \frac{a_0}{1 + a_0}, \qquad a_0 \in [0.1,\, 1.0]
$$

| Term | Role | Maps to | Change vs. current Shelley |
|---|---|---|---|
| $\lambda_{\text{size}} \cdot \nu$ | **Size mass** — stake-accessible component | [Maintain and diversify a competitive delegator yield](../../README.md#33-maintain-and-diversify-a-competitive-delegator-yield) | Unchanged shape; ceiling reduced by factor $(1-\mu)$ |
| $\lambda_{\text{pledge}} \cdot A(\nu, \pi)$ | **Pledge mass** — commitment instrument | [Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators) | $A$ redesigned (see §4.4); coefficient encoding unchanged |

The **substantive simplification**: the envelope no longer carries a viability term. The convex constraint at the envelope level is the existing two-coefficient constraint $\lambda_{\text{size}} + \lambda_{\text{pledge}} = 1$. The viability budget is sized by $\mu$ (the macro split of §4.1), not by an envelope coefficient.

This decouples three concerns that previously shared one budget surface:

- **Viability** ($X$) is sized by $\mu$ at the macro level — bounded by $\mu \cdot PoolsPot$.
- **Delegator base yield** is shaped by $\lambda_{\text{size}}$ at the envelope level — bounded by $RewardPot \cdot 1/(1+a_0)$.
- **Pledge commitment bonus** is shaped by $\lambda_{\text{pledge}}$ — bounded by $RewardPot \cdot a_0/(1+a_0)$.

Each is governable independently. Raising $\mu$ (more viability) reduces $RewardPot$ proportionally — both the size and pledge terms shrink in absolute ADA. Raising $a_0$ (more pledge influence) reshapes the size/pledge split inside $E$ — without touching the viability channel.

### 4.3. The ViabilityPackage channel — pack distribution rule

The ViabilityPackage channel is the budget pot $\mu \cdot PoolsPot^{\text{epoch}}$ that flows directly to qualified operator reward accounts, parallel to (not part of) the per-pool envelope. The channel is defined by three rules: who qualifies (eligibility), how much each qualified pool receives (injection rule), and how the budget closes (sizing identity).

**Pack distribution form.** A qualified pool $p$ receives, per epoch:

$$
\boxed{\;X_p \;=\; X_0 \cdot \max\!\big(0,\, 1 - \tfrac{\nu_p - \nu_{\min}}{\nu^* - \nu_{\min}}\big) \cdot \mathbb{1}[\nu_p \geq \nu_{\min}] \cdot \mathbb{1}[n_t(p) \geq 1]\;}
$$

where:
- $X_0$ is the **peak pack** in ADA/epoch — the injection granted to a pool sitting just above the production threshold.
- $\nu^*$ is the **phase-out terminal** — pools at or above $\nu^*$ receive zero pack.
- $n_t(p) \geq 1$ is the **per-epoch production gate** — the pool must have produced ≥ 1 block *in the current epoch* (using SL-D1 §5.5.1's existing $n$ variable; no new ledger state).
- $\mathbb{1}[\nu \geq \nu_{\min}]$ is the **structural production threshold gate** ([§3.1.2 R1](../README.md#312-structural-enforce-the-production-threshold)).

The pack is *not* gated by $\bar p$ as a multiplier — it is gated by $n_t \geq 1$ as an indicator. A pool that produces at least one block in the epoch qualifies, regardless of whether $\bar p$ is high or low.

#### 4.3.1. Why the per-epoch production gate

The per-epoch gate ($n_t \geq 1$) composes with the production threshold ($\nu \geq \nu_{\min}$) to form a two-layer admission system:

- $\nu_{\min}$ — *can produce* (Poisson feasibility — at saturation $\lambda \approx 43$ blocks/epoch, at threshold $\lambda \approx 1$). [§3.1.2 R1](../README.md#312-structural-enforce-the-production-threshold) requires this to become explicit and enforced.
- $n_t \geq 1$ — *did produce, this epoch* (empirical confirmation, evaluated each epoch).

Four properties follow:

- **Demonstrated, not declared.** Registering a pool costs ~500 ADA and a configuration file; *producing a block in the current epoch* requires sustained operational capability — the relays must be online, the keys must be live, the slot leadership must be honoured. The gate filters the *active* productive cohort.
- **No new ledger state.** SL-D1 §5.5.1 already exposes $n$ (per-epoch block count) as an observable input to $\bar p$. The per-epoch gate consumes the same variable. No new $n^{\text{cum}}$ counter is required. The pack mechanism adds zero state to the ledger beyond the parameter $\mu$.
- **Sybil-resistant by Poisson.** An entity that registers a Sybil pool at exactly $\nu_{\min}$ has $\lambda = 1$ block/epoch, so $P(n_t \geq 1) \approx 63\%$. The pool collects the pack only ~2 epochs out of 3. This is a real, structural cost on fragmentation — see §4.4.
- **Variance is real, but bounded.** A small pool legitimately at the production threshold misses the pack ~37% of epochs. The pack is therefore a *probabilistic* income, not a guaranteed one. Larger pools (above viability threshold ~3M ADA, $\lambda \geq 3$) collect ≥ 95% of epochs.

#### 4.3.2. Empirical N_q and budget closure

The eligible-set size $N_q$ in any given epoch is the count of pools satisfying both gates simultaneously. From the diagnostic ([census/mainnet-analysis/README.md L234](../diagnostic/sub-flows/census/mainnet-analysis/README.md), [pools-distribution/mainnet-analysis/README.md L1410](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md), [single-spo/README.md](../diagnostic/sub-flows/census/mainnet-analysis/single-spo/README.md)) at epoch 623:

| Population | Count above $\nu_{\min}$ | Expected ≥ 1 block per epoch |
|---|---:|---:|
| All pools (single-SPO + MPO-attached) | 733 | **~900** |
| → Above viability threshold (≥3M ADA, $\lambda \geq 3$) | 731 | ~720 (≥ 95%) |
| → Marginal (1M–3M, $\lambda \in [1, 3]$) | 220 | ~180 (63–95%) |
| Single-SPO only | 477 | ~440 |

The working baseline is $N_q \approx 900$.

The budget identity:

$$
ViabilityPackage^{\text{epoch}} \;=\; \mu \cdot PoolsPot^{\text{epoch}} \;=\; \sum_{p \in N_q} X_p
$$

For uniform $X_p = X_0$ (no phase-out) the sum reduces to $N_q \cdot X_0$, giving $X_0 = \mu \cdot PoolsPot / N_q$. For the linear phase-out, the closed form depends on the population distribution of $\nu$ across $[\nu_{\min}, \nu^*]$ — see §4.3.4 for the worked example.

For the working configuration $\mu = 20\%$, $N_q \approx 900$, $PoolsPot \approx 15.4$M ADA/epoch:

| Quantity | Value |
|---|---:|
| ViabilityPackage budget per epoch | $\sim 3.08$M ADA |
| Per-pool flat injection ($X_p = \mu \cdot PoolsPot / N_q$) | $\sim 3,420$ ADA/epoch |
| Annualised per pool (73 epochs/year) | $\sim 250$K ADA/year |
| At ADA = $0.10$ (V2 stress price) | $\sim$ \$25,000/year per qualified pool |

This **clears the §4.5 lower bound** of \$7,160/year operator floor with margin — covering infrastructure plus skilled labour at standard DevOps rates plus a credible part-time wage. At higher ADA prices, the surplus grows: at ADA = $1.00$, the same 250K ADA/year delivers ~$250K/year per operator.

#### 4.3.3. Two-tier coverage decomposition

The pack quantity $X_p$ is not an opaque ADA figure — it is the protocol's response to a fiat-denominated operating cost that decomposes into two semantically distinct tiers, taken from the diagnostic [§4.5 — *Is operator revenue competitive?*](../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#45-is-operator-revenue-competitive--a-market-benchmark) and finding [OPE.O6.F4](../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#454-implications).

**Tier 1 — Infrastructure cost ($C_{\text{infra}}$).** Hardware, hosting, network, monitoring required to run one block producer + two relays + monitoring/DNS/backups. Per [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour): **\$110–270/month** (\$1,320–3,240/year), VPS or bare-metal benchmarks (Hetzner, OVH, Contabo, AWS Lightsail, Q1 2026). Machine-amortisable, drifts slowly, supplier-priced.

**Tier 2 — Human time cost ($C_{\text{human}}$).** Skilled hours for monitoring, upgrades, security, governance. Per [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour): **5–15 hours/month**, with hard-fork spikes. DevOps/SRE rates (ZipRecruiter, Salary.com, PayScale, 2026):

| Role | Hourly rate (USD) |
|---|---:|
| DevOps / Sysadmin (junior) | \$43–67 |
| SRE / DevOps Engineer (mid) | \$64–78 |
| Senior DevOps Engineer | \$72–86 |

Lower bound (10 hrs/mo × \$43/hr): **\$5,160/year**. Upper bound (20 hrs/mo × \$86/hr) ≈ \$20,000/year.

**Total fiat operating cost.** [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour) cites a conservative lower-bound of **~\$7,160/year** (\$2,000 mid-range infra + \$5,160 labour at the lowest market rate). Below this, the operator donates skilled labour to the network — the structural condition finding [OPE.O6.F4](../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#454-implications) names.

##### The coverage identity

At ADA-price anchor $e$ (USD per ADA), the pack must cover both tiers:

$$
\boxed{\;X_0^{\text{ADA/epoch}} \cdot e \;\geq\; \tfrac{1}{12}(C_{\text{infra}}^{\text{USD/month}} + C_{\text{human}}^{\text{USD/month}}) \cdot \tfrac{12}{73}\;}
$$

(The factor $12/73$ converts USD/month to USD/epoch with 73 epochs/year.) Combined with the budget identity $\mu \cdot PoolsPot = \sum_p X_p$, this links the macro split parameter $\mu$ to the fiat operating-cost stack via the population $N_q$ and the phase-out shape.

##### Properties

The viability channel must satisfy nine properties.

**P1 — Two-tier additive decomposition.** $X_0 = X_{\text{infra}} + X_{\text{human}}$ at the calibration level: each tier is independently inspected, reviewed, and updated. Mirrors [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour).

**P2 — Coverage identity.** At the chosen anchor price $e$, $X_0 \cdot e$ covers $C_{\text{infra}}^{\text{USD}} + C_{\text{human}}^{\text{USD}}$ per epoch.

**P3 — Price-range robustness.** Coverage holds across the stated ADA-price range $[e_{\min}, e_{\max}]$. Four anchoring rules. *(a) Floor-anchored* — $X_0$ calibrated at $e_{\min}$ (overpayment above). *(b) Reference-anchored* — calibrated at $e_{\text{ref}}$ (breaks at extremes). *(c) Oracle-anchored* — $X_0(t) \propto 1/e(t)$ each epoch. *(d) Governance-rebalanced* — $X_0$ stays ADA-fixed inside a managed range; if price breaches the range, governance lifts $\mu$ to maintain coverage. Choice = OQ1.

**P4 — Stress-price compliance.** $e_{\min}$ ≤ V2 stress floor ADA = \$0.10 ([§3.1.3 KPI](../README.md#313-economic-every-productive-pool-must-be-profitable)). Spot at \$0.25 (April 2026), so stress floor is 2.5× below.

**P5 — Independent tier governance.** $C_{\text{infra}}$ and $C_{\text{human}}$ are *separately* parameter-update-grade. Different review cadences: hardware costs slow, labour costs sensitive to regional wage shifts.

**P6 — Budget-closure consistency.** $\mu \cdot PoolsPot = \sum_{p \in N_q} X_p$ holds in expectation. Raising the per-pool target $X_0$ without compensating $\mu$ shrinks $N_q$ (budget pressure tightens the qualified set, or per-pool dilution kicks in). Explicit, governable trade-off.

**P7 — Pledge stability under stress rebalance.** When P3 rule (d) fires, governance lifts $\mu$ — *not* $a_0$. The envelope's pledge mass $\lambda_{\text{pledge}} = a_0/(1+a_0)$ is held constant under price stress, so the Sybil-tax mass backing [Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators) does not degrade with market conditions. Delegators absorb the shock through reduced size mass ($P_{\max}$ shrinks proportionally to $1-\mu$); the security mechanism is decoupled from price.

##### Governance-grade price stabilization (P3 rule d), restated for the channel architecture

In the previous (envelope-coupled) framing, stabilization required a coupled $(a_0, b_0)$ update bounded by the PPI guardrail $a_0 \leq 1$. With the channel architecture, **stabilization is a single-lever operation on $\mu$**:

$$
\mu_{\text{stress}} \;=\; \mu_{\text{nominal}} \cdot \tfrac{e_{\text{nominal}}}{e_{\text{stress}}}
$$

To keep $X_0$ in ADA at constant fiat coverage when price drops by factor $r$, raise $\mu$ by factor $r$. The constitutional handle is $\mu \in [0, \mu_{\max}]$, with $\mu_{\max}$ a guardrail to be set in the CIP. The previous bound $\lambda_{\text{viability}} \leq 0.20$ (driven by the PPI ceiling) no longer applies — $\mu$ has its own range.

| Stress level | $\mu$ | ViabilityPackage / epoch | $X_0$ at $N_q = 900$ |
|---|---:|---:|---:|
| Nominal | 0.20 | 3.08M ADA | 3,420 ADA/epoch |
| Price drops 2.5× → keep coverage | 0.50 | 7.7M ADA | 8,550 ADA/epoch |
| Price drops 5× | 1.0 | 15.4M ADA | 17,100 ADA/epoch |
| Beyond | > 1.0 | (impossible — $\mu$ can't exceed PoolsPot) | — |

The channel architecture shifts the *range* of $\mu$ to be the binding constraint. At $\mu = 1$, the entire PoolsPot is consumed by the viability channel — the per-pool envelope $E$ receives nothing, delegators earn zero base yield. This is the absolute ceiling. In practice, governance would not approach this bound — it indicates a sustained sub-$0.10$ ADA price scenario where the V2 economics are themselves under question.

The political framing is unchanged: delegators (size mass) absorb the shock; operators (viability channel) retain coverage; Sybil resistance (pledge mass) is preserved.

##### Numerical anchor — aligned with §4.5

Taking the [The cost of operating a pool — infrastructure and labour](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#451-the-cost-of-operating-a-pool-infrastructure-and-labour) low / mid / high cost stack:

| Quantity | Low | Mid | High |
|---|---:|---:|---:|
| $C_{\text{infra}}^{\text{USD/month}}$ | 110 | 190 | 270 |
| $C_{\text{human}}^{\text{USD/month}}$ (10 hrs × \$43 / 12 × \$65 / 15 × \$86) | 430 | 780 | 1290 |
| $C_{\text{op}}^{\text{USD/month}}$ | 540 | 970 | 1560 |
| $C_{\text{op}}^{\text{USD/year}}$ | 6,480 | 11,640 | 18,720 |
| Required $X_0^{\text{ADA/year}}$ at ADA = \$0.10 (stress) | 64,800 | 116,400 | 187,200 |
| Required $X_0^{\text{ADA/year}}$ at ADA = \$0.25 (spot) | 25,920 | 46,560 | 74,880 |
| Required $X_0^{\text{ADA/year}}$ at ADA = \$1.00 | 6,480 | 11,640 | 18,720 |
| Required $X_0^{\text{ADA/epoch}}$ at ADA = \$0.10 | 888 | 1,595 | 2,564 |

The working configuration ($\mu = 20\%$, $N_q = 900$) delivers $X_0 \approx 3,420$ ADA/epoch — sitting **above the high anchor** at the stress price. The pack at $\mu = 20\%$ is generous; a tighter calibration ($\mu \approx 12\%$) would land precisely on the §4.5.1 mid-range cost target. The CIP draft will need to converge on a specific value; $\mu = 20\%$ remains a working figure.

#### 4.3.4. Phase-out shape and the monotonicity invariant

The pack design imposes two coupled requirements on the phase-out: *the injection must decay as the pool grows* (anti-regressive intent), and *the operator must always benefit from growing* (no perverse incentive to stay small). The two requirements resolve to a closed bound once $X_0$, $\nu^*$, and the envelope coefficients are fixed.

##### Phase-out shape

Linear ramp from $X_0$ at the production threshold to $0$ at the terminal $\nu^*$:

$$
X_p(\nu) \;=\; X_0 \cdot \max\!\big(0,\, 1 - \tfrac{\nu - \nu_{\min}}{\nu^* - \nu_{\min}}\big) \cdot \text{(eligibility gates)}
$$

The pack concentrates where it is needed:

- *Below $\nu_{\min}$* — sub-threshold, ineligible
- *At $\nu_{\min}$* — peak pack $X_0$
- *Between $\nu_{\min}$ and $\nu^*$* — degressive linear ramp
- *At or above $\nu^*$* — zero pack

Above $\nu^*$, the operator earns reward through the envelope only ($\lambda_{\text{size}} \cdot \nu + \lambda_{\text{pledge}} \cdot A$).

##### The monotonicity invariant

The operator's total per-epoch reward sums two channels:

$$
f_{\text{total}}(\nu, \pi) \;=\; \underbrace{\bar p \cdot P_{\max} \cdot E(\nu, \pi)}_{\text{envelope (RewardPot)}} \;+\; \underbrace{X_p(\nu) \cdot \mathbb{1}[\text{eligible}]}_{\text{ViabilityPackage channel}}
$$

with $P_{\max} = (1-\mu) \cdot PoolsPot / k$ — the per-pool ceiling reduced by factor $(1-\mu)$ relative to current Shelley.

For monotonic growth across the phase-out region (with $\bar p \approx 1$, ignoring the small pledge contribution which is itself monotone in $\nu$ for the new $A$):

$$
\frac{\partial f_{\text{total}}}{\partial \nu} \;=\; P_{\max} \cdot \big[\lambda_{\text{size}} + \lambda_{\text{pledge}} \cdot \tfrac{\partial A}{\partial \nu}\big] \;-\; \frac{X_0}{\nu^* - \nu_{\min}} \;>\; 0
$$

Ignoring $\lambda_{\text{pledge}} \cdot \partial A/\partial \nu \geq 0$ (always non-negative — slack in the bound), the binding constraint is:

$$
\boxed{\;\nu^* - \nu_{\min} \;>\; \frac{X_0}{P_{\max} \cdot \lambda_{\text{size}}}\;}
$$

In words: *the phase-out distance must exceed the ratio of pack height to size-mass per unit ν*. A pool growing past $\nu^*$ recovers, in size-mass gain, more than it loses in pack drop-off.

##### Numerical instantiation

For the working configuration: $\mu = 20\%$, $a_0 = 0.3$ (current Shelley value), $PoolsPot \approx 15.4$M ADA/epoch, $k = 500$, $X_0 = 3,420$ ADA/epoch, $N_q = 900$:

- $P_{\max} = (1 - 0.20) \cdot 15.4\text{M} / 500 = 24,640$ ADA/epoch per saturated pool
- $\lambda_{\text{size}} = 1/(1 + 0.3) = 0.769$
- Bound: $\nu^* - \nu_{\min} > 3,420 / (24,640 \cdot 0.769) \approx 0.180$

In absolute stake ($z_0 \approx 67$M ADA): $\nu^* > \nu_{\min} + 0.180 \cdot 67\text{M} \approx 13$M ADA.

A natural choice aligned with the [9-tier taxonomy](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md) is to terminate the phase-out at the *Healthy*-to-*Healthy-Plus* boundary (~15M ADA), giving $\nu^* \approx 0.224$ — comfortably above the monotonicity floor of 0.180.

| Pool tier | Stake range | Pack at start of tier | Pack at end of tier |
|---|---|---:|---:|
| Sub-Viable | < 1M | n/a (production gate) | n/a |
| Marginal | 1–5M | 3,420 ADA/epoch (peak) | ~2,420 ADA/epoch |
| Healthy | 5–15M | ~2,420 ADA/epoch | 0 (terminal) |
| Healthy-Plus | 15–50M | 0 | 0 |
| Saturated | 50–67M | 0 | 0 |

The pack covers exactly the under-supported population (Marginal + Healthy) and disengages cleanly above.

##### Property added

**P8 — Strict size-monotonicity inside the production zone.** $\partial f_{\text{total}} / \partial \nu > 0$ holds for every $\nu \in [\nu_{\min}, 1]$, modulo the A-pathology inherited from current Shelley (cf. [solution-evaluation/pools-distribution/README §2.2](../solution-evaluation/pools-distribution/README.md): non-monotonicity in $\pi$ for $\nu < 0.5$, which the new $A$ partially fixes — see §4.4). Equivalently: for any $X_0$ and $\mu$ chosen by governance, the phase-out terminal must satisfy $\nu^* - \nu_{\min} > X_0 / (P_{\max} \cdot \lambda_{\text{size}})$. This prevents the design from rewarding pools that stay small for the comfort of the pack.

##### Design knobs the property exposes

The monotonicity bound and the budget identity give governance four coupled levers:

| Knob | Effect on the pack | Effect on the rest |
|---|---|---|
| Raise $\mu$ | Larger ViabilityPackage budget — either raise $X_0$ or extend $\nu^*$ | $P_{\max}$ shrinks; envelope (size + pledge) compresses; delegator yield drops |
| Raise $X_0$ | Per-pool support stronger at threshold | Tightens monotonicity bound; $\nu^*$ must grow proportionally |
| Push $\nu^*$ outward | Phase-out covers larger tier | Per-pool average drops (more pools sharing the same budget) |
| Tighten $\nu^*$ inward | Pack focuses on smallest tier | Risks monotonicity violation if $X_0$ stays high |

Three independent paths: $\mu$ (budget), $X_0$ (intensity), $\nu^*$ (coverage breadth). The CIP draft must pick a calibration on these three; the working configuration $(\mu = 20\%, X_0 \approx 3,420, \nu^* = 15\text{M})$ is illustrative.

#### 4.3.5. Edge cases and parameters to resolve

The pack framing leaves four sub-questions. They do not gate the architecture's feasibility but they shape its calibration.

- **Variance and sparsity at the threshold.** The per-epoch gate $n_t \geq 1$ means a pool at production threshold ($\lambda \approx 1$ block/epoch) misses the pack ~37% of epochs (Poisson). Above viability ($\lambda \geq 3$), miss rate < 5%. Three handling options. *(a) Accept as feature* — the variance is a Sybil tax on fragmentation (OQ5 stance). *(b) Multi-epoch window* — replace $\mathbb{1}[n_t \geq 1]$ with $\mathbb{1}[\sum_{e=t-N+1}^t n_p(e) \geq 1]$ for some $N$, smoothing the qualification over $N$ epochs. *(c) Reduced X near threshold* — taper the pack itself for very-low-$\lambda$ pools to acknowledge the productivity uncertainty. The whiteboard's working choice is (a); (b) is the OQ5 alternative.
- **Re-entry behaviour.** If a pool deregisters and re-registers, the per-epoch gate reapplies naturally (the new pool starts with $n_t = 0$ in its first epoch). No carry-over question — unlike the lifetime gate that the early draft considered.
- **Denomination of $X_0$.** Three options. *(a)* ADA-fixed: governable but drifts with price (same pathology as current $minPoolCost$). *(b)* Fiat-anchored via oracle: addresses [§3.1.3 R3](../README.md#313-economic-every-productive-pool-must-be-profitable) directly but introduces an oracle dependency. *(c)* Hybrid: ADA-fixed with periodic governance review against a fiat reference. The governance-grade rebalance of §4.3.3 (P3 rule d) is a (c)-class instrument operating on $\mu$.
- **Per-pool target vs dilution.** Two budget-rule alternatives. *(i) Target-fixed*: $X_0$ set as governance parameter; if $N_q \cdot X_0 > \mu \cdot PoolsPot$, the system either tops up from reserve or dilutes proportionally. *(ii) Dilution-floating*: $X_0 = \mu \cdot PoolsPot / N_q$ derived from budget closure; $X_0$ varies with $N_q$ each epoch. The whiteboard adopts (ii) for simplicity — automatic Sybil dilution defence (cf. §4.4) — but (i) is preferable if $X_0$ stability matters for operator planning.

#### 4.3.6. Fallback alternatives if the pack does not pan out

If the per-epoch-gate + linear-phase-out design hits a blocker, four continuous-form alternatives remain available as channel-distribution rules:

| Form | Functional shape (per pool, in the channel) | Behaviour |
|---|---|---|
| V1 — Equal-share | $X_p = \mu \cdot PoolsPot / N_q \cdot \mathbb{1}[\nu \geq \nu_{\min}]$ | Equipartition over the productive set (no per-epoch gate, no phase-out) |
| V2 — Threshold ramp | Linear ramp without per-epoch gate | Smooths over Poisson variance; less Sybil resistance |
| V3 — Fiat-anchored continuous | $X_p \propto C_{\text{fiat}} / e(t)$ via oracle each epoch | Continuous fiat-indexed; oracle dependency |
| V4 — Saturation-decreasing | $X_p = X_0 \cdot (1 - \nu / \nu_{\text{sat}})$ | Smooth, larger for small pools, zero at saturation; no hard terminal |

The whiteboard's working hypothesis is *linear ramp with per-epoch gate $n_t \geq 1$*. The fallbacks differ along two dimensions: (i) whether the qualifying gate is per-epoch ($n_t$) or structural only ($\nu \geq \nu_{\min}$), and (ii) whether the per-pool injection is flat (V1), declining linearly with a hard terminal (working hypothesis, V2), continuous-fiat (V3), or saturation-tapered without terminal (V4).

### 4.4. The pledge term $A$ — redesign with 50/50 saturation and a plateau

The current $A(\nu, \pi) = \nu^2 \pi [1 - \pi(1 - \nu)]$ has its peak at $(\nu = 1,\, \pi = 1)$ — *saturated, fully self-pledged*. That endgame is exactly what the Cardano consensus model is **not** designed to reward: a 100%-pledged saturated pool is a *private* pool, with no external delegation and therefore no [delegation-as-counter-power](../the-intended-game/README.md#342-delegation-as-counter-power) accountability mechanism. The Intended Game [The structural requirement](../the-intended-game/README.md#346-the-structural-requirement) explicitly requires *both* meaningful operator commitment (pledge) *and* meaningful external delegation; pledge alone destroys the second leg, and the reward function should not pay for it.

The whiteboard redesigns $A$ to **saturate at $\pi = 0.5$ and plateau above** — a concave rise from $\pi = 0$ that delivers most of the bonus by 20%, levels off as it approaches 50%, and stays at the maximum for any pledge above 50%:

$$
\boxed{\;A_{\text{new}}(\nu, \pi) \;=\; \nu \cdot 4 \bar\pi (1 - \bar\pi),\qquad \bar\pi = \min(\pi,\, 0.5)\;}
$$

This is the rising half of a parabola, capped at its peak. It is C¹-continuous at $\pi = 0.5$ (the slope vanishes there and stays zero), the factor $\nu$ (linear, *not* $\nu^2$) removes the small-pool quadratic penalty diagnosed in [solution-evaluation/pools-distribution/README §2.2.1](../solution-evaluation/pools-distribution/README.md).

#### 4.4.1. Why this shape

Four structural properties motivate the redesign jointly:

- **Concave in $[0, 0.5]$.** The marginal reward of adding pledge is *steepest at low pledge* and *shallowest near 50%*. An operator at $\pi = 0.05$ already extracts 19% of the maximum; at $\pi = 0.20$, 64%; at $\pi = 0.40$, 96%. Reaching the optimum is an *attainable target* rather than a distant ceiling.
- **Plateau above 50%.** Any pledge beyond 50% earns no marginal bonus. A 100%-pledged pool is *not penalised* — it earns the same $A$ as a 50/50 pool — but it has committed twice the capital for the same reward. The economic gradient pushes toward 50/50 without forbidding ideological full-pledge configurations.
- **Zero at $\pi = 0$.** The custodial branch still earns nothing on this term. It reaches viability through $V$, by design (cf. §4.3 and [§3.2.2 R3](../README.md#322-specification)).
- **Linear in $\nu$.** Replaces the quadratic outer factor $\nu^2$. A pool at half-saturation now earns half the pledge bonus, not a quarter. Small pools are no longer doubly-penalised.

#### 4.4.2. Impacts on operator strategy

The redesign produces measurable shifts across the eight relevant configurations:

| Configuration | Current $A_{\text{Shelley}}$ | New $A_{\text{new}}$ | Direction |
|---|---:|---:|---|
| Saturated, fully self-pledged ($\nu=1,\pi=1$) | 1.000 | 1.000 | Same value — but *no longer peak* |
| Saturated, 50/50 ($\nu=1,\pi=0.5$) | 0.500 | **1.000** | New peak (with plateau) |
| Saturated, 20/80 ($\nu=1,\pi=0.2$) | 0.200 | 0.640 | 3.2× larger |
| Saturated, custodial ($\nu=1,\pi=0$) | 0.000 | 0.000 | Unchanged — covered by $V$ |
| Healthy 50/50 ($\nu \approx 0.22,\pi=0.5$) | 0.054 | 0.224 | 4× larger |
| Marginal 50/50 ($\nu \approx 0.045,\pi=0.5$) | 0.0023 | 0.045 | ~20× larger |
| Saturated, retail pledge ($\nu=1,\pi=0.0007$) | 0.0007 | 0.0028 | 4× larger |
| MPO fragmenting at $\pi=0.05$ across many pools | $\approx 0.05$ each | $\approx 0.19$ each | 4× larger ⚠ |

Eight implications follow from this table.

**I1 — The dominant strategy moves to 50/50.** The optimum shifts from *(ν=1, π=1)* to the entire plateau $(ν=1, \pi \geq 0.5)$. The cheapest point on the plateau is $\pi = 0.5$ — the operator who reaches it has minimised committed capital for maximum bonus. The rational target is to attract enough delegation to reach 1:1 with their pledge.

**I2 — Private pools are economically inert, not penalised.** A 100%-pledged saturated pool earns the same $A$ as a 50/50 pool ($A = 1$). The reward function does not actively punish over-pledging — it simply stops rewarding it. The full-pledge operator has *immobilised twice the capital* for the same return, which represents the opportunity cost of capital better deployed elsewhere (DeFi, second pool, ADA appreciation thesis). The signal is economic gradient, not prohibition.

**I3 — The custodial branch is unchanged on this term.** A custodial pool ($\pi = 0$) still earns $A_{\text{new}} = 0$ — same as current Shelley. The custodial population reaches viability through $V$ and forgoes the commitment bonus by business-model choice. The architectural distinction of [§3.2.2 R3](../README.md#322-specification) is preserved.

**I4 — Small pools are decisively un-penalised.** The shift from $\nu^2$ to $\nu$ multiplies the commitment bonus at the Healthy tier by 4×, at Marginal by 20×, at Sub-reliable by 50× (at the 50/50 plateau). Combined with the V pack, this is the structural answer to capital-capability bias: a Marginal-tier operator pledging 50% of their pool's stake earns a *visible* yield differential, exactly what [§3.2.2 R1](../README.md#322-specification) requires.

**I5 — Delegation-as-counter-power is restored.** Under $A_{\text{new}}$, the operator economically *needs* delegators to reach the plateau without over-committing capital. A pool that fails to attract delegation is structurally pushed below the plateau, reducing yield per ADA pledged. This re-establishes the accountability loop [The Intended Game §3.4.2](../the-intended-game/README.md#342-delegation-as-counter-power) describes.

**I6 — Yield-differential to delegators becomes visible at low pledge already.** Because the curve is concave, even modest pledge (π = 0.10–0.20) extracts 36–64% of the maximum bonus. A pool at $\pi = 0.20$ vs a pool at $\pi = 0$ produces a yield gap delegators can read. The dormant pledge-bonus budget (95.6% return-to-reserve per [POL.O7](../diagnostic/README.md)) becomes a contestable economic dimension *for retail operators*, not just for whales.

**I7 — Pledge-bonus utilisation should rise materially.** The plateau means saturating-pool operators no longer face an unreachable target (77M ADA pledge). They reach the maximum at 33.5M and are inert above. The fraction of the $\lambda_{\text{pledge}}$ budget actually distributed should rise from <5% (current) toward [§3.2.2 KPI](../README.md#322-specification) target >50%.

**I8 — A subtle Sybil-tax concern emerges at very-low pledge.** The concave shape near $\pi = 0$ behaves like $4\pi$, *four times* the slope of the current Shelley $\pi$ (linear at saturation). An MPO fragmenting capital across many pools at uniformly low π earns *more* commitment bonus per pool under the new shape than under the current one. This is the opposite of the [§3.2.2 R2](../README.md#322-specification) entity-level Sybil tax. The redesign does not, on its own, strengthen the Sybil property — it makes the bonus accessible to small pools by softening the very-low-pledge edge. The Sybil tax remains an entity-level concern that requires the deferred §4.4.3 primitive.

#### 4.4.3. What stays deferred

Two structural concerns are still out of scope for this whiteboard iteration:

- **Entity-level evaluation ([§3.2.2 R2](../README.md#322-specification)).** $A_{\text{new}}$ remains pool-local. The entity-aggregate identity $(\Pi_{\text{ent}}, \Sigma_{\text{ent}})$ that would make the Sybil tax bite at the fleet level requires an entity-identity primitive (CIP-0161 / CPS-0021 CPD class), absent from the protocol. The whiteboard's V pack lives entirely in $V$ and is unaffected.
- **Custodial transparency in $A$.** Whether custodial registration should additionally appear as a transparency signal in $A$ — beyond simply being absent from it — remains parked alongside OQ2/OQ3.

#### 4.4.4. The Sybil-steepening question (OQ6)

Impact I8 introduces a real concern: the proposed concave rise rewards very-low-pledge configurations relatively heavily. The shape was *intentional* — it makes the bonus accessible to small operators who can pledge 5–20% but not 50% — but it also softens the implicit Sybil tax at the very-low-π edge. A higher-exponent rise preserves the plateau at $\pi \geq 0.5$ while steepening the climb from $\pi = 0$. Three candidate shapes for the rising portion (all capped above 0.5):

| Form (rising portion, $\bar\pi = \min(\pi, 0.5)$) | $\pi=0.05$ | $\pi=0.20$ | $\pi=0.50$ | $\pi=1.00$ | Rise character | Low-$\pi$ Sybil softness |
|---|---:|---:|---:|---:|---|---|
| Current Shelley (saturated): $\pi$ | 0.050 | 0.200 | 0.500 | 1.000 | Linear | — (peak at $\pi=1$) |
| **Proposed**: $4\bar\pi(1-\bar\pi)$ | 0.190 | 0.640 | 1.000 | 1.000 | Concave (super-linear) | Soft (over-rewards) |
| Linear-cap: $\min(2\pi, 1)$ | 0.100 | 0.400 | 1.000 | 1.000 | Linear, kink at 0.5 | Neutral |
| Steeper: $\min(16\pi^2(1-\pi)^2 \cdot \mathbb{1}[\pi \leq 0.5] + \mathbb{1}[\pi > 0.5],\, 1)$ | 0.034 | 0.410 | 1.000 | 1.000 | Quartic rise, plateau | Hard (under-rewards) |

The proposed shape ($4\bar\pi(1-\bar\pi)$) matches the design intent — *very rewarding from 0 to 20%, levelling off toward 50%, plateau above*. It accepts the Sybil softness at low π as the cost of accessibility for retail single-pool operators.

The linear-cap is the simplest alternative — a kinked function that climbs at constant slope to the plateau. It does not deliver the *very rewarding 0–20%* promise (only 40% of max at π=0.20).

The steeper form preserves Sybil resistance at low pledge but loses the accessibility property — at π = 0.05, only 3.4% of max bonus, which is inconsistent with the design intent.

Mid-position option: a *threshold + concave rise* — $A = 0$ for $\pi < \pi_{\min}^{\text{bonus}}$, then concave from there. Adds one parameter ($\pi_{\min}^{\text{bonus}}$, e.g., 0.02) and converts the very-low-π softness into a hard cliff at the threshold.

The choice is OQ6, and it is the natural sequel to the Sybil-tax deferral of §4.4.3. *In the present iteration, the proposed shape is the working hypothesis*; it carries the tradeoff explicitly and pushes harder Sybil work onto the entity-level primitive.

### 4.5. Governance levers — $\mu$ at the macro level, $a_0$ at the envelope level

The two-channel architecture exposes two governance parameters operating at different levels of the reward pipeline. They are *independent* in the sense that adjusting one does not automatically force the other.

| Parameter | Level | Range | Effect |
|---|---|---|---|
| $\mu$ | Macro split (within PoolsPot) | $[0, \mu_{\max}]$ — new parameter, ceiling to be set by CIP | ViabilityPackage share of PoolsPot. Raising $\mu$ enlarges the operator-viability budget at the cost of $RewardPot$ (delegator yield + pledge bonus shrink proportionally to $1-\mu$). |
| $a_0$ | Envelope (within RewardPot) | $[0.1, 1.0]$ — Shelley constitutional, **unchanged** | Pledge influence inside the envelope. Raising $a_0$ shifts mass from the size term ($\lambda_{\text{size}} = 1/(1+a_0)$) to the pledge term ($\lambda_{\text{pledge}} = a_0/(1+a_0)$), without touching the viability channel. |

The decoupling is the architectural payoff. In the previous (3-term envelope) framing, viability, size, and pledge competed within a single convex sum constrained by an extended PPI guardrail. With the channel architecture:

- **Viability calibration** is a $\mu$ decision. Independent from the envelope shape.
- **Pledge calibration** is an $a_0$ decision. Independent from the viability budget.
- **Delegator yield** is the residual: $RewardPot \cdot \lambda_{\text{size}} = (1-\mu) \cdot PoolsPot \cdot 1/(1+a_0)$.

Three V2 milestones map to three governance levers:

| V2 milestone | Lever | Mechanism |
|---|---|---|
| [Guarantee operator viability across the entire productive population](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population) operator viability | $\mu$ | Sets ViabilityPackage budget |
| [Restore the notion of pledge among operators](../../README.md#32-restore-the-notion-of-pledge-among-operators) pledge as Sybil signal | $a_0$ + new $A$ shape | Sets pledge mass and its peak location |
| [Maintain and diversify a competitive delegator yield](../../README.md#33-maintain-and-diversify-a-competitive-delegator-yield) competitive delegator yield | $1 - \mu$ × $\lambda_{\text{size}}$ | Residual after $\mu$ and $a_0$ are set |

The current Shelley calibration is the limiting case $\mu = 0$, $a_0 = 0.3$, $A = A_{\text{Shelley}}$. The proposal moves to $\mu = 20\%$ (working value), $a_0 = 0.3$ (unchanged), $A = A_{\text{new}}$ (50/50 plateau redesign). The constitutional cost is **one new parameter** ($\mu$) and **one parameter-update on $A$'s functional form** (the latter a ledger-rule change, not a constitutional bound modification — the bounds $a_0 \in [0.1, 1.0]$ are unchanged).

##### Comparison with the earlier 3-term envelope framing

| Concern | 3-term envelope (earlier draft) | 2-channel architecture (current) |
|---|---|---|
| Constitutional change | New parameter $b_0$ alongside $a_0$, plus reparameterised PPI guardrail | Single new parameter $\mu$ at macro level; $a_0$ guardrail unchanged |
| Governance complexity | Coupled $(a_0, b_0)$ updates to preserve $\lambda_{\text{pledge}}$ under stress | Single $\mu$ update; $a_0$ untouched |
| V leak structure | Inside the envelope, near the ν-axis cliff | Inside the channel, bounded by population dilution |
| Mental model | "Viability is one-third of the envelope" | "Viability is a separate channel; the envelope is unchanged in shape" |

The channel architecture is *strictly less invasive* on the existing constitutional surface. The §4.4.3 pledge-stability-under-stress invariant, which previously required a coupled $(a_0, b_0)$ update, now requires only a $\mu$ update — $a_0$ is held constant by *not touching it*.

### 4.6. Split-resistance — analysed across both channels

A reward function passes the **split-resistance invariant** when no operator gains by splitting a single pool of stake $\Sigma$ into two pools of stake $\Sigma/2$ (or, more generally, $N$ pools of stake $\Sigma/N$). The invariant is the per-pool projection of the [§3.2.2 R2](../README.md#322-specification) entity-level Sybil-tax requirement: in the absence of an entity-identity primitive (parked as a follow-up CIP per §4.4.3), the invariant is the only structural defence against fragmentation.

With the channel architecture, the invariant must be checked against *both* the envelope and the ViabilityPackage channel. The envelope passes cleanly; the channel still has a residual leak, but bounded by the per-epoch production gate and population dilution.

#### 4.6.1. Envelope channel — split-neutral by construction

Setup. An operator with total stake $\Sigma$ and pledge $P$ compares operating one pool ($\nu_1 = \Sigma/z_0$, $\pi_1 = P/\Sigma$) versus two pools, each with stake $\Sigma/2$ and pledge $P/2$ ($\nu_2 = \nu_1/2$, $\pi_2 = \pi_1$).

| Envelope term | Single-pool | Two-pool aggregate | Verdict |
|---|---|---|---|
| Size mass: $\lambda_{\text{size}} \cdot \nu$ | $\lambda_{\text{size}} \cdot \nu_1$ | $2 \cdot \lambda_{\text{size}} \cdot \nu_1/2 = \lambda_{\text{size}} \cdot \nu_1$ | **Neutral** ✓ |
| Pledge mass: $\lambda_{\text{pledge}} \cdot \nu \cdot 4\bar\pi(1-\bar\pi)$ | $\lambda_{\text{pledge}} \cdot \nu_1 \cdot 4\bar\pi_1(1-\bar\pi_1)$ | $\lambda_{\text{pledge}} \cdot \nu_1 \cdot 4\bar\pi_1(1-\bar\pi_1)$ ($\pi$ unchanged) | **Neutral** ✓ |

Both envelope terms are linear in $\nu$ (with the new $A$ shape), and the pledge ratio $\pi$ is preserved under proportional splitting. The envelope's contribution to total reward is *exactly the same* whether the operator runs one pool or N pools — the entire $RewardPot$ portion of the formula is split-neutral. This is the structural payoff of the channel architecture: fragmentation cannot multiply the size or pledge mass.

#### 4.6.2. ViabilityPackage channel — bounded leak, two mitigation mechanisms

The channel pays $X_p = X_0 \cdot (\text{phase-out factor}) \cdot \mathbb{1}[\nu \geq \nu_{\min}] \cdot \mathbb{1}[n_t \geq 1]$ per qualified pool. Splitting a pool from stake $\Sigma$ to two of stake $\Sigma/2$ has two competing effects on the channel:

- **Sub-additivity of the phase-out shape.** $V(\nu_1) < 2 V(\nu_1/2)$ when both halves are in the phase-out region — splitting a pool above the phase-out terminal into two halves below it creates pack income from zero. The same structural concavity flagged in the previous draft.
- **Per-epoch production gate damping.** A pool at half-stake has half the Poisson rate; $P(n_t \geq 1)$ drops from $1 - e^{-\lambda}$ to $1 - e^{-\lambda/2}$. At $\lambda = 2$ (Σ = 2M ADA, half = 1M each): $P_1 = 0.865$ vs $2 \cdot P_2 = 2 \cdot 0.632 = 1.26$. The expected pack-collection rate falls by $(1.26 - 0.865)/1.26 \approx 31\%$ relative to the deterministic split surplus.
- **Population dilution.** If the pack uses *dilution-floating* sizing ($X_0 = \mu \cdot PoolsPot / N_q$), then adding the entity's second pool to $N_q$ shrinks every pool's pack proportionally. For $N_q = 900$, the dilution factor is $(N_q+1)/N_q \approx 1.001$ per added pool — small but cumulative under mass fragmentation.

##### Quantitative leak under the channel architecture

For an operator with $\Sigma = 2$M ADA (just above the production threshold) considering split into two 1M-ADA pools, with $X_0 = 3,420$ ADA/epoch and per-pool operating cost matched to $X_0$:

| Quantity | Single pool ($\Sigma = 2$M) | Split (2 × 1M) | Net change |
|---|---:|---:|---:|
| Pack collected (deterministic) | $X_0 \cdot v(\nu_1) \approx 0.91 \cdot X_0$ | $2 \cdot X_0 \cdot v(\nu_1/2) \approx 1.94 \cdot X_0$ | $+1.03 \cdot X_0$ |
| × Per-epoch gate factor | $\times 0.865$ → 0.79 $X_0$ | $\times 0.632$ each → 1.23 $X_0$ | $+0.44 \cdot X_0$ |
| − Operating cost increase | 0 | $+1.0 \cdot X_0$ | $-1.0 \cdot X_0$ |
| **Net Sybil surplus** | — | — | **$-0.56 \cdot X_0$** ≈ −1,915 ADA/epoch |

In the working configuration, the Poisson gate plus the operating-cost wash *flips the leak negative* for the marginal-tier split. Splitting a 2M-ADA pool into two 1M-ADA pools **loses ~140K ADA/year** to the operator after running costs.

The leak survives only when the unified pool sits *above* the phase-out terminal (where $V = 0$, no pack lost) and the splits land at the threshold (where Poisson sparsity minimally damps). For an operator at $\Sigma = 15$M ($\nu = \nu^*$, no pack) splitting into 15 pools at $\nu_{\min}$ each:

- Original pack: 0
- Split pack: $15 \cdot X_0 \cdot 0.632$ (Poisson at threshold) $\approx 9.5 \cdot X_0$
- Operating cost increase: $14 \cdot X_0$
- Dilution: $X_0$ shrinks by factor $N_q/(N_q+14) \approx 0.985$
- Net: $9.5 \cdot 0.985 \cdot X_0 - 14 \cdot X_0 \approx -4.65 \cdot X_0$ ≈ **−16K ADA/year**

The combination of per-epoch gate, population dilution, and the realistic operating cost makes N-way fragmentation *net negative* across a wide range of configurations — a sharp improvement over the envelope-coupled architecture's worst case (+125K ADA/year).

#### 4.6.3. Why the channel architecture improves the leak structure

Three factors compose to make the channel-based leak smaller than the envelope-based leak it replaces:

- **Decoupled budget.** In the envelope architecture, splitting let the operator extract a viability contribution that came at the expense of *other operators' size yield* (since $\lambda_{\text{viability}}$ was inside a convex sum). With the channel, the budget is hard-capped at $\mu \cdot PoolsPot$; growing $N_q$ via fragmentation dilutes each fragment's pack pro-rata.
- **Per-epoch gate.** $\mathbb{1}[n_t \geq 1]$ damps the leak by Poisson factors that scale with $1 - e^{-\lambda}$. Splitting halves $\lambda$ per pool, which dampens the eligibility probability super-linearly at low $\lambda$.
- **Operating-cost matching.** When $X_0$ is calibrated to match operating cost per §4.3.3, the marginal cost of an additional pool exactly offsets the marginal pack income. Net Sybil surplus is sensitive only to the *over-payment* of $X_0$ above operating cost.

#### 4.6.4. Why a residual leak persists, and the resolution path

Even with all three damping mechanisms, the leak is non-zero in specific regions — specifically at the seams of the phase-out and the per-epoch gate, where small fragmentation can still extract value when the unified pool sits in a no-pack zone and splits land in active-pack zones.

The structural source remains: the channel allocates per pool, not per entity. Without an entity primitive, *any* per-pool allocation rule with anti-regressive properties admits some fragmentation surplus. The resolution path is unchanged from the previous draft:

- **Entity-level $V$** (eliminates the leak by construction): $X$ computed on entity-aggregate stake $\Sigma_{\text{ent}}$, distributed proportionally to the entity's pools. Requires the entity-identity primitive parked as a follow-up CIP.

The whiteboard's stage 1 CIP scope accepts the residual leak: the channel architecture's combination of per-epoch gate, population dilution, and operating-cost matching makes the leak materially smaller than in any of the four evaluated CIPs (CIP-0050/0037 break Sybil entirely at low pledge; CIP-0023/0082 amplify the MPO advantage by 500× per [Evidence base](../../README.md#3211-evidence-base)). A stage 2 CIP introduces the entity primitive and closes the leak completely.

##### Property added

**P9 — Envelope split-neutrality and bounded channel leak.** The envelope $E(\nu, \pi) = \lambda_{\text{size}} \cdot \nu + \lambda_{\text{pledge}} \cdot A_{\text{new}}(\nu, \pi)$ is fully split-neutral: $f_{\text{envelope}}(\Sigma) = N \cdot f_{\text{envelope}}(\Sigma/N)$ for any proportional split. The ViabilityPackage channel admits a bounded fragmentation surplus — typically negative when operating costs match $X_0$, positive only at specific regions of the phase-out boundary, and strictly smaller than the worst-case leak of any per-pool envelope-based viability mechanism. Full closure of the channel leak requires entity-level evaluation, scoped as a stage 2 follow-up CIP.

## 5. Open questions to converge on next

Seven design choices remain to resolve before the proposal is ready for CIP submission.

- **OQ1 — Channel distribution rule.** Three sub-questions: (a) phase-out shape (linear ramp vs alternative; §4.3.4 working hypothesis is linear); (b) per-epoch gate vs multi-epoch window (§4.3.5 default is per-epoch $n_t \geq 1$); (c) target-fixed vs dilution-floating $X_0$ (§4.3.5 default is dilution-floating).
- **OQ2 — Entity-identity primitive.** *Scoped out of this CIP.* Self-attested pool grouping, on-chain entity certificate, inferred clustering, or no primitive. Closes the channel Sybil leak (§4.6.4). Targeted as a stage 2 follow-up CIP.
- **OQ3 — Custodial branch in $A$.** *Scoped out of this CIP, jointly with OQ2.* Whether custodial registration should appear as a transparency signal in $A$ depends on the entity-identity primitive of OQ2.
- **OQ4 — Calibration of $\mu$.** Working value $\mu = 20\%$ delivers $\sim 250$K ADA/year per qualified pool — generous against the §4.5.1 lower-bound ($\sim 65$K ADA/year at stress price). A tighter calibration ($\mu \approx 12\%$) lands precisely on the mid-range cost target. Trade-off between *operator surplus above cost* and *delegator yield* must be settled by governance discussion before CIP submission.
- **OQ5 — Anchoring rule for $X_0$.** Choice among (a) ADA-fixed, (b) oracle-anchored, (c) governance-rebalanced via $\mu$ (per §4.3.3 P3 rule d), or (d) hybrid. Determines how the channel responds to ADA-price drift.
- **OQ6 — Sybil-steepening of $A$.** The new $A$ shape ($\nu \cdot 4\bar\pi(1-\bar\pi)$ with plateau) is concave near $\pi = 0$ and slightly over-rewards very-low-pledge configurations relative to current Shelley. Steeper alternatives ($16\bar\pi^2(1-\bar\pi)^2$, threshold-and-rise) preserve Sybil resistance at low $\pi$ at the cost of accessibility for retail. The whiteboard's working choice (concave) accepts the softness as the price of retail accessibility.
- **OQ7 — Variance handling at the threshold.** Per-epoch gate exposes pools at $\nu_{\min}$ to a 37% miss rate. Options: (a) accept as a feature; (b) multi-epoch averaging window; (c) reduced $X_0$ near threshold to acknowledge productivity uncertainty. The whiteboard's working choice is (a).

## 6. Next steps — toward the stage 1 CIP

The whiteboard is the source draft for a forthcoming CIP submission, scoped as **stage 1** of a multi-stage reward-system reform (entity-level Sybil tax = stage 2, scoped out).

- **Iteration 1 — Calibration convergence.** Resolve OQ1, OQ4, OQ5, OQ6, OQ7 to specific values. The whiteboard provides working defaults; governance discussion picks the calibration.
- **Iteration 2 — Quantitative evaluation against the 9-tier × n-MPO grid.** Apply the per-CIP evaluation template ([Exec summary / Evaluation findings / §1 Intro / §2 Mechanism / §3 Limits](../solution-evaluation/operator-delegator/cip-0023.md)) to this proposal, mirroring CIP-0023/0082/0050/0037 evaluations. Admissibility = improvement on every cell where the four CIPs regress.
- **Iteration 3 — CIP draft.** Transform the whiteboard into a CIP-formatted document per [CIP-0001 §Document Structure](../../../Context/CIPs-repo/CIP-0001/README.md): Preamble (YAML frontmatter), Abstract, Motivation, Specification, Rationale, Path to Active, Copyright. The whiteboard sections map as: §1 → Motivation, §2 + §3 → Rationale (constraints + alternatives), §4 → Specification, §5 + §6 → Path to Active.

The **build surface** these iterations feed into — the ledger, CDDL, Constitution-guardrail, node, and assurance work items required to ship this stage-1 design, and the hard-fork-then-parameter-update rollout sequence — is inventoried in [Build Estimation / Scoping](../../implementation-scope/README.md).

## References

- Current Shelley reward formula: [diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md §2.3](../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md)
- V2 specification: [reward-system-spec/README.md §3.1, §3.2, §3.4, §4.4](../README.md)
- *The Intended Game* security properties: [the-intended-game/README.md §3.4](../the-intended-game/README.md)
- Cross-CIP synthesis: [solution-evaluation/synthesis.md](../solution-evaluation/synthesis.md)
- CIP evaluations: [cip-0023](../solution-evaluation/operator-delegator/cip-0023.md), [cip-0082](../solution-evaluation/operator-delegator/cip-0082.md), [cip-0050](../solution-evaluation/pools-distribution/cip-0050.md), [cip-0037](../solution-evaluation/pools-distribution/cip-0037.md)
- Cardano Constitution: <https://github.com/IntersectMBO/cardano-constitution/tree/main/cardano-constitution-2>
