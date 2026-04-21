#!/bin/bash
set -e

# ============================================================================
# One-shot script: download snapshot, start db-sync, wait for sync.
# Run from: spo-incentives/mainnet-indexer/
#
#   cd spo-incentives/mainnet-indexer && bash run.sh
# ============================================================================

DBSYNC_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DBSYNC_DIR"

echo "============================================"
echo "  Cardano db-sync — mainnet"
echo "  Directory: $DBSYNC_DIR"
echo "============================================"
echo ""

# --- Check Docker ---
if ! docker info &> /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Start Docker Desktop first."
    exit 1
fi
echo "[OK] Docker running"

# --- Check disk ---
AVAILABLE_GB=$(df -g "$HOME" 2>/dev/null | tail -1 | awk '{print $4}' || echo "?")
echo "[INFO] Disk available: ${AVAILABLE_GB} GB (need ~250 GB)"
echo ""

# --- Download snapshot if not present ---
SNAPSHOT_DIR="$DBSYNC_DIR/snapshots"
mkdir -p "$SNAPSHOT_DIR"

# Check for existing snapshot
EXISTING_SNAPSHOT=$(ls "$SNAPSHOT_DIR"/db-sync-snapshot*.tgz 2>/dev/null | head -1)

if [ -z "$EXISTING_SNAPSHOT" ]; then
    echo "Downloading db-sync 13.6 mainnet snapshot..."
    echo "This is ~78 GB and will take a while depending on your connection."
    echo ""

    # Latest 13.6 snapshot from IOG S3 bucket
    SNAPSHOT_URL="https://update-cardano-mainnet.iohk.io/cardano-db-sync/13.6/db-sync-snapshot-schema-13.6-block-13249206-x86_64.tgz"

    # Try to download
    if command -v curl &> /dev/null; then
        curl -L -o "$SNAPSHOT_DIR/snapshot.tgz" --progress-bar "$SNAPSHOT_URL" || {
            echo ""
            echo "Download failed. You can manually download a 13.6 snapshot from:"
            echo "  https://update-cardano-mainnet.iohk.io/cardano-db-sync/index.html#13.6/"
            echo ""
            echo "Place it in: $SNAPSHOT_DIR/"
            echo "Then re-run this script."
            exit 1
        }
        EXISTING_SNAPSHOT="$SNAPSHOT_DIR/snapshot.tgz"
    else
        echo "curl not found. Please download a snapshot manually from:"
        echo "  https://update-cardano-mainnet.iohk.io/cardano-db-sync/index.html#13.6/"
        echo "Place it in: $SNAPSHOT_DIR/"
        exit 1
    fi
    echo ""
    echo "[OK] Snapshot downloaded: $EXISTING_SNAPSHOT"
else
    echo "[OK] Snapshot found: $(basename "$EXISTING_SNAPSHOT")"
fi

# --- Set RESTORE_SNAPSHOT env var ---
# The path is relative to the container mount (/snapshots/)
SNAPSHOT_BASENAME=$(basename "$EXISTING_SNAPSHOT")
export RESTORE_SNAPSHOT="/snapshots/$SNAPSHOT_BASENAME"
echo "  RESTORE_SNAPSHOT=$RESTORE_SNAPSHOT"
echo ""

# --- Pull images ---
echo "Pulling Docker images (this may take a few minutes first time)..."
docker compose pull
echo ""

# --- Start ---
echo "Starting services..."
docker compose up -d
echo ""

echo "============================================"
echo "  Services started!"
echo "============================================"
echo ""
echo "Monitor progress:"
echo "  docker compose logs -f                      # all services"
echo "  docker compose logs -f cardano-db-sync      # db-sync only"
echo "  docker compose logs -f cardano-node         # node only"
echo ""
echo "Check sync status:"
echo "  docker compose exec postgres psql -U postgres -d cexplorer \\"
echo "    -c \"SELECT MAX(block_no) FROM block;\""
echo ""
echo "Connect to PostgreSQL:"
echo "  psql postgresql://postgres:delegator-analysis-2026@localhost:5433/cexplorer"
echo ""
echo "Once synced, the PostgreSQL endpoint is ready for downstream ingestion."
echo "Export the connection string before running any analysis pipeline:"
echo "  export DBSYNC_CONN_STR='postgresql://postgres:delegator-analysis-2026@localhost:5433/cexplorer'"
echo ""
echo "Timeline:"
echo "  - Mithril node bootstrap: ~30-90 min (automatic via mithril-bootstrap service)"
echo "  - DB-sync snapshot restore: ~30-60 min"
echo "  - Node sync to tip: ~1-3 hours after Mithril bootstrap"
echo "  - DB-sync catch-up: ~1-4 hours after node is synced"
echo ""

# --- Follow logs ---
echo "Following db-sync logs (Ctrl+C to detach, services keep running)..."
echo ""
docker compose logs -f cardano-db-sync
