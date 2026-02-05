#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

COUNT="${1:-1000}"
CONCURRENCY="${2:-50}"
HOST="${AEROSPIKE_HOST:-127.0.0.1}"
PORT="${AEROSPIKE_PORT:-3000}"

echo "============================================"
echo "  aerospike-py Benchmark Suite"
echo "  count=$COUNT concurrency=$CONCURRENCY"
echo "  host=$HOST port=$PORT"
echo "============================================"

python "$SCRIPT_DIR/bench_compare.py" \
  --count "$COUNT" \
  --concurrency "$CONCURRENCY" \
  --host "$HOST" \
  --port "$PORT"
