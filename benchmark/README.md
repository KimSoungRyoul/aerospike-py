# Benchmark: aerospike-py vs Official aerospike (C Client)

aerospike-py (Rust/PyO3)가 공식 aerospike Python client (C extension)보다 얼마나 빠른지 측정합니다.

## Methodology

일관된 결과를 위해 다음을 적용합니다:

1. **Warmup** (기본 200회) - 커넥션 풀, 서버 캐시 안정화 후 측정 시작
2. **Multiple rounds** (기본 5회) - 라운드별 median을 구한 뒤 median-of-medians 보고
3. **데이터 분리** - read 벤치마크 전 데이터를 미리 seed, put은 독립 측정
4. **GC 비활성화** - 측정 구간에서 Python GC off
5. **키 격리** - 각 client가 고유 prefix 사용, 서로 간섭 없음

## Comparison Targets

| Column | Client | Description |
| ------ | ------ | ----------- |
| aerospike-py (Rust) | `aerospike.Client` | Rust 기반 sync client |
| official aerospike (C) | `aerospike.client` (PyPI) | 공식 C extension sync client |
| aerospike-py async (Rust) | `aerospike.AsyncClient` | Rust 기반 async + `asyncio.gather` |

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
# 기본 (1000 ops x 5 rounds, concurrency 50)
bash benchmark/run_all.sh

# 커스텀: count rounds concurrency
bash benchmark/run_all.sh 2000 7 100

# 직접 실행
python benchmark/bench_compare.py --count 1000 --rounds 5 --warmup 200 --concurrency 50
```

## Output

```text
Benchmark config:
  ops/round  = 1,000
  rounds     = 5
  warmup     = 200
  concurrency= 50

====================================================================================================
  aerospike-py Benchmark  (1,000 ops x 5 rounds, warmup=200, async concurrency=50)
====================================================================================================

  Avg Latency (ms)  —  lower is better  [median of round means]
  ──────────────────────────────────────────────────────────────────────────────
  Operation    |   aerospike-py (Rust) | official aerospike (C) |   aerospike-py async |     Rust vs C |    Async vs C
  put          |              0.310ms  |               0.580ms  |              0.041ms | 1.9x faster   | 14.1x faster
  get          |              0.195ms  |               0.398ms  |              0.028ms | 2.0x faster   | 14.2x faster
  batch_get    |              0.044ms  |               0.088ms  |              0.031ms | 2.0x faster   |  2.8x faster
  scan         |              0.011ms  |               0.030ms  |              0.009ms | 2.7x faster   |  3.3x faster

  Stability (stdev of round median latency, ms)  —  lower = more stable
  ──────────────────────────────────────────────────────────────────────────────
  Operation    |            Rust stdev |              C stdev  |         Async stdev
  put          |              0.008ms  |              0.015ms  |              0.003ms
  get          |              0.005ms  |              0.012ms  |              0.002ms
```

## Metrics

| Metric | Description |
| ------ | ----------- |
| avg_ms | median of round means (낮을수록 좋음) |
| p50_ms | median of round medians |
| p99_ms | aggregated 99th percentile |
| ops_per_sec | median of round throughputs (높을수록 좋음) |
| stdev_ms | 라운드 간 median 편차 (낮을수록 안정적) |
| Rust vs C | aerospike-py sync이 C client 대비 몇 배 빠른지 |
| Async vs C | aerospike-py async가 C client 대비 몇 배 빠른지 |

## Environment Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `AEROSPIKE_HOST` | `127.0.0.1` | Aerospike host |
| `AEROSPIKE_PORT` | `3000` | Aerospike port |

## Why Faster?

- **Rust async runtime**: 내부적으로 Tokio 기반 비동기 I/O
- **Zero-copy**: PyO3를 통한 효율적인 Python-Rust 타입 변환
- **Native async**: `AsyncClient` + `asyncio.gather`로 수천 개 동시 요청
- **No GIL bottleneck**: Rust 코드 실행 중 GIL 해제 (`py.allow_threads`)
