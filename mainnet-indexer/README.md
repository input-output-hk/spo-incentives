# Mainnet Indexer

A local Docker Compose stack that turns the Cardano mainnet chain into a
queryable PostgreSQL database. It is the data source that feeds the sub-flow
scripts under `spo-incentives/reward-system-spec/diagnostic/sub-flows/` and
any delegator/UTxO analysis pipeline that consumes `cexplorer` directly.

The stack bundles cardano-node (block producer follower), a Mithril bootstrap
step (to skip the multi-day cold sync of the node DB), cardano-db-sync (the
indexer that writes chain events into PostgreSQL), and PostgreSQL itself. Two
db-sync instances are defined — a pruned one for staking/delegation analysis
(no `tx_out` table) and a full one for UTxO analysis — each backed by a
separate Postgres.

## What it produces

Once synced, the stack exposes two independent PostgreSQL endpoints on the
host, both populated with the standard cardano-db-sync schema (database name
`cexplorer`):

| Instance | Host port | Schema | Purpose |
|---|---|---|---|
| Pruned | `localhost:5433` | No `tx_out` / `tx_in` | Delegation history, pool state, epoch stake, rewards |
| Full | `localhost:5434` | Complete schema incl. UTxO | Non-participant analysis (§5), UTxO-level studies |

The pruned instance is restored from an IOG snapshot (~78 GB compressed, ~150
GB restored). The full instance syncs from genesis and takes considerably
longer.

## Prerequisites

- Docker Desktop (or a compatible Docker engine) with the Compose plugin.
- ~300 GB of free disk for the pruned instance alone. Add ~200 GB if the full
  instance is also enabled.
- macOS on Apple Silicon is supported. `cardano-node` and the Mithril
  bootstrap step run natively on ARM64; `cardano-db-sync` currently has no
  ARM64 image and runs under Rosetta emulation (`platform: linux/amd64` in
  the compose file).

## Quick start

One-shot path (downloads snapshot, starts the pruned stack, follows logs):

```bash
cd spo-incentives/mainnet-indexer
bash run.sh
```

Interactive path (creates an external runtime directory at
`/Users/nhenin/dev/local-infra/cardano-dbsync` with convenience scripts —
`start.sh`, `stop.sh`, `status.sh`, `connect.sh`):

```bash
bash spo-incentives/mainnet-indexer/setup.sh
```

To bring up the optional full instance alongside the pruned one:

```bash
docker compose --profile full up -d
```

## Components

The compose file declares five services:

- `postgres` — Postgres 17, tuned for ~4 GB shared memory, exposed on
  `5433`.
- `mithril-bootstrap` — one-shot container that downloads the latest mainnet
  Mithril snapshot into the `node-db` volume so that `cardano-node` does not
  need to sync from genesis. Skips itself on subsequent runs when the
  snapshot is already present.
- `cardano-node` — 10.6.2, native ARM64, reads from the pre-populated
  `node-db` volume and exposes an IPC socket on the `node-ipc` volume.
- `cardano-db-sync` — 13.6.0.4 pruned instance, depends on a healthy
  `cardano-node` and `postgres`, restores from a snapshot placed under
  `./snapshots/` when `RESTORE_SNAPSHOT` is set.
- `cardano-db-sync-full` + `postgres-full` — the full-schema pair, gated
  behind the `full` profile so that `docker compose up -d` alone does not
  start them.

Secrets (`postgres_user`, `postgres_password`, `postgres_db`) are mounted from
files under `./secrets/`. `setup.sh` generates a random password on first
run; `run.sh` assumes the secrets are already in place.

## Snapshots

The `snapshots/` directory holds the db-sync snapshot archive that
`cardano-db-sync` restores at startup. Two helper scripts are provided:

- `snapshots/download_snapshot.sh` — single-shot curl download.
- `snapshots/download_resilient.sh` — resumable download with retries, for
  flaky connections.

The IOG snapshot index lives at
<https://update-cardano-mainnet.iohk.io/cardano-db-sync/index.html#13.6/> —
check it before running the download scripts, since the filename in `run.sh`
is pinned to a specific block and may age out.

Snapshots are consumed via the container mount point `/snapshots/`. The
`RESTORE_SNAPSHOT` env var must use that container path (e.g.
`/snapshots/db-sync-snapshot-schema-13.6-block-13249206-x86_64.tgz`), not a
host path.

## Sync timeline

| Stage | Duration |
|---|---|
| Mithril bootstrap of node DB | 30-90 min |
| DB-sync snapshot restore | 30-60 min |
| Node catch-up to tip | 1-3 h after bootstrap |
| DB-sync catch-up to tip | 1-4 h after node is synced |

With a fresh snapshot the pruned instance is queryable in 3-8 hours on a
typical home connection. Without a snapshot, db-sync from genesis takes
3-5 days.

## Connecting

The connection string is written to
`/Users/nhenin/dev/local-infra/cardano-dbsync/connection_string.txt` by
`setup.sh`. The downstream ingestion scripts read it via the
`DBSYNC_CONN_STR` environment variable:

```bash
export DBSYNC_CONN_STR="$(cat /Users/nhenin/dev/local-infra/cardano-dbsync/connection_string.txt)"
```

For ad-hoc psql access:

```bash
psql -h localhost -p 5433 -U postgres -d cexplorer
```

## Reset and teardown

Stopping the containers preserves all volumes:

```bash
docker compose down
```

Wiping everything (node DB, both Postgres clusters, db-sync state) requires
removing the named volumes explicitly:

```bash
docker compose down -v
```

Note that `down -v` deletes ~150-300 GB of on-disk data; the next start
will re-bootstrap from Mithril and re-restore the snapshot.

## Troubleshooting

- **`cardano-db-sync` exits with a schema mismatch.** The snapshot's schema
  version must match the db-sync image version. The current pairing is
  schema 13.6 with image 13.6.0.4. If IOG publishes a newer snapshot, also
  bump the image tag in `docker-compose.yml`.
- **Mithril bootstrap hangs.** Check that outbound HTTPS to
  `aggregator.release-mainnet.api.mithril.network` is not blocked.
- **`postgres_password` permission denied.** Docker on macOS occasionally
  loses secret-file permissions after a host reboot; re-run
  `chmod 600 secrets/*`.
- **Port 5433/5434 already in use.** Edit the `ports` mapping in the
  corresponding Postgres service; the container side stays at `5432`.

## Last synced

Compose file pinned to cardano-node `10.6.2` and cardano-db-sync `13.6.0.4`
on 2026/04/15. The Mithril client version is pinned to `2603.1` in the
bootstrap script.
