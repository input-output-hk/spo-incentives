## 2. The divergence — when the optimal move breaks the game

> **Status:** Staging area. This section was extracted from [*The Intended Game*](the-intended-game/README.md) Part II and will be progressively integrated into the §1.2 narrative. Cross-references to §2–4 below refer to sections in *The Intended Game*.

Sections 2–4 of [*The Intended Game*](the-intended-game/README.md) described the game as designed: three player classes, each with a clear trajectory, converging on an incentive-compatible equilibrium. The SL-D1 reward curve was meant to produce that game. This section examines what actually happens when each player class tries to play it.

The approach is simple: follow each participant through the trajectory the mechanism promises (entry → progression → endgame), and identify the point at which the reward curve stops rewarding the intended strategy. Each perspective reveals a different face of the same structural failure — and together, they show why the equilibrium described in [*The Intended Game* §4](the-intended-game/README.md#4-the-aligned-dynamics) never materialises.

### 2.2 The delegator's experience

#### 2.2.1 Entry

A delegator holds ADA and wants yield. They open a pool explorer and look for the best pool to delegate to.

The mechanism promised ([*The Intended Game* §3.3](the-intended-game/README.md#33-delegators)) that as the system matures, delegators would be able to differentiate pools on commitment-based criteria — pledge level, track record, margin — and that delegation choices would function as an accountability mechanism ([*The Intended Game* §2.3](the-intended-game/README.md#23-delegators)), rewarding committed operators and punishing uncommitted ones.

The delegator starts comparing pools, looks at expected yield, and they all look roughly the same.

This is not an accident — it is a direct consequence of the reward formula. The size fraction ($\lambda_{\min} \approx 76.9\%$) dominates pool rewards and is entirely insensitive to pledge. The pledge fraction ($\lambda_{\max} \approx 23.1\%$) is the only component that differentiates on commitment, but its contribution is so small that it disappears into the noise of block-production variance.

A pool with 1M ADA pledged and a pool with zero pledge offer functionally identical yield.

The mechanism provides an accountability tool — liquid delegation — but removes the *information* needed to use it.

#### 2.2.2 Progression

A more diligent delegator looks at pledge levels directly, reasoning that even if yield differences are invisible, delegating to high-pledge pools on principle supports the network.

But this strategy has no economic payoff. Moving delegation from a zero-pledge pool to a high-pledge pool does not measurably improve the return. The delegator is subsidising the operator's commitment with *opportunity cost* (the foregone yield from a larger, more liquid pool) for a reward difference that cannot be measured.

Meanwhile, the pools that *are* easy to find — the ones with the largest delegations, the most name recognition, the exchange-affiliated ones — are rarely the most committed. They compete on convenience and brand, not pledge.

The information environment the mechanism creates does not help identify commitment; it buries it. The accountability mechanism described in [*The Intended Game* §2.3](the-intended-game/README.md#23-delegators) — delegators policing operators through capital reallocation — requires a signal to act on. The SL-D1 curve produces no such signal.

There is also a subtler problem: a delegator cannot distinguish an operator running one pool with genuine commitment from an operator running ten pools with minimal commitment each.

Multi-pool operators (MPOs) can spread capital across a fleet, pledging minimally per pool, and capture more total reward than a single committed operator. The mechanism does not penalise this — it arguably rewards it.

Delegation to any one pool in an MPO fleet reinforces a structure the mechanism was supposed to prevent.

#### 2.2.3 Endgame

The mechanism's theoretical optimum reveals the deepest problem: the delegator is not part of it.

The maximum-reward pool ($\pi = 1$, $\nu = 1$) is fully funded by the operator's own pledge. There is no room for delegation.

The reward curve's ideal state is a network of 500 private pools in which delegators play no role whatsoever. The accountability mechanism — the reason delegator participation matters for consensus security — is absent at the optimum.

Delegators are not just poorly served by the endgame; they are *excluded* from it.

#### 2.2.4 The delegator's verdict

The mechanism promises delegators a role as the network's accountability layer, but gives them no signal to act on, no economic reward for commitment-based choices, and an endgame that eliminates them entirely.

The rational response — confirmed on mainnet — is to delegate based on convenience, brand, or exchange integration, ignoring pledge completely.

The accountability function collapses.

### 2.3 The transaction submitter's experience

#### 2.3.1 Entry

A transaction submitter uses Cardano for settlement. They do not participate in the staking game directly, but they depend on its output: a sufficiently decentralised, secure, accountable network of block producers.

The mechanism promised ([*The Intended Game* §2.4](the-intended-game/README.md#24-the-dependency-chain)) that the reward curve would produce this by aligning operator and delegator incentives around commitment and community oversight.

The network the mechanism has actually produced tells a different story.

The independent operator base — the population the mechanism was designed for — has collapsed to 283 viable operators after removing MPO fleet members (O5). 78% of their stake is non-compliant. Their share of the network is declining.

The entities that dominate block production compete on fleet scale and delegation capture, not pledge commitment.

Structural populations (exchanges, institutional staking providers) totalling 7.39B ADA cannot pledge custodied assets at all — an architectural constraint that no parameter change can fix (§1.2.2 O4).

#### 2.3.2 Progression

The reserve is depleting. Monetary expansion — which currently funds ~99.8% of the epoch pot (§1.1.2 O1) — will decline as the reserve crosses its half-life.

The game's economic viability will progressively shift onto fee revenue — transaction submitters' fees.

Transaction submitters are being asked to fund, through increasing volume and willingness to pay, a staking game whose mechanism has failed to produce the security properties they depend on.

The operator landscape is consolidating rather than diversifying. The accountability layer is non-functional. The pledge mechanism — the protocol's Sybil defence — is unused: 95.6% of the pledge-bonus budget returns to reserve every epoch (§1.2.2 O1).

#### 2.3.3 Endgame

Transaction submitters need the network to be *more* secure and decentralised as it becomes more valuable — as the economic stakes of each transaction grow, so does the cost of a consensus failure.

But the mechanism's trajectory points in the opposite direction.

The reward curve optimises toward concentration (fewer, larger operators with minimal pledge) and away from the distributed, committed operator base that consensus security requires.

The incentive-responsive field holds only 36% of active stake (O6) — the rest is structurally immune to the reward signal.

The mechanism cannot course-correct through parameter changes alone because the populations it cannot reach (CEX, IVaaS, non-compliant MPOs) hold the majority of stake.

#### 2.3.4 The transaction submitter's verdict

The mechanism was supposed to produce the security properties transaction submitters depend on.

Instead, it has produced an operator landscape that is consolidating, an accountability layer that is inert, and a Sybil defence that is unused — and transaction submitters are about to become the primary funders of this system as the reserve depletes.

### 2.4 What the three perspectives reveal together

The three player experiences are not three separate failures — they are three views of a single structural contradiction.

The dependency chain described in [*The Intended Game* §2.4](the-intended-game/README.md#24-the-dependency-chain) requires *interdependence*: operators need delegators for scale, delegators need operators for block production, and the reward curve should make their partnership the individually rational path for both. The SL-D1 curve breaks this interdependence at every level:

- **At entry**, the operator has no visible tool to attract delegation based on commitment, and the delegator has no signal to differentiate on. The two players cannot find each other through the mechanism.
- **At progression**, increasing pledge produces no competitive advantage the delegator can detect, so the operator rationally abandons pledge as a strategy. The delegator, seeing no commitment-based signal, rationally delegates on convenience. Both players optimise away from the intended strategy — not because they are irrational, but because they *are* rational.
- **At endgame**, the reward curve's theoretical optimum eliminates the delegator entirely. The operator fills the pool with their own capital. The dependency chain collapses: the mechanism's ideal state is one where the accountability layer does not exist.

The result is not a failure of adoption or education. The players are not making mistakes — they are responding correctly to the incentives the mechanism actually provides.

The dominant strategy at every stage of the game, for every player class, is the exact opposite of what the protocol needs for consensus security.

The equilibrium the curve converges toward is not the one described in [*The Intended Game* §4](the-intended-game/README.md#4-the-aligned-dynamics). It is one where pledge is minimised, delegation is driven by brand rather than commitment, accountability is inert, and the operator landscape consolidates around fleet scale rather than individual commitment.

The mainnet evidence confirms this comprehensively: 95.6% of the pledge-bonus budget unused (§1.2.2 O1), 82% of what *is* used flowing to three entities (§1.2.2 O4), 73% of pools below viability (§1.2.2 O2), and the incentive-responsive field holding only 36% of active stake (O6).

The mechanism is not failing to reach equilibrium — it *has* reached equilibrium. It is simply the wrong one.

---

## Sandbox

> **Everything below this line is draft / work-in-progress material.**
> It will be restructured and integrated into the main document as sections are finalized.

---

## [SANDBOX] Cross-Cutting Analysis

### 2.1 Problem–Pipeline Map

<!-- TODO: table mapping each identified problem to the pipeline stage(s) where it originates -->
<!-- Columns: Problem | Pipeline Stage | Root Cause | Addressed by CIP(s) -->

### 2.2 CIP Coverage Matrix

<!-- TODO: matrix showing which CIPs address which problems, and whether they are complements or substitutes -->
<!-- Reuse the combination logic from the sandbox material -->

### 2.3 Combination Logic

<!-- TODO: migrate and clean up the combination compatibility analysis from sandbox §7 -->
<!-- Fee layer × Stake-cap layer independence, clean combinations, edge cases -->

### 2.4 Gaps & Open Questions

<!-- TODO: problems that no CIP addresses, parametrization unknowns, simulation needs -->

---

## 2. Fee Structure Adjustments equivalence

### 2.1 CIP-0023 margin floor

#### 2.1.1 Formulas

##### 2.1.1.1 SL-D1 (Original)

$$
m_{\text{eff}} := \max(m, m_{\min})
$$

##### 2.1.1.2 Reader-Friendly

$$
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, \mu^{\text{operator}}_{\text{min}})
$$

### 2.2 CIP-0023 operator/member substitution

#### 2.2.1 Formulas

##### 2.2.1.1 SL-D1 (Original)

$$
r_{\text{operator}}^{(23)} = r_{\text{operator}}(\hat f,c,m_{\text{eff}},s,\sigma),\qquad
r_{\text{member}}^{(23)} = r_{\text{member}}(\hat f,c,m_{\text{eff}},t,\sigma)
$$

##### 2.2.1.2 Reader-Friendly

$$
{Reward^{\text{operator}}}^{(23)} =
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(23)} =
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

### 2.3 CIP-0082 Stage 1

#### 2.3.1 Formulas

##### 2.3.1.1 SL-D1 (Original)

$$
c := 170
$$

##### 2.3.1.2 Reader-Friendly

$$
Cost^{\text{operator}}_{\text{fixed}} := 170
$$

### 2.4 CIP-0082 Stage 2

#### 2.4.1 Formulas

##### 2.4.1.1 SL-D1 (Original)

$$
c := 0,\qquad m_{\text{eff}} := \max(m, 0.03)
$$

##### 2.4.1.2 Reader-Friendly

$$
Cost^{\text{operator}}_{\text{fixed}} := 0,\qquad
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, 0.03)
$$

##### 2.4.1.3 SL-D1 (Original)

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

##### 2.4.1.4 Reader-Friendly

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

### 2.5 CIP-0082 Stage 3 and Stage 4

#### 2.5.1 Formulas

##### 2.5.1.1 SL-D1 (Original)

$$
k:=750 \Rightarrow z_0=\frac{1}{750},\qquad
k:=1000 \Rightarrow z_0=\frac{1}{1000}
$$

##### 2.5.1.2 Reader-Friendly

$$
k^{\text{protocol}}_{\text{targetPools}}:=750 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{750},\qquad
k^{\text{protocol}}_{\text{targetPools}}:=1000 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{1000}
$$

## 3. Pledge & Curve Adjustments equivalence

### 3.1 CIP-0050 capped eligible stake

#### 3.1.1 Formulas

##### 3.1.1.1 SL-D1 (Original)

$$
\sigma'_L := \min(\sigma, z_0, Ls)
$$

##### 3.1.1.2 Reader-Friendly

$$
\sigma^{\text{totalStaked},(L)}_{\text{capped}} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

### 3.2 CIP-0050 reward curve substitution

#### 3.2.1 Formulas

##### 3.2.1.1 SL-D1 (Original)

$$
f^{(50)}(s,\sigma)
= \frac{R}{1+a_0}
\left(
\sigma'_L + s'a_0\cdot\frac{\sigma'_L - s'\left(\frac{z_0-\sigma'_L}{z_0}\right)}{z_0}
\right)
$$

##### 3.2.1.2 Reader-Friendly

$$
PoolPot^{\text{optimal},(50)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(L)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

### 3.3 CIP-0037 dynamic saturation

#### 3.3.1 Formulas

##### 3.3.1.1 SL-D1 (Original)

$$
z_{\text{dyn}}(s) := z_0 \cdot \phi(s)
$$

##### 3.3.1.2 Reader-Friendly

$$
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})
:=
k^{\text{protocol}}_{\text{saturation}}\cdot \phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
$$

##### 3.3.1.3 SL-D1 (Original)

$$
\phi(s)=\max\!\left(\epsilon,\min\!\left(1,\frac{s}{s_{\text{ref}}}\right)\right)
$$

##### 3.3.1.4 Reader-Friendly

$$
\phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
= \max\left(
\epsilon^{\text{protocol}}_{\text{saturationFloor}},
\min\left(1,\frac{\pi^{\text{pledged}}}{\sigma^{\text{owner}}_{\text{pledgeRef}}}\right)
\right)
$$

### 3.4 CIP-0037 capped stake and reward curve substitution

#### 3.4.1 Formulas

##### 3.4.1.1 SL-D1 (Original)

$$
\sigma'_{37}:=\min(\sigma,z_{\text{dyn}}(s))
$$

##### 3.4.1.2 Reader-Friendly

$$
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

##### 3.4.1.3 SL-D1 (Original)

$$
f^{(37)}(s,\sigma)
= \frac{R}{1+a_0}
\left(
\sigma'_{37} + s'a_0\cdot\frac{\sigma'_{37} - s'\left(\frac{z_0-\sigma'_{37}}{z_0}\right)}{z_0}
\right)
$$

##### 3.4.1.4 Reader-Friendly

$$
PoolPot^{\text{optimal},(37)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(37)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

## 4. Status Quo

Status quo summary:

- Every pool faces the same global saturation threshold, $k^{\text{protocol}}_{\text{saturation}}=\frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$.
- Pool reward production depends on capped stake, capped pledge, and the global skin-in-the-game factor $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$.
- After performance adjustment, the realized pool allocation is split by fixed cost first, then by operator margin and stake ownership.
- If the operator fails to meet the registered pledge in an epoch, the pool allocation is zeroed.

### 4.1 Treasury & Pool Pots Distribution

These formulas define the epoch-level reward budget before any pool-level reward curve is applied.
They first build the gross pot from fees, non-refundable deposits, and reserve-sourced monetary expansion, then split that budget between the treasury and the pool side.

#### 4.1.1 Formulas

##### 4.1.1.1 Reader-Friendly

$$
Pot^{\text{epoch}}
= Fee^{\text{epoch}}_{\text{tx}}
+
Deposit^{\text{epoch}}_{\text{nonRefundable}}
+
\min\left(\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}},1\right)\rho^{\text{monetaryExpansion}}_{\text{rate}}(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

$$
PoolsPot^{\text{epoch}}
:=
(1-\tau^{\text{treasury}}_{\text{rate}})\,Pot^{\text{epoch}}
$$

$$
TreasuryPot^{\text{epoch}}
:=
\tau^{\text{treasury}}_{\text{rate}}\,Pot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} + TreasuryPot^{\text{epoch}}
= Pot^{\text{epoch}}
$$

##### 4.1.1.2 Mainnet Reader-Friendly

$$
Pot^{\text{epoch}}
= Fee^{\text{epoch}}_{\text{tx}}
+
Deposit^{\text{epoch}}_{\text{nonRefundable}}
+
\min\left(\frac{Blocks^{\text{epoch}}_{\text{produced}}}{21{,}600},1\right)\cdot 0.3\% \cdot \left(45\,\text{billion} - Supply^{\text{system}}_{\text{circulating}}\right)
$$

$$
PoolsPot^{\text{epoch}}
:=
80\% \cdot Pot^{\text{epoch}}
$$

$$
TreasuryPot^{\text{epoch}}
:=
20\% \cdot Pot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} + TreasuryPot^{\text{epoch}}
= Pot^{\text{epoch}}
$$

##### 4.1.1.3 Concept glossary

**Pot^{epoch}**  
Total reward pot available for distribution at the end of the epoch. It aggregates transaction fees, non‑refundable deposits, and the monetary expansion drawn from the reserve.

**Fee^{epoch}_{tx}**  
Total transaction fees collected during the epoch from all transactions included in blocks.

**Deposit^{epoch}_{nonRefundable}**  
Deposits that become permanently locked or effectively removed from circulation during the epoch (for example deposits that are not reclaimed).

**Blocks^{epoch}_{produced}**  
Number of blocks actually produced on chain during the epoch.

**Blocks^{epoch}_{expected}**  
Expected number of blocks during an epoch according to the protocol parameters.

**ρ^{monetaryExpansion}_{rate}**  
Monetary expansion rate controlling how much ADA is drawn from the reserve to fund epoch rewards.

**Supply^{system}_{total}**  
Maximum ADA supply defined by the protocol.

**Supply^{system}_{circulating}**  
Current circulating supply of ADA already issued into the system.

**T_∞**  
Maximum ADA supply defined by the protocol (same conceptual quantity as the total supply limit).

**T**  
Current circulating supply used when computing the remaining reserve.

**τ^{treasury}_{rate}**  
Treasury tax rate applied to the epoch pot before rewards are distributed to pools and delegators.

**PoolsPot^{epoch}**  
Portion of the epoch reward pot allocated to stake pools and delegators after the treasury share is taken.

**TreasuryPot^{epoch}**  
Portion of the epoch reward pot allocated to the treasury.

### 4.2 Pools Distribution

These formulas define how the epoch-level pools pot is distributed across individual pools before the operator/member split.
For each pool $i$, they first compute the theoretical pool entitlement from stake, pledge, and saturation, then apply apparent performance to obtain the actual pool allocation.

#### 4.2.1 Formulas

##### 4.2.1.1 Reader-Friendly

$$
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked}}_{\text{capped},i}
+
\pi^{\text{pledged}}_{\text{capped},i}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked}}_{\text{capped},i}
-
\pi^{\text{pledged}}_{\text{capped},i}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked}}_{\text{capped},i}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

$$
PoolPot^{\text{actual}}_{i}
:=
\bar p^{\text{pool}}_{\text{apparent},i}
\cdot
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
$$

$$
\sum_i PoolPot^{\text{actual}}_{i} \le PoolsPot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} - \sum_i PoolPot^{\text{actual}}_{i}
\quad \text{is not paid out and remains accounted in } (Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

##### 4.2.1.2 Mainnet Reader-Friendly

$$
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
= \frac{PoolsPot^{\text{epoch}}}{1+30\%}
\left(
\sigma^{\text{totalStaked}}_{\text{capped},i}
+
\pi^{\text{pledged}}_{\text{capped},i}\cdot 30\%
\cdot
\frac{
\sigma^{\text{totalStaked}}_{\text{capped},i}
-
\pi^{\text{pledged}}_{\text{capped},i}
\left(
\frac{0.2\%-\sigma^{\text{totalStaked}}_{\text{capped},i}}{0.2\%}
\right)
}{
0.2\%
}
\right)
$$

$$
PoolPot^{\text{actual}}_{i}
:=
\bar p^{\text{pool}}_{\text{apparent},i}
\cdot
PoolPot^{\text{optimal}}_{i}\left(\pi^{\text{pledged}}_{i},\sigma^{\text{totalStaked}}_{i}\right)
$$

$$
\sum_i PoolPot^{\text{actual}}_{i} \le PoolsPot^{\text{epoch}}
$$

$$
PoolsPot^{\text{epoch}} - \sum_i PoolPot^{\text{actual}}_{i}
\quad \text{is not paid out and remains accounted in } (Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

##### 4.2.1.3 Concept glossary

| Reader-Friendly | Meaning | Mainnet baseline |
| --- | --- | --- |
| $PoolsPot^{\text{epoch}}$ | Pool-side budget entering the pool reward curve | Inherited from section `4.1` |
| $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Skin-in-the-game effect strength | $30\%$ |
| $k^{\text{protocol}}_{\text{saturation}}$ | Pool saturation threshold | $0.2\%$ |
| $\sigma^{\text{totalStaked}}_{i}$ | Pool $i$ total-staked share, i.e. pledged $+$ delegated, before the saturation cap is applied | Dynamic |
| $\pi^{\text{pledged}}_{i}$ | Pool $i$ pledged share inside $\sigma^{\text{totalStaked}}_{i}$, before the saturation cap is applied | Dynamic |
| $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | Pool $i$ total-staked share after saturation cap | $\min(\sigma^{\text{totalStaked}}_{i},0.2\%)$ |
| $\pi^{\text{pledged}}_{\text{capped},i}$ | Pool $i$ pledged share after saturation cap | $\min(\pi^{\text{pledged}}_{i},0.2\%)$ |
| $PoolPot^{\text{optimal}}_{i}$ | Theoretical pool-$i$ allocation before performance adjustment | Dynamic |
| $\bar p^{\text{pool}}_{\text{apparent},i}$ | Apparent performance multiplier for pool $i$ | No fixed baseline; pool- and epoch-specific, typically near $1$ over time for a well-performing pool |
| $PoolPot^{\text{actual}}_{i}$ | Actual pool-$i$ allocation after performance adjustment | Dynamic |
| $\sum_i PoolPot^{\text{actual}}_{i}$ | Total actual allocations distributed across all pools | Dynamic |
| $PoolsPot^{\text{epoch}}-\sum_i PoolPot^{\text{actual}}_{i}$ | Undistributed remainder not paid out to pools. SL-D1 says it is "sent back to the reserves"; read that here as remaining accounted in $(T_{\infty}-T)$ / $(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})$, not as a literal round-trip transfer. | Dynamic |

### 4.3 Operator reward

$$
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
= \begin{cases}
PoolPot^{\text{actual}}_{i}, & PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}} \\
Cost^{\text{operator}}_{\text{fixed}}
+
\left(PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}\right)
\left(
\mu^{\text{operator}}
+
\left(1-\mu^{\text{operator}}\right)\frac{\pi^{\text{pledged}}_{i}}{\sigma^{\text{totalStaked}}_{i}}
\right), & PoolPot^{\text{actual}}_{i} > Cost^{\text{operator}}_{\text{fixed}}
\end{cases}
$$

### 4.4 Member reward

$$
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
= \begin{cases}
0, & PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}} \\
\left(PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}\right)\left(1-\mu^{\text{operator}}\right)\frac{\sigma^{\text{poolMember}}_{\text{delegated},i}}{\sigma^{\text{totalStaked}}_{i}},
& PoolPot^{\text{actual}}_{i} > Cost^{\text{operator}}_{\text{fixed}}
\end{cases}
$$

### 4.5 Pledge enforcement

$$
\text{if pledged amount is not met in epoch } \Rightarrow PoolPot^{\text{actual}}_{i} = 0
$$

---

## 5. Fee Structure Adjustments

### 5.1 CIP-0023 (minimum operator margin floor)

Proposal summary:

- CIP-0023 introduces a protocol minimum operator margin, $\mu^{\text{operator}}_{\text{min}}$.
- It does not change reward production, saturation, or the fixed fee.
- The only change is in the operator/member split: if a pool registers a lower margin, the protocol clamps it up to the minimum during reward calculation.
- The policy intent is to reduce zero-margin fee wars while preserving the rest of the Shelley reward pipeline.

Reward production is unchanged. Fee split uses margin floor:

$$
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, \mu^{\text{operator}}_{\text{min}})
$$

Use $\mu^{\text{operator}}_{\text{floored}}$ in operator/member formulas:

$$
{Reward^{\text{operator}}}^{(23)} =
Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(23)} =
Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
Cost^{\text{operator}}_{\text{fixed}},
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

Practical effect:
If a pool advertises a margin below the protocol floor, delegators still generate the same pool allocation as under status quo, but a larger share of that allocation is redirected to the operator through $\mu^{\text{operator}}_{\text{floored}}$.

---

### 5.2 CIP-0082 (staged fee-floor and k changes)

Proposal summary:

- CIP-0082 is a staged reform rather than a single formula swap.
- Stage 1 lowers the protocol fixed-fee floor to 170 ADA.
- Stage 2 removes the fixed-fee floor and replaces it with a minimum operator rate of 3%.
- Stages 3 and 4 increase the target number of pools, which lowers the saturation threshold from $\frac{1}{500}$ to $\frac{1}{750}$ and then $\frac{1}{1000}$ if those governance decisions are adopted.

#### 5.2.1 Stage 1

Stage 1 keeps the same reward equations, but reduces the protocol floor applied to fixed operator cost:

$$
Cost^{\text{operator}}_{\text{fixed}} := 170
$$

#### 5.2.2 Stage 2

Stage 2 is the core mechanism change: the fixed-fee floor is removed, and a minimum operator rate is enforced in the split formula.

$$
Cost^{\text{operator}}_{\text{fixed}} := 0,\qquad
\mu^{\text{operator}}_{\text{floored}} := \max(\mu^{\text{operator}}, 0.03)
$$

Equivalent CIP statement:

$$
\text{poolRateEff} = \max(\text{poolRate},\text{minPoolRate})
$$

Use $Cost^{\text{operator}}_{\text{fixed}}=0$ and $\mu^{\text{operator}}_{\text{floored}}$ in the same split functions:

$$
{Reward^{\text{operator}}}^{(82,\text{Stage 2})}
= Reward^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i},
0,
\mu^{\text{operator}}_{\text{floored}},
\pi^{\text{pledged}}_{i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

$$
{Reward^{\text{member}}}^{(82,\text{Stage 2})}
= Reward^{\text{member}}
\left(
PoolPot^{\text{actual}}_{i},
0,
\mu^{\text{operator}}_{\text{floored}},
\sigma^{\text{poolMember}}_{\text{delegated},i},
\sigma^{\text{totalStaked}}_{i}
\right)
$$

#### 5.2.3 Stage 3 and Stage 4

Stages 3 and 4 do not change the reward split logic directly. They change the protocol target pool count, so the same baseline reward function is recomputed with a smaller saturation size:

$$
k^{\text{protocol}}_{\text{targetPools}}:=750 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{750},\qquad
k^{\text{protocol}}_{\text{targetPools}}:=1000 \Rightarrow k^{\text{protocol}}_{\text{saturation}}=\frac{1}{1000}
$$

Recompute:

$$
\sigma^{\text{totalStaked}}_{\text{capped}}=\min(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}}),\qquad
\pi^{\text{pledged}}_{\text{capped}}=\min(\pi^{\text{pledged}},k^{\text{protocol}}_{\text{saturation}})
$$

in the same baseline reward function.

Practical effect:
Stage 2 shifts operator compensation away from fixed-fee protection and toward proportional fees, while Stages 3 and 4 make saturation tighter by design so the same total stake is spread across more target pools.

---

## 6. Pledge & Curve Adjustments

### 6.1 CIP-0050 (pledge leverage cap)

Proposal summary:

- CIP-0050 introduces a new leverage parameter, $L^{\text{protocol}}_{\text{pledgeLeverage}}$.
- A pool can only earn full rewards on stake that is supported by both the global saturation threshold and enough pledge.
- In practice, reward-eligible stake is capped at $L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}$ in addition to the normal saturation cap.
- The policy intent is to penalize large under-pledged pools and reduce MPO leverage without imposing a blanket penalty on small pools that are not over-leveraged.

Introduce pledge leverage:

$$
\sigma^{\text{totalStaked},(L)}_{\text{capped}} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by $\sigma^{\text{totalStaked},(L)}_{\text{capped}}$:

$$
PoolPot^{\text{optimal},(50)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(L)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(L)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

Then:

$$
PoolPot^{\text{actual},(50)}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal},(50)}_{i}
$$

with the same operator/member split forms.

Practical effect:
Once a pool grows beyond the leverage-supported level, additional stake no longer increases rewards. Delegators then have an incentive to move to pools whose pledge still supports full reward earning.

---

### 6.2 CIP-0037 (dynamic pledge-linked saturation)

Proposal summary:

- CIP-0037 replaces the single global saturation threshold with a pool-specific saturation threshold that depends on pledge.
- Low-pledge pools saturate earlier, while high-pledge pools preserve more headroom up to the global cap.
- The scaling rule uses a reference pledge level, $\sigma^{\text{owner}}_{\text{pledgeRef}}$, and a minimum floor, $\epsilon^{\text{protocol}}_{\text{saturationFloor}}$, so small pools are not forced all the way down to zero effective saturation.
- The policy intent is to make growth capacity depend more directly on capital commitment rather than only on raw delegated stake.

Dynamic saturation depends on pledge:

$$
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})
:=
k^{\text{protocol}}_{\text{saturation}}\cdot \phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
$$

$$
\phi^{\text{protocol}}_{\text{saturationScale}}(\pi^{\text{pledged}})
= \max\left(
\epsilon^{\text{protocol}}_{\text{saturationFloor}},
\min\left(1,\frac{\pi^{\text{pledged}}}{\sigma^{\text{owner}}_{\text{pledgeRef}}}\right)
\right)
$$

Capped pool stake becomes:

$$
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by $\sigma^{\text{totalStaked},(37)}_{\text{capped}}$ in the same baseline reward function:

$$
PoolPot^{\text{optimal},(37)}_{i}
= \frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
\sigma^{\text{totalStaked},(37)}_{\text{capped}}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-\sigma^{\text{totalStaked},(37)}_{\text{capped}}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

and:

$$
PoolPot^{\text{actual},(37)}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal},(37)}_{i}
$$

Practical effect:
Unlike CIP-0050, which adds an extra leverage cap, CIP-0037 changes the saturation threshold itself. The reward curve therefore becomes pool-specific: the same delegated stake can be fully rewarded in one pool but oversaturated in another depending on pledge.

---

## 7. Combination Logic

### 7.1 Combination compatibility (technical only)

This section is purely technical. It only describes which formulas can be combined cleanly in this document, and which combinations require an additional composition rule to be defined explicitly.

Two independent layers are modified across these proposals:

- Fee layer: the operator/member split after the per-pool allocation has already been computed. This is where `baseline`, `CIP-0023`, and `CIP-0082` operate.
- Stake-cap layer: the reward-eligible pool stake used inside $PoolPot^{\text{optimal}}_{i}$. This is where `baseline`, `CIP-0050`, and `CIP-0037` operate.

Because the two layers are independent in the current formulation, one rule from each layer can be combined directly.

#### 7.1.1 Clean combinations already defined in this document

| Fee rule | Stake-cap rule | Technical status | Meaning |
| --- | --- | --- | --- |
| baseline | baseline | Defined | Status quo |
| CIP-0023 | baseline | Defined | Minimum operator margin floor only |
| CIP-0082 | baseline | Defined | Fee reform only |
| baseline | CIP-0050 | Defined | Pledge leverage cap only |
| baseline | CIP-0037 | Defined | Dynamic pledge-linked saturation only |
| CIP-0023 | CIP-0050 | Defined by composition | Margin floor + leverage cap |
| CIP-0023 | CIP-0037 | Defined by composition | Margin floor + dynamic saturation |
| CIP-0082 | CIP-0050 | Defined by composition | Fee reform + leverage cap |
| CIP-0082 | CIP-0037 | Defined by composition | Fee reform + dynamic saturation |

#### 7.1.2 Same-layer combinations that are not canonical in this document

- `CIP-0023 + CIP-0082` is not treated as a standard combination here because both proposals modify the fee layer. A single effective fee rule must be chosen for the split step.
- `CIP-0050 + CIP-0037` is not treated as a standard combination here because both proposals modify the stake-cap layer. The document currently models them as alternative ways to redefine reward-eligible stake.

#### 7.1.3 Technically possible but requiring an explicit extra definition

The main advanced case is `CIP-0050 + CIP-0037`. If both are applied together, the natural composite capped stake is:

$$
\sigma^{\text{totalStaked},(50+37)}_{\text{capped}}
:=
\min\left(
\sigma^{\text{totalStaked}},
\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}),
L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}
\right)
$$

This combined cap can then replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ in the same baseline reward function. However, this document does not treat it as canonical unless that composite rule is explicitly adopted.

For `CIP-0023 + CIP-0082`, a combination is also technically possible, but only after defining precedence for the fee layer. In practice that means deciding whether `CIP-0082` supersedes `CIP-0023`, or whether one rule contributes parameters to a single merged effective fee rule.

---

### 7.2 Composition rule (combined scenarios)

- In the default formulation of this document, choose exactly one stake-cap rule: baseline / CIP-0050 / CIP-0037.
- Choose exactly one fee rule: baseline / CIP-0023 / CIP-0082.
- Cross-layer combinations are obtained by applying both selected rules in the same canonical pipeline.
- Same-layer combinations require an explicit extra definition before they become canonical formulas in this document.
- Apply the selected rules in the same canonical pipeline:

$$
Pot^{\text{epoch}}
\rightarrow
\left(TreasuryPot^{\text{epoch}},PoolsPot^{\text{epoch}}\right)
\rightarrow
PoolPot^{\text{optimal}}_{i}
\rightarrow
PoolPot^{\text{actual}}_{i}
\rightarrow
\left(Reward^{\text{operator}},Reward^{\text{member}}\right)
$$

## 8. Notation convention

- Player/entity goes in superscript: $x^{\text{player}}$
- Variable role/type goes in subscript: $x_{\text{role}}$
- Example used in this document: $\mu^{\text{operator}}$
- Greek base-symbol semantics used here:
  - $\sigma$: stake share variables (pronounced "SIG-muh" in English)
  - $\pi$: pledge share variables (pronounced "pie" in English)
  - $\bar p$: apparent performance factor
  - $\mu$: margin variables (pronounced "myoo" in English)

## 9. Symbol mapping (SL-D1 -> Reader-Friendly)

| SL-D1 symbol | Reader-Friendly symbol | Mapping detail |
| --- | --- | --- |
| $k$ | $k^{\text{protocol}}_{\text{targetPools}}$ | Direct rename |
| $z_0$ | $k^{\text{protocol}}_{\text{saturation}}$ | $k^{\text{protocol}}_{\text{saturation}} := \frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$ |
| $\sigma$ | $\sigma^{\text{totalStaked}}_{i}$ | $\sigma$ is reserved for total-staked-share variables (relative stake fractions), pronounced "SIG-muh" in English. The index $i$ identifies the pool. |
| $s$ | $\pi^{\text{pledged}}_{i}$ | $\pi$ is used for pledged-share variables to distinguish pledged stake from the full pool stake, pronounced "pie" in English. The index $i$ identifies the pool. |
| $\sigma'$ | $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | $\sigma^{\text{totalStaked}}_{\text{capped},i} := \min(\sigma^{\text{totalStaked}}_{i}, k^{\text{protocol}}_{\text{saturation}})$ |
| $s'$ | $\pi^{\text{pledged}}_{\text{capped},i}$ | $\pi^{\text{pledged}}_{\text{capped},i} := \min(\pi^{\text{pledged}}_{i}, k^{\text{protocol}}_{\text{saturation}})$ |
| $a_0$ | $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Direct rename |
| $R$ | $PoolsPot^{\text{epoch}}$ | Renamed for semantic precision: this is the post-treasury pool budget entering the reward curve, not the amount ultimately paid out. |
| $f$ | $PoolPot^{\text{optimal}}_{i}$ | Renamed to make the per-pool allocation explicit and indexed by pool $i$. |
| $\bar p$ | $\bar p^{\text{pool}}_{\text{apparent},i}$ | $p$ denotes performance; the bar denotes apparent/realized performance multiplier for pool $i$. |
| $\hat f$ | $PoolPot^{\text{actual}}_{i}$ | Renamed to make the realized per-pool allocation explicit and indexed by pool $i$. |
| $c$ | $Cost^{\text{operator}}_{\text{fixed}}$ | Direct rename |
| $m$ | $\mu^{\text{operator}}$ | $\mu$ denotes margin (pronounced "myoo" in English). |
| $t$ | $\sigma^{\text{poolMember}}_{\text{delegated},i}$ | Direct rename with pool index $i$. |

Additional reward-pot terms:

| SL-D1 symbol | Reader-Friendly symbol | Mapping detail |
| --- | --- | --- |
| $\tau$ | $\tau^{\text{treasury}}_{\text{rate}}$ | Direct rename |
| $F$ | $Fee^{\text{epoch}}_{\text{tx}}$ | Direct rename |
| $D$ | $Deposit^{\text{epoch}}_{\text{nonRefundable}}$ | Direct rename |
| $\eta$ | $\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}}$ | Keep the epoch block-production ratio explicit rather than introducing a standalone named symbol. |
| $\rho$ | $\rho^{\text{monetaryExpansion}}_{\text{rate}}$ | Monetary expansion parameter in SL-D1. |
| $T_{\infty}$ | $Supply^{\text{system}}_{\text{total}}$ | Total supply cap/reference |
| $T$ | $Supply^{\text{system}}_{\text{circulating}}$ | Current circulating supply |

## 10. Detailed variable glossary

Conventions:

| Rule | Meaning |
| --- | --- |
| $\sigma$ variables | Relative stake shares (fractions of total active stake), not absolute ADA |
| $Reward_{\cdot}$, $Cost_{\cdot}$, $Fee_{\cdot}$, $Deposit_{\cdot}$, $Reserve_{\cdot}$ | ADA-denominated quantities |
| $\tau^{\text{treasury}}_{\text{rate}}$, $\rho^{\text{monetaryExpansion}}_{\text{rate}}$, $\mu^{\text{operator}}$ | Unitless rates/fractions |

Core protocol control variables:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $k^{\text{protocol}}_{\text{targetPools}}$ | Protocol target number of pools (SL-D1 $k$) | Integer, $>0$ | Decentralization target anchor |
| $k^{\text{protocol}}_{\text{saturation}}$ | Saturation threshold per pool | Relative share | $k^{\text{protocol}}_{\text{saturation}}=\frac{1}{k^{\text{protocol}}_{\text{targetPools}}}$ |
| $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Skin-in-the-game effect strength (SL-D1 $a_0$) | Fraction, $\ge 0$ | Higher value increases pledge sensitivity |

Pool stake and pledge state:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\sigma^{\text{totalStaked}}_{i}$ | Total staked share in pool $i$ | Relative share | Total staked means pledged + delegated stake before the saturation cap is applied |
| $\pi^{\text{pledged}}_{i}$ | Pool-$i$ pledged share | Relative share | Pledged component inside $\sigma^{\text{totalStaked}}_{i}$ |
| $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | Pool-$i$ total-staked share after saturation cap | Relative share | $\min(\sigma^{\text{totalStaked}}_{i},k^{\text{protocol}}_{\text{saturation}})$ |
| $\pi^{\text{pledged}}_{\text{capped},i}$ | Pool-$i$ pledged share after saturation cap | Relative share | $\min(\pi^{\text{pledged}}_{i},k^{\text{protocol}}_{\text{saturation}})$ |
| $\sigma^{\text{poolMember}}_{\text{delegated},i}$ | Single member stake delegated into pool $i$ | Relative share | Split term uses $\sigma^{\text{poolMember}}_{\text{delegated},i}/\sigma^{\text{totalStaked}}_{i}$ |

Epoch reward-pot inputs:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\tau^{\text{treasury}}_{\text{rate}}$ | Treasury take rate | Fraction | Applied before pool distribution |
| $Fee^{\text{epoch}}_{\text{tx}}$ | Epoch transaction fees | ADA | Reward-pot input |
| $Deposit^{\text{epoch}}_{\text{nonRefundable}}$ | Epoch non-refundable deposits | ADA | Reward-pot input |
| $Blocks^{\text{epoch}}_{\text{produced}}$ | Blocks produced during the epoch | Count | Used in the SL-D1 performance ratio $\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}}$ |
| $Blocks^{\text{epoch}}_{\text{expected}}$ | Expected blocks for the epoch under ideal conditions | Count / expectation | Kept explicit to avoid treating $\eta$ as a standalone protocol parameter |
| $Supply^{\text{system}}_{\text{circulating}}$ | Current circulating supply | ADA | Used as the $T$ term in $T_{\infty}-T$ |
| $\rho^{\text{monetaryExpansion}}_{\text{rate}}$ | Monetary expansion rate | Fraction | Scales the monetary-expansion term $\left(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}}\right)$ |
| $Supply^{\text{system}}_{\text{total}}$ | Total supply cap/reference | ADA | Used as the $T_{\infty}$ term; $Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}}$ is the reserve balance entering the formula |
| $Pot^{\text{epoch}}$ | Epoch gross reward pot before treasury split | ADA | Helper concept: fee + deposits + reserve-sourced monetary expansion |
| $PoolsPot^{\text{epoch}}$ | Epoch pool pot after treasury split | ADA | Net pool budget entering the reward curve before pool-level underdistribution |
| $TreasuryPot^{\text{epoch}}$ | Epoch treasury pot | ADA | Treasury share cut from the same gross pot before pool distribution |

Pool performance and payout split:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\bar p^{\text{pool}}_{\text{apparent},i}$ | Apparent pool-$i$ performance multiplier | Fraction | Typically near $[0,1]$ |
| $PoolPot^{\text{optimal}}_{i}$ | Optimal pool-$i$ allocation before performance adjustment | ADA | Reward-curve output for pool $i$ before performance adjustment |
| $PoolPot^{\text{actual}}_{i}$ | Actual pool-$i$ allocation | ADA | $PoolPot^{\text{actual}}_{i}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot PoolPot^{\text{optimal}}_{i}$ |
| $Cost^{\text{operator}}_{\text{fixed}}$ | Fixed operator fee | ADA/epoch | Charged first from the pool-$i$ allocation |
| $\mu^{\text{operator}}$ | Operator variable margin | Fraction | Usually in $[0,1]$ |
| $Reward^{\text{operator}}$ | Total operator reward | ADA | Fixed cost + margin + owner share |
| $Reward^{\text{member}}$ | Member/delegator reward | ADA | Remainder after fixed cost and margin split |

CIP-specific extension variables:

| Symbol | Meaning | Unit / Domain | Notes |
| --- | --- | --- | --- |
| $\mu^{\text{operator}}_{\text{min}}$ | Minimum operator margin floor | Fraction | CIP-0023 / CIP-0082 |
| $\mu^{\text{operator}}_{\text{floored}}$ | Effective operator margin | Fraction | $\max(\mu^{\text{operator}},\mu^{\text{operator}}_{\text{min}})$ |
| $L^{\text{protocol}}_{\text{pledgeLeverage}}$ | Pledge leverage multiplier | Scalar | CIP-0050 cap with $L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}$ |
| $\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}})$ | Dynamic saturation threshold | Relative share | CIP-0037 pledge-dependent saturation |
| $\sigma^{\text{owner}}_{\text{pledgeRef}}$ | Reference pledge level | Relative share | CIP-0037 normalization anchor |
| $\epsilon^{\text{protocol}}_{\text{saturationFloor}}$ | Minimum floor for dynamic saturation scale | Fraction | Floor in $\phi^{\text{protocol}}_{\text{saturationScale}}$ |
