#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

COUNT="${1:-1000}"
ROUNDS="${2:-5}"
CONCURRENCY="${3:-50}"
HOST="${AEROSPIKE_HOST:-127.0.0.1}"
PORT="${AEROSPIKE_PORT:-3000}"

python "$SCRIPT_DIR/bench_compare.py" \
  --count "$COUNT" \
  --rounds "$ROUNDS" \
  --concurrency "$CONCURRENCY" \
  --host "$HOST" \
  --port "$PORT"
