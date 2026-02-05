# Benchmark: aerospike-py vs Official C Client

aerospike-py (Rust/PyO3)가 공식 aerospike Python client (C extension)보다 얼마나 빠른지 측정합니다.

## Prerequisites

- Running Aerospike server (Docker)
- aerospike-py installed: `maturin develop`
- **Official C client installed: `pip install aerospike`** (비교 대상)

```bash
# Aerospike server
docker run -d --name aerospike \
  -p 3000:3000 \
  -e "NAMESPACE=test" \
  -e "CLUSTER_NAME=docker" \
  aerospike/aerospike-server

# Install both clients
maturin develop              # aerospike-py (Rust)
pip install aerospike        # official C client
```

## Run

```bash
# 전체 벤치마크 (기본 1000 ops)
bash benchmark/run_all.sh

# ops 수 지정
bash benchmark/run_all.sh 5000

# 개별 실행
python benchmark/bench_sync.py --count 1000
python benchmark/bench_async.py --count 1000 --concurrency 50
```

## What's Measured

### `bench_sync.py` - Sync 1:1 비교

동일 조건에서 aerospike-py `Client` vs 공식 C client를 직접 비교:

| Operation | Description |
|-----------|-------------|
| put | 단일 레코드 쓰기 |
| get | 단일 레코드 읽기 |
| batch_get | 다중 레코드 읽기 (get_many) |
| scan | 전체 set 스캔 |

출력 예시:
```
  Avg Latency (ms) - lower is better
  ────────────────────────────────────────────────────────────
  Operation    |   aerospike-py |     official C |        Speedup
  ────────────────────────────────────────────────────────────
  put          |        0.312ms |        0.587ms |   1.88x faster
  get          |        0.198ms |        0.401ms |   2.03x faster
  batch_get    |        0.045ms |        0.089ms |   1.98x faster
  scan         |        0.012ms |        0.031ms |   2.58x faster
```

### `bench_async.py` - Async 성능 비교

공식 C client는 async API가 없으므로:
1. **Sequential 비교**: aerospike-py async (순차) vs C client sync (순차)
2. **Concurrency 이점**: aerospike-py의 `asyncio.gather` 동시 실행 성능

| Operation | Description |
|-----------|-------------|
| put/get (seq) | 순차 실행 latency/throughput 비교 |
| put/get (conc) | asyncio.gather 동시 실행 throughput |
| batch_get | 배치 읽기 throughput 비교 |

## Metrics

| Metric | Description |
|--------|-------------|
| **avg_ms** | 평균 latency (낮을수록 좋음) |
| **p50_ms** | 중간값 latency |
| **p99_ms** | 99th percentile latency |
| **ops_per_sec** | 초당 처리량 (높을수록 좋음) |
| **Speedup** | aerospike-py가 C client 대비 몇 배 빠른지 |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AEROSPIKE_HOST` | `127.0.0.1` | Aerospike host |
| `AEROSPIKE_PORT` | `3000` | Aerospike port |

## Why Faster?

- **Rust async runtime**: 내부적으로 Tokio 기반 비동기 I/O 사용
- **Zero-copy where possible**: PyO3를 통한 효율적인 Python ↔ Rust 타입 변환
- **Native async**: `AsyncClient`는 Python asyncio와 직접 통합, `asyncio.gather`로 수천 개 동시 요청 가능
- **No GIL bottleneck**: Rust 코드 실행 중 GIL 해제 (`py.allow_threads`)
