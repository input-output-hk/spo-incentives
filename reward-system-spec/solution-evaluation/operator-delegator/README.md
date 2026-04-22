# Operator / Delegator — Fee layer

> **Status:** Active 2026/04/22. Subfolder of [`../README.md`](../README.md). Candidates that act on the fee layer of the Cardano reward pipeline. Sources in §5.

## TL;DR

- **Scope.** Operator/member split *after* the per-pool allocation — the reward envelope produced by the SL-D1 formula is untouched; what changes is how it is divided.
- **Primary V2 targets.** §3.1 operator viability and §3.3 competitive delegator yield. No effect on §3.2 / §3.4 — those need stake-cap reforms ([`../pools-distribution/`](../pools-distribution/README.md)).
- **Sequencing.** Fee-first, consistent with V2 dependency chain — viability before concentration-reduction.
- **Design decision on this layer.** Margin floor (CIP-0023) vs rate floor (CIP-0082 stage 2) — same-layer pairing requires explicit precedence rule, not a union.

## 1. Fee-layer parameters

| Parameter | Type | Current role |
| --- | --- | --- |
| `minPoolCost` | Absolute ADA fixed-fee floor | Deducted from per-pool allocation before the margin split |
| `minPoolMargin` (CIP-0023) | Relative % margin floor | Applied after `minPoolCost` |
| `minPoolRate` (CIP-0082 stage 2) | Proportional rate floor | **Replaces** `minPoolCost` under the 4-stage reform |

## 2. Candidates

| Candidate | Instrument | V2 primary | Evaluation | Source |
| --- | --- | --- | --- | --- |
| **CIP-0023** — Fair Min Fees | `minPoolMargin` floor | §3.1, §3.3 | [`cip-0023.md`](cip-0023.md) | [CIP-0023](https://cips.cardano.org/cip/CIP-0023) · PR [#66](https://github.com/cardano-foundation/CIPs/pull/66) |
| **CIP-0082** — Improved Rewards Scheme Parameters | 4-stage: `minPoolCost` → `minPoolRate` + `k` increases | §3.1, §3.3, §3.4 | [`cip-0082.md`](cip-0082.md) | [CIP-0082](https://cips.cardano.org/cip/CIP-0082) |

## 3. Composition

| Composition | Status |
| --- | --- |
| CIP-0023 ⊕ CIP-0082 (same-layer) | **Not canonical** — both rewrite the per-pool fee split. Pick one primitive (margin floor or rate floor); union is incoherent |
| Fee layer ⊕ stake-cap layer (cross-layer) | **Clean** — layers act on different stages of the reward pipeline. No precedence rule required |

**Design decision.** Is the right primitive a *margin* floor (CIP-0023) or a *rate* floor (CIP-0082 stage 2)? Does the absolute floor (`minPoolCost`) survive the reform? These are analysed in both per-CIP files.

## 4. Reading order

1. [`cip-0023.md`](cip-0023.md) — narrower instrument, single parameter, clearer historical lineage.
2. [`cip-0082.md`](cip-0082.md) — broader 4-stage reform that subsumes and extends the CIP-0023 intent.

## 5. References

- **Folder parent:** [`../README.md`](../README.md).
- **Cross-layer subfolder:** [`../pools-distribution/README.md`](../pools-distribution/README.md).
- **Transversal parameter:** [`../k-parameter.md`](../k-parameter.md).
- **Synthesis:** [`../synthesis.md`](../synthesis.md).
