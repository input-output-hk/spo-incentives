---
CPS: ???
Title: CPS-3 — Restore a Competitive Delegator Yield
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

The mechanism no longer produces a staking return that competes — with risk-free alternatives, with other PoS chains, or even with itself from two years ago. The delegator yield has **fallen from 5.3% to 2.0% in 413 epochs (5.5 years)**, tracking reserve depletion with $R^2 = 0.99$. At 2.0%, Cardano sits **below the USD risk-free rate (4.3%)** and at the bottom of the PoS landscape.

The return signal is already too weak to drive delegation: net return converges to **1.95–2.34%** across the entire retail market regardless of effective price, operator type, or pool size — a **0.39pp spread** delegators cannot meaningfully act on. As the epoch pot continues to shrink, this spread compresses proportionally; at **1.0% base yield (~3.5 years)**, the same relative dispersion produces ~0.20pp, indistinguishable from block-production noise. *The incentive mechanism's core assumption — that delegators can differentiate pools by return and thereby discipline operator pricing — fails in the current yield regime and will fail more completely in every subsequent one.*

This CPS formally defines the **delegator-yield collapse** problem at the intra-pool reward-split layer.

## Problem

This CPS builds on the mainnet evidence documented in [The Operator's Cut — Mainnet Analysis](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#1332-restore-a-competitive-delegator-yield) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (operator/delegator distribution layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#1332-restore-a-competitive-delegator-yield). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
