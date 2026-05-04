---
CPS: ???
Title: CPS-9 — The Fee-Generating Population Must Expand for the Pipeline to Survive
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

The reserve is finite and depleting on a known schedule. When it approaches exhaustion, the epoch pot contracts to whatever fees and deposits provide — *a pot roughly 500× smaller than the one the staking population is calibrated to expect*. For the pipeline to remain viable, the submitter population must grow along three dimensions simultaneously: **volume** (transactions per epoch), **breadth** (distinct fee-paying actors), and **intensity** (fee per transaction).

The current trajectory satisfies only the third condition (for script transactions). Volume is flat, breadth is declining, and the mechanism design addresses none of the three: there is no incentive for new actors to submit transactions, no reward for the addresses that generate fee revenue, and no penalty for the concentration of fees in a shrinking set of addresses. *The pipeline's future funding source is treated as exogenous — an assumption that the population data contradicts.* The constituency mismatch (CEN.O9) compounds the problem: roughly **30%** of fee revenue already comes from addresses that cannot delegate.

This CPS formally defines the **fee-population growth requirement** at the transaction-submitter layer, and frames it as a complement (not a substitute) to the fee-input insufficiency CPS.

## Problem

This CPS builds on the mainnet evidence documented in [The Staking Census — Mainnet Analysis §6](../../diagnostic/sub-flows/census/mainnet-analysis/README.md#6-transaction-submitters). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#2232-the-fee-generating-population-must-expand-for-the-pipeline-to-survive) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (transaction submitters layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#2232-the-fee-generating-population-must-expand-for-the-pipeline-to-survive). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
