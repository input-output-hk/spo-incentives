# `k` parameter — Changing the scalar without revising the function that uses it

**Scope:** mechanical effect of raising `k` on the operator/delegator split **when the reward function $\hat f'(\nu, \pi, \bar p) = \bar p \cdot P_{\max} \cdot E(\nu, \pi)$ is held fixed** — only the scalar `k` moves, which flows through to $P_{\max} = R/k$ and $z_0 = 1/k$. Any evaluation that also changes the function itself (CIP-0050 via $\sigma'$ clipping, CIP-0037 via a new saturation curve) is out of scope and lives in [`../pools-distribution/`](../pools-distribution/README.md).

The `k` parameter — `stakePoolTargetNum` in the Cardano protocol — sets the **target number of pools** the network is calibrated for. It enters the SL-D1 reward formula in two derived places: the per-pool saturation threshold `z₀ = 1/k` and the per-pool reward ceiling `P_max = R/k`. Raising `k` mechanically compresses both: the saturation cap drops (more pools, smaller ceiling each) and the reward ceiling shrinks proportionally.

The protocol's only previous `k` change was Aug 2020 — `k: 150 → 500` — and it produced today's MPO landscape (83 attributed entities operating 475 productive pools, 75.5 % of productive stake). That is the natural-experiment baseline against which any future `k` raise must be evaluated. The mechanical question is whether the same outcome is structurally inevitable under the current weak-pledge regime, or whether something has changed in the operator population that would make a future raise behave differently.

This document evaluates **the `k` lever in isolation** — what changes when only the scalar `k` moves, holding the reward formula and the operator/member split formula fixed. It is the standalone analysis underneath CIP-0082 stages 3–4 (`k: 500 → 750 → 1000`) and a precondition for understanding why the V2 dependency chain treats `k` as the *last* lever to activate, not the first.

*The core question this evaluation asks: under the current weak-pledge equilibrium, does a `k` raise distribute new pool slots to independent operators, or does it absorb horizontally into existing MPO fleets — repeating the 2020 pattern?*

The argument proceeds in three parts:

1. **Introduction** (§1). The lever's identity, why it sits in the operator-delegator folder despite acting transversally, and the diagnostic findings that anchor the analysis (the 2020 `k: 150 → 500` outcome, current MPO concentration, the non-pledge equilibrium).

2. **Mechanism** (§2). Formula references inherited from the sub-flows, what `k` moves and what it does NOT move (a key result: hollow pool reward per ADA is `k`-invariant — the formula's `k` cancels), and the four mechanical channels: top-tail compression, pledge-amplification for self-pledged pools below the new saturation, hollow-pool invariance, and the structural-threshold invariance that means production and viability thresholds do not respond to `k`.

3. **Limits as a standalone proposal** (§3). Three synthesis findings — S1 (top-tail compression + narrow pledge amplification + bottom unchanged — Regresses + Delivers narrowly + Blind spot), S2 (a fine tool for a narrow demand-side segment, insufficient on the supply side because the formula stays intact — Regresses), S3 (MPO fleet absorption under weak pledge, historical and structural — Regresses).

The Executive summary below packages the verdict; the Findings summary table after it is the navigation index for §3.

## Executive summary

- **Verdict.** **A standalone `k`-raise is not a reform** — within the current SL-D1 formula it compresses the top of the reward distribution ($P_{\max} = R/k$ shrinks), amplifies the pledge bonus for a narrow band of fully self-pledged pools below the new saturation, and leaves hollow Sub-reliable and Healthy operators **mechanically unchanged**. The documented historical effect of raising `k` under weak pledge is MPO fleet expansion — the opposite of the nominal §3.4 concentration goal. Coherent **only** as step 3 of a three-step V2 sequence: fee-layer reform → stake-cap layer → `k` recalibration.
- **Instrument.** A single scalar protocol parameter `stakePoolTargetNum`. Governance path: standard Parameter Change action. No hard fork. No change to the reward formula or the operator/member split formula — only the scalar $k$ moves. Two derived quantities shift: the saturation threshold $z_0 = 1/k$ and the ceiling $P_{\max} = R/k$.
- **Three synthesis findings carry the verdict** — detailed in the next section and re-surfaced inline:
  - **S1** — A standalone `k`-raise compresses the top of the distribution and amplifies the pledge bonus for self-pledged pools; hollow pools below saturation are mechanically unchanged, and the production + viability thresholds (the two structural boundaries below saturation) are k-invariant (4 F's: §2.2–§3.1).
  - **S2** — A fine tool for a narrow segment, insufficient on its own: the demand side — the ROS-focused delegator market the k-raise targets — is a single-digit-percent slice of productive stake once custodial and loyal retail are removed; and the operator side stays in its non-pledge equilibrium because the reward formula that produces the equilibrium is not touched by a k-raise (2 F's: §3.2).
  - **S3** — Under the current weak-pledge regime, new pool slots are absorbed horizontally by existing MPO fleets — historical precedent plus the structural economics of fleet expansion (2 F's: §3.3).

## Table of Contents

- [Executive summary](#executive-summary)
- [Findings summary](#findings-summary)
- [1. Introduction](#1-introduction)
  - [1.1. Identity card](#11-identity-card)
  - [1.2. Origin and context](#12-origin-and-context)
  - [1.3. Related diagnostic findings](#13-related-diagnostic-findings)
  - [1.4. What the `k`-lever mechanically does vs what CIP-0082 advertises](#14-what-the-k-lever-mechanically-does-vs-what-cip-0082-advertises)
- [2. Mechanism](#2-mechanism)
  - [2.1. Formulas inherited from the sub-flows](#21-formulas-inherited-from-the-sub-flows)
  - [2.2. What `k` moves — and what it does not](#22-what-k-moves-and-what-it-does-not)
  - [2.3. Updated calibration at current parameters (epoch ~623, 2026/04)](#23-updated-calibration-at-current-parameters-epoch-623-202604)
    - [2.3.1. Pool reward across nine tiers](#231-pool-reward-across-nine-tiers-hollow-pool-epoch)
    - [2.3.2. Operator annualised revenue across nine tiers](#232-operator-annualised-revenue-across-nine-tiers-hollow-minpoolcost-170-yr)
    - [2.3.3. Delegator net ROS across nine tiers](#233-delegator-net-ros-across-nine-tiers-yr)
    - [2.3.4. Pledge-amplification channel](#234-pledge-amplification-channel-self-pledged-pools-bonus-from-math56)
    - [2.3.5. Per-entity revenue by n-MPO bracket](#235-per-entity-revenue-by-n-mpo-bracket-hollow-yr)
- [3. Limits of a standalone `k`-raise](#3-limits-of-a-standalone-k-raise)
  - [3.1. S1 — Top-tail compression + narrow pledge amplification; bottom unchanged](#31-k-levers1-top-tail-compression-narrow-pledge-amplification-bottom-unchanged)
  - [3.2. S2 — A fine tool for a narrow delegator segment, insufficient on the operator side](#32-k-levers2-a-fine-tool-for-a-narrow-delegator-segment-and-insufficient-on-the-operator-side-because-the-formula-is-unchanged)
  - [3.3. S3 — MPO fleet absorption under weak pledge](#33-k-levers3-mpo-fleet-absorption-under-weak-pledge)
  - [3.4. References](#34-references)

## Findings summary

CIP / lever evaluations use a three-level taxonomy mirroring the diagnostic's `SUBFLOW.O<n>.F<m>`: **S<n>** = synthesis-level verdict statement; **F<m>** = quantified finding anchored in §2 / §3 evidence; each F tagged **[D] Delivers / [R] Regresses / [B] Blind spot**. Each finding is re-surfaced as an inline callout where it emerges in the body.

| Code | Tag | Claim | Emerges in |
|---|---|---|---|
| **k-lever.S1** | | **A standalone `k`-raise compresses the top of the distribution and amplifies the pledge bonus for self-pledged pools; hollow pools below saturation are mechanically unchanged** | §3.1 |
| k-lever.S1.F1 | [R] | Above the new $z_0 = 1/k$, pool reward caps at $P_{\max} = R/k$. At $k: 500 \to 1000$, Large-healthy / Near-saturation / Saturated / Oversaturated pools converge to the same ceiling of **~11 942 ₳/ep** (–50 % vs today) | §2.3 pool-reward table, §3.1 |
| k-lever.S1.F2 | [D] | For self-pledged pools below the new saturation, the pledge bonus $\lambda_{\text{pledge}} A(\nu, \pi)$ scales as $k^2 \nu_{\text{old}}^3 \cdot R/k$ → **linear in k**. A fully self-pledged 15 M pool sees its bonus grow from +28 ₳/ep (k=500) to +191 ₳/ep (k=1000) | §2.3 pledge-amplification sub-table, §3.1 |
| k-lever.S1.F3 | [B] | Hollow pools below saturation: $\hat f' = R \cdot \lambda_{\text{size}} \cdot \sigma_{\text{rel}}$ — **k-independent**. Dormant, Sub-block, Sub-reliable, Healthy tiers see zero mechanical change in pool reward, operator revenue, or delegator ROS | §2.3 pool-reward table, §3.1 |
| k-lever.S1.F4 | [B] | **Of the three structural thresholds in the nine-tier taxonomy, `k` moves only saturation.** Production threshold $\text{stake}_n = n \cdot S_{\text{active}} / (L \cdot f)$ (Praos slot mechanics, $L$ and $f$ constant) and viability threshold $c / (R \lambda_{\text{size}} / \text{CircSupply})$ (hollow-pool break-even) contain no `k`. At mainnet today: 3-block threshold ≈ 2.92 M ₳, break-even ≈ 0.54 M ₳ (minPoolCost=170) — both k-invariant. A k-raise does not rescue any pool at the production or viability boundary | §2.2 "What `k` does not move", §3.1 |
| **k-lever.S2** | | **A fine tool for a narrow delegator segment, and insufficient on the operator side because the reward formula is unchanged** | §3.2 |
| k-lever.S2.F1 | [R] | **The ROS-focused delegator segment is a minority of productive stake.** Of 21.57 B ₳ productive stake: **4.55 B custodial** (21.1 %, funds not discretionary) + 17.02 B retail. Within retail, CEN.O4.F2: **42 %** of delegations are loyal (not moved in 2.7+ years) → effectively ROS-inert. Of the 21 % volatile delegations, CEN.O6.F1: **50.5 %** of switches land on yield-identical pools; non-identical moves show visibility asymmetry, not yield (CEN.O6.F3). Genuinely ROS-responsive segment ≈ **8 % of productive stake at best** — single-digit channel, not a network-level redistribution mechanism | §3.2 |
| k-lever.S2.F2 | [R] | **Changing `k` without revising the reward formula leaves the non-pledge equilibrium intact.** Operators don't pledge because pledge yield is structurally dominated by passive-delegation yield (POL.O2.F2: 0.68 %/yr vs 2.3 %/yr). POL.O2.F1: 78 % of stake at pledge < 1 %. POL.O5.F3: 41/48 saturation-scale MPOs forfeit the bonus. A k-raise amplifies the bonus for the narrow band of fully self-pledged pools below the new $z_0$, but keeps $A(0, \nu) = 0$ (hollow pools untouched) and leaves the surrounding formula — which is what produces the dominance relation — unchanged. **Insufficient on the operator side**: changing `k` cannot fix a non-pledge equilibrium produced by the formula around `k` | §3.2 |
| **k-lever.S3** | | **Under the current weak-pledge regime, new pool slots are absorbed horizontally by existing MPO fleets — historical precedent plus structural economics** | §3.3 |
| k-lever.S3.F1 | [R] | Historical `k: 150 → 500` (Aug 2020) produced the MPO fleet landscape POL.O5.F1 documents today (83 attributed entities control 75.5 % of productive stake across 475 productive pools) | §3.3 |
| k-lever.S3.F2 | [R] | Structural economics favour MPO fleet expansion over new-entrant entry: ~500 ADA registration cost per pool vs median MPO entity revenue of hundreds of K ₳/yr (operator-delegator §4.3.3); existing operational infrastructure scales horizontally; pledge is not binding (S2.F2). No mechanism in the k-raise forecloses the expansion pattern | §3.3 |

*Cross-CIP link.* This doc is the companion to **CIP-0082.S3** (pool-count expansions — stages 3 and 4). CIP-0082's stage 3 and 4 raise `k` inside the CIP-0082 timeline (3 epochs after the Margin swap); this doc evaluates the same lever in isolation from the fee reform of CIP-0082 stages 1–2. All findings below apply equally to CIP-0082 stages 3–4 under the standalone assumption.

## 1. Introduction

`k` (protocol parameter `stakePoolTargetNum`) is the scalar that sets Cardano's **target pool population**. It is not a CIP; it is an existing parameter whose adjustment is proposed recurrently in governance discussions and is embedded as stages 3–4 of CIP-0082. This doc evaluates a raise of `k` considered **in isolation** — no accompanying change to the reward formula, no accompanying stake-cap layer.

### 1.1. Identity card

| Field | Value |
| --- | --- |
| Parameter | `stakePoolTargetNum` |
| Current value | `k = 500` |
| Governance path | Standard Parameter Change action (Conway-era) |
| Hard fork required | No |
| Layer | Neither fee nor stake-cap — sets the scalar of the existing SL-D1 reward formula |
| Reference | [Pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards) |

### 1.2. Origin and context

**Historical moves.** `k` has been raised exactly once in Cardano's live protocol history: **`k: 150 → 500`** in August 2020, roughly one year after Shelley launch. The raise was motivated by the same nominal argument that recurs today — more pools → more decentralisation. The recorded post-event outcome was the emergence of the multi-pool-operator (MPO) pattern: existing operators registered additional pools to capture the new slots, and by 2022 the MPO fleet landscape had stabilised at the form the diagnostic documents today (POL.O5.F1).

**Current governance discussions.** Raising `k` is (i) embedded as stages 3–4 of CIP-0082 (`500 → 750 → 1000`), (ii) occasionally advanced as a standalone governance proposal outside the CIP-0082 package. This doc covers the standalone case; the CIP-0082-embedded case is analysed in [`cip-0082.md`](cip-0082.md) §3.3.

### 1.3. Related diagnostic findings

A standalone `k`-raise touches the operator/delegator split through the pool-reward ceiling $P_{\max} = R/k$ and the saturation threshold $z_0 = 1/k$. The advertised mechanism — "amplified pledge bonus steers delegation toward small pledged pools" — relies on a chain of behaviours the diagnostic measures directly. Seven findings bear on the analysis.

| Finding | Why shared | Supporting observations |
| --- | --- | --- |
| **POL.O2.F1 — 78 % of staked ADA sits in pools with pledge ratio < 1 %; stake-weighted median is 0.07 %** | **Pledge is rare across the entire stake distribution, not just at the small-pool end.** The amplified pledge bonus a k-raise provides rewards a behaviour the vast majority of the network does not currently exhibit, regardless of pool size | — |
| **POL.O2.F2 — Yield on pledge capital is 0.68 %/yr at best (full saturation + full self-pledge) vs ~2.3 %/yr on passive delegation** | The bonus is **priced as irrelevant by operators** because the pledge-capital opportunity cost (passive delegation yield) exceeds the pledge-bonus yield at every realistic scale. A k-raise amplifies a reward that still loses the opportunity-cost comparison | "The 'game' for operators is overwhelmingly about size (ν), not commitment (π)" — POL.O2.F2 |
| **POL.O6.F2 — 78 % of single-pool stake is non-compliant (pledge ratio < 2 %). Compliant + exemplary classes combined hold 5.8 % — economically negligible** | Even single-pool operators — the population the pledge mechanism was *designed* for — do not play the pledge game. Pledge rarity is a universal feature, not a bottom-tier feature | — |
| **POL.O5.F3 — 42 of 48 saturation-scale MPOs are non-compliant**, forfeiting ~550 K ADA/epoch (~40.2 M ₳/yr) in pledge bonus rather than locking capital | Among the population that *could* play the pledge game (has enough capital), 85 % choose not to. The amplified bonus from a k-raise does not change the opportunity-cost calculus enough to flip this choice | — |
| **POL.O5.F1 — 83 attributed entities operate 475 productive pools holding 16.29 B ₳ (75.5 % of productive stake)** | Three quarters of the network's stake is controlled by multi-pool operators who could absorb new slots created by a k-raise at ~500 ADA registration cost each | POL.O5.F2 (MPO saturation-scale split — 48 entities could self-pledge ≥ 1 pool) |
| **POL.O3.F5 / POL.O3.F6 — Tier boundaries are dynamic functions of `k`; CIPs targeting `k` reshape the upper tail only** | A k-raise is an upper-tail-only operation: $z_0$ halves, Large-healthy / Near-saturation / Saturated tiers reclassify; lower tiers (Sub-reliable and below) are untouched | — |
| **OPE.O7.F1 — Delegation is not clearly yield-following** (65.9 % of retail delegators sit in hollow MPO pools at 2.18 % net ROS, while hollow single-pool near-saturation pools at 2.34 % hold only 2.7 %) | The k-raise's advertised delegator-response channel is not supported by the observed distribution. Delegation *is not sticky* — delegators do move — but the observed flow aligns with brand, wallet integration, and active customer acquisition rather than ROS | OPE.O7.F2 (pledge premium is **negative** in retail data: balanced 1.98 % vs hollow 2.08 %) |

**What the diagnostic says about the population at the "pledge + scale" intersection.** The operators reaching high pledge ratios at meaningful scale are precisely the **"Custodial-by-pledge" segment** from [operator-delegator §4.3.3](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md) — 10 entities, 36 pools, 1.59 B ADA in total, only **122 delegations** across all of them. Their pledge ratio is high precisely *because* they do not compete for external delegation: the "delegated" stake is almost entirely affiliated capital (foundation treasury, protocol treasury, or closely-held funds). Named examples in the diagnostic include Cardano Foundation (93.9 % pledge ratio), Chuck/Bux (81.1 %), Liqwid (73.9 %) — all **private / treasury-affiliated pools**, not retail-delegation-capturing pools. The diagnostic is explicit: compliant class pools exist, "but only for operators who *own* their delegated stake". The "size + high pledge + active retail delegation capture" triad the k-raise mechanism implicitly targets is **structurally empty on mainnet** — the population that would make the k-raise redistribute does not exist.

### 1.4. What the `k`-lever mechanically does vs what CIP-0082 advertises

CIP-0082 stages 3–4 articulate the advertised mechanism directly:

> *"Stage 3 increases k from 500 to 750. [...] Firstly, increasing k increases the pledge benefit. The more effective the pledge benefit, the greater Cardano's sybil attack resistance. Secondly, increasing k may get stale delegations moving again by oversaturating large pools. This will cause many delegators to reconsider their delegation, potentially helping smaller community pools find delegations."*

This is a four-step causal chain:

1. More slots created → pool-count target rises (§3.4 pool-level metric).
2. Shrinking $z_0 = 1/k$ → amplified pledge bonus (§3.2 pledge signal).
3. Operators respond to amplified bonus by pledging more (operator-side behaviour).
4. Delegators respond to pledge-as-yield signal by migrating from saturated MPO pools to smaller pledged pools (demand-side behaviour → §3.1 viability support).

The mechanical content of a k-raise under the current formula:

| Step | Mechanical support |
| --- | --- |
| 1. More slots | **Direct** — pool-count target rises by construction |
| 2. Amplified pledge bonus | **Partial** — the bonus is amplified for fully self-pledged pools below the new $z_0$ (linear in `k`); hollow pools see *zero* change because $A(\nu, 0) = 0$; pools above the new $z_0$ see compression of the ceiling $P_{\max}$ |
| 3. Operators self-pledge more | **Not supported** — POL.O2.F2: pledge yield (0.68 %/yr) is structurally below passive-delegation yield (2.3 %/yr). POL.O5.F3: 42 of 48 saturation-scale MPOs already forfeit the bonus. Amplifying a dominated reward does not flip the opportunity cost |
| 4. Delegators migrate on yield signal | **Not supported** — OPE.O7.F1/F2: delegation is not sticky (delegators do move) but the observed flow does not clearly track ROS. And the only pools at the "high pledge + large size" intersection (Cardano Foundation 93.9 %, Chuck/Bux 81.1 %, Liqwid 73.9 %) are **private / treasury-affiliated**, not delegation-capturing — there is no observed destination population for the migration the mechanism assumes |

The chain breaks at **three of the four steps**. Moreover, the one step that does hold mechanically (step 1, more slots) only satisfies the *pool-level* §3.4 metric that POL.O5.F1 already identifies as an inadequate metric for concentration — entity-level Nakamoto regresses under weak pledge when the slots are absorbed horizontally by existing MPO fleets (§3.3).

**The population at the "pledge + scale" intersection is private, not delegation-capturing.** The operators reaching high pledge ratios at meaningful scale fall squarely in the **Custodial-by-pledge segment** (10 entities, 36 pools, 1.59 B ADA, only 122 delegations across the whole segment) — named examples include Cardano Foundation (93.9 %), Chuck/Bux (81.1 %), Liqwid (73.9 %). They reach high pledge ratios precisely *because* they do not compete for external delegation: their "delegated" stake is almost entirely affiliated capital. On the other side of the distribution, the retail-delegation-capturing brands in the **retail market** (516 entities, 809 pools, 17.02 B ADA, 98.3 % of all delegations — e.g. Everstake, Coinbase, Binance, AWP / Atomic Wallet) run at near-zero pledge and capture delegation through wallet integration and marketing. **The intersection "high pledge + large pool + retail delegation capture" is structurally empty on mainnet** — there is no observed population the k-raise's amplified bonus could redistribute stake toward.

## 2. Mechanism

This section imports the simplified reward formula from [pools-distribution §2.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#233-simplified-reward-function) and the operator/member split formula from [operator-delegator §1.1.1](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md) — the only formulas that matter for a standalone `k`-raise. **Nothing about them changes when `k` moves.** What changes is the scalar `k` itself and two derived quantities.

### 2.1. Formulas inherited from the sub-flows

**Pool reward** (hollow or pledged, below or above saturation):

$$\hat f'(\nu, \pi, \bar p) = \underbrace{\bar p}_{\text{performance}} \cdot \underbrace{P_{\max}}_{\text{ceiling}} \cdot \underbrace{E(\nu, \pi)}_{\text{envelope}}$$

with

$$P_{\max} = \frac{R}{k}, \qquad E(\nu, \pi) = \lambda_{\text{size}}\,\nu + \lambda_{\text{pledge}}\,A(\nu, \pi), \qquad A(\nu, \pi) = \nu^2 \cdot \pi \cdot \bigl[1 - \pi(1-\nu)\bigr]$$

Normalised coordinates $\nu = \sigma / z_0$ (stake saturation level) and $\pi = s / \sigma$ (within-pool pledge ratio), with $z_0 = 1/k$. On mainnet at $a_0 = 0.3$: $\lambda_{\text{size}} = 1/(1+a_0) \approx 76.9\,\%$ and $\lambda_{\text{pledge}} = a_0/(1+a_0) \approx 23.1\,\%$.

**Operator / member split** (case $\hat f' > c$, typical productive pool):

$$r_{\text{op}} = c + m(\hat f' - c) + (1-m)(\hat f' - c)\,\rho_{\text{op}}$$

$$r_{\text{mem}} = (1-m)(\hat f' - c)\,\rho_{\text{mem}}$$

with $c$ = `minPoolCost`, $m$ = pool margin, $\rho_{\text{op}} = s / \sigma$ = pledge-to-stake ratio, $\rho_{\text{mem}} = 1 - \rho_{\text{op}}$. For $\hat f' \le c$, the operator absorbs the entire pool reward and the delegator share is zero.

### 2.2. What `k` moves — and what it does not

A standalone `k`-raise modifies only the scalar $k$. The formulas above are unchanged. The derived quantities shift:

| Quantity | At $k = 500$ | At $k = 750$ | At $k = 1000$ | Nature of change |
|---|---:|---:|---:|---|
| $z_0 = 1/k$ (relative) | 0.2 % | 0.133 % | 0.1 % | Halved at $k=1000$ |
| $z_0$ absolute (×Supply ≈ 38.49 B ₳) | 77 M ₳ | 51.3 M ₳ | 38.5 M ₳ | Halved at $k=1000$ |
| $P_{\max} = R/k$ (at $R \approx 15.53$ M ₳) | 31 060 ₳/ep | 20 707 ₳/ep | 15 530 ₳/ep | Halved at $k=1000$ |
| Saturated hollow reward ($P_{\max} \cdot \lambda_{\text{size}}$) | ≈ 23 885 ₳/ep | ≈ 15 923 ₳/ep | ≈ 11 942 ₳/ep | Halved at $k=1000$ |

**What `k` does NOT move.**

- The envelope shape $E(\nu, \pi)$. $\lambda_{\text{size}}$ and $\lambda_{\text{pledge}}$ are fixed functions of $a_0$, which is not touched.
- The operator/member split formula. `minPoolCost` and `minPoolRate` / `poolRate` are independent parameters.
- **Per-ADA gross reward for a hollow pool below saturation.** Expanding $\hat f'$ for $\pi = 0, \nu < 1$:

$$\hat f' = \bar p \cdot \frac{R}{k} \cdot \lambda_{\text{size}} \cdot \nu = \bar p \cdot \frac{R}{k} \cdot \lambda_{\text{size}} \cdot \frac{\sigma_{\text{abs}} \cdot k}{\text{CircSupply}} = \bar p \cdot R \cdot \lambda_{\text{size}} \cdot \frac{\sigma_{\text{abs}}}{\text{CircSupply}}$$

**The `k` cancels.** For any hollow pool staying below saturation at the new `k`, the absolute reward is invariant. This is the key mechanical result that refutes the "k-raise pushes the viability line up" framing.

- **The production threshold.** From [pools-distribution §4.1.2.1](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#4121-block-production-threshold), the stake needed to produce $n$ blocks/epoch reliably is $\text{stake}_n \approx n \cdot S_{\text{active}} / (L \cdot f)$, where $L = 432\,000$ slots/epoch and $f = 0.05$ are fixed protocol constants. **No `k` in the formula.** The ~3 M ₳ "3-block threshold" and ~1 M ₳ "1-block threshold" are functions of Praos slot mechanics and participation ($S_{\text{active}}$) — not of `k`. A k-raise does not shift them.
- **The viability threshold.** From the [pools-distribution viability-threshold derivation](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#4122-viability-threshold), break-even stake = Fixed cost / (Reward per ADA per epoch) = $c / (R \lambda_{\text{size}} / \text{CircSupply})$. **No `k` in the formula** for hollow pools. At today's `minPoolCost = 170`, break-even ≈ 0.54 M ₳; at `minPoolCost = 340`, ≈ 1.09 M ₳. Neither number responds to `k`.

**Structural consequence.** Of the three thresholds that structure the nine-tier taxonomy (production, viability, saturation), **`k` acts on only one — saturation.** The sub-block tier (< ~1 M ₳) stays where it is under any k-raise; the sub-reliable tier (< ~3 M ₳ or more precisely < 0.54 M ₳ for break-even at minPoolCost=170) stays where it is; only the upper saturation line $z_0$ moves. A k-raise is strictly an upper-tail reparameterisation — it does not rescue any pool at the production or viability boundary.

> **Finding k-lever.S1.F4 [B] — Of the three structural thresholds in the nine-tier taxonomy, `k` moves only saturation.** Production threshold ($n \cdot S_{\text{active}} / (L \cdot f)$, Praos slot mechanics with $L$ and $f$ constant) and viability threshold ($c / (R \lambda_{\text{size}} / \text{CircSupply})$, hollow-pool break-even) contain no `k` — they are functions of participation, the reward pot, and fixed protocol constants. At mainnet today: 3-block threshold ≈ 2.92 M ₳, hollow-pool break-even ≈ 0.54 M ₳ (minPoolCost=170). Both are k-invariant. A k-raise is strictly an upper-tail reparameterisation — it **does not rescue any pool at the production or viability boundary**, regardless of how much $z_0$ shrinks. This strengthens S1.F3 (reward k-invariance) at the structural level: not only do rewards of hollow sub-saturation pools not change, the very boundaries that define "sub-block" and "sub-reliable" are k-invariant as well.

> **Finding k-lever.S1.F3 [B] — Hollow pools below saturation see zero mechanical change under a `k`-raise.** The formula collapses to $\hat f' = \bar p \cdot R \cdot \lambda_{\text{size}} \cdot \sigma_{\text{abs}} / \text{CircSupply}$ — the scalar `k` disappears. Consequently, operator revenue (capped at `minPoolCost`) and delegator ROS are both invariant for the entire Sub-reliable, Sub-block, and Dormant populations. The `k`-raise's rationale that it "helps small pools" has no mechanical foundation in the formula; any positive effect must come through a behavioural channel, not the reward mechanism.

### 2.3. Updated calibration at current parameters (epoch ~623, 2026/04)

All calibrations use today's parameters: $R \approx 15.53$ M ₳/epoch (PoolsPot), CircSupply × $z_0$ ≈ 38.49 B ₳, $a_0 = 0.3$, `minPoolCost = 170 ₳`, 73 epochs/year. Hollow-pool convention ($\bar p = 1$, $\pi = 0$, declared $m = 0$) matches CIP-0023 and CIP-0082 worked calibrations. Representative σ per tier follows the canonical nine-tier taxonomy from [pools-distribution §4.1.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions).

#### 2.3.1. Pool reward across nine tiers (hollow pool, ₳/epoch)

The ceiling $P_{\max} = R/k$ shrinks with `k`; the envelope $E(0, \nu) = \lambda_{\text{size}} \nu$ clips at $\nu = 1$ (saturation). Rewards below the new saturation are k-invariant; rewards at or above it are pinned to $P_{\max} \cdot \lambda_{\text{size}}$.

| Canonical tier | Rep. σ | $k = 500$ (current) | $k = 750$ | $k = 1000$ | Change |
|---|---:|---:|---:|---:|---|
| Zero-stake | 0 | 0 | 0 | 0 | — |
| Dormant | 50 K ₳ | 15.6 | 15.6 | 15.6 | unchanged (below all $z_0$) |
| Sub-block | 500 K ₳ | 155.8 | 155.8 | 155.8 | unchanged |
| Sub-reliable | 2 M ₳ | 623 | 623 | 623 | unchanged |
| Healthy | 15 M ₳ | 4 675 | 4 675 | 4 675 | unchanged |
| Large healthy | 50 M ₳ | 15 584 | 15 584 | **11 942** | compressed at $k=1000$ (now above $z_0$) |
| Near-saturation | 67 M ₳ | 20 883 | **15 923** | **11 942** | compressed from $k=750$ onward |
| Saturated | 77 M ₳ | 23 885 | 15 923 | 11 942 | compressed at every step |
| Oversaturated | 85 M ₳ | 23 885 | 15 923 | 11 942 | compressed at every step |

> **Finding k-lever.S1.F1 [R] — Top-tail compression.** At $k: 500 \to 1000$, every pool with σ above the new $z_0 = 38.5$ M ₳ converges to the same ceiling of ≈ 11 942 ₳/ep — a **–50 %** reward cut for today's Saturated-tier pools, and smaller cuts for Large-healthy. The k-raise acts exclusively on the upper tail. The rest of the nine-tier distribution is inert.

#### 2.3.2. Operator annualised revenue across nine tiers (hollow, `minPoolCost = 170`, ₳/yr)

Under today's fee structure, the operator take is the minimum of $\hat f'$ and `minPoolCost` for hollow pools. Since `minPoolCost = 170` < $\hat f'$ for every tier from Sub-reliable up, **operator take is invariant**: 170 × 73 = **12 410 ₳/yr**. Sub-threshold tiers (Dormant, Sub-block) absorb the entire — unchanged — pool reward.

| Canonical tier | Rep. σ | $k = 500$ | $k = 750$ | $k = 1000$ |
|---|---:|---:|---:|---:|
| Dormant | 50 K ₳ | 1 139 | 1 139 | 1 139 |
| Sub-block | 500 K ₳ | 11 373 | 11 373 | 11 373 |
| Sub-reliable | 2 M ₳ | 12 410 | 12 410 | 12 410 |
| Healthy | 15 M ₳ | 12 410 | 12 410 | 12 410 |
| Large healthy | 50 M ₳ | 12 410 | 12 410 | 12 410 |
| Near-saturation | 67 M ₳ | 12 410 | 12 410 | 12 410 |
| Saturated | 77 M ₳ | 12 410 | 12 410 | 12 410 |
| Oversaturated | 85 M ₳ | 12 410 | 12 410 | 12 410 |

**Operator revenue is fully invariant under a standalone `k`-raise** across every productive tier. The cap-at-`minPoolCost` structure eats the top-tail compression entirely. This is the isolation property of `k` in the current fee regime.

#### 2.3.3. Delegator net ROS across nine tiers (%/yr)

Delegator net ROS = $(\hat f' - c)/\sigma \times 73$ under hollow / full-delegation assumption. Sub-threshold tiers pay 100 % to fee (ROS = 0). Above break-even, ROS shrinks one-for-one with the cap compression.

| Canonical tier | Rep. σ | $k = 500$ | $k = 750$ | $k = 1000$ |
|---|---:|---:|---:|---:|
| Dormant | 50 K ₳ | 0 % | 0 % | 0 % |
| Sub-block | 500 K ₳ | 0 % | 0 % | 0 % |
| Sub-reliable | 2 M ₳ | 1.65 % | 1.65 % | 1.65 % |
| Healthy | 15 M ₳ | 2.19 % | 2.19 % | 2.19 % |
| Large healthy | 50 M ₳ | 2.25 % | 2.25 % | **1.72 %** |
| Near-saturation | 67 M ₳ | 2.26 % | **1.66 %** | **1.24 %** |
| Saturated | 77 M ₳ | 2.26 % | **1.49 %** | **1.12 %** |
| Oversaturated | 85 M ₳ | 2.05 % | **1.35 %** | **1.01 %** |

**Reading.** The k-raise is a **delegator-side regression at the top** and a **non-event at the bottom**. A delegator at a Saturated pool sees ROS halve (2.26 % → 1.12 %) across $k: 500 \to 1000$; a delegator at a Sub-reliable or Healthy pool sees no change at all. The instrument does not redirect ROS — it extinguishes it above the new $z_0$.

#### 2.3.4. Pledge-amplification channel (self-pledged pools, bonus from $\lambda_{\text{pledge}} A(\nu, \pi)$)

For pools with meaningful self-pledge, the envelope's second term contributes an additional reward on top of the hollow base. Under full self-pledge ($\pi = 1$), $A(\nu, 1) = \nu^3$. Since $\nu$ doubles when $k$ doubles (for fixed $\sigma_{\text{abs}}$) and $P_{\max}$ halves, the absolute bonus scales **linearly in `k`**.

For a fully self-pledged pool at σ = 15 M ₳ (Healthy tier):

| $k$ | $\nu = \sigma / z_0$ | $A(\nu, 1) = \nu^3$ | Bonus = $\lambda_{\text{pledge}} \cdot A \cdot P_{\max}$ | Total $\hat f'$ (hollow + bonus) |
|---:|---:|---:|---:|---:|
| 500 | 0.195 | 0.00739 | **28.3 ₳/ep** | 4 675 + 28 = 4 703 |
| 750 | 0.292 | 0.0250 | **108 ₳/ep** | 4 675 + 108 = 4 783 |
| 1000 | 0.390 | 0.0592 | **218 ₳/ep** | 4 675 + 218 = 4 893 |

> **Finding k-lever.S1.F2 [D] — Pledge-bonus amplification for self-pledged pools.** A fully self-pledged 15 M pool's bonus grows from 28 ₳/ep at $k = 500$ to 218 ₳/ep at $k = 1000$ — **7.7× amplification in absolute terms**. Annualised: +20 660 ₳/yr operator revenue for a fully self-pledged 15 M pool. This is the *only* genuinely positive mechanical effect a standalone k-raise delivers.

#### 2.3.5. Per-entity revenue by n-MPO bracket (hollow, ₳/yr)

Mean pools/entity and mean pool stake from [operator-delegator §4.4](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#44-operator-profitability-versus-delegator-return) (retail hollow segment, epoch 623; 73 epochs/yr).

| n-MPO bracket | Entities | Pools/entity | Mean stake/pool | $k = 500$ | $k = 750$ | $k = 1000$ |
|---|---:|---:|---:|---:|---:|---:|
| Single-pool — Sub-reliable (< 3 M) | 155 | 1 | 1.81 M | 12 410 | 12 410 | 12 410 |
| Single-pool — Healthy (3–38.5 M) | 214 | 1 | 11.40 M | 12 410 | 12 410 | 12 410 |
| Single-pool — Large healthy (38.5–62 M) | 29 | 1 | 50.69 M | 12 410 | 12 410 | 12 410 |
| Single-pool — Near-saturation (62–77 M) | 16 | 1 | 69.38 M | 12 410 | 12 410 | 12 410 |
| 2-pool MPO | 17 | 2.00 | 38.24 M | 24 820 | 24 820 | 24 820 |
| 3–5 pool MPO | 24 | 3.92 | 29.47 M | 48 647 | 48 647 | 48 647 |
| 6–10 pool MPO | 9 | 7.44 | 35.37 M | 92 330 | 92 330 | 92 330 |
| 11+ pool MPO | 7 | 19.29 | 33.41 M | 239 389 | 239 389 | 239 389 |

**Every bracket is k-invariant** under the standalone-k-raise assumption. Operator revenue depends only on the number of pools in the fleet × the flat-fee cap per pool. The k-lever, as an instrument that moves only the scalar `k`, does not redistribute operator revenue between single-pool and MPO populations at all.

## 3. Limits of a standalone `k`-raise

Three structural limits — one per synthesis finding, each tied to the mechanical analysis of §2.

### 3.1. k-lever.S1 — Top-tail compression + narrow pledge amplification; bottom unchanged

**What the k-raise mechanically does** is the sum of three effects, already quantified in §2.3:

1. **[R] Top-tail compression.** Above the new $z_0$, the ceiling $P_{\max}$ shrinks with $k$. Every pool with $\sigma > z_0^{\text{new}}$ has its pool reward re-capped. At $k: 500 \to 1000$, Saturated and Oversaturated pools lose ≈ 50 %.
2. **[D] Pledge-bonus amplification.** For self-pledged pools below the new $z_0$, the bonus $\lambda_{\text{pledge}} A(\nu, \pi)$ scales linearly in `k` in absolute terms. The narrow band of pools that capture this is §3.2's subject.
3. **[B] Bottom invariance.** Hollow pools below saturation: no change. The "k-raise helps small pools" framing has no mechanical basis — the formula shows $\hat f' = R \lambda_{\text{size}} \sigma_{\text{abs}} / \text{CircSupply}$, with the `k` exactly cancelling.

**The arithmetic invariance at the bottom corrects a common misreading.** Earlier iterations of this evaluation, and several governance discussions, conclude that a k-raise "pushes the viability line up" or "makes sub-threshold pools worse". This is not what the formula does when only `k` changes. What pushes the viability line up is a change in the fee structure (e.g. `minPoolCost` increase) or the reward pot (e.g. reserve depletion lowering $R$) — not a change in `k`. The k-raise does reshape the upper tail (POL.O3.F6), but the diagnostic's §3.1 population sits in the lower tail — untouched.

### 3.2. k-lever.S2 — A fine tool for a narrow delegator segment, and insufficient on the operator side because the formula is unchanged

The CIP-0082 rationale states the redistribution hypothesis explicitly (stages 3–4):

> *"Increasing k may get stale delegations moving again by oversaturating large pools. This will cause many delegators to reconsider their delegation, potentially helping smaller community pools find delegations."*

Taken at face value, this is a **ROS-based redistribution claim**: delegators choose pools partly on yield; oversaturation cuts yield at the top; therefore delegators migrate toward smaller, better-yielding pools. The k-raise is in principle the right tool *if* the delegator population it targets exists at scale and *if* the non-pledge equilibrium on the operator side can be reversed without touching the formula. The diagnostic undermines both conditions.

> **Finding k-lever.S2.F1 [R] — The ROS-focused delegator segment is a minority of productive stake.** Decomposing the 21.57 B ₳ of productive stake from [operator-delegator §4.3.3](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md):
>
> | Segment | Stake | Share | Responsive to a ROS signal? |
> |---|---:|---:|---|
> | Custodial (funds not discretionary) | 4.55 B ₳ | 21.1 % | **No** — funds are custodied; reallocation is not a retail choice |
> | Retail, loyal tenure ≥ 2.7 yr (CEN.O4.F2) | ~0.42 × 17.02 B ≈ 7.15 B ₳ | ~33 % | **No** — 42 % of delegations have not moved in 2.7+ years |
> | Retail, volatile tenure < 25 d (CEN.O4.F2) | ~0.21 × 17.02 B ≈ 3.57 B ₳ | ~17 % | Potentially — but 50.5 % of switches land on yield-identical pools (CEN.O6.F1), and non-identical moves show **visibility**, not yield, asymmetry (CEN.O6.F3: moves to smaller pools accept higher take) |
> | Retail, middle tenure | ~0.37 × 17.02 B ≈ 6.30 B ₳ | ~29 % | Unclear |
>
> The ROS-responsive segment that the k-raise redistribution mechanism actually targets is **at most the subset of the retail-volatile tier whose switches are not yield-identical** — under the 50.5 %-yield-identical figure of CEN.O6.F1, that is ≈ 0.50 × 17 % ≈ **8 % of productive stake at best**, with a further discount for the visibility asymmetry. CIP-0082's k-raise can in principle move stake among that segment — but a single-digit-percent redistribution channel is not a network-level concentration reform.

> **Finding k-lever.S2.F2 [R] — Changing `k` without revising the reward formula leaves the non-pledge equilibrium intact, so the operator side is insufficient on its own.** Operators do not pledge today for a well-understood reason: POL.O2.F2 shows pledge yield is structurally dominated by passive-delegation yield (0.68 %/yr vs ~2.3 %/yr). POL.O2.F1: 78 % of staked ADA sits in pools with pledge ratio < 1 %. POL.O5.F3: 42 of 48 saturation-scale MPOs forfeit the bonus (~40.2 M ₳/yr) rather than lock capital. A k-raise amplifies the pledge-bonus term $\lambda_{\text{pledge}} A(\nu, \pi)$ by roughly linear-in-`k` for fully self-pledged pools below the new $z_0$, but keeps $A(\nu, 0) = 0$ — hollow and near-hollow pools (the overwhelming majority of productive stake) are untouched — and, more importantly, leaves the surrounding formula that makes pledge a dominated strategy *unchanged*. Changing `k` without changing the formula that produces the dominance relationship does not flip the opportunity-cost calculus. The non-pledge equilibrium persists; the amplified bonus is a larger prize for a behaviour operators still have no reason to adopt. **The proposal is insufficient on the operator side.** The instruments that would genuinely change the equilibrium (CIP-0050's $\sigma'$ clipping, CIP-0037's new saturation curve) change the formula itself — and sit out of scope for a standalone k-raise.

**Composite reading.** The CIP-0082 k-raise is not a wrong instrument in the abstract — it is a *narrow* instrument meeting a *narrow* audience on the demand side, and an *insufficient* instrument on the supply side because it leaves the formula that explains the non-pledge equilibrium unchanged. On the demand side it reaches only the ROS-responsive fraction of the retail-volatile segment — single-digit-percent of productive stake. On the supply side it amplifies a reward that is dominated by passive delegation yield *under the same formula that made pledge dominated in the first place*. The redistribution the CIP advertises would require either (a) a much larger ROS-responsive delegator market than the census documents, or (b) a reward-formula change that flips the pledge-vs-delegation opportunity cost. A standalone k-raise delivers neither.

### 3.3. k-lever.S3 — MPO fleet absorption under weak pledge

The behavioural alternative to the amplified-pledge-signal channel is **MPO fleet absorption**: existing multi-pool operators register additional pools to capture the new slots, regardless of pledge signal. Two anchors establish this pattern — one empirical (Cardano's only previous k-raise), one structural (the economics of fleet expansion on current mainnet).

> **Finding k-lever.S3.F1 [R] — Historical `k: 150 → 500` (Aug 2020) produced today's MPO landscape.** The only previous k-raise in Cardano's live protocol history. Within two years of the raise, the MPO fleet pattern POL.O5.F1 documents today had stabilised: **83 attributed entities controlling 75.5 %** of productive stake across **475 productive pools**. The raise did not produce a proportional increase in independent entities; it produced multi-pool expansion by existing operators. This is not a predictive model — it is the actual observed outcome of the one natural experiment Cardano has run on `k` at scale.

> **Finding k-lever.S3.F2 [R] — Structural economics favour fleet expansion over new-entrant entry.** Three quantitative anchors from the diagnostic, all directly observable on mainnet (no modelling required): **(i)** Pool registration cost is ~500 ADA per pool. Median retail MPO entity revenue (operator-delegator §4.3.3): **25 K – 1 M ₳/yr** depending on fleet size — an existing MPO can register a new pool at sub-0.05 % of annual revenue. **(ii)** Operational infrastructure scales near-horizontally: an operator already running $N$ pools has the relay topology, monitoring, keyset tooling, and ops capacity to run $N+1$ pools at near-zero marginal cost. **(iii)** Pledge is not binding on fleet expansion under the current formula — per S2.F2, 42 of 48 saturation-scale MPOs already operate without meeting pledge targets; adding new pools does not trigger any pledge-based penalty that forecloses the expansion. For a new-entrant operator to out-compete an existing MPO for a new slot, they would need to match the MPO's brand / wallet / marketing channel (S2.F3) — a channel the k-raise does not amplify. The economic gradient favours expansion, not entry.

**Precondition.** The regression is conditional on weak pledge. Once a stake-cap layer binds (CIP-0050's `L` or CIP-0037's dynamic saturation), MPO fleet expansion is structurally foreclosed — the k-raise then becomes a decentralisation lever (by forcing new entrants to capture the new slots). This is the CIP-0050 "synergy" argument. It is also the reason the correct sequence is: fee-layer → stake-cap → k-recalibration (step 3). **A standalone k-raise before step 2 is operating in the regressive regime.**

### 3.4. References

- **Missing-CPS anchors:** V2 [§3.1 operator viability](../../README.md#31-guarantee-operator-viability-across-the-entire-productive-population), [§3.4 concentration](../../README.md#34-reduce-the-concentration-effects-that-distort-both-populations).
- **Formulas inherited:** [pools-distribution §2.3 simplified reward function](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#23-reward-function) ($\hat f'$, $P_{\max}$, $E$, $A$); [operator-delegator §1.1.1 split formula](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md) ($r_{\text{op}}$, $r_{\text{mem}}$).
- **Numerical baselines:** §2.2 ($z_0$, $P_{\max}$ per k-value); §2.3 (nine-tier and n-MPO quantifications). Nine-tier taxonomy: [pools-distribution §4.1.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions). n-MPO brackets: [operator-delegator §4.4](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#44-operator-profitability-versus-delegator-return).
- **Diagnostic findings:** OPE.O7.F1, OPE.O7.F2 (operator-delegator); POL.O2.F1, POL.O2.F2, POL.O3.F5, POL.O3.F6, POL.O5.F1, POL.O5.F2, POL.O5.F3, POL.O6.F2 (pools-distribution).
- **Companion evaluation:** [`cip-0082.md`](cip-0082.md) §3.3 — same structural critique applied to CIP-0082 stages 3–4 (where the k-raise is sequenced after the Margin swap). The standalone analysis here is the baseline; cip-0082.md §3.3 adds the flat-yield interaction (the Margin swap removes the ROS signal the k-raise depends on).
- **Stake-cap pairing candidates (precondition for a constructive k-raise):** [`../pools-distribution/cip-0050.md`](../pools-distribution/cip-0050.md), [`../pools-distribution/cip-0037.md`](../pools-distribution/cip-0037.md). Note: those CIPs *change the reward formula* (CIP-0050 via σ′ clipping, CIP-0037 via a new saturation curve); once either is active, the analysis in this doc no longer directly applies.
- **Canonical source:** [Pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards) (Cardano docs).

> **Status:** Active 2026/04/23. Companion to CIP-0082 stages 3–4.
