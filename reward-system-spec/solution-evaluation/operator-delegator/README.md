# Operator / Delegator — Fee layer

> **Status:** Active 2026/04/23. Subfolder of [`../README.md`](../README.md). Candidates that act on the fee layer of the Cardano reward pipeline. Sources in §5.

## Executive summary

- **Scope.** Operator / member split *after* the per-pool allocation — the reward envelope produced by the SL-D1 formula is untouched; what changes is how it is divided.

- **What the CIPs in this folder correctly identify.** CIP-0023 and CIP-0082 target what our mainnet diagnostic identifies as the **priority-1 problem for a V2 reform: the viability of small operators**. The diagnostic shows 73 % of productive pools sit below the ~3 M ₳ viability line, and no single-pool operator in the retail market earns a competitive wage (OPE.O6.F4, POL.O3.F1). Both CIPs correctly flag this population as the one a reform must address.

- **What they get only partly right — they address ROS attractiveness, not profitability structure.** Both CIPs act on fee-layer pricing (flat-fee reduction, margin / rate floors) to make small pools more *ROS-attractive* to delegators. But neither revises the reward-distribution formula itself. For a hollow pool below saturation, pool reward still scales linearly with pool stake ($\hat f' = R \lambda_{\text{size}} \sigma_{\text{rel}}$). Small-operator **absolute profitability** therefore changes only if delegation actually migrates from large pools to small ones — the fee reform by itself does not raise what a small-pool operator earns at constant size.

- **The redistribution bet is unevidenced.** Both CIPs implicitly depend on that migration. The diagnostic does not support it empirically: delegation is not sticky, but not clearly yield-following either — the observed flow tracks brand, wallet integration, and visibility (OPE.O7.F1). There is no mainnet signal that the migration will occur at the scale the CIPs need.

- **If the migration does not happen, the reforms invert their intent.** Without the redistribution, fee-layer tightening produces the opposite outcome of what the CIPs target:
  - **Fragilises the small-operator population** — Sub-viable operator revenue cut **–9×** under the Margin swap alternative (cip-0082.md §3.1.F2), while remaining below the ~28 600 ₳/yr cost floor (OPE.O6.F4).
  - **Amplifies n-MPO concentration** — the transfer compounds with fleet size: **+200 K ₳/yr** per 11+ pool MPO entity vs **–11 K ₳/yr** per sub-viable single-pool operator (cip-0082.md §3.1.F3). More pools per entity = larger capture of the reform's upside.
  - **Amplifies profit disparity** — proportional margin rules scale operator take linearly with pool reward, so large pools capture the largest absolute transfer by construction.

- **A principled separation — abstract viability from pricing.** `minPoolCost` (flat fee / fixed cost) and `minPoolRate` / `poolRate` (rate / commission) are **pricing tools**. Operators should remain free to set them to compete on an open market; the pricing signal is what delegators can read to distinguish between operators. The **viability floor** (the minimum income a productive operator needs to cover operational cost) is a different function and belongs on a different layer. Conflating them — as CIP-0023 and CIP-0082 do by using pricing floors to bolt viability into the fee structure — forces every operator into the same pricing regime whether they need the floor or not, and weakens the pricing signal. A V2 design should:
  - Keep pricing tools (flat fee + rate) **fully flexible** as competitive levers.
  - Engineer the viability floor elsewhere — on the reward-distribution layer (pre-split), not on the fee-split layer (post-split). Stake-cap instruments ([`../pools-distribution/`](../pools-distribution/README.md)) reshape the reward-eligible stake before the formula applies; a dedicated viability primitive is an open design question.

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
| **`k` lever** — target-pool count (standalone) | `stakePoolTargetNum` | §3.1, §3.4 | [`k-parameter.md`](k-parameter.md) | Protocol parameter — no dedicated CIP; filed here as the standalone analysis holds the pool-distribution formula fixed and affects the operator/member split via $P_{\max} = R/k$ |

## 3. Composition

| Composition | Status |
| --- | --- |
| CIP-0023 ⊕ CIP-0082 (same-layer) | **Not canonical** — both rewrite the per-pool fee split. Pick one primitive (margin floor or rate floor); union is incoherent |
| Fee layer ⊕ stake-cap layer (cross-layer) | **Clean** — layers act on different stages of the reward pipeline. No precedence rule required |

**Design decision.** Is the right primitive a *margin* floor (CIP-0023) or a *rate* floor (CIP-0082 stage 2)? Does the absolute floor (`minPoolCost`) survive the reform? These are analysed in both per-CIP files.

## 4. Reading order

1. [`cip-0023.md`](cip-0023.md) — narrower instrument, single parameter, clearer historical lineage.
2. [`cip-0082.md`](cip-0082.md) — broader 4-stage reform that subsumes and extends the CIP-0023 intent.
3. [`k-parameter.md`](k-parameter.md) — the standalone `k`-lever analysis; companion to CIP-0082.S3 (stages 3–4).

## 5. References

- **Folder parent:** [`../README.md`](../README.md).
- **Cross-layer subfolder:** [`../pools-distribution/README.md`](../pools-distribution/README.md).
- **Transversal lever in this folder:** [`k-parameter.md`](k-parameter.md) — standalone `k`-raise analysis; see also companion §2 above.
- **Synthesis:** [`../synthesis.md`](../synthesis.md).
