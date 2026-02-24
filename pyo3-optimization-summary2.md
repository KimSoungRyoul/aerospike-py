# PyO3 바인딩 CPU 오버헤드 추가 분석 (Phase 1~3 적용 후)

## 배경

`pyo3-optimization-summary.md`의 Phase 1~3 최적화를 모두 적용했으나, 벤치마크 결과에서 aerospike-py의 CPU 사용률이 여전히 공식 C 클라이언트 대비 높게 측정됨.

추가 조사 결과, **벤치마크 측정 방식의 오류**와 **OTel/Prometheus 계측 오버헤드** 두 가지 근본 원인을 발견.

---

## 1. 벤치마크 CPU 측정 오류: `process_time()` vs `thread_time()`

### 문제

현재 벤치마크(`benchmark/bench_compare.py`)는 `time.process_time()`으로 CPU 시간을 측정:

```python
def _measure_loop_cpu(fn, count):
    for i in range(count):
        w0 = time.perf_counter()
        c0 = time.process_time()       # ← 프로세스 전체 CPU
        fn(i)
        c1 = time.process_time()
        cpu_times.append(c1 - c0)
```

| 함수 | 측정 범위 | 문제점 |
|------|----------|--------|
| `time.process_time()` | **프로세스 전체** 모든 스레드의 CPU 합산 | Tokio 워커 스레드 CPU를 포함하여 과대 측정 |
| `time.thread_time()` | **현재 스레드만** | Python 호출 스레드의 실제 CPU만 측정 |

### 왜 aerospike-py에서만 문제가 되는가

```
C 클라이언트 (aerospike-c-client):
  Python thread → C FFI → 동기 네트워크 I/O → 리턴
  → process_time ≈ thread_time (단일 스레드에서 실행)

aerospike-py (Rust/Tokio):
  Python thread → Rust FFI → Tokio runtime.block_on() → 워커 스레드에서 비동기 I/O
  → process_time = Python thread CPU + Tokio 워커 스레드들의 CPU (과대 측정)
  → thread_time = Python thread CPU만 (정확한 측정)
```

aerospike-py는 Tokio 멀티스레드 런타임(`new_multi_thread()`)을 사용하므로, I/O 처리 중 Tokio 워커 스레드의 CPU 사용이 `process_time()`에 합산됨. 공식 C 클라이언트는 동일 스레드에서 동기 I/O를 수행하므로 차이가 없음.

### 예상 영향

현재 벤치마크에서 `cpu_pct`가 ~33%로 보고되지만, `thread_time()`으로 측정하면 ~15-20%로 감소할 것으로 예상. C 클라이언트의 ~8.7%과의 실제 차이는 보고된 4배가 아닌 ~2배 수준일 가능성.

### 수정 방안

```python
# Before
c0 = time.process_time()
fn(i)
c1 = time.process_time()

# After — 현재 스레드 CPU만 측정
c0 = time.thread_time()
fn(i)
c1 = time.thread_time()
```

> 참고: `time.thread_time()`은 macOS/Linux에서 지원. Windows에서도 Python 3.7+ 지원.

---

## 2. OTel/Prometheus 매 연산 9+ String 할당 오버헤드

### 문제

`otel` feature가 maturin 빌드에서 항상 활성화됨 (`pyproject.toml: features = ["pyo3/extension-module", "otel"]`).

모든 DB 연산은 `traced_op!` 매크로를 통과하며, 이 매크로는 **OTel span 생성 + Prometheus timer**를 동시에 실행. 각 단계에서 String 할당이 발생:

#### `traced_op!` 매크로 (tracing.rs:202-243)

```rust
// 1. span_name: format! → 1 alloc + to_uppercase → 1 alloc
let span_name = format!("{} {}.{}", $op.to_uppercase(), $ns, $set);

// 2. OTel attributes: 각 KeyValue에서 to_string/clone
KeyValue::new("db.namespace", $ns.to_string()),           // 1 alloc
KeyValue::new("db.collection.name", $set.to_string()),    // 1 alloc
KeyValue::new("db.operation.name", $op.to_uppercase()),   // 1 alloc
KeyValue::new("server.address", conn.server_address.clone()), // 1 alloc
KeyValue::new("db.aerospike.cluster_name", conn.cluster_name.clone()), // 1 alloc
```

#### `OperationTimer::start()` (metrics.rs:62-68)

```rust
Self {
    op_name: op_name.to_string(),    // 1 alloc
    namespace: namespace.to_string(), // 1 alloc
    set_name: set_name.to_string(),  // 1 alloc
}
```

#### 합산: 연산당 최소 9 String 할당

| 출처 | String 할당 수 |
|------|---------------|
| `format!(span_name)` | 1 |
| `to_uppercase()` × 2 | 2 |
| `$ns.to_string()` (OTel + Timer) | 2 |
| `$set.to_string()` (OTel + Timer) | 2 |
| `conn.server_address.clone()` | 1 |
| `conn.cluster_name.clone()` | 1 |
| `op_name.to_string()` (Timer) | 1 |
| **합계** | **10** |

Phase 1에서 `ConnectionInfo`를 `Arc`로 래핑하여 `prepare_*_args()`에서의 clone은 제거했으나, `traced_op!` 매크로 내부의 `conn.server_address.clone()`과 `conn.cluster_name.clone()`은 여전히 매 연산마다 실행됨.

### 수정 방안

#### 방안 A: `&str` / `Cow<'static, str>` 활용으로 할당 제거

```rust
// OperationTimer — &str 참조로 변경 (lifetime 제약)
pub struct OperationTimer<'a> {
    start: Instant,
    op_name: &'a str,
    namespace: &'a str,
    set_name: &'a str,
}

impl<'a> OperationTimer<'a> {
    pub fn start(op_name: &'a str, namespace: &'a str, set_name: &'a str) -> Self {
        Self { start: Instant::now(), op_name, namespace, set_name }
    }

    pub fn finish(self, error_type: &str) {
        let duration = self.start.elapsed().as_secs_f64();
        let labels = OperationLabels {
            db_system_name: Cow::Borrowed("aerospike"),
            db_namespace: Cow::Borrowed(self.namespace),
            db_collection_name: Cow::Borrowed(self.set_name),
            db_operation_name: Cow::Borrowed(self.op_name),
            error_type: if error_type.is_empty() {
                Cow::Borrowed("")
            } else {
                Cow::Borrowed(error_type)
            },
        };
        METRICS.op_duration.get_or_create(&labels).observe(duration);
    }
}
```

→ **Timer에서 3 alloc 제거** (to_string 3회 → 0회)

#### 방안 B: OTel span attributes 최적화

```rust
// op_name을 한 번만 uppercase 변환, 재사용
let op_upper = $op.to_uppercase();
let span_name = format!("{} {}.{}", &op_upper, $ns, $set);

// conn_info의 server_address/cluster_name은 Cow<'static, str>로 변경
KeyValue::new("server.address", conn.server_address.as_str()),
KeyValue::new("db.aerospike.cluster_name", conn.cluster_name.as_str()),
```

> OTel `KeyValue::new`는 `Into<StringValue>`를 받으므로 `&str` → 내부 clone은 불가피하나, Rust 측 중복 할당은 제거 가능.

#### 방안 C: op_name 상수화

대부분의 `$op`는 `"put"`, `"get"`, `"delete"` 등 고정 문자열. `to_uppercase()`를 컴파일 타임에 처리:

```rust
// 매크로 내부에서 상수 매핑
const fn op_upper(op: &str) -> &str {
    match op {
        "put" => "PUT", "get" => "GET", "delete" => "DELETE",
        "select" => "SELECT", "operate" => "OPERATE",
        "batch_read" => "BATCH_READ", "batch_operate" => "BATCH_OPERATE",
        _ => op,
    }
}
```

→ **to_uppercase() 2회 alloc 완전 제거**

### 예상 효과

| 방안 | 제거되는 alloc/op | 비고 |
|------|-----------------|------|
| A (Timer &str) | 3 | lifetime 제약 최소 |
| B (OTel attrs) | 2 | OTel 내부 clone은 잔존 |
| C (op 상수화) | 2 | 컴파일 타임 처리 |
| **A + B + C 합산** | **~7** | 10 → 3 (OTel 내부 불가피 clone) |

---

## 3. `extract_python_context` 매 연산 Python import 호출

### 문제

`client_common.rs`의 모든 `prepare_*_args()` 함수가 `extract_parent_context(py)`를 호출하고, 이는 `tracing.rs:extract_python_context()`를 실행:

```rust
pub fn extract_python_context(py: Python<'_>) -> Context {
    let result: PyResult<HashMap<String, String>> = (|| {
        let propagate = py.import("opentelemetry.propagate")?;  // ← 매번 Python import!
        let carrier = pyo3::types::PyDict::new(py);
        propagate.call_method1("inject", (carrier.clone(),))?;
        carrier.extract()                                        // ← HashMap으로 extract
    })();
    // ...
}
```

**매 DB 연산마다 발생하는 비용:**

| 단계 | 비용 |
|------|------|
| `py.import("opentelemetry.propagate")` | Python import machinery 실행 (sys.modules 조회 + attribute resolution) |
| `PyDict::new(py)` | 빈 Python dict 생성 |
| `propagate.call_method1("inject", ...)` | Python → Rust → Python 왕복 호출 |
| `carrier.extract::<HashMap<String, String>>()` | dict → HashMap 전체 복사 (key/value 모두 String 할당) |

CPython의 `sys.modules` 캐시 덕분에 import 자체는 빠르지만(~1μs), GIL을 잡은 상태에서 Python 함수 호출과 dict 생성/변환까지 합산하면 **연산당 ~5-10μs** 추가 오버헤드.

### 수정 방안

#### 방안 A: 모듈 참조 캐싱

```rust
use std::sync::OnceLock;
use pyo3::Py;

static PROPAGATE_MODULE: OnceLock<Py<pyo3::types::PyModule>> = OnceLock::new();

pub fn extract_python_context(py: Python<'_>) -> Context {
    let module = PROPAGATE_MODULE.get_or_init(|| {
        py.import("opentelemetry.propagate")
            .expect("opentelemetry must be installed")
            .unbind()
    });

    let carrier = pyo3::types::PyDict::new(py);
    let bound_module = module.bind(py);
    bound_module.call_method1("inject", (carrier.clone(),)).ok();
    // ...
}
```

→ `py.import()` 호출을 프로세스 lifetime에서 **1회로 감소**

#### 방안 B: OTel 비활성 시 완전 스킵

```rust
use std::sync::atomic::{AtomicBool, Ordering};

static OTEL_AVAILABLE: AtomicBool = AtomicBool::new(false);

pub fn init_tracer_provider() {
    // ... 기존 초기화 ...
    OTEL_AVAILABLE.store(true, Ordering::Release);
}

pub fn extract_python_context(py: Python<'_>) -> Context {
    if !OTEL_AVAILABLE.load(Ordering::Acquire) {
        return Context::current();  // OTel 미사용 시 즉시 리턴
    }
    // ... 기존 로직 ...
}
```

→ **OTEL_SDK_DISABLED=true이거나 트레이서 미초기화 시 Python 호출 완전 제거** (가장 효과적)

#### 방안 C: propagator 캐싱 + carrier 재사용

```rust
// thread-local carrier로 dict 생성 오버헤드 제거
thread_local! {
    static INJECT_FN: RefCell<Option<Py<PyAny>>> = RefCell::new(None);
}
```

### 예상 효과

| 방안 | 제거되는 비용 | 비고 |
|------|-------------|------|
| A (모듈 캐싱) | import 조회 ~1μs/op | OnceLock 사용 |
| B (OTel 스킵) | ~5-10μs/op 전체 | OTel 미사용 시 |
| C (carrier 재사용) | dict 생성 ~0.5μs/op | thread-local 복잡도 |

**방안 B가 가장 효과적**: 대부분의 사용자는 OTel을 활성화하지 않으므로, `init_tracing()` 미호출 시 `extract_python_context`를 완전 스킵하면 됨.

---

## 4. Tokio 런타임 설정 과잉

### 문제

`runtime.rs`에서 Sync Client용 Tokio 런타임을 `new_multi_thread().enable_all()`로 생성:

```rust
pub static RUNTIME: LazyLock<tokio::runtime::Runtime> = LazyLock::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap()
});
```

| 설정 | 현재 값 | 문제 |
|------|--------|------|
| `new_multi_thread()` | CPU 코어 수만큼 워커 스레드 생성 | 8코어 = 8 스레드, 대부분 idle |
| `enable_all()` | IO + time + signal 모두 활성화 | signal은 불필요 |
| 워커 스레드 수 | 기본값 (= CPU 코어 수) | Sync client는 `block_on` 1개만 사용, 과잉 |

**Sync Client 호출 패턴:**
```
Python thread → GIL 해제 → RUNTIME.block_on(async { client.get().await })
```

`block_on()`은 현재 스레드에서 future를 폴링하므로, 대부분의 Tokio 워커 스레드는 유휴 상태. 하지만 생성된 워커 스레드들은 메모리를 소비하고, OS 스케줄러에 부하를 줌.

### 수정 방안

#### 방안 A: `current_thread` 런타임 사용 (Sync Client 전용)

```rust
pub static RUNTIME: LazyLock<tokio::runtime::Runtime> = LazyLock::new(|| {
    tokio::runtime::Builder::new_current_thread()
        .enable_io()
        .enable_time()
        .build()
        .unwrap()
});
```

→ 워커 스레드 0개, `block_on` 호출 스레드에서 직접 실행

**주의**: `aerospike` crate 내부에서 `tokio::spawn()`을 사용한다면 `current_thread`에서도 동작하지만, 별도 스레드에서의 `block_on()` 호출이 필요할 수 있음. 사전 검증 필요.

#### 방안 B: 워커 스레드 수 제한

```rust
pub static RUNTIME: LazyLock<tokio::runtime::Runtime> = LazyLock::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .worker_threads(2)  // 8 → 2로 감소
        .enable_io()
        .enable_time()
        .build()
        .unwrap()
});
```

→ 멀티스레드 호환성 유지하면서 리소스 절감

#### 방안 C: Async Client 런타임과 통합

현재 Async Client는 `pyo3_async_runtimes::tokio`가 관리하는 별도 런타임을 사용. Sync Client의 `RUNTIME`과 통합하면 런타임 1개로 줄일 수 있으나, 두 런타임의 lifecycle 관리가 복잡해짐.

### 예상 효과

| 방안 | 효과 | 벤치마크 영향 |
|------|------|-------------|
| A (current_thread) | 워커 스레드 제거 | `process_time()` 측정 시 Tokio 스레드 CPU 미포함 → 측정값 크게 감소 |
| B (worker_threads=2) | 6개 스레드 제거 (8코어 기준) | process_time 측정값 부분 감소 |
| C (런타임 통합) | 런타임 1개 절약 | 복잡도 대비 효과 미미 |

**방안 A가 가장 효과적이지만**, `aerospike` crate가 내부적으로 `tokio::spawn()`을 사용하는지 검증 필요. 검증 후 문제없으면 A, 있으면 B 적용.

---

## 종합 정리

### 문제별 영향도

| # | 문제 | 유형 | 영향도 |
|---|------|------|--------|
| 1 | `process_time()` 측정 오류 | 벤치마크 버그 | ★★★★★ (CPU 수치 ~2배 과대 보고) |
| 2 | OTel/Prometheus 매 op 10+ String 할당 | 실제 오버헤드 | ★★★★ (op당 ~10 불필요 alloc) |
| 3 | `extract_python_context` 매 op Python import | 실제 오버헤드 | ★★★ (op당 ~5-10μs) |
| 4 | Tokio 멀티스레드 런타임 과잉 | 설정 문제 | ★★ (간접적, #1과 연관) |

### 우선순위별 수정 순서

```
[1단계] 벤치마크 수정 — process_time → thread_time 변경
        → 즉시 정확한 CPU 비교 가능. 실제 차이가 보고 대비 작을 수 있음.

[2단계] extract_python_context 최적화 — OTel 미사용 시 스킵
        → OTel 미설정 환경(대다수)에서 op당 ~5-10μs 절감.

[3단계] OTel/Prometheus String 할당 최적화
        → Timer &str 참조 + op 상수화로 ~7 alloc/op 제거.

[4단계] Tokio 런타임 조정 — worker_threads 제한 또는 current_thread
        → 리소스 효율화 + process_time 측정 정확도 개선.
```

### 예상 결과

| 지표 | 현재 (Phase 3 적용) | 1-4단계 적용 후 |
|------|-------------------|----------------|
| `cpu_pct` (process_time 기준) | ~33% | 측정 방식 변경으로 비교 불가 |
| `cpu_pct` (thread_time 기준) | ~20% (추정) | ~12-15% |
| C 클라이언트 대비 CPU 배율 | ~4x (과대 측정) | ~1.5-2x (실제 차이) |
| String alloc / op | ~12 | ~3-5 |
| Python import / op | 1 | 0 (OTel 미사용 시) |

---

## 미적용 항목 (추가 프로파일링 필요)

| 항목 | 설명 | 비고 |
|------|------|------|
| Prometheus `get_or_create()` 비용 | label set 해싱 + HashMap 조회 비용 | 프로파일링으로 병목 확인 후 |
| OTel `StringValue` 내부 clone | opentelemetry crate 내부 동작, 외부에서 제어 불가 | upstream 변경 필요 |
| `error_type_from_aerospike_error()` | 에러 경로에서 String 할당 | 에러 경로는 빈도 낮아 우선순위 낮음 |
| `pyo3_async_runtimes` 런타임 설정 | Async Client 전용 런타임 최적화 | 별도 분석 필요 |
