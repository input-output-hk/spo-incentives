# Pools distribution — Stake-cap layer

> **Status:** Active 2026/04/22. Subfolder of [`../README.md`](../README.md). Candidates that act on the stake-cap layer of the Cardano reward pipeline. Sources in §5.

## Executive summary

- **Scope.** Reward-eligible pool stake $\sigma'$ used inside the SL-D1 reward curve. The fee split that follows is untouched ([`../operator-delegator/`](../operator-delegator/README.md)); what changes is the allocation envelope itself.
- **Primary V2 targets.** §3.2 (restore pledge as signal) and §3.4 (concentration reduction via entity-level Sybil cost).
- **V1 baseline.** Static cap $\sigma' = \min(\sigma, 1/k)$. Stake-cap CIPs make the cap pledge-linked.
- **Design decision on this layer.** Hard cap (CIP-0050) vs smooth curve (CIP-0037) — same-layer pairing requires explicit precedence rule.

## 1. Stake-cap formulas

| Mechanism | Formula | Parameters |
| --- | --- | --- |
| V1 baseline | $\sigma' = \min(\sigma,\ 1/k)$ | $k$ only |
| CIP-0050 — pledge-leverage cap | $\sigma' = \min(\sigma,\ 1/k,\ L\cdot p)$ | $L$ (one scalar) |
| CIP-0037 — dynamic saturation | $\text{sat}(p) = \text{orig\_sat} \cdot \max\!\bigl(e,\ \min(1/k,\ \tfrac{p}{\text{orig\_sat}}\cdot\ell)\bigr)$ | $(e, \ell, p_{100\%})$ — three anchors |

## 2. Candidates

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0050** — Pledge Leverage-Based Staking Rewards | Pledge-leverage cap `L` | §3.2, §3.4 | [`cip-0050.md`](cip-0050.md) | [CIP-0050](https://cips.cardano.org/cip/CIP-0050) · PR [#242](https://github.com/cardano-foundation/CIPs/pull/242), [#1042](https://github.com/cardano-foundation/CIPs/pull/1042) |
| **CIP-0037** — Dynamic Saturation Based on Pledge | Pledge-linked saturation curve | §3.2, §3.4 | [`cip-0037.md`](cip-0037.md) | [CIP-0037](https://cips.cardano.org/cip/CIP-0037) · PR [#163](https://github.com/cardano-foundation/CIPs/pull/163) |

## 3. Composition

| Composition | Status |
| --- | --- |
| CIP-0050 ⊕ CIP-0037 (same-layer) | **Not canonical** — both rewrite $\sigma'$. Technical $\min(\sigma, \sigma^{\text{dyn,sat}}(p), L\cdot p)$ is well-defined but requires explicit governance adoption |
| Stake-cap layer ⊕ fee layer (cross-layer) | **Clean** — different pipeline stages, no precedence rule required |

**Design decision.** Hard cap (CIP-0050 step function at $L\cdot p$) or smooth curve (CIP-0037 monotone function of pledge)? Both make pledge load-bearing again; they differ on how sharply they penalise under-pledged delegation. A head-to-head comparison is maintained as a separate working document.

## 4. Interaction with `k`

Stake-cap reforms and `k` are tightly coupled:

- **CIP-0050.** Text explicitly argues that $L$ converts a `k` raise from a concentration risk into a decentralisation lever.
- **CIP-0037.** Uses `orig_sat = supply / k` as reference scale. A `k` change *directly reshapes* the saturation curve; joint recalibration of $(e, \ell, p_{100\%})$ required.

Analysis: [`../k-parameter.md`](../k-parameter.md) §5.3–5.4.

## 5. V2 milestone interaction

Stake-cap reforms tighten the viability envelope for undercapitalised independent operators — which is why V2 sequences **fee layer before stake-cap layer**. A stake-cap reform deployed without a fee-layer instrument risks displacing delegation away from the subthreshold tail V2 §3.1 aims to protect.

## 6. Reading order

1. [`cip-0050.md`](cip-0050.md) — simpler primitive (single cap), well-studied simulation base.
2. [`cip-0037.md`](cip-0037.md) — richer parametrisation (three anchors), more calibration degrees of freedom.

## 7. References

- **Folder parent:** [`../README.md`](../README.md).
- **Cross-layer subfolder:** [`../operator-delegator/README.md`](../operator-delegator/README.md).
- **Transversal parameter:** [`../k-parameter.md`](../k-parameter.md).
- **Head-to-head:** CIP-0050-vs-0037 comparison maintained as a separate working document.
- **Synthesis:** [`../synthesis.md`](../synthesis.md).
