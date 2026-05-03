# Cardano Problem Statements

This folder holds the **Cardano Problem Statements (CPSs)** that have been formalised so far from the [Mainnet Diagnostic](../diagnostic/README.md). A CPS is **a question the mechanism has stopped answering**, scoped tightly enough that any candidate solution (CIP) can be evaluated against the same problem definition.

The full set of structural problems the diagnostic induces lives at [Induced Problems](../diagnostic/README.md) (rendered as the [findings page](../generated-website/findings.html) on the site). Only **two** of those eleven problems are presently maintained as formal CPS documents in this folder; the others remain in their narrative form on the diagnostic's findings page until — and unless — they cross the threshold where a formal problem statement adds enough scoping value to justify the maintenance overhead.

## In this folder

- **[Closing the Consensus Incentive Gap](closing-the-consensus-incentive-gap/README.md)** — *Microeconomics — pledge as Sybil instrument.* The reward formula is at war with its security model: its global maximum is a private pool with no delegator participation; 95.6% of the pledge-bonus budget returns to reserve unused. Anchors CIP-0050 and CIP-0037 against a shared problem definition.
- **[Funding the Protocol Without a Reserve](funding-the-protocol-without-a-reserve/README.md)** — *Macroeconomics — pot survival.* The mechanism has no defined path from reserve-funded to fee-funded sustainability; the reserve has crossed its half-life on a known schedule and fees cover ~0.17% of the pot. Anchors CIP-0163.

## On the rest of the induced problems

The diagnostic surfaces nine further structural problems that share the same induction shape (design intent → mainnet evidence → named gap) but have not been promoted to formal CPS documents. The reasons vary: some are still maturing analytically (the non-participant population analysis is incomplete), some may merge with adjacent CPSs during triage (the two fee-base problems read as two angles on the same gap), and some may end up framed as boundary conditions rather than freestanding statements (the price-regime constraints).

For all nine, the canonical narrative — including the supporting observations and findings — lives on the [Induced Problems page](../generated-website/findings.html), which extracts each problem directly from the diagnostic's *Problem Induction* sub-sections and renders them as rich, cross-linked cards. That presentation is more useful at this stage than full CPS templates with placeholder *Use Cases / Goals / Open Questions* sections.

## Transition note

The two CPSs in this folder are themselves **transitional artefacts**. As the analysis matures, their content is likely to be re-homed (either consolidated into the Induced Problems narrative, or extracted into the IntersectMBO/CIPs repository as canonical CPSs once the community process picks them up). This folder will track that movement — when a CPS migrates upstream, its entry here will become a stub that points to the canonical home.
