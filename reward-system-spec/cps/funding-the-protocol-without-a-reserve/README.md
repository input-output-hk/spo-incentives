---
CPS: ???
Title: CPS-6 — Funding the Protocol Without a Reserve
Category: Ledger
Status: Draft
Authors:
    - Nicolas Henin <nicolas.henin@iohk.io>
Proposed Solutions:
    - CIP-0163
Discussions: []
Created: 2026/03/25
License: Apache-2.0
---

## Abstract

Cardano's staking reward system has **no defined path** from reserve-funded to fee-funded sustainability. The epoch pot is funded **~99.8%** by monetary expansion from a finite reserve that has **crossed its half-life in ~5.7 years** (13.29B → 6.45B ADA). Transaction fees — the only sustainable long-term alternative — cover **~0.17%** of the pot at epoch 623, and even at full realistic network capacity would reach only **~1.3%** of the reserve expansion term. Closing the gap requires **12–16×** current throughput, implying both a capacity upgrade (Leios) and a fundamental shift in transaction demand.

The two protocol parameters that govern this layer ($\rho = 0.3\%$, $\tau = 20\%$) have **never been adjusted since Shelley** and have never been the subject of a formal governance proposal. The reserve is depleting on a known schedule, with **significant reward pressure projected at epochs 1000–1200 (~2028–2029)**, and **no protocol-level or governance-level mechanism currently manages the transition** from reserve-funded to fee-funded rewards.

A second-order complication compounds the gap: the mechanism today operates at **~44% distribution efficiency** because **~16.8B ADA (~43.6% of supply)** does not participate in delegation. The undistributed residual returns to reserve, *extending its life by **4.61B ADA** as a side-effect of low participation rather than a design feature*. Any reform that increases participation will improve distribution efficiency *and* accelerate depletion — a tension the current design does not acknowledge.

This CPS formally defines the **reward sustainability problem** at the epoch-budget layer of the reward pipeline. It is grounded in the mainnet evidence documented in the dedicated [Treasury & Pool Pots Distribution — Mainnet Analysis](../../diagnostic/sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) sub-report and invites the community to propose solutions through the CIP process.

## Problem

This CPS builds upon the mainnet evidence documented in the dedicated [sub-report: Treasury & Pool Pots Distribution — Mainnet Analysis](../../diagnostic/sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md), which provides the full empirical analysis, data, figures, and reproduction scripts behind the findings summarised here. All observations below reference the sub-report's observation framework (O1–O4) and their supporting findings (F1.x–F4.x).

### Context

Every epoch, the Cardano protocol assembles a reward pot from three on-chain sources — monetary expansion from the reserve, transaction fees, and non-refundable deposit flows — then splits it between the treasury (20%) and the pools pot (80%). The pools pot is the total budget that downstream stages of the reward pipeline (pool-level distribution, operator/delegator split) divide across individual participants.

The design was specified in *SL-D1* (Kant, Brünjes & Coutts, 2019) and has been operational since the Shelley hard fork on 2020/07/29. The mechanism's governing parameters ($\rho$, $\tau$) have never been modified.

### Observations

The [sub-report](../../diagnostic/sub-flows/treasury-and-pool-pots-distribution/mainnet-analysis/README.md) documents four observations from mainnet data (epochs 208–623) at this pipeline stage:

**O1 — The epoch pot is a single-source budget.** Monetary expansion provides ~99.83% of the pot. Transaction fees contribute ~0.17% (epoch 623); deposit flows are unmeasurable at epoch granularity. Block production is reliable (η ≈ 0.977) — the pot assembles as designed. The bottleneck is not operational; it is structural: the revenue mix is almost entirely dependent on a depleting resource.

**O2 — The reserve has crossed its half-life.** The reserve has gone from 13.29B to 6.45B ADA — half depleted in ~5.7 years. The decline is exponential: each epoch draws 0.3% of whatever remains, so the absolute draw shrinks over time. At current parameters and participation levels, the reserve reaches ~2B ADA around epochs 1000–1200 (~2028–2029), at which point per-epoch rewards drop significantly. Full depletion is projected around epoch 3500 (~2040s).

**O3 — The reward mechanism operates at ~44% of its potential.** Only ~6.78M of ~15.39M ADA allocated to the pools pot actually reaches operators and delegators each epoch — the rest returns to the reserve. Cumulatively, 4.61B ADA (~71% of the current reserve stock) exists because rewards were not fully distributed. The root cause is that ~16.8B ADA (~43.6% of circulating supply) does not participate in delegation. This creates a paradox: the return-to-reserve mechanism slows depletion, but it is a side effect of low participation, not a design feature. Greater adoption — normally desirable — would remove this safety margin and accelerate reserve consumption.

**O4 — Reward parameters have never been adjusted.** The monetary expansion rate ($\rho = 0.3\%$) and the treasury rate ($\tau = 20\%$) are unchanged since Shelley. The decentralisation parameter $d$ was gradually reduced to 0 and $k$ was raised from 150 to 500, but the reward-level parameters remain at their day-one values. Neither has been the subject of a formal governance proposal.

### The problem

These observations are individually informative, but their significance emerges **when read together**. Each constrains what the system can do; the combination reveals what it **cannot** do.

The epoch pot depends almost entirely on a **depleting resource** (O1). That resource is **already half-spent** (O2). The only alternative funding source — transaction fees — covers **~0.17%** of the pot today (epoch 623), and even at full realistic capacity would reach only **~1.3%** (O1).

Closing this gap requires **12–16× today's throughput**, implying both a capacity upgrade (Leios) and a structural increase in transaction demand — **neither of which is on a defined timeline**. Meanwhile, the parameters governing the draw have **never been reviewed** (O4), and **no governance process exists to do so**.

**The reward system has no viable path from reserve-funded to fee-funded sustainability.** The reserve is depleting on a known schedule, the only alternative revenue source is **orders of magnitude too small**, and the parameters governing the transition have never been subject to governance.

*This is not a failure of any individual parameter — it is a design gap at the epoch-budget layer.*

The ~44% distribution efficiency (O3) adds a further complication: activating inactive ADA would **increase distribution efficiency but accelerate reserve consumption**. Any sustainability strategy must account for this tension.

## Use Cases

**Stake pool operator evaluating long-term viability.** An operator running a pool today earns rewards funded ~99.8% by monetary expansion. As the reserve depletes, per-epoch rewards will decline — gradually at first, then significantly around epochs 1000–1200 (~2028–2029). An operator planning infrastructure investments, pledge commitments, or business models over a multi-year horizon has no visibility into how rewards will transition, whether parameters will be adjusted, or what fee revenue trajectory to expect. Without a defined transition path, rational operators must discount future reward expectations heavily, which undermines the *participation constraint* the mechanism depends on.

**Delegator assessing long-term yield.** A delegator choosing between staking and alternative uses of their ADA needs to assess the yield trajectory. Current yields (~2–3% annual) are sustained by reserve expansion. As the reserve shrinks, yields will decline unless fee revenue grows proportionally — a growth that requires 12–16× current throughput. A delegator cannot currently determine when yields will decline materially, or whether governance will intervene. This uncertainty affects delegation decisions and, in aggregate, participation levels.

**Governance actor considering parameter adjustments.** An actor in the Voltaire governance framework considering proposals related to $\rho$ or $\tau$ has no formal problem definition to scope their analysis against. What is the target? What constraints must be respected? What is the acceptable reward floor? Without a CPS defining these boundaries, governance proposals risk being ad hoc rather than systematic.

**DApp developer assessing fee economics.** A developer building applications on Cardano contributes to the fee revenue that will eventually need to sustain the staking game. Today, their contribution is negligible relative to expansion. Understanding when and how fee revenue becomes critical — and what throughput levels are needed — is relevant to application design, pricing strategy, and ecosystem sustainability planning.

## Goals

The following goals are ranked by importance. A solution to this problem should address the highest-ranked goals first; lower-ranked goals are desirable but may involve trade-offs.

1. **Define a credible transition path** from reserve-funded to fee-funded rewards. This path should be robust to uncertainty in fee revenue growth and should not depend on a single lever (e.g., Leios alone).

2. **Maintain the participation constraint** for operators and delegators throughout the transition. Reward levels must remain sufficient to keep staking *individually rational* — if rewards drop below opportunity cost, rational actors exit, which weakens consensus security.

3. **Establish governance processes** for periodic review of $\rho$ and $\tau$. These parameters have been static since Shelley. A solution should define when, how, and against what criteria they should be reviewed — without prescribing specific values (that is the role of CIPs responding to this CPS).

4. **Account for the participation paradox** (O3). Activating inactive ADA increases distribution efficiency but accelerates reserve depletion. A solution should model this interaction rather than treating participation growth as unambiguously positive.

5. **Provide visibility** to ecosystem participants. Operators, delegators, and governance actors need legible information about the reward trajectory, parameter review schedule, and transition milestones to make informed decisions.

**Non-goals:**

- Prescribing specific values for $\rho$ or $\tau$ — that is the role of CIPs proposed as solutions to this CPS.
- Modifying the pool-level reward curve or the operator/delegator split — those are downstream problems addressed by separate CPS/CIP pairs at the §1.2 and §1.3 layers.
- Redesigning the fee mechanism itself (e.g., congestion pricing, tiered fees) — though such changes may be proposed as CIPs responding to this CPS.

## Open Questions

These questions are intended to save time for potential solution authors. Any CIP proposed against this CPS should consider them in its design.

- **What is the minimum viable reward level?** Below what per-epoch reward does the participation constraint break — i.e., at what point does rational operator exit begin? This threshold defines the hard deadline for the transition.

- **How should $\rho$ and $\tau$ be adjusted as the reserve/fee balance shifts?** Should adjustments be discrete (governance votes at defined milestones) or continuous (algorithmic, responsive to on-chain metrics)? What are the trade-offs of each approach?

- **What is the interaction between Leios and fee revenue growth?** Leios increases throughput capacity, but capacity is not demand. What transaction demand growth assumptions are needed for fee revenue to meaningfully contribute, and over what timeline?

- **Should $\tau$ adapt dynamically to fee revenue levels?** If fee revenue grows, should a larger share go to the pools pot (to sustain staking) or to the treasury (to fund ecosystem development)? The current fixed 80/20 split may not be optimal across all revenue regimes.

- **What role does the ~44% non-participating stake play?** If inactive ADA enters delegation — through governance incentives, exchange staking, or new products — the return-to-reserve buffer shrinks. Should a solution *encourage* participation (improving efficiency) or *account for it as a risk* (accelerating depletion)? Can it do both? CIP-0163 proposes one approach: tightening eligibility (proof-of-life) while distributing the full pot — but its interaction with $\rho$ requires careful modelling.

- **What is the interaction between full-pot distribution and reserve depletion?** CIP-0163 proposes eliminating the return-to-reserve residual, which currently returns ~10.3M ADA/epoch to the reserve (O3). This would accelerate nominal depletion unless $\rho$ is reduced to compensate. What is the net effect on reserve lifetime under different $\rho$ scenarios? How does the proof-of-life mechanism (removing lost/inactive stake from the reward base) offset the faster draw?

- **How does lost stake interact with reward sustainability?** CPS-0022 estimates that a significant and growing fraction of delegated ADA is permanently inaccessible. Rewards flowing to lost stake are effectively removed from circulation forever. Any solution to the sustainability problem must account for this drain — either by excluding lost stake from the reward base (as CIP-0163 proposes) or by modelling it as a permanent leakage factor in reserve projections.

- **How do downstream CIPs interact with reward sustainability?** CIP-0050, CIP-0037, CIP-0023, and CIP-0082 all modify how the pools pot is distributed, not its size. But by changing distribution efficiency and operator/delegator incentives, they may affect participation levels, which in turn affect the return-to-reserve rate (O3). Are these interactions material?

- **What is the governance readiness for parameter changes?** The Voltaire governance framework (CIP-1694) enables parameter changes, but $\rho$ and $\tau$ have never been touched. Is the community equipped to evaluate proposals affecting these parameters? What analytical tools, dashboards, or decision frameworks would be needed? CPS-0007 identified governance readiness as a systemic concern — that concern applies directly here.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
