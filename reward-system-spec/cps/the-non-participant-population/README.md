---
CPS: ???
Title: CPS-7 — The Non-Participant Population
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

**14.36B ADA (39.8%)** of circulating supply sits outside the delegation system, and the staking rate has declined from **71% (epoch ~260) to 59% (epoch 623)** — driven by supply growth outpacing stake inflows, not by delegators leaving. The non-participant decomposition reveals an asymmetry: only **134.6M ADA (0.37% of circulation)** belongs to accounts with a registered stake credential that have simply not delegated — the *addressable* non-participant pool. The remaining **14.2B ADA** sits in addresses with **no stake credential at all** — enterprise-format exchange custody, DeFi-locked Plutus contracts without staking parts, Byron-era legacy outputs, and base addresses whose staking key was never registered.

*Incentive changes cannot reach the bulk of non-participation*; only structural protocol changes (enabling enterprise-address staking, mandating staking-capable script addresses in DeFi standards, delegation-by-default for new base addresses) could move it. The implication is sharp: any reform that improves distribution efficiency by activating non-participant ADA simultaneously accelerates reserve depletion (see [Funding the Protocol Without a Reserve](../funding-the-protocol-without-a-reserve/README.md)) — the two problems are coupled.

This CPS formally defines the **structural non-participation** problem at the population-substrate layer.

> **Status:** Draft skeleton. The full empirical analysis is referenced in the diagnostic; this CPS will be elaborated as the dedicated non-participant analysis matures.

## Problem

This CPS builds on the mainnet evidence documented in [The Staking Census — Mainnet Analysis](../../diagnostic/sub-flows/census/mainnet-analysis/README.md). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#2133-the-non-participant-population) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (staking populations layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#2133-the-non-participant-population). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
