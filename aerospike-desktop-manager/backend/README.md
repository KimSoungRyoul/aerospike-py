# Aerospike Desktop Manager — Backend

FastAPI 기반 REST API 서버. `aerospike-py` AsyncClient의 thin wrapper로,
Aerospike 클러스터 관리에 필요한 모든 기능을 HTTP 엔드포인트로 제공합니다.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- `aerospike-py` (상위 프로젝트에서 빌드)

## Quick Start

```bash
# 의존성 설치
uv sync

# 개발 서버 (http://localhost:8000)
uv run uvicorn main:app --reload --port 8000

# Swagger UI
open http://localhost:8000/docs
```

## Project Structure

```
backend/
├── pyproject.toml          # uv 프로젝트 설정 (의존성, ruff, pytest)
├── main.py                 # FastAPI 앱 진입점, 라우터 마운트
├── config.py               # pydantic-settings 환경 설정 (ADM_ prefix)
├── dependencies.py         # DI: get_client(), get_connection_manager()
├── exceptions.py           # aerospike-py 예외 → HTTP 상태 코드 중앙 매핑
│
├── models/                 # Pydantic 요청/응답 모델
│   ├── admin.py            #   사용자/역할 관리 요청
│   ├── cluster.py          #   NodeInfo, NamespaceStats, SetInfo, ClusterOverview
│   ├── common.py           #   OkResponse, ErrorResponse
│   ├── connection.py       #   ConnectionProfile, ConnectionStatus
│   ├── index.py            #   IndexInfo, CreateIndexRequest
│   ├── record.py           #   PutRequest, ScanResult, BatchReadRequest 등
│   └── udf.py              #   UdfInfo, UdfUploadRequest, UdfExecuteRequest
│
├── routers/                # API 라우터 (각각 하나의 리소스 담당)
│   ├── admin.py            #   /api/v1/c/{conn_id}/admin      — 사용자/역할 CRUD
│   ├── batch.py            #   /api/v1/c/{conn_id}/batch      — 배치 read/operate/remove
│   ├── cluster.py          #   /api/v1/c/{conn_id}/cluster    — 클러스터 개요, 노드
│   ├── connections.py      #   /api/v1/connections             — 연결 관리
│   ├── import_export.py    #   /api/v1/c/{conn_id}/data       — JSON/CSV import/export
│   ├── indexes.py          #   /api/v1/c/{conn_id}/indexes    — Secondary Index
│   ├── metrics.py          #   /api/v1/c/{conn_id}/metrics    — 서버 메트릭 + WebSocket
│   ├── namespaces.py       #   /api/v1/c/{conn_id}/namespaces — NS/셋/빈
│   ├── operations.py       #   /api/v1/c/{conn_id}/records    — touch, append, operate 등
│   ├── records.py          #   /api/v1/c/{conn_id}/records    — CRUD + scan
│   ├── terminal.py         #   /api/v1/c/{conn_id}/info       — info 명령 실행
│   ├── truncate.py         #   /api/v1/c/{conn_id}/truncate   — 데이터 절삭
│   └── udfs.py             #   /api/v1/c/{conn_id}/udfs       — UDF 관리
│
├── services/               # 비즈니스 로직
│   ├── connection_manager.py   # 멀티 클러스터 연결 lifecycle
│   └── import_export.py        # JSON/CSV 변환
│
└── utils/                  # 순수 유틸리티 (상태 없음)
    ├── info_parser.py      #   Aerospike info 응답 파서
    ├── key_helpers.py      #   PK 파싱, 키 빌드
    └── serialization.py    #   레코드 값 직렬화 (bytes→hex 등)
```

## URL Structure

```
/api/v1/health                          — 헬스 체크
/api/v1/metrics/client                  — 글로벌 클라이언트 메트릭

/api/v1/connections                     — 연결 관리
/api/v1/c/{conn_id}/cluster             — 클러스터 정보
/api/v1/c/{conn_id}/namespaces          — 네임스페이스
/api/v1/c/{conn_id}/records             — 레코드 CRUD + operations
/api/v1/c/{conn_id}/batch               — 배치 작업
/api/v1/c/{conn_id}/indexes             — 인덱스
/api/v1/c/{conn_id}/truncate            — 절삭
/api/v1/c/{conn_id}/udfs               — UDF
/api/v1/c/{conn_id}/admin              — 사용자/역할
/api/v1/c/{conn_id}/metrics            — 서버/NS 메트릭 + WebSocket
/api/v1/c/{conn_id}/info               — info 명령
/api/v1/c/{conn_id}/data               — import/export
```

## Error Handling

모든 라우터에서 `try/except`를 사용하지 않습니다.
`exceptions.py`의 중앙 핸들러가 `aerospike-py` 예외를 자동으로 HTTP 응답으로 변환합니다:

| Exception | HTTP Status |
|-----------|-------------|
| `RecordNotFound` | 404 |
| `RecordExistsError` / `RecordGenerationError` | 409 |
| `InvalidArgError` / `ClientError` / `AerospikeIndexError` / `UDFError` | 400 |
| `AdminError` | 403 |
| `AerospikeTimeoutError` | 504 |
| `ClusterError` | 503 |
| `ServerError` | 502 |
| `AerospikeError` (catch-all) | 500 |

## Configuration

환경 변수 (`ADM_` prefix):

| Variable | Default | Description |
|----------|---------|-------------|
| `ADM_CORS_ORIGINS` | `["http://localhost:5173", ...]` | CORS 허용 오리진 |
| `ADM_METRICS_POLL_INTERVAL` | 2.0 | WebSocket 메트릭 폴링 간격 (초) |

## Development

```bash
# 린트
uv run ruff check .

# 포맷
uv run ruff format .

# 테스트
uv run pytest
```
