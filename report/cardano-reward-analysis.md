# Cardano Reward Formulas: From Design Intent to Mainnet Reality

## Motivation

The *Shelley-era Delegation and Incentives Design Specification* (SL-D1) defined the economic rules that were meant to guide Cardano toward a stable, decentralized equilibrium of $k$ well-funded stake pools.
Five years of mainnet operation have exposed significant divergences between those design intentions and the on-chain reality.
The *Analysis of Cardano's Incentive Mechanism* (Lopez de Lara, 2025/11) documented the key findings empirically: a stratified equilibrium with 873 active operators below the 3M ADA viability threshold, a pledge mechanism that is functionally irrelevant for most pools, and a capital-constrained environment where ~16B ADA remains outside consensus.

This document is the formula-level companion to that analysis.
It restates the SL-D1 reward pipeline in reader-friendly, domain-oriented notation, then isolates *where* and *how* each stage of the pipeline contributes to the observed problems.
The same notation is then used to express the four community CIP proposals (CIP-0023, CIP-0050, CIP-0082, CIP-0037) as targeted substitutions within that pipeline, making it possible to compare each proposal against the status quo on a formula-by-formula basis.

The goal is not to re-derive the math, but to provide a self-contained reference that connects *protocol intent*, *observed failure modes*, and *proposed remedies* in a single, auditable document.

## Canonical sources

- **SL-D1**: *Engineering Design Specification for Delegation and Incentives in Cardano-Shelley* (Kant et al.).
- **Empirical baseline**: *Analysis of Cardano's Incentive Mechanism* (Lopez de Lara, 2025/11).
- **CIP proposals**: CIP-0023, CIP-0037, CIP-0050, CIP-0082.


## Table of Contents

- [1. Reward Flow](#1-reward-flow)
  - [1.1 Treasury & Pool Pots Distribution](#11-treasury--pool-pots-distribution)
    - [1.1.1 Flow Overview](#111-flow-overview)
    - [1.1.2 Formulas](#112-formulas)
      - [1.1.2.1 SL-D1 (Original)](#1121-sl-d1-original)
      - [1.1.2.2 Reader-Friendly](#1122-reader-friendly)
      - [1.1.2.3 Mainnet Reader-Friendly](#1123-mainnet-reader-friendly)
      - [1.1.2.4 Concept glossary](#1124-concept-glossary)
    - [1.1.3 Mainnet Observations](#113-mainnet-observations)
    - [1.1.4 Problems](#114-problems)
    - [1.1.5 Prior Art & Cited Solutions](#115-prior-art--cited-solutions)
  - [1.2 Pools Distribution](#12-pools-distribution)
    - [1.2.1 Flow Overview](#121-flow-overview)
    - [1.2.2 Formulas](#122-formulas)
      - [1.2.2.1 SL-D1 (Original)](#1221-sl-d1-original)
      - [1.2.2.2 Interpretation of the original reward function](#1222-interpretation-of-the-original-reward-function)
      - [1.2.2.3 Why rewrite the original formulation](#1223-why-rewrite-the-original-formulation)
      - [1.2.2.4 Normalized saturation coordinates](#1224-normalized-saturation-coordinates)
      - [1.2.2.5 Reader-friendly reward function](#1225-reader-friendly-reward-function)
      - [1.2.2.6 Summary in normalized notation](#1226-summary-in-normalized-notation)
      - [1.2.2.7 Mainnet parameterization (normalized form)](#1227-mainnet-parameterization-normalized-form)
      - [1.2.2.8 Concept glossary](#1228-concept-glossary)
    - [1.2.3 Mainnet Observations](#123-mainnet-observations)
    - [1.2.4 Problems](#124-problems)
    - [1.2.5 Prior Art & Cited Solutions](#125-prior-art--cited-solutions)
    - [1.2.6 CIP Evaluation: Pledge & Curve Adjustments](#126-cip-evaluation-pledge--curve-adjustments)
      - [1.2.6.1 CIP-0050 — Pledge Leverage Cap](#1261-cip-0050--pledge-leverage-cap)
      - [1.2.6.2 CIP-0037 — Dynamic Pledge-Linked Saturation](#1262-cip-0037--dynamic-pledge-linked-saturation)
  - [1.3 Operator / Delegator Distribution](#13-operator--delegator-distribution)
    - [1.3.1 Flow Overview](#131-flow-overview)
    - [1.3.2 Formulas](#132-formulas)
      - [1.3.2.1 SL-D1 (Original)](#1321-sl-d1-original)
      - [1.3.2.2 Residual split decomposition](#1322-residual-split-decomposition)
      - [1.3.2.3 Reader-Friendly](#1323-reader-friendly)
    - [1.3.3 Structural Decomposition](#133-structural-decomposition)
    - [1.3.4 Mainnet Observations](#134-mainnet-observations)
    - [1.3.5 Problems](#135-problems)
    - [1.3.6 Prior Art & Cited Solutions](#136-prior-art--cited-solutions)
    - [1.3.7 CIP Evaluation: Fee Structure Adjustments](#137-cip-evaluation-fee-structure-adjustments)
      - [1.3.7.1 CIP-0023 — Fair Min Fees](#1371-cip-0023--fair-min-fees)
      - [1.3.7.2 CIP-0082 — Improved Rewards Scheme](#1372-cip-0082--improved-rewards-scheme)
- [Appendices](#appendices)
  - [A. Notation Convention](#a-notation-convention)
  - [B. Symbol Mapping (SL-D1 → Reader-Friendly)](#b-symbol-mapping-sl-d1--reader-friendly)
  - [C. Detailed Variable Glossary](#c-detailed-variable-glossary)
- [Sandbox](#sandbox) *(draft material)*

## 1. Reward Flow

### 1.1 Treasury & Pool Pots Distribution

#### 1.1.1 Flow Overview

![Treasury & Pool Pots Distribution — Flow Diagram](image.png)

Before any individual pool receives rewards, the protocol must first answer one question:
**how much ADA is available for distribution this epoch?**

This stage assembles the **epoch pot** from three on-chain sources — transaction fees, non-refundable deposits, and a monetary expansion draw from the reserve — then splits it in two: a fixed share goes to the **treasury**, and the remainder becomes the **pools pot**, the total budget that the next stage (§1.2) will distribute across individual pools.

Two design choices embedded at this stage matter for the rest of the analysis:

- **Cooperative-behavior gate.** The monetary expansion draw is scaled by the ratio of blocks actually produced to blocks expected. If pools collectively miss slots, the entire epoch pot shrinks. This discourages sabotage but also means the pot depends on aggregate network health.

- **Fixed split rule.** The treasury/pools ratio is a protocol constant ($\tau$), not a function of network activity or reserve level. It does not adapt as the balance between fees and expansion shifts over time.

#### 1.1.2 Formulas

The formulas are presented in three layers: the original SL-D1 notation, a reader-friendly rewrite, and the mainnet-parameterized form.

##### 1.1.2.1 SL-D1 (Original)

The design spec defines three quantities. First, the **gross epoch pot** — the total ADA entering the reward pipeline this epoch:

$$
Pot^{\text{epoch}}
:=
F + D + \min(\eta,1)\rho\,(T_{\infty}-T)
$$

Then, the **treasury/pools split** — a single parameter $\tau$ determines how much goes to the treasury vs. pools:

$$
R
:=
(1-\tau)\,Pot^{\text{epoch}}
$$

$$
TreasuryPot^{\text{epoch}}
:=
\tau\,Pot^{\text{epoch}}
$$

> **Reading note.** $F$ = fees, $D$ = deposits, $\eta$ = block-production ratio, $\rho$ = monetary expansion rate, $(T_{\infty}-T)$ = remaining reserve. The mapping to reader-friendly names is in the glossary below (§1.1.2.4).

##### 1.1.2.2 Reader-Friendly

Same logic, with self-documenting names. The epoch pot aggregates **three inputs** — fees, deposits, and a reserve draw gated by the block-production ratio:

$$
Pot^{\text{epoch}}
=
Fee^{\text{epoch}}_{\text{tx}}
+
Deposit^{\text{epoch}}_{\text{nonRefundable}}
+
\min\left(\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}},1\right)\rho^{\text{monetaryExpansion}}_{\text{rate}}(Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}})
$$

The split is then purely multiplicative — no pool-level logic involved:

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

##### 1.1.2.3 Mainnet Reader-Friendly

Substituting the current mainnet protocol parameters ($\rho = 0.3\%$, $\tau = 20\%$, 21,600 expected blocks per epoch, 45 billion max supply):

$$
Pot^{\text{epoch}}
=
Fee^{\text{epoch}}_{\text{tx}}
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

Conservation — the split is exhaustive, nothing is lost:

$$
PoolsPot^{\text{epoch}} + TreasuryPot^{\text{epoch}}
=
Pot^{\text{epoch}}
$$

##### 1.1.2.4 Concept glossary

| SL-D1 | Reader-Friendly | Meaning | Mainnet baseline |
| --- | --- | --- | --- |
| $F$ | $Fee^{\text{epoch}}_{\text{tx}}$ | Epoch transaction fees | Dynamic |
| $D$ | $Deposit^{\text{epoch}}_{\text{nonRefundable}}$ | Epoch non-refundable deposits | Dynamic |
| $\eta$ | $\frac{Blocks^{\text{epoch}}_{\text{produced}}}{Blocks^{\text{epoch}}_{\text{expected}}}$ | Epoch block-production ratio | $Blocks^{\text{epoch}}_{\text{expected}}=21{,}600$ |
| $\rho$ | $\rho^{\text{monetaryExpansion}}_{\text{rate}}$ | Monetary expansion rate | $0.3\%$ |
| $T_{\infty}-T$ | $Supply^{\text{system}}_{\text{total}}-Supply^{\text{system}}_{\text{circulating}}$ | Reserve entering the monetary-expansion term | $45\,\text{billion} - Supply^{\text{system}}_{\text{circulating}}$ |
| $\tau$ | $\tau^{\text{treasury}}_{\text{rate}}$ | Treasury take rate | $20\%$ treasury / $80\%$ pools |
| $R$ | $PoolsPot^{\text{epoch}}$ | Pool-side share of the epoch pot | $80\% \cdot Pot^{\text{epoch}}$ |
| n/a | $TreasuryPot^{\text{epoch}}$ | Treasury-side share of the epoch pot | $20\% \cdot Pot^{\text{epoch}}$ |

#### 1.1.3 Mainnet Observations

The epoch-level analysis (epochs 208–617) yields four observations at this pipeline stage. The full data, visuals, and methodology are in the dedicated sub-report: [`report/mainnet/treasury-and-pool-pots-distribution/`](mainnet/%20treasury-and-pool-pots-distribution/README.md).

| # | Observation | Section | Status |
| --- | --- | --- | --- |
| | **O1 — The epoch pot is a single-source budget** | | |
| F1.1 | Monetary expansion dominates the epoch pot (~99.8%) | §3.1 | Structural — unchanged since Shelley |
| F1.2 | Fee revenue is structurally insufficient — even at full capacity, fees cover ~1.3% of expansion | §3.3, §4.2 | 12–16× capacity gap; no CIP in scope |
| F1.3 | Deposit contribution is small and unmeasurable at epoch granularity | §3.4 | Data limitation |
| F1.4 | SPOs produce ~97% of their assigned blocks — the pot assembles reliably | §3.5 | Avg η = 0.977 |
| | **O2 — The reserve has crossed its half-life** | | |
| F2.1 | Reserve is half-depleted (−50.95%) in 5.5 years | §3.2 | Ongoing decline |
| F2.2 | Significant reward pressure expected at epochs 1000–1200 | §4.1 | Projected ~2028–2029 |
| | **O3 — The reward mechanism operates at ~44% of its potential** | | |
| F3.1 | Only ~44% of the pools pot is distributed to operators and delegators — the rest returns to the reserve | §3.7 | 6.8M distributed out of 15.5M |
| F3.2 | 4.55B ADA cumulative (~70% of current reserve) exists because of undistributed rewards | §3.7 | Slows depletion but is not by design |
| F3.3 | The primary driver is inactive stake — ~17B ADA (~44%) does not participate in delegation | §3.7 | Staking mechanism half-utilised |
| | **O4 — Reward parameters have never been adjusted** | | |
| F4.1 | Treasury split and expansion rate never adjusted since Shelley | §3.8 | τ = 20%, ρ = 0.3% — constant |

##### The big picture

Five and a half years after Shelley, the epoch-budget stage tells a clear story: **the system works, but it runs on a finite fuel supply that is now half-spent.**

##### O1 — The epoch pot is a single-source budget

The protocol assembles the epoch reward pot from three sources: monetary expansion, transaction fees, and deposit flows. In practice only one matters.

**Monetary expansion: ~99.8% of the pot** (F1.1). Every epoch, 0.3% of the reserve is drawn. This has dominated the pot in every single epoch since Shelley — fees have never crossed 3%, even during peak NFT/DeFi activity.

**Transaction fees: ~0.19% of the pot** (F1.2). At current levels, fees are negligible. Even at full realistic network capacity (3.1 TPS, ~1.34M tx/epoch), fee revenue would reach only ~254K ADA/epoch — barely 1.3% of the reserve expansion term. Reaching fee self-sufficiency would require **12–16× today's realistic maximum throughput**: both a capacity upgrade (Leios) and a fundamental shift in transaction demand.

**Deposits: unmeasurable at epoch granularity** (F1.3). The non-refundable deposit flow is not directly available in the Koios dataset. Cross-validation shows a median gap of only ~49K ADA against treasury stock deltas — a rounding error.

**Block production: the pot assembles reliably** (F1.4). SPOs produce ~97% of their assigned blocks on average (η = 0.977). The pot assembly mechanism works as intended — block production is not a bottleneck.

##### O2 — The reserve has crossed its half-life

The reserve has gone from **13.29B to 6.53B ADA** — half depleted in ~5.5 years (F2.1). The decline is exponential: each epoch draws 0.3% of whatever remains, so the absolute draw shrinks over time. The nominal expansion has already halved, from ~39.9M to ~19.5M ADA/epoch.

**Projected timeline** (F2.2). At current parameters and participation levels, the reserve reaches ~2B ADA around epochs 1000–1200 (~2028–2029) — at which point per-epoch rewards drop significantly. Full depletion is projected around epoch 3500 (~2040s).

##### O3 — The reward mechanism operates at ~44% of its potential

Every epoch, the protocol allocates ~15.5M ADA to the pools pot. Only **~6.8M ADA (~44%) is actually distributed as rewards** to operators and delegators — the remaining ~8.7M returns to the reserve (F3.1).

This is not a small leak. Over 400+ epochs, **4.55B ADA** has flowed back to the reserve through this mechanism — roughly **70% of the current reserve stock** exists because rewards were not fully distributed (F3.2). It is the single biggest reason the reserve has lasted as long as it has.

The root cause is straightforward: **the staking mechanism is half-utilised** (F3.3). Out of ~38.5B ADA in circulation, only ~21.6B (~56%) participates in delegation. The remaining ~17B ADA sits outside the system entirely — it earns no rewards, but it still dilutes the distribution. If that inactive stake were to enter consensus — through governance incentives, exchange staking changes, or new delegation products — this buffer would shrink and reserve depletion would accelerate.

This creates a paradox: the return-to-reserve mechanism slows depletion, but it is a side effect of low participation, not a design feature. Greater adoption — normally desirable — would remove this safety margin.

##### O4 — Reward parameters have never been adjusted

The two parameters that shape this entire pipeline — the monetary expansion rate ($\rho = 0.3\%$) and the treasury rate ($\tau = 20\%$) — have **never been adjusted** since Shelley inception (F4.1). The decentralisation parameter $d$ was gradually reduced to 0 and $k$ was raised from 150 to 500, but the reward-level parameters remain at their day-one values. Neither has been the subject of a formal governance proposal.

> **Scope note.** Observations O1–O4 are structural to the epoch-budget layer and fall **outside the scope of the four CIPs** under evaluation (CIP-0023, CIP-0037, CIP-0050, CIP-0082). They document the sustainability context within which all CIP proposals operate, and distinguish them from the problems the CIPs actually target — at the pool-distribution and operator/delegator layers downstream.

#### 1.1.4 Problems

The observations above point to two structural problems at this pipeline stage. Neither is addressed by the four CIPs under evaluation — they operate downstream (§1.2, §1.3).

**P1.1 — Reserve dependency with no transition path.**
The epoch pot is funded almost entirely by a depleting resource (O1). The reserve has crossed its half-life (O2) and the parameters governing the draw have never been reviewed (O4). There is currently no mechanism — protocol-level or governance-level — to manage the transition from reserve-funded to fee-funded rewards. The system is on a known countdown with no scheduled response.

**P1.2 — Fee revenue is orders of magnitude below self-sufficiency.**
Even at full realistic network capacity, fees would cover ~1.3% of the reserve expansion term (O1). Closing this gap requires 12–16× today's realistic maximum throughput — implying both a capacity upgrade (Leios) and a structural increase in transaction demand and fee levels. No single lever is sufficient.

> **Note.** The ~44% distribution efficiency (O3) is not a problem *at this stage* — it is a consequence of participation levels, which are shaped by incentives defined at the pool-distribution (§1.2) and operator/delegator (§1.3) layers. It is documented here because it materially affects reserve depletion timing.

#### 1.1.5 Prior Art & Cited Solutions

These solutions have been discussed in the literature or community but fall **outside the scope** of this stream (issue #12). They are listed here for completeness.

- **Tiered fee models** (Kiayias et al., 2023) — congestion-based pricing to increase fee revenue per transaction.
- **Leios throughput upgrade** — necessary precondition for fee growth, but "provides the highway, not the traffic" (Lopez de Lara, 2025/11, §5).
- **Dynamic $\rho$ governance** — periodic review of the monetary expansion rate to balance reserve longevity against reward levels.
- **Adaptive $\tau$ governance** — adjusting the treasury/pools split in response to ecosystem needs rather than keeping it fixed.
- **Staking participation incentives** — mechanisms to bring inactive ADA into delegation, which would increase distribution efficiency but accelerate reserve depletion (the O3 paradox).

### 1.2 Pools Distribution

#### 1.2.1 Flow Overview

This stage takes the **pools pot** ($PoolsPot^{\text{epoch}}$) produced by §1.1 and distributes it across individual pools. The output is a per-pool allocation ($PoolPot^{\text{actual}}_i$) that feeds into §1.3 (operator/delegator split).

For each pool $i$, the protocol performs three steps:

1. **Saturation clipping.** Both total stake ($\sigma_i$) and pledge ($s_i$) are capped at the saturation threshold $z_0 = 1/k$. This prevents any single pool from capturing a disproportionate share.

2. **Reward curve evaluation.** A reward function $f$ computes the pool's *optimal* allocation from its clipped stake and pledge. The curve has two components: a **base stake term** (proportional to delegation) and a **pledge-bonus term** (nonlinear, governed by $a_0$). The pledge bonus is meant to reward operator commitment ("skin in the game").

3. **Performance adjustment.** The optimal allocation is scaled by apparent performance $\bar{p}_i$ to produce the *actual* allocation. Pools that miss blocks receive less. If the registered pledge is not met, the allocation is zeroed entirely.

Any rewards not distributed (because $\sum_i \hat{f}_i < R$) return to the reserve — this is the mechanism behind O3 in §1.1.3.

Two design choices matter for the rest of the analysis:

- **Pledge sensitivity via $a_0$.** The parameter $a_0$ controls how much additional reward a pool can earn through pledge. At $a_0 = 0.3$, the pledge bonus represents at most ~23% of the optimal allocation. Whether this is sufficient to meaningfully incentivise pledge is a central question at this layer.

- **Uniform saturation threshold.** All pools share the same cap $z_0 = 1/k$. There is no mechanism to differentiate saturation based on pledge level or pool characteristics — CIP-0050 and CIP-0037 both propose to change this.

#### 1.2.2 Formulas

The formulas are presented in the same layered approach as §1.1: original SL-D1, then a reader-friendly rewrite using normalized saturation coordinates, then mainnet parameterization.

The original SL-D1 presentation mixes saturation clipping and reward evaluation in a single expression. The rewrite below separates these two concerns without changing the math — it makes the saturation regimes and pledge-bonus structure easier to read and analyze.

##### 1.2.2.1 SL-D1 (Original)

The original SL-D1 pool-distribution rules are:

$$
f(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma' + s'a_0\cdot\frac{\sigma' - s'\left(\frac{z_0-\sigma'}{z_0}\right)}{z_0}
\right)
$$

$$
\hat f(s,\sigma,\bar p) := \bar p \cdot f(s,\sigma)
$$

$$
\sum_i \hat f(s_i,\sigma_i,\bar p_i) \le R
$$

$$
R - \sum_i \hat f(s_i,\sigma_i,\bar p_i) \; \text{is not paid out and remains accounted in } (T_{\infty}-T)
$$

$$
\text{if pledge not met in epoch } \Rightarrow \hat f = 0
$$

##### 1.2.2.2 Interpretation of the original reward function

The SL-D1 pool-distribution rule is centered on the reward function \(f\), and the actual pool allocation is then obtained through \(\hat f\). The core reward function is evaluated on the clipped inputs
$s' := \min(s,z_0)$ and $\sigma' := \min(\sigma,z_0)$, not directly on the raw quantities $s$ and $\sigma$.
Thus:

- $s$ is the operator pledge before clipping
- $\sigma$ is the total stake delegated to the pool before clipping
- $s'$ is the pledge after clipping at the saturation threshold
- $\sigma'$ is the total stake after clipping at the saturation threshold

In this notation, the function has two components:

- a base term, $\sigma'$, which rewards stake up to saturation
- a pledge-bonus term, $s'a_0 \cdot \dfrac{\sigma' - s'\left(\frac{z_0-\sigma'}{z_0}\right)}{z_0}$

The factor $\left(\frac{z_0-\sigma'}{z_0}\right)$ measures the remaining headroom before saturation. As the pool approaches saturation, this headroom shrinks and the pledge-bonus term is progressively dampened. The outer factor $\dfrac{R}{1+a_0}$ keeps the overall reward mass bounded.

##### 1.2.2.3 Why rewrite the original formulation

The original SL-D1 formula is correct, but awkward to analyze directly.

First, it mixes two separate concerns in a single expression:

- the clipping step that enforces saturation, and
- the reward computation performed after clipping.

Second, the pledge-sensitive part is harder to read than it needs to be. The term
$\sigma' - s'\left(\frac{z_0-\sigma'}{z_0}\right)$
hides a quadratic dependence on pledge that only becomes obvious after expansion.

Third, the most natural coordinates for analysis are not the raw stake shares $s$ and $\sigma$, but their positions relative to the saturation threshold $z_0$.

##### 1.2.2.4 Normalized saturation coordinates

To make the structure explicit, we now move to the **non-saturated regime**, where clipping is inactive. In that regime,

$$
s' = s
\qquad\text{and}\qquad
\sigma' = \sigma
$$

so the SL-D1 formula can be rewritten without the clipping operators.

We then introduce two normalized coordinates, both measured **relative to the saturation threshold** $z_0$:
The purpose of this change of variables is to express the reward curve directly in saturation coordinates.

$$
\pi := \frac{s}{z_0}
\qquad\text{and}\qquad
\nu := \frac{\sigma}{z_0}
$$

###### 1.2.2.4.1 Domain and interpretation

Under the non‑saturated regime $0 < s \le \sigma \le z_0$, the normalized variables satisfy

$$
0 < \pi \le \nu \le 1
$$

This change of variables expresses both inputs relative to the pool saturation threshold $z_0$. In other words, instead of measuring pledge and total stake directly as fractions of the total stake supply, we measure their **distance to saturation**.

Substituting $s = \pi z_0$ and $\sigma = \nu z_0$ into the original SL‑D1 reward curve allows the function to be rewritten entirely in terms of the normalized variables $(\pi, \nu)$.

This reveals an important structural property of the reward curve: the allocation depends only on the **ratios of pledge and total stake relative to the saturation threshold**, not on their absolute values. Pools that share the same normalized coordinates $(\pi,\nu)$ therefore receive the same fraction of the saturated pool reward.

The saturation threshold $z_0$ thus acts purely as a **scaling parameter**, while the shape of the reward curve itself is governed by the pledge‑influence parameter $a_0$.

This normalization allows the reward function to be analyzed in the compact domain

$$
0 \le \pi \le \nu \le 1
$$

which simplifies both the mathematical analysis and the economic interpretation of the reward mechanism.

These variables have a simple interpretation:

- $\pi$ is the **pledge saturation level**: it tells us what fraction of the saturation threshold is covered by operator pledge
- $\nu$ is the **total-stake saturation level**: it tells us what fraction of the saturation threshold is covered by the pool’s total stake

So, in the non-saturated regime:

- $\pi = 1$ would mean the pledge alone already reaches the saturation threshold
- $\nu = 1$ would mean the total pool stake reaches the saturation threshold
- $0 < \pi \le \nu < 1$ expresses the economically valid non-saturated domain

Equivalently, the original stake variables can be recovered as:

$$
s = \pi z_0
\qquad\text{and}\qquad
\sigma = \nu z_0
$$

###### 1.2.2.4.2 Rewriting the reward curve in saturation coordinates
Substituting these identities into the non-saturated SL-D1 formula gives:

$$
f(\pi z_0,\nu z_0)
=
z_0R
\left(
\frac{1}{1+a_0}\nu
+ 
\frac{a_0}{1+a_0}\left(\pi\nu-\pi^2(1-\nu)\right)
\right)
$$

This expression makes the structure of the reward curve much clearer.

- The factor $z_0R$ is the **maximum reward scale of a fully saturated pool**
- The term $\frac{1}{1+a_0}\nu$ is the **base stake component**
- The term $\frac{a_0}{1+a_0}\left(\pi\nu-\pi^2(1-\nu)\right)$ is the **pledge-sensitive component**

The nonlinear pledge-sensitive part is therefore isolated as

$$
A(\pi,\nu) := \pi\nu - \pi^2(1-\nu)
$$

which we call the **pledge-bonus activation function**.

This naming is useful because $A(\pi,\nu)$ is the only nonlinear part of the normalized reward curve. Once extracted, it can be analyzed separately from the outer scaling factors.

##### 1.2.2.5 Reader-friendly reward function

Define the following three derived quantities:

$$
P_{\max} := z_0R
$$

$$
\lambda_{\min} := \frac{1}{1+a_0}
$$

$$
\lambda_{\max} := \frac{a_0}{1+a_0}
$$

They each have a direct interpretation:

- $P_{\max}$ is the **reward ceiling** — the maximum any single pool can earn per epoch. It is the reward of a fully saturated ($\nu = 1$), fully pledged ($\pi = 1$), perfectly performing ($\bar{p} = 1$) pool. No pool can exceed it. In the ideal design, $k$ pools each earn $P_{\max}$ and the entire pot $R$ is distributed.

- $\lambda_{\min}$ is the **size fraction** — the share of $P_{\max}$ a pool can capture through stake alone, without any pledge. This defines the **size ceiling**: a pool at full saturation with zero pledge earns $\lambda_{\min} \times P_{\max}$.

- $\lambda_{\max}$ is the **pledge fraction** — the remaining share of $P_{\max}$ that the pledge bonus can unlock. This is the **commitment premium**: the gap between the size ceiling and the absolute ceiling. Unlocking it in full requires the operator to pledge the entire saturation amount ($\pi = 1$, i.e. pledge $= z_0$).

These coefficients satisfy

$$
\lambda_{\min} + \lambda_{\max} = 1
$$

The reward function is then:

$$
f'(\pi,\nu)
=
P_{\max}
\left(
\lambda_{\min}\nu
+
\lambda_{\max}A(\pi,\nu)
\right)
$$

This reads as a product of two factors: the **ceiling** ($P_{\max}$) and the **proportioning envelope** $E(\pi,\nu) = \lambda_{\min}\nu + \lambda_{\max}A(\pi,\nu)$. The envelope determines what fraction of $P_{\max}$ the pool captures, and ranges from 0 to 1:

| Tier | Envelope value | What it requires | Interpretation |
| --- | --- | --- | --- |
| Absolute ceiling | $E = 1$ | $\nu = 1, \pi = 1$ | Full saturation + full pledge → pool earns $P_{\max}$ |
| Size ceiling | $E = \lambda_{\min}$ | $\nu = 1, \pi = 0$ | Full saturation, zero pledge → pool earns $\lambda_{\min} \times P_{\max}$ |
| Typical pool | $E \ll 1$ | $\nu \ll 1$ | Undersaturated → reward scales linearly with $\nu$ |

Two structural properties of the envelope are worth noting:

- The **base term** $\lambda_{\min}\nu$ is **linear in $\nu$** — it depends only on total pool size relative to saturation. The distribution of stake across pools does not affect the aggregate base: $\sum_i \lambda_{\min}\nu_i = \lambda_{\min} \cdot \text{total\_stake}/z_0$ regardless of how many pools share that stake.

- The **bonus term** $\lambda_{\max}A(\pi,\nu)$ is **non-linear** — it depends on both $\pi$ and $\nu$, and at maximum pledge ($\pi = \nu$) reduces to $\lambda_{\max}\nu^3$. The cubic dependence means the bonus is structurally suppressed at low saturation levels and favours fewer, larger pools.

The purpose of this normalized form is not to change the reward rule, but to expose its internal structure: a ceiling, a size-proportional base, and a commitment-sensitive bonus whose activation is governed by $A(\pi,\nu)$.

##### 1.2.2.6 Summary in normalized notation

Using the normalized variables introduced above, the non-saturated reward rule can be summarized as follows.


| Rule / function | Mathematical form | Reader-friendly interpretation |
| --- | --- | --- |
| Pledge-bonus activation | $A(\pi,\nu) := \pi\nu - \pi^2(1-\nu)$ | Isolates the nonlinear pledge-sensitive part of the reward curve. Inputs: $\pi$ = normalized pledge level, $\nu$ = normalized total-stake level. |
| Normalized optimal pool reward | $f'(\pi,\nu) = P_{\max}\left(\lambda_{\min}\nu + \lambda_{\max}A(\pi,\nu)\right)$ | Gives the pool's optimal pre-performance reward in normalized notation. Uses $P_{\max}$ as the saturated reward scale, $\lambda_{\min}$ as the base stake weight, and $\lambda_{\max}$ as the pledge-bonus weight. |
| Performance-adjusted pool allocation | $\hat f'(\pi,\nu,\bar p) := \bar p \cdot f'(\pi,\nu)$ | Applies apparent performance $\bar p$ to the normalized optimal reward. This is the actual pool allocation in normalized notation. |
| Epoch consistency condition | $\sum_i \hat f'(\pi_i,\nu_i,\bar p_i) \le R$ | The sum of all realized pool allocations cannot exceed the epoch pool-side budget $R$. |
| Undistributed remainder | $R - \sum_i \hat f'(\pi_i,\nu_i,\bar p_i)$ | Portion of the pool-side epoch budget that is not paid out because of performance adjustment and remains accounted in the reserve term $(T_{\infty}-T)$. |
| Pledge enforcement | $\text{if pledge not met in epoch } \Rightarrow \hat f' = 0$ | If the registered pledge is not met, the pool allocation is zeroed before any operator/member split. |


##### 1.2.2.7 Mainnet parameterization (normalized form)

On mainnet, the key protocol parameters are currently:

$$
\alpha^{\text{protocol}}_{\text{skinInTheGame}} = 30\% = 0.3
$$

$$
k^{\text{protocol}}_{\text{targetPools}} = 500
\qquad\Rightarrow\qquad
z_0 = k^{\text{protocol}}_{\text{saturation}} = \frac{1}{500} = 0.2\%
$$

From these we obtain the normalized reward weights:

$$
\lambda_{\min} = \frac{1}{1+0.3} \approx 76.923\%
$$

$$
\lambda_{\max} = \frac{0.3}{1+0.3} \approx 23.077\%
$$

The maximum reward scale of a fully saturated pool becomes:

$$
P_{\max} = z_0 \cdot R = 0.2\% \cdot PoolsPot^{\text{epoch}}
$$

The normalized optimal reward function therefore becomes:

$$
f'(\pi,\nu)
=
P_{max}
\left(
76.923\%\,\nu
+ 
23.077\%\,A(\pi,\nu)
\right)
$$

Applying apparent performance gives the actual pool allocation in normalized form:

$$
\hat f'(\pi,\nu,\bar p)
=
\bar p
\cdot
P_{max}
\left(
76.923\%\,\nu
+ 
23.077\%\,A(\pi,\nu)
\right)
$$

These formulas are mathematically identical to the normalized expressions above, but with the current Cardano mainnet parameters substituted explicitly.

###### The playing field at current parameters

The three reward tiers under mainnet conditions (epoch 616, $R \approx 15.53\text{M ADA}$):

| Tier | Formula | Reward/epoch | Capital required |
| --- | --- | --- | --- |
| **Absolute ceiling** ($P_{\max}$) | $\frac{R}{k}$ | ~31K ADA | 77M ADA stake + 77M ADA pledge |
| **Size ceiling** ($\lambda_{\min} P_{\max}$) | $\frac{R}{k} \cdot 76.923\%$ | ~23.9K ADA | 77M ADA stake. No pledge. |
| **Commitment premium** ($\lambda_{\max} P_{\max}$) | $\frac{R}{k} \cdot 23.077\%$ | ~7.2K ADA | The gap — requires 77M ADA personal pledge |

The size ceiling is accessible to **any** saturated pool regardless of pledge. The commitment premium reserves 23.1% of $P_{\max}$ for pledge activation — but unlocking it requires operator capital equal to the full saturation threshold. The implied yield on that capital commitment ($\lambda_{\max} \cdot P_{\max}$ annualized / $z_0$ in ADA) is substantially below the passive delegation yield, making the pledge bonus economically weak as an incentive.

The full formula including apparent performance reads as a cascade of multiplicative factors:

$$
\hat f'(\pi,\nu,\bar p) = \underbrace{\bar{p}}_{\text{performance}} \;\cdot\; \underbrace{P_{\max}}_{\text{ceiling}} \;\cdot\; \underbrace{E(\pi,\nu)}_{\text{proportioning envelope}}
$$

Each factor acts as a discount from $P_{\max}$. When all three equal their ideal value (1, $P_{\max}$, 1), the pool earns the full ceiling. Every departure reduces the payout, and the difference returns to the reserve. For the detailed mainnet decomposition of these factors, see the pools-distribution sub-report (§1.2.3).

##### 1.2.2.8 Concept glossary

| SL-D1 | Reader-Friendly / Normalized | Meaning | Mainnet baseline |
| --- | --- | --- | --- |
| $R$ | $PoolsPot^{\text{epoch}}$ | Pool-side reward budget entering the pool reward curve | Inherited from section `1.1` |
| $a_0$ | $\alpha^{\text{protocol}}_{\text{skinInTheGame}}$ | Strength of the pledge (“skin‑in‑the‑game”) effect in the reward curve | $30\%$ |
| $z_0$ | $k^{\text{protocol}}_{\text{saturation}}$ | Global saturation threshold per pool | $0.2\%$ |
| $\sigma$ | $\sigma^{\text{totalStaked}}_{i}$ | Total stake share of pool $i$ before clipping | Dynamic |
| $s$ | $\pi^{\text{pledged}}_{i}$ | Pledged stake share of pool $i$ before clipping | Dynamic |
| $\sigma'$ | $\sigma^{\text{totalStaked}}_{\text{capped},i}$ | Total stake share after applying the saturation cap | $\min(\sigma^{\text{totalStaked}}_{i},0.2\%)$ |
| $s'$ | $\pi^{\text{pledged}}_{\text{capped},i}$ | Pledge share after applying the saturation cap | $\min(\pi^{\text{pledged}}_{i},0.2\%)$ |
| $f$ | $PoolPot^{\text{optimal}}_{i}$ | Optimal pool allocation before performance adjustment | Dynamic |
| $\bar p$ | $\bar p^{\text{pool}}_{\text{apparent},i}$ | Apparent performance multiplier of pool $i$ | Typically near $1$ |
| $\hat f$ | $PoolPot^{\text{actual}}_{i}$ | Actual pool allocation after performance adjustment | Dynamic |
| n/a | $\pi$ | Normalized pledge coordinate ($\pi=s/z_0$) | Dimensionless, $0<\pi<1$ (non‑saturated regime) |
| n/a | $\nu$ | Normalized total-stake coordinate ($\nu=\sigma/z_0$) | Dimensionless, $0<\nu<1$ (non‑saturated regime) |
| n/a | $A(\pi,\nu)$ | Pledge‑bonus activation function. Only nonlinear part of the reward curve; ranges 0 → 1. At maximum pledge ($\pi=\nu$): $A = \nu^3$ (cubic suppression at low saturation) | $A(\pi,\nu)=\pi\nu-\pi^2(1-\nu)$ |
| n/a | $P_{\max}$ | **Reward ceiling** — maximum any single pool can earn per epoch. The reward of an ideal pool ($\nu=1, \pi=1, \bar{p}=1$). In the ideal design, $k$ pools each earn $P_{\max}$ and the full pot is distributed | $P_{\max}=z_0R$ |
| n/a | $\lambda_{\min}$ | **Size fraction** — share of $P_{\max}$ accessible through stake alone (zero pledge). Defines the size ceiling. Linear in $\nu$ → distribution-neutral | $\lambda_{\min}=\frac{1}{1+a_0}$ |
| n/a | $\lambda_{\max}$ | **Pledge fraction** — remaining share of $P_{\max}$ unlockable by pledge commitment. Gap between size ceiling and absolute ceiling. Non-linear in $(\pi,\nu)$ → distribution-sensitive | $\lambda_{\max}=\frac{a_0}{1+a_0}$ |
| n/a | $E(\pi,\nu)$ | **Proportioning envelope** — fraction of $P_{\max}$ the pool captures based on size and pledge. $E = \lambda_{\min}\nu + \lambda_{\max}A(\pi,\nu)$, ranges 0 → 1 | $E=1$ at $(\pi,\nu)=(1,1)$ |
| n/a | $f'(\pi,\nu)$ | Normalized optimal reward = ceiling × envelope | $P_{\max} \cdot E(\pi,\nu)$ |
| n/a | $\hat f'(\pi,\nu,\bar p)$ | Actual pool allocation = performance × ceiling × envelope | $\bar p \cdot P_{\max} \cdot E(\pi,\nu)$ |
| $\sum_i \hat f$ | $\sum_i PoolPot^{\text{actual}}_{i}$ | Total rewards distributed across pools | Dynamic |
| $R-\sum_i \hat f$ | $PoolsPot^{\text{epoch}}-\sum_i PoolPot^{\text{actual}}_{i}$ | Undistributed remainder remaining accounted in reserves | Dynamic |

#### 1.2.3 Mainnet Observations

> Full analysis with data, figures, and reproduction scripts: [`report/mainnet/pools-distribution/`](report/mainnet/pools-distribution/README.md)

| # | Observation | Section | Status |
| --- | --- | --- | --- |
| | **O1 — The pledge bonus is functionally irrelevant at realistic pledge levels** | | |
| F1.1 | At median pledge, the bonus adds ~0.006% to pool rewards — undetectable by delegators | §4.5.3 | Structural — a0 curve too flat |
| F1.2 | Only 37 out of 731 healthy pools (5%) receive a pledge bonus above 1% | §4.5.3 | Dominated by high-pledge institutional pools |
| F1.3 | 83% of pools with stake (2,266 out of 2,718) pledge below 100K ADA — well within the flat zone of the a0 curve | §4.5.3 | Pledge has no meaningful effect below ~1M ADA |
| F1.4 | Yield on pledge capital is 0.68%/yr at best (full saturation + full pledge) — below passive delegation yield of ~2.3%/yr | §4.4 | Economically irrational to pledge |
| F1.5 | 22.1% of the pools pot (~3.4M ADA/epoch) is reserved for the pledge bonus but returns to reserve unused | §4.6 | Structural cost of maintaining $a_0 = 0.3$ |
| | **O2 — The pool landscape is stratified far from the k = 500 design target** | | |
| F2.1 | 1,987 pools with stake (73%) sit below the 3M ADA viability line — they carry only 2.7% of active stake | §3.1 | Structural imbalance |
| F2.2 | 731 healthy pools carry 97.3% of active stake — concentration above the viability line | §3.1 | Viability threshold acts as a cliff |
| F2.3 | Only 7 pools are at or above the saturation point (z₀ = 76.99M ADA) — the mechanism designed for 500 saturated pools reaches barely 1.4% of its target | §3.2 | Saturation cap nearly inactive |
| | **O3 — Saturation is structurally underutilised** | | |
| F3.1 | Active stake (21.75B ADA) fills only 56.5% of the theoretical capacity (k × z₀ = 38.49B ADA) — at most 282 pools could theoretically saturate | §3.2 | Capital constraint |
| F3.2 | 104 pools are within the near-saturation zone (≥80% of z₀) — the equilibrium state produces a thin cluster, not a broad plateau | §3.2 | Far from the k = 500 vision |
| F3.3 | The top 100 pools capture 23.2% of recent rewards; the top 250 capture 46.9% | §3.4 | Reward distribution is moderately concentrated |
| | **O4 — The delegation market is capital-constrained** | | |
| F4.1 | 16.75B ADA (43.5% of supply) does not participate in delegation — this is the binding constraint on pool saturation | §3.2 | Mirrors O3 from stage 1 (return-to-reserve) |
| F4.2 | If all circulating ADA delegated, the system could support all 500 target pools at saturation — the pool structure is not the bottleneck, participation is | §3.2 | k = 500 is feasible only at full participation |
| F4.3 | The attributed MPO entities control ~29% of supply and ~51% of staked ADA — institutional concentration shapes the delegation landscape | §3.5 | Structural feature, not anomaly |

##### The big picture

The pool reward curve was designed to produce an equilibrium of **k = 500 well-funded, pledge-committed stake pools**. Five and a half years of mainnet operation show a fundamentally different landscape: **a stratified market where the pledge bonus is irrelevant, saturation barely binds, and participation is the binding constraint.**

##### O1 — The pledge bonus is functionally irrelevant at realistic pledge levels

The reward curve includes a pledge bonus controlled by `a0 = 0.3`. Its purpose is to incentivize operators to commit personal capital — the more pledge relative to pool size, the higher the reward. In practice, this incentive barely exists.

**The a0 curve is too flat to matter** (F1.1). At the median pledge level of healthy pools, the pledge bonus adds approximately **0.006%** to pool rewards. Even at 1M ADA pledge (~$400K at current prices), the bonus is only ~0.39% — invisible to any delegator comparing pool yields.

**The bonus only activates at extreme pledge levels** (F1.2). Only **37 out of 731 healthy pools** (5%) receive a pledge bonus above 1%. These are almost exclusively high-pledge institutional or foundation pools (Cardano Foundation, Adalite, Wave) with pledges above 50M ADA. For the remaining 95% of the healthy pool landscape, the a0 mechanism does not function as an incentive.

**The economics of pledging are structurally inverted** (F1.4). The playing field analysis (§1.2.2.7) shows that the pledge fraction ($\lambda_{\max}$) reserves 23.1% of $P_{\max}$ for commitment incentives — but unlocking the full bonus requires 77M ADA of personal capital for an incremental yield of 0.68%/yr. This is below the ~2.3%/yr passive delegation yield. At every pool size below full saturation, the bonus is even weaker: the activation function $A(\pi,\nu)$ reduces to $\nu^3$ at maximum pledge, so undersaturation cubically suppresses the incentive. The result: 22.1% of the pools pot (~3.4M ADA/epoch) is structurally unreachable and returns to the reserve (F1.5).

**Most pools pledge far below the activation zone** (F1.3). The pledge distribution is heavily right-skewed: 83% of pools with stake pledge below 100K ADA — well within the flat zone of the a0 curve where the bonus is effectively zero. The median pledge-to-stake ratio for healthy pools is **0.14%**. The pledge bonus was designed for a world where operators commit meaningful personal capital; the actual pool landscape is one where most operators commit a negligible fraction.

##### O2 — The pool landscape is stratified far from the k = 500 design target

The reward formulas define a uniform saturation point $z_0 = \text{Supply}/k$ (currently **76.99M ADA**). The design intent was a flat landscape of 500 comparably-sized pools. Mainnet shows a steeply stratified distribution instead.

**The viability threshold creates a cliff** (F2.1, F2.2). Of 2,718 pools with stake, **1,987 (73%)** sit below the 3M ADA viability line established in the prior report. Together they carry only **2.7% of active stake**. The remaining **731 healthy pools** carry **97.3%** — effectively the entire delegation market. The transition across the viability threshold is not gradual; it is a cliff in both block production frequency and economic sustainability.

**Saturation is barely reached** (F2.3). Only **7 pools** are at or above the saturation point — out of a design target of 500. The saturation cap, the core mechanism designed to prevent stake concentration, is nearly inactive. It affects less than **1.4%** of its intended scope.

##### O3 — Saturation is structurally underutilised

The saturation mechanism cannot reach its design equilibrium because the available capital is insufficient.

**The delegation market can support at most 282 saturated pools** (F3.1). Active stake (21.75B ADA) fills only **56.5%** of the theoretical capacity defined by k × z₀ (38.49B ADA). Even under perfect redistribution — every ADA optimally allocated — only 282 pools could reach saturation. The k = 500 target requires participation that does not exist.

**The near-saturation zone is thin** (F3.2). Only **104 pools** sit above 80% of z₀. Rather than the broad plateau of comparable pools that the design envisions, the landscape produces a thin cluster of near-saturated pools surrounded by a long tail of undersized operations.

**Reward concentration is moderate but tilted** (F3.3). The top 100 pools capture 23.2% of recent rewards; the top 250 capture 46.9%. The distribution is not as extreme as a winner-take-all market, but it is far from the flat reward landscape the formulas were designed to produce.

##### O4 — The delegation market is capital-constrained

The binding constraint on the pool landscape is not the reward formulas — it is the amount of ADA participating in delegation.

**43.5% of supply sits outside consensus** (F4.1). Of 38.49B ADA in circulation, only **21.75B** participates in delegation. The remaining **16.75B ADA** earns no rewards and delegates to no pool. This is the same inactive-stake observation documented at stage 1 (§1.1 O3), but here its consequence is direct: it limits how many pools can reach viability and saturation.

**k = 500 is feasible only at full participation** (F4.2). If all circulating ADA entered delegation, 500 saturated pools would be achievable (38.49B / 76.99M ≈ 500). The design target implicitly assumed near-complete participation. Actual participation at 56.5% makes it structurally impossible.

**Institutional actors shape the landscape** (F4.3). The attributed MPO entities — exchanges, custodians, and infrastructure providers — control approximately **29% of supply** and **51% of staked ADA**. Delegation decisions by Coinbase, Binance, Figment, Kiln, and similar institutions are not marginal effects; they define the structural distribution of the pool market. This is neither a bug nor a temporary state — it is the stable configuration of a staking economy where institutional actors dominate capital deployment.

> **Scope note.** Observations O1–O4 document the structural state of the pool-level reward distribution and directly motivate the CIP proposals under evaluation. CIP-0050 (pledge leverage cap) and CIP-0037 (dynamic pledge-linked saturation) both operate at this layer, targeting the pledge-bonus ineffectiveness (O1), the stratification (O2), and the saturation underutilisation (O3). The capital constraint (O4) is upstream and outside CIP scope.

#### 1.2.4 Problems

<!-- TODO: define each problem with evidence from mainnet observations -->
<!-- Expected problems at this layer:
  P2.1 — Pledge paradox: the pledge bonus is designed to incentivise operator commitment, but the a0 curve is too flat to matter at realistic pledge levels
  P2.2 — Viability gap: a large fraction of pools operate below economic viability, creating centralisation pressure
  P2.3 — Capital constraint: inactive stake limits the delegation market, leaving most pools far from saturation
  P2.4 — Uniform saturation threshold: z0 = 1/k treats all pools identically regardless of pledge or quality
-->

#### 1.2.5 Prior Art & Cited Solutions

<!-- TODO: cite solutions from the report and community discussions that are outside stream scope -->
<!-- e.g. pool alliances / virtual pools, latent stake activation, k parameter governance -->

#### 1.2.6 CIP Evaluation: Pledge & Curve Adjustments

> Both CIP-0050 and CIP-0037 operate at this layer.
> They modify the reward-eligible stake definition inside the pool reward curve.

##### 1.2.6.1 CIP-0050 — Pledge Leverage Cap

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the cleaned formulas from §1.2.2)
  3. Which problems from §1.2.4 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. parametrization of L)
-->

##### 1.2.6.2 CIP-0037 — Dynamic Pledge-Linked Saturation

<!-- TODO: same structure as 1.2.6.1 -->

### 1.3 Operator / Delegator Distribution

#### 1.3.1 Flow Overview

These formulas define how a pool's realized allocation is split between the operator and the rest of the pool participants.
The split happens only after the pool-level reward has already been computed and adjusted by apparent performance.

The distribution logic is sequential:

- first, the operator fixed cost is covered
- second, the operator margin is applied to the remaining amount
- finally, the residual reward is distributed proportionally across stake holders

In this final step, the operator still receives a stake-proportional share through the pledge held inside the pool, while delegators receive the complementary share.

#### 1.3.2 Formulas

The operator and member rewards are two complementary views of the same split rule applied to the realized pool allocation.
Once the pool-level reward has been computed, the split follows the same sequence:

- cover the operator fixed cost first
- apply the operator margin to the remaining amount
- distribute the residual proportionally across stake holders

Under this rule, the operator receives both the explicit operator share and the stake-proportional share attached to the pledge held inside the pool, while each member receives a stake-proportional share of the residual amount.

##### 1.3.2.1 SL-D1 (Original)

Operator reward, using the operator stake-share ratio $\frac{s}{\sigma}$ as a single input:

$$
r_{\text{operator}}\left(\hat f,c,m,\frac{s}{\sigma}\right)=
\begin{cases}
\hat f, & \hat f \le c \\
 c + (\hat f-c)\left(m + (1-m)\frac{s}{\sigma}\right), & \hat f > c
\end{cases}
$$

Member reward, using the member stake-share ratio $\frac{t}{\sigma}$ as a single input:

$$
r_{\text{member}}\left(\hat f,c,m,\frac{t}{\sigma}\right)=
\begin{cases}
0, & \hat f \le c \\
(\hat f-c)(1-m)\frac{t}{\sigma}, & \hat f > c
\end{cases}
$$


##### 1.3.2.2 Residual split decomposition

Before switching to reader-friendly variable names, it is useful to separate the split rule into the two regimes induced by the fixed operator cost $c$. Let

$$
\rho_{\text{operator}} = \frac{s}{\sigma}, \qquad
\rho_{\text{member}} = \frac{t}{\sigma}
$$

denote the operator and member pool-share ratios.

If the realized pool allocation does not cover the fixed cost,

$$
\hat f \le c
$$

then the operator absorbs the full realized reward and members receive nothing:

$$
r_{\text{operator}}(\hat f,c,m,\rho_{\text{operator}}) = \hat f,
\qquad
r_{\text{member}}(\hat f,c,m,\rho_{\text{member}}) = 0
$$

If instead the realized pool allocation is large enough to cover the fixed cost,

$$
\hat f > c
$$

let

$$
\mu(\hat f,c,m) := m(\hat f-c),
\qquad
\psi(\hat f,c,m) := (1-m)(\hat f-c)
$$

where $\mu(\hat f,c,m)$ is the operator margin extracted from the residual reward and $\psi(\hat f,c,m)$ is the remaining amount to be shared proportionally across stake holders.

The split then becomes

$$
r_{\text{operator}}(\hat f,c,m,\rho_{\text{operator}})
=
c + \mu(\hat f,c,m) + \psi(\hat f,c,m)\,\rho_{\text{operator}}
$$

$$
r_{\text{member}}(\hat f,c,m,\rho_{\text{member}})
=
\psi(\hat f,c,m)\,\rho_{\text{member}}
$$

This makes the three-layer structure explicit: fixed cost first, operator margin second, proportional sharing of the remainder third.

##### 1.3.2.3 Reader-Friendly

Let the operator and member pool-share ratios be defined as:

$$
\rho^{\text{operator}}_{i} := \frac{\pi^{\text{pledged}}_{i}}{\sigma^{\text{totalStaked}}_{i}},
\qquad
\rho^{\text{member}}_{i} := \frac{\sigma^{\text{poolMember}}_{\text{delegated},i}}{\sigma^{\text{totalStaked}}_{i}}
$$

If the realized pool allocation does not cover the fixed cost,

$$
PoolPot^{\text{actual}}_{i} \le Cost^{\text{operator}}_{\text{fixed}}
$$

then the operator absorbs the full realized reward and members receive nothing:

$$
Reward^{\text{operator}} = PoolPot^{\text{actual}}_{i}
$$

$$
Reward^{\text{member}} = 0
$$

If instead the realized pool allocation is large enough to cover the fixed cost, define the three layers of the split directly as:

$$
Cost := Cost^{\text{operator}}_{\text{fixed}}
$$

$$
Margin := \mu^{\text{operator}}
\left(
PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}
\right)
$$

$$
Share := \left(1-\mu^{\text{operator}}\right)
\left(
PoolPot^{\text{actual}}_{i}-Cost^{\text{operator}}_{\text{fixed}}
\right)
$$

Then the split becomes:

$$
Reward^{\text{operator}} = Cost + Margin + Share\,\rho^{\text{operator}}_{i}
$$

$$
Reward^{\text{member}} = Share\,\rho^{\text{member}}_{i}
$$

This makes the split easy to read: fixed cost first, operator margin second, and proportional sharing of the remainder third.

#### 1.3.3 Structural Decomposition

<!-- TODO: decompose the split into its three layers and their economic roles -->
<!-- Key axes: fixed cost as base compensation, margin as proportional take, residual as delegator yield -->

#### 1.3.4 Mainnet Observations

<!-- TODO: integrate data from pool-landscape-mainnet.md -->
<!-- Key patterns: minPoolCost usage, margin distribution, fee-war dynamics, ROS variance across pool tiers -->

#### 1.3.5 Problems

<!-- TODO: clearly define each problem with evidence -->
<!-- Expected problems at this layer:
  - minPoolCost distortion: 170 ADA fixed cost penalizes small pools relative to their total reward
  - Fee wars: zero-margin race to bottom erodes operator sustainability
  - ROS inequality: delegator return varies significantly by pool despite similar performance
  - Operator insolvency: break-even threshold sits at ~3M ADA under current fee structure
-->

#### 1.3.6 Prior Art & Cited Solutions

<!-- TODO: cite solutions from the report and community discussions that are outside stream scope -->
<!-- e.g. minPoolMargin community consensus, two-stage parameter introduction via hardfork -->

#### 1.3.7 CIP Evaluation: Fee Structure Adjustments

> Both CIP-0023 and CIP-0082 operate at this layer.
> They modify the operator/member split rule without changing the pool-level reward curve.

##### 1.3.7.1 CIP-0023 — Fair Min Fees

<!-- TODO for each CIP at this layer:
  1. Mechanism summary (one paragraph)
  2. Formula substitution (reference the cleaned formulas)
  3. Which problems from §1.3.5 does it address?
  4. Expected effects (positive)
  5. Risks / side effects
  6. Open questions (e.g. what value for minPoolRate?)
-->

##### 1.3.7.2 CIP-0082 — Improved Rewards Scheme

<!-- TODO: same structure as 1.3.7.1, note the staged approach -->

---

## Appendices

### A. Notation Convention

<!-- TODO: migrate from sandbox §8 -->

### B. Symbol Mapping (SL-D1 → Reader-Friendly)

<!-- TODO: migrate from sandbox §9 -->

### C. Detailed Variable Glossary

<!-- TODO: migrate from sandbox §10 -->

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
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

### 3.2 CIP-0050 reward curve substitution

#### 3.2.1 Formulas

##### 3.2.1.1 SL-D1 (Original)

$$
f^{(50)}(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma'_L + s'a_0\cdot\frac{\sigma'_L - s'\left(\frac{z_0-\sigma'_L}{z_0}\right)}{z_0}
\right)
$$

##### 3.2.1.2 Reader-Friendly

$$
{PoolPot^{\text{optimal}}_{i}}^{(50)}
=
\frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}}{k^{\text{protocol}}_{\text{saturation}}}
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
=
\max\left(
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
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

##### 3.4.1.3 SL-D1 (Original)

$$
f^{(37)}(s,\sigma)
=
\frac{R}{1+a_0}
\left(
\sigma'_{37} + s'a_0\cdot\frac{\sigma'_{37} - s'\left(\frac{z_0-\sigma'_{37}}{z_0}\right)}{z_0}
\right)
$$

##### 3.4.1.4 Reader-Friendly

$$
{PoolPot^{\text{optimal}}_{i}}^{(37)}
=
\frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}}{k^{\text{protocol}}_{\text{saturation}}}
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
=
Fee^{\text{epoch}}_{\text{tx}}
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
=
Pot^{\text{epoch}}
$$

##### 4.1.1.2 Mainnet Reader-Friendly

$$
Pot^{\text{epoch}}
=
Fee^{\text{epoch}}_{\text{tx}}
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
=
Pot^{\text{epoch}}
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
=
\frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
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
=
\frac{PoolsPot^{\text{epoch}}}{1+30\%}
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
=
\begin{cases}
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
=
\begin{cases}
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
=
Reward^{\text{operator}}
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
=
Reward^{\text{member}}
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
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)} := \min\left(\sigma^{\text{totalStaked}},k^{\text{protocol}}_{\text{saturation}},L^{\text{protocol}}_{\text{pledgeLeverage}}\cdot\pi^{\text{pledged}}\right)
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by ${\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}$:

$$
{PoolPot^{\text{optimal}}_{i}}^{(50)}
=
\frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(L)}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

Then:

$$
{PoolPot^{\text{actual}}_{i}}^{(50)}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot {PoolPot^{\text{optimal}}_{i}}^{(50)}
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
=
\max\left(
\epsilon^{\text{protocol}}_{\text{saturationFloor}},
\min\left(1,\frac{\pi^{\text{pledged}}}{\sigma^{\text{owner}}_{\text{pledgeRef}}}\right)
\right)
$$

Capped pool stake becomes:

$$
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
:=
\min(\sigma^{\text{totalStaked}},\sigma^{\text{protocol}}_{\text{saturationDynamic}}(\pi^{\text{pledged}}))
$$

Replace $\sigma^{\text{totalStaked}}_{\text{capped}}$ by ${\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}$ in the same baseline reward function:

$$
{PoolPot^{\text{optimal}}_{i}}^{(37)}
=
\frac{PoolsPot^{\text{epoch}}}{1+\alpha^{\text{protocol}}_{\text{skinInTheGame}}}
\left(
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
+
\pi^{\text{pledged}}_{\text{capped}}\cdot \alpha^{\text{protocol}}_{\text{skinInTheGame}}
\cdot
\frac{
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}
-
\pi^{\text{pledged}}_{\text{capped}}
\left(
\frac{k^{\text{protocol}}_{\text{saturation}}-{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(37)}}{k^{\text{protocol}}_{\text{saturation}}}
\right)
}{
k^{\text{protocol}}_{\text{saturation}}
}
\right)
$$

and:

$$
{PoolPot^{\text{actual}}_{i}}^{(37)}=\bar p^{\text{pool}}_{\text{apparent},i}\cdot {PoolPot^{\text{optimal}}_{i}}^{(37)}
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
{\sigma^{\text{totalStaked}}_{\text{capped}}}^{(50+37)}
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
