# Analysis of Cardano's Incentive Mechanism

This repository hosts the ongoing analysis of Cardano's reward and delegation
mechanism, along with the local infrastructure needed to reproduce the
empirical work. It serves as the central hub for community feedback on the
incentive design and on the proposed successor specification.

The work is organised in three self-contained folders, each with its own
README.

## 📘 [`reward-system-spec/`](reward-system-spec/README.md) — The V2 Specification

The current centerpiece of the repository: *The Cardano Reward System V2 —
Specification for a Sustainable Successor*. It is a long-form monograph in
three acts:

- **Diagnostic** — empirical analysis of the current mainnet mechanism,
  grounded in on-chain data (pool concentration, pledge dilution, delegator
  mobility, reward flow).
- **The Intended Game** — the theoretical frame Cardano's reward design was
  built on (Brünjes & Kiayias 2020; Kiayias et al. 2021, 2024) and the
  equilibrium it targets.
- **V2 Specification** — the constitutional, microeconomic, macroeconomic,
  and evaluation requirements for a successor mechanism that restores the
  intended properties.

Start here: [`reward-system-spec/README.md`](reward-system-spec/README.md).

## 📄 [`report-november-2025/`](report-november-2025/) — The Original Report

The LaTeX source and supporting data for "Analysis of Cardano's Incentive
Mechanism" (November 2025) — the first public iteration of this work. The V2
specification in `reward-system-spec/` supersedes its prescriptive parts but
the empirical appendices remain useful as a snapshot.

Appendices:

- [Appendix A](report-november-2025/appendixA.txt) — pool viability analysis
  over epochs 548–583.
- [Appendix B](report-november-2025/appendixB.csv) — per-epoch pool-level
  delegation, block production, reward, and owner-stake data.
- [Appendix C](report-november-2025/appendixC.txt) — pledge analysis.

## ⚙️ [`mainnet-indexer/`](mainnet-indexer/README.md) — Local Infrastructure

A Docker Compose stack that turns the Cardano mainnet chain into a queryable
PostgreSQL database (cardano-node + Mithril bootstrap + cardano-db-sync +
Postgres). It is the data source behind every empirical claim in
`reward-system-spec/diagnostic/`, and the entry point for anyone who wants
to reproduce or extend the analysis locally.

See [`mainnet-indexer/README.md`](mainnet-indexer/README.md) for setup,
sync timelines, and connection details.

## 📣 Community Feedback

This repository is the official hub for gathering community input on the
incentive mechanism and the V2 proposal. Stake Pool Operators, ada holders,
DReps, and anyone who cares about the incentive design are invited to join
the [discussion](https://github.com/input-output-hk/spo-incentives/discussions).

## Code of Conduct

Interactions in this repository follow the terms of the
[Code of Conduct](CODE_OF_CONDUCT.md).
