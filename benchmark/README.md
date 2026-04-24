# aerospike-py 벤치마크 최종 결론

> 측정 기간: 2026-04 | 10 VUs, 60초 (single mode 기준), k6 부하 테스트
> 비교 대상: **aerospike-py** (Rust/PyO3) vs **aerospike** 공식 Python client (C extension)
> 부하 앱: FastAPI + DLRM inference, batch_read 9 set × 200 keys per request

상세 측정값은 `results/` 하위 문서 참고.

---

## 1. aerospike-py vs 공식 Python client (Python 3.11 + GIL)

**같은 부하, 같은 서버, 같은 FastAPI 앱. 클라이언트만 교체하여 비교.**

| 지표 | aerospike-py | 공식 aerospike | aerospike-py 우위 |
|---|---:|---:|---:|
| single mode p95 (k6) | **189 ms** | 324 ms | **−42%** |
| single mode avg | **126 ms** | 188 ms | **1.49× faster** |
| single mode median | **101 ms** | 192 ms | **1.90× faster** |
| gather mode p95 | **234 ms** | 266 ms | **−12%** |
| FastAPI E2E p95 (서버 측정) | **202 ms** | 274 ms | **−26%** |

**결론**: 일반적인 production 조건(3.11 + GIL)에서 **p95 기준 1.5~1.7배 빠름**. 동시 호출(gather)에서도 우위 유지.

**원인**: 공식 C client 는 sync API 를 `loop.run_in_executor(ThreadPoolExecutor, ...)` 로 래핑해서 매 요청마다 스레드 풀 hop + GIL 획득/해제가 직렬화됨. aerospike-py 는 Rust/Tokio 네이티브 async → I/O 대기 중 GIL 해제 → 동시성 훨씬 잘 확보.

---

## 2. Free-threaded 환경 (Python 3.14t, GIL 제거)

**같은 하드웨어, 같은 앱, 같은 이미지(C client 를 소스 빌드해서 포함) — Python 런타임만 3.14t 로 교체.**

### 각 클라이언트의 자체 개선 (3.11 → 3.14t)

| 클라이언트 | p95 개선 | TPS 개선 |
|---|---:|---:|
| aerospike-py | 189 → **97 ms** (**−49%**) | 41.6 → **61.2 iter/s** (**+47%**) |
| 공식 aerospike | 324 → **128 ms** (**−60%**) | — |

GIL 을 공유 자원으로 놓고 경합하던 비용이 사라져서 **두 클라이언트 모두 큰 폭으로 개선**. aerospike-py 는 Rust 코드 변경 없이 Python 3.14t 런타임만 바꿔서 얻은 효과.

### 같은 3.14t 조건에서 클라이언트 간 비교

| 구성 | aerospike-py p95 | 공식 aerospike p95 | 차이 |
|---|---:|---:|---|
| 둘 다 같이 부하 (공정한 서버 부하) | 126 ms | 128 ms | **≈ 동등** (노이즈 수준) |
| 각각 단독 부하, 서버 독점 | **97 ms** | 134 ms | aerospike-py **−28%** |
| 단독 부하, gather mode | **107 ms** | 253 ms | aerospike-py **−58%** |

**결론**:
- **3.11 에 있던 42% latency 격차는 GIL 제거로 대부분 소멸** — 공동 부하 조건에서 두 클라이언트가 거의 동등.
- 단, 단독 부하(각각 서버를 독점하는 조건)에서는 **aerospike-py 가 여전히 28~58% 빠름** — 네이티브 async + lazy dict 변환 이점은 GIL 제거 후에도 잔존.
- Concurrency 가 올라갈수록(gather) 격차 확대 — 공식 client 가 여전히 `ThreadPoolExecutor` hop 을 타는 부분이 원인으로 추정.

---

## 3. aerospike-py 주요 성능 최적화 포인트

### 3.1 Rust/Tokio 네이티브 async (아키텍처)
- Python asyncio event loop 에서 바로 `await` 가능. 공식 client 처럼 `run_in_executor` 로 sync 를 감쌀 필요 없음.
- I/O 대기 중 GIL 해제 → 동일 이벤트 루프 안에서 다른 coroutine 이 CPU 점유 가능.

### 3.2 Lazy dict 변환 (`BatchReadHandle`)
- `batch_read()` 는 `Arc<Vec<BatchRecord>>` 를 wrap 한 handle 만 반환 (~10μs).
- Python dict 변환(`.as_dict()`)은 호출자가 필요할 때 수행 → 변환 비용을 event loop 스케줄링에 맞게 분산.

### 3.3 단일 FFI 경계로 batch 처리
- batch_read 전체를 **한 번의 FFI 호출** 안에서 완료. Python ↔ native 경계를 여러 번 넘나들지 않음.
- 공식 C extension 대비 경계 왕복 오버헤드 제거.

### 3.4 Stage profiling toggle — 프로덕션에서도 상시 활성 가능
- `AEROSPIKE_PY_INTERNAL_METRICS=1` 로 Rust 내부 10 단계 latency 측정.
- OFF 대비 E2E 오버헤드 **사실상 0** (노이즈 수준).
- 프로덕션에서 상시 켜두고 성능 회귀를 즉시 관측 가능.

### 3.5 `gather(9회)` → 단일 `batch_read(mixed keys)` 전환
- 9개 set 의 key 를 합쳐 batch_read 1회로 호출 (`mode=single`).
- GIL 하에서의 직렬화 병목(`key_parse` 9× 대기, `as_dict` 9× 순차 resume) 제거.
- 실측: p95 189ms → 126ms (**−33%**, 3.11 + GIL 기준).

### 3.6 Python 3.14t free-threaded 호환
- `#[pymodule(gil_used = true)]` 선언에도 3.14t 인터프리터가 GIL 재활성화하지 않음 → **Rust 코드 변경 없이** free-threaded 혜택 즉시 적용.
- 내부 구조가 이미 thread-safe (`ArcSwapOption`, `Arc<Vec<...>>`, atomic flags, `Mutex`-protected metrics registry).

---

## 4. 최종 권장 사항

| 순위 | 조치 | 예상 효과 |
|---|---|---|
| 1 | 공식 client 쓰는 기존 Python 앱을 **aerospike-py 로 교체** | p95 **−42%** (3.11 기준) |
| 2 | Python 런타임을 **3.14t free-threaded 로 전환** | p95 **−49%** 추가, TPS **+47%** (Rust 변경 불필요) |
| 3 | `gather(N회)` → 단일 `batch_read(mixed keys)` 패턴 적용 | GIL 하에서 p95 **−33%** |
| 4 | Stage profiling toggle 을 prod 에 **상시 ON** | 회귀 즉시 감지, 오버헤드 ≈ 0 |

합쳐 적용 시 **3.14t + aerospike-py + single batch_read** 로 p95 **97ms** 수준 달성 (원본 공식 + 3.11 대비 **약 3.3배 빠름**).
