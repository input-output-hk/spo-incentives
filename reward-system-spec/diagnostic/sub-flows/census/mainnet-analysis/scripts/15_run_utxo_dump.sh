#!/usr/bin/env bash
# 15_run_utxo_dump.sh
# Dump the full UTxO set via cardano-cli inside the node container.
#
# The node socket is at /ipc/node.socket inside the cardano-node container.
# cardano-cli runs inside the container and writes the JSON to /data/ (the
# node-db volume), which we then docker-cp out.
#
# Usage:
#   cd spo-incentives/mainnet-indexer
#   bash ../../report/sub-flows/census/mainnet-analysis/scripts/15_run_utxo_dump.sh
#
# Output:
#   /tmp/utxo_whole.json  (on host — large file, 10-30 GB)

set -euo pipefail

CONTAINER="dbsync-cardano-node-1"
SOCKET="/ipc/node.socket"
DUMP_PATH="/data/utxo_whole.json"

echo "=== UTxO dump via cardano-cli ==="
echo ""

# 1. Check node is running and socket exists
echo "Checking node socket..."
if ! docker exec "$CONTAINER" test -S "$SOCKET" 2>/dev/null; then
    echo "ERROR: Node socket not found at $SOCKET"
    echo "       Node is still validating ImmutableDB. Wait for validation to complete."
    echo ""
    echo "Check progress with:"
    echo "  docker compose logs cardano-node --tail=3"
    exit 1
fi

# 2. Check node is synced (tip should be recent)
echo "Checking node sync status..."
TIP=$(docker exec -e CARDANO_NODE_SOCKET_PATH="$SOCKET" "$CONTAINER" \
    cardano-cli query tip --mainnet 2>&1) || {
    echo "ERROR: cardano-cli query tip failed:"
    echo "$TIP"
    exit 1
}
echo "Node tip:"
echo "$TIP" | head -10
echo ""

# 3. Dump UTxO — this is the slow part (5-15 minutes)
echo "Starting UTxO dump (this takes 5-15 minutes on mainnet)..."
echo "Writing to $DUMP_PATH inside container..."
START=$(date +%s)

docker exec -e CARDANO_NODE_SOCKET_PATH="$SOCKET" "$CONTAINER" \
    cardano-cli query utxo --whole-utxo --mainnet --out-file "$DUMP_PATH" || {
    echo "ERROR: UTxO dump failed"
    exit 1
}

END=$(date +%s)
ELAPSED=$((END - START))
echo "  Done in ${ELAPSED}s"

# 4. Check file size inside container
SIZE=$(docker exec "$CONTAINER" du -h "$DUMP_PATH" | cut -f1)
echo "  File size: $SIZE"

# 5. Copy to host
echo "Copying to host /tmp/utxo_whole.json ..."
docker cp "$CONTAINER:$DUMP_PATH" /tmp/utxo_whole.json
echo "  Done."

# 6. Clean up inside container
docker exec "$CONTAINER" rm -f "$DUMP_PATH"

echo ""
echo "=== Next step ==="
echo "Run the Python classifier:"
echo "  cd spo-incentives/report/sub-flows/census/mainnet-analysis/scripts"
echo "  python3 15_utxo_from_cli.py /tmp/utxo_whole.json"
