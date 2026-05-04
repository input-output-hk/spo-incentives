---
CPS: ???
Title: CPS-4 — The Operator Population Is Highly Concentrated and Stable
Category: Ledger
Status: Draft
Authors:
    - Nicolas Henin <nicolas.henin@iohk.io>
Proposed Solutions: []
Discussions: []
Created: 2026/04/30
License: Apache-2.0
---

## Abstract

The intended design assumes a competitive field of $k$ single-pool operators converging toward a balanced equilibrium. *The on-chain population has already converged — toward concentration, not competition.* **83 attributed entities control 76.7% of productive stake through 449 productive pools.** The productive set has been in **quasi-equilibrium at ~950 pools since epoch 300**, with **1.7% turnover per epoch** — replacement, not expansion. **12 entities operating 11+ pools each control 40.4% of productive stake.**

Three structurally distinct sub-populations coexist within this concentrated landscape, and the dominant ones are *structurally insensitive* to the pledge signal the mechanism relies on: custodial operators (CEX + IVaaS, 7.40B ADA) cannot pledge by architectural constraint; community and opaque MPO fleets have *chosen* not to pledge despite the capacity (rational response to the pledge-value inversion); only the contracting single-pool operator population (477 pools, 5.28B ADA) bears the full cost of the fee structure. The operator population is not a single competitive field — *it is a segmented and highly concentrated market.*

This CPS formally defines the **operator-concentration problem** at the population-substrate layer.

## Problem

This CPS builds on the mainnet evidence documented in [The Staking Census — Mainnet Analysis](../../diagnostic/sub-flows/census/mainnet-analysis/README.md). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#2131-the-operator-population-is-highly-concentrated-and-stable) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (staking populations layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#2131-the-operator-population-is-highly-concentrated-and-stable). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

### The problem

> *To be elaborated during CPS triage. Some of these draft CPSs may be merged with adjacent ones, promoted with their own dedicated sub-report, or retired if the gap is judged too narrow to warrant a standalone CPS.*

## Use Cases

> *To be filled. Typical structure: one user persona per use case (operator, delegator, governance actor, dApp developer), each describing what they cannot currently do because of the gap.*

## Goals

> *To be filled. Ranked list of properties any candidate solution must satisfy, with non-goals clearly stated.*

## Open Questions

> *To be filled. Questions that any CIP authoring against this CPS should consider — interaction with adjacent layers, calibration uncertainty, governance prerequisites, etc.*

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
