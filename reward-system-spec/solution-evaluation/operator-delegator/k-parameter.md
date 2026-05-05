# `k` parameter — Standalone analysis

> **Lever:** `stakePoolTargetNum` · **Current value:** 500 · **Governance path:** Parameter Change action (no hard fork) · **Companion to** [CIP-0082](cip-0082.md) stages 3–4 · **No-go as a standalone — under the current weak-pledge equilibrium, new pool slots get absorbed horizontally by existing multi-pool fleets**

This is a sub-document of the CIP-0082 evaluation. It looks at `k` on its own — what changes when only the scalar `k` moves while the reward formula and the operator / member split stay fixed. `k` shows up in the SL-D1 reward formula in two derived places ($z_0 = 1/k$ and $P_{\max} = R/k$), and a raise is a single Parameter Change action (no hard fork). The lever appears as stages 3–4 of CIP-0082 and occasionally as a standalone governance proposal — and rests on a single empirical baseline: the 2020 `k: 150 → 500` raise.

**Raising `k` standalone is a regressive lever in today's weak-pledge regime — it compresses the top tail without redistributing, amplifies a pledge bonus no operator profile is positioned to claim, and lets new slots feed the existing multi-pool fleet.** Of the three structural thresholds in the diagnostic, `k` moves only saturation; production and viability are k-invariant.

Three findings frame the verdict:

- The 2020 `k: 150 → 500` raise produced today's 83-entity MPO landscape — registration cost stays ~500 ADA, infrastructure scales near-horizontally, pledge does not bind expansion.
- The redistribution channel is at most ~8 % of productive stake on demand, and the supply-side amplification runs into the same 0.68 %/yr vs 2.3 %/yr opportunity cost that produces the current non-pledge equilibrium.
- The mechanical effect lands only on the upper tail; below the new $z_0$, hollow pools see zero change in pool reward, operator revenue, or delegator ROS.

*A standalone k-raise becomes a decentralisation tool only after fee-layer and stake-cap reforms have flipped the regime — fee-layer → stake-cap → k-recalibration is the canonical order.*

## Table of Contents

- [1. What raising `k` proposes](#1-what-raising-k-proposes)
- [2. The problem it tries to fix](#2-the-problem-it-tries-to-fix)
- [3. Verdict — three reasons it fails as a standalone](#3-verdict-three-reasons-it-fails-as-a-standalone)
- [4. What it does to mainnet today](#4-what-it-does-to-mainnet-today)
- [5. Read more](#5-read-more)
- [Appendix A — Mechanism in detail](#appendix-a-mechanism-in-detail)
  - [A.1. Formulas inherited from the sub-flows](#a1-formulas-inherited-from-the-sub-flows)
  - [A.2. What `k` moves and what it does not](#a2-what-k-moves-and-what-it-does-not)
  - [A.3. Updated calibration at current parameters (epoch 623)](#a3-updated-calibration-at-current-parameters-epoch-623)
- [Appendix B — Findings](#appendix-b-findings)
  - [B.1. S3 — MPO fleet absorption under weak pledge](#b1-s3-mpo-fleet-absorption-under-weak-pledge)
  - [B.2. S2 — Narrow demand-side segment, insufficient operator-side mechanism](#b2-s2-narrow-demand-side-segment-insufficient-operator-side-mechanism)
  - [B.3. S1 — Top-tail compression with narrow pledge amplification, bottom unchanged](#b3-s1-top-tail-compression-with-narrow-pledge-amplification-bottom-unchanged)
- [Appendix C — Origin, V2 mapping, and references](#appendix-c-origin-v2-mapping-and-references)

## 1. What raising `k` proposes

`k` (protocol parameter `stakePoolTargetNum`) sets Cardano's target pool population. It is currently **500** and shows up in the SL-D1 reward formula in two derived places:

- the per-pool saturation threshold $z_0 = 1/k$;
- the per-pool reward ceiling $P_{\max} = R/k$.

A k-raise is a single Parameter Change action — no hard fork, no formula change. It appears as stages 3–4 of CIP-0082 (`500 → 750 → 1000`), and occasionally as a standalone governance proposal.

This document evaluates the standalone case: what happens when `k` moves and nothing else does.

## 2. The problem it tries to fix

CIP-0082's own rationale states the mechanism this way:

> *"Increasing k may get stale delegations moving again by oversaturating large pools. This will cause many delegators to reconsider their delegation, potentially helping smaller community pools find delegations."*

Two effects are claimed:

- the saturation cap shrinks, so pools above it lose reward and delegators have an incentive to migrate;
- the pledge bonus is amplified for self-pledged pools below the cap, making pledge a more meaningful signal.

The lever also doubles as a proxy for **decentralisation**: more pools, more operators, lower concentration.

Cardano has used the lever once — `k: 150 → 500` in August 2020. That single natural experiment is the only empirical baseline available; any future raise has to be evaluated against what actually happened then.

## 3. Verdict — three reasons it fails as a standalone

A standalone k-raise does not decentralise stake on today's mainnet. Three reasons, each backed by the diagnostic.

#### 1. The 2020 `k: 150 → 500` raise produced today's 83-entity MPO landscape — the same script reruns.

Cardano's only previous k-raise produced the multi-pool landscape the diagnostic now documents: **83 attributed entities, 449 productive pools, 76.7 % of productive stake** (POL.O5.F1). The economic gradient is unchanged: new pool slots cost ~500 ADA to register, existing operators scale near-horizontally on relay topology and ops capacity, and pledge does not bind fleet growth (POL.O5.F3: 42 of 48 saturation-scale MPOs already operate at zero pledge).

*A standalone k-raise does nothing to break this pattern — the natural experiment has already been run.* → [MPO fleet absorption under weak pledge](#b1-s3-mpo-fleet-absorption-under-weak-pledge)

#### 2. The redistribution channel is ~8 % of stake on demand, structurally dominated on supply.

On the demand side, decomposing the 21.57 B ADA of productive stake leaves at best **~8 % of productive stake** in the ROS-responsive segment once custodial holdings (21.1 %), loyal tenure ≥ 2.7 yr (~33 %), and yield-identical switches (50.5 % of volatile-tier moves) are stripped out. On the supply side, the amplified pledge bonus runs into the same opportunity cost that produced the current non-pledge equilibrium: pledge yield 0.68 %/yr against passive-delegation yield 2.3 %/yr.

*The k-raise amplifies a prize in linear `k` for a behaviour operators have no reason to adopt — into a delegator base too small to redistribute network-level concentration.* → [Narrow demand, unmoved supply](#b2-s2-narrow-demand-side-segment-insufficient-operator-side-mechanism)

#### 3. `k` moves only saturation — production and viability lines do not budge, and the bottom is mechanically frozen.

Of the three structural thresholds, **`k` moves only saturation**: production ($n \cdot S_{\text{active}} / (L \cdot f)$, Praos slot mechanics) and viability ($c / (R \lambda_{\text{size}} / \text{CircSupply})$, hollow-pool break-even) contain no `k`. Below the new $z_0$, the `k` cancels exactly in the hollow-pool reward formula: Sub-reliable, Sub-block, and Dormant tiers see zero change in pool reward, zero change in operator revenue (capped at `minPoolCost`), zero change in delegator ROS.

*The bottom of the distribution V2 §3.1 names as foundational priority is mechanically untouched.* → [Top-tail compression, bottom unchanged](#b3-s1-top-tail-compression-with-narrow-pledge-amplification-bottom-unchanged)

#### Bottom line.

A standalone k-raise today is not a decentralisation tool — it is a regressive lever in the current weak-pledge regime. It compresses the top of the reward distribution without redistributing revenue, amplifies a pledge bonus that no operator profile is positioned to claim, and lets new slots be absorbed by existing multi-pool fleets.

It becomes a useful decentralisation lever only **after** a fee-layer change makes pledge worthwhile, and a stake-cap layer prevents fleet absorption. The correct sequence is fee-layer → stake-cap → k-recalibration.

The remainder of the document walks the lever in three steps: §4 quantifies the three measurable mainnet effects (top-tail compression, pledge-bonus amplification, bottom-tier invariance); Appendix A unpacks the formulas, separates what `k` does and does not move, and re-runs the calibration at today's parameters; Appendix B documents the per-finding evidence with verdict tags.

## 4. What it does to mainnet today

A standalone k-raise has three measurable effects on mainnet:

- it compresses the top of the reward distribution;
- it amplifies the pledge bonus for the small population of self-pledged pools;
- it leaves everything below the new saturation cap mechanically unchanged.

#### Pool reward by tier.

| Canonical tier | Rep. σ | $k = 500$ (current) | $k = 750$ | $k = 1000$ | Change |
|---|---:|---:|---:|---:|---|
| Sub-reliable | 2 M | 623 | 623 | 623 | unchanged |
| Healthy | 15 M | 4 675 | 4 675 | 4 675 | unchanged |
| Large healthy | 50 M | 15 584 | 15 584 | **11 942** | compressed at $k = 1000$ |
| Saturated | 77 M | 23 885 | **15 923** | **11 942** | compressed at every step |

*Table 4.1 — Pool reward by tier across k-values. The bottom of the distribution is k-invariant; the top compresses ~50 % between k = 500 and k = 1000.*

#### Operator revenue does not move.

Operator take is capped at `minPoolCost` for every productive tier. As a result, every n-MPO bracket — from single-pool operators to 11+ pool fleets — sees zero revenue change at any k-value. The top-tail compression is absorbed entirely by the cap.

A k-raise creates new pool slots. It does not redistribute revenue from existing ones.

#### Pledge-bonus amplification is real but lands on no one.

A fully self-pledged 15 M ADA pool sees its bonus grow from 28 ADA/epoch at $k = 500$ to 218 ADA/epoch at $k = 1000$ — a 7.7× amplification.

The catch is who fits the profile. The implicit target — high pledge ratio, meaningful scale, retail delegation capture — does not exist on mainnet:

- The 10 largest custodial-by-pledge entities (Cardano Foundation 93.9 %, Chuck/Bux 81.1 %, Liqwid 73.9 %) reach high pledge precisely because they do not compete for retail delegation: their stake is private or treasury-affiliated. Across all 10 entities, **122 delegations** in total.
- The pools that do attract retail delegation (Everstake, Coinbase, Binance, AWP/Atomic Wallet) run at near-zero pledge.

The amplified bonus is a prize with no recipient.

## 5. Read more

- **The CIP that embeds this lever** — [CIP-0082 — Improved Rewards Scheme](cip-0082.md) (stages 3–4)
- **Stake-cap pairing — the precondition for a constructive k-raise** — [CIP-0050 — Pledge Leverage](../pools-distribution/cip-0050.md) · [CIP-0037 — Dynamic Saturation](../pools-distribution/cip-0037.md)
- **How it fits the four-CIP bundle** — [Cross-CIP Analysis & Verdict](../README.md)
- **Mechanism in detail** (formulas, what k moves and doesn't) — [Appendix A](#appendix-a-mechanism-in-detail)
- **Findings list** — [Appendix B](#appendix-b-findings)
- **Origin, V2 mapping, references** — [Appendix C](#appendix-c-origin-v2-mapping-and-references)

## Appendix A — Mechanism in detail

### A.1. Formulas inherited from the sub-flows

**Pool reward** (hollow or pledged, below or above saturation):

$$\hat f'(\nu, \pi, \bar p) = \bar p \cdot P_{\max} \cdot E(\nu, \pi)$$

with

$$P_{\max} = \frac{R}{k}, \qquad E(\nu, \pi) = \lambda_{\text{size}}\,\nu + \lambda_{\text{pledge}}\,A(\nu, \pi), \qquad A(\nu, \pi) = \nu^2 \cdot \pi \cdot \bigl[1 - \pi(1-\nu)\bigr]$$

Normalised coordinates $\nu = \sigma / z_0$ (stake saturation level) and $\pi = s / \sigma$ (within-pool pledge ratio), with $z_0 = 1/k$. On mainnet at $a_0 = 0.3$: $\lambda_{\text{size}} = 1/(1+a_0) \approx 76.9\,\%$ and $\lambda_{\text{pledge}} = a_0/(1+a_0) \approx 23.1\,\%$.

**Operator / member split** (case $\hat f' > c$, typical productive pool):

$$r_{\text{op}} = c + m(\hat f' - c) + (1-m)(\hat f' - c)\,\rho_{\text{op}}, \qquad r_{\text{mem}} = (1-m)(\hat f' - c)\,\rho_{\text{mem}}$$

with $c$ = `minPoolCost`, $m$ = pool margin. For $\hat f' \le c$, the operator absorbs the entire pool reward.

### A.2. What `k` moves and what it does not

A standalone k-raise changes only the scalar `k`. The reward formula is unchanged. A few derived quantities scale with `k`; most do not.

| Quantity | $k = 500$ | $k = 750$ | $k = 1000$ | Nature of change |
|---|---:|---:|---:|---|
| $z_0 = 1/k$ (relative) | 0.2 % | 0.133 % | 0.1 % | Halved at $k=1000$ |
| $z_0$ absolute (×Supply ≈ 38.49 B ADA) | 77 M | 51.3 M | 38.5 M | Halved at $k=1000$ |
| $P_{\max} = R/k$ (at $R \approx 15.53$ M ADA) | 31 060 | 20 707 | 15 530 | Halved at $k=1000$ |
| Saturated hollow reward ($P_{\max} \cdot \lambda_{\text{size}}$) | ≈ 23 885 | ≈ 15 923 | ≈ 11 942 | Halved at $k=1000$ |

*Table A.1 — Derived quantities at three k-values.*

**What `k` does NOT move:**

- **The envelope shape $E(\nu, \pi)$.** $\lambda_{\text{size}}$ and $\lambda_{\text{pledge}}$ are fixed functions of $a_0$, which is not touched.
- **Per-ADA gross reward for a hollow pool below saturation.** Expanding $\hat f'$ for $\pi = 0$, $\nu < 1$:

  $$\hat f' = \bar p \cdot \frac{R}{k} \cdot \lambda_{\text{size}} \cdot \nu = \bar p \cdot \frac{R}{k} \cdot \lambda_{\text{size}} \cdot \frac{\sigma_{\text{abs}} \cdot k}{\text{CircSupply}} = \bar p \cdot R \cdot \lambda_{\text{size}} \cdot \frac{\sigma_{\text{abs}}}{\text{CircSupply}}$$

  **The `k` cancels.** For any hollow pool staying below saturation at the new `k`, the absolute reward is invariant. This is the key mechanical result that refutes the "k-raise pushes the viability line up" framing.

- **The production threshold.** From [pools-distribution §4.1.2.1](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#4121-block-production-threshold), the stake needed to produce $n$ blocks/epoch reliably is $\text{stake}_n \approx n \cdot S_{\text{active}} / (L \cdot f)$, where $L = 432\,000$ slots/epoch and $f = 0.05$ are fixed. **No `k` in the formula.**
- **The viability threshold.** Break-even stake = `minPoolCost` / (Reward per ADA per epoch) = $c / (R \lambda_{\text{size}} / \text{CircSupply})$ — also k-invariant. At today's `minPoolCost = 170`, break-even ≈ 0.54 M ADA.

#### What this means for the nine-tier taxonomy.

The taxonomy rests on three thresholds: production, viability, saturation. **A k-raise moves only saturation.** The production line (~1 M, Sub-block) and the viability line (~0.54 M, hollow break-even) stay exactly where they are. Only the upper bound $z_0$ shifts — and only the upper tail with it.

### A.3. Updated calibration at current parameters (epoch 623)

All calibrations use today's parameters: $R \approx 15.53$ M ADA/epoch, $a_0 = 0.3$, `minPoolCost = 170 ADA`, 73 epochs/year. Hollow-pool convention ($\bar p = 1$, $\pi = 0$, declared $m = 0$). The diagnostic groups pools by stake size into **nine canonical tiers** running from *Dormant* (~50 K, too small to produce blocks reliably) to *Oversaturated*; full definitions in [pools-distribution §4.1.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions).

**Pool reward across nine tiers (hollow pool, ADA/epoch).**

| Canonical tier | Rep. σ | $k = 500$ | $k = 750$ | $k = 1000$ |
|---|---:|---:|---:|---:|
| Dormant | 50 K | 15.6 | 15.6 | 15.6 |
| Sub-block | 500 K | 155.8 | 155.8 | 155.8 |
| Sub-reliable | 2 M | 623 | 623 | 623 |
| Healthy | 15 M | 4 675 | 4 675 | 4 675 |
| Large healthy | 50 M | 15 584 | 15 584 | **11 942** |
| Near-saturation | 67 M | 20 883 | **15 923** | **11 942** |
| Saturated | 77 M | 23 885 | 15 923 | 11 942 |
| Oversaturated | 85 M | 23 885 | 15 923 | 11 942 |

*Table A.2 — Pool reward by tier across k-values. Tiers below the new $z_0$ are k-invariant; tiers above converge to a common ceiling.*

**Operator annualised revenue does not move with `k`.** Every productive pool from Sub-reliable upward earns `minPoolCost × 73 = 12 410 ADA/yr` regardless of the value of `k`. The cap at `minPoolCost` absorbs the top-tail compression entirely — operators never see the cut.

**Delegator net ROS** is the opposite picture: a cut at the top, no change at the bottom.

| Canonical tier | Rep. σ | $k = 500$ | $k = 750$ | $k = 1000$ |
|---|---:|---:|---:|---:|
| Sub-reliable | 2 M | 1.65 % | 1.65 % | 1.65 % |
| Healthy | 15 M | 2.19 % | 2.19 % | 2.19 % |
| Large healthy | 50 M | 2.25 % | 2.25 % | **1.72 %** |
| Saturated | 77 M | 2.26 % | **1.49 %** | **1.12 %** |

*Table A.3 — Delegator net ROS by tier across k-values. A delegator at a Saturated pool sees ROS halve across $k: 500 \to 1000$; a delegator at a Sub-reliable or Healthy pool sees no change at all.*

**Pledge-amplification channel.** For pools with meaningful self-pledge, the bonus $\lambda_{\text{pledge}} A(\nu, \pi)$ scales **linearly in `k`**. For a fully self-pledged 15 M pool:

| $k$ | $\nu$ | $A(\nu, 1) = \nu^3$ | Bonus = $\lambda_{\text{pledge}} \cdot A \cdot P_{\max}$ |
|---:|---:|---:|---:|
| 500 | 0.195 | 0.00739 | **28 ADA/ep** |
| 750 | 0.292 | 0.0250 | **108 ADA/ep** |
| 1000 | 0.390 | 0.0592 | **218 ADA/ep** |

*Table A.4 — Pledge bonus for a fully self-pledged 15 M pool across k-values. 7.7× absolute amplification; annualised, +20 660 ADA/yr.*

This pledge-bonus amplification is the only positive mechanical effect a standalone k-raise delivers. It also lands on a population that is empty in practice — the operators reaching high pledge ratios at scale are private/treasury-affiliated, not pools that compete for retail delegation.

## Appendix B — Findings

The three cards below isolate the three reasons a standalone k-raise fails today: MPO fleet absorption (S3), narrow demand side and unmoved supply side (S2), and top-tail-only mechanical effect (S1). Each card lists its quantified findings.

<article class="sro-card sro-card-pro" id="b1-s3-mpo-fleet-absorption-under-weak-pledge" data-group="3" markdown="1">
<header class="sro-head">
<span class="sro-badge sro-group-3">S3</span>
<div class="sro-titles"><span class="sro-eyebrow">Synthesis 03 · 2 findings</span><h3 class="sro-title">MPO fleet absorption under weak pledge</h3></div>
<span class="sro-count">2 findings</span>
</header>
<p class="sro-abstract" markdown="1">**Under the current weak-pledge regime, new pool slots are absorbed horizontally by existing MPO fleets.** The behavioural alternative to the amplified-pledge-signal channel is MPO fleet absorption — existing multi-pool operators register additional pools to capture the new slots regardless of pledge signal. Two anchors establish the pattern: one empirical, one structural.</p>
<div class="sro-findings-label">Findings</div>
<ol class="sro-findings" markdown="1">
<li class="sro-finding" id="s3-f1" data-group="3" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-3" href="#s3-f1" title="S3.F1 — Regresses"><span class="sro-fid-label">[R] #1</span><span class="sro-fid-ref">S3.F1</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Historical `k: 150 → 500` (Aug 2020) produced today's MPO landscape.** The only previous k-raise in Cardano's live protocol history. Within two years of the raise, the MPO fleet pattern stabilised at the form the diagnostic now documents: **83 attributed entities controlling 76.7 %** of productive stake across **449 productive pools**. The raise did not produce a proportional increase in independent entities; it produced multi-pool expansion by existing operators. This is not a predictive model — it is the actual observed outcome of the one natural experiment Cardano has run on `k` at scale.</div></div>
</li>
<li class="sro-finding" id="s3-f2" data-group="3" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-3" href="#s3-f2" title="S3.F2 — Regresses"><span class="sro-fid-label">[R] #2</span><span class="sro-fid-ref">S3.F2</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Structural economics favour fleet expansion over new-entrant entry.** Three quantitative anchors from the diagnostic, all directly observable on mainnet (no modelling required): **(i)** Pool registration cost is ~500 ADA per pool. Median retail MPO entity revenue: 25 K – 1 M ADA/yr depending on fleet size — an existing MPO can register a new pool at sub-0.05 % of annual revenue. **(ii)** Operational infrastructure scales near-horizontally: an operator already running $N$ pools has the relay topology, monitoring, keyset tooling, and ops capacity to run $N+1$ pools at near-zero marginal cost. **(iii)** Pledge is not binding on fleet expansion under the current formula — 42 of 48 saturation-scale MPOs already operate without meeting pledge targets. For a new-entrant operator to out-compete an existing MPO for a new slot, they would need to match the MPO's brand / wallet / marketing channel — a channel the k-raise does not amplify. The economic gradient favours expansion, not entry.</div></div>
</li>
</ol>
</article>

#### What would change this.

The regression is conditional on weak pledge. Once a stake-cap layer binds — CIP-0050's `L`, or CIP-0037's dynamic saturation — fleet expansion is no longer possible at the upper tail, and new pool slots have to go to new entrants.

In that order, a k-raise becomes a decentralisation tool. The correct sequence is therefore:

1. fee-layer fix (so pledge is not a dominated strategy);
2. stake-cap (so the upper tail cannot absorb new slots);
3. k-recalibration.

**A standalone k-raise before a stake-cap makes things worse, not better.**

<article class="sro-card sro-card-pro" id="b2-s2-narrow-demand-side-segment-insufficient-operator-side-mechanism" data-group="2" markdown="1">
<header class="sro-head">
<span class="sro-badge sro-group-2">S2</span>
<div class="sro-titles"><span class="sro-eyebrow">Synthesis 02 · 2 findings</span><h3 class="sro-title">Narrow demand-side segment, insufficient operator-side mechanism</h3></div>
<span class="sro-count">2 findings</span>
</header>
<p class="sro-abstract" markdown="1">**A fine tool for a narrow delegator segment, insufficient on the operator side because the formula is unchanged.** The CIP-0082 rationale frames this as a ROS-based redistribution claim — delegators choose pools partly on yield, oversaturation cuts yield at the top, therefore delegators migrate toward smaller pools. The diagnostic undermines both conditions.</p>
<div class="sro-findings-label">Findings</div>
<ol class="sro-findings" markdown="1">
<li class="sro-finding" id="s2-f1" data-group="2" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-2" href="#s2-f1" title="S2.F1 — Regresses"><span class="sro-fid-label">[R] #1</span><span class="sro-fid-ref">S2.F1</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**The ROS-focused delegator segment is a minority of productive stake.** Decomposing the 21.57 B ADA of productive stake:

<table class="sro-evidence-table">
<thead><tr><th>Segment</th><th>Stake</th><th>Share</th><th>Responsive to a ROS signal?</th></tr></thead>
<tbody>
<tr><td>Custodial (funds not discretionary)</td><td>4.55 B</td><td>21.1 %</td><td><strong>No</strong> &mdash; funds are custodied, reallocation is not a retail choice</td></tr>
<tr><td>Retail, loyal tenure &ge; 2.7 yr</td><td>~7.15 B</td><td>~33 %</td><td><strong>No</strong> &mdash; 42 % of delegations have not moved in 2.7+ years</td></tr>
<tr><td>Retail, volatile tenure &lt; 25 d</td><td>~3.57 B</td><td>~17 %</td><td>Potentially &mdash; but 50.5 % of switches land on yield-identical pools, and non-identical moves show <strong>visibility</strong>, not yield, asymmetry</td></tr>
<tr><td>Retail, middle tenure</td><td>~6.30 B</td><td>~29 %</td><td>Unclear</td></tr>
</tbody>
</table>

The ROS-responsive segment that the k-raise redistribution mechanism actually targets is **at most the subset of the retail-volatile tier whose switches are not yield-identical** — at best ~8 % of productive stake. A single-digit-percent redistribution channel is not a network-level concentration reform.</div></div>
</li>
<li class="sro-finding" id="s2-f2" data-group="2" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-2" href="#s2-f2" title="S2.F2 — Regresses"><span class="sro-fid-label">[R] #2</span><span class="sro-fid-ref">S2.F2</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Changing `k` without revising the reward formula leaves the non-pledge equilibrium intact.** Operators do not pledge today for a well-understood reason: pledge yield (0.68 %/yr at best) is structurally dominated by passive-delegation yield (~2.3 %/yr). 78 % of staked ADA sits in pools with pledge ratio < 1 %; 42 of 48 saturation-scale MPOs forfeit the bonus. A k-raise amplifies the pledge-bonus term roughly linearly in `k` for fully self-pledged pools below the new $z_0$, but keeps $A(\nu, 0) = 0$ — hollow pools (the overwhelming majority of productive stake) untouched — and leaves the surrounding formula that makes pledge a dominated strategy *unchanged*. The amplified bonus is a larger prize for a behaviour operators still have no reason to adopt.</div></div>
</li>
</ol>
</article>

#### Why the demand side is narrow and the supply side is unmoved.

A k-raise is not a wrong instrument in the abstract. It is a narrow instrument facing a narrow audience on the demand side, and an insufficient instrument on the supply side because the formula that produces the non-pledge equilibrium is unchanged.

The implicit target of the amplified pledge bonus is "high pledge + meaningful scale + retail delegation capture". On mainnet, this combination does not exist:

- Operators with high pledge ratios at scale are the **Custodial-by-pledge segment** — 10 entities, 36 pools, 1.59 B ADA, only **122 delegations** in total. Cardano Foundation (93.9 % pledge ratio), Chuck/Bux (81.1 %), Liqwid (73.9 %) are all private or treasury-affiliated, not chasing retail.
- Brands that do attract retail delegation (Everstake, Coinbase, Binance, AWP/Atomic Wallet) run at near-zero pledge and capture delegation through wallet integration and marketing.

The amplified bonus is a larger prize for a profile no one currently fills.

<article class="sro-card sro-card-pro" id="b3-s1-top-tail-compression-with-narrow-pledge-amplification-bottom-unchanged" data-group="1" markdown="1">
<header class="sro-head">
<span class="sro-badge sro-group-1">S1</span>
<div class="sro-titles"><span class="sro-eyebrow">Synthesis 01 · 4 findings · the design-strength row</span><h3 class="sro-title">Top-tail compression with narrow pledge amplification, bottom unchanged</h3></div>
<span class="sro-count">4 findings</span>
</header>
<p class="sro-abstract" markdown="1">**Top-tail compression + narrow pledge amplification; bottom unchanged.** The mechanical content of a standalone k-raise is the sum of four effects on the reward function — three regressive or blind, one delivery. The findings below isolate each one.</p>
<div class="sro-findings-label">Findings</div>
<ol class="sro-findings" markdown="1">
<li class="sro-finding" id="s1-f1" data-group="1" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-1" href="#s1-f1" title="S1.F1 — Regresses"><span class="sro-fid-label">[R] #1</span><span class="sro-fid-ref">S1.F1</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Top-tail compression.** At $k: 500 \to 1000$, every pool with $\sigma$ above the new $z_0 = 38.5$ M ADA converges to the same ceiling of ≈ 11 942 ADA/ep — a **−50 %** reward cut for today's Saturated-tier pools. The k-raise acts exclusively on the upper tail.</div></div>
</li>
<li class="sro-finding" id="s1-f4" data-group="1" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-1" href="#s1-f4" title="S1.F4 — Blind spot"><span class="sro-fid-label">[B] #2</span><span class="sro-fid-ref">S1.F4</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Of the three structural thresholds, `k` moves only saturation.** Production threshold ($n \cdot S_{\text{active}} / (L \cdot f)$, Praos slot mechanics) and viability threshold ($c / (R \lambda_{\text{size}} / \text{CircSupply})$, hollow-pool break-even) contain no `k`. At mainnet today: 3-block threshold ≈ 2.92 M ADA, hollow-pool break-even ≈ 0.54 M ADA. Both are k-invariant. **A k-raise does not rescue any pool at the production or viability boundary.**</div></div>
</li>
<li class="sro-finding" id="s1-f3" data-group="1" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-1" href="#s1-f3" title="S1.F3 — Blind spot"><span class="sro-fid-label">[B] #3</span><span class="sro-fid-ref">S1.F3</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Hollow pools below saturation see zero mechanical change.** The formula collapses to $\hat f' = \bar p \cdot R \cdot \lambda_{\text{size}} \cdot \sigma_{\text{abs}} / \text{CircSupply}$ — the scalar `k` disappears. Operator revenue (capped at `minPoolCost`) and delegator ROS are both invariant for the entire Sub-reliable, Sub-block, and Dormant populations. The "k-raise helps small pools" framing has no mechanical foundation.</div></div>
</li>
<li class="sro-finding" id="s1-f2" data-group="1" markdown="1">
<a class="sro-fid sro-fid-stack sro-group-1" href="#s1-f2" title="S1.F2 — Delivers"><span class="sro-fid-label">[D] #4</span><span class="sro-fid-ref">S1.F2</span></a>
<div class="sro-body" markdown="1"><div class="sro-evidence" markdown="1">**Pledge-bonus amplification for self-pledged pools.** For self-pledged pools below the new saturation, the bonus $\lambda_{\text{pledge}} A(\nu, \pi)$ scales linearly in `k` in absolute terms. A fully self-pledged 15 M pool's bonus grows from 28 ADA/ep at $k = 500$ to 218 ADA/ep at $k = 1000$ — **7.7× amplification**, +20 660 ADA/yr. This is the only genuinely positive mechanical effect a standalone k-raise delivers — but it lands on a population (Custodial-by-pledge) that does not capture retail delegation.</div></div>
</li>
</ol>
</article>

#### A common misreading, corrected.

A recurring claim — in earlier drafts of this evaluation and in governance discussions — is that a k-raise "pushes the viability line up" and makes sub-threshold pools worse. The formula does not behave that way when only `k` moves.

What does push the viability line up is a change in the fee structure (`minPoolCost`) or the reward pot ($R$, e.g. reserve depletion). A `k` change leaves both untouched.

## Appendix C — Origin, V2 mapping, and references

### C.1. Identity card

| Field | Value |
| --- | --- |
| Parameter | `stakePoolTargetNum` |
| Current value | `k = 500` |
| Governance path | Standard Parameter Change action (Conway-era) |
| Hard fork required | No |
| Layer | Neither fee nor stake-cap — sets the scalar of the existing SL-D1 reward formula |
| Reference | [Pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards) |

### C.2. Origin and context

**Historical moves.** `k` has been raised once in Cardano's live history: `k: 150 → 500` in August 2020, about a year after Shelley launch. The argument was the same one heard today — more pools means more decentralisation. The observed outcome was the rise of the multi-pool-operator pattern that the diagnostic now documents.

**Current governance discussions.** A k-raise appears in two forms today:

- as stages 3–4 of CIP-0082 (`500 → 750 → 1000`);
- as a standalone proposal outside the CIP-0082 package.

This document covers the standalone case. The CIP-0082-embedded case is analysed in [`cip-0082.md`](cip-0082.md).

### C.3. References

- **Companion CIP evaluation:** [`cip-0082.md`](cip-0082.md) — same structural critique applied to CIP-0082 stages 3–4.
- **Stake-cap pairing candidates (precondition for a constructive k-raise):** [`../pools-distribution/cip-0050.md`](../pools-distribution/cip-0050.md), [`../pools-distribution/cip-0037.md`](../pools-distribution/cip-0037.md). Note: those CIPs *change the reward formula* (CIP-0050 via σ′ clipping, CIP-0037 via a new saturation curve); once either is active, the analysis in this doc no longer directly applies.
- **Formulas inherited:** [pools-distribution §2.3 simplified reward function](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#23-reward-function) ($\hat f'$, $P_{\max}$, $E$, $A$); [operator-delegator §1.1.1 split formula](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md).
- **Numerical baselines:** Appendix A of this file. Nine-tier taxonomy: [pools-distribution §4.1.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#413-tier-definitions). n-MPO brackets: [operator-delegator §4.4](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md#44-operator-profitability-versus-delegator-return).
- **Diagnostic findings cited:** OPE.O7.F1, OPE.O7.F2 (operator-delegator); POL.O2.F1, POL.O2.F2, POL.O3.F5, POL.O3.F6, POL.O5.F1, POL.O5.F3, POL.O6.F2 (pools-distribution); CEN.O4.F2, CEN.O6.F1, CEN.O6.F3 (census).
- **Canonical source:** [Pledging & rewards reference](https://docs.cardano.org/about-cardano/learn/pledging-rewards).

> **Status:** Active 2026/04/23. Companion to CIP-0082 stages 3–4.
