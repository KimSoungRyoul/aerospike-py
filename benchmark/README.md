# Benchmark

Performance benchmarks comparing aerospike-py (Rust/PyO3) against the existing aerospike C client.

## Prerequisites

- Running Aerospike server (Docker recommended)
- aerospike-py installed (`maturin develop`)
- (Optional) aerospike C client: `pip install aerospike`

## Run

```bash
# All benchmarks (default 1000 ops)
bash benchmark/run_all.sh

# Custom count
bash benchmark/run_all.sh 5000

# Individual
python benchmark/bench_sync.py --count 1000
python benchmark/bench_async.py --count 1000 --concurrency 50
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AEROSPIKE_HOST` | `127.0.0.1` | Aerospike host |
| `AEROSPIKE_PORT` | `3000` | Aerospike port |

## Measured Operations

### Sync (`bench_sync.py`)

| Operation | Description |
|-----------|-------------|
| `put` | Single record write |
| `get` | Single record read |
| `batch_get` | Multi-record read (get_many) |
| `scan` | Full set scan |

### Async (`bench_async.py`)

| Operation | Description |
|-----------|-------------|
| `put_sequential` | Sequential async writes |
| `put_concurrent` | Concurrent writes (asyncio.gather) |
| `get_sequential` | Sequential async reads |
| `get_concurrent` | Concurrent reads (asyncio.gather) |
| `batch_get` | Batch read |
| `scan` | Full set scan |

## Metrics

- **avg_ms**: Average latency per operation
- **p50_ms**: Median latency
- **p99_ms**: 99th percentile latency
- **ops_per_sec**: Throughput (operations per second)
- **total_ms**: Total elapsed time

## Interpreting Results

- aerospike-py uses a Rust async runtime internally, so even sync operations benefit from efficient I/O
- The async benchmark shows the advantage of concurrent operations via `asyncio.gather`
- Batch operations (`get_many`) are more efficient than individual operations for bulk reads
