# CIP Scenario Run Notes

Executed against [Rewards-Sharing-Simulation-Engine](/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine) with the canonical matrix generated from `config/cip_scenario_axes.json`.

## Completed runs

| Scenario ID | Output directory | Runtime | Pool count | Operator count | Nakamoto | Total pledge fraction |
| --- | --- | --- | --- | --- | --- | --- |
| `baseline__baseline__k500` | `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/5-matrix-baseline__baseline__k500` | `52.76s` | `501` | `408` | `158` | `0.6339` |
| `baseline__baseline__k1000` | `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/6-matrix-baseline__baseline__k1000` | `91.34s` | `1013` | `678` | `177` | `0.8037` |
| `baseline__cip0050__k500` | `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/8-matrix-baseline__cip0050__k500` | `62.29s` | `502` | `407` | `156` | `0.6344` |

## Notes

- `baseline__cip0050__k1000` was not executed in this pass.
- An incomplete directory was created during an interrupted earlier attempt: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine/output/7-matrix-baseline__cip0050__k500`.
- The current reward engine still lacks support for fee-layer scenarios (`CIP-0023`, `CIP-0082`) and dynamic pledge-linked saturation (`CIP-0037`).
