---
CPS: ???
Title: CPS-1 — Guarantee Operator Viability Across the Productive Population
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

The reward mechanism **fails to provide a viable economic proposition** to its smallest participants. **No single-pool operator in the retail market earns a competitive wage**: the median single-pool revenue is **~25,000 ₳/yr** (≈ $6,250 at $0.25/ADA), enough to cover infrastructure but not the 5–15 hrs/month of skilled work required to maintain a node. Competitive compensation begins only at the **2-pool MPO tier** (~68,700 ₳/yr).

The cause is **structural, not competitive**: the flat fee follows a **$1/\sigma$ hyperbola** (47.5% of pool reward at the sub-reliable tier, 1.5% at near-saturation), creating a **corridor** between the production threshold (~1M ₳, set by Poisson physics) and the viability threshold (~3M ₳, set by the fee structure) where pools produce blocks but cannot sustain their operators. *The operators who charge the most earn the least.* The dead zone is **not static** — as the reserve depletes, the confiscatory zone expands upward, eroding viability for pools that are productive today.

This CPS formally defines the **operator-viability gap** at the intra-pool reward-split layer.

## Problem

This CPS builds on the mainnet evidence documented in [The Operator's Cut — Mainnet Analysis](../../diagnostic/sub-flows/operator-delegator-distribution/mainnet-analysis/README.md). The full induction reasoning, supporting observations, and figures are in the diagnostic — this CPS extracts the formal problem statement and scopes it for solution authoring.

> **Diagnostic source:** [Problem Induction in the parent diagnostic](../../diagnostic/README.md#1331-guarantee-operator-viability-across-the-productive-population) — pulled into a standalone CPS so candidate CIPs can be evaluated against a single, named gap.

### Context

> *Pulled from the diagnostic prose. To be tightened during CPS triage.*

The diagnostic establishes the context for this gap in its narrative — the design intent (the SL-D1 specification and the Reward Sharing Schemes paper), the mainnet evidence (sub-report observations and findings), and the induction that links them. Rather than duplicate that text here, this CPS references it directly so the formal definition stays synchronised with the empirical work.

### Observations

The supporting observations from the mainnet sub-report (operator/delegator distribution layer) are listed in the diagnostic's [Mainnet Observations table](../../diagnostic/README.md#1331-guarantee-operator-viability-across-the-productive-population). Each observation carries its findings (F1, F2, …) and links back to the section of the sub-report where the data and figures live.

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
