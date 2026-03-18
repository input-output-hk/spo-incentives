# Mainnet Entity-Owner-Capital Status Quo

## Table of Contents
- [Scope](#scope)
- [Input Construction](#input-construction)
- [Run Parameters](#run-parameters)
- [Result](#result)
- [Read](#read)
- [Artifacts](#artifacts)
- [Limits](#limits)

## Scope

This run tries to correct the main weakness of the earlier mainnet-like batch:
large pool active stake was being treated as if it were operator-controlled capital.

## Input Construction

The engine input is rebuilt in two layers:
- operator layer: current positive pools are grouped by attributed MPO entity where available, otherwise by repeated reward address when it clearly repeats, otherwise left standalone
- capital basis: each operator group gets `min(current active stake, max(observed owner stake, declared pledge))`
- delegator layer: the remaining active stake is split into synthetic delegator cohorts of `30,000,000` ADA each

| Positive pools | Mapped entity pools | Entity groups | Reward-grouped pools | Operator groups | Pools with owner snapshot | Delegator cohorts | Agent count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2718 | 396 | 26 | 44 | 2302 | 2643 | 626 | 2928 |

| Active stake (ADA) | Operator capital (ADA) | Public delegation (ADA) | Operator share |
| --- | --- | --- | --- |
| 21,747,864,605.370 | 2,971,210,581.064 | 18,776,654,024.306 | 13.66% |

## Run Parameters

- `k = 500`
- `a0 = 0.3`
- `seed = 42`
- `max_iterations = 150`
- `iterations_after_convergence = 10`
- metrics tracked: `[1, 2, 6, 17, 18, 24, 25, 30]`

## Result

| Scenario | Pools | Operators | Nakamoto | Rounds | Step 1 pools | Max pools/op | Mean margin | Median margin | Pledge fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Status Quo | 506 | 451 | 198 | 18 | 5158 | 19 | 0.0276 | 0.0000 | 0.732 |

## Read

This run is still an approximation, but it is a better one for the operator-count question:
- operator-side stake is no longer seeded from full pool active stake
- large multi-pool clusters no longer start with all delegated stake as if it were their own
- the residual active stake remains in the system as delegator cohorts instead of disappearing

## Artifacts

- stake distribution: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/synthetic-stake-distribution-2928-agents.csv`
- operator groups CSV: `/Users/nhenin/dev/ARC/stream-SPO/spo-incentives/scenarii-evaluation/outputs/mainnet_entity_owner_capital_operator_groups.csv`
- input summary JSON: `/Users/nhenin/dev/ARC/stream-SPO/spo-incentives/scenarii-evaluation/outputs/mainnet_entity_owner_capital_input_summary.json`
- engine output: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/24-mainnet-entity-owner-capital-status-quo`

## Limits

- MPO attribution still depends on local clustering, not a canonical on-chain entity id.
- Delegator cohorts are synthetic tranches, not real wallet-level delegates.
- The engine still lets any agent become an operator if economics justify it.