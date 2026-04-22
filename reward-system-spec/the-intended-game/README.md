# The Intended Game
### A Narrative Description of the Consensus Incentive Mechanism

> **Status:** Working document — companion to the main [Cardano Reward Pipeline](../diagnostic/README.md) analysis ([§1.2](../diagnostic/README.md#12-pools-distribution)) and the CPS [*Closing the Consensus Incentive Gap*](../diagnostic/sub-flows/pools-distribution/cps/README.md).

<br>

## Table of Contents

- [What this document is for](#what-this-document-is-for)
- [1. The design objective](#1-the-design-objective)
- [2. The players](#2-the-players)
  - [2.1 Transaction submitters — the source of economic demand](#21-transaction-submitters-the-source-of-economic-demand)
    - [2.1.1 Why they matter](#211-why-they-matter)
    - [2.1.2 How they feed the game](#212-how-they-feed-the-game)
    - [2.1.3 A latent constraint — marginal today, existential tomorrow](#213-a-latent-constraint-marginal-today-existential-tomorrow)
  - [2.2 Operators — capital at risk](#22-operators-capital-at-risk)
    - [2.2.1 An open seat at the deflationary table](#221-an-open-seat-at-the-deflationary-table)
    - [2.2.2 The participation constraint](#222-the-participation-constraint)
    - [2.2.3 Pledge as the primary instrument](#223-pledge-as-the-primary-instrument)
    - [2.2.4 The arc from newcomer to pillar](#224-the-arc-from-newcomer-to-pillar)
  - [2.3 Delegators — the oversight layer](#23-delegators-the-oversight-layer)
    - [2.3.1 Yield-seeking with minimal effort](#231-yield-seeking-with-minimal-effort)
    - [2.3.2 Liquid delegation as continuous approval](#232-liquid-delegation-as-continuous-approval)
    - [2.3.3 The delegator as ethical arbiter](#233-the-delegator-as-ethical-arbiter)
    - [2.3.4 Myopic and non-myopic delegation](#234-myopic-and-non-myopic-delegation)
  - [2.4 The dependency chain](#24-the-dependency-chain)
- [3. The progression](#3-the-progression)
  - [3.1 Transaction submitters — from subsidy to self-sufficiency](#31-transaction-submitters-from-subsidy-to-self-sufficiency)
  - [3.2 Operators — from first pledge to full commitment](#32-operators-from-first-pledge-to-full-commitment)
  - [3.3 Delegators — from passive yield to active oversight](#33-delegators-from-passive-yield-to-active-oversight)
  - [3.4 The security properties the equilibrium must satisfy](#34-the-security-properties-the-equilibrium-must-satisfy)
    - [3.4.1 Accountability — the bond and the enforcer](#341-accountability-the-bond-and-the-enforcer)
    - [3.4.2 Delegation as counter-power — the protocol's substitute for governance](#342-delegation-as-counter-power-the-protocols-substitute-for-governance)
    - [3.4.3 Sybil resistance — making fragmentation expensive](#343-sybil-resistance-making-fragmentation-expensive)
    - [3.4.4 Decentralisation — more than a pool count](#344-decentralisation-more-than-a-pool-count)
    - [3.4.5 The properties are not independent](#345-the-properties-are-not-independent)
    - [3.4.6 The structural requirement](#346-the-structural-requirement)
- [4. The aligned dynamics — the virtuous cycle](#4-the-aligned-dynamics-the-virtuous-cycle)

<br>

## What this document is for

The formal game-theoretic properties of the Cardano reward curve were established in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020, EuroS&P), which proves that *k* pools is a Nash equilibrium under certain assumptions. The engineering specification *SL-D1* (Kant, Brünjes & Coutts, 2019) translates those results into protocol-level formulas and parameters.

> [!IMPORTANT]
> What neither document provides is a **narrative description of the game as it should play out** — the players, their motivations, how they enter and progress, and the equilibrium they should converge toward.

This matters because evaluating whether the mechanism *works* requires a clear picture of what *working* looks like — not as a mathematical proof, but as a readable account that the community and CIP authors can reason about.

This document produces that missing description.

<br>

## 1. The design objective

The protocol needs a specific set of properties at the consensus layer: a sufficiently large number of independent block producers, each with meaningful personal capital at risk (**Sybil resistance**), subject to continuous community oversight (**accountability**), with no single entity able to capture a dominant share of consensus power (**decentralisation**).

These are not aspirational qualities — they are the security invariants that the consensus layer depends on.

Cardano cannot enforce these properties by fiat. It has no licensing authority, no operator selection committee, no means of compelling participation. It must instead rely on **mechanism design**: defining a set of economic rules — the reward curve — such that rational, self-interested participants, each optimising their own payoff, collectively produce and maintain the desired system properties.

The reward curve *is* the mechanism. Its success or failure is measured by a single criterion: does the *equilibrium* — the stable state toward which rational play converges — exhibit the security invariants above?

For this to work, two conditions must hold:

| Condition | Meaning |
|---|---|
| **Individual rationality** | Each player must be better off entering the game than staying out. |
| **Incentive compatibility** | The strategy that maximises each player's individual reward must also be the strategy that reinforces the system's security properties. |

When these conditions hold, the protocol does not need to trust its participants — it only needs them to be rational.

<br>

## 2. The players

The mechanism operates through three distinct classes of participant. Each has a different *motivation* for entering the game, a different set of *actions* (in mechanism-design terms, a different *strategy space*), and a different *trajectory* — the way their participation evolves as the system matures. Understanding all three is necessary before evaluating whether the reward curve aligns them correctly.

| Player | Role | Strategic instrument |
|---|---|---|
| **Transaction submitters** | Source of economic demand | Fee payments — revealed-preference signal for network value |
| **Operators** | Block production and network security | **Pledge** — personal capital locked as a commitment bond |
| **Delegators** | Capital allocation and operator oversight | **Liquid delegation** — continuous, revocable approval signal |

### 2.1 Transaction submitters — the source of economic demand

#### 2.1.1 Why they matter

Transaction submitters need reliable, censorship-resistant settlement. They do not participate in the staking game directly — they are *users* of the service that the game produces. Their willingness to pay fees is a revealed-preference signal: it measures the real-world value the network delivers.

#### 2.1.2 How they feed the game

They submit transactions and pay fees. Those fees — together with the monetary expansion draw from the reserve — fund the epoch pot that the reward pipeline distributes ([§1.1](../diagnostic/README.md#11-treasury-pool-pots-distribution)). Transaction submitters are the reason the system exists: without them, there is no economic activity to secure, and no sustainable revenue to fund the operators who secure it.

#### 2.1.3 A latent constraint — marginal today, existential tomorrow

In the current regime, transaction fees are negligible (~0.19% of the epoch pot — [§1.1.2](../diagnostic/README.md#112-mainnet-observations) (DIA.1.1.O1)). The game is almost entirely funded by monetary expansion from a depleting reserve.

As the reserve crosses its half-life and expansion shrinks ([§1.1.2](../diagnostic/README.md#112-mainnet-observations) (DIA.1.1.O2)), the system's economic viability progressively shifts onto fee revenue.

> [!NOTE]
> Transaction submitters are a **latent constraint**: marginal today, existential tomorrow. Their long-term participation is what makes the staking game *sustainably worth playing* for every other participant.

### 2.2 Operators — capital at risk

#### 2.2.1 An open seat at the deflationary table

A prospective operator believes in Cardano. ADA has a capped supply and a depleting reserve — it is structurally deflationary.

From this perspective, the consensus game looks like an investment thesis, not a job offer: by operating a pool, an operator continuously accumulates an asset whose scarcity increases mechanically over time. The nominal yield in ADA, compounded by the deflationary trajectory of the asset itself, makes the expected real return deeply attractive on a long horizon.

And critically, the entry should be *accessible* — the mechanism is supposed to let anyone with conviction and a realistic initial stake begin building this position. Not an exclusive club; an open, meritocratic game where commitment is the competitive edge.

> This is the narrative that attracts operators: a credible, long-term capital accumulation path anchored in consensus participation, open to anyone who believes in the technology.

#### 2.2.2 The participation constraint

Operators seek a return on two forms of capital: the ADA they pledge and the infrastructure they maintain. A rational operator enters the game when the expected reward — block production fees, pool margin, and stake-proportional share — exceeds the combined opportunity cost of pledged capital and operational expenses. In mechanism-design terms, the *participation constraint* must be satisfied: the operator must be better off running a pool than simply delegating the same ADA.

#### 2.2.3 Pledge as the primary instrument

The operator's primary strategic instrument is **pledge**: personal capital locked into the pool.

Pledge serves as the protocol's *commitment mechanism* — the signal through which an operator demonstrates alignment with the network's interests. An operator who pledges significant ADA has more to lose from protocol failure or malicious behaviour than one who pledges nothing. This "skin in the game" is the protocol's primary defence against Sybil attacks.

Operators also set a *margin* (their fee) and maintain infrastructure quality (uptime, latency) — but the reward curve at this layer is primarily sensitive to pledge and total stake, not operational quality.

#### 2.2.4 The arc from newcomer to pillar

A new operator starts with a small pledge, minimal delegation, and sub-viable block production. Over time, the intended trajectory is one of *increasing commitment*: as the operator builds reputation and attracts delegation, they pledge more, their pool grows, and they earn a larger share of the pools pot. The mechanism should make each step up in pledge produce a measurable competitive advantage — visible to delegators and economically meaningful to the operator — so that the progression from "new pool" to "established pool" to "fully committed pool" is a legible arc that both players can follow.

### 2.3 Delegators — the oversight layer

#### 2.3.1 Yield-seeking with minimal effort

Delegators seek yield on their ADA holdings with minimal effort and risk. They do not produce blocks and bear no operational cost. Their entire strategic space reduces to a single decision: *which pool to delegate to*. A rational delegator maximises risk-adjusted return, favouring pools with high expected yield, reliable performance, and trustworthy operators.

The natural selection metric is the **annualised return on stake (ROS)** — the single number that aggregates pool performance, operator fees, and saturation into a comparable yield figure. But the formula's structure ensures that the yield spread between well-run pools is narrow — a few tenths of a percent. This narrow spread is a design consequence, not an accident: it means that yield alone cannot meaningfully differentiate most of the pool landscape. A second criterion enters — one the formula does not price but that the mechanism depends on.

#### 2.3.2 Liquid delegation as continuous approval

Their strategic instrument is **liquid delegation**: the ability to freely choose a pool — and freely withdraw at any time.

This makes delegation a *continuous approval signal*. No operator can capture stake permanently; an operator who underperforms or behaves badly faces immediate capital flight.

> [!IMPORTANT]
> Liquid delegation is the protocol's **accountability mechanism** and its primary anti-monopoly tool. But this mechanism only functions if pools *need* delegators — if operators depend on community-sourced stake to reach their optimal reward. Without this dependency, delegators have no leverage and the accountability channel collapses.

#### 2.3.3 The delegator as ethical arbiter

Because the yield spread between well-run pools is narrow, the delegator's choice is not purely economic — it is partly an expression of values. Two pools that offer identical ROS may differ in ways the formula does not capture but that matter to the delegator and to the network:

**Commitment.** A pool where the operator has pledged meaningful personal capital is structurally more aligned with the delegator's interest than one where the operator pledges nothing. The operator has more to lose, the accountability channel is active, and the pool is less likely to change strategy abruptly.

**Independence.** Delegating to an independent single-pool operator contributes to decentralisation in a way that delegating to the tenth pool of a large multi-pool operator (MPO) fleet does not. The protocol does not distinguish between the two — the formula treats every pool identically — but the delegator who values a decentralised network may deliberately choose the independent operator.

**Transparency and conduct.** Operators differ in how they communicate fee changes, maintain infrastructure, and engage with the community. These are reputational signals that the protocol does not encode but that delegators can observe and act on. A delegator who exits a pool after a surprise margin increase is exercising the accountability mechanism — even if the formal yield difference is negligible.

The delegator, in this sense, acts as an **ethical arbiter** of the pool landscape. Where the formula is indifferent, the delegator is not. The mechanism's long-term health depends on enough delegators treating this ethical dimension as part of their decision — supporting commitment, independence, and transparency beyond what yield alone would justify.

#### 2.3.4 Myopic and non-myopic delegation

The formal literature distinguishes two delegator models that map directly onto the yield-vs-ethics tension above.

A **myopic** delegator optimises for the *current epoch*. The decision is purely backward-looking: which pool delivered the highest ROS last epoch? The myopic delegator treats delegation as a spot market — move to the best-yielding pool, every epoch, ignoring second-order effects. Under this model, delegation flows toward the largest, most reliable, lowest-fee pools. The myopic delegator has no reason to consider pledge, operator commitment, or network-level properties: none of these affect the per-ADA yield in the next five days.

A **non-myopic** delegator anticipates the *downstream effects* of delegation decisions. This delegator recognises that moving stake into a pool changes the pool's size, affects its yield through saturation dynamics, and — in aggregate — shapes the pool landscape. Brünjes & Kiayias (2020) prove that the *k*-pool equilibrium holds under non-myopic play: delegators who factor in the long-term consequences of their delegation converge on a distribution of *k* pools.

The non-myopic delegator is the one for whom the ethical dimension of pool selection is not a luxury but a rational strategy: supporting committed, independent operators produces a more decentralised, more accountable network — which is a more valuable network — which sustains the yield the delegator depends on.

> [!IMPORTANT]
> The mechanism implicitly *assumes* non-myopic delegation. The equilibrium results in the formal literature require delegators who look past the current epoch. But the information environment the mechanism creates — where yield differences between pools are negligible, where pledge is invisible, where pool size is the dominant signal — rewards myopic behaviour. The mechanism needs non-myopic delegators to reach its intended equilibrium, but it provides myopic delegators with no reason to become non-myopic.

This is the core tension in the delegator's role. The ethical arbitration that the mechanism depends on operates *outside* the formula, sustained only by the delegator's understanding that the network they help shape is the network they depend on.

### 2.4 The dependency chain

These three roles form a dependency chain:

```
Transaction submitters          Operators                    Delegators
  generate economic    ──▶    commit capital &     ──▶    select & police
  value that funds             infrastructure to           the operators
  the game                     secure the network
```

The mechanism's task is to make each link *individually rational* and *incentive-compatible* — so that the chain holds without requiring trust between participants.

At this layer (pool distribution), the reward curve directly governs the operator–delegator relationship. Neither player alone should be able to maximise rewards — the mechanism deliberately requires both.

This **interdependence** is the core of the design: operators need delegators for scale, delegators need operators for block production, and the reward curve should make their partnership the individually rational path for both.

Transaction submitters are upstream — their contribution is mediated through the epoch pot ([§1.1](../diagnostic/README.md#11-treasury-pool-pots-distribution)) — but they set the ultimate economic boundary within which the operator–delegator game plays out.

<br>

## 3. The progression

Each player class experiences the game through its own trajectory — entry, progression, and endgame. A well-designed mechanism makes each trajectory *individually rational* at every stage, so that no player has a reason to drop out or deviate.

### 3.1 Transaction submitters — from subsidy to self-sufficiency

**Entry.** Early adopters use the network for basic settlement. Transaction volume is low, and fees contribute negligibly to the epoch pot. The game is almost entirely funded by monetary expansion from the reserve — a bootstrap subsidy that makes staking rewards viable before organic demand exists.

**Progression.** As the network matures, transaction volume and diversity grow. Fee revenue increases, gradually reducing dependence on the reserve. The ratio of fees to expansion becomes a measure of the system's economic maturity.

**Endgame.** Fee revenue fully replaces monetary expansion as the primary funding source for the epoch pot. The staking game is self-sustaining: operators and delegators are paid by the economic activity they secure, not by a depleting reserve. The protocol has achieved *economic self-sufficiency*.

### 3.2 Operators — from first pledge to full commitment

**Entry.** A new operator registers a pool, pledges an initial amount, and begins attracting delegation. The mechanism must make this *individually rational*: the expected payoff should offer a credible path forward — not just survival, but growth — so that the *participation constraint* is met from the start.

**Progression.** As the operator builds reputation and delegation, the mechanism should reward increasing pledge commitment. Each step up in pledge should produce a measurable competitive advantage — visible to delegators, economically meaningful to the operator. The progression from "new pool" to "established pool" to "fully committed pool" should be a legible arc that both operators and delegators can follow.

**Endgame.** The operator has committed deeply (high pledge) and earned broad delegation. Their pool captures the maximum reward the protocol offers. This state should require *both* high pledge and high delegation to reach — it cannot be attained by capital alone or by delegation alone.

### 3.3 Delegators — from passive yield to active oversight

**Entry.** A new delegator selects a pool and allocates stake. Early on, differentiation between pools is low — delegation may be driven by brand, community ties, or social signals rather than on-chain metrics. The mechanism must still make participation *individually rational*: delegation yield should exceed the opportunity cost of holding idle ADA.

**Progression.** As the pool landscape matures and the mechanism produces legible differences between pools, delegators increasingly differentiate on *commitment-based criteria*: pledge level, track record, margin policy. Delegation flows toward the most committed operators and away from uncommitted ones. The accountability mechanism becomes active — delegators are now *policing* operator behaviour through capital reallocation.

**Endgame.** Delegators act as an efficient market for operator commitment — and as ethical arbiters of the pool landscape ([§2.3.3](#233-the-delegator-as-ethical-arbiter)). Capital moves fluidly to the pools that best combine commitment and performance, and exits quickly from those that fall short. The accountability mechanism operates at full power: no operator can sustain high rewards without continuous community approval. This endgame requires non-myopic delegation ([§2.3.4](#234-myopic-and-non-myopic-delegation)): delegators who factor in commitment, independence, and network health — not only current-epoch yield — into their allocation decisions.

### 3.4 The security properties the equilibrium must satisfy

The three trajectories above describe individual paths. But the protocol does not care which path any single operator or delegator takes — it cares whether the *equilibrium* that emerges from the aggregate of all rational choices preserves the security invariants defined in [§1](#1-the-design-objective).

The formal literature — *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020) and the SL-D1 engineering specification (Kant, Brünjes & Coutts, 2019) — defines these invariants implicitly through the constraints the reward function must satisfy: the equilibrium must exhibit *k* independent block producers, each bearing a non-trivial personal cost, subject to continuous community oversight, with no single entity able to capture a dominant share of consensus power. Four properties encode these invariants. They are not a menu of desirable features — they are load-bearing elements of the security argument. Losing any one degrades the model; losing two or more can break it.

| Property | What it secures | Mechanism |
|---|---|---|
| **Accountability** | Operators are identifiable and have something to lose | Pledge (static bond) + delegation (dynamic discipline) |
| **Delegation as counter-power** | Community oversight substitutes for governance | Revocable staking rights create a credible exit threat |
| **Sybil resistance** | *k* pools represent *k* independent entities | Pledge bonus makes fragmentation economically dominated |
| **Decentralisation** | No single actor dominates block production | Calibrated entry barrier: commitment, not wealth alone |

#### 3.4.1 Accountability — the bond and the enforcer

The Ouroboros security model assumes that block producers are *identifiable* and have *something to lose*. Accountability is the property that connects a block-producing identity to a real economic cost: if the operator misbehaves — equivocates, censors, goes offline — there must exist a mechanism through which that behaviour imposes a loss on the operator that is proportional to the damage it causes.

Cardano's consensus layer does not implement slashing. Unlike protocols that destroy a validator's deposit upon detectable misbehaviour, Ouroboros relies on an indirect accountability structure built from two components that operate at different time-scales:

**Pledge as a static bond.** Capital registered in the pool certificate creates a visible, on-chain commitment. It is not locked in the custodial sense — the operator retains the keys — but it is *declared*: the protocol observes it at every epoch boundary, and failure to maintain the declared amount triggers a total reward wipe for that epoch (the pledge-unmet penalty). This bond serves a signalling function: an operator who has pledged substantial capital has an observable, verifiable stake in the pool's continued operation. The cost of abandoning or sabotaging the pool includes forfeiting the competitive position that pledge confers.

**Delegation as a dynamic discipline.** Delegators can revoke their delegation unilaterally, at any epoch boundary, without the operator's consent (SL-D1 [§3.4.6](#346-the-structural-requirement)). This is the protocol's primary enforcement mechanism: an operator who degrades performance, raises fees exploitatively, or behaves dishonestly faces capital flight. The pool shrinks, rewards drop, and the operator's income falls — not because the protocol punished them, but because the community withdrew its approval.

These two components are not redundant. The static bond ensures that the operator has a *minimum* cost of entry and a *minimum* exposure to the pool's fate — it exists even when no delegator is watching. The dynamic discipline ensures that the operator faces *continuous* pressure to maintain performance — it operates even when the bond is too small to matter on its own.

> A system that relies on only one component is fragile. Pledge without delegation produces accountability that is entirely self-referential: the operator answers to no one but themselves. Delegation without pledge produces accountability without cost: the operator can walk away from a misbehaving pool and register a new one at zero loss. The security model requires both — a floor of personal exposure *and* a continuous external check.

#### 3.4.2 Delegation as counter-power — the protocol's substitute for governance

Delegation in the SL-D1 design is not merely a capital-routing mechanism. It is the protocol's substitute for the governance layer that Cardano does not have at the consensus level.

The formal design separates control over *funds* (payment keys) from rights in the *PoS protocol* (staking keys). A delegator who assigns their staking key to a pool does not transfer custody — they grant a revocable licence to include their stake in the pool's block-production weight. The revocation is non-consensual: the protocol processes it without requiring the operator's approval. This makes delegation a *continuous approval signal* rather than a one-time capital commitment.

The disciplinary power of this mechanism depends on a structural condition: **the operator must need delegators more than delegators need the operator.** If a pool is filled entirely with the operator's own capital, delegator exit is irrelevant — there are no delegators to leave. If a pool is filled entirely by external delegation, delegator exit destroys the operator's income — but only if the operator has something at stake that makes rebuilding costly. The ratio between owner stake and delegated stake determines the *leverage* delegators have over the operator.

> [!NOTE]
> The pledge/delegation ratio is not an accounting detail — it defines the **power structure** within the pool. For the credible exit threat to function, both parties must have real stakes: the operator cannot be replaced without cost (their pledge and infrastructure matter), and the delegators cannot be ignored without cost (their departure shrinks the pool materially). This mutual dependency is the structural condition the mechanism must produce.

#### 3.4.3 Sybil resistance — making fragmentation expensive

The *k*-pool target assumes that *k* pools represent *k* *independent* block-producing entities. Sybil resistance is the property that makes this assumption defensible: creating additional block-producing identities must carry a cost high enough that fragmentation is economically dominated by honest, single-pool operation.

Brünjes & Kiayias (2020, §4) formalise this through the pledge parameter *a₀*. The reward function *r(σ, λ)* includes a pledge-sensitive component — the *λ_max · A(π, ν)* term — designed so that splitting capital across *n* pools dilutes the pledge bonus per pool. An attacker who fragments into *n* identities must commit capital linearly: each pool requires its own pledge to earn the bonus. The intended cost of a Sybil attack scales as *O(n)* in committed capital.

This defence has a quantitative precondition: **the pledge bonus must be large enough that forfeiting it is costly.** If the bonus is negligible, the Sybil tax approaches zero — an attacker who registers additional pools forgoes a bonus that was worth nothing to begin with. The formal mechanism exists; whether its economic bite is sufficient is a question of parameter calibration.

There is a subtlety in *how* the Sybil cost operates. When the cost comes from the pledge mechanism itself — forfeiting a meaningful bonus by fragmenting — it is the *design* that provides the defence. When the cost comes from raw capital requirements alone — an attacker simply running out of money — the defence is incidental, not engineered. The mechanism should ensure that the Sybil cost operates through the reward structure, not merely through wealth constraints that exist independently of the protocol.

#### 3.4.4 Decentralisation — more than a pool count

Decentralisation is the property that the *k*-pool target is supposed to produce: consensus power distributed across many independent entities, with no single actor or coordinated group able to dominate block production.

This requires more than a count of pools. A network with 500 pool certificates but a handful of controlling entities is not decentralised in any security-relevant sense — it merely *appears* decentralised at the certificate level while concentrating power at the entity level. Decentralisation requires that pools be operated by *distinct, economically independent* actors.

The entry barrier determines who can participate. If the barrier is too high — requiring enormous personal capital per pool — the operator set shrinks to a small, wealthy elite, and block production becomes permissioned by wealth. If the barrier is too low — requiring no meaningful commitment — entry is cheap, but competitive dynamics drive concentration through brand, convenience, and scale rather than through commitment. In both cases, the resulting equilibrium fails the decentralisation test, though for different structural reasons.

The mechanism must calibrate the barrier so that *commitment* — not wealth alone and not zero-cost entry — determines who can participate. The entry requirement should be high enough to be meaningful but low enough that operators of moderate means can enter, with delegation providing the growth path beyond the initial commitment.

#### 3.4.5 The properties are not independent

These four properties interact, and the interactions constrain the design space.

**Accountability × delegation-as-counter-power** are two faces of the same disciplinary structure. In a system without slashing, the *only* continuous enforcement mechanism is delegator exit. Pledge creates the *precondition* for that mechanism to have force — the operator must have something at stake — but delegation creates the *mechanism itself*. Accountability without delegation is a bond with no enforcer. Delegation without accountability is a vote with no consequence. Neither alone produces the discipline the protocol requires; together, they form a closed feedback loop.

**Sybil resistance × decentralisation** are in tension. A higher Sybil cost (requiring more pledge per pool) raises the entry barrier, which can reduce the number of independent operators. A lower Sybil cost (requiring less pledge) lowers the barrier but makes fragmentation cheap. The mechanism must find a calibration where the pledge requirement is high enough to impose a real cost on fragmentation but low enough — with delegation providing the remaining stake — that operators of moderate means can still enter and compete.

**Decentralisation × delegation-as-counter-power** reinforce each other when the equilibrium satisfies both. More independent operators means more choices for delegators, which strengthens the exit threat, which improves accountability, which makes the operator landscape more trustworthy, which attracts more delegation to committed pools. This is the virtuous cycle that §4 describes. It requires all four properties to be present simultaneously — remove any one, and the cycle breaks.

#### 3.4.6 The structural requirement

Taken together, the four properties impose a specific structural requirement on the equilibrium the mechanism must produce:

> [!IMPORTANT]
> **Each pool must combine meaningful operator commitment with meaningful external delegation.**
>
> Operator commitment (pledge) is required for accountability and Sybil resistance — it creates the bond that makes misbehaviour costly and fragmentation expensive. External delegation is required for counter-power and decentralisation — it creates the oversight mechanism and ensures that the entry barrier does not exclude operators of moderate means.

An equilibrium where operators fund pools entirely from their own capital satisfies accountability in a narrow sense but eliminates delegation's disciplinary role and restricts participation to the capital-rich. An equilibrium where operators commit nothing satisfies no property — the bond is absent, the Sybil defence is gone, and concentration emerges through market dynamics unchecked by any commitment signal.

The design's target is an equilibrium where the pledge/delegation ratio within each pool reflects genuine *interdependence* between operator and community — where neither party can be absent without degrading the security properties the consensus layer depends on. This is the benchmark against which any evaluation of the mechanism's actual performance must be measured.

<br>

## 4. The aligned dynamics — the virtuous cycle

When all three trajectories function as intended, they form a self-reinforcing cycle:

```
              ┌─────────────────────────────────────────┐
              │                                         │
              ▼                                         │
     Transaction demand                                 │
     funds the epoch pot                                │
              │                                         │
              ▼                                         │
     Rewards sustain                             A more secure,
     operator & delegator  ──▶  Committed    ──▶ decentralised network
     participation              operators        is a more valuable
              │                 compete on       network
              │                 pledge                  │
              ▼                    │                     │
     Delegators reward             │                    │
     the most committed  ◀────────┘                     │
     operators                                          │
              │                                         │
              └─────────────────────────────────────────┘
```

Transaction submitters generate economic demand that funds the epoch pot. The epoch pot rewards operators and delegators, making participation *individually rational* for both.

Operators compete on pledge commitment because the mechanism makes pledge the primary competitive dimension. Delegators reward the most committed operators because the mechanism makes commitment observable and economically meaningful.

This selective pressure produces an operator landscape that is decentralised (many independent, committed pools), accountable (delegators can exit at any time), and Sybil-resistant (pledge is costly to fake).

A more secure, decentralised network is a more valuable network — which attracts more transaction demand, which grows fee revenue, which funds better rewards, which sustains the cycle.

> [!NOTE]
> This is the **incentive-compatible equilibrium** the mechanism should converge toward: a state where each player, pursuing their own rational self-interest, reinforces the system's security properties — and where no player can improve their payoff by deviating.

The reward curve's success or failure is measured against this target.

> **Next:** The divergence analysis — examining what actually happens when each player class tries to play this game — has been moved to the [main report §2](../diagnostic/README.md#2-the-player-populations).
