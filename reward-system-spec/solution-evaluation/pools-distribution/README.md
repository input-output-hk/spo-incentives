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

## 1. Stake-cap formulas

Both candidates reshape $\sigma'$ (reward-eligible pool stake) as a **linear function of pledge**, with the V1 ceiling $\text{orig\_sat} = 1/k$ as hard upper bound. They differ only on what happens below the slope:

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

## 2. Candidates

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0050** — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` | §3.2, §3.4 | [`cip-0050.md`](cip-0050.md) | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| **CIP-0037** — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve | §3.2, §3.4 | [`cip-0037.md`](cip-0037.md) | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

## 3. Composition

| Composition | Status |
| --- | --- |
| CIP-0050 ⊕ CIP-0037 (same-layer) | **Not canonical — redundant by construction.** Both instruments are the same linear-in-pledge primitive capped at `orig_sat`. Stacking them (`σ' = min(σ, orig_sat, L·p, sat₀₀₃₇(p))`) is technically well-defined but adds no expressive power over picking the stricter of the two envelopes and the floor choice |
| Stake-cap layer ⊕ fee layer (cross-layer) | **Clean** — different pipeline stages, no precedence rule required |

**Design decision — reduced to a single question.** Given the kinship in §1, picking between CIP-0050 and CIP-0037 is essentially **"floor or no floor?"**:

- **No floor (CIP-0050).** Zero-pledge pools collapse to $\sigma' = 0$ — the hardest possible pressure on the custodial-by-extraction segment (21 % of productive stake). One governance parameter $L$.
- **Floor (CIP-0037).** Zero-pledge pools keep 20 % of V1 capacity — softer landing for Sub-viable tier and below; same clip from Healthy tier up. Two effective governance parameters $(e, \ell)$.

All other properties (monotonicity in pledge, MPO fleet-split penalty on the slope, entity-level §3.4 gap for ceiling-regime pools, §3.1 small-operator viability risk) carry across one-for-one.

## 4. Interaction with `k`

Stake-cap reforms and `k` are tightly coupled:

- **CIP-0050.** $L$ is dimensionless — independent of `k`. Text explicitly argues that $L$ converts a `k` raise from a concentration risk into a decentralisation lever.
- **CIP-0037.** Both the floor ($e \cdot \text{orig\_sat}$) and the ceiling ($\text{orig\_sat}$) are functions of `k` via $\text{orig\_sat} = \text{Supply}/k$. A `k` change *directly reshapes* the entire saturation curve; joint recalibration of $(e, \ell)$ is required to preserve the intended regime boundaries.

*Important scope note.* Both CIP-0050 and CIP-0037 **change the pool-distribution part of the SL-D1 formula** (via $\sigma'$ clipping and a new saturation function respectively). The standalone `k`-lever analysis at [`../operator-delegator/k-parameter.md`](../operator-delegator/k-parameter.md) deliberately holds the formula fixed. Once either CIP-0050 or CIP-0037 is active, the standalone analysis no longer directly applies — joint evaluation with the stake-cap primitive is required.

## 5. V2 milestone interaction

Stake-cap reforms tighten the viability envelope for undercapitalised independent operators — which is why V2 sequences **fee layer before stake-cap layer**. A stake-cap reform deployed without a fee-layer instrument risks displacing delegation away from the subthreshold tail V2 §3.1 aims to protect.

## 6. Reading order

1. [`cip-0050.md`](cip-0050.md) — the primitive in its cleanest one-scalar form ($L$). Start here: every structural finding on the slope carries into CIP-0037.
2. [`cip-0037.md`](cip-0037.md) — the same primitive with an added floor and two effective governance parameters $(e, \ell)$. Read as "CIP-0050 plus floor" — the §2.1 formula walkthrough makes the kinship explicit.

## 7. References

- **Folder parent:** [`../README.md`](../README.md).
- **Cross-layer subfolder:** [`../operator-delegator/README.md`](../operator-delegator/README.md).
- **Standalone `k`-lever analysis (held-formula-fixed assumption):** [`../operator-delegator/k-parameter.md`](../operator-delegator/k-parameter.md).
- **Head-to-head:** CIP-0050-vs-0037 comparison maintained as a separate working document.
- **Synthesis:** [`../synthesis.md`](../synthesis.md).
