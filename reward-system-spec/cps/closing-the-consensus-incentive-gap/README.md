---
CPS: ???
Title: CPS-2 — Closing the Consensus Incentive Gap
Category: Ledger
Status: Draft
Authors:
    - Nicolas Henin <nicolas.henin@iohk.io>
Proposed Solutions:
    - CIP-0050
    - CIP-0037
Discussions: []
Created: 2026/03/25
License: Apache-2.0
---

## Abstract

The SL-D1 pool reward curve is the protocol's **only tool** for shaping the operator ecosystem that secures consensus. Its design should produce an equilibrium of $k$ **independent, well-pledged pools accountable to delegators**. After five years of mainnet operation, the equilibrium that has emerged is *structurally hostile to that intent*.

The reward formula is **at war with the security model it was meant to support**. Its global maximum is reached at $\pi = 1, \nu = 1$ — a fully-pledged, fully-saturated pool with **no delegator participation** — eliminating the accountability mechanism the protocol depends on. Reaching that optimum requires **77M ADA (~30M USD)** of personal capital for a yield of **0.68%/yr**, well below the **2.3%/yr** delegators earn passively. *The rational actor should never pledge.*

The progression toward that optimum is invisible: at median pledge the bonus adds **~0.006%** to rewards, undetectable in any pool comparison tool. The entry is a cliff — **73% of pools** sit below the **~3M ADA** viability threshold and operate at a loss. Meanwhile only **8 pools** reach saturation (1.6% of the $k = 500$ design target), and the playing field itself is half the size the design assumed: **~16.75B ADA (43.5%)** of circulating supply does not participate in delegation.

The dominant strategy at every level — entry, progression, endgame — has converged on **maximising delegation and minimising pledge**, exactly the opposite of what consensus security requires. **95.6%** of the pledge-bonus budget returns to reserve unused — *the single largest addressable inefficiency in the system*, unchanged since Shelley launch.

This CPS formally defines the **consensus incentive gap** at the pool-distribution layer of the reward pipeline. It is grounded in the mainnet evidence documented in the dedicated [Pools Pot Distribution Gaps — Mainnet Analysis](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md) sub-report and invites the community to propose solutions through the CIP process.

## Problem

This CPS builds upon the mainnet evidence documented in the dedicated [sub-report: The Pools Pot Distribution Gaps — Mainnet Analysis](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md), which provides the full empirical analysis, data, figures, and reproduction scripts behind the findings summarised here.

### Context

The pool reward curve is not merely a reward-distribution mechanism. It is the protocol's only tool for shaping the operator ecosystem that secures consensus. Cardano does not select operators by committee or licence — it defines a set of economic rules and lets actors self-select. The reward curve *is* the game. Its design determines who plays, how they progress, and what the endgame looks like.

The protocol needs a specific set of properties at this layer: a sufficiently large number of independent block producers, each with meaningful personal capital at risk (*Sybil resistance*), subject to continuous community oversight (*accountability*), with no single entity able to capture a dominant share of consensus power (*decentralisation*). The reward curve's success or failure is measured by a single criterion: does the equilibrium it defines exhibit these security invariants?

For this to work, two conditions must hold. First, participation must be *individually rational*: each player must be better off entering the game than staying out. Second, the mechanism must be *incentive-compatible*: the strategy that maximises each player's individual reward must also be the strategy that reinforces the system's security properties.

### The intended game

The mechanism operates through three participant classes — transaction submitters, operators, and delegators — forming a dependency chain. Transaction submitters generate economic value that funds the game. Operators commit capital and infrastructure to secure the network. Delegators allocate capital to select and police operators.

At this layer, the reward curve directly governs the operator–delegator relationship. Neither player alone should be able to maximise rewards — the mechanism deliberately requires both. Operators need delegators for scale, delegators need operators for block production, and the reward curve should make their partnership the individually rational path for both.

Each player class experiences the game through its own trajectory — entry, progression, and endgame:

**Operators.** Entry: register a pool, pledge an initial amount, attract delegation — the mechanism should offer a credible path forward. Progression: increasing pledge commitment produces measurable competitive advantage visible to delegators. Endgame: deep commitment (high pledge) + broad delegation = maximum reward. This state should require *both* — it cannot be attained by capital alone or by delegation alone.

**Delegators.** Entry: select a pool, allocate stake. Progression: differentiate pools on commitment-based criteria (pledge, track record, margin), reallocate accordingly. Endgame: act as an efficient market for operator commitment — capital moves to committed pools, exits from uncommitted ones. The accountability mechanism operates at full power.

**The aligned dynamics.** When both trajectories function as intended, they form a self-reinforcing cycle: operators compete on pledge commitment, delegators reward the most committed operators, selective pressure produces a decentralised, accountable, Sybil-resistant landscape. This is the *incentive-compatible equilibrium* the mechanism should converge toward.

### Observations

The [sub-report](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md) documents the following observations at this pipeline stage:

**O1 — The pledge bonus is functionally irrelevant at realistic pledge levels.** At median pledge the bonus adds ~0.006% to rewards — undetectable. Yield on pledge capital (0.68%/yr at best) is below passive delegation yield (~2.3%/yr). 22.1% of the pools pot (~3.4M ADA/epoch) returns to reserve unused because the $a_0$ curve is too flat.

**O2 — The pool landscape is stratified far from the k = 500 design target.** 73% of pools (1,987) sit below the 3M ADA viability line, carrying only 2.7% of active stake. Only 7 pools reach saturation — 1.4% of the $k = 500$ target.

**O3 — Saturation is structurally underutilised.** Active stake fills 56.5% of theoretical capacity ($k \times z_0$). At most 282 pools could saturate under perfect redistribution. The near-saturation zone holds only 104 pools.

**O4 — The delegation market is capital-constrained.** 16.75B ADA (43.5%) does not participate in delegation. 85 MPO entities control ~51% of staked ADA.

### The participation constraint

The pool landscape the reward curve is supposed to shape is fundamentally constrained by a capital base that is half the size the design assumed. $k = 500$ implicitly required near-complete participation. At 56.5%, the target is structurally unreachable — at most 282 pools could saturate (O3). The saturation cap, the core mechanism designed to prevent stake concentration, binds for only 7 pools (O2). The viability threshold acts as a cliff: 73% of pools sit below it, carrying only 2.7% of active stake (O2).

No formula change at this layer can close the participation gap itself — it requires upstream intervention to bring inactive ADA into delegation. But the participation constraint is not a separate problem: it is the playing field on which the incentive game operates, and any solution to the game must account for it. Activating inactive ADA would also interact with reserve sustainability (see companion CPS [*Funding the Protocol Without a Reserve*](../funding-the-protocol-without-a-reserve/README.md)).

The ~17B ADA outside delegation includes exchange-held ADA, governance-inactive holdings, and lost stake. Each category has different activation dynamics — exchange staking policies, governance incentives (CIP-1694), and the lost-stake problem (CPS-0022) — but from the reward curve's perspective they are indistinguishable: absent capital that the mechanism cannot reach.

### Where the design breaks

The SL-D1 reward curve fails at all three levels of the game:

**The endgame eliminates the delegator entirely.** The reward function decomposes into a size fraction ($\lambda_{\text{size}} \approx 76.9\%$) and a pledge fraction ($\lambda_{\text{pledge}} \approx 23.1\%$). The formula's maximum ($P_{\max}$) is reached when $\pi = 1$ and $\nu = 1$: the operator pledges the full saturation amount *and* the pool is fully saturated.

But since pledge counts as stake, an operator who pledges $z_0$ (currently **77M ADA**) fills the entire pool with their own capital. **There is no room for delegators.** The "dream" the reward curve defines is a pool with no community participation — a private operation where the operator is both the sole funder and the sole beneficiary.

*The accountability mechanism is eliminated at the endgame.*

This means the reward curve's ideal state **contradicts the protocol's security model**. The mechanism designed to produce 500 pools anchored by community trust instead defines an optimum of **500 private pools with no delegator oversight**.

**The endgame is economically irrational.** Reaching $P_{\max}$ requires **77M ADA (~30M USD)** of personal capital. The incremental reward is ~**7.2K ADA/epoch** ($\lambda_{\text{pledge}} \cdot P_{\max}$), a yield of ~**0.68%/yr**.

The same 77M ADA passively delegated would earn **~2.3%/yr** — more than three times the return, with zero operational burden.

*The rational actor should never pledge.*

The curve presents a **double failure**: sub-economic yield **and** removal of the delegator accountability layer.

**The progression is invisible.** The pledge bonus is **too small to be a competitive differentiator** at any realistic scale (O1). Delegators comparing pool yields cannot detect it. An operator who pledges 1M ADA looks the same to delegators as one who pledges nothing. *The delegator accountability mechanism cannot function because there is nothing for delegators to differentiate on.*

**The entry creates a cliff, not a ramp.** **73% of pools** sit below the viability threshold (O2). Below-viability pools owe **647K ADA/epoch** in fixed costs but earn only **182K ADA** — **destroying value for delegators by 3.6×**. New operators face a binary outcome: *clear the viability cliff or operate at a loss with no visible competitive tool to distinguish themselves*.

**The result on mainnet.** The dominant strategy at every level — entry, progression, endgame — is to **maximise delegation and minimise pledge**. *This is the exact opposite of what the protocol needs for consensus security.*

The evidence confirms this at scale:

- 82% of MPO-level pledge bonus flows to three entities — two by private choice, one by institutional mandate.
- 41 of 48 saturation-scale MPOs choose non-compliance, forfeiting ~550K ADA/epoch collectively.
- Structural populations (CEX, IVaaS) totalling 7.39B ADA cannot pledge custodied assets — an architectural constraint immune to parameter changes.
- The incentive-responsive field holds only 36% of active stake.
- The independent operator base has collapsed to 283 viable operators after removing MPO fleet members, with 78% of their stake non-compliant.
- 95.6% of the pledge-bonus budget returns to reserve unused, unchanged since Shelley launch (O1).

## Use Cases

**Stake pool operator deciding whether to increase pledge.** An operator with 500K ADA considering whether to pledge more needs to know if the reward curve will make that commitment visible and economically meaningful to delegators. Currently, the answer is no: the bonus is ~0.006% at median pledge, undetectable in pool comparison tools. The operator's rational choice is to minimise pledge and compete on marketing — the opposite of what the protocol needs.

**Stake pool operator assessing viability.** An operator considering whether to enter the pool ecosystem needs to know whether $k = 500$ saturated pools is a realistic target. At current participation, only 282 pools could saturate — an operator entering the market competes for a structurally undersized pie. The viability cliff (73% of pools below it) means the entry decision is binary: clear the threshold or operate at a loss with no gradual path.

**Delegator selecting a pool.** A delegator comparing pools cannot use pledge commitment as a selection criterion because the reward curve makes pledge economically invisible. Two pools with identical stake but radically different pledge levels offer nearly identical yields. The accountability mechanism — delegators rewarding commitment — cannot function.

**Protocol designer evaluating CIP-0050 or CIP-0037.** Both proposals restructure the pledge-saturation relationship to make pledge a meaningful competitive dimension. A designer evaluating these CIPs needs a clear statement of what the current curve fails to produce — the equilibrium it should target — to assess whether the proposed modifications achieve it. Both operate within the existing capital base; a designer must also understand that the participation constraint bounds the effectiveness of any curve modification.

**Governance actor evaluating parameter changes.** The pledge influence parameter $a_0 = 0.3$ has been unchanged since Shelley. A governance actor considering adjustments needs to understand that the problem is not just the *value* of $a_0$ but the *structure* of the curve: even at higher $a_0$, the endgame contradiction persists. Similarly, CIP-0082 proposes increasing $k$ to 750 and then 1000 — but if $k = 500$ is already unreachable at 56.5% participation, increasing $k$ widens the gap further.

## Goals

1. **Align the endgame with the protocol's security model.** The reward curve's maximum should require *both* operator commitment (pledge) and community delegation — not be achievable by capital alone. The delegator accountability mechanism must be present at the optimum, not absent.

2. **Make pledge a legible competitive dimension.** The reward difference between high-pledge and low-pledge pools must be large enough for delegators to detect and act on. Pledge should be a first-order selection criterion, not a rounding error.

3. **Create a credible entry-to-endgame progression.** The mechanism should offer a gradual path from entry to viability to optimality — not a cliff at viability and an invisible progression beyond it. Each step up in pledge should produce a measurable, delegator-visible competitive advantage.

4. **Ensure the dominant strategy aligns with consensus security.** The strategy that maximises individual operator reward should also be the strategy that strengthens decentralisation, Sybil resistance, and accountability — not the strategy that undermines them.

5. **Preserve incentive compatibility with the operator–delegator dependency.** Operators must need delegators, and delegators must have leverage. The mechanism should not permit operators to self-fund to optimality, nor should it permit delegators to ignore operator commitment.

6. **Account for the participation constraint.** Any solution must be viable at the current participation rate (~56.5%) and should not depend on near-complete participation that may never materialise. Solutions should define the feasible $k$ range at current participation and model the interaction between curve reform and participation activation.

**Non-goals:**

- Prescribing specific parameter values ($a_0$, $k$, pledge leverage $L$, saturation scaling functions) — that is the role of CIPs responding to this CPS.
- Modifying the operator/delegator fee split — that is a downstream problem at §1.3.
- Addressing reward sustainability at the epoch-budget layer — that is the scope of the companion CPS (*Funding the Protocol Without a Reserve*).
- Addressing lost stake specifically — that is the scope of CPS-0022.

## Open Questions

- **Can the endgame contradiction be resolved within the existing curve structure?** The $a_0$ pledge bonus is additive within the SL-D1 formula. Is there a parameterisation of $a_0$ that makes the endgame require delegation? Or does resolving the contradiction require a structural change (as CIP-0050 and CIP-0037 propose)?

- **What pledge-to-reward sensitivity is sufficient for delegator legibility?** At what reward differential can delegators reliably detect and act on pledge differences? This defines the minimum effective sensitivity the curve must produce.

- **How should the viability cliff be addressed?** Is the cliff primarily a fixed-cost problem (minPoolCost — addressed by CIP-0082 and CIP-0074), a curve-shape problem, or a participation problem? Can the entry path be smoothed without creating free-rider dynamics?

- **What is the interaction between curve reform and MPO behaviour?** 85 MPO entities control ~51% of staked ADA. If the curve is reformed to reward pledge more aggressively, how will MPOs respond? Will they consolidate pools and increase pledge, or will architectural constraints (custodied assets, governance structures) prevent adaptation?

- **How do structural non-compliant populations (CEX, IVaaS) affect the achievable equilibrium?** 7.39B ADA in custodied assets cannot pledge by architectural constraint. If the curve is reformed to strongly reward pledge, these populations are structurally disadvantaged. Does this improve decentralisation (by shifting stake toward independent operators) or create a two-tier system?

- **What participation rate does the design actually require?** The $k = 500$ target implies a required capital base. What is the minimum participation rate at which $k = 500$ is feasible? What is the feasible $k$ at current participation? How does $k$ interact with participation rate — does increasing $k$ (as CIP-0082 proposes) make the constraint tighter or looser?

- **What is the interaction with participation activation?** 16.75B ADA sits outside delegation. If that ADA enters the system, does it flow toward high-pledge pools (reinforcing a reformed curve) or toward existing large pools (amplifying concentration)? Activating inactive ADA also accelerates reserve depletion (see companion CPS *Funding the Protocol Without a Reserve*).

- **Can governance incentives (CIP-1694) meaningfully activate stake?** The Voltaire governance framework introduces DRep delegation, which requires stake key registration. Does this create a pathway to activate currently inactive ADA, or does it primarily affect already-delegated stake?

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
