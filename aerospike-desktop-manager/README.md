# Aerospike Desktop Manager

Web-based Aerospike cluster management tool inspired by [tiny-rdm](https://github.com/tiny-craft/tiny-rdm).
FastAPI + React (TypeScript) 기반의 풀스택 애플리케이션으로, `aerospike-py` AsyncClient를 thin REST wrapper로 제공합니다.

## Features

- **Multi-Cluster 연결 관리** — 여러 Aerospike 클러스터를 동시에 연결/관리
- **Cluster Inspector** — 노드, 네임스페이스, 셋, 빈 정보 조회
- **Record CRUD** — put, get, select, exists, remove + scan (페이지네이션)
- **Record Operations** — touch, append, prepend, increment, remove_bin, operate, operate_ordered
- **Batch Operations** — batch_read, batch_operate, batch_remove
- **Secondary Index 관리** — 생성/삭제 (numeric, string, geo2dsphere)
- **UDF 관리** — 업로드, 삭제, apply (실행)
- **Truncate** — 네임스페이스/셋 데이터 절삭
- **Admin** — 사용자/역할 CRUD, 권한 부여/회수, 화이트리스트, 쿼터
- **실시간 Metrics** — WebSocket 기반 서버/네임스페이스 메트릭 스트리밍
- **Info Terminal** — Aerospike info 명령어 직접 실행
- **Import/Export** — JSON, CSV 형식 데이터 내보내기/가져오기

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+ & npm
- `aerospike-py` (상위 디렉토리에서 빌드)

## Quick Start

```bash
cd aerospike-desktop-manager

# 의존성 설치
make install

# 백엔드 개발 서버 (http://localhost:8000)
make backend

# 프론트엔드 개발 서버 (http://localhost:5173)
make frontend
```

## Project Structure

```
aerospike-desktop-manager/
├── Makefile                    # 개발 명령어
├── Dockerfile.backend          # 프로덕션 Docker 이미지
├── docker-compose.yaml
│
├── backend/
│   ├── pyproject.toml          # uv 프로젝트 설정
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # pydantic-settings 환경 설정
│   ├── dependencies.py         # DI: get_client(), get_connection_manager()
│   ├── exceptions.py           # aerospike-py 예외 → HTTP 상태 코드 매핑
│   │
│   ├── models/
│   │   ├── admin.py            # 사용자/역할 요청 모델
│   │   ├── cluster.py          # NodeInfo, NamespaceStats, SetInfo, etc.
│   │   ├── common.py           # OkResponse, ErrorResponse
│   │   ├── connection.py       # ConnectionProfile, ConnectionStatus
│   │   ├── index.py            # IndexInfo, CreateIndexRequest
│   │   ├── record.py           # PutRequest, ScanResult, BatchReadRequest, etc.
│   │   └── udf.py              # UdfInfo, UdfUploadRequest, UdfExecuteRequest
│   │
│   ├── routers/
│   │   ├── admin.py            # /api/v1/c/{conn_id}/admin
│   │   ├── batch.py            # /api/v1/c/{conn_id}/batch
│   │   ├── cluster.py          # /api/v1/c/{conn_id}/cluster
│   │   ├── connections.py      # /api/v1/connections
│   │   ├── import_export.py    # /api/v1/c/{conn_id}/data
│   │   ├── indexes.py          # /api/v1/c/{conn_id}/indexes
│   │   ├── metrics.py          # /api/v1/c/{conn_id}/metrics (+ WebSocket)
│   │   ├── namespaces.py       # /api/v1/c/{conn_id}/namespaces
│   │   ├── operations.py       # /api/v1/c/{conn_id}/records (touch, append, etc.)
│   │   ├── records.py          # /api/v1/c/{conn_id}/records (CRUD + scan)
│   │   ├── terminal.py         # /api/v1/c/{conn_id}/info
│   │   ├── truncate.py         # /api/v1/c/{conn_id}/truncate
│   │   └── udfs.py             # /api/v1/c/{conn_id}/udfs
│   │
│   ├── services/
│   │   ├── connection_manager.py   # 멀티 클러스터 연결 관리
│   │   └── import_export.py        # JSON/CSV 변환
│   │
│   └── utils/
│       ├── info_parser.py      # Aerospike info 응답 파서
│       ├── key_helpers.py      # PK 파싱, 키 빌드
│       └── serialization.py    # 레코드 값 직렬화 (bytes→hex 등)
│
└── frontend/                   # React + TypeScript + Vite
    ├── src/
    │   ├── api/                # Axios API 클라이언트 모듈
    │   ├── components/         # React 컴포넌트
    │   ├── hooks/              # 커스텀 훅
    │   ├── pages/              # 페이지 컴포넌트
    │   └── stores/             # Zustand 상태 관리
    └── dist/                   # 프로덕션 빌드 아웃풋
```

## API Endpoints

### Global

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/metrics/client` | aerospike-py OTel Prometheus metrics |

### Connections (`/api/v1/connections`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | 연결 목록 |
| POST | `/` | 연결 생성 |
| POST | `/test` | 연결 테스트 |
| GET | `/{conn_id}` | 연결 상태 조회 |
| PUT | `/{conn_id}` | 연결 프로필 수정 |
| DELETE | `/{conn_id}` | 연결 삭제 |

### Cluster (`/api/v1/c/{conn_id}/cluster`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | 클러스터 개요 |
| GET | `/nodes` | 노드 목록 |
| GET | `/nodes/{node_name}` | 노드 통계 |

### Namespaces (`/api/v1/c/{conn_id}/namespaces`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | 네임스페이스 목록 |
| GET | `/{ns}` | 네임스페이스 상세 |
| GET | `/{ns}/sets` | 셋 목록 |
| GET | `/{ns}/bins` | 빈 목록 |

### Records (`/api/v1/c/{conn_id}/records`)

| Method | Path | AsyncClient Method |
|--------|------|--------------------|
| POST | `/put` | `client.put(key, bins, meta)` |
| POST | `/get` | `client.get(key)` |
| POST | `/select` | `client.select(key, bins)` |
| POST | `/exists` | `client.exists(key)` |
| POST | `/remove` | `client.remove(key)` |
| POST | `/scan` | `client.scan(ns, set)` + 페이지네이션 |
| POST | `/touch` | `client.touch(key, val)` |
| POST | `/append` | `client.append(key, bin, val)` |
| POST | `/prepend` | `client.prepend(key, bin, val)` |
| POST | `/increment` | `client.increment(key, bin, offset)` |
| POST | `/remove-bin` | `client.remove_bin(key, bin_names)` |
| POST | `/operate` | `client.operate(key, ops)` |
| POST | `/operate-ordered` | `client.operate_ordered(key, ops)` |
| GET | `/{ns}/{set}/{pk}` | RESTful alias → `client.get()` |
| DELETE | `/{ns}/{set}/{pk}` | RESTful alias → `client.remove()` |

### Batch (`/api/v1/c/{conn_id}/batch`)

| Method | Path | AsyncClient Method |
|--------|------|--------------------|
| POST | `/read` | `client.batch_read(keys, bins)` |
| POST | `/operate` | `client.batch_operate(keys, ops)` |
| POST | `/remove` | `client.batch_remove(keys)` |

### Truncate (`/api/v1/c/{conn_id}/truncate`)

| Method | Path | AsyncClient Method |
|--------|------|--------------------|
| POST | `/` | `client.truncate(ns, set, nanos)` |

### Indexes (`/api/v1/c/{conn_id}/indexes`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{ns}` | 인덱스 목록 |
| POST | `/{ns}` | 인덱스 생성 |
| DELETE | `/{ns}/{index_name}` | 인덱스 삭제 |

### UDFs (`/api/v1/c/{conn_id}/udfs`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | UDF 목록 |
| POST | `/` | UDF 업로드 |
| DELETE | `/{module}` | UDF 삭제 |
| POST | `/apply` | UDF 실행 |

### Admin (`/api/v1/c/{conn_id}/admin`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | 사용자 목록 |
| GET | `/users/{username}` | 사용자 정보 |
| POST | `/users` | 사용자 생성 |
| DELETE | `/users/{username}` | 사용자 삭제 |
| PUT | `/users/{username}/password` | 비밀번호 변경 |
| POST | `/users/{username}/grant-roles` | 역할 부여 |
| POST | `/users/{username}/revoke-roles` | 역할 회수 |
| GET | `/roles` | 역할 목록 |
| GET | `/roles/{role}` | 역할 정보 |
| POST | `/roles` | 역할 생성 |
| DELETE | `/roles/{role}` | 역할 삭제 |
| POST | `/roles/{role}/grant-privileges` | 권한 부여 |
| POST | `/roles/{role}/revoke-privileges` | 권한 회수 |
| PUT | `/roles/{role}/whitelist` | 화이트리스트 설정 |
| PUT | `/roles/{role}/quotas` | 쿼터 설정 |

### Metrics (`/api/v1/c/{conn_id}/metrics`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/server` | 서버 통계 |
| GET | `/namespace/{ns}` | 네임스페이스 통계 |
| WebSocket | `/stream` | 실시간 메트릭 스트림 |

### Info Terminal (`/api/v1/c/{conn_id}/info`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | info 명령 실행 |
| POST | `/info-all` | 전체 노드 info 명령 실행 |

### Data Import/Export (`/api/v1/c/{conn_id}/data`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/export/{ns}/{set_name}` | JSON/CSV 내보내기 |
| POST | `/import/{ns}/{set_name}` | JSON 가져오기 |

## Error Handling

모든 `aerospike-py` 예외는 중앙 예외 핸들러에서 자동으로 HTTP 상태 코드로 변환됩니다:

| Exception | HTTP Status |
|-----------|-------------|
| `RecordNotFound` | 404 |
| `RecordExistsError` / `RecordGenerationError` | 409 |
| `InvalidArgError` / `ClientError` | 400 |
| `AerospikeTimeoutError` | 504 |
| `ClusterError` | 503 |
| `AdminError` | 403 |
| `AerospikeIndexError` / `UDFError` | 400 |
| `ServerError` | 502 |
| `AerospikeError` (catch-all) | 500 |

응답 형식:
```json
{
  "error": "RecordNotFound",
  "detail": "Record not found: (test, users, 123)"
}
```

## Configuration

환경 변수 (`ADM_` prefix):

| Variable | Default | Description |
|----------|---------|-------------|
| `ADM_APP_TITLE` | Aerospike Desktop Manager | 앱 타이틀 |
| `ADM_CORS_ORIGINS` | `["http://localhost:5173", ...]` | CORS 허용 오리진 |
| `ADM_DEFAULT_AEROSPIKE_HOST` | 127.0.0.1 | 기본 호스트 |
| `ADM_DEFAULT_AEROSPIKE_PORT` | 3000 | 기본 포트 |
| `ADM_METRICS_POLL_INTERVAL` | 2.0 | WebSocket 메트릭 폴링 간격 (초) |

## Development

```bash
# 린트
make lint

# 테스트
make test

# 프론트엔드 빌드
make build
```

## Docker

```bash
# docker-compose로 실행
make docker-up

# 중지
make docker-down
```

## License

See the root project [LICENSE](../LICENSE).
