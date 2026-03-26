# The Intended Game: A Narrative Description of the Consensus Incentive Mechanism

> **Status:** Working document — companion to the main [Cardano Reward Pipeline](../../../cardano-reward-analysis.md) analysis (§1.2) and the CPS [*Closing the Consensus Incentive Gap*](../cps/README.md).

## Motivation

The formal game-theoretic properties of the Cardano reward curve were established in *Reward Sharing Schemes for Stake Pools* (Brünjes, Kiayias et al., 2020, EuroS&P), which proves that $k$ pools is a Nash equilibrium under certain assumptions. The engineering specification *SL-D1* (Kant, Brünjes & Coutts, 2019) translates those results into protocol-level formulas and parameters.

What neither document provides is a **narrative description of the game as it should play out** — the players, their motivations, how they enter and progress, and the equilibrium they should converge toward. This matters because evaluating whether the mechanism *works* requires a clear picture of what *working* looks like — not as a mathematical proof, but as a readable account that the community and CIP authors can reason about.

This document produces that missing description.

## 1. The design objective

The protocol needs a specific set of properties at this layer: a sufficiently large number of independent block producers, each with meaningful personal capital at risk (*Sybil resistance*), subject to continuous community oversight (*accountability*), with no single entity able to capture a dominant share of consensus power (*decentralisation*). These are not aspirational qualities — they are the security invariants that the protocol's consensus layer depends on.

Cardano cannot enforce these properties by fiat. It has no licensing authority, no operator selection committee, no means of compelling participation. It must instead rely on *mechanism design*: defining a set of economic rules — the reward curve — such that rational, self-interested participants, each optimising their own payoff, collectively produce and maintain the desired system properties. The reward curve *is* the mechanism. Its success or failure is measured by a single criterion: does the *equilibrium* — the stable state toward which rational play converges — exhibit the security invariants above?

For this to work, two conditions must hold. First, participation must be *individually rational*: each player must be better off entering the game than staying out. Second, the mechanism must be *incentive-compatible*: the strategy that maximises each player's individual reward must also be the strategy that reinforces the system's security properties. When these conditions hold, the protocol does not need to trust its participants — it only needs them to be rational.

## 2. The players

The mechanism operates through three distinct classes of participant. Each has a different *motivation* for entering the game, a different set of *actions* (in mechanism-design terms, a different *strategy space*), and a different *trajectory* — the way their participation evolves as the system matures. Understanding all three is necessary before evaluating whether the reward curve aligns them correctly.

### 2.1 Transaction submitters

Transaction submitters are the source of economic demand.

- **Motivation.** They need reliable, censorship-resistant settlement. They do not participate in the staking game directly — they are *users* of the service that the game produces. Their willingness to pay fees is a revealed-preference signal: it measures the real-world value the network delivers.
- **How they operate.** They submit transactions and pay fees. Those fees — together with the monetary expansion draw from the reserve — fund the epoch pot that the reward pipeline distributes (§1.1). Transaction submitters are the reason the system exists: without them, there is no economic activity to secure, and no sustainable revenue to fund the operators who secure it.
- **How they evolve.** In the current regime, transaction fees are negligible (~0.19% of the epoch pot — §1.1.2 O1). The game is almost entirely funded by monetary expansion from a depleting reserve. As the reserve crosses its half-life and expansion shrinks (§1.1.2 O2), the system's economic viability progressively shifts onto fee revenue. Transaction submitters are therefore a latent constraint: marginal today, existential tomorrow. Their long-term participation is what makes the staking game *sustainably worth playing* for every other participant.

### 2.2 Operators

Operators register pools and produce blocks.

- **Motivation.** Operators seek a return on two forms of capital: the ADA they pledge and the infrastructure they maintain. A rational operator enters the game when the expected reward — block production fees, pool margin, and stake-proportional share — exceeds the combined opportunity cost of pledged capital and operational expenses. In mechanism-design terms, the *participation constraint* must be satisfied: the operator must be better off running a pool than simply delegating the same ADA.
- **How they operate.** Their primary strategic instrument is **pledge**: personal capital locked into the pool. Pledge serves as the protocol's *commitment mechanism* — the signal through which an operator demonstrates alignment with the network's interests. An operator who pledges significant ADA has more to lose from protocol failure or malicious behaviour than one who pledges nothing. This "skin in the game" is the protocol's primary defence against Sybil attacks. Operators also set a *margin* (their fee) and maintain infrastructure quality (uptime, latency) — but the reward curve at this layer is primarily sensitive to pledge and total stake, not operational quality.
- **How they evolve.** A new operator starts with a small pledge, minimal delegation, and sub-viable block production. Over time, the intended trajectory is one of *increasing commitment*: as the operator builds reputation and attracts delegation, they pledge more, their pool grows, and they earn a larger share of the pools pot. The mechanism should make each step up in pledge produce a measurable competitive advantage — visible to delegators and economically meaningful to the operator — so that the progression from "new pool" to "established pool" to "fully committed pool" is a legible arc that both players can follow.

### 2.3 Delegators

Delegators allocate stake to pools of their choice.

- **Motivation.** Delegators seek yield on their ADA holdings with minimal effort and risk. They do not produce blocks and bear no operational cost. Their decision is purely allocative: which pool to delegate to, and when to move. A rational delegator maximises risk-adjusted return, favouring pools with high expected yield, reliable performance, and trustworthy operators.
- **How they operate.** Their strategic instrument is **liquid delegation**: the ability to freely choose a pool — and freely withdraw at any time. This makes delegation a *continuous approval signal*. No operator can capture stake permanently; an operator who underperforms or behaves badly faces immediate capital flight. Liquid delegation is the protocol's *accountability mechanism* and its primary anti-monopoly tool. But this mechanism only functions if pools *need* delegators — if operators depend on community-sourced stake to reach their optimal reward. Without this dependency, delegators have no leverage and the accountability channel collapses.
- **How they evolve.** Delegators respond to the information environment the mechanism creates. Early on, when pools are new and differentiation is low, delegation may be driven by brand, community ties, or social signals. As the mechanism matures, delegators should increasingly be able to differentiate pools on *commitment-based criteria* — pledge level, track record, margin policy — and reallocate accordingly. The mechanism should make these criteria observable and economically meaningful, so that delegator behaviour reinforces the operator progression described above: committed pools attract more delegation, which rewards commitment further, creating a virtuous cycle.

### 2.4 The dependency chain

These three roles form a dependency chain. Transaction submitters generate the economic value that funds the game. Operators commit capital and infrastructure to secure the network that processes those transactions. Delegators allocate capital to select and police the operators. The mechanism's task is to make each link *individually rational* and *incentive-compatible* — so that the chain holds without requiring trust between participants.

At this layer (pool distribution), the reward curve directly governs the operator–delegator relationship. Neither player alone should be able to maximise rewards — the mechanism deliberately requires both. This *interdependence* is the core of the design: operators need delegators for scale, delegators need operators for block production, and the reward curve should make their partnership the individually rational path for both. Transaction submitters are upstream — their contribution is mediated through the epoch pot (§1.1) — but they set the ultimate economic boundary within which the operator–delegator game plays out.

## 3. The progression

Each player class experiences the game through its own trajectory — entry, progression, and endgame. A well-designed mechanism makes each trajectory *individually rational* at every stage, so that no player has a reason to drop out or deviate.

### 3.1 Transaction submitters

- **Entry.** Early adopters use the network for basic settlement. Transaction volume is low, and fees contribute negligibly to the epoch pot. The game is almost entirely funded by monetary expansion from the reserve — a bootstrap subsidy that makes staking rewards viable before organic demand exists.
- **Progression.** As the network matures, transaction volume and diversity grow. Fee revenue increases, gradually reducing dependence on the reserve. The ratio of fees to expansion becomes a measure of the system's economic maturity.
- **Endgame.** Fee revenue fully replaces monetary expansion as the primary funding source for the epoch pot. The staking game is self-sustaining: operators and delegators are paid by the economic activity they secure, not by a depleting reserve. The protocol has achieved *economic self-sufficiency*.

### 3.2 Operators

- **Entry.** A new operator registers a pool, pledges an initial amount, and begins attracting delegation. The mechanism must make this *individually rational*: the expected payoff should offer a credible path forward — not just survival, but growth — so that the *participation constraint* is met from the start.
- **Progression.** As the operator builds reputation and delegation, the mechanism should reward increasing pledge commitment. Each step up in pledge should produce a measurable competitive advantage — visible to delegators, economically meaningful to the operator. The progression from "new pool" to "established pool" to "fully committed pool" should be a legible arc that both operators and delegators can follow.
- **Endgame.** The operator has committed deeply (high pledge) and earned broad delegation. Their pool captures the maximum reward the protocol offers. This state should require *both* high pledge and high delegation to reach — it cannot be attained by capital alone or by delegation alone.

### 3.3 Delegators

- **Entry.** A new delegator selects a pool and allocates stake. Early on, differentiation between pools is low — delegation may be driven by brand, community ties, or social signals rather than on-chain metrics. The mechanism must still make participation *individually rational*: delegation yield should exceed the opportunity cost of holding idle ADA.
- **Progression.** As the pool landscape matures and the mechanism produces legible differences between pools, delegators increasingly differentiate on *commitment-based criteria*: pledge level, track record, margin policy. Delegation flows toward the most committed operators and away from uncommitted ones. The accountability mechanism becomes active — delegators are now *policing* operator behaviour through capital reallocation.
- **Endgame.** Delegators act as an efficient market for operator commitment. Capital moves fluidly to the pools that best combine commitment and performance, and exits quickly from those that fall short. The accountability mechanism operates at full power: no operator can sustain high rewards without continuous community approval.

## 4. The aligned dynamics

When all three trajectories function as intended, they form a self-reinforcing cycle. Transaction submitters generate economic demand that funds the epoch pot. The epoch pot rewards operators and delegators, making participation *individually rational* for both. Operators compete on pledge commitment because the mechanism makes pledge the primary competitive dimension. Delegators reward the most committed operators because the mechanism makes commitment observable and economically meaningful. This selective pressure produces an operator landscape that is decentralised (many independent, committed pools), accountable (delegators can exit at any time), and Sybil-resistant (pledge is costly to fake). A more secure, decentralised network is a more valuable network — which attracts more transaction demand, which grows fee revenue, which funds better rewards, which sustains the cycle.

This is the *incentive-compatible equilibrium* the mechanism should converge toward: a state where each player, pursuing their own rational self-interest, reinforces the system's security properties — and where no player can improve their payoff by deviating. The reward curve's success or failure is measured against this target.

## 5. Where the design breaks

The SL-D1 reward curve fails at all three levels of this game. The failures are examined from the deepest (endgame) to the most visible (entry), because the endgame contradiction is the one that defines what the whole curve optimises toward.

**The endgame eliminates the delegator from the game entirely.** The reward function decomposes into two components: a **size fraction** ($\lambda_{\min} \approx 76.9\%$) that rewards delegation regardless of pledge, and a **pledge fraction** ($\lambda_{\max} \approx 23.1\%$) that rewards operator commitment. The formula's maximum — $P_{\max}$ — is reached when $\pi = 1$ and $\nu = 1$: the operator pledges the full saturation amount *and* the pool is fully saturated. But since pledge counts as stake, an operator who pledges $z_0$ (currently 77M ADA) fills the entire pool with their own capital. There is no room for delegators. The "dream" the reward curve defines is a pool with no community participation — a private operation where the operator is both the sole funder and the sole beneficiary. The accountability mechanism — delegators voting with their feet — is eliminated at the endgame because there are no feet left to vote with.

This means the reward curve's ideal state *contradicts the protocol's security model*. The mechanism designed to produce 500 pools anchored by community trust instead defines an optimum of 500 private pools with no delegator oversight. The anti-monopoly tool is absent precisely where rewards are highest.

**The endgame is also economically irrational.** Even setting aside the design contradiction, reaching $P_{\max}$ requires 77M ADA (~30M USD at recent prices) of personal capital. The incremental reward for this commitment is approximately 7.2K ADA/epoch ($\lambda_{\max} \cdot P_{\max}$), a yield of ~0.68%/yr on the pledged capital. The same 77M ADA passively delegated to any saturated pool would earn ~2.3%/yr — more than three times the return, with zero operational burden. The rational actor should never pledge. The curve therefore presents a double failure at the endgame: it asks operators to lock capital at a yield *below* the opportunity cost of delegating it, and the state it defines as optimal removes the delegator accountability layer. No rational progression path leads to the endgame, and even if it did, reaching it would weaken the network.

**The progression is invisible.** Even if an operator accepts the sub-optimal yield, the pledge bonus is too small to be a competitive differentiator. At median pledge, the bonus adds ~0.006% to pool rewards (O1). Delegators comparing pool yields cannot detect it. There is no visible signal that says "this pool is more committed" — the game's progression system produces no legible advantage at any realistic scale. An operator who pledges 1M ADA looks the same to delegators as one who pledges nothing. The delegator accountability mechanism cannot function because there is nothing for delegators to differentiate on.

**The entry creates a cliff, not a ramp.** 73% of pools sit below the viability threshold (O2). The transition from sub-viable to viable is not gradual — it is a cliff in block production frequency and economic sustainability. Below-viability pools owe 647K ADA/epoch in fixed costs but earn only 182K ADA — destroying value for delegators by 3.6× (O2). The curve does not offer a credible early-game path. New operators face a binary outcome: attract enough delegation to clear the viability cliff, or operate at a loss with no visible competitive tool (since pledge is invisible) to distinguish themselves.

**The result on mainnet.** The dominant strategy at every level of the game — entry, progression, endgame — is to maximise delegation and minimise pledge. This is the exact opposite of what the protocol needs for consensus security. And at the theoretical optimum the curve defines, the delegator — the protocol's anti-monopoly safeguard — is absent entirely.

The evidence confirms this at scale. 82% of the MPO-level pledge bonus flows to three entities — two by private choice, one by institutional mandate (O4). 41 of 48 capital-sufficient MPOs choose non-compliance, forfeiting ~550K ADA/epoch collectively, because they optimise across custody rules, governance, brand, and adjacent business lines — a multi-game environment the single-game formula cannot reach (O4). Structural populations (CEX, IVaaS) totalling 7.39B ADA cannot pledge custodied assets at all — an architectural constraint immune to any parameter change (O4). The incentive-responsive field holds only 36% of active stake (O6). The independent operator base — the population the mechanism was designed for — has collapsed to 283 viable operators after removing MPO fleet members, with 78% of their stake non-compliant and their share declining (O5). 95.6% of the pledge-bonus budget returns to reserve unused, unchanged since Shelley launch (O1).
