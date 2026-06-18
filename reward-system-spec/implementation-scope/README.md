# Build Estimation / Scoping — what it would take to build the V2 reward reform

This page sizes the work that building the report's recommended reward-system change would involve — the engineering, data-format, and governance tasks it would touch — so the community can weigh the size of the job before deciding whether to take it forward.

Everything before this page explained **what is wrong** with today's staking rewards and **what to change**. This page asks the next question: **what would it cost to build that change?** It names every task the work would require, gives a first-pass estimate of the team size and time the build would take ([§10](#10-effort-team-and-timing)), and leaves precise costing to the engineering teams who would carry it out.

<div class="cps-lifecycle" aria-label="CPS lifecycle">
<a class="cps-stage cps-stage-done" href="intended-game.html" title="The Intended Game — plain-prose design baseline">
<span class="cps-stage-num">Stage 01</span>
<span class="cps-stage-label">The Intended Game</span>
<span class="cps-stage-meta">Design intent &middot; baseline</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="diagnostic.html" title="The Mainnet Diagnostic — observations &amp; findings">
<span class="cps-stage-num">Stage 02</span>
<span class="cps-stage-label">Mainnet evidence</span>
<span class="cps-stage-meta">Observations &amp; Findings</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="problem-statements.html" title="Induced Problems — proto-CPS scoped against the diagnostic">
<span class="cps-stage-num">Stage 03</span>
<span class="cps-stage-label">Induced problem</span>
<span class="cps-stage-meta">proto-CPS</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="solution-design.html" title="Solution Design — prioritising the nine problems into directions and milestones">
<span class="cps-stage-num">Stage 04</span>
<span class="cps-stage-label">Solution Design</span>
<span class="cps-stage-meta">Directions &amp; milestones</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<a class="cps-stage cps-stage-done" href="solution-evaluation.html" title="Evaluation of the four reward-related CIPs against the nine induced problems">
<span class="cps-stage-num">Stage 05</span>
<span class="cps-stage-label">CIPs (Evaluation)</span>
<span class="cps-stage-meta">IntersectMBO governance</span>
</a>
<span class="cps-stage-arrow" aria-hidden="true">&rarr;</span>
<div class="cps-stage cps-stage-current" title="You are here — Build Estimation / Scoping, sizing the build">
<span class="cps-stage-num">Stage 06</span>
<span class="cps-stage-label">Build Estimation / Scoping</span>
<span class="cps-stage-meta">Build sizing &middot; this page</span>
</div>
</div>

# Table of Contents

- [1. What we are building](#1-what-we-are-building)
- [2. Why this needs a hard fork](#2-why-this-needs-a-hard-fork)
- [3. The ledger](#3-the-ledger)
- [4. CDDL](#4-cddl)
- [5. Constitution & guardrails](#5-constitution-guardrails)
- [6. Surrounding software](#6-surrounding-software)
- [7. Specification & testing](#7-specification-testing)
- [8. Rollout order](#8-rollout-order)
- [9. Work-item summary](#9-work-item-summary)
- [10. Effort, team, and timing](#10-effort-team-and-timing)
- [11. Open design choice](#11-open-design-choice)
- [Glossary](#glossary)

# 1. What we are building

**The problem.** Today a pool's reward comes from two things added together: a **size reward** (bigger pools earn more — the larger part) and a **pledge reward** (a bonus for operators who stake their own ADA). The report shows the pledge-reward formula is broken: it punishes small pools, and it perversely pays some operators *more* for pledging *less*. As a result, small honest pools can't earn a living, and the pledge bonus mostly goes unspent.

**The fix — four moves.** The report recommends a "gradual repair" made of four steps, applied in order. In plain terms:

1. **Fix the pledge-bonus formula.** Replace the mis-shaped formula with a better one that stops punishing small pools and stops rewarding under-commitment. *(A rule change — needs a hard fork.)*
2. **Turn the dial toward pledge.** Nudge the balance setting **a₀** so commitment counts for more and raw size counts for less. *(Just turning an existing dial — a governance vote, no hard fork.)*
3. **Add a survival slice for small pools.** Carve out a third part of the reward — **λ_viability** — reserved to keep small but genuine pools financially viable. It is **paid for by trimming the size reward, not by printing new ADA**, and a pool only receives it if its operator actually pledges. *(A new part of the formula — needs a hard fork and a new protocol parameter.)*
4. **Put the idle pledge budget to work.** Today about **95.6% of the money set aside for pledge bonuses is never paid out** — it just flows back to the reserve. Moves 1 and 2 fix this automatically; there is nothing extra to build, only a result to confirm.

**The slightly more precise version** (for the technically inclined): the reward envelope is `E = λ_size·ν + λ_pledge·A(ν, π)`. Move 1 redesigns the pledge-bonus function `A`. Move 2 shifts the `λ_size` / `λ_pledge` balance via `a₀`. Move 3 turns the two-part split into a three-part split `λ_size + λ_pledge + λ_viability` (still totalling 100%), where `λ_viability` is conditional on the operator's pledge. Move 4 is the automatic consequence of 1 and 2 — the dormant `λ_pledge` budget finally gets distributed. All four act on the reward formula **before** the operator/delegator split, i.e. on how the total pool reward is calculated, not on fees.

**What is *not* part of this build** (each is a separate, later piece of the Solution Design):

- **A minimum pool size (`σ_min`) and a "Pool Alliance"** for small operators — [Solution Design Milestone 3](../README.md#23-milestone-3-a-pool-alliance-rocket-pool-like-for-cardano). The survival slice *interacts* with the idea of a minimum size, but the four moves don't require it to ship.
- **Lock-up / liquid-staking products for delegators** — [Solution Design Milestone 2](../README.md#222-what-smart-contracts-unlock-diversification-and-programmable-pledge).
- **Treating an operator's whole fleet as one entity** (the anti-Sybil "entity" work) and the **governance monitoring dashboard** — [Solution Design §2.5](../README.md#25-research-axis-reduce-the-concentration-effects-that-distort-both-populations) and [§3.1](../README.md#31-milestone-1-reward-system-extension-a-governance-dashboard-for-the-system-properties-populations).

**About the fee-related CIPs (CIP-0023 and CIP-0082 stage 2).** The report's CIP review credited **CIP-0023** for correctly spotting a real problem — that the flat per-pool fee (`minPoolCost`) hits small pools hardest — and even found its mechanism *partly* helps (it narrows the unfairness between small and large pools from 38× to 13×). So it is worth being clear how that fits here:

- The *problem* CIP-0023 spotted is answered by **move 3 (the survival slice)** — which this page does size. We deliberately **do not** rebuild CIP-0023's own mechanism (a minimum-margin fee floor) as the viability fix, because the report's recommendation rests on keeping fee tools as *free competitive levers* and putting the survival support in the reward formula instead. So its absence here is a deliberate choice, not an oversight.
- The one CIP-0023-aligned action that *is* available — **lowering `minPoolCost`** — needs **no build at all**. It is an existing dial (already moved once, from 340 to 170 ADA, by a governance vote) and can be turned again the same way. It is noted in the rollout ([§8](#8-rollout-order)), not in the build list.

# 2. Why this needs a hard fork

A quick definition: a **hard fork** is a change to the network's *rules*, as opposed to a **parameter update**, which only changes a *setting* within limits the rules already allow. Every node must adopt a hard fork together at an agreed time; a parameter update just needs a governance vote.

**The reward formula is a rule.** Every node recalculates rewards the same way at the end of each epoch — that agreement *is* the consensus. **Moves 1 and 3 change how rewards are computed** (a new pledge-bonus shape, and a new third slice), so they change the rule and therefore **require a hard fork**. If some nodes used the old formula and others the new one, they would compute different rewards and the network would split. This is not a detail that can be reduced or worked around; it is the nature of the change.

Two specifics worth flagging up front:

- **Move 1 takes effect the moment the fork happens.** The new pledge-bonus formula is part of the live reward calculation immediately — it cannot be shipped "switched off" and tuned later. So its exact shape must be **agreed and tested before the fork**. (Move 3's survival slice *can* ship switched off — set to 0% — and be turned on later by a vote.)
- **Move 2 is the one step that is *not* a hard fork.** Turning the `a₀` dial stays within its existing legal range (0.1 to 1.0), so it is an ordinary governance vote that can be done after the fork.

# 3. The ledger

The **ledger** is the core software (`cardano-ledger`) that computes rewards each epoch. This is where the heart of the change lives. All of the following ship together in a new "ledger era" (the versioned rule-set a hard fork switches the network into).

- **3.1 — Replace the pledge-bonus formula `A` (move 1).** Swap the old, mis-shaped formula for the repaired one in the reward calculation. This changes the *rule*, not a setting, so there is no new parameter. The exact repaired formula is decided during design ([§8](#8-rollout-order)) and must be locked in before the fork ([§2](#2-why-this-needs-a-hard-fork)).
- **3.2 — Add the survival slice and the new dial that controls it (move 3).** Introduce a new protocol parameter (working name `b₀`, a "viability-influence" dial) and rewrite the formula so the reward splits **three ways** — size, pledge, and survival — instead of two, always still totalling 100%. Add the **condition**: a pool only earns the survival slice if its operator meets a pledge requirement (a minimum pledge, or a step-up schedule — to be specified). Set the new dial's default so that, until governance turns it up, the formula behaves exactly like today's two-part split.
- **3.3 — Re-wire the size/pledge balance (move 2).** Make sure the size and pledge shares are still driven correctly by the `a₀` dial under the new three-way split, so a later governance vote on `a₀` reshapes the reward as intended.
- **3.4 — Confirm the idle pledge budget now gets paid out (move 4).** No new code, but a result to verify: with the repaired formula and rebalanced dial, far more of the pledge budget is actually distributed instead of flowing back to the reserve. Check that the reserve / treasury / pool-pot bookkeeping still balances afterwards.
- **3.5 — Wire it all into the epoch reward calculation cleanly,** and make sure the per-pool reward breakdown that tools and explorers read still reports correctly under the new formula.

# 4. CDDL

**CDDL (Concise Data Definition Language)** is the schema describing exactly how on-chain data is encoded as bytes. Adding a new protocol parameter means teaching this schema (and the read/write code) about it.

- **4.1 — Add the new survival dial to the parameter-update format.** Give the new parameter a slot in the data structure used for parameter changes, define its type, and update the code that encodes/decodes it. *(Move 1's formula change is pure logic — it needs no data-format change.)*
- **4.2 — Add the new dial to the era's parameter set,** including the default value that makes the new formula behave like today's until it is switched on.
- **4.3 — Keep old and new software compatible.** Make sure software from before and after the change can still read each other's data safely.
- **4.4 — Add encoding tests** confirming the new field round-trips correctly (part of the test work in [§7](#7-specification-testing)).

# 5. Constitution & guardrails

A reminder: **guardrails** are limits, written into the **Cardano Constitution**, on how far each parameter can be moved; they are enforced on-chain by the **Guardrails Script**. Reference text of the Constitution: <https://raw.githubusercontent.com/IntersectMBO/cardano-constitution/refs/heads/main/cardano-constitution-2/cardano-constitution-2.txt.md>.

The Constitution's **Appendix I** already sets guardrails for the existing reward parameters — for example `a₀` (codes `PPI-01`–`04`, limited to 0.1–1.0) and `minPoolCost` (codes `MPC-01`–`03`, limited to 0–500 ADA). The new dial slots into the same machinery.

- **5.1 — Add a guardrail for the new survival dial.** Write a new entry in Appendix I giving the new parameter a legal range (with its own code, e.g. `PVI-01`/`PVI-02`). The exact range comes out of the design work.
- **5.2 — Re-check how the `a₀` guardrail is written, now that the reward splits three ways.** This is the one subtle constitutional point. Today `a₀` is defined assuming a *two-part* reward. Adding the survival slice makes it *three-part*, which changes how `a₀` feeds the formula — so the way the `a₀` guardrail is expressed probably needs updating, even if its numeric range (0.1–1.0) stays the same. This must be checked against the actual Constitution text, not assumed. *(This extra constitutional step is exactly what the alternative design in [§11](#11-open-design-choice) avoids — worth weighing.)*
- **5.3 — Update the Guardrails Script** (the on-chain program that enforces the limits) so it knows about the new dial's range and any reworded `a₀` rule.
- **5.4 — Use the right governance actions, in the right order.** The Constitution's own rules (`HARDFORK-05` and `NEW-CONSTITUTION-01a`) say new parameters must be added to Appendix I with guardrails, via a hard fork. In practice that means: a **Guardrails-update action** defines the new dial's limits first; the formula changes and the new parameter then arrive through a **Hard Fork action**; and later, ordinary **parameter-update votes** turn the dials.
- **5.5 — Confirm (and document) that the *core* Constitution does not need amending.** The reform is designed to *uphold* the Constitution's existing principles on fair compensation, fair treatment, and monetary stability — not to change them. So the heavyweight "amend the Constitution" path is **not** needed; only the lighter guardrail and parameter steps are. Spelling out which kind of change each step is will itself be part of the CIP.

# 6. Surrounding software

The ledger does the calculation, but a lot of other software displays, queries, or re-implements it. Each needs a matching update once the new rules ship.

- **6.1 — The node** (`cardano-node`) must adopt the new rule-set and the hard-fork switch-over, with integration testing.
- **6.2 — The command-line tool** (`cardano-cli`) must let people propose the new parameter and read it back.
- **6.3 — The chain database** (`cardano-db-sync`, which feeds explorers and analytics) needs columns for the new parameter and the reshaped rewards.
- **6.4 — Reward calculators and analytics** (the official [reward calculator](https://github.com/cardano-foundation/cardano-reward-calculator), plus community sites like PoolTool, AdaStat, Cexplorer) need to model the new formula so the numbers people see are right.
- **6.5 — Wallets and explorers** should show the new parameter and, ideally, whether a pool qualifies for the survival slice.
- **6.6 — Operator documentation** needs updating so stake-pool operators understand the pledge condition for the survival slice.

# 7. Specification & testing

Cardano's rules are also written down in a precise, machine-checked **formal specification**; it and the test suite must move in step with the code.

- **7.1 — Update the formal specification** (the mathematically precise version of the rules) for the new formula, the three-way split, the new dial, and the pledge condition.
- **7.2 — Prove the change does exactly what's intended.** Two checks: **(a)** before the fork, the old formula still reproduces today's real rewards exactly (a safety baseline); **(b)** after the fork, the new formula produces the intended results across the full range of pool sizes and operator types. (Note: because move 1 is live at the fork, the *whole* reform cannot be "identical to today until switched on" — only the survival slice can default to off.)
- **7.3 — Add targeted tests** for the new rules: that the three shares always total 100%, that the pledge condition works, that the repaired bonus formula has the intended shape (helps small pools, rewards balanced pledge, doesn't favour fully-private pools), and that bigger pools never earn less than smaller ones.
- **7.4 — Add the data-format tests** noted in [§4.4](#4-cddl).
- **7.5 — Update the written design document** so the new mechanism has an authoritative reference, like the original 2019 design spec did for today's formula.

# 8. Rollout order

The steps are sequenced so the network never runs an untested reward rule:

1. **Agree the design, write the CIP, get it ratified.** Lock down the repaired formula, the survival slice and its pledge condition, and the `a₀` target. *(The repaired formula must be settled now, because it goes live at the fork — it can't be tuned afterwards.)*
2. **Set the guardrails.** A guardrails-update action defines the legal range for the new dial and any reworded `a₀` rule.
3. **Ship the hard fork.** It carries the new formula and the new dial — with the survival slice **defaulted to off**, so rewards are unchanged on day one.
4. **Turn the dials on, by vote.** Governance gradually raises `a₀` (move 2) and the survival slice (move 3) toward their target values — visible on the monitoring dashboard once that exists.
5. **Watch and adjust.** Later votes fine-tune the dials as evidence comes in.

**A bonus lever that needs no building.** Separately from all of the above, governance can lower **`minPoolCost`** (the flat per-pool fee, currently 170 ADA, legal range 0–500) by an ordinary vote. This is the simple step that CIP-0023 was pointing at for small-pool fairness. It pairs naturally with the four moves but requires **no ledger, data-format, or Constitution work** — which is why it sits here in the rollout rather than in the build list.

# 9. Work-item summary

Every build item, with where it lives and whether it requires a hard fork. "Follows era" means the item isn't itself a rule change but has to ship alongside the new rules.

| # | Work item | Where (software / document) | Kind | Needs a hard fork? |
|---|---|---|---|:---:|
| 3.1 | Replace the pledge-bonus formula (move 1) | cardano-ledger | Reward rule | ✅ Yes |
| 3.2 | Add survival slice + its new dial + pledge condition (move 3) | cardano-ledger | Reward rule | ✅ Yes |
| 3.3 | Re-wire the size/pledge balance (move 2) | cardano-ledger | Reward rule | ✅ Yes (the dial itself is turned later, by vote) |
| 3.4 | Confirm idle pledge budget now pays out (move 4) | cardano-ledger | Verification | ✅ Yes |
| 3.5 | Wire into epoch reward calc + reporting | cardano-ledger | Reward rule | ✅ Yes |
| 4.1–4.3 | Data-format (CDDL) slot for the new dial | cardano-ledger | Data format | ✅ Yes |
| 5.1 | Guardrail for the new dial (Appendix I) | Constitution | Constitution | ✅ Yes (via the fork's guardrail action) |
| 5.2 | Re-word the `a₀` guardrail for the 3-way split | Constitution | Constitution | ✅ Yes (via the fork's guardrail action) |
| 5.3 | Update the Guardrails Script | Constitution (on-chain program) | Constitution | ✅ Yes (via the fork's guardrail action) |
| 5.4 | Run the hard-fork + guardrail governance actions | Governance | Governance | ✅ Yes |
| 5.5 | Document that no core-Constitution amendment is needed | CIP / governance | Documentation | — |
| 6.1 | Node adopts the new rule-set | cardano-node | Surrounding software | ✅ Yes |
| 6.2 | CLI: propose + read the new dial | cardano-cli | Surrounding software | Follows era |
| 6.3 | Chain database columns for new dial + rewards | cardano-db-sync | Surrounding software | Follows era |
| 6.4 | Reward calculators / analytics | reward-calculator + community | Surrounding software | Follows era |
| 6.5–6.6 | Wallet/explorer display + operator docs | ecosystem | Surrounding software / docs | Follows era |
| 7.1 | Update the formal specification | formal-ledger-specifications | Specification | ✅ Yes |
| 7.2 | Old-formula baseline + new-formula correctness tests | cardano-ledger tests | Testing | ✅ Yes |
| 7.3–7.4 | Targeted rule tests + data-format tests | cardano-ledger tests | Testing | ✅ Yes |
| 7.5 | Update the written design document | reward-system-spec | Documentation | — |
| 8.4 | Votes to turn on `a₀` + survival slice | Governance | Governance | ❌ No (after the fork) |

The only steps that are **not** part of the hard fork are the votes that *turn the dials on* afterwards. Everything else is the build.

# 10. Effort, team, and timing

The sections above name the work. This one sizes it and places it in the calendar: a team estimate, a duration, and a recommendation on when to do which part.

**Team and duration.** The work in [§3](#3-the-ledger) through [§7](#7-specification-testing) — the ledger change, the data-format work, the Constitution and guardrails code, the surrounding software, and the specification and tests — is a **six-month project sized at 4–6 full-time-equivalent (FTE) engineers**. An FTE is a unit of sustained effort: one person working full-time for the period. The actual roster is larger — specialists in the formal specification, the data format (CDDL), the Constitution guardrails, and the chain database (`db-sync`) rotate in for the stage that needs them and back out — and their combined load across the six months averages 4–6 full-time engineers. That span covers preparation, implementation, and testing: the engineering build, end to end.

Two things sit **outside** that six months, because they run on the network's clock rather than the team's: the time governance actions take to be approved, and the scheduling and coordination of the hard fork that ships the change ([§8](#8-rollout-order)).

**On costing.** This estimate is in **people and months**. A figure in money depends on who staffs the work and at what rate — which the engineering teams that would carry it out are best placed to set. The 4–6 FTE over six months is the unit a budget can be built from.

**Timing — write the CIP in 2026, build it after Dijkstra.** 2026 is the year to **write the CIP and carry it through ratification**. The build comes later. Two reasons set this order:

- **The specification has to be settled before any node work begins.** The repaired pledge-bonus formula goes live the instant the hard fork happens and cannot be tuned afterwards ([§2](#2-why-this-needs-a-hard-fork)), so its shape must be agreed and approved first. 2026 is the year to do that agreeing.
- **2026's engineering capacity is committed elsewhere.** The reform competes with other network priorities for the same teams, and those priorities hold for 2026.

So the build targets a **ledger era following Dijkstra**: the CIP ratified in 2026 becomes the specification that a later era's hard fork implements. This matches the rollout sequence in [§8](#8-rollout-order) — agree and ratify the design, then ship the fork — and places the six-month build in the window where the engineering capacity for it is free.

| Question | Answer |
|---|---|
| How much effort? | 4–6 FTE engineers; a larger roster rotating through stages |
| How long? | ~6 months — the build alone ([§3](#3-the-ledger)–[§7](#7-specification-testing)) |
| Outside that estimate | Governance approval time; hard-fork scheduling and coordination |
| When to write and ratify the CIP? | 2026 |
| When to build and ship it? | A ledger era following Dijkstra |

# 11. Open design choice

There is a genuine fork in the road that the CIP must settle before building, because it changes part of the work above.

- **The recommended design (sized on this page)** puts the small-pool survival support **inside the reward formula**, as a third slice (`λ_viability`).
- **An alternative design** (explored in a [separate whiteboard](../solution-evaluation/v2-proposal/new-CIP.md), and *not* the report's current recommendation) puts it in a **separate channel** alongside the formula instead — funded by a single new dial called `μ` ("mu") — leaving the existing two-part formula untouched.

Both need the same core work (the repaired formula, a new dial, data-format and guardrail changes, a hard fork). They differ mainly here:

| | Recommended: slice *inside* the formula | Alternative: separate *channel* |
|---|---|---|
| The new dial | a "viability-influence" dial (`b₀`) | a single share dial (`μ`) |
| Constitution work | new dial **plus** re-wording the `a₀` guardrail (item 5.2) | just the new dial; `a₀` left alone |
| Can it ship fully "off"? | only the slice can; the repaired formula is live at the fork | the whole channel can default to off |
| Effect on delegator rewards | the slice and delegator rewards share one budget | kept separate — survival support never competes with delegator yield |

**Why it matters for this page:** if the project ever switches to the channel design, items **3.2** and **5.2** are the ones that change. Which design is the real intention is best confirmed with the report's authors — see the note in the project's review state.

# Glossary

The terms this page uses, grouped by topic. Each is also defined inline the first time it appears in the text.

**The staking system**

- **Epoch** — Cardano's accounting period, about 5 days. Staking rewards are calculated once per epoch.
- **Stake pool** — a node that produces blocks on behalf of the ADA delegated to it. Run by an **operator (SPO — Stake Pool Operator)**.
- **MPO (Multi-Pool Operator)** — one entity running many pools.
- **Delegation** — an ADA holder pointing their stake at a pool to earn a share of its rewards, without giving up custody of their coins.
- **Pledge** — ADA the *operator* locks into their *own* pool, as a visible signal of commitment ("skin in the game").
- **Reserve** — a large pre-created pot of ADA that funds most staking rewards today; it shrinks every epoch and is not replenished.
- **Pool pot** — the ADA paid out to all pools in a given epoch (assembled from the reserve plus transaction fees).

**The reward formula** (how each pool's pay is calculated)

- **Reward envelope** — the formula that decides a pool's reward. Today it has **two parts** that are added together:
  - a **size reward** — scales with how big the pool is. This is the larger part.
  - a **pledge reward** — a bonus for operators who pledge their own ADA.
- **a₀ (pronounced "a-nought", the *pledge-influence* parameter)** — the single dial that sets the balance between the size reward and the pledge reward. Higher a₀ = pledge counts for more.
- The few symbols the formula uses, in plain terms:
  - **ν (Greek "nu")** — a pool's **size**, measured against the point where it is considered "full" (saturated).
  - **π (Greek "pi")** — a pool's **pledge ratio**: what fraction of the pool's stake the operator pledged themselves.
  - **A(ν, π)** — the **pledge-bonus function**: the piece of the formula that turns size-and-pledge into the pledge reward. The report's central finding is that this piece is mis-shaped.
  - **λ ("lambda") weights** — the shares of the reward going to each part: **λ_size** (size), **λ_pledge** (pledge), and the proposed new **λ_viability** (a small-pool survival slice). They always add up to 100%.

**How Cardano changes its rules** (the "change machinery")

- **Protocol parameter** — an adjustable setting of the network (for example a₀, or `minPoolCost`). Can be changed by a governance vote, within fixed limits.
- **Parameter Update** — a governance action that changes a parameter's *value*. It needs a vote, but **no new software** — the capability already exists.
- **Hard fork** — a change to the network's *rules themselves* (not just a setting). Every node must upgrade and switch over together at an agreed moment. A reward-formula change is a hard fork. Requires new node software **and** a governance-approved "Hard Fork" action.
- **Ledger** — the core software (the `cardano-ledger` project) that tracks balances and computes rewards each epoch. Changing the reward formula means changing this code.
- **CDDL (Concise Data Definition Language)** — the schema that defines exactly how on-chain data is encoded. Adding a new parameter means updating this schema and the code that reads/writes it.
- **Guardrails** — hard limits, written into the Cardano Constitution, on how far each parameter can be moved (e.g. a₀ must stay between 0.1 and 1.0). Enforced automatically on-chain by a small program called the **Guardrails Script**.
- **Cardano Constitution** — the network's governing document (version 2, ratified in 2024). Its **Appendix I** lists every parameter's guardrails. Each guardrail has a code (e.g. `PPI-01` for a₀, `MPC-01` for `minPoolCost`).
- **CIP (Cardano Improvement Proposal)** — the standard document format for formally proposing a protocol change to the community and governance.

> **Status:** First-pass scope, 2026/06/10. Sizes the report's recommended four-move reform ([Solution Evaluation §4](../solution-evaluation/README.md#4-recommendations-on-adjustments-to-the-current-mechanism) / [Solution Design Milestone 1](../README.md#21-milestone-1-repair-pledge-sustain-the-small-spo-base)). Lists the build, with a first-pass team-and-duration estimate ([§10](#10-effort-team-and-timing)); leaves precise costing to the engineering teams. To be refined as the CIP takes shape.
