# PyO3 바인딩 CPU 오버헤드 최적화 구현 요약

## 배경

벤치마크에서 aerospike-py(Rust/PyO3)의 CPU 사용률이 공식 C 클라이언트 대비 ~4-5배 높았다.

- rust_sync PUT: cpu_p50=0.063ms, cpu_pct=33.3%
- c_sync PUT: cpu_p50=0.013ms, cpu_pct=8.7%

I/O Wait는 비슷(0.126 vs 0.137ms)하므로 네트워크가 아닌 **Python↔Rust 타입 변환 오버헤드**가 원인.

---

## Phase 1: Quick Wins (불필요한 할당 제거)

### 1-1. ConnectionInfo → Arc\<ConnectionInfo\>

| 항목 | 내용 |
|------|------|
| **문제** | 매 API 호출마다 `conn_info.clone()`으로 String 2개(server_address, cluster_name) 복제 (13곳의 `prepare_*_args()`) |
| **수정** | `ConnectionInfo`를 `Arc`로 래핑하여 `Arc::clone()` (포인터 복제, ~1ns) |
| **파일** | `client_common.rs`, `client.rs`, `async_client.rs`, `query.rs` |
| **효과** | op당 ~2 String alloc 제거 |

### 1-2. HashMap::with_capacity 적용

| 항목 | 내용 |
|------|------|
| **문제** | `value.rs` — `HashMap::new()`로 dict 변환 시 capacity 없이 시작 → 여러 번 rehash |
| **수정** | `HashMap::with_capacity(dict.len())` |
| **파일** | `types/value.rs` |
| **효과** | dict 변환 시 rehash 제거 |

### 1-3. meta dict 키 인터닝

| 항목 | 내용 |
|------|------|
| **문제** | `"gen"`, `"ttl"` 문자열을 매 record 변환마다 새로 생성 |
| **수정** | `intern!(py, "gen")`, `intern!(py, "ttl")`로 한 번만 생성 |
| **파일** | `types/record.rs`, `record_helpers.rs` |
| **효과** | record당 2 alloc 제거 |

### 1-4. 문자열/바이트 변환 최적화

| 항목 | 내용 |
|------|------|
| **문제** | `PyString.extract::<String>()` — UTF-8 재검증+복사, `PyBytes.extract::<Vec<u8>>()` — 중간 추출 단계 |
| **수정** | 문자열: `s.to_str()?.to_owned()` (CPython UTF-8 캐시 활용), 바이트: `b.as_bytes().to_vec()` (직접 슬라이스 접근) |
| **파일** | `types/value.rs`, `types/key.rs`, `types/bin.rs` |
| **효과** | 문자열당 UTF-8 재검증 제거 |

---

## Phase 2: Batch 경로 최적화

### 2-3. batch 결과 변환 시 이중 key 변환 제거

| 항목 | 내용 |
|------|------|
| **문제** | `batch_types.rs`에서 `key_to_py()` 호출 후, `record_to_py()`에서 다시 `key_to_py()` 호출 → 같은 key를 2번 Python 객체로 변환 |
| **수정** | `record_to_py_with_key()` 함수 추가. `key_to_py()` 결과를 전달하여 재사용 |
| **파일** | `batch_types.rs`, `types/record.rs` |
| **효과** | batch record당 ~5 alloc 제거 |

---

## Phase 3: PyList/PyDict 최적화

### 3-1. PyList::empty() + append → PyList::new()

| 항목 | 내용 |
|------|------|
| **문제** | 빈 리스트 생성 후 반복 append → 내부 리사이즈 발생 |
| **수정** | 사전에 변환된 아이템 배열로 `PyList::new()` 한 번에 생성 |
| **파일** | `types/value.rs`, `record_helpers.rs`, `client.rs`, `async_client.rs` |
| **효과** | 리스트당 O(log N) 리사이즈 제거 |

### 3-2. get() key 왕복 변환 제거

| 항목 | 내용 |
|------|------|
| **문제** | `get()` 호출 시 Python key → Rust Key (`py_to_key`) → 다시 Python key (`key_to_py`) → 총 ~8 불필요 alloc |
| **수정** | GIL 해제 전 `key_to_py()`를 미리 계산하여 I/O 후 Rust→Python key 재변환 회피 |
| **파일** | `client.rs`, `async_client.rs` |
| **적용 메서드** | `get()`, `select()`, `operate()`, `operate_ordered()` (sync + async) |
| **효과** | get()당 ~8 alloc 제거 |

---

## 수정된 파일 목록

```
rust/src/types/value.rs       — Phase 1-2, 1-4, 3-1
rust/src/types/key.rs          — Phase 1-4
rust/src/types/bin.rs          — Phase 1-4
rust/src/types/record.rs       — Phase 1-3, 2-3, 3-2 (record_to_py_with_key 추가)
rust/src/record_helpers.rs     — Phase 1-3, 3-1
rust/src/batch_types.rs        — Phase 2-3
rust/src/client_common.rs      — Phase 1-1 (Arc<ConnectionInfo>)
rust/src/client.rs             — Phase 1-1, 3-1, 3-2
rust/src/async_client.rs       — Phase 1-1, 3-1, 3-2
rust/src/query.rs              — Phase 1-1
```

---

## 예상 효과

| Phase | 대상 | 예상 개선 |
|-------|------|----------|
| 1-1 | ConnectionInfo Arc | op당 ~2 String alloc 제거 |
| 1-2 | HashMap capacity | dict 변환 시 rehash 제거 |
| 1-3 | meta key intern | record당 2 alloc 제거 |
| 1-4 | 문자열/바이트 | 문자열당 UTF-8 재검증 제거 |
| 2-3 | 이중 key 변환 | batch record당 ~5 alloc 제거 |
| 3-1 | PyList pre-alloc | 리스트당 O(log N) 리사이즈 제거 |
| 3-2 | get() key 왕복 | get()당 ~8 alloc 제거 |

**Phase 1-2만으로도** 단일 put/get 호출에서 ~4-6 불필요 할당 제거 → CPU 시간 20-40% 감소 예상.
**Phase 3까지 적용 시** 특히 batch 연산에서 N 비례 감소 → 대량 배치에서 50%+ CPU 절감 가능.

---

## 미적용 항목 (Phase 4 — 프로파일링 후 결정)

| 항목 | 설명 | 비고 |
|------|------|------|
| 4-1. OTel 문자열 최적화 | `traced_op!` 매크로에서 `.to_string()` → `Cow<'_, str>` | OTel API가 `&str`에서도 내부 할당 → 순 이득 미미 |
| 4-2. `pyo3_disable_reference_pool` | `Py<T>` drop 시 글로벌 참조 풀 동기화 오버헤드 제거 | async client의 Tokio 스레드 안전성 감사 필요 |
| 4-3. FFI 직접 호출 | `PyDict_SetItem`, `PyList_SET_ITEM` 직접 호출 | unsafe 코드 증가, 프로파일링으로 필요성 확인 후 |
| 2-1. batch key clone | `k.clone()`으로 모든 batch key 복제 | `BatchOperation` API가 owned Key 요구 — 회피 불가 |
| 2-2. batch ops clone | `self.ops.clone()`으로 전체 Vec 복제 | `BatchOperation::write`가 owned Vec 요구 — 회피 불가 |

---

## 검증 결과

- `cargo check` — 컴파일 성공 (경고 없음)
- `make build` — release 빌드 성공
- `make test-unit` — **344 테스트 모두 통과**
- `make lint` — ruff check + clippy 모두 통과
