---
CPS: ???
Title: CPS-11 — The Three Constraints Pull in Different Directions
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

The reward pipeline's long-term viability requires three conditions to hold simultaneously: the **fee input must grow**, the **submitter population must expand**, and the **ADA price must be deflationary in real terms**. These three constraints are **not independent** — they interact, and in some configurations they contradict.

A rising ADA price increases the fiat cost of transacting (suppresses fee volume); a falling ADA price makes operator and delegator rewards insufficient; a stable ADA price satisfies neither. The mechanism design does not acknowledge this trilemma — the reward curve, the fee formula, and the reserve schedule were each designed in isolation. *The ADA price is the hidden variable that connects all three, and the mechanism offers no instrument to manage the tension between them.*

This CPS formally defines the **price-fee-supply trilemma** at the boundary-conditions layer. It sits intentionally last in the diagnostic because it is the constraint the protocol has the *least* ability to address directly — but any solution at the lower layers must operate within these boundary conditions.

> **Status:** Draft skeleton. This CPS may end up as a *meta-CPS* that frames how the lower-layer CPSs interact rather than a freestanding problem statement.

## Problem

This CPS builds on the mainnet evidence documented in [The Diagnostic §3 — The ₳ Price Constraint](../../diagnostic/README.md#3-the-price-constraint). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#332-the-three-constraints-pull-in-different-directions) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (ADA price constraint layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#332-the-three-constraints-pull-in-different-directions). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
