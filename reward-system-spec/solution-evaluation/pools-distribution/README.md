# Pools distribution — Stake-cap layer

> **Status:** Active 2026/04/23. Subfolder of [`../README.md`](../README.md). Candidates that act on the stake-cap layer of the Cardano reward pipeline. Sources in §5.

## Executive summary

- **Scope.** Reward-eligible pool stake $\sigma'$ used inside the SL-D1 reward curve. The fee split that follows is untouched ([`../operator-delegator/`](../operator-delegator/README.md)); what changes is the allocation envelope itself — these CIPs act on **the reward-distribution formula**, upstream of the operator/member split.

- **What the CIPs in this folder correctly identify.** CIP-0050 and CIP-0037 act on what our mainnet diagnostic confirms is a **broken signal**: pledge is priced as irrelevant by the operator population. POL.O2.F2 shows pledge yield is structurally dominated by passive-delegation yield (0.68 %/yr vs ~2.3 %/yr); POL.O2.F1: 78 % of staked ADA sits in pools with pledge ratio < 1 %; POL.O4.F3: 41 of 48 capital-sufficient MPOs forfeit the bonus. Both CIPs target this correctly by making pledge **binding** on the reward formula — without pledge, reward is clipped.

- **Right layer, different target from the fee CIPs.** These CIPs act on the correct V2 layer (reward-distribution, pre-split) — the layer the principled critique of [`../operator-delegator/README.md`](../operator-delegator/README.md) identified as the right home for distributional fixes. But their **target** is V2 §3.2 (pledge-as-signal) and §3.4 (concentration via Sybil cost), **not** §3.1 (small-operator viability). The V2 priority-1 problem (small-operator viability) is not what these instruments solve.

- **The capital-capability bias.** By making pledge binding, both CIPs implicitly discriminate by the operator's **capital capability**, not by operator quality or network contribution:
  - **Custodial entities (21 % of productive stake)** hold custodied retail funds they legally cannot self-pledge — reward for this segment collapses to the pledge floor regardless of operator quality.
  - **Retail small operators (POL.O5.F2: 78 % of single-pool stake non-compliant at pledge < 2 %)** mostly don't have the capital to raise pledge — their only response is to accept reduced reward or exit.
  - **Capital-sufficient MPOs (POL.O4.F2: 48 entities)** can in principle pledge more; a subset will choose to, a subset will not.

  The reform rewards the population that *can* pledge and penalises the population that *cannot* — independent of whether the penalised pools produce reliable blocks, serve delegators well, or contribute to decentralisation by any other measure.

- **The side effect on small-operator viability.** Small retail pools that have attracted delegation in reliance on V1 rules (low pledge + significant delegation) see their $\sigma'$ clipped — both operator revenue and delegator ROS drop. This is the **opposite direction** of the V2 §3.1 viability goal. The stake-cap layer in its current form does not help the small-operator population the fee-layer reforms also failed to help — it can actively worsen it for the low-pledge subset.

- **The bet.** Both CIPs implicitly bet that operators will respond by **increasing pledge** rather than by accepting reduced reward. Two populations make that bet hard:
  - Custodial entities cannot respond (structural). Their reward drops with no recourse.
  - Retail small operators have no capital to pledge more. Their only move is to exit or shrink.

  The population that *can* respond (capital-sufficient MPOs) already has the pledge-bonus choice available today and has empirically opted against it (POL.O4.F3). There is no mainnet signal that reshaping $\sigma'$ flips that choice for a meaningful fraction of the population.

- **A principled framing — consistent with the fee-layer critique.** The companion [`../operator-delegator/README.md`](../operator-delegator/README.md) argues that viability should be abstracted from pricing tools. The same separation applies here: **pledge-as-signal** (what §3.2 targets) is a different function from **viability** (what §3.1 targets). A stake-cap instrument that restores pledge-as-signal is legitimate on its own terms, but should not be advanced as a solution to small-operator viability, and should not be deployed without an active viability instrument protecting the low-pledge retail population that the stake-cap rule would otherwise penalise.

## Contents

- [Executive summary](#executive-summary)
- [1. Stake-cap formulas](#1-stake-cap-formulas)
- [2. Why a new instrument when V1 already has a pledge lever?](#2-why-a-new-instrument-when-v1-already-has-a-pledge-lever)
  - [2.1 The `a₀` lever rebalances, it doesn't tilt](#21-the-a-lever-rebalances-it-doesnt-tilt)
  - [2.2 The deeper bottleneck — A(π, ν) itself](#22-the-deeper-bottleneck--aπ-ν-itself)
    - [2.2.1 Anatomy of the function — before any numbers](#221-anatomy-of-the-function--before-any-numbers)
    - [2.2.2 What A actually pays — three operators across three pledge levels](#222-what-a-actually-pays--three-operators-across-three-pledge-levels)
    - [2.2.3 The cubic ν³ — visualised](#223-the-cubic-ν³--visualised)
    - [2.2.4 What this means for the CIP critique](#224-what-this-means-for-the-cip-critique)
  - [2.3 What this implies for the CIP candidates in this folder](#23-what-this-implies-for-the-cip-candidates-in-this-folder)
- [3. Candidates](#3-candidates)
- [4. Composition](#4-composition)
- [5. Interaction with `k`](#5-interaction-with-k)
- [6. V2 milestone interaction](#6-v2-milestone-interaction)
- [7. Reading order](#7-reading-order)
- [8. References](#8-references)

## 1. Stake-cap formulas

**The shared intent.** Under V1, the saturation cap is a **constant** — `orig_sat = 1/k ≈ 67.44 M ₳` at `k = 500` — independent of pledge. A pool can attract delegation up to that ceiling regardless of how much pledge the operator puts up; pledge enters the reward calculation only via the small bonus term $a_0$ in the SL-D1 numerator (worth ≈ 30 % of the reward at $a_0 = 0.3$, but structurally dominated by passive-delegation yield — see POL.O2.F2).

Both CIPs in this folder share a single intent: **replace this constant horizontal cap with a function of pledge**. The new cap rises linearly with the operator's pledge until it reaches the V1 ceiling $\text{orig\_sat}$ — beyond that, the new rule and V1 coincide. The intent is identical for both candidates: *to earn the V1 ceiling, an operator must pledge enough; below that pledge level, the effective cap is reduced proportionally.*

Both candidates therefore reshape $\sigma'$ (reward-eligible pool stake) as a **linear function of pledge**, with the V1 ceiling $\text{orig\_sat} = 1/k$ as hard upper bound. They differ only on what happens below the slope:

| Mechanism | Simplified formula | Effective parameters |
| --- | --- | --- |
| V1 baseline | $\sigma' = \min(\sigma,\ \text{orig\_sat})$ | $k$ only |
| CIP-0050 — pledge-leverage cap | $\sigma' = \min\!\bigl(\sigma,\ \text{orig\_sat},\ L\cdot p\bigr)$ | $L$ (one scalar) |
| CIP-0037 — dynamic saturation | $\sigma' = \min\!\bigl(\sigma,\ \mathrm{clamp}(\ell\cdot p,\ e\cdot\text{orig\_sat},\ \text{orig\_sat})\bigr)$ | $(e, \ell)$ — $p_{100\%} = \text{orig\_sat}/\ell$ is derived |

**Structural kinship.** For any pool large enough that $\sigma \geq \text{orig\_sat}$, the two candidates are **the same primitive** — a linear-in-pledge slope capped at the V1 saturation — differing only on what happens when pledge is low:

- **CIP-0050** clips the stake cap to $L \cdot p$ — at zero pledge, $\sigma' = 0$ (hard break).
- **CIP-0037** clamps the stake cap to $\ell \cdot p$ but places a **floor** at $e \cdot \text{orig\_sat}$ — at zero pledge, $\sigma' = e \cdot \text{orig\_sat} \approx 13.49$ M ₳ at reference.

Reference leverages differ by convention ($\ell = 125$ vs $L = 100$), not by design intent.

![CIP-0037 vs CIP-0050 — same primitive + floor](figures/cip0037_02_vs_cip0050.png)

Panel (b) matches leverage at $\ell = L = 125$ to isolate the floor as the sole structural difference. **CIP-0037 is CIP-0050 plus a floor** — both target V2 §3.2 pledge-as-signal and §3.4 concentration via the same mechanism; CIP-0037 softens the low-pledge edge at a three-scalar governance cost instead of a one-scalar one.

## 2. Why a new instrument when V1 already has a pledge lever?

V1 already exposes a pledge-incentive knob: the **pledge influence factor** $a_0$ (currently `0.3` on mainnet). It enters the SL-D1 reward envelope as the weight of the pledge-bonus term:

$$E(\pi, \nu) \;=\; \underbrace{\lambda_{\min} \cdot \nu}_{\text{base — independent of pledge}} \;+\; \underbrace{\lambda_{\max} \cdot A(\pi, \nu)}_{\text{bonus — pledge-sensitive}}$$

with $\lambda_{\min} = 1/(1+a_0)$, $\lambda_{\max} = a_0/(1+a_0)$, and the **pledge-bonus activation function**

$$A(\pi, \nu) \;:=\; \pi\nu \;-\; \pi^2(1-\nu)$$

(Notation and derivation in [diagnostic / pools-distribution §2.3](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#235-reader-friendly-reward-function).)

**What π and ν actually mean.** Both are **dimensionless ratios**, normalised by the V1 saturation cap $z_0 = 1/k$ (≈ **67.44 M ADA** at the mainnet `k = 500`). Think of $z_0$ as "the size of one fully-saturated pool" — the reference unit in which the formula expresses everything.

| Symbol | Definition | Range | What it measures | Concrete example |
|---|---|---:|---|---|
| **ν**  | $\sigma / z_0$ | $[0, 1+]$ | **Stake saturation level** — what fraction of one full V1 pool your *total* stake represents | Healthy 15 M pool: $\nu = 15/67.44 = 0.222$.  Saturated pool: $\nu \approx 1$. |
| **π**  | $p / z_0$ | $[0, \nu]$ | **Pledge saturation level** — what fraction of one full V1 pool your *self-pledge* represents | Pool with 100 k pledge: $\pi = 0.100/67.44 = 0.0015$.  Fully-pledged saturated pool: $\pi = 1$. |

Two structural constraints to internalise:

- **π ≤ ν** by construction — your pledge is part of your total stake (you can't pledge more than the pool holds). The diagonal **π = ν** is the line of *full self-pledge* (no delegators, the operator owns 100 % of the pool).
- The familiar **pledge ratio** (pledge as fraction of pool stake) you see in CIP discussions is exactly $\rho = p/\sigma = \pi/\nu$. Mainnet's stake-weighted median is $\rho \approx 0.07\,\%$ (POL.O2.F1) — operators sit very far below the diagonal.

A reading shortcut: when you see **π** in the formula, think *"how much pledge is the operator putting in, expressed in V1-pool units"*. When you see **ν**, think *"how big is this pool, expressed in V1-pool units"*. Both are bounded by 1 in the design domain.

The natural question is therefore: *why propose CIP-0050 / CIP-0037 instead of just raising `a₀`?* The answer requires looking at three nested layers — the lever's **shape**, the bonus function's **structure**, and what no proposal currently touches.

### 2.1 The `a₀` lever rebalances, it doesn't tilt

Raising `a₀` shifts more weight from the base term ($\lambda_{\min}\nu$) onto the bonus term ($\lambda_{\max}A$). For a low-pledge pool this *reduces* the base by more than the bonus can recover — the operator is punished smoothly, not catalysed.

![V1 levers vs CIP-0050 / CIP-0037 — Healthy pool](figures/cip_levers_01_smooth_vs_hard.png)

Panel (a). For a Healthy pool ($\sigma = 15$ M, $\nu \approx 0.222$): raising $a_0$ from `0.3` → `1.0` drops the zero-pledge reward to **65 %** of baseline; raising to `3.0` drops it to **32 %**. The bonus barely recovers across the full pledge range — even at 600 k of self-pledge the higher-`a₀` curves stay below baseline. **The `a₀` lever cannot make pledge "matter more" without first making low-pledge pools earn less.**

Panel (b). CIP-0050 and CIP-0037 don't touch $(λ_{\min}, λ_{\max})$. They clip $\sigma'$ before the reward formula runs, so the penalty hits the **base term** $λ_{\min} \cdot \nu'$ — which is structurally *much larger* than $λ_{\max} \cdot A$ at any reasonable pool size. That is why their cliff is steep where `a₀` tweaks barely move the needle.

### 2.2 The deeper bottleneck — A(π, ν) itself

Both `a₀` (rebalancing) and CIP-0050 / CIP-0037 (clipping) operate **around** the A function. Neither modifies it. So before plugging any numbers in, dissect the function itself: what does it say structurally, and is the structure even sound?

#### 2.2.1 Anatomy of the function — before any numbers

![Structural anatomy of A(π, ν) — domain triangle and non-monotonicity](figures/cip_levers_04_A_structural_anatomy.png)

**(i) Not all (π, ν) tuples are valid — the domain is a triangle, not a rectangle.**

A is written as a function of two variables π and ν, suggesting they are independent inputs. They are not. The protocol enforces

$$p \;\leq\; \sigma \quad\Longleftrightarrow\quad \pi \;\leq\; \nu$$

— pledge cannot exceed pool stake, because pledge *is part of* the pool's stake. Half of the unit square `[0,1] × [0,1]` is therefore unreachable: the upper triangle (π > ν) corresponds to operator configurations the protocol forbids.

This is already a **structural smell**. A well-designed two-variable function expresses two *independent* degrees of freedom. Here π and ν are coupled by an external constraint that the formula ignores. The natural reparametrisation is `(ν, ρ)` where `ρ = π/ν` is the pledge ratio (both bounded in `[0, 1]`, both independent) — but the formula uses `(π, ν)` instead. The mismatch propagates: every reasoning about A has to carry the side-condition "and remember π ≤ ν", which is exactly the kind of invisible footgun that produces the pathologies below.

Panel (a) of the figure shows this: the green triangle is the entire valid domain of A; the hatched region above the diagonal is impossible. The orange strip near `π = 0` is where mainnet actually operates (median pledge ratio 0.07 % — operators sit very far from the diagonal).

**(ii) Tour of the boundaries.**

| Boundary | What it represents | A reduces to |
|---|---|---|
| `π = 0` (left edge) | Zero pledge | $A = 0$ — no bonus, sensible. |
| `ν = 1` (top edge of the valid triangle, at saturation) | Saturated pool | $A = \pi - \pi^2 \cdot 0 = \pi$ — linear in pledge, well-behaved. |
| `π = ν` (the diagonal) | Full self-pledge — operator owns 100 % of the pool | $A = \nu \cdot \nu - \nu^2 (1-\nu) = \nu^3$ — **cubic in pool size**. |

The third boundary is where the construction collapses. The carefully shaped quadratic-in-π expression `πν − π²(1−ν)` becomes simply `ν³` when the operator commits everything they own. That cube is the load-bearing pathology — coming back to it shortly.

**(iii) The penalty term `−π²(1−ν)` and what it was supposed to do.**

The two terms have distinct intents. The first, `πν`, is a bilinear "pledge × stake" reward — bigger pool with more pledge earns more bonus. The second, `−π²(1−ν)`, is a **splitting penalty** the SL-D1 design adds on purpose: an MPO who splits a fixed pledge `P` across `N` pools (each with `p = P/N` and total stake `Nσ_i`) sees the per-pool A reduced by something quadratic in their per-pool pledge fraction. The whitepaper's intent was to make MPO splitting reward-neutral.

The construction *does* achieve that intent in some regions. But it pays a heavy price elsewhere — pathology (iv) below.

**(iv) The structural defect — A is non-monotone in π for any ν < 0.5.**

Take the partial derivative of A with respect to π at fixed ν:

$$\frac{\partial A}{\partial \pi} \;=\; \nu \;-\; 2\pi(1-\nu)$$

This is zero at `π* = ν / (2(1−ν))` and negative for `π > π*`. Two regimes follow:

- For `ν ≥ 0.5`: `π* ≥ ν`, so the maximum sits **at or beyond the boundary** of the valid domain. Inside the valid domain, A is monotone increasing in π — pledging more always earns more bonus. ✓
- For `ν < 0.5`: `π* < ν`, so the maximum sits **inside** the valid domain. Increasing pledge from `π*` up to `π = ν` (full self-pledge) **decreases** A. *Pledging more pays less.*

Worked example at `ν = 0.3`:

| π | A(π, 0.3) |
|---:|---:|
| 0.10 | 0.02300 |
| 0.15 | 0.02925 |
| 0.20 | 0.03200 |
| **0.214 (= π*)** | **0.03214 ← max** |
| 0.25 | 0.03125 |
| **0.30 (= ν, full self-pledge)** | **0.02700 — 16 % BELOW the max** |

For a pool at half-saturation (`σ = 33 M`, `ν = 0.5`), the optimal pledge is exactly the pool's full stake — the boundary is the maximum. Below half-saturation, an operator who fully self-pledges *destroys* part of their bonus by doing so. The formula whose stated purpose is "skin in the game" pays you **less for putting in more skin**, for the entire population of pools below half-saturation — which is essentially the entire mainnet population.

Panel (b) of the figure shows this: each curve is A at fixed ν as a function of π over the valid domain `[0, ν]`. The gold star marks the interior maximum; the square marks the full self-pledge endpoint. For `ν < 0.5`, the square is *below* the star.

**(v) Summary of structural critiques — before any numbers.**

1. The domain is a triangle, not a rectangle — π and ν are coupled, the formula's parametrisation hides this.
2. On the full-self-pledge boundary (π = ν), the elaborate quadratic construction collapses to `ν³`.
3. For any pool below half-saturation, A is non-monotone in π — pledging beyond `π* = ν/(2(1−ν))` actively reduces the bonus.
4. The intended MPO-splitting penalty (`−π²(1−ν)`) is achieved at the cost of these defects.

These are pre-empirical defects: they hold regardless of mainnet data, regardless of what `a₀` is set to, regardless of CIP reforms acting on σ′. They are properties of the algebra. With this in hand, the next subsection puts numbers on what they mean for actual operators.

#### 2.2.2 What A actually pays — three operators across three pledge levels

**Cast.** Three honest operators, all running pools of different sizes:

- **Bob** runs a Sub-viable 2 M ADA pool ($\nu \approx 0.03$).
- **Charles** runs a Healthy 15 M ADA pool ($\nu \approx 0.222$).
- **Alice** runs a Saturated 67 M ADA pool ($\nu \approx 0.99$).

All three are below half-saturation except Alice, so Bob and Charles already sit in the non-monotone regime described in (iv). Now follow the same three pledge configurations on each.

##### Scenario A — what mainnet actually does today (median pledge ratio 0.07 %)

This is where 78 % of staked ADA actually sits today (POL.O2.F1). Operators put down a token amount of pledge and earn near-zero bonus — but lose nothing significant either, because the opportunity cost of pledging that token amount is also small.

| Operator | Pool σ | Pledge p (0.07 %) | Yearly bonus from A |
|---|---:|---:|---:|
| Bob | 2 M | 1 400 ₳ | **0.3 ₳/yr** ($0.08) |
| Charles | 15 M | 10 500 ₳ | **18 ₳/yr** ($4.50) |
| Alice | 67 M | 47 000 ₳ | **362 ₳/yr** ($90) |

Even Alice — a Saturated pool with the median pledge ratio — only earns ~$90/yr in pledge bonus. The formula is essentially silent about pledge for everyone in this scenario. *This is the equilibrium the diagnostic captures.*

##### Scenario B — what CIP-0050 demands at L = 100  (1 % pledge ratio)

To reach the CIP-0050 compliance threshold (`p ≥ σ/L`), each operator must commit substantially more capital. The bonus *does* grow — but the disparity across pool sizes already shows up sharply.

| Operator | Pool σ | Pledge p (1 %) | Yearly bonus from A |
|---|---:|---:|---:|
| Bob | 2 M | 20 000 ₳ | **4.6 ₳/yr** |
| Charles | 15 M | 150 000 ₳ | **257 ₳/yr** |
| Alice | 67 M | 670 000 ₳ | **5 168 ₳/yr** |

Same act (1 % pledge ratio) — Alice earns **1 123× more bonus than Bob** for committing the same *fraction* of her pool. And Bob has just been asked to lock 20 000 ₳ ($5 000) of his own capital to earn 4.6 ₳/yr ($1.15) in bonus. *The yield on his pledge is 0.023 % vs 2.3 % passive — he loses ~100× by complying.*

##### Scenario C — the maximum signal anyone can give (100 % self-pledge)

The strongest possible commitment: every ADA in the pool is the operator's own. No MPO games, no delegator slack — pure skin-in-the-game. This sits exactly on the diagonal `π = ν` and triggers the cubic collapse from (ii).

| Operator | Pool σ | Pledge p (100 %) | Yearly bonus from A |
|---|---:|---:|---:|
| Bob | 2 M | 2 M | **14 ₳/yr** |
| Charles | 15 M | 15 M | **5 762 ₳/yr** |
| Alice | 67 M | 67 M | **513 463 ₳/yr** |

Even at the *maximum possible commitment*, Alice earns **37 595× more bonus than Bob** — because the cubic `ν³` shapes the diagonal, not the strength of the commitment signal.

Furthermore — and this is pathology (iv) made tangible — Bob is on the *wrong side* of the maximum. His optimal pledge is `π* = ν/(2(1-ν)) = 0.0153`, which is `p* ≈ 1 030 000 ₳` (about 51 % of his pool). At full self-pledge he earns 14 ₳/yr; at the optimal interior pledge he would earn ~17 ₳/yr — *2 % more bonus by withholding half his potential pledge*. The formula incentivises him to under-commit.

![The pledge bonus paradox — A(π, ν) at full self-pledge](figures/cip_levers_02_A_anatomy.png)

Panel (a) is Scenario C as a bar chart at log scale (the disparity is too large for linear axes). Panel (b) re-expresses the same disparity as a "bonus yield" — bonus per ADA of pledge per year — and overlays the passive-delegation yield (~2.3 %/yr from POL.O2.F2) the operator gives up by locking that pledge: Bob's pledge yields **0.0007 %/yr** in bonus, Charles's **0.038 %/yr**, Alice's **0.77 %/yr**. All three are below passive delegation, but Bob is by far the most penalised.

#### 2.2.3 The cubic ν³ — visualised

Combine the diagonal collapse from (ii) with the non-monotone pathology from (iv): the operator who gives the *strongest possible signal* (full self-pledge, π = ν) is paid by `ν³` — a destruction operator on sub-unit numbers.

![The cubic crush — why ν³ destroys small-pool pledge](figures/cip_levers_03_cubic_crush.png)

Panel (a) shows `ν³` (red) versus quadratic `ν²` (orange) and linear `ν` (green, "fair share"). On linear axes, the cubic curve hugs zero until `ν ≈ 0.5` and then leaps to 1 at full saturation — so anyone running a pool below half-saturation is in the flat region where pledge barely matters.

Panel (b) shows the same curves on log axes — the gap between cubic and linear is **multiplicative**, not additive. For Bob's `ν = 0.03`: the cubic gives `2.6 × 10⁻⁵`, while a linear A would give `0.030` — a **1 137× ratio**. That ratio is what the formula is destroying.

Panel (c) makes the cubic crush tangible in dollars. Bob's 2 M pool, fully self-pledged:

| A kernel | Bob's yearly bonus | In USD @ $0.25/ADA |
|---|---:|---:|
| **current  A = ν³** | 14 ₳/yr | $3.41 |
| alt. quadratic  A = ν² | 461 ₳/yr | $115 |
| alt. linear  A = ν   ("fair share") | 15 529 ₳/yr | $3 882 |
| alt. scale-free  A = 1 | 523 612 ₳/yr | $130 903 |

Compare to the **passive-delegation alternative**: if Bob delegates that 2 M instead of pledging it, he earns ~46 000 ₳/yr at 2.3 %/yr. Under the current cubic, pledging costs him ~46 000 ₳/yr in opportunity for 14 ₳/yr in bonus. *Pledging is a 3 286× loss for him.* Under a linear A, the bonus alone (15 529 ₳/yr) would be a third of his opportunity cost — pledging would still lose, but less catastrophically. Under the scale-free kernel, pledging would be net positive even for the smallest operator.

#### 2.2.4 What this means for the CIP critique

Walking through the structural anatomy and the three scenarios reveals one cumulative argument:

1. **The function is structurally awkward** before any data is plugged in (§2.2.1). Coupled inputs, non-monotonic in π for sub-half-saturation pools, and on the full self-pledge diagonal it collapses to a cubic.
2. **Mainnet today (Scenario A).** The bonus is silent for everyone. POL.O2.F1 is the predictable equilibrium of a formula with a near-zero gradient in the operating region.
3. **At CIP-0050 compliance (Scenario B).** The disparity across pool sizes becomes severe — Alice gets 1 123× more bonus than Bob for the same *relative* effort. Bob loses ~100× by complying.
4. **At maximum commitment (Scenario C).** The disparity becomes catastrophic — 37 595× — and the cubic `ν³` is the algebraic reason.

CIP-0050 and CIP-0037 modify the *enforcement* of pledge (clip σ′ if pledge is too low) but not the *pricing* of pledge inside A. After their reform, the relative bonus disparity across operator sizes remains identical; the non-monotone regime for `ν < 0.5` remains identical; the diagonal cubic collapse remains identical. They patch around A without touching it.

A reform that touched A directly — replacing `π² (1 − ν)` with a kernel that doesn't cube small pools, or reparametrising A in terms of `(ν, ρ)` so the inputs are independent — would be the most structural way to repair the pledge signal at its source. **No CIP currently in scope proposes this.** This is the deepest critique of both candidates in this folder: they accept A as given and patch around it, when A is the load-bearing piece of the pledge incentive.

This reading extends the formal critique at [diagnostic / pools-distribution §2.3.5](../../diagnostic/sub-flows/pools-distribution/mainnet-analysis/README.md#235-reader-friendly-reward-function): *"the bonus term $\lambda_{\max}A(\pi,\nu)$ is non-linear — at maximum pledge it reduces to $\lambda_{\max}\nu^3$. The cubic dependence means the bonus is structurally suppressed at low saturation levels and favours fewer, larger pools."*

### 2.3 What this implies for the CIP candidates in this folder

The two CIPs in this folder accept the V1 reward formula as given and patch around it via $\sigma'$ clipping. Three honest readings follow from §2.1 and §2.2:

- **CIP-0050 and CIP-0037 are not strictly worse than raising `a₀`.** They achieve the same intent (make pledge bind) without the smooth-but-uniformly-painful penalty that an `a₀` raise imposes on every low-pledge pool. The cliff/floor shape is *different*, not necessarily *worse*.
- **The "MPO fleet-splitting" property neither `a₀` nor an A reform would deliver as cleanly.** CIP-0050's revenue-neutral pool-splitting ($N \cdot L \cdot (P/N) = L \cdot P$) is an *algebraic identity* of its primitive that smooth levers cannot reproduce without coordination across pools. This is the strongest standalone argument for the CIP-0050 family.
- **None of the three reform vectors (`a₀`, σ' clip, A redesign) are mutually exclusive — and the deepest one is missing from the conversation.** The CIP discussion treats `σ'` clipping as the only available primitive. A revision of A itself — replacing $\pi^2(1-\nu)$ with a kernel that doesn't cube small pools — would be the most structural way to repair the pledge signal at the right end of the formula. No CIP currently in scope proposes this.

The remainder of this folder evaluates the two `σ'`-clipping candidates on their own terms. The framing above is a reading aid, not a verdict — it reframes "is CIP-0050/0037 the right reform?" as "is `σ'` clipping the right *layer* of intervention?".

## 3. Candidates

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0050** — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` | §3.2, §3.4 | [`cip-0050.md`](cip-0050.md) | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| **CIP-0037** — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve | §3.2, §3.4 | [`cip-0037.md`](cip-0037.md) | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

## 4. Composition

| Composition | Status |
| --- | --- |
| CIP-0050 ⊕ CIP-0037 (same-layer) | **Not canonical — redundant by construction.** Both instruments are the same linear-in-pledge primitive capped at `orig_sat`. Stacking them (`σ' = min(σ, orig_sat, L·p, sat₀₀₃₇(p))`) is technically well-defined but adds no expressive power over picking the stricter of the two envelopes and the floor choice |
| Stake-cap layer ⊕ fee layer (cross-layer) | **Clean** — different pipeline stages, no precedence rule required |

**Design decision — reduced to a single question.** Given the kinship in §1, picking between CIP-0050 and CIP-0037 is essentially **"floor or no floor?"**:

- **No floor (CIP-0050).** Zero-pledge pools collapse to $\sigma' = 0$ — the hardest possible pressure on the custodial-by-extraction segment (21 % of productive stake). One governance parameter $L$.
- **Floor (CIP-0037).** Zero-pledge pools keep 20 % of V1 capacity — softer landing for Sub-viable tier and below; same clip from Healthy tier up. Two effective governance parameters $(e, \ell)$.

All other properties (monotonicity in pledge, MPO fleet-split penalty on the slope, entity-level §3.4 gap for ceiling-regime pools, §3.1 small-operator viability risk) carry across one-for-one.

## 5. Interaction with `k`

Stake-cap reforms and `k` are tightly coupled:

- **CIP-0050.** $L$ is dimensionless — independent of `k`. Text explicitly argues that $L$ converts a `k` raise from a concentration risk into a decentralisation lever.
- **CIP-0037.** Both the floor ($e \cdot \text{orig\_sat}$) and the ceiling ($\text{orig\_sat}$) are functions of `k` via $\text{orig\_sat} = \text{Supply}/k$. A `k` change *directly reshapes* the entire saturation curve; joint recalibration of $(e, \ell)$ is required to preserve the intended regime boundaries.

*Important scope note.* Both CIP-0050 and CIP-0037 **change the pool-distribution part of the SL-D1 formula** (via $\sigma'$ clipping and a new saturation function respectively). The standalone `k`-lever analysis at [`../operator-delegator/k-parameter.md`](../operator-delegator/k-parameter.md) deliberately holds the formula fixed. Once either CIP-0050 or CIP-0037 is active, the standalone analysis no longer directly applies — joint evaluation with the stake-cap primitive is required.

## 6. V2 milestone interaction

Stake-cap reforms tighten the viability envelope for undercapitalised independent operators — which is why V2 sequences **fee layer before stake-cap layer**. A stake-cap reform deployed without a fee-layer instrument risks displacing delegation away from the subthreshold tail V2 §3.1 aims to protect.

## 7. Reading order

1. [`cip-0050.md`](cip-0050.md) — the primitive in its cleanest one-scalar form ($L$). Start here: every structural finding on the slope carries into CIP-0037.
2. [`cip-0037.md`](cip-0037.md) — the same primitive with an added floor and two effective governance parameters $(e, \ell)$. Read as "CIP-0050 plus floor" — the §2.1 formula walkthrough makes the kinship explicit.

## 8. References

- **Folder parent:** [`../README.md`](../README.md).
- **Cross-layer subfolder:** [`../operator-delegator/README.md`](../operator-delegator/README.md).
- **Standalone `k`-lever analysis (held-formula-fixed assumption):** [`../operator-delegator/k-parameter.md`](../operator-delegator/k-parameter.md).
- **Head-to-head:** CIP-0050-vs-0037 comparison maintained as a separate working document.
- **Synthesis:** [`../synthesis.md`](../synthesis.md).
