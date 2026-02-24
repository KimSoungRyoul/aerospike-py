# Async Architecture Comparison: aerospike-py vs Official Python Client

공식 Aerospike Python Client의 async 방식과 aerospike-py의 async 방식에 대한 아키텍처 비교 및 성능 분석 문서.

---

## 1. Async 아키텍처 비교

### 1.1 공식 Aerospike Python Client — `run_in_executor` 패턴

공식 Python 클라이언트는 C 확장 모듈 기반이며, 내부적으로 **동기 블로킹 API**만 제공한다.
async 지원은 Python 레벨에서 `asyncio.loop.run_in_executor()`를 사용하여 블로킹 호출을 스레드풀로 위임하는 방식이다.

```python
# 공식 클라이언트의 async 패턴 (개념 코드)
import asyncio
import aerospike

class AsyncAerospikeClient:
    def __init__(self, config):
        self._client = aerospike.client(config).connect()
        self._loop = asyncio.get_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)

    async def get(self, key):
        # 동기 블로킹 호출을 스레드풀로 위임
        return await self._loop.run_in_executor(
            self._executor,
            self._client.get,  # C 확장 동기 함수
            key
        )

    async def put(self, key, bins):
        return await self._loop.run_in_executor(
            self._executor,
            self._client.put,
            key, bins
        )
```

**호출 흐름:**
```
Python asyncio → ThreadPoolExecutor.submit() → OS Thread 생성/재사용
→ GIL 획득 → C 확장 진입 → GIL 해제 → 동기 네트워크 I/O (블로킹)
→ GIL 재획득 → C→Python 결과 변환 → Future.set_result()
→ asyncio 이벤트 루프로 결과 전달
```

### 1.2 aerospike-py — Rust Tokio `future_into_py` 패턴

aerospike-py는 Rust의 Tokio async 런타임을 직접 활용한다.
PyO3의 `pyo3_async_runtimes::tokio::future_into_py`를 통해 Rust Future를 Python awaitable로 변환한다.

```rust
// aerospike-py의 실제 구현 (rust/src/async_client.rs)
fn get<'py>(
    &self,
    py: Python<'py>,
    key: &Bound<'_, PyAny>,
    policy: Option<&Bound<'_, PyDict>>,
) -> PyResult<Bound<'py, PyAny>> {
    let client = self.get_client()?;
    let args = client_common::prepare_get_args(py, key, policy, &self.connection_info)?;

    // Python 키를 미리 변환 (I/O 이후 Rust→Python 재변환 방지)
    let key_py = key_to_py(py, &args.key)?;

    let rp = args.read_policy().clone();
    // Rust Future를 Python awaitable로 직접 변환
    future_into_py(py, async move {
        let record = client.get(&rp, &args.key, Bins::All).await?;
        Python::attach(|py| record_to_py_with_key(py, &record, key_py))
    })
}
```

```python
# Python 측 사용법 (동일한 인터페이스)
import aerospike_py

async def main():
    client = await aerospike_py.AsyncClient(config).connect()
    record = await client.get(key)  # Rust Future가 직접 await됨
```

**호출 흐름:**
```
Python asyncio → PyO3 future_into_py() → Tokio 런타임에 Future 등록
→ GIL 즉시 해제 → Tokio epoll/kqueue 비동기 I/O (논블로킹)
→ I/O 완료 시 GIL 획득 → Rust→Python 결과 변환
→ Python Future.set_result() → asyncio 이벤트 루프로 결과 전달
```

---

## 2. 성능 차이 발생 지점

### 2.1 스레드 오버헤드 vs Zero-Thread I/O

| 구분 | 공식 클라이언트 (`run_in_executor`) | aerospike-py (`future_into_py`) |
|------|-----------------------------------|---------------------------------|
| I/O 모델 | 스레드풀 기반 블로킹 I/O | Tokio epoll/kqueue 논블로킹 I/O |
| 스레드 생성 | 요청당 OS 스레드 할당 필요 | 스레드 생성 없음 (Tokio 워커 재사용) |
| 컨텍스트 스위칭 | OS 스레드 간 전환 발생 | 코루틴 전환만 발생 (userspace) |
| 스레드 스택 메모리 | ~8MB per thread (기본) | ~수 KB per task |
| 동시 요청 한계 | ThreadPoolExecutor max_workers 제한 | 수만 개 동시 태스크 가능 |

**핵심:** `run_in_executor`는 매 async 호출마다 OS 스레드를 점유한다. 스레드풀 크기(기본 `min(32, cpu_count + 4)`)를 초과하면 대기열이 발생한다. 반면 Tokio는 소수의 워커 스레드에서 수천 개의 Future를 멀티플렉싱한다.

```
[공식 클라이언트: 1000 동시 요청]

Thread-1  ████████░░░░░░░░  (블로킹 I/O 대기)
Thread-2  ░░████████░░░░░░  (블로킹 I/O 대기)
Thread-3  ░░░░████████░░░░  (블로킹 I/O 대기)
...
Thread-16 ░░░░░░░░████████  (블로킹 I/O 대기)
Thread-17 대기열에서 대기...  (스레드풀 포화)
~Thread-1000 대기열에서 대기...

→ 16개 스레드 = 16개 동시 I/O, 나머지 984개는 큐에서 대기


[aerospike-py: 1000 동시 요청]

Tokio Worker-1  ╠═Task-1═╣╠═Task-5═╣╠═Task-9═╣...   (이벤트 루프)
Tokio Worker-2  ╠═Task-2═╣╠═Task-6═╣╠═Task-10═╣...  (이벤트 루프)
Tokio Worker-3  ╠═Task-3═╣╠═Task-7═╣╠═Task-11═╣...  (이벤트 루프)
Tokio Worker-4  ╠═Task-4═╣╠═Task-8═╣╠═Task-12═╣...  (이벤트 루프)

→ 4개 워커에서 1000개 태스크 동시 처리 (I/O 대기 시 다른 태스크 실행)
```

### 2.2 GIL 경합 패턴

| 구분 | 공식 클라이언트 | aerospike-py |
|------|----------------|-------------|
| GIL 획득 횟수/요청 | 최소 3회 (submit → C 진입 → 결과 반환) | 2회 (인자 파싱 → 결과 반환) |
| GIL 보유 시간 | C 확장 진입/퇴출 시 반복 획득 | I/O 중 GIL 완전 해제 |
| 고동시성 GIL 경합 | 심각 (스레드 수 = GIL 경쟁자 수) | 최소 (Tokio 워커만 경쟁) |

**상세 분석:**

```
[공식 클라이언트 — GIL 타임라인 (1개 요청)]

asyncio loop:  ──GIL──┐
                       │ executor.submit()
Thread-N:              └──GIL 대기──GIL 획득──C진입──GIL해제──I/O──GIL획득──변환──GIL해제──┐
asyncio loop:                                                                           └──GIL──결과처리

총 GIL 전환: 3~4회, 스레드 간 GIL 핸드오프 포함


[aerospike-py — GIL 타임라인 (1개 요청)]

asyncio loop:  ──GIL──┐
                       │ future_into_py() 호출, 인자 파싱
                       │ GIL 해제, Tokio에 Future 등록
Tokio:                 └──────────비동기 I/O (GIL 없음)──────────┐
                                                                  │ I/O 완료
asyncio loop:  ──────────────────────────────────────GIL 획득──결과변환──GIL해제

총 GIL 전환: 2회, 스레드 간 핸드오프 없음
```

`run_in_executor`에서는 N개의 스레드풀 스레드가 모두 GIL 경쟁자가 된다. 반면 aerospike-py의 `future_into_py`에서는 결과 변환 시점에만 GIL을 잠시 획득하므로, GIL 경합이 동시 요청 수에 비례하여 증가하지 않는다.

### 2.3 Python ↔ Native 경계 횟수

| 구분 | 공식 클라이언트 | aerospike-py |
|------|----------------|-------------|
| 경계 횟수/요청 | 4회 | 2회 |
| 경계 오버헤드 | Python→C→Python→C→Python | Python→Rust→Python |

```
[공식 클라이언트 — 경계 횟수]

① Python → C (executor.submit → 동기 함수 호출)
② C → Python (ctypes/cffi 콜백, 에러 핸들링)
③ Python → C (결과 역직렬화를 위한 C 버퍼 접근)
④ C → Python (최종 결과 반환)

추가: run_in_executor 자체의 Python 레이어 오버헤드
     - concurrent.futures.Future 생성
     - threading 동기화 프리미티브


[aerospike-py — 경계 횟수]

① Python → Rust (PyO3 인자 파싱, future_into_py 호출)
   → Tokio에서 순수 Rust 비동기 I/O 수행 (경계 없음)
② Rust → Python (결과를 Python 객체로 변환, Future 완료)

※ PyO3의 제로카피 최적화로 경계 비용 자체도 낮음
```

### 2.4 Serialization / Deserialization

| 구분 | 공식 클라이언트 | aerospike-py |
|------|----------------|-------------|
| 직렬화 레이어 | Python dict → C struct → wire format | Python dict → Rust struct → wire format |
| 역직렬화 레이어 | wire format → C struct → Python dict | wire format → Rust struct → Python dict |
| 중간 복사 | C 힙 할당 + Python 힙 할당 (2벌) | Rust 스택/힙 → Python 힙 (1벌, 최적화 가능) |
| 문자열 처리 | C char* → Python str (복사) | Rust &str → Python str (PyO3 intern 활용) |
| 정수 처리 | C long → Python int (boxing) | Rust i64 → Python int (PyO3 직접 변환) |
| dict 키 intern | 미지원 | `intern!()` 매크로로 "gen", "ttl" 등 캐싱 |

**aerospike-py의 직렬화 최적화 예시:**

```rust
// record_helpers.rs — PyO3 intern!()으로 반복되는 dict 키를 캐싱
pub fn record_to_meta(py: Python<'_>, record: &Record) -> PyResult<Py<PyAny>> {
    let meta = PyDict::new(py);
    // intern!()은 Python 인터프리터 수명 동안 문자열을 캐싱
    // → 매번 새 Python str 객체를 할당하지 않음
    meta.set_item(intern!(py, "gen"), record.generation)?;
    meta.set_item(intern!(py, "ttl"), ttl)?;
    Ok(meta.into_any().unbind())
}
```

공식 클라이언트에서는 C 확장 → Python 변환 시 모든 문자열과 딕셔너리 키를 매번 새로 할당한다. aerospike-py는 PyO3의 `intern!()` 매크로를 통해 자주 사용되는 키("gen", "ttl" 등)를 Python 인터프리터 수명 동안 캐싱하여 할당을 제거한다.

---

## 3. 정량적 성능 차이 예측

> **주의:** 아래 수치는 아키텍처 분석에 기반한 예측값이며, 실제 벤치마크 결과는 워크로드, 네트워크 환경, 페이로드 크기에 따라 달라질 수 있다.

### 3.1 단일 요청 레이턴시

| 작업 | 공식 클라이언트 (예측) | aerospike-py (예측) | 차이 |
|------|----------------------|--------------------|----- |
| get (1KB record) | ~150μs | ~80μs | ~1.9x |
| put (1KB record) | ~170μs | ~90μs | ~1.9x |
| get (작은 record, <100B) | ~120μs | ~50μs | ~2.4x |
| batch_read (100건) | ~2.5ms | ~1.2ms | ~2.1x |

**레이턴시 분해 (get 1KB 기준):**

| 구성 요소 | 공식 클라이언트 | aerospike-py | 비고 |
|----------|---------------|-------------|------|
| 인자 파싱 | ~5μs | ~3μs | PyO3 직접 추출 vs ctypes |
| 스레드 핸드오프 | ~15μs | 0μs | executor.submit 오버헤드 |
| GIL 획득/해제 | ~10μs (×3) | ~5μs (×2) | 횟수 차이 |
| 네트워크 I/O | ~60μs | ~60μs | 동일 (서버 응답 시간) |
| 역직렬화 | ~20μs | ~7μs | intern + 제로카피 |
| 결과 반환 핸드오프 | ~10μs | ~2μs | Future 완료 비용 |
| **합계** | **~150μs** | **~80μs** | **~1.9x** |

### 3.2 동시성 처리량 (Throughput)

| 동시 요청 수 | 공식 클라이언트 (ops/sec) | aerospike-py (ops/sec) | 차이 |
|------------|-------------------------|----------------------|----- |
| 1 (순차) | ~6,500 | ~12,500 | ~1.9x |
| 10 | ~45,000 | ~100,000 | ~2.2x |
| 100 | ~120,000 | ~350,000 | ~2.9x |
| 1,000 | ~150,000 (포화) | ~500,000 | ~3.3x |
| 10,000 | ~150,000 (큐 대기) | ~550,000 | ~3.7x |

**동시성 증가에 따른 성능 격차 확대 원인:**

1. **스레드풀 포화:** 공식 클라이언트는 스레드풀(기본 16~36개) 초과 시 처리량이 정체
2. **GIL 경합 비례 증가:** 스레드 수가 늘수록 GIL 획득 대기 시간이 선형 증가
3. **메모리 압박:** 스레드당 스택 메모리(~8MB)로 인한 메모리 사용량 급증
4. **Tokio의 확장성:** epoll/kqueue 기반으로 동시 연결 수에 거의 무관한 성능

### 3.3 메모리 효율성

| 동시 요청 수 | 공식 클라이언트 (메모리) | aerospike-py (메모리) |
|------------|----------------------|---------------------|
| 100 | ~800MB (스레드 스택) | ~10MB |
| 1,000 | ~8GB (스레드 스택) | ~15MB |
| 10,000 | 실행 불가 | ~50MB |

---

## 4. 아키텍처 다이어그램

### 4.1 공식 Aerospike Python Client

```
┌─────────────────────────────────────────────────────────────┐
│                     Python Process                          │
│                                                             │
│  ┌──────────────┐     ┌──────────────────────────────────┐  │
│  │  asyncio      │     │     ThreadPoolExecutor           │  │
│  │  Event Loop   │     │  ┌────────┐ ┌────────┐          │  │
│  │               │────▶│  │Thread-1│ │Thread-2│ ...      │  │
│  │  await get()  │     │  │ ┌────┐ │ │ ┌────┐ │          │  │
│  │  await put()  │     │  │ │ C  │ │ │ │ C  │ │          │  │
│  │  await ...()  │     │  │ │Ext │ │ │ │Ext │ │          │  │
│  │               │◀────│  │ └──┬─┘ │ │ └──┬─┘ │          │  │
│  └──────────────┘     │  └────┼────┘ └────┼────┘          │  │
│                        │       │           │               │  │
│         GIL ◀──────────┼───────┼───────────┘               │  │
│      (경합 심함)       └───────┼──────────────────────────┘  │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │  동기 블로킹 I/O
                                 ▼
                        ┌────────────────┐
                        │   Aerospike    │
                        │   Server       │
                        └────────────────┘

특징:
• 매 요청마다 OS 스레드 점유
• GIL 획득/해제 3~4회/요청
• 스레드풀 크기가 동시성 상한
• C 확장의 동기 I/O를 스레드로 감싸는 구조
```

### 4.2 aerospike-py (Rust + Tokio + PyO3)

```
┌─────────────────────────────────────────────────────────────┐
│                     Python Process                          │
│                                                             │
│  ┌──────────────┐     ┌──────────────────────────────────┐  │
│  │  asyncio      │     │   Rust (PyO3) + Tokio Runtime    │  │
│  │  Event Loop   │     │                                  │  │
│  │               │────▶│  future_into_py()                │  │
│  │  await get() ─┼────▶│  ┌─────────────────────────┐    │  │
│  │  await put() ─┼────▶│  │   Tokio Event Loop       │    │  │
│  │  await ...() ─┼────▶│  │                           │    │  │
│  │               │     │  │  ┌Task─┐ ┌Task─┐ ┌Task─┐ │    │  │
│  │               │◀────│  │  │get  │ │put  │ │get  │ │    │  │
│  │  (결과 수신)   │     │  │  └──┬──┘ └──┬──┘ └──┬──┘ │    │  │
│  └──────────────┘     │  │     │       │       │     │    │  │
│                        │  │  epoll/kqueue 멀티플렉싱  │    │  │
│         GIL ◀──────────┤  └─────┼───────┼───────┼────┘    │  │
│      (경합 최소)       └────────┼───────┼───────┼─────────┘  │
│                                 │       │       │            │
└─────────────────────────────────┼───────┼───────┼────────────┘
                                  │       │       │
                                  ▼       ▼       ▼
                              ┌────────────────────────┐
                              │    Aerospike Server     │
                              │ (비동기 논블로킹 연결)   │
                              └────────────────────────┘

특징:
• OS 스레드 생성 없이 Tokio 태스크로 처리
• GIL 획득/해제 2회/요청 (인자 파싱 + 결과 반환)
• 동시 요청 수에 제한 거의 없음
• Rust의 제로코스트 추상화 + PyO3 최적화
```

### 4.3 요청 처리 흐름 비교

```
[공식 클라이언트: await client.get(key)]

  Python          ThreadPool         C Extension        Network
    │                 │                   │                │
    │──submit()──▶   │                   │                │
    │  (Future생성)   │──GIL획득─▶       │                │
    │                 │                   │──GIL해제──▶   │
    │                 │                   │   블로킹대기    │
    │                 │                   │◀──응답────────│
    │                 │◀──GIL획득──결과변환│                │
    │                 │──GIL해제──▶       │                │
    │◀──결과전달──────│                   │                │
    │                 │                   │                │
    │  총 지연: 네트워크 + 스레드 오버헤드 + GIL 경합       │


[aerospike-py: await client.get(key)]

  Python          PyO3/Tokio                            Network
    │                 │                                    │
    │──future_into_py│                                    │
    │  (인자파싱,      │                                    │
    │   GIL해제)      │──epoll/kqueue 등록──▶              │
    │                 │        (GIL 없음)                   │
    │                 │                    ◀──응답──────────│
    │                 │──GIL획득──결과변환──▶               │
    │◀──결과전달──────│                                    │
    │                 │                                    │
    │  총 지연: 네트워크 + 최소 변환 오버헤드                │
```

---

## 5. 요약

### 핵심 차이점

| 항목 | 공식 클라이언트 | aerospike-py |
|------|----------------|-------------|
| **언어** | C 확장 (CPython API) | Rust (PyO3 바인딩) |
| **Async 전략** | `run_in_executor` (스레드 위임) | `future_into_py` (네이티브 async) |
| **I/O 모델** | 동기 블로킹 + 스레드풀 | Tokio 비동기 논블로킹 |
| **GIL 영향** | 높음 (스레드 수 = GIL 경쟁자 수) | 최소 (결과 변환 시만 GIL 획득) |
| **경계 횟수** | 4회/요청 | 2회/요청 |
| **동시성 한계** | 스레드풀 크기 (16~36) | 사실상 무제한 (Tokio 태스크) |
| **메모리 효율** | ~8MB/스레드 | ~수KB/태스크 |

### 아키텍처적 우위

aerospike-py의 `future_into_py` 패턴이 가지는 근본적인 이점:

1. **Zero-Thread Overhead:** OS 스레드를 생성하지 않으므로 컨텍스트 스위칭, 스택 메모리, 스레드 생성 비용이 없다.

2. **Minimal GIL Contention:** I/O 수행 중 GIL을 완전히 해제하며, 결과 변환 시에만 최소한으로 획득한다. 동시 요청이 많아도 GIL 경합이 선형 증가하지 않는다.

3. **Reduced Boundary Crossings:** Python ↔ Native 경계를 2회만 통과하므로 경계 오버헤드가 절반 이하이다.

4. **Optimized Serialization:** PyO3의 `intern!()`, 제로카피, 직접 타입 변환 등으로 데이터 변환 비용을 최소화한다.

이러한 아키텍처 차이는 **동시성이 높아질수록 성능 격차가 확대**되며, 특히 수백~수천 개의 동시 요청을 처리하는 고성능 서버 환경에서 aerospike-py의 이점이 극대화된다. 단일 순차 요청에서도 ~1.9x의 레이턴시 개선이 예측되지만, 1,000개 이상의 동시 요청에서는 ~3.3x 이상의 처리량 차이가 발생할 것으로 예측된다.
