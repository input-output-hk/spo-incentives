---
CPS: ???
Title: CPS-10 — The Mechanism Assumes Deflation but Cannot Produce It
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

The protocol's monetary policy — a capped supply with declining emission — creates the *conditions* for deflation (scarcity), but scarcity alone does not produce appreciation. Appreciation requires demand growth exceeding supply growth, and demand for ADA is a function of the chain's utility (transaction throughput, DeFi activity, application adoption, institutional custody, speculative interest). *None of these are protocol parameters. None are addressable by the incentive mechanism.*

The mechanism is therefore **structurally dependent on an exogenous variable it cannot influence**. If the ADA price stagnates or declines in real terms, the pipeline's ADA-denominated rewards lose purchasing power — operators exit (the marginal ones first), delegators undelegate (micro-delegators have the least to lose), the staking rate declines further. Each effect reduces the security budget, which reduces the chain's attractiveness, which suppresses demand for ADA — *a reflexive loop with no internal floor*.

This CPS formally defines the **deflation-assumption gap** at the price-constraint layer.

> **Status:** Draft skeleton. The remediation space here lies primarily outside the protocol parameters and overlaps with utility-driving reforms (Leios, DeFi standards) handled by other CIP threads.

## Problem

This CPS builds on the mainnet evidence documented in [The Diagnostic §3 — The ₳ Price Constraint](../../diagnostic/README.md#3-the-price-constraint). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#331-the-mechanism-assumes-deflation-but-cannot-produce-it) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (ADA price constraint layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#331-the-mechanism-assumes-deflation-but-cannot-produce-it). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
