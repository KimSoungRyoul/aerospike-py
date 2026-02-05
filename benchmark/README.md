# Benchmark: aerospike-py vs Official aerospike (C Client)

aerospike-py (Rust/PyO3)가 공식 aerospike Python client (C extension)보다 얼마나 빠른지 측정합니다.

3개 클라이언트를 한 테이블에서 비교합니다:

| Column | Client | Description |
| ------ | ------ | ----------- |
| aerospike-py (Rust) | `aerospike.Client` | Rust 기반 sync client |
| official aerospike (C) | `aerospike.client` (PyPI) | 공식 C extension sync client |
| aerospike-py async (Rust) | `aerospike.AsyncClient` | Rust 기반 async client + `asyncio.gather` |

## Prerequisites

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
# 기본 (1000 ops, concurrency 50)
bash benchmark/run_all.sh

# ops 수, concurrency 지정
bash benchmark/run_all.sh 5000 100

# 직접 실행
python benchmark/bench_compare.py --count 1000 --concurrency 50
```

## Output Example

```text
==========================================================================================
  aerospike-py Benchmark  (1,000 ops, async concurrency=50)
==========================================================================================

  Avg Latency (ms)  —  lower is better
  ──────────────────────────────────────────────────────────────────────────────────
  Operation    |   aerospike-py (Rust) | official aerospike (C) |   aerospike-py async |     Rust vs C |    Async vs C
  ──────────────────────────────────────────────────────────────────────────────────
  put          |              0.312ms  |               0.587ms  |              0.041ms | 1.9x faster   | 14.3x faster
  get          |              0.198ms  |               0.401ms  |              0.029ms | 2.0x faster   | 13.8x faster
  batch_get    |              0.045ms  |               0.089ms  |              0.032ms | 2.0x faster   |  2.8x faster
  scan         |              0.012ms  |               0.031ms  |              0.010ms | 2.6x faster   |  3.1x faster

  Throughput (ops/sec)  —  higher is better
  ──────────────────────────────────────────────────────────────────────────────────
  Operation    |   aerospike-py (Rust) | official aerospike (C) |   aerospike-py async |     Rust vs C |    Async vs C
  ──────────────────────────────────────────────────────────────────────────────────
  put          |            3,205/s    |            1,703/s     |           24,390/s   | 1.9x faster   | 14.3x faster
  get          |            5,050/s    |            2,493/s     |           34,482/s   | 2.0x faster   | 13.8x faster
  batch_get    |           22,222/s    |           11,235/s     |           31,250/s   | 2.0x faster   |  2.8x faster
  scan         |           83,333/s    |           32,258/s     |          100,000/s   | 2.6x faster   |  3.1x faster
```

## Metrics

| Metric | Description |
| ------ | ----------- |
| avg_ms | 평균 latency (낮을수록 좋음) |
| p50_ms | 중간값 latency |
| p99_ms | 99th percentile latency |
| ops_per_sec | 초당 처리량 (높을수록 좋음) |
| Rust vs C | aerospike-py sync이 C client 대비 몇 배 빠른지 |
| Async vs C | aerospike-py async가 C client 대비 몇 배 빠른지 |

## Environment Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `AEROSPIKE_HOST` | `127.0.0.1` | Aerospike host |
| `AEROSPIKE_PORT` | `3000` | Aerospike port |

## Why Faster?

- **Rust async runtime**: 내부적으로 Tokio 기반 비동기 I/O
- **Zero-copy**: PyO3를 통한 효율적인 Python ↔ Rust 타입 변환
- **Native async**: `AsyncClient` + `asyncio.gather`로 수천 개 동시 요청
- **No GIL bottleneck**: Rust 코드 실행 중 GIL 해제 (`py.allow_threads`)
