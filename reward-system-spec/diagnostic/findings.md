---
page: findings
source: diagnostic/README.md
date_updated: 2026/04/22
purpose: canonical synthesis for problem-statements.html — decoupled from the long-form diagnostic README
---

# Findings Index

This document curates every finding that appears on `problem-statements.html`. It exists
to decouple the public-facing synthesis from the long-form analytical README,
so each finding carries an editorially-chosen title, an explicit tier and
parent, an explicit list of supporting observations, a curated 2–4 paragraph
summary fit for the synthesis page, and a backlink anchor to the full reasoning
in `diagnostic.html`.

`build_site.py` reads this file (not the regex pipeline over `diagnostic/README.md`)
to render `problem-statements.html`. The observation table itself stays in
`diagnostic/README.md` — observations *are* the README — but the mapping
finding → observations is explicit here.

Date formatting follows the workspace rule (`YYYY/MM/DD`).

## §1 The Reward Flow

Reserve → Pools → Operators/Delegators

### 1.1.3. — Funding the Protocol Without a Reserve

<!-- FINDING
id: 1.1.3
parent: 1.1
parent_title: Treasury & Pool Pots Distribution
tier: sustainability
observatory_anchor: 113-problem-induction-funding-the-protocol-without-a-reserve
observations:
  - obs-112-1
  - obs-112-2
  - obs-112-3
  - obs-112-4
-->

The epoch pot is funded almost entirely by monetary expansion from the reserve
(O1). That reserve is finite and has crossed its half-life (O2): 13.29B ADA has
fallen to 6.53B ADA in 5.5 years, with significant reward pressure expected at
epochs 1000–1200 (~2028–2029).

The reward mechanism operates at only ~44% of its potential (O3): roughly
4.55B ADA cumulatively — about 70% of the current reserve — exists because
~17B ADA does not participate in delegation and its share of the pot returns
to the reserve instead of reaching operators and delegators. Reward parameters
ρ (0.3%) and τ (20%) have never been adjusted since Shelley (O4), and neither
has been subject to a governance proposal.

Each observation constrains what the pipeline can do. Read together, they
reveal that the mechanism is not producing the conditions for its own
sustainability: the funding source is exhausting, the participation base is
incomplete, and the governing parameters are frozen.

### 1.2.3. — Closing the Consensus Incentive Gap: The pledge paradox & Non-Participant problem

<!-- FINDING
id: 1.2.3
parent: 1.2
parent_title: Pools Distribution
tier: mechanism
observatory_anchor: 123-problem-induction-closing-the-consensus-incentive-gap-the-pledge-paradox-non-participant-problem
observations:
  - obs-122-1
  - obs-122-2
  - obs-122-3
  - obs-122-4
  - obs-122-5
  - obs-122-6
  - obs-122-7
  - obs-212-7
-->

Two causes account for **54% of the pools pot returning to reserve** (O1): a
31.6% participation gap and a 22.1% unused pledge-incentive budget, of which
95.6% is wasted. The pledge mechanism itself is economically broken (O2) —
yield on pledge capital tops out at 0.68%/yr, below passive delegation, and
78% of staked ADA sits in pools with pledge ratio below 1%.

The pool landscape is stratified into four tiers far from the $k = 500$
target (O3): 73% of pools sit below viability and only 8 reach saturation.
Multi-pool operators control 76.7% of productive stake (O4): 83 attributed entities hold
16.24B ADA, and 42 of the 48 saturation-scale MPOs are zero-pledge.

The single-pool operator base has collapsed to 284 productive single-pool operators once MPO
fleets are removed (O5). The incentive-responsive field — the portion of the
network that actually reacts to the pledge signal — holds only 36% of active
stake (O6).

Together these observations describe a gap between the equilibrium the
mechanism was designed to produce and the equilibrium it actually produces.
Parameter adjustments alone do not close it.

### 1.3.3. — Two Compounding Failures: Operator Viability and Delegator Yield

<!-- FINDING
id: 1.3.3
parent: 1.3
parent_title: Operator / Delegator Distribution
tier: mechanism
observatory_anchor: 133-problem-induction
observations:
  - obs-132-1
  - obs-132-5
  - obs-132-6
  - obs-132-7
  - obs-132-8
  - obs-132-9
  - obs-212-6
-->

<!-- FINDING
id: 1.3.3.1
observations:
  - obs-132-1
  - obs-132-6
-->

<!-- FINDING
id: 1.3.3.2
observations:
  - obs-132-5
  - obs-132-7
  - obs-132-8
  - obs-132-9
  - obs-212-6
-->

The intra-pool split fails at both ends. **Operator viability is not
guaranteed:** no single-pool operator in the retail market earns a competitive
wage (O6). A sub-reliable operator absorbs 48.3% of pool rewards yet earns
24,820 ₳/yr; an 11+ pool MPO absorbs 7.7% yet earns 1,035,496 ₳/yr — 42× more
revenue at 6× less effective price. The flat fee follows a $1/\sigma$ hyperbola
(O1) that creates a corridor between the production threshold (~1M ₳) and the
viability threshold (~3M ₳) where pools produce blocks but cannot sustain
their operators.

**Delegator yield is no longer competitive** with risk-free alternatives or
with other PoS chains (O8). The delegator yield has fallen from 5.3% to 2.0%
in 413 epochs, tracking reserve depletion with $R^2 = 0.99$. The return
spread across the retail market is 0.39pp (O5) — too narrow to drive
delegation decisions. Delegation follows visibility, not return (O7): 65.9%
of retail delegators sit in hollow MPO pools at 2.18% net return, while
hollow single-pool pools at 2.34% hold only 2.7% of delegators.

A third structural consequence — the concentration of rewards among a small
number of large entities (O6, O7, O8) — is not a separate problem: it is the
predictable outcome of the first two. A fee structure that makes small pools
unviable, combined with a yield regime too compressed for delegators to
differentiate, mechanically concentrates rewards in fleets that can amortise
the drag.

The mechanism is on a structural clock (O8): reserve depletion compresses
yield, widens the confiscatory zone, and erodes the signal every epoch. No
formula change at §1.3 alone can raise the ceiling — the three layers (epoch
budget, reward curve, intra-pool split) must be designed as one system.

## §2 The Player Populations

Staking populations & transaction submitters

### 2.1.3. — Each Staking Population Is Structurally Frozen

<!-- FINDING
id: 2.1.3
parent: 2.1
parent_title: The Staking Populations
tier: concentration
observatory_anchor: 213-problem-induction-distribution-distortions-across-the-three-populations
observations:
  - obs-212-1
  - obs-212-2
  - obs-212-3
  - obs-212-4
  - obs-212-5
  - obs-212-6
  - obs-212-7
  - obs-122-5
  - obs-122-6
  - obs-132-7
-->

<!-- FINDING
id: 2.1.3.1
observations:
  - obs-212-1
  - obs-122-5
  - obs-122-6
  - obs-132-3
-->

<!-- FINDING
id: 2.1.3.2
observations:
  - obs-212-2
  - obs-212-3
  - obs-212-4
  - obs-212-5
  - obs-212-6
  - obs-132-7
-->

<!-- FINDING
id: 2.1.3.3
observations:
  - obs-212-7
-->

The populations on which the reward pipeline operates each exhibit a
structural condition that no parameter adjustment within the current mechanism
can alter.

**The operator population is not a single competitive field** (O1, O2).
Seventy-three named entities control 76.7% of productive stake through 464
pools, and the productive set has been in quasi-equilibrium at ~950 pools
since epoch 300 with 1.7% turnover per epoch — replacement, not expansion.
Within this landscape, three structurally distinct sub-populations coexist:
custodial operators that cannot pledge client capital, MPO fleets that have
chosen not to pledge despite capacity, and single-pool operators
bearing the full cost of the fee structure.

**The stake-holder population is a frozen power law** (O3, O4, O5, O6). One
thousand delegators — 0.07% of the base — control 57% of staked ADA; the Gini
coefficient is 0.976. Concentration crystallised by epoch 300 and has not
moved since. Half of all delegation switches produce zero yield change (O6):
mobility exists but it does not produce competitive pressure because it is
not yield-driven. The only asymmetric signal is pool size — delegators drift
toward visibility, not commitment.

**The non-participant population is structurally growing** (O7). The staking
rate has fallen from 71% to 59%, driven by supply growth outpacing stake
inflows. Of the 14.36B ADA outside delegation, only 0.37% is addressable —
the remainder sits in enterprise addresses, DeFi scripts, and dormant wallets
that the reward mechanism cannot reach.

### 2.2.3. — The Fee Base Contracts While the Pipeline Needs It to Grow

<!-- FINDING
id: 2.2.3
parent: 2.2
parent_title: Transaction Submitters
tier: fees
observatory_anchor: 223-problem-induction-tx-submitter-demand-side-fees-the-canonical-answer-to-m01-are-not-growing-fast-enough-at-current-throughput
observations:
  - obs-222-8
  - obs-222-9
  - obs-222-10
  - obs-222-11
  - obs-112-1
-->

The reward pipeline's long-term viability rests on a single assumption: that
transaction fees will eventually replace monetary expansion as the dominant
source of the epoch pot. Today, fees contribute approximately 0.19% of the
pot; reaching self-sufficiency would require fee revenue to grow by
roughly **~100× (two orders of magnitude)** — combining higher throughput
(Leios), structurally higher transaction demand, and tiered per-tx pricing.

**The submitter population is moving in the opposite direction** (O8).
Distinct fee-paying addresses per epoch have fallen from ~512,000 (epoch 300)
to ~158,000 (epoch 384) — a 69% decline — while transaction count has held
above 300K per epoch. The fee base is not expanding; it is consolidating
toward fewer, more active actors.

**The constituency that generates the most fee revenue is structurally
excluded from the rewards it funds** (O9, O10). Eighty-two percent of
submitter addresses carry a staking credential, but 30.6% of fee revenue
comes from enterprise and script addresses that cannot delegate. Post-Alonzo,
script transactions represent 12.6% of count but 29.7% of fees, and exceed
40% during high-DeFi epochs. Fee revenue is concentrated but below the
delegation Gini (O11): the top 10 fee-paying addresses generate 30.5% of all
fees; the top 500 generate 51.5%.

The gap between current fee input and the level required for sustainability
is a structural deficit, not a transient shortfall. Volume is flat, breadth
is declining, and no parameter change within the current mechanism addresses
any of the three growth dimensions — volume, breadth, intensity — the
pipeline depends on.

## §3 The ₳/Fiat Money Constraint Layer

Fees, monetary policy, and the exogenous exchange rate

### 3.1.1. — A deflationist ₳ — what mechanisms can complement finite supply?

<!-- FINDING
id: 3.1.1
parent: 3.1
parent_title: The ₳/Fiat Money Constraint Layer
tier: sustainability
observatory_anchor: 311-a-deflationist-what-mechanisms-can-complement-finite-supply
observations:
  - obs-112-2
  - obs-132-9
-->

The reward pipeline distributes ADA, but every participant decides in fiat
terms — operator infrastructure costs, delegator opportunity costs versus
DeFi alternatives, transaction fees. The mechanism therefore needs the ADA
price to be **deflationary in real terms** as the emission rate declines:
otherwise the pipeline's ADA-denominated output loses purchasing power and
the security budget contracts.

The protocol's **only deflationary property is the supply cap**. A capped,
declining-emission monetary policy creates *scarcity* — a *necessary*
condition for deflation. *But scarcity alone is not sufficient.* Appreciation
requires demand growth exceeding supply growth, and demand for ADA is a
function of on-chain utility (transaction throughput, DeFi activity,
application adoption, institutional custody, speculative interest) — *none
of which are protocol parameters*.

**The deflationist promise rests on a single property — finite supply — and
that property is necessary but not sufficient.** Pre-Conway,
scarcity-as-only-lever was a forced choice: there was no on-chain governance
pipeline to add complementary properties. Post-Conway, it is a design gap.
Finite supply was never enough, and the post-Conway era removes the excuse
for treating it as if it were.

### 3.1.2. — ₳/Fiat volatility — what instruments can wire governance to price observations?

<!-- FINDING
id: 3.1.2
parent: 3.1
parent_title: The ₳/Fiat Money Constraint Layer
tier: sustainability
observatory_anchor: 312-fiat-volatility-what-instruments-can-wire-governance-to-price-observations
observations:
  - obs-112-4
  - obs-132-9
-->

Whatever direction the ADA/Fiat exchange rate moves, the mechanism **absorbs
the consequence passively** — there is no on-chain instrument that responds
to price observations, redirects emission, or recalibrates fees against
real-economy conditions. The reward pipeline's long-term viability requires
three macroeconomic conditions to hold simultaneously: operator and delegator
real revenue must remain viable (deflationary ADA price), the fee input must
grow and the submitter population must expand, and the fiat cost of
transacting must remain low enough to keep activity on Cardano.

These three constraints are not independent. A rising ADA price preserves
operator and delegator viability but raises the fiat cost of transacting,
suppressing fee volume; a falling ADA price lowers the fiat cost of
transacting but compresses operator and delegator real revenue; a stable ADA
price satisfies neither extreme. *The ₳/Fiat exchange rate is the hidden
variable that connects all three, and the mechanism offers no instrument to
manage them.*

**Pre-Conway, the absence of an instrument was a constraint** — there was no
on-chain mechanism to recalibrate against macroeconomic conditions, so the
mechanism's passivity was forced. Post-Conway, it is a design gap that the
governance pipeline can now address: parameter recalibration against price
observations, oracle-informed fee-formula updates, treasury-funded operator
support during sustained price downturns, governance-triggered emission
adjustment under defined trigger conditions. The diagnostic point is that
**the layer of monetary management exists now** — the mechanism's passivity
is no longer required.

## Schema — the `<!-- FINDING … -->` metadata block

Each `### X.Y.Z — Title` section carries one comment-block immediately after
the heading. Fields:

- **id** — matches the section heading number (e.g., `1.1.3`, `3.3`).
- **parent** — the enclosing section (`1.1`, `2.2`, `3`).
- **parent_title** — human-readable parent label shown on the card header
  (e.g., `Treasury & Pool Pots Distribution`).
- **tier** — one of `mechanism`, `concentration`, `structure`, `demand`,
  `fees`, `sustainability`, `general`. Drives the filter chips on
  `problem-statements.html`.
- **observatory_anchor** — the `id=…` in the rendered `diagnostic.html`
  that the *Read full finding on the Mainnet Diagnostic →* link points to.
- **observations** — YAML list of global observation ids (`obs-XYZ-N`) from
  `diagnostic/README.md` that support the finding. Empty list is valid
  (§3.3 currently has none — the supporting material is narrative, not a
  tabulated observation yet).

The body of each section (everything between the heading and the next
`###` or `##`) becomes the card summary, rendered with the same markdown
pipeline as observation bodies.

## Editorial notes for review

- **Titles proposed for three findings that previously lacked them.** The
  regex pipeline fell back to `"Problem Induction"` for §1.3.3, §2.1.3, and
  §2.2.3. Suggested titles above — adjust freely.
- **§3 added.** Previously absent from `problem-statements.html` because its structure
  (`## 3.3 Problem Induction` with `### 3.3.x` children) did not match the
  `### X.Y.Z` pattern. Treated here as a single finding at id `3.3`
  consolidating §3.3.1 and §3.3.2. Splitting into two separate findings is an
  option if the Mainnet Diagnostic page keeps them distinct.
- **Diagnostic anchor for §3.3** is a placeholder (`33-problem-induction`).
  The actual slug depends on the python-markdown TOC rule applied when
  `diagnostic.html` is rebuilt; confirm after the next build.
