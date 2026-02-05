#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

COUNT="${1:-1000}"
HOST="${AEROSPIKE_HOST:-127.0.0.1}"
PORT="${AEROSPIKE_PORT:-3000}"

echo "============================================"
echo "  aerospike-py Benchmark Suite"
echo "  count=$COUNT host=$HOST port=$PORT"
echo "============================================"

echo ""
echo ">>> Sync Benchmark"
python "$SCRIPT_DIR/bench_sync.py" --count "$COUNT" --host "$HOST" --port "$PORT"

echo ""
echo ">>> Async Benchmark"
python "$SCRIPT_DIR/bench_async.py" --count "$COUNT" --host "$HOST" --port "$PORT"

echo ""
echo "Done."
