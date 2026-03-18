# CIP Scenario Matrix

Canonical first-pass scenario matrix for SPO incentive evaluation.

Scope:
- Baseline `K`: `500`
- High `K`: `1000`
- Baseline `a0`: `0.3`
- Note: First-pass canonical matrix limited to current K vs K=1000. K=750 is intentionally excluded from this matrix.

## Canonical matrix

| Scenario ID | Fee rule | Stake-cap rule | K | Support in current reward engine | Notes |
| --- | --- | --- | --- | --- | --- |
| baseline__baseline__k500 | baseline | baseline | 500 | supported | Direct status-quo mapping. |
| baseline__baseline__k1000 | baseline | baseline | 1000 | supported | Direct status-quo mapping. |
| baseline__cip0050__k500 | baseline | cip0050 | 500 | supported | Mapped to CIP50RSS in the current rewards-sharing engine. |
| baseline__cip0050__k1000 | baseline | cip0050 | 1000 | supported | Mapped to CIP50RSS in the current rewards-sharing engine. |
| baseline__cip0037__k500 | baseline | cip0037 | 500 | unsupported | Dynamic pledge-linked saturation is not implemented in the current rewards-sharing engine. |
| baseline__cip0037__k1000 | baseline | cip0037 | 1000 | unsupported | Dynamic pledge-linked saturation is not implemented in the current rewards-sharing engine. |
| cip0023__baseline__k500 | cip0023 | baseline | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0023__baseline__k1000 | cip0023 | baseline | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0023__cip0050__k500 | cip0023 | cip0050 | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0023__cip0050__k1000 | cip0023 | cip0050 | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0023__cip0037__k500 | cip0023 | cip0037 | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0023__cip0037__k1000 | cip0023 | cip0037 | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__baseline__k500 | cip0082 | baseline | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__baseline__k1000 | cip0082 | baseline | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__cip0050__k500 | cip0082 | cip0050 | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__cip0050__k1000 | cip0082 | cip0050 | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__cip0037__k500 | cip0082 | cip0037 | 500 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |
| cip0082__cip0037__k1000 | cip0082 | cip0037 | 1000 | unsupported | The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost. |

## Governance bundles

| Bundle | Preferred scenario(s) | Stress-test scenario(s) | Notes |
| --- | --- | --- | --- |
| Stability-first incrementalism | `cip0023__baseline__k500` | `cip0023__baseline__k1000` | Keep K at the current level for the primary decision; use K=1000 as a pressure test, not as the default rollout. |
| Viability-first egalitarianism | `cip0082__cip0050__k500` | `cip0082__cip0050__k1000` | Pair fee reform with a moderate leverage guardrail before considering K expansion. |
| Security-first skin-in-the-game | `baseline__cip0050__k500` | `baseline__cip0037__k500`, `baseline__cip0050__k1000` | Use CIP-0050 as the canonical stake-cap scenario today; keep CIP-0037 as an advanced comparison because it needs extra simulator work. |

## Supported reward-engine commands

Target engine path: `/Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine`

### `baseline__baseline__k500`

```bash
cd /Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine
.venv/bin/python main.py --n=1000 --k=500 --a0=0.3 --reward_scheme=0 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__baseline__k500 --no-generate_graphs
```

### `baseline__baseline__k1000`

```bash
cd /Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine
.venv/bin/python main.py --n=1000 --k=1000 --a0=0.3 --reward_scheme=0 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__baseline__k1000 --no-generate_graphs
```

### `baseline__cip0050__k500`

```bash
cd /Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine
.venv/bin/python main.py --n=1000 --k=500 --a0=0.3 --reward_scheme=4 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__cip0050__k500 --no-generate_graphs --L=100
```

### `baseline__cip0050__k1000`

```bash
cd /Users/nhenin/dev/ARC/stream-SPO/Rewards-Sharing-Simulation-Engine
.venv/bin/python main.py --n=1000 --k=1000 --a0=0.3 --reward_scheme=4 --max_iterations=200 --iterations_after_convergence=10 --seed=42 --execution_id=matrix-baseline__cip0050__k1000 --no-generate_graphs --L=100
```

## Unsupported scenarios

- `baseline__cip0037__k500`: Dynamic pledge-linked saturation is not implemented in the current rewards-sharing engine.
- `baseline__cip0037__k1000`: Dynamic pledge-linked saturation is not implemented in the current rewards-sharing engine.
- `cip0023__baseline__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0023__baseline__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0023__cip0050__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0023__cip0050__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0023__cip0037__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0023__cip0037__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__baseline__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__baseline__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__cip0050__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__cip0050__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__cip0037__k500`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.
- `cip0082__cip0037__k1000`: The current rewards-sharing engine does not model the Cardano ledger fee-layer changes behind minPoolMargin/minPoolRate/minPoolCost.

