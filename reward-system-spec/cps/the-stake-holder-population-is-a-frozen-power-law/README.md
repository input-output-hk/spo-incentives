---
CPS: ???
Title: CPS-5 — The Stake-Holder Population Is a Frozen Power Law
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

The intended design assumes that delegators form a competitive demand side — mobile capital that disciplines operators through reallocation. *The on-chain population is a power law that crystallised early and has not moved since.* **1,000 delegators (0.07% of the base) control 57% of staked ADA**; the Gini coefficient is **0.976**. The median delegator holds **32 ADA**; the mean is **16,055 ADA** — a **500× gap**. This concentration profile locked in by **epoch 300**: a subsequent 9× growth in delegator count produced no measurable change in the top-1% share.

The behavioural evidence completes the picture: switching scales with stake size (whales average 3.06 lifetime switches; micro-delegators 0.67), but this mobility does *not* produce competitive pressure because it is **not yield-driven** — half of all switches produce zero yield change, take direction is symmetric, and the only asymmetric signal is pool size. *The population that could discipline operators — whales, holding 14.1B ADA — moves, but not in response to the signals the mechanism produces.*

This CPS formally defines the **frozen-distribution / yield-blind delegation** problem at the population-substrate layer.

## Problem

This CPS builds on the mainnet evidence documented in [The Staking Census — Mainnet Analysis](../../diagnostic/sub-flows/census/mainnet-analysis/README.md). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#2132-the-stake-holder-population-is-a-frozen-power-law) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (staking populations layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#2132-the-stake-holder-population-is-a-frozen-power-law). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
