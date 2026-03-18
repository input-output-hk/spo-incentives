# SPO Incentives Decision Model (v2)

Date: 2026-03-04  
Scope: decision framing for CIP scenario evaluation and final vote.

## 1) Core framing

The policy space is a 3-axis tension:

1. **ROI** (economic attractiveness)
2. **Skin in the Game** (capital commitment required to earn full rewards)
3. **Decentralization Quality** (actual distribution of control across independent entities)

Important clarification:
- **Sybil resistance** and **anti-monopoly** are not separate top-level objectives.
- They are outcomes of axis 2 + axis 3.

## 2) Axis definitions and primary KPIs

## 2.1 ROI

Policy question: does the reward system create viable and fair returns across pool sizes?

Primary KPIs:
- Break-even stake (ADA) at chosen cost basis (ADA/epoch).
- Delegator net ROA at ~3M ADA pool stake.
- Delegator net ROA at saturated pool stake.
- ROA dispersion: `ROA_saturated - ROA_3M`.

Interpretation:
- Lower break-even is better for small SPO viability.
- Lower ROA dispersion is better for fairness.

## 2.2 Skin in the Game

Policy question: how much capital commitment is required to scale stake responsibly?

Primary KPIs:
- Effective leverage cap (`stake / pledge`) where full rewards still apply.
- Pledge required to earn full rewards at target stake levels.
- Capital needed to control X% of active stake under scenario assumptions.

Interpretation:
- Lower allowed leverage and higher required pledge improve anti-free-rider pressure.
- Excessively strict commitment can reduce inclusion of smaller operators.

## 2.3 Decentralization Quality

Policy question: how concentrated is block-production influence at entity level?

Primary KPIs:
- Entity-level Nakamoto coefficient (or MAV equivalent).
- Top-10 entity stake share.
- Concentration indicator (HHI or similar).
- Number/share of viable independent SPOs.

Interpretation:
- Higher Nakamoto and lower concentration are better.
- "More pools" is not enough without entity-level diversity.

## 3) Hard constraints (must pass)

A scenario is not vote-eligible if it fails one of these:

- **Reward sustainability:** no material deterioration in reward-budget sustainability trend.
- **Protocol safety/performance:** no unacceptable downside in liveness/performance.
- **Implementation feasibility:** implementable in realistic governance and release windows.

These are constraints, not score axes.

## 4) Mapping CIPs to the 3 axes

| CIP | ROI impact | Skin in the game impact | Decentralization quality impact | Typical risk |
|---|---|---|---|---|
| `CIP-0023` | High (fee fairness) | Low-Medium | Medium (indirect via delegation flow) | Can reduce fixed-fee support for some operators if badly tuned |
| `CIP-0082` | High (fee + staged structure) | Medium (via pledge relevance and `K` changes) | Medium-High (if delegation actually redistributes) | Potential viability shifts if parameters are not staged carefully |
| `CIP-0050` | Medium | High (explicit leverage discipline with `L`) | High (if MPO leverage behaviors are constrained) | If too strict, may pressure growth-phase SPOs |
| `CIP-0037` | Low-Medium | High (pledge-linked saturation) | High (anti-splitting mechanism) | Hard calibration and higher political resistance |

## 5) Four vote options on this model

## Option A: ROI-first with moderate commitment discipline
- Priority order: ROI -> Skin in the Game -> Decentralization Quality
- Typical package: `CIP-0023` (or `CIP-0082` stage 1-2) + light `CIP-0050` guardrail.
- `K`: hold initially, revisit only after measured effects.

## Option B: Skin in the Game-first
- Priority order: Skin in the Game -> Decentralization Quality -> ROI
- Typical package: `CIP-0050` (lower/moderate `L`) + optional `CIP-0037`.
- `K`: do not increase before leverage discipline is active and measured.

## Option C: Decentralization Quality-first
- Priority order: Decentralization Quality -> Skin in the Game -> ROI
- Typical package: `CIP-0050` + calibrated pledge-linked controls, then conditional `K` debate.
- `K`: conditional only if entity-level concentration improves.

## Option D: Measured Baseline (status quo with strict evidence gates)
- Priority order: preserve baseline while collecting stronger evidence.
- Typical package: no immediate economic change, pre-committed gate criteria and timeline.
- `K`: unchanged during the evidence window.

## 6) Vote-ready scorecard template

Use a 0-100 scale for each axis, then apply policy weights.

Definitions:
- `ROI_score`
- `SITG_score`
- `DQ_score`
- `Constraint_pass` in `{0,1}`

Composite:
- `Total = Constraint_pass * (wR * ROI_score + wS * SITG_score + wD * DQ_score)`
- `wR + wS + wD = 1.0`

Example policy-weight sets:
- ROI-first: `wR=0.50, wS=0.25, wD=0.25`
- SITG-first: `wR=0.20, wS=0.50, wD=0.30`
- DQ-first: `wR=0.20, wS=0.30, wD=0.50`
- Balanced: `wR=0.34, wS=0.33, wD=0.33`

## 7) Minimum ballot language

Ballot question:
"Which policy frontier should guide SPO incentive reform over the next decision window?"

Options:
1. Option A - ROI-first with moderate commitment discipline
2. Option B - Skin in the Game-first
3. Option C - Decentralization Quality-first
4. Option D - Measured Baseline

Post-vote requirement:
- Publish 30/90-day scorecard updates for all KPIs and constraints.

## 8) Suggested first visual pack

1. 3-axis radar per option (`ROI`, `SITG`, `DQ`).
2. ROI fairness chart (`ROA_3M` vs `ROA_saturated`).
3. Commitment chart (required pledge and effective leverage).
4. Entity concentration chart (Nakamoto + Top-10 share).
5. Constraint dashboard (pass/fail with notes).

