# The Intended Game: A Narrative Description of the Consensus Incentive Mechanism

> **Status:** Working document — companion to the main [Cardano Reward Pipeline](../../../cardano-reward-analysis.md) analysis (§1.2) and the CPS [*Closing the Consensus Incentive Gap*](../cps/README.md).

---

## Table of Contents

- [Motivation](#motivation)
- [1. The design objective](#1-the-design-objective)
- [2. The players](#2-the-players)
  - [2.1 Transaction submitters](#21-transaction-submitters)
    - [2.1.1 Motivation](#211-motivation)
    - [2.1.2 How they operate](#212-how-they-operate)
    - [2.1.3 How they evolve](#213-how-they-evolve)
  - [2.2 Operators](#22-operators)
    - [2.2.1 An open seat at the deflationary table](#221-an-open-seat-at-the-deflationary-table)
    - [2.2.2 The participation constraint](#222-the-participation-constraint)
    - [2.2.3 How they operate](#223-how-they-operate)
    - [2.2.4 How they evolve](#224-how-they-evolve)
  - [2.3 Delegators](#23-delegators)
    - [2.3.1 Motivation](#231-motivation)
    - [2.3.2 How they operate](#232-how-they-operate)
    - [2.3.3 How they evolve](#233-how-they-evolve)
  - [2.4 The dependency chain](#24-the-dependency-chain)
- [3. The progression](#3-the-progression)
  - [3.1 Transaction submitters](#31-transaction-submitters)
    - [3.1.1 Entry](#311-entry)
    - [3.1.2 Progression](#312-progression)
    - [3.1.3 Endgame](#313-endgame)
  - [3.2 Operators](#32-operators)
    - [3.2.1 Entry](#321-entry)
    - [3.2.2 Progression](#322-progression)
    - [3.2.3 Endgame](#323-endgame)
  - [3.3 Delegators](#33-delegators)
    - [3.3.1 Entry](#331-entry)
    - [3.3.2 Progression](#332-progression)
    - [3.3.3 Endgame](#333-endgame)
- [4. The aligned dynamics](#4-the-aligned-dynamics)

---

## Motivation

The formal game-theoretic properties of the Cardano reward curve were established in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020, EuroS&P), which proves that $k$ pools is a Nash equilibrium under certain assumptions. The engineering specification *SL-D1* (Kant, Brünjes & Coutts, 2019) translates those results into protocol-level formulas and parameters.

What neither document provides is a **narrative description of the game as it should play out** — the players, their motivations, how they enter and progress, and the equilibrium they should converge toward. This matters because evaluating whether the mechanism *works* requires a clear picture of what *working* looks like — not as a mathematical proof, but as a readable account that the community and CIP authors can reason about.

This document produces that missing description.

---

## 1. The design objective

The protocol needs a specific set of properties at this layer: a sufficiently large number of independent block producers, each with meaningful personal capital at risk (*Sybil resistance*), subject to continuous community oversight (*accountability*), with no single entity able to capture a dominant share of consensus power (*decentralisation*).

These are not aspirational qualities — they are the security invariants that the protocol's consensus layer depends on.

Cardano cannot enforce these properties by fiat. It has no licensing authority, no operator selection committee, no means of compelling participation. It must instead rely on *mechanism design*: defining a set of economic rules — the reward curve — such that rational, self-interested participants, each optimising their own payoff, collectively produce and maintain the desired system properties.

The reward curve *is* the mechanism. Its success or failure is measured by a single criterion: does the *equilibrium* — the stable state toward which rational play converges — exhibit the security invariants above?

For this to work, two conditions must hold.

First, participation must be *individually rational*: each player must be better off entering the game than staying out.

Second, the mechanism must be *incentive-compatible*: the strategy that maximises each player's individual reward must also be the strategy that reinforces the system's security properties.

When these conditions hold, the protocol does not need to trust its participants — it only needs them to be rational.

## 2. The players

The mechanism operates through three distinct classes of participant. Each has a different *motivation* for entering the game, a different set of *actions* (in mechanism-design terms, a different *strategy space*), and a different *trajectory* — the way their participation evolves as the system matures. Understanding all three is necessary before evaluating whether the reward curve aligns them correctly.

### 2.1 Transaction submitters

Transaction submitters are the source of economic demand.

#### 2.1.1 Motivation

They need reliable, censorship-resistant settlement. They do not participate in the staking game directly — they are *users* of the service that the game produces. Their willingness to pay fees is a revealed-preference signal: it measures the real-world value the network delivers.

#### 2.1.2 How they operate

They submit transactions and pay fees. Those fees — together with the monetary expansion draw from the reserve — fund the epoch pot that the reward pipeline distributes (§1.1). Transaction submitters are the reason the system exists: without them, there is no economic activity to secure, and no sustainable revenue to fund the operators who secure it.

#### 2.1.3 How they evolve

In the current regime, transaction fees are negligible (~0.19% of the epoch pot — §1.1.2 O1). The game is almost entirely funded by monetary expansion from a depleting reserve.

As the reserve crosses its half-life and expansion shrinks (§1.1.2 O2), the system's economic viability progressively shifts onto fee revenue.

Transaction submitters are therefore a latent constraint: marginal today, existential tomorrow. Their long-term participation is what makes the staking game *sustainably worth playing* for every other participant.

### 2.2 Operators

Operators register pools and produce blocks.

#### 2.2.1 An open seat at the deflationary table

A prospective operator believes in Cardano. ADA has a capped supply and a depleting reserve — it is structurally deflationary.

From this perspective, the consensus game looks like an investment thesis, not a job offer: by operating a pool, an operator continuously accumulates an asset whose scarcity increases mechanically over time. The nominal yield in ADA, compounded by the deflationary trajectory of the asset itself, makes the expected real return deeply attractive on a long horizon.

And critically, the entry should be *accessible* — the mechanism is supposed to let anyone with conviction and a realistic initial stake begin building this position. Not an exclusive club; an open, meritocratic game where commitment is the competitive edge.

This is the narrative that attracts operators: a credible, long-term capital accumulation path anchored in consensus participation, open to anyone who believes in the technology.

#### 2.2.2 The participation constraint

Operators seek a return on two forms of capital: the ADA they pledge and the infrastructure they maintain. A rational operator enters the game when the expected reward — block production fees, pool margin, and stake-proportional share — exceeds the combined opportunity cost of pledged capital and operational expenses. In mechanism-design terms, the *participation constraint* must be satisfied: the operator must be better off running a pool than simply delegating the same ADA.

#### 2.2.3 How they operate

Their primary strategic instrument is **pledge**: personal capital locked into the pool.

Pledge serves as the protocol's *commitment mechanism* — the signal through which an operator demonstrates alignment with the network's interests. An operator who pledges significant ADA has more to lose from protocol failure or malicious behaviour than one who pledges nothing. This "skin in the game" is the protocol's primary defence against Sybil attacks.

Operators also set a *margin* (their fee) and maintain infrastructure quality (uptime, latency) — but the reward curve at this layer is primarily sensitive to pledge and total stake, not operational quality.

#### 2.2.4 How they evolve

A new operator starts with a small pledge, minimal delegation, and sub-viable block production. Over time, the intended trajectory is one of *increasing commitment*: as the operator builds reputation and attracts delegation, they pledge more, their pool grows, and they earn a larger share of the pools pot. The mechanism should make each step up in pledge produce a measurable competitive advantage — visible to delegators and economically meaningful to the operator — so that the progression from "new pool" to "established pool" to "fully committed pool" is a legible arc that both players can follow.

### 2.3 Delegators

Delegators allocate stake to pools of their choice.

#### 2.3.1 Motivation

Delegators seek yield on their ADA holdings with minimal effort and risk. They do not produce blocks and bear no operational cost. Their decision is purely allocative: which pool to delegate to, and when to move. A rational delegator maximises risk-adjusted return, favouring pools with high expected yield, reliable performance, and trustworthy operators.

#### 2.3.2 How they operate

Their strategic instrument is **liquid delegation**: the ability to freely choose a pool — and freely withdraw at any time.

This makes delegation a *continuous approval signal*. No operator can capture stake permanently; an operator who underperforms or behaves badly faces immediate capital flight.

Liquid delegation is the protocol's *accountability mechanism* and its primary anti-monopoly tool.

But this mechanism only functions if pools *need* delegators — if operators depend on community-sourced stake to reach their optimal reward. Without this dependency, delegators have no leverage and the accountability channel collapses.

#### 2.3.3 How they evolve

Delegators respond to the information environment the mechanism creates. Early on, when pools are new and differentiation is low, delegation may be driven by brand, community ties, or social signals.

As the mechanism matures, delegators should increasingly be able to differentiate pools on *commitment-based criteria* — pledge level, track record, margin policy — and reallocate accordingly.

The mechanism should make these criteria observable and economically meaningful, so that delegator behaviour reinforces the operator progression described above: committed pools attract more delegation, which rewards commitment further, creating a virtuous cycle.

### 2.4 The dependency chain

These three roles form a dependency chain.

Transaction submitters generate the economic value that funds the game. Operators commit capital and infrastructure to secure the network that processes those transactions. Delegators allocate capital to select and police the operators.

The mechanism's task is to make each link *individually rational* and *incentive-compatible* — so that the chain holds without requiring trust between participants.

At this layer (pool distribution), the reward curve directly governs the operator–delegator relationship. Neither player alone should be able to maximise rewards — the mechanism deliberately requires both.

This *interdependence* is the core of the design: operators need delegators for scale, delegators need operators for block production, and the reward curve should make their partnership the individually rational path for both.

Transaction submitters are upstream — their contribution is mediated through the epoch pot (§1.1) — but they set the ultimate economic boundary within which the operator–delegator game plays out.

## 3. The progression

Each player class experiences the game through its own trajectory — entry, progression, and endgame. A well-designed mechanism makes each trajectory *individually rational* at every stage, so that no player has a reason to drop out or deviate.

### 3.1 Transaction submitters

#### 3.1.1 Entry

Early adopters use the network for basic settlement. Transaction volume is low, and fees contribute negligibly to the epoch pot. The game is almost entirely funded by monetary expansion from the reserve — a bootstrap subsidy that makes staking rewards viable before organic demand exists.

#### 3.1.2 Progression

As the network matures, transaction volume and diversity grow. Fee revenue increases, gradually reducing dependence on the reserve. The ratio of fees to expansion becomes a measure of the system's economic maturity.

#### 3.1.3 Endgame

Fee revenue fully replaces monetary expansion as the primary funding source for the epoch pot. The staking game is self-sustaining: operators and delegators are paid by the economic activity they secure, not by a depleting reserve. The protocol has achieved *economic self-sufficiency*.

### 3.2 Operators

#### 3.2.1 Entry

A new operator registers a pool, pledges an initial amount, and begins attracting delegation. The mechanism must make this *individually rational*: the expected payoff should offer a credible path forward — not just survival, but growth — so that the *participation constraint* is met from the start.

#### 3.2.2 Progression

As the operator builds reputation and delegation, the mechanism should reward increasing pledge commitment. Each step up in pledge should produce a measurable competitive advantage — visible to delegators, economically meaningful to the operator. The progression from "new pool" to "established pool" to "fully committed pool" should be a legible arc that both operators and delegators can follow.

#### 3.2.3 Endgame

The operator has committed deeply (high pledge) and earned broad delegation. Their pool captures the maximum reward the protocol offers. This state should require *both* high pledge and high delegation to reach — it cannot be attained by capital alone or by delegation alone.

### 3.3 Delegators

#### 3.3.1 Entry

A new delegator selects a pool and allocates stake. Early on, differentiation between pools is low — delegation may be driven by brand, community ties, or social signals rather than on-chain metrics. The mechanism must still make participation *individually rational*: delegation yield should exceed the opportunity cost of holding idle ADA.

#### 3.3.2 Progression

As the pool landscape matures and the mechanism produces legible differences between pools, delegators increasingly differentiate on *commitment-based criteria*: pledge level, track record, margin policy. Delegation flows toward the most committed operators and away from uncommitted ones. The accountability mechanism becomes active — delegators are now *policing* operator behaviour through capital reallocation.

#### 3.3.3 Endgame

Delegators act as an efficient market for operator commitment. Capital moves fluidly to the pools that best combine commitment and performance, and exits quickly from those that fall short. The accountability mechanism operates at full power: no operator can sustain high rewards without continuous community approval.

## 4. The aligned dynamics

When all three trajectories function as intended, they form a self-reinforcing cycle.

Transaction submitters generate economic demand that funds the epoch pot. The epoch pot rewards operators and delegators, making participation *individually rational* for both.

Operators compete on pledge commitment because the mechanism makes pledge the primary competitive dimension. Delegators reward the most committed operators because the mechanism makes commitment observable and economically meaningful.

This selective pressure produces an operator landscape that is decentralised (many independent, committed pools), accountable (delegators can exit at any time), and Sybil-resistant (pledge is costly to fake).

A more secure, decentralised network is a more valuable network — which attracts more transaction demand, which grows fee revenue, which funds better rewards, which sustains the cycle.

This is the *incentive-compatible equilibrium* the mechanism should converge toward: a state where each player, pursuing their own rational self-interest, reinforces the system's security properties — and where no player can improve their payoff by deviating.

The reward curve's success or failure is measured against this target.

> **Note:** The divergence analysis — examining what actually happens when each player class tries to play this game — has been moved to the [main report §2](../../../cardano-reward-analysis.md#2-the-divergence--when-the-optimal-move-breaks-the-game).
